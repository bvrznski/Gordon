# Execution Checkpoint Types
# ==========================
#
# PHASE 3.10.14 - Resumability and Serialization Enhancements

"""
Checkpoint types for Cycle resumability.

A checkpoint provides serialization-ready state that can be used to resume
a partially completed Cycle. It is NOT:
    - A durable persistence mechanism (Core handles storage)
    - A complete Thread snapshot (only contains Cycle-local data)
    - A backup of runtime execution state

A checkpoint IS:
    - Immutable, serializable state at a safe interruption point
    - Contains enough information to revalidate and resume execution
    - Validation-aware (can detect stale or incompatible checkpoints)
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# Cycle Checkpoint (resumable Cycle state)
# =============================================================================

@dataclass(frozen=True, slots=True)
class CycleCheckpoint:
    """
    Immutable checkpoint of a partially completed Cycle.
    
    Purpose: Allow safe interruption and resumption of bounded semantic work.
    
    Contents:
        - Cycle identity and ownership
        - Selecting Loop reference  
        - Source Thread revision (for validation)
        - Completed Stage identifiers
        - Current Stage index
        - Accepted Stage results
        - Local immutable working state
        - Artifacts produced so far
        - Provenance metadata
    
    Not included:
        - Live coroutines or async handles
        - Open file descriptors
        - Mutable service instances
        - Callable closures (lambda functions, etc.)
    
    Resumption rules:
        - Thread identity must match
        - Cycle identity must match  
        - Expected Thread revision must match current state
        - Stage sequence must be compatible
        - Cannot re-run completed Stages unless explicitly idempotent
        
    Validation is performed at resumption time, not checkpoint creation.
    """
    
    # Identity (required)
    cycle_id: str
    thread_id: str
    selecting_loop_id: str
    
    # Source information
    snapshot_revision: int  # Thread revision when checkpoint created
    cycle_type: str  # e.g., "interpretation", "response"
    
    # Completed work tracking
    completed_stage_ids: Tuple[str, ...] = field(default_factory=tuple)
    next_stage_index: int = 0
    
    # Local state (immutable working data)
    local_state: Dict[str, Any] = field(default_factory=dict)
    
    # Artifacts produced so far
    artifact_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    created_at_utc: float = field(default_factory=lambda: 0.0)
    checkpoint_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    
    def is_complete(self) -> bool:
        """Check if the cycle has completed all stages."""
        return self.next_stage_index >= len(self.completed_stage_ids)
    
    def can_resume(self, current_thread_revision: int) -> Tuple[bool, Optional[str]]:
        """
        Check if this checkpoint can be used to resume given current state.
        
        Returns (can_resume, reason_if_not).
        """
        if current_thread_revision != self.snapshot_revision:
            return False, (
                f"Thread revision mismatch: expected {self.snapshot_revision}, "
                f"current {current_thread_revision}"
            )
        return True, None
    
    def to_resumption_descriptor(self) -> "CycleResumptionDescriptor":
        """Create a descriptor for resuming this cycle."""
        return CycleResumptionDescriptor(
            checkpoint_id=self.checkpoint_id,
            thread_id=self.thread_id,
            cycle_type=self.cycle_type,
            next_stage_index=self.next_stage_index,
            local_state=dict(self.local_state),
        )


@dataclass(frozen=True, slots=True)
class CycleResumptionDescriptor:
    """
    Minimal information needed to resume a Cycle from checkpoint.
    
    This is what Core's resumption system uses. It excludes any transient
    runtime data that will be reconstructed.
    """
    
    checkpoint_id: str
    thread_id: str
    cycle_type: str
    
    # Where to resume
    next_stage_index: int = 0
    
    # Local state needed for continuation
    local_state: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def empty(cls, thread_id: str, cycle_type: str) -> "CycleResumptionDescriptor":
        """Create an empty resumption descriptor for a new cycle."""
        return cls(
            checkpoint_id="",
            thread_id=thread_id,
            cycle_type=cycle_type,
        )


# =============================================================================
# Checkpoint Validation Result
# =============================================================================

class CheckpointValidationResult(Enum):
    """
    Result of validating a CycleCheckpoint.
    
    Validations performed:
        - Schema version matches
        - Thread identity is valid
        - Expected revision matches current state (if applicable)
        - Stage sequence compatibility
        - No circular references
    """
    
    VALID = "valid"
    STALE_VERSION = "stale_version"
    INVALID_THREAD = "invalid_thread"
    INCOMPATIBLE_CYCLE_TYPE = "incompatible_cycle_type"
    STAGE_SEQUENCE_MISMATCH = "stage_sequence_mismatch"
    SCHEMA_VERSION_UNSUPPORTED = "schema_version_unsupported"
    SERIALIZATION_ERROR = "serialization_error"


@dataclass(frozen=True, slots=True)
class CheckpointValidation:
    """Result of validating a checkpoint."""
    
    is_valid: bool
    result_code: str  # One of CheckpointValidationResult values
    message: str = ""
    details: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# Serialization Helpers (to_dict/from_dict for key types)
# =============================================================================

def thread_snapshot_to_dict(snapshot: "ThreadSnapshot") -> Dict[str, Any]:
    """
    Convert ThreadSnapshot to serializable dictionary.
    
    Note: This requires import from snapshot module to avoid circular imports.
          The actual implementation will be in the snapshot module itself.
    """
    # Import locally to avoid circular dependency
    from agent.execution.threads.snapshot import ThreadSnapshot
    if not isinstance(snapshot, ThreadSnapshot):
        raise TypeError(f"Expected ThreadSnapshot, got {type(snapshot)}")
    
    return {
        "snapshot_id": snapshot.snapshot_id,
        "thread_id": snapshot.thread_id,
        "semantic_version": snapshot.semantic_version,
        "captured_at_utc": snapshot.captured_at_utc,
        "name": snapshot.name,
        "purpose": snapshot.purpose,
        "kind": snapshot.kind,
        "context_data": dict(snapshot.context_data),
        "previous_snapshot_ids": list(snapshot.previous_snapshot_ids),
        "checkpoint_id": snapshot.checkpoint_id,
        "parent_thread_id": snapshot.parent_thread_id,
        "child_thread_ids": list(snapshot.child_thread_ids),
    }


def thread_delta_to_dict(delta: "ThreadSemanticDelta") -> Dict[str, Any]:
    """
    Convert ThreadSemanticDelta to serializable dictionary.
    
    Note: This requires import from delta module.
    """
    # Import locally to avoid circular dependency
    from agent.execution.threads.delta import ThreadSemanticDelta
    if not isinstance(delta, ThreadSemanticDelta):
        raise TypeError(f"Expected ThreadSemanticDelta, got {type(delta)}")
    
    return {
        "source_cycle_id": delta.source_cycle_id,
        "loop_id": delta.loop_id,
        "expected_thread_version": delta.expected_thread_version,
        "change_type": delta.change_type,
        "changes": dict(delta.changes),
        "provenance": delta.provenance,
        "validation_result": delta.validation_result.value if delta.validation_result else None,
        "rejection_reason": delta.rejection_reason,
    }


def loop_decision_to_dict(decision: "LoopDecision") -> Dict[str, Any]:
    """
    Convert LoopDecision to serializable dictionary.
    
    Note: This requires import from coordinator module.
    """
    # Import locally to avoid circular dependency
    from agent.execution.coordinator import LoopDecision
    if not isinstance(decision, LoopDecision):
        raise TypeError(f"Expected LoopDecision, got {type(decision)}")
    
    return {
        "decision_kind": decision.decision_kind,
        "thread_id": decision.thread_id,
        "thread_revision": decision.thread_revision,
        "rationale": decision.rationale,
        "cycle_definition": None,  # Avoid serializing complex objects
        "target_loop_definition": None,
        "condition": None,
        "child_thread_id": decision.child_thread_id,
    }


def cycle_outcome_to_dict(outcome: "CycleOutcome") -> Dict[str, Any]:
    """
    Convert CycleOutcome to serializable dictionary.
    
    Note: This requires import from cycles module.
    """
    # Import locally to avoid circular dependency
    from agent.execution.cycles import CycleOutcome as CyclesCycleOutcome
    if not isinstance(outcome, CyclesCycleOutcome):
        raise TypeError(f"Expected CycleOutcome, got {type(outcome)}")
    
    return {
        "cycle_id": outcome.cycle_id,
        "thread_id": outcome.thread_id,
        "status": outcome.status.value if hasattr(outcome.status, 'value') else str(outcome.status),
        "source_thread_revision": outcome.source_thread_revision,
        "loop_decision_id": outcome.loop_decision_id,
        "semantic_delta": None,  # Avoid serializing complex objects
        "completion_reason": outcome.completion_reason,
        "stage_results": [],  # Stage results typically don't serialize well
        "stages_completed": outcome.stages_completed,
    }


# =============================================================================
# Export all public symbols
# =============================================================================

__all__ = [
    "CycleCheckpoint",
    "CycleResumptionDescriptor",
    "CheckpointValidationResult",
    "CheckpointValidation",
    "thread_snapshot_to_dict",
    "thread_delta_to_dict",
    "loop_decision_to_dict",
    "cycle_outcome_to_dict",
]