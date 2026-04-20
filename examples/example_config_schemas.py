"""Configuration schemas for use with the SCConfigManager class."""


class ConfigSchema:
    """Base class for configuration schemas."""

    def __init__(self):
        self.default = {
            "AmberAPI": {
                "APIKey": "<Your API Key Here>",
                "BaseUrl": "https://api.amber.com.au/v1",
                "Timeout": 10,
            },
            "Files": {
                "LogfileName": "example.log",
                "LogfileMaxLines": 5000,
                "LogfileVerbosity": "summary",
                "ConsoleVerbosity": "summary",
            },
            "Email": {
                "EnableEmail": False,
                "SendEmailsTo": "<Your email address here>",
                "SMTPServer": "<Your SMTP server here>",
                "SMTPPort": 587,
                "SMTPUsername": "<Your SMTP username here>",
                "SMTPPassword": "<Your SMTP password here>",
                "SubjectPrefix": None,
            },
        }

        self.placeholders = {
            "AmberAPI": {
                "APIKey": "<Your API Key Here>",
            },
            "Email": {
                "SMTPUsername": "<Your SMTP username here>",
                "SMTPPassword": "<Your SMTP password here>",
            }
        }

        self.validation = {
            "AmberAPI": {
                "type": "dict",
                "schema": {
                    "APIKey": {"type": "string", "required": False, "nullable": True},
                    "BaseUrl": {"type": "string", "required": True},
                    "Timeout": {"type": "number", "required": True, "min": 5, "max": 60},
                },
            },
        }
