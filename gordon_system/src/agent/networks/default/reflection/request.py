# Reflection Request Models
# ==========================

"""
Immutable models for reflection requests, purposes, subjects, and scopes.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies (no imports from Core or Execution)
    - Bounded by explicit limits
    - Semantic content only (no live objects)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, FrozenSet
from datetime import datetime


# =============================================================================
# ID TYPES
# =============================================================================

ReflectionRequestId = str
"""Unique identifier for a reflection request."""

InternalContextId = str
"""Reference to an InternalContext instance."""

InternalEpisodeId = str
"""Reference to an InternalEpisode instance."""

InternalThoughtId = str
"""Reference to an InternalThought instance."""

CorrelationId = str
"""Correlation ID for distributed tracing."""

CausationId = str
"""Causation ID if request results from another event."""


# =============================================================================
# REFLECTION PURPOSE - Canonical purpose representation
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionPurpose:
    """
    Immutable description of the reflection purpose.
    
    Purpose defines what the reflection is trying to accomplish without
    embedding runtime implementation details.
    
    PROPERTIES:
        • kind: Canonical purpose category (ReflectionPurposeKind.*)
        • statement: Human-readable description
        • expected_context: What context projections are needed
        • allowed_products: Which product kinds may be produced
        • completion_rules: Conditions for successful completion
        • recursion_limit: How deep recursive reflection is allowed
        • required_confidence: Minimum confidence threshold
    """
    
    kind: str  # ReflectionPurposeKind.*
    """The canonical purpose category."""
    
    statement: str = ""
    """Human-readable description of what this reflection does."""
    
    expected_context: Tuple[str, ...] = field(default_factory=tuple)
    """Required context projections (e.g., 'memory', 'identity')."""
    
    allowed_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product kinds this purpose is allowed to produce."""
    
    completion_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for successful completion."""
    
    recursion_limit: int = 3
    """Maximum recursive reflection depth."""
    
    required_confidence: float = 0.5
    """Minimum confidence level required (0.0 to 1.0)."""
    
    @classmethod
    def experience_review(cls) -> ReflectionPurpose:
        """Create an experience review purpose."""
        return cls(
            kind="experience_review",
            statement="Review past experience to derive insights",
            expected_context=("memory", "execution"),
            allowed_products=("insight", "lesson", "pattern"),
            completion_rules=("at_least_one_insight",),
            recursion_limit=2,
            required_confidence=0.6,
        )
    
    @classmethod
    def failure_review(cls) -> ReflectionPurpose:
        """Create a failure review purpose."""
        return cls(
            kind="failure_review",
            statement="Analyze failure to identify causes and lessons",
            expected_context=("memory", "execution", "outcome"),
            allowed_products=(
                "insight", "cause_hypothesis", "lesson", 
                "correction_proposal"
            ),
            completion_rules=("at_least_one_cause",),
            recursion_limit=2,
            required_confidence=0.5,
        )
    
    @classmethod
    def pattern_discovery(cls) -> ReflectionPurpose:
        """Create a pattern discovery purpose."""
        return cls(
            kind="pattern_discovery",
            statement="Detect patterns across semantic activity",
            expected_context=("memory", "narrative"),
            allowed_products=("pattern",),
            completion_rules=("at_least_one_pattern",),
            recursion_limit=1,
            required_confidence=0.7,
        )
    
    @classmethod
    def insight_generation(cls) -> ReflectionPurpose:
        """Create an insight generation purpose."""
        return cls(
            kind="insight_generation",
            statement="Generate new insights from prior activity",
            expected_context=("memory", "thoughts"),
            allowed_products=("insight",),
            completion_rules=("at_least_one_insight",),
            recursion_limit=3,
            required_confidence=0.8,
        )


# =============================================================================
# REFLECTION SUBJECT - What is being reflected upon
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionSubject:
    """
    Immutable description of the reflection subject.
    
    Subject defines what the reflection is analyzing without embedding
    live objects or full data structures.
    
    PROPERTIES:
        • kind: Canonical subject category (ReflectionSubjectKind.*)
        • subject_id: ID reference to the subject entity
        • summary: Brief description of the subject
        • source_revision: Revision number at time of reflection
        • artifact_references: References to relevant artifacts
        • temporal_bounds: Start and end times for relevance
    """
    
    kind: str  # ReflectionSubjectKind.*
    """The canonical subject category."""
    
    subject_id: Optional[str] = None
    """ID reference to the subject entity (if applicable)."""
    
    summary: str = ""
    """Brief description of what is being reflected upon."""
    
    source_revision: int = 1
    """Source system revision number at reflection start."""
    
    artifact_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to relevant artifacts (memory IDs, thought IDs, etc.)."""
    
    temporal_bounds_start_utc: Optional[datetime] = None
    """Start of temporal relevance window."""
    
    temporal_bounds_end_utc: Optional[datetime] = None
    """End of temporal relevance window."""
    
    @classmethod
    def execution_thread(cls, thread_id: str) -> ReflectionSubject:
        """Create a subject for an ExecutionThread."""
        return cls(
            kind="execution_thread",
            subject_id=thread_id,
            summary=f"ExecutionThread {thread_id}",
        )
    
    @classmethod
    def task(cls, task_id: str, description: str = "") -> ReflectionSubject:
        """Create a subject for a Task."""
        return cls(
            kind="task",
            subject_id=task_id,
            summary=description or f"Task {task_id}",
        )
    
    @classmethod
    def decision(cls, decision_id: str) -> ReflectionSubject:
        """Create a subject for a Decision."""
        return cls(
            kind="decision",
            subject_id=decision_id,
            summary=f"Decision {decision_id}",
        )
    
    @classmethod
    def internal_episode(cls, episode_id: str) -> ReflectionSubject:
        """Create a subject for an InternalEpisode."""
        return cls(
            kind="internal_episode",
            subject_id=episode_id,
            summary=f"InternalEpisode {episode_id}",
        )
    
    @classmethod
    def general_experience(cls, description: str = "") -> ReflectionSubject:
        """Create a general experience subject."""
        return cls(
            kind="general_experience",
            summary=description or "General internal experience",
        )


# =============================================================================
# REFLECTION SCOPE - Bounded constraints on reflection
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionScope:
    """
    Immutable scope constraints for a reflection episode.
    
    Scope prevents one reflection from becoming unbounded by imposing
    explicit limits on resources and evidence.
    
    PROPERTIES:
        • maximum_evidence_items: Hard limit on evidence collection
        • maximum_prior_thoughts: Max thoughts to consider
        • maximum_temporal_range_seconds: Maximum age of relevant activity
        • maximum_plan_steps: Max steps in reflection plan
        • maximum_products_expected: Expected upper bound on products
        • maximum_follow_up_proposals: Max proposals allowed
        • excluded_subjects: Subjects that must not be included
        • permitted_product_kinds: Which product kinds are allowed
        • required_confidence: Minimum confidence threshold
    """
    
    # Evidence limits
    maximum_evidence_items: int = 100
    """Maximum evidence items to collect."""
    
    maximum_prior_thoughts: int = 50
    """Maximum prior thoughts to consider."""
    
    maximum_temporal_range_seconds: float = 86400.0  # 24 hours
    """Maximum age of relevant activity (in seconds)."""
    
    # Planning limits
    maximum_plan_steps: int = 20
    """Maximum steps in the reflection plan."""
    
    maximum_products_expected: int = 15
    """Expected upper bound on reflective products."""
    
    maximum_follow_up_proposals: int = 5
    """Maximum follow-up proposals allowed."""
    
    # Subject constraints
    excluded_subjects: Tuple[str, ...] = field(default_factory=tuple)
    """Subject IDs that must not be included."""
    
    permitted_product_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Which product kinds are permitted (empty = all)."""
    
    # Quality thresholds
    required_confidence: float = 0.5
    """Minimum confidence threshold for products."""
    
    maximum_recursion_depth: int = 3
    """Maximum recursive reflection depth allowed."""
    
    require_new_evidence_for_recursion: bool = True
    """If true, child reflections need new evidence."""
    
    @classmethod
    def surface_level(cls) -> ReflectionScope:
        """Create a scope for shallow reflection."""
        return cls(
            maximum_evidence_items=25,
            maximum_prior_thoughts=10,
            maximum_temporal_range_seconds=3600.0,  # 1 hour
            maximum_plan_steps=5,
            maximum_products_expected=3,
            maximum_follow_up_proposals=2,
        )
    
    @classmethod
    def standard_level(cls) -> ReflectionScope:
        """Create a scope for normal reflection."""
        return cls(
            maximum_evidence_items=100,
            maximum_prior_thoughts=50,
            maximum_temporal_range_seconds=86400.0,  # 24 hours
            maximum_plan_steps=20,
            maximum_products_expected=15,
            maximum_follow_up_proposals=5,
        )
    
    @classmethod
    def deep_level(cls) -> ReflectionScope:
        """Create a scope for thorough reflection."""
        return cls(
            maximum_evidence_items=250,
            maximum_prior_thoughts=100,
            maximum_temporal_range_seconds=604800.0,  # 7 days
            maximum_plan_steps=30,
            maximum_products_expected=30,
            maximum_follow_up_proposals=10,
        )


# =============================================================================
# REFLECTION REQUEST - Main request type
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionRequest:
    """
    Immutable request to perform one bounded reflection episode.
    
    The request is semantic - it contains references to data but does not
    contain live objects or runtime handles. It defines WHAT should be
    reflected upon, not HOW the reflection should be implemented.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • purpose: What kind of reflection is being requested
        • subject: What is being reflected upon
        • scope: Bounded constraints on the reflection
        • context_id: Reference to InternalContext revision
        • context_revision: Context version at request time
        • originating_episode_id: Parent episode if derived
        • originating_thought_ids: Thoughts that triggered this request
        • expected_products: Which products are desired
        • completion_requirements: Success criteria
        • requested_by: Who/what made the request
        • correlation_id: For distributed tracing
        • causation_id: If results from another event
        • provenance: Where this request originated
    
    BOUNDEDNESS:
        Every limit is explicit. Overflow must be recorded.
    
    NOT RESPONSIBLE FOR:
        - Executing reflection algorithms
        - Allocating runtime resources
        - Scheduling execution
        - Storing persistent results
    """
    
    # Identity and metadata
    request_id: ReflectionRequestId
    """Unique identifier for this request."""
    
    purpose: ReflectionPurpose
    """What kind of reflection is being requested."""
    
    subject: ReflectionSubject
    """What is being reflected upon."""
    
    scope: ReflectionScope
    """Bounded constraints on the reflection."""
    
    # Context binding
    context_id: InternalContextId
    """Reference to InternalContext revision."""
    
    context_revision: int = 1
    """Context version at request time."""
    
    # Origin tracking
    originating_episode_id: Optional[InternalEpisodeId] = None
    """ID of parent episode if derived from one."""
    
    originating_thought_ids: Tuple[InternalThoughtId, ...] = field(
        default_factory=tuple
    )
    """Thought IDs that triggered this request."""
    
    # Product expectations
    expected_products: FrozenSet[str] = field(default_factory=frozenset)
    """Product kinds expected from this reflection."""
    
    completion_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Explicit conditions for successful completion."""
    
    # Coordination metadata
    requested_by: str = "DEFAULT_NETWORK"
    """Who/what made the request (ReflectionRequester.*)."""
    
    correlation_id: CorrelationId = ""
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[CausationId] = None
    """Causation ID if this results from another event."""
    
    provenance: str = "canonical"
    """Provenance reference (where request type is documented)."""
    
    # Timestamps
    requested_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When the request was created."""
    
    @classmethod
    def new(
        cls,
        purpose: ReflectionPurpose,
        subject: ReflectionSubject,
        scope: ReflectionScope,
        context_id: str,
        request_id: Optional[str] = None,
    ) -> ReflectionRequest:
        """
        Create a new reflection request with default metadata.
        
        Args:
            purpose: The purpose of this reflection
            subject: What is being reflected upon
            scope: Bounded constraints on the reflection
            context_id: Reference to the InternalContext revision
            request_id: Optional explicit ID (auto-generated if None)
            
        Returns:
            New ReflectionRequest instance with valid metadata
        """
        return cls(
            request_id=request_id or f"reflection_request_{id(purpose)}",
            purpose=purpose,
            subject=subject,
            scope=scope,
            context_id=context_id,
            context_revision=1,
            expected_products=frozenset(scope.permitted_product_kinds),
        )
    
    def can_produce_product(self, product_kind: str) -> bool:
        """Check if this request is allowed to produce a given product kind."""
        permitted = self.scope.permitted_product_kinds
        return not permitted or product_kind in permitted
    
    def exceeds_scope_limits(self, evidence_count: int, products_count: int) -> Tuple[str, ...]:
        """
        Check if counts exceed scope limits.
        
        Args:
            evidence_count: Number of evidence items collected
            products_count: Number of products generated
            
        Returns:
            List of exceeded limits (empty if within bounds)
        """
        violations = []
        if evidence_count > self.scope.maximum_evidence_items:
            violations.append("evidence_limit_exceeded")
        if products_count > self.scope.maximum_products_expected:
            violations.append("products_limit_exceeded")
        return tuple(violations)