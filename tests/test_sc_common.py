"""Unit tests for the sc_common module."""

import os
import subprocess  # noqa: S404
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sc_foundation.sc_common import SCCommon


def test_is_valid_hostname_valid_ipv4():
    """Test is_valid_hostname with valid IPv4 addresses."""
    assert SCCommon.is_valid_hostname("192.168.1.1") is True
    assert SCCommon.is_valid_hostname("10.0.0.1") is True
    assert SCCommon.is_valid_hostname("127.0.0.1") is True
    assert SCCommon.is_valid_hostname("255.255.255.255") is True


def test_is_valid_hostname_invalid_ipv4():
    """Test is_valid_hostname with invalid IPv4 addresses."""
    assert SCCommon.is_valid_hostname("256.1.1.1") is False
    assert SCCommon.is_valid_hostname("192.168.1") is False
    assert SCCommon.is_valid_hostname("192.168.1.1.1") is False
    assert SCCommon.is_valid_hostname("192.168.1.a") is False


def test_is_valid_hostname_valid_ipv6():
    """Test is_valid_hostname with valid IPv6 addresses."""
    assert SCCommon.is_valid_hostname("::1") is True
    assert SCCommon.is_valid_hostname("2001:db8::1") is True
    assert SCCommon.is_valid_hostname("fe80::1") is True


def test_is_valid_hostname_valid_dns():
    """Test is_valid_hostname with valid DNS hostnames."""
    assert SCCommon.is_valid_hostname("example.com") is True
    assert SCCommon.is_valid_hostname("subdomain.example.com") is True
    assert SCCommon.is_valid_hostname("test-host.example.org") is True
    assert SCCommon.is_valid_hostname("localhost") is True
    assert SCCommon.is_valid_hostname("example.com.") is True  # FQDN


def test_is_valid_hostname_invalid_dns():
    """Test is_valid_hostname with invalid DNS hostnames."""
    assert SCCommon.is_valid_hostname("-example.com") is False
    assert SCCommon.is_valid_hostname("example-.com") is False
    assert SCCommon.is_valid_hostname("example..com") is False
    assert SCCommon.is_valid_hostname("ex@mple.com") is False
    assert SCCommon.is_valid_hostname("a" * 64 + ".com") is False  # Label too long


def test_is_valid_hostname_invalid_input():
    """Test is_valid_hostname with invalid input types."""
    assert SCCommon.is_valid_hostname("") is False
    assert SCCommon.is_valid_hostname(None) is False  # type: ignore[arg-type]
    assert SCCommon.is_valid_hostname(123) is False  # type: ignore[arg-type]
    assert SCCommon.is_valid_hostname([]) is False  # type: ignore[arg-type]


@patch("sc_foundation.sc_common.subprocess.run")
@patch("sc_foundation.sc_common.platform.system")
def test_ping_host_success_linux(mock_platform, mock_run):
    """Test ping_host success on Linux."""
    mock_platform.return_value = "Linux"
    mock_run.return_value = MagicMock(returncode=0)

    result = SCCommon.ping_host("192.168.1.1")

    assert result is True
    mock_run.assert_called_once_with(
        ["ping", "-c", "1", "-W", "1", "192.168.1.1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
        check=False
    )


@patch("sc_foundation.sc_common.subprocess.run")
@patch("sc_foundation.sc_common.platform.system")
def test_ping_host_success_windows(mock_platform, mock_run):
    """Test ping_host success on Windows."""
    mock_platform.return_value = "Windows"
    mock_run.return_value = MagicMock(returncode=0)

    result = SCCommon.ping_host("192.168.1.1")

    assert result is True
    mock_run.assert_called_once_with(
        ["ping", "-n", "1", "-W", "1", "192.168.1.1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
        check=False
    )


@patch("sc_foundation.sc_common.subprocess.run")
@patch("sc_foundation.sc_common.platform.system")
def test_ping_host_failure(mock_platform, mock_run):
    """Test ping_host failure."""
    mock_platform.return_value = "Linux"
    mock_run.return_value = MagicMock(returncode=1)

    result = SCCommon.ping_host("192.168.1.1")

    assert result is False


def test_ping_host_invalid_ip():
    """Test ping_host with invalid IP address."""
    with pytest.raises(RuntimeError, match="Invalid IP address"):
        SCCommon.ping_host("192.168.3.4.5")


def test_ping_host_untrusted_input():
    """Test ping_host with untrusted input."""
    with pytest.raises(RuntimeError, match="Invalid IP address"):
        SCCommon.ping_host("192.168.1.1; rm -rf /")


def test_check_internet_connection():
    """Test check_internet_connection."""
    assert SCCommon.check_internet_connection() is True  # This will depend on your actual internet connection


def test_get_project_root():
    """Test get_project_root."""
    root = SCCommon.get_project_root()
    assert root is not None
    assert root.is_dir()
    assert (root / "src").is_dir() or (root / "README.md").is_file()  # Check for common project files

    # Test environment variable override
    special_dir = "/Users/nick/dev/sc-foundation"
    os.environ["SC_FOUNDATION_PROJECT_ROOT"] = special_dir
    root = SCCommon.get_project_root()
    assert root is not None
    assert root.is_dir()
    assert root == Path(special_dir)


def test_is_probable_path_absolute_path():
    """Test is_probable_path with absolute paths."""
    assert SCCommon.is_probable_path("/usr/bin/python") is True
    assert SCCommon.is_probable_path("C:\\Windows\\System32") is True
    assert SCCommon.is_probable_path(Path("/usr/bin/python")) is True


def test_is_probable_path_relative_path():
    """Test is_probable_path with relative paths."""
    assert SCCommon.is_probable_path("./config.yaml") is True
    assert SCCommon.is_probable_path("../data/file.txt") is True
    assert SCCommon.is_probable_path("folder/file.txt") is True


def test_is_probable_path_file_extension():
    """Test is_probable_path with file extensions."""
    assert SCCommon.is_probable_path("config.yaml") is True
    assert SCCommon.is_probable_path("data.json") is True
    assert SCCommon.is_probable_path("script.py") is True


def test_is_probable_path_not_path():
    """Test is_probable_path with non-path strings."""
    assert SCCommon.is_probable_path("justtext") is False
    assert SCCommon.is_probable_path("no-extension") is False


@patch("sc_foundation.sc_common.SCCommon.get_os")
@patch("sc_foundation.sc_common.os.pathconf")
def test_is_probable_path_too_long(mock_pathconf, mock_get_os):
    """Test is_probable_path with path too long."""
    mock_get_os.return_value = "linux"
    mock_pathconf.return_value = 100

    long_path = "a" * 150 + ".txt"
    assert SCCommon.is_probable_path(long_path) is False


@patch("sc_foundation.sc_common.Path.cwd")
def test_select_file_location_absolute_path(mock_cwd):  # noqa: ARG001
    """Test select_file_location with absolute path."""
    result = SCCommon.select_file_location("/etc/config.yaml")
    assert result == Path("/etc/config.yaml")


@patch("sc_foundation.sc_common.Path.cwd")
def test_select_file_location_relative_path(mock_cwd):
    """Test select_file_location with relative path."""
    mock_cwd.return_value = Path("/home/user")

    result = SCCommon.select_file_location("config/settings.yaml")
    assert str(result).find("/home/user/config/settings.yaml")


@patch("sc_foundation.sc_common.os.getpid")
def test_get_process_id(mock_getpid):
    """Test get_process_id."""
    mock_getpid.return_value = 12345
    assert SCCommon.get_process_id() == 12345
    mock_getpid.assert_called_once()


def test_get_process_id_integration():
    """Test get_process_id integration."""
    pid = SCCommon.get_process_id()
    assert isinstance(pid, int)
    assert pid > 0


# test_select_file_location_absolute_path()
# test_select_file_location_relative_path()
# test_get_project_root()
