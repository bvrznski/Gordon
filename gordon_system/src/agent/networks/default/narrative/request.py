# Narrative Request Models
# ========================

"""
Immutable models for narrative requests and their components.

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

# Import enums for type references
from .enums import FactualityClassification


# =============================================================================
# ID TYPES
# =============================================================================

NarrativeRequestId = str
"""Unique identifier for a narrative request."""

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
# NARRATIVE PURPOSE - Canonical purpose representation
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativePurpose:
    """
    Immutable description of the narrative purpose.
    
    Purpose defines what the narrative is trying to accomplish without
    embedding runtime implementation details.
    """
    
    kind: str  # NarrativePurposeKind.*
    """The canonical purpose category."""
    
    statement: str = ""
    """Human-readable description of what this narrative does."""
    
    expected_context: Tuple[str, ...] = field(default_factory=tuple)
    """Required context projections (e.g., 'memory', 'identity')."""
    
    allowed_source_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Source kinds this purpose is allowed to use."""
    
    completion_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for successful completion."""
    
    recursion_limit: int = 3
    """Maximum recursive narrative depth allowed."""
    
    required_confidence: float = 0.5
    """Minimum confidence level required (0.0 to 1.0)."""
    
    @classmethod
    def conversation_continuity(cls) -> NarrativePurpose:
        """Create a conversation continuity purpose."""
        return cls(
            kind="conversation_continuity",
            statement="Maintain conversation thread and participant understanding",
            expected_context=("memory", "conversation"),
            allowed_source_kinds=("conversation_event", "memory_record"),
            completion_rules=("participant_objectives_represented",),
            recursion_limit=2,
            required_confidence=0.6,
        )
    
    @classmethod
    def task_continuity(cls) -> NarrativePurpose:
        """Create a task continuity purpose."""
        return cls(
            kind="task_continuity",
            statement="Track task progress, decisions, and outcomes",
            expected_context=("memory", "execution"),
            allowed_source_kinds=(
                "execution_outcome",
                "decision_record",
                "plan_record"
            ),
            completion_rules=("objective_represented",),
            recursion_limit=2,
            required_confidence=0.5,
        )
    
    @classmethod
    def autobiographical_integration(cls) -> NarrativePurpose:
        """Create an autobiographical integration purpose."""
        return cls(
            kind="autobiographical_integration",
            statement="Integrate experiences into self-model continuity",
            expected_context=("memory", "identity"),
            allowed_source_kinds=(
                "internal_episode",
                "internal_thought",
                "reflective_product"
            ),
            completion_rules=("at_least_one_theme",),
            recursion_limit=3,
            required_confidence=0.7,
        )


# =============================================================================
# NARRATIVE SUBJECT - What the narrative is about
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeSubject:
    """
    Immutable description of the narrative subject.
    
    Subject defines what the narrative is analyzing without embedding
    live objects or full data structures.
    """
    
    kind: str  # NarrativeSubjectKind.*
    """The canonical subject category."""
    
    subject_id: Optional[str] = None
    """ID reference to the subject entity (if applicable)."""
    
    summary: str = ""
    """Brief description of what the narrative is about."""
    
    source_revision: int = 1
    """Source system revision number at narrative start."""
    
    artifact_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to relevant artifacts (memory IDs, thought IDs, etc.)."""
    
    temporal_bounds_start_utc: Optional[datetime] = None
    """Start of temporal relevance window."""
    
    temporal_bounds_end_utc: Optional[datetime] = None
    """End of temporal relevance window."""
    
    @classmethod
    def conversation(cls, conversation_id: str) -> NarrativeSubject:
        """Create a subject for a conversation."""
        return cls(
            kind="conversation",
            subject_id=conversation_id,
            summary=f"Conversation {conversation_id}",
        )
    
    @classmethod
    def task(cls, task_id: str, description: str = "") -> NarrativeSubject:
        """Create a subject for a task."""
        return cls(
            kind="task",
            subject_id=task_id,
            summary=description or f"Task {task_id}",
        )
    
    @classmethod
    def agent(cls) -> NarrativeSubject:
        """Create a subject for Gordon's own activity."""
        return cls(
            kind="agent",
            summary="Gordon's activity and experience",
        )


# =============================================================================
# NARRATIVE SCOPE - Bounded constraints on narrative
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeScope:
    """
    Immutable scope constraints for a narrative episode.
    
    Scope prevents one narrative from becoming unbounded by imposing
    explicit limits on resources and evidence.
    """
    
    # Evidence limits
    maximum_events: int = 100
    """Maximum events to include in the narrative."""
    
    maximum_participants: int = 20
    """Maximum participants to include."""
    
    maximum_source_references: int = 50
    """Maximum source references allowed."""
    
    maximum_relations: int = 200
    """Maximum relations between events."""
    
    maximum_themes: int = 15
    """Maximum themes to identify."""
    
    maximum_gaps: int = 30
    """Maximum gaps to document."""
    
    maximum_conflicts: int = 20
    """Maximum conflicts to document."""
    
    # Planning limits
    maximum_plan_steps: int = 30
    """Maximum steps in the narrative plan."""
    
    maximum_products_expected: int = 15
    """Expected upper bound on products."""
    
    maximum_branches: int = 5
    """Maximum alternate interpretations or perspectives."""
    
    # Context constraints
    temporal_range_seconds: float = 86400.0  # 24 hours
    """Maximum age of relevant activity (in seconds)."""
    
    permitted_source_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Which source kinds are permitted (empty = all)."""
    
    permitted_perspective_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Which perspective kinds are permitted (empty = all)."""
    
    # Quality thresholds
    minimum_source_confidence: float = 0.3
    """Minimum confidence threshold for source inclusion."""
    
    maximum_recursion_depth: int = 3
    """Maximum recursive narrative depth allowed."""
    
    require_new_evidence_for_recursion: bool = True
    """If true, child narratives need new evidence."""
    
    @classmethod
    def compact_scope(cls) -> NarrativeScope:
        """Create a scope for compact narrative."""
        return cls(
            maximum_events=25,
            maximum_participants=5,
            maximum_source_references=10,
            maximum_relations=50,
            maximum_themes=5,
            maximum_gaps=10,
            maximum_conflicts=5,
            temporal_range_seconds=3600.0,  # 1 hour
        )
    
    @classmethod
    def standard_scope(cls) -> NarrativeScope:
        """Create a scope for normal narrative."""
        return cls(
            maximum_events=100,
            maximum_participants=20,
            maximum_source_references=50,
            maximum_relations=200,
            maximum_themes=15,
            maximum_gaps=30,
            maximum_conflicts=20,
            temporal_range_seconds=86400.0,  # 24 hours
        )
    
    @classmethod
    def comprehensive_scope(cls) -> NarrativeScope:
        """Create a scope for thorough narrative."""
        return cls(
            maximum_events=500,
            maximum_participants=50,
            maximum_source_references=200,
            maximum_relations=1000,
            maximum_themes=30,
            maximum_gaps=100,
            maximum_conflicts=50,
            temporal_range_seconds=604800.0,  # 7 days
        )


# =============================================================================
# NARRATIVE SOURCE REFERENCE - Evidence source for narrative
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeSourceReference:
    """
    Immutable reference to a source of evidence for the narrative.
    
    Every source must include factuality classification and provenance.
    """
    
    # Source identity
    source_id: str
    """Unique identifier for the source."""
    
    kind: str  # SourceKind.*
    """The category of this source."""
    
    owner: str
    """Owner of the source (e.g., 'memory', 'execution')."""
    
    revision: int = 1
    """Source system revision number at capture time."""
    
    captured_at_utc: datetime
    """When this source was captured or retrieved."""
    
    # Factuality and quality
    factuality_classification: str  # FactualityClassification.*
    """Factuality of the source content."""
    
    confidence: float = 0.5
    """Confidence in the source (0.0 to 1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for the source."""
    
    # Artifact reference
    artifact_reference: Optional[str] = None
    """Reference to the original artifact if available."""
    
    @classmethod
    def memory_record(
        cls,
        memory_id: str,
        owner: str = "memory",
        factuality: str = FactualityClassification.RECORDED,
        confidence: float = 0.8,
    ) -> NarrativeSourceReference:
        """Create a source reference for a memory record."""
        return cls(
            source_id=memory_id,
            kind="memory_record",
            owner=owner,
            revision=1,
            captured_at_utc=datetime.utcnow(),
            factuality_classification=factuality,
            confidence=confidence,
        )
    
    @classmethod
    def execution_outcome(
        cls,
        outcome_id: str,
        owner: str = "execution",
        factuality: str = FactualityClassification.OBSERVED,
        confidence: float = 0.95,
    ) -> NarrativeSourceReference:
        """Create a source reference for an execution outcome."""
        return cls(
            source_id=outcome_id,
            kind="execution_outcome",
            owner=owner,
            revision=1,
            captured_at_utc=datetime.utcnow(),
            factuality_classification=factuality,
            confidence=confidence,
        )
    
    @classmethod
    def conversation_event(
        cls,
        event_id: str,
        owner: str = "conversation",
        factuality: str = FactualityClassification.RECORDED,
        confidence: float = 0.9,
    ) -> NarrativeSourceReference:
        """Create a source reference for a conversation event."""
        return cls(
            source_id=event_id,
            kind="conversation_event",
            owner=owner,
            revision=1,
            captured_at_utc=datetime.utcnow(),
            factuality_classification=factuality,
            confidence=confidence,
        )


# =============================================================================
# NARRATIVE PERSPECTIVE - Narrative viewpoint
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativePerspective:
    """
    Immutable description of the narrative perspective.
    
    Perspective determines available evidence and interpretation limits.
    A perspective is not objective truth.
    """
    
    kind: str  # NarrativePerspectiveKind.*
    """The canonical perspective category."""
    
    participant_id: Optional[str] = None
    """Participant ID if this is a participant-specific perspective."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this perspective (e.g., 'missing evidence')."""
    
    bias_risk: float = 0.0
    """Estimated risk of bias in this perspective (0.0 to 1.0)."""
    
    available_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs available from this perspective."""
    
    unavailable_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence that is not accessible from this perspective."""
    
    @classmethod
    def agent_first_person(cls) -> NarrativePerspective:
        """Create an agent first-person perspective."""
        return cls(
            kind="agent_first_person",
            participant_id="agent",
            available_evidence=("internal_state", "actions", "observations"),
            limitations=(
                "cannot_access_other_participant_thoughts",
                "potential_self_serving_bias"
            ),
            bias_risk=0.2,
        )
    
    @classmethod
    def external_observer(cls) -> NarrativePerspective:
        """Create an external observer perspective."""
        return cls(
            kind="external_observer",
            available_evidence=("actions", "statements", "outcomes"),
            limitations=(
                "no_access_to_internal_state",
                "interpretation_risk"
            ),
            bias_risk=0.1,
        )


# =============================================================================
# NARRATIVE TEMPORAL SCOPE - Temporal constraints
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeTemporalScope:
    """
    Immutable temporal scope for the narrative.
    
    Narrative time includes event time, recording time, recollection time,
    interpretation time, and simulation time. These should not be collapsed.
    """
    
    start_time_utc: Optional[datetime] = None
    """Start of relevant time period."""
    
    end_time_utc: Optional[datetime] = None
    """End of relevant time period."""
    
    event_time_precision: str = "second"
    """Precision for event timestamps (second, minute, hour, day)."""
    
    record_time_precision: str = "millisecond"
    """Precision for recording timestamps."""
    
    uncertainty_buffer_seconds: float = 60.0
    """Buffer for uncertain temporal relations."""
    
    @classmethod
    def from_window(
        cls,
        start_utc: datetime,
        end_utc: datetime,
    ) -> NarrativeTemporalScope:
        """Create a temporal scope from a time window."""
        return cls(
            start_time_utc=start_utc,
            end_time_utc=end_utc,
            event_time_precision="second",
            record_time_precision="millisecond",
            uncertainty_buffer_seconds=30.0,
        )


# =============================================================================
# NARRATIVE REQUEST - Main request type
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeRequest:
    """
    Immutable request to perform one bounded narrative episode.
    
    The request is semantic - it contains references to data but does not
    contain live objects or runtime handles. It defines WHAT should be
    narrated, not HOW the narrative should be implemented.
    """
    
    # Identity and metadata
    request_id: NarrativeRequestId
    """Unique identifier for this request."""
    
    purpose: NarrativePurpose
    """What kind of narrative is being requested."""
    
    subject: NarrativeSubject
    """What the narrative is about."""
    
    scope: NarrativeScope
    """Bounded constraints on the narrative."""
    
    # Context binding
    context_id: InternalContextId
    """Reference to InternalContext revision."""
    
    context_revision: int = 1
    """Context version at request time."""
    
    temporal_scope: NarrativeTemporalScope = field(
        default_factory=NarrativeTemporalScope
    )
    """Temporal scope for the narrative."""
    
    # Source references (evidence)
    source_references: Tuple[NarrativeSourceReference, ...] = field(default_factory=tuple)
    """Sources of evidence for the narrative."""
    
    perspective: NarrativePerspective = field(
        default_factory=NarrativePerspective
    )
    """Narrative perspective to use."""
    
    # Origin tracking
    originating_episode_id: Optional[InternalEpisodeId] = None
    """ID of parent episode if derived from one."""
    
    originating_thought_ids: Tuple[InternalThoughtId, ...] = field(
        default_factory=tuple
    )
    """Thought IDs that triggered this request."""
    
    # Product expectations
    expected_products: FrozenSet[str] = field(default_factory=frozenset)
    """Product kinds expected from this narrative."""
    
    completion_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Explicit conditions for successful completion."""
    
    # Coordination metadata
    requested_by: str = "DEFAULT_NETWORK"
    """Who/what made the request (NarrativeRequester.*)."""
    
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
        purpose: NarrativePurpose,
        subject: NarrativeSubject,
        scope: NarrativeScope,
        context_id: str,
        request_id: Optional[str] = None,
    ) -> NarrativeRequest:
        """
        Create a new narrative request with default metadata.
        
        Args:
            purpose: The purpose of this narrative
            subject: What the narrative is about
            scope: Bounded constraints on the narrative
            context_id: Reference to the InternalContext revision
            request_id: Optional explicit ID (auto-generated if None)
            
        Returns:
            New NarrativeRequest instance with valid metadata
        """
        return cls(
            request_id=request_id or f"narrative_request_{id(purpose)}",
            purpose=purpose,
            subject=subject,
            scope=scope,
            context_id=context_id,
            context_revision=1,
            expected_products=frozenset(scope.permitted_source_kinds),
            perspective=NarrativePerspective(kind="agent_first_person"),
        )
    
    def can_produce_product(self, product_kind: str) -> bool:
        """Check if this request is allowed to produce a given product kind."""
        # By default, all products are allowed unless restricted
        return True
    
    def exceeds_scope_limits(
        self,
        event_count: int,
        source_count: int,
        participant_count: int,
    ) -> Tuple[str, ...]:
        """
        Check if counts exceed scope limits.
        
        Args:
            event_count: Number of events in the narrative
            source_count: Number of source references used
            participant_count: Number of participants identified
            
        Returns:
            List of exceeded limits (empty if within bounds)
        """
        violations = []
        if event_count > self.scope.maximum_events:
            violations.append("event_limit_exceeded")
        if source_count > self.scope.maximum_source_references:
            violations.append("source_limit_exceeded")
        if participant_count > self.scope.maximum_participants:
            violations.append("participant_limit_exceeded")
        return tuple(violations)