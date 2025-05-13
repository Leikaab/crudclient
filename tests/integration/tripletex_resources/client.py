from crudclient.api import API
from crudclient.client import Client

from .resources import TripletexCompany, TripletexCountries, TripletexSuppliers


class TripletexClient(Client):
    """
    Custom client for Tripletex API.
    """

    def _handle_response(self, response):
        """
        Handle the response from the API.

        This method overrides the default _handle_response method to handle 204 No Content responses.
        """
        if response.status_code == 204:
            return {}

        return super()._handle_response(response)


class TripletexAPI(API):
    """
    API client for Tripletex.
    """

    client_class = TripletexClient

    def _register_endpoints(self):
        """
        Register API endpoints.
        """
        assert self.client is not None, "Client is required!"
        self.countries = TripletexCountries(self.client)
        self.suppliers = TripletexSuppliers(self.client)
        self.company = TripletexCompany(self.client)
