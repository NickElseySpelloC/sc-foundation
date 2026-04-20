# Date Helper

::: sc_foundation.sc_date_helper.DateHelper

## Freeze time feature

The DateHelper functions that return the current system date or time - now(), now_str(), today(), today_add_days(), etc. - support a "freeze time feature". This allows the system date and time lookup to be modified in one of three ways:

1. Freeze the time forever at a specific date and time.
2. Set the time to a designated datetime once, and then run the clock forward for every subsequent call.
3. Offset the current system date & time (positive or negative) by a set amount, for example +3 hours, -2 days, etc.

You can control this behaviour by creating a JSON file called freeze_time.json in one of the following locations:

1. The current working directory
2. The project root directory
3. The [Project Root]/logs/ directory (if it exists)

The file must be structured as per the examples below. 

* Look for a freeze_time.json file in the project root folder.
* If freeze_time = valid datetime and one_time = false, then every call to now() will return the same datetime
* If freeze_time = valid datetime and one_time = true, then the first call to now() will return the specified datetime and each subsequent call will tick forward according to the normal clock.
* If offset_time_unit and offset_time_amount are set, then use timedelta to adjust the time. 


### Example 1: Freeze the time forever at a specific date and time:
```json
{
    "freeze_time": "2026-02-21T12:34:56",
    "one_time": false
}
```
The freeze_time key must be an [ISO 8601 string ](https://www.learnbyexample.org/working-with-iso-8601-in-python) and timezones are supported (e.g. "2026-04-01T12:34:56.789012+11:00"). If no timezone is supplied, the local timezone is assumed. 

### Example 2: Set the time to a designated datetime once, and then run the clock forward for every subsequent call.
```json
{
    "freeze_time": "2026-02-21T12:34:56Z",
    "one_time": true
}
```

To accomplish this, DateHelper will rewrite the file to the example 3 format below after the first call for a system datetime.

### Example 3: Offset the current system date & time by a set amount
```json
{
    "offset_time_unit": "hours",
    "offset_time_amount": 3,
}
```

The offset_time_unit can be any time interval type supported by [timedelta](https://docs.python.org/3/library/datetime.html#datetime.timedelta). The offset_time_amount can be a positive or negative decimal or whole number.

### Other points to note

* The freeze_time.json file must be writable. 
* If freeze_time and offset_time_amount are both set, freeze_time wins.
* All other date, datetime, time related functions in this library that get the system time will also honor the freeze time functionality.
