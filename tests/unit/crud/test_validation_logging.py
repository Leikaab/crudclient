"""
Unit tests for logging during CRUD request and response data validation.
"""

import json
import logging
from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError as PydanticValidationError

from crudclient.exceptions import DataValidationError

# Import necessary fixtures/models from conftest or helpers
from .conftest import BaseTestCrud

SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource", "secret": "password123"}  # Added sensitive field


# --- Test Class for Request Validation Logging ---


class TestCrudRequestValidationLogging:
    """Tests logging for request data validation errors."""

    @pytest.mark.parametrize(
        "operation_name, operation_args",
        [
            ("create", {"data": SAMPLE_PAYLOAD}),
            ("update", {"resource_id": "1", "data": SAMPLE_PAYLOAD}),
            ("partial_update", {"resource_id": "1", "data": {"name": "Partial", "secret": "newpass"}}),
            # Custom action needs careful setup if data validation happens before client call
            # ("custom_action", {"action": "validate-me", "method": "post", "data": SAMPLE_PAYLOAD}),
        ],
    )
    def test_request_validation_error_logs_error(
        self,
        base_test_crud: BaseTestCrud,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        operation_name: str,
        operation_args: dict[str, Any],
    ) -> None:
        """
        GIVEN a CRUD operation (create, update, partial_update)
        WHEN input data fails Pydantic validation before the API call
        THEN an ERROR log should be emitted with validation details.
        """
        # Instantiate a minimal ValidationError to trigger the except block
        # Provide an empty list for line_errors to avoid type complexity
        validation_error = PydanticValidationError.from_exception_data(title="BaseTestModel", line_errors=[])

        # Mock the internal _dump_data method to raise the validation error
        mocker.patch.object(base_test_crud, "_dump_data", side_effect=validation_error)

        # Set caplog level for the specific logger
        caplog.set_level(logging.ERROR, logger="crudclient.crud.operations")

        operation_func = getattr(base_test_crud, operation_name)

        # Expect DataValidationError to be raised
        with pytest.raises(DataValidationError):
            operation_func(**operation_args)

        # Assert Log
        error_log_found = False
        expected_model_name = getattr(base_test_crud._datamodel, "__name__", "Unknown")
        # Adjust expected error JSON to match the minimal error created
        expected_error_json = json.dumps([])

        for record in caplog.records:
            if (
                record.name == "crudclient.crud.operations"
                and record.levelno == logging.ERROR
                and f"Request data validation failed during '{operation_name}'" in record.message
                and f"resource '{expected_model_name}'" in record.message
                and expected_error_json in record.message
            ):
                error_log_found = True
                # Verify that the raw sensitive data is NOT in the log message
                assert "password123" not in record.message
                assert "newpass" not in record.message
                break
        assert error_log_found, f"Expected ERROR log for {operation_name} request validation not found"

    # Optional: Add a specific test for custom_action if its validation path differs significantly
    # def test_custom_action_request_validation_error_logs_error(...):
    #    ...


# --- Test Class for Response Validation Logging ---


class TestCrudResponseValidationLogging:
    """Tests logging for response data validation errors."""

    INVALID_RESPONSE_PAYLOAD = {"id": "not-an-int", "name": "Invalid ID Type", "secret": "response-secret"}
    INVALID_LIST_RESPONSE_PAYLOAD = [
        {"id": 1, "name": "Valid Item"},
        {"id": "not-an-int-either", "name": "Invalid Item", "secret": "list-secret"},
    ]

    @pytest.mark.parametrize(
        "operation_name, operation_args, client_method_name",
        [
            ("read", {"resource_id": "1"}, "get"),
            # Provide valid request data (including ID) so error happens on response
            ("create", {"data": {"id": 1, "name": "Valid Create"}}, "post"),
            ("update", {"resource_id": "1", "data": {"id": 1, "name": "Valid Update"}}, "put"),
            ("partial_update", {"resource_id": "1", "data": {"name": "Valid Partial"}}, "patch"),  # Assume valid request data
            # Custom action might return single item or list, test separately if needed
        ],
    )
    def test_single_item_response_validation_error_logs_error(
        self,
        base_test_crud: BaseTestCrud,
        mock_client: MagicMock,
        caplog: pytest.LogCaptureFixture,
        operation_name: str,
        operation_args: dict[str, Any],
        client_method_name: str,
    ) -> None:
        """
        GIVEN a CRUD operation returning a single item
        WHEN the API response data fails Pydantic validation
        THEN an ERROR log should be emitted with validation details.
        """
        # Mock the client method to return invalid data
        client_method = getattr(mock_client, client_method_name)
        # Return raw dict, conversion happens in CRUD layer
        client_method.return_value = self.INVALID_RESPONSE_PAYLOAD

        # Set caplog level for the response conversion logger
        # Capture logs from both possible sources
        caplog.set_level(logging.ERROR, logger="crudclient.crud.response_conversion")
        caplog.set_level(logging.ERROR, logger="crudclient.response_strategies.default")

        operation_func = getattr(base_test_crud, operation_name)

        # Expect DataValidationError during response conversion
        with pytest.raises(DataValidationError):
            operation_func(**operation_args)

        # Assert Log
        error_log_found = False
        expected_model_name = getattr(base_test_crud._datamodel, "__name__", "Unknown")
        # Make JSON assertion less strict - check for key parts instead of exact match
        expected_input = "'input': 'not-an-int'"
        expected_loc = "'loc': ('id',)"  # Note: Pydantic v2 uses list ['id']
        expected_msg = "'msg': 'Input should be a valid integer"  # Partial match
        expected_type = "'type': 'int_parsing'"

        for record in caplog.records:
            # Check for logs from either logger
            if (
                record.name in ["crudclient.crud.response_conversion", "crudclient.response_strategies.default"]
                and record.levelno == logging.ERROR
                and f"Response data validation failed for model {expected_model_name}" in record.message
                # Check for key error details substrings
                and expected_input in record.message
                and (expected_loc in record.message or "'loc': ['id']" in record.message)  # Allow tuple or list loc
                and expected_msg in record.message
                and expected_type in record.message
            ):
                error_log_found = True
                # Verify redaction (though less likely in response logs unless explicitly added)
                assert "response-secret" not in record.message
                break
        assert error_log_found, f"Expected ERROR log for {operation_name} response validation not found"

    def test_list_response_validation_error_logs_error(
        self,
        base_test_crud: BaseTestCrud,
        mock_client: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        GIVEN a 'list' operation
        WHEN the API response list contains data that fails Pydantic validation
        THEN an ERROR log should be emitted with validation details.
        """
        # Mock the client's get method to return a list with invalid data
        mock_client.get.return_value = self.INVALID_LIST_RESPONSE_PAYLOAD

        # Set caplog level for the response conversion logger
        # Capture logs from both possible sources
        caplog.set_level(logging.ERROR, logger="crudclient.crud.response_conversion")
        caplog.set_level(logging.ERROR, logger="crudclient.response_strategies.default")

        # Expect DataValidationError during response conversion
        with pytest.raises(DataValidationError):
            base_test_crud.list()

        # Assert Log
        error_log_found = False
        expected_model_name = getattr(base_test_crud._datamodel, "__name__", "Unknown")
        # Make JSON assertion less strict - check for key parts instead of exact match
        expected_input = "'input': 'not-an-int-either'"
        expected_loc = "'loc': ('id',)"  # Note: Pydantic v2 uses list ['id']
        expected_msg = "'msg': 'Input should be a valid integer"  # Partial match
        expected_type = "'type': 'int_parsing'"

        for record in caplog.records:
            # Check for logs from _convert_to_list_model or _validate_list_return
            if (
                record.name in ["crudclient.crud.response_conversion", "crudclient.response_strategies.default"]
                and record.levelno == logging.ERROR
                and (
                    f"Response list item validation failed for model {expected_model_name}" in record.message
                    or f"Response list validation failed for model {expected_model_name}" in record.message
                )  # Allow for different messages
                # Check for key error details substrings
                and expected_input in record.message
                and (expected_loc in record.message or "'loc': ['id']" in record.message)  # Allow tuple or list loc
                and expected_msg in record.message
                and expected_type in record.message
            ):
                error_log_found = True
                # Verify redaction
                assert "list-secret" not in record.message
                break
        assert error_log_found, "Expected ERROR log for list response validation not found"
