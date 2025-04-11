from typing import Any, Dict, Optional


class TestingError(Exception):
    pass


class MockConfigurationError(TestingError):
    pass


class VerificationError(TestingError):
    pass


class RequestNotConfiguredError(MockConfigurationError):
    pass


class AuthStrategyError(TestingError):
    pass


class CRUDOperationError(TestingError):
    pass


class DataStoreError(TestingError):
    pass


class ResourceNotFoundError(DataStoreError):
    pass


class SpyError(TestingError):
    pass


class FakeAPIError(TestingError):

    def __init__(self, status_code: int, detail: Any, headers: Optional[Dict[str, str]] = None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers or {}
        super().__init__(f"FakeAPI Error {status_code}: {detail}")
