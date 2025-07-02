# Testing Helper Consolidation

This document outlines overlaps between `crudclient.testing` and `apiconfig.testing` and proposes consolidating utilities to simplify maintenance.

## Observed Overlaps

- `crudclient.testing.auth.auth_header_verification` only re-exports `apiconfig.testing.auth_verification.AuthHeaderVerification`.
- `crudclient.testing.auth.verification.AuthVerificationHelpers` duplicated functionality provided by `apiconfig.testing.auth_verification` (e.g. header checks, JWT helpers, `AuthTestHelpers`) and has now been removed.
- The `Verifier` class in `crudclient.testing.verification` is a generic utility for asserting calls on spies/mocks. It could be useful for other packages.

## Proposed Changes

1. **Re-export from `apiconfig.testing`**
   - Remove `crudclient.testing.auth.auth_header_verification` and import `AuthHeaderVerification` directly from `apiconfig.testing`.
   - Replace `AuthVerificationHelpers` with the helpers already available in `apiconfig.testing` such as `AuthHeaderVerification`, `AdvancedAuthVerification`, and `AuthTestHelpers`.
2. **Move `Verifier` to `apiconfig.testing`**
   - Transfer the implementation of `Verifier` and its `SpyTarget` protocol to `apiconfig.testing` so both projects rely on the same mock verification logic.
   - Keep re-exports in `crudclient.testing` for backward compatibility.
3. **Update Documentation and Changelog**
   - Document the migration path for users in the changelog.
   - Update examples in the `crudclient.testing` README to show imports from `apiconfig.testing`.

## Benefits

- **Reduced duplication**: one canonical implementation of auth and verification helpers.
- **Easier maintenance**: fixes and new features only need to be implemented once.
- **Shared utilities**: other projects using `apiconfig` gain access to `Verifier`.
