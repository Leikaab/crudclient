from unittest.mock import patch

import pytest
import requests_mock

from crudclient.api import API
from crudclient.client import Client, ClientConfig
from crudclient.crud import Crud
from crudclient.exceptions import ClientInitializationError, InvalidClientError


class MockCrud(Crud):
    def __init__(self, client):
        super().__init__(client, "/test")


class MockAPI(API):
    client_class = Client

    def _register_endpoints(self):
        self.test_resource = MockCrud(self.client)


class TestAPI:
    @pytest.fixture
    def mock_client_config(self):
        return ClientConfig(base_url="https://api.example.com", api_key="test_key")

    @pytest.fixture
    def requests_mocker(self):
        with requests_mock.Mocker() as m:
            yield m

    def test_init_with_client(self, mock_client_config):
        # Test initializing API with an existing client
        client = Client(mock_client_config)
        api = MockAPI(client=client)
        assert api.client == client
        assert api.client_config is None

    def test_init_with_client_config(self, mock_client_config):
        # Test initializing API with a client configuration
        api = MockAPI(client_config=mock_client_config)
        assert isinstance(api.client, Client)
        assert api.client_config == mock_client_config

    def test_init_with_invalid_client(self):
        # Test that an InvalidClientError is raised when an invalid client is provided
        with pytest.raises(InvalidClientError):
            MockAPI(client="invalid_client")

    def test_init_with_invalid_client_config(self):
        # Test that an InvalidClientError is raised when an invalid client config is provided
        with pytest.raises(InvalidClientError):
            MockAPI(client_config="invalid_config")

    def test_register_endpoints(self, mock_client_config):
        # Test that endpoints are correctly registered
        api = MockAPI(client_config=mock_client_config)
        assert hasattr(api, "test_resource")
        assert isinstance(api.test_resource, MockCrud)

    def test_initialize_client_success(self, mock_client_config):
        # Test successful client initialization
        api = MockAPI(client_config=mock_client_config)
        assert isinstance(api.client, Client)

    def test_initialize_client_failure(self):
        # Test client initialization failure
        class FailingAPI(API):
            client_class = None

            def _register_endpoints(self):
                pass

        with pytest.raises(ClientInitializationError):
            FailingAPI(client_config=ClientConfig(base_url="https://api.example.com"))

    def test_context_manager(self, mock_client_config, requests_mocker):
        # Test the context manager functionality
        requests_mocker.get("https://api.example.com/test", json={"status": "success"})
        with MockAPI(client_config=mock_client_config) as api:
            assert isinstance(api, MockAPI)
            response = api.test_resource.list()
            assert response == '{"status": "success"}'

    def test_close(self, mock_client_config):
        # Test the close method
        api = MockAPI(client_config=mock_client_config)
        api.close()
        assert api.client is None

    def test_use_custom_resource(self, mock_client_config, requests_mocker):
        # Test using a custom resource
        api = MockAPI(client_config=mock_client_config)
        custom_resource = api.use_custom_resource(MockCrud)
        assert isinstance(custom_resource, MockCrud)

        requests_mocker.get("https://api.example.com/test", json={"status": "custom"})
        response = custom_resource.list()
        assert response == '{"status": "custom"}'

    @patch("crudclient.api.logger")
    def test_logging(self, mock_logger, mock_client_config):
        # Test that proper logging occurs during initialization
        MockAPI(client_config=mock_client_config)
        mock_logger.debug.assert_called_with(f"Initializing API class with client class Client, using client_config: {mock_client_config}")

    def test_api_args_kwargs(self, mock_client_config):
        # Test that additional args and kwargs are properly stored
        test_kwargs = {"a": "b", "c": "d"}
        api = MockAPI(client_config=mock_client_config, **test_kwargs)
        assert api.api_kwargs == test_kwargs

    def test_client_initialization_error_handling(self):
        # Test error handling during client initialization
        class ErrorClient(Client):
            def __init__(self, config):
                raise Exception("Test error")

        class ErrorAPI(API):
            client_class = ErrorClient

            def _register_endpoints(self):
                pass

        with pytest.raises(ClientInitializationError):
            ErrorAPI(client_config=ClientConfig(base_url="https://api.example.com"))

    def test_exit_with_exception(self, mock_client_config, requests_mocker):
        # Test that exceptions are properly propagated when using the context manager
        requests_mocker.get("https://api.example.com/test", json={"status": "success"})

        def raise_exception():
            with MockAPI(client_config=mock_client_config) as api:
                api.test_resource.list()  # This should work
                raise ValueError("Test exception")

        with pytest.raises(ValueError):
            raise_exception()

    def test_crud_operations(self, mock_client_config, requests_mocker):
        # Test that CRUD operations work correctly through the API
        api = MockAPI(client_config=mock_client_config)

        # Test list operation
        requests_mocker.get("https://api.example.com/test", json={"items": [1, 2, 3]})
        assert api.test_resource.list() == '{"items": [1, 2, 3]}'

        # Test create operation
        requests_mocker.post("https://api.example.com/test", json={"id": 4})
        assert api.test_resource.create({"name": "test"}) == '{"id": 4}'

        # Test get operation
        requests_mocker.get("https://api.example.com/test/4", json={"id": 4, "name": "test"})
        assert api.test_resource.get("4") == '{"id": 4, "name": "test"}'

        # Test update operation
        requests_mocker.put("https://api.example.com/test/4", json={"id": 4, "name": "updated"})
        assert api.test_resource.update("4", {"name": "updated"}) == '{"id": 4, "name": "updated"}'

        # Test delete operation
        requests_mocker.delete("https://api.example.com/test/4", json={"status": "deleted"})
        assert api.test_resource.delete("4") == '{"status": "deleted"}'

    def test_custom_action(self, mock_client_config, requests_mocker):
        # Test custom action on a resource
        api = MockAPI(client_config=mock_client_config)

        requests_mocker.post("https://api.example.com/test/4/activate", json={"status": "activated"})
        response = api.test_resource.custom_action("activate", resource_id="4")
        assert response == '{"status": "activated"}'
