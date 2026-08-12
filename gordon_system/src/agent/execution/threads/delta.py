# Thread Semantic Delta Model
# ============================

"""
Thread semantic delta application model.

Deltas represent changes to thread state. The canonical flow is:

    Cycle produces outcome
            ↓
    Outcome contains proposed semantic delta
            ↓
    Loop interprets outcome
            ↓
    Thread validates and accepts or rejects delta
            ↓
    Thread advances semantic version

A delta should specify:
    - Source Cycle (which cycle produced this delta)
    - Expected Thread version (for validation)
    - Proposed changes (what state changes)
    - Provenance (how the change was derived)
    - Validation result
    - Acceptance status
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class DeltaValidationResult(Enum):
    """
    Result of delta validation.
    
    When a Thread receives a proposed semantic delta from a Cycle/Loop:
        VALID: Delta is acceptable and can be applied
        STALE_VERSION: Expected version doesn't match current version
        INVALID_CONTENT: Content violates thread constraints or invariants
        UNAUTHORIZED: Source cycle/loop not authorized to make this change
        PENDING_VALIDATION: Cannot validate yet (e.g., awaiting external input)
    """
    
    VALID = "valid"
    STALE_VERSION = "stale_version"
    INVALID_CONTENT = "invalid_content"
    UNAUTHORIZED = "unauthorized"
    PENDING_VALIDATION = "pending_validation"


@dataclass(frozen=True)
class ThreadSemanticDelta:
    """
    An immutable semantic delta to apply to thread state.
    
    A delta is a minimal, self-contained description of a state change that
    the Thread can validate and accept or reject.
    """
    
    # Source information
    source_cycle_id: str  # Which Cycle produced this delta?
    loop_id: Optional[str] = None  # Which Loop interpreted it?
    
    # Version tracking (for stale delta detection)
    expected_thread_version: int = 0  # What version should the thread be at? (0 means any)
    
    # Proposed changes (one or more)
    change_type: str = ""  # e.g., "objective_added", "state_transition", "fact_accepted"
    changes: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: str = "cycle_outcome"  # How this delta was derived
    
    # Validation metadata (set by Thread when processing)
    validation_result: Optional[DeltaValidationResult] = None
    rejection_reason: Optional[str] = None
    accepted_version: Optional[int] = None
    
    def is_stale(self, current_version: int) -> bool:
        """Check if this delta's expected version doesn't match current state."""
        return self.expected_thread_version != current_version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert delta to dictionary for serialization."""
        return {
            "source_cycle_id": self.source_cycle_id,
            "loop_id": self.loop_id,
            "expected_thread_version": self.expected_thread_version,
            "change_type": self.change_type,
            "changes": dict(self.changes),
            "provenance": self.provenance,
            "validation_result": self.validation_result.value if self.validation_result else None,
            "rejection_reason": self.rejection_reason,
        }


@dataclass(frozen=True)
class ThreadDeltaBatch:
    """
    A batch of semantic deltas to apply atomically.
    
    All deltas in a batch must be for the same thread and have consistent
    version expectations. The thread will either accept all or reject all.
    """
    
    thread_id: str
    deltas: Tuple[ThreadSemanticDelta, ...]
    batch_version: int = 0  # Batch sequence number
    
    def expected_version(self) -> Optional[int]:
        """Get the expected version from the first delta (if any)."""
        if self.deltas:
            return self.deltas[0].expected_thread_version
        return None


@dataclass(frozen=True)
class DeltaApplicationResult:
    """
    Result of applying a semantic delta to thread state.
    
    Contains both the success/failure status and the updated state information.
    """
    
    # Application outcome
    applied: bool
    new_semantic_version: int
    
    # Changes that were actually applied (may differ from requested)
    applied_changes: Dict[str, Any]
    
    # Validation details
    validation_result: DeltaValidationResult = DeltaValidationResult.VALID
    rejection_reason: Optional[str] = None
    
    # Associated artifacts
    associated_cycle_id: Optional[str] = None
    timestamp_utc: float = field(default_factory=lambda: 0.0)
    
    @classmethod
    def success(
        cls,
        new_version: int,
        applied_changes: Dict[str, Any],
        **kwargs,
    ) -> "DeltaApplicationResult":
        """Create a successful application result."""
        return cls(
            applied=True,
            new_semantic_version=new_version,
            applied_changes=applied_changes,
            timestamp_utc=0.0,
            **kwargs,
        )
    
    @classmethod
    def rejected(
        cls,
        reason: str,
        validation_result: DeltaValidationResult = DeltaValidationResult.INVALID_CONTENT,
        **kwargs,
    ) -> "DeltaApplicationResult":
        """Create a rejection result."""
        return cls(
            applied=False,
            new_semantic_version=0,  # No version change
            applied_changes={},
            validation_result=validation_result,
            rejection_reason=reason,
            timestamp_utc=0.0,
            **kwargs,
        )


@dataclass(frozen=True)
class ThreadDeltaValidator:
    """
    Validator for semantic deltas before application.
    
    The validator enforces thread invariants and ensures that only valid
    changes are applied to the thread's semantic state.
    """
    
    # Current thread state (for version checking)
    current_version: int
    
    def validate_delta(self, delta: ThreadSemanticDelta) -> DeltaValidationResult:
        """
        Validate a single delta against current state.
        
        Returns:
            VALID if delta is acceptable
            STALE_VERSION if expected version doesn't match
            INVALID_CONTENT if content violates invariants
        """
        # Check version (T-006: stale semantic delta cannot be silently applied)
        if delta.is_stale(self.current_version):
            return DeltaValidationResult.STALE_VERSION
        
        # Validate change type is recognized
        valid_change_types = {
            "objective_added",
            "objective_completed",
            "objective_abandoned",
            "state_transition",
            "fact_accepted",
            "context_updated",
            "mode_changed",
        }
        
        if delta.change_type not in valid_change_types:
            return DeltaValidationResult.INVALID_CONTENT
        
        # Check for required fields based on change type
        if delta.change_type.startswith("objective_"):
            if "objective_id" not in delta.changes:
                return DeltaValidationResult.INVALID_CONTENT
        
        # All checks passed
        return DeltaValidationResult.VALID
    
    def validate_batch(self, batch: ThreadDeltaBatch) -> Tuple[bool, Optional[str]]:
        """
        Validate an entire batch of deltas.
        
        Returns (is_valid, error_message).
        """
        if not batch.deltas:
            return True, None
        
        # Check version consistency across batch
        expected_version = batch.expected_version()
        if expected_version is not None and expected_version != self.current_version:
            return False, f"Expected thread version {expected_version}, got {self.current_version}"
        
        # Validate each delta
        for i, delta in enumerate(batch.deltas):
            result = self.validate_delta(delta)
            if result != DeltaValidationResult.VALID:
                return False, f"Delta {i} validation failed: {result.value}"
        
        return True, None
    
    def apply_delta(
        self,
        delta: ThreadSemanticDelta,
        current_state_version: int,
    ) -> Tuple[bool, int, Optional[str]]:
        """
        Attempt to apply a validated delta.
        
        Returns (success, new_version, error_message).
        """
        # Double-check validation
        validation = self.validate_delta(delta)
        if validation != DeltaValidationResult.VALID:
            return False, current_state_version, f"Invalid delta: {validation.value}"
        
        # In a real implementation, this would actually modify state
        # For now, just increment version (delta represents the change)
        new_version = current_state_version + 1
        
        return True, new_version, None


__all__ = [
    "DeltaValidationResult",
    "ThreadSemanticDelta",
    "ThreadDeltaBatch",
    "DeltaApplicationResult",
    "ThreadDeltaValidator",
]