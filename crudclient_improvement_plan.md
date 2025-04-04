# CrudClient Improvement Plan (TODO)

This plan outlines tasks based on project analysis and feedback, prioritized for improving the `crudclient` library.

## High Priority

1.  **Improve Error Handling & Logging:**
    *   **Enhance Request/Response Logging (`client.py`):**
        *   Modify `_request` to log request details (method, URL, params, relevant headers, payload snippet) at DEBUG level *before* sending.
        *   Modify `_request` or `_handle_response` to log response details (status code, relevant headers, body snippet) at DEBUG level *after* receiving.
        *   Ensure error logs in `_handle_error_response` include request context (method, URL) alongside status code and error data.
    *   **Preserve Raw Response Data (`client.py`):**
        *   Review `_handle_response` and `_handle_error_response` to ensure the full `requests.Response` object is accessible internally *before* potential parsing errors or exceptions occur.
        *   Consider attaching the raw `requests.Response` object to raised exceptions (see below) for deeper debugging capabilities.
    *   **Refine Exception Hierarchy & Handling:**
        *   Define a new specific exception, e.g., `CrudClientError(APIError)`, in `exceptions.py` to represent errors originating from this library.
        *   Modify `_handle_error_response` in `client.py` to catch `requests.HTTPError` and raise the new `CrudClientError`, embedding the original exception and potentially the raw `requests.Response`.
        *   Review `crud.py` (`custom_action`'s `try/except ValueError`) to ensure `ValueError` during model conversion is either re-raised appropriately (perhaps as a `CrudClientError`) or logged with sufficient detail, rather than silently returning the raw response.

2.  **Refine Pydantic Response Model Strategy:**
    *   Investigate and design a more flexible strategy for handling diverse API response structures with Pydantic models within `Crud`.
    *   Goal: Allow consumer libraries to easily adapt `crudclient` to APIs with varying response formats (e.g., different pagination structures, data nesting).

## Medium Priority

3.  **Update Typing & Stubs:**
    *   Ensure all necessary type hints and *all* public API docstrings reside exclusively in the `.pyi` files (`client.pyi`, `config.pyi`, etc.), removing any redundant method/function docstrings from `.py` files.
    *   Investigate and update type hinting syntax to leverage PEP 695 Type Parameter Syntax where applicable.
    *   Update CI/CD (`tests.yml`) Python matrix to reflect supported versions compatible with PEP 695 (likely removing Python 3.10, 3.11 if focusing on 3.12+ features).

4.  **Testing Enhancements:**
    *   **Integration Tests:** Define specific Pydantic models for API responses in integration tests (e.g., `test_jsonplaceholder.py`) instead of generic `BaseModel` for stricter validation.
    *   **Error Cases:** Add more tests (unit and/or integration) for specific API error conditions (4xx, 5xx, malformed responses).
    *   **Downstream Testing:** Investigate strategies to leverage tests from dependent libraries (fikenpy, tripletex, oneflowpy) to validate `crudclient` changes (e.g., dedicated CI workflow, local test harness).

## Low Priority / Future Work

5.  **Evaluate Pydantic for `ClientConfig`:**
    *   Carefully assess the feasibility and benefits of using Pydantic for `ClientConfig`, ensuring it doesn't hinder the ease of subclassing required by users.

6.  **Increase Mypy Strictness:**
    *   Revisit enabling stricter `mypy` checks after the library stabilizes beyond the alpha stage.

7.  **Asynchronous Support:**
    *   Explore adding `asyncio`/`httpx` support for non-blocking API calls.