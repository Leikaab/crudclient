from .auth_error_verification import AuthErrorVerification

# Re-export the classes from their respective modules
from .auth_extraction_utils import AuthExtractionUtils
from .auth_header_verification import AuthHeaderVerification
from .auth_token_verification import AuthTokenVerification


class AuthVerificationHelpers:

    # Header verification methods
    verify_basic_auth_header = AuthHeaderVerification.verify_basic_auth_header
    verify_bearer_auth_header = AuthHeaderVerification.verify_bearer_auth_header
    verify_api_key_header = AuthHeaderVerification.verify_api_key_header
    assert_auth_header_format = AuthHeaderVerification.assert_auth_header_format

    # Token verification methods
    verify_oauth_token = AuthTokenVerification.verify_oauth_token
    verify_token_refresh = AuthTokenVerification.verify_token_refresh
    verify_token_expiration = AuthTokenVerification.verify_token_expiration
    assert_token_usage = AuthTokenVerification.assert_token_usage
    assert_refresh_behavior = AuthTokenVerification.assert_refresh_behavior
    assert_token_has_scopes = AuthTokenVerification.assert_token_has_scopes

    # Extraction utilities
    extract_basic_auth_credentials = AuthExtractionUtils.extract_basic_auth_credentials
    extract_bearer_token = AuthExtractionUtils.extract_bearer_token
    extract_jwt_payload = AuthExtractionUtils.extract_jwt_payload

    # Error verification methods
    assert_auth_error_response = AuthErrorVerification.assert_auth_error_response
    assert_rate_limit_headers = AuthErrorVerification.assert_rate_limit_headers


# For backward compatibility
__all__ = ["AuthVerificationHelpers", "AuthExtractionUtils", "AuthHeaderVerification", "AuthTokenVerification", "AuthErrorVerification"]
