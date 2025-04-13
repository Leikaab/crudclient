from crudclient.exceptions import CrudClientError


class ConcurrencyError(CrudClientError):
    pass


class ValidationFailedError(CrudClientError):
    pass
