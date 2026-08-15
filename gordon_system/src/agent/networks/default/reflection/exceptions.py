# Reflection Coordination Exceptions
# ==================================

"""
Domain-specific exception types for reflection coordination.

ARCHITECTURAL PRINCIPLES:
    - All exceptions inherit from base CoordinationException
    - Each exception is typed and descriptive
    - Exceptions are raised at validation time, not runtime
"""

from __future__ import annotations


class ReflectionCoordinationError(Exception):
    """Base exception for all reflection coordination errors."""
    pass


# =============================================================================
# REQUEST VALIDATION EXCEPTIONS
# =============================================================================

class InvalidReflectionRequest(ReflectionCoordinationError):
    """Raised when a reflection request is invalid."""
    
    def __init__(self, message: str = "Invalid reflection request", details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class InvalidReflectionPurpose(ReflectionCoordinationError):
    """Raised when a reflection purpose is invalid."""
    
    def __init__(self, purpose: str, message: str = "Invalid reflection purpose"):
        self.purpose = purpose
        self.message = f"{message}: {purpose}"
        super().__init__(self.message)


class InvalidReflectionSubject(ReflectionCoordinationError):
    """Raised when a reflection subject is invalid."""
    
    def __init__(self, subject: str, message: str = "Invalid reflection subject"):
        self.subject = subject
        self.message = f"{message}: {subject}"
        super().__init__(self.message)


class InvalidReflectionScope(ReflectionCoordinationError):
    """Raised when a reflection scope is invalid."""
    
    def __init__(self, message: str = "Invalid reflection scope", constraints: tuple | None = None):
        self.constraints = constraints or ()
        self.message = f"{message}: {', '.join(self.constraints)}"
        super().__init__(self.message)


# =============================================================================
# RECURSION EXCEPTIONS
# =============================================================================

class ReflectionRecursionLimitExceeded(ReflectionCoordinationError):
    """Raised when recursion depth limit would be exceeded."""
    
    def __init__(
        self,
        current_depth: int,
        max_depth: int,
        message: str = "Reflection recursion limit exceeded",
    ):
        self.current_depth = current_depth
        self.max_depth = max_depth
        self.message = f"{message}: depth={current_depth}, max={max_depth}"
        super().__init__(self.message)


class RepeatedReflectionRejected(ReflectionCoordinationError):
    """Raised when an equivalent reflection without new evidence is rejected."""
    
    def __init__(
        self,
        parent_purpose: str,
        parent_subject: str,
        message: str = "Repeated equivalent reflection rejected",
    ):
        self.parent_purpose = parent_purpose
        self.parent_subject = parent_subject
        self.message = f"{message}: purpose={parent_purpose}, subject={parent_subject}"
        super().__init__(self.message)


# =============================================================================
# VALIDATION EXCEPTIONS
# =============================================================================

class ReflectionInvariantViolation(ReflectionCoordinationError):
    """Raised when an architectural invariant is violated."""
    
    def __init__(
        self,
        invariant_id: str,
        message: str = "Architectural invariant violated",
    ):
        self.invariant_id = invariant_id
        self.message = f"{message}: {invariant_id}"
        super().__init__(self.message)


class InvalidReflectionPlan(ReflectionCoordinationError):
    """Raised when a reflection plan is invalid."""
    
    def __init__(
        self,
        plan_id: str,
        message: str = "Invalid reflection plan",
        issues: tuple | None = None,
    ):
        self.plan_id = plan_id
        self.issues = issues or ()
        self.message = f"{message}: {plan_id}, issues={', '.join(self.issues)}"
        super().__init__(self.message)


class InvalidReflectionEvidence(ReflectionCoordinationError):
    """Raised when reflection evidence is invalid."""
    
    def __init__(
        self,
        evidence_id: str,
        message: str = "Invalid reflection evidence",
    ):
        self.evidence_id = evidence_id
        self.message = f"{message}: {evidence_id}"
        super().__init__(self.message)


class InvalidReflectionOutcome(ReflectionCoordinationError):
    """Raised when a reflection outcome is invalid."""
    
    def __init__(
        self,
        outcome_kind: str,
        message: str = "Invalid reflection outcome",
    ):
        self.outcome_kind = outcome_kind
        self.message = f"{message}: {outcome_kind}"
        super().__init__(self.message)


# =============================================================================
# CAPABILITY EXCEPTIONS
# =============================================================================

class ReflectionCapabilityUnavailable(ReflectionCoordinationError):
    """Raised when a capability is unavailable."""
    
    def __init__(
        self,
        capability_category: str,
        message: str = "Reflection capability unavailable",
    ):
        self.capability_category = capability_category
        self.message = f"{message}: {capability_category}"
        super().__init__(self.message)


class ReflectionCapabilityFailure(ReflectionCoordinationError):
    """Raised when a capability fails to complete."""
    
    def __init__(
        self,
        request_id: str,
        error_category: str,
        message: str = "Reflection capability failure",
    ):
        self.request_id = request_id
        self.error_category = error_category
        self.message = f"{message}: {request_id}, error={error_category}"
        super().__init__(self.message)