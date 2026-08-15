# Gordon Workspace Network - Broadcast Distribution Semantics
# =============================================================
#
# Phase 4.6.7: Workspace Broadcast Distribution and Target Coordination
#
# Canonical implementation of semantic distribution artifacts for Workspace Broadcasts.
#
# ARCHITECTURAL PURPOSE:
# ----------------------
# This module defines the immutable, runtime-neutral semantic contracts for
# distributing canonical Workspace Broadcasts to externally owned cognitive consumers.
#
# DISTRIBUTION PIPELINE:
# ======================
#
# WorkspaceBroadcast (Phase 4.6.6 output)
#     ↓
# Distribution Request
#     ↓
# Target Eligibility Assessment
#     ↓
# Target-Specific Disclosure Projection
#     ↓
# Delivery Projection
#     ↓
# Runtime delivery (external to this module)
#     ↓
# Acknowledgement receipt (external to this module)
#     ↓
# Distribution Outcome
#
# DISTRIBUTION ENDS HERE.
# No runtime transport, messaging, IPC, scheduling, or execution.
#
# ARCHITECTURAL INVARIANTS:
# -------------------------
# DIST-INV-001: Distribution is semantic coordination only - not runtime transport
# DIST-INV-002: Every distribution request references one exact Broadcast revision
# DIST-INV-003: Target projections never exceed Broadcast scope
# DIST-INV-004: Distribution uses least disclosure sufficient for purpose
# DIST-INV-005: All public distribution artifacts are deeply immutable
# DIST-INV-006: No runtime time acquisition or internal identity generation
# DIST-INV-007: Equivalent inputs produce equivalent outputs (deterministic)
# DIST-INV-008: Fan-out and fan-in are explicitly bounded
# DIST-INV-009: Correlation preserves exact references through the pipeline
# DIST-INV-010: Workspace State mutation occurs only through typed Delta proposals


from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from enum import Enum


# =============================================================================
# IDENTITY TYPES - Immutable references
# =============================================================================

WorkspaceBroadcastDistributionIdentity = str
"""
Unique identifier for a workspace broadcast distribution instance.

Rules:
    - Deterministically derived or externally supplied
    - Replayable (same input produces same output)
    - Never generated internally (no UUIDs, timestamps)
"""

WorkspaceBroadcastDistributionRevision = int
"""
Monotonically increasing revision number for distributions.

Revision rules:
    - Revision 1 is initial creation
    - Each semantic change requires a new revision
    - Identity + Revision = unique artifact reference

No in-place mutation allowed. Create new revision instead.
"""

WorkspaceBroadcastDistributionReference = str
"""
Immutable reference to Workspace Broadcast Distribution.

Format: "identity@revision"
Examples:
    "distribution_abc123@1"
    "broadcast_delivery_xyz@3"

Used for linking without ownership.
"""


# =============================================================================
# DISTRIBUTION REQUEST
# =============================================================================

class WorkspaceBroadcastDistributionPurpose(Enum):
    """
    Canonical distribution purposes for broadcasts.
    
    Purpose defines intended semantic use. It does not grant target-processing
    authority.
    """
    
    # Global availability to all eligible consumers
    GLOBAL_COGNITIVE_AVAILABILITY = "global_cognitive_availability"
    
    # Targeted availability to specific consumers
    TARGETED_COGNITIVE_AVAILABILITY = "targeted_cognitive_availability"
    
    # Working Memory context projection
    WORKING_MEMORY_CONTEXT_PROJECTION = "working_memory_context_projection"
    
    # Memory encoding eligibility projection
    MEMORY_ENCODING_ELIGIBILITY_PROJECTION = "memory_encoding_eligibility_projection"
    
    # Executive context projection
    EXECUTIVE_CONTEXT_PROJECTION = "executive_context_projection"
    
    # Decision context projection
    DECISION_CONTEXT_PROJECTION = "decision_context_projection"
    
    # Attention context projection
    ATTENTION_CONTEXT_PROJECTION = "attention_context_projection"
    
    # Alerting context projection
    ALERT_CONTEXT_PROJECTION = "alert_context_projection"
    
    # Focus context projection
    FOCUS_CONTEXT_PROJECTION = "focus_context_projection"
    
    # Motivation context projection
    MOTIVATION_CONTEXT_PROJECTION = "motivation_context_projection"
    
    # Reasoning context projection
    REASONING_CONTEXT_PROJECTION = "reasoning_context_projection"
    
    # Planning context projection
    PLANNING_CONTEXT_PROJECTION = "planning_context_projection"
    
    # Perception context projection
    PERCEPTION_CONTEXT_PROJECTION = "perception_context_projection"
    
    # Learning context projection
    LEARNING_CONTEXT_PROJECTION = "learning_context_projection"
    
    # Prediction context projection
    PREDICTION_CONTEXT_PROJECTION = "prediction_context_projection"
    
    # World model context projection
    WORLD_MODEL_CONTEXT_PROJECTION = "world_model_context_projection"
    
    # Identity context projection
    IDENTITY_CONTEXT_PROJECTION = "identity_context_projection"
    
    # Monitoring context projection
    MONITORING_CONTEXT_PROJECTION = "monitoring_context_projection"
    
    # Recovery context projection
    RECOVERY_CONTEXT_PROJECTION = "recovery_context_projection"
    
    # Audit projection
    AUDIT_PROJECTION = "audit_projection"
    
    # User visibility projection
    USER_VISIBILITY_PROJECTION = "user_visibility_projection"
    
    # General purpose (default)
    GENERAL = "general"
    
    # Unknown purpose
    UNKNOWN = "unknown"


class WorkspaceBroadcastDistributionScope(Enum):
    """
    Canonical distribution scope dimensions for broadcasts.
    
    Scope defines the boundaries of what may be distributed. Distribution
    must not silently broaden Broadcast scope.
    """
    
    BROADCAST_SCOPE = "broadcast_scope"
    CONTENT_SCOPE = "content_scope"
    CANDIDATE_SCOPE = "candidate_scope"
    COALITION_SCOPE = "coalition_scope"
    CONSUMER_SCOPE = "consumer_scope"
    TARGET_SUBSET = "target_subset"
    NETWORK_SUBSET = "network_subset"
    CAPABILITY_SUBSET = "capability_subset"
    PRIVACY_SCOPE = "privacy_scope"
    DISCLOSURE_SCOPE = "disclosure_scope"
    POLICY_SCOPE = "policy_scope"
    SECURITY_SCOPE = "security_scope"
    AUTHORITY_SCOPE = "authority_scope"
    TEMPORAL_SCOPE = "temporal_scope"
    ACKNOWLEDGEMENT_SCOPE = "acknowledgement_scope"
    EVIDENCE_SCOPE = "evidence_scope"
    CONTEXT_SCOPE = "context_scope"
    FAN_OUT_BOUND = "fan_out_bound"
    PROJECTION_SIZE_BOUND = "projection_size_bound"


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionAuthorityRequirement:
    """
    Immutable requirement for distribution authority.
    
    Authority requirements define what must be present for a distribution
    to be considered valid from an authorization perspective.
    """
    
    requirement_kind: str
    """Kind of authority requirement."""
    
    required_value: str
    """Value that must be present."""
    
    strict: bool = False
    """Whether the requirement is strict (must be present) or advisory."""


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionAuthority:
    """
    Immutable authority context for distribution.
    
    Distribution authority may cover construction of distribution requests,
    selection of eligible targets, creation of target projections, application
    of disclosure policy, requiring/accepting acknowledgements, recording
    rejections, invalidating distributions, and proposing Workspace State Deltas.
    
    Authority does NOT imply ownership of the Broadcast Content or authority to
    modify source Content, target State, Policy, Security, Working Memory write,
    memory encoding, Decision, or Execution.
    """
    
    authority_id: str
    """Unique identifier for this authority context."""
    
    authority_kind: str
    """Kind of authority (e.g., 'workspace_admin', 'broadcast_publisher')."""
    
    issued_at_semantic_time: str
    """Semantic time reference when authority was issued."""
    
    expires_at_semantic_time: Optional[str] = None
    """Semantic time reference when authority expires (if applicable)."""
    
    constraints: Tuple[WorkspaceDistributionAuthorityRequirement, ...] = field(
        default_factory=tuple
    )
    """Additional constraints on this authority."""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Scope of what this authority permits."""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionRequest:
    """
    Immutable request to distribute a broadcast to eligible targets.
    
    The request carries the semantic intent for distribution without performing
    any runtime operations. It specifies which consumers may receive what
    projections under what conditions.
    """
    
    identity: str
    """Unique identifier for this distribution request."""
    
    revision: int
    """Revision number for this request."""
    
    broadcast_ref: str
    """
    Reference to the WorkspaceBroadcast that is the source of this distribution.
    
    CRITICAL: This is ONLY a reference. The Request does NOT own the Broadcast.
    It preserves provenance without ownership.
    """
    
    purpose: WorkspaceBroadcastDistributionPurpose
    """Intended semantic use for the distributed content."""
    
    scope: Tuple[WorkspaceBroadcastDistributionScope, ...] = field(default_factory=tuple)
    """Dimensions of distribution scope."""
    
    targets: Tuple[str, ...]
    """References to target consumers eligible to receive this distribution."""
    
    requirements: Tuple[WorkspaceDistributionRequirement, ...] = field(
        default_factory=tuple
    )
    """Semantic delivery requirements for this distribution."""
    
    constraints: Tuple[WorkspaceDistributionConstraint, ...] = field(
        default_factory=tuple
    )
    """Delivery constraints applied to this distribution."""
    
    authority: WorkspaceDistributionAuthority
    """Authority context permitting this distribution."""
    
    disclosure_policy: WorkspaceDistributionDisclosurePolicy
    """Disclosure policy governing what may be disclosed to whom."""
    
    correlation_ref: str = ""
    """
    Reference to correlation context for tracing across systems.
    
    Correlation must connect:
        Broadcast → Distribution Request → Target Projection → 
        Delivery Projection → Acknowledgement → Outcome
    
    It must not be inferred from arrival order.
    """
    
    causation_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to causal predecessors in the distribution lineage."""
    
    acknowledgement_policy: WorkspaceAcknowledgementPolicy
    """Policy defining what acknowledgements are required."""
    
    expiration_semantic_time: Optional[str] = None
    """Semantic time reference when this distribution expires (if applicable)."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """
    Reference to semantic time anchor. Never uses runtime time.
    """
    
    privacy: WorkspacePrivacy = field(default_factory=lambda: WorkspacePrivacy())
    """Privacy classification for this distribution."""
    
    provenance_ref: str = ""
    """Reference to provenance trail for this request."""


# =============================================================================
# TARGET SEMANTICS
# =============================================================================

class WorkspaceBroadcastTargetKind(Enum):
    """
    Canonical kinds of broadcast targets (external consumers).
    
    A target reference identifies an externally owned semantic consumer.
    It must NOT contain a live target object, service address, network endpoint,
    runtime process, callback, function, coroutine, queue, thread, or credential.
    """
    
    # Core cognitive networks
    EXECUTIVE_NETWORK = "executive_network"
    DECISION_NETWORK = "decision_network"
    ATTENTION_NETWORK = "attention_network"
    ALERTING_NETWORK = "alerting_network"
    FOCUSING_NETWORK = "focusing_network"
    DEFAULT_NETWORK = "default_network"
    MOTIVATION_NETWORK = "motivation_network"
    
    # Working Memory
    WORKING_MEMORY = "working_memory"
    
    # Capability subsystems
    MEMORY_CAPABILITY = "memory_capability"
    REASONING_CAPABILITY = "reasoning_capability"
    PLANNING_CAPABILITY = "planning_capability"
    PERCEPTION_CAPABILITY = "perception_capability"
    PREDICTION_CAPABILITY = "prediction_capability"
    WORLD_MODEL_CAPABILITY = "world_model_capability"
    LEARNING_CAPABILITY = "learning_capability"
    CREATIVITY_CAPABILITY = "creativity_capability"
    IMAGINATION_CAPABILITY = "imagination_capability"
    IDENTITY_CAPABILITY = "identity_capability"
    MONITORING_CAPABILITY = "monitoring_capability"
    RECOVERY_CAPABILITY = "recovery_capability"
    ACTION_CAPABILITY = "action_capability"
    
    # External interfaces
    USER_INTERFACE = "user_interface"
    AUDIT = "audit"
    EXTERNAL_AUTHORITY = "external_authority"
    
    # General / unspecified
    GENERAL = "general"
    UNKNOWN = "unknown"


class WorkspaceBroadcastTargetEligibilityStatus(Enum):
    """
    Canonical eligibility statuses for targets.
    
    Eligibility must consider:
        - Broadcast scope
        - Audience/target kind
        - Target capability projection
        - Privacy
        - Policy
        - Security
        - Disclosure
        - Content compatibility
        - Projection-size limits
        - Acknowledgement requirements
        - Target availability
    
    Eligibility does NOT perform runtime discovery.
    """
    
    ELIGIBLE = "eligible"
    ELIGIBLE_WITH_CONDITIONS = "eligible_with_conditions"
    PARTIALLY_ELIGIBLE = "partially_eligible"
    DEFERRED = "deferred"
    RESTRICTED = "restricted"
    POLICY_RESTRICTED = "policy_restricted"
    SECURITY_RESTRICTED = "security_restricted"
    PRIVACY_RESTRICTED = "privacy_restricted"
    UNSUPPORTED_CONTENT = "unsupported_content"
    UNSUPPORTED_PROJECTION = "unsupported_projection"
    STALE_TARGET = "stale_target"
    TARGET_UNAVAILABLE = "target_unavailable"
    TARGET_INVALID = "target_invalid"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class WorkspaceBroadcastTargetAvailabilityStatus(Enum):
    """
    Canonical availability statuses for targets.
    
    Availability must be externally supplied. The semantic distribution
    package must NOT:
        - Ping targets
        - Poll targets
        - Open connections
        - Inspect runtime processes
        - Retry discovery
    """
    
    AVAILABLE = "available"
    AVAILABLE_WITH_LIMITATIONS = "available_with_limitations"
    DEGRADED = "degraded"
    BUSY = "busy"
    DEFERRED = "deferred"
    SUSPENDED = "suspended"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastTargetEligibility:
    """
    Immutable eligibility assessment for a target.
    
    This is the semantic distribution package's assessment of whether a
    target may receive a broadcast projection. It does NOT perform runtime
    connectivity checks.
    """
    
    target_ref: str
    """Reference to the target being assessed."""
    
    status: WorkspaceBroadcastTargetEligibilityStatus
    """Eligibility status result."""
    
    reason: str = ""
    """Explanation for eligibility decision (if applicable)."""
    
    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met (for ELIGIBLE_WITH_CONDITIONS)."""
    
    assessed_at_semantic_time: str = "semantic_time_origin"
    """Semantic time reference when eligibility was assessed."""
    
    @property
    def is_eligible(self) -> bool:
        """Check if target is fully eligible."""
        return self.status == WorkspaceBroadcastTargetEligibilityStatus.ELIGIBLE
    
    @property
    def has_conditions(self) -> bool:
        """Check if there are conditions to satisfy."""
        return len(self.conditions) > 0


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastTargetAvailability:
    """
    Immutable availability assessment for a target.
    
    This is externally supplied information about whether a target is
    currently available to receive broadcasts. It does NOT perform runtime
    discovery itself.
    """
    
    target_ref: str
    """Reference to the target being assessed."""
    
    status: WorkspaceBroadcastTargetAvailabilityStatus
    """Availability status result."""
    
    reason: str = ""
    """Explanation for availability decision (if applicable)."""
    
    last_checked_semantic_time: str = "semantic_time_origin"
    """Semantic time reference when availability was last checked."""
    
    @property
    def is_available(self) -> bool:
        """Check if target is currently available."""
        return self.status in (
            WorkspaceBroadcastTargetAvailabilityStatus.AVAILABLE,
            WorkspaceBroadcastTargetAvailabilityStatus.AVAILABLE_WITH_LIMITATIONS,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastTargetCapabilityProjection:
    """
    Immutable projection of a target's capabilities.
    
    This describes what the target can accept and process without containing
    any capability implementation. It is used to determine compatibility with
    broadcast projections.
    """
    
    target_ref: str
    """Reference to the target."""
    
    supported_projection_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Kinds of projections this target supports."""
    
    accepted_content_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Content kinds this target accepts."""
    
    accepted_disclosure_levels: Tuple[WorkspaceDistributionDisclosureLevel, ...] = field(
        default_factory=tuple
    )
    """Disclosure levels this target accepts."""
    
    max_projection_size: int = 10000
    """Maximum projection size (in bytes) this target can handle."""
    
    acknowledgement_support: bool = True
    """Whether this target supports acknowledgements."""
    
    required_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Context references required by this target."""
    
    unsupported_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that are not supported by this target."""
    
    target_revision: int = 1
    """Current revision of the target's capability specification."""
    
    is_valid: bool = True
    """Whether the target capability projection is currently valid."""
    
    expires_at_semantic_time: Optional[str] = None
    """Semantic time reference when this projection expires."""


# =============================================================================
# DISCLOSURE POLICY
# =============================================================================

class WorkspaceDistributionDisclosureLevel(Enum):
    """
    Canonical disclosure levels for projections.
    
    Distribution must follow: least disclosure sufficient for the declared purpose
    
    Disclosure must preserve:
        - Field inclusion/exclusion rules
        - Redaction requirements
        - Summarization boundaries
        - Privacy restrictions
        - Policy and Security restrictions
        - Target-specific limitations
        - Provenance preservation
    """
    
    # Reference only (identity, no content)
    REFERENCE_ONLY = "reference_only"
    
    # Minimal summary
    MINIMAL_SUMMARY = "minimal_summary"
    
    # Bounded summary with constraints
    BOUNDED_SUMMARY = "bounded_summary"
    
    # Context for target-specific processing
    TARGET_CONTEXT = "target_context"
    
    # Full projection allowed within scope
    FULL_ALLOWED_PROJECTION = "full_allowed_projection"
    
    # Restricted content
    RESTRICTED = "restricted"
    
    # Owner-only disclosure
    OWNER_ONLY = "owner_only"
    
    # Policy-restricted
    POLICY_RESTRICTED = "policy_restricted"
    
    # Security-restricted
    SECURITY_RESTRICTED = "security_restricted"
    
    # User private (maximally restricted)
    USER_PRIVATE = "user_private"
    
    # Redacted version
    REDACTED = "redacted"
    
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionFieldRule:
    """
    Immutable rule for field-level disclosure control.
    
    Field rules define which fields are included, excluded, or redacted
    in a target-specific projection.
    """
    
    field_name: str
    """Name of the field this rule applies to."""
    
    action: str  # 'include', 'exclude', 'redact'
    """Action to take for this field."""
    
    condition_ref: Optional[str] = None
    """Reference to condition that must be met (if applicable)."""
    
    redaction_mask: Optional[str] = None
    """Mask pattern for redacted fields (if applicable)."""


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionDisclosurePolicy:
    """
    Immutable disclosure policy for a distribution.
    
    The policy governs what may be disclosed to each target, including which
    fields are included, excluded, or redacted. It must follow the principle
    of least disclosure sufficient for the declared purpose.
    """
    
    policy_id: str
    """Unique identifier for this disclosure policy."""
    
    default_level: WorkspaceDistributionDisclosureLevel = (
        WorkspaceDistributionDisclosureLevel.MINIMAL_SUMMARY
    )
    """Default disclosure level when none specified."""
    
    field_rules: Tuple[WorkspaceDistributionFieldRule, ...] = field(
        default_factory=tuple
    )
    """Field-level disclosure rules."""
    
    target_specific_levels: Tuple[Tuple[str, WorkspaceDistributionDisclosureLevel], ...] = (
        field(default_factory=tuple)
    )
    """
    Target-specific disclosure levels.
    
    Format: [(target_ref, level), ...]
    """
    
    preserve_provenance: bool = True
    """Whether provenance must always be preserved."""
    
    @property
    def is_least_disclosure(self) -> bool:
        """
        Check if policy follows least disclosure principle.
        
        The policy should minimize disclosed fields while still serving the
        declared purpose. This is a semantic check, not an enforcement.
        """
        # Count total field rules vs excluded/limited rules
        excluded_count = sum(
            1 for r in self.field_rules if r.action in ('exclude', 'redact')
        )
        return excluded_count > len(self.field_rules) / 2 if self.field_rules else True


# =============================================================================
# PROJECTIONS
# =============================================================================

class WorkspaceBroadcastTargetProjectionKind(Enum):
    """
    Canonical kinds of target-specific projections.
    
    Projection kind does NOT imply that the target accepts or acts upon it.
    The target owns interpretation and processing decisions.
    """
    
    # Reference to source artifact (minimal disclosure)
    REFERENCE = "reference"
    
    # Summary with bounded detail
    SUMMARY = "summary"
    
    # Context for target-specific processing
    CONTEXT = "context"
    
    # Content projection (with scope-limited details)
    CONTENT_PROJECTION = "content_projection"
    
    # Coalition projection (for multi-candidate scenarios)
    COALITION_PROJECTION = "coalition_projection"
    
    # Decision support context
    DECISION_SUPPORT_PROJECTION = "decision_support_projection"
    
    # Executive context
    EXECUTIVE_CONTEXT_PROJECTION = "executive_context_projection"
    
    # Attention context
    ATTENTION_CONTEXT_PROJECTION = "attention_context_projection"
    
    # Working Memory admission projection
    WORKING_MEMORY_ADMISSION_PROJECTION = "working_memory_admission_projection"
    
    # Memory encoding eligibility projection
    MEMORY_ENCODING_ELIGIBILITY_PROJECTION = "memory_encoding_eligibility_projection"
    
    # Reasoning context
    REASONING_CONTEXT_PROJECTION = "reasoning_context_projection"
    
    # Planning context
    PLANNING_CONTEXT_PROJECTION = "planning_context_projection"
    
    # Learning feedback projection
    LEARNING_FEEDBACK_PROJECTION = "learning_feedback_projection"
    
    # Monitoring context
    MONITORING_CONTEXT_PROJECTION = "monitoring_context_projection"
    
    # Recovery context
    RECOVERY_CONTEXT_PROJECTION = "recovery_context_projection"
    
    # User visible projection (limited disclosure)
    USER_VISIBLE_PROJECTION = "user_visible_projection"
    
    # Audit trail projection
    AUDIT_PROJECTION = "audit_projection"
    
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastTargetProjectionIdentity:
    """
    Identity for a target-specific broadcast projection.
    """
    
    identity: str
    """Unique identifier for this projection."""
    
    revision: int = 1
    """Revision number for this projection."""


WorkspaceBroadcastTargetProjectionReference = str
"""
Immutable reference to Workspace Broadcast Target Projection.

Format: "projection_identity@revision"
Examples:
    "target_projection_abc123@1"
    "broadcast_to_target_xyz@3"
"""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastTargetProjection:
    """
    Immutable projection of a broadcast toward one specific target.
    
    A target projection must preserve:
        - Source Broadcast identity and revision
        - Target identity and revision
        - Distribution identity and revision
        - Projection purpose and kind
        - Included/excluded/redacted fields
        - Content references (NOT ownership)
        - Context references
        - Conditions and limitations
        - Authority context
        - Disclosure level
        - Privacy classification
        - Provenance
    
    A target projection is NOT a copy of target State. It is a semantic
    projection FROM the broadcast TO the target.
    """
    
    identity: WorkspaceBroadcastTargetProjectionIdentity
    """Unique identity for this projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    distribution_ref: str
    """Reference to Distribution Request that produced this projection."""
    
    target_ref: str
    """Reference to target consumer (NOT ownership)."""
    
    projection_kind: WorkspaceBroadcastTargetProjectionKind
    """Kind of projection being created."""
    
    # Scope specification
    included_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that are included in this projection."""
    
    excluded_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that are explicitly excluded from this projection."""
    
    redacted_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that are redacted (partially hidden) in this projection."""
    
    # Content references (NOT ownership)
    content_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to content items in this projection."""
    
    context_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to contextual information."""
    
    # Target-specific constraints
    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met by the target."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Limitations on how this projection may be used."""
    
    authority_ref: str = ""
    """Reference to authority context for this projection."""
    
    disclosure_level: WorkspaceDistributionDisclosureLevel = (
        WorkspaceDistributionDisclosureLevel.MINIMAL_SUMMARY
    )
    """Disclosure level for this target-specific projection."""
    
    privacy_class: str = "internal_only"
    """Privacy classification for this projection."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time anchor for this projection."""
    
    provenance_ref: str = ""
    """Reference to provenance trail."""
    
    @property
    def is_full_projection(self) -> bool:
        """
        Check if this is a full projection (all non-sensitive fields included).
        
        This is a semantic property - it doesn't guarantee the target can
        process all fields, only that no fields are intentionally excluded.
        """
        return (
            len(self.excluded_fields) == 0 and
            self.disclosure_level == WorkspaceDistributionDisclosureLevel.FULL_ALLOWED_PROJECTION
        )
    
    @property
    def is_reference_only(self) -> bool:
        """Check if this is a reference-only projection."""
        return (
            len(self.content_refs) == 0 and
            self.projection_kind == WorkspaceBroadcastTargetProjectionKind.REFERENCE
        )


# =============================================================================
# WORKING MEMORY PROJECTIONS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceWorkingMemoryProjection:
    """
    Immutable projection of broadcast content for Working Memory admission.
    
    Working Memory is owned by the Memory capability. The Workspace Network
    may project selected Content references, bounded summaries, contextual
    relevance, expected retention value, urgency, freshness, constraints,
    privacy, and provenance.
    
    The Workspace Network must NOT:
        - Allocate Working Memory slots
        - Evict Working Memory content
        - Insert directly into Working Memory
        - Control rehearsal or retention
        - Mutate Working Memory State
    """
    
    projection_id: str
    """Unique identifier for this working memory projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str
    """Reference to target Working Memory instance."""
    
    # Content reference (NOT ownership)
    content_ref: str = ""
    """Reference to content item for Working Memory."""
    
    summary_text: str = ""
    """Human-readable summary of bounded length."""
    
    # Relevance metrics
    expected_retention_value: float = 0.5
    """Expected value of retaining this in Working Memory (0.0-1.0)."""
    
    urgency: float = 0.0
    """Urgency of admission (0.0-1.0)."""
    
    freshness_semantic_time: str = "semantic_time_origin"
    """Semantic time reference for content freshness."""
    
    # Constraints
    expected_retention_duration: Optional[str] = None
    """Expected duration content should be retained."""
    
    priority_boost: float = 0.0
    """Priority boost for admission (if applicable)."""
    
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints on Working Memory admission."""
    
    privacy_class: str = "internal_only"
    """Privacy classification."""
    
    provenance_ref: str = ""
    """Reference to provenance trail."""
    
    @property
    def is_admissible(self) -> bool:
        """
        Check if this content appears admissible to Working Memory.
        
        This is a semantic assessment - not an admission decision.
        Working Memory owns the actual admission decision.
        """
        # Basic checks for admissibility
        return (
            self.content_ref != "" and
            len(self.summary_text) > 0 and
            self.expected_retention_value >= 0.0 and
            self.expected_retention_value <= 1.0
        )


@dataclass(frozen=True, slots=True)
class WorkspaceWorkingMemoryAdmissionProjection:
    """
    Immutable projection for Working Memory admission decision.
    
    This is what the Workspace Network projects to Working Memory when
    requesting admission of broadcast content.
    """
    
    projection_id: str
    """Unique identifier for this admission projection."""
    
    working_memory_projection_ref: str
    """Reference to the Working Memory Projection being proposed."""
    
    target_ref: str
    """Reference to target Working Memory instance."""
    
    # Admission request data
    content_ref: str = ""
    """Content reference being proposed for admission."""
    
    summary_text: str = ""
    """Summary text for Working Memory."""
    
    expected_retention_value: float = 0.5
    
    urgency: float = 0.0
    
    priority_boost: float = 0.0
    
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    
    # Request metadata
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""
    
    @property
    def is_valid_admission_request(self) -> bool:
        """
        Check if this projection represents a valid Working Memory admission request.
        
        A valid request must have content reference and summary text.
        """
        return self.content_ref != "" and len(self.summary_text) > 0


@dataclass(frozen=True, slots=True)
class WorkspaceWorkingMemoryAcknowledgement:
    """
    Immutable acknowledgement from Working Memory about a projection.
    
    Working Memory ownership means it decides whether to admit content,
    how long to retain it, when to evict it, and how to process it. This
    acknowledgement records Working Memory's semantic response, not its
    internal processing decisions.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    working_memory_projection_ref: str
    """Reference to the Working Memory Projection being acknowledged."""
    
    target_ref: str
    """Reference to source Working Memory instance."""
    
    # Acknowledgement kind
    status: WorkspaceBroadcastTargetEligibilityStatus = (
        WorkspaceBroadcastTargetEligibilityStatus.ELIGIBLE
    )
    
    admission_decision: Optional[str] = None
    """
    Decision outcome from Working Memory.
    
    Valid values:
        - "ADMITTED"
        - "ADMITTED_WITH_LIMITATIONS"
        - "DEFERRED"
        - "REJECTED_CAPACITY"
        - "REJECTED_POLICY"
        - "REJECTED_SECURITY"
        - "REJECTED_SCOPE"
        - "STALE_PROJECTION"
        - "UNSUPPORTED"
    """
    
    # Working Memory specific
    retention_duration: Optional[str] = None
    """Duration Working Memory plans to retain the content."""
    
    eviction_reason: Optional[str] = None
    """Reason for eviction (if applicable)."""
    
    constraints_applied: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints applied by Working Memory."""
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


# =============================================================================
# MEMORY ENCODING PROJECTIONS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceMemoryEncodingEligibilityProjection:
    """
    Immutable projection indicating Broadcast Content relevance for memory encoding.
    
    The Workspace Network may indicate that Broadcast Content appears relevant
    for later memory encoding. It must NOT:
        - Create episodic/semantic/autobiographical memory
        - Persist Content directly
        - Select memory consolidation policy
        - Perform encoding
        - Mutate Memory State
    
    Memory owns all encoding decisions and persistence.
    """
    
    projection_id: str
    """Unique identifier for this encoding eligibility projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    content_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to content items that may be relevant for memory encoding."""
    
    # Relevance indicators
    contextual_relevance: float = 0.5
    """How contextually relevant this content is (0.0-1.0)."""
    
    long_term_value: float = 0.5
    """Expected long-term value of encoding this content (0.0-1.0)."""
    
    competition_outcome_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to Competition outcomes that selected this content."""
    
    # Request metadata
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceMemoryEncodingAcknowledgement:
    """
    Immutable acknowledgement about memory encoding eligibility.
    
    This records Memory's semantic assessment of whether content is eligible
    for later encoding. It does NOT record encoding decisions or persistence.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    memory_encoding_projection_ref: str
    """Reference to the Memory Encoding Eligibility Projection being acknowledged."""
    
    target_ref: str
    """Reference to source Memory instance."""
    
    # Acknowledgement status
    is_eligible_for_encoding: bool = False
    
    encoding_reason: Optional[str] = None
    """Reason for eligibility decision (if applicable)."""
    
    # Future action indicators
    may_consolidate_later: bool = True
    """Whether memory may consolidate this content later."""
    
    requires_relevance_update: bool = False
    """Whether relevance should be re-evaluated."""
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


# =============================================================================
# NETWORK-SPECIFIC PROJECTIONS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceExecutiveBroadcastProjection:
    """
    Immutable projection of Broadcast content for Executive Network consumption.
    
    The projection may include:
        - Active Broadcast reference
        - Task relevance
        - Decision relevance
        - Unresolved conflict
        - Interruption significance
        - Context update
        - Limitations
        - Privacy
        - Provenance
    
    The Workspace Network must NOT:
        - Mutate Executive State
        - Create Executive Decisions
        - Create commitments
        - Assign Executive priority
        - Direct runtime control
    """
    
    projection_id: str
    """Unique identifier for this executive projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "executive_network"
    
    # Content
    task_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to tasks that may be relevant."""
    
    decision_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to decisions that may be relevant."""
    
    unresolved_conflict_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to conflicts that may need resolution."""
    
    # Significance indicators
    interruption_significance: float = 0.0
    """How much this broadcast may interrupt current work (0.0-1.0)."""
    
    context_update_value: float = 0.5
    """Value of updating Executive context with this information (0.0-1.0)."""
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    privacy_class: str = "internal_only"
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceExecutiveBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Executive Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    executive_projection_ref: str
    """Reference to the Executive Broadcast Projection being acknowledged."""
    
    target_ref: str = "executive_network"
    
    # Acknowledgement status
    received: bool = True
    
    context_updated: Optional[str] = None
    """Context update result (if applicable)."""
    
    priority_adjusted: bool = False
    """Whether Executive priority was adjusted."""
    
    conflict_assessed_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Conflicts that were assessed as a result of this broadcast."""
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceDecisionBroadcastProjection:
    """
    Immutable projection of Broadcast content for Decision Network consumption.
    
    The projection may support:
        - Candidate generation context
        - Action Evaluation context
        - Decision review
        - Selected-Action invalidation context
        - Evidence
        - Uncertainty
        - Current global context
    
    A Workspace Broadcast is NOT automatically an ActionSelectionRequest.
    The Decision Network owns interpretation and admission.
    """
    
    projection_id: str
    """Unique identifier for this decision projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "decision_network"
    
    # Context
    candidate_generation_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    action_evaluation_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    decision_review_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    selected_action_invalidation_context_refs: Tuple[str, ...] = field(
        default_factory=tuple
    )
    
    # Evidence and uncertainty
    evidence_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    current_uncertainty: float = 0.5
    
    global_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceDecisionBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Decision Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    decision_projection_ref: str
    """Reference to the Decision Broadcast Projection being acknowledged."""
    
    target_ref: str = "decision_network"
    
    # Acknowledgement status
    received: bool = True
    
    context_integrated: bool = False
    """Whether context was integrated into Decision Network state."""
    
    decision_impact_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Decisions that may be impacted by this broadcast."""
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceAttentionBroadcastProjection:
    """
    Immutable projection of Broadcast content for Attention Network consumption.
    
    The projection may expose:
        - Globally available Content
        - Interruption relevance
        - Focus conflict
        - Attentional demand
        - Target relevance
    
    The Workspace Network must NOT allocate or seize Attention.
    """
    
    projection_id: str
    """Unique identifier for this attention projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "attention_network"
    
    # Content availability
    globally_available_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Relevance indicators
    interruption_relevance: float = 0.0
    
    focus_conflict_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    attentional_demand: float = 0.0
    
    target_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceAttentionBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Attention Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    attention_projection_ref: str
    """Reference to the Attention Broadcast Projection being acknowledged."""
    
    target_ref: str = "attention_network"
    
    # Acknowledgement status
    received: bool = True
    
    attention_requested: bool = False
    """Whether attention was requested by this broadcast."""
    
    focus_conflict_detected_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Focus conflicts that were detected."""
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceAlertingBroadcastProjection:
    """
    Immutable projection of Broadcast content for Alerting Network consumption.
    
    The projection may expose:
        - Threat-relevant Broadcast
        - Anomaly
        - Integrity concern
        - Urgent context
        - Stale target warning
    
    The Workspace Network must NOT create alerts on behalf of Alerting unless
    an explicit external contract defines that transformation.
    """
    
    projection_id: str
    """Unique identifier for this alerting projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "alerting_network"
    
    # Alert indicators
    threat_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    anomaly_detected: bool = False
    
    integrity_concern_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    urgent_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    stale_target_warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceAlertingBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Alerting Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    alerting_projection_ref: str
    """Reference to the Alerting Broadcast Projection being acknowledged."""
    
    target_ref: str = "alerting_network"
    
    # Acknowledgement status
    received: bool = True
    
    threat_assessed_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Threats that were assessed from this broadcast."""
    
    alerts_created_refs: Tuple[str, ...] = field(default_factory=tuple)
    """Alerts that were created as a result of this broadcast."""
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceFocusingBroadcastProjection:
    """
    Immutable projection of Broadcast content for Focusing Network consumption.
    
    The projection may expose:
        - Currently relevant Content
        - Candidate coalition
        - Focus relevance
        - Conflict
        - Continuity significance
    
    Focusing owns focus allocation decisions.
    """
    
    projection_id: str
    """Unique identifier for this focusing projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "focusing_network"
    
    # Content relevance
    currently_relevant_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    candidate_coalition_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    focus_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    focus_conflict_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    continuity_significance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceFocusingBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Focusing Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    focusing_projection_ref: str
    """Reference to the Focusing Broadcast Projection being acknowledged."""
    
    target_ref: str = "focusing_network"
    
    # Acknowledgement status
    received: bool = True
    
    focus_relevance_assessed_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    focus_allocation_suggested: bool = False
    """Whether focus allocation was suggested."""
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceDefaultNetworkBroadcastProjection:
    """
    Immutable projection of Broadcast content for Default Network consumption.
    
    The projection may expose:
        - Unresolved context
        - Associative material
        - Autobiographical reference
        - Long-horizon implication
        - Internal simulation context
    
    The Workspace Network must NOT invoke Default Network processing.
    """
    
    projection_id: str
    """Unique identifier for this default network projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "default_network"
    
    # Content types
    unresolved_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    associative_material_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    autobiographical_reference_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    long_horizon_implication_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    internal_simulation_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceDefaultNetworkBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Default Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    default_network_projection_ref: str
    """Reference to the Default Network Broadcast Projection being acknowledged."""
    
    target_ref: str = "default_network"
    
    # Acknowledgement status
    received: bool = True
    
    internal_simulation_context_generated_refs: Tuple[str, ...] = field(
        default_factory=tuple
    )
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceMotivationBroadcastProjection:
    """
    Immutable projection of Broadcast content for Motivation Network consumption.
    
    The projection may expose:
        - Motivational relevance
        - Urgency
        - Conflict
        - Approach significance
        - Avoidance significance
        - Persistence significance
    
    Motivation owns motivational interpretation decisions.
    """
    
    projection_id: str
    """Unique identifier for this motivation projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "motivation_network"
    
    # Relevance indicators
    motivational_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    urgency_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    conflict_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    approach_significance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    avoidance_significance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    persistence_significance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceMotivationBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Motivation Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    motivation_projection_ref: str
    """Reference to the Motivation Broadcast Projection being acknowledged."""
    
    target_ref: str = "motivation_network"
    
    # Acknowledgement status
    received: bool = True
    
    motivational_relevance_assessed_refs: Tuple[str, ...] = field(
        default_factory=tuple
    )
    
    drive_state_adjusted: bool = False
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceReasoningBroadcastProjection:
    """
    Immutable projection of Broadcast content for Reasoning Network consumption.
    
    The projection may expose:
        - Evidence
        - Unresolved contradiction
        - Context
        - Uncertainty
        - Candidate coalition
        - Global constraint
    
    The Workspace Network must NOT perform Reasoning or invoke a model.
    """
    
    projection_id: str
    """Unique identifier for this reasoning projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "reasoning_network"
    
    # Content
    evidence_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    unresolved_contradiction_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    uncertainty_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    candidate_coalition_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    global_constraint_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceReasoningBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Reasoning Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    reasoning_projection_ref: str
    """Reference to the Reasoning Broadcast Projection being acknowledged."""
    
    target_ref: str = "reasoning_network"
    
    # Acknowledgement status
    received: bool = True
    
    reasoning_context_updated_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    contradictions_identified_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspacePlanningBroadcastProjection:
    """
    Immutable projection of Broadcast content for Planning Network consumption.
    
    The projection may expose:
        - Task context
        - Plan relevance
        - Dependency change
        - Blocker
        - Goal relation
        - Decision relation
    
    The Workspace Network must NOT create or revise Plans.
    """
    
    projection_id: str
    """Unique identifier for this planning projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "planning_network"
    
    # Content
    task_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    plan_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    dependency_change_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    blocker_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    goal_relation_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    decision_relation_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspacePlanningBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Planning Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    planning_projection_ref: str
    """Reference to the Planning Broadcast Projection being acknowledged."""
    
    target_ref: str = "planning_network"
    
    # Acknowledgement status
    received: bool = True
    
    plan_relevance_assessed_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    dependency_changes_identified_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspacePerceptionBroadcastProjection:
    """
    Immutable projection of Broadcast content for Perception Network consumption.
    
    The projection may expose:
        - Globally relevant perceptual context
        - Expected interpretation context
        - Uncertainty
        - Cross-modal integration requirement
    
    The Workspace Network must NOT alter raw perception pipelines.
    """
    
    projection_id: str
    """Unique identifier for this perception projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "perception_network"
    
    # Content
    globally_relevant_perceptual_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    expected_interpretation_context_refs: Tuple[str, ...] = field(
        default_factory=tuple
    )
    
    uncertainty_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    cross_modal_integration_requirements: Tuple[str, ...] = field(
        default_factory=tuple
    )
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspacePerceptionBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Perception Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    perception_projection_ref: str
    """Reference to the Perception Broadcast Projection being acknowledged."""
    
    target_ref: str = "perception_network"
    
    # Acknowledgement status
    received: bool = True
    
    perceptual_context_updated_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceLearningBroadcastProjection:
    """
    Immutable projection of Broadcast content for Learning Network consumption.
    
    The projection may expose:
        - Selected Content
        - Competition outcome
        - Rejected alternatives
        - Contextual relevance
        - Later acknowledgement references
    
    Learning must NOT mutate the current Broadcast or historical Competition.
    """
    
    projection_id: str
    """Unique identifier for this learning projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "learning_network"
    
    # Content
    selected_content_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    competition_outcome_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    rejected_alternative_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    contextual_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    later_acknowledgement_reference_refs: Tuple[str, ...] = field(
        default_factory=tuple
    )
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceLearningBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Learning Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    learning_projection_ref: str
    """Reference to the Learning Broadcast Projection being acknowledged."""
    
    target_ref: str = "learning_network"
    
    # Acknowledgement status
    received: bool = True
    
    learning_signal_generated_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspacePredictionBroadcastProjection:
    """
    Immutable projection of Broadcast content for Prediction Network consumption.
    
    These projections may expose:
        - Currently relevant context
        - Prediction gap
        - Unexpected change
        - Scenario constraint
        - Uncertainty
        - Selected globally available Content
    
    The Workspace Network must NOT invoke predictive models.
    """
    
    projection_id: str
    """Unique identifier for this prediction projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "prediction_network"
    
    # Content
    currently_relevant_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    prediction_gap_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    unexpected_change_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    scenario_constraint_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    uncertainty_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    globally_available_content_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspacePredictionBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Prediction Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    prediction_projection_ref: str
    """Reference to the Prediction Broadcast Projection being acknowledged."""
    
    target_ref: str = "prediction_network"
    
    # Acknowledgement status
    received: bool = True
    
    prediction_gap_identified_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    unexpected_change_assessed_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceWorldModelBroadcastProjection:
    """
    Immutable projection of Broadcast content for World Model consumption.
    
    These projections may expose:
        - Currently relevant context
        - Scenario constraint
        - Uncertainty
        - Selected globally available Content
    
    The Workspace Network must NOT invoke predictive models or world model updates.
    """
    
    projection_id: str
    """Unique identifier for this world model projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "world_model"
    
    # Content
    currently_relevant_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    scenario_constraint_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    uncertainty_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    globally_available_content_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceWorldModelBroadcastAcknowledgement:
    """
    Immutable acknowledgement from World Model about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    world_model_projection_ref: str
    """Reference to the World Model Broadcast Projection being acknowledged."""
    
    target_ref: str = "world_model"
    
    # Acknowledgement status
    received: bool = True
    
    scenario_constraint_assessed_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceMonitoringBroadcastProjection:
    """
    Immutable projection for Monitoring Network consumption.
    
    The projection may express monitoring relevance. The Workspace Network
    does NOT perform runtime Monitoring.
    """
    
    projection_id: str
    """Unique identifier for this monitoring projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "monitoring_network"
    
    # Monitoring relevance
    monitorable_events_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    anomaly_candidates_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    pattern_change_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    baseline_deviations_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceMonitoringBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Monitoring Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    monitoring_projection_ref: str
    """Reference to the Monitoring Broadcast Projection being acknowledged."""
    
    target_ref: str = "monitoring_network"
    
    # Acknowledgement status
    received: bool = True
    
    events_monitored_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceRecoveryBroadcastProjection:
    """
    Immutable projection for Recovery Network consumption.
    
    The projection may expose:
        - Degraded Workspace State
        - Unavailable target
        - Failed distribution projection
        - Invalidated Broadcast
        - Restoration context
    
    The Workspace Network must NOT execute recovery procedures.
    """
    
    projection_id: str
    """Unique identifier for this recovery projection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    target_ref: str = "recovery_network"
    
    # Recovery indicators
    degraded_state_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    unavailable_target_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    failed_projection_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    invalidated_broadcast_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    restoration_context_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceRecoveryBroadcastAcknowledgement:
    """
    Immutable acknowledgement from Recovery Network about a projection.
    """
    
    acknowledgement_id: str
    """Unique identifier for this acknowledgement."""
    
    recovery_projection_ref: str
    """Reference to the Recovery Broadcast Projection being acknowledged."""
    
    target_ref: str = "recovery_network"
    
    # Acknowledgement status
    received: bool = True
    
    restoration_plan_created_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing and provenance
    acknowledged_at_semantic_time: str = "semantic_time_origin"
    
    correlation_ref: str = ""
    
    provenance_ref: str = ""


# =============================================================================
# DELIVERY PROJECTIONS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceDistributionRequirement:
    """
    Immutable delivery requirement for a distribution.
    
    Requirements define what must be true about the delivery process.
    They are semantic assertions, not runtime enforcement mechanisms.
    """
    
    requirement_kind: str
    """Kind of requirement."""
    
    required_value: Optional[str] = None
    """Required value if applicable (for specific requirements)."""
    
    is_mandatory: bool = True
    """Whether this requirement must be met for valid delivery."""


class WorkspaceDistributionRequirementKind(Enum):
    """
    Canonical kinds of distribution requirements.
    """
    
    EXACT_BROADCAST_REVISION = "exact_broadcast_revision"
    EXACT_TARGET_REVISION = "exact_target_revision"
    MINIMAL_DISCLOSURE = "minimal_disclosure"
    ACKNOWLEDGEMENT_REQUIRED = "acknowledgement_required"
    ORDER_PRESERVATION_REQUIRED = "order_preservation_required"
    DEDUPLICATION_REQUIRED = "deduplication_required"
    EXPIRATION_ENFORCEMENT = "expiration_enforcement"
    PRIVACY_PRESERVATION = "privacy_preservation"
    POLICY_PRESERVATION = "policy_preservation"
    SECURITY_PRESERVATION = "security_preservation"
    PROVENANCE_PRESERVATION = "provenance_preservation"
    BOUNDED_PROJECTION = "bounded_projection"
    CORRELATION_PRESERVATION = "correlation_preservation"
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionConstraint:
    """
    Immutable delivery constraint for a distribution.
    
    Constraints limit what may happen during delivery. They are semantic
    boundaries, not runtime enforcement mechanisms.
    """
    
    constraint_kind: str
    """Kind of constraint."""
    
    bound_value: int = 0
    """Numeric bound if applicable."""
    
    scope_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to scopes this constraint applies to."""


class WorkspaceDistributionConstraintKind(Enum):
    """
    Canonical kinds of distribution constraints.
    """
    
    TARGET_SCOPE = "target_scope"
    CONTENT_SCOPE = "content_scope"
    DISCLOSURE_SCOPE = "disclosure_scope"
    PRIVACY_SCOPE = "privacy_scope"
    POLICY_SCOPE = "policy_scope"
    SECURITY_SCOPE = "security_scope"
    AUTHORITY_SCOPE = "authority_scope"
    TEMPORAL_SCOPE = "temporal_scope"
    PROJECTION_SIZE = "projection_size"
    TARGET_COUNT = "target_count"
    ACKNOWLEDGEMENT_COUNT = "acknowledgement_count"
    DELIVERY_ATTEMPT_POLICY_REFERENCE = "delivery_attempt_policy_reference"
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDeliveryProjectionIdentity:
    """
    Identity for a delivery projection.
    """
    
    identity: str
    """Unique identifier for this delivery projection."""
    
    revision: int = 1
    """Revision number for this projection."""


WorkspaceBroadcastDeliveryProjectionReference = str
"""
Immutable reference to Workspace Broadcast Delivery Projection.

Format: "delivery_projection_identity@revision"
Examples:
    "delivery_projection_abc123@1"
    "delivery_to_target_xyz@3"
"""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDeliveryProjection:
    """
    Immutable semantic instruction for runtime infrastructure to attempt delivery.
    
    A Delivery Projection represents a semantic instruction to external runtime
    infrastructure to attempt delivery of one exact target-specific Broadcast
    projection. It preserves all required metadata but contains NO runtime
    implementation details.
    
    It MUST NOT contain:
        - Network address
        - Queue name
        - Topic name
        - Socket
        - Callback
        - Retry loop
        - Transport implementation
        - Credentials
    
    Runtime delivery belongs to Core-owned communication infrastructure.
    """
    
    identity: WorkspaceBroadcastDeliveryProjectionIdentity
    """Unique identity for this delivery projection."""
    
    distribution_ref: str
    """Reference to Distribution Request that produced this delivery projection."""
    
    target_projection_ref: str
    """Reference to Target Projection being delivered."""
    
    target_ref: str
    """Reference to intended target consumer (NOT ownership)."""
    
    # Delivery metadata
    requirements: Tuple[WorkspaceDistributionRequirement, ...] = field(
        default_factory=tuple
    )
    """Delivery requirements for this delivery attempt."""
    
    constraints: Tuple[WorkspaceDistributionConstraint, ...] = field(
        default_factory=tuple
    )
    """Constraints applied to this delivery attempt."""
    
    acknowledgement_policy: WorkspaceAcknowledgementPolicy
    """Acknowledgement policy for this delivery."""
    
    expiration_semantic_time: Optional[str] = None
    """Semantic time reference when this delivery expires (if applicable)."""
    
    correlation_ref: str = ""
    """Reference to correlation context for tracing."""
    
    causation_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to causal predecessors in the delivery lineage."""
    
    privacy_class: str = "internal_only"
    """Privacy classification for this delivery."""
    
    provenance_ref: str = ""
    """Reference to provenance trail."""
    
    @property
    def is_runtime_neutral(self) -> bool:
        """
        Check if this delivery projection contains no runtime-specific details.
        
        Runtime-neutral projections contain only semantic references, not
        concrete runtime addresses or implementations.
        """
        # Check for absence of runtime-specific fields
        return (
            self.requirements is not None and  # Requirements exist
            len(self.concurrency_checks) == 0  # No concurrent access checks needed
        )
    
    @property
    def concurrency_checks(self) -> Tuple[str, ...]:
        """
        Return any concurrency-related checks for this delivery.
        
        This property exists to demonstrate that runtime state management
        is NOT performed here - it would be handled by Core infrastructure.
        """
        # In a real implementation, this might check delivery timestamps,
        # sequence numbers, or other ordering constraints. Here it's always
        # empty since we don't perform concurrency management.
        return ()


# =============================================================================
# ACKNOWLEDGEMENT POLICY AND TYPES
# =============================================================================

class WorkspaceAcknowledgementPolicy(Enum):
    """
    Canonical acknowledgement policies for distributions.
    
    Acknowledgement policy defines semantic expectations. It does NOT wait
    for acknowledgements - that is runtime work.
    """
    
    NONE_REQUIRED = "none_required"
    """No acknowledgements required."""
    
    RECEIPT_REQUIRED = "receipt_required"
    """Acknowledgement that message was received."""
    
    VALIDATION_REQUIRED = "validation_required"
    """Acknowledgement that projection was validated."""
    
    ACCEPTANCE_REQUIRED = "acceptance_required"
    """Acknowledgement that projection was accepted for processing."""
    
    PROCESSING_DECISION_REQUIRED = "processing_decision_required"
    """Acknowledgement of the target's processing decision."""
    
    BOUNDED_PARTIAL_ACKNOWLEDGEMENT = "bounded_partial_acknowledgement"
    """At least some targets must acknowledge (not all required)."""
    
    ALL_TARGETS_REQUIRED = "all_targets_required"
    """All specified targets must acknowledge for success."""
    
    ANY_TARGET_REQUIRED = "any_target_required"
    """At least one target must acknowledge for partial success."""
    
    SELECTED_TARGETS_REQUIRED = "selected_targets_required"
    """Specific selected targets must acknowledge."""
    
    UNKNOWN = "unknown"


class WorkspaceBroadcastAcknowledgementKind(Enum):
    """
    Canonical acknowledgement kinds.
    
    Acknowledgements must reference exact Delivery Projections and not
    overstate what occurred. For example, RECEIVED does NOT imply
    WORKING_MEMORY_ADMITTED or MEMORY_ENCODED.
    """
    
    # Basic delivery acknowledgements
    RECEIVED = "received"
    """Message was received by target infrastructure."""
    
    VALIDATED = "validated"
    """Projection was validated against schema and constraints."""
    
    ACCEPTED = "accepted"
    """Projection was accepted for further processing by the target."""
    
    ACCEPTED_WITH_LIMITATIONS = "accepted_with_limitations"
    """Projection accepted but with some limitations applied."""
    
    # Working Memory specific
    ADMITTED = "admitted"
    """Content was admitted to Working Memory."""
    
    # Semantic outcomes
    DEFERRED = "deferred"
    """Processing deferred to later time or condition."""
    
    REJECTED = "rejected"
    """Projection rejected (not accepted for processing)."""
    
    UNSUPPORTED = "unsupported"
    """Target does not support this projection kind."""
    
    STALE_PROJECTION = "stale_projection"
    """Projection is stale relative to target's current State."""
    
    STALE_BROADCAST = "stale_broadcast"
    """Broadcast revision is stale relative to target's knowledge."""
    
    STALE_TARGET = "stale_target"
    """Target's State has changed since projection was created."""
    
    DUPLICATE = "duplicate"
    """Same or equivalent projection already delivered."""
    
    POLICY_RESTRICTED = "policy_restricted"
    """Disclosed content violates policy restrictions."""
    
    SECURITY_RESTRICTED = "security_restricted"
    """Disclosed content violates security restrictions."""
    
    PRIVACY_RESTRICTED = "privacy_restricted"
    """Disclosed content violates privacy restrictions."""
    
    CAPACITY_LIMITED = "capacity_limited"
    """Target cannot accept at this time (capacity exhausted)."""
    
    TARGET_UNAVAILABLE = "target_unavailable"
    """Target is currently unavailable for delivery."""
    
    FAILED = "failed"
    """Delivery attempt failed."""
    
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastAcknowledgementIdentity:
    """
    Identity for an acknowledgement.
    """
    
    identity: str
    """Unique identifier for this acknowledgement."""
    
    revision: int = 1
    """Revision number for this acknowledgement."""


WorkspaceBroadcastAcknowledgementReference = str
"""
Immutable reference to Workspace Broadcast Acknowledgement.

Format: "acknowledgement_identity@revision"
Examples:
    "ack_abc123@1"
    "delivery_ack_xyz@3"
"""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastAcknowledgement:
    """
    Immutable acknowledgement of delivery or processing.
    
    An acknowledgement must reference:
        - Exact Delivery Projection
        - Exact target
        - Exact Broadcast revision
        - Target response identity and revision
        - Target authority
        - Limitations
        - Conditions
        - Correlation
        - Causation
        - Privacy
        - Provenance
    
    Acknowledgement is NOT processing success. It must not overstate what
    occurred.
    """
    
    identity: WorkspaceBroadcastAcknowledgementIdentity
    """Unique identity for this acknowledgement."""
    
    delivery_projection_ref: str
    """Reference to Delivery Projection being acknowledged (NOT ownership)."""
    
    target_ref: str
    """Reference to target that sent this acknowledgement."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    kind: WorkspaceBroadcastAcknowledgementKind
    """Kind of acknowledgement."""
    
    # Response data
    response_identity: Optional[str] = None
    """Identity of the target's internal processing response."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Limitations on what this acknowledgement means."""
    
    conditions_applied: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that were applied to produce this acknowledgement."""
    
    correlation_ref: str = ""
    """Reference to correlation context."""
    
    causation_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to causal predecessors."""
    
    privacy_class: str = "internal_only"
    """Privacy classification for this acknowledgement."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time reference when acknowledged."""
    
    provenance_ref: str = ""
    """Reference to provenance trail."""
    
    @property
    def is_success(self) -> bool:
        """
        Check if this acknowledgement indicates successful delivery/processing.
        
        Success means the target accepted the projection for processing,
        not that it was fully processed or had any State effects.
        """
        return self.kind in (
            WorkspaceBroadcastAcknowledgementKind.RECEIVED,
            WorkspaceBroadcastAcknowledgementKind.VALIDATED,
            WorkspaceBroadcastAcknowledgementKind.ACCEPTED,
            WorkspaceBroadcastAcknowledgementKind.ACCEPTED_WITH_LIMITATIONS,
            WorkspaceBroadcastAcknowledgementKind.ADMITTED,
        )
    
    @property
    def is_rejection(self) -> bool:
        """
        Check if this acknowledgement indicates rejection.
        
        Rejections include explicit rejections, unsupported projections,
        stale responses, and capacity limitations.
        """
        return self.kind in (
            WorkspaceBroadcastAcknowledgementKind.REJECTED,
            WorkspaceBroadcastAcknowledgementKind.UNSUPPORTED,
            WorkspaceBroadcastAcknowledgementKind.STALE_PROJECTION,
            WorkspaceBroadcastAcknowledgementKind.STALE_BROADCAST,
            WorkspaceBroadcastAcknowledgementKind.STALE_TARGET,
            WorkspaceBroadcastAcknowledgementKind.DUPLICATE,
            WorkspaceBroadcastAcknowledgementKind.POLICY_RESTRICTED,
            WorkspaceBroadcastAcknowledgementKind.SECURITY_RESTRICTED,
            WorkspaceBroadcastAcknowledgementKind.PRIVACY_RESTRICTED,
            WorkspaceBroadcastAcknowledgementKind.CAPACITY_LIMITED,
            WorkspaceBroadcastAcknowledgementKind.TARGET_UNAVAILABLE,
            WorkspaceBroadcastAcknowledgementKind.FAILED,
        )


# =============================================================================
# REJECTIONS AND DEFERRALS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionRejection:
    """
    Immutable record of distribution rejection.
    
    A rejection is a semantic outcome. It is NOT necessarily an exception.
    Rejections include:
        - Target ineligibility
        - Target unavailability
        - Unsupported content or projection
        - Policy, Security, Privacy restrictions
        - Authority missing
        - Stale broadcasts/targets/projections
        - Invalid scope or disclosure
        - Missing dependencies
        - Capacity limitations
        - Expiration
        - Duplicate delivery
        - Conflicting requirements
    """
    
    rejection_id: str
    """Unique identifier for this rejection."""
    
    distribution_ref: str
    """Reference to Distribution Request that was rejected."""
    
    target_ref: str
    """Reference to target that caused the rejection."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    reason: WorkspaceBroadcastDistributionRejectionReason
    """Reason for the rejection."""
    
    context_data_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to contextual data at time of rejection."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time reference when rejection occurred."""
    
    provenance_ref: str = ""
    """Reference to provenance trail."""
    
    @property
    def is_eligibility_rejection(self) -> bool:
        """Check if rejection is due to target eligibility issues."""
        return self.reason in (
            WorkspaceBroadcastDistributionRejectionReason.TARGET_INELIGIBLE,
            WorkspaceBroadcastDistributionRejectionReason.TARGET_INVALID,
        )
    
    @property
    def is_availability_rejection(self) -> bool:
        """Check if rejection is due to target availability issues."""
        return self.reason == WorkspaceBroadcastDistributionRejectionReason.TARGET_UNAVAILABLE
    
    @property
    def is_policy_security_rejection(self) -> bool:
        """Check if rejection is due to Policy, Security, or Privacy restrictions."""
        return self.reason in (
            WorkspaceBroadcastDistributionRejectionReason.POLICY_RESTRICTION,
            WorkspaceBroadcastDistributionRejectionReason.SECURITY_RESTRICTION,
            WorkspaceBroadcastDistributionRejectionReason.PRIVACY_RESTRICTION,
        )
    
    @property
    def is_stale_rejection(self) -> bool:
        """Check if rejection is due to staleness issues."""
        return self.reason in (
            WorkspaceBroadcastDistributionRejectionReason.STALE_BROADCAST,
            WorkspaceBroadcastDistributionRejectionReason.STALE_TARGET,
            WorkspaceBroadcastDistributionRejectionReason.STALE_PROJECTION,
        )


class WorkspaceBroadcastDistributionRejectionReason(Enum):
    """
    Canonical rejection reasons.
    """
    
    TARGET_INELIGIBLE = "target_ineligible"
    TARGET_UNAVAILABLE = "target_unavailable"
    UNSUPPORTED_CONTENT = "unsupported_content"
    UNSUPPORTED_PROJECTION = "unsupported_projection"
    POLICY_RESTRICTION = "policy_restriction"
    SECURITY_RESTRICTION = "security_restriction"
    PRIVACY_RESTRICTION = "privacy_restriction"
    AUTHORITY_MISSING = "authority_missing"
    STALE_BROADCAST = "stale_broadcast"
    STALE_TARGET = "stale_target"
    STALE_PROJECTION = "stale_projection"
    INVALID_SCOPE = "invalid_scope"
    INVALID_DISCLOSURE = "invalid_disclosure"
    MISSING_DEPENDENCY = "missing_dependency"
    CAPACITY_LIMITED = "capacity_limited"
    EXPIRED = "expired"
    DUPLICATE = "duplicate"
    CONFLICT = "conflict"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionDeferral:
    """
    Immutable record of distribution deferral.
    
    Deferrals indicate that delivery should be attempted later or under
    different conditions. They are semantic continuations, not runtime
    scheduling decisions.
    """
    
    deferral_id: str
    """Unique identifier for this deferral."""
    
    distribution_ref: str
    """Reference to Distribution Request being deferred."""
    
    target_ref: str
    """Reference to target that caused the deferral."""
    
    reason: Optional[str] = None
    """Reason for deferral (if applicable)."""
    
    deferred_until_semantic_time: Optional[str] = None
    """Semantic time reference when deferral expires."""
    
    conditions_to_recheck: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that should be rechecked before retry."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time reference when deferral occurred."""
    
    provenance_ref: str = ""
    """Reference to provenance trail."""


# =============================================================================
# PARTIAL DELIVERY
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastPartialDelivery:
    """
    Immutable record of partial delivery.
    
    Partial delivery means some targets succeeded while others failed. It
    must preserve:
        - Delivered targets (with their acknowledgements)
        - Undelivered targets (with rejections or deferrals)
        - Accepted fields (for target-specific projections)
        - Rejected fields
        - Limitations and conditions
        - Unresolved acknowledgements
        - Provenance
    """
    
    partial_delivery_id: str
    """Unique identifier for this partial delivery record."""
    
    distribution_ref: str
    """Reference to Distribution Request that produced this partial delivery."""
    
    # Delivery results
    successfully_delivered_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to targets that were successfully delivered to."""
    
    partially_delivered_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to targets with partial success."""
    
    failed_delivery_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to targets where delivery failed."""
    
    deferral_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to targets where delivery was deferred."""
    
    # Field-level results (for target-specific projections)
    accepted_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that were accepted across all deliveries."""
    
    rejected_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that were rejected across some deliveries."""
    
    # Constraints
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this partial delivery."""
    
    conditions_applied: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that were applied."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time reference when partial delivery occurred."""
    
    provenance_ref: str = ""
    """Reference to provenance trail."""


# =============================================================================
# DUPLICATE DELIVERY
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDuplicateDeliveryAssessment:
    """
    Immutable assessment of whether a delivery is duplicate.
    
    Distinguish:
        - Same Delivery Projection identity and revision (definite duplicate)
        - Same Broadcast-target pair (may be duplicate)
        - Semantically equivalent target projection (assessment required)
        - Replayed delivery (history replay, may be acceptable)
        - Superseded projection (replacement, not duplicate)
        - Non-duplicate (new delivery)
    """
    
    assessment_id: str
    """Unique identifier for this duplicate assessment."""
    
    delivery_projection_ref: str
    """Reference to Delivery Projection being assessed."""
    
    previous_delivery_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to potentially duplicate prior deliveries."""
    
    # Assessment result
    is_duplicate: bool = False
    
    assessment_kind: str = ""
    """
    Kind of duplicate assessment.
    
    Valid values:
        - "exact_identity_match"
        - "broadcast_target_pair_match"
        - "semantic_equivalence"
        - "replayed_delivery"
        - "superseded_projection"
        - "non_duplicate"
    """
    
    # Semantic equivalence check
    semantic_similarity: float = 0.0
    
    # Context
    correlation_ref: str = ""
    
    provenance_ref: str = ""


# =============================================================================
# STALE TARGET HANDLING
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastStaleTargetAssessment:
    """
    Immutable assessment of whether a target is stale.
    
    Stale targets have State that has changed since projections were created,
    making previous projections potentially invalid. A stale target projection
    must NOT be silently treated as current.
    """
    
    assessment_id: str
    """Unique identifier for this stale assessment."""
    
    target_ref: str
    """Reference to target being assessed."""
    
    projected_target_state_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to target State at time of projection creation."""
    
    current_target_state_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to target's current State (if available)."""
    
    # Assessment result
    is_stale: bool = False
    
    stale_reasons: Tuple[WorkspaceBroadcastStaleTargetReason, ...] = field(
        default_factory=tuple
    )
    """Reasons why the target may be stale."""
    
    staleness_severity: float = 0.0
    """
    Severity of staleness (0.0-1.0).
    
    Higher values indicate greater potential for projection invalidation.
    """
    
    recommended_action: str = ""
    """
    Recommended action when stale target detected.
    
    Valid values:
        - "regenerate_projection"
        - "skip_delivery"
        - "deliver_with_stale_marker"
        - "request_target_update"
    """
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time reference when assessment occurred."""
    
    provenance_ref: str = ""


class WorkspaceBroadcastStaleTargetReason(Enum):
    """
    Canonical stale target reasons.
    """
    
    TARGET_REVISION_CHANGED = "target_revision_changed"
    TARGET_CAPABILITY_CHANGED = "target_capability_changed"
    TARGET_SCOPE_CHANGED = "target_scope_changed"
    TARGET_POLICY_CHANGED = "target_policy_changed"
    TARGET_SECURITY_CHANGED = "target_security_changed"
    TARGET_PRIVACY_CHANGED = "target_privacy_changed"
    TARGET_STATE_CHANGED = "target_state_changed"
    TARGET_PROJECTION_EXPIRED = "target_projection_expired"
    UNKNOWN = "unknown"


# =============================================================================
# DELIVERY CONFLICTS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDeliveryConflict:
    """
    Immutable record of a delivery conflict.
    
    Conflicting authoritative responses must NOT use silent last-write-wins.
    Each conflict must be preserved with full context.
    """
    
    conflict_id: str
    """Unique identifier for this conflict."""
    
    distribution_ref: str
    """Reference to Distribution Request where conflict occurred."""
    
    target_refs: Tuple[str, ...]
    """References to targets involved in the conflict."""
    
    # Conflict details
    kind: WorkspaceBroadcastDeliveryConflictKind
    """Kind of conflict."""
    
    first_response_ref: Optional[str] = None
    """Reference to first response (if applicable)."""
    
    second_response_ref: Optional[str] = None
    """Reference to second conflicting response."""
    
    resolution_method: str = ""
    """
    Method used to resolve or track this conflict.
    
    Valid values:
        - "preserve_all"
        - "priority_order"
        - "timestamp_order"
        - "require_manual_review"
        - "semantic_merge"
    """
    
    resolved: bool = False
    
    resolved_at_semantic_time: Optional[str] = None
    """Semantic time reference when resolved (if applicable)."""
    
    resolution_notes: str = ""
    """Notes about how the conflict was handled."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time reference when conflict detected."""
    
    provenance_ref: str = ""


class WorkspaceBroadcastDeliveryConflictKind(Enum):
    """
    Canonical delivery conflict kinds.
    """
    
    TARGET_ELIGIBILITY_CONFLICT = "target_eligibility_conflict"
    DISCLOSURE_CONFLICT = "disclosure_conflict"
    POLICY_CONFLICT = "policy_conflict"
    SECURITY_CONFLICT = "security_conflict"
    PRIVACY_CONFLICT = "privacy_conflict"
    AUTHORITY_CONFLICT = "authority_conflict"
    REVISION_CONFLICT = "revision_conflict"
    ACKNOWLEDGEMENT_CONFLICT = "acknowledgement_conflict"
    SCOPE_CONFLICT = "scope_conflict"
    TARGET_CAPABILITY_CONFLICT = "target_capability_conflict"
    UNKNOWN = "unknown"


# =============================================================================
# CORRELATION AND CAUSATION
# =============================================================================

WorkspaceDistributionCorrelationId = str


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionCorrelationReference:
    """
    Immutable reference to correlation context.
    
    Correlation connects the entire distribution pipeline for traceability.
    """
    
    correlation_id: str
    """Unique ID for this correlation context."""
    
    parent_correlation_ids: Tuple[str, ...] = field(default_factory=tuple)
    """References to parent correlation contexts (for chaining)."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time reference for this correlation."""


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionCorrelationContext:
    """
    Immutable context for correlation across distribution steps.
    """
    
    correlation_id: str
    """Unique ID for this correlation context."""
    
    # Pipeline stage references
    broadcast_ref: Optional[str] = None
    
    distribution_request_ref: Optional[str] = None
    
    target_projection_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    delivery_projection_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    acknowledgement_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    outcome_ref: Optional[str] = None
    
    # Context data
    source_system_id: str = ""
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionCausationReference:
    """
    Immutable reference to a causal relationship in the distribution lineage.
    
    Causation preserves how one step led to the next without implying
    temporal ordering (which belongs to runtime).
    """
    
    causation_id: str
    """Unique identifier for this causation."""
    
    cause_ref: str
    """Reference to causal predecessor."""
    
    effect_ref: str
    """Reference to causal successor."""
    
    relation: WorkspaceDistributionCausationRelation
    """Kind of causal relationship."""
    
    evidence_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to evidence supporting this causation."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time reference for this causation."""
    
    provenance_ref: str = ""


class WorkspaceDistributionCausationRelation(Enum):
    """
    Canonical causation relations in distribution lineage.
    """
    
    DISTRIBUTION_REQUESTED_BY_BROADCAST = "distribution_requested_by_broadcast"
    TARGET_PROJECTION_DERIVED_FROM_BROADCAST = (
        "target_projection_derived_from_broadcast"
    )
    DELIVERY_PROJECTION_DERIVED_FROM_TARGET_PROJECTION = (
        "delivery_projection_derived_from_target_projection"
    )
    ACKNOWLEDGEMENT_RESPONDS_TO_DELIVERY = "acknowledgement_responds_to_delivery"
    OUTCOME_DERIVED_FROM_ACKNOWLEDGEMENTS = "outcome_derived_from_acknowledgements"
    DELTA_DERIVED_FROM_DISTRIBUTION_OUTCOME = "delta_derived_from_distribution_outcome"
    INVALIDATED_BY_BROADCAST_REVISION = "invalidated_by_broadcast_revision"
    INVALIDATED_BY_TARGET_REVISION = "invalidated_by_target_revision"
    SUPERSEDES_DISTRIBUTION = "supersedes_distribution"
    MIGRATED_FROM_DISTRIBUTION = "migrated_from_distribution"
    UNKNOWN = "unknown"


# =============================================================================
# DISTRIBUTION DISPOSITION
# =============================================================================

WorkspaceBroadcastDistributionDispositionKind = str


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionDisposition:
    """
    Immutable disposition of a distribution attempt for one target.
    
    A disposition records the semantic result of attempting to distribute
    to a specific target. It does NOT imply any runtime success or failure.
    """
    
    disposition_id: str
    """Unique identifier for this disposition."""
    
    target_ref: str
    """Reference to target being processed."""
    
    distribution_ref: str
    """Reference to Distribution Request."""
    
    # Disposition result
    kind: WorkspaceBroadcastDistributionDispositionKind
    
    # Context
    broadcast_ref: str = ""
    
    projection_ref: Optional[str] = None
    
    delivery_projection_ref: Optional[str] = None
    
    acknowledgement_ref: Optional[str] = None
    
    limitation_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    condition_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""
    
    @property
    def is_success(self) -> bool:
        """Check if disposition indicates successful distribution."""
        return self.kind in (
            "TARGET_ELIGIBLE",
            "PROJECTION_CREATED",
            "DELIVERY_PROJECTED",
            "ACKNOWLEDGED",
            "ACCEPTED",
            "ACCEPTED_WITH_LIMITATIONS",
            "PARTIALLY_ACCEPTED",
        )
    
    @property
    def is_failure(self) -> bool:
        """Check if disposition indicates failed distribution."""
        return self.kind in (
            "TARGET_INELIGIBLE",
            "REJECTED",
            "STALE",
            "DUPLICATE",
            "CONFLICTING",
            "TARGET_UNAVAILABLE",
            "EXPIRED",
            "INVALIDATED",
        )


# =============================================================================
# DISTRIBUTION OUTCOME
# =============================================================================

WorkspaceBroadcastDistributionOutcomeKind = str


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionOutcomeIdentity:
    """
    Identity for a distribution outcome.
    """
    
    identity: str
    """Unique identifier for this outcome."""
    
    revision: int = 1
    """Revision number for this outcome."""


WorkspaceBroadcastDistributionOutcomeReference = str
"""
Immutable reference to Workspace Broadcast Distribution Outcome.

Format: "outcome_identity@revision"
Examples:
    "outcome_abc123@1"
    "distribution_result_xyz@3"
"""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionOutcome:
    """
    Immutable semantic record of a distribution attempt's result.
    
    The outcome must preserve:
        - Source Broadcast
        - Source Distribution Request
        - Target dispositions (for each target)
        - Acknowledgements (received or missing)
        - Rejections and deferrals
        - Partial deliveries
        - Unresolved targets
        - Limitations and blockers
        - Continuation recommendations
        - Privacy and provenance
    
    The outcome does NOT:
        - Perform runtime delivery
        - Wait for acknowledgements
        - Retry failed deliveries
        - Mutate State directly
    """
    
    identity: WorkspaceBroadcastDistributionOutcomeIdentity
    """Unique identity for this outcome."""
    
    distribution_ref: str
    """Reference to Distribution Request that produced this outcome."""
    
    broadcast_ref: str
    """Reference to source Broadcast (NOT ownership)."""
    
    # Outcome result
    kind: WorkspaceBroadcastDistributionOutcomeKind
    
    # Target-level results
    target_dispositions: Tuple[WorkspaceBroadcastDistributionDisposition, ...]
    """Dispositions for each target in the distribution."""
    
    # Acknowledgements
    received_acknowledgement_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to acknowledgements that were received."""
    
    missing_acknowledgement_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to targets where acknowledgements are expected but missing."""
    
    # Rejections and deferrals
    rejection_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to rejections that occurred."""
    
    deferral_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to deferrals that occurred."""
    
    partial_delivery_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to partial deliveries that occurred."""
    
    # Constraints and blockers
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Limitations on the distribution outcome."""
    
    blockers: Tuple[str, ...] = field(default_factory=tuple)
    """Blockers that prevented full distribution."""
    
    # Continuation
    continuation_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to continuations suggested by this outcome."""
    
    # Semantic and provenance
    semantic_time_ref: str = "semantic_time_origin"
    
    privacy_class: str = "internal_only"
    
    provenance_ref: str = ""


class WorkspaceBroadcastDistributionCompleteness(Enum):
    """
    Canonical completeness values for distribution outcomes.
    
    Completeness is assessed relative to the exact Distribution Request's
    requirements and constraints.
    """
    
    COMPLETE = "complete"
    """All targets successfully processed."""
    
    COMPLETE_WITH_LIMITATIONS = "complete_with_limitations"
    """All targets processed but with some limitations applied."""
    
    SUBSTANTIALLY_COMPLETE = "substantially_complete"
    """Most targets processed; missing only non-critical targets."""
    
    PARTIAL = "partial"
    """Some targets processed; others failed or were skipped."""
    
    MINIMAL = "minimal"
    """Only minimal progress made on distribution."""
    
    MISSING_REQUIRED_TARGET = "missing_required_target"
    """A required target was not reached."""
    
    MISSING_REQUIRED_ACKNOWLEDGEMENT = "missing_required_acknowledgement"
    """An acknowledgement was expected but not received."""
    
    DISCLOSURE_LIMITED = "disclosure_limited"
    """Disclosure limitations prevented full distribution."""
    
    CAPACITY_LIMITED = "capacity_limited"
    """Target capacity prevented full distribution."""
    
    INVALID = "invalid"
    """Distribution could not be completed due to invalid request."""
    
    UNKNOWN = "unknown"


class WorkspaceBroadcastDistributionValidity(Enum):
    """
    Canonical validity values for distribution outcomes.
    """
    
    VALID = "valid"
    """Outcome is semantically valid and complete."""
    
    VALID_WITH_LIMITATIONS = "valid_with_limitations"
    """Outcome is valid but with some limitations."""
    
    PROVISIONAL = "provisional"
    """Outcome is provisional, awaiting further acknowledgements."""
    
    STALE = "stale"
    """Outcome may be stale relative to target State."""
    
    EXPIRED = "expired"
    """Distribution attempt expired before completion."""
    
    CONFLICTED = "conflicted"
    """Conflicting responses prevented resolution."""
    
    INVALID = "invalid"
    """Outcome is semantically invalid (e.g., broken invariants)."""
    
    UNKNOWN = "unknown"


# =============================================================================
# FAN-OUT AND FAN-IN BOUNDS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceDistributionFanOutBounds:
    """
    Immutable bounds on fan-out for a distribution.
    
    No broadcast-to-all behavior by default. Every target must be included
    by explicit semantic eligibility. Bounds are enforced at the semantic
    level - exceeding them is an error condition.
    """
    
    # Target count bounds
    max_targets: int = 100
    
    max_target_kinds: int = 20
    
    # Projection bounds per target
    max_projections_per_target: int = 10
    
    # Content reference bounds
    max_content_refs_per_projection: int = 50
    
    # Disclosure bounds
    max_disclosed_fields_per_projection: int = 100
    
    # Coalition bounds
    max_coalition_members_per_broadcast: int = 20
    
    # Condition and limitation bounds
    max_conditions_per_target: int = 10
    
    max_limitations_per_target: int = 10
    
    # Pending acknowledgment bounds
    max_pending_acknowledgements: int = 500


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionFanInBounds:
    """
    Immutable bounds on fan-in for a distribution outcome.
    
    No unbounded acknowledgement accumulation. Bounds prevent denial of
    service through excessive response accumulation.
    """
    
    # Acknowledgement bounds
    max_acknowledgements: int = 1000
    
    # Response bounds per target
    max_responses_per_target: int = 10
    
    # Conflict bounds
    max_conflicting_responses: int = 50
    
    # Limitation bounds
    max_limitations_per_outcome: int = 20
    
    # Rejection reason bounds
    max_rejection_reasons_per_outcome: int = 30
    
    # Provenance parent bounds
    max_provenance_parents: int = 100
    
    # Unresolved target bounds
    max_unresolved_targets: int = 50


# =============================================================================
# DETERMINISTIC TARGET ORDERING
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceDistributionTargetOrder:
    """
    Immutable specification of deterministic target ordering for distribution.
    
    Independent target processing order must be deterministic. Recommended
    canonical ordering:
        1. Target kind (alphabetical)
        2. Target owner namespace (if applicable)
        3. Target identity
        4. Target revision
        5. Projection kind
        6. Projection identity
        7. Canonical semantic digest
    
    Do NOT use: registration order, arrival order, transport order,
    runtime completion order, memory address, dictionary insertion order.
    
    Ordering must NOT resolve semantic conflicts - that is a separate concern.
    """
    
    order_id: str
    """Unique identifier for this ordering."""
    
    target_order: Tuple[str, ...]
    """Ordered list of target references."""
    
    # Ordering rules applied
    kind_sorted: bool = True
    namespace_sorted: bool = False
    
    identity_sorted: bool = True
    
    # Semantic digest (for verification)
    canonical_digest: str = ""
    
    @property
    def is_deterministic(self) -> bool:
        """
        Check if ordering meets determinism requirements.
        
        Deterministic ordering must not depend on runtime factors like
        arrival order, memory address, or dictionary insertion order.
        """
        # In a real implementation, this would verify the ordering algorithm
        # is deterministic. Here we return True for all orders since we're
        # specifying rather than computing them.
        return self.order_id != ""


# =============================================================================
# DISTRIBUTION HISTORY AND LINEAGE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionHistoryEntry:
    """
    History entry for distribution lifecycle events.
    
    History must be: immutable, append-only, bounded, deterministic,
    provenance-preserving.
    """
    
    entry_id: str
    """Unique identifier for this history entry."""
    
    entry_type: str
    """Type of event (e.g., 'request_created', 'target_evaluated', 'delivered')."""
    
    timestamp_semantic_time: str
    """Semantic time reference for when this occurred."""
    
    data_ref: Optional[str] = None
    """Reference to relevant data at time of event."""
    
    metadata: Tuple[str, ...] = field(default_factory=tuple)
    """Additional metadata about this entry."""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionHistory:
    """
    Immutable history record for a distribution.
    
    History may record:
        - Distribution Request created
        - Target evaluated (accepted/rejected/deferred/unavailable)
        - Projection created
        - Delivery Projection created
        - Acknowledgement received
        - Duplicate detected
        - Stale target detected
        - Conflict detected
        - Partial outcome produced
        - Distribution invalidated/superseded/completed
    
    History must be: immutable, append-only, bounded, deterministic,
    provenance-preserving.
    """
    
    identity: str
    """Identity of the distribution being recorded."""
    
    revision: int
    """Current revision of this history record."""
    
    distribution_ref: str
    """Reference to the distribution itself."""
    
    entries: Tuple[WorkspaceBroadcastDistributionHistoryEntry, ...]
    """Chronological list of historical events."""
    
    provenance_ref: str = ""
    """Reference to provenance trail for this history."""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionLineageRelation:
    """
    Relation between lineage nodes in the distribution graph.
    
    Lineage must preserve exact revisions and semantic relationships.
    """
    
    relation_id: str
    """Unique identifier for this lineage relation."""
    
    relation_type: str
    """Type of relation (e.g., 'distributes', 'projects_to', 'derives_from')."""
    
    source_node_id: str
    """Source node in the relationship."""
    
    target_node_id: str
    """Target node in the relationship."""
    
    metadata: Tuple[str, ...] = field(default_factory=tuple)
    """Additional metadata about this relation."""


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionLineage:
    """
    Immutable lineage record for a distribution.
    
    Lineage preserves relationships from Distribution Request through
    Target Projections to Delivery Projections and Acknowledgements.
    
    Valid relations:
        - Distributes Broadcast
        - Projects to Target
        - Delivery derived from Projection
        - Acknowledgement responds to Delivery
        - Outcome derived from Response
        - Revises Distribution
        - Supersedes Distribution
        - Invalidates Distribution
        - Migrated from Distribution
    """
    
    identity: str
    """Unique identifier for this lineage record."""
    
    revision: int
    """Current revision of this lineage record."""
    
    distribution_ref: str
    """Reference to the distribution itself."""
    
    nodes: Tuple[str, ...]
    """Nodes in the lineage graph (references)."""
    
    relations: Tuple[WorkspaceBroadcastDistributionLineageRelation, ...]
    """Semantic relationships between nodes."""
    
    provenance_ref: str = ""
    """Reference to provenance trail."""


# =============================================================================
# INVALIDATION AND CONTINUATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionInvalidation:
    """
    Immutable record of distribution invalidation.
    
    Invalidation represents when a distribution is no longer considered valid,
    without deleting the artifact (preserves history).
    
    Invalidation does NOT retract runtime messages directly. It produces
    semantic invalidation artifacts for runtime coordination.
    """
    
    invalidation_id: str
    """Unique identifier for this invalidation record."""
    
    invalidation_kind: str
    """Kind of invalidation that occurred."""
    
    invalidating_ref: str
    """Reference to what caused the invalidation."""
    
    invalidated_distribution_ref: str
    """Reference to the distribution being invalidated."""
    
    reason: str
    """Explanation for why this invalidation occurred."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time anchor for this invalidation."""
    
    @property
    def is_broadcast_related(self) -> bool:
        """Check if invalidation is related to Broadcast changes."""
        return self.invalidation_kind in (
            "broadcast_revised",
            "broadcast_invalidated",
            "broadcast_expired",
        )
    
    @property
    def is_target_related(self) -> bool:
        """Check if invalidation is related to Target State changes."""
        return self.invalidation_kind in (
            "target_revised",
            "target_invalidated",
            "target_capability_revised",
        )


class WorkspaceBroadcastDistributionInvalidationReason(Enum):
    """
    Canonical invalidation reasons.
    """
    
    BROADCAST_REVISED = "broadcast_revised"
    BROADCAST_INVALIDATED = "broadcast_invalidated"
    BROADCAST_EXPIRED = "broadcast_expired"
    TARGET_REVISED = "target_revised"
    TARGET_INVALIDATED = "target_invalidated"
    TARGET_CAPABILITY_REVISED = "target_capability_revised"
    DISCLOSURE_POLICY_REVISED = "disclosure_policy_revised"
    POLICY_REVISED = "policy_revised"
    SECURITY_REVISED = "security_revised"
    PRIVACY_REVISED = "privacy_revised"
    AUTHORITY_REVOKED = "authority_revoked"
    SCOPE_CHANGED = "scope_changed"
    ACKNOWLEDGEMENT_CONFLICT = "acknowledgement_conflict"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionContinuation:
    """
    Immutable record of a semantic continuation request.
    
    Continuation represents a decision about what to do next with the
    distribution, without performing any runtime operations.
    
    `RETRY_VIA_RUNTIME_POLICY` is a semantic request to runtime infrastructure.
    The Continuation does NOT perform retry itself.
    """
    
    continuation_id: str
    """Unique identifier for this continuation request."""
    
    continuation_kind: str
    """Kind of continuation requested."""
    
    distribution_ref: Optional[str] = None
    """
    Reference to Distribution Request being continued (if applicable).
    For example, when proceeding to re-delivery or retry.
    """
    
    reason: str = ""
    """Explanation for why this continuation was requested."""
    
    semantic_time_ref: str = "semantic_time_origin"
    """Semantic time anchor for this continuation."""
    
    @property
    def is_runtime_request(self) -> bool:
        """
        Check if continuation requests runtime action.
        
        Runtime requests include RETRY_VIA_RUNTIME_POLICY and similar,
        which are semantic instructions to external infrastructure, not
        self-executing operations.
        """
        return self.continuation_kind in (
            "retry_via_runtime_policy",
        )
    
    @property
    def is_state_change(self) -> bool:
        """
        Check if continuation results in State change.
        
        State changes include invalidation and supersession, which produce
        new artifacts rather than modifying existing ones.
        """
        return self.continuation_kind in (
            "invalidate_distribution",
            "supersede_distribution",
        )


class WorkspaceBroadcastDistributionContinuationKind(Enum):
    """
    Canonical continuation kinds for distributions.
    """
    
    # Continue with current distribution
    NONE = "none"
    """No continuation needed."""
    
    COMPLETE = "complete"
    """Distribution completed successfully."""
    
    REQUEST_TARGET_PROJECTION = "request_target_projection"
    REQUEST_TARGET_AVAILABILITY = "request_target_availability"
    REQUEST_POLICY_REVIEW = "request_policy_review"
    REQUEST_SECURITY_REVIEW = "request_security_review"
    REQUEST_DISCLOSURE_REVIEW = "request_disclosure_review"
    REQUEST_AUTHORITY = "request_authority"
    
    CREATE_DELIVERY_PROJECTIONS = "create_delivery_projections"
    WAIT_FOR_ACKNOWLEDGEMENTS = "wait_for_acknowledgements"
    PROCESS_ACKNOWLEDGEMENTS = "process_acknowledgements"
    REVISE_TARGET_PROJECTION = "revise_target_projection"
    
    RETRY_VIA_RUNTIME_POLICY = "retry_via_runtime_policy"
    """Semantic request to runtime infrastructure for retry."""
    
    DEFER_TARGET = "defer_target"
    DROP_OPTIONAL_TARGET = "drop_optional_target"
    REBUILD_DISTRIBUTION = "rebuild_distribution"
    INVALIDATE_DISTRIBUTION = "invalidate_distribution"
    SUPERSEDE_DISTRIBUTION = "supersede_distribution"
    
    PROPOSE_STATE_DELTA = "propose_state_delta"
    PROCEED_TO_ACTIVATION_CONTINUITY = "proceed_to_activation_continuity"
    
    SUSPEND = "suspend"
    TERMINATE = "terminate"
    FAIL = "fail"
    UNKNOWN = "unknown"


# =============================================================================
# STATE INTEGRATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceDistributionStateDeltaProposal:
    """
    Immutable proposal for Workspace State Delta based on distribution results.
    
    Distribution results may propose typed operations to update Workspace State,
    but they must NOT mutate Workspace State directly. The proposal must reference
    exact revisions and preserve privacy and provenance.
    
    Potential typed operations:
        - ADD_DISTRIBUTION_REQUEST
        - ADD_TARGET_PROJECTION
        - ADD_DELIVERY_PROJECTION
        - ADD_ACKNOWLEDGEMENT
        - ADD_REJECTION
        - ADD_DEFERRAL
        - ADD_PARTIAL_DELIVERY
        - ADD_DISTRIBUTION_OUTCOME
        - ADD_TARGET_BLOCKER
        - RESOLVE_TARGET_BLOCKER
        - INVALIDATE_DISTRIBUTION
        - SUPERSEDE_DISTRIBUTION
        - SET_DISTRIBUTION_CONTINUATION
    
    The proposal must reference:
        - Exact Workspace Network State revision
        - Exact Distribution revision
        - Exact Broadcast revision
        - Exact acknowledgement revisions
        - Expected target State revision
        - Authority
        - Privacy
        - Provenance
    
    It must NOT mutate Workspace State directly.
    """
    
    delta_id: str
    """Unique identifier for this State Delta proposal."""
    
    # Source references (for revision tracking)
    workspace_state_revision_ref: str
    """Reference to Workspace Network State revision that this delta extends."""
    
    distribution_ref: str
    """Reference to Distribution Request producing this delta."""
    
    broadcast_ref: str = ""
    """Reference to source Broadcast (NOT ownership)."""
    
    # Typed operations
    add_distribution_request: Optional[WorkspaceBroadcastDistributionRequest] = None
    
    add_target_projection: Optional[WorkspaceBroadcastTargetProjection] = None
    
    add_delivery_projection: Optional[WorkspaceBroadcastDeliveryProjection] = None
    
    add_acknowledgement: Optional[WorkspaceBroadcastAcknowledgement] = None
    
    add_rejection: Optional[WorkspaceBroadcastDistributionRejection] = None
    
    add_deferral: Optional[WorkspaceBroadcastDistributionDeferral] = None
    
    add_partial_delivery: Optional[WorkspaceBroadcastPartialDelivery] = None
    
    add_distribution_outcome: Optional[WorkspaceBroadcastDistributionOutcome] = None
    
    # State management operations
    add_target_blocker: Optional[str] = None
    """Reference to target that is blocking further distribution."""
    
    resolve_target_blocker: Optional[str] = None
    """Reference to target whose blocker status should be resolved."""
    
    invalidate_distribution: Optional[WorkspaceBroadcastDistributionInvalidation] = None
    
    supersede_distribution: Optional[str] = None
    """Reference to distribution being superseded."""
    
    set_distribution_continuation: Optional[WorkspaceBroadcastDistributionContinuation] = None
    
    # Constraints and provenance
    authority_ref: str = ""
    
    privacy_class: str = "internal_only"
    
    semantic_time_ref: str = "semantic_time_origin"
    
    provenance_ref: str = ""


# =============================================================================
# VALIDATION
# =============================================================================

WorkspaceBroadcastDistributionValidationResultKind = str


@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastDistributionValidationResult:
    """
    Immutable validation result for a distribution artifact.
    
    Validation is side-effect-free. It must NOT perform delivery, repair silently,
    query targets, invoke Core, or mutate State.
    
    Valid statuses include:
        - VALID
        - VALID_WITH_WARNINGS
        - VALID_WITH_LIMITATIONS
        - INCOMPLETE
        - PARTIAL
        - STALE
        - EXPIRED
        - DUPLICATE
        - CONFLICTING
        - TARGET_UNAVAILABLE
        - TARGET_INELIGIBLE
        - ACKNOWLEDGEMENT_REQUIRED
        - POLICY_REVIEW_REQUIRED
        - SECURITY_REVIEW_REQUIRED
        - DISCLOSURE_REVIEW_REQUIRED
        - AUTHORITY_REQUIRED
        - CAPACITY_LIMITED
        - INVALID
        - UNKNOWN
    """
    
    validation_id: str
    """Unique identifier for this validation."""
    
    artifact_ref: str
    """Reference to artifact being validated (NOT ownership)."""
    
    # Validation result
    is_valid: bool = False
    
    status: WorkspaceBroadcastDistributionValidationResultKind
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Warnings encountered during validation."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """Errors that prevented full validity."""
    
    # Specific checks
    is_stale: bool = False
    
    is_duplicate: bool = False
    
    has_conflicts: bool = False
    
    target_unavailable_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    target_ineligible_refs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Recommendations
    requires_acknowledgement: bool = False
    
    requires_policy_review: bool = False
    
    requires_security_review: bool = False
    
    requires_disclosure_review: bool = False
    
    requires_authority: bool = False
    
    capacity_limited: bool = False
    
    # Semantic and provenance
    validated_at_semantic_time: str = "semantic_time_origin"
    
    privacy_class: str = "internal_only"
    
    provenance_ref: str = ""


# =============================================================================
# PRIVACY AND PROVENANCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspacePrivacy:
    """
    Immutable privacy classification for a distribution artifact.
    
    Privacy controls what information may be disclosed and to whom. It is
    separate from Policy (rules) and Security (authentication/authorization).
    """
    
    # Classification level
    classification: str = "internal_only"
    """
    Valid values:
        - "public" - Available to all eligible consumers
        - "workspace_internal" - Within workspace only
        - "network_internal" - Within specific network only
        - "team_internal" - Within team/department only
        - "owner_only" - Owner-only disclosure
        - "user_private" - User private (maximally restricted)
    """
    
    # Field-level privacy rules
    redact_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that must be redacted."""
    
    anonymize_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that must be anonymized."""
    
    encrypt_fields: Tuple[str, ...] = field(default_factory=tuple)
    """Fields that must be encrypted at rest."""
    
    # Access control
    allowed_consumer_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to consumers that may receive this artifact."""
    
    required_auth_ref: Optional[str] = None
    """Reference to authorization that must be present."""
    
    # Retention
    retention_semantic_time: Optional[str] = None
    
    @property
    def is_maximally_restricted(self) -> bool:
        """
        Check if privacy is maximally restricted (owner-only or user-private).
        """
        return self.classification in ("owner_only", "user_private")
    
    @property
    def is_public(self) -> bool:
        """Check if privacy allows public disclosure."""
        return self.classification == "public"


@dataclass(frozen=True, slots=True)
class WorkspaceDistributionProvenance:
    """
    Immutable provenance record for a distribution artifact.
    
    Provenance preserves the chain of custody from original source through
    all transformations to final delivery. It is critical for audit and
    accountability.
    """
    
    provenance_id: str
    """Unique identifier for this provenance."""
    
    # Source information
    origin_ref: str
    """Reference to original source artifact."""
    
    origin_kind: str = ""
    """Kind of origin (e.g., 'workspace_broadcast', 'selection_outcome')."""
    
    # Transformation history
    transformations: Tuple[str, ...] = field(default_factory=tuple)
    """References to transformation steps."""
    
    # Chain of custody
    custody_chain: Tuple[Tuple[str, str], ...] = field(
        default_factory=tuple
    )
    """
    Chain of custody records.
    
    Format: [(agent_id, timestamp_semantic_time), ...]
    """
    
    # Audit trail
    audit_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to related audit records."""
    
    # Semantic time anchor
    semantic_time_ref: str = "semantic_time_origin"
    
    @property
    def chain_length(self) -> int:
        """Return length of provenance custody chain."""
        return len(self.custody_chain)


# =============================================================================
# ARCHITECTURAL LAWS
# =============================================================================

ARCHITECTURAL_LAWS = """
WORKSPACE-DIST-LAW-001: Distribution is semantic coordination, not runtime transport.
WORKSPACE-DIST-LAW-002: Every Distribution Request references one exact Broadcast revision.
WORKSPACE-DIST-LAW-003: Every Target Projection references one exact target revision.
WORKSPACE-DIST-LAW-004: Target-specific projection scope never exceeds Broadcast scope.
WORKSPACE-DIST-LAW-005: Distribution uses least disclosure sufficient for purpose.
WORKSPACE-DIST-LAW-006: Consumers remain externally owned.
WORKSPACE-DIST-LAW-007: Working Memory admission remains externally owned.
WORKSPACE-DIST-LAW-008: Memory encoding remains externally owned.
WORKSPACE-DIST-LAW-009: Target processing is never implemented by semantic distribution contracts.
WORKSPACE-DIST-LAW-010: Delivery Projections contain no transport implementation.
WORKSPACE-DIST-LAW-011: Acknowledgements reference exact Delivery Projection revisions.
WORKSPACE-DIST-LAW-012: Acknowledgement does not imply target processing success unless explicitly stated.
WORKSPACE-DIST-LAW-013: Duplicate acknowledgements produce no duplicate semantic State effects.
WORKSPACE-DIST-LAW-014: Conflicting authoritative responses use no silent last-write-wins.
WORKSPACE-DIST-LAW-015: Stale target responses are explicit.
WORKSPACE-DIST-LAW-016: Distribution fan-out and fan-in are bounded.
WORKSPACE-DIST-LAW-017: Distribution ordering is deterministic.
WORKSPACE-DIST-LAW-018: Distribution changes Workspace State only through typed Delta proposals.
WORKSPACE-DIST-LAW-019: All public distribution artifacts are deeply immutable.
WORKSPACE-DIST-LAW-020: Package import performs no delivery, discovery, or runtime work.
"""

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Identity types
    "WorkspaceBroadcastDistributionIdentity",
    "WorkspaceBroadcastDistributionRevision",
    "WorkspaceBroadcastDistributionReference",
    
    # Distribution Request
    "WorkspaceBroadcastDistributionPurpose",
    "WorkspaceBroadcastDistributionScope",
    "WorkspaceDistributionAuthorityRequirement",
    "WorkspaceDistributionAuthority",
    "WorkspaceBroadcastDistributionRequest",
    
    # Target semantics
    "WorkspaceBroadcastTargetKind",
    "WorkspaceBroadcastTargetEligibilityStatus",
    "WorkspaceBroadcastTargetAvailabilityStatus",
    "WorkspaceBroadcastTargetEligibility",
    "WorkspaceBroadcastTargetAvailability",
    "WorkspaceBroadcastTargetCapabilityProjection",
    
    # Disclosure policy
    "WorkspaceDistributionDisclosureLevel",
    "WorkspaceDistributionFieldRule",
    "WorkspaceDistributionDisclosurePolicy",
    
    # Projections
    "WorkspaceBroadcastTargetProjectionKind",
    "WorkspaceBroadcastTargetProjectionIdentity",
    "WorkspaceBroadcastTargetProjectionReference",
    "WorkspaceBroadcastTargetProjection",
    
    # Working Memory projections
    "WorkspaceWorkingMemoryProjection",
    "WorkspaceWorkingMemoryAdmissionProjection",
    "WorkspaceWorkingMemoryAcknowledgement",
    
    # Memory encoding projections
    "WorkspaceMemoryEncodingEligibilityProjection",
    "WorkspaceMemoryEncodingAcknowledgement",
    
    # Network-specific projections
    "WorkspaceExecutiveBroadcastProjection",
    "WorkspaceExecutiveBroadcastAcknowledgement",
    "WorkspaceDecisionBroadcastProjection",
    "WorkspaceDecisionBroadcastAcknowledgement",
    "WorkspaceAttentionBroadcastProjection",
    "WorkspaceAttentionBroadcastAcknowledgement",
    "WorkspaceAlertingBroadcastProjection",
    "WorkspaceAlertingBroadcastAcknowledgement",
    "WorkspaceFocusingBroadcastProjection",
    "WorkspaceFocusingBroadcastAcknowledgement",
    "WorkspaceDefaultNetworkBroadcastProjection",
    "WorkspaceDefaultNetworkBroadcastAcknowledgement",
    "WorkspaceMotivationBroadcastProjection",
    "WorkspaceMotivationBroadcastAcknowledgement",
    "WorkspaceReasoningBroadcastProjection",
    "WorkspaceReasoningBroadcastAcknowledgement",
    "WorkspacePlanningBroadcastProjection",
    "WorkspacePlanningBroadcastAcknowledgement",
    "WorkspacePerceptionBroadcastProjection",
    "WorkspacePerceptionBroadcastAcknowledgement",
    "WorkspaceLearningBroadcastProjection",
    "WorkspaceLearningBroadcastAcknowledgement",
    "WorkspacePredictionBroadcastProjection",
    "WorkspacePredictionBroadcastAcknowledgement",
    "WorkspaceWorldModelBroadcastProjection",
    "WorkspaceWorldModelBroadcastAcknowledgement",
    "WorkspaceMonitoringBroadcastProjection",
    "WorkspaceMonitoringBroadcastAcknowledgement",
    "WorkspaceRecoveryBroadcastProjection",
    "WorkspaceRecoveryBroadcastAcknowledgement",
    
    # Delivery Projections
    "WorkspaceDistributionRequirement",
    "WorkspaceDistributionRequirementKind",
    "WorkspaceDistributionConstraint",
    "WorkspaceDistributionConstraintKind",
    "WorkspaceBroadcastDeliveryProjectionIdentity",
    "WorkspaceBroadcastDeliveryProjectionReference",
    "WorkspaceBroadcastDeliveryProjection",
    
    # Acknowledgements
    "WorkspaceAcknowledgementPolicy",
    "WorkspaceBroadcastAcknowledgementKind",
    "WorkspaceBroadcastAcknowledgementIdentity",
    "WorkspaceBroadcastAcknowledgementReference",
    "WorkspaceBroadcastAcknowledgement",
    
    # Rejections and deferrals
    "WorkspaceBroadcastDistributionRejection",
    "WorkspaceBroadcastDistributionRejectionReason",
    "WorkspaceBroadcastDistributionDeferral",
    
    # Partial delivery
    "WorkspaceBroadcastPartialDelivery",
    
    # Duplicate handling
    "WorkspaceBroadcastDuplicateDeliveryAssessment",
    
    # Stale target handling
    "WorkspaceBroadcastStaleTargetAssessment",
    "WorkspaceBroadcastStaleTargetReason",
    
    # Conflicts
    "WorkspaceBroadcastDeliveryConflict",
    "WorkspaceBroadcastDeliveryConflictKind",
    
    # Correlation and causation
    "WorkspaceDistributionCorrelationId",
    "WorkspaceDistributionCorrelationReference",
    "WorkspaceDistributionCorrelationContext",
    "WorkspaceDistributionCausationReference",
    "WorkspaceDistributionCausationRelation",
    
    # Dispositions and outcomes
    "WorkspaceBroadcastDistributionDisposition",
    "WorkspaceBroadcastDistributionOutcomeIdentity",
    "WorkspaceBroadcastDistributionOutcomeReference",
    "WorkspaceBroadcastDistributionOutcome",
    "WorkspaceBroadcastDistributionCompleteness",
    "WorkspaceBroadcastDistributionValidity",
    
    # Bounds
    "WorkspaceDistributionFanOutBounds",
    "WorkspaceDistributionFanInBounds",
    
    # Target ordering
    "WorkspaceDistributionTargetOrder",
    
    # History and lineage
    "WorkspaceBroadcastDistributionHistoryEntry",
    "WorkspaceBroadcastDistributionHistory",
    "WorkspaceBroadcastDistributionLineageRelation",
    "WorkspaceBroadcastDistributionLineage",
    
    # Invalidation and continuation
    "WorkspaceBroadcastDistributionInvalidation",
    "WorkspaceBroadcastDistributionInvalidationReason",
    "WorkspaceBroadcastDistributionContinuation",
    "WorkspaceBroadcastDistributionContinuationKind",
    
    # State integration
    "WorkspaceDistributionStateDeltaProposal",
    
    # Validation
    "WorkspaceBroadcastDistributionValidationResult",
    
    # Privacy and provenance
    "WorkspacePrivacy",
    "WorkspaceDistributionProvenance",
    
    # Architectural laws
    "ARCHITECTURAL_LAWS",
]