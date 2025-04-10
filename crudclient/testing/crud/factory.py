from .combined import CombinedCrudMock
from .create import CreateMock
from .delete import DeleteMock
from .read import ReadMock
from .update import UpdateMock


class CrudMockFactory:
    @staticmethod
    def create() -> CreateMock:
        return CreateMock()

    @staticmethod
    def read() -> ReadMock:
        return ReadMock()

    @staticmethod
    def update() -> UpdateMock:
        return UpdateMock()

    @staticmethod
    def delete() -> DeleteMock:
        return DeleteMock()

    @staticmethod
    def combined() -> CombinedCrudMock:
        return CombinedCrudMock()
