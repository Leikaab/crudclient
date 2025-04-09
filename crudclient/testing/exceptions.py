

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
