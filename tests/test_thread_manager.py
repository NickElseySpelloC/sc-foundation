"""Unit tests for the thread_manager module."""

import threading
from unittest.mock import MagicMock, patch

from sc_foundation.thread_manager import ManagedThread, RestartPolicy, ThreadManager

# ---- Helpers ----


def make_logger():
    """Return a mock logger compatible with ManagedThread."""
    logger = MagicMock()
    logger.log_message = MagicMock(return_value=None)
    logger.log_fatal_error = MagicMock(return_value=None)
    return logger


def quick_task():
    """A task that returns immediately."""
    pass


def crashing_task():
    """A task that always raises."""  # noqa: DOC501
    msg = "intentional crash"
    raise RuntimeError(msg)


# ---- RestartPolicy ----

def test_restart_policy_defaults():
    policy = RestartPolicy()
    assert policy.mode == "never"
    assert policy.max_restarts == 3
    assert policy.backoff_seconds == 2.0


def test_restart_policy_custom_values():
    policy = RestartPolicy(mode="on_crash", max_restarts=5, backoff_seconds=0.5)
    assert policy.mode == "on_crash"
    assert policy.max_restarts == 5
    assert policy.backoff_seconds == 0.5


# ---- ManagedThread ----

def test_managed_thread_starts_and_completes():
    """Thread starts, runs target, and finishes without crashing."""
    mt = ManagedThread(name="test", target=quick_task, logger=make_logger())
    mt.start()
    mt.join(timeout=2.0)
    assert not mt.crashed()


def test_managed_thread_crashed_initially_false():
    mt = ManagedThread(name="test", target=quick_task, logger=make_logger())
    assert not mt.crashed()


def test_managed_thread_stop_sets_stop_event():
    stop_event = threading.Event()
    mt = ManagedThread(name="test", target=quick_task, stop_event=stop_event, logger=make_logger())
    mt.stop()
    assert stop_event.is_set()


def test_managed_thread_crash_sets_crashed_flag():
    """A thread that raises an exception sets the crashed flag."""
    mt = ManagedThread(
        name="test",
        target=crashing_task,
        logger=make_logger(),
        restart=RestartPolicy(mode="never"),
    )
    mt.start()
    mt.join(timeout=2.0)
    assert mt.crashed()


def test_managed_thread_no_double_start():
    """Calling start() on an already-running thread is a no-op."""
    stop_event = threading.Event()

    def blocking():
        stop_event.wait(timeout=5.0)

    mt = ManagedThread(name="test", target=blocking, logger=make_logger())
    mt.start()
    first_thread = mt._thread  # noqa: SLF001
    mt.start()  # second call should be ignored
    assert mt._thread is first_thread  # noqa: SLF001
    stop_event.set()
    mt.join(timeout=2.0)


def test_managed_thread_join_with_no_thread_is_safe():
    """join() before start() does not raise."""
    mt = ManagedThread(name="test", target=quick_task, logger=make_logger())
    mt.join(timeout=0.1)  # should not raise


def test_managed_thread_never_restart_calls_on_fatal_crash():
    """on_fatal_crash callback is invoked when mode='never' and thread crashes."""
    fatal_cb = MagicMock()
    mt = ManagedThread(
        name="crasher",
        target=crashing_task,
        logger=make_logger(),
        restart=RestartPolicy(mode="never"),
        on_fatal_crash=fatal_cb,
    )
    mt.start()
    mt.join(timeout=2.0)
    fatal_cb.assert_called_once_with("crasher")


def test_managed_thread_on_crash_restarts_after_failure():
    """Thread with mode='on_crash' retries after an exception."""
    call_count = [0]

    def flaky():
        call_count[0] += 1
        if call_count[0] < 2:
            msg = "transient error"
            raise RuntimeError(msg)

    with patch("sc_foundation.thread_manager.time.sleep"):
        mt = ManagedThread(
            name="flaky",
            target=flaky,
            logger=make_logger(),
            restart=RestartPolicy(mode="on_crash", max_restarts=3, backoff_seconds=0.0),
        )
        mt.start()
        mt.join(timeout=5.0)

    assert call_count[0] >= 2


def test_managed_thread_on_crash_exceeds_max_restarts_calls_fatal():
    """on_fatal_crash is called after max_restarts is exceeded."""
    fatal_cb = MagicMock()

    with patch("sc_foundation.thread_manager.time.sleep"):
        mt = ManagedThread(
            name="crasher",
            target=crashing_task,
            logger=make_logger(),
            restart=RestartPolicy(mode="on_crash", max_restarts=2, backoff_seconds=0.0),
            on_fatal_crash=fatal_cb,
        )
        mt.start()
        mt.join(timeout=5.0)

    fatal_cb.assert_called_once_with("crasher")


def test_managed_thread_always_restarts_on_normal_exit():
    """Thread with mode='always' re-runs the target after a normal exit."""
    call_count = [0]
    stop_event = threading.Event()

    def counting_task():
        call_count[0] += 1
        if call_count[0] >= 3:
            stop_event.set()

    with patch("sc_foundation.thread_manager.time.sleep"):
        mt = ManagedThread(
            name="counter",
            target=counting_task,
            stop_event=stop_event,
            logger=make_logger(),
            restart=RestartPolicy(mode="always", max_restarts=10, backoff_seconds=0.0),
        )
        mt.start()
        mt.join(timeout=5.0)

    assert call_count[0] >= 3


def test_managed_thread_always_exceeds_max_restarts_calls_fatal():
    """on_fatal_crash is called when mode='always' exceeds max_restarts on normal exits."""
    fatal_cb = MagicMock()

    with patch("sc_foundation.thread_manager.time.sleep"):
        mt = ManagedThread(
            name="quick",
            target=quick_task,
            logger=make_logger(),
            restart=RestartPolicy(mode="always", max_restarts=2, backoff_seconds=0.0),
            on_fatal_crash=fatal_cb,
        )
        mt.start()
        mt.join(timeout=5.0)

    fatal_cb.assert_called_once_with("quick")


# ---- ThreadManager ----

def test_thread_manager_add_returns_managed_thread():
    tm = ThreadManager(logger=make_logger())
    mt = tm.add("t1", quick_task)
    assert isinstance(mt, ManagedThread)
    assert mt.name == "t1"


def test_thread_manager_add_stores_thread():
    tm = ThreadManager(logger=make_logger())
    tm.add("t1", quick_task)
    assert len(tm._threads) == 1  # noqa: SLF001


def test_thread_manager_add_with_args_and_kwargs():
    tm = ThreadManager(logger=make_logger())
    mt = tm.add("t1", quick_task, args=(1, 2), kwargs={"key": "val"})
    assert mt.args == (1, 2)
    assert mt.kwargs == {"key": "val"}


def test_thread_manager_add_uses_global_stop_by_default():
    tm = ThreadManager(logger=make_logger())
    mt = tm.add("t1", quick_task)
    assert mt.stop_event is tm.global_stop


def test_thread_manager_add_uses_custom_stop_event():
    tm = ThreadManager(logger=make_logger())
    custom_stop = threading.Event()
    mt = tm.add("t1", quick_task, stop_event=custom_stop)
    assert mt.stop_event is custom_stop


def test_thread_manager_add_uses_provided_restart_policy():
    tm = ThreadManager(logger=make_logger())
    policy = RestartPolicy(mode="on_crash", max_restarts=5)
    mt = tm.add("t1", quick_task, restart=policy)
    assert mt.restart.mode == "on_crash"
    assert mt.restart.max_restarts == 5


def test_thread_manager_exit_on_fatal_true_sets_callback():
    tm = ThreadManager(logger=make_logger(), exit_on_fatal=True)
    mt = tm.add("t1", quick_task)
    assert mt.on_fatal_crash is not None


def test_thread_manager_exit_on_fatal_false_no_callback():
    tm = ThreadManager(logger=make_logger(), exit_on_fatal=False)
    mt = tm.add("t1", quick_task)
    assert mt.on_fatal_crash is None


def test_thread_manager_start_all_and_join_all():
    """All threads run to completion."""
    results = []

    def task(value):
        results.append(value)

    tm = ThreadManager(logger=make_logger())
    tm.add("t1", task, args=(1,))
    tm.add("t2", task, args=(2,))
    tm.start_all()
    tm.join_all(timeout_per_thread=2.0)

    assert sorted(results) == [1, 2]


def test_thread_manager_stop_all_signals_global_stop():
    """stop_all() sets the global stop event."""
    stop_event = threading.Event()
    tm = ThreadManager(logger=make_logger(), global_stop=stop_event)

    def blocking():
        stop_event.wait(timeout=5.0)

    tm.add("t1", blocking)
    tm.start_all()
    tm.stop_all()
    tm.join_all(timeout_per_thread=2.0)

    assert stop_event.is_set()


def test_thread_manager_any_crashed_false_on_clean_exit():
    tm = ThreadManager(logger=make_logger(), exit_on_fatal=False)
    tm.add("t1", quick_task)
    tm.start_all()
    tm.join_all(timeout_per_thread=2.0)
    assert not tm.any_crashed()


def test_thread_manager_any_crashed_true_after_crash():
    tm = ThreadManager(logger=make_logger(), exit_on_fatal=False)
    tm.add("t1", crashing_task)
    tm.start_all()
    tm.join_all(timeout_per_thread=2.0)
    assert tm.any_crashed()


def test_thread_manager_handle_fatal_crash_calls_before_exit_and_os_exit():
    before_exit = MagicMock()
    tm = ThreadManager(logger=make_logger(), before_exit=before_exit)

    with patch("sc_foundation.thread_manager.time.sleep"), patch("os._exit") as mock_exit:
        tm._handle_fatal_crash("some_thread")  # noqa: SLF001

    before_exit.assert_called_once()
    mock_exit.assert_called_once_with(1)


def test_thread_manager_handle_fatal_crash_without_before_exit():
    """_handle_fatal_crash still calls os._exit when no before_exit is set."""
    tm = ThreadManager(logger=make_logger())

    with patch("sc_foundation.thread_manager.time.sleep"), patch("os._exit") as mock_exit:
        tm._handle_fatal_crash("some_thread")  # noqa: SLF001

    mock_exit.assert_called_once_with(1)


def test_thread_manager_stop_all_calls_stop_on_bound_method_instance():
    """stop_all() invokes stop() on the target's owning instance if available."""
    class Worker:
        def __init__(self):
            self.stopped = False

        def run(self):
            pass

        def stop(self):
            self.stopped = True

    worker = Worker()
    tm = ThreadManager(logger=make_logger())
    tm.add("worker", worker.run)
    tm.stop_all()
    assert worker.stopped


def test_thread_manager_stop_all_falls_back_to_shutdown():
    """stop_all() falls back to shutdown() if stop() is not on the instance."""
    class Worker:
        def __init__(self):
            self.shutdown_called = False

        def run(self):
            pass

        def shutdown(self):
            self.shutdown_called = True

    worker = Worker()
    tm = ThreadManager(logger=make_logger())
    tm.add("worker", worker.run)
    tm.stop_all()
    assert worker.shutdown_called


def test_thread_manager_custom_global_stop_event():
    """ThreadManager uses a provided global_stop event."""
    custom_stop = threading.Event()
    tm = ThreadManager(logger=make_logger(), global_stop=custom_stop)
    assert tm.global_stop is custom_stop
