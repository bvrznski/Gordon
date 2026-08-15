# Gordon Cognitive Architecture - Phase 4.5.1
# ===========================================

"""
Action Semantic Exceptions

Custom exception types for Action semantics operations.
These are purely semantic exceptions, not runtime execution errors.

Runtime-neutral: Yes
Executable: No
"""

from typing import Optional


class ActionSemanticError(Exception):
    """
    Base exception for Action semantic errors.
    
    This is the root of the Action semantic exception hierarchy.
    All Action-related semantic validation errors should derive from this.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    def __init__(self, message: str):
        super().__init__(message)


class ActionIdentityError(ActionSemanticError):
    """
    Exception raised for Action Identity related errors.
    
    This includes:
        - Invalid identity format
        - Identity mismatch
        - Revision lineage violation
    
    Runtime-neutral: Yes
    Executable: No
    """


class ActionRevisionError(ActionSemanticError):
    """
    Exception raised for Action Revision related errors.
    
    This includes:
        - Invalid revision number
        - Parent revision not found
        - Conceptual continuity violation
    
    Runtime-neutral: Yes
    Executable: No
    """


class ActionValidationError(ActionSemanticError):
    """
    Exception raised when Action validation fails.
    
    Runtime-neutral: Yes
    Executable: No
    """


class ActionConstraintViolation(ActionValidationError):
    """
    Exception raised when an Action violates a constraint.
    
    This indicates the Action is invalid due to:
        - Constraint violation
        - Policy or Security prohibition
        - Authority requirement not met
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    def __init__(self, message: str, constraint_kind: Optional[str] = None):
        self.constraint_kind = constraint_kind
        super().__init__(message)


class ActionBoundednessError(ActionValidationError):
    """
    Exception raised when Action boundedness is violated.
    
    This includes:
        - Collection exceeds maximum size
        - Target limit exceeded
        - Scope boundary violation
    
    Runtime-neutral: Yes
    Executable: No
    """


class ActionRuntimeNeutralityError(ActionSemanticError):
    """
    Exception raised when runtime state leaks into Action semantics.
    
    This is a serious architectural violation indicating:
        - Callback or executable code embedded in Action
        - Runtime handle stored in Action
        - Live subsystem object referenced
    
    Runtime-neutral: Yes
    Executable: No
    """


class ActionInvalidationError(ActionSemanticError):
    """
    Exception raised when an Action is invalidated.
    
    This indicates the Action can no longer be selected or executed:
        - Target changed
        - Context stale
        - Premise violated
    
    Runtime-neutral: Yes
    Executable: No
    """


class ActionAuthorizationError(ActionSemanticError):
    """
    Exception raised for Authorization-related errors.
    
    This includes:
        - Unauthorized action attempt
        - Authority expiration
        - Authorization scope violation
    
    Runtime-neutral: Yes
    Executable: No
    """


__all__ = [
    "ActionSemanticError",
    "ActionIdentityError",
    "ActionRevisionError",
    "ActionValidationError",
    "ActionConstraintViolation",
    "ActionBoundednessError",
    "ActionRuntimeNeutralityError",
    "ActionInvalidationError",
    "ActionAuthorizationError",
]