from typing import Any, Dict, List, Optional

from .response import MockResponse


class BasicResponseBuilder:

    DEFAULT_HEADERS = {"Content-Type": "application/json"}

    @classmethod
    def create_response(
        cls,
        status_code: int = 200,
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = "application/json",
    ) -> MockResponse:
        final_headers = cls.DEFAULT_HEADERS.copy()
        if headers:
            final_headers.update(headers)
        if content_type:
            final_headers["Content-Type"] = content_type
        else:
            # If content_type is explicitly None, remove the default
            final_headers.pop("Content-Type", None)

        # Handle 204 No Content specifically
        if status_code == 204:
            return MockResponse(status_code=status_code, headers=final_headers)

        # Handle non-JSON responses
        if content_type != "application/json":
            if not isinstance(data, (str, bytes)) and data is not None:
                raise ValueError(f"Data must be str or bytes for content type {content_type}, got {type(data)}")
            return MockResponse(status_code=status_code, text=data, headers=final_headers)

        # Build JSON response body
        response_body: Dict[str, Any] = {}
        if data is not None:
            response_body["data"] = data
        if metadata is not None:
            response_body["metadata"] = metadata
        if links is not None:
            response_body["links"] = links
        if errors is not None:
            response_body["errors"] = errors

        # Return JSON response only if there's content or it's not a 204
        json_data = response_body if response_body else None
        return MockResponse(status_code=status_code, json_data=json_data, headers=final_headers)

    @classmethod
    def created(
        cls,
        data: Any,
        location: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        final_headers = headers or {}
        if location:
            final_headers["Location"] = location
        return cls.create_response(
            status_code=201,
            data=data,
            metadata=metadata,
            links=links,
            headers=final_headers,
        )

    @classmethod
    def no_content(cls, headers: Optional[Dict[str, str]] = None) -> MockResponse:
        # 204 should not have a Content-Type header typically
        final_headers = headers or {}
        return cls.create_response(status_code=204, headers=final_headers, content_type=None)

    @classmethod
    def create_nested_response(
        cls,
        structure: Dict[str, Any],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        final_headers = cls.DEFAULT_HEADERS.copy()
        if headers:
            final_headers.update(headers)
        return MockResponse(status_code=status_code, json_data=structure, headers=final_headers)
