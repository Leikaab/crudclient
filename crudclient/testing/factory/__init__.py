"""
Factory module for creating mock client helpers.

This package provides helper functions and utilities for configuring mock clients
and creating pre-configured mock instances for testing.
"""

from crudclient.testing.factory.simple_mock import create_simple_mock_client

__all__ = ['create_simple_mock_client']
