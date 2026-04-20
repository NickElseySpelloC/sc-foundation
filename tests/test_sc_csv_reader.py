import datetime as dt
import sys

from sc_foundation import CSVReader

CSV_FILE = "tests/test_csv.csv"
NEW_CSV_FILE = "tests/test_csv_new.csv"

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
        "minimum": dt.date(2025, 7, 8),
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
]

extra_data = [
    {
        "Symbol": "AAPL",
        "Date": dt.date(2023, 10, 1),
        "Name": "Apple Inc.",
        "Currency": "USD",
        "Price": 150.00,
    },
    {
        "Symbol": "AAPL",
        "Date": dt.date(2023, 11, 1),
        "Name": "Apple Inc.",
        "Currency": "USD",
        "Price": 155.00,
    },
]


def sum_list_values(data: list[dict]) -> float:
    """
    Helper function to sum values in a list of dict.

    Args:
        data (dict): The data to sum values from.

    Returns:
        float: The sum of all the Price keys in the list.
    """
    sum_value = 0
    for row in data:
        sum_value += row.get("Price", 0.0)
    return sum_value


def test_read_csv():
    """Test the CSVReader class reading from a CSV file."""
    # Create an instance of the CSVReader class
    try:
        csv_reader = CSVReader(CSV_FILE, header_config)
        csv_data = csv_reader.read_csv()
    except (ImportError, TypeError, ValueError) as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    else:
        assert isinstance(csv_data, list), "CSV data should be a list"
        assert len(csv_data) > 0, "CSV data should not be empty"
        assert sum_list_values(csv_data) > 147, "Sum of values in the sheet should be greater than 147"


def test_sort_csv_data():
    try:
        csv_reader = CSVReader(CSV_FILE, header_config)
        csv_data = csv_reader.read_csv()
        if not csv_data:
            print("CSV data is empty, cannot sort data.")
            sys.exit(1)
        csv_data = csv_reader.sort_csv_data(csv_data)
    except (ImportError, TypeError, ValueError) as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    else:
        assert isinstance(csv_data, list), "CSV data should be a list"
        assert len(csv_data) > 0, "CSV data should not be empty"
        sum_value = round(sum_list_values(csv_data), 0)
        assert sum_value == 771, "Sum of values in the sheet should be 771"


def test_merge_data_sets():
    try:
        csv_reader = CSVReader(CSV_FILE, header_config)
        csv_data = csv_reader.read_csv()
        if not csv_data:
            print("CSV data is empty, cannot merge with extra data.")
            sys.exit(1)
        csv_data = csv_reader.merge_data_sets(csv_data, extra_data)
    except (ImportError, TypeError, ValueError) as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    else:
        assert isinstance(csv_data, list), "CSV data should be a list"
        assert len(csv_data) > 0, "CSV data should not be empty"
        sum_value = round(sum_list_values(csv_data), 0)
        assert sum_value == 1076, "Sum of values in the sheet should be 1076"


def test_trim_csv_data():
    try:
        csv_reader = CSVReader(CSV_FILE, header_config)
        csv_data = csv_reader.read_csv()

        if not csv_data:
            print("CSV data is empty, cannot trim data.")
            sys.exit(1)
        csv_data = csv_reader.trim_csv_data(csv_data)
    except (ImportError, TypeError, ValueError) as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    else:
        assert isinstance(csv_data, list), "CSV data should be a list"
        assert len(csv_data) == 3, "CSV data should have 3 rows after trimming"
        sum_value = round(sum_list_values(csv_data), 0)
        assert sum_value == 145, "Sum of values in the sheet should be 145"


def test_write_csv():
    try:
        csv_reader = CSVReader(CSV_FILE, header_config)
        csv_data = csv_reader.read_csv()
        if not csv_data:
            print("CSV data is empty, cannot write data.")
            sys.exit(1)
        csv_data = csv_reader.merge_data_sets(csv_data, extra_data)
        csv_data = csv_reader.trim_csv_data(csv_data)
        result = csv_reader.write_csv(csv_data, NEW_CSV_FILE)
    except (ImportError, TypeError, ValueError) as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    else:
        assert result, "write_csv() shoudl return True"


# test_trim_csv_data()
