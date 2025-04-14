# tests/unit/auth/test_auth_logging.py
import logging
from unittest.mock import Mock

import pytest

from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import CustomAuth

# AuthenticationError is not raised by the methods being tested now


# mock_request is no longer needed as we call prepare_request_headers directly


def test_basic_auth_logs_header_application(caplog: pytest.LogCaptureFixture) -> None:
    """Verify BasicAuth logs header application at DEBUG level without credentials."""
    username = "testuser"
    password = "testpassword"
    auth = BasicAuth(username=username, password=password)
    caplog.set_level(logging.DEBUG, logger="crudclient.auth.basic")  # Target the specific logger

    headers = auth.prepare_request_headers()  # Call the correct method

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "DEBUG"
    assert record.name == "crudclient.auth.basic"
    assert "[BasicAuth] Adding Basic Authentication header to request" in record.message  # Match exact log
    assert "Authorization" in headers  # Check header is returned
    assert username not in record.message
    assert password not in record.message


def test_bearer_auth_logs_header_application(caplog: pytest.LogCaptureFixture) -> None:
    """Verify BearerAuth logs header application at DEBUG level without token."""
    token = "secret-token"
    auth = BearerAuth(token=token)
    caplog.set_level(logging.DEBUG, logger="crudclient.auth.bearer")  # Target the specific logger

    headers = auth.prepare_request_headers()  # Call the correct method

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "DEBUG"
    assert record.name == "crudclient.auth.bearer"
    assert "[BearerAuth] Injecting Bearer token into Authorization header." in record.message  # Match exact log
    assert token not in record.message  # Verify token isn't logged
    assert "Authorization" in headers  # Check header is returned


# BearerAuth refresh tests removed as the functionality is not implemented.


def test_custom_auth_logs_header_callback_invocation(caplog: pytest.LogCaptureFixture) -> None:
    """Verify CustomAuth logs header callback invocation at DEBUG level."""
    mock_callable = Mock(return_value={"X-Custom-Header": "value"})
    auth = CustomAuth(header_callback=mock_callable)  # Use correct parameter
    caplog.set_level(logging.DEBUG, logger="crudclient.auth.custom")  # Target the specific logger

    headers = auth.prepare_request_headers()  # Call the correct method

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "DEBUG"
    assert record.name == "crudclient.auth.custom"
    assert "[CustomAuth] Invoking custom header callback to modify request" in record.message  # Match exact log
    mock_callable.assert_called_once()
    assert headers == {"X-Custom-Header": "value"}  # Check header is returned
