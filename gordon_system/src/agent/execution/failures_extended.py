# Extended Execution Failure Types
# ================================
#
# PHASE 3.10.14 - Failure Provenance Enhancements

"""
Extended failure types with provenance tracking.

These types provide:
    - Detailed categorization of failures
    - Traceable causal chains
    - Recovery guidance
    - Retry safety information
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple
from enum import Enum
import uuid


# =============================================================================
# Failure Categories (Extended)
# =============================================================================

class ExecutionFailureCategory(Enum):
    """
    Category of failure for classification and handling.
    
    These categories determine:
        - Retry eligibility
        - Recovery options  
        - Escalation path
        - Logging severity
    
    Semantic failures (can be recovered by retrying with different approach):
        - SEMANTIC: Logic or constraint violation
        - VALIDATION: Input validation failure
        - LOOP_SELECTION: Loop couldn't select a valid cycle
        
    Infrastructure failures (external system issues, may need external fix):
        - INFRASTRUCTURE: Lower-level error
        - CAPABILITY: Capability invocation failed
        - TIMEOUT: Execution exceeded time budget
        
    Lifecycle failures (thread state issues):
        - LIFECYCLE_CONFLICT: State transition conflict
        - REVISION_CONFLICT: Thread revision mismatch
        
    Budget/Resource failures:
        - BUDGET_EXHAUSTED: Resource limit reached
        - CHILD_LIMIT_REACHED: Too many child threads
        - CYCLE_LIMIT_REACHED: Too many cycles for thread
        
    Cancellation/interruption (not really failure, but terminal):
        - CANCELLATION: Execution was cancelled
        - INTERRUPTION: Execution was interrupted
        
    Security:
        - SECURITY_VIOLATION: Unauthorized operation attempted
    """
    
    # Semantic failures (can be recovered by different approach)
    SEMANTIC = "semantic"
    VALIDATION = "validation"
    LOOP_SELECTION = "loop_selection"
    
    # Infrastructure failures (external system issues)
    INFRASTRUCTURE = "infrastructure"
    CAPABILITY = "capability"
    TIMEOUT = "timeout"
    
    # Lifecycle failures
    LIFECYCLE_CONFLICT = "lifecycle_conflict"
    REVISION_CONFLICT = "revision_conflict"
    
    # Budget/Resource failures
    BUDGET_EXHAUSTED = "budget_exhausted"
    CHILD_LIMIT_REACHED = "child_limit_reached"
    CYCLE_LIMIT_REACHED = "cycle_limit_reached"
    
    # Cancellation/interruption
    CANCELLATION = "cancellation"
    INTERRUPTION = "interruption"
    
    # Security failures
    SECURITY_VIOLATION = "security_violation"


class ExecutionFailureLayer(Enum):
    """
    Layer where failure originated.
    
    Helps determine appropriate handling and escalation.
    """
    
    COORDINATOR = "coordinator"
    THREAD = "thread"
    LOOP = "loop"
    CYCLE = "cycle"
    STAGE = "stage"
    CAPABILITY = "capability"
    CORE = "core"  # Core infrastructure layer


# =============================================================================
# Extended Failure Record
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExecutionFailure:
    """
    Structured failure record with provenance tracking.
    
    A failure record should distinguish:
        - SEMANTIC: Logic or constraint violation (can retry with different approach)
        - VALIDATION: Input validation failure (fix input, then retry)
        - LIFECYCLE: Thread state transition conflict
        - REVISION_CONFLICT: Expected vs actual thread revision mismatch
        - CAPABILITY: Capability invocation failed
        - INFRASTRUCTURE: Lower-level error (network, resource exhaustion)
        - CANCELLATION: Execution was cancelled (not really a failure)
        - INTERRUPTION: Execution was interrupted (temporary loss of control)
        - BUDGET: Resource budget exhausted
        - SECURITY: Unauthorized operation attempted
    
    The key insight is that failures have:
        1. A category (what kind of problem?)
        2. A layer (where did it happen?)
        3. A recovery story (can we retry? what's needed?)
        4. Provenance (why did it happen, causal chain)
    """
    
    # Core failure info
    category: ExecutionFailureCategory
    code: str  # Machine-readable error code
    message: str  # Human-readable explanation
    
    # Context
    layer: ExecutionFailureLayer
    source_id: str  # Which component reported this? (thread/loop/cycle/stage ID)
    
    # Recovery guidance
    recoverable: bool  # Can execution attempt this again?
    retry_safe: bool   # Is it safe to retry without side effects?
    
    # Provenance
    cause_reference: Optional[str] = None  # Reference to what caused this
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    occurred_at_utc: float = field(default_factory=lambda: 0.0)
    failure_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    
    @classmethod
    def semantic(
        cls,
        message: str,
        source_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "ExecutionFailure":
        """Create a semantic failure."""
        import time
        return cls(
            category=ExecutionFailureCategory.SEMANTIC,
            code="SEMANTIC_ERROR",
            message=message,
            layer=ExecutionFailureLayer.STAGE,
            source_id=source_id,
            recoverable=True,  # Can retry with different approach
            retry_safe=True,   # No side effects if we try again
            occurred_at_utc=time.monotonic(),
            metadata=metadata or {},
        )
    
    @classmethod
    def validation(
        cls,
        message: str,
        source_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "ExecutionFailure":
        """Create a validation failure."""
        import time
        return cls(
            category=ExecutionFailureCategory.VALIDATION,
            code="VALIDATION_ERROR",
            message=message,
            layer=ExecutionFailureLayer.STAGE,
            source_id=source_id,
            recoverable=True,  # Fix input and retry
            retry_safe=True,
            occurred_at_utc=time.monotonic(),
            metadata=metadata or {},
        )
    
    @classmethod
    def infrastructure(
        cls,
        message: str,
        source_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "ExecutionFailure":
        """Create an infrastructure failure."""
        import time
        return cls(
            category=ExecutionFailureCategory.INFRASTRUCTURE,
            code="INFRASTRUCTURE_ERROR",
            message=message,
            layer=ExecutionFailureLayer.CORE,
            source_id=source_id,
            recoverable=False,  # Infrastructure issue may need external fix
            retry_safe=False,
            occurred_at_utc=time.monotonic(),
            metadata=metadata or {},
        )
    
    @classmethod
    def cancellation(
        cls,
        message: str,
        source_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "ExecutionFailure":
        """Create a cancellation failure (not really an error)."""
        import time
        # Use ExecutionFailureLayer.COORDINATOR - defined before this class
        return cls(
            category=ExecutionFailureCategory.CANCELLATION,
            code="CANCELLATION",
            message=message,
            layer=ExecutionFailureLayer.COORDINATOR,
            source_id=source_id,
            recoverable=False,  # Cancellation is final
            retry_safe=True,
            occurred_at_utc=time.monotonic(),
            metadata=metadata or {},
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert failure to dictionary for serialization."""
        return {
            "failure_id": self.failure_id,
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "code": self.code,
            "message": self.message,
            "layer": self.layer.value if hasattr(self.layer, 'value') else str(self.layer),
            "source_id": self.source_id,
            "recoverable": self.recoverable,
            "retry_safe": self.retry_safe,
            "cause_reference": self.cause_reference,
            "metadata": dict(self.metadata),
            "occurred_at_utc": self.occurred_at_utc,
        }


# =============================================================================
# Execution Layer (for failure records)
# =============================================================================

class ExecutionLayer(Enum):
    """Execution layer where an operation occurs."""
    
    COORDINATOR = "coordinator"
    THREAD = "thread"
    LOOP = "loop"
    CYCLE = "cycle"
    STAGE = "stage"


# =============================================================================
# Failure Classification Helpers
# =============================================================================

def classify_failure(exception: Exception, source_id: str) -> ExecutionFailure:
    """
    Classify an exception into a structured failure record.
    
    This translates runtime exceptions into semantic failure categories.
    """
    import time
    
    # Map common exception types to failure categories
    if isinstance(exception, TimeoutError):
        return ExecutionFailure(
            category=ExecutionFailureCategory.TIMEOUT,
            code="TIMEOUT_ERROR",
            message=str(exception),
            layer=ExecutionLayer.STAGE,
            source_id=source_id,
            recoverable=False,
            retry_safe=False,
            occurred_at_utc=time.monotonic(),
        )
    
    elif isinstance(exception, (ValueError, TypeError)):
        return ExecutionFailure(
            category=ExecutionFailureCategory.VALIDATION,
            code="VALIDATION_ERROR",
            message=str(exception),
            layer=ExecutionLayer.STAGE,
            source_id=source_id,
            recoverable=True,
            retry_safe=False,
            occurred_at_utc=time.monotonic(),
        )
    
    elif isinstance(exception, RuntimeError):
        return ExecutionFailure(
            category=ExecutionFailureCategory.SEMANTIC,
            code="RUNTIME_ERROR",
            message=str(exception),
            layer=ExecutionLayer.STAGE,
            source_id=source_id,
            recoverable=True,
            retry_safe=False,
            occurred_at_utc=time.monotonic(),
        )
    
    else:
        # Generic failure
        return ExecutionFailure(
            category=ExecutionFailureCategory.INFRASTRUCTURE,
            code="UNKNOWN_ERROR",
            message=str(exception),
            layer=ExecutionLayer.STAGE,
            source_id=source_id,
            recoverable=False,
            retry_safe=False,
            occurred_at_utc=time.monotonic(),
        )


def is_retryable(failure: ExecutionFailure) -> bool:
    """Check if a failure can be retried."""
    return failure.recoverable and failure.retry_safe


# =============================================================================
# Export all public symbols
# =============================================================================

__all__ = [
    # Categories
    "ExecutionFailureCategory",
    
    # Layer
    "ExecutionFailureLayer",
    "ExecutionLayer",  # Backward compatibility
    
    # Failure record
    "ExecutionFailure",
    
    # Helpers
    "classify_failure",
    "is_retryable",
]