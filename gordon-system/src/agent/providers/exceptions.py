# Provider Exceptions - Error Taxonomy
# =====================================
"""
Provider error types for consistent failure handling across all providers.

This module defines Gordon-owned exception types that providers translate
their implementation-specific errors into.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import asyncio


@dataclass(frozen=True)
class ProviderError(Exception):
    """
    Base exception for all provider-related errors.
    
    All provider exceptions should inherit from this and provide:
    - provider_id: Which provider failed
    - operation: What operation was being attempted
    - retryable: Whether the operation can be retried
    - underlying_cause: The original error for debugging
    """
    message: str
    provider_id: Optional[str] = None
    operation: Optional[str] = None
    retryable: bool = False
    underlying_cause: Optional[Exception] = None
    
    def __str__(self) -> str:
        parts = [f"ProviderError: {self.message}"]
        if self.provider_id:
            parts.append(f"provider={self.provider_id}")
        if self.operation:
            parts.append(f"operation={self.operation}")
        return "; ".join(parts)


@dataclass(frozen=True)
class ProviderConfigError(ProviderError):
    """Provider configuration is invalid or incomplete."""
    field: Optional[str] = None
    
    @classmethod
    def missing_field(cls, field: str, provider_id: str) -> "ProviderConfigError":
        return cls(
            message=f"Missing required configuration field: {field}",
            provider_id=provider_id,
            operation="configuration",
            retryable=False,
            field=field
        )
    
    @classmethod
    def invalid_value(cls, field: str, value: Any, expected: str, provider_id: str) -> "ProviderConfigError":
        return cls(
            message=f"Invalid configuration value for '{field}': {value} (expected: {expected})",
            provider_id=provider_id,
            operation="configuration",
            retryable=False,
            field=field
        )


@dataclass(frozen=True)
class ProviderAuthenticationError(ProviderError):
    """Authentication or authorization failed."""
    
    @classmethod
    def invalid_credentials(cls, provider_id: str) -> "ProviderAuthenticationError":
        return cls(
            message="Invalid credentials",
            provider_id=provider_id,
            operation="authentication",
            retryable=False
        )
    
    @classmethod
    def expired_token(cls, provider_id: str) -> "ProviderAuthenticationError":
        return cls(
            message="Token has expired",
            provider_id=provider_id,
            operation="authentication",
            retryable=True
        )


@dataclass(frozen=True)
class ProviderNotReadyError(ProviderError):
    """Provider is not ready to accept requests."""
    
    @classmethod
    def uninitialized(cls, provider_id: str) -> "ProviderNotReadyError":
        return cls(
            message=f"Provider '{provider_id}' has not been initialized",
            provider_id=provider_id,
            operation="request",
            retryable=False
        )
    
    @classmethod
    def initializing(cls, provider_id: str) -> "ProviderNotReadyError":
        return cls(
            message=f"Provider '{provider_id}' is still initializing",
            provider_id=provider_id,
            operation="request",
            retryable=True
        )


@dataclass(frozen=True)
class ProviderUnavailableError(ProviderError):
    """Provider is unavailable (server down, connection refused, etc.)."""
    
    @classmethod
    def network_error(cls, provider_id: str, cause: Optional[Exception] = None) -> "ProviderUnavailableError":
        return cls(
            message="Network error",
            provider_id=provider_id,
            operation="request",
            retryable=True,
            underlying_cause=cause
        )
    
    @classmethod
    def server_error(cls, provider_id: str, status_code: Optional[int] = None) -> "ProviderUnavailableError":
        status = f" (status={status_code})" if status_code else ""
        return cls(
            message=f"Provider server error{status}",
            provider_id=provider_id,
            operation="request",
            retryable=True
        )


@dataclass(frozen=True)
class ProviderTimeoutError(ProviderError, asyncio.TimeoutError):
    """Request timed out."""
    
    @classmethod
    def connection_timeout(cls, provider_id: str) -> "ProviderTimeoutError":
        return cls(
            message="Connection timeout",
            provider_id=provider_id,
            operation="request",
            retryable=True
        )
    
    @classmethod
    def request_timeout(cls, provider_id: str, deadline: float) -> "ProviderTimeoutError":
        return cls(
            message=f"Request timed out after {deadline}s",
            provider_id=provider_id,
            operation="request",
            retryable=False  # Non-idempotent requests shouldn't be retried
        )


@dataclass(frozen=True)
class ProviderResourceError(ProviderError):
    """Resource allocation or management error."""
    
    @classmethod
    def gpu_oom(cls, provider_id: str) -> "ProviderResourceError":
        return cls(
            message="GPU out of memory",
            provider_id=provider_id,
            operation="inference",
            retryable=False  # Requires user intervention to reduce load
        )
    
    @classmethod
    def max_concurrent_exceeded(cls, provider_id: str) -> "ProviderResourceError":
        return cls(
            message="Maximum concurrent requests exceeded",
            provider_id=provider_id,
            operation="request",
            retryable=True
        )


@dataclass(frozen=True)
class ProviderCapabilityError(ProviderError):
    """Requested capability is not supported."""
    
    @classmethod
    def unsupported_capability(cls, provider_id: str, capability: str) -> "ProviderCapabilityError":
        return cls(
            message=f"Capability '{capability}' is not supported",
            provider_id=provider_id,
            operation="request",
            retryable=False
        )
    
    @classmethod
    def unsupported_model(cls, provider_id: str, model_id: str) -> "ProviderCapabilityError":
        return cls(
            message=f"Model '{model_id}' is not loaded or supported",
            provider_id=provider_id,
            operation="request",
            retryable=False
        )


@dataclass(frozen=True)
class ProviderRequestError(ProviderError):
    """Client request is invalid."""
    
    @classmethod
    def validation_error(cls, provider_id: str, message: str) -> "ProviderRequestError":
        return cls(
            message=f"Request validation failed: {message}",
            provider_id=provider_id,
            operation="request",
            retryable=False
        )
    
    @classmethod
    def context_overflow(cls, provider_id: str, requested: int, max_tokens: int) -> "ProviderRequestError":
        return cls(
            message=f"Context overflow: requested {requested} tokens, max is {max_tokens}",
            provider_id=provider_id,
            operation="request",
            retryable=False
        )


@dataclass(frozen=True)
class ProviderResponseError(ProviderError):
    """Provider response could not be processed."""
    
    @classmethod
    def malformed_response(cls, provider_id: str) -> "ProviderResponseError":
        return cls(
            message="Malformed provider response",
            provider_id=provider_id,
            operation="response",
            retryable=False
        )
    
    @classmethod
    def incomplete_stream(cls, provider_id: str) -> "ProviderResponseError":
        return cls(
            message="Stream ended prematurely",
            provider_id=provider_id,
            operation="streaming",
            retryable=False
        )


@dataclass(frozen=True)
class ProviderRateLimitError(ProviderError):
    """Rate limit exceeded."""
    
    @classmethod
    def request_rate_limited(cls, provider_id: str) -> "ProviderRateLimitError":
        return cls(
            message="Request rate limited",
            provider_id=provider_id,
            operation="request",
            retryable=True
        )
    
    @classmethod
    def token_rate_limited(cls, provider_id: str) -> "ProviderRateLimitError":
        return cls(
            message="Token rate limited",
            provider_id=provider_id,
            operation="request",
            retryable=True
        )


@dataclass(frozen=True)
class ProviderInternalError(ProviderError):
    """Provider internal error (bug, unexpected state, etc.)."""
    
    @classmethod
    def internal_error(cls, provider_id: str) -> "ProviderInternalError":
        return cls(
            message="Internal provider error",
            provider_id=provider_id,
            operation="request",
            retryable=False  # Indicates a bug that needs fixing
        )
    
    @classmethod
    def state_mismatch(cls, provider_id: str, expected: str, actual: str) -> "ProviderInternalError":
        return cls(
            message=f"State mismatch: expected {expected}, got {actual}",
            provider_id=provider_id,
            operation="request",
            retryable=False
        )


# Exception classification utilities

def classify_error(error: Exception) -> Dict[str, Any]:
    """
    Classify an error for handling and observability.
    
    Returns a dictionary with:
    - category: One of the分类 categories
    - retryable: Whether to retry
    - log_level: Logging level to use
    - alert: Whether this should trigger an alert
    """
    result = {
        "category": "unknown",
        "retryable": False,
        "log_level": "error",
        "alert": False
    }
    
    if isinstance(error, ProviderConfigError):
        result.update({
            "category": "configuration",
            "retryable": False,
            "log_level": "warning",
            "alert": True  # Configuration errors need attention
        })
    
    elif isinstance(error, ProviderAuthenticationError):
        result.update({
            "category": "authentication",
            "retryable": False,
            "log_level": "error",
            "alert": True
        })
    
    elif isinstance(error, (ProviderNotReadyError, ProviderUnavailableError)):
        result.update({
            "category": "availability",
            "retryable": True,
            "log_level": "warning",
            "alert": False
        })
    
    elif isinstance(error, ProviderTimeoutError):
        result.update({
            "category": "timeout",
            "retryable": error.retryable,
            "log_level": "warning",
            "alert": False
        })
    
    elif isinstance(error, (ProviderResourceError, ProviderCapabilityError)):
        result.update({
            "category": "resource_or_capability",
            "retryable": False,
            "log_level": "error",
            "alert": True
        })
    
    elif isinstance(error, ProviderRequestError):
        result.update({
            "category": "client_request",
            "retryable": False,
            "log_level": "warning",
            "alert": False  # User error, not provider issue
        })
    
    elif isinstance(error, ProviderResponseError):
        result.update({
            "category": "provider_response",
            "retryable": False,
            "log_level": "error",
            "alert": True
        })
    
    elif isinstance(error, ProviderRateLimitError):
        result.update({
            "category": "rate_limit",
            "retryable": True,
            "log_level": "info",
            "alert": False
        })
    
    elif isinstance(error, ProviderInternalError):
        result.update({
            "category": "internal",
            "retryable": False,
            "log_level": "error",
            "alert": True  # Likely a bug
        })
    
    else:
        # Unknown error - classify conservatively
        result.update({
            "category": "unknown",
            "retryable": False,
            "log_level": "error",
            "alert": True
        })
    
    return result


__all__ = [
    # Base exception
    "ProviderError",
    
    # Configuration errors
    "ProviderConfigError",
    
    # Availability errors
    "ProviderNotReadyError",
    "ProviderUnavailableError",
    "ProviderTimeoutError",
    
    # Resource errors
    "ProviderResourceError",
    
    # Capability errors
    "ProviderCapabilityError",
    
    # Request/response errors
    "ProviderRequestError",
    "ProviderResponseError",
    
    # Rate limiting
    "ProviderRateLimitError",
    
    # Internal errors
    "ProviderInternalError",
    
    # Utility
    "classify_error",
]