# Default Network State Models
# ============================

"""
Canonical DefaultNetwork state models for runtime-neutral coordination.

All state models are deeply immutable to ensure deterministic behavior,
replayability, and thread safety. No live objects, callbacks, or runtime
handles may be embedded in these models.

PHASE 4.3.12: Runtime-Neutral State Contracts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .result import DefaultNetworkResult


# =============================================================================
# DEFAULT NETWORK STATE SNAPSHOT (read-only state view)
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkStateSnapshot:
    """
    Read-only snapshot of the Default Network's computational state.
    
    This captures only bounded computational state. It does NOT include
    cognitive goals, active task state, or global history.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-SNAPSHOT-INV-001: Snapshot is immutable (deeply frozen)
        DEFAULT-SNAPSHOT-INV-002: No runtime references in snapshot data
        DEFAULT-SNAPSHOT-INV-003: Bounded state coverage
        
    CONTENT:
      - revision: State revision at time of capture
      - created_at_utc: When snapshot was taken
      - episode_index: Episode tracking (bounded)
      - pending_requests: Pending external requests (bounded)

    PROVENANCE:
      - provenance: Snapshot creation record

    NOT INCLUDES:
      - Live objects, callbacks, or service handles
      - Runtime scheduling handles
      - External capability implementations
      - Unbounded state growth
    """
    
    # State reference
    revision: int
    """State revision at time of capture."""
    
    created_at_utc: datetime
    """When this snapshot was taken."""
    
    # Bounded state projections
    episode_index_ref: Optional[str] = None
    """Reference to episode index (not embedded)."""
    
    pending_requests_count: int = 0
    """Count of pending external requests."""
    
    confidence: float = 0.5
    """Confidence in snapshot accuracy (0.0 to 1.0)."""
    
    provenance_ref: Optional[str] = None
    """Reference to snapshot provenance record."""
    
    @classmethod
    def from_state(cls, state: DefaultNetworkState) -> "DefaultNetworkStateSnapshot":
        """Create a snapshot from current state."""
        return cls(
            revision=state.revision,
            created_at_utc=datetime.utcnow(),
            episode_index_ref=None,
            pending_requests_count=len(state.pending_requests.pending_request_refs),
            confidence=1.0,
            provenance_ref=None,
        )


# =============================================================================
# DEFAULT NETWORK STATE REVISION
# =============================================================================

DefaultNetworkStateRevision = int
"""Monotonically increasing state revision number."""


# =============================================================================
# DEFAULT NETWORK STATE PROVENANCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkStateProvenance:
    """
    Complete provenance record for a DefaultNetwork state snapshot.
    
    Tracks state creation without embedding runtime references.
    """
    
    # State reference
    state_revision: int
    
    # Processing metadata
    created_at_utc: datetime
    processing_version: str = "1.0.0"
    
    # Request correlation
    last_processed_request_id: Optional[str] = None
    
    @classmethod
    def new(
        cls,
        state_revision: int,
        created_at_utc: datetime,
    ) -> DefaultNetworkStateProvenance:
        """Create a new provenance record."""
        return cls(
            state_revision=state_revision,
            created_at_utc=created_at_utc,
            processing_version="1.0.0",
            last_processed_request_id=None,
        )


# =============================================================================
# BOUNDED COLLECTIONS
# =============================================================================

@dataclass(frozen=True, slots=True)
class BoundedEpisodeIndex:
    """
    Bounded index of active and waiting episode references.
    
    All collections are bounded with overflow handling.
    """
    
    # Active episodes
    active_episode_refs: Tuple[str, ...]
    """References to active episodes."""
    
    waiting_episode_refs: Tuple[str, ...]
    """References to episodes waiting for input."""
    
    completed_episode_digests: Tuple[str, ...]
    """Digests of completed episodes (short summary, not full content)."""
    
    # Bounded size
    max_active_episodes: int = 100
    max_waiting_episodes: int = 50
    max_completed_digests: int = 200
    
    @classmethod
    def empty(cls) -> BoundedEpisodeIndex:
        """Create an empty episode index."""
        return cls(
            active_episode_refs=(),
            waiting_episode_refs=(),
            completed_episode_digests=(),
        )
    
    def add_active(self, ref: str) -> BoundedEpisodeIndex:
        """Add a new active episode reference with overflow handling."""
        refs = tuple(ref for ref in self.active_episode_refs if len(self.active_episode_refs) < self.max_active_episodes)
        return BoundedEpisodeIndex(
            active_episode_refs=(*refs, ref),
            waiting_episode_refs=self.waiting_episode_refs,
            completed_episode_digests=self.completed_episode_digests,
            max_active_episodes=self.max_active_episodes,
            max_waiting_episodes=self.max_waiting_episodes,
            max_completed_digests=self.max_completed_digests,
        )
    
    def add_waiting(self, ref: str) -> BoundedEpisodeIndex:
        """Add a waiting episode reference with overflow handling."""
        refs = tuple(ref for ref in self.waiting_episode_refs if len(self.waiting_episode_refs) < self.max_waiting_episodes)
        return BoundedEpisodeIndex(
            active_episode_refs=self.active_episode_refs,
            waiting_episode_refs=(*refs, ref),
            completed_episode_digests=self.completed_episode_digests,
            max_active_episodes=self.max_active_episodes,
            max_waiting_episodes=self.max_waiting_episodes,
            max_completed_digests=self.max_completed_digests,
        )
    
    def add_completed(self, digest: str) -> BoundedEpisodeIndex:
        """Add a completed episode digest with overflow handling."""
        digests = tuple(d for d in self.completed_episode_digests if len(self.completed_episode_digests) < self.max_completed_digests)
        return BoundedEpisodeIndex(
            active_episode_refs=self.active_episode_refs,
            waiting_episode_refs=self.waiting_episode_refs,
            completed_episode_digests=(*digests, digest),
            max_active_episodes=self.max_active_episodes,
            max_waiting_episodes=self.max_waiting_episodes,
            max_completed_digests=self.max_completed_digests,
        )


@dataclass(frozen=True, slots=True)
class BoundedExternalRequestIndex:
    """
    Bounded index of pending external requests.
    
    All collections are bounded with overflow handling.
    """
    
    pending_request_refs: Tuple[str, ...]
    """References to pending external requests."""
    
    consumed_result_refs: Tuple[str, ...]
    """IDs of already consumed capability results."""
    
    # Bounds
    max_pending_requests: int = 50
    max_consumed_results: int = 100
    
    @classmethod
    def empty(cls) -> BoundedExternalRequestIndex:
        """Create an empty request index."""
        return cls(
            pending_request_refs=(),
            consumed_result_refs=(),
        )


@dataclass(frozen=True, slots=True)
class BoundedProposalIndex:
    """
    Bounded index of pending proposals.
    
    All collections are bounded with overflow handling.
    """
    
    pending_proposal_refs: Tuple[str, ...]
    """References to pending proposals."""
    
    # Bound
    max_pending_proposals: int = 50
    
    @classmethod
    def empty(cls) -> BoundedProposalIndex:
        """Create an empty proposal index."""
        return cls(
            pending_proposal_refs=(),
        )


@dataclass(frozen=True, slots=True)
class BoundedThoughtHistory:
    """
    Bounded history of recently generated thoughts.
    
    Contains only references/summaries, not full thought content.
    """
    
    recent_thought_refs: Tuple[str, ...]
    """References to recent thoughts."""
    
    # Bound
    max_recent_thoughts: int = 100
    
    @classmethod
    def empty(cls) -> BoundedThoughtHistory:
        """Create an empty thought history."""
        return cls(
            recent_thought_refs=(),
        )


@dataclass(frozen=True, slots=True)
class DefaultNetworkPathStates:
    """
    Path-specific state projections.
    
    Each specialized path maintains its own bounded state projection.
    These are NOT the full specialized states - just projections needed
    by the root network for coordination.
    """
    
    thought_generation_state: Optional[str] = None
    reflection_state: Optional[str] = None
    simulation_state: Optional[str] = None
    counterfactual_state: Optional[str] = None
    narrative_state: Optional[str] = None
    identity_state: Optional[str] = None
    memory_state: Optional[str] = None
    predictive_state: Optional[str] = None
    workspace_state: Optional[str] = None
    
    @classmethod
    def empty(cls) -> DefaultNetworkPathStates:
        """Create an empty path states projection."""
        return cls()


@dataclass(frozen=True, slots=True)
class BoundedTransitionHistory:
    """
    Bounded history of state transitions.
    
    Contains only transition references/summaries, not full content.
    """
    
    recent_transitions: Tuple[str, ...]
    """References to recent transitions."""
    
    # Bound
    max_recent_transitions: int = 100
    
    @classmethod
    def empty(cls) -> BoundedTransitionHistory:
        """Create an empty transition history."""
        return cls(
            recent_transitions=(),
        )


# =============================================================================
# DEFAULT NETWORK STATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkState:
    """
    Canonical state snapshot of the Default Network.
    
    This is a complete bounded snapshot that enables deterministic replay
    and idempotent processing.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-STATE-INV-001: State is immutable (deeply frozen)
        DEFAULT-STATE-INV-002: State contains no runtime references
        DEFAULT-STATE-INV-003: State is bounded (no unbounded growth)
        DEFAULT-STATE-INV-004: State revision increases on every change
        
    PROPERTIES:
        • revision: Current state revision number
        • created_at_utc: When this state snapshot was created
        
    EPISODE TRACKING:
        • episode_index: Index of active/waiting/completed episodes
        
    EXTERNAL INTERFACE:
        • pending_requests: Pending external requests index
        • consumed_results: Already consumed capability results
        
    INTERNAL COGNITION:
        • thought_history: Recent thought references
        • path_states: Path-specific state projections
        
    OBSERVABILITY:
        • transition_history: Transition references
        • configuration_revision: Configuration version
        
    PROVENANCE:
        • provenance: State snapshot provenance
    
    NOT RESPONSIBLE FOR:
        • Owning authoritative Memory, Identity, Narrative
        • Scheduling runtime execution
        • Creating threads or processes
    """
    
    # Revision and timing
    revision: DefaultNetworkStateRevision
    """Current state revision number."""
    
    created_at_utc: datetime
    """When this state snapshot was created."""
    
    # Episode tracking
    episode_index: BoundedEpisodeIndex
    """Index of active/waiting/completed episodes."""
    
    # External interface
    pending_requests: BoundedExternalRequestIndex
    """Pending external requests index."""
    
    consumed_results: Tuple[str, ...]
    """Already consumed capability result IDs."""
    
    pending_proposals: BoundedProposalIndex
    """Pending proposals index."""
    
    # Internal cognition
    thought_history: BoundedThoughtHistory
    """Recent thought references."""
    
    path_states: DefaultNetworkPathStates
    """Path-specific state projections."""
    
    transition_history: BoundedTransitionHistory
    """Transition references."""
    
    # Configuration and provenance
    configuration_revision: Optional[str] = None
    """Configuration version."""
    
    provenance: Optional[DefaultNetworkStateProvenance] = None
    """State snapshot provenance."""
    
    @classmethod
    def initial_state(cls) -> DefaultNetworkState:
        """Create an initial state with revision 1."""
        now = datetime.utcnow()
        return cls(
            revision=1,
            created_at_utc=now,
            episode_index=BoundedEpisodeIndex.empty(),
            pending_requests=BoundedExternalRequestIndex.empty(),
            consumed_results=(),
            pending_proposals=BoundedProposalIndex.empty(),
            thought_history=BoundedThoughtHistory.empty(),
            path_states=DefaultNetworkPathStates.empty(),
            transition_history=BoundedTransitionHistory.empty(),
        )
    
    def next_revision(self, new_provenance: DefaultNetworkStateProvenance) -> DefaultNetworkState:
        """Create a new state with incremented revision."""
        return DefaultNetworkState(
            revision=self.revision + 1,
            created_at_utc=new_provenance.created_at_utc,
            episode_index=self.episode_index,
            pending_requests=self.pending_requests,
            consumed_results=self.consumed_results,
            pending_proposals=self.pending_proposals,
            thought_history=self.thought_history,
            path_states=self.path_states,
            transition_history=self.transition_history,
            configuration_revision=self.configuration_revision,
            provenance=new_provenance,
        )


# =============================================================================
# DEFAULT NETWORK TRANSITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkTransition:
    """
    Canonical record of a state transition.
    
    Each transition is an immutable record that captures the semantic
    change from one state to another.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-TRANS-INV-001: Transition records are immutable
        DEFAULT-TRANS-INV-002: Transition has no runtime side effects
        DEFAULT-TRANS-INV-003: Transitions enable deterministic replay
    
    PROPERTIES:
        • transition_id: Unique identifier for this transition record
        • prior_state_revision: State revision before the change
        • resulting_state_revision: State revision after the change
        
    CONTEXT:
        • request_id: Request that triggered this transition (if any)
        • episode_id: Episode being coordinated (if any)
        • path: Path that caused the transition (if any)
        
    ACTION:
        • kind: What kind of state change occurred
        • details: Detailed description of the change
        
    TIMESTAMPING:
        • occurred_at_utc: When this transition occurred
        • provenance: Transition record provenance
    
    NOT RESPONSIBLE FOR:
        • Executing side effects (state is immutable)
        • Scheduling runtime actions
    """
    
    # Identity
    transition_id: str
    """Unique identifier for this transition."""
    
    # Revision tracking
    prior_state_revision: int
    """State revision before the change."""
    
    resulting_state_revision: int
    """State revision after the change."""
    
    # Context (required - no defaults)
    request_id: str
    """Request that triggered this transition."""
    
    episode_id: str
    """Episode being coordinated."""
    
    path: str
    """Path that caused the transition."""
    
    # Action kind
    kind: str  # TransitionKind.*
    """What kind of state change occurred."""
    
    # Timestamping and provenance (required - no defaults)
    occurred_at_utc: datetime
    """When this transition occurred."""
    
    # Optional fields with defaults - must come after required fields
    details: str = ""
    """Detailed description of the change."""
    
    affected_references: Tuple[str, ...] = field(default_factory=tuple)
    """References affected by this transition."""
    
    provenance: Optional[DefaultNetworkStateProvenance] = None
    """Transition record provenance."""
    
    @classmethod
    def new(
        cls,
        prior_revision: int,
        resulting_revision: int,
        kind: str,
        request_id: Optional[str] = None,
        episode_id: Optional[str] = None,
        path: Optional[str] = None,
        details: str = "",
        affected_references: Optional[Tuple[str, ...]] = None,
    ) -> DefaultNetworkTransition:
        """Create a new transition record."""
        now = datetime.utcnow()
        return cls(
            transition_id=f"transition:{hash((kind, request_id or '', episode_id or '', prior_revision)) & 0xFFFFFFFFFFFFFFFF:x}",
            prior_state_revision=prior_revision,
            resulting_state_revision=resulting_revision,
            request_id=request_id,
            episode_id=episode_id,
            path=path,
            kind=kind,
            details=details,
            affected_references=affected_references or (),
            occurred_at_utc=now,
            provenance=None,
        )


# =============================================================================
# DEFAULT NETWORK DIAGNOSTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkDiagnostics:
    """
    Canonical diagnostics record for observability.
    
    Diagnostics are advisory - they do not affect coordination logic.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-DIAG-INV-001: Diagnostics are immutable
        DEFAULT-DIAG-INV-002: Diagnostics contain no runtime references
        
    PROPERTIES:
        • request_validation_summary: Validation results for the request
        • selected_path: Which path was chosen
        • local_step_count: How many local steps were taken
        
    INPUT PROCESSING:
        • consumed_input_count: How many inputs were processed
        • rejected_input_count: How many inputs were rejected
        
    OUTPUT SUMMARY:
        • generated_thought_count: Thoughts generated
        • product_count: Products produced
        • external_request_count: External requests created
        • proposal_count: Proposals issued
        
    STATE SUMMARY:
        • transition_count: State transitions recorded
        
    CAPACITY TRACKING:
        • capacity_usage: How close to bounds the processing came
    
    OBSERVABILITY:
        • warnings: Non-fatal warnings encountered
        • determinism_metadata: Information for deterministic replay verification
        • provenance_summary: Summary of provenance tracking
    
    NOT RESPONSIBLE FOR:
        • Hidden chain-of-thought (all reasoning must be explicit)
        • Runtime performance metrics
    """
    
    # Required fields (no defaults)
    request_validation_summary: Tuple[str, ...]
    """Validation results for the request."""
    
    input_processing_summary: Tuple[str, ...]
    """Summary of input processing."""
    
    generated_thought_count: int
    """Thoughts generated."""
    
    product_count: int
    """Products produced."""
    
    external_request_count: int
    """External requests created."""
    
    proposal_count: int
    """Proposals issued."""
    
    transition_count: int
    """State transitions recorded."""
    
    warnings: Tuple[str, ...]
    """Non-fatal warnings encountered."""
    
    determinism_metadata: Dict[str, Any] = field(default_factory=dict)
    """Information for deterministic replay verification."""
    
    provenance_summary: str = ""
    """Summary of provenance tracking."""
    
    # Optional fields with defaults - must come after required fields
    selected_path: Optional[str] = None
    """Which path was chosen."""
    
    local_step_count: int = 0
    """How many local semantic steps were taken."""
    
    capacity_usage: float = 0.0
    """How close to bounds (0.0 to 1.0)."""
    
    @classmethod
    def new(cls) -> DefaultNetworkDiagnostics:
        """Create a new diagnostics record."""
        return cls(
            request_validation_summary=(),
            local_step_count=0,
            input_processing_summary=(),
            generated_thought_count=0,
            product_count=0,
            external_request_count=0,
            proposal_count=0,
            transition_count=0,
            capacity_usage=0.0,
            warnings=(),
            determinism_metadata={},
        )


# =============================================================================
# DEFAULT NETWORK OUTCOME
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkOutcome:
    """
    Canonical outcome record for one bounded semantic progression.
    
    Outcome represents the result of coordination - what was actually
    achieved during this processing cycle.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-OUTCOME-INV-001: Outcome is immutable
        DEFAULT-OUTCOME-INV-002: Outcome has no runtime implications
        
    PROPERTIES:
        • status: Overall outcome classification
        • path_outcomes: Individual path results (if composite)
        
    PRODUCTS:
        • accepted_products: Products that were successfully generated
        • rejected_products: Products that were discarded
        
    UNRESOLVED:
        • unresolved_items: Items that remain unresolved
        • missing_requirements: Requirements not met
        
    QUALITY:
        • confidence: Overall confidence in the outcome (0.0 to 1.0)
        • completeness_status: How complete the outcome is
    
    BOUNDS:
        • limitations: Any bounds that affected processing
        
    PROVENANCE:
        • provenance: Outcome record provenance
    
    NOT RESPONSIBLE FOR:
        • Scheduling continuation
        • Executing side effects
    """
    
    # Status (required - no defaults)
    status: str  # OutcomeStatus.*
    """Overall outcome classification."""
    
    path_outcomes: Tuple[str, ...]
    """Individual path results."""
    
    accepted_products: Tuple[str, ...]
    """Product IDs that were successfully generated."""
    
    rejected_products: Tuple[str, ...]
    """Product IDs that were discarded."""
    
    unresolved_items: Tuple[str, ...]
    """Items that remain unresolved."""
    
    missing_requirements: Tuple[str, ...]
    """Requirements not met."""
    
    limitations: Tuple[str, ...]
    """Bounds that affected processing."""
    
    # Quality (optional - with defaults)
    confidence: float = 0.5
    """Confidence in the outcome (0.0 to 1.0)."""
    
    completeness_status: str = "partial"
    """How complete the outcome is."""
    
    provenance: Optional[DefaultNetworkStateProvenance] = None
    """Outcome record provenance."""
    
    @classmethod
    def success(cls, accepted_products: Tuple[str, ...]) -> DefaultNetworkOutcome:
        """Create a successful outcome."""
        return cls(
            status="success",
            path_outcomes=(),
            accepted_products=accepted_products,
            rejected_products=(),
            unresolved_items=(),
            missing_requirements=(),
            confidence=0.85,
            completeness_status="complete",
            limitations=(),
        )
    
    @classmethod
    def waiting_for_external(cls) -> DefaultNetworkOutcome:
        """Create an outcome indicating external result needed."""
        return cls(
            status="waiting_for_external_result",
            path_outcomes=(),
            accepted_products=(),
            rejected_products=(),
            unresolved_items=(),
            missing_requirements=("external_capability_result",),
            confidence=0.5,
            completeness_status="partial",
            limitations=(),
        )
    
    @classmethod
    def failed(cls, reason: str) -> DefaultNetworkOutcome:
        """Create a failed outcome."""
        return cls(
            status="failed",
            path_outcomes=(),
            accepted_products=(),
            rejected_products=(),
            unresolved_items=(),
            missing_requirements=(reason,),
            confidence=0.0,
            completeness_status="invalid",
            limitations=("processing_failed",),
        )


# =============================================================================
# DEFAULT NETWORK CONTINUATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkContinuation:
    """
    Canonical continuation recommendation for future coordination.
    
    Continuation is ADVISORY - it does NOT schedule or execute anything.
    It's evidence for external systems to consider when deciding what
    to do next.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-CONT-INV-001: Continuation is immutable
        DEFAULT-CONT-INV-002: Continuation has no runtime implications
        DEFAULT-CONT-INV-003: Continuation does NOT execute
        
    PROPERTIES:
        • kind: Recommended next step classification
        • recommended_purpose: Suggested purpose for next cycle
        
    EPISODE:
        • continue_episode: Whether to continue current episode
        • new_episode_required: Whether a new episode should be created
        
    EXTERNAL INTERFACE:
        • required_external_requests: External requests that must be satisfied
        
    UNRESOLVED:
        • unresolved_conditions: Conditions that still need to be met
        
    QUALITY:
        • confidence: Confidence in this recommendation (0.0 to 1.0)
        
    EXPLANATION:
        • explanation: Human-readable justification for the recommendation
        • evidence_summary: Summary of supporting evidence
    
    PROVENANCE:
        • provenance: Continuation record provenance
    
    NOT RESPONSIBLE FOR:
        • Scheduling execution
        • Creating threads or tasks
        • Waiting for external results
        • Automatically continuing coordination
    """
    
    # Required fields (no defaults)
    kind: str  # DefaultNetworkContinuationKind.*
    """Recommended next step classification."""
    
    required_external_requests: Tuple[str, ...]
    """External request IDs that must be satisfied."""
    
    unresolved_conditions: Tuple[str, ...]
    """Conditions that still need to be met."""
    
    evidence_summary: Tuple[str, ...]
    """Summary of supporting evidence."""
    
    # Optional fields with defaults - must come after required fields
    recommended_purpose: Optional[str] = None
    """Suggested purpose for next cycle."""
    
    recommended_path: Optional[str] = None
    """Suggested path for next cycle."""
    
    continue_episode: bool = False
    """Whether to continue current episode."""
    
    new_episode_required: bool = False
    """Whether a new episode should be created."""
    
    confidence: float = 0.5
    """Confidence in this recommendation (0.0 to 1.0)."""
    
    explanation: str = ""
    """Human-readable justification for the recommendation."""
    
    provenance: Optional[DefaultNetworkStateProvenance] = None
    """Continuation record provenance."""
    
    @classmethod
    def complete(cls) -> DefaultNetworkContinuation:
        """Create a continuation indicating completion."""
        return cls(
            kind="complete",
            required_external_requests=(),
            unresolved_conditions=(),
            confidence=1.0,
            explanation="Current episode completed successfully.",
            evidence_summary=("Outcome reached terminal state",),
        )
    
    @classmethod
    def request_external_result(cls, external_request_id: str) -> DefaultNetworkContinuation:
        """Create a continuation indicating an external result is needed."""
        return cls(
            kind="request_external_result",
            required_external_requests=(external_request_id,),
            unresolved_conditions=(),
            confidence=0.8,
            explanation="External capability result required to proceed.",
            evidence_summary=("External result not yet supplied",),
        )
    
    @classmethod
    def continue_current(cls, purpose: str) -> DefaultNetworkContinuation:
        """Create a continuation indicating the current episode should continue."""
        return cls(
            kind="continue_current_episode",
            recommended_purpose=purpose,
            continue_episode=True,
            required_external_requests=(),
            unresolved_conditions=(),
            confidence=0.75,
            explanation="Current episode has uncompleted work.",
            evidence_summary=("Episode not in terminal state",),
        )
    
    @classmethod
    def fail(cls, reason: str) -> DefaultNetworkContinuation:
        """Create a continuation indicating failure."""
        return cls(
            kind="fail",
            required_external_requests=(),
            unresolved_conditions=(reason,),
            confidence=0.0,
            explanation=f"Processing failed: {reason}",
            evidence_summary=("Irrecoverable condition",),
        )


# =============================================================================
# STATE TRANSITION RECORD
# =============================================================================

StateTransitionRecord = DefaultNetworkTransition
"""
Type alias for state transition records.
    
This preserves the semantic contract of transitions across versions.
"""
