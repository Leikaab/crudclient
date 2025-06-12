# Design Patterns in `crudclient.testing`

This document summarizes the key software design patterns employed within the `crudclient.testing` module to facilitate robust and maintainable testing of the `crudclient` library.

The testing utilities now contain inline type hints in the implementation files, eliminating the need for separate `.pyi` stubs.

## 1. Factory Pattern

*   **What:** Provides an interface for creating objects, allowing subclasses or factory implementations to determine the exact type of object created.
*   **Why:** Used to centralize and simplify the creation of test doubles (like `MockClient` or specific auth mocks) with various configurations needed for different test scenarios. It decouples the test setup from the specific implementation details of the doubles.
*   **Where:** Implemented in dedicated factory classes such as `crudclient.testing.mock_client_factory.MockClientFactory`, `crudclient.testing.simple_mock_factory.SimpleMockFactory`, and `crudclient.testing.auth.factory` for creating authentication-related mocks.

## 2. Verifier Pattern

*   **What:** Encapsulates the logic for verifying interactions with test doubles (mocks, spies, fakes). It provides dedicated functions or methods for making assertions about method calls, arguments, call counts, or state changes.
*   **Why:** Decouples assertion logic from the test double itself and the main test flow, leading to cleaner tests and reusable verification logic. This is particularly useful for complex checks, such as call sequences, specific header contents, or authentication details.
*   **Where:** General verification logic resides in `crudclient.testing.verification.Verifier` (often raising `VerificationError`). More specialized verification helpers exist for specific concerns, such as those in `crudclient.testing.auth` modules (e.g., `auth_header_verification`, `auth_token_verification`), which typically raise standard `AssertionError` exceptions for integration with testing frameworks like `pytest`.

## 3. Test Spy Pattern

*   **What:** A type of test double that records information about how it was called during test execution (e.g., methods called, arguments passed). Spies often wrap real objects or provide minimal stubbing, focusing primarily on interaction recording rather than replacing behavior entirely.
*   **Why:** Used to verify indirect outputs or side effects of the system under test. For example, confirming that specific methods on a collaborator were invoked correctly without significantly altering the collaborator's core behavior.
*   **Where:** Implemented with base classes like `crudclient.testing.spy.base.SpyBase` and concrete spies such as `crudclient.testing.spy.client_spy.ClientSpy` and `crudclient.testing.spy.api_spy.ApiSpy`.

## 4. Mock Object Pattern

*   **What:** Creates simulated objects that mimic the behavior of real objects in controlled ways, often replacing external dependencies. Mocks are configured with expected interactions and corresponding responses or actions.
*   **Why:** Used extensively to isolate the system under test from its dependencies, such as HTTP clients, authentication mechanisms, or specific API endpoints, during unit tests. This allows components to be tested in isolation without needing network access, external services, or complex setup. Mocks can be configured to return specific data, simulate delays, or raise errors.
*   **Where:** Found throughout the testing module. Key examples include `MockClient` (typically created via `crudclient.testing.mock_client_factory.MockClientFactory`), base classes for mocking specific components like `crudclient.testing.auth.base.AuthMockBase`, and `crudclient.testing.crud.base.BaseCrudMock`.

## 5. Fake Object Pattern

*   **What:** Provides a functional, but simplified, implementation of a component's interface. Fakes have working behavior but replace complex or heavy dependencies (like databases or network calls) with lighter alternatives (like in-memory storage or simplified logic).
*   **Why:** Useful for integration tests where the interaction *between* components is the focus, but external dependencies are undesirable or impractical. Fakes offer more realistic behavior than mocks for certain scenarios but are simpler and faster than using the real components.
*   **Where:** Key examples are `crudclient.testing.doubles.fake_api.FakeAPI` (which simulates the `crudclient.api.API` interface) and its backing `crudclient.testing.doubles.data_store.DataStore` (which simulates a simple in-memory data store).

## 6. Builder Pattern

*   **What:** Separates the construction of a complex object from its representation, allowing the same construction process to create different variations of the object. Often implemented using fluent interfaces.
*   **Why:** Used to simplify the setup of complex test doubles or test data. It allows tests to specify only the necessary configuration details for an object (like a mock response or a complex mock client setup), making test setup more readable, maintainable, and less error-prone compared to large constructors or numerous setter methods.
*   **Where:** Explicitly used in `crudclient.testing.response_builder` for constructing mock HTTP responses. The principles are also applied within factories like `crudclient.testing.mock_client_factory.MockClientFactory`, where methods allow step-by-step configuration of the `MockClient` being built.