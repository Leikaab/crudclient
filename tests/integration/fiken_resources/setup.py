import os
from typing import Optional, TypeVar, cast

from crudclient.api import API
from crudclient.client import Client, ClientConfig
from crudclient.crud import Crud

from .models import Company, Contact, User

T = TypeVar("T")


class FikenConfig(ClientConfig):
    hostname: str = "https://api.fiken.no/api/"
    version: str = "v2"
    api_key: str = os.getenv("FIKEN_ACCESS_TOKEN", "")
    timeout: Optional[float] = 10.0
    retries: Optional[int] = 3


class FikenCrud(Crud[T]):

    _company_slug: str | None = None

    def _endpoint_prefix(self) -> tuple[str | None] | list[str | None]:
        return ["companies", self._company_slug]

    def bind_company(self, company_slug: str):
        self._company_slug = company_slug
        return self


class FikenUser(FikenCrud[User]):
    _resource_path = "user"
    _datamodel = User
    allowed_actions = ["read"]

    def read(self, *args) -> User:
        response = super().custom_action(action="", method="GET")
        return cast(User, response)

    def _endpoint_prefix(self) -> tuple[str | None] | list[str | None]:
        return [""]


class FikenCompanies(FikenCrud[Company]):
    _resource_path = "companies"
    _datamodel = Company
    allowed_actions = ["list"]

    @classmethod
    def _endpoint_prefix(self) -> tuple[str | None] | list[str | None]:
        return [""]


class FikenContacts(FikenCrud[Contact]):
    _resource_path = "contacts"
    _datamodel = Contact


class FikenAPI(API):
    client_class = Client

    def _register_endpoints(self):
        self.user = FikenUser(self.client)
        self.companies = FikenCompanies(self.client)
        self.contacts = FikenContacts(self.client)
