from crudclient.client import Client


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
