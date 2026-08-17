# Gordon Phase 5.7.6-I: Perspective Engine - Exceptions
# ===============================================================================
"""
Exception hierarchy for the Perspective Engine.

Defines custom exception types for perspective-related errors while maintaining
integration with the broader error handling system (Phase 3.7.35).
"""

from __future__ import annotations

from typing import Optional, Tuple


# =============================================================================
# BASE EXCEPTION
# =============================================================================

class PerspectiveError(Exception):
    """
    Base exception for all perspective-related errors.
    
    This is the root of the perspective engine exception hierarchy and
    integrates with Phase 3.7.35 failure handling patterns.
    """
    
    def __init__(self, message: str = "", *args: object) -> None:
        super().__init__(message, *args)
        self.message = message
    
    @property
    def error_type(self) -> str:
        """Get the error type name."""
        return self.__class__.__name__


# =============================================================================
# REFERENCE FRAME EXCEPTIONS
# =============================================================================

class ReferenceFrameError(PerspectiveError):
    """
    Exception for reference frame errors.
    
    Raised when a reference frame is invalid or cannot be constructed.
    """
    pass


class InvalidReferenceFrame(ReferenceFrameError):
    """
    Raised when a reference frame has invalid coordinates or properties.
    """
    pass


class FrameTransformError(ReferenceFrameError):
    """
    Raised when a frame transformation fails.
    """
    pass


# =============================================================================
# OBSERVER EXCEPTIONS
# =============================================================================

class ObserverError(PerspectiveError):
    """
    Exception for observer-related errors.
    
    Raised when an observer operation fails or state is invalid.
    """
    pass


class InvalidObserverState(ObserverError):
    """
    Raised when observer state is invalid or inconsistent.
    """
    pass


class ObserverCapacityExceeded(ObserverError):
    """
    Raised when observer capacity has been exceeded.
    """
    
    def __init__(self, max_capacity: int, current_count: int) -> None:
        super().__init__(
            f"Observer capacity exceeded: {current_count} >= {max_capacity}"
        )
        self.max_capacity = max_capacity
        self.current_count = current_count


# =============================================================================
# TRANSFORMATION EXCEPTIONS
# =============================================================================

class TransformationError(PerspectiveError):
    """
    Exception for viewpoint transformation errors.
    
    Raised when a perspective transformation fails or is invalid.
    """
    pass


class InvalidTransformationType(TransformationError):
    """
    Raised when an unknown or unsupported transformation type is requested.
    """
    
    def __init__(self, transform_type: str) -> None:
        super().__init__(f"Invalid transformation type: {transform_type}")
        self.transform_type = transform_type


class TransformationConflict(TransformationError):
    """
    Raised when a transformation conflicts with current state or constraints.
    """
    
    def __init__(self, reason: str) -> None:
        super().__init__(f"Transformation conflict: {reason}")
        self.reason = reason


# =============================================================================
# TRANSITION EXCEPTIONS
# =============================================================================

class TransitionError(PerspectiveError):
    """
    Exception for perspective transition errors.
    
    Raised when a perspective state transition fails or is invalid.
    """
    pass


class InvalidTransition(TransitionError):
    """
    Raised when a transition is invalid given current state.
    """
    
    def __init__(self, from_state: str, to_state: str, reason: str) -> None:
        super().__init__(
            f"Invalid transition from {from_state} to {to_state}: {reason}"
        )
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason


class TransitionConflict(TransitionError):
    """
    Raised when a transition conflicts with existing state.
    """
    
    def __init__(self, conflict_description: str) -> None:
        super().__init__(f"Transition conflict: {conflict_description}")
        self.conflict_description = conflict_description


# =============================================================================
# VALIDATION EXCEPTIONS
# =============================================================================

class ValidationError(PerspectiveError):
    """
    Exception for perspective validation errors.
    
    Raised when perspective state fails validation checks.
    """
    pass


class InvalidPerspectiveState(ValidationError):
    """
    Raised when perspective state is invalid or inconsistent.
    """
    
    def __init__(self, issues: list[str]) -> None:
        super().__init__(
            f"Invalid perspective state: {'; '.join(issues)}"
        )
        self.issues = issues


class InvalidSnapshot(ValidationError):
    """
    Raised when a snapshot fails validation.
    """
    
    def __init__(self, reason: str) -> None:
        super().__init__(f"Invalid snapshot: {reason}")
        self.reason = reason


# =============================================================================
# DIAGNOSTICS EXCEPTIONS
# =============================================================================

class DiagnosticsError(PerspectiveError):
    """
    Exception for diagnostics-related errors.
    
    Raised when diagnostic recording or reporting fails.
    """
    pass


class MetricCollectionFailure(DiagnosticsError):
    """
    Raised when metric collection fails unexpectedly.
    """
    pass


# =============================================================================
# INTEGRITY EXCEPTIONS
# =============================================================================

class IntegrityError(PerspectiveError):
    """
    Exception for perspective integrity violations.
    
    Raised when perspective state integrity cannot be guaranteed.
    """
    
    def __init__(self, message: str = "Integrity check failed") -> None:
        super().__init__(f"Perspective integrity error: {message}")
        self.message = message


class SnapshotCorruption(IntegrityError):
    """
    Raised when a perspective snapshot is corrupted or invalid.
    """
    
    def __init__(self, snapshot_id: str) -> None:
        super().__init__(
            f"Snapshot corruption detected for snapshot: {snapshot_id}"
        )
        self.snapshot_id = snapshot_id


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    # Base classes
    "PerspectiveError",
    
    # Reference frame exceptions
    "ReferenceFrameError",
    "InvalidReferenceFrame",
    "FrameTransformError",
    
    # Observer exceptions
    "ObserverError",
    "InvalidObserverState",
    "ObserverCapacityExceeded",
    
    # Transformation exceptions
    "TransformationError",
    "InvalidTransformationType",
    "TransformationConflict",
    
    # Transition exceptions
    "TransitionError",
    "InvalidTransition",
    "TransitionConflict",
    
    # Validation exceptions
    "ValidationError",
    "InvalidPerspectiveState",
    "InvalidSnapshot",
    
    # Diagnostics exceptions
    "DiagnosticsError",
    "MetricCollectionFailure",
    
    # Integrity exceptions
    "IntegrityError",
    "SnapshotCorruption",
)