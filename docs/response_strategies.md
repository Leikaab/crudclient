# Response Model Strategies

This document explains the response model strategy pattern used by the `crudclient.Crud` class to handle different API response formats when converting them into Pydantic models.

## Overview

APIs can return data in various structures. The response model strategy pattern provides a flexible way for your `Crud` subclass to interpret these different structures and correctly map them to your defined Pydantic `_datamodel`. This allows you to configure how single items and lists of items are extracted and validated.

## Available Strategies

The `crudclient` library provides two built-in strategies:

### DefaultResponseModelStrategy

This is the default strategy used by `Crud` if no other strategy is specified. It handles common, straightforward response formats:

1.  **Single item responses:** Expects a JSON object (dictionary) that directly maps to the fields of your `_datamodel`.
2.  **List responses:** Handles several formats:
    *   A JSON array (list) where each element is an object mapping to your `_datamodel`.
    *   A JSON object containing a specific key (defined in the `Crud` subclass's `_list_return_keys` attribute, defaulting to `["data", "results", "items"]`) whose value is the JSON array of items.
    *   A JSON object that maps to an `ApiResponse` model, if the `Crud` subclass defines an `_api_response_model`.

### PathBasedResponseModelStrategy

This strategy allows you to extract data from nested JSON structures using dot-notation paths. This is useful for APIs that wrap the core data within metadata or other containers.

1.  **Single item responses:** Uses the path specified in the `Crud` subclass's `_single_item_path` attribute to locate the JSON object representing the single item within the response (e.g., `"data.item"` accesses `response["data"]["item"]`).
2.  **List responses:** Uses the path specified in the `Crud` subclass's `_list_item_path` attribute to locate the JSON array of items within the response (e.g., `"data.items"` accesses `response["data"]["items"]`).

## Using Response Model Strategies

You configure the strategy within your `Crud` subclass definition.

### Default Strategy Usage

If the `DefaultResponseModelStrategy` meets your needs, no extra configuration is required.

```python
from crudclient import Crud
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

# Uses DefaultResponseModelStrategy by default
class UsersCrud(Crud[User]):
    _resource_path = "users"
    _datamodel = User
```

### Path-Based Strategy Usage

To use the path-based strategy, set the `_response_model_strategy` class attribute to `PathBasedResponseModelStrategy` and define the necessary path attributes (`_single_item_path`, `_list_item_path`).

```python
from crudclient import Crud
from crudclient.response_strategies import PathBasedResponseModelStrategy
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

class UsersCrud(Crud[User]):
    _resource_path = "users"
    _datamodel = User
    # Specify the strategy
    _response_model_strategy = PathBasedResponseModelStrategy
    # Specify paths to extract data
    _single_item_path = "data.user"
    _list_item_path = "data.users"
```

## Creating a Custom Strategy

For complex scenarios not covered by the built-in strategies, you can create your own. Subclass `crudclient.response_strategies.ResponseModelStrategy` and implement the `convert_single` and `convert_list` methods.

```python
from typing import Type, Optional, Union, List, TypeVar
from crudclient.response_strategies import ResponseModelStrategy
from crudclient.types import JSONDict, JSONList, RawResponse, ApiResponse
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class CustomStrategy(ResponseModelStrategy[T]):
    def __init__(
        self,
        datamodel: Optional[Type[T]] = None,
        api_response_model: Optional[Type[ApiResponse]] = None,
        # Add any other parameters your custom strategy needs
        custom_config_value: str = "default",
    ):
        # Ensure you call the superclass __init__ if it requires it
        # super().__init__(datamodel=datamodel, api_response_model=api_response_model)
        self.datamodel = datamodel
        self.api_response_model = api_response_model
        self.custom_config_value = custom_config_value
        # Initialize other attributes

    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]:
        # Implement your logic to extract and convert a single item
        # Example: Access data using self.custom_config_value
        if not self.datamodel:
            return data # Return raw if no datamodel
        # ... custom extraction logic ...
        extracted_data = data.get("payload", {})
        return self.datamodel.model_validate(extracted_data)

    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]:
        # Implement your logic to extract and convert a list of items
        if not self.datamodel:
            return data # Return raw if no datamodel
        # ... custom extraction logic ...
        items_data = data.get("items_list", [])
        return [self.datamodel.model_validate(item) for item in items_data]

# --- Usage in Crud subclass ---
class User(BaseModel):
    id: int
    name: str

class UsersCrud(Crud[User]):
    _resource_path = "users"
    _datamodel = User
    # Use your custom strategy
    _response_model_strategy = CustomStrategy
    # You might pass configuration via __init_subclass__ or other means
    # depending on how CustomStrategy is designed to be configured.
    # For this example, assume CustomStrategy can be configured directly
    # or picks up attributes from the Crud class if needed.
```

Then, assign your custom class to the `_response_model_strategy` attribute in your `Crud` subclass. Ensure your strategy's `__init__` method handles any required parameters (like `datamodel`) and any custom configuration it needs.

## Fallback Behavior

For backward compatibility, if the chosen strategy fails to convert the response (e.g., due to unexpected data format or an error within the strategy itself), the `Crud` class will attempt to fall back to its original, pre-strategy conversion logic. This helps ensure that existing code relying on the older behavior might still function even when introducing or modifying strategies. However, relying on this fallback is not recommended for new implementations; it's best to ensure your chosen strategy correctly handles all expected response formats.

## Why Use Strategies?

*   **Flexibility**: Adapt to various API response structures without complex subclassing of `Crud`.
*   **Reusability**: Define a strategy once and reuse it across multiple `Crud` endpoints sharing the same response format.
*   **Separation of Concerns**: Keeps the logic for handling response formats separate from the core CRUD operation logic.
*   **Extensibility**: Easily add new ways to handle responses as API requirements evolve.