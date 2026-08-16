# Default Network Exceptions
# =========================

"""
Network-specific exceptions for the DefaultNetwork.

These are semantic exceptions - they do NOT involve runtime error handling
machinery like thread management or resource cleanup.

PHASE 4.3.1: Semantic Exception Definitions
"""

from __future__ import annotations

from typing import Optional


# =============================================================================
# BASE EXCEPTION (semantic, no runtime machinery)
# =============================================================================

class DefaultNetworkError(Exception):
    """
    Base exception for DefaultNetwork errors.
    
    All DefaultNetwork-specific exceptions inherit from this.
    These are semantic exceptions - they describe validation failures,
    ownership violations, and other semantic issues without runtime
    resource management implications.
    """
    
    pass


# =============================================================================
# VALIDATION EXCEPTIONS (semantic validation failures)
# =============================================================================

class ValidationError(DefaultNetworkError):
    """Raised when validation fails for inputs, outputs, or assessments."""
    
    def __init__(self, message: str, check_id: Optional[str] = None) -> None:
        """
        Initialize a validation error.
        
        Args:
            message: Human-readable error description
            check_id: Optional identifier for the validation check that failed
        """
        self.check_id = check_id
        super().__init__(message)


class InputValidationError(ValidationError):
    """Raised when input validation fails."""
    
    pass


class OutputValidationError(ValidationError):
    """Raised when output validation fails."""
    
    pass


class AssessmentValidationError(ValidationError):
    """Raised when assessment validation fails."""
    
    pass


# =============================================================================
# CONFIGURATION EXCEPTIONS (semantic configuration failures)
# =============================================================================

class ConfigurationError(DefaultNetworkError):
    """Raised when configuration is invalid or inconsistent."""
    
    pass


class ActivationThresholdError(ConfigurationError):
    """Raised when activation thresholds are out of valid range."""
    
    pass


class CapacityBoundError(ConfigurationError):
    """Raised when a capacity bound would be exceeded."""
    
    pass


# =============================================================================
# STATE EXCEPTIONS (semantic state errors)
# =============================================================================

class StateError(DefaultNetworkError):
    """Raised when state operations fail or state is inconsistent."""
    
    pass


class StateTransitionError(StateError):
    """Raised when an invalid state transition is attempted."""
    
    pass


class StateBoundsError(StateError):
    """Raised when state would exceed bounded limits."""
    
    pass


# =============================================================================
# PROTOCOL EXCEPTIONS (semantic protocol violations)
# =============================================================================

class ProtocolError(DefaultNetworkError):
    """Raised when protocol requirements are violated."""
    
    pass


class OwnershipViolation(ProtocolError):
    """
    Raised when an operation attempts to own or mutate a system it shouldn't.
    
    This enforces the core architectural principle that networks do NOT own
    Memory, Consciousness, Action, or other canonical systems.
    """
    
    def __init__(self, message: str, violated_system: Optional[str] = None) -> None:
        """
        Initialize an ownership violation error.
        
        Args:
            message: Human-readable description of the violation
            violated_system: Optional name of the system whose ownership was violated
        """
        self.violated_system = violated_system
        super().__init__(message)


# =============================================================================
# BOUNDS EXCEPTIONS (semantic boundary violations)
# =============================================================================

class BoundsError(DefaultNetworkError):
    """Raised when a value would exceed semantic bounds."""
    
    pass


class InputBoundsError(BoundsError):
    """Raised when input exceeds allowed bounds."""
    
    pass


class OutputBoundsError(BoundsError):
    """Raised when output exceeds allowed bounds."""
    
    pass


class ActivationBoundsError(BoundsError):
    """Raised when activation level exceeds valid range."""
    
    pass


# =============================================================================
# UTILITY EXCEPTIONS (semantic utility failures)
# =============================================================================

class DiagnosticError(DefaultNetworkError):
    """Raised when diagnostics collection or emission fails."""
    
    pass


class HealthCheckError(DefaultNetworkError):
    """Raised when health check cannot be performed."""
    
    pass