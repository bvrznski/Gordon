# Execution Failure Taxonomy
# ==========================

"""
Contract-level failures that may occur during execution.

These are neutral, stable failure types that cross Core-Execution boundaries.
Infrastructure-specific exceptions are translated to these before returning
to the execution layer.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, Any, Tuple


# =============================================================================
# Failure Categories (Neutral - no semantics)
# =============================================================================

class FailureCategory(Enum):
    """
    Category of failure for classification and handling.
    
    These categories determine:
        - Retry eligibility
        - Recovery options
        - Escalation path
        - Logging severity
    """
    
    # Execution-level failures
    EXECUTION_REJECTED = "execution_rejected"
    EXECUTION_UNAVAILABLE = "execution_unavailable"
    
    # Lifecycle failures
    LIFECYCLE_CONFLICT = "lifecycle_conflict"
    INVALID_TRANSITION = "invalid_transition"
    
    # Persistence failures
    CHECKPOINT_UNAVAILABLE = "checkpoint_unavailable"
    CHECKPOINT_CORRUPTED = "checkpoint_corrupted"
    
    # Recovery failures
    RECOVERY_UNAVAILABLE = "recovery_unavailable"
    
    # Resource failures
    RESOURCE_DENIED = "resource_denied"
    RESOURCE_REVOKED = "resource_revoked"
    
    # Cancellation-related
    CANCELLATION_REQUESTED = "cancellation_requested"
    
    # Timeout failures
    EXECUTION_TIMED_OUT = "execution_timed_out"
    
    # Contract violations
    CONTRACT_VIOLATION = "contract_violation"
    
    # Serialization failures
    SERIALIZATION_FAILURE = "serialization_failure"
    
    # Unsupported operations
    UNSUPPORTED_SNAPSHOT_VERSION = "unsupported_snapshot_version"
    
    # Infrastructure (translated from lower layer)
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"


# =============================================================================
# Failure Types (Neutral - no semantics)
# =============================================================================

class ExecutionRejected(Exception):
    """Execution request was rejected by Core."""
    pass


class ExecutionUnavailable(Exception):
    """Execution unit is unavailable (e.g., already terminated)."""
    pass


class LifecycleConflict(Exception):
    """Requested lifecycle transition conflicts with current state."""
    pass


class InvalidTransition(Exception):
    """Lifecycle transition is not allowed in the current state."""
    pass


class CheckpointUnavailable(Exception):
    """Checkpoint cannot be accessed for restoration."""
    pass


class CheckpointCorrupted(Exception):
    """Checkpoint exists but is corrupted or invalid."""
    pass


class RecoveryUnavailable(Exception):
    """Recovery mechanism is unavailable."""
    pass


class ResourceDenied(Exception):
    """Resource request was denied by Core."""
    pass


class ResourceRevoked(Exception):
    """Previously granted resource has been revoked."""
    pass


class ExecutionTimedOut(Exception):
    """Execution exceeded its time budget."""
    pass


class ContractViolation(Exception):
    """Contract boundary was violated (e.g., illegal import)."""
    pass


class SerializationFailure(Exception):
    """Failed to serialize or deserialize execution state."""
    pass


# =============================================================================
# Contract Failure Container
# =============================================================================

@dataclass(frozen=True)
class ContractFailure:
    """
    Structured failure information for Core-Execution boundary.
    
    This is what gets returned from Core contracts instead of raw exceptions.
    """
    
    code: str  # Machine-readable failure code
    category: FailureCategory
    message: str  # Human-readable explanation
    retryable: bool  # Can execution attempt this again?
    execution_id: Optional[str] = None  # Which unit failed (if any)
    recovery_hint: Optional[str] = None  # How might recovery work?
    
    # Additional diagnostic data
    source_layer: Optional[str] = None  # Where did it originate?
    causal_chain: Tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert failure to dictionary for serialization."""
        return {
            "code": self.code,
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "message": self.message,
            "retryable": self.retryable,
            "execution_id": self.execution_id,
            "recovery_hint": self.recovery_hint,
            "source_layer": self.source_layer,
        }
    
    @classmethod
    def from_exception(cls, exc: Exception) -> "ContractFailure":
        """Create a ContractFailure from an exception."""
        if isinstance(exc, cls.__class__):
            return exc
        
        # Translate common exception types to contract failures
        category = FailureCategory.EXECUTION_REJECTED
        code = "EXECUTION_REJECTED"
        
        if isinstance(exc, CheckpointUnavailable):
            category = FailureCategory.CHECKPOINT_UNAVAILABLE
            code = "CHECKPOINT_UNAVAILABLE"
        elif isinstance(exc, ResourceDenied):
            category = FailureCategory.RESOURCE_DENIED
            code = "RESOURCE_DENIED"
        elif isinstance(exc, ExecutionTimedOut):
            category = FailureCategory.EXECUTION_TIMED_OUT
            code = "EXECUTION_TIMED_OUT"
        elif isinstance(exc, ContractViolation):
            category = FailureCategory.CONTRACT_VIOLATION
            code = "CONTRACT_VIOLATION"
        
        return cls(
            code=code,
            category=category,
            message=str(exc),
            retryable=False,
            source_layer="core",
        )


__all__ = [
    # Categories
    "FailureCategory",
    
    # Exception types
    "ExecutionRejected",
    "ExecutionUnavailable", 
    "LifecycleConflict",
    "InvalidTransition",
    "CheckpointUnavailable",
    "CheckpointCorrupted",
    "RecoveryUnavailable",
    "ResourceDenied",
    "ResourceRevoked",
    "ExecutionTimedOut",
    "ContractViolation",
    "SerializationFailure",
    
    # Container
    "ContractFailure",
]