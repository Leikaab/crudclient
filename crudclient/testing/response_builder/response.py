from typing import Dict, Optional, Union


class MockResponse:
    def __init__(
        self,
        status_code: int,
        json_data: Optional[Dict] = None,
        text: Optional[Union[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self.json_data = json_data
        self.text = text
        self.headers = headers if headers is not None else {}

    def json(self) -> Optional[Dict]:
        return self.json_data
