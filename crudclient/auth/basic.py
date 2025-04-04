import base64
from typing import Dict

from crudclient.auth.base import AuthStrategy


class BasicAuth(AuthStrategy):

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def prepare_request_headers(self) -> Dict[str, str]:
        auth_string = f"{self.username}:{self.password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}"}

    def prepare_request_params(self) -> Dict[str, str]:
        return {}
