import logging

from .api import API
from .client import Client
from .config import ClientConfig
from .crud import Crud
from .exceptions import APIError, ConfigurationError
from .models import ApiResponse
from .types import JSONDict, JSONList, RawResponse

# Set up logging for the library.
# By default, the library will not emit any logs.
# It's up to the consuming application to configure logging.
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__all__ = [
    "API",
    "Client",
    "ClientConfig",
    "Crud",
    "APIError",
    "ConfigurationError",
    "ApiResponse",
    "JSONDict",
    "JSONList",
    "RawResponse",
]

__version__ = "0.6.0"
