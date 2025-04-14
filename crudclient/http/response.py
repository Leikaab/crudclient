import logging
from typing import Union

import requests
from requests.exceptions import JSONDecodeError

from ..exceptions import ResponseParsingError
from ..types import RawResponseSimple

logger = logging.getLogger(__name__)


class ResponseHandler:

    def handle_response(self, response: requests.Response) -> RawResponseSimple:
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        if not response.ok:
            logger.debug(f"Response not OK: {response.status_code}")
            response.raise_for_status()

        if response.status_code == 204:
            logger.debug("Received 204 No Content response, returning None")
            return None

        content_type = response.headers.get("Content-Type", "")
        logger.debug(f"Processing response with content type: {content_type}")

        if content_type.startswith("application/json"):
            return self.parse_json_response(response)
        elif content_type.startswith("application/octet-stream") or content_type.startswith("multipart/form-data"):
            return self.parse_binary_response(response)
        else:
            return self.parse_text_response(response)

    def parse_json_response(self, response: requests.Response) -> Union[dict, list, str]:
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        logger.debug("Parsing JSON response")
        try:
            return response.json()
        except JSONDecodeError as e:
            logger.error(
                "Failed to parse JSON response despite 'application/json' Content-Type. " "Status: %s, URL: %s, Error: %s",
                response.status_code,
                response.url,
                e,
                exc_info=True,
            )
            raise ResponseParsingError(
                message=f"Failed to decode JSON response from {response.url}",
                original_exception=e,
                response=response,
            ) from e

    def parse_binary_response(self, response: requests.Response) -> bytes:
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        logger.debug("Parsing binary response")
        return response.content

    def parse_text_response(self, response: requests.Response) -> str:
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        logger.debug("Parsing text response")
        return response.text
