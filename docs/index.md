# Spello Consulting Foundation Library

## Available Classes

The Spello Consulting Foundation library provides some foundational classes for:

- [SCCommon](reference/common.md): Some common functions used by other classes.
- [SCConfigManager](reference/configmanager.md): Reading from and validating YAML style config files
- [SCLogging](reference/logging.md): Logging messages to the console and a log file and sending email in plain text or HTML format
- [CSVReader](reference/csvreader.md): Reading data from and and writing to CSV files
- [DateHelper](reference/datehelper.md): Date and datetime helper functions
- [JSONEncoder](reference/jsonencoder.md): Helps convert dicts and lists to json and back, preserving datetime and enum data types.

## Installing the library

The library is available from PyPi, so to add it to your Python project use pip:

    pip install sc-foundation

Or better yet, use UV:

    uv add sc-foundation


## Configuration File 
The library uses a YAML file for configuration. An example config file (*config.yaml.example*) is [available on Github](https://github.com/NickElseySpelloC/sc-foundation). Copy this to *[your_app_name].yaml* before using the library. 

Here's the example file - the library expects to find the Files and Email sections in the file:

```yaml
AmberAPI:
    APIKey: somerandomkey342
    BaseUrl: https://api.amber.com.au/v1
    Timeout: 15

Files:
    LogfileName: logfile.log
    LogfileMaxLines: 500
    LogProcessID: False
    LogfileVerbosity: detailed
    ConsoleVerbosity: detailed

Email:
    EnableEmail: True
    SMTPServer: smtp.gmail.com
    SMTPPort: 587
    SMTPUsername: me@gmail.com
    SMTPPassword: <Your SMTP password>
    SubjectPrefix: "[Bob Portfolio]: "
```

### Configuration Parameters

#### Section: Files

| Parameter | Description | 
|:--|:--|
| LogfileName | The name of the log file, can be a relative or absolute path. | 
| LogfileMaxLines | Maximum number of lines to keep in the log file. If zero, file will never be truncated. | 
| LogfileVerbosity | The level of detail captured in the log file. One of: none; error; warning; summary; detailed; debug; all | 
| ConsoleVerbosity | Controls the amount of information written to the console. One of: error; warning; summary; detailed; debug; all. Errors are written to stderr all other messages are written to stdout | 

#### Section: Email

| Parameter | Description | 
|:--|:--|
| EnableEmail | Set to *True* if you want to allow the app to send emails. If True, the remaining settings in this section must be configured correctly. | 
| SMTPServer | The SMTP host name that supports TLS encryption. If using a Google account, set to smtp.gmail.com |
| SMTPPort | The port number to use to connect to the SMTP server. If using a Google account, set to 587 |
| SMTPUsername | Your username used to login to the SMTP server. If using a Google account, set to your Google email address. Alternatively, set the SMTP_USERNAME environment variable.  |
| SMTPPassword | The password used to login to the SMTP server. If using a Google account, create an app password for the app at https://myaccount.google.com/apppasswords. Alternatively, set the SMTP_PASSWORD environment variable.  |
| SubjectPrefix | Optional. If set, the app will add this text to the start of any email subject line for emails it sends. |

## Example code

Here's an example module that shows how to use the library classes. Use the **API Reference** navigation to view the API methods for each class. The code example and the companion config and Excel files is available in the examples/ folder in the Github repo.

```python

  {%
    include "../examples/example.py"
  %}
```