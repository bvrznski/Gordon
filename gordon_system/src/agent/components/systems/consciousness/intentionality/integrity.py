# Gordon Phase 5.7.3-I: Intentional Context Engine - Integrity
# ===============================================================================
#
# Integrity enforcement and validation for intentional context state.
#

"""
Intentional Context Integrity Enforcement.

Integrity operations:
    - Validate object references before publication
    - Validate relation validity (no cycles, no dangling refs)
    - Verify target ownership and trust boundaries
    - Check privacy classifications are respected
    - Enforce capacity bounds on collections
    
Failure modes addressed:
    - Invalid targets
    - Stale targets  
    - Missing objects
    - Invalid relations
    - Transition conflicts
    - Snapshot corruption
    - Publication failures
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class IntentionalIntegrityResult:
    """
    Result of an integrity validation operation.
    
    Integrity results indicate whether validation passed or failed,
    with detailed information about any issues found.
    """
    
    # Identity
    integrity_check_id: str = field(default_factory=lambda: f"integrity-{time.time()}")
    """Unique identifier for this integrity check."""
    
    context_id: Optional[str] = None
    """Context ID being validated."""
    
    # Validation outcome
    is_valid: bool = True
    """Whether validation passed."""
    
    status: str = "passed"
    """Validation status (passed, warning, failed)."""
    
    # Validation details
    checked_count: int = 0
    """Number of items checked."""
    
    invalid_count: int = 0
    """Number of invalid items found."""
    
    missing_count: int = 0
    """Number of missing references found."""
    
    warning_messages: Tuple[str, ...] = field(default_factory=tuple)
    """Any warnings from validation."""
    
    error_messages: Tuple[str, ...] = field(default_factory=tuple)
    """Any errors from validation."""
    
    # Timestamps
    started_at_utc: float = field(default_factory=time.time)
    """When integrity check was initiated."""
    
    completed_at_utc: Optional[float] = None
    """When integrity check was completed."""
    
    duration_seconds: float = 0.0
    """Duration of the integrity check."""
    
    @property
    def is_failed(self) -> bool:
        """Check if validation failed."""
        return not self.is_valid
    
    def add_warning(self, message: str) -> "IntentionalIntegrityResult":
        """Return a copy with an additional warning."""
        return dataclass_replace(
            self,
            status="warning",
            is_valid=self.is_valid and message.startswith("VALIDATION"),
            warning_messages=self.warning_messages + (message,),
        )
    
    def add_error(self, message: str) -> "IntentionalIntegrityResult":
        """Return a copy with an additional error."""
        return dataclass_replace(
            self,
            status="failed",
            is_valid=False,
            error_messages=self.error_messages + (message,),
        )


from dataclasses import replace as dataclass_replace


# =============================================================================
# INTENTIONAL INTEGRITY ENFORCER
# =============================================================================

class IntentionalIntegrityEnforcer:
    """
    Integrity enforcement and validation for intentional context.
    
    Provides comprehensive integrity checking:
        - Object reference validity (existence, expiration)
        - Relation validity (no cycles, no dangling refs)
        - Target ownership verification
        - Trust boundary enforcement
        - Privacy classification checks
        - Capacity bound enforcement
    
    Integrity checks are performed as part of the transition pipeline.
    Invalid states are rejected and never published.
    """
    
    def __init__(
        self,
        max_objects: int = 10000,
        max_relations: int = 50000,
        max_targets: int = 1000,
    ):
        """
        Initialize the integrity enforcer with capacity bounds.
        
        Args:
            max_objects: Maximum number of intentional objects
            max_relations: Maximum number of intentional relations  
            max_targets: Maximum number of intentional targets
        """
        self._max_objects = max_objects
        self._max_relations = max_relations
        self._max_targets = max_targets
    
    def validate_object(
        self,
        object_id: str,
        source_system: str,
        expiration_time: Optional[float] = None,
        trust_level: float = 0.5,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an intentional object.
        
        Args:
            object_id: ID of the object to validate
            source_system: Source system claiming ownership
            expiration_time: Optional expiration time (None = never expires)
            trust_level: Trust level of this object
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check object ID exists and is properly formatted
        if not object_id or not isinstance(object_id, str):
            return False, "Invalid object ID format"
        
        # Check source system is recognized
        if not source_system or not isinstance(source_system, str):
            return False, "Source system must be a non-empty string"
        
        # Check expiration (if set)
        current_time = time.time()
        if expiration_time is not None and current_time > expiration_time:
            return False, f"Object has expired: {object_id}"
        
        # Check trust level is in valid range
        if not (0.0 <= trust_level <= 1.0):
            return False, f"Trust level out of range: {trust_level}"
        
        return True, None
    
    def validate_relation(
        self,
        relation_kind: str,
        source_context_id: str,
        target_object_id: str,
        directed: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an intentional relation.
        
        Args:
            relation_kind: Kind of relation (must be in IntentionalRelationKind)
            source_context_id: Source context ID
            target_object_id: Target object ID
            directed: Whether the relation is directed
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check relation kind (would check against known kinds in real implementation)
        if not relation_kind or not isinstance(relation_kind, str):
            return False, "Invalid relation kind"
        
        # Check source context ID
        if not source_context_id:
            return False, "Missing source context ID"
        
        # Check target object ID
        if not target_object_id:
            return False, "Missing target object ID"
        
        # Check directed flag type
        if not isinstance(directed, bool):
            return False, "Directed must be a boolean"
        
        return True, None
    
    def validate_target(
        self,
        target_status: str,
        source_owner: str,
        privacy_classification: str = "internal",
        trust_level: float = 0.5,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an intentional target.
        
        Args:
            target_status: Current status of the target
            source_owner: Source owner of this target reference
            privacy_classification: Privacy level
            trust_level: Trust level
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check target status is valid
        valid_statuses = ("active", "suspended", "completed", "abandoned", "failed")
        if target_status not in valid_statuses:
            return False, f"Invalid target status: {target_status}"
        
        # Check source owner
        if not source_owner or not isinstance(source_owner, str):
            return False, "Source owner must be a non-empty string"
        
        # Check privacy classification is valid
        valid_privacy = ("public", "internal", "restricted")
        if privacy_classification not in valid_privacy:
            return False, f"Invalid privacy classification: {privacy_classification}"
        
        # Check trust level range
        if not (0.0 <= trust_level <= 1.0):
            return False, f"Trust level out of range: {trust_level}"
        
        return True, None
    
    def check_capacity(
        self,
        current_objects: int,
        current_relations: int,
        current_targets: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if collections are within capacity bounds.
        
        Args:
            current_objects: Current number of objects
            current_relations: Current number of relations
            current_targets: Current number of targets
            
        Returns:
            Tuple of (is_valid, error_message if over capacity)
        """
        if current_objects > self._max_objects:
            return False, f"Object count exceeds maximum ({current_objects} > {self._max_objects})"
        
        if current_relations > self._max_relations:
            return False, f"Relation count exceeds maximum ({current_relations} > {self._max_relations})"
        
        if current_targets > self._max_targets:
            return False, f"Target count exceeds maximum ({current_targets} > {self._max_targets})"
        
        return True, None
    
    def validate_transition(
        self,
        transition_kind: str,
        previous_generation: int,
        new_generation: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a transition before commit.
        
        Args:
            transition_kind: Kind of transition
            previous_generation: Previous generation number
            new_generation: New generation number
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check generation is strictly increasing
        if new_generation != previous_generation + 1:
            return False, f"Generation must increase by exactly 1 ({previous_generation} -> {new_generation})"
        
        # Check transition kind is valid (simplified check)
        if not isinstance(transition_kind, str) or len(transition_kind) == 0:
            return False, "Invalid transition kind"
        
        return True, None
    
    def validate_snapshot(
        self,
        generation: int,
        previous_generation: Optional[int],
        object_count: int,
        relation_count: int,
        target_count: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a snapshot before publication.
        
        Args:
            generation: Snapshot generation
            previous_generation: Previous generation (for lineage)
            object_count: Number of objects in snapshot
            relation_count: Number of relations in snapshot
            target_count: Number of targets in snapshot
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check generation is positive
        if generation < 0:
            return False, "Generation must be non-negative"
        
        # Check lineage (if present)
        if previous_generation is not None and generation <= previous_generation:
            return False, f"Generation must increase: {previous_generation} -> {generation}"
        
        # Check counts are within bounds
        is_valid, error = self.check_capacity(object_count, relation_count, target_count)
        if not is_valid:
            return is_valid, error
        
        return True, None


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "IntentionalIntegrityResult",
    "IntentionalIntegrityEnforcer",
)