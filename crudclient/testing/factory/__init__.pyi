"""
Factory module for creating mock client helpers.

This package provides helper functions and utilities for configuring mock clients
and creating pre-configured mock instances for testing.
"""
import os
import sys

from crudclient.testing.factory.simple_mock import create_simple_mock_client
from crudclient.testing.factory_module import MockClientFactory

__all__ = ['create_simple_mock_client', 'MockClientFactory']
