# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2025-06-02

### Changed
- **BREAKING**: Migrated all authentication strategies to use apiconfig library
- **BREAKING**: Consolidated auth module from 6 files to single `auth.py` file
- **BREAKING**: `BearerAuth` now uses `access_token=` parameter instead of `token=`
- **BREAKING**: Empty credentials now raise `AuthStrategyError` instead of being silently accepted
- **BREAKING**: Custom header names no longer supported in `BearerAuth` (use `CustomAuth` instead)
- **BREAKING**: `CustomAuth` callback validation errors now raise `AuthStrategyError` instead of `TypeError`
- **BREAKING**: `ApiKeyAuth` now validates that the API key cannot be empty

### Added
- Token expiration and refresh support in `BearerAuth`
- Stricter validation for all auth strategies
- `AuthStrategyError` for auth-specific exceptions
- Enhanced error messages with detailed validation feedback
- Support for immutable auth strategy instances
- Improved type hints and documentation

### Removed
- Redundant auth strategy implementations (now delegated to apiconfig)
- ~285 lines of duplicated authentication code
- Support for empty credentials in auth strategies
- Custom header name support in `BearerAuth`

### Migration Guide
To migrate from v0.7.x to v0.8.0:

1. **Update BearerAuth usage**:
   ```python
   # Old
   auth = BearerAuth(token="your_token")

   # New
   auth = BearerAuth(access_token="your_token")
   ```

2. **Handle empty credentials**:
   ```python
   # Old (silently accepted)
   auth = BasicAuth(username="", password="")

   # New (raises exception)
   try:
       auth = BasicAuth(username="", password="")
   except AuthStrategyError as e:
       print(f"Invalid credentials: {e}")
   ```

3. **Update custom headers**:
   ```python
   # Old
   auth = BearerAuth(token="token", header_name="X-Custom")

   # New
   def custom_header_callback(request):
       request.headers["X-Custom"] = f"Bearer token"
       return request

   auth = CustomAuth(apply_auth=custom_header_callback)
   ```

4. **Update exception handling**:
   ```python
   # Old
   try:
       auth = CustomAuth(apply_auth="not_callable")
   except TypeError:
       pass

   # New
   try:
       auth = CustomAuth(apply_auth="not_callable")
   except AuthStrategyError:
       pass
   ```

For detailed migration information, see the [auth migration documentation](docs/apiconfig_auth_migration/README.md).