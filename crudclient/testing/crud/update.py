import copy
import json
import re
from typing import Any, Dict, Union

from crudclient.exceptions import NotFoundError
from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock
from .exceptions import ConcurrencyError
from .request_record import RequestRecord


class UpdateMock(BaseCrudMock):

    def _ensure_mock_response(self, response_obj: Any, **kwargs: Any) -> MockResponse:
        if isinstance(response_obj, MockResponse):
            return response_obj
        if isinstance(response_obj, dict):
            return MockResponse(status_code=200, json_data=response_obj)
        if isinstance(response_obj, list):
            return MockResponse(status_code=200, text=json.dumps(response_obj))
        if isinstance(response_obj, str):
            return MockResponse(status_code=200, text=response_obj)
        # Fallback for other types
        return MockResponse(status_code=200, text=str(response_obj))

    def _handle_request(self, method: str, url: str, **kwargs: Any) -> Any:
        # Process parent_id if present
        parent_id = kwargs.pop("parent_id", None)
        if parent_id and self._parent_id_handling:  # type: ignore[attr-defined]
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method=method, url=url, params=kwargs.get("params"), data=kwargs.get("data"), json=kwargs.get("json"), headers=kwargs.get("headers")
        )
        self.request_history.append(record)  # type: ignore[attr-defined]

        # Find a matching pattern
        pattern = self._find_matching_pattern(method, url, **kwargs)

        if pattern:
            response_obj = pattern["response"]

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if "error" in pattern and pattern["error"]:
                raise pattern["error"]

            # Ensure response_obj is a MockResponse
            response_obj = self._ensure_mock_response(response_obj, **kwargs)

            record.response = response_obj

            # Return the appropriate response format
            # Return the appropriate response format
            json_content = response_obj.json()
            if json_content is not None:
                return json_content
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        default_json = self.default_response.json()
        if default_json is not None:
            return default_json
        return self.default_response.text

    def __init__(self) -> None:
        super().__init__()
        self.default_response = MockResponse(status_code=200, json_data={"id": 1, "name": "Updated Resource"})
        self._stored_resources: Dict[str, Dict[str, Any]] = {}  # id -> resource dict
        self._resource_versions: Dict[str, int] = {}  # id -> version number
        self._resource_etags: Dict[str, str] = {}  # id -> ETag value

    def put(self, url: str, **kwargs: Any) -> Any:
        return self._handle_request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Any:
        return self._handle_request("PATCH", url, **kwargs)

    def with_update_response(self, url_pattern: str, updated_data: Dict[str, Any], **kwargs: Any) -> "UpdateMock":
        self.with_response(url_pattern=url_pattern, response=MockResponse(status_code=200, json_data=updated_data), **kwargs)
        return self

    def with_partial_update_response(
        self, url_pattern: str, partial_data: Dict[str, Any], full_response_data: Dict[str, Any], **kwargs: Any
    ) -> "UpdateMock":
        self.with_response(url_pattern=url_pattern, response=MockResponse(status_code=200, json_data=full_response_data), json=partial_data, **kwargs)
        return self

    def with_conditional_update(
        self, url_pattern: str, condition_field: str, condition_value: Any, success_data: Dict[str, Any], error_data: Dict[str, Any], **kwargs: Any
    ) -> "UpdateMock":
        def conditional_response(**request_kwargs: Any) -> MockResponse:
            request_json = request_kwargs.get("json", {})
            if request_json.get(condition_field) == condition_value:
                return MockResponse(status_code=200, json_data=success_data)
            else:
                return MockResponse(status_code=422, json_data=error_data)

        self.with_response(url_pattern=url_pattern, response=conditional_response, **kwargs)
        return self

    def with_not_found(self, url_pattern: str, **kwargs: Any) -> "UpdateMock":
        # Use the inherited with_response method to configure the not found error
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(status_code=404, json_data={"error": "Resource not found"}),
            error=NotFoundError("HTTP error occurred: 404, Resource not found"),
            status_code=404,  # Explicitly set status code for clarity
            params=kwargs.get("params"),
            data=kwargs.get("data"),
            json=kwargs.get("json"),
            headers=kwargs.get("headers"),
            max_calls=kwargs.get("max_calls", float("inf")),
        )
        return self

    def with_stored_resource(self, resource_id: Union[str, int], resource: Dict[str, Any]) -> "UpdateMock":
        str_id = str(resource_id)
        self._stored_resources[str_id] = copy.deepcopy(resource)
        self._resource_versions[str_id] = 1  # Initial version
        self._resource_etags[str_id] = f'W/"{hash(json.dumps(resource))}"'  # Initial ETag

        return self

    def _check_concurrency(self, resource_id: str, control_type: str, version_field: str, **kwargs: Any) -> None:
        if control_type == "etag":
            headers = kwargs.get("headers", {})
            if_match = headers.get("If-Match")
            current_etag = self._resource_etags.get(resource_id)
            if if_match and current_etag and if_match != current_etag:
                raise ConcurrencyError("ETag mismatch: Resource has been modified.")
        elif control_type == "version":
            json_data = kwargs.get("json", {})
            if version_field in json_data:
                client_version = json_data[version_field]
                current_version = self._resource_versions.get(resource_id)
                if current_version is not None and client_version != current_version:
                    raise ConcurrencyError(f"Version mismatch: Expected {current_version}, got {client_version}.")

    def _update_stored_resource(self, resource_id: str, version_field: str, update_data: Dict[str, Any], is_partial: bool) -> Dict[str, Any]:
        updated_resource = copy.deepcopy(self._stored_resources[resource_id])

        if is_partial:
            # Partial update (PATCH)
            updated_resource.update(update_data)
        else:
            # Full update (PUT) - replace the entire resource except ID
            original_id = updated_resource.get("id")
            updated_resource = update_data
            if original_id is not None:
                updated_resource["id"] = original_id

        # Update version and ETag
        new_version = self._resource_versions.get(resource_id, 0) + 1
        self._resource_versions[resource_id] = new_version
        updated_resource[version_field] = new_version
        self._resource_etags[resource_id] = f'W/"{hash(json.dumps(updated_resource))}"'

        # Store the updated resource
        self._stored_resources[resource_id] = updated_resource
        return updated_resource

    def with_concurrency_control(self, url_pattern: str, control_type: str = "etag", version_field: str = "version") -> "UpdateMock":
        # Override the put method to handle concurrency control
        original_put = self.put

        def put_with_concurrency_control(url: str, **kwargs: Any) -> Any:
            # Check if this URL matches the pattern
            if re.search(url_pattern, url):
                # Extract the resource ID from the URL
                id_match = re.search(r"/([^/]+)$", url)
                if id_match:
                    resource_id = id_match.group(1)

                    # If the resource exists
                    if resource_id in self._stored_resources:
                        # Perform concurrency check
                        self._check_concurrency(resource_id, control_type, version_field, **kwargs)

                        # Update the resource (full update for PUT)
                        json_data = kwargs.get("json", {})
                        updated_resource = self._update_stored_resource(resource_id, version_field, json_data, is_partial=False)
                        return updated_resource
            # If no matching resource or pattern, call the original put method
            return original_put(url, **kwargs)

        # Replace the put method with our wrapper
        self.put = put_with_concurrency_control  # type: ignore[method-assign]
        # Also override the patch method for partial updates
        original_patch = self.patch

        def patch_with_concurrency_control(url: str, **kwargs: Any) -> Any:
            # Check if this URL matches the pattern
            if re.search(url_pattern, url):
                # Extract the resource ID from the URL
                id_match = re.search(r"/([^/]+)$", url)
                if id_match:
                    resource_id = id_match.group(1)

                    if resource_id in self._stored_resources:
                        # Perform concurrency check
                        self._check_concurrency(resource_id, control_type, version_field, **kwargs)

                        # Update the resource (partial update for PATCH)
                        json_data = kwargs.get("json", {})
                        updated_resource = self._update_stored_resource(resource_id, version_field, json_data, is_partial=True)
                        return updated_resource

            # If no matching resource or pattern, call the original patch method
            return original_patch(url, **kwargs)

        # Replace the patch method with our wrapper
        self.patch = patch_with_concurrency_control  # type: ignore[method-assign]
        return self

    def with_optimistic_locking(self, url_pattern: str, version_field: str = "version") -> "UpdateMock":
        return self.with_concurrency_control(url_pattern, "version", version_field)

    def with_etag_concurrency(self, url_pattern: str) -> "UpdateMock":
        return self.with_concurrency_control(url_pattern, "etag")

    def with_concurrency_conflict(self, url_pattern: str, resource_id: Union[str, int], **kwargs: Any) -> "UpdateMock":
        # Add the conflict response for the specific resource
        self.with_response(
            url_pattern=f"{url_pattern}/{resource_id}$",
            response=MockResponse(
                status_code=409,  # Conflict
                json_data={
                    "error": "Concurrency conflict",
                    "message": "Resource has been modified by another request",
                    "resourceId": str(resource_id),
                },
            ),
            **kwargs,
        )

        return self
