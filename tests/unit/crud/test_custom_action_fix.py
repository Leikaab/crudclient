# tests/unit/crud/test_custom_action_fix.py
"""
Tests specifically for the bug fix related to _prepare_request_body_kwargs in custom_action.
"""

from unittest.mock import MagicMock

from .conftest import BaseTestCrud

# Sample data
TEST_DATA = {"param": "value"}


def test_custom_action_post_with_data(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called with POST method and data
    THEN it should successfully process the request without AttributeError
    """
    # GIVEN
    mock_client.post.return_value = {"id": 1, "name": "Test"}

    # WHEN - This would previously fail with AttributeError
    result = base_test_crud.custom_action(action="test-action", method="post", data=TEST_DATA)

    # THEN - If we get here without exception, the fix is working
    assert result is not None


def test_custom_action_put_with_data(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called with PUT method and data
    THEN it should successfully process the request without AttributeError
    """
    # GIVEN
    mock_client.put.return_value = {"id": 1, "name": "Test"}

    # WHEN - This would previously fail with AttributeError
    result = base_test_crud.custom_action(action="test-action", method="put", data=TEST_DATA)

    # THEN - If we get here without exception, the fix is working
    assert result is not None


def test_custom_action_patch_with_data(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called with PATCH method and data
    THEN it should successfully process the request without AttributeError
    """
    # GIVEN
    mock_client.patch.return_value = {"id": 1, "name": "Test"}

    # WHEN - This would previously fail with AttributeError
    result = base_test_crud.custom_action(action="test-action", method="patch", data=TEST_DATA)

    # THEN - If we get here without exception, the fix is working
    assert result is not None


def test_custom_action_with_files(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called with files parameter
    THEN it should successfully process the request without AttributeError
    """
    # GIVEN
    mock_client.post.return_value = {"id": 1, "name": "Test"}
    files = {"file": ("filename.txt", b"file content")}

    # WHEN - This would previously fail with AttributeError
    result = base_test_crud.custom_action(
        action="upload",
        method="post",
        data=TEST_DATA,
        files=files
    )

    # THEN - If we get here without exception, the fix is working
    assert result is not None


def test_custom_action_with_content_type(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called with content_type parameter
    THEN it should successfully process the request without AttributeError
    """
    # GIVEN
    mock_client.post.return_value = {"id": 1, "name": "Test"}

    # WHEN - This would previously fail with AttributeError
    result = base_test_crud.custom_action(
        action="form-submit",
        method="post",
        data=TEST_DATA,
        content_type="application/x-www-form-urlencoded"
    )

    # THEN - If we get here without exception, the fix is working
    assert result is not None
