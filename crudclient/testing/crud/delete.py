import copy
import json
import re
from typing import Any, Dict, Union

from crudclient.exceptions import CrudClientError
from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock
from .request_record import RequestRecord


class DeleteMock(BaseCrudMock):
    def __init__(self):
        super().__init__()
        self.default_response = MockResponse(status_code=204, json_data=None)
        self._stored_resources = {}  # id -> resource dict
        self._dependencies = {}  # id -> list of dependent resource IDs
        self._soft_deleted_resources = {}  # id -> resource dict (for soft deletes)
        self._cascade_enabled = False  # Whether cascading deletes are enabled
        self._soft_delete_enabled = False  # Whether soft deletes are enabled

    def delete(self, url: str, **kwargs: Any) -> Any:
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop("parent_id", None)
        if parent_id and self._parent_id_handling:  # type: ignore
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="DELETE", url=url, params=kwargs.get("params"), data=kwargs.get("data"), json=kwargs.get("json"), headers=kwargs.get("headers")
        )
        self.request_history.append(record)  # type: ignore

        # Find a matching pattern
        pattern = self._find_matching_pattern("DELETE", url, **kwargs)

        if pattern:
            response_obj = pattern["response"]

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if "error" in pattern and pattern["error"]:
                raise pattern["error"]

            # Ensure response_obj is a MockResponse
            if not isinstance(response_obj, MockResponse):
                if isinstance(response_obj, dict):
                    response_obj = MockResponse(status_code=204, json_data=response_obj)
                elif isinstance(response_obj, list):
                    response_obj = MockResponse(status_code=204, text=json.dumps(response_obj))
                elif isinstance(response_obj, str):
                    response_obj = MockResponse(status_code=204, text=response_obj)
                else:
                    response_obj = MockResponse(status_code=204, text=str(response_obj))

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

    def with_success(self, url_pattern: str, **kwargs: Any) -> "DeleteMock":
        self.with_response(url_pattern=url_pattern, response=MockResponse(status_code=204, json_data=None), **kwargs)
        return self

    def with_resource_in_use_error(self, url_pattern: str, **kwargs: Any) -> "DeleteMock":
        # Create a mock response for resource in use error
        mock_response = MockResponse(status_code=409, json_data={"error": "Resource is in use and cannot be deleted"})

        # Create the error instance
        error_instance = CrudClientError("HTTP error occurred: 409, Resource is in use and cannot be deleted")

        # Use the inherited with_response method
        self.with_response(
            url_pattern=url_pattern,
            response=mock_response,
            error=error_instance,
            status_code=409,  # Explicitly set status code
            params=kwargs.get("params"),
            data=kwargs.get("data"),
            json=kwargs.get("json"),
            headers=kwargs.get("headers"),
            max_calls=kwargs.get("max_calls", float("inf")),
        )
        return self

    def with_stored_resource(self, resource_id: Union[str, int], resource: Dict[str, Any]) -> "DeleteMock":
        str_id = str(resource_id)
        self._stored_resources[str_id] = copy.deepcopy(resource)
        return self

    def with_dependency(self, resource_id: Union[str, int], dependent_id: Union[str, int]) -> "DeleteMock":
        str_id = str(resource_id)
        if str_id not in self._dependencies:
            self._dependencies[str_id] = []

        self._dependencies[str_id].append(str(dependent_id))
        return self

    def with_cascading_delete(self, enabled: bool = True) -> "DeleteMock":
        self._cascade_enabled = enabled

        # Override the delete method to handle cascading deletes
        original_delete = self.delete

        def delete_with_cascading(url: str, **kwargs: Any) -> Any:
            # Extract the resource ID from the URL
            id_match = re.search(r"/([^/]+)$", url)
            if id_match:
                resource_id = id_match.group(1)

                # If the resource exists and has dependencies
                if resource_id in self._stored_resources:
                    # If soft delete is enabled, store the resource
                    if self._soft_delete_enabled:
                        self._soft_deleted_resources[resource_id] = self._stored_resources[resource_id]

                    # If the resource has dependencies and cascading is enabled
                    if resource_id in self._dependencies and self._cascade_enabled:
                        # Delete all dependent resources
                        for dependent_id in self._dependencies[resource_id]:
                            if dependent_id in self._stored_resources:
                                # If soft delete is enabled, store the dependent resource
                                if self._soft_delete_enabled:
                                    self._soft_deleted_resources[dependent_id] = self._stored_resources[dependent_id]
                                # Remove from stored resources
                                del self._stored_resources[dependent_id]

                    # Remove the resource itself
                    del self._stored_resources[resource_id]

                    # Return success
                    return {"status": "success"}

            # If no matching resource or no cascading needed, call the original delete
            return original_delete(url, **kwargs)

        # Replace the delete method with our wrapper
        self.delete = delete_with_cascading

        return self

    def with_soft_delete(self, enabled: bool = True) -> "DeleteMock":
        self._soft_delete_enabled = enabled

        # Override the delete method to handle soft deletes
        original_delete = self.delete

        def delete_with_soft_delete(url: str, **kwargs: Any) -> Any:
            # Extract the resource ID from the URL
            id_match = re.search(r"/([^/]+)$", url)
            if id_match:
                resource_id = id_match.group(1)

                # If the resource exists
                if resource_id in self._stored_resources:
                    # Store in soft deleted resources
                    self._soft_deleted_resources[resource_id] = self._stored_resources[resource_id]
                    # Remove from stored resources
                    del self._stored_resources[resource_id]

                    # Return success
                    return {"status": "success"}

            # If no matching resource, call the original delete
            return original_delete(url, **kwargs)

        # Replace the delete method with our wrapper
        self.delete = delete_with_soft_delete

        return self

    def with_referential_integrity_check(self, url_pattern: str) -> "DeleteMock":
        # Create a CrudClientError with a specific message
        error = CrudClientError("Referential integrity violation: Cannot delete resource with dependencies")

        # Use the inherited with_response method
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=409, json_data={"error": "Referential integrity violation", "message": "Cannot delete resource with dependencies"}
            ),
            error=error,
            status_code=409,  # Explicitly set status code
            max_calls=float("inf"),
        )

        # Override the delete method to raise the error
        original_delete = self.delete

        def delete_with_integrity_check(url: str, **kwargs: Any) -> Any:
            # Check if this URL matches the pattern
            if re.search(url_pattern, url):
                # Extract the resource ID from the URL
                id_match = re.search(r"/([^/]+)$", url)
                if id_match:
                    resource_id = id_match.group(1)
                    # Check if the resource has dependencies
                    if resource_id in self._dependencies:
                        # Create a CrudClientError with a specific message
                        error = CrudClientError("Referential integrity violation: Cannot delete resource with dependencies")

                        # Record the request with an error response
                        record = RequestRecord(
                            method="DELETE",
                            url=url,
                            params=kwargs.get("params"),
                            data=kwargs.get("data"),
                            json=kwargs.get("json"),
                            headers=kwargs.get("headers"),
                            response=MockResponse(status_code=409, json_data={"error": "Referential integrity violation"}),
                        )
                        self.request_history.append(record)  # type: ignore

                        # Raise the error immediately
                        raise error

            # If no integrity violation, call the original delete method
            return original_delete(url, **kwargs)

        # Replace the delete method with our wrapper
        self.delete = delete_with_integrity_check

        return self

    def verify_resource_deleted(self, resource_id: Union[str, int], soft_delete: bool = False) -> None:
        str_id = str(resource_id)

        # Check that the resource is not in stored resources
        assert str_id not in self._stored_resources, f"Resource {str_id} was not deleted"

        # If checking soft deletes, verify it's in soft deleted resources
        if soft_delete:
            assert str_id in self._soft_deleted_resources, f"Resource {str_id} was not soft deleted"

    def verify_dependencies_deleted(self, resource_id: Union[str, int], soft_delete: bool = False) -> None:
        str_id = str(resource_id)

        # Check that the resource has dependencies
        if str_id not in self._dependencies:
            return  # No dependencies to check

        # Check that all dependencies were deleted
        for dependent_id in self._dependencies[str_id]:
            assert dependent_id not in self._stored_resources, f"Dependent resource {dependent_id} was not deleted"

            # If checking soft deletes, verify it's in soft deleted resources
            if soft_delete:
                assert dependent_id in self._soft_deleted_resources, f"Dependent resource {dependent_id} was not soft deleted"
