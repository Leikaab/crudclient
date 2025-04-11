# tests/unit/crud/test_crud_operations.py
"""
This file previously contained all unit tests for the CRUD operations base class.

The tests have been refactored into separate files within this directory
for better organization and maintainability:

- test_list_operations.py: Tests for the 'list' operation.
- test_create_operations.py: Tests for the 'create' operation.
- test_read_operations.py: Tests for the 'read' operation.
- test_update_operations.py: Tests for the 'update' and 'partial_update' operations.
- test_destroy_operations.py: Tests for the 'destroy' operation.
- test_custom_actions.py: Tests for the 'custom_action' method.
- test_error_handling.py: Tests for generic client errors and API (4xx/5xx) errors.

Please refer to the individual files for specific tests.

Consider moving common constants (SAMPLE_PAYLOAD, etc.) to conftest.py.
"""

# Imports might be needed if constants remain here, otherwise remove unused.
# from unittest.mock import MagicMock # No longer needed if no tests here
# import pytest # No longer needed if no tests here
# from pydantic import ValidationError # Potentially needed by TestModel if constants stay
# from crudclient.exceptions import AuthenticationError, CrudClientError, InvalidResponseError, ModelConversionError, NotFoundError # No longer needed if no tests here

from .conftest import TestModel  # Keep if constants use TestModel

# Sample data (Consider moving to conftest.py)
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = TestModel(**SAMPLE_PAYLOAD)  # type: ignore[arg-type]
SAMPLE_LIST_PAYLOAD = [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]
SAMPLE_MODEL_LIST = [TestModel(**item) for item in SAMPLE_LIST_PAYLOAD]  # type: ignore[arg-type]

# --- All test functions have been moved to separate files ---
