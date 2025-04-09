"""
Data generation utilities for mock client.

This module provides utilities for generating random data for API responses,
allowing for the creation of realistic test data based on schema definitions.
It supports generating primitive types, nested objects, and arrays with
configurable properties.
"""

import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Union


class DataGenerationBuilder:
    """
    Builder for generating random data for API responses.

    This class provides methods to generate realistic random data based on schema
    definitions. It can create primitive values, nested objects, and arrays with
    various data types, making it useful for creating test data that closely
    resembles production data structures.
    """

    @staticmethod
    def create_random_data(
        schema: Dict[str, Any],
        count: int = 1
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Create random data based on a schema definition.

        This method generates random data that conforms to the provided schema,
        which defines the structure and types of the data. It can generate both
        single objects and collections of objects.

        Args:
            schema: Schema defining the structure and types of the data to generate
            count: Number of items to generate (returns a single item if count=1)

        Returns:
            Random data matching the schema, either as a single object or a list of objects
        """
        def generate_item(schema_def):
            result = {}
            for key, value_type in schema_def.items():
                if isinstance(value_type, dict):
                    # Nested object
                    result[key] = generate_item(value_type)
                elif isinstance(value_type, list) and len(value_type) > 0:
                    # Array of items
                    if isinstance(value_type[0], dict):
                        # Array of objects
                        array_count = random.randint(1, 5)
                        result[key] = [generate_item(value_type[0]) for _ in range(array_count)]
                    else:
                        # Array of primitives
                        array_count = random.randint(1, 5)
                        result[key] = [_generate_primitive(value_type[0]) for _ in range(array_count)]
                else:
                    # Primitive type
                    result[key] = _generate_primitive(value_type)
            return result

        def _generate_primitive(type_hint):
            if type_hint == 'string' or type_hint == str:
                return ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10)))
            elif type_hint == 'email':
                return f"{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"
            elif type_hint == 'name':
                first_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Edward', 'Fiona']
                last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis']
                return f"{random.choice(first_names)} {random.choice(last_names)}"
            elif type_hint == 'int' or type_hint == int:
                return random.randint(1, 1000)
            elif type_hint == 'float' or type_hint == float:
                return round(random.uniform(1.0, 1000.0), 2)
            elif type_hint == 'bool' or type_hint == bool:
                return random.choice([True, False])
            elif type_hint == 'date':
                days = random.randint(0, 365 * 2)
                date = datetime.now() - timedelta(days=days)
                return date.strftime('%Y-%m-%d')
            elif type_hint == 'datetime':
                days = random.randint(0, 365 * 2)
                hours = random.randint(0, 23)
                minutes = random.randint(0, 59)
                seconds = random.randint(0, 59)
                dt = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
                return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            elif type_hint == 'uuid':
                return str(uuid.uuid4())
            elif type_hint == 'url':
                return f"https://example.com/{''.join(random.choices(string.ascii_lowercase, k=8))}"
            elif type_hint == 'ip':
                return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            else:
                return str(type_hint)  # Default to string representation

        if count == 1:
            return generate_item(schema)
        else:
            return [generate_item(schema) for _ in range(count)]
