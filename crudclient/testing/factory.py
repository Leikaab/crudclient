"""
Factory Pattern Implementation for Mock Client Creation.

This module utilizes the **Factory pattern** to provide a centralized and
flexible way to create and configure various mock client instances
(`MockClient`, `SimpleMockClient`) needed for testing different scenarios.
It encapsulates the complex setup logic behind simple creation methods.

Key Components:
- `MockClientFactory`: A class implementing Factory Methods (`create`,
  `from_client_config`, etc.) to produce configured `MockClient` instances.
- `create_simple_mock_client`: A factory function for creating `SimpleMockClient`
  instances.
"""

# Re-export the factory class and function from their new locations
from .mock_client_factory import MockClientFactory
from .simple_mock_factory import create_simple_mock_client

# Make linters happy about unused imports
__all__ = ["MockClientFactory", "create_simple_mock_client"]
