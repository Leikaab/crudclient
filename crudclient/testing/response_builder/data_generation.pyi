# crudclient/testing/response_builder/data_generation.pyi
from typing import Any, Dict, List, Union


class DataGenerationBuilder:
    """
    Utility class for generating random test data based on a schema definition.

    Provides methods to create random data for testing API responses, following
    a specified schema structure.
    """

    @staticmethod
    def create_random_data(
        schema: Dict[str, Any],
        count: int = 1
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Generate random data based on a schema definition.

        The schema is a dictionary where keys are field names and values define the data type.
        Supported types include:
        - Primitive types: 'string'/str, 'int'/int, 'float'/float, 'bool'/bool
        - Special types: 'email', 'name', 'date', 'datetime', 'uuid', 'url', 'ip'
        - Nested objects (as dictionaries)
        - Arrays (as lists with a single item defining the array element type)

        Args:
            schema: A dictionary defining the structure and types of data to generate
            count: Number of items to generate (if 1, returns a single item; otherwise a list)

        Returns:
            Either a single dictionary or a list of dictionaries with randomly generated data
            that matches the provided schema.

        Examples:
            ```python
            # Generate a single user
            user = DataGenerationBuilder.create_random_data({
                "id": "uuid",
                "name": "name",
                "email": "email",
                "age": "int",
                "is_active": "bool",
                "created_at": "datetime",
                "address": {
                    "street": "string",
                    "city": "string",
                    "zip": "string"
                },
                "tags": ["string"]
            })

            # Generate multiple users
            users = DataGenerationBuilder.create_random_data({
                "id": "uuid",
                "name": "name"
            }, count=5)
            ```
        """
        ...
