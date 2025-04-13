from abc import ABC, abstractmethod
from typing import Dict


class AuthStrategy(ABC):

    @abstractmethod
    def prepare_request_headers(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def prepare_request_params(self) -> Dict[str, str]:
        pass


# Alias for backward compatibility
BaseAuthStrategy = AuthStrategy
