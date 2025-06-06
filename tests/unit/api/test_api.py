import pytest

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.exceptions import (
    ConfigurationError,  # Replaced ClientInitializationError, InvalidClientError
)

# Import fixtures from conftest.py
from .conftest import MockAPI, MockCrud


class TestAPI:

    def test_init_with_client(self, default_mock_client_config):
        # Arrange
        client = Client(default_mock_client_config)

        # Act
        api = MockAPI(client=client)

        # Assert
        assert api.client == client
        assert api.client_config is None

    def test_init_with_client_config(self, default_mock_client_config):
        # Arrange

        # Act
        api = MockAPI(client_config=default_mock_client_config)

        # Assert
        assert isinstance(api.client, Client)
        assert api.client_config == default_mock_client_config

    def test_init_with_invalid_client(self):
        # Arrange
        invalid_client = "invalid_client"

        # Act & Assert
        with pytest.raises(ConfigurationError):
            MockAPI(client=invalid_client)  # type: ignore

    def test_init_with_invalid_client_config(self):
        # Arrange
        invalid_config = "invalid_config"

        # Act & Assert
        with pytest.raises(ConfigurationError):
            MockAPI(client_config=invalid_config)  # type: ignore

    def test_register_endpoints(self, default_mock_client_config):
        # Arrange

        # Act
        api = MockAPI(client_config=default_mock_client_config)

        # Assert
        assert hasattr(api, "test_resource")
        assert isinstance(api.test_resource, MockCrud)

    def test_initialize_client_success(self, default_mock_client_config):
        # Arrange

        # Act
        api = MockAPI(client_config=default_mock_client_config)

        # Assert
        assert isinstance(api.client, Client)

    def test_initialize_client_failure(self, standard_data):
        # Arrange
        class FailingAPI(API):
            client_class = None

            def _register_endpoints(self):
                pass

            def _register_groups(self):
                pass

        client_config = ClientConfig(hostname=standard_data.get("hostname"))

        # Act & Assert
        with pytest.raises(ConfigurationError):
            FailingAPI(client_config=client_config)

    def test_context_manager(self, default_mock_client_config, requests_mocker, standard_data):
        # Arrange
        requests_mocker.get(standard_data.get("full_url"), json={"data": [1, 2, 3]})

        # Act
        with MockAPI(client_config=default_mock_client_config) as api:
            assert isinstance(api, MockAPI)
            response = api.test_resource.list()

        # Assert
        assert response == [1, 2, 3]

    def test_close(self, default_mock_client_config, mocker):
        """Ensure API.close closes the underlying client and resets attributes."""

        # Arrange
        api = MockAPI(client_config=default_mock_client_config)
        client = api.client
        assert client is not None  # mypy/pylint guard
        close_mock = mocker.patch.object(client, "close", wraps=client.close)
        log_mock = mocker.patch("crudclient.api.logger")

        # Act
        api.close()

        # Assert
        close_mock.assert_called_once_with()
        log_mock.info.assert_has_calls(
            [
                mocker.call("Closing client session."),
                mocker.call("Client session fully closed and client set to None."),
            ]
        )
        assert api.client is None
        assert client.http_client.session_manager.is_closed

    def test_use_custom_resource(self, default_mock_client_config, requests_mocker, standard_data):
        # Arrange
        api = MockAPI(client_config=default_mock_client_config)
        requests_mocker.get(standard_data.get("full_url"), json={"data": [1, 2, 3]})

        # Act
        custom_resource = api.use_custom_resource(MockCrud)
        response = custom_resource.list()

        # Assert
        assert isinstance(custom_resource, MockCrud)
        assert response == [1, 2, 3]

    def test_logging(self, default_mock_client_config, mocker):
        # Arrange
        mock_logger = mocker.patch("crudclient.api.logger")

        # Act
        MockAPI(client_config=default_mock_client_config)

        # Assert
        mock_logger.debug.assert_called_with(f"Initializing API class with client class Client, using client_config: {default_mock_client_config}")

    def test_api_args_kwargs(self, default_mock_client_config):
        # Arrange
        test_kwargs = {"a": "b", "c": "d"}

        # Act
        api = MockAPI(client=None, client_config=default_mock_client_config, **test_kwargs)

        # Assert
        assert api.api_kwargs == test_kwargs

    def test_client_initialization_error_handling(self):
        # Arrange
        class ErrorClient(Client):
            def __init__(self, config):
                raise Exception("Test error")

        class ErrorAPI(API):
            client_class = ErrorClient

            def _register_endpoints(self):
                pass

            def _register_groups(self):
                pass

        client_config = ClientConfig(hostname="https://api.example.com")

        # Act & Assert
        with pytest.raises(ConfigurationError):
            ErrorAPI(client_config=client_config)

    def test_exit_with_exception(self, default_mock_client_config, requests_mocker, standard_data):
        # Arrange
        requests_mocker.get(standard_data.get("full_url"), json={"status": "success"})

        def raise_exception():
            with MockAPI(client_config=default_mock_client_config) as api:
                api.test_resource.list()  # type: ignore
                raise ValueError("Test exception")

        # Act & Assert
        with pytest.raises(ValueError):
            raise_exception()

    def test_crud_operations(self, default_mock_client_config, requests_mocker, standard_data):
        # Arrange
        api = MockAPI(client_config=default_mock_client_config)
        hostname = standard_data.get("full_url")

        # Setup mock responses
        requests_mocker.get(hostname, json={"items": [1, 2, 3]})
        requests_mocker.post(hostname, json={"id": 4})
        requests_mocker.get(f"{hostname}/4", json={"id": 4, "name": "test"})
        requests_mocker.put(f"{hostname}/4", json={"id": 4, "name": "updated"})
        requests_mocker.delete(f"{hostname}/4", json={"status": "deleted"})

        # Act & Assert - List operation
        list_response = api.test_resource.list()
        assert list_response == [1, 2, 3]

        # Act & Assert - Create operation
        create_response = api.test_resource.create({"name": "test"})
        assert create_response == {"id": 4}

        # Act & Assert - Get operation
        read_response = api.test_resource.read("4")
        assert read_response == {"id": 4, "name": "test"}

        # Act & Assert - Update operation
        update_response = api.test_resource.update("4", {"name": "updated"})
        assert update_response == {"id": 4, "name": "updated"}

        # Act & Assert - Delete operation
        delete_response = api.test_resource.destroy("4")
        assert delete_response is None

    def test_custom_action(self, default_mock_client_config, requests_mocker, standard_data):
        # Arrange
        api = MockAPI(client_config=default_mock_client_config)
        requests_mocker.post(f"{standard_data.get('full_url')}/4/activate", json={"status": "activated"})

        # Act
        response = api.test_resource.custom_action("activate", resource_id="4")

        # Assert
        assert response == {"status": "activated"}
