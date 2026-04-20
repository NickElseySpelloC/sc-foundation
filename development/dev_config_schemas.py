"""Configuration schemas for use with the SCConfigManager class."""


class ConfigSchema:
    """Base class for configuration schemas."""

    def __init__(self):
        self.default = {
            "AmberAPI": {
                "APIKey": "<Your API Key Here>",
                "BaseUrl": "https://api.amber.com.au/v1",
                "Timeout": 10,
            }
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
            "ShellyDevices": {
                "schema": {
                    "Devices": {
                        "schema": {
                            "schema": {
                                "Outputs": {
                                    "schema": {
                                        "schema": {
                                            "Colour": {"type": "string", "required": False, "nullable": True},
                                            "Size": {"type": "string", "required": False, "nullable": True},
                                        },
                                    },
                                },
                            },
                        },
                    },
                }
            }
        }
