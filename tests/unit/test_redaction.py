# tests/unit/test_redaction.py
import logging
from typing import Any, Dict, cast  # Add cast
from unittest.mock import MagicMock  # Import MagicMock

import pytest
from apiconfig.utils.redaction import redact_body
from pydantic import BaseModel, Field, ValidationError

from crudclient.exceptions import DataValidationError

# mock_client_config fixture is automatically discovered by pytest from tests/unit/http/conftest.py
# No explicit import needed.

# --- Fixtures ---
# mock_client_config is imported above

# Re-use mock_client_config from http/conftest.py if possible, or redefine if needed
# For simplicity here, let's assume we can import it or a similar fixture exists
# If not, we'd define one similar to http/conftest.py:mock_client_config

# --- Test Response Body Redaction ---


def test_log_response_body_redaction_simple(
    mock_client_config: MagicMock,  # Use the imported fixture type
    caplog: pytest.LogCaptureFixture,
):
    """Verify simple sensitive keys in JSON response body are redacted."""
    mock_client_config.log_response_body = True  # Enable body logging
    caplog.set_level("DEBUG")
    test_logger = logging.getLogger("test_response_body_simple")
    # http_logger = HttpLifecycleLogger(config=mock_client_config, logger=test_logger) # Not used directly

    response_body = {
        "user_id": 123,
        "session_token": "sensitive-session-data",
        "user_details": {
            "email": "test@example.com",
            "password_hash": "should-not-be-logged",  # Assuming password_hash is sensitive
            "api_key": "user-specific-key",
        },
        "permissions": ["read", "write"],
    }
    # Simulate logging the response body (adapt based on actual HttpLifecycleLogger method)
    # Assuming a method like log_response_body exists or is part of log_request_completion
    # For this test, let's directly call redact_body and log it
    redacted_body = redact_body(response_body)
    test_logger.debug(f"Response body (redacted): {str(redacted_body)}")

    body_log_found = False
    for record in caplog.records:
        if record.levelname == "DEBUG" and "Response body (redacted):" in record.message:
            body_log_found = True
            log_output = record.message
            # Check sensitive keys are redacted
            assert "'session_token': '[REDACTED]'" in log_output  # Use single quotes
            assert "'password_hash': '[REDACTED]'" in log_output  # Use single quotes
            # api_key should be redacted as it's in the sensitive list
            assert "'api_key': '[REDACTED]'" in log_output  # Use single quotes and expect redaction

            # Check non-sensitive keys are present
            assert "'user_id': 123" in log_output  # Use single quotes
            assert "'email': 'test@example.com'" in log_output  # Use single quotes
            assert "'permissions': ['read', 'write']" in log_output  # Use single quotes

            # Ensure original secrets are not present (except api_key due to expected bug)
            assert "sensitive-session-data" not in log_output
            assert "should-not-be-logged" not in log_output
            assert "user-specific-key" not in log_output  # Should be redacted
            break
    assert body_log_found, "Response body log message not found"


def test_log_response_body_redaction_nested_list(
    mock_client_config: MagicMock,  # Use the imported fixture type
    caplog: pytest.LogCaptureFixture,
):
    """Verify sensitive keys in nested lists within response body are redacted."""
    mock_client_config.log_response_body = True  # Enable body logging
    caplog.set_level("DEBUG")
    test_logger = logging.getLogger("test_response_body_nested")
    # http_logger = HttpLifecycleLogger(config=mock_client_config, logger=test_logger) # Not used directly

    response_body = {
        "results": [
            {"id": 1, "data": "abc", "secret_code": "alpha-secret"},
            {"id": 2, "data": "def", "credentials": {"token": "beta-token"}},
            {"id": 3, "data": "ghi", "value": "gamma-value-visible"},  # Assuming 'value' itself isn't always sensitive
        ],
        "metadata": {"count": 3},
    }
    redacted_body = redact_body(response_body)
    test_logger.debug(f"Response body (redacted): {str(redacted_body)}")

    body_log_found = False
    for record in caplog.records:
        if record.levelname == "DEBUG" and "Response body (redacted):" in record.message:
            body_log_found = True
            log_output = record.message
            # Check sensitive keys are redacted
            assert "'secret_code': '[REDACTED]'" in log_output  # Use single quotes
            assert "'token': '[REDACTED]'" in log_output  # Use single quotes

            # Check non-sensitive data remains (expecting failure for list handling based on previous test)
            # assert '"id": 1' in log_output # This might fail if list redaction is broken
            # assert '"data": "abc"' in log_output # This might fail
            # assert '"id": 2' in log_output # This might fail
            # assert '"data": "def"' in log_output # This might fail
            # Check non-sensitive data remains (using single quotes)
            assert "'id': 1" in log_output
            assert "'data': 'abc'" in log_output
            assert "'id': 2" in log_output
            assert "'data': 'def'" in log_output
            assert "'id': 3" in log_output
            assert "'data': 'ghi'" in log_output
            assert "'value': 'gamma-value-visible'" in log_output
            assert "'count': 3" in log_output

            # Ensure original secrets are not present
            assert "alpha-secret" not in log_output
            assert "beta-token" not in log_output
            break
    assert body_log_found, "Response body log message not found"


# --- Test DataValidationError Redaction ---


class SensitiveModel(BaseModel):
    user_id: int
    username: str
    password: str = Field(..., repr=False)  # Pydantic repr=False helps but we test logging
    api_key: str = Field(..., repr=False)
    nested: Dict[str, Any] = {}


# Removed defunct test_data_validation_error_log_redaction


def test_data_validation_error_exception_redaction():
    """Verify sensitive data is redacted in DataValidationError exception attributes."""
    invalid_data = {
        "user_id": "not-an-int",
        "username": "testuser",
        "password": "plain_password_secret_ex",
        "api_key": "plain_api_key_secret_ex",
        "nested": {"access_token": "nested_access_token_secret_ex"},
    }

    try:
        SensitiveModel.model_validate(invalid_data)
        pytest.fail("ValidationError was not raised")
    except ValidationError as e:
        # Simulate the raising of DataValidationError as done in response_conversion.py
        # It redacts the data *before* passing it to the exception constructor.
        redacted_input_data_for_exception = redact_body(invalid_data)
        try:
            # Use the correct constructor parameters: message, data, pydantic_error
            raise DataValidationError(
                "Validation failed",  # message (positional)
                data=redacted_input_data_for_exception,  # data (keyword)
                pydantic_error=e,  # pydantic_error (keyword)
            )
        except DataValidationError as dve:
            # Inspect the exception instance attributes
            # The redacted data is stored in the 'data' attribute
            assert hasattr(dve, "data"), "Exception missing 'data' attribute"
            redacted_data = dve.data  # Access the correct attribute

            assert isinstance(redacted_data, dict)
            # Check sensitive fields are redacted
            assert redacted_data.get("password") == "[REDACTED]"
            assert redacted_data.get("api_key") == "[REDACTED]"  # Should be redacted
            assert redacted_data.get("nested", {}).get("access_token") == "[REDACTED]"

            # Check non-sensitive fields
            assert redacted_data.get("username") == "testuser"
            assert redacted_data.get("user_id") == "not-an-int"

            # Ensure original secrets are not present in the stored data (except api_key)
            original_password = invalid_data["password"]
            # original_api_key = invalid_data["api_key"] # Removed unused variable
            nested_dict = cast(Dict, invalid_data.get("nested", {}))  # Explicitly cast to Dict
            original_token = nested_dict.get("access_token")

            # Check the actual dictionary values after redaction
            assert redacted_data.get("password") != original_password
            assert redacted_data.get("api_key") != invalid_data["api_key"]  # Should be redacted
            assert redacted_data.get("nested", {}).get("access_token") != original_token

            # str(dve) does not include the data, so no need to check it here.
            # repr(dve) would include it, but checking the dict directly is cleaner.

        except Exception as final_e:
            pytest.fail(f"Error during DataValidationError inspection: {final_e}")
