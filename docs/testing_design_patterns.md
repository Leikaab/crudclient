# Design Patterns in `crudclient.testing`

This document summarizes the key software design patterns employed within the `crudclient.testing` module to facilitate robust and maintainable testing of the `crudclient` library.

## 1. Factory Pattern

*   **What:** Provides an interface for creating objects in a superclass, but lets subclasses alter the type of objects that will be created.
*   **Why:** Used to centralize and simplify the creation of mock objects (like `MockClient`) with various configurations needed for different test scenarios. It decouples the test setup from the specific mock implementation details.
*   **Where:** Primarily implemented in `crudclient.testing.factory.MockClientFactory` and potentially within specific mock modules like `crudclient.testing.auth.factory`.

## 2. Verifier Pattern

*   **What:** Encapsulates the logic for verifying interactions with test doubles (mocks or spies). It provides a dedicated interface for making assertions about method calls, arguments, and call counts.
*   **Why:** Decouples assertion logic from the test double itself, leading to cleaner tests and reusable verification logic. Useful for complex checks (e.g., call sequences, auth details).
*   **Where:** Implemented generally by the static methods in `crudclient.testing.verification.Verifier` (often raising `VerificationError`). More specialized, functional helpers exist for specific spy types (`crudclient.testing.spy.verification_helpers`) or authentication details (`crudclient.testing.auth.verification`), which often raise `AssertionError`.

## 3. Test Spy Pattern

*   **What:** A type of test double that records information about how it was called during the test execution. Unlike mocks, spies often wrap real objects or provide minimal stubbing, focusing on interaction recording.
*   **Why:** Used to verify indirect outputs or interactions of the system under test. For example, confirming that specific methods on a collaborator were called with the correct arguments, without necessarily altering the collaborator's behavior significantly.
*   **Where:** Implemented with base classes like `crudclient.testing.spy.base.SpyBase` and concrete spies such as `crudclient.testing.spy.client_spy.ClientSpy` and `crudclient.testing.spy.api_spy.ApiSpy`.

## 4. Mock Object Pattern

*   **What:** Creates simulated objects that mimic the behavior of real objects in controlled ways. Mocks are typically used to isolate the system under test from its dependencies.
*   **Why:** Used extensively to replace real components like the HTTP client, authentication mechanisms, or CRUD endpoints during unit tests. This allows testing components in isolation without needing external services or complex setup. Mocks can be configured to return specific responses or simulate error conditions.
*   **Where:** Found throughout the testing module, with key examples including `crudclient.testing.core.client.MockClient`, `crudclient.testing.auth.base.AuthMockBase`, and `crudclient.testing.crud.base.BaseCrudMock`.

## 5. Fake Object Pattern

*   **What:** Provides a functional, but simplified, implementation of a component's interface. Fakes have working behavior but substitute complex dependencies (like databases or network calls) with simpler alternatives (like in-memory storage).
*   **Why:** Used for higher-level integration tests where the interaction between components is important, but external dependencies are undesirable. Fakes offer more realism than mocks but are simpler than running the real component.
*   **Where:** Key examples are `crudclient.testing.doubles.fake_api.FakeAPI` (which simulates the `API` interface) and its backing `crudclient.testing.doubles.data_store.DataStore` (which simulates a database in memory).

## 6. Builder Pattern

*   **What:** Separates the construction of a complex object from its representation, allowing the same construction process to create different representations. Often used for setting up objects with many optional parameters or configurations.
*   **Why:** Used implicitly or explicitly in the configuration of mock objects (e.g., `MockClient`, `BaseCrudMock`). It allows tests to specify only the necessary configuration details for a mock, making test setup more fluent and readable, especially when dealing with complex mock behaviors or responses.
*   **Where:** While not always a dedicated `Builder` class, the pattern's principles are applied in the configuration methods or initialization parameters of various mock objects, particularly within `crudclient.testing.factory` and the mock classes themselves.