# Oriented Network Exceptions
# ============================

"""
Exception types for the OrientedNetwork.

Phase 4.7.1: Minimal Error Model Scaffold
"""

from __future__ import annotations


# =============================================================================
# PHASE 4.7.1: ERROR ROOT
# =============================================================================

class OrientedNetworkError(Exception):
    """
    Root exception type for all Oriented Network errors.
    """

    pass


# =============================================================================
# PHASE 4.7.1: CONFIGURATION ERRORS
# =============================================================================

class OrientedNetworkConfigurationError(OrientedNetworkError):
    """
    Raised when configuration validation fails.
    """

    def __init__(self, message: str, **context) -> None:
        super().__init__(message)
        self.context = context


# =============================================================================
# PHASE 4.7.1: INITIALIZATION ERRORS
# =============================================================================

class OrientedNetworkInitializationError(OrientedNetworkError):
    """
    Raised when network initialization fails.
    """

    def __init__(self, message: str, **context) -> None:
        super().__init__(message)
        self.context = context


# =============================================================================
# PHASE 4.7.1: SCAFFOLD ERRORS
# =============================================================================

class OrientedNetworkScaffoldError(OrientedNetworkError):
    """
    Raised when attempting an operation that is deferred to future phases.
    """

    def __init__(self, message: str, **context) -> None:
        super().__init__(message)
        self.context = context


# =============================================================================
# PHASE 4.7.1: UNSUPPORTED OPERATION ERRORS
# =============================================================================

class OrientedNetworkUnsupportedOperationError(OrientedNetworkError):
    """
    Raised when attempting an operation not supported in this phase.
    """

    def __init__(self, message: str, **context) -> None:
        super().__init__(message)
        self.context = context