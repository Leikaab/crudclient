#!/usr/bin/env python3
"""
Cleanup utility for removing orphaned test suppliers from Tripletex test environment.

This script identifies and removes suppliers created by integration tests that may have
been left behind due to test failures or interruptions.

Usage:
    python scripts/cleanup_test_suppliers.py [--dry-run] [--prefix PREFIX]
"""
import argparse
import logging
import sys
from pathlib import Path

from tests.integration.conftest import TEST_SUPPLIER_PREFIX
from tests.integration.tripletex_resources.setup import (
    TripletexAPI,
    TripletexTestConfig,
)

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def cleanup_test_suppliers(dry_run: bool = False, prefix: str = TEST_SUPPLIER_PREFIX) -> int:
    """
    Clean up test suppliers from the Tripletex test environment.

    Args:
        dry_run: If True, only report what would be deleted without actually deleting
        prefix: The prefix to identify test suppliers (default: TEST_CRUDCLIENT_)
    """
    config = TripletexTestConfig()
    api = TripletexAPI(client_config=config)

    logger.info(f"Starting cleanup of suppliers with prefix: {prefix}")
    if dry_run:
        logger.info("DRY RUN MODE - No suppliers will be deleted")

    try:
        page = 0
        total_found = 0
        total_deleted = 0
        errors = []

        while True:
            # Fetch suppliers in batches
            logger.debug(f"Fetching page {page}")
            suppliers = api.suppliers.list(params={"from": page * 100, "count": 100})

            if not suppliers.values:
                break

            # Find test suppliers by prefix
            for supplier in suppliers.values:
                if supplier.name and supplier.name.startswith(prefix):
                    total_found += 1
                    logger.info(f"Found test supplier: {supplier.name} (ID: {supplier.id}, Number: {supplier.supplierNumber})")

                    if not dry_run:
                        try:
                            api.suppliers.destroy(supplier.id)
                            total_deleted += 1
                            logger.info(f"  ✓ Deleted supplier {supplier.id}")
                        except Exception as e:
                            error_msg = f"Failed to delete supplier {supplier.id}: {e}"
                            logger.error(f"  ✗ {error_msg}")
                            errors.append(error_msg)

            # Check if there are more pages
            if len(suppliers.values) < 100:
                break

            page += 1

        # Summary
        logger.info("=" * 60)
        logger.info("Cleanup Summary:")
        logger.info(f"  Total test suppliers found: {total_found}")
        if not dry_run:
            logger.info(f"  Successfully deleted: {total_deleted}")
            logger.info(f"  Failed to delete: {len(errors)}")

            if errors:
                logger.error("Errors encountered:")
                for error in errors:
                    logger.error(f"  - {error}")
        else:
            logger.info(f"  Would delete: {total_found} suppliers (dry run)")

    except Exception as e:
        logger.error(f"Fatal error during cleanup: {e}")
        return 1

    return 0 if not errors else 1


def main() -> None:
    """Main entry point for the cleanup script."""
    parser = argparse.ArgumentParser(description="Clean up orphaned test suppliers from Tripletex test environment")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    parser.add_argument("--prefix", default=TEST_SUPPLIER_PREFIX, help=f"Prefix to identify test suppliers (default: {TEST_SUPPLIER_PREFIX})")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    exit_code = cleanup_test_suppliers(dry_run=args.dry_run, prefix=args.prefix)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
