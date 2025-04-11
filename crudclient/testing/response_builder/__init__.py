from .response import MockResponse


class ResponseBuilder:

    @staticmethod
    def create_validation_error(fields=None, status_code=422, error_code="VALIDATION_ERROR", message="Validation failed"):
        if fields is None:
            fields = {"field": "Invalid value"}

        data = {"error": {"code": error_code, "message": message, "fields": fields}}

        return MockResponse(status_code=status_code, json_data=data, headers={"Content-Type": "application/json"})

    @staticmethod
    def create_rate_limit_error(limit=100, remaining=0, reset_seconds=60, status_code=429):
        data = {"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Rate limit exceeded. Please try again later."}}

        headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_seconds),
        }

        return MockResponse(status_code=status_code, json_data=data, headers=headers)

    @staticmethod
    def create_auth_error(error_type="invalid_token", status_code=401):
        error_messages = {
            "invalid_token": "The access token is invalid or has expired",
            "invalid_credentials": "Invalid username or password",
            "missing_credentials": "Authentication credentials were not provided",
            "insufficient_scope": "The access token does not have the required scope",
            "mfa_required": "Multi-factor authentication is required",
        }

        message = error_messages.get(error_type, "Authentication failed")

        data = {"error": {"code": error_type.upper(), "message": message}}

        headers = {"Content-Type": "application/json", "WWW-Authenticate": f'Bearer error="{error_type}", error_description="{message}"'}

        return MockResponse(status_code=status_code, json_data=data, headers=headers)
