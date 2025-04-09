# Planned File Structure: `crudclient/testing/`

This structure reflects the design plan for the optional testing utilities module, intended for both internal use and potential consumer use via `pip install crudclient[testing]`.

```
crudclient/
├── __init__.py
├── api.py
├── client.py
├── config.py
├── crud.py
├── exceptions.py
├── models.py
├── response_strategies.py
├── types.py
├── auth/
│   ├── __init__.py
│   ├── base.py
│   ├── basic.py
│   ├── bearer.py
│   └── custom.py
├── crud/
│   ├── __init__.py
│   ├── base.py
│   ├── endpoint.py
│   ├── operations.py
│   └── response_conversion.py
├── http/
│   ├── __init__.py
│   ├── client.py
│   ├── errors.py
│   ├── request.py
│   ├── response.py
│   ├── retry.py
│   └── session.py
├── response_strategies/
│   ├── __init__.py
│   ├── base.py
│   ├── default.py
│   ├── path_based.py
│   └── types.py
└── testing/                 # << NEW Testing Utilities Module
    ├── __init__.py          # Exports public interface (factories, doubles, helpers)
    ├── README.md            # Documentation for this module
    ├── exceptions.py        # Testing-specific exceptions
    ├── factory.py           # Main MockClientFactory
    ├── types.py             # Shared types for testing module
    ├── verification.py      # High-level verification coordination (optional)
    ├── auth/
    │   ├── __init__.py
    │   ├── base.py          # MockAuthStrategy base
    │   ├── basic.py         # MockBasicAuth
    │   ├── bearer.py        # MockBearerAuth
    │   ├── custom.py        # MockCustomAuth
    │   ├── factory.py       # MockAuthFactory
    │   └── verification.py  # Auth-specific verification helpers
    ├── core/
    │   ├── __init__.py
    │   ├── client.py        # MockClient implementation
    │   ├── http_client.py   # MockHTTPClient implementation
    │   ├── request.py       # MockRequest / request matching utils
    │   └── response.py      # MockResponse / response simulation utils
    ├── crud/
    │   ├── __init__.py
    │   ├── base.py          # MockCRUDOperation base
    │   ├── create.py        # MockCreateOperation
    │   ├── delete.py        # MockDeleteOperation
    │   ├── exceptions.py    # Mock CRUD exceptions
    │   ├── factory.py       # MockCRUDFactory
    │   ├── read.py          # MockReadOperation
    │   ├── update.py        # MockUpdateOperation
    │   └── verification.py  # CRUD-specific verification helpers
    ├── doubles/
    │   ├── __init__.py
    │   ├── data_store.py    # InMemoryDataStore for FakeAPI
    │   ├── fake_api.py      # FakeAPI implementation
    │   └── stubs.py         # Pre-configured stubs
    ├── helpers/
    │   ├── __init__.py
    │   ├── assertions.py    # User-facing assertion functions (assert_called_once_with, etc.)
    │   └── config.py        # Helpers to simplify mock configuration
    ├── response_builder/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── data.py          # Mock data generation
    │   ├── error.py         # Mock error response generation
    │   ├── headers.py       # Mock header generation
    │   └── pagination.py    # Mock pagination response generation
    └── spy/
        ├── __init__.py
        ├── auth_spy.py      # Spy wrapper for auth mocks
        ├── call_record.py   # Data structure for a recorded call
        ├── client_spy.py    # Spy wrapper for client mocks
        ├── crud_spy.py      # Spy wrapper for crud mocks
        ├── http_spy.py      # Spy wrapper for http mocks
        └── recorder.py      # InteractionRecorder (stores CallRecords)