import os
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

from crudclient.api import API
from crudclient.client import Client, ClientConfig
from crudclient.crud import Crud
from crudclient.models import ApiResponse
from crudclient.types import JSONDict

from .models import Company, User

T = TypeVar("T")


class FikenConfig(ClientConfig):
    hostname: str = "https://api.fiken.no/api/"
    version: str = "v2"
    api_key: str = os.getenv("FIKEN_ACCESS_TOKEN", "")
    timeout: Optional[float] = 10.0
    retries: Optional[int] = 3


class FikenCrud(Crud[T]):

    _company_slug: str | None = None

    @classmethod
    def _endpoint_prefix(cls) -> tuple[str | None] | list[str | None]:
        return ["companies", cls._company_slug]

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

    @classmethod
    def _endpoint_prefix(cls) -> tuple[str | None] | list[str | None]:
        return [""]


class FikenCompanies(FikenCrud[Company]):
    _resource_path = "companies"
    _datamodel = Company
    allowed_actions = ["list"]

    @classmethod
    def _endpoint_prefix(cls) -> tuple[str | None] | list[str | None]:
        return [""]


class FikenContacts(FikenCrud[User]):
    _resource_path = "contacts"

    def _validate_list_return(self, data: Dict[str, Any] | List[Dict[str, Any]] | bytes | str) -> List[Dict[str, Any]] | List[User] | ApiResponse:
        return cast(List[Dict[str, Any]], data)


class FikenAPI(API):
    client_class = Client

    def _register_endpoints(self):
        self.user = FikenUser(self.client)
        self.companies = FikenCompanies(self.client)
        self.contacts = FikenContacts(self.client)
