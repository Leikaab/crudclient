from typing import Any, Callable, Dict, List, Optional

from .response import MockResponse

class ValidationErrorBuilder:
    """
    Provides static methods to create MockResponse objects representing
    various schema validation errors.
    """

    @staticmethod
    def create_schema_validation_error(
        invalid_fields: Dict[str, str],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
        error_format: str = "standard",
    ) -> MockResponse:
        """
        Creates a MockResponse for a schema validation error.

        Args:
            invalid_fields: A dictionary mapping field names to error messages.
            status_code: The HTTP status code for the response.
            error_code: A custom error code string.
            message: The main error message.
            error_format: The format of the error response ('standard', 'json_api', 'detailed', 'simple').

        Returns:
            A MockResponse object representing the validation error.
        """
        ...

    @staticmethod
    def create_field_validator(
        field_name: str,
        validators: List[Callable[[Any], Optional[str]]],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        error_format: str = "standard",
    ) -> Callable[[Dict[str, Any]], Optional[MockResponse]]:
        """
        Creates a validator function for a single field.

        Args:
            field_name: The name of the field to validate.
            validators: A list of validator functions for the field.
            status_code: The status code for validation errors.
            error_code: The error code for validation errors.
            error_format: The error format for validation errors.

        Returns:
            A function that takes request data and returns a MockResponse if validation fails, else None.
        """
        ...

    @staticmethod
    def create_data_validator(
        validators: Dict[str, List[Callable[[Any], Optional[str]]]],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
        error_format: str = "standard",
        require_all_fields: bool = False,
    ) -> Callable[[Dict[str, Any]], Optional[MockResponse]]:
        """
        Creates a validator function for multiple fields in a data dictionary.

        Args:
            validators: A dictionary mapping field names to lists of validator functions.
            status_code: The status code for validation errors.
            error_code: The error code for validation errors.
            message: The main error message for validation failures.
            error_format: The error format for validation errors.
            require_all_fields: If True, missing fields defined in validators will cause an error.

        Returns:
            A function that takes request data and returns a MockResponse if validation fails, else None.
        """
        ...

class BusinessLogicConstraintBuilder:
    """
    Provides static methods to create MockResponse objects representing
    various business logic constraint violations.
    """

    @staticmethod
    def create_business_rule_error(
        rule_name: str,
        message: str,
        status_code: int = 422,
        error_code: str = "BUSINESS_RULE_VIOLATION",
        details: Optional[Dict[str, Any]] = None,
    ) -> MockResponse:
        """
        Creates a MockResponse for a generic business rule violation.

        Args:
            rule_name: The name of the violated rule.
            message: The error message describing the violation.
            status_code: The HTTP status code.
            error_code: The custom error code.
            details: Optional additional details about the error.

        Returns:
            A MockResponse object representing the business rule error.
        """
        ...

    @staticmethod
    def create_unique_constraint_error(
        field_name: str,
        value: Any,
        entity_type: str = "resource",
        status_code: int = 409,
        error_code: str = "UNIQUE_CONSTRAINT_VIOLATION",
    ) -> MockResponse:
        """
        Creates a MockResponse for a unique constraint violation.

        Args:
            field_name: The name of the field that must be unique.
            value: The value that caused the violation.
            entity_type: The type of entity being created/updated.
            status_code: The HTTP status code (typically 409 Conflict).
            error_code: The custom error code.

        Returns:
            A MockResponse object representing the unique constraint error.
        """
        ...

    @staticmethod
    def create_foreign_key_constraint_error(
        field_name: str,
        value: Any,
        referenced_entity: str,
        status_code: int = 422,
        error_code: str = "FOREIGN_KEY_CONSTRAINT_VIOLATION",
    ) -> MockResponse:
        """
        Creates a MockResponse for a foreign key constraint violation.

        Args:
            field_name: The name of the foreign key field.
            value: The value provided for the foreign key.
            referenced_entity: The type of entity being referenced.
            status_code: The HTTP status code.
            error_code: The custom error code.

        Returns:
            A MockResponse object representing the foreign key constraint error.
        """
        ...

    @staticmethod
    def create_state_transition_error(
        entity_type: str,
        current_state: str,
        target_state: str,
        allowed_transitions: List[str],
        status_code: int = 422,
        error_code: str = "INVALID_STATE_TRANSITION",
    ) -> MockResponse:
        """
        Creates a MockResponse for an invalid state transition error.

        Args:
            entity_type: The type of entity whose state transition failed.
            current_state: The current state of the entity.
            target_state: The attempted target state.
            allowed_transitions: A list of valid target states from the current state.
            status_code: The HTTP status code.
            error_code: The custom error code.

        Returns:
            A MockResponse object representing the state transition error.
        """
        ...

    @staticmethod
    def create_dependency_constraint_error(
        entity_type: str,
        entity_id: str,
        dependent_entities: List[Dict[str, Any]],
        status_code: int = 422,
        error_code: str = "DEPENDENCY_CONSTRAINT_VIOLATION",
    ) -> MockResponse:
        """
        Creates a MockResponse for a dependency constraint violation.

        Args:
            entity_type: The type of the entity that cannot be modified/deleted.
            entity_id: The ID of the entity.
            dependent_entities: A list of entities that depend on this one.
            status_code: The HTTP status code.
            error_code: The custom error code.

        Returns:
            A MockResponse object representing the dependency constraint error.
        """
        ...

    @staticmethod
    def create_business_rule_validator(
        rule_name: str,
        validator_function: Callable[[Dict[str, Any]], bool],
        error_message: str,
        status_code: int = 422,
        error_code: str = "BUSINESS_RULE_VIOLATION",
        details_function: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> Callable[[Dict[str, Any]], Optional[MockResponse]]:
        """
        Creates a validator function based on a custom business rule.

        Args:
            rule_name: The name of the business rule.
            validator_function: A function that takes data and returns True if the rule passes, False otherwise.
            error_message: The error message to use if the rule fails.
            status_code: The status code for the error response.
            error_code: The error code for the error response.
            details_function: An optional function to generate details for the error response.

        Returns:
            A function that takes request data and returns a MockResponse if the rule fails, else None.
        """
        ...
