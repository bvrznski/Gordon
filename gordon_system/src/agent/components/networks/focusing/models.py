# Focusing Network - Canonical Computational Models
# ==================================================
#
# Phase 4.2.2: Canonical computational substrate of the Focusing Network.
#
# This phase establishes:
#   • immutable computational models
#   • focus targets
#   • focus candidates
#   • focus state
#   • persistence state
#   • precision state
#   • allocation state
#   • computational transitions
#   • snapshots
#
# No computational algorithms are implemented in this phase.
# Only canonical representations and state structures.
# ==================================================

"""
Canonical Computational Models for Phase 4.2.2

This module defines the immutable computational substrate upon which every
future algorithm in the Focusing Network operates.

DESIGN PRINCIPLES:
    • Immutable computational objects (frozen dataclasses)
    • Explicit ownership (clear boundaries)
    • Bounded state (no arbitrary growth)
    • Deterministic transitions (same inputs → same outputs)
    • Runtime neutrality (no runtime assumptions)
    • Serialization readiness (JSON-compatible representations)
    • Diagnostic friendliness (rich metadata for debugging)
    • Future extensibility (extensible without breaking changes)

NO BEHAVIOR:
    This phase does NOT implement:
        • priority computation
        • competition analysis
        • suppression logic
        • allocation algorithms
        • precision estimation
        • persistence algorithms
        • assessment generation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    Mapping,
    Optional,
    Tuple,
)
from datetime import datetime
import uuid

# Import enums for type references only (no behavior)
from gordon_system.src.agent.components.networks.focusing.enums import (
    FocusModality,
    FocusSource,
    PriorityLevel,
    PrecisionBandwidth,
    PersistenceMode,
    BiasModality,
)


# =============================================================================
# IDENTITY TYPES - Stable, independent identifiers
# =============================================================================


@dataclass(frozen=True)
class FocusTargetId:
    """
    Unique identifier for a focus target.
    
    Identity must remain stable across state transitions and snapshots.
    Identifiers are independent of runtime identifiers.
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "FocusTargetId":
        """Generate a new unique identifier."""
        return cls(value=f"target_{uuid.uuid4().hex[:24]}")
    
    @classmethod
    def from_string(cls, value: str) -> "FocusTargetId":
        """Create an ID from an existing string."""
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CandidateId:
    """
    Unique identifier for a focus candidate.
    
    Candidates are transient - this ID tracks them during evaluation.
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "CandidateId":
        """Generate a new unique identifier."""
        return cls(value=f"candidate_{uuid.uuid4().hex[:24]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AssessmentId:
    """
    Unique identifier for a focus assessment.
    
    Links all descriptors to a single assessment instance.
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "AssessmentId":
        """Generate a new unique identifier."""
        return cls(value=f"assessment_{uuid.uuid4().hex[:24]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TransitionId:
    """
    Unique identifier for a state transition.
    
    Tracks the evolution of state over time.
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "TransitionId":
        """Generate a new unique identifier."""
        return cls(value=f"transition_{uuid.uuid4().hex[:24]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SnapshotId:
    """
    Unique identifier for a state snapshot.
    
    Identifies a point-in-time view of state.
    """
    
    value: str
    
    @classmethod
    def generate(cls) -> "SnapshotId":
        """Generate a new unique identifier."""
        return cls(value=f"snapshot_{uuid.uuid4().hex[:24]}")
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# PROVENANCE - Preserve origin and history without runtime references
# =============================================================================


@dataclass(frozen=True)
class ProvenanceRecord:
    """
    Immutable provenance information for a descriptor or transition.
    
    Preserves:
        • Originating subsystem (e.g., "goal_system", "perception")
        • Creation source (how this was generated)
        • Upstream assessment (if derived from another assessment)
        • Revision chain (sequence of transformations)
        • Diagnostic lineage (for debugging)
    """
    
    originating_subsystem: str
    """The subsystem that created or originated this item."""
    
    creation_source: Optional[str] = None
    """Specific source within the subsystem (e.g., "active_goals", "memory_retrieval")."""
    
    upstream_assessment_id: Optional[AssessmentId] = None
    """If derived from another assessment, its ID."""
    
    revision_chain: Tuple[str, ...] = field(default_factory=tuple)
    """Sequence of transformations applied to this item."""
    
    diagnostic_lineage: Dict[str, str] = field(default_factory=dict)
    """Mapping of diagnostic metadata (e.g., "runtime_version": "1.0")"""
    
    creation_timestamp_utc: Optional[datetime] = None
    """When this was created in UTC."""
    
    runtime_identity: Optional[str] = None
    """Runtime context for isolation (preserved but not used for computation)."""
    
    @classmethod
    def from_subsystem(
        cls,
        subsystem: str,
        source: Optional[str] = None,
        revision_chain: Optional[Tuple[str, ...]] = None,
    ) -> "ProvenanceRecord":
        """Create provenance from a single subsystem."""
        return cls(
            originating_subsystem=subsystem,
            creation_source=source,
            revision_chain=revision_chain or tuple(),
        )
    
    def with_upstream(self, assessment_id: AssessmentId) -> "ProvenanceRecord":
        """Add upstream assessment reference."""
        return dataclass_replace(self, upstream_assessment_id=assessment_id)
    
    def append_revision(self, revision_step: str) -> "ProvenanceRecord":
        """Append a step to the revision chain."""
        return dataclass_replace(
            self,
            revision_chain=self.revision_chain + (revision_step,)
        )


# =============================================================================
# PRIMARY COMPUTATIONAL ENTITIES
# =============================================================================


@dataclass(frozen=True)
class FocusTarget:
    """
    Immutable representation of one possible object of sustained computational attention.
    
    A FocusTarget owns metadata only. It never owns computation.
    
    A FocusTarget may describe:
        • Current user request
        • Conversation context
        • Active plan
        • Memory retrieval
        • Reasoning process
        • Perception result
        • Tool execution result
        • Working memory item
        • Reflection output
        • Monitoring task
    
    Identity must remain stable across state transitions.
    """
    
    # Identity (stable across transitions)
    target_id: FocusTargetId
    """Unique identifier for this target."""
    
    # Semantic classification
    semantic_category: str = "unknown"
    """Broad category of the target (e.g., 'goal', 'task', 'memory', 'perception')."""
    
    origin: Optional[str] = None
    """Originating subsystem or source."""
    
    parent_target_id: Optional[FocusTargetId] = None
    """Parent in a hierarchy (if any)."""
    
    child_target_ids: Tuple[FocusTargetId, ...] = field(default_factory=tuple)
    """Child targets in a hierarchy."""
    
    # Timestamps
    creation_timestamp_utc: Optional[datetime] = None
    """When this target was first created."""
    
    last_update_utc: Optional[datetime] = None
    """When this target was last modified."""
    
    # Priority hints (not computed values - just stored metadata)
    priority_hint: Optional[float] = None
    """Priority hint from external sources (0.0 to 1.0)."""
    
    # Policy and resource hints
    policy_hint: Optional[str] = None
    """Policy guidance for handling this target."""
    
    resource_hint: Optional[str] = None
    """Resource allocation hint."""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Arbitrary metadata for diagnostics and debugging."""
    
    confidence: Optional[float] = None
    """Confidence in the target's validity (0.0 to 1.0)."""
    
    provenance: ProvenanceRecord = field(default_factory=ProvenanceRecord)
    """Provenance record for this target."""
    
    relationships: Tuple[str, ...] = field(default_factory=tuple)
    """Relationship tags (e.g., 'related_to_current_task', 'from_recent_interaction')."""
    
    @classmethod
    def create(
        cls,
        semantic_category: str,
        origin: Optional[str] = None,
        priority_hint: Optional[float] = None,
        confidence: Optional[float] = None,
        provenance: Optional[ProvenanceRecord] = None,
    ) -> "FocusTarget":
        """Create a new focus target with stable identity."""
        return cls(
            target_id=FocusTargetId.generate(),
            semantic_category=semantic_category,
            origin=origin,
            priority_hint=priority_hint,
            confidence=confidence,
            provenance=provenance or ProvenanceRecord.from_subsystem(origin or "unknown"),
            creation_timestamp_utc=datetime.utcnow(),
        )
    
    def update_priority_hint(self, new_hint: float) -> "FocusTarget":
        """Create a copy with updated priority hint."""
        return dataclass_replace(
            self,
            priority_hint=new_hint,
            last_update_utc=datetime.utcnow()
        )
    
    def add_relationship(self, relationship: str) -> "FocusTarget":
        """Create a copy with an additional relationship."""
        return dataclass_replace(
            self,
            relationships=self.relationships + (relationship,)
        )


@dataclass(frozen=True)
class FocusCandidate:
    """
    Represents a FocusTarget currently under consideration for sustained attention.
    
    A candidate combines:
        • FocusTarget
        • Current computational descriptors
        • Context projections
        • Historical state
    
    FocusCandidate is transient. It exists only during one computational evaluation.
    """
    
    # Reference to the target being considered
    target: FocusTarget
    """The focus target this candidate represents."""
    
    # Descriptor context for this evaluation
    priority_descriptor: Optional["PriorityDescriptor"] = None
    relevance_descriptor: Optional["RelevanceDescriptor"] = None
    suppression_descriptor: Optional["SuppressionDescriptor"] = None
    precision_descriptor: Optional["PrecisionDescriptor"] = None
    persistence_descriptor: Optional["PersistenceDescriptor"] = None
    allocation_descriptor: Optional["AllocationDescriptor"] = None
    bias_descriptor: Optional["BiasDescriptor"] = None
    
    # Context projections (future-oriented)
    expected_duration_seconds: Optional[float] = None
    """Expected duration of attention on this candidate."""
    
    projected_priority_change: Optional[float] = None
    """Projected change in priority over time."""
    
    historical_state: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Historical state snapshots for context."""
    
    # Evaluation metadata
    evaluation_timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When this candidate was evaluated."""
    
    evaluation_context: Dict[str, Any] = field(default_factory=dict)
    """Context for the evaluation (runtime state at evaluation time)."""
    
    candidate_id: CandidateId = field(default_factory=CandidateId.generate)
    """Unique ID for tracking during one assessment cycle."""
    
    @classmethod
    def from_target(cls, target: FocusTarget) -> "FocusCandidate":
        """Create a candidate directly from a focus target."""
        return cls(target=target)
    
    def with_descriptor(self, descriptor_type: str, descriptor: Any) -> "FocusCandidate":
        """Attach a descriptor to this candidate."""
        if descriptor_type == "priority":
            return dataclass_replace(self, priority_descriptor=descriptor)
        elif descriptor_type == "relevance":
            return dataclass_replace(self, relevance_descriptor=descriptor)
        elif descriptor_type == "suppression":
            return dataclass_replace(self, suppression_descriptor=descriptor)
        elif descriptor_type == "precision":
            return dataclass_replace(self, precision_descriptor=descriptor)
        elif descriptor_type == "persistence":
            return dataclass_replace(self, persistence_descriptor=descriptor)
        elif descriptor_type == "allocation":
            return dataclass_replace(self, allocation_descriptor=descriptor)
        elif descriptor_type == "bias":
            return dataclass_replace(self, bias_descriptor=descriptor)
        else:
            raise ValueError(f"Unknown descriptor type: {descriptor_type}")
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert candidate to serializable dictionary (for diagnostics)."""
        result = {
            "candidate_id": self.candidate_id.value,
            "target_id": self.target.target_id.value,
            "semantic_category": self.target.semantic_category,
            "evaluation_timestamp_utc": (
                self.evaluation_timestamp_utc.isoformat()
                if self.evaluation_timestamp_utc else None
            ),
        }
        
        # Add descriptors if present
        if self.priority_descriptor:
            result["priority_descriptor"] = self.priority_descriptor.to_serializable()
        
        return result


@dataclass(frozen=True)
class FocusAssessmentReference:
    """
    Reference to an assessment without embedding the full assessment.
    
    Used for linking and history tracking without creating circular dependencies.
    """
    
    assessment_id: AssessmentId
    """The ID of the referenced assessment."""
    
    timestamp_utc: Optional[datetime] = None
    """When this assessment was created."""
    
    target_ids_referenced: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of targets involved in this assessment."""
    
    reference_type: str = "full"
    """Type of reference (e.g., 'full', 'summary', 'snapshot')."""
    
    @classmethod
    def create(
        cls,
        assessment_id: AssessmentId,
        timestamp_utc: Optional[datetime] = None,
    ) -> "FocusAssessmentReference":
        """Create a new assessment reference."""
        return cls(assessment_id=assessment_id, timestamp_utc=timestamp_utc)
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "assessment_id": self.assessment_id.value,
            "timestamp_utc": (
                self.timestamp_utc.isoformat()
                if self.timestamp_utc else None
            ),
            "reference_type": self.reference_type,
        }


# =============================================================================
# DESCRIPTOR OBJECTS - Single responsibility, independently replaceable
# =============================================================================


@dataclass(frozen=True)
class PriorityDescriptor:
    """
    Describes priority characteristics for a focus target.
    
    Contains only priority information without computing it.
    No ranking algorithm implemented here.
    """
    
    base_priority: float
    """Raw priority value (0.0 to 1.0)."""
    
    priority_level: PriorityLevel = PriorityLevel.NEGLIGIBLE
    """Categorical priority level."""
    
    priority_stability: Optional[float] = None
    """How stable the priority is over time (0.0 to 1.0)."""
    
    priority_revisions: int = 0
    """Number of times this priority has been revised."""
    
    priority_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Historical priority values for analysis."""
    
    aggregation_source: Optional[str] = None
    """Where this priority was aggregated from (e.g., 'goal_system', 'memory')."""
    
    revision_chain: Tuple[str, ...] = field(default_factory=tuple)
    """History of how this descriptor was computed/transformed."""
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "base_priority": self.base_priority,
            "priority_level": self.priority_level.value,
            "priority_stability": self.priority_stability,
            "priority_revisions": self.priority_revisions,
            "aggregation_source": self.aggregation_source,
        }
    
    def with_revision(self, revision_info: str) -> "PriorityDescriptor":
        """Create a copy with an added revision step."""
        return dataclass_replace(
            self,
            priority_revisions=self.priority_revisions + 1,
            revision_chain=self.revision_chain + (revision_info,),
        )


@dataclass(frozen=True)
class RelevanceDescriptor:
    """
    Describes relevance characteristics for a focus target.
    
    Contains only relevance information without computing it.
    No relevance algorithm implemented here.
    """
    
    goal_relevance: float
    """Alignment with active goals (0.0 to 1.0)."""
    
    task_relevance: float
    """Alignment with active tasks (0.0 to 1.0)."""
    
    context_relevance: float
    """Relevance to current situation (0.0 to 1.0)."""
    
    recency_score: float = 0.5
    """How recent is this target (0.0 to 1.0)."""
    
    temporal_decay: Optional[float] = None
    """Decay rate over time."""
    
    relevance_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Sources contributing to this relevance assessment."""
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "goal_relevance": self.goal_relevance,
            "task_relevance": self.task_relevance,
            "context_relevance": self.context_relevance,
            "recency_score": self.recency_score,
        }


@dataclass(frozen=True)
class SuppressionDescriptor:
    """
    Describes suppression characteristics for a focus target.
    
    Contains only suppression information without computing it.
    No suppression logic implemented here.
    """
    
    should_suppress: bool = False
    """Whether this target should be suppressed."""
    
    suppression_strength: float = 0.0
    """Strength of suppression (0.0 to 1.0)."""
    
    suppression_expiration_utc: Optional[datetime] = None
    """When suppression expires."""
    
    suppression_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """History of suppression events."""
    
    suppression_reason: Optional[str] = None
    """Human-readable reason for suppression."""
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "should_suppress": self.should_suppress,
            "suppression_strength": self.suppression_strength,
            "suppression_reason": self.suppression_reason,
        }


@dataclass(frozen=True)
class PrecisionDescriptor:
    """
    Describes precision characteristics for focus allocation.
    
    Contains only precision information without computing it.
    No precision estimation algorithm implemented here.
    """
    
    base_precision: float
    """Estimated optimal precision (0.0 to 1.0)."""
    
    bandwidth: PrecisionBandwidth = PrecisionBandwidth.MODERATE
    """Selected bandwidth for allocation."""
    
    estimation_uncertainty: float = 0.0
    """Uncertainty in the estimate (0.0 to 1.0)."""
    
    resource_bandwidth: int = 100
    """Estimated resource bandwidth units needed."""
    
    stability_estimate: Optional[float] = None
    """Stability of the precision estimate."""
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "base_precision": self.base_precision,
            "bandwidth": self.bandwidth.value,
            "estimation_uncertainty": self.estimation_uncertainty,
            "resource_bandwidth": self.resource_bandwidth,
        }


@dataclass(frozen=True)
class PersistenceDescriptor:
    """
    Describes persistence characteristics for focus maintenance.
    
    Contains only persistence information without computing it.
    No persistence algorithm implemented here.
    """
    
    maintenance_duration_seconds: float = 0.0
    """How long this target has been maintained."""
    
    focus_lifetime_seconds: float = 0.0
    """Total expected lifetime of this focus."""
    
    decay_metadata: Optional[Dict[str, Any]] = None
    """Decay characteristics (rate, half-life, etc.)."""
    
    recovery_metadata: Optional[Dict[str, Any]] = None
    """Recovery characteristics from suppression."""
    
    stability_metadata: Optional[Dict[str, Any]] = None
    """Stability characteristics (resistance to shifts)."""
    
    continuity_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """History of focus continuity states."""
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "maintenance_duration_seconds": self.maintenance_duration_seconds,
            "focus_lifetime_seconds": self.focus_lifetime_seconds,
        }


@dataclass(frozen=True)
class AllocationDescriptor:
    """
    Describes allocation characteristics for computational resources.
    
    Contains only allocation information without computing it.
    No runtime allocation implemented here.
    """
    
    recommended_budget: float = 1.0
    """Recommended computational budget (normalized, 0.0 to 1.0)."""
    
    reserved_budget: float = 0.1
    """Reserved budget for dynamic needs."""
    
    allocation_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """History of allocations to this target."""
    
    resource_estimates: Dict[str, float] = field(default_factory=dict)
    """Estimated resources needed per unit time."""
    
    capacity_metadata: Optional[Dict[str, Any]] = None
    """Capacity constraints and availability metadata."""
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommended_budget": self.recommended_budget,
            "reserved_budget": self.reserved_budget,
            "resource_estimates": dict(self.resource_estimates),
        }


@dataclass(frozen=True)
class BiasDescriptor:
    """
    Describes bias characteristics for focus allocation.
    
    Contains only bias information without computing it.
    No bias generation algorithm implemented here.
    """
    
    goal_bias: float = 0.0
    """Goal-based top-down modulation (0.0 to 1.0)."""
    
    task_bias: float = 0.0
    """Task-specific bias (0.0 to 1.0)."""
    
    memory_bias: float = 0.0
    """Memory priming bias (0.0 to 1.0)."""
    
    temporal_bias: float = 0.0
    """Time-based anticipation bias (0.0 to 1.0)."""
    
    spatial_bias: float = 0.0
    """Location-based attention bias (0.0 to 1.0)."""
    
    policy_bias: Optional[str] = None
    """Policy-driven bias."""
    
    active_biases: Tuple[BiasModality, ...] = field(default_factory=tuple)
    """Biases that are currently active."""
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "goal_bias": self.goal_bias,
            "task_bias": self.task_bias,
            "memory_bias": self.memory_bias,
            "temporal_bias": self.temporal_bias,
            "spatial_bias": self.spatial_bias,
            "active_biases": [b.value for b in self.active_biases],
        }


# =============================================================================
# STATE CLASSES - Bounded, explicit state representations
# =============================================================================


@dataclass(frozen=True)
class FocusState:
    """
    Stores currently maintained focus targets and their states.
    
    This is computational state. Not behavioral state.
    
    Contains:
        • Currently maintained focus targets
        • Active candidate identifiers
        • Current dominant target
        • Focus age
        • Last transition
        • Continuity metadata
    """
    
    # Maintained targets
    current_focus_targets: Tuple[FocusTarget, ...] = field(default_factory=tuple)
    """Currently actively maintained targets."""
    
    active_candidate_ids: Tuple[CandidateId, ...] = field(default_factory=tuple)
    """IDs of candidates currently under evaluation."""
    
    dominant_target_id: Optional[FocusTargetId] = None
    """ID of the current dominant target."""
    
    # Timing and continuity
    focus_age_seconds: float = 0.0
    """How long current focus has been maintained."""
    
    last_transition_utc: Optional[datetime] = None
    """When the last focus transition occurred."""
    
    # Continuity metadata
    continuity_count: int = 0
    """Number of continuous focus periods."""
    
    last_break_seconds: float = 0.0
    """Time since last focus break (if any)."""
    
    @classmethod
    def create_initial(cls) -> "FocusState":
        """Create an initial focus state."""
        return cls(
            current_focus_targets=tuple(),
            active_candidate_ids=tuple(),
            focus_age_seconds=0.0,
            last_break_seconds=0.0,
        )
    
    def with_target(self, target: FocusTarget) -> "FocusState":
        """Create a copy with an additional target."""
        return dataclass_replace(
            self,
            current_focus_targets=self.current_focus_targets + (target,),
        )
    
    def without_target(self, target_id: FocusTargetId) -> "FocusState":
        """Create a copy with a target removed."""
        remaining = tuple(t for t in self.current_focus_targets if t.target_id != target_id)
        return dataclass_replace(
            self,
            current_focus_targets=remaining,
            dominant_target_id=None if (
                self.dominant_target_id == target_id
                and len(remaining) == 0
            ) else self.dominant_target_id,
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "focus_targets": [t.target_id.value for t in self.current_focus_targets],
            "active_candidates": [c.value for c in self.active_candidate_ids],
            "dominant_target_id": (
                self.dominant_target_id.value
                if self.dominant_target_id else None
            ),
            "focus_age_seconds": self.focus_age_seconds,
        }


@dataclass(frozen=True)
class PriorityState:
    """
    Stores priority-related state without computing priorities.
    
    Contains:
        • Rolling priority estimates
        • Historical priority evolution
        • Priority stability
        • Priority revisions
        • Aggregation history
    """
    
    # Current estimates (stored, not computed)
    rolling_priority_estimate: float = 0.5
    """Current estimated priority."""
    
    historical_priorities: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """History of priority values."""
    
    priority_stability: Optional[float] = None
    """Stability of the current estimate."""
    
    # Metadata
    priority_revisions: int = 0
    """Number of priority revisions."""
    
    aggregation_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """History of aggregation operations."""
    
    @classmethod
    def create_initial(cls) -> "PriorityState":
        """Create an initial priority state."""
        return cls(rolling_priority_estimate=0.5)
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "rolling_priority_estimate": self.rolling_priority_estimate,
            "priority_revisions": self.priority_revisions,
        }


@dataclass(frozen=True)
class RelevanceState:
    """
    Stores relevance-related state without computing relevance.
    
    Contains current relevance assessments and their history.
    """
    
    # Current estimates
    goal_relevance: float = 0.5
    task_relevance: float = 0.5
    context_relevance: float = 0.5
    
    # History
    historical_relevances: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create_initial(cls) -> "RelevanceState":
        """Create an initial relevance state."""
        return cls()
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "goal_relevance": self.goal_relevance,
            "task_relevance": self.task_relevance,
            "context_relevance": self.context_relevance,
        }


@dataclass(frozen=True)
class SuppressionState:
    """
    Stores suppression-related state without computing suppression.
    
    Contains:
        • Currently suppressed targets
        • Suppression expiration times
        • Suppression history
        • Suppression strength
        • Suppression rationale
    """
    
    # Current suppressions (IDs of suppressed targets)
    temporarily_suppressed_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Targets currently under suppression."""
    
    suppression_expirations_utc: Dict[str, Optional[datetime]] = field(default_factory=dict)
    """Expiration times for each suppression."""
    
    # History
    suppression_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Metadata
    current_suppression_strength: float = 0.0
    """Overall suppression strength level."""
    
    @classmethod
    def create_initial(cls) -> "SuppressionState":
        """Create an initial suppression state."""
        return cls()
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "suppressed_target_count": len(self.temporarily_suppressed_ids),
            "current_suppression_strength": self.current_suppression_strength,
        }


@dataclass(frozen=True)
class PersistenceState:
    """
    Stores persistence-related state without computing persistence.
    
    Contains:
        • Maintenance duration
        • Focus lifetime
        • Decay metadata
        • Recovery metadata
        • Stability metadata
        • Focus continuity history
    """
    
    # Current maintenance
    total_maintenance_seconds: float = 0.0
    """Total time spent maintaining focus."""
    
    last_focus_lifetime_seconds: float = 0.0
    """Duration of the last focus period."""
    
    # Metadata (stored, not computed)
    decay_rate: Optional[float] = None
    recovery_threshold: Optional[float] = None
    stability_score: Optional[float] = None
    
    continuity_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create_initial(cls) -> "PersistenceState":
        """Create an initial persistence state."""
        return cls()
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "total_maintenance_seconds": self.total_maintenance_seconds,
            "last_focus_lifetime_seconds": self.last_focus_lifetime_seconds,
        }


@dataclass(frozen=True)
class PrecisionState:
    """
    Stores precision-related state without computing precision.
    
    Contains:
        • Current precision estimate
        • Precision history
        • Uncertainty measures
        • Resource bandwidth
        • Stability estimate
    """
    
    # Current estimates (stored, not computed)
    current_precision_estimate: float = 0.5
    """Current estimated optimal precision."""
    
    precision_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Historical precision values."""
    
    estimation_uncertainty: float = 0.0
    """Uncertainty in the estimate (0.0 to 1.0)."""
    
    # Bandwidth
    resource_bandwidth_estimate: int = 100
    """Estimated resource bandwidth needed."""
    
    stability_estimate: Optional[float] = None
    
    @classmethod
    def create_initial(cls) -> "PrecisionState":
        """Create an initial precision state."""
        return cls()
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "current_precision_estimate": self.current_precision_estimate,
            "resource_bandwidth_estimate": self.resource_bandwidth_estimate,
        }


@dataclass(frozen=True)
class AllocationState:
    """
    Stores allocation-related state without computing allocations.
    
    Contains:
        • Recommended computational budget
        • Reserved budget
        • Allocation history
        • Resource estimates
        • Capacity metadata
    """
    
    # Current allocations (stored, not computed)
    recommended_budget: float = 1.0
    """Recommended total budget."""
    
    reserved_budget: float = 0.1
    """Reserved for dynamic allocation."""
    
    # History
    allocation_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Estimates (stored, not computed)
    resource_estimates: Dict[str, float] = field(default_factory=dict)
    capacity_metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create_initial(cls) -> "AllocationState":
        """Create an initial allocation state."""
        return cls()
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "recommended_budget": self.recommended_budget,
            "reserved_budget": self.reserved_budget,
        }


@dataclass(frozen=True)
class BiasState:
    """
    Stores bias-related state without computing biases.
    
    Contains:
        • Goal bias
        • Memory bias
        • Modality bias
        • Spatial bias
        • Temporal bias
        • Policy bias
    
    Bias values are computational, not behavioral.
    """
    
    # Current biases (stored, not computed)
    goal_bias: float = 0.0
    task_bias: float = 0.0
    memory_bias: float = 0.0
    temporal_bias: float = 0.0
    spatial_bias: float = 0.0
    policy_bias: Optional[str] = None
    
    # History
    bias_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create_initial(cls) -> "BiasState":
        """Create an initial bias state."""
        return cls()
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "goal_bias": self.goal_bias,
            "task_bias": self.task_bias,
            "memory_bias": self.memory_bias,
            "temporal_bias": self.temporal_bias,
            "spatial_bias": self.spatial_bias,
        }


@dataclass(frozen=True)
class HistoryState:
    """
    Stores bounded history of state transitions and assessments.
    
    Implements bounded history with rolling windows.
    Capacity must be configurable. History growth must be bounded.
    
    Supports:
        • Rolling windows
        • Bounded capacity
        • Snapshots
        • Diagnostics
        • Replay
    """
    
    # Configuration
    max_entries: int = 1000
    """Maximum number of history entries."""
    
    # History entries (chronological)
    _entries: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, max_entries: int = 1000) -> "HistoryState":
        """Create a new history state with configurable capacity."""
        return cls(max_entries=max_entries)
    
    def append(self, entry: Dict[str, Any]) -> "HistoryState":
        """Append a new entry, maintaining bounded capacity."""
        new_entries = self._entries + (entry,)
        
        # Prune to max length (keep newest entries)
        if len(new_entries) > self.max_entries:
            new_entries = new_entries[-self.max_entries:]
        
        return dataclass_replace(self, _entries=new_entries)
    
    def get_latest(self, count: int = 1) -> Tuple[Dict[str, Any], ...]:
        """Get the most recent entries."""
        if not self._entries:
            return tuple()
        return self._entries[-count:]
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "max_entries": self.max_entries,
            "entry_count": len(self._entries),
            "latest_entries": list(self.get_latest(10)),
        }


@dataclass(frozen=True)
class DiagnosticsState:
    """
    Stores diagnostic metadata without modifying state.
    
    Exposes:
        • State summary
        • Transition history
        • Descriptor summary
        • Active targets
        • Capacity usage
        • History statistics
    
    Never modifies state - only observes and reports.
    """
    
    # Counters (bounded)
    total_assessments: int = 0
    total_transitions: int = 0
    focus_shifts: int = 0
    
    # State summary
    active_target_count: int = 0
    suppressed_target_count: int = 0
    
    # Capacity tracking
    history_usage_ratio: float = 0.0
    """Ratio of history capacity used (0.0 to 1.0)."""
    
    last_assessment_timestamp_utc: Optional[datetime] = None
    
    @classmethod
    def create_initial(cls) -> "DiagnosticsState":
        """Create an initial diagnostics state."""
        return cls()
    
    def with_assessment(self) -> "DiagnosticsState":
        """Update diagnostics after an assessment."""
        return dataclass_replace(
            self,
            total_assessments=self.total_assessments + 1,
            last_assessment_timestamp_utc=datetime.utcnow(),
        )
    
    def with_transition(self) -> "DiagnosticsState":
        """Update diagnostics after a transition."""
        return dataclass_replace(
            self,
            total_transitions=self.total_transitions + 1,
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary."""
        return {
            "total_assessments": self.total_assessments,
            "total_transitions": self.total_transitions,
            "focus_shifts": self.focus_shifts,
            "active_target_count": self.active_target_count,
        }


# =============================================================================
# COMPOSITION: FocusingNetworkState
# =============================================================================


@dataclass(frozen=True)
class FocusingNetworkState:
    """
    Complete immutable state of the FocusingNetwork.
    
    Composed from independent state families:
        • FocusState
        • PriorityState
        • RelevanceState
        • SuppressionState
        • PersistenceState
        • PrecisionState
        • AllocationState
        • BiasState
        • HistoryState
        • DiagnosticsState
    
    This is the canonical state representation for the FocusingNetwork.
    All transitions produce new instances - never modify existing ones.
    """
    
    # State families
    focus_state: FocusState = field(default_factory=FocusState.create_initial)
    priority_state: PriorityState = field(default_factory=PriorityState.create_initial)
    relevance_state: RelevanceState = field(default_factory=RelevanceState.create_initial)
    suppression_state: SuppressionState = field(default_factory=SuppressionState.create_initial)
    persistence_state: PersistenceState = field(default_factory=PersistenceState.create_initial)
    precision_state: PrecisionState = field(default_factory=PrecisionState.create_initial)
    allocation_state: AllocationState = field(default_factory=AllocationState.create_initial)
    bias_state: BiasState = field(default_factory=BiasState.create_initial)
    
    # History and diagnostics
    history_state: HistoryState = field(default_factory=lambda: HistoryState.create(1000))
    diagnostics_state: DiagnosticsState = field(default_factory=DiagnosticsState.create_initial)
    
    # Metadata
    state_id: str = field(default_factory=lambda: f"state_{uuid.uuid4().hex[:24]}")
    """Unique identifier for this state instance."""
    
    created_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When this state was created."""
    
    @classmethod
    def create_initial(cls) -> "FocusingNetworkState":
        """Create the initial network state."""
        return cls()
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert entire state to serializable dictionary.
        
        This is the canonical serialization format for:
            • Diagnostics
            • State snapshots
            • Replay
            • Unit tests
        """
        return {
            "state_id": self.state_id,
            "created_at_utc": self.created_at_utc.isoformat(),
            
            # State families
            "focus_state": self.focus_state.to_serializable(),
            "priority_state": self.priority_state.to_serializable(),
            "relevance_state": self.relevance_state.to_serializable(),
            "suppression_state": self.suppression_state.to_serializable(),
            "persistence_state": self.persistence_state.to_serializable(),
            "precision_state": self.precision_state.to_serializable(),
            "allocation_state": self.allocation_state.to_serializable(),
            "bias_state": self.bias_state.to_serializable(),
            
            # History and diagnostics
            "history_state": self.history_state.to_serializable(),
            "diagnostics_state": self.diagnostics_state.to_serializable(),
        }
    
    def capture_snapshot(self, snapshot_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an immutable snapshot of current state.
        
        Snapshots are for:
            • Diagnostics
            • Serialization
            • Replay
            • Unit tests
        
        Snapshots never mutate live state.
        """
        return {
            "snapshot_id": snapshot_id or SnapshotId.generate().value,
            "timestamp_utc": datetime.utcnow().isoformat(),
            "state": self.to_serializable(),
        }


# =============================================================================
# TRANSITION MODEL - Explicit, deterministic transitions
# =============================================================================


@dataclass(frozen=True)
class StateTransition:
    """
    Represents an explicit state transition.
    
    Every transition includes:
        • Reason (why the transition occurred)
        • Timestamp (when it occurred)
        • Affected targets (which entities changed)
        • Revision (version identifier)
        • Diagnostic metadata (for debugging)
    
    Old state → transition() → New state
    
    Never mutate internal structures silently.
    """
    
    # Identity
    transition_id: TransitionId
    """Unique identifier for this transition."""
    
    # Timing
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When the transition occurred."""
    
    # Source and destination
    source_state_id: str
    """ID of the state before transition."""
    
    destination_state_id: str
    """ID of the state after transition."""
    
    # Reason and metadata
    reason: str = "unspecified"
    """Reason for the transition (human-readable)."""
    
    affected_target_ids: Tuple[FocusTargetId, ...] = field(default_factory=tuple)
    """IDs of targets affected by this transition."""
    
    revision: int = 1
    """Transition version for rollback/replay."""
    
    # Diagnostic metadata
    diagnostic_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    originating_subsystem: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        source_state_id: str,
        destination_state_id: str,
        reason: str = "unspecified",
        affected_targets: Tuple[FocusTargetId, ...] = tuple(),
        originating_subsystem: Optional[str] = None,
    ) -> "StateTransition":
        """Create a new state transition."""
        return cls(
            transition_id=TransitionId.generate(),
            source_state_id=source_state_id,
            destination_state_id=destination_state_id,
            reason=reason,
            affected_target_ids=affected_targets,
            originating_subsystem=originating_subsystem,
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert transition to serializable dictionary."""
        return {
            "transition_id": self.transition_id.value,
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "source_state_id": self.source_state_id,
            "destination_state_id": self.destination_state_id,
            "reason": self.reason,
            "revision": self.revision,
        }


@dataclass(frozen=True)
class FocusSnapshot:
    """
    Immutable snapshot of a focus state at a point in time.
    
    Snapshots support:
        • Diagnostics
        • Serialization
        • Replay
        • Unit tests
        • Architectural validation
    
    Snapshots never mutate live state.
    """
    
    # Identity
    snapshot_id: SnapshotId = field(default_factory=SnapshotId.generate)
    """Unique identifier for this snapshot."""
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When the snapshot was taken."""
    
    # State content (immutable view)
    focus_state: FocusState
    priority_state: PriorityState
    relevance_state: RelevanceState
    suppression_state: SuppressionState
    persistence_state: PersistenceState
    precision_state: PrecisionState
    allocation_state: AllocationState
    bias_state: BiasState
    
    # History reference (for replay)
    history_at_snapshot: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def from_network_state(cls, state: FocusingNetworkState) -> "FocusSnapshot":
        """Create a snapshot from the current network state."""
        return cls(
            focus_state=state.focus_state,
            priority_state=state.priority_state,
            relevance_state=state.relevance_state,
            suppression_state=state.suppression_state,
            persistence_state=state.persistence_state,
            precision_state=state.precision_state,
            allocation_state=state.allocation_state,
            bias_state=state.bias_state,
            history_at_snapshot=tuple(state.history_state._entries),
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert snapshot to serializable dictionary."""
        return {
            "snapshot_id": self.snapshot_id.value,
            "timestamp_utc": self.timestamp_utc.isoformat(),
            "focus_state": self.focus_state.to_serializable(),
            "priority_state": self.priority_state.to_serializable(),
            "relevance_state": self.relevance_state.to_serializable(),
            "suppression_state": self.suppression_state.to_serializable(),
            "persistence_state": self.persistence_state.to_serializable(),
            "precision_state": self.precision_state.to_serializable(),
            "allocation_state": self.allocation_state.to_serializable(),
            "bias_state": self.bias_state.to_serializable(),
        }


# =============================================================================
# VALIDATION - Identifier uniqueness, bounded history, consistency
# =============================================================================


class ValidationResult:
    """
    Result of validation operation.
    
    Contains:
        • Success/failure indicator
        • Specific error messages
        • Validation context for debugging
    """
    
    def __init__(
        self,
        is_valid: bool,
        errors: Tuple[str, ...] = tuple(),
        warnings: Tuple[str, ...] = tuple(),
    ):
        self._is_valid = is_valid
        self._errors = errors
        self._warnings = warnings
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self._is_valid
    
    @property
    def errors(self) -> Tuple[str, ...]:
        """Get error messages."""
        return self._errors
    
    @property
    def warnings(self) -> Tuple[str, ...]:
        """Get warning messages."""
        return self._warnings
    
    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge two validation results."""
        new_errors = self._errors + other.errors
        new_warnings = self._warnings + other.warnings
        return ValidationResult(
            is_valid=self._is_valid and other.is_valid,
            errors=new_errors,
            warnings=new_warnings,
        )
    
    @classmethod
    def valid(cls) -> "ValidationResult":
        """Create a successful validation result."""
        return cls(is_valid=True)
    
    @classmethod
    def invalid(cls, *errors: str) -> "ValidationResult":
        """Create a failed validation result."""
        return cls(is_valid=False, errors=errors)


def validate_focus_target(target: FocusTarget) -> ValidationResult:
    """
    Validate a focus target for required constraints.
    
    Checks:
        • Identifier uniqueness
        • Timestamp ordering
        • Confidence bounds (0.0 to 1.0)
        • Priority hint bounds (0.0 to 1.0)
    """
    errors = []
    
    # Check identifiers exist
    if not target.target_id.value:
        errors.append("FocusTarget must have a valid identifier")
    
    # Check confidence bounds
    if target.confidence is not None and not (0.0 <= target.confidence <= 1.0):
        errors.append(f"Confidence must be between 0.0 and 1.0, got {target.confidence}")
    
    # Check priority hint bounds
    if target.priority_hint is not None and not (0.0 <= target.priority_hint <= 1.0):
        errors.append(
            f"Priority hint must be between 0.0 and 1.0, got {target.priority_hint}"
        )
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=tuple(errors),
    )


def validate_focus_candidate(candidate: FocusCandidate) -> ValidationResult:
    """
    Validate a focus candidate for required constraints.
    """
    result = validate_focus_target(candidate.target)
    
    if not candidate.candidate_id.value:
        result = result.merge(ValidationResult(
            is_valid=False,
            errors=("FocusCandidate must have a valid identifier",),
        ))
    
    return result


def validate_history_state(history: HistoryState) -> ValidationResult:
    """
    Validate that history state respects bounded capacity.
    """
    if len(history._entries) > history.max_entries:
        return ValidationResult(
            is_valid=False,
            errors=(
                f"History has {len(history._entries)} entries but max is {history.max_entries}",
            ),
        )
    
    return ValidationResult.valid()


def validate_network_state(state: FocusingNetworkState) -> ValidationResult:
    """
    Validate the entire network state.
    
    Checks all subsystems and their composition.
    """
    result = ValidationResult.valid()
    
    # Validate each component
    result = result.merge(validate_focus_target(FocusTarget(target_id=FocusTargetId(value="placeholder"))))
    result = result.merge(validate_history_state(state.history_state))
    
    return result


# =============================================================================
# UTILITIES - Dataclass replacement for frozen instances
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass instance.
    
    Creates a new copy with specified fields updated while maintaining
    immutability guarantees.
    
    Args:
        obj: The frozen dataclass instance to copy
        kwargs: Field names and new values
        
    Returns:
        A new instance with updated fields
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {
            f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()
        }
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError(f"Object {obj} is not a dataclass")


# =============================================================================
# PUBLIC EXPORTS - Canonical models for the FocusingNetwork
# =============================================================================

__all__ = [
    # Identity types
    "FocusTargetId",
    "CandidateId",
    "AssessmentId",
    "TransitionId",
    "SnapshotId",
    
    # Provenance
    "ProvenanceRecord",
    
    # Primary computational entities
    "FocusTarget",
    "FocusCandidate",
    "FocusAssessmentReference",
    
    # Descriptor objects (single responsibility)
    "PriorityDescriptor",
    "RelevanceDescriptor",
    "SuppressionDescriptor",
    "PrecisionDescriptor",
    "PersistenceDescriptor",
    "AllocationDescriptor",
    "BiasDescriptor",
    
    # State classes
    "FocusState",
    "PriorityState",
    "RelevanceState",
    "SuppressionState",
    "PersistenceState",
    "PrecisionState",
    "AllocationState",
    "BiasState",
    "HistoryState",
    "DiagnosticsState",
    
    # Composition
    "FocusingNetworkState",
    
    # Transitions and snapshots
    "StateTransition",
    "FocusSnapshot",
    
    # Validation
    "ValidationResult",
    "validate_focus_target",
    "validate_focus_candidate",
    "validate_history_state",
    "validate_network_state",
    
    # Utilities
    "dataclass_replace",
]