"""Manual testing code for the sc_foundation libraries. Should not be included in the distrbution."""

import platform
from enum import StrEnum
from pathlib import Path

from sc_foundation import (
    DateHelper,
    JSONEncoder,
)

CONFIG_FILE = "development/dev_config.yaml"
JSON_FILE = "development/dev_data.json"


class APIMode(StrEnum):
    LIVE = "Live Prices"
    OFFLINE = "Offline Cache"
    DISABLED = "Pricing Disabled"


def test_json_encoder():
    # Create an object with various data types
    data_obj = {
        "DaysOfWeek": "Sat,Sun,Tue",
        "string": "Hello, World!",
        "integer": 42,
        "float": 123.456,
        "datetime": DateHelper.now(),
        "date": DateHelper.today(),
        "api_mode": APIMode.LIVE,
    }

    print(f"Original Data Object:\n{data_obj}\n")

    # Make a JSON ready version of the object
    json_ready_data_obj = JSONEncoder.ready_dict_for_json(data_obj)
    print(f"JSON Ready Data Object:\n{json_ready_data_obj}\n")

    # Make a JSON string from the object
    json_string = JSONEncoder.serialise_to_json(data_obj)
    print(f"JSON String:\n{json_string}\n")

    # Save the to a JSON file
    file_path = Path(JSON_FILE)
    JSONEncoder.save_to_file(data_obj, file_path)
    print(f"Data saved to {file_path.resolve()}\n")

    # Read the JSON file back
    loaded_data = JSONEncoder.read_from_file(file_path)
    print(f"Loaded Data Object:\n{loaded_data}\n")


def main():
    """Main function to run the example code."""
    print(f"Hello from sc-foundation running on {platform.system()}")

    test_json_encoder()


if __name__ == "__main__":
    main()
