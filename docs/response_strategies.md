# Response Model Strategies

This document explains the response model strategy pattern implemented in the `Crud` class for handling different API response formats.

## Overview

The response model strategy pattern provides a flexible way to handle different API response formats when converting them to Pydantic models. This is particularly useful when working with APIs that have different response structures or when you need to extract data from nested structures.

## Available Strategies

### DefaultResponseModelStrategy

The `DefaultResponseModelStrategy` implements the original behavior of the `Crud` class for backward compatibility. It handles the following response formats:

1. Single item responses:
   - Expects a dictionary that can be directly converted to the data model.

2. List responses:
   - A list of dictionaries that can be directly converted to the data model.
   - A dictionary with a key from `_list_return_keys` (default: "data", "results", "items") containing a list of items.
   - A dictionary that can be converted to an `ApiResponse` model if `_api_response_model` is specified.

### PathBasedResponseModelStrategy

The `PathBasedResponseModelStrategy` allows for extracting data from nested structures using dot notation path expressions. This is useful when working with APIs that return deeply nested data.

1. Single item responses:
   - Uses `_single_item_path` to extract data from the response (e.g., "data.item" to access `response["data"]["item"]`).
   - Optionally applies a pre-transform function to the data before extraction.

2. List responses:
   - Uses `_list_item_path` to extract list data from the response (e.g., "data.items" to access `response["data"]["items"]`).
   - Optionally applies a pre-transform function to the data before extraction.
   - Falls back to using the `ApiResponse` model if specified.

## Using Response Model Strategies

### Basic Usage

To use the default strategy, you don't need to do anything special. The `Crud` class will use the `DefaultResponseModelStrategy` by default.

```python
class UsersCrud(Crud[User]):
    _resource_path = "users"
    _datamodel = User
```

### Using the Path-Based Strategy

To use the path-based strategy, set the `_response_model_strategy` class attribute to `PathBasedResponseModelStrategy` and specify the path expressions:

```python
class UsersCrud(Crud[User]):
    _resource_path = "users"
    _datamodel = User
    _response_model_strategy = PathBasedResponseModelStrategy
    _single_item_path = "data.user"
    _list_item_path = "data.users"
```

### Creating a Custom Strategy

You can create your own strategy by subclassing `ResponseModelStrategy` and implementing the required methods:

```python
class CustomResponseModelStrategy(ResponseModelStrategy[T]):
    def __init__(
        self,
        datamodel: Optional[Type[T]] = None,
        api_response_model: Optional[Type[ApiResponse]] = None,
        # Add any additional parameters your strategy needs
    ):
        self.datamodel = datamodel
        self.api_response_model = api_response_model
        # Initialize any additional attributes

    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]:
        # Implement your custom logic for converting single item responses
        pass

    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]:
        # Implement your custom logic for converting list responses
        pass
```

Then use it in your `Crud` subclass:

```python
class UsersCrud(Crud[User]):
    _resource_path = "users"
    _datamodel = User
    _response_model_strategy = CustomResponseModelStrategy
    # Add any additional configuration your strategy needs
```

## Fallback Behavior

For backward compatibility, if the strategy fails to convert the response, the `Crud` class will fall back to the original behavior. This ensures that existing code continues to work even with the new strategy pattern.

## Benefits

1. **Flexibility**: Easily adapt to different API response formats without subclassing.
2. **Reusability**: Create strategies that can be reused across different `Crud` subclasses.
3. **Maintainability**: Separate the response conversion logic from the CRUD operations.
4. **Extensibility**: Add new strategies as needed without modifying the core `Crud` class.