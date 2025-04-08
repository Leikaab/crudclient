"""
Tests for the enhanced test doubles.
"""

import pytest
from typing import Any, Dict, List, Optional

from crudclient.client import Client
from crudclient.api import API
from crudclient.config import ClientConfig

from tests.unit.mock_client.fake_api import FakeAPI, FakeDatabase
from tests.unit.mock_client.stub_client import StubClient, StubAPI, StubCrud
from tests.unit.mock_client.spy_modules.base import SpyBase
from tests.unit.mock_client.spy_modules.client_spy import ClientSpy
from tests.unit.mock_client.spy_modules.api_spy import ApiSpy
from tests.unit.mock_client.spy_modules.crud_spy import CrudSpy


class TestModel:
    """Test model for API tests."""

    def __init__(self, id: Optional[str] = None, name: Optional[str] = None, value: Any = None, **kwargs):
        self.id = id
        self.name = name
        self.value = value
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestFakeAPI:
    """Tests for the FakeAPI class."""

    def test_fake_api_crud_operations(self):
        """Test basic CRUD operations with FakeAPI."""
        # Create a FakeAPI instance
        api = FakeAPI()

        # Register an endpoint
        users = api.register_endpoint("users", "/users", TestModel)

        # Create a user
        user = users.create({"name": "John Doe", "email": "john@example.com"})
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.id is not None  # ID should be generated

        # Get the user
        retrieved_user = users.get(user.id)
        assert retrieved_user.id == user.id
        assert retrieved_user.name == "John Doe"

        # Update the user
        updated_user = users.update(user.id, {"name": "Jane Doe"})
        assert updated_user.id == user.id
        assert updated_user.name == "Jane Doe"
        assert updated_user.email == "john@example.com"  # Unchanged field

        # List users
        user_list = users.list()
        assert len(user_list) == 1
        assert user_list[0].id == user.id

        # Delete the user
        result = users.delete(user.id)
        assert result is True

        # List should be empty now
        assert len(users.list()) == 0

    def test_fake_api_filtering(self):
        """Test filtering with FakeAPI."""
        # Create a FakeAPI instance
        api = FakeAPI()

        # Register an endpoint
        products = api.register_endpoint("products", "/products")

        # Create some products
        products.create({"name": "Product A", "price": 10, "category": "electronics"})
        products.create({"name": "Product B", "price": 20, "category": "electronics"})
        products.create({"name": "Product C", "price": 30, "category": "books"})
        products.create({"name": "Product D", "price": 40, "category": "books"})

        # Filter by category
        electronics = products.list(category="electronics")
        assert len(electronics) == 2
        assert electronics[0]["name"] == "Product A"
        assert electronics[1]["name"] == "Product B"

        # Filter by price using operator
        expensive = products.list(filters={"price": {"$gt": 25}})
        assert len(expensive) == 2
        assert expensive[0]["name"] == "Product C"
        assert expensive[1]["name"] == "Product D"

        # Combined filter
        expensive_electronics = products.list(
            category="electronics",
            filters={"price": {"$gt": 15}}
        )
        assert len(expensive_electronics) == 1
        assert expensive_electronics[0]["name"] == "Product B"

    def test_fake_api_sorting_and_pagination(self):
        """Test sorting and pagination with FakeAPI."""
        # Create a FakeAPI instance
        api = FakeAPI()

        # Register an endpoint
        items = api.register_endpoint("items", "/items")

        # Create some items
        for i in range(10):
            items.create({"name": f"Item {i}", "order": i})

        # Test sorting (ascending)
        sorted_items = items.list(sort_by="order")
        assert len(sorted_items) == 10
        assert sorted_items[0]["order"] == 0
        assert sorted_items[9]["order"] == 9

        # Test sorting (descending)
        sorted_items_desc = items.list(sort_by="order", sort_desc=True)
        assert len(sorted_items_desc) == 10
        assert sorted_items_desc[0]["order"] == 9
        assert sorted_items_desc[9]["order"] == 0

        # Test pagination
        page1 = items.list(page=1, page_size=3, sort_by="order")
        assert len(page1) == 3
        assert page1[0]["order"] == 0
        assert page1[2]["order"] == 2

        page2 = items.list(page=2, page_size=3, sort_by="order")
        assert len(page2) == 3
        assert page2[0]["order"] == 3
        assert page2[2]["order"] == 5

    def test_fake_api_bulk_operations(self):
        """Test bulk operations with FakeAPI."""
        # Create a FakeAPI instance
        api = FakeAPI()

        # Register an endpoint
        tasks = api.register_endpoint("tasks", "/tasks")

        # Bulk create
        created_tasks = tasks.bulk_create([
            {"name": "Task 1", "completed": False},
            {"name": "Task 2", "completed": False},
            {"name": "Task 3", "completed": False},
        ])
        assert len(created_tasks) == 3

        # Get IDs for later use
        task_ids = [task["id"] for task in created_tasks]

        # Bulk update
        updated_tasks = tasks.bulk_update([
            {"id": task_ids[0], "completed": True},
            {"id": task_ids[1], "completed": True},
        ])
        assert len(updated_tasks) == 2
        assert updated_tasks[0]["completed"] is True
        assert updated_tasks[1]["completed"] is True

        # Verify the updates
        all_tasks = tasks.list()
        assert len(all_tasks) == 3
        assert sum(1 for task in all_tasks if task["completed"]) == 2

        # Bulk delete
        deleted_count = tasks.bulk_delete([task_ids[0], task_ids[2]])
        assert deleted_count == 2

        # Verify the deletions
        remaining_tasks = tasks.list()
        assert len(remaining_tasks) == 1
        assert remaining_tasks[0]["id"] == task_ids[1]


class TestStubClient:
    """Tests for the StubClient class."""

    def test_stub_client_configuration(self):
        """Test configuring the StubClient."""
        # Create a StubClient
        client = StubClient({"base_url": "https://api.example.com"})

        # Configure responses
        client.configure_get(response={"data": [{"id": 1, "name": "Test"}]})
        client.configure_post(response={"id": 2, "name": "Created"})

        # Test the configured responses
        get_response = client.get("/items")
        assert "data" in get_response
        assert get_response["data"][0]["name"] == "Test"

        post_response = client.post("/items", json={"name": "New Item"})
        assert post_response["name"] == "Created"

    def test_stub_client_custom_handlers(self):
        """Test custom handlers in StubClient."""
        # Create a StubClient
        client = StubClient({"base_url": "https://api.example.com"})

        # Configure a custom handler
        def get_handler(endpoint, params=None):
            if endpoint == "/users":
                return {"data": [{"id": 1, "name": "User 1"}]}
            elif endpoint == "/items":
                return {"data": [{"id": 1, "name": "Item 1"}]}
            return {"error": "Not found"}

        client.configure_get(handler=get_handler)

        # Test the custom handler
        users_response = client.get("/users")
        assert users_response["data"][0]["name"] == "User 1"

        items_response = client.get("/items")
        assert items_response["data"][0]["name"] == "Item 1"

        error_response = client.get("/unknown")
        assert "error" in error_response


class TestStubAPI:
    """Tests for the StubAPI class."""

    def test_stub_api_configuration(self):
        """Test configuring the StubAPI."""
        # Create a StubAPI
        api = StubAPI()

        # Register an endpoint and configure it
        users = api.register_endpoint("users", "/users", TestModel)
        users.configure_list(response=[
            TestModel(id="1", name="User 1"),
            TestModel(id="2", name="User 2"),
        ])
        users.configure_get(response=TestModel(id="1", name="User 1"))

        # Test the configured responses
        user_list = users.list()
        assert len(user_list) == 2
        assert user_list[0].name == "User 1"

        user = users.get("1")
        assert user.id == "1"
        assert user.name == "User 1"

    def test_stub_api_custom_handlers(self):
        """Test custom handlers in StubAPI."""
        # Create a StubAPI
        api = StubAPI()

        # Register an endpoint and configure custom handlers
        products = api.register_endpoint("products", "/products")

        def list_handler(**kwargs):
            category = kwargs.get("category")
            if category == "electronics":
                return [{"id": "1", "name": "Product 1", "category": "electronics"}]
            elif category == "books":
                return [{"id": "2", "name": "Book 1", "category": "books"}]
            return []

        products.configure_list(handler=list_handler)

        # Test the custom handler
        electronics = products.list(category="electronics")
        assert len(electronics) == 1
        assert electronics[0]["category"] == "electronics"

        books = products.list(category="books")
        assert len(books) == 1
        assert books[0]["category"] == "books"

        other = products.list(category="other")
        assert len(other) == 0


class TestClientSpy:
    """Tests for the ClientSpy class."""

    def test_client_spy_records_calls(self):
        """Test that ClientSpy records method calls."""
        # Create a stub client to use as delegate
        stub = StubClient({"base_url": "https://api.example.com"})
        stub.configure_get(response={"data": [{"id": 1}]})

        # Create a spy that delegates to the stub
        spy = ClientSpy({"base_url": "https://api.example.com"}, delegate=stub)

        # Make some calls
        spy.get("/users")
        spy.post("/users", json={"name": "New User"})

        # Verify the calls were recorded
        spy.assert_called("get")
        spy.assert_called("post")
        spy.assert_called_with("get", "/users")
        spy.assert_called_with("post", "/users", json={"name": "New User"})

        # Check call count
        spy.assert_call_count("get", 1)
        spy.assert_call_count("post", 1)

    def test_client_spy_verification_helpers(self):
        """Test the verification helpers in ClientSpy."""
        # Create a spy
        spy = ClientSpy({"base_url": "https://api.example.com"})

        # Make some calls
        spy.get("/users")
        spy.get("/items")
        spy.post("/users", json={"name": "User 1"})

        # Verify endpoints were called
        spy.assert_endpoint_called("/users")
        spy.assert_endpoint_called("/items")
        spy.assert_endpoint_called_with_method("get", "/users")
        spy.assert_endpoint_called_with_method("post", "/users")

        # Verify JSON payload
        spy.assert_json_payload_sent("post", "/users", {"name": "User 1"})


class TestApiSpy:
    """Tests for the ApiSpy class."""

    def test_api_spy_records_calls(self):
        """Test that ApiSpy records method calls."""
        # Create a stub API to use as delegate
        stub = StubAPI()
        users = stub.register_endpoint("users", "/users")
        users.configure_list(response=[{"id": "1", "name": "User 1"}])

        # Create a spy that delegates to the stub
        spy = ApiSpy(delegate=stub)

        # Register an endpoint (this should be recorded)
        spy.register_endpoint("products", "/products")

        # Make some calls through the delegate's endpoint
        spy.users.list()

        # Verify the calls were recorded
        spy.assert_called("register_endpoint")
        spy.assert_called_with("register_endpoint", "products", "/products")

        # Check endpoint registration
        spy.assert_endpoint_registered("products")


class TestCrudSpy:
    """Tests for the CrudSpy class."""

    def test_crud_spy_records_calls(self):
        """Test that CrudSpy records method calls."""
        # Create a stub CRUD to use as delegate
        stub = StubCrud("users", "/users")
        stub.configure_list(response=[{"id": "1", "name": "User 1"}])
        stub.configure_get(response={"id": "1", "name": "User 1"})
        stub.configure_create(response={"id": "2", "name": "User 2"})

        # Create a spy that delegates to the stub
        spy = CrudSpy(delegate=stub)

        # Make some calls
        spy.list()
        spy.get("1")
        spy.create({"name": "User 2"})

        # Verify the calls were recorded
        spy.assert_called("list")
        spy.assert_called("get")
        spy.assert_called("create")

        spy.assert_called_with("get", "1")
        spy.assert_called_with("create", {"name": "User 2"})

        # Check resource operations
        spy.assert_resource_created({"name": "User 2"})


def test_integration_of_test_doubles():
    """Test the integration of all test doubles."""
    # Create a FakeAPI for the backend
    fake_api = FakeAPI()
    users = fake_api.register_endpoint("users", "/users", TestModel)

    # Add some data
    users.create({"name": "User 1", "email": "user1@example.com"})
    users.create({"name": "User 2", "email": "user2@example.com"})

    # Create a StubClient that returns predefined responses
    stub_client = StubClient({"base_url": "https://api.example.com"})
    stub_client.configure_get(response={"data": [{"id": "1", "name": "User 1"}]})

    # Create a ClientSpy to track calls
    client_spy = ClientSpy({"base_url": "https://api.example.com"}, delegate=stub_client)

    # Create a StubAPI that uses the spy client
    stub_api = StubAPI(client=client_spy)
    api_users = stub_api.register_endpoint("users", "/users", TestModel)

    # Configure the stub API endpoint
    api_users.configure_list(response=[
        TestModel(id="1", name="User 1"),
        TestModel(id="2", name="User 2"),
    ])

    # Create a CrudSpy to track calls to the API endpoint
    crud_spy = CrudSpy(delegate=api_users)

    # Make some calls through the spy
    users_list = crud_spy.list()

    # Verify the results
    assert len(users_list) == 2
    assert users_list[0].name == "User 1"

    # Verify the calls were recorded
    crud_spy.assert_called("list")

    # The client spy should not have been called because we used the stub API's response
    client_spy.assert_not_called("get")
