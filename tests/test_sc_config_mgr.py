"""pytest for SCConfigManager class."""
import sys

from sc_foundation import DateHelper, SCConfigManager

# Remove the period if running this in the debugger
from .config_schemas import ConfigSchema

CONFIG_FILE = "tests/config.yaml"


print("Running test for SCConfigManager...")
# Get our default schema, validation schema, and placeholders
schemas = ConfigSchema()

# Initialize the SC_ConfigManager class
try:
    config = SCConfigManager(
        config_file=CONFIG_FILE,
        default_config=schemas.default,
        validation_schema=schemas.validation,
        placeholders=schemas.placeholders
    )
except RuntimeError as e:
    print(f"Configuration file error: {e}", file=sys.stderr)
    sys.exit(1)


def test_get_value():
    """Test reading configuration values from the config file."""
    value1 = config.get("Testing", "Value1")
    value2 = config.get("Testing", "Value2")

    string1 = config.get("Testing", "String1")
    string2 = config.get("Testing", "String2")

    assert value1 == value2, "Value1 and Value2 should be equal"
    assert string1 == string2, "String1 and String2 should be equal"

    print("Configuration values read successfully:")


def test_load_config():
    """Test loading the configuration file."""
    assert config.load_config(), "Failed to load configuration"

    print("Configuration loaded successfully.")


def test_check_for_config_changes():
    """Test checking for changes in the configuration file."""
    # Create a fake last check time well in the past
    last_check = DateHelper.add(DateHelper.now(), days=-365)
    assert config.check_for_config_changes(last_check) is not None, "Configuration changes were not detected"

    print("Configuration changes detected successfully.")


def test_register_logger():
    """Test registering a logger with the configuration manager will be tested in test_sc_logging."""
    # Nothing to do here.


def test_check_for_placeholders():
    """Test checking for placeholders in the configuration."""
    assert not config.check_for_placeholders(schemas.placeholders), "Placeholders were found in the configuration"

    print("No placeholders found in the configuration.")


def test_get_logger_settings():
    """Test getting logger settings from the configuration."""
    logger_settings = config.get_logger_settings()

    assert isinstance(logger_settings, dict), "Logger settings should be a dictionary"
    assert "logfile_name" in logger_settings, "Logger settings should contain 'logfile_name'"

    print("Logger settings retrieved successfully:", logger_settings)


# test_check_for_config_changes()
