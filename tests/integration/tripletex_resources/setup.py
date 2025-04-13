import logging
from typing import TypeVar

from dotenv import load_dotenv

from crudclient.response_strategies import ModelDumpable

from .auth import TripletexAuthStrategy
from .client import TripletexAPI, TripletexClient
from .config import TripletexConfig, TripletexTestConfig
from .crud import TripletexCrud
from .models import (
    Country,
    CountryResponse,
    Supplier,
    SupplierResponse,
    TokenSessionResponse,
)
from .resources import TripletexCountries, TripletexSuppliers

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
    "TripletexCountries",
    "TripletexSuppliers",
    "Country",
    "CountryResponse",
    "Supplier",
    "SupplierResponse",
    "TokenSessionResponse",
]
