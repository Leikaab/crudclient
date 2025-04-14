# tests/unit/test_logging_config.py
import io
import logging

import pytest

# Get the root logger for the crudclient package
# This assumes your library's root logger is named 'crudclient'
# Adjust if your actual logger name is different.
# It's often good practice to define this centrally, e.g., in crudclient/__init__.py
# like: logger = logging.getLogger(__name__)
crud_logger = logging.getLogger("crudclient")
http_logger = logging.getLogger("crudclient.http")


# Helper function to ensure cleanup
@pytest.fixture(autouse=True)
def ensure_logging_cleanup():
    """Ensure logging state is reset after each test."""
    original_level = crud_logger.level
    original_handlers = crud_logger.handlers[:]
    original_http_level = http_logger.level
    original_http_handlers = http_logger.handlers[:]
    # Ensure propagation is managed if necessary, depends on setup
    original_propagate = crud_logger.propagate
    original_http_propagate = http_logger.propagate

    yield  # Run the test

    # Restore original state
    crud_logger.setLevel(original_level)
    crud_logger.handlers = original_handlers
    crud_logger.propagate = original_propagate

    http_logger.setLevel(original_http_level)
    http_logger.handlers = original_http_handlers
    http_logger.propagate = original_http_propagate

    # If tests modify the root logger, reset it too
    # logging.getLogger().handlers = [] # Be careful with global root logger


def test_logging_default_configuration(caplog):
    """Verify the default logging configuration for the library.

    - No handlers attached directly to the library logger (or only NullHandler).
    - Propagation to the root logger is enabled.
    - Logs are captured if the root logger is configured (simulated by caplog).
    """
    # 1. Check for handlers on the library's logger
    # It should ideally be empty, or contain only a NullHandler added by the library itself.
    has_only_null_handler = len(crud_logger.handlers) == 1 and isinstance(crud_logger.handlers[0], logging.NullHandler)
    assert (
        len(crud_logger.handlers) == 0 or has_only_null_handler
    ), f"Expected 0 handlers or 1 NullHandler on {crud_logger.name}, found: {crud_logger.handlers}"

    # 2. Check if propagation is enabled (standard practice)
    assert crud_logger.propagate is True, f"Expected {crud_logger.name} to propagate messages by default."

    # 3. Verify logs *are* captured by root logger config (using caplog) due to propagation
    caplog.set_level(logging.DEBUG, logger="crudclient")  # Ensure caplog listens

    # Trigger logs
    crud_logger.debug("Default: Crud debug message.")
    http_logger.info("Default: HTTP info message.")
    crud_logger.warning("Default: Crud warning message.")

    # Assert logs were captured by caplog because they propagated
    assert len(caplog.records) >= 3, "Logs should have propagated to caplog's handler"
    assert "Default: Crud debug message." in caplog.text
    assert "Default: HTTP info message." in caplog.text
    assert "Default: Crud warning message." in caplog.text


def test_logging_set_level_root(caplog):
    """Verify setting the level on the root crudclient logger captures messages."""
    # Add caplog's handler to the crudclient logger
    # No need to explicitly add handler, caplog does this implicitly
    # when you use caplog.set_level(..., logger='crudclient')
    caplog.set_level(logging.DEBUG, logger="crudclient")

    # Trigger logs at various levels
    crud_logger.debug("Root debug message.")
    http_logger.info("HTTP info message via root.")  # Should propagate
    crud_logger.warning("Root warning message.")
    http_logger.debug("HTTP debug message via root.")  # Should propagate

    # Assert messages at DEBUG level and above were captured
    assert len(caplog.records) == 4
    assert "Root debug message." in caplog.text
    assert "HTTP info message via root." in caplog.text
    assert "Root warning message." in caplog.text
    assert "HTTP debug message via root." in caplog.text


def test_logging_set_level_sub_logger(caplog):
    """Verify setting a different level on a sub-logger filters correctly."""
    # Set root to DEBUG, but sub-logger to INFO
    caplog.set_level(logging.DEBUG, logger="crudclient")  # Capture everything from root
    http_logger.setLevel(logging.INFO)  # Filter http messages

    # Trigger logs
    crud_logger.debug("Root debug again.")
    http_logger.debug("HTTP debug filtered.")  # Should be filtered by http_logger's level
    http_logger.info("HTTP info allowed.")  # Should be allowed by http_logger
    crud_logger.warning("Root warning again.")

    # Assert filtering worked
    # We expect Root debug, HTTP info, Root warning
    assert len(caplog.records) == 3
    assert "Root debug again." in caplog.text
    assert "HTTP debug filtered." not in caplog.text
    assert "HTTP info allowed." in caplog.text
    assert "Root warning again." in caplog.text


def test_logging_add_handler_captures_logs():
    """Verify adding a standard handler captures logs."""
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
    handler.setFormatter(formatter)

    # Add handler specifically to the crud logger
    crud_logger.addHandler(handler)
    crud_logger.setLevel(logging.INFO)  # Set level to INFO for this test

    # Trigger logs
    crud_logger.debug("Crud debug filtered by level.")
    crud_logger.info("Crud info message.")
    http_logger.warning("HTTP warning propagates.")  # Assumes http logger propagates

    # Check the stream content
    log_output = log_stream.getvalue()

    assert "Crud debug filtered by level." not in log_output
    assert "crudclient:INFO:Crud info message." in log_output
    # Check propagation: http message should appear formatted by the handler on crud_logger
    assert "crudclient.http:WARNING:HTTP warning propagates." in log_output

    # Cleanup: Remove the handler
    crud_logger.removeHandler(handler)


def test_logging_custom_formatter():
    """Verify a custom formatter formats logs correctly."""
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    # Define a custom format
    custom_format = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
    formatter = logging.Formatter(custom_format, datefmt="%Y-%m-%d")  # Example date format
    handler.setFormatter(formatter)

    crud_logger.addHandler(handler)
    crud_logger.setLevel(logging.WARNING)  # Set level for this test

    # Trigger a log
    crud_logger.warning("A warning with custom format.")

    # Check the stream content for the custom format
    log_output = log_stream.getvalue()

    # We can't assert the exact timestamp, but check the structure
    assert "] WARNING in crudclient: A warning with custom format." in log_output
    assert log_output.startswith("[")  # Starts with our date format marker

    # Cleanup
    crud_logger.removeHandler(handler)
