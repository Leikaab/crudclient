import os

import pytest

from .fiken_resources.setup import Company, Contact, FikenAPI, FikenConfig, User


@pytest.fixture
def api():
    config = FikenConfig()
    return FikenAPI(client_config=config)


def test_api_configuration(api):
    assert api.client.base_url == "https://api.fiken.no/api/v2"

    # Skip auth tests if no token is provided
    token = os.getenv("FIKEN_ACCESS_TOKEN", "")
    if token:
        # Check that we have an auth strategy set up
        assert api.client.config.auth_strategy is not None
        # Check that the auth strategy is a BearerAuth
        from crudclient.auth.bearer import BearerAuth
        assert isinstance(api.client.config.auth_strategy, BearerAuth)
        # Check that the token is set correctly
        assert api.client.config.auth_strategy.token == token
        assert len(api.client.config.auth_strategy.token) == 43
        assert api.client.config.auth_strategy.token != ""


def test_retrive_user(api):
    user = api.user.read()
    assert isinstance(user, User)
    assert user.name is not None
    assert user.email is not None


def test_list_companies(api):
    companies = api.companies.list()

    assert isinstance(companies, list)
    assert len(companies) > 0
    assert all(isinstance(company, Company) for company in companies)


def test_list_contacts(api):
    contacts = api.contacts.bind_company("fiken-demo-faktisk-plante-as2").list()
    assert isinstance(contacts, list)
    assert len(contacts) > 0
    assert all(isinstance(contact, Contact) for contact in contacts)
