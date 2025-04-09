"""
Advanced test doubles for the crudclient testing framework.

This module provides more sophisticated test doubles beyond simple mocks,
including FakeAPI with an in-memory data store and specialized stubs.
"""

from .data_store import DataStore, ValidationException
from .data_store_helpers import RelationshipType
from .fake_api import FakeAPI, FakeCrud
from .stubs import Response, CrudBase, StubResponse, StubClient, StubCrud, StubAPI

__all__ = [
    'DataStore',
    'ValidationException',
    'RelationshipType',
    'FakeAPI',
    'FakeCrud',
    'Response',
    'CrudBase',
    'StubResponse',
    'StubClient',
    'StubCrud',
    'StubAPI',
]
