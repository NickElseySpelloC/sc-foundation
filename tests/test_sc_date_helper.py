"""pytest for DateHelper class."""
import datetime as dt
import json
import time
from pathlib import Path

import pytest

from sc_foundation import DateHelper, SCCommon

CONFIG_FILE = "tests/config.yaml"


def test_add():
    """Test add."""
    date_obj = dt.date(2025, 2, 1)
    datetime_obj = dt.datetime(2025, 2, 1, 12, 30, 45)  # noqa: DTZ001
    datetime_with_utctz_obj = dt.datetime(2025, 2, 1, 12, 30, 45, tzinfo=dt.UTC)

    assert DateHelper.add(date_obj, days=5) == dt.date(2025, 2, 6), "Adding 5 days to 2025-02-01 should be 2025-02-06"
    assert DateHelper.add(datetime_obj, days=1, hours=3) == dt.datetime(2025, 2, 2, 15, 30, 45), "Adding 1 day and 3 hours to 2025-02-01 12:30:45 should be 2025-02-02 15:30:45"  # noqa: DTZ001
    assert DateHelper.add(datetime_with_utctz_obj, days=1, hours=3) == dt.datetime(2025, 2, 2, 15, 30, 45, tzinfo=dt.UTC), "Adding 1 day and 3 hours to 2025-02-01 12:30:45+00:00 should be 2025-02-02 15:30:45+00:00"
    with pytest.raises(TypeError) as exc_info:
        DateHelper.add(date_obj, dogs=5)
    assert str(exc_info.typename) == "TypeError", "Adding invalid keyword arguments should raise TypeError"


def test_format():
    """Test format."""
    date_obj = dt.date(2025, 2, 1)
    time_obj = dt.time(12, 30, 45, 123)
    datetime_obj = dt.datetime(2025, 2, 1, 12, 30, 45)  # noqa: DTZ001
    datetime_with_utctz_obj = dt.datetime(2025, 2, 1, 12, 30, 45, tzinfo=dt.UTC)

    # Test the default format
    assert DateHelper.format(date_obj) == "2025-02-01", "Formatted date should be '2025-02-01'"
    assert DateHelper.format(time_obj) == "12:30:45", "Formatted time should be '12:30:45'"
    assert DateHelper.format(datetime_obj) == "2025-02-01 12:30:45", "Formatted datetime should be '2025-02-01 12:30:45'"
    assert DateHelper.format(datetime_with_utctz_obj, hide_tz=False) == "2025-02-01 12:30:45+00:00", "Formatted datetime with tz should be '2025-02-01T12:30:45+00:00'"

    # Test the ISO format
    assert DateHelper.format(date_obj, "ISO") == "2025-02-01", "ISO formatted date should be '2025-02-01'"
    assert DateHelper.format(time_obj, "ISO") == "12:30:45.000123", "ISO formatted time should be '12:30:45.000123'"
    assert DateHelper.format(datetime_obj, "ISO") == "2025-02-01T12:30:45", "ISO formatted datetime should be '2025-02-01T12:30:45'"
    assert DateHelper.format(datetime_with_utctz_obj, "ISO") == "2025-02-01T12:30:45+00:00", "ISO formatted datetime with tz should be '2025-02-01T12:30:45+00:00'"

    # Test some manual format
    assert DateHelper.format(date_obj, format_str="%d-%m-%Y") == "01-02-2025", "Formatted date should be '01-02-2025'"
    assert DateHelper.format(time_obj, format_str="%H:%M:%S.%f") == "12:30:45.000123", "Formatted time should be '12:30:45.000123'"
    assert DateHelper.format(datetime_obj, format_str="%d-%m-%Y %H:%M") == "01-02-2025 12:30", "Formatted datetime should be '01-02-2025 12:30'"


def test_extract():
    """Test extract."""
    date_str = "2025-02-04"
    datetime_str = "2025-02-04 12:30:45"
    datetime_with_tz_str = "2025-02-04 12:30:45+11:00"
    datetime_iso_str = "2025-02-04T12:30:45+11:00"
    time_str = "12:30:45"
    time_with_ms_str = "12:30:45.123456"
    assert DateHelper.extract(date_str) == dt.date(2025, 2, 4), "Extracted date should be 2025-02-04"
    assert DateHelper.extract(datetime_str) == dt.datetime(2025, 2, 4, 12, 30, 45), "Extracted datetime should be 2025-02-04 12:30:45"  # noqa: DTZ001
    assert DateHelper.extract(datetime_with_tz_str, "%Y-%m-%d %H:%M:%S%z") == dt.datetime(2025, 2, 4, 12, 30, 45, tzinfo=dt.timezone(dt.timedelta(hours=11))), "Extracted datetime with tz should be 2025-02-04 12:30:45+11:00"
    assert DateHelper.extract(datetime_iso_str, "ISO") == dt.datetime(2025, 2, 4, 12, 30, 45, tzinfo=dt.timezone(dt.timedelta(hours=11))), "Extracted ISO datetime should be 2025-02-04 12:30:45+11:00"
    assert DateHelper.extract(datetime_iso_str, "ISO", hide_tz=True) == dt.datetime(2025, 2, 4, 12, 30, 45), "Extracted ISO datetime with hide_tz=True should be 2025-02-04 12:30:45"  # noqa: DTZ001
    assert DateHelper.extract(time_str) == dt.time(12, 30, 45), "Extracted time should be 12:30:45"
    assert DateHelper.extract(time_with_ms_str) == dt.time(12, 30, 45, 123456), "Extracted time with ms should be 12:30:45.123456"

    # Test format classification
    assert isinstance(DateHelper.extract(date_str, format_str="%Y-%m-%d"), dt.date), "Should return a date object when format_str indicates a date"
    assert isinstance(DateHelper.extract(datetime_str, format_str="%Y-%m-%d %H:%M:%S"), dt.datetime), "Should return a datetime object when format_str indicates a datetime"
    assert isinstance(DateHelper.extract(time_str, format_str="%H:%M:%S"), dt.time), "Should return a time object when format_str indicates a time"

    assert isinstance(DateHelper.extract(date_str, format_str="ISO"), dt.date), "Should return a date object when format_str indicates a date"
    assert isinstance(DateHelper.extract(datetime_str, format_str="ISO"), dt.datetime), "Should return a datetime object when format_str indicates a datetime"
    assert isinstance(DateHelper.extract(time_str, format_str="ISO"), dt.time), "Should return a time object when format_str indicates a time"

    assert isinstance(DateHelper.extract(date_str, dt_type=dt.date), dt.date), "Should return a date object when format_str indicates a date"
    assert isinstance(DateHelper.extract(datetime_str, dt_type=dt.datetime), dt.datetime), "Should return a datetime object when format_str indicates a datetime"
    assert isinstance(DateHelper.extract(time_str, dt_type=dt.time), dt.time), "Should return a time object when format_str indicates a time"

    assert isinstance(DateHelper.extract_date(date_str), dt.date), "Should return a date object when format_str indicates a date"
    assert isinstance(DateHelper.extract_datetime(datetime_str), dt.datetime), "Should return a datetime object when format_str indicates a datetime"
    assert isinstance(DateHelper.extract_time(time_str), dt.time), "Should return a time object when format_str indicates a time"


def test_add_timezone():
    """Test adding timezone to a datetime."""
    naive_datetime = dt.datetime(2025, 2, 1, 12, 30, 45)  # noqa: DTZ001
    aware_datetime = DateHelper.add_timezone(naive_datetime, tzinfo=dt.UTC)
    assert aware_datetime.tzinfo == dt.UTC, "Timezone should be set to UTC"
    assert aware_datetime.replace(tzinfo=None) == naive_datetime, "Naive datetime should match the aware datetime without tzinfo"


def test_remove_timezone():
    """Test removing timezone from a datetime."""
    aware_datetime = dt.datetime(2025, 2, 1, 12, 30, 45, tzinfo=dt.UTC)
    naive_datetime = DateHelper.remove_timezone(aware_datetime)
    assert naive_datetime.tzinfo is None, "Timezone should be removed"
    assert naive_datetime == aware_datetime.replace(tzinfo=None), "Naive datetime should match the aware datetime without tzinfo"


def test_days_between():
    """Test calculating the number of days between two dates."""
    d1 = dt.date(2024, 1, 1)
    d2 = dt.date(2024, 1, 10)
    assert DateHelper.days_between(d1, d2) == 9, "Days between 2024-01-01 and 2024-01-10 should be 9"


def test_get_file_date():
    """Test getting the file date."""
    file_path = Path(CONFIG_FILE)
    file_date = DateHelper.get_file_date(CONFIG_FILE)

    local_tz = dt.datetime.now().astimezone().tzinfo
    check_file_date = dt.datetime.fromtimestamp(file_path.stat().st_mtime, tz=local_tz).date()
    assert file_date == check_file_date, "File date should match the last modified date of the file"


def test_get_file_datetime():
    """Test getting the file datetime."""
    file_path = Path(CONFIG_FILE)
    file_date = DateHelper.get_file_datetime(CONFIG_FILE)

    local_tz = dt.datetime.now().astimezone().tzinfo
    check_file_datetime = dt.datetime.fromtimestamp(file_path.stat().st_mtime, tz=local_tz)
    assert file_date == check_file_datetime, "File datetime should match the last modified datetime of the file"


def test_get_local_timezone():
    """Test getting the local timezone."""
    local_tz = DateHelper.get_local_timezone()
    expected_tz = dt.datetime.now().astimezone().tzinfo
    assert local_tz == expected_tz, "Local timezone should match the system's local timezone"


def test_is_valid_date():
    """Test is_valid_date."""
    date_str = "2025-05-04"
    datetime_str = "2025-05-04 12:10:08"
    assert DateHelper.is_valid_date(date_str, "%Y-%m-%d"), "Date '2025-05-04' should be valid"
    assert DateHelper.is_valid_date(datetime_str, "%Y-%m-%d %H:%M:%S"), "Datetime '2025-05-04  12:10:08' should be valid"


def test_is_valid_datetime():
    """Test is_valid_datetime."""
    date_str = "2025-05-04"
    datetime_str = "2025-05-04 12:10:08"
    assert DateHelper.is_valid_datetime(date_str, "%Y-%m-%d"), "Date '2025-05-04' should be valid as datetime"
    assert DateHelper.is_valid_datetime(datetime_str, "%Y-%m-%d %H:%M:%S"), "Datetime '2025-05-04  12:10:08' should be valid"


def test_is_valid_time():
    """Test is_valid_time."""
    time_str = "12:10:08"
    assert DateHelper.is_valid_time(time_str, "%H:%M:%S"), "Time '12:10:08' should be valid"


def test_now():
    """Test today()."""
    local_tz = dt.datetime.now().astimezone().tzinfo
    time_now = dt.datetime.now(tz=local_tz)
    time_now_str = DateHelper.format(time_now, "%Y-%m-%d %H:%M")
    func_time_now_str = DateHelper.format(DateHelper.now(), "%Y-%m-%d %H:%M")
    assert time_now_str == func_time_now_str, "Now should return the current time"


def test_frozen_now():
    """Test now() with frozen time."""
    project_root = SCCommon.get_project_root()
    freeze_file = project_root / "freeze_time.json"

    try:
        # Scenario 1: Freeze time forever (one_time = false)
        freeze_config = {
            "freeze_time": "2026-02-21T12:34:56+11:00",
            "one_time": False
        }
        with freeze_file.open("w") as f:
            json.dump(freeze_config, f, indent=4)

        t1 = DateHelper.now()
        time.sleep(1.5)
        t2 = DateHelper.now()

        assert t1 == t2, "Frozen time should return the same datetime on multiple calls"
        assert str(t1) == "2026-02-21 12:34:56+11:00", f"Frozen time should be '2026-02-21 12:34:56+11:00', got '{t1}'"

        # Clean up for next test
        freeze_file.unlink()

        # Scenario 2: Freeze time and then tick forward after first read (one_time = true)
        freeze_config = {
            "freeze_time": "2026-03-15T08:00:00",
            "one_time": True
        }
        with freeze_file.open("w") as f:
            json.dump(freeze_config, f, indent=4)

        t1 = DateHelper.now()
        assert t1.year == 2026, "First call should return frozen time"
        assert t1.month == 3, "First call should return frozen time"
        assert t1.day == 15, "First call should return frozen time"
        assert t1.hour == 8, "First call should return frozen time"

        time.sleep(2)  # Wait 2 seconds

        t2 = DateHelper.now()
        time_diff = (t2 - t1).total_seconds()
        assert 1.5 <= time_diff <= 2.5, f"Second call should be ~2 seconds later, got {time_diff:.2f} seconds"

        # Verify config was updated to offset_time
        with freeze_file.open("r") as f:
            updated_config = json.load(f)
        assert updated_config.get("freeze_time") is None, "freeze_time should be None after one_time use"
        assert "offset_time_unit" in updated_config, "offset_time_unit should be set after one_time use"
        assert "offset_time_amount" in updated_config, "offset_time_amount should be set after one_time use"

        # Clean up for next test
        freeze_file.unlink()

        # Scenario 3: Offset time
        freeze_config = {
            "offset_time_unit": "hours",
            "offset_time_amount": 5
        }
        with freeze_file.open("w") as f:
            json.dump(freeze_config, f, indent=4)

        actual_now = dt.datetime.now(tz=DateHelper.get_local_timezone())
        offset_now = DateHelper.now()
        diff_hours = (offset_now - actual_now).total_seconds() / 3600

        assert 4.9 <= diff_hours <= 5.1, f"Offset should be ~5 hours, got {diff_hours:.2f} hours"

    finally:
        # Clean up freeze_time.json if it exists
        if freeze_file.exists():
            freeze_file.unlink()


def test_now_str():
    """Test getting string representation of the current time."""
    local_tz = dt.datetime.now().astimezone().tzinfo
    time_now = dt.datetime.now(tz=local_tz)
    time_str = DateHelper.format(time_now, "%Y-%m-%d %H:%M")
    formatted_now = DateHelper.format(DateHelper.now(), "%Y-%m-%d %H:%M")
    assert time_str == formatted_now, "Current time string representation should match the formatted datetime"


def test_now_utc():
    """Test now() with UTC timezone."""
    time_now_utc = DateHelper.now_utc()
    assert time_now_utc.tzinfo == dt.UTC, "Timezone should be set to UTC"


def test_today_add_days():
    """Test today() with add_days."""
    today_date = DateHelper.today()
    future_date = DateHelper.add(today_date, days=5)
    assert future_date == today_date + dt.timedelta(days=5), "Adding 5 days to today should return the correct date"


def test_today():
    """Test today()."""
    local_tz = dt.datetime.now().astimezone().tzinfo
    today_date = dt.datetime.now(tz=local_tz).date()
    assert DateHelper.today() == today_date, "Today should return the current date"


def test_today_str():
    """Test getting string representation of today's date."""
    today_str = DateHelper.today_str()
    formatted_today = DateHelper.format(DateHelper.today())
    assert today_str == formatted_today, "Today's string representation should match the formatted date"


def test_today_utc():
    """Test today() with UTC timezone."""
    today_utc = DateHelper.today_utc()
    assert today_utc == dt.datetime.now(dt.UTC).date(), "Today's date in UTC should match the current UTC date"


# test_add()
# test_format()
# test_extract()
# test_add_timezone()
# test_get_file_date()
# test_get_file_datetime()
# test_get_local_timezone()
# test_is_valid_date()
# test_is_valid_datetime()
# test_is_valid_time()
# test_now()
# test_frozen_now()
# test_now_str()
# test_now_utc()
# test_today_add_days()
# test_today()
# test_today_str()
# test_today_utc()
# test_remove_timezone()
