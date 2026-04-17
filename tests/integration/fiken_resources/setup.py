import os
from typing import Any, List, Optional, Type, TypeVar, cast

from dotenv import load_dotenv

from crudclient.api import API
from crudclient.auth import BearerAuth
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud import Crud
from crudclient.response_strategies import ModelDumpable
from crudclient.utils.endpoint_builder import EndpointBuilder

from .models import Company, Contact, User

# Load environment variables from .env file
load_dotenv()


T = TypeVar("T", bound=ModelDumpable)


# Custom EndpointBuilder classes for Fiken API
class FikenEndpointBuilder(EndpointBuilder):
    """EndpointBuilder for standard Fiken resources that need company context."""

    endpoint_prefix = ["companies"]
    prefix_mode = "append"

    def get_prefix_segments(self, crud_instance: Optional[Any] = None) -> List[str]:
        """Override to add dynamic company slug from crud_instance."""
        segments = super().get_prefix_segments(crud_instance)

        # Add company slug if available from crud_instance
        if crud_instance and hasattr(crud_instance, "_company_slug") and crud_instance._company_slug:
            segments.append(crud_instance._company_slug)

        return segments


class FikenRootEndpointBuilder(EndpointBuilder):
    """EndpointBuilder for Fiken resources that don't need company context."""

    endpoint_prefix = []
    prefix_mode = "override"


class FikenConfig(ClientConfig):
    hostname = "https://api.fiken.no/api/"
    version = "v2"
    api_key = os.getenv("FIKEN_ACCESS_TOKEN")

    def __init__(self) -> None:
        super().__init__()
        if self.api_key:
            self.auth_strategy = BearerAuth(access_token=self.api_key)


class FikenCrud(Crud[T]):

    _company_slug: str | None = None

    @property
    def endpoint_builder_class(self) -> Type[EndpointBuilder]:
        """Use FikenEndpointBuilder for company-scoped resources."""
        return FikenEndpointBuilder

    def bind_company(self, company_slug: str) -> "FikenCrud[T]":
        self._company_slug = company_slug
        return self


class FikenUser(FikenCrud[User]):
    _resource_path = "user"
    _datamodel = User
    allowed_actions = ["read"]

    @property
    def endpoint_builder_class(self) -> Type[EndpointBuilder]:
        """Use FikenRootEndpointBuilder for user endpoint (no company context)."""
        return FikenRootEndpointBuilder

    def read(self, *args: Any, **kwargs: Any) -> User:
        response = super().custom_action(action="", method="get")
        return cast(User, response)


class FikenCompanies(FikenCrud[Company]):
    _resource_path = "companies"
    _datamodel = Company
    allowed_actions = ["list"]

    @property
    def endpoint_builder_class(self) -> Type[EndpointBuilder]:
        """Use FikenRootEndpointBuilder for companies endpoint (no company context)."""
        return FikenRootEndpointBuilder


class FikenContacts(FikenCrud[Contact]):
    _resource_path = "contacts"
    _datamodel = Contact


class FikenAPI(API):
    client_class = Client

    def _register_endpoints(self) -> None:
        assert self.client is not None, "Client is required!"
        self.user = FikenUser(self.client)
        self.companies = FikenCompanies(self.client)
        self.contacts = FikenContacts(self.client)
