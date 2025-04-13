# crudclient/testing/response_builder/data_generation.py
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union


class DataGenerationBuilder:

    @staticmethod
    def create_random_data(schema: Dict[str, Any], count: int = 1) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        if count == 1:
            return DataGenerationBuilder._generate_item(schema)
        else:
            return [DataGenerationBuilder._generate_item(schema) for _ in range(count)]

    @staticmethod
    def _generate_item(schema_def: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for key, value_type in schema_def.items():
            result[key] = DataGenerationBuilder._process_field_value(value_type)
        return result

    @staticmethod
    def _process_field_value(value_type: Any) -> Any:
        if isinstance(value_type, dict):
            # Nested object
            return DataGenerationBuilder._generate_item(value_type)
        elif isinstance(value_type, list) and len(value_type) > 0:
            # Array of items
            return DataGenerationBuilder._generate_array(value_type[0])
        else:
            # Primitive type
            return DataGenerationBuilder._generate_primitive(value_type)

    @staticmethod
    def _generate_array(element_type: Any) -> List[Any]:
        array_count = random.randint(1, 5)

        if isinstance(element_type, dict):
            # Array of objects
            return [DataGenerationBuilder._generate_item(element_type) for _ in range(array_count)]
        else:
            # Array of primitives
            return [DataGenerationBuilder._generate_primitive(element_type) for _ in range(array_count)]

    @staticmethod
    def _generate_primitive(type_hint: Any) -> Any:
        # String types
        if type_hint in ("string", str):
            return DataGenerationBuilder._generate_random_string()
        elif type_hint == "email":
            return DataGenerationBuilder._generate_email()
        elif type_hint == "name":
            return DataGenerationBuilder._generate_name()
        elif type_hint == "url":
            return DataGenerationBuilder._generate_url()
        elif type_hint == "ip":
            return DataGenerationBuilder._generate_ip()
        # Number types
        elif type_hint in ("int", int):
            return random.randint(1, 1000)
        elif type_hint in ("float", float):
            return round(random.uniform(1.0, 1000.0), 2)
        # Boolean type
        elif type_hint in ("bool", bool):
            return random.choice([True, False])
        # Date and time types
        elif type_hint == "date":
            return DataGenerationBuilder._generate_date()
        elif type_hint == "datetime":
            return DataGenerationBuilder._generate_datetime()
        # ID types
        elif type_hint == "uuid":
            return str(uuid.uuid4())
        # Default case
        else:
            return str(type_hint)  # Default to string representation

    @staticmethod
    def _generate_random_string(length: Optional[int] = None) -> str:
        if length is None:
            length = random.randint(5, 10)
        return "".join(random.choices(string.ascii_letters, k=length))

    @staticmethod
    def _generate_email() -> str:
        username = "".join(random.choices(string.ascii_lowercase, k=8))
        return f"{username}@example.com"

    @staticmethod
    def _generate_name() -> str:
        first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    @staticmethod
    def _generate_date() -> str:
        days = random.randint(0, 365 * 2)
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def _generate_datetime() -> str:
        days = random.randint(0, 365 * 2)
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        dt = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _generate_url() -> str:
        path = "".join(random.choices(string.ascii_lowercase, k=8))
        return f"https://example.com/{path}"

    @staticmethod
    def _generate_ip() -> str:
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
