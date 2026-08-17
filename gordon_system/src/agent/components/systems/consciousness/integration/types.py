# Gordon Phase 5.7.8-I: Conscious Integration - Types
# ===============================================================================

"""
Canonical data structures for the integration layer.

This module defines immutable, typed contracts that define the interface
for composite context snapshots and transition records.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Dict, Optional


# =============================================================================
# ENGINE SNAPSHOT REFERENCE
# =============================================================================

@dataclass(frozen=True)
class EngineSnapshotReference:
    """
    Immutable reference to a committed engine snapshot.
    
    This is the contract used by the integration layer to collect references
    from individual engines without requiring full payload access.
    """

    engine_id: str
    """The engine identity that produced this reference."""

    context_id: str
    """Context ID for lineage tracking."""

    generation: int = 0
    """Generation number of the engine snapshot."""

    timestamp_utc: float = field(default_factory=time.time)
    """Timestamp when this reference was created."""

    transition_id: Optional[str] = None
    """Transition that produced this snapshot (if any)."""

    @classmethod
    def from_engine(
        cls,
        engine_id: str,
        context_id: str,
        generation: int,
        timestamp_utc: Optional[float] = None,
        transition_id: Optional[str] = None,
    ) -> EngineSnapshotReference:
        """
        Create a reference from engine state.

        Args:
            engine_id: Engine identity
            context_id: Context ID
            generation: Generation number
            timestamp_utc: Creation timestamp (optional)
            transition_id: Transition ID (optional)
        """
        return cls(
            engine_id=engine_id,
            context_id=context_id,
            generation=generation,
            timestamp_utc=timestamp_utc if timestamp_utc is not None else time.time(),
            transition_id=transition_id,
        )


# =============================================================================
# ENGINE GENERATION MAP
# =============================================================================

@dataclass(frozen=True)
class EngineGenerationMap:
    """
    Immutable mapping of engine IDs to their committed generations.
    
    This captures the exact generation state of all engines at a point in time.
    """

    engine_ids: Tuple[str, ...]
    """All engine IDs in this map."""

    generation_map: Dict[str, int] = field(default_factory=dict)
    """Engine ID -> generation mapping."""

    def get(self, engine_id: str) -> Optional[int]:
        """Get generation for an engine ID."""
        return self.generation_map.get(engine_id)

    def with_generation(self, engine_id: str, generation: int) -> EngineGenerationMap:
        """Return a copy with updated generation for an engine."""
        new_map = dict(self.generation_map)
        new_map[engine_id] = generation
        return dataclass_replace(
            self,
            engine_ids=tuple(sorted(set(self.engine_ids + (engine_id,)))),
            generation_map=new_map,
        )

    @classmethod
    def from_refs(cls, refs: Tuple[EngineSnapshotReference, ...]) -> EngineGenerationMap:
        """Create a map from snapshot references."""
        generations = {ref.engine_id: ref.generation for ref in refs}
        engine_ids = tuple(ref.engine_id for ref in refs)
        return cls(engine_ids=engine_ids, generation_map=generations)


# =============================================================================
# UNRESOLVED REFERENCE
# =============================================================================

@dataclass(frozen=True)
class UnresolvedReference:
    """
    Explicit unresolved reference with classification.
    
    Used when an engine references another entity that cannot be resolved
    within the current context boundaries.
    """

    referencing_engine_id: str
    """Engine that holds this reference."""

    referenced_entity_type: str
    """Type of the referenced entity (e.g., 'intentional_target', 'world_entity')."""

    reference_value: str
    """The raw reference value."""

    resolution_status: str = "unresolved"
    """
    Status classification:
        - unresolved: Cannot resolve currently
        - remembered: Referenced from memory/past context
        - hypothetical: Theoretical, not yet observed
        - external: Outside current capability scope
    """

    confidence: float = 0.0
    """Confidence that this reference is valid."""

    @property
    def is_critical(self) -> bool:
        """Check if this unresolved reference is critical to context validity."""
        return self.resolution_status == "unresolved"


# =============================================================================
# COMPOSITE SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class CompositeSnapshot:
    """
    Immutable composite snapshot of the current conscious context.

    This is the canonical publication - a bounded, deterministic aggregation
    of committed engine references at a point in time.
    """

    # Identity and revisioning (required fields first)
    context_id: str = field(default_factory=lambda: f"context-{uuid.uuid4().hex[:8]}")
    """Unique identifier for this logical context."""

    generation: int = 0
    """Current composite generation (strictly monotonic)."""

    previous_generation: int = 0
    """Previous generation number (for lineage tracking)."""

    schema_version: str = "5.7.8"
    """Schema version for compatibility tracking."""

    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    """When this snapshot was created."""

    transition_id: Optional[str] = None
    """Transition that produced this snapshot (if any)."""

    # Engine references (by identity, not full content)
    experiential_field_ref: Optional[EngineSnapshotReference] = None
    intentional_context_ref: Optional[EngineSnapshotReference] = None
    temporal_context_ref: Optional[EngineSnapshotReference] = None
    presence_ref: Optional[EngineSnapshotReference] = None
    awareness_ref: Optional[EngineSnapshotReference] = None
    perspective_ref: Optional[EngineSnapshotReference] = None
    situated_world_ref: Optional[EngineSnapshotReference] = None

    # Engine generation map (for alignment tracking)
    engine_generation_map: EngineGenerationMap = field(
        default_factory=EngineGenerationMap
    )

    # Summary information (bounded, computed from references)
    source_summary: Dict[str, str] = field(default_factory=dict)
    """Summary of registered sources."""

    privacy_summary: str = "internal"
    """Overall privacy classification of this context."""

    trust_summary: str = "medium"
    """Overall trust classification of this context."""

    degradation_modes: Tuple[str, ...] = field(default_factory=tuple)
    """Current degradation modes (if any)."""

    consistency_level: str = "strict"
    """Consistency level for this snapshot."""

    # Validation status
    cross_engine_validation_passed: bool = True
    """Whether all cross-engine invariants passed validation."""

    unresolved_references: Tuple[UnresolvedReference, ...] = field(default_factory=tuple)
    """Explicit unresolved references."""

    provenance: Optional[str] = None
    """Provenance information for this snapshot."""

    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""

    causation_id: Optional[str] = None
    """Causation ID for tracking chain."""

    @classmethod
    def initial(cls, context_id: str) -> "CompositeSnapshot":
        """
        Create an initial empty composite snapshot.

        Args:
            context_id: Initial context ID

        Returns:
            Initial composite snapshot with zero generations
        """
        return cls(
            context_id=context_id,
            generation=0,
            previous_generation=0,
            created_at_utc=time.time(),
            consistency_level="strict",
        )

    @property
    def is_empty(self) -> bool:
        """Check if this snapshot has no engine references."""
        refs = [
            self.experiential_field_ref,
            self.intentional_context_ref,
            self.temporal_context_ref,
            self.presence_ref,
            self.awareness_ref,
            self.perspective_ref,
            self.situated_world_ref,
        ]
        return all(ref is None for ref in refs)

    @property
    def is_valid(self) -> bool:
        """Check if this snapshot has passed validation."""
        return (
            self.cross_engine_validation_passed
            and not self.has_missing_required_engines
        )

    @property
    def has_missing_required_engines(self) -> bool:
        """Check if any required engines are missing."""
        required = ["experiential_field", "presence", "perspective"]
        for engine_id in required:
            ref = getattr(self, f"{engine_id}_ref")
            if ref is None:
                return True
        return False

    def with_generation(self, new_generation: int) -> "CompositeSnapshot":
        """Return a copy with the specified generation."""
        return dataclass_replace(
            self,
            generation=new_generation,
            previous_generation=self.generation,
        )

    def with_transitions(
        self,
        experiential_field_ref: Optional[EngineSnapshotReference] = None,
        intentional_context_ref: Optional[EngineSnapshotReference] = None,
        temporal_context_ref: Optional[EngineSnapshotReference] = None,
        presence_ref: Optional[EngineSnapshotReference] = None,
        awareness_ref: Optional[EngineSnapshotReference] = None,
        perspective_ref: Optional[EngineSnapshotReference] = None,
        situated_world_ref: Optional[EngineSnapshotReference] = None,
    ) -> "CompositeSnapshot":
        """Return a copy with updated engine references."""
        return dataclass_replace(
            self,
            experiential_field_ref=experiential_field_ref,
            intentional_context_ref=intentional_context_ref,
            temporal_context_ref=temporal_context_ref,
            presence_ref=presence_ref,
            awareness_ref=awareness_ref,
            perspective_ref=perspective_ref,
            situated_world_ref=situated_world_ref,
        )

    def with_engine_generations(
        self, engine_generation_map: EngineGenerationMap
    ) -> "CompositeSnapshot":
        """Return a copy with updated engine generation map."""
        return dataclass_replace(self, engine_generation_map=engine_generation_map)

    def with_degradation(self, *modes: str) -> "CompositeSnapshot":
        """Return a copy with degradation modes."""
        return dataclass_replace(
            self,
            degradation_modes=tuple(sorted(set(self.degradation_modes + modes))),
        )

    def with_validation_passed(self, passed: bool) -> "CompositeSnapshot":
        """Return a copy with updated validation status."""
        return dataclass_replace(self, cross_engine_validation_passed=passed)

    def with_unresolved_refs(
        self, *refs: UnresolvedReference
    ) -> "CompositeSnapshot":
        """Return a copy with unresolved references."""
        return dataclass_replace(
            self,
            unresolved_references=tuple(set(self.unresolved_references + refs)),
        )


# =============================================================================
# INTEGRATION TRANSITION
# =============================================================================

@dataclass(frozen=True)
class IntegrationTransition:
    """
    Immutable record of an integration transition commit.

    This records the atomic commitment of a new composite generation.
    """

    # Identity (required fields first)
    context_id: str
    """Context ID being transitioned."""

    previous_generation: int
    """Generation before this transition."""

    new_generation: int
    """New generation after this transition."""

    transition_id: str = field(default_factory=lambda: f"transition-{uuid.uuid4().hex[:8]}")
    """Unique identifier for this transition."""

    # Timing
    started_at_utc: float = field(default_factory=time.time)
    """When transition was initiated."""

    committed_at_utc: float = field(default_factory=time.time)
    """When transition was committed."""

    # Trigger and metadata
    trigger: str = "internal"
    """What triggered this transition."""

    requested_engine_updates: Tuple[str, ...] = field(default_factory=tuple)
    """Engine IDs that were requested to update."""

    committed_engine_transitions: Dict[str, int] = field(default_factory=dict)
    """Engine ID -> new generation for engines that committed."""

    unchanged_engine_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Engines that remained at the same generation."""

    rejected_engine_results: Tuple[str, ...] = field(default_factory=tuple)
    """Engine IDs whose results were rejected."""

    # Validation
    generation_alignment_passed: bool = True
    """Whether generation alignment validation passed."""

    cross_engine_validation_passed: bool = True
    """Whether cross-engine invariant validation passed."""

    unresolved_reference_count: int = 0
    """Number of unresolved references in final composite."""

    # Degradation and classification
    degradation_modes: Tuple[str, ...] = field(default_factory=tuple)
    """Degradation modes introduced or changed."""

    privacy_summary: str = "internal"
    """Privacy classification of new context."""

    trust_summary: str = "medium"
    """Trust classification of new context."""

    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Any warnings during validation."""

    provenance: Optional[str] = None
    """Provenance information for this transition."""

    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""

    causation_id: Optional[str] = None
    """Causation ID for tracking chain."""

    status: str = "completed"
    """
    Transition status:
        - completed: Fully committed
        - rolled_back: Rolled back due to failure
        - partial: Partial success with degraded modes
    """

    @classmethod
    def initial(cls, context_id: str) -> "IntegrationTransition":
        """Create an initial transition for the first generation."""
        return cls(
            context_id=context_id,
            previous_generation=0,
            new_generation=1,
            started_at_utc=time.time(),
            committed_at_utc=time.time(),
            status="completed",
        )


# =============================================================================
# INTEGRATION RESULT
# =============================================================================

@dataclass(frozen=True)
class IntegrationResult:
    """
    Result of an integration operation.

    Represents the outcome of attempting to commit a new composite generation.
    """

    # Identity
    transition_id: str

    # Outcome
    succeeded: bool = False
    """Whether the integration succeeded."""

    status: str = "pending"
    """Final status of the integration."""

    # New state (if successful)
    new_composite_snapshot: Optional[CompositeSnapshot] = None
    """New composite snapshot (if committed)."""

    new_generation: int = 0
    """New generation number (if successful)."""

    # Partial outcomes
    partial_success: bool = False
    """Whether this was a partial success."""

    skipped_engines: Tuple[str, ...] = field(default_factory=tuple)
    """Engines that were skipped (optional)."""

    rejected_engine_snapshots: Dict[str, str] = field(default_factory=dict)
    """Engine ID -> reason for rejection."""

    # Failure information
    failure_reason: Optional[str] = None
    """Reason for failure (if failed)."""

    @property
    def is_failed(self) -> bool:
        """Check if this result represents a failure."""
        return not self.succeeded

    @property
    def is_degraded(self) -> bool:
        """Check if this result represents degraded operation."""
        return self.partial_success


# =============================================================================
# PARTIAL OUTCOME
# =============================================================================

@dataclass(frozen=True)
class PartialOutcome:
    """
    Record of a partial integration outcome.

    Used when some engines succeed while others fail, allowing bounded
    degradation instead of complete failure.
    """

    successful_engines: Tuple[str, ...] = field(default_factory=tuple)
    """Engines that successfully committed."""

    failed_engines: Dict[str, str] = field(default_factory=dict)
    """Engine ID -> error message for failures."""

    rejected_engines: Dict[str, str] = field(default_factory=dict)
    """Engine ID -> rejection reason (validation failure)."""

    preserved_previous_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Engines that retained their previous references."""

    new_references: Dict[str, EngineSnapshotReference] = field(default_factory=dict)
    """New engine references introduced."""

    @property
    def has_failures(self) -> bool:
        """Check if any engines failed."""
        return len(self.failed_engines) > 0

    @property
    def is_full_success(self) -> bool:
        """Check if all requested engines succeeded."""
        return len(self.failed_engines) == 0 and len(self.rejected_engines) == 0


# =============================================================================
# DEGRADATION MODE
# =============================================================================

@dataclass(frozen=True)
class DegradationMode:
    """
    Explicit degradation state with metadata.
    """

    mode: str
    """Degradation mode identifier."""

    severity: str = "warning"
    """
    Severity level:
        - info: Informational only
        - warning: May affect some consumers
        - critical: Major impact on context validity
    """

    affected_consumers: Tuple[str, ...] = field(default_factory=tuple)
    """Consumer IDs that may be affected."""

    recovery_path: Optional[str] = None
    """Description of how to recover from this degradation."""

    max_duration_seconds: float = 0.0
    """Maximum allowed duration (0 = no limit)."""

    description: str = ""
    """Human-readable description."""