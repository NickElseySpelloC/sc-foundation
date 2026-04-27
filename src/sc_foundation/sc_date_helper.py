"""Some basic shorts for handling dates."""

import contextlib
import datetime as dt
import json
from pathlib import Path

import pytz
from astral import LocationInfo
from astral.sun import sun
from tzfpy import get_tz

from sc_foundation.sc_common import SCCommon


class DateHelper:  # noqa: PLR0904
    """
    Class for simplyify date operations.

    This class provides static methods to handle date formatting, parsing, and calculations.

    This function supports a freeze time feature for testing purposes. See 'Freeze time feature' in the documentation below for more details.
    """

    @staticmethod
    def add(dt_obj: dt.date | dt.datetime, **kwargs) -> dt.date | dt.datetime:
        """
        Add a timedelta to a date or datetime object.

        Args:
            dt_obj (date | datetime): The date or datetime object to which the timedelta will be added.
            **kwargs (keyword arguments): The keyword arguments to pass to the timedelta constructor (e.g., days=1, hours=2).

        Raises:
            TypeError: If dt_obj is not a date or datetime object, or if the keyword arguments are not valid for a timedelta.

        Returns:
            result (date | datetime): A new date or datetime object with the added timedelta.
        """
        if dt_obj is None or not isinstance(dt_obj, (dt.date, dt.datetime)):
            msg = f"Invalid data type passed DateHelper.add({dt_obj}). Expected a date or datetime object."
            raise TypeError(msg)

        try:
            return dt_obj + dt.timedelta(**kwargs)
        except TypeError as e:
            msg = f"Invalid keyword arguments for timedelta in DateHelper.add(dt_obj={dt_obj}, kwargs={kwargs}): {e}"
            raise TypeError(msg) from e

    @staticmethod
    def add_date(dt_obj: dt.date, **kwargs) -> dt.date:
        """
        Add a timedelta to a date object.

        Args:
            dt_obj (date): The date object to which the timedelta will be added.
            **kwargs (keyword arguments): The keyword arguments to pass to the timedelta constructor (e.g., days=1, hours=2).

        Raises:
            TypeError: If dt_obj is not a date object, or if the keyword arguments are not valid for a timedelta.

        Returns:
            result (date): A new date object with the added timedelta.
        """
        if dt_obj is None or not isinstance(dt_obj, dt.date):
            msg = f"Invalid data type passed DateHelper.add_date({dt_obj}). Expected a date object."
            raise TypeError(msg)

        try:
            return dt_obj + dt.timedelta(**kwargs)
        except TypeError as e:
            msg = f"Invalid keyword arguments for timedelta in DateHelper.add_date(dt_obj={dt_obj}, kwargs={kwargs}): {e}"
            raise TypeError(msg) from e

    @staticmethod
    def add_datetime(dt_obj: dt.datetime, **kwargs) -> dt.datetime:
        """
        Add a timedelta to a datetime object.

        Args:
            dt_obj (datetime): The datetime object to which the timedelta will be added.
            **kwargs (keyword arguments): The keyword arguments to pass to the timedelta constructor (e.g., days=1, hours=2).

        Raises:
            TypeError: If dt_obj is not a datetime object, or if the keyword arguments are not valid for a timedelta.

        Returns:
            result (datetime): A new datetime object with the added timedelta.
        """
        if dt_obj is None or not isinstance(dt_obj, dt.datetime):
            msg = f"Invalid data type passed DateHelper.add_datetime({dt_obj}). Expected a datetime object."
            raise TypeError(msg)

        try:
            return dt_obj + dt.timedelta(**kwargs)
        except TypeError as e:
            msg = f"Invalid keyword arguments for timedelta in DateHelper.add_datetime(dt_obj={dt_obj}, kwargs={kwargs}): {e}"
            raise TypeError(msg) from e

    @staticmethod
    def add_timezone(dt_obj: dt.datetime, tzinfo: dt.tzinfo | None = None) -> dt.datetime:
        """
        Add timezone information to a datetime object.

        Args:
            dt_obj (datetime): The datetime object to which the timezone information will be added.
            tzinfo (tzinfo): The timezone information to add to the datetime object. Defaults to the local timezone if not provided.

        Raises:
            TypeError: If dt_obj is not a date or datetime object, or if the keyword arguments are not valid for a timedelta.

        Returns:
            result (datetime): A new datetime object with the added timezone information, or None if dt_obj is None or not a datetime object.
        """
        if dt_obj is None or not isinstance(dt_obj, dt.datetime):
            msg = f"Invalid data type passed DateHelper.add_timezone({dt_obj}). Expected a datetime object."
            raise TypeError(msg)
        if tzinfo is None:
            tzinfo = DateHelper.get_local_timezone()
        return dt_obj.replace(tzinfo=tzinfo)

    @staticmethod
    def combine(date_obj: dt.date, time_obj: dt.time, tzinfo: dt.tzinfo | None = None) -> dt.datetime:
        """
        Combine a date object and a time object into a datetime object.

        Args:
            date_obj (date): The date object to combine.
            time_obj (time): The time object to combine.
            tzinfo (tzinfo, optional): The timezone information to add to the combined datetime object. Defaults to the local timezone if not provided.

        Raises:
            TypeError: If date_obj is not a date object, or if time_obj is not a time object.

        Returns:
            result (datetime): A datetime object combining the date and time, with the specified timezone information.
        """
        if date_obj is None or not isinstance(date_obj, dt.date):
            msg = f"Invalid data type for date_obj in DateHelper.combine(date_obj={date_obj}, time_obj={time_obj}): Expected a date object."
            raise TypeError(msg)
        if time_obj is None or not isinstance(time_obj, dt.time):
            msg = f"Invalid data type for time_obj in DateHelper.combine(date_obj={date_obj}, time_obj={time_obj}): Expected a time object."
            raise TypeError(msg)
        if tzinfo is None:
            tzinfo = DateHelper.get_local_timezone()
        return dt.datetime.combine(date_obj, time_obj, tzinfo=tzinfo)

    @staticmethod
    def convert_timezone(dt_obj: dt.datetime, tzinfo: dt.tzinfo | None = None) -> dt.datetime:
        """
        Convert a datetime object to a different timezone.

        Args:
            dt_obj (datetime): The datetime object to convert. Defaults to the local timezone if not provided.
            tzinfo (tzinfo): The timezone to which the datetime object will be converted. Defaults to the local timezone if not provided.

        Raises:
            TypeError: If dt_obj is not a datetime object or if tzinfo is not a tzinfo object.

        Returns:
            result (datetime): A new datetime object representing the same moment in time as dt_obj, but with the specified timezone information.
        """
        if dt_obj is None or not isinstance(dt_obj, dt.datetime):
            msg = f"Invalid data type for dt_obj in DateHelper.convert_timezone(dt_obj={dt_obj}, tzinfo={tzinfo}): Expected a datetime object."
            raise TypeError(msg)
        if tzinfo is None:
            tzinfo = DateHelper.get_local_timezone()
        if dt_obj.tzinfo is None:
            dt_obj = DateHelper.add_timezone(dt_obj, tzinfo=tzinfo)
        if dt_obj.tzinfo == tzinfo:
            return dt_obj

        return dt_obj.astimezone(tz=tzinfo)

    @staticmethod
    def days_between(start_date: dt.date | dt.datetime, end_date: dt.date | dt.datetime) -> int:
        """
        Calculate the number of days between two date or datetime objects.

        Args:
            start_date (date): The start date.
            end_date (date): The end date.

        Raises:
            TypeError: If start_date or end_date is not a date or datetime object.

        Returns:
            difference (int): The number of days between the two dates, or None if either date is None.
        """
        if start_date is None or end_date is None:
            error_msg = f"Invalid input for DateHelper.days_between(start_date={start_date}, end_date={end_date}): Both start_date and end_date must be provided."
            raise TypeError(error_msg)
        if isinstance(start_date, dt.datetime):
            start_date = start_date.date()
        if isinstance(end_date, dt.datetime):
            end_date = end_date.date()
        return (end_date - start_date).days

    @staticmethod
    def extract(dt_str: str, format_str: str | None = None, hide_tz: bool = False, dt_type: type | None = None) -> dt.date | dt.datetime | dt.time:  # noqa: PLR0912, PLR0915
        """
        Extract a date or datetime from a string.

        format_str is optional. If not provided, the function will attempt to parse the string using the 'friendly date, datetime and time formats (see the format() function).
        If format_str is provided, it will be used to parse the string. If format_str is "ISO", the function will attempt to parse the string using the ISO 8601 format.
        If the string cannot be parsed using the provided format_str or the default formats, the function will raise a ValueError.

        Args:
            dt_str (str): The string to extract the date, datetime, or time from.
            format_str (Optional[str], optional): The format string to use for parsing the date, datetime, or time. If None, the function will attempt to parse the string using common date and datetime formats.
            hide_tz (bool, optional): Whether to remove timezone information from the extracted datetime object. Defaults to False.
            dt_type (type, optional): The type of object to extract (dt.date, dt.datetime, or dt.time). If provided, only that type will be attempted. If None, the function will attempt to parse the string as a datetime first, then a date, then a time.

        Raises:
            ValueError: If the string cannot be parsed using the provided format_str or the default formats.

        Returns:
            result (date | datetime | time): A date, datetime or time object extracted from the string.
        """
        return_dt_obj = None
        if format_str is not None:  # noqa: PLR1702
            if format_str.upper() == "ISO":
                # If dt_type is specified, only try parsing as that type
                if dt_type is dt.datetime:
                    try:
                        return_dt_obj = dt.datetime.fromisoformat(dt_str)
                    except ValueError as e:
                        error_msg = f"Could not parse datetime from string '{dt_str}' using ISO format: {e}"
                        raise ValueError(error_msg) from e
                elif dt_type is dt.date:
                    try:
                        return_dt_obj = dt.date.fromisoformat(dt_str)
                    except ValueError as e:
                        error_msg = f"Could not parse date from string '{dt_str}' using ISO format: {e}"
                        raise ValueError(error_msg) from e
                elif dt_type is dt.time:
                    try:
                        return_dt_obj = dt.time.fromisoformat(dt_str)
                    except ValueError as e:
                        error_msg = f"Could not parse time from string '{dt_str}' using ISO format: {e}"
                        raise ValueError(error_msg) from e
                else:
                    # Try parsing as datetime first, then date, then time
                    try:
                        return_dt_obj = dt.datetime.fromisoformat(dt_str)
                    except ValueError:
                        try:
                            return_dt_obj = dt.date.fromisoformat(dt_str)
                        except ValueError:
                            try:
                                return_dt_obj = dt.time.fromisoformat(dt_str)
                            except ValueError as e:
                                error_msg = f"Could not parse date/datetime/time from string '{dt_str}' using ISO format: {e}"
                                raise ValueError(error_msg) from e
            else:
                try:
                    # If dt_type is specified, use it; otherwise classify the format string
                    if dt_type is not None:
                        return_dt_obj = dt.datetime.strptime(dt_str, format_str)  # noqa: DTZ007
                        if dt_type is dt.date:
                            return_dt_obj = return_dt_obj.date()
                        elif dt_type is dt.time:
                            return_dt_obj = return_dt_obj.time()
                        # else dt_type is dt.datetime, keep as is
                    else:
                        format_class = DateHelper._classify_format_str(format_str)
                        return_dt_obj = dt.datetime.strptime(dt_str, format_str)  # noqa: DTZ007
                        if format_class == "date":
                            return_dt_obj = return_dt_obj.date()
                        elif format_class == "time":
                            return_dt_obj = return_dt_obj.time()
                except ValueError as e:
                    error_msg = f"Could not parse date/datetime/time from string '{dt_str}' using format '{format_str}': {e}"
                    raise ValueError(error_msg) from e
        else:  # noqa: PLR5501
            # If dt_type is specified, only try parsing as that type
            if dt_type is dt.datetime:
                with contextlib.suppress(ValueError):
                    return_dt_obj = dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S%z")
                if return_dt_obj is None:
                    with contextlib.suppress(ValueError):
                        return_dt_obj = dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007
            elif dt_type is dt.date:
                with contextlib.suppress(ValueError):
                    return_dt_obj = dt.datetime.strptime(dt_str, "%Y-%m-%d").date()  # noqa: DTZ007
            elif dt_type is dt.time:
                with contextlib.suppress(ValueError):
                    return_dt_obj = dt.datetime.strptime(dt_str, "%H:%M:%S.%f").time()  # noqa: DTZ007
                if return_dt_obj is None:
                    with contextlib.suppress(ValueError):
                        return_dt_obj = dt.datetime.strptime(dt_str, "%H:%M:%S").time()  # noqa: DTZ007
            else:
                # Try parsing as datetime first, then date, then time
                with contextlib.suppress(ValueError):
                    return dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S%z")
                with contextlib.suppress(ValueError):
                    return dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007
                with contextlib.suppress(ValueError):
                    return dt.datetime.strptime(dt_str, "%Y-%m-%d").date()  # noqa: DTZ007
                with contextlib.suppress(ValueError):
                    return dt.datetime.strptime(dt_str, "%H:%M:%S.%f").time()  # noqa: DTZ007
                with contextlib.suppress(ValueError):
                    return dt.datetime.strptime(dt_str, "%H:%M:%S").time()  # noqa: DTZ007

        if return_dt_obj is None:
            type_hint = f" as {dt_type.__name__}" if dt_type else ""
            error_msg = f"Could not parse date/datetime/time from string '{dt_str}'{type_hint} using the default formats."
            raise ValueError(error_msg)

        # If we have a datetime object with timezone info and hide_tz is True, remove the timezone info before returning the datetime object.
        if isinstance(return_dt_obj, dt.datetime):
            if hide_tz and return_dt_obj.tzinfo is not None:
                return_dt_obj = return_dt_obj.replace(tzinfo=None)
            if not hide_tz and return_dt_obj.tzinfo is None:
                local_tz = DateHelper.get_local_timezone()
                return_dt_obj = return_dt_obj.replace(tzinfo=local_tz)

        return return_dt_obj

    @staticmethod
    def extract_date(dt_str: str, format_str: str | None = None, hide_tz: bool = False) -> dt.date:
        """
        Extract a date from a string.

        See extract() for more details.

        Args:
            dt_str (str): The string to extract the date from.
            format_str (Optional[str], optional): The format string to use for parsing the date. Defaults to None, which will attempt to parse using common date formats.
            hide_tz (bool, optional): Whether to remove timezone information from the extracted datetime object. Defaults to False. Only applies if format_str is None or does not specify a date-only format.

        Returns:
            result (date): A date object extracted from the string.
        """
        return DateHelper.extract(dt_str, format_str=format_str, hide_tz=hide_tz, dt_type=dt.date)  # type: ignore[call-arg]

    @staticmethod
    def extract_datetime(dt_str: str, format_str: str | None = None, hide_tz: bool = False) -> dt.datetime:
        """
        Extract a date from a string.

        See extract() for more details.

        Args:
            dt_str (str): The string to extract the datetime from.
            format_str (Optional[str], optional): The format string to use for parsing the datetime. Defaults to None, which will attempt to parse using common datetime formats.
            hide_tz (bool, optional): Whether to remove timezone information from the extracted datetime object. Defaults to False. Only applies if format_str is None or does not specify a datetime-only format.

        Returns:
            result (datetime): A datetime object extracted from the string.
        """
        return DateHelper.extract(dt_str, format_str=format_str, hide_tz=hide_tz, dt_type=dt.datetime)  # type: ignore[call-arg]

    @staticmethod
    def extract_time(dt_str: str, format_str: str | None = None, hide_tz: bool = False) -> dt.time:
        """
        Extract a time from a string.

        See extract() for more details.

        Args:
            dt_str (str): The string to extract the time from.
            format_str (Optional[str], optional): The format string to use for parsing the time. Defaults to None, which will attempt to parse using common time formats.
            hide_tz (bool, optional): Whether to remove timezone information from the extracted time object. Defaults to False. Only applies if format_str is None or does not specify a time-only format.

        Returns:
            result (time): A time object extracted from the string.
        """
        return DateHelper.extract(dt_str, format_str=format_str, hide_tz=hide_tz, dt_type=dt.time)  # type: ignore[call-arg]

    @staticmethod
    def format(dt_obj: dt.date | dt.datetime | dt.time, format_str: str | None = None, hide_tz: bool = True) -> str:
        """
        Format a date object to a string.

        If format_str is None, then dt_obj will use the default format according to it's type:
           date: %Y-%m-%d
           datetime: %Y-%m-%d %H:%M:%S
           time: %H:%M:%S
        The timezone will be included in the datetime string if it's included in dt_obj and hide_tz is False:
           datetime: %Y-%m-%d %H:%M:%S+11:00

        If format_str is "ISO" then the ISO 8601 format will be used.
            date: %Y-%m-%d
            datetime: %Y-%m-%dT%H:%M:%S[TZ]
            time: %H:%M:%S
        The timezone will be included in the datetime string if it's included in dt_obj.

        Args:
            dt_obj (date | datetime | time): The date, datetime, or time object to format.
            format_str (str, optional): The format string to use for formatting the date, datetime, or time.
            hide_tz (bool, optional): Whether to hide the timezone information in the formatted string. Only applies to datetime objects when format_str is None. Defaults to True.

        Raises:
            ValueError: If dt_obj is None or if format_str is not a valid format string for the type of dt_obj.

        Returns:
            formatted_str: The datetime object formatted as a string, or None if dt_obj is None or an unsupported type.
        """
        if dt_obj is None or not isinstance(dt_obj, (dt.date, dt.datetime, dt.time)):
            error_msg = f"Invalid input for DateHelper.format(dt_obj={dt_obj}, format_str={format_str}): dt_obj must be provided and be a valid type."
            raise ValueError(error_msg)
        if format_str is None:
            if isinstance(dt_obj, dt.datetime):
                if dt_obj.tzinfo is not None and not hide_tz:
                    format_str = "%Y-%m-%d %H:%M:%S%:z"
                else:
                    format_str = "%Y-%m-%d %H:%M:%S"
            elif isinstance(dt_obj, dt.date):
                format_str = "%Y-%m-%d"
            elif isinstance(dt_obj, dt.time):
                format_str = "%H:%M:%S"

        elif format_str.upper() == "ISO":
            # Use .isoformat() instead of strftime for ISO format to ensure correct formatting of timezone-aware datetimes
            return dt_obj.isoformat()

        try:
            return dt_obj.strftime(format_str)
        except ValueError as e:
            error_msg = f"Invalid format string for DateHelper.format(dt_obj={dt_obj}, format_str={format_str}): {e}"
            raise ValueError(error_msg) from e

    @staticmethod
    def get_file_date(file_path: str | Path) -> dt.date | None:
        """
        Get the last modified date of a file.

        Args:
            file_path (str | Path): Path to the file. Can be a string or a Path object.

        Returns:
            date_obj (date): The last modified date of the file as a date object, or None if the file does not exist.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            return None

        local_tz = DateHelper.get_local_timezone()
        return dt.datetime.fromtimestamp(file_path.stat().st_mtime, tz=local_tz).date()

    @staticmethod
    def get_file_datetime(file_path: str | Path) -> dt.datetime | None:
        """
        Get the last modified datetime of a file.

        Args:
            file_path (str | Path): Path to the file. Can be a string or a Path object.

        Returns:
            datetime_obj (datetime): The last modified datetime of the file as a date object, or None if the file does not exist.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            return None

        local_tz = DateHelper.get_local_timezone()
        return dt.datetime.fromtimestamp(file_path.stat().st_mtime, tz=local_tz)

    @staticmethod
    def get_local_timezone() -> dt.tzinfo:
        """
        Get the local timezone of the system.

        Returns:
            tzinfo (tzinfo): The local timezone of the system.
        """
        local_tz = dt.datetime.now().astimezone().tzinfo    # Issue 1
        return local_tz  # pyright: ignore[reportReturnType]

    @staticmethod
    def is_valid_date(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
        """
        Check if a date or datetime string is valid according to the specified format.

        If format_str is "ISO", the function will attempt to parse the string using the ISO 8601 format.

        Args:
            date_str (str): The date string to check.
            format_str (Optional[str], optional): The format string to use for checking the date. Defaults to "%Y-%m-%d".

        Returns:
            result (bool): True if the date string is valid, False otherwise.
        """
        local_tz = DateHelper.get_local_timezone()
        try:
            if format_str.upper() == "ISO":
                dt.datetime.fromisoformat(date_str)
            else:
                dt.datetime.strptime(date_str, format_str).replace(tzinfo=local_tz)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def is_valid_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> bool:
        """
        Check if a date or datetime string is valid according to the specified format.

        If format_str is "ISO", the function will attempt to parse the string using the ISO 8601 format.

        Args:
            dt_str (str): The datetime string to check.
            format_str (Optional[str], optional): The format string to use for checking the datetime. Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            result (bool): True if the datetime string is valid, False otherwise.
        """
        local_tz = DateHelper.get_local_timezone()
        try:
            if format_str.upper() == "ISO":
                dt.datetime.fromisoformat(dt_str)
            else:
                dt.datetime.strptime(dt_str, format_str).replace(tzinfo=local_tz)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def is_valid_time(time_str: str, format_str: str = "%H:%M:%S") -> bool:
        """
        Check if a time string is valid according to the specified format.

        If format_str is "ISO", the function will attempt to parse the string using the ISO 8601 format.

        Args:
            time_str (str): The time string to check.
            format_str (Optional[str], optional): The format string to use for checking the time. Defaults to "%H:%M:%S".

        Returns:
            result (bool): True if the time string is valid, False otherwise.
        """
        local_tz = DateHelper.get_local_timezone()
        try:
            if format_str.upper() == "ISO":
                dt.datetime.fromisoformat(time_str)
            else:
                dt.datetime.strptime(time_str, format_str).replace(tzinfo=local_tz)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def midnight(dt_date: dt.date | None = None, tzinfo: dt.tzinfo | None = None) -> dt.datetime:
        """
        Get today's date at midnight.

        Args:
            dt_date (date, optional): The date for which to get midnight. If None, today's date will be used.
            tzinfo (tzinfo, optional): The timezone information to use for getting today's date at midnight. Defaults to the local timezone if not provided.

        Returns:
            result (datetime): Today's date at midnight as a datetime object, using the local timezone.
        """
        if tzinfo is None:
            tzinfo = DateHelper.get_local_timezone()
        if dt_date is None:
            dt_date = DateHelper.today(tzinfo=tzinfo)
        return DateHelper.combine(dt_date, dt.time(0, 0, 0), tzinfo=tzinfo)

    @staticmethod
    def now(tzinfo: dt.tzinfo | None = None) -> dt.datetime:
        """
        Get today's date and time.

        Args:
            tzinfo (tzinfo, optional): The timezone information to use for getting the current datetime. Defaults to the local timezone if not provided.

        Returns:
            result (datetime): Today's date and time as a date object, using the local timezone.
        """
        if tzinfo is None:
            tzinfo = DateHelper.get_local_timezone()

        freeze_time = DateHelper._get_frozen_time()
        if freeze_time is not None:
            return freeze_time
        return dt.datetime.now(tz=tzinfo)

    @staticmethod
    def now_str(format_str: str | None = "%Y-%m-%d %H:%M:%S", tzinfo: dt.tzinfo | None = None) -> str:
        """
        Get the current time in string format.

        If format_str is "ISO" then the ISO 8601 format will be used.

        Args:
            format_str (Optional[str], optional): The format string to use for formatting the datetime.
            tzinfo (tzinfo, optional): The timezone information to use for getting the current datetime. Defaults to the local timezone if not provided.

        Returns:
            result (str): Current time as a formatted string, using the specified datetime format.
        """
        return DateHelper.format(DateHelper.now(tzinfo=tzinfo), format_str)  # type: ignore[call-arg]

    @staticmethod
    def now_utc() -> dt.datetime:
        """
        Get today's date and time in UTC.

        Returns:
            result (datetime): Today's date and time as a date object, using UTC timezone.

        Returns:
            result (datetime): Today's date and time as a date object, using the local timezone.
        """
        return DateHelper.now(tzinfo=dt.UTC)

    @staticmethod
    def today(tzinfo: dt.tzinfo | None = None) -> dt.date:
        """
        Get today's date.

        Args:
            tzinfo (tzinfo, optional): The timezone information to use for getting today's date. Defaults to the local timezone if not provided.

        Returns:
            result (date): Today's date as a date object, using the local timezone.
        """
        if tzinfo is None:
            tzinfo = DateHelper.get_local_timezone()
        return DateHelper.now(tzinfo=tzinfo).date()

    @staticmethod
    def today_add_days(days: int, tzinfo: dt.tzinfo | None = None) -> dt.date:
        """
        Get today's date ofset by days.

        Args:
            days (int): The number of days to offset from today. Can be positive or negative
            tzinfo (tzinfo, optional): The timezone information to use for getting today's date. Defaults to the local timezone if not provided.

        Returns:
            result (date): Today's date offset by the specified number of days.
        """
        return DateHelper.add(DateHelper.today(tzinfo=tzinfo), days=days)  # type: ignore[call-arg]

    @staticmethod
    def today_str(format_str: str | None = "%Y-%m-%d") -> str:
        """
        Get today's date in string format.

        If format_str is "ISO" then the ISO 8601 format will be used.

        Args:
            format_str (Optional[str], optional): The format string to use for formatting the date.

        Returns:
            result (str): Today's date as a formatted string, using the specified date format.
        """
        return DateHelper.format(DateHelper.today(), format_str)  # type: ignore[call-arg]

    @staticmethod
    def today_utc() -> dt.date:
        """
        Get today's date in UTC.

        Returns:
            result (date): Today's date as a date object, using UTC timezone.

        Returns:
            result (datetime): Today's date and time as a date object, using the local timezone.
        """
        return DateHelper.today(tzinfo=dt.UTC)

    @staticmethod
    def remove_timezone(dt_obj: dt.datetime) -> dt.datetime:
        """
        Remove timezone information from a datetime object.

        Args:
            dt_obj (datetime): The datetime object from which the timezone information will be removed.

        Raises:
            TypeError: If dt_obj is not a date or datetime object.

        Returns:
            result (datetime): A new datetime object with the timezone information removed.
        """
        if dt_obj is None or not isinstance(dt_obj, dt.datetime):
            msg = f"Invalid data type passed DateHelper.remove_timezone({dt_obj}). Expected a datetime object."
            raise TypeError(msg)
        return dt_obj.replace(tzinfo=None)

    @staticmethod
    def get_dawn_dusk_times(latitude: float, longitude: float, timezone: str | None = None, as_at: dt.date | None = None) -> dict:
        """Get the dawn and dusk times based on the location returned from the configured location configuration.

        The returned dict contains:
            - as_date (date): The date for which the times are calculated.
            - timezone (str): The timezone of the location.
            - latitude (float): The latitude of the location.
            - longitude (float): The longitude of the location.
            - dawn (datetime): The dawn time.
            - sunrise (datetime): The sunrise time.
            - noon (datetime): The noon time.
            - sunset (datetime): The sunset time.
            - dusk (datetime): The dusk time.

        Args:
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.
            timezone (str, optional): The timezone of the location. If not provided, the timezone will be determined based on the latitude and longitude.
            as_at (date, optional): The date for which to get the dawn and dusk times. Defaults to today.

        Returns:
            result (dict): A dictionary containing the following key described above.
        """
        name = "sc_foundation DateHelper"
        if timezone is None:
            tz_name = get_tz(longitude, latitude)
            timezone = tz_name or str(dt.datetime.now().astimezone().tzinfo)

        if as_at is None:
            as_at = DateHelper.today(tzinfo=pytz.timezone(timezone))

        # Create location object and compute times
        location = LocationInfo(name=name, region="", timezone=timezone, latitude=latitude, longitude=longitude)
        s = sun(location.observer, date=as_at, tzinfo=pytz.timezone(timezone))

        return_data = {
            "as_date": as_at,
            "timezone": timezone,
            "latitude": latitude,
            "longitude": longitude,
            "dawn": s["dawn"],
            "sunrise": s["sunrise"],
            "noon": s["noon"],
            "sunset": s["sunset"],
            "dusk": s["dusk"],
        }
        return return_data

    # ==================================== INTERNAL FUNCTIONS ====================================

    @staticmethod
    def _get_frozen_time() -> dt.datetime | None:  # noqa: PLR0915
        """
        See if we need to return a frozen time for testing purposes.

        If a frozen time is set, it will be returned instead of the current time. See the documentation for the freeze time feature for more details.

        Returns:
            result (datetime): The datetime to use instead of the current time, or None if no freeze time is configured.
        """
        freeze_time_file = DateHelper._find_freeze_time_file()
        if freeze_time_file is None:
            return None

        try:
            with freeze_time_file.open("r") as f:
                config = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

        # Handle freeze_time (takes priority over offset_time)
        freeze_time_str = config.get("freeze_time")
        if freeze_time_str:
            try:
                # Parse the freeze_time datetime (ISO format, timezone optional)
                frozen_dt = dt.datetime.fromisoformat(freeze_time_str)

                # Add local timezone if missing
                if frozen_dt.tzinfo is None:
                    frozen_dt = frozen_dt.replace(tzinfo=DateHelper.get_local_timezone())

                # Handle one_time feature
                one_time = config.get("one_time", False)
                if one_time:
                    # Calculate offset from current time to frozen time
                    actual_now = dt.datetime.now(tz=DateHelper.get_local_timezone())
                    time_diff = frozen_dt - actual_now

                    # Convert to the largest appropriate unit
                    total_seconds = time_diff.total_seconds()

                    # Determine the best unit and amount
                    if abs(total_seconds) >= 86400:  # days
                        offset_amount = total_seconds / 86400
                        offset_unit = "days"
                    elif abs(total_seconds) >= 3600:  # hours
                        offset_amount = total_seconds / 3600
                        offset_unit = "hours"
                    elif abs(total_seconds) >= 60:  # minutes
                        offset_amount = total_seconds / 60
                        offset_unit = "minutes"
                    else:  # seconds
                        offset_amount = total_seconds
                        offset_unit = "seconds"

                    # Update the config: remove freeze_time, add offset_time
                    config["freeze_time"] = None
                    config["one_time"] = False
                    config["offset_time_unit"] = offset_unit
                    config["offset_time_amount"] = offset_amount

                    # Write back to file
                    try:
                        with freeze_time_file.open("w") as f:
                            json.dump(config, f, indent=4)
                    except OSError:
                        pass  # If we can't write, just continue
            except (ValueError, TypeError):
                pass  # Invalid datetime format, fall through to offset_time
            else:
                return frozen_dt

        # Handle offset_time
        offset_unit = config.get("offset_time_unit")
        offset_amount = config.get("offset_time_amount")

        if offset_unit and offset_amount is not None:
            try:
                # Create timedelta with the specified unit and amount
                kwargs = {offset_unit: offset_amount}
                offset = dt.timedelta(**kwargs)

                actual_now = dt.datetime.now(tz=DateHelper.get_local_timezone())
                return actual_now + offset
            except (TypeError, ValueError):
                pass  # Invalid offset parameters

        return None

    @staticmethod
    def _find_freeze_time_file() -> Path | None:
        """
        Look for a file named "freeze_time.json" in the current working directory, project root folder or the logs folder.

        Returns:
            result (Path | None): The path to the "freeze_time.json" file if found, otherwise None.
        """
        current_dir = Path.cwd()
        project_root = SCCommon.get_project_root()
        logs_dir = project_root / "logs"
        for folder in [current_dir, project_root, logs_dir]:
            freeze_time_file = folder / "freeze_time.json"
            if freeze_time_file.exists():
                return freeze_time_file
        return None

    @staticmethod
    def _classify_format_str(format_str: str) -> str:
        """
        Classify the format string as "date", "datetime", or "time" based on its content.

        Args:
            format_str (str | None): The format string to classify.

        Returns:
            result (str): The classification of the format string ("date", "datetime", or "time").
        """
        date_format_tokens = ["%Y", "%y", "%B", "%m", "%A", "%a", "%d", "%j"]
        time_format_tokens = ["%H", "%I", "%p", "%M", "%S", "%f", "%z", "%Z"]
        if format_str is None:
            return "datetime"
        if any(x in format_str for x in date_format_tokens):
            if any(x in format_str for x in time_format_tokens):
                return "datetime"
            return "date"
        if any(x in format_str for x in time_format_tokens):
            return "time"
        return "datetime"
