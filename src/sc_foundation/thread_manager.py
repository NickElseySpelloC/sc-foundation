from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class RestartPolicy:
    mode: str = "never"  # "never" | "on_crash" | "always"
    max_restarts: int = 3
    backoff_seconds: float = 2.0


@dataclass
class ManagedThread:
    """Encapsulates a thread with crash handling and optional restart logic."""
    name: str
    target: Callable[..., Any]
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    stop_event: threading.Event = field(default_factory=threading.Event)
    logger: Any = None
    restart: RestartPolicy = field(default_factory=RestartPolicy)
    on_fatal_crash: Callable[[str], None] | None = None  # NEW: callback for unrecoverable crashes

    _thread: threading.Thread | None = field(init=False, default=None)
    _crash_event: threading.Event = field(init=False, default_factory=threading.Event)
    _start_lock: threading.Lock = field(init=False, default_factory=threading.Lock)

    # ---- Public methods ----

    def start(self):
        """Start the thread if it's not already running."""
        with self._start_lock:
            if self._thread and self._thread.is_alive():
                return
            self._crash_event.clear()
            # Make thread non-daemon for clean join (prevents late dummy finalizer)
            self._thread = threading.Thread(target=self._runner, name=self.name, daemon=False)
            self._thread.start()

    def stop(self):
        """Signal the thread to stop cooperatively."""
        self.stop_event.set()

    def join(self, timeout: float | None = None):
        """Join the thread, waiting for it to finish.

        Args:
            timeout (float | None): Maximum time to wait for the thread to finish. If None, wait indefinitely.
        """
        if self._thread:
            self._thread.join(timeout=timeout)

    def crashed(self) -> bool:
        """Check if the thread has crashed.

        Returns:
            bool: True if the thread has crashed, False otherwise.
        """
        return self._crash_event.is_set()

    # ---- Internal methods ----

    def _runner(self):
        restarts = 0
        while not self.stop_event.is_set():
            try:
                self.logger.log_message(f"[{self.name}] thread starting.", "debug")
                self.target(*self.args, **self.kwargs)
                # Normal exit
                self.logger and self.logger.log_message(f"[{self.name}] exited normally.", "debug")  # pyright: ignore[reportUnusedExpression]
                if self.restart.mode == "always" and not self.stop_event.is_set():
                    restarts += 1
                    if restarts > self.restart.max_restarts:
                        self.logger and self.logger.log_fatal_error(
                            f"[{self.name}] exceeded max restarts ({self.restart.max_restarts}).", report_stack=False
                        )  # pyright: ignore[reportUnusedExpression]
                        self._crash_event.set()
                        # NEW: trigger fatal crash handler
                        if self.on_fatal_crash:
                            self.on_fatal_crash(self.name)
                        break
                    time.sleep(self.restart.backoff_seconds * restarts)
                    continue
                break
            except Exception as e:  # noqa: BLE001
                self.logger and self.logger.log_message(f"[{self.name}] crashed with error: {e}", "error")  # pyright: ignore[reportUnusedExpression]
                self._crash_event.set()
                if self.restart.mode in {"on_crash", "always"}:
                    restarts += 1
                    if restarts > self.restart.max_restarts:
                        self.logger and self.logger.log_fatal_error(
                            f"[{self.name}] exceeded max restarts ({self.restart.max_restarts}).", report_stack=False
                        )  # pyright: ignore[reportUnusedExpression]
                        # NEW: trigger fatal crash handler
                        if self.on_fatal_crash:
                            self.on_fatal_crash(self.name)
                        break
                    time.sleep(self.restart.backoff_seconds * restarts)
                    continue
                # NEW: no restart policy, crash is fatal
                if self.on_fatal_crash:
                    self.on_fatal_crash(self.name)
                break


class ThreadManager:
    """Manages multiple threads with cooperative stopping and crash handling."""
    def __init__(
        self,
        logger: Any,
        global_stop: threading.Event | None = None,
        exit_on_fatal: bool = True,
        before_exit: Callable[[], None] | None = None,
    ):
        self.logger = logger
        self.global_stop = global_stop or threading.Event()
        self.exit_on_fatal = exit_on_fatal
        self.before_exit = before_exit
        self._threads: list[ManagedThread] = []
        self._lock = threading.Lock()

    # ---- Public methods ----

    def add(
        self,
        name: str,
        target: Callable[..., Any],
        *,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        restart: RestartPolicy | None = None,
        stop_event: threading.Event | None = None,
    ) -> ManagedThread:
        """Add a new managed thread.

        Args:
            name (str): Name of the thread.
            target (Callable[..., Any]): The target function to run in the thread.
            args (tuple[Any, ...], optional): Positional arguments for the target function.
            kwargs (dict[str, Any], optional): Keyword arguments for the target function.
            restart (RestartPolicy | None, optional): Restart policy for the thread.
            stop_event (threading.Event | None, optional): Event to signal the thread to stop.

        Returns:
            ManagedThread: The managed thread instance.
        """
        mt = ManagedThread(
            name=name,
            target=target,
            args=args,
            kwargs=kwargs or {},
            stop_event=stop_event or self.global_stop,
            logger=self.logger,
            restart=restart or RestartPolicy(mode="never"),
            on_fatal_crash=self._handle_fatal_crash if self.exit_on_fatal else None,  # NEW
        )
        with self._lock:
            self._threads.append(mt)
        return mt

    def start_all(self):
        """Start all managed threads."""
        with self._lock:
            for t in self._threads:
                t.start()

    def stop_all(self):
        """Signal all threads to stop cooperatively."""
        with self._lock:  # noqa: PLR1702
            for t in self._threads:
                # Signal cooperative stop
                t.stop()
                # If target is a bound method, try a graceful stopper on the instance
                try:
                    obj = getattr(t.target, "__self__", None)  # bound method -> instance
                    if obj is not None:
                        for meth in ("stop", "shutdown", "close"):
                            fn = getattr(obj, meth, None)
                            if callable(fn):
                                try:
                                    fn()
                                except Exception as e:  # noqa: BLE001
                                    self.logger and self.logger.log_message(f"[{t.name}] error calling {meth}(): {e}", "error")  # pyright: ignore[reportUnusedExpression]
                                break
                except Exception as e:  # noqa: BLE001
                    self.logger and self.logger.log_message(f"[{t.name}] stop hook error: {e}", "error")  # pyright: ignore[reportUnusedExpression]

    def join_all(self, timeout_per_thread: float = 5.0):
        """Join all threads, waiting for them to finish."""
        with self._lock:
            for t in self._threads:
                t.join(timeout=timeout_per_thread)

    def any_crashed(self) -> bool:
        """Check if any managed thread has crashed.

        Returns:
            bool: True if any thread has crashed, False otherwise.
        """
        with self._lock:
            return any(t.crashed() for t in self._threads)

    # ---- Internal methods ----

    def _handle_fatal_crash(self, thread_name: str):
        """Called when a thread crashes fatally (no restart or max restarts exceeded)."""
        self.stop_all()
        time.sleep(2.0)
        # self.logger.log_fatal_error(f"Thread [{thread_name}] crashed fatally. Shutting down application.", report_stack=True, exit_app=False)
        self.logger.log_fatal_error(f"Thread [{thread_name}] crashed fatally. Shutting down application.", report_stack=True, exit_app=False)
        if self.before_exit:
            self.before_exit()
        os._exit(1)
