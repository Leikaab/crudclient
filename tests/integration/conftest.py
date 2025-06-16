"""
Pytest configuration and fixtures for integration tests.
"""

import datetime
import logging
import os
import uuid
from typing import List, Optional

import pytest
from dotenv import load_dotenv

from .tripletex_resources import TripletexAPI, TripletexTestConfig

# Load environment variables from .env file
load_dotenv()

# Environment variable that controls running live tests
RUN_LIVE_TESTS = os.getenv("RUN_LIVE_TESTS")

logger = logging.getLogger(__name__)


def pytest_collection_modifyitems(config, items):
    """Skip integration tests when RUN_LIVE_TESTS is not set."""
    if RUN_LIVE_TESTS:
        return

    skip_marker = pytest.mark.skip(reason="RUN_LIVE_TESTS not set; skipping integration tests")
    for item in items:
        item.add_marker(skip_marker)


# Prefix for test suppliers to identify them for cleanup
TEST_SUPPLIER_PREFIX = "TEST_CRUDCLIENT_"


@pytest.fixture
def api():
    """
    Create a Tripletex API client for testing.
    """
    config = TripletexTestConfig()
    return TripletexAPI(client_config=config)


@pytest.fixture
def supplier_tracker(api):
    """
    Track suppliers created during tests for cleanup.
    Returns a list that tests can append supplier IDs to.
    """
    created_suppliers: List[int] = []

    yield created_suppliers

    # Cleanup: Delete all tracked suppliers
    for supplier_id in created_suppliers:
        try:
            api.suppliers.destroy(supplier_id)
            logger.info(f"Cleaned up test supplier with ID: {supplier_id}")
        except Exception as e:
            logger.warning(f"Failed to clean up supplier {supplier_id}: {e}")


@pytest.fixture
def unique_supplier_name():
    """
    Generate a unique supplier name with test prefix and timestamp.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{TEST_SUPPLIER_PREFIX}{timestamp}_{unique_id}"


@pytest.fixture
def find_unused_supplier_number(api):
    """
    Factory fixture to find an unused supplier number.
    """

    def _find_unused(start_number: int = 900000, max_attempts: int = 100) -> Optional[str]:
        """
        Find an unused supplier number starting from start_number.

        Args:
            start_number: Starting number to search from (default: 900000)
            max_attempts: Maximum number of attempts (default: 100)

        Returns:
            An unused supplier number as string, or None if not found
        """
        for attempt in range(max_attempts):
            supplier_number = str(start_number + attempt)

            # Check if this supplier number exists
            existing_suppliers = api.suppliers.list(params={"supplierNumber": supplier_number})

            if len(existing_suppliers.values) == 0:
                return supplier_number

        return None

    return _find_unused


@pytest.fixture(scope="session", autouse=True)
def cleanup_orphaned_test_suppliers(request):
    """
    Session-level fixture that runs after all tests to clean up any orphaned test suppliers.
    This catches suppliers that weren't cleaned up due to test failures.
    """

    def cleanup():
        config = TripletexTestConfig()
        api = TripletexAPI(client_config=config)

        try:
            # List all suppliers (we'll filter by name)
            # Using pagination to handle large numbers
            page = 0
            cleaned_count = 0

            while True:
                suppliers = api.suppliers.list(params={"from": page * 100, "count": 100})

                if not suppliers.values:
                    break

                # Find test suppliers by prefix
                for supplier in suppliers.values:
                    if supplier.name and supplier.name.startswith(TEST_SUPPLIER_PREFIX):
                        try:
                            api.suppliers.destroy(supplier.id)
                            cleaned_count += 1
                            logger.info(f"Cleaned up orphaned test supplier: {supplier.name} (ID: {supplier.id})")
                        except Exception as e:
                            logger.warning(f"Failed to clean up orphaned supplier {supplier.name} (ID: {supplier.id}): {e}")

                # Check if there are more pages
                if len(suppliers.values) < 100:
                    break

                page += 1

            if cleaned_count > 0:
                logger.info(f"Total orphaned test suppliers cleaned up: {cleaned_count}")

        except Exception as e:
            logger.error(f"Error during orphaned supplier cleanup: {e}")

    # Register the cleanup function to run after the session
    request.addfinalizer(cleanup)
