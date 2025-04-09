
from typing import Any, Dict, List, Optional

from .response import MockResponse


class BasicResponseBuilder:

    @staticmethod
    def create_response(
        status_code: int = 200,
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        response_body: Dict[str, Any] = {}

        if data is not None:
            response_body["data"] = data

        if metadata is not None:
            response_body["metadata"] = metadata

        if links is not None:
            response_body["links"] = links

        if errors is not None:
            response_body["errors"] = errors

        return MockResponse(
            status_code=status_code,
            json_data=response_body,
            headers=headers or {"Content-Type": "application/json"}
        )

    @staticmethod
    def create_nested_response(
        structure: Dict[str, Any],
        status_code: int = 200,
    ) -> MockResponse:
        return MockResponse(
            status_code=status_code,
            json_data=structure,
            headers={"Content-Type": "application/json"}
        )

    @staticmethod
    def create_graphql_response(
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        extensions: Optional[Dict[str, Any]] = None,
    ) -> MockResponse:
        response_body: Dict[str, Any] = {}

        if data is not None:
            response_body["data"] = data

        if errors is not None:
            response_body["errors"] = errors

        if extensions is not None:
            response_body["extensions"] = extensions

        return MockResponse(
            status_code=200 if not errors else 400,
            json_data=response_body,
            headers={"Content-Type": "application/json"}
        )
