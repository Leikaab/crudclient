# crudclient/testing/factory.py

# Re-export the factory class and function from their new locations
from .mock_client_factory import MockClientFactory
from .simple_mock_factory import create_simple_mock_client

# Make linters happy about unused imports
__all__ = ["MockClientFactory", "create_simple_mock_client"]
