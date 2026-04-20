# CSV Reader

CSVReader class for extracting data from CSV and updating files. 


The **header_config** argument to \__init__() is a list of dict objects that defines the expected structure of the CSV file. Each dict object in the list should have the following keys:

- **name**: The name of the column.
- **type**: The type of the column, which can be 'str', 'int', 'float', 'date', 'datetime' or 'time'.
- **format** (optional): A string that defines the format for date, datetime, time or float types (e.g., "%Y-%m-%d" for date or ".2f" for float).
- **match** (optional): A boolean indicating if this column should be used for matching records in the merge_data_sets() function.
- **sort** (optional): An integer indicating the sort order of the column.
- **minimum** (optional): A date, datetime or int that defines a minimum value for filtering by date or datetime.

For example, consider this CSV file:

    Symbol,Date,Name,Currency,Price
    ACM0006AU,2025-04-28,AB Managed Volatility Equities,AUD,1.82
    CSA0038AU,2025-04-28,Bentham Global Income,AUD,1.00
    ETL0018AU,2025-04-28,PIMCO Global Bond Wholesale,AUD,0.90

The header configuration might look like this:

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
            "minimum": None,
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



::: sc_foundation.sc_csv_reader.CSVReader