"""
Factory for creating CRUD operation mocks.

This module provides a factory class for creating instances of the various
CRUD operation mocks, making it easier to set up mocks for testing.
"""

from .create import CreateMock
from .read import ReadMock
from .update import UpdateMock
from .delete import DeleteMock
from .combined import CombinedCrudMock


class CrudMockFactory:
    """
    Factory for creating CRUD operation mocks.

    This class provides static methods for creating instances of the various
    CRUD operation mocks, making it easier to set up mocks for testing.
    """

    @staticmethod
    def create() -> CreateMock:
        """
        Create a Create operation mock.

        Returns:
            A new instance of CreateMock
        """
        return CreateMock()

    @staticmethod
    def read() -> ReadMock:
        """
        Create a Read operation mock.

        Returns:
            A new instance of ReadMock
        """
        return ReadMock()

    @staticmethod
    def update() -> UpdateMock:
        """
        Create an Update operation mock.

        Returns:
            A new instance of UpdateMock
        """
        return UpdateMock()

    @staticmethod
    def delete() -> DeleteMock:
        """
        Create a Delete operation mock.

        Returns:
            A new instance of DeleteMock
        """
        return DeleteMock()

    @staticmethod
    def combined() -> CombinedCrudMock:
        """
        Create a combined CRUD mock.

        Returns:
            A new instance of CombinedCrudMock
        """
        return CombinedCrudMock()
