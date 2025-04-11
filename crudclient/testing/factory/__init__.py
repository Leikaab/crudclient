import os
import sys

from crudclient.testing.factory.simple_mock import create_simple_mock_client

# Removed problematic import of MockClientFactory causing circular dependency

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the MockClientFactory class from the factory.py file

__all__ = ['create_simple_mock_client', 'MockClientFactory']
