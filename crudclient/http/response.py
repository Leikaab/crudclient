import logging
from typing import Union

import requests

from ..types import RawResponseSimple

# Set up logging
logger = logging.getLogger(__name__)


class ResponseHandler:

    def handle_response(self, response: requests.Response) -> RawResponseSimple:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        if not response.ok:
            # Let the caller handle error responses
            logger.debug(f"Response not OK: {response.status_code}")
            # We don't handle error responses here, just raise an exception
            # to indicate that the caller should handle it
            response.raise_for_status()

        # Special handling for 204 No Content responses
        if response.status_code == 204:
            logger.debug("Received 204 No Content response, returning None")
            return None

        content_type = response.headers.get("Content-Type", "")
        logger.debug(f"Processing response with content type: {content_type}")

        # Use startswith() for more precise Content-Type checking
        if content_type.startswith("application/json"):
            return self.parse_json_response(response)
        elif content_type.startswith("application/octet-stream") or content_type.startswith("multipart/form-data"):
            return self.parse_binary_response(response)
        else:
            return self.parse_text_response(response)

    def parse_json_response(self, response: requests.Response) -> Union[dict, list, str]:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        logger.debug("Parsing JSON response")
        try:
            return response.json()
        except ValueError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # If the content type is explicitly JSON but parsing failed, raise the exception
            if response.headers.get("Content-Type", "").startswith("application/json"):
                # Re-raise the original JSONDecodeError
                response.json()
            # Otherwise, return the text content
            return response.text

    def parse_binary_response(self, response: requests.Response) -> bytes:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        logger.debug("Parsing binary response")
        return response.content

    def parse_text_response(self, response: requests.Response) -> str:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        logger.debug("Parsing text response")
        return response.text
