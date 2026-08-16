# Gordon Workspace Network - Broadcast Construction Semantics
# ==============================================================
#
# Phase 4.6.6: Workspace Broadcast Construction
#
# Canonical implementation of semantic broadcast construction artifacts.
#
# ARCHITECTURAL PURPOSE:
# ----------------------
# This module defines the immutable, runtime-neutral semantic contracts for
# constructing Workspace Broadcasts from Selection Outcomes.
#
# BROADCAST CONSTRUCTION PIPELINE:
# ================================
#
# WorkspaceSelectionOutcome (Phase 4.6.5 output)
#     ↓
# Broadcast Request
#     ↓
# Broadcast Context
#     ↓
# Broadcast Scope
#     ↓
# Broadcast Construction
#     ↓
# Broadcast Validation
#     ↓
# WorkspaceBroadcast (canonical product)
#
# CONSTRUCTION ENDS HERE.
# No delivery, messaging, IPC, execution, or scheduling.
#
# ARCHITECTURAL INVARIANTS:
# -------------------------
# BC-INV-001: Broadcast is immutable (frozen dataclasses)
# BC-INV-002: Broadcast never owns Candidate content (only references)
# BC-INV-003: Broadcast never performs runtime transport
# BC-INV-004: Broadcast preserves provenance from Selection Outcome
# BC-INV-005: Replay produces identical Broadcast artifacts
# BC-INV-006: No runtime time acquisition in broadcast semantics
# BC-INV-007: External identity providers only (no internal UUIDs)
# BC-INV-008: All collections are bounded and deeply immutable

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum

# =============================================================================
# IDENTITY TYPES - Immutable references
# =============================================================================

WorkspaceBroadcastIdentity = str
"""
Unique identifier for a workspace broadcast instance.

Rules:
    - Deterministically derived or externally supplied
    - Replayable (same input produces same output)
    - Never generated internally (no UUIDs, timestamps)

Examples: Content hash with prefix, source system ID with context.
"""

WorkspaceBroadcastRevision = int
"""
Monotonically increasing revision number for broadcasts.

Revision rules:
    - Revision 1 is initial creation
    - Each semantic change requires a new revision
    - Identity + Revision = unique artifact reference

No in-place mutation allowed. Create new revision instead.
"""

WorkspaceBroadcastReference = str
"""
Immutable reference to Workspace Broadcast.

Format: "identity@revision"
Examples:
    "broadcast_abc123@1"
    "selection_result_xyz@3"

Used for linking without ownership.
"""


# =============================================================================
# BROADCAST REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastRequest:
    """
    Immutable request to construct a broadcast from Selection Outcome.

    The request carries the semantic intent for broadcast construction
    without performing any runtime operations.
    """

    identity: str
    """Unique identifier for this broadcast request."""

    revision: int
    """Revision number for this request."""

    selection_outcome_ref: str
    """
    Reference to the WorkspaceSelectionOutcome that is the source of
    this broadcast construction.
    """

    context_ref: str = ""
    """Reference to additional context for broadcast construction."""

    scope_ref: str = ""
    """Reference to scope specification."""

    semantic_time_ref: str = "semantic_time_origin"
    """
    Reference to semantic time anchor. Never uses runtime time.
    """

    authority_ref: str = ""
    """Reference to authority that authorized this broadcast."""

    provenance_ref: str = ""
    """Reference to provenance trail for this request."""


# =============================================================================
# BROADCAST CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastContext:
    """
    Immutable context accompanying a broadcast.

    Context provides semantic framing without embedding runtime objects.
    It describes the circumstances and conditions surrounding a broadcast.
    """

    # Source information
    source_network: str = ""
    """Network that originated the broadcast content."""

    source_package: str = ""
    """Package within the source network."""

    correlation_id: str = ""
    """Correlation ID for tracing across systems."""

    causation_id: Optional[str] = None
    """Causation chain reference (if applicable)."""

    # Context classification
    task_context: Optional[str] = None
    """Task-related context if applicable."""

    goal_context: Optional[str] = None
    """Goal-related context if applicable."""

    decision_context: Optional[str] = None
    """Decision-related context if applicable."""

    reasoning_context: Optional[str] = None
    """Reasoning-related context if applicable."""

    planning_context: Optional[str] = None
    """Planning-related context if applicable."""

    executive_context: Optional[str] = None
    """Executive-related context if applicable."""

    attention_context: Optional[str] = None
    """Attention-related context if applicable."""

    motivation_context: Optional[str] = None
    """Motivation-related context if applicable."""

    temporal_context: Optional[str] = None
    """Temporal-related context if applicable."""

    spatial_context: Optional[str] = None
    """Spatial-related context if applicable."""

    environmental_context: Optional[str] = None
    """Environmental-related context if applicable."""

    identity_context: Optional[str] = None
    """Identity-related context if applicable."""

    perceptual_context: Optional[str] = None
    """Perceptual-related context if applicable."""

    operational_context: Optional[str] = None
    """Operational-related context if applicable."""

    # Additional context fields
    semantic_domain: str = ""
    """Domain of semantic content (e.g., 'finance', 'healthcare')."""

    audience_type: Tuple[str, ...] = field(default_factory=tuple)
    """Types of consumers this broadcast is intended for."""

    @classmethod
    def from_selection_outcome(cls, outcome_ref: str) -> WorkspaceBroadcastContext:
        """
        Create context for a broadcast derived from Selection Outcome.

        Args:
            outcome_ref: Reference to the Selection Outcome

        Returns:
            New context with selection source information.
        """
        return cls(
            source_network="WORKSPACE_NETWORK",
            source_package="selection",
            correlation_id=f"broadcast_from_{outcome_ref}",
            executive_context="SELECTION_OUTCOME_BROADCAST",
        )


# =============================================================================
# BROADCAST SCOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastScope:
    """
    Immutable scope specification for broadcast.

    Scope defines which systems may receive and how the broadcast is processed.
    It is independent of runtime state and execution.
    """

    # Consumer scope
    target_audiences: Tuple[str, ...] = field(default_factory=tuple)
    """Audience kinds eligible to consume this broadcast."""

    minimum_confidence: float = 0.5
    """Minimum confidence threshold for consumers (0.0-1.0)."""

    broadcast_depth: int = 3
    """Maximum depth of broadcast propagation (bounded, max 10)."""

    disclosure_level: str = "internal_only"
    """Disclosure classification for the broadcast."""

    # Authority scope
    authority_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints on which authorities may process this broadcast."""

    # Privacy scope
    privacy_classification: str = "internal_only"
    """Privacy classification for disclosure control."""

    # Visibility scope
    visibility_limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Specific systems or networks that may see this broadcast."""

    # Accessibility scope
    accessibility_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for accessibility."""

    @classmethod
    def for_global_workspace(cls) -> WorkspaceBroadcastScope:
        """
        Create scope for global workspace availability.

        Returns:
            Scope suitable for broad distribution within workspace.
        """
        return cls(
            target_audiences=(
                "working_memory",
                "reasoning",
                "planning",
                "memory",
                "prediction",
            ),
            minimum_confidence=0.7,
            broadcast_depth=3,
            disclosure_level="workspace_internal",
        )


# =============================================================================
# BROADCAST VISIBILITY
# =============================================================================

class WorkspaceBroadcastVisibility(Enum):
    """
    Canonical visibility states for broadcasts.

    Visibility is semantic only - it does NOT perform delivery.
    """

    # =========================================================================
    # ACCESSIBLE STATES
    # =========================================================================

    PUBLIC = "public"
    """Available to all eligible consumers without restrictions."""

    RESTRICTED = "restricted"
    """Available only to consumers meeting specific conditions."""

    CONFIDENTIAL = "confidential"
    """Confidential access with limited distribution."""

    CLASSIFIED = "classified"
    """Highly restricted classification level."""

    # =========================================================================
    # PROTECTED STATES
    # =========================================================================

    HIDDEN = "hidden"
    """Not visible in normal discovery mechanisms."""

    DEFERRED = "deferred"
    """Visibility deferred to later time or condition."""


# =============================================================================
# BROADCAST AVAILABILITY
# =============================================================================

class WorkspaceBroadcastAvailability(Enum):
    """
    Canonical availability states for broadcasts.

    Availability is semantic - it does NOT perform runtime delivery.
    """

    # =========================================================================
    # AVAILABLE STATES
    # =========================================================================

    GLOBAL_AVAILABILITY = "global_availability"
    """Available globally to all eligible consumers."""

    CONDITIONAL_AVAILABILITY = "conditional_availability"
    """Available only when specific conditions are met."""

    # =========================================================================
    # TEMPORARY STATES
    # =========================================================================

    DEFERRED_AVAILABILITY = "deferred_availability"
    """Availability deferred to later time or condition."""

    SUSPENDED_AVAILABILITY = "suspended_availability"
    """Availability suspended temporarily."""

    WITHDRAWN_AVAILABILITY = "withdrawn_availability"
    """Withdrawn by authority (not deleted)."""

    EXPIRED_AVAILABILITY = "expired_availability"
    """Expired based on time-based conditions."""


# =============================================================================
# BROADCAST EVIDENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastEvidence:
    """
    Immutable evidence supporting broadcast construction.

    Evidence documents the basis for semantic decisions without embedding runtime state.
    """

    evidence_type: str
    """Type of evidence (e.g., 'validation', 'verification', 'corroboration')."""

    value: float
    """Strength or confidence value for this evidence."""

    source_ref: str
    """Reference to source of evidence (NOT ownership)."""

    semantic_time_ref: str = ""
    """Reference to semantic time anchor for this evidence."""


# =============================================================================
# BROADCAST JUSTIFICATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastJustification:
    """
    Immutable justification for broadcast construction decisions.

    Justification documents WHY a broadcast was constructed in a particular way.
    """

    justification_kind: str
    """Kind of justification (e.g., 'selection_criterion', 'semantic_coherence')."""

    explanation: str
    """Explanation of the justification reasoning."""

    supporting_evidence: Tuple[WorkspaceBroadcastEvidence, ...] = field(
        default_factory=tuple
    )
    """Supporting evidence for this justification."""

    confidence: float = 1.0
    """Confidence level in this justification (0.0-1.0)."""

    uncertainty: float = 0.0
    """Uncertainty level in this justification (0.0-1.0)."""


# =============================================================================
# BROADCAST CONFIDENCE AND UNCERTAINTY
# =============================================================================

WorkspaceBroadcastConfidence = float
"""
Confidence level for broadcast semantic content.

Range: 0.0 (no confidence) to 1.0 (complete confidence)
"""

WorkspaceBroadcastUncertainty = float
"""
Uncertainty level associated with broadcast semantic content.

Range: 0.0 (no uncertainty) to 1.0 (complete uncertainty)
Rules:
    - Confidence + Uncertainty ≤ 1.0
    - Independent measures of certainty
"""


# =============================================================================
# BROADCAST PAYLOAD
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastPayloadIdentity:
    """
    Identity for a broadcast payload.

    Payloads are immutable semantic projections that represent the actual
    content being broadcast.
    """

    identity: str
    """Unique identifier for this payload."""

    revision: int = 1
    """Revision number for this payload."""


WorkspaceBroadcastPayloadReference = str
"""
Immutable reference to Workspace Broadcast Payload.

Format: "payload_identity@revision"
Examples:
    "payload_abc123@1"
    "selection_summary_xyz@3"
"""


class WorkspaceBroadcastPayloadKind(Enum):
    """
    Canonical kinds of broadcast payloads.
    """

    # =========================================================================
    # SINGLETON PAYLOADS - Single candidate selection
    # =========================================================================

    SINGLETON = "singleton"
    """Single candidate selected as winner."""

    # =========================================================================
    # COALITION PAYLOADS - Multiple coordinated candidates
    # =========================================================================

    COALITION = "coalition"
    """Multiple compatible winners forming a coalition."""

    # =========================================================================
    # COMPOSITE PAYLOADS - Complex structures
    # =========================================================================

    COMPOSITE = "composite"
    """Composite structure with multiple related payloads."""

    CONTEXTUAL = "contextual"
    """Contextual payload providing background information."""

    # =========================================================================
    # SUMMARY PAYLOADS - Aggregated content
    # =========================================================================

    SELECTION_SUMMARY = "selection_summary"
    """Summary of selection outcome and reasoning."""

    COALITION_SUMMARY = "coalition_summary"
    """Summary of coalition composition and rationale."""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastPayload:
    """
    Immutable semantic projection representing broadcast content.

    Payloads reference (NOT own) source artifacts. They are immutable
    projections that preserve provenance.
    """

    identity: WorkspaceBroadcastPayloadIdentity
    """Unique identity for this payload."""

    payload_kind: WorkspaceBroadcastPayloadKind
    """Kind of payload being represented."""

    # Content references (NEVER owns content, only references)
    candidate_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to Candidates in this payload."""

    summary_text: str = ""
    """Human-readable summary of payload content."""

    # Semantic projections
    semantic_projection: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Semantic projections from source to broadcast context."""

    provenance_ref: str = ""
    """Reference to provenance trail for this payload."""

    @property
    def is_singleton(self) -> bool:
        """Check if this is a singleton payload (single candidate)."""
        return len(self.candidate_refs) == 1

    @property
    def is_coalition(self) -> bool:
        """Check if this is a coalition payload (multiple candidates)."""
        return self.payload_kind == WorkspaceBroadcastPayloadKind.COALITION and len(
            self.candidate_refs
        ) > 1

    @property
    def candidate_count(self) -> int:
        """Return count of candidates in payload."""
        return len(self.candidate_refs)


# =============================================================================
# BROADCAST PROJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastProjection:
    """
    Immutable semantic projection from source to broadcast context.

    Projections preserve the relationship between original content and
    its broadcast representation.
    """

    projection_id: str
    """Unique identifier for this projection."""

    source_ref: str
    """Reference to source artifact (NOT ownership)."""

    broadcast_ref: str
    """Reference to broadcast that contains this projection."""

    projection_kind: str
    """Kind of projection (e.g., 'semantic_equivalent', 'abstraction')."""

    semantic_preservation: Tuple[str, ...] = field(default_factory=tuple)
    """Aspects preserved in the projection."""

    contextual_adaptation: Tuple[str, ...] = field(default_factory=tuple)
    """Contextual adaptations made for broadcast."""

    provenance_ref: str = ""
    """Reference to provenance trail."""


# =============================================================================
# BROADCAST AUDIENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastAudience:
    """
    Immutable audience specification for broadcast.

    Audience defines which consumers are eligible to receive this broadcast.
    It is semantic only - does NOT perform routing or delivery.
    """

    # Intended audiences (who we want to reach)
    intended_consumers: Tuple[str, ...] = field(default_factory=tuple)
    """Target consumers for this broadcast."""

    # Eligible audiences (who meets criteria)
    eligible_consumers: Tuple[str, ...] = field(default_factory=tuple)
    """Consumers meeting all eligibility requirements."""

    # Excluded audiences (explicitly blocked)
    excluded_consumers: Tuple[str, ...] = field(default_factory=tuple)
    """Consumers explicitly excluded from receiving this broadcast."""

    # Conditional audiences (pending verification)
    conditional_consumers: Tuple[Tuple[str, str], ...] = field(
        default_factory=tuple
    )
    """
    Consumers with conditions that must be verified.
    Format: [(consumer_id, condition_ref), ...]
    """

    # Audience metadata
    audience_type: Tuple[str, ...] = field(default_factory=tuple)
    """Types of consumers (e.g., 'working_memory', 'reasoning')."""

    minimum_confidence: float = 0.5
    """Minimum confidence threshold for delivery."""

    @property
    def has_intended(self) -> bool:
        """Check if any intended consumers are specified."""
        return len(self.intended_consumers) > 0

    @property
    def has_eligible(self) -> bool:
        """Check if any eligible consumers are specified."""
        return len(self.eligible_consumers) > 0


# =============================================================================
# BROADCAST HISTORY
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastHistoryEntry:
    """
    History entry for broadcast lifecycle events.

    Each entry records a state change without embedding runtime timestamps.
    """

    entry_id: str
    """Unique identifier for this history entry."""

    entry_type: str
    """Type of event (e.g., 'creation', 'revision', 'supersession')."""

    timestamp_semantic_time: str
    """
    Semantic time reference for when this occurred.
    Never uses runtime time acquisition.
    """

    data_ref: Optional[str] = None
    """Reference to relevant data at time of event."""

    metadata: Tuple[str, ...] = field(default_factory=tuple)
    """Additional metadata about this entry."""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastHistory:
    """
    Immutable history record for a broadcast.

    History preserves the complete lifecycle of a broadcast from creation
    through any revisions and eventual invalidation.
    """

    identity: str
    """Identity of the broadcast being recorded."""

    revision: int
    """Current revision of this history record."""

    broadcast_ref: str
    """Reference to the broadcast itself."""

    entries: Tuple[WorkspaceBroadcastHistoryEntry, ...]
    """Chronological list of historical events."""

    provenance_ref: str = ""
    """Reference to provenance trail for this history."""


# =============================================================================
# BROADCAST LINEAGE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceLineageNode:
    """
    Node in a broadcast lineage graph.

    Lineage preserves the semantic relationships between artifacts.
    """

    node_id: str
    """Unique identifier for this lineage node."""

    node_kind: str
    """Kind of node (e.g., 'selection_outcome', 'broadcast', 'payload')."""

    reference: str
    """Reference to the artifact (NOT ownership)."""

    semantic_time_ref: str = ""
    """Semantic time anchor for this node."""


@dataclass(frozen=True, slots=True)
class WorkspaceLineageRelation:
    """
    Relation between lineage nodes.

    Relations capture how artifacts are semantically connected.
    """

    relation_id: str
    """Unique identifier for this relation."""

    relation_type: str
    """Type of relation (e.g., 'derives_from', 'extends', 'supersedes')."""

    source_node_id: str
    """Source node in the relationship."""

    target_node_id: str
    """Target node in the relationship."""

    metadata: Tuple[str, ...] = field(default_factory=tuple)
    """Additional metadata about this relation."""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastLineage:
    """
    Immutable lineage record for a broadcast.

    Lineage preserves relationships from Selection Outcome through
    Broadcast to Payload and referenced Candidates.
    """

    identity: str
    """Unique identifier for this lineage record."""

    revision: int
    """Current revision of this lineage record."""

    broadcast_ref: str
    """Reference to the broadcast itself."""

    nodes: Tuple[WorkspaceLineageNode, ...]
    """Nodes in the lineage graph."""

    relations: Tuple[WorkspaceLineageRelation, ...]
    """Semantic relationships between nodes."""

    provenance_ref: str = ""
    """Reference to provenance trail."""


# =============================================================================
# BROADCAST INVALIDATION
# =============================================================================

class WorkspaceBroadcastInvalidationKind(Enum):
    """
    Canonical invalidation kinds for broadcasts.
    """

    # =========================================================================
    # SELECTION REVISION - Original selection is updated
    # =========================================================================

    SELECTION_REVISION = "selection_revision"
    """Selection Outcome has been revised."""

    # =========================================================================
    # CANDIDATE REVISION - Referenced candidates are updated
    # =========================================================================

    CANDIDATE_REVISION = "candidate_revision"
    """Referenced Candidates have been revised."""

    # =========================================================================
    # EVALUATION REVISION - Evaluation results change
    # =========================================================================

    EVALUATION_REVISION = "evaluation_revision"
    """Underlying evaluation has been revised."""

    # =========================================================================
    # POLICY REVISION - Policy constraints changed
    # =========================================================================

    POLICY_REVISION = "policy_revision"
    """Policy restrictions have been updated."""

    # =========================================================================
    # SECURITY REVISION - Security classification changes
    # =========================================================================

    SECURITY_REVISION = "security_revision"
    """Security classification has been modified."""

    # =========================================================================
    # CONTEXT REVISION - Context is no longer valid
    # =========================================================================

    CONTEXT_REVISION = "context_revision"
    """Context has become invalid or outdated."""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastInvalidation:
    """
    Immutable record of broadcast invalidation.

    Invalidation represents when a broadcast is no longer considered valid,
    without deleting the artifact (preserves history).
    """

    invalidation_id: str
    """Unique identifier for this invalidation record."""

    invalidation_kind: WorkspaceBroadcastInvalidationKind
    """Kind of invalidation that occurred."""

    invalidating_ref: str
    """
    Reference to what caused the invalidation (e.g., revised Selection Outcome).
    """

    invalidated_broadcast_ref: str
    """Reference to the broadcast being invalidated."""

    reason: str
    """Explanation for why this invalidation occurred."""

    semantic_time_ref: str = ""
    """Semantic time anchor for this invalidation."""


# =============================================================================
# BROADCAST CONTINUATION
# =============================================================================

class WorkspaceBroadcastContinuationKind(Enum):
    """
    Canonical continuation kinds for broadcasts.
    """

    # =========================================================================
    # PROCEED TO DISTRIBUTION - Continue to Phase 4.6.7
    # =========================================================================

    PROCEED_TO_DISTRIBUTION = "proceed_to_distribution"
    """Proceed to distribution phase (runtime delivery)."""

    # =========================================================================
    # SUSPEND BROADCAST - Temporarily halt processing
    # =========================================================================

    SUSPEND_BROADCAST = "suspend_broadcast"
    """Suspend broadcast until conditions are met."""

    # =========================================================================
    # WITHDRAW BROADCAST - Permanently remove from circulation
    # =========================================================================

    WITHDRAW_BROADCAST = "withdraw_broadcast"
    """Withdraw broadcast (not delete, preserve history)."""

    # =========================================================================
    # REBUILD BROADCAST - Reconstruct from source
    # =========================================================================

    REBUILD_BROADCAST = "rebuild_broadcast"
    """Rebuild broadcast from Selection Outcome."""

    # =========================================================================
    # REPLAY BROADCAST - Recreate identical instance
    # =========================================================================

    REPLAY_BROADCAST = "replay_broadcast"
    """Recreate an identical broadcast (deterministic replay)."""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastContinuation:
    """
    Immutable record of a semantic continuation request.

    Continuation represents a decision about what to do next with the
    broadcast, without performing any runtime operations.
    """

    continuation_id: str
    """Unique identifier for this continuation request."""

    continuation_kind: WorkspaceBroadcastContinuationKind
    """Kind of continuation requested."""

    target_ref: Optional[str] = None
    """
    Reference to target artifact (if applicable).
    For example, Distribution Request when proceeding to distribution.
    """

    reason: str = ""
    """Explanation for why this continuation was requested."""

    semantic_time_ref: str = ""
    """Semantic time anchor for this continuation."""


# =============================================================================
# MAIN ARTIFACT: BROADCAST
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcast:
    """
    Immutable canonical semantic artifact representing a broadcast.

    This is the primary product of Phase 4.6.6 - the complete semantic
    representation of what becomes globally available, without any runtime
    transport or delivery semantics.

    ARCHITECTURAL INVARIANTS:
        WB-INV-001: Broadcast references Selection Outcome (ownership preserved)
        WB-INV-002: Broadcast never owns Candidate content (only references)
        WB-INV-003: Broadcast is deeply immutable (frozen dataclass)
        WB-INV-004: Replay produces identical broadcast instances
        WB-INV-005: No runtime time acquisition in broadcast semantics
        WB-INV-006: Provenance preserved from Selection Outcome through to Broadcast

    BROADCAST PURPOSE:
        - What information is globally available?
        - What semantic artifacts compose the broadcast?
        - What is their authoritative meaning?
        - What context accompanies the broadcast?

    BROADCAST DOES NOT ANSWER:
        - Who receives it? (Audience is semantic only)
        - When is it delivered? (Runtime delivery belongs to Phase 4.6.7)
        - How is it transported? (Runtime transport not in scope)
        - Which thread executes it? (Runtime execution not in scope)
        - Whether delivery succeeds? (Delivery validation not in scope)
    """

    # Identity and metadata (required fields first)
    identity: str
    """Unique identifier for this broadcast."""

    revision: int
    """Current revision of this broadcast."""

    selection_outcome_ref: str
    """
    Reference to the Selection Outcome that produced this broadcast.

    CRITICAL: This is ONLY a reference. The Broadcast does NOT own
    the Selection Outcome. It preserves provenance without ownership.
    """

    payload: WorkspaceBroadcastPayload
    """The canonical payload being made globally available."""

    # Optional fields with defaults (must come after required fields)
    broadcast_ref: WorkspaceBroadcastReference = ""
    """
    Reference to self in format "identity@revision".
    Computed from identity and revision.
    """

    context: WorkspaceBroadcastContext = field(default_factory=lambda: WorkspaceBroadcastContext())
    """Semantic context accompanying the broadcast."""

    scope: WorkspaceBroadcastScope = field(default_factory=WorkspaceBroadcastScope.for_global_workspace)
    """Semantic scope specification for the broadcast."""

    audience: WorkspaceBroadcastAudience = field(default_factory=WorkspaceBroadcastAudience)
    """
    Semantic audience specification.

    This defines WHO may receive, not HOW or WHEN delivery occurs.
    """

    visibility: WorkspaceBroadcastVisibility = WorkspaceBroadcastVisibility.PUBLIC
    """Semantic visibility state."""

    availability: WorkspaceBroadcastAvailability = (
        WorkspaceBroadcastAvailability.GLOBAL_AVAILABILITY
    )
    """Semantic availability state."""

    confidence: WorkspaceBroadcastConfidence = 1.0
    """Confidence level in broadcast content (0.0-1.0)."""

    uncertainty: WorkspaceBroadcastUncertainty = 0.0
    """Uncertainty level in broadcast content (0.0-1.0)."""

    evidence: Tuple[WorkspaceBroadcastEvidence, ...] = field(default_factory=tuple)
    """Supporting evidence for the broadcast."""

    justification: Optional[WorkspaceBroadcastJustification] = None
    """Justification for broadcast construction decisions."""

    projections: Tuple[WorkspaceBroadcastProjection, ...] = field(
        default_factory=tuple
    )
    """Projections preserving relationships to source artifacts."""

    history: Optional[WorkspaceBroadcastHistory] = None
    """
    Immutable history record for this broadcast.

    If present, preserves complete lifecycle from creation through revisions.
    """

    lineage: Optional[WorkspaceBroadcastLineage] = None
    """
    Immutable lineage record preserving relationships from Selection Outcome
    through to Payload and referenced Candidates.
    """

    invalidation: Optional[WorkspaceBroadcastInvalidation] = None
    """
    Record of any invalidation event for this broadcast.

    If None, the broadcast is currently valid. If present, shows what
    caused the broadcast to be invalidated (preserves history).
    """

    continuation: Optional[WorkspaceBroadcastContinuation] = None
    """
    Record of any continuation request for this broadcast.

    This represents a decision about next steps without performing runtime work.
    """

    provenance_ref: str = ""
    """Reference to complete provenance trail."""

    # Derived properties
    @property
    def is_singleton(self) -> bool:
        """Check if this broadcast contains a single payload."""
        return self.payload.is_singleton

    @property
    def is_coalition(self) -> bool:
        """Check if this broadcast contains a coalition of payloads."""
        return self.payload.is_coalition

    @property
    def candidate_count(self) -> int:
        """Return count of candidates referenced in broadcast."""
        return self.payload.candidate_count

    # Validation helpers (no mutation, no side effects)
    def is_valid_for_audience(self, audience_id: str) -> bool:
        """
        Check if this broadcast is valid for a specific audience.

        This is semantic validation only - NOT runtime delivery.

        Args:
            audience_id: The audience identifier to check

        Returns:
            True if this broadcast is semantically valid for the audience
        """
        # Check exclusion list
        if audience_id in self.audience.excluded_consumers:
            return False

        # Check eligibility (if specified)
        if (
            self.audience.eligible_consumers
            and audience_id not in self.audience.eligible_consumers
        ):
            return False

        # Check confidence threshold
        if self.confidence < self.scope.minimum_confidence:
            return False

        # Broadcast is valid for this audience
        return True

    def with_continuation(
        self, continuation: WorkspaceBroadcastContinuation
    ) -> "WorkspaceBroadcast":
        """
        Create a new broadcast instance with updated continuation.

        This preserves immutability by returning a new instance.

        Args:
            continuation: The continuation request to add

        Returns:
            New broadcast instance with the continuation set
        """
        return dataclasses.replace(self, continuation=continuation)

    def with_invalidation(
        self, invalidation: WorkspaceBroadcastInvalidation
    ) -> "WorkspaceBroadcast":
        """
        Create a new broadcast instance marked as invalidated.

        This preserves immutability by returning a new instance.

        Args:
            invalidation: The invalidation record to add

        Returns:
            New broadcast instance with the invalidation set
        """
        return dataclasses.replace(self, invalidation=invalidation)


# =============================================================================
# ARCHITECTURAL LAWS
# =============================================================================

ARCHITECTURAL_LAWS = """
BROADCAST CONSTRUCTION CONSUMERS:
    - Broadcast consumes Selection Outcome references
    - Broadcast never mutates Selection Outcome
    - Broadcast never owns Content (only references)
    - Broadcast never creates runtime state

BROADCAST PRODUCERS:
    - Broadcast produces canonical semantic artifacts
    - Broadcast preserves provenance from source through output
    - Broadcast enables global cognitive availability

RUNTIME BOUNDARY:
    - Broadcast never performs delivery (runtime transport)
    - Broadcast never executes actions
    - Broadcast never schedules tasks
    - Broadcast never transports messages

SEMANTIC INVARIANTS:
    - Broadcast preserves ownership (references only, no ownership transfer)
    - Broadcast preserves provenance (semantic history maintained)
    - Broadcast is deterministic (same input = same output)
    - Broadcast is replayable (no runtime time acquisition)

AUDIENCE SEMANTICS:
    - Audience defines who MAY receive (not who DOES receive)
    - Audience never performs routing (runtime does)
    - Audience is always semantic, never operational

VISIBILITY AND AVAILABILITY:
    - Visibility and availability are semantic states
    - They do NOT control runtime delivery
    - They define what IS available, not when it IS delivered
"""

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Identity types
    "WorkspaceBroadcastIdentity",
    "WorkspaceBroadcastRevision",
    "WorkspaceBroadcastReference",
    "WorkspaceBroadcastPayloadIdentity",
    "WorkspaceBroadcastPayloadReference",

    # Request and context
    "WorkspaceBroadcastRequest",
    "WorkspaceBroadcastContext",
    "WorkspaceBroadcastScope",

    # Payload types
    "WorkspaceBroadcastPayloadKind",
    "WorkspaceBroadcastPayload",
    "WorkspaceBroadcastProjection",

    # Audience, visibility, availability
    "WorkspaceBroadcastAudience",
    "WorkspaceBroadcastVisibility",
    "WorkspaceBroadcastAvailability",

    # Evidence and justification
    "WorkspaceBroadcastEvidence",
    "WorkspaceBroadcastJustification",

    # Confidence and uncertainty
    "WorkspaceBroadcastConfidence",
    "WorkspaceBroadcastUncertainty",

    # History, lineage, invalidation, continuation
    "WorkspaceBroadcastHistoryEntry",
    "WorkspaceBroadcastHistory",
    "WorkspaceLineageNode",
    "WorkspaceLineageRelation",
    "WorkspaceBroadcastLineage",
    "WorkspaceBroadcastInvalidationKind",
    "WorkspaceBroadcastInvalidation",
    "WorkspaceBroadcastContinuationKind",
    "WorkspaceBroadcastContinuation",

    # Main artifact
    "WorkspaceBroadcast",
]