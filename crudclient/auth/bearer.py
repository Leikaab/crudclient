from typing import Dict

from crudclient.auth.base import AuthStrategy


class BearerAuth(AuthStrategy):

    def __init__(self, token: str):
        self.token = token

    def prepare_request_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def prepare_request_params(self) -> Dict[str, str]:
        return {}
