"""CSVReader class for extracting data from CSV files."""
import csv
import datetime as dt
import operator
from pathlib import Path

from sc_foundation.sc_date_helper import DateHelper


class CSVReader:
    """Class for reading and writing CSV files with header configuration."""
    def __init__(self, file_path: Path | str, header_config: list[dict] | None = None):
        """Initialize the CSVReader with the file path.

        Args:
            file_path (Path | str): The path to the CSV file. If the file does not exist, it won't be created.
            header_config (Optional(list[dict]), optional): The header configuration for the CSV file.

        Raises:
            TypeError: If header_config is not structured correctly.
            ImportError: If the file not exists but doesn't have a valid extension.
        """
        # If it's a string, convert to Path
        if isinstance(file_path, str):
            file_path = Path(file_path)

        self.file_exists = False
        self.file_path = file_path
        if header_config is None:
            self.header_config = []
        else:
            self.header_config = header_config
            error_msg = self._validate_header()
            if error_msg:
                raise TypeError(error_msg)

        # Check if the file exists
        if self.file_path.is_file():
            # Check extension to see if it's an Excel file
            if self.file_path.suffix.lower() in {".csv", ".txt"}:
                self.file_exists = True
            else:
                msg = f"File {self.file_path} is not a valid Excel file."
                raise ImportError(msg)

    def _validate_header(self) -> str:  # noqa: PLR0911, PLR0912
        """Validate the header configuration has the allowed structure.

            If header_config has been supplied, validate it:
            1. Make sure it's a list of dictionaries.
            2. Ensure each header is a dictionary with 'name' and 'type' keys.
            3. 'type' can be 'str', 'int', 'float', 'date', 'datetime', 'time' or 'bool'.
            4. If 'date', 'datetime' or 'time', it can have an optional 'format' key.
            5. The only allowed attributes in the header dictionaries are 'name', 'type', 'format', 'match' and 'sort'

        Returns:
            str: An error message if the header configuration is invalid, otherwise an empty string.
        """
        if not self.header_config:
            return ""

        if not isinstance(self.header_config, list):
            return "header_config must be a list of dictionaries."

        allowed_keys = {"name", "type", "format", "match", "sort", "minimum"}
        allowed_types = {"str", "int", "float", "date", "datetime", "time", "bool"}

        for header in self.header_config:
            if not isinstance(header, dict):
                return "Each header in header_config must be a dictionary."
            # If keys are not one of the allowed keys, return an error
            if not set(header.keys()).issubset(allowed_keys):
                return f"Invalid keys in header configuration. Allowed keys are: {', '.join(allowed_keys)}."
            if "name" not in header or "type" not in header:
                return "Each header must have 'name' and 'type' keys."
            if header["type"] not in allowed_types:
                return f"Invalid type '{header['type']}' in header configuration. Allowed types are: {', '.join(allowed_types)}."

        # If 'format' is provided, it must be a string
        for header in self.header_config:
            if "format" in header and not isinstance(header["format"], str):
                return "If 'format' is provided, it must be a string."

        # If 'sort' is provided, it must be an int
        for header in self.header_config:
            if "sort" in header and not isinstance(header["sort"], int):
                return "If 'sort' is provided, it must be an int."

        # If 'match' is provided, it must be a boolean
        for header in self.header_config:
            if "match" in header and not isinstance(header["match"], bool):
                return "If 'match' is provided, it must be a boolean."

        # If 'minimum' is provided, it must be a date or an int or None
        # and the type must be Date or Datetime
        for header in self.header_config:
            if "minimum" in header and not (isinstance(header["minimum"], (int, dt.date)) or header["minimum"] is None):
                return "If 'minimum' is provided, it must be a date, and int or None."
            if "minimum" in header and header["type"] != "date" and header["type"] != "datetime":
                return "If 'minimum' is provided, the type must be 'date' or 'datetime'."

        return ""

    def read_csv(self) -> list[dict] | None:  # noqa: PLR0912
        """Read the CSV file and return its content.

        If the file does not exist, return None. If the file has a header but no data, returns an empty list.

        Raises:
            ImportError: If the CSV file is empty or has no header.
            ValueError: A value read from the CSV file cannot be converted to the expected type as defined in header_config.

        Returns:
            data (list[dict]): A list of rows from the CSV file or None if the file does not exist.
        """
        # Return None if the file does not exist
        if not self.file_exists:
            return None

        # Read the CSV file
        csv_data = []
        with self.file_path.open(newline="", encoding="utf-8") as csvfile:  # noqa: PLR1702
            reader = csv.reader(csvfile)

            # Read the header
            file_headers = next(reader, None)
            if file_headers is None:
                error_msg = f"CSV file {self.file_path} is empty or has no header."
                raise ImportError(error_msg)

            # Validate the header against the provided configuration:
            # 1. All the header names in self.header_config must exist in file_headers, but not necessarily in the same order.
            # 2. If additional headers are present in the CSV file that are not in self.header_config, add them to file_headers with a type of 'str'.
            header_names = []
            if self.header_config:
                # Check if all headers in header_config are in file_headers
                header_names = [header["name"] for header in self.header_config]
                missing_headers = [
                    header for header in header_names if header not in file_headers
                ]
                if missing_headers:
                    error_msg = f"CSV file {self.file_path} is missing headers: {', '.join(missing_headers)}."
                    raise ImportError(error_msg)

            # Add any additional headers from the CSV file that are not in header_config
            additional_headers = [
                header for header in file_headers if header not in header_names
            ]
            for additional_header in additional_headers:
                self.header_config.append(
                    {"name": additional_header, "type": "str"}
                )

            # Reorder self.header_config to match the headers in the CSV file
            if file_headers is not None:
                self.header_config.sort(key=lambda x: file_headers.index(x["name"]))  # type: ignore[call-arg]

            # Read the data rows from the CSV file
            for row in reader:
                if row:
                    # Convert the row to a dictionary using the self.header_config to convert the data types
                    row_dict = {}
                    for i, header in enumerate(file_headers):
                        if i < len(self.header_config):
                            try:
                                config = self.header_config[i]
                                if config["type"] == "date":
                                    # Convert date strings to time objects
                                    date_format = config.get("format", "%Y-%m-%d")
                                    row_dict[header] = DateHelper.extract(row[i], date_format)
                                elif config["type"] == "datetime":
                                    # Convert datetime strings to datetime objects
                                    datetime_format = config.get("format", "%Y-%m-%d %H:%M:%S")
                                    row_dict[header] = DateHelper.extract(row[i], datetime_format)
                                elif config["type"] == "time":
                                    # Convert time strings to time objects
                                    time_format = config.get("format", "%H:%M:%S")
                                    row_dict[header] = DateHelper.extract(row[i], time_format)
                                elif config["type"] == "float":
                                    # Convert float strings to float and round if specified
                                    row_dict[header] = float(row[i])
                                    if "format" in config:
                                        row_dict[header] = float(format(row_dict[header], config["format"]))
                                elif config["type"] == "int":
                                    # Convert Int strings to int
                                    row_dict[header] = int(row[i])
                                elif config["type"] == "bool":
                                    # Convert Boolean strings to bool
                                    row_dict[header] = row[i].lower() in {"true", "1", "yes"}
                                else:
                                    # Default to string type
                                    row_dict[header] = row[i]
                            except (ValueError, TypeError) as e:
                                error_msg = (
                                    f"Value '{row[i]}' in row {reader.line_num} cannot be converted to the expected type "
                                    f"for column '{header}'."
                                )
                                raise ValueError(error_msg) from e
                        else:
                            # default to string type for additional headers
                            row_dict[header] = row[i]

                    csv_data.append(row_dict)

            return csv_data

    def sort_csv_data(self, csv_data: list[dict]) -> list[dict]:
        """Sort the CSV data based on the header configuration.

        Args:
            csv_data (list[dict]): The data read from the CSV file.

        Returns:
            list[dict]: The sorted data.
        """
        if not self.header_config:
            return csv_data

        # Get headers that have a 'sort' key and sort them by sort order
        sort_headers = [
            header for header in self.header_config
            if "sort" in header
        ]

        # If no sort headers, return original data
        if not sort_headers:
            return csv_data

        # Sort the headers by their sort value (ascending order)
        sort_headers.sort(key=operator.itemgetter("sort"))

        # Sort the data by each sort header in order
        sorted_data = sorted(
            csv_data,
            key=lambda row: tuple(row[header["name"]] for header in sort_headers)
        )

        return sorted_data

    def merge_data_sets(self, primary_list: list[dict], append_list: list[dict]) -> list[dict]:
        """Merges two lists of dictionaries based on header configuration match fields and sorts the result.

        Args:
            primary_list (list[dict]): The primary list of dictionaries.
            append_list (list[dict]): The list of dictionaries to append or override.

        Raises:
            ValueError: If the dictionaries in the lists do not have the same structure.

        Returns:
            list[dict]: The merged and sorted list of dictionaries.
        """
        # Validate inputs
        if not primary_list and not append_list:
            return []

        def validate_structure(ref_list: list[dict], other_list: list[dict]):
            if not ref_list or not other_list:
                return
            ref_keys = set(ref_list[0].keys())
            for item in other_list:
                if set(item.keys()) != ref_keys:
                    error_msg = "Dictionaries in both lists must have the same structure."
                    raise ValueError(error_msg)

        try:
            validate_structure(primary_list, append_list)
            validate_structure(append_list, primary_list)
        except ValueError as e:
            raise ValueError(e) from e

        # Get match fields from header_config
        match_fields = [
            header["name"] for header in self.header_config
            if header.get("match", False) is True
        ]

        # If no match fields, simply append
        if not match_fields:
            merged = primary_list + append_list
        else:
            def match_key(d):
                return tuple(d[field] for field in match_fields)

            # Build a lookup from primary_list
            primary_map = {match_key(d): d for d in primary_list}

            # Override or add from append_list
            for d in append_list:
                primary_map[match_key(d)] = d

            merged = list(primary_map.values())

        return merged

    def trim_csv_data(self, csv_data: list[dict], max_lines: int | None = None, max_days: int | None = None) -> list[dict]:  # noqa: PLR0912
        """Trim the CSV data based on the header configuration and optionally the max_lines arg.

        Args:
            csv_data (list[dict]): The data read from the CSV file.
            max_lines (Optional(int), optional): If provided, the maximum number of lines to return from csv_data.
                If this is >0 then it will return the first max_lines lines, if <0 then it will return all but the last abs(max_lines) lines. If None, no trimming is done.
            max_days (Optional(int), optional): If provided, the maximum number of days to keep in the data based on date headers with 'minimum' set as an int. This overrides any 'minimum' values in the header configuration.

        Returns:
            list[dict]: The trimmed data.
        """
        if not self.header_config:
            return csv_data

        # Get headers that have a 'minimum' key
        minimum_headers = [
            header for header in self.header_config
            if "minimum" in header
        ]

        # If no minimum headers and no max_lines, return original data
        if not minimum_headers and max_lines is None:
            return csv_data

        # Trim based on header configuration
        trimmed_data = csv_data
        for header in minimum_headers:
            field_name = header["name"]
            field_type = header["type"]
            minimum_value = header["minimum"]

            # Calculate the cutoff date
            if max_days is not None:
                if field_type == "date":
                    cutoff = DateHelper.today_add_days(-max_days)
                elif field_type == "datetime":
                    cutoff = DateHelper.add(DateHelper.now(), days=-max_days)
                    # cutoff = DateHelper.remove_timezone(cutoff)  # Issue 33
                else:
                    continue  # Skip if field type is not date or datetime
            elif isinstance(minimum_value, (dt.date, dt.datetime)):
                cutoff = minimum_value
            elif isinstance(minimum_value, int):
                if field_type == "date":
                    cutoff = DateHelper.today_add_days(-minimum_value)
                elif field_type == "datetime":
                    cutoff = DateHelper.add(DateHelper.now(), days=-minimum_value)
                    # cutoff = DateHelper.remove_timezone(cutoff)   # Issue 33
                else:
                    continue  # Skip if field type is not date or datetime
            else:
                continue  # Skip if minimum is neither date nor int

            # Filter out records with dates prior to cutoff_date
            trimmed_data = [
                row for row in trimmed_data
                if field_name in row and isinstance(row[field_name], (dt.date, dt.datetime)) and row[field_name] >= cutoff
            ]

        # If max_lines is specified, trim the data to that many lines
        if max_lines is not None and max_lines != 0:
            if max_lines > 0:
                trimmed_data = trimmed_data[:max_lines]
            else:  # max_lines < 0
                trimmed_data = trimmed_data[max_lines:]

        return trimmed_data

    def write_csv(self, data: list[dict], new_filename: Path | str | None = None) -> bool:  # noqa: PLR0912
        """Write data to the CSV file.

        1. If the file does not exist, it will be created.
        2. If the file exists, it will be overwritten.
        3. The header will be written based on the header_config.
        4. The data will be written in the order of the header_config.
        5. If a header in the data does not exist in the header_config, it will be ignored.
        6. If a header in the header_config does not exist in the data, throw an exception.
        7. Date fields are formatted according to the format specified in header_config.

        Args:
            data (list[dict]): The data to write to the CSV file.
            new_filename (Optional(Path | str), optional)): If provided, the data will be written to this file instead of the original file.

        Raises:
            ValueError: If the data is empty or if a header in header_config is not found in the data.

        Returns:
            True if the data was written successfully, False otherwise.
        """
        if new_filename is not None:
            # If a new filename is provided, use it
            if isinstance(new_filename, str):
                new_filename = Path(new_filename)
            self.file_path = new_filename
            # Check if the file exists
            self.file_exists = bool(self.file_path.is_file())

        use_temp_file = False
        if self.file_exists:
            # If file already exists, create a temporary file to write to
            use_temp_file = True
        else:
            # Create the file if it does not exist
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.touch()
            self.file_exists = True

        # Validate the data against the header_config
        if not data:
            error_msg = "No data to write to CSV file."
            raise ValueError(error_msg)

        # Check if all headers in header_config are in the data
        for header in self.header_config:
            if header["name"] not in data[0]:
                error_msg = f"Header '{header['name']}' not found in data."
                raise ValueError(error_msg)

        # Format the data according to header_config
        formatted_data = []
        for row in data:
            formatted_row = {}
            for header in self.header_config:
                field_name = header["name"]
                value = row[field_name]

                # Format according to header config
                if header["type"] == "date" and isinstance(value, dt.date):
                    date_format = header.get("format", "%Y-%m-%d")
                    formatted_row[field_name] = value.strftime(date_format)
                elif header["type"] == "datetime" and isinstance(value, dt.datetime):
                    datetime_format = header.get("format", "%Y-%m-%d %H:%M:%S")
                    formatted_row[field_name] = value.strftime(datetime_format)
                elif header["type"] == "time" and isinstance(value, dt.time):
                    time_format = header.get("format", "%H:%M")
                    formatted_row[field_name] = value.strftime(time_format)
                elif header["type"] == "float" and "format" in header:
                    formatted_row[field_name] = format(value, header["format"])
                else:
                    formatted_row[field_name] = value

            formatted_data.append(formatted_row)

        # Write the CSV file
        if use_temp_file:
            temporary_path = self.file_path.with_suffix(".tmp")

            with temporary_path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=[header["name"] for header in self.header_config])
                writer.writeheader()
                writer.writerows(formatted_data)
            # Replace the original file with the temporary file
            temporary_path.replace(self.file_path)
        else:
            with self.file_path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=[header["name"] for header in self.header_config])
                writer.writeheader()
                writer.writerows(formatted_data)

        return True

    def update_csv_file(self, new_data: list[dict], new_filename: Path | str | None = None, max_lines: int | None = None, max_days: int | None = None) -> list[dict]:
        """Appends or merges the new_data into an existing CSV file. If the file does not exist, it will be created.

        This function will also sort and trim the combined data according to the header configuration.

        Args:
            new_data (list[dict]): The new data to append or merge.
            new_filename (Optional(Path | str), optional)): If provided, the data will be written to this file instead of the original file.
            max_lines (Optional(int), optional): If provided, the maximum number of lines to return from csv_data.
                If this is >0 then it will return the first max_lines lines, if <0 then it will return all but the last abs(max_lines) lines. If None, no trimming is done.
            max_days (Optional(int), optional): If provided, the maximum number of days to keep in the data based on date headers with 'minimum' set as an int. This overrides any 'minimum' values in the header configuration.

        Raises:
            RuntimeError: If there is a problem processign the data.

        Returns:
            merged_data (list[dict]): The merged and sorted data after appending or merging the new_data.
        """
        # Read the existing CSV data
        try:
            current_data = self.read_csv()
        except (ImportError, TypeError, ValueError) as e:
            raise RuntimeError(e) from e

        if current_data:
            # Merge / append the extra data
            try:
                merged_data = self.merge_data_sets(current_data, new_data)
            except ValueError as e:
                raise RuntimeError(e) from e

            # Sort the data according to the header configuration
            merged_data = self.sort_csv_data(merged_data)

            # Trim the CSV data
            merged_data = self.trim_csv_data(merged_data, max_lines=max_lines, max_days=max_days)
        else:
            # If no current data, just use the new_data
            merged_data = new_data

        # Save the modified CSV data
        self.write_csv(merged_data, new_filename)
        return merged_data
