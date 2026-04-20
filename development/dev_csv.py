"""Manual testing code for the sc-foundation libraries. Should not be included in the distrbution."""

import datetime as dt
import sys

from sc_foundation import CSVReader, DateHelper

csv_file_name = "development/dev_csv.csv"

header_config = [
    {
        "name": "Symbol",
        "type": "str",
        "match": True,
        "sort": 2,
    },
    {
        "name": "Date",
        "type": "date",
        "format": "%Y-%m-%d",
        "match": True,
        "sort": 1,
        # "minimum": 30,
    },
    {
        "name": "Timestamp",
        "type": "datetime",
        "format": "%Y-%m-%d %H:%M:%S",
        "match": True,
        "sort": 1,
        "minimum": 30,
    },
    {
        "name": "Name",
        "type": "str",
    },
    {
        "name": "Currency",
        "type": "str",
    },
    {
        "name": "Price",
        "type": "float",
        "format": ".2f",
    },
    {
        "name": "Time",
        "type": "time",
        "format": "%H:%M",
    },
    {
        "name": "IsValid",
        "type": "bool",
    },
]


def main():
    extra_data = [
        {
            "Symbol": "AAPL",
            "Date": DateHelper.today(),
            "Timestamp": DateHelper.now(),
            "Name": "Apple Inc.",
            "Currency": "USD",
            "Price": 150.00,
            "Time": dt.time(9, 45),
            "IsValid": True,
        },
        ]

    # Create an instance of the CSVReader class
    try:
        csv_reader = CSVReader(csv_file_name, header_config)
    except (ImportError, TypeError, ValueError) as e:
        print(e, file=sys.stderr)
        return

    csv_reader.update_csv_file(extra_data, max_days=10)


if __name__ == "__main__":
    main()
