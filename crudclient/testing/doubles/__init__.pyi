"""
Testing doubles for the crudclient testing framework.

This module provides various test doubles including stubs, fakes, and mocks
that can be used for testing applications that use crudclient.
"""

from .data_store import DataStore
from .data_store_definitions import ValidationException
from .data_store_relationships import RelationshipType
from .fake_api import FakeAPI, FakeCrud
from .stubs import Response, StubResponse
from .stubs_api import StubAPI
from .stubs_client import StubClient
from .stubs_crud import CrudBase, StubCrud

__all__ = [
    "DataStore",
    "ValidationException",
    "RelationshipType",
    "FakeAPI",
    "FakeCrud",
    "Response",
    "CrudBase",
    "StubResponse",
    "StubClient",
    "StubCrud",
    "StubAPI",
]
