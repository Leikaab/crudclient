import logging
from typing import TypeVar

from dotenv import load_dotenv

from crudclient.response_strategies import ModelDumpable

from .api import TripletexAPI
from .auth import TripletexAuthStrategy
from .client import TripletexClient
from .config import TripletexConfig, TripletexTestConfig
from .crud import TripletexCrud
from .endpoints import TripletexCompany, TripletexCountries, TripletexSuppliers
from .models import (
    Company,
    CompanyResponse,
    Country,
    CountryResponse,
    Supplier,
    SupplierResponse,
    TokenSessionResponse,
)

T = TypeVar("T", bound=ModelDumpable)

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Re-export all the classes
__all__ = [
    "TripletexAuthStrategy",
    "TripletexAPI",
    "TripletexClient",
    "TripletexConfig",
    "TripletexTestConfig",
    "TripletexCrud",
    "TripletexCompany",
    "TripletexCountries",
    "TripletexSuppliers",
    "Company",
    "CompanyResponse",
    "Country",
    "CountryResponse",
    "Supplier",
    "SupplierResponse",
    "TokenSessionResponse",
]
