import os

import pytest

from .fiken_resources.setup import Company, Contact, FikenAPI, FikenConfig, User


@pytest.fixture
def api():
    config = FikenConfig()
    return FikenAPI(client_config=config)


def test_api_configuration(api):
    assert api.client.base_url == "https://api.fiken.no/api/v2"
    assert api.client.config.api_key == os.getenv("FIKEN_ACCESS_TOKEN", "")
    assert len(api.client.config.api_key) == 43
    assert api.client.config.api_key != ""
    assert len(api.client.config.api_key) > 0


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
