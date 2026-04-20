"""pytest for SCLogger class."""
import sys

from sc_foundation import SCCommon, SCConfigManager, SCLogger

# Remove the period if running this in the debugger
from .config_schemas import ConfigSchema

CONFIG_FILE = "tests/config.yaml"
SIMPLE_TEXT_FILE = "tests/simple_text.txt"


print("Running test for SCLogging...")
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

# Initialize the SC_Logger class
try:
    logger = SCLogger(config.get_logger_settings())
except RuntimeError as e:
    print(f"Logger initialisation error: {e}", file=sys.stderr)
    sys.exit(1)


def test_log_normal():
    """Test logging a normal message."""
    message = f"Test message from {sys._getframe().f_code.co_name}"  # noqa: SLF001

    assert logger.log_message(message, "summary") is None, "Logging normal message."


def test_log_error():
    """Test logging an error message."""
    message = f"Test error message from {sys._getframe().f_code.co_name}"  # noqa: SLF001

    assert logger.log_message(message, "error") is None, "Logging error message."


def test_trim_logfile():
    assert logger.trim_logfile() is None, "Trimming log file."


def test_register_email_settings():
    """Test registering email settings."""
    email_settings = config.get_email_settings()

    print(f"Email settings retrieved from configuration: {email_settings}")

    assert isinstance(email_settings, dict), "Email settings should be a dictionary"
    assert "SendEmailsTo" in email_settings, "Email settings should contain 'SendEmailsTo'"

    if email_settings is not None:
        assert logger.register_email_settings(email_settings) is None, "Registering email settings."
    else:
        print("No email settings found in the configuration.")


def test_send_email():
    """Test sending an email."""
    email_settings = config.get_email_settings()
    text_msg = "Hello world from sc-utility example code."
    text_content_path = SCCommon.select_file_location(SIMPLE_TEXT_FILE)

    if email_settings is not None:
        assert logger.register_email_settings(email_settings) is None, "Registering email settings."

        assert logger.send_email("Hello world", text_msg, test_mode=True), "Sending text string email."
        assert text_content_path is not None, "Text content path should not be None."
        assert logger.send_email("Hello world", text_content_path, test_mode=True), "Sending text file email."
    else:
        print("No email settings found in the configuration, skipping email test.")


# test_register_email_settings()
