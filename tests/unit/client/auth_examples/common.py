"""
Common imports and utilities for authentication examples.
"""

import pytest
from unittest.mock import MagicMock

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.exceptions import AuthenticationError

from tests.unit.mock_client.factory import create_mock_client
from tests.unit.mock_client.auth import (
    create_basic_auth_mock, create_bearer_auth_mock,
    create_api_key_auth_mock, create_custom_auth_mock,
    AuthVerificationHelpers
)
