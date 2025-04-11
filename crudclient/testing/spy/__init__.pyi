"""
Spy components for the crudclient testing framework.

This module provides components focused on recording interactions with mock objects
for later verification. It includes both basic spy implementations and enhanced
spy implementations with more sophisticated features.
"""

from .api_spy import ApiSpy
from .base import SpyBase
from .client_spy import ClientSpy
from .crud_spy import CrudSpy
from .enhanced import (
    CallRecord,
    ClassSpy,
    EnhancedSpyBase,
    EnhancedSpyFactory,
    FunctionSpy,
    MethodSpy,
)
from .method_call import MethodCall
from .verification_helpers import (
    verify_call_arguments,
    verify_call_sequence,
    verify_call_timing,
    verify_no_unexpected_calls,
)

__all__ = [
    # Basic spy components
    "MethodCall",
    "SpyBase",
    "ApiSpy",
    "ClientSpy",
    "CrudSpy",
    # Enhanced spy components
    "CallRecord",
    "EnhancedSpyBase",
    "MethodSpy",
    "ClassSpy",
    "FunctionSpy",
    "EnhancedSpyFactory",
    # Verification helpers
    "verify_call_sequence",
    "verify_no_unexpected_calls",
    "verify_call_timing",
    "verify_call_arguments",
]
