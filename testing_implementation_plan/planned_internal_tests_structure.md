# Planned File Structure: `tests/` (Internal Tests)

This structure outlines the organization for the internal tests of the `crudclient` library. It mirrors the main library structure, utilizes the testing utilities from `crudclient.testing`, and includes dedicated tests for those utilities.

```
tests/
├── __init__.py
├── README.md             # Overview of the internal test suite
├── conftest.py           # Global test fixtures (rarely needed, prefer specific confests)
├── debuglogger.py        # Existing debug utility (keep as is or refactor if needed)
├── integration/
│   ├── __init__.py
│   ├── conftest.py       # Shared fixtures for integration tests (e.g., VCR setup, env var loading)
│   ├── test_fiken.py     # Example integration test suite
│   ├── test_jsonplaceholder.py # Example integration test suite
│   ├── test_oneflow.py   # Example integration test suite
│   ├── test_tripletex.py # Example integration test suite
│   ├── fiken_resources/  # Resources specific to fiken tests
│   │   └── ...
│   ├── jsonplaceholder_resources/ # Resources specific to jsonplaceholder tests
│   │   └── ...
│   ├── oneflow_resources/ # Resources specific to oneflow tests
│   │   └── ...
│   └── tripletex_resources/ # Resources specific to tripletex tests
│       └── ...
└── unit/
    ├── __init__.py
    ├── conftest.py       # Shared fixtures for all unit tests (e.g., basic mock setup)
    ├── test_config.py    # Unit tests for crudclient/config.py
    ├── api/
    │   ├── __init__.py
    │   ├── conftest.py   # Fixtures specific to API tests
    │   └── test_api.py   # Unit tests for crudclient/api.py
    ├── auth/
    │   ├── __init__.py
    │   ├── conftest.py   # Fixtures specific to auth tests
    │   ├── test_auth_base.py
    │   ├── test_auth_basic.py
    │   ├── test_auth_bearer.py
    │   ├── test_auth_custom.py
    │   └── test_auth_failures.py # Example specific test focus
    ├── client/
    │   ├── __init__.py
    │   ├── conftest.py   # Fixtures specific to client tests
    │   ├── test_client_auth.py
    │   ├── test_client_base.py
    │   ├── test_client_data.py # Example specific test focus
    │   ├── test_client_error_handling.py
    │   └── test_client_initialization.py
    ├── crud/
    │   ├── __init__.py
    │   ├── conftest.py   # Fixtures specific to crud tests
    │   ├── test_crud_base.py
    │   ├── test_crud_endpoint.py
    │   ├── test_crud_operations.py
    │   └── test_response_conversion.py
    ├── http/
    │   ├── __init__.py
    │   ├── conftest.py   # Fixtures specific to http tests
    │   ├── test_error_handler.py
    │   ├── test_http_client.py
    │   ├── test_request.py
    │   ├── test_response.py
    │   ├── test_retry_handler.py
    │   └── test_session.py
    ├── response_strategies/
    │   ├── __init__.py
    │   ├── conftest.py   # Fixtures specific to response strategy tests
    │   ├── test_base_strategy.py
    │   ├── test_default_strategy.py
    │   └── test_path_based_strategy.py
    └── testing/            # << NEW: Unit tests FOR the crudclient.testing module
        ├── __init__.py
        ├── conftest.py   # Fixtures specific to testing the testing utilities
        ├── test_factory.py
        ├── test_exceptions.py
        ├── test_types.py
        ├── auth/
        │   ├── __init__.py
        │   ├── test_factory.py
        │   ├── test_strategies.py # Test mock auth strategies
        │   └── test_verification.py
        ├── core/
        │   ├── __init__.py
        │   ├── test_client.py
        │   ├── test_http_client.py
        │   ├── test_request.py
        │   └── test_response.py
        ├── crud/
        │   ├── __init__.py
        │   ├── test_factory.py
        │   ├── test_operations.py # Test mock crud operations
        │   └── test_verification.py
        ├── doubles/
        │   ├── __init__.py
        │   ├── test_data_store.py
        │   ├── test_fake_api.py
        │   └── test_stubs.py
        ├── helpers/
        │   ├── __init__.py
        │   ├── test_assertions.py
        │   └── test_config.py
        ├── response_builder/
        │   ├── __init__.py
        │   ├── test_builder.py # Test various response building functions
        │   └── test_pagination.py # etc.
        └── spy/
            ├── __init__.py
            ├── test_recorder.py
            ├── test_call_record.py
            └── test_spies.py # Test the spy wrappers themselves

```

**Key Changes & Rationale:**

1.  **Mirrors `crudclient`:** The `tests/unit/` subdirectories (api, auth, client, crud, http, response_strategies) directly correspond to the main library's structure.
2.  **Uses `crudclient.testing`:** All tests within `tests/unit/` (outside `tests/unit/testing/`) will now `import` necessary mocks, factories, and helpers from `crudclient.testing`.
3.  **No `tests/unit/mock_client/`:** This directory is removed from the plan, as its functionality is moved to `crudclient/testing/`.
4.  **`tests/unit/testing/`:** A new dedicated subdirectory is added to contain the unit tests *for* the `crudclient.testing` module itself. This keeps the tests of the tools separate from the tests using the tools. Its internal structure mirrors `crudclient/testing/`.
5.  **Modular `conftest.py`:** Follows the recommendation to place fixtures close to where they are used, with `conftest.py` files at different levels (`tests/conftest.py`, `tests/unit/conftest.py`, `tests/unit/client/conftest.py`, etc.).
6.  **Integration Tests:** Remain separate in `tests/integration/`, likely organized by the service they integrate with.

This structure provides a clear, modular organization for internal testing.