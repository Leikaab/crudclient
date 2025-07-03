from crudclient.api import API

from .client import TripletexClient
from .endpoints import (
    LedgerGroup,
    TripletexCompany,
    TripletexCountries,
    TripletexSuppliers,
)


class TripletexAPI(API):
    """
    API client for Tripletex.
    """

    client_class = TripletexClient

    def _register_endpoints(self) -> None:
        """
        Register API endpoints.
        """
        assert self.client is not None, "Client is required!"
        self.countries = TripletexCountries(self.client)
        self.suppliers = TripletexSuppliers(self.client)
        self.company = TripletexCompany(self.client)

    def _register_groups(self) -> None:
        """
        Register top-level ResourceGroup instances.

        This method instantiates the LedgerGroup which handles operations on /ledger
        and contains nested resources for ledger-specific vouchers and historical vouchers.
        """
        assert self.client is not None, "Client is required!"
        self.ledger = LedgerGroup(self.client, parent=None)
