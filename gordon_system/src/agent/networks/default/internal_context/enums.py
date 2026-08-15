# Internal Context Enums and Canonical Vocabulary
# ================================================

"""
Canonical vocabulary for the InternalContext model.

This module defines:
    - Context purposes (why context was assembled)
    - Scope constraints (what's included/excluded)
    - Projection kinds (what types of projections exist)
    - Conflict categories (how conflicts are classified)
    - Completeness states (how complete a context is)
    - Transition types (how contexts evolve)

ARCHITECTURAL PRINCIPLES:
    • Immutable enum values
    • Deterministic ordering where applicable
    • Bounded sets (no unbounded expansion)
    • No runtime dependencies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, FrozenSet
from datetime import timedelta


# =============================================================================
# CONTEXT PURPOSE - Why context was assembled
# =============================================================================

class InternalContextPurpose:
    """
    Purpose for which internal context was assembled.
    
    Purpose determines:
        • Required projections
        • Expected freshness
        • Context capacity
        • Confidence requirements
        • Validation rules
    
    Purpose does NOT:
        • Execute the activity
        • Create or schedule episodes
        • Update state
    """
    
    # Reflection and self-analysis
    REFLECTION = "reflection"
    """Self-referential processing for insight generation."""
    
    SIMULATION = "simulation"
    """Prospective or counterfactual scenario simulation."""
    
    COUNTERFACTUAL_ANALYSIS = "counterfactual_analysis"
    """Analysis of what-could-have-been scenarios."""
    
    NARRATIVE_INTEGRATION = "narrative_integration"
    """Integration of new information into existing narrative."""
    
    IDENTITY_INTEGRATION = "identity_integration"
    """Processing identity tensions and continuity."""
    
    MEMORY_INTEGRATION = "memory_integration"
    """Memory consolidation and association processing."""
    
    PROBLEM_INCUBATION = "problem_incubation"
    """Background problem solving without active effort."""
    
    CREATIVE_SYNTHESIS = "creative_synthesis"
    """Combining disparate ideas into novel solutions."""
    
    FUTURE_PROJECTION = "future_projection"
    """Future state simulation and planning."""
    
    SELF_EVALUATION = "self_evaluation"
    """Assessment of current state and performance."""
    
    CONCERN_REVIEW = "concern_review"
    """Review of unresolved concerns and pending issues."""
    
    WORKSPACE_CANDIDATE_GENERATION = "workspace_candidate_generation"
    """Generate candidates for conscious workspace submission."""
    
    GENERAL_INTERNAL_COGNITION = "general_internal_cognition"
    """General internal coordination without specific purpose."""
    
    @classmethod
    def all_purposes(cls) -> Tuple[str, ...]:
        """Return all valid purpose values."""
        return (
            cls.REFLECTION,
            cls.SIMULATION,
            cls.COUNTERFACTUAL_ANALYSIS,
            cls.NARRATIVE_INTEGRATION,
            cls.IDENTITY_INTEGRATION,
            cls.MEMORY_INTEGRATION,
            cls.PROBLEM_INCUBATION,
            cls.CREATIVE_SYNTHESIS,
            cls.FUTURE_PROJECTION,
            cls.SELF_EVALUATION,
            cls.CONCERN_REVIEW,
            cls.WORKSPACE_CANDIDATE_GENERATION,
            cls.GENERAL_INTERNAL_COGNITION,
        )
    
    @classmethod
    def requires_memory(cls, purpose: str) -> bool:
        """Check if a purpose typically requires memory projection."""
        required = {
            cls.REFLECTION,
            cls.NARRATIVE_INTEGRATION,
            cls.IDENTITY_INTEGRATION,
            cls.MEMORY_INTEGRATION,
            cls.PROBLEM_INCUBATION,
            cls.CREATIVE_SYNTHESIS,
            cls.FUTURE_PROJECTION,
            cls.CONCERN_REVIEW,
        }
        return purpose in required
    
    @classmethod
    def requires_objectives(cls, purpose: str) -> bool:
        """Check if a purpose typically requires objectives projection."""
        required = {
            cls.SIMULATION,
            cls.COUNTERFACTUAL_ANALYSIS,
            cls.FUTURE_PROJECTION,
            cls.PROBLEM_INCUBATION,
        }
        return purpose in required
    
    @classmethod
    def requires_prediction(cls, purpose: str) -> bool:
        """Check if a purpose typically requires predictive projection."""
        required = {
            cls.SIMULATION,
            cls.COUNTERFACTUAL_ANALYSIS,
            cls.FUTURE_PROJECTION,
        }
        return purpose in required


# =============================================================================
# CONTEXT COMPLETENESS - How complete the context is
# =============================================================================

class ContextCompleteness:
    """
    Structured completeness assessment for internal context.
    
    Completeness is distinct from confidence. A context can be:
        • Complete but low confidence (all items present, uncertain about their quality)
        • Partial but high confidence (few items, very certain about them)
        • Insufficient (missing required items for the purpose)
    """
    
    COMPLETE = "complete"
    """All required projections are present with sufficient content."""
    
    SUFFICIENT = "sufficient"
    """Satisfactory for current purpose despite some optional omissions."""
    
    PARTIAL = "partial"
    """Some required or optional projections are missing or incomplete."""
    
    INSUFFICIENT = "insufficient"
    """Missing critical required projections for the stated purpose."""
    
    INVALID = "invalid"
    """Context failed validation and cannot be used."""
    
    @classmethod
    def is_usable(cls, completeness: str) -> bool:
        """Check if a completeness level represents a usable context."""
        return completeness in {cls.COMPLETE, cls.SUFFICIENT}
    
    @classmethod
    def is_acceptable_for_reflection(cls, completeness: str) -> bool:
        """Check if completeness is acceptable for reflection purposes."""
        # Reflection can proceed with partial information
        return completeness in {cls.COMPLETE, cls.SUFFICIENT, cls.PARTIAL}
    
    @classmethod
    def is_acceptable_for_simulation(cls, completeness: str) -> bool:
        """Check if completeness is acceptable for simulation purposes."""
        # Simulation requires more complete context
        return completeness in {cls.COMPLETE, cls.SUFFICIENT}


# =============================================================================
# CONTEXT CONFIDENCE - Quality of evidence
# =============================================================================

class ContextConfidence:
    """
    Structured confidence assessment for internal context.
    
    Confidence measures evidential quality, not truth. High confidence
    means strong supporting evidence; low confidence means weak or 
    conflicting evidence.
    """
    
    VERY_HIGH = 0.9
    """Strong consensus with minimal uncertainty."""
    
    HIGH = 0.75
    """Good evidence with minor uncertainty."""
    
    MEDIUM = 0.5
    """Mixed evidence, some uncertainty."""
    
    LOW = 0.25
    """Weak or conflicting evidence."""
    
    VERY_LOW = 0.1
    """Minimal supporting evidence."""
    
    @classmethod
    def is_reliable(cls, confidence: float) -> bool:
        """Check if confidence level is considered reliable."""
        return confidence >= cls.MEDIUM
    
    @classmethod
    def get_level_name(cls, confidence: float) -> str:
        """Get the name for a confidence level."""
        if confidence >= cls.VERY_HIGH:
            return "very_high"
        elif confidence >= cls.HIGH:
            return "high"
        elif confidence >= cls.MEDIUM:
            return "medium"
        elif confidence >= cls.LOW:
            return "low"
        else:
            return "very_low"


# =============================================================================
# CONTEXT FRESHNESS - How recent the information is
# =============================================================================

class ContextFreshness:
    """
    Structured freshness assessment for internal context.
    
    Freshness evaluates temporal relevance of context items without
    requiring wall-clock access during assembly (uses injected time).
    """
    
    FRESH = "fresh"
    """Recent and current."""
    
    RECENT = "recent"
    """Somewhat recent, still relevant."""
    
    STALE = "stale"
    """Older information, may need verification."""
    
    EXPIRED = "expired"
    """Beyond acceptable age for this context."""
    
    @classmethod
    def is_acceptable(cls, freshness: str) -> bool:
        """Check if freshness level is acceptable."""
        return freshness in {cls.FRESH, cls.RECENT}


# =============================================================================
# CONFLICT CATEGORIES - How conflicts are classified
# =============================================================================

class ContextConflictCategory:
    """
    Categories of conflict that can arise during context assembly.
    
    Conflicts are never silently resolved. They are recorded and may
    influence confidence or completeness assessment.
    """
    
    REVISION_MISMATCH = "revision_mismatch"
    """Source projection revisions differ unexpectedly."""
    
    OBJECTIVE_CONFLICT = "objective_conflict"
    """Conflicting objective statements."""
    
    IDENTITY_CONFLICT = "identity_conflict"
    """Conflicting identity projections."""
    
    MEMORY_CONFLICT = "memory_conflict"
    """Conflicting memory representations."""
    
    NARRATIVE_CONFLICT = "narrative_conflict"
    """Conflicting narrative elements."""
    
    PREDICTION_CONFLICT = "prediction_conflict"
    """Conflicting predictive projections."""
    
    COMMITMENT_CONFLICT = "commitment_conflict"
    """Conflicting commitment statements."""
    
    TEMPORAL_CONFLICT = "temporal_conflict"
    """Temporal inconsistency (e.g., future event in past tense)."""
    
    PROVENANCE_CONFLICT = "provenance_conflict"
    """Incompatible provenance information."""
    
    POLICY_CONFLICT = "policy_conflict"
    """Violates active policy constraints."""
    
    UNKNOWN = "unknown"
    """Cannot be categorized."""
    
    @classmethod
    def all_categories(cls) -> Tuple[str, ...]:
        """Return all valid conflict categories."""
        return (
            cls.REVISION_MISMATCH,
            cls.OBJECTIVE_CONFLICT,
            cls.IDENTITY_CONFLICT,
            cls.MEMORY_CONFLICT,
            cls.NARRATIVE_CONFLICT,
            cls.PREDICTION_CONFLICT,
            cls.COMMITMENT_CONFLICT,
            cls.TEMPORAL_CONFLICT,
            cls.PROVENANCE_CONFLICT,
            cls.POLICY_CONFLICT,
            cls.UNKNOWN,
        )


# =============================================================================
# TRANSITION TYPES - How contexts evolve
# =============================================================================

class ContextTransitionType:
    """
    Types of transitions between context states.
    
    Transitions are immutable records of how context changes. They do not
    mutate the original context but create a new transition record.
    """
    
    CREATED = "created"
    """New context was assembled from scratch."""
    
    REFRESHED = "refreshed"
    """Context was refreshed with updated projections."""
    
    EXPANDED = "expanded"
    """Context scope was widened (more projections added)."""
    
    REDUCED = "reduced"
    """Context scope was narrowed (projections removed due to capacity)."""
    
    REVISED = "revised"
    """Context was revised based on validation or new information."""
    
    INVALIDATED = "invalidated"
    """Context became invalid (e.g., source data corrupted)."""
    
    SUPERSEDED = "superseded"
    """Context was replaced by a newer version."""
    
    @classmethod
    def all_types(cls) -> Tuple[str, ...]:
        """Return all valid transition types."""
        return (
            cls.CREATED,
            cls.REFRESHED,
            cls.EXPANDED,
            cls.REDUCED,
            cls.REVISED,
            cls.INVALIDATED,
            cls.SUPERSEDED,
        )


# =============================================================================
# PROJECTION KINDS - What types of projections exist
# =============================================================================

class ProjectionKind:
    """
    Kinds of projections that can be included in internal context.
    
    Each projection kind has specific requirements and validation rules.
    """
    
    OBJECTIVES = "objectives"
    """Executive-owned objectives and commitments."""
    
    COMMITMENTS = "commitments"
    """Active commitments (task, safety, cleanup)."""
    
    MEMORY = "memory"
    """Memory projections (episodic, semantic, autobiographical)."""
    
    IDENTITY = "identity"
    """Identity projections (self-model, values, roles)."""
    
    NARRATIVE = "narrative"
    """Narrative projections (current themes, threads)."""
    
    PREDICTION = "prediction"
    """Predictive projections (outcomes, uncertainty estimates)."""
    
    WORKSPACE = "workspace"
    """Workspace projections (broadcast state, candidates)."""
    
    WORKING_MEMORY = "working_memory"
    """Working memory projections (maintained items, reasoning artifacts)."""
    
    EXECUTION = "execution"
    """Execution projections (thread reference, behavioral mode)."""
    
    ATTENTION = "attention"
    """Attention projections (focused targets, distraction pressure)."""
    
    AFFECT = "affect"
    """Affect projections (valence, urgency, concern strength)."""
    
    CONCERNS = "concerns"
    """Concern projections (unresolved problems, pending risks)."""
    
    RESOURCES = "resources"
    """Resource projections (computational pressure, capacity limits)."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid projection kinds."""
        return (
            cls.OBJECTIVES,
            cls.COMMITMENTS,
            cls.MEMORY,
            cls.IDENTITY,
            cls.NARRATIVE,
            cls.PREDICTION,
            cls.WORKSPACE,
            cls.WORKING_MEMORY,
            cls.EXECUTION,
            cls.ATTENTION,
            cls.AFFECT,
            cls.CONCERNS,
            cls.RESOURCES,
        )
    
    @classmethod
    def get_required_kinds(cls, purpose: str) -> FrozenSet[str]:
        """Get projection kinds required for a given purpose."""
        requirements = {
            # Reflection typically needs identity and memory
            InternalContextPurpose.REFLECTION: frozenset({
                cls.MEMORY,
                cls.IDENTITY,
                cls.CONCERNS,
            }),
            # Simulation needs objectives, prediction, memory
            InternalContextPurpose.SIMULATION: frozenset({
                cls.OBJECTIVES,
                cls.PREDICTION,
                cls.MEMORY,
            }),
            # Future projection needs objectives, prediction
            InternalContextPurpose.FUTURE_PROJECTION: frozenset({
                cls.OBJECTIVES,
                cls.PREDICTION,
            }),
            # Narrative integration needs narrative, memory, identity
            InternalContextPurpose.NARRATIVE_INTEGRATION: frozenset({
                cls.NARRATIVE,
                cls.MEMORY,
                cls.IDENTITY,
            }),
            # Default to minimal requirements for unknown purposes
        }
        
        return requirements.get(purpose, frozenset())


# =============================================================================
# SCOPE CONSTRAINTS - What's included/excluded
# =============================================================================

@dataclass(frozen=True, slots=True)
class ContextSubjectId:
    """
    Identifier for a context subject (what the context is about).
    
    Used to scope context assembly to specific subjects or entities.
    """
    
    value: str  # e.g., "user_123", "task_abc", "topic_xyz"
    
    @classmethod
    def from_string(cls, s: str) -> ContextSubjectId:
        """Create a subject ID from string."""
        return cls(value=s)


@dataclass(frozen=True, slots=True)
class ContextTemporalHorizon:
    """
    Temporal scope constraints for context.
    
    Defines the time range relevant to the context assembly.
    """
    
    start_inclusive: bool  # Whether start is inclusive
    start_utc: float  # Start timestamp (Unix epoch)
    end_inclusive: bool  # Whether end is inclusive
    end_utc: float  # End timestamp (Unix epoch)
    
    @classmethod
    def for_last_hours(cls, hours: int) -> ContextTemporalHorizon:
        """Create a temporal horizon for the last N hours."""
        import time
        current = time.time()
        start = current - (hours * 3600)
        return cls(
            start_inclusive=True,
            start_utc=start,
            end_inclusive=True,
            end_utc=current,
        )
    
    @classmethod
    def for_last_days(cls, days: int) -> ContextTemporalHorizon:
        """Create a temporal horizon for the last N days."""
        import time
        current = time.time()
        start = current - (days * 86400)
        return cls(
            start_inclusive=True,
            start_utc=start,
            end_inclusive=True,
            end_utc=current,
        )


@dataclass(frozen=True, slots=True)
class InternalContextScope:
    """
    Immutable scope constraints for internal context.
    
    Defines the boundaries of what information is included in a context.
    """
    
    # Subject identity
    subject_ids: Tuple[ContextSubjectId, ...]
    """Subjects the context is about."""
    
    # Objective scope
    objective_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Specific objectives to include (empty = all active)."""
    
    # Temporal scope
    temporal_horizon: ContextTemporalHorizon = field(
        default_factory=lambda: ContextTemporalHorizon.for_last_hours(24)
    )
    """Time range of relevance."""
    
    # Conceptual scope
    concept_keys: Tuple[str, ...] = field(default_factory=tuple)
    """Specific concepts or topics to include."""
    
    # Capacity constraints
    maximum_items_per_projection: int = 100
    """Maximum items per projection (to prevent unbounded growth)."""
    
    maximum_total_projections: int = 20
    """Maximum different projection kinds."""
    
    maximum_conflicts: int = 50
    """Maximum conflict records to retain."""
    
    # Quality thresholds
    minimum_confidence: float = 0.3
    """Minimum confidence threshold for included items."""
    
    # Freshness constraints
    maximum_age_seconds: float | None = None
    """Maximum age in seconds (None = no constraint)."""
    
    @classmethod
    def default_scope(cls) -> InternalContextScope:
        """Create a default scope with reasonable defaults."""
        return cls(subject_ids=())


# =============================================================================
# BOUNDED CONTEXT CAPACITY - Maximum sizes for various collections
# =============================================================================

@dataclass(frozen=True, slots=True)
class ContextCapacity:
    """
    Capacity constraints for internal context.
    
    Ensures that contexts remain bounded and don't grow unreasonably large.
    """
    
    # Per-projection limits
    maximum_objectives: int = 50
    maximum_commitments: int = 50
    maximum_memory_references: int = 200
    maximum_identity_values: int = 100
    maximum_narrative_references: int = 50
    maximum_predictions: int = 100
    maximum_workspace_items: int = 30
    maximum_working_memory_items: int = 50
    maximum_concerns: int = 100
    maximum_conflicts: int = 50
    maximum_provenance_records: int = 20
    
    # Total context limits
    maximum_total_items: int = 1000
    maximum_total_size_bytes: int = 1024 * 1024  # 1 MB
    
    # Time-based bounds
    maximum_context_age_seconds: float = 3600.0  # 1 hour
    
    @classmethod
    def strict_capacity(cls) -> ContextCapacity:
        """Create a capacity with stricter limits for sensitive contexts."""
        return cls(
            maximum_objectives=25,
            maximum_commitments=25,
            maximum_memory_references=100,
            maximum_conflicts=20,
            maximum_total_items=500,
            maximum_context_age_seconds=1800.0,  # 30 minutes
        )
    
    @classmethod
    def permissive_capacity(cls) -> ContextCapacity:
        """Create a capacity with more relaxed limits for exploratory contexts."""
        return cls(
            maximum_objectives=100,
            maximum_commitments=100,
            maximum_memory_references=500,
            maximum_conflicts=100,
            maximum_total_items=2000,
            maximum_context_age_seconds=7200.0,  # 2 hours
        )


# =============================================================================
# OVERFLOW BEHAVIOR - What happens when capacity is exceeded
# =============================================================================

class OverflowBehavior:
    """
    Behavior when context exceeds its capacity.
    
    Determines how overflow items are handled during assembly.
    """
    
    TRUNCATED = "truncated"
    """Items beyond capacity are omitted with records."""
    
    PARTIAL = "partial"
    """Context is marked as partial with omission details."""
    
    REJECTED = "rejected"
    """Entire context is rejected if any overflow detected."""
    
    DEGRADED = "degraded"
    """Context proceeds with degraded quality but lower confidence."""
    
    @classmethod
    def is_acceptable(cls, behavior: str) -> bool:
        """Check if an overflow behavior represents a usable result."""
        return behavior in {cls.TRUNCATED, cls.PARTIAL}