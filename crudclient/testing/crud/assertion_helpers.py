from typing import Any, Dict, List, Optional, Type

from crudclient.testing.response_builder.response import MockResponse  # Assuming Request object structure

# Placeholder for the actual Request object type used in request_history
# Replace with the actual import if available


class Request:
    url: str
    method: str
    params: Optional[Dict[str, Any]]
    data: Optional[Dict[str, Any]]
    json: Optional[Dict[str, Any]]
    response: MockResponse


def check_request_payload(
    requests: List[Request],
    payload: Dict[str, Any],
    url_pattern: Optional[str],
    match_all: bool,
) -> None:
    if not requests:
        raise AssertionError(
            f"No matching requests found. Filter: url_pattern={url_pattern}"
        )

    if match_all:
        for i, request in enumerate(requests):
            request_json = request.json or {}
            for key, value in payload.items():
                if key not in request_json:
                    raise AssertionError(
                        f"Request {i} missing payload key '{key}'. "
                        f"URL: {request.url}"
                    )
                if callable(value):
                    if not value(request_json[key]):
                        raise AssertionError(
                            f"Request {i} payload key '{key}' failed validation. "
                            f"URL: {request.url}"
                        )
                elif request_json[key] != value:
                    raise AssertionError(
                        f"Request {i} payload key '{key}' has value '{request_json[key]}', "
                        f"expected '{value}'. URL: {request.url}"
                    )
    else:
        # At least one request must match all payload
        found_match = False
        for request in requests:
            all_match = True
            request_json = request.json or {}
            for key, value in payload.items():
                if key not in request_json:
                    all_match = False
                    break
                if callable(value):
                    if not value(request_json[key]):
                        all_match = False
                        break
                elif request_json[key] != value:
                    all_match = False
                    break

            if all_match:
                found_match = True
                break

        if not found_match:
            raise AssertionError(
                f"No request matched all payload {payload}. "
                f"Filter: url_pattern={url_pattern}"
            )


def check_operation_parameters(
    requests: List[Request],
    expected_params: Dict[str, Any],
    url_pattern: str,
    method: Optional[str],
) -> None:
    assert requests, f"No matching requests found for URL pattern: {url_pattern}, method: {method}"

    # Find a request that matches all expected parameters
    found_matching_request = False
    for request in requests:
        all_params_match = True
        for key, value in expected_params.items():
            param_found = False
            param_matches = False

            # Check in params, data, or json
            if request.params and key in request.params:
                param_found = True
                param_matches = request.params[key] == value
            elif request.data and key in request.data:
                param_found = True
                param_matches = request.data[key] == value
            elif request.json and key in request.json:
                param_found = True
                param_matches = request.json[key] == value

            if not param_found or not param_matches:
                all_params_match = False
                break

        if all_params_match:
            found_matching_request = True
            break

    if found_matching_request:
        return

    # If we get here, no request matched all parameters
    # Find the closest match to provide a helpful error message
    for i, request in enumerate(requests):
        for key, value in expected_params.items():
            if request.params and key in request.params:
                if request.params[key] != value:
                    raise AssertionError(
                        f"Request {i} param '{key}' has value '{request.params[key]}', "
                        f"expected '{value}'. URL: {request.url}"
                    )
            elif request.data and key in request.data:
                if request.data[key] != value:
                    raise AssertionError(
                        f"Request {i} data '{key}' has value '{request.data[key]}', "
                        f"expected '{value}'. URL: {request.url}"
                    )
            elif request.json and key in request.json:
                if request.json[key] != value:
                    raise AssertionError(
                        f"Request {i} json '{key}' has value '{request.json[key]}', "
                        f"expected '{value}'. URL: {request.url}"
                    )

    # If we get here, parameters were missing in all requests
    raise AssertionError(
        f"No request matched all expected parameters: {expected_params}. "
        f"URL pattern: {url_pattern}, method: {method}"
    )


def check_response_handling(
    requests: List[Request],
    expected_status: int,
    expected_data: Optional[Dict[str, Any]],
    url_pattern: str,
    method: Optional[str],
) -> None:
    assert requests, f"No matching requests found for URL pattern: {url_pattern}, method: {method}"

    for i, request in enumerate(requests):
        # Check status code
        assert request.response.status_code == expected_status, (
            f"Request {i} response status code is {request.response.status_code}, "
            f"expected {expected_status}. URL: {request.url}"
        )

        # Check response data if provided
        if expected_data:
            response_json = request.response.json()  # Use the public json() method
            if not response_json:
                continue
            for key, value in expected_data.items():
                assert key in response_json, (
                    f"Request {i} response missing key '{key}'. URL: {request.url}"
                )
                assert response_json[key] == value, (
                    f"Request {i} response key '{key}' has value '{response_json[key]}', "
                    f"expected '{value}'. URL: {request.url}"
                )


def check_error_handling(
    requests: List[Request],
    expected_error_type: Type[Exception],
    expected_status: Optional[int],
    url_pattern: str,
    method: Optional[str],
) -> bool:
    assert requests, f"No matching requests found for URL pattern: {url_pattern}, method: {method}"

    error_found_in_history = False
    for i, request in enumerate(requests):
        # Check if the response associated with the request has an error attribute
        if hasattr(request.response, 'error') and request.response.error:  # type: ignore[attr-defined]
            error_found_in_history = True
            assert isinstance(request.response.error, expected_error_type), (  # type: ignore[attr-defined]
                f"Request {i} error type is {type(request.response.error)}, "  # type: ignore[attr-defined]
                f"expected {expected_error_type}. URL: {request.url}"
            )

            # Check status code if provided
            if expected_status:
                assert request.response.status_code == expected_status, (
                    f"Request {i} response status code is {request.response.status_code}, "
                    f"expected {expected_status}. URL: {request.url}"
                )
            # If we found a matching error in history, we can stop checking history
            break

    return error_found_in_history
