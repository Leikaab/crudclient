
import json
import re
from typing import Any

from crudclient.testing.crud.request_record import RequestRecord
from crudclient.testing.response_builder.response import MockResponse
from crudclient.testing.simple_mock.core import SimpleMockClientCore


class SimpleMockClientRequestHandling(SimpleMockClientCore):

    def _request(self, method: str, url: str, **kwargs: Any) -> str:
        # Record the request
        record = RequestRecord(
            method=method,
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Find a matching response pattern
        for pattern in self.response_patterns:
            if (pattern['method'] == method.upper()
                    and re.search(pattern['url_pattern'], url)):

                # Check if we've reached the max calls for this pattern
                if pattern['call_count'] >= pattern['max_calls']:
                    continue

                # Check params matcher
                params_match = True
                if pattern['params'] is not None:
                    request_params = kwargs.get('params', {})
                    for key, value in pattern['params'].items():
                        if key not in request_params or request_params[key] != value:
                            params_match = False
                            break

                # Check data matcher
                data_match = True
                if pattern['data'] is not None:
                    request_data = kwargs.get('data', {})
                    for key, value in pattern['data'].items():
                        if key not in request_data or request_data[key] != value:
                            data_match = False
                            break

                # Check json matcher
                json_match = True
                if pattern['json'] is not None:
                    request_json = kwargs.get('json', {})
                    for key, value in pattern['json'].items():
                        if key not in request_json or request_json[key] != value:
                            json_match = False
                            break

                # Check headers matcher
                headers_match = True
                if pattern['headers'] is not None:
                    request_headers = kwargs.get('headers', {})
                    for key, value in pattern['headers'].items():
                        if key not in request_headers or request_headers[key] != value:
                            headers_match = False
                            break

                # If all matchers pass, return the response
                if params_match and data_match and json_match and headers_match:
                    pattern['call_count'] += 1
                    response_obj = pattern['response']

                    # Handle callable responses
                    if callable(response_obj):
                        response_obj = response_obj(**kwargs)

                    # Ensure it's a MockResponse
                    if not isinstance(response_obj, MockResponse):
                        if isinstance(response_obj, dict):
                            response_obj = MockResponse(json_data=response_obj)
                        elif isinstance(response_obj, list):
                            # Convert list to JSON string
                            response_obj = MockResponse(text=json.dumps(response_obj))
                        elif isinstance(response_obj, str):
                            response_obj = MockResponse(text=response_obj)
                        else:
                            response_obj = MockResponse(text=str(response_obj))

                    record.response = response_obj

                    # Convert to string
                    if hasattr(response_obj, '_json_data') and response_obj._json_data:
                        return json.dumps(response_obj._json_data)
                    return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        # Convert to string
        if hasattr(self.default_response, '_json_data') and self.default_response._json_data:
            return json.dumps(self.default_response._json_data)
        return self.default_response.text

    def get(self, url: str, **kwargs: Any) -> str:
        return self._request('GET', url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> str:
        return self._request('POST', url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> str:
        return self._request('PUT', url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> str:
        return self._request('DELETE', url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> str:
        return self._request('PATCH', url, **kwargs)
