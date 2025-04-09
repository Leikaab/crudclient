"""
Validation error simulation for mock responses.

This module provides utilities for simulating schema validation errors
and business logic constraints in mock API responses. It includes tools
for creating validation error responses and validator functions for common
data types and business rules.
"""

from typing import Any, Dict, List, Optional, Union, Callable
import re
from datetime import datetime

from .response import MockResponse


class ValidationErrorBuilder:
    """
    Builder for creating mock responses with validation errors.

    This class provides methods to generate responses that simulate validation
    errors in various formats. It can be used to test how client code handles
    validation failures from APIs, with support for different error response
    formats used by various API styles.
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
        Create a response with schema validation errors.

        This method creates a response that simulates validation errors for specific
        fields, with support for different error response formats used by various
        API styles.

        Args:
            invalid_fields: Dictionary mapping field names to error messages
            status_code: HTTP status code for the response (typically 400 or 422)
            error_code: Error code for the validation error
            message: Overall error message
            error_format: Format of the error response (standard, json_api, detailed, simple)

        Returns:
            A MockResponse instance with validation errors in the specified format
        """
        if error_format == "standard":
            response_data = {
                "error": error_code,
                "message": message,
                "errors": [
                    {"field": field, "message": error_msg}
                    for field, error_msg in invalid_fields.items()
                ]
            }
        elif error_format == "json_api":
            response_data = {
                "errors": [
                    {
                        "status": str(status_code),
                        "code": error_code,
                        "title": message,
                        "source": {"pointer": f"/data/attributes/{field}"},
                        "detail": error_msg
                    }
                    for field, error_msg in invalid_fields.items()
                ]
            }
        elif error_format == "detailed":
            response_data = {
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": [
                        {
                            "field": field,
                            "message": error_msg,
                            "code": f"{error_code}_{field.upper()}"
                        }
                        for field, error_msg in invalid_fields.items()
                    ]
                }
            }
        else:
            # Simple format
            response_data = {
                "error": message,
                "fields": invalid_fields
            }

        return MockResponse(
            status_code=status_code,
            json_data=response_data
        )

    @staticmethod
    def create_field_validator(
        field_name: str,
        validators: List[Callable[[Any], Optional[str]]],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        error_format: str = "standard",
    ) -> Callable[[Dict[str, Any]], Optional[MockResponse]]:
        """
        Create a validator function for a specific field.

        This method creates a function that validates a specific field using
        the provided validator functions. If validation fails, it returns a
        MockResponse with appropriate error details.

        Args:
            field_name: Name of the field to validate
            validators: List of validator functions that return error messages or None if valid
            status_code: HTTP status code for validation error responses
            error_code: Error code for validation error responses
            error_format: Format of the error response

        Returns:
            A function that validates the field and returns a response or None if valid
        """
        def validator_function(data: Dict[str, Any]) -> Optional[MockResponse]:
            if not isinstance(data, dict):
                return ValidationErrorBuilder.create_schema_validation_error(
                    {field_name: "Invalid data format"},
                    status_code=status_code,
                    error_code=error_code,
                    error_format=error_format
                )

            if field_name not in data:
                return ValidationErrorBuilder.create_schema_validation_error(
                    {field_name: "Field is required"},
                    status_code=status_code,
                    error_code=error_code,
                    error_format=error_format
                )

            field_value = data[field_name]

            for validator in validators:
                error_message = validator(field_value)
                if error_message:
                    return ValidationErrorBuilder.create_schema_validation_error(
                        {field_name: error_message},
                        status_code=status_code,
                        error_code=error_code,
                        error_format=error_format
                    )

            return None  # No validation errors

        return validator_function

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
        Create a validator function for multiple fields.

        This method creates a function that validates multiple fields using
        the provided validator functions. If validation fails for any field,
        it returns a MockResponse with all validation errors.

        Args:
            validators: Dictionary mapping field names to lists of validator functions
            status_code: HTTP status code for validation error responses
            error_code: Error code for validation error responses
            message: Error message for validation error responses
            error_format: Format of the error response
            require_all_fields: Whether all fields are required

        Returns:
            A function that validates the data and returns a response or None if valid
        """
        def validator_function(data: Dict[str, Any]) -> Optional[MockResponse]:
            if not isinstance(data, dict):
                return ValidationErrorBuilder.create_schema_validation_error(
                    {"_general": "Invalid data format"},
                    status_code=status_code,
                    error_code=error_code,
                    message=message,
                    error_format=error_format
                )

            invalid_fields = {}

            for field_name, field_validators in validators.items():
                if field_name not in data:
                    if require_all_fields:
                        invalid_fields[field_name] = "Field is required"
                    continue

                field_value = data[field_name]

                for validator in field_validators:
                    error_message = validator(field_value)
                    if error_message:
                        invalid_fields[field_name] = error_message
                        break

            if invalid_fields:
                return ValidationErrorBuilder.create_schema_validation_error(
                    invalid_fields,
                    status_code=status_code,
                    error_code=error_code,
                    message=message,
                    error_format=error_format
                )

            return None  # No validation errors

        return validator_function


class BusinessLogicConstraintBuilder:
    """
    Builder for creating mock responses with business logic constraints.

    This class provides methods to generate responses that simulate business
    logic constraint violations, such as unique constraints, foreign key
    constraints, state transitions, and dependencies. These are useful for
    testing how client code handles business rule violations.
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
        Create a response with a business rule violation error.

        This method creates a response that simulates a violation of a business rule,
        with details about the rule that was violated.

        Args:
            rule_name: Name of the business rule that was violated
            message: Error message describing the violation
            status_code: HTTP status code for the response
            error_code: Error code for the response
            details: Additional details about the violation

        Returns:
            A MockResponse instance with business rule violation error
        """
        response_data: Dict[str, Any] = {
            "error": error_code,
            "message": message,
            "rule": rule_name
        }

        if details:
            response_data["details"] = details

        return MockResponse(
            status_code=status_code,
            json_data=response_data
        )

    @staticmethod
    def create_unique_constraint_error(
        field_name: str,
        value: Any,
        entity_type: str = "resource",
        status_code: int = 409,
        error_code: str = "UNIQUE_CONSTRAINT_VIOLATION",
    ) -> MockResponse:
        """
        Create a response with a unique constraint violation error.

        This method creates a response that simulates a violation of a unique
        constraint, such as attempting to create a resource with a duplicate
        unique identifier.

        Args:
            field_name: Name of the field with the unique constraint
            value: Value that violates the constraint
            entity_type: Type of entity with the constraint
            status_code: HTTP status code for the response
            error_code: Error code for the response

        Returns:
            A MockResponse instance with unique constraint violation error
        """
        message = f"A {entity_type} with {field_name} '{value}' already exists"

        return MockResponse(
            status_code=status_code,
            json_data={
                "error": error_code,
                "message": message,
                "field": field_name,
                "value": value
            }
        )

    @staticmethod
    def create_foreign_key_constraint_error(
        field_name: str,
        value: Any,
        referenced_entity: str,
        status_code: int = 422,
        error_code: str = "FOREIGN_KEY_CONSTRAINT_VIOLATION",
    ) -> MockResponse:
        """
        Create a response with a foreign key constraint violation error.

        This method creates a response that simulates a violation of a foreign key
        constraint, such as attempting to reference a non-existent resource.

        Args:
            field_name: Name of the field with the foreign key constraint
            value: Value that violates the constraint
            referenced_entity: Type of entity referenced by the foreign key
            status_code: HTTP status code for the response
            error_code: Error code for the response

        Returns:
            A MockResponse instance with foreign key constraint violation error
        """
        message = f"No {referenced_entity} found with {field_name} '{value}'"

        return MockResponse(
            status_code=status_code,
            json_data={
                "error": error_code,
                "message": message,
                "field": field_name,
                "value": value,
                "referenced_entity": referenced_entity
            }
        )

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
        Create a response with a state transition error.

        This method creates a response that simulates an invalid state transition,
        such as attempting to move a resource from one state to another when that
        transition is not allowed.

        Args:
            entity_type: Type of entity with the state
            current_state: Current state of the entity
            target_state: Target state that is not allowed
            allowed_transitions: List of allowed transitions from the current state
            status_code: HTTP status code for the response
            error_code: Error code for the response

        Returns:
            A MockResponse instance with state transition error
        """
        message = f"Cannot transition {entity_type} from '{current_state}' to '{target_state}'"

        return MockResponse(
            status_code=status_code,
            json_data={
                "error": error_code,
                "message": message,
                "current_state": current_state,
                "target_state": target_state,
                "allowed_transitions": allowed_transitions
            }
        )

    @staticmethod
    def create_dependency_constraint_error(
        entity_type: str,
        entity_id: str,
        dependent_entities: List[Dict[str, Any]],
        status_code: int = 422,
        error_code: str = "DEPENDENCY_CONSTRAINT_VIOLATION",
    ) -> MockResponse:
        """
        Create a response with a dependency constraint error.

        This method creates a response that simulates a dependency constraint
        violation, such as attempting to delete a resource that has dependent
        resources.

        Args:
            entity_type: Type of entity with dependencies
            entity_id: ID of the entity
            dependent_entities: List of dependent entities
            status_code: HTTP status code for the response
            error_code: Error code for the response

        Returns:
            A MockResponse instance with dependency constraint error
        """
        message = f"Cannot perform operation on {entity_type} '{entity_id}' due to existing dependencies"

        return MockResponse(
            status_code=status_code,
            json_data={
                "error": error_code,
                "message": message,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "dependencies": dependent_entities
            }
        )

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
        Create a validator function for a business rule.

        This method creates a function that validates a business rule using
        the provided validator function. If validation fails, it returns a
        MockResponse with appropriate error details.

        Args:
            rule_name: Name of the business rule
            validator_function: Function that returns True if the rule is satisfied
            error_message: Error message if the rule is violated
            status_code: HTTP status code for error responses
            error_code: Error code for error responses
            details_function: Function to generate additional details about the violation

        Returns:
            A function that validates the business rule and returns a response or None if valid
        """
        def rule_validator(data: Dict[str, Any]) -> Optional[MockResponse]:
            if not validator_function(data):
                details = None
                if details_function:
                    details = details_function(data)

                return BusinessLogicConstraintBuilder.create_business_rule_error(
                    rule_name=rule_name,
                    message=error_message,
                    status_code=status_code,
                    error_code=error_code,
                    details=details
                )

            return None  # Rule satisfied

        return rule_validator


# Common validator functions
def required_field(value: Any) -> Optional[str]:
    """
    Validate that a field is not None or empty.

    Args:
        value: The value to validate

    Returns:
        An error message if validation fails, None otherwise
    """
    if value is None:
        return "Field is required"
    if isinstance(value, str) and not value.strip():
        return "Field cannot be empty"
    return None


def min_length(min_len: int) -> Callable[[Any], Optional[str]]:
    """
    Validate that a string has a minimum length.

    Args:
        min_len: The minimum length required

    Returns:
        A validator function that returns an error message if validation fails
    """
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return "Field must be a string"
        if len(value) < min_len:
            return f"Field must be at least {min_len} characters long"
        return None
    return validator


def max_length(max_len: int) -> Callable[[Any], Optional[str]]:
    """
    Validate that a string has a maximum length.

    Args:
        max_len: The maximum length allowed

    Returns:
        A validator function that returns an error message if validation fails
    """
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return "Field must be a string"
        if len(value) > max_len:
            return f"Field cannot be longer than {max_len} characters"
        return None
    return validator


def pattern_match(pattern: str, error_msg: str = "Field has invalid format") -> Callable[[Any], Optional[str]]:
    """
    Validate that a string matches a pattern.

    Args:
        pattern: The regex pattern to match
        error_msg: The error message to return if validation fails

    Returns:
        A validator function that returns an error message if validation fails
    """
    regex = re.compile(pattern)

    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return "Field must be a string"
        if not regex.match(value):
            return error_msg
        return None
    return validator


def min_value(min_val: Union[int, float]) -> Callable[[Any], Optional[str]]:
    """
    Validate that a number is at least a minimum value.

    Args:
        min_val: The minimum value allowed

    Returns:
        A validator function that returns an error message if validation fails
    """
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, (int, float)):
            return "Field must be a number"
        if value < min_val:
            return f"Field must be at least {min_val}"
        return None
    return validator


def max_value(max_val: Union[int, float]) -> Callable[[Any], Optional[str]]:
    """
    Validate that a number is at most a maximum value.

    Args:
        max_val: The maximum value allowed

    Returns:
        A validator function that returns an error message if validation fails
    """
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, (int, float)):
            return "Field must be a number"
        if value > max_val:
            return f"Field cannot be greater than {max_val}"
        return None
    return validator


def one_of(allowed_values: List[Any], error_msg: str = "Field has invalid value") -> Callable[[Any], Optional[str]]:
    """
    Validate that a value is one of a set of allowed values.

    Args:
        allowed_values: The list of allowed values
        error_msg: The error message to return if validation fails

    Returns:
        A validator function that returns an error message if validation fails
    """
    def validator(value: Any) -> Optional[str]:
        if value not in allowed_values:
            return error_msg
        return None
    return validator


def is_email() -> Callable[[Any], Optional[str]]:
    """
    Validate that a string is a valid email address.

    Returns:
        A validator function that returns an error message if validation fails
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return pattern_match(email_pattern, "Field must be a valid email address")


def is_url() -> Callable[[Any], Optional[str]]:
    """
    Validate that a string is a valid URL.

    Returns:
        A validator function that returns an error message if validation fails
    """
    url_pattern = r"^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w%!$&'()*+,;=:]+)*(?:\?[-\w%!$&'()*+,;=:/?]+)?(?:#[-\w%!$&'()*+,;=:/?]+)?$"
    return pattern_match(url_pattern, "Field must be a valid URL")


def is_date(format_str: str = "%Y-%m-%d") -> Callable[[Any], Optional[str]]:
    """
    Validate that a string is a valid date in the specified format.

    Args:
        format_str: The expected date format

    Returns:
        A validator function that returns an error message if validation fails
    """
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return "Field must be a string"
        try:
            datetime.strptime(value, format_str)
            return None
        except ValueError:
            return f"Field must be a valid date in the format {format_str}"
    return validator
