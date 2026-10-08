# tests/unit/crud/test_endpoint_builder_usage.py
"""
Unit tests for how Crud uses the EndpointBuilder from apiconfig.
"""

import warnings
from typing import Any, List, Optional, Tuple, Union
from unittest.mock import MagicMock

import pytest
from apiconfig.utils.endpoint_builder import EndpointBuilder

from crudclient.crud.base import Crud
from crudclient.utils import endpoint_builder as legacy_endpoint_builder

from .conftest import BaseTestCrud, ParentCrud


class LegacyPrefixCrud(Crud[Any]):
    _resource_path = "contacts"

    def _endpoint_prefix(self) -> Union[Tuple[Optional[str], Optional[str]], List[Optional[str]]]:
        return ["companies", "acme"]


class LegacyGetEndpointCrud(Crud[Any]):
    _resource_path = "items"

    def _get_endpoint(self, *args: Any, parent_args: Optional[Any] = None) -> str:
        return "custom/items"


def test_operations_do_not_emit_deprecation_warnings(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a plain Crud subclass
    WHEN the built-in operations build endpoints
    THEN no DeprecationWarning is emitted.
    """
    mock_client.get.return_value = []
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        base_test_crud.list()
    mock_client.get.assert_called_once()
    assert mock_client.get.call_args[0][0] == "test-resources"


def test_nested_operation_uses_parent_path(nested_base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a Crud nested under a parent
    WHEN list is called with a parent id
    THEN the endpoint is placed under the parent path.
    """
    mock_client.get.return_value = []
    nested_base_test_crud.list(parent_id="9")
    assert mock_client.get.call_args[0][0] == f"{ParentCrud._resource_path}/9/test-resources"


def test_legacy_endpoint_prefix_override_is_honoured(mock_client: MagicMock) -> None:
    """
    GIVEN a subclass that overrides the deprecated _endpoint_prefix
    WHEN it is created and an endpoint is built
    THEN a DeprecationWarning is emitted and the prefix is still used.
    """
    with pytest.warns(DeprecationWarning, match="_endpoint_prefix"):
        crud = LegacyPrefixCrud(mock_client)
    mock_client.get.return_value = {"id": 1}
    crud.read("1")
    assert mock_client.get.call_args[0][0] == "companies/acme/contacts/1"


def test_legacy_get_endpoint_override_is_still_called(mock_client: MagicMock) -> None:
    """
    GIVEN a subclass that overrides the deprecated _get_endpoint
    WHEN an operation runs
    THEN the override builds the endpoint.
    """
    crud = LegacyGetEndpointCrud(mock_client)
    mock_client.get.return_value = []
    crud.list()
    assert mock_client.get.call_args[0][0] == "custom/items"


def test_empty_and_none_segments_are_skipped(base_test_crud: BaseTestCrud) -> None:
    """
    GIVEN the deprecated _get_endpoint adapter
    WHEN it gets None and empty segments
    THEN they are left out of the path instead of raising.
    """
    with pytest.warns(DeprecationWarning):
        assert base_test_crud._get_endpoint("1", None, "") == "test-resources/1"


def test_old_import_path_reexports_apiconfig() -> None:
    """The crudclient.utils.endpoint_builder module re-exports apiconfig's builder."""
    assert legacy_endpoint_builder.EndpointBuilder is EndpointBuilder
