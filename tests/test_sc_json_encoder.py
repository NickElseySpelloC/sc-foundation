from enum import StrEnum
from pathlib import Path

from sc_foundation import DateHelper, JSONEncoder

JSON_FILE = "tests/test_json.json"


class APIMode(StrEnum):
    LIVE = "Live Prices"
    OFFLINE = "Offline Cache"
    DISABLED = "Pricing Disabled"


data_obj = {
    "string": "Hello, World!",
    "integer": 42,
    "float": 123.456,
    "datetime": DateHelper.now(),
    "date": DateHelper.today(),
    "api_mode": APIMode.LIVE,
}


def test_write_json():
    """Test the JSONEncoder class writing to and reading from a JSON file."""
    # Save the to a JSON file
    file_path = Path(JSON_FILE)
    result = JSONEncoder.save_to_file(data_obj, file_path)
    assert result is True, "Failed to save data to JSON file"


def test_read_json():
    """Test the JSONEncoder class reading from a JSON file."""
    file_path = Path(JSON_FILE)
    loaded_data = JSONEncoder.read_from_file(file_path)
    assert isinstance(loaded_data, dict), "Loaded data should be a dictionary"
    assert loaded_data.get("string") == data_obj.get("string"), "String value mismatch"
    assert loaded_data.get("integer") == data_obj.get("integer"), "Integer value mismatch"
    assert loaded_data.get("float") == data_obj.get("float"), "Float value mismatch"
    assert loaded_data.get("datetime") == data_obj.get("datetime"), "Datetime value mismatch"
    assert loaded_data.get("date") == data_obj.get("date"), "Date value mismatch"
    assert loaded_data.get("api_mode") == data_obj.get("api_mode"), "API mode value mismatch"
