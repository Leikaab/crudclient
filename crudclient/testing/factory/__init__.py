"""
Factory module for creating mock client helpers.

This package provides helper functions and utilities for configuring mock clients
and creating pre-configured mock instances for testing.
"""
from crudclient.testing.factory_module import MockClientFactory
from crudclient.testing.factory.simple_mock import create_simple_mock_client
import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the MockClientFactory class from the factory.py file

__all__ = ['create_simple_mock_client', 'MockClientFactory']
