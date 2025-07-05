import os
import uuid

import pytest

from tests.integration.tripletex_resources.models import Company

from .tripletex_resources import TripletexAPI, TripletexTestConfig


@pytest.fixture
def api() -> TripletexAPI:
    """
    Create a Tripletex API client for testing.
    """
    config = TripletexTestConfig()
    return TripletexAPI(client_config=config)


def generate_unique_name():
    """
    Generate a unique name for a company to avoid conflicts in the test environment.
    """
    return f"Test Company {uuid.uuid4()}"


@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skip live API rate limiting tests in CI - file-based rate limiter doesn't work across matrix jobs",
)
@pytest.mark.no_parallel
def test_update_company_minimal(api):
    """
    Test updating a company with minimal data.

    This test updates only the company name without including ID or version.
    This tests the non-standard api_client behavior where the update works with just the name.

    NB! this test is passing in a consumer library that users our crudclient as a depenency.
    this test should never be changed in any way, as it would break the consumer library, and our intentions!

    """

    # Generate a unique name for the update
    new_name = generate_unique_name()

    # Create minimal update data - just the name
    updated_company: Company = api.company.update(data={"name": new_name})

    # Check that the company was updated correctly
    assert isinstance(updated_company, Company)
    assert updated_company.name == new_name

    read_company = api.company.read(updated_company.id)
    assert isinstance(read_company, Company)
    assert read_company.name == updated_company.name
    assert read_company.id == updated_company.id

    newest_name = generate_unique_name()

    updated_company2: Company = api.company.update(data={"name": newest_name})
    read_company2 = api.company.read(updated_company.id)

    assert updated_company.id == updated_company2.id == read_company.id == read_company2.id
    assert updated_company2.name == read_company2.name
