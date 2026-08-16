# Workspace Candidate Semantics
# =============================

"""
Canonical Workspace Candidate definitions.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - External time providers only
    - External identity providers only
    - Bounded collections
    - Semantic-time preservation

SEMANTIC MODEL OVERVIEW
=======================

Workspace Candidate represents a validated, admissible, immutable semantic 
projection of Workspace Content that is eligible for future Workspace evaluation.

A Candidate is NOT:
    - Workspace Content (the source)
    - a Competition Result
    - a Winner
    - a Broadcast
    - a Decision
    - an Action
    - a Plan

ADMISSION PIPELINE:
    
    Externally owned artifact
            ↓
    Workspace Content
            ↓
    Admission Request
            ↓
    Admission Validation
            ↓
    Admission Constraints
            ↓
    Admission Decision
            ↓
    Workspace Candidate
            ↓
    Candidate Pool

No evaluation occurs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Set
from enum import Enum


# =============================================================================
# IDENTITY TYPES - Immutable references
# =============================================================================

WorkspaceCandidateIdentity = str
"""
Unique identifier for a workspace candidate instance.

Must be:
    - Deterministically derived or externally supplied
    - Replayable (same input produces same output)
    - Never generated internally (no UUIDs, timestamps)

Examples: Content hash with prefix, source system ID with context.
"""


WorkspaceCandidateRevision = int
"""
Monotonically increasing revision number for candidates.

Revision rules:
    - Revision 1 is initial creation
    - Each semantic change requires a new revision
    - Identity + Revision = unique artifact reference

No in-place mutation allowed. Create new revision instead.
"""


WorkspaceCandidateReference = str
"""
Immutable reference to Workspace Candidate.

Format: "identity@revision"
Examples:
    "candidate_abc123@1"
    "insight_from_reasoning@5"

Used for linking without ownership.
"""


# =============================================================================
# CANDIDATE FINGERPRINT - Semantic integrity
# =============================================================================

WorkspaceCandidateFingerprint = str
"""
Short fingerprint for quick identification and comparison.

Purpose: Fast lookup, duplicate detection, indexing.

Rules:
    - Always deterministically derived from identity
    - May be shorter than full digest
    - Must be stable across runs (same input = same output)

Examples: First 8 characters of digest, hash prefix.
"""


WorkspaceCandidateDigest = str
"""
Cryptographic or deterministic digest of candidate semantic content.

Purpose: Verify integrity, detect changes, ensure replayability.

Rules:
    - Derived from semantic representation (not runtime state)
    - Must be deterministic (same input = same output)
    - Never use timestamps, UUIDs, or random values in calculation

Examples: SHA-256 hash of candidate data structure.
"""


# =============================================================================
# CANDIDATE KINDS TAXONOMY
# =============================================================================

class WorkspaceCandidateKind(Enum):
    """
    Canonical categories of semantic content proposed as candidates.
    
    This taxonomy is extensible. New kinds may be added without modifying core semantics.
    """

    # =========================================================================
    # PERCEPTUAL CONTENT - From external sensory input
    # =========================================================================

    PERCEPTUAL_INPUT = "perceptual_input"
    """Raw or minimally processed sensory data."""

    VISUAL_PERCEPTION = "visual_perception"
    """Visual sensor readings (images, video frames)."""

    AUDIO_PERCEPTION = "audio_perception"
    """Audio sensor readings."""

    TEXT_PERCEPTION = "text_perception"
    """Text input from external sources."""

    # =========================================================================
    # REASONING CONTENT - Logical and inference artifacts
    # =========================================================================

    REASONING_RESULT = "reasoning_result"
    """Conclusion from logical inference."""

    DEDUCTION = "deduction"
    """Deductive reasoning result."""

    INDUCTION = "induction"
    """Inductive reasoning result."""

    ABDUCTION = "abduction"
    """Abductive reasoning result (best explanation)."""

    REASONING_CHAIN = "reasoning_chain"
    """Complete chain of reasoning steps."""

    # =========================================================================
    # GOAL CONTENT - Objective-related information
    # =========================================================================

    GOAL_STATEMENT = "goal_statement"
    """Explicit goal formulation."""

    OBJECTIVE = "objective"
    """High-level objective or purpose."""

    SUBGOAL = "subgoal"
    """Intermediate goal toward larger objective."""

    GOAL_PROGRESS = "goal_progress"
    """Progress report for a goal."""

    # =========================================================================
    # TASK CONTENT - Action-related information
    # =========================================================================

    TASK_DECLARATION = "task_declaration"
    """Statement of a task to be performed."""

    TASK_STEP = "task_step"
    """Individual step within a task."""

    TASK_SEQUENCE = "task_sequence"
    """Ordered sequence of tasks."""

    # =========================================================================
    # EXECUTIVE CONTENT - Coordination and control
    # =========================================================================

    DECISION_PROPOSAL = "decision_proposal"
    """Proposed decision for consideration."""

    EXECUTIVE_SUMMARY = "executive_summary"
    """High-level summary for executive review."""

    STRATEGY_PROPOSAL = "strategy_proposal"
    """Proposed strategy or approach."""

    # =========================================================================
    # PLANNING CONTENT - Temporal and strategic
    # =========================================================================

    PLAN_OUTLINE = "plan_outline"
    """High-level plan structure."""

    EXECUTION_PLAN = "execution_plan"
    """Detailed execution plan with steps."""

    TIMELINE = "timeline"
    """Temporal sequence of events."""

    # =========================================================================
    # PREDICTION CONTENT - Forecasts and expectations
    # =========================================================================

    PREDICTION = "prediction"
    """Forecast of future state."""

    EXPECTATION = "expectation"
    """Expected outcome or result."""

    SCENARIO = "scenario"
    """Plausible future scenario."""

    # =========================================================================
    # LEARNING CONTENT - Knowledge acquisition
    # =========================================================================

    LEARNED_PATTERN = "learned_pattern"
    """Pattern identified from experience."""

    GENERALIZATION = "generalization"
    """General principle derived from examples."""

    METACOGNITIVE_INSIGHT = "metacognitive_insight"
    """Insight about the agent's own reasoning process."""

    # =========================================================================
    # IDENTITY CONTENT - Self-concept and role
    # =========================================================================

    ROLE_DEFINITION = "role_definition"
    """Definition of a role or responsibility."""

    CAPABILITY_DECLARATION = "capability_declaration"
    """Statement of capabilities."""

    COMMITMENT = "commitment"
    """Explicit commitment or pledge."""

    # =========================================================================
    # MOTIVATIONAL CONTENT - Drive and direction
    # =========================================================================

    VALUE_STATEMENT = "value_statement"
    """Statement of core values."""

    PREFERENCE = "preference"
    """Preferred outcome or approach."""

    NEED = "need"
    """Fundamental need or requirement."""

    # =========================================================================
    # EMOTIONAL CONTENT - Affective state
    # =========================================================================

    EMOTIONAL_STATE = "emotional_state"
    """Report of affective state."""

    FEELING = "feeling"
    """Specific emotional feeling."""

    MOOD = "mood"
    """Extended affective background."""

    # =========================================================================
    # ENVIRONMENTAL CONTENT - Contextual information
    # =========================================================================

    ENVIRONMENT_STATE = "environment_state"
    """State of the external environment."""

    SITUATION_REPORT = "situation_report"
    """Current situation assessment."""

    CONTEXT_SUMMARY = "context_summary"
    """Summary of relevant context."""

    # =========================================================================
    # TEMPORAL CONTENT - Time-related
    # =========================================================================

    EVENT_REFERENCE = "event_reference"
    """Reference to a past event."""

    TEMPORAL_SEQUENCE = "temporal_sequence"
    """Sequence of temporal events."""

    DURATION_ESTIMATE = "duration_estimate"
    """Estimated duration for an activity."""

    # =========================================================================
    # SPATIAL CONTENT - Location-related
    # =========================================================================

    LOCATION_REFERENCE = "location_reference"
    """Reference to a location."""

    SPATIAL_RELATIONSHIP = "spatial_relationship"
    """Relationship between locations."""

    NAVIGATION_PLAN = "navigation_plan"
    """Plan for spatial navigation."""

    # =========================================================================
    # SOCIAL CONTENT - Interpersonal
    # =========================================================================

    RELATIONSHIP_DECLARATION = "relationship_declaration"
    """Statement about social relationships."""

    SOCIAL_NORM = "social_norm"
    """Described social norm or expectation."""

    COLLABORATIVE_GOAL = "collaborative_goal"
    """Goal shared across agents."""

    # =========================================================================
    # RISK CONTENT - Uncertainty and threat
    # =========================================================================

    RISK_ASSESSMENT = "risk_assessment"
    """Assessment of potential risk."""

    THREAT_REPORT = "threat_report"
    """Report of an identified threat."""

    VULNERABILITY_REPORT = "vulnerability_report"
    """Report of a vulnerability."""

    # =========================================================================
    # SECURITY CONTENT - Protection
    # =========================================================================

    SECURITY_POLICY = "security_policy"
    """Security policy statement."""

    ACCESS_REQUEST = "access_request"
    """Request for access authorization."""

    AUDIT_EVENT = "audit_event"
    """Record of an audit event."""

    # =========================================================================
    # POLICY CONTENT - Rules and governance
    # =========================================================================

    RULE_DECLARATION = "rule_declaration"
    """Formal rule or constraint."""

    POLICY_STATEMENT = "policy_statement"
    """Policy statement or guideline."""

    REGULATION_REFERENCE = "regulation_reference"
    """Reference to external regulation."""

    # =========================================================================
    # MONITORING CONTENT - Observation
    # =========================================================================

    METRIC_VALUE = "metric_value"
    """Observed metric value."""

    ANOMALY_DETECTION = "anomaly_detection"
    """Detection of anomalous behavior."""

    PERFORMANCE_REPORT = "performance_report"
    """Performance assessment report."""

    # =========================================================================
    # RECOVERY CONTENT - Restoration
    # =========================================================================

    FAILURE_REPORT = "failure_report"
    """Report of a failure or error."""

    RECOVERY_PLAN = "recovery_plan"
    """Plan for recovery from failure."""

    STATE_RESTORE = "state_restore"
    """Request to restore previous state."""

    # =========================================================================
    # SYSTEM CONTENT - Infrastructure
    # =========================================================================

    CONFIGURATION_STATEMENT = "configuration_statement"
    """Configuration state or parameter."""

    RESOURCE_REQUEST = "resource_request"
    """Request for resources."""

    SYSTEM_HEALTH_REPORT = "system_health_report"
    """Report on system health status."""

    # =========================================================================
    # DIAGNOSTIC CONTENT - Troubleshooting
    # =========================================================================

    ERROR_REPORT = "error_report"
    """Detailed error report."""

    DEBUG_INFORMATION = "debug_information"
    """Debug-related information."""

    TRACE_REFERENCE = "trace_reference"
    """Reference to execution trace."""

    # =========================================================================
    # META-COGNITIVE CONTENT - Self-reflection
    # =========================================================================

    COGNITIVE_STATEMENT = "cognitive_statement"
    """Statement about cognitive process."""

    METACOGNITION = "metacognition"
    """Thinking about thinking."""

    REASONING_REFLECTION = "reasoning_reflection"
    """Reflection on reasoning process."""

    # =========================================================================
    # ATTENTION CONTENT - Focus and salience
    # =========================================================================

    SALIENCE_ASSESSMENT = "salience_assessment"
    """Assessment of content salience."""

    FOCUS_REQUEST = "focus_request"
    """Request to focus attention."""

    ATTENTION_CUE = "attention_cue"
    """Cue directing attention."""

    # =========================================================================
    # ALERT CONTENT - Urgent notification
    # =========================================================================

    ALERT_NOTIFICATION = "alert_notification"
    """Alert notification for urgent matters."""

    CRITICAL_MESSAGE = "critical_message"
    """Critical priority message."""

    EMERGENCY_ALERT = "emergency_alert"
    """Emergency situation alert."""

    # =========================================================================
    # WORLD MODEL CONTENT - Semantic knowledge base
    # =========================================================================

    FACT_STATEMENT = "fact_statement"
    """Stated fact or known truth."""

    BELIEF_STATEMENT = "belief_statement"
    """Belief or hypothesis."""

    MODEL_UPDATE = "model_update"
    """Update to world model."""

    # =========================================================================
    # SIMULATION CONTENT - Hypothetical
    # =========================================================================

    SIMULATION_RESULT = "simulation_result"
    """Result from simulation run."""

    HYPOTHETICAL_STATEMENT = "hypothetical_statement"
    """Hypothetical scenario or statement."""

    IMAGINED_OUTCOME = "imagined_outcome"
    """Imagined possible outcome."""

    # =========================================================================
    # IMAGINATION CONTENT - Creative generation
    # =========================================================================

    CREATIVE_IDEA = "creative_idea"
    """Creative idea or concept."""

    IMAGINATION_RESULT = "imagination_result"
    """Result from imagination process."""

    SYMBOLIC_CONSTRUCTION = "symbolic_construction"
    """Symbolic representation or model."""

    # =========================================================================
    # CREATIVITY CONTENT - Novelty and innovation
    # =========================================================================

    NOVELTY_REPORT = "novelty_report"
    """Report of novel insight or creation."""

    INNOVATION_PROPOSAL = "innovation_proposal"
    """Proposal for innovation."""

    DESIGN_DESCRIPTION = "design_description"
    """Description of a design artifact."""

    # =========================================================================
    # UNKNOWN CONTENT - Undefined category
    # =========================================================================

    UNKNOWN_KIND = "unknown"
    """Unknown or unclassified content kind."""

    UNCLASSIFIED = "unclassified"
    """Content not yet classified."""

    CUSTOM_KIND = "custom"
    """Custom kind defined externally."""


# =============================================================================
# CANDIDATE STATE TAXONOMY
# =============================================================================

class WorkspaceCandidateState(Enum):
    """
    Canonical states in candidate lifecycle.
    
    These are semantic states, NOT runtime states.
    """

    # =========================================================================
    # SUBMISSION STATES
    # =========================================================================

    SUBMITTED = "submitted"
    """Candidate has been submitted for admission."""

    VALIDATED = "validated"
    """Candidate has passed validation checks."""

    ADMITTED = "admitted"
    """Candidate has been admitted to workspace."""

    # =========================================================================
    # EVALUATION STATES
    # =========================================================================

    DEFERRED = "deferred"
    """Admission deferred to later time."""

    RESTRICTED = "restricted"
    """Admission restricted pending conditions."""

    # =========================================================================
    # FINAL STATES
    # =========================================================================

    SUSPENDED = "suspended"
    """Candidate suspended temporarily."""

    RESTORED = "restored"
    """Previously suspended candidate restored."""

    WITHDRAWN = "withdrawn"
    """Candidate withdrawn by submitter."""

    EXPIRED = "expired"
    """Candidate expired (time-based)."""

    INVALIDATED = "invalidated"
    """Candidate invalidated by authority."""

    ARCHIVED = "archived"
    """Historical preservation state."""

    TERMINATED = "terminated"
    """Final termination of candidate life cycle."""


# =============================================================================
# ELIGIBILITY TAXONOMY
# =============================================================================

class WorkspaceEligibility(Enum):
    """
    Canonical eligibility states for candidates.
    
    Eligibility is semantic - it is NOT a runtime state.
    """

    # =========================================================================
    # VALID STATES
    # =========================================================================

    ELIGIBLE = "eligible"
    """Candidate meets all eligibility requirements."""

    CONDITIONALLY_ELIGIBLE = "conditionally_eligible"
    """Candidate eligible pending conditions."""

    # =========================================================================
    # PENDING STATES
    # =========================================================================

    DEFERRED_ELIGIBILITY = "deferred_eligibility"
    """Eligibility assessment deferred."""

    RESTRICTED_ELIGIBILITY = "restricted_eligibility"
    """Eligibility restricted by constraints."""

    PENDING_ELIGIBILITY = "pending_eligibility"
    """Eligibility assessment pending."""

    # =========================================================================
    # EXCLUDED STATES
    # =========================================================================

    REJECTED = "rejected"
    """Candidate rejected - not eligible."""

    SUSPENDED_ELIGIBILITY = "suspended_eligibility"
    """Eligibility suspended temporarily."""

    RESTORED_ELIGIBILITY = "restored_eligibility"
    """Previously suspended eligibility restored."""

    EXPIRED_ELIGIBILITY = "expired_eligibility"
    """Eligibility expired (time-based)."""

    WITHDRAWN_ELIGIBILITY = "withdrawn_eligibility"
    """Eligibility withdrawn by submitter."""

    INVALIDATED_ELIGIBILITY = "invalidated_eligibility"
    """Eligibility invalidated by authority."""

    UNKNOWN_ELIGIBILITY = "unknown_eligibility"
    """Eligibility status unknown."""


# =============================================================================
# CANDIDATE STATUS TAXONOMY
# =============================================================================

class WorkspaceCandidateStatus(Enum):
    """
    Canonical status states for candidates.
    
    Status represents the current point in the admission pipeline.
    """

    PENDING = "pending"
    """Waiting for validation."""

    VALIDATING = "validating"
    """Currently being validated."""

    VALIDATION_FAILED = "validation_failed"
    """Validation failed."""

    ADMISSIBLE = "admissible"
    """Passed validation, ready for admission decision."""

    ADMISSION_PENDING = "admission_pending"
    """Waiting for admission decision."""

    ADMISSION_REJECTED = "admission_rejected"
    """Admission rejected."""

    DEFERRED_STATUS = "deferred_status"
    """Admission deferred."""

    SUSPENDED_STATUS = "suspended_status"
    """Suspended pending conditions."""

    RESTORED_STATUS = "restored_status"
    """Previously suspended, restored."""

    EXPIRED_STATUS = "expired_status"
    """Expired (time-based)."""

    WITHDRAWN_STATUS = "withdrawn_status"
    """Withdrawn by submitter."""

    INVALIDATED_STATUS = "invalidated_status"
    """Invalidated by authority."""

    ADMITTED_STATUS = "admitted_status"
    """Admitted to workspace."""


# =============================================================================
# CANDIDATE VALIDITY TAXONOMY
# =============================================================================

class WorkspaceCandidateValidity(Enum):
    """
    Canonical validity states for candidates.
    
    Validity assesses whether the candidate meets semantic requirements.
    """

    # =========================================================================
    # VALID STATES
    # =========================================================================

    VALID = "valid"
    """Meets all semantic requirements."""

    INVALID = "invalid"
    """Fails required checks."""

    # =========================================================================
    # TEMPORAL STATES
    # =========================================================================

    STALE = "stale"
    """May have expired validity."""

    SUPERSEDED = "superseded"
    """Replaced by newer revision."""

    PROVISIONAL = "provisional"
    """Temporary validity, pending verification."""

    TENTATIVE = "tentative"
    """Preliminary validity assessment."""

    VERIFIED = "verified"
    """Verified against external sources."""

    UNVERIFIED = "unverified"
    """Not externally verified."""

    # =========================================================================
    # RELATIONAL STATES
    # =========================================================================

    CONFLICTED = "conflicted"
    """Conflicts with other valid content."""

    WITHDRAWN_VALIDITY = "withdrawn_validity"
    """Withdrawn by authority."""


# =============================================================================
# CANDIDATE SEMANTIC CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateContext:
    """
    Immutable context for workspace candidate.

    Context provides semantic framing without embedding runtime objects.
    It describes the circumstances and conditions surrounding a candidate.

    ARCHITECTURAL INVARIANTS:
        WCX-INV-001: Context never becomes part of candidate identity
        WCX-INV-002: Context is never executable
        WCX-INV-003: Context has no runtime time acquisition

    NOT RESPONSIBLE FOR:
        - Runtime state embedding
        - Time-based evaluation
        - External system interaction
    """

    # Source information
    source_network: str = ""
    """Network that originated the candidate content."""

    source_package: str = ""
    """Package within the source network."""

    source_artifact_id: Optional[str] = None
    """Reference to original artifact (NOT ownership)."""

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
    """Types of consumers this candidate is intended for."""

    relevance_score: float = 0.5
    """Relevance assessment without runtime time acquisition."""

    @classmethod
    def from_reflection(cls, thought_id: str = "") -> WorkspaceCandidateContext:
        """
        Create context for reflection-originated content.
        
        Args:
            thought_id: ID of the reflecting thought (optional)
            
        Returns:
            New context with reflection source information.
        """
        return cls(
            source_network="DEFAULT_NETWORK",
            source_package="reflection",
            correlation_id=f"reflect_{thought_id}" if thought_id else "semantic_time_origin",
        )

    @classmethod
    def for_executive(cls, correlation_id: str) -> WorkspaceCandidateContext:
        """
        Create context from Executive coordination.

        Args:
            correlation_id: Correlation ID from executive

        Returns:
            New WorkspaceCandidateContext instance
        """
        return cls(
            source_network="EXECUTIVE_NETWORK",
            source_package="coordination",
            correlation_id=correlation_id,
            executive_context="COORDINATION",
        )

    @classmethod
    def for_planning(cls, task_id: str) -> WorkspaceCandidateContext:
        """Create context for planning content."""
        return cls(
            source_network="DEFAULT_NETWORK",
            source_package="planning",
            correlation_id=f"plan_{task_id}",
            task_context="PLANNING_PHASE",
            planning_context="STRATEGIC",
        )

    @classmethod
    def for_decision(cls, decision_id: str) -> WorkspaceCandidateContext:
        """Create context for decision content."""
        return cls(
            source_network="EXECUTIVE_NETWORK",
            source_package="decisions",
            correlation_id=f"dec_{decision_id}",
            decision_context="EVALUATION_AND_SELECTION",
        )

    @classmethod
    def for_reasoning(cls, reasoning_id: str) -> WorkspaceCandidateContext:
        """Create context for reasoning content."""
        return cls(
            source_network="DEFAULT_NETWORK",
            source_package="reasoning",
            correlation_id=f"reason_{reasoning_id}",
            reasoning_context="DEDUCTIVE",
        )


# =============================================================================
# CANDIDATE SCOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateScope:
    """
    Immutable scope specification for workspace candidate.

    Scope defines which systems may receive and how the candidate is processed.
    It is independent of runtime state and execution.

    ARCHITECTURAL INVARIANTS:
        WCS-INV-001: Scope never determines broadcast delivery (runtime does)
        WCS-INV-002: Scope never acquires runtime time
        WCS-INV-003: Scope is always bounded

    NOT RESPONSIBLE FOR:
        - Runtime broadcast execution
        - Target capability mutation
        - Time-based scope evaluation
    """

    # Consumer scope
    target_audiences: Tuple[str, ...] = field(default_factory=tuple)
    """Audience kinds eligible to consume this candidate."""

    minimum_confidence: float = 0.5
    """Minimum confidence threshold for consumers (0.0-1.0)."""

    broadcast_depth: int = 3
    """Maximum depth of broadcast propagation (bounded, max 10)."""

    disclosure_level: str = "internal_only"
    """Disclosure classification for the candidate."""

    # Authority scope
    authority_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints on which authorities may process this candidate."""

    # Privacy scope
    privacy_classification: str = "internal_only"
    """Privacy classification for disclosure control."""

    # Visibility scope
    visibility_limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Specific systems or networks that may see this candidate."""

    # Accessibility scope
    accessibility_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for accessibility."""

    # Broadcast eligibility
    broadcast_eligible: bool = True
    """Whether this candidate is eligible for broadcast."""

    @classmethod
    def for_general_workspace(cls) -> WorkspaceCandidateScope:
        """
        Create scope for general workspace availability.

        Returns:
            Scope suitable for broad distribution within workspace.
        """
        return cls(
            target_audiences=("working_memory", "reasoning", "planning"),
            minimum_confidence=0.7,
            broadcast_depth=2,
            disclosure_level="internal_only",
            privacy_classification="internal_only",
            broadcast_eligible=True,
        )

    @classmethod
    def for_executive_review(cls) -> WorkspaceCandidateScope:
        """
        Create scope for Executive review.

        Returns:
            Scope suitable only for executive systems.
        """
        return cls(
            target_audiences=("executive",),
            minimum_confidence=0.9,
            broadcast_depth=1,
            disclosure_level="internal_only",
            privacy_classification="internal_only",
            broadcast_eligible=True,
        )

    @classmethod
    def for_public(cls) -> WorkspaceCandidateScope:
        """
        Create scope for public availability.

        Returns:
            Scope with minimal restrictions.
        """
        return cls(
            target_audiences=("all",),
            minimum_confidence=0.5,
            broadcast_depth=10,
            disclosure_level="public",
            privacy_classification="public",
            broadcast_eligible=True,
        )


# =============================================================================
# CANDIDATE VALIDITY INFORMATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateValidityInfo:
    """
    Immutable validity information for workspace candidate.

    Validity assesses whether the candidate meets canonical requirements.
    It is semantic only and does not require runtime evaluation.

    ARCHITECTURAL INVARIANTS:
        WCVAL-INV-001: Validity is independent of runtime state
        WCVAL-INV-002: Invalid content may still be broadcast (with warning)
        WCVAL-INV-003: Validity never implies truth

    VALIDITY STATES:
        valid       - Meets all semantic requirements
        invalid     - Fails required checks
        stale       - May have expired validity
        superseded  - Replaced by newer revision
        provisional - Temporary validity, pending verification
        tentative   - Preliminary validity assessment
        verified    - Verified against external sources
        unverified  - Not externally verified
        conflicted  - Conflicts with other valid content
        withdrawn   - Withdrawn by authority
    """

    # Validity assessment
    is_valid: bool = True
    """Whether this candidate meets semantic requirements."""

    validity_state: str = "valid"
    """Detailed validity state (see VALIDITY STATES)."""

    validation_errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation errors (if any)."""

    validity_threshold: float = 0.8
    """Minimum confidence threshold for validity assessment."""

    # Verification status
    verified: bool = False
    """Whether this candidate has been externally verified."""

    verification_source: Optional[str] = None
    """Reference to verification source (if verified)."""

    # Temporal validity
    is_stale: bool = False
    """Whether validity may have expired."""

    is_superseded: bool = False
    """Whether newer revision supersedes this one."""


# =============================================================================
# ADMISSION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceAdmissionRequest:
    """
    Immutable admission request for a candidate.

    An Admission Request represents an external proposal to admit a candidate
    into the workspace. It does NOT imply admission - that requires external
    authority decision.

    PROPERTIES:
        • request_id: Unique identifier for this request
        • candidate_identity: ID of the candidate being proposed
        • content_reference: Reference to WorkspaceContent revision
        • requester: Who is making this request (external)
        • authority: External authority responsible for admission
        • reason: Why this candidate should be admitted
        • intent: Purpose of the proposal
        • priority_ref: Priority reference for urgency
        • context: Semantic context for interpretation
        • scope: Broadcast scope requirements
        • policy_ref: Policy constraints to check
        • security_ref: Security classification
        • constraints: Explicit constraint declarations
        • evidence: Supporting evidence for eligibility
        • assumptions: Background assumptions for analysis

    ARCHITECTURAL INVARIANTS:
        WAR-INV-001: Admission requests are immutable
        WAR-INV-002: Requests never imply admission
        WAR-INV-003: Requesters have no inherent authority
    """

    # Request identity
    request_id: str
    """Unique identifier for this request."""

    # Candidate information
    candidate_identity: WorkspaceCandidateIdentity
    """ID of the candidate being proposed."""

    content_reference: str
    """Reference to WorkspaceContent revision being proposed."""

    # Authority information
    requester: Optional[str] = None
    """Entity making this request (external, not authority)."""

    authority: Optional[str] = None
    """External authority responsible for admission decision."""

    # Request content
    reason: str = ""
    """Human-readable explanation for proposal."""

    intent: str = "admit"
    """Admission intent (admit, review, assess)."""

    priority_reference: Optional[str] = None
    """Priority reference for urgency (external time provider)."""

    # Context and scope
    context: WorkspaceCandidateContext = field(
        default_factory=WorkspaceCandidateContext
    )
    """Semantic context for interpretation."""

    scope: WorkspaceCandidateScope = field(
        default_factory=WorkspaceCandidateScope.for_general_workspace
    )
    """Broadcast scope requirements."""

    # Constraints and constraints
    policy_reference: Optional[str] = None
    """Policy constraints to check against."""

    security_reference: Optional[str] = None
    """Security classification reference."""

    constraints: Tuple[WorkspaceCandidateConstraint, ...] = field(
        default_factory=tuple
    )
    """Explicit constraint declarations."""

    # Evidence and assumptions
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Supporting evidence for eligibility."""

    assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Background assumptions for analysis."""

    @classmethod
    def from_content(
        cls,
        request_id: str,
        candidate_identity: str,
        content_reference: str,
        requester: Optional[str] = None,
        authority: Optional[str] = None,
    ) -> WorkspaceAdmissionRequest:
        """
        Create an admission request from a content reference.

        Args:
            request_id: Unique identifier for this request
            candidate_identity: ID of the candidate being proposed
            content_reference: Reference to WorkspaceContent revision
            requester: External entity making this request (optional)
            authority: External authority responsible (optional)

        Returns:
            New WorkspaceAdmissionRequest instance
        """
        return cls(
            request_id=request_id,
            candidate_identity=candidate_identity,
            content_reference=content_reference,
            requester=requester,
            authority=authority,
            intent="admit",
            context=WorkspaceCandidateContext(),
            scope=WorkspaceCandidateScope.for_general_workspace(),
        )


@dataclass(frozen=True, slots=True)
class WorkspaceCandidateConstraint:
    """
    Immutable constraint specification for a candidate.

    Constraints represent requirements that must be satisfied for admission.
    They are semantic and do not include runtime enforcement logic.

    TYPES OF CONSTRAINTS:
        • privacy: Data privacy classification
        • security: Security level required
        • policy: Policy compliance requirement
        • ownership: Ownership verification needed
        • authority: Authority validation needed
        • consumer: Consumer eligibility requirements
        • scope: Broadcast scope limitations
        • dependency: Required dependencies
        • resource: Resource availability requirement
        • context: Context completeness requirement
        • temporal: Time-based constraints

    ARCHITECTURAL INVARIANTS:
        WCN-INV-001: Constraints are immutable
        WCN-INV-002: Constraints never enforce (only describe)
        WCN-INV-003: Constraint violation ≠ admission rejection
    """

    # Constraint identity
    constraint_id: str
    """Unique identifier for this constraint."""

    # Constraint type
    constraint_type: str  # privacy, security, policy, etc.
    """Type of constraint (see TYPES OF CONSTRAINTS)."""

    # Constraint specification
    requirement: str = ""
    """Requirement specification."""

    severity: str = "warning"  # warning, error, critical
    """Severity if constraint not satisfied."""

    # Enforcement information
    enforceable: bool = False
    """Whether this can be enforced (not all constraints are)."""

    enforcement_authority: Optional[str] = None
    """Authority responsible for enforcement."""

    # Metadata
    description: str = ""
    """Human-readable description."""

    reference: Optional[str] = None
    """Reference to source of constraint requirement."""

    @classmethod
    def privacy_constraint(
        cls,
        classification: str,
        requirement: str,
    ) -> WorkspaceCandidateConstraint:
        """
        Create a privacy constraint.

        Args:
            classification: Privacy classification required
            requirement: Specific requirement

        Returns:
            New privacy constraint instance
        """
        return cls(
            constraint_id=f"priv_{classification}",
            constraint_type="privacy",
            requirement=requirement,
            severity="critical",
            enforceable=True,
            enforcement_authority="security_authority",
            description=f"Privacy classification must be {classification}",
            reference="privacy_policy_v1",
        )

    @classmethod
    def security_constraint(
        cls,
        level: str,
        requirement: str,
    ) -> WorkspaceCandidateConstraint:
        """
        Create a security constraint.

        Args:
            level: Security level required
            requirement: Specific requirement

        Returns:
            New security constraint instance
        """
        return cls(
            constraint_id=f"sec_{level}",
            constraint_type="security",
            requirement=requirement,
            severity="critical",
            enforceable=True,
            enforcement_authority="security_authority",
            description=f"Security level must be {level}",
            reference="security_policy_v1",
        )

    @classmethod
    def policy_constraint(
        cls,
        policy_id: str,
        requirement: str,
    ) -> WorkspaceCandidateConstraint:
        """
        Create a policy constraint.

        Args:
            policy_id: Policy identifier
            requirement: Specific requirement

        Returns:
            New policy constraint instance
        """
        return cls(
            constraint_id=f"pol_{policy_id}",
            constraint_type="policy",
            requirement=requirement,
            severity="error",
            enforceable=True,
            enforcement_authority="compliance_authority",
            description=f"Policy {policy_id} must be satisfied",
            reference=policy_id,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceCandidateDependency:
    """
    Immutable dependency specification for a candidate.

    Dependencies represent semantic relationships that affect eligibility.
    They are referenced but not resolved (no runtime lookup).

    TYPES OF DEPENDENCIES:
        • required: Must be present
        • optional: May be present
        • blocking: Prevents admission if missing
        • semantic: Semantic relationship requirement
        • context: Context completeness requirement
        • policy: Policy prerequisite
        • security: Security prerequisite

    ARCHITECTURAL INVARIANTS:
        WCD-INV-001: Dependencies are referenced, not resolved
        WCD-INV-002: Missing dependency ≠ automatic rejection
        WCD-INV-003: Dependencies preserve semantic relationships
    """

    # Dependency identity
    dependency_id: str
    """Unique identifier for this dependency."""

    # Dependency type
    dependency_type: str  # required, optional, blocking, etc.
    """Type of dependency (see TYPES OF DEPENDENCIES)."""

    # Dependency specification
    reference: Optional[str] = None
    """Reference to the dependency (semantic pointer only)."""

    is_satisfied: bool = False
    """Whether this dependency is currently satisfied."""

    # Metadata
    description: str = ""
    """Human-readable description."""

    required_by: Optional[str] = None
    """Who requires this dependency."""

    @classmethod
    def required_dependency(
        cls,
        reference: str,
        description: str = "",
    ) -> WorkspaceCandidateDependency:
        """
        Create a required dependency.

        Args:
            reference: Reference to the dependency
            description: Human-readable description

        Returns:
            New required dependency instance
        """
        return cls(
            dependency_id=f"req_{reference[:16]}",
            dependency_type="required",
            reference=reference,
            is_satisfied=False,
            description=description or f"Requires {reference}",
            required_by="admission_authority",
        )

    @classmethod
    def optional_dependency(
        cls,
        reference: str,
        description: str = "",
    ) -> WorkspaceCandidateDependency:
        """
        Create an optional dependency.

        Args:
            reference: Reference to the dependency
            description: Human-readable description

        Returns:
            New optional dependency instance
        """
        return cls(
            dependency_id=f"opt_{reference[:16]}",
            dependency_type="optional",
            reference=reference,
            is_satisfied=False,
            description=description or f"May use {reference}",
            required_by=None,
        )

    @classmethod
    def blocking_dependency(
        cls,
        reference: str,
        description: str = "",
    ) -> WorkspaceCandidateDependency:
        """
        Create a blocking dependency.

        Args:
            reference: Reference to the dependency
            description: Human-readable description

        Returns:
            New blocking dependency instance
        """
        return cls(
            dependency_id=f"blk_{reference[:16]}",
            dependency_type="blocking",
            reference=reference,
            is_satisfied=False,
            description=description or f"Must satisfy {reference}",
            required_by="admission_authority",
        )


# =============================================================================
# ADMISSION VALIDATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceAdmissionValidation:
    """
    Immutable validation result for an admission request.

    Validation checks the semantic integrity of an admission request
    without performing any evaluation or selection.

    ARCHITECTURAL INVARIANTS:
        WAV-INV-001: Validation never performs repair
        WAV-INV-002: Validation never mutates artifacts
        WAV-INV-003: Validation is deterministic and replayable

    VALIDATION CHECKS:
        • identity: Candidate identity format valid
        • revision: Revision number monotonically increasing
        • ownership: Referenced content exists and is accessible
        • authority: Requesting authority has correct authorization
        • provenance: Complete origin chain preserved
        • content existence: Referenced content exists
        • reference integrity: All references are syntactically valid
        • privacy: Privacy classification valid and consistent
        • policy compatibility: No conflicts with current policies
        • security compatibility: Security requirements met
        • dependency completeness: Required dependencies present
        • constraint satisfaction: All constraints satisfied
        • scope correctness: Scope boundaries valid
        • context completeness: Required context provided

    VALIDATION RESULTS:
        passed      - All checks passed
        failed      - At least one check failed
        warning     - Some non-critical issues found
    """

    # Validation identity
    validation_id: str
    """Unique identifier for this validation."""

    # Request information
    request_id: str
    """ID of the admission request being validated."""

    candidate_identity: WorkspaceCandidateIdentity
    """Candidate identity from request."""

    # Validation results
    is_valid: bool = True
    """Whether all required checks passed."""

    validation_state: str = "passed"
    """Detailed validation state (passed, failed, warning)."""

    checked_items: Tuple[str, ...] = field(default_factory=tuple)
    """List of items that were checked."""

    errors: Tuple[str, ...] = field(default_factory=tuple)
    """Validation errors (if any)."""

    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Non-critical warnings (if any)."""

    # Validation metadata
    validated_at_ref: str = "semantic_time_origin"
    """Semantic time reference of validation."""

    validating_authority: Optional[str] = None
    """Authority that performed validation."""

    @classmethod
    def passed(
        cls,
        validation_id: str,
        request_id: str,
        candidate_identity: str,
        checked_items: Tuple[str, ...] = (),
    ) -> WorkspaceAdmissionValidation:
        """
        Create a passed validation result.

        Args:
            validation_id: Unique identifier for this validation
            request_id: ID of the validated request
            candidate_identity: Candidate identity from request
            checked_items: List of items that were checked

        Returns:
            New WorkspaceAdmissionValidation instance (is_valid=True)
        """
        return cls(
            validation_id=validation_id,
            request_id=request_id,
            candidate_identity=candidate_identity,
            is_valid=True,
            validation_state="passed",
            checked_items=checked_items,
        )

    @classmethod
    def failed(
        cls,
        validation_id: str,
        request_id: str,
        candidate_identity: str,
        errors: Tuple[str, ...],
        checked_items: Tuple[str, ...] = (),
    ) -> WorkspaceAdmissionValidation:
        """
        Create a failed validation result.

        Args:
            validation_id: Unique identifier for this validation
            request_id: ID of the validated request
            candidate_identity: Candidate identity from request
            errors: List of validation errors
            checked_items: List of items that were checked

        Returns:
            New WorkspaceAdmissionValidation instance (is_valid=False)
        """
        return cls(
            validation_id=validation_id,
            request_id=request_id,
            candidate_identity=candidate_identity,
            is_valid=False,
            validation_state="failed",
            errors=errors,
            checked_items=checked_items,
        )

    @classmethod
    def warning(
        cls,
        validation_id: str,
        request_id: str,
        candidate_identity: str,
        warnings: Tuple[str, ...],
        checked_items: Tuple[str, ...] = (),
    ) -> WorkspaceAdmissionValidation:
        """
        Create a warning validation result.

        Args:
            validation_id: Unique identifier for this validation
            request_id: ID of the validated request
            candidate_identity: Candidate identity from request
            warnings: List of non-critical warnings
            checked_items: List of items that were checked

        Returns:
            New WorkspaceAdmissionValidation instance (is_valid=True with warnings)
        """
        return cls(
            validation_id=validation_id,
            request_id=request_id,
            candidate_identity=candidate_identity,
            is_valid=True,
            validation_state="warning",
            warnings=warnings,
            checked_items=checked_items,
        )


# =============================================================================
# ADMISSION DECISION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceAdmissionDecision:
    """
    Immutable admission decision from external workspace authority.

    The decision comes from external authority. The Default Network must never
    fabricate acceptance.

    ARCHITECTURAL INVARIANTS:
        WAD-INV-001: Admission does not imply evaluation
        WAD-INV-002: Admission does not select among candidates
        WAD-INV-003: Decisions are deterministic and replayable

    POSSIBLE OUTCOMES:
        accepted          - Candidate admitted to workspace
        rejected          - Candidate rejected
        deferred          - Admission deferred to later time
        conditionally_accepted - Admitted with constraints
        conditionally_rejected - Rejected pending conditions
        suspended         - Temporarily suspended
        withdrawn         - Withdrawn by submitter
        expired           - Expired (time-based)
        invalidated       - Invalidated by authority
    """

    # Decision identity
    decision_id: str
    """Unique identifier for this decision."""

    # Request information
    request_id: str
    """ID of the admission request being decided on."""

    candidate_identity: WorkspaceCandidateIdentity
    """ID of the candidate being evaluated."""

    content_reference: str
    """Reference to WorkspaceContent revision involved."""

    # Decision outcome
    outcome: str  # accepted, rejected, deferred, etc.
    """Decision outcome (see POSSIBLE OUTCOMES)."""

    # Decision details
    reason: str = ""
    """Human-readable explanation."""

    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this decision."""

    justification: Optional[str] = None
    """Detailed justification for the decision."""

    # Authority information
    authority: Optional[str] = None
    """External authority that made the decision."""

    confidence: float = 0.5
    """Confidence in the decision (0.0-1.0)."""

    uncertainty: str = "none"
    """Uncertainty classification for the decision."""

    # Timestamps
    decided_at_ref: str = "semantic_time_origin"
    """Semantic time reference of decision."""

    # Additional metadata
    constraints_applied: Tuple[WorkspaceCandidateConstraint, ...] = field(
        default_factory=tuple
    )
    """Constraints applied to admitted candidate."""

    dependencies_unsatisfied: Tuple[str, ...] = field(default_factory=tuple)
    """Unsatisfied dependencies (if any)."""

    @classmethod
    def accept(
        cls,
        decision_id: str,
        request_id: str,
        candidate_identity: str,
        content_reference: str,
        reason: str = "",
        authority: Optional[str] = None,
        evidence: Tuple[str, ...] = (),
        justification: Optional[str] = None,
    ) -> WorkspaceAdmissionDecision:
        """
        Create an acceptance decision.

        Args:
            decision_id: Unique identifier for this decision
            request_id: ID of the accepted request
            candidate_identity: ID of the accepted candidate
            content_reference: Reference to WorkspaceContent revision
            reason: Explanation for acceptance
            authority: External authority that made the decision
            evidence: Evidence supporting this decision
            justification: Detailed justification

        Returns:
            New WorkspaceAdmissionDecision instance (outcome=accepted)
        """
        return cls(
            decision_id=decision_id,
            request_id=request_id,
            candidate_identity=candidate_identity,
            content_reference=content_reference,
            outcome="accepted",
            reason=reason or "Candidate meets workspace criteria",
            authority=authority,
            confidence=0.9,
            evidence=evidence,
            justification=justification,
        )

    @classmethod
    def reject(
        cls,
        decision_id: str,
        request_id: str,
        candidate_identity: str,
        content_reference: str,
        reason: str = "",
        authority: Optional[str] = None,
        evidence: Tuple[str, ...] = (),
        justification: Optional[str] = None,
    ) -> WorkspaceAdmissionDecision:
        """
        Create a rejection decision.

        Args:
            decision_id: Unique identifier for this decision
            request_id: ID of the rejected request
            candidate_identity: ID of the rejected candidate
            content_reference: Reference to WorkspaceContent revision
            reason: Explanation for rejection
            authority: External authority that made the decision
            evidence: Evidence supporting this decision
            justification: Detailed justification

        Returns:
            New WorkspaceAdmissionDecision instance (outcome=rejected)
        """
        return cls(
            decision_id=decision_id,
            request_id=request_id,
            candidate_identity=candidate_identity,
            content_reference=content_reference,
            outcome="rejected",
            reason=reason or "Does not meet workspace criteria",
            authority=authority,
            confidence=0.95,
            evidence=evidence,
            justification=justification,
        )

    @classmethod
    def defer(
        cls,
        decision_id: str,
        request_id: str,
        candidate_identity: str,
        content_reference: str,
        reason: str = "",
        authority: Optional[str] = None,
        evidence: Tuple[str, ...] = (),
        justification: Optional[str] = None,
    ) -> WorkspaceAdmissionDecision:
        """
        Create a deferral decision.

        Args:
            decision_id: Unique identifier for this decision
            request_id: ID of the deferred request
            candidate_identity: ID of the deferred candidate
            content_reference: Reference to WorkspaceContent revision
            reason: Explanation for deferral
            authority: External authority that made the decision
            evidence: Evidence supporting this decision
            justification: Detailed justification

        Returns:
            New WorkspaceAdmissionDecision instance (outcome=deferred)
        """
        return cls(
            decision_id=decision_id,
            request_id=request_id,
            candidate_identity=candidate_identity,
            content_reference=content_reference,
            outcome="deferred",
            reason=reason or "Workspace capacity unavailable at this time",
            authority=authority,
            confidence=0.85,
            evidence=evidence,
            justification=justification,
        )

    @classmethod
    def conditionally_accept(
        cls,
        decision_id: str,
        request_id: str,
        candidate_identity: str,
        content_reference: str,
        constraints: Tuple[WorkspaceCandidateConstraint, ...],
        reason: str = "",
        authority: Optional[str] = None,
        evidence: Tuple[str, ...] = (),
        justification: Optional[str] = None,
    ) -> WorkspaceAdmissionDecision:
        """
        Create a conditional acceptance decision.

        Args:
            decision_id: Unique identifier for this decision
            request_id: ID of the accepted request
            candidate_identity: ID of the accepted candidate
            content_reference: Reference to WorkspaceContent revision
            constraints: Constraints that must be satisfied
            reason: Explanation for conditional acceptance
            authority: External authority that made the decision
            evidence: Evidence supporting this decision
            justification: Detailed justification

        Returns:
            New WorkspaceAdmissionDecision instance (outcome=conditionally_accepted)
        """
        return cls(
            decision_id=decision_id,
            request_id=request_id,
            candidate_identity=candidate_identity,
            content_reference=content_reference,
            outcome="conditionally_accepted",
            reason=reason or "Candidate accepted pending constraint satisfaction",
            authority=authority,
            confidence=0.85,
            evidence=evidence,
            justification=justification,
            constraints_applied=constraints,
        )


# =============================================================================
# WORKSPACE CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidate:
    """
    Immutable workspace candidate model.

    A Workspace Candidate represents a validated, admissible, immutable semantic
    projection of Workspace Content that is eligible for future Workspace evaluation.

    A Candidate is NOT:
        - Workspace Content (the source)
        - a Competition Result
        - a Winner
        - a Broadcast
        - a Decision
        - an Action
        - a Plan

    ARCHITECTURAL INVARIANTS:
        WCC-INV-001: Every Candidate references exactly one Workspace Content revision
        WCC-INV-002: Candidates never duplicate Workspace Content
        WCC-INV-003: Admission precedes evaluation
        WCC-INV-004: No evaluation occurs in admission phase
        WCC-INV-005: No selection occurs in admission phase

    NOT RESPONSIBLE FOR:
        - Evaluation (belongs to future phases)
        - Competition (belongs to future phases)
        - Winner selection (belongs to future phases)
        - Runtime scheduling (belongs to runtime layer)
        - Broadcasting delivery (belongs to runtime layer)
    """

    # Identity and revisioning
    candidate_id: WorkspaceCandidateIdentity
    """Unique identifier for this candidate."""

    # Reference to source Content (required before defaults)
    content_reference: str
    """Reference to the single WorkspaceContent revision this represents."""

    # Candidate classification (required before defaults)
    kind: str  # WorkspaceCandidateKind.*
    """Canonical category of candidate."""

    state: str  # WorkspaceCandidateState.*
    """Current state in lifecycle."""

    eligibility: str  # WorkspaceEligibility.*
    """Semantic eligibility status."""

    validity: str  # WorkspaceCandidateValidity.*
    """Semantic validity status."""

    status: str  # WorkspaceCandidateStatus.*
    """Current pipeline status."""

    # Optional fields with defaults
    revision: WorkspaceCandidateRevision = 1
    """Monotonically increasing revision number."""

    fingerprint: WorkspaceCandidateFingerprint = ""
    """Short fingerprint for quick identification."""

    digest: WorkspaceCandidateDigest = ""
    """Cryptographic digest of semantic content."""

    # Source and provenance
    source_network: str = ""
    """Network that originated this candidate."""

    source_artifact_ref: Optional[str] = None
    """Reference to original artifact (NOT ownership)."""

    correlation_id: str = ""
    """Correlation ID for tracing across systems."""

    causation_id: Optional[str] = None
    """Causation chain reference."""

    # Context and scope
    context: WorkspaceCandidateContext = field(
        default_factory=WorkspaceCandidateContext
    )
    """Semantic context for interpretation."""

    scope: WorkspaceCandidateScope = field(
        default_factory=WorkspaceCandidateScope.for_general_workspace
    )
    """Broadcast scope requirements."""

    # Validity information
    validity_info: WorkspaceCandidateValidityInfo = field(
        default_factory=WorkspaceCandidateValidityInfo
    )
    """Validity assessment information."""

    # Admission pipeline references (external, not embedded objects)
    admission_request_ref: Optional[str] = None
    """Reference to admission request (if submitted)."""

    validation_result_ref: Optional[str] = None
    """Reference to validation result."""

    admission_decision_ref: Optional[str] = None
    """Reference to admission decision (if decided)."""

    pool_reference: Optional[str] = None
    """Reference to Candidate Pool (if in a pool)."""

    # Timestamps (semantic references only)
    submitted_at_ref: str = "semantic_time_origin"
    """Semantic time reference of submission."""

    validated_at_ref: Optional[str] = None
    """Semantic time reference of validation."""

    decided_at_ref: Optional[str] = None
    """Semantic time reference of admission decision."""

    # Metadata
    priority: float = 0.5
    """Priority level (semantic only, no runtime scheduling)."""

    @classmethod
    def new_from_content(
        cls,
        candidate_id: str,
        content_reference: str,
        kind: str,
        source_network: str = "",
        source_artifact_ref: Optional[str] = None,
    ) -> WorkspaceCandidate:
        """
        Create a new workspace candidate from a content reference.

        This is the canonical way to create a candidate. It ensures all
        architectural invariants are satisfied.

        Args:
            candidate_id: Unique identifier for this candidate (external or deterministic)
            content_reference: Reference to WorkspaceContent revision
            kind: Canonical category of candidate
            source_network: Network originating this candidate
            source_artifact_ref: Reference to original artifact

        Returns:
            New WorkspaceCandidate instance with state=SUBMITTED, eligibility=PENDING_ELIGIBILITY

        ARCHITECTURAL INVARIANTS SATISFIED:
            • Exactly one Content revision referenced (content_reference)
            • No runtime dependencies
            • Immutable data structure (frozen=True)
        """
        return cls(
            candidate_id=candidate_id,
            content_reference=content_reference,
            kind=kind,
            state="submitted",
            eligibility="pending_eligibility",
            validity="tentative",
            status="pending",
            source_network=source_network or "unknown",
            source_artifact_ref=source_artifact_ref,
            correlation_id=f"candidate_{candidate_id[:16]}",
            context=WorkspaceCandidateContext(),
            scope=WorkspaceCandidateScope.for_general_workspace(),
            validity_info=WorkspaceCandidateValidityInfo(
                is_valid=True,  # Initial validity assessment
                validation_errors=(),
            ),
            fingerprint=candidate_id[:8],  # Deterministic fingerprint
        )

    @classmethod
    def validated_from_candidate(
        cls,
        candidate: WorkspaceCandidate,
        validation_result_ref: str,
    ) -> WorkspaceCandidate:
        """
        Create a new candidate revision after validation.

        Args:
            candidate: The original candidate
            validation_result_ref: Reference to the validation result

        Returns:
            New WorkspaceCandidate instance with state=VALIDATED, eligibility=PENDING_ELIGIBILITY
        """
        return cls(
            candidate_id=candidate.candidate_id,
            revision=candidate.revision + 1,
            fingerprint=candidate.fingerprint,
            digest=candidate.digest,
            content_reference=candidate.content_reference,
            kind=candidate.kind,
            state="validated",
            eligibility="pending_eligibility",
            validity=candidate.validity_info.validity_state if candidate.validity_info.is_valid else "invalid",
            status="validating" if candidate.status == "pending" else candidate.status,
            source_network=candidate.source_network,
            source_artifact_ref=candidate.source_artifact_ref,
            correlation_id=candidate.correlation_id,
            causation_id=candidate.causation_id,
            context=candidate.context,
            scope=candidate.scope,
            validity_info=candidate.validity_info,
            admission_request_ref=candidate.admission_request_ref,
            validation_result_ref=validation_result_ref,
            admission_decision_ref=None,
            pool_reference=candidate.pool_reference,
            submitted_at_ref=candidate.submitted_at_ref,
            validated_at_ref="semantic_time_origin",
        )

    @classmethod
    def admitted_from_candidate(
        cls,
        candidate: WorkspaceCandidate,
        admission_decision_ref: str,
        pool_reference: Optional[str] = None,
    ) -> WorkspaceCandidate:
        """
        Create a new candidate revision after admission.

        Args:
            candidate: The original candidate (now validated)
            admission_decision_ref: Reference to the admission decision
            pool_reference: Reference to the Candidate Pool (optional)

        Returns:
            New WorkspaceCandidate instance with state=ADMITTED, eligibility=ELIGIBLE

        ARCHITECTURAL INVARIANTS SATISFIED:
            • Admission decision reference recorded (not evaluated)
            • Pool reference recorded (if admitted)
            • Eligibility set to ELIGIBLE (semantic, not runtime state)
        """
        return cls(
            candidate_id=candidate.candidate_id,
            revision=candidate.revision + 1,
            fingerprint=candidate.fingerprint,
            digest=candidate.digest,
            content_reference=candidate.content_reference,
            kind=candidate.kind,
            state="admitted",
            eligibility="eligible",
            validity="verified" if candidate.validity_info.verified else "valid",
            status="admitted_status",
            source_network=candidate.source_network,
            source_artifact_ref=candidate.source_artifact_ref,
            correlation_id=candidate.correlation_id,
            causation_id=candidate.causation_id,
            context=candidate.context,
            scope=candidate.scope,
            validity_info=WorkspaceCandidateValidityInfo(
                is_valid=True,
                validity_state="verified",
                verified=True,
                verification_source=admission_decision_ref,
            ),
            admission_request_ref=candidate.admission_request_ref,
            validation_result_ref=candidate.validation_result_ref,
            admission_decision_ref=admission_decision_ref,
            pool_reference=pool_reference,
            submitted_at_ref=candidate.submitted_at_ref,
            validated_at_ref=candidate.validated_at_ref,
            decided_at_ref="semantic_time_origin",
        )


# =============================================================================
# DUPLICATE AND EQUIVALENCE SEMANTICS
# =============================================================================

class DuplicateAssessment(Enum):
    """
    Canonical duplicate assessment kinds for workspace candidates.
    
    These determine whether candidates are distinct or equivalent.
    """

    DISTINCT = "distinct"
    """Candidates are definitely distinct."""

    RELATED = "related"
    """Related but not duplicates (different revisions)."""

    POSSIBLE_DUPLICATE = "possible_duplicate"
    """May be a duplicate, needs verification."""

    PROBABLE_DUPLICATE = "probable_duplicate"
    """Likely a duplicate (same fingerprint)."""

    IDENTICAL = "identical"
    """Exact duplicate (same content reference)."""

    REVISION_OF_EXISTING = "revision_of_existing"
    """A revision of an existing candidate."""

    SUPERSEDES_EXISTING = "supersedes_existing"
    """Supersedes an existing candidate."""


@dataclass(frozen=True, slots=True)
class WorkspaceCandidateEquivalence:
    """
    Immutable equivalence record for candidate assessment.

    Equivalence determines whether two candidates represent the same
    semantic content or different revisions of the same content.

    TYPES OF EQUIVALENCE:
        • identical: Same fingerprint and content reference
        • revision: Same identity, different revision
        • related: Different identities but related semantics
        • duplicate: Same fingerprint (probable duplicate)
        • equivalent: Same meaning, different representation

    ARCHITECTURAL INVARIANTS:
        WCE-INV-001: Equivalence is semantic only
        WCE-INV-002: Duplicate detection does not evaluate value
        WCE-INV-003: Equivalence never implies admission
    """

    # Assessment identity
    assessment_id: str
    """Unique identifier for this equivalence assessment."""

    # Candidates being compared
    candidate_a_ref: str
    """Reference to first candidate."""

    candidate_b_ref: str
    """Reference to second candidate."""

    # Assessment result
    equivalence_kind: str  # DuplicateAssessment.*
    """Kind of equivalence (see TYPES OF EQUIVALENCE)."""

    confidence: float = 0.5
    """Confidence in the assessment (0.0-1.0)."""

    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this assessment."""

    # Fingerprint comparison
    fingerprint_match: bool = False
    """Whether fingerprints match exactly."""

    content_reference_match: bool = False
    """Whether content references match exactly."""

    # Timestamps
    assessed_at_ref: str = "semantic_time_origin"
    """Semantic time reference of assessment."""

    assessing_authority: Optional[str] = None
    """Authority that performed the assessment."""


@dataclass(frozen=True, slots=True)
class WorkspaceCandidateDuplicate:
    """
    Immutable duplicate record for candidate management.

    Duplicates represent candidates that refer to the same semantic content
    and must be managed appropriately (not deleted).

    TYPES OF DUPLICATES:
        • identical: Same fingerprint and content reference
        • probable: Same fingerprint, different content reference (need verification)
        • revision_of: A newer revision of existing candidate
        • superseding: Supersedes existing candidate

    ARCHITECTURAL INVARIANTS:
        WCDP-INV-001: Duplicates are not deleted (semantic preservation)
        WCDP-INV-002: Duplicate detection is deterministic
        WCDP-INV-003: Duplicate management does not evaluate value
    """

    # Record identity
    record_id: str
    """Unique identifier for this duplicate record."""

    # Candidates involved
    primary_candidate_ref: str
    """Reference to the primary (original) candidate."""

    duplicate_candidate_ref: str
    """Reference to the duplicate candidate."""

    # Duplicate kind
    duplicate_kind: str  # DuplicateAssessment.*
    """Kind of duplicate relationship."""

    resolution_status: str = "pending"
    """Current resolution status (pending, resolved, merged)."""

    # Evidence and metadata
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this duplicate claim."""

    detected_at_ref: str = "semantic_time_origin"
    """Semantic time reference of detection."""

    detecting_authority: Optional[str] = None
    """Authority that performed the detection."""


# =============================================================================
# CANDIDATE POOL
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidatePool:
    """
    Immutable bounded candidate pool.

    The Candidate Pool contains admitted Candidates only.
    It performs:
        • no scoring
        • no ordering
        • no competition
        • no prioritization

    The pool is a semantic container - it has no runtime scheduling behavior.
    New pools are created for each state change (immutable).

    ARCHITECTURAL INVARIANTS:
        WCP-INV-001: Pool contains only admitted Candidates
        WCP-INV-002: No ordering in the pool
        WCP-INV-003: No competition in the pool
        WCP-INV-004: No prioritization in the pool

    NOT RESPONSIBLE FOR:
        • Runtime scheduling (belongs to runtime layer)
        • Candidate evaluation (belongs to future phases)
        • Winner selection (belongs to future phases)
    """

    # Pool identity
    pool_id: str
    """Unique identifier for this pool instance."""

    revision: int = 1
    """Revision number of this pool state."""

    fingerprint: Optional[str] = None
    """Fingerprint summarizing pool contents."""

    digest: Optional[str] = None
    """Cryptographic digest of pool state."""

    # Pool contents (bounded, never unbounded)
    candidate_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to admitted candidates in the pool."""

    # Pool metadata
    source_networks: Tuple[str, ...] = field(default_factory=tuple)
    """Source networks represented in this pool."""

    created_at_ref: str = "semantic_time_origin"
    """Semantic time reference of pool creation."""

    updated_at_ref: Optional[str] = None
    """Semantic time reference of last update."""

    # Pool capacity
    max_capacity: int = 100
    """Maximum number of candidates allowed in the pool (bounded)."""

    current_count: int = 0
    """Current number of candidates in the pool."""

    # Ownership and provenance
    ownership: str = "workspace_network"
    """Owner of this pool."""

    provenance_ref: Optional[str] = None
    """Reference to pool provenance record."""

    # Constraints
    constraints: Tuple[WorkspaceCandidateConstraint, ...] = field(
        default_factory=tuple
    )
    """Constraints applied to all candidates in the pool."""

    @classmethod
    def empty(cls) -> WorkspaceCandidatePool:
        """
        Create an empty candidate pool.

        Returns:
            New WorkspaceCandidatePool instance with no candidates.
        """
        return cls(
            pool_id="pool_empty",
            revision=1,
            fingerprint="empty_pool",
            digest="empty_pool",
            candidate_refs=(),
            source_networks=(),
            created_at_ref="semantic_time_origin",
            max_capacity=100,
            current_count=0,
        )

    @classmethod
    def from_candidates(
        cls,
        candidates: Tuple[WorkspaceCandidate, ...],
    ) -> WorkspaceCandidatePool:
        """
        Create a pool from candidate instances.

        Args:
            candidates: Tuple of admitted WorkspaceCandidates

        Returns:
            New WorkspaceCandidatePool instance with candidates added.
        """
        # Extract references
        refs = tuple(c.candidate_id for c in candidates)
        
        # Count unique source networks
        networks = tuple(set(
            c.source_network for c in candidates 
            if c.source_network
        ))

        return cls(
            pool_id=f"pool_{len(refs)}_candidates",
            revision=1,
            fingerprint=f"pool_{hash(refs) & 0xFFFFFFFF:08x}",
            digest=f"pool_digest_{hash((refs, networks)) & 0xFFFFFFFF:08x}",
            candidate_refs=refs[:100],  # Bounded to max_capacity
            source_networks=networks,
            created_at_ref="semantic_time_origin",
            max_capacity=100,
            current_count=len(refs),
        )

    @classmethod
    def from_references(
        cls,
        pool_id: str,
        candidate_refs: Tuple[str, ...],
        sources: Tuple[str, ...] = (),
    ) -> WorkspaceCandidatePool:
        """
        Create a pool from candidate references.

        Args:
            pool_id: Unique identifier for this pool instance
            candidate_refs: References to admitted candidates
            sources: Source networks (optional)

        Returns:
            New WorkspaceCandidatePool instance.
        """
        return cls(
            pool_id=pool_id,
            revision=1,
            fingerprint=f"pool_{hash(candidate_refs) & 0xFFFFFFFF:08x}",
            digest=f"pool_digest_{hash((candidate_refs, sources)) & 0xFFFFFFFF:08x}",
            candidate_refs=candidate_refs[:100],  # Bounded
            source_networks=sources,
            created_at_ref="semantic_time_origin",
            max_capacity=100,
            current_count=len(candidate_refs),
        )


# =============================================================================
# INVALIDATION SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateInvalidation:
    """
    Immutable invalidation record for a candidate.

    Invalidation represents the semantic termination of a candidate's life cycle.
    It is performed by external authority, not the workspace itself.

    POSSIBLE REASONS:
        • owner_withdrawal: Withdrawn by content owner
        • policy_violation: Violates workspace policy
        • security_violation: Security concern detected
        • dependency_failure: Required dependency no longer satisfied
        • content_invalid: Semantic invalidity detected
        • expired_reference: Referenced content has expired
        • superseded_revision: Newer revision supersedes this one
        • semantic_inconsistency: Inconsistent with other valid content

    ARCHITECTURAL INVARIANTS:
        WCI-INV-001: Invalidated candidates are not deleted (preserved)
        WCI-INV-002: Invalidation is performed by external authority only
        WCI-INV-003: Invalidation does not mutate the candidate (creates record)
    """

    # Required fields first
    invalidation_id: str
    """Unique identifier for this invalidation."""

    candidate_ref: str
    """Reference to the invalidated candidate."""

    reason: str  # See POSSIBLE REASONS
    """Reason for invalidation."""

    content_reference: Optional[str] = None
    """Content reference at time of invalidation."""

    authority: Optional[str] = None
    """External authority that performed the invalidation."""

    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this invalidation."""

    invalidated_at_ref: str = "semantic_time_origin"
    """Semantic time reference of invalidation."""

    is_final: bool = False
    """Whether this invalidation is final (cannot be restored)."""

    @classmethod
    def by_owner(
        cls,
        invalidation_id: str,
        candidate_ref: str,
        content_reference: str,
    ) -> WorkspaceCandidateInvalidation:
        """
        Create an owner withdrawal invalidation.

        Args:
            invalidation_id: Unique identifier for this invalidation
            candidate_ref: Reference to the invalidated candidate
            content_reference: Content reference at time of invalidation

        Returns:
            New WorkspaceCandidateInvalidation instance (reason=owner_withdrawal)
        """
        return cls(
            invalidation_id=invalidation_id,
            candidate_ref=candidate_ref,
            content_reference=content_reference,
            reason="owner_withdrawal",
            evidence=("Owner explicitly requested withdrawal",),
            is_final=False,  # Can be restored if re-submitted
        )

    @classmethod
    def by_policy_violation(
        cls,
        invalidation_id: str,
        candidate_ref: str,
        content_reference: str,
        policy_id: str,
    ) -> WorkspaceCandidateInvalidation:
        """
        Create a policy violation invalidation.

        Args:
            invalidation_id: Unique identifier for this invalidation
            candidate_ref: Reference to the invalidated candidate
            content_reference: Content reference at time of invalidation
            policy_id: ID of violated policy

        Returns:
            New WorkspaceCandidateInvalidation instance (reason=policy_violation)
        """
        return cls(
            invalidation_id=invalidation_id,
            candidate_ref=candidate_ref,
            content_reference=content_reference,
            reason="policy_violation",
            authority="compliance_authority",
            evidence=(f"Violates policy {policy_id}",),
            is_final=True,  # Policy violations are typically final
        )

    @classmethod
    def by_content_invalid(
        cls,
        invalidation_id: str,
        candidate_ref: str,
        content_reference: str,
        errors: Tuple[str, ...],
    ) -> WorkspaceCandidateInvalidation:
        """
        Create a semantic invalidity invalidation.

        Args:
            invalidation_id: Unique identifier for this invalidation
            candidate_ref: Reference to the invalidated candidate
            content_reference: Content reference at time of invalidation
            errors: Validation errors that caused invalidity

        Returns:
            New WorkspaceCandidateInvalidation instance (reason=content_invalid)
        """
        return cls(
            invalidation_id=invalidation_id,
            candidate_ref=candidate_ref,
            content_reference=content_reference,
            reason="content_invalid",
            authority="validation_authority",
            evidence=errors,
            is_final=False,  # Can be restored with corrected content
        )


@dataclass(frozen=True, slots=True)
class WorkspaceCandidateSuspension:
    """
    Immutable suspension record for a candidate.

    Suspension temporarily disables a candidate without invalidating it.
    The candidate can be restored to active status later.

    TYPES OF SUSPENSIONS:
        • capacity: Workspace capacity exceeded
        • priority_lower: Lower priority candidates suspended
        • review_required: Suspended pending review
        • condition_pending: Suspended pending condition satisfaction

    ARCHITECTURAL INVARIANTS:
        WCSU-INV-001: Suspended candidates are not deleted (preserved)
        WCSU-INV-002: Suspension is temporary by definition
        WCSU-INV-003: Suspensions can be lifted for restoration
    """

    # Suspension identity (required fields first)
    suspension_id: str
    """Unique identifier for this suspension."""

    # Candidate being suspended (required before defaults)
    candidate_ref: str
    """Reference to the suspended candidate."""

    reason: str  # See TYPES OF SUSPENSIONS
    """Reason for suspension."""

    content_reference: Optional[str] = None
    """Content reference at time of suspension."""

    authority: Optional[str] = None
    """External authority that performed the suspension."""

    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this suspension."""

    suspended_at_ref: str = "semantic_time_origin"
    """Semantic time reference of suspension."""

    expires_at_ref: Optional[str] = None
    """Optional semantic time reference when suspension ends."""

    can_be_restored: bool = True
    """Whether this candidate can be restored."""

    restoration_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for restoration."""

    @classmethod
    def by_capacity(
        cls,
        suspension_id: str,
        candidate_ref: str,
        content_reference: str,
    ) -> WorkspaceCandidateSuspension:
        """
        Create a capacity-based suspension.

        Args:
            suspension_id: Unique identifier for this suspension
            candidate_ref: Reference to the suspended candidate
            content_reference: Content reference at time of suspension

        Returns:
            New WorkspaceCandidateSuspension instance (reason=capacity)
        """
        return cls(
            suspension_id=suspension_id,
            candidate_ref=candidate_ref,
            content_reference=content_reference,
            reason="capacity",
            authority="workspace_capacity_authority",
            evidence=("Workspace capacity limit exceeded",),
            suspended_at_ref="semantic_time_origin",
            expires_at_ref=None,  # No fixed expiration
            can_be_restored=True,
            restoration_conditions=("available_capacity", "pending_review"),
        )

    @classmethod
    def by_priority(
        cls,
        suspension_id: str,
        candidate_ref: str,
        content_reference: str,
        priority_threshold: float,
    ) -> WorkspaceCandidateSuspension:
        """
        Create a priority-based suspension.

        Args:
            suspension_id: Unique identifier for this suspension
            candidate_ref: Reference to the suspended candidate
            content_reference: Content reference at time of suspension
            priority_threshold: Priority threshold that caused suspension

        Returns:
            New WorkspaceCandidateSuspension instance (reason=priority_lower)
        """
        return cls(
            suspension_id=suspension_id,
            candidate_ref=candidate_ref,
            content_reference=content_reference,
            reason="priority_lower",
            authority="workspace_priority_authority",
            evidence=(f"Priority below threshold {priority_threshold:.2f}",),
            suspended_at_ref="semantic_time_origin",
            expires_at_ref=None,
            can_be_restored=True,
            restoration_conditions=("increased_priority", "pending_review"),
        )


@dataclass(frozen=True, slots=True)
class WorkspaceCandidateRestoration:
    """
    Immutable restoration record for a candidate.

    Restoration re-enables a previously suspended or rejected candidate.
    The candidate retains its original identity but gets a new revision.

    TYPES OF RESTORATIONS:
        • suspension_lifted: Suspension period ended
        • condition_satisfied: Required conditions now satisfied
        • review_approved: Review process completed successfully
        • policy_update: Policy change allows previously blocked content

    ARCHITECTURAL INVARIANTS:
        WCR-INV-001: Restored candidates get new revision (not mutated)
        WCR-INV-002: Restoration is performed by external authority only
        WCR-INV-003: Restore history is preserved in candidate lineage
    """

    # Restoration identity (required fields first)
    restoration_id: str
    """Unique identifier for this restoration."""

    # Candidate being restored (required before defaults)
    candidate_ref: str
    """Reference to the candidate being restored."""

    reason: str  # See TYPES OF RESTORATIONS
    """Reason for restoration."""

    content_reference: Optional[str] = None
    """Content reference at time of restoration."""

    authority: Optional[str] = None
    """External authority that performed the restoration."""

    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this restoration."""

    restored_at_ref: str = "semantic_time_origin"
    """Semantic time reference of restoration."""

    previous_state: Optional[str] = None
    """State before restoration (for lineage tracking)."""

    @classmethod
    def by_condition(
        cls,
        restoration_id: str,
        candidate_ref: str,
        content_reference: str,
        conditions_met: Tuple[str, ...],
    ) -> WorkspaceCandidateRestoration:
        """
        Create a condition-satisfied restoration.

        Args:
            restoration_id: Unique identifier for this restoration
            candidate_ref: Reference to the restored candidate
            content_reference: Content reference at time of restoration
            conditions_met: Conditions that are now satisfied

        Returns:
            New WorkspaceCandidateRestoration instance (reason=condition_satisfied)
        """
        return cls(
            restoration_id=restoration_id,
            candidate_ref=candidate_ref,
            content_reference=content_reference,
            reason="condition_satisfied",
            authority="admission_authority",
            evidence=conditions_met,
            restored_at_ref="semantic_time_origin",
            previous_state="suspended",
        )


# =============================================================================
# EXPIRATION SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateExpiration:
    """
    Immutable expiration record for a candidate.

    Expiration represents the semantic end of a candidate's time-bound life.
    Expiration never acquires runtime clocks internally - it uses external references.

    TYPES OF EXPIRATION:
        • time_limited: Time-based expiration (external reference)
        • event_based: Event-triggered expiration
        • revision_based: Superseded by newer revision
        • policy_expired: Policy no longer applies

    ARCHITECTURAL INVARIANTS:
        WCEX-INV-001: Expiration uses external time references only
        WCEX-INV-002: Expired candidates are preserved (not deleted)
        WCEX-INV-003: Expiration does not mutate the candidate
    """

    # Expiration identity (required fields first)
    expiration_id: str
    """Unique identifier for this expiration."""

    # Candidate being expired (required before defaults)
    candidate_ref: str
    """Reference to the expired candidate."""

    reason: str  # See TYPES OF EXPIRATION
    """Reason for expiration."""

    content_reference: Optional[str] = None
    """Content reference at time of expiration."""

    authority: Optional[str] = None
    """External authority that determined expiration."""

    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this expiration."""

    expired_at_ref: str = "semantic_time_origin"
    """Semantic time reference of expiration."""

    original_expiration_ref: Optional[str] = None
    """Original external time reference for the expiration condition."""

    @classmethod
    def by_time(
        cls,
        expiration_id: str,
        candidate_ref: str,
        content_reference: str,
        lifetime_class: str,
    ) -> WorkspaceCandidateExpiration:
        """
        Create a time-based expiration.

        Args:
            expiration_id: Unique identifier for this expiration
            candidate_ref: Reference to the expired candidate
            content_reference: Content reference at time of expiration
            lifetime_class: The lifetime classification that expired

        Returns:
            New WorkspaceCandidateExpiration instance (reason=time_limited)
        """
        return cls(
            expiration_id=expiration_id,
            candidate_ref=candidate_ref,
            content_reference=content_reference,
            reason="time_limited",
            authority="workspace_time_authority",
            evidence=(f"Lifetime class {lifetime_class} expired",),
            expired_at_ref="semantic_time_origin",
            original_expiration_ref=f"time_boundary_{lifetime_class}",
        )

    @classmethod
    def by_revision(
        cls,
        expiration_id: str,
        candidate_ref: str,
        content_reference: str,
        superseding_candidate_ref: Optional[str] = None,
    ) -> WorkspaceCandidateExpiration:
        """
        Create a revision-based expiration.

        Args:
            expiration_id: Unique identifier for this expiration
            candidate_ref: Reference to the expired candidate
            content_reference: Content reference at time of expiration
            superseding_candidate_ref: Reference to replacing candidate (optional)

        Returns:
            New WorkspaceCandidateExpiration instance (reason=revision_based)
        """
        return cls(
            expiration_id=expiration_id,
            candidate_ref=candidate_ref,
            content_reference=content_reference,
            reason="revision_based",
            authority="workspace_content_authority",
            evidence=(f"Superseded by newer revision",),
            expired_at_ref="semantic_time_origin",
            original_expiration_ref=None,
        )


# =============================================================================
# PROVENANCE SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateProvenance:
    """
    Immutable provenance record for a candidate.

    Provenance preserves the complete origin chain without embedding runtime objects.
    Every candidate must preserve full provenance - no provenance loss is allowed.

    ARCHITECTURAL INVARIANTS:
        WCPV-INV-001: Origin preserved (source network, package, artifact)
        WCPV-INV-002: Owner preserved (external to workspace)
        WCPV-INV-003: Content revision preserved (no mutation allowed)
        WCPV-INV-004: References preserved (all semantic pointers maintained)
        WCPV-INV-005: Lineage preserved (evolution history intact)

    NOT RESPONSIBLE FOR:
        • Runtime time acquisition
        • External system interaction
        • Semantic content evaluation
    """

    # Provenance identity
    provenance_id: str
    """Unique identifier for this provenance record."""

    # Origin information
    origin_network: str = ""
    """Network that originated the source content."""

    origin_package: str = ""
    """Package within the originating network."""

    origin_artifact_id: Optional[str] = None
    """ID of the original artifact (external, not owned)."""

    # External ownership reference (NOT ownership transfer)
    external_owner_ref: Optional[str] = None
    """Reference to external owner (never transferred to workspace)."""

    # Content revision reference
    content_revision: int = 1
    """Revision of the source content at origin."""

    # Semantic lineage references
    parent_provenance_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to parent provenance records (for lineage)."""

    derivation_chain: Tuple[str, ...] = field(default_factory=tuple)
    """Chain of semantic derivations from origin."""

    # Evidence and assumptions
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence."""

    assumption_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to background assumptions."""

    # Timestamps (external references only)
    created_at_ref: str = "semantic_time_origin"
    """Semantic time reference of provenance creation."""

    last_updated_ref: Optional[str] = None
    """Semantic time reference of last update."""

    @classmethod
    def from_source(
        cls,
        provenance_id: str,
        origin_network: str,
        origin_package: str,
        origin_artifact_id: str,
        external_owner_ref: Optional[str],
    ) -> WorkspaceCandidateProvenance:
        """
        Create a new provenance record from source information.

        Args:
            provenance_id: Unique identifier for this provenance
            origin_network: Network that originated the content
            origin_package: Package within the network
            origin_artifact_id: ID of the original artifact (external)
            external_owner_ref: Reference to external owner

        Returns:
            New WorkspaceCandidateProvenance instance.
        """
        return cls(
            provenance_id=provenance_id,
            origin_network=origin_network,
            origin_package=origin_package,
            origin_artifact_id=origin_artifact_id,
            external_owner_ref=external_owner_ref,
            content_revision=1,
        )


# =============================================================================
# OWNERSHIP SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateOwnership:
    """
    Immutable ownership record for a workspace candidate.

    Ownership separates:
        • External ownership (of source content) - never transferred
        • Workspace ownership (of candidate semantics and lifecycle)
        • Authority responsibility - decision-making power

    ARCHITECTURAL INVARIANTS:
        WCO-INV-001: Source content ownership preserved (external)
        WCO-INV-002: Candidate semantics owned by workspace network
        WCO-INV-003: Authority ≠ ownership (authority can act without owning)
        WCO-INV-004: No implicit ownership transfer

    NOT RESPONSIBLE FOR:
        • Runtime enforcement of ownership
        • Legal ownership determination
        • External system interactions
    """

    # Ownership record identity
    ownership_id: str
    """Unique identifier for this ownership record."""

    # Workspace-owned (candidate semantics)
    workspace_ownership: bool = True
    """Workspace Network owns candidate semantics and lifecycle."""

    # Source-owned (external, never transferred)
    source_content_owner_ref: Optional[str] = None
    """Reference to external owner of source content (never transferred)."""

    # Authority assignments
    submit_authority: Optional[str] = None
    """Authority responsible for submission."""

    admit_authority: Optional[str] = None
    """Authority responsible for admission decisions."""

    invalidate_authority: Optional[str] = None
    """Authority responsible for invalidation decisions."""

    restore_authority: Optional[str] = None
    """Authority responsible for restoration decisions."""

    # Responsibility assignments
    provenance_responsibility: str = "workspace_network"
    """Entity responsible for preserving provenance."""

    lifecycle_responsibility: str = "workspace_network"
    """Entity responsible for lifecycle management."""

    @classmethod
    def for_candidate(
        cls,
        ownership_id: str,
        source_content_owner_ref: Optional[str],
        submit_authority: Optional[str] = None,
        admit_authority: Optional[str] = None,
    ) -> WorkspaceCandidateOwnership:
        """
        Create an ownership record for a candidate.

        Args:
            ownership_id: Unique identifier for this ownership record
            source_content_owner_ref: Reference to external content owner
            submit_authority: Authority for submissions (optional)
            admit_authority: Authority for admission decisions (optional)

        Returns:
            New WorkspaceCandidateOwnership instance.
        """
        return cls(
            ownership_id=ownership_id,
            workspace_ownership=True,  # Workspace owns candidate semantics
            source_content_owner_ref=source_content_owner_ref,
            submit_authority=submit_authority,
            admit_authority=admit_authority,
            invalidate_authority="workspace_invalidation_authority",
            restore_authority="workspace_restore_authority",
        )


# =============================================================================
# AUTHORITY SEMANTICS
# =============================================================================

class WorkspaceAuthorityKind(Enum):
    """
    Canonical kinds of authority in the workspace.
    
    Authority includes:
        • submit: Submit candidates for admission
        • admit: Make admission decisions
        • reject: Reject candidates
        • invalidate: Invalidate candidates
        • restore: Restore suspended candidates
        • withdraw: Withdraw candidates

    Authority does NOT include:
        • runtime scheduling (runtime layer)
        • evaluation (future phases)
        • competition (future phases)
        • broadcast delivery (runtime layer)
    """

    SUBMIT = "submit"
    """Authority to submit candidates for admission."""

    ADMIT = "admit"
    """Authority to admit candidates to workspace."""

    REJECT = "reject"
    """Authority to reject candidate submissions."""

    INVALIDATE = "invalidate"
    """Authority to invalidate candidates."""

    RESTORE = "restore"
    """Authority to restore suspended or invalidated candidates."""

    WITHDRAW = "withdraw"
    """Authority to withdraw candidates by submitter."""

    VALIDATE = "validate"
    """Authority to validate candidate structure and constraints."""

    ASSESS = "assess"
    """Authority to assess candidate validity (advisory only)."""

    SUPERVISE = "supervise"
    """Supervisory authority over the admission process."""


@dataclass(frozen=True, slots=True)
class WorkspaceCandidateAuthority:
    """
    Immutable authority record for workspace operations.

    Authority represents permission to perform specific operations.
    It is separate from ownership and responsibility.

    TYPES OF AUTHORITY:
        • submit: Submit candidates
        • admit: Make admission decisions
        • reject: Reject candidates
        • invalidate: Invalidate candidates
        • restore: Restore candidates
        • withdraw: Withdraw candidates

    ARCHITECTURAL INVARIANTS:
        WCA-INV-001: Authority is separate from ownership
        WCA-INV-002: Authority does not imply evaluation (semantic only)
        WCA-INV-003: Authority assignments are immutable records
    """

    # Authority record identity
    authority_id: str
    """Unique identifier for this authority record."""

    # Authority kind
    authority_kind: str  # WorkspaceAuthorityKind.*
    """Type of authority (see TYPES OF AUTHORITY)."""

    # Authority scope
    scope: str = "workspace"
    """Scope of authority application."""

    # Authority holder (external reference)
    holder_ref: Optional[str] = None
    """Reference to entity holding this authority."""

    # Authority validity
    is_active: bool = True
    """Whether this authority is currently active."""

    valid_from_ref: str = "semantic_time_origin"
    """Semantic time reference when authority became valid."""

    valid_until_ref: Optional[str] = None
    """Optional semantic time reference when authority expires."""

    # Metadata
    description: str = ""
    """Human-readable description of this authority."""

    @classmethod
    def for_admission(
        cls,
        authority_id: str,
        holder_ref: Optional[str],
    ) -> WorkspaceCandidateAuthority:
        """
        Create an admission authority record.

        Args:
            authority_id: Unique identifier for this authority
            holder_ref: Reference to authority holder

        Returns:
            New WorkspaceCandidateAuthority instance (kind=admit)
        """
        return cls(
            authority_id=authority_id,
            authority_kind="admit",
            scope="workspace",
            holder_ref=holder_ref,
            is_active=True,
            description="Authority to make admission decisions for workspace candidates.",
        )

    @classmethod
    def for_validation(
        cls,
        authority_id: str,
        holder_ref: Optional[str],
    ) -> WorkspaceCandidateAuthority:
        """
        Create a validation authority record.

        Args:
            authority_id: Unique identifier for this authority
            holder_ref: Reference to authority holder

        Returns:
            New WorkspaceCandidateAuthority instance (kind=validate)
        """
        return cls(
            authority_id=authority_id,
            authority_kind="validate",
            scope="workspace",
            holder_ref=holder_ref,
            is_active=True,
            description="Authority to validate candidate structure and constraints.",
        )


# =============================================================================
# LIFECYCLE SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateLifecycle:
    """
    Immutable lifecycle record for a candidate.

    The lifecycle describes the semantic journey of a candidate through its
    existence. It is a record, not an active state machine.

    POSSIBLE STATES (see also WorkspaceCandidateState enum):
        • submitted: Initial submission
        • validated: Passed validation checks
        • admitted: Admitted to workspace
        • deferred: Admission deferred
        • restricted: Admitted with restrictions
        • suspended: Temporarily unavailable
        • restored: Previously suspended, now active
        • withdrawn: Withdrawn by submitter
        • expired: Time-based expiration
        • invalidated: Invalidated by authority
        • archived: Historical preservation
        • terminated: Final termination

    ARCHITECTURAL INVARIANTS:
        WCL-INV-001: Lifecycle is semantic, not runtime state
        WCL-INV-002: Lifecycle preserves all state transitions
        WCL-INV-003: No automatic transitions (external only)
    """

    # Lifecycle identity
    lifecycle_id: str
    """Unique identifier for this lifecycle record."""

    # Candidate reference
    candidate_ref: str
    """Reference to the candidate whose lifecycle this describes."""

    # Current state
    current_state: str  # WorkspaceCandidateState.*
    """Current lifecycle state."""

    # State history (append-only)
    state_history: Tuple[str, ...] = field(default_factory=tuple)
    """History of state transitions (append-only)."""

    # Timestamps for each transition
    timestamps: Dict[str, str] = field(default_factory=dict)
    """Mapping from state to semantic time reference."""

    # Lifecycle metadata
    submitted_at_ref: str = "semantic_time_origin"
    """Semantic time reference of initial submission."""

    current_state_since_ref: str = "semantic_time_origin"
    """When current state began."""

    lifecycle_authority: Optional[str] = None
    """Authority responsible for lifecycle management."""

    @classmethod
    def new_lifecycle(
        cls,
        lifecycle_id: str,
        candidate_ref: str,
    ) -> WorkspaceCandidateLifecycle:
        """
        Create a new lifecycle record for a candidate.

        Args:
            lifecycle_id: Unique identifier for this lifecycle record
            candidate_ref: Reference to the candidate

        Returns:
            New WorkspaceCandidateLifecycle instance with state=SUBMITTED.
        """
        return cls(
            lifecycle_id=lifecycle_id,
            candidate_ref=candidate_ref,
            current_state="submitted",
            state_history=("submitted",),
            timestamps={"submitted": "semantic_time_origin"},
            submitted_at_ref="semantic_time_origin",
            current_state_since_ref="semantic_time_origin",
        )

    def transition_to(self, new_state: str, timestamp_ref: str = "semantic_time_origin") -> WorkspaceCandidateLifecycle:
        """
        Create a new lifecycle record with state transition.

        Args:
            new_state: The target state (from WorkspaceCandidateState)
            timestamp_ref: Semantic time reference of the transition

        Returns:
            New WorkspaceCandidateLifecycle instance with updated state.
        """
        return WorkspaceCandidateLifecycle(
            lifecycle_id=self.lifecycle_id,
            candidate_ref=self.candidate_ref,
            current_state=new_state,
            state_history=self.state_history + (new_state,),
            timestamps={**self.timestamps, new_state: timestamp_ref},
            submitted_at_ref=self.submitted_at_ref,
            current_state_since_ref=timestamp_ref,
        )


# =============================================================================
# HISTORY SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateHistory:
    """
    Immutable history record for a candidate.

    History is the complete record of all events affecting a candidate.
    It is append-only, bounded, and preserves provenance.

    ARCHITECTURAL INVARIANTS:
        WCH-INV-001: History is immutable (append-only)
        WCH-INV-002: History is bounded (no unbounded growth)
        WCH-INV-003: History preserves provenance
        WCH-INV-004: History never implies evaluation

    NOT RESPONSIBLE FOR:
        • Runtime event tracking
        • Event correlation across candidates
        • Real-time processing
    """

    # History identity
    history_id: str
    """Unique identifier for this history record."""

    # Candidate reference
    candidate_ref: str
    """Reference to the candidate whose history this describes."""

    # History entries (append-only, bounded)
    entries: Tuple[str, ...] = field(default_factory=tuple)
    """History entries (semantic records)."""

    # History metadata
    total_entries: int = 0
    """Total number of entries in history."""

    first_entry_at_ref: str = "semantic_time_origin"
    """When the first entry was recorded."""

    last_entry_at_ref: Optional[str] = None
    """When the last entry was recorded."""

    # Boundedness
    max_entries: int = 1000
    """Maximum number of history entries (bounded)."""

    @classmethod
    def new_history(
        cls,
        history_id: str,
        candidate_ref: str,
    ) -> WorkspaceCandidateHistory:
        """
        Create a new history record for a candidate.

        Args:
            history_id: Unique identifier for this history record
            candidate_ref: Reference to the candidate

        Returns:
            New WorkspaceCandidateHistory instance.
        """
        return cls(
            history_id=history_id,
            candidate_ref=candidate_ref,
            entries=("candidate_created",),
            total_entries=1,
            first_entry_at_ref="semantic_time_origin",
            last_entry_at_ref="semantic_time_origin",
            max_entries=1000,
        )

    def add_entry(self, entry: str) -> WorkspaceCandidateHistory:
        """
        Add an entry to history.

        Args:
            entry: The semantic history entry to record

        Returns:
            New WorkspaceCandidateHistory instance with entry added.
        """
        new_total = self.total_entries + 1
        return WorkspaceCandidateHistory(
            history_id=self.history_id,
            candidate_ref=self.candidate_ref,
            entries=self.entries + (entry,) if len(self.entries) < self.max_entries else self.entries,
            total_entries=min(new_total, self.max_entries),
            first_entry_at_ref=self.first_entry_at_ref,
            last_entry_at_ref="semantic_time_origin",
            max_entries=self.max_entries,
        )


# =============================================================================
# LINEAGE SEMANTICS
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateLineage:
    """
    Immutable lineage record for a candidate.

    Lineage preserves the semantic evolution path of a candidate.
    It tracks parent-child relationships and derivations.

    TYPES OF LINEAGE RELATIONSHIPS:
        • revision_parent: Direct revision (r1 → r2 → r3)
        • supersession: New revision replaces old
        • derivation: Semantically derived from another candidate

    ARCHITECTURAL INVARIANTS:
        WCLN-INV-001: Lineage preserves semantic evolution
        WCLN-INV-002: No lineage loss (complete chain preserved)
        WCLN-INV-003: Lineage is immutable (new nodes only)

    NOT RESPONSIBLE FOR:
        • Runtime lineage tracking
        • Dynamic lineage updates
        • Event processing
    """

    # Lineage identity
    lineage_id: str
    """Unique identifier for this lineage record."""

    # Candidate reference
    candidate_ref: str
    """Reference to the candidate whose lineage this describes."""

    # Lineage nodes (semantic pointers)
    parent_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to parent candidates (for revision chains)."""

    derivation_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to derived candidates."""

    root_ref: Optional[str] = None
    """Root reference in the lineage chain."""

    # Revision information
    current_revision: int = 1
    """Current revision number."""

    total_revisions: int = 1
    """Total revisions in lineage chain."""

    # Timestamps (external references)
    first_created_at_ref: str = "semantic_time_origin"
    """When the root candidate was created."""

    last_modified_at_ref: Optional[str] = None
    """When this revision was created."""

    @classmethod
    def new_lineage(
        cls,
        lineage_id: str,
        candidate_ref: str,
    ) -> WorkspaceCandidateLineage:
        """
        Create a new lineage record for a candidate.

        Args:
            lineage_id: Unique identifier for this lineage record
            candidate_ref: Reference to the candidate

        Returns:
            New WorkspaceCandidateLineage instance.
        """
        return cls(
            lineage_id=lineage_id,
            candidate_ref=candidate_ref,
            parent_refs=(),
            derivation_refs=(),
            root_ref=candidate_ref,
            current_revision=1,
            total_revisions=1,
            first_created_at_ref="semantic_time_origin",
        )

    def add_revision(self, new_candidate_ref: str) -> WorkspaceCandidateLineage:
        """
        Add a revision to the lineage.

        Args:
            new_candidate_ref: Reference to the new revision

        Returns:
            New WorkspaceCandidateLineage instance with revision added.
        """
        return WorkspaceCandidateLineage(
            lineage_id=self.lineage_id,
            candidate_ref=new_candidate_ref,
            parent_refs=self.parent_refs + (self.candidate_ref,) if self.candidate_ref else (),
            derivation_refs=self.derivation_refs,
            root_ref=self.root_ref or self.candidate_ref,
            current_revision=self.current_revision + 1,
            total_revisions=self.total_revisions + 1,
            first_created_at_ref=self.first_created_at_ref,
            last_modified_at_ref="semantic_time_origin",
        )

    def add_derivation(self, derived_candidate_ref: str) -> WorkspaceCandidateLineage:
        """
        Add a derivation relationship.

        Args:
            derived_candidate_ref: Reference to the derived candidate

        Returns:
            New WorkspaceCandidateLineage instance with derivation added.
        """
        return WorkspaceCandidateLineage(
            lineage_id=self.lineage_id,
            candidate_ref=derived_candidate_ref,
            parent_refs=self.parent_refs,
            derivation_refs=self.derivation_refs + (self.candidate_ref,),
            root_ref=self.root_ref or self.candidate_ref,
            current_revision=self.current_revision,
            total_revisions=self.total_revisions,
            first_created_at_ref=self.first_created_at_ref,
        )


# =============================================================================
# ARCHITECTURAL LAWS
# =============================================================================

"""
ARCHITECTURAL LAWS for Workspace Candidate Admission and Intake.

These are semantic principles that govern the behavior of the admission system.
They are NOT runtime enforcement - they are declarative rules.

LAW 01: Admission precedes evaluation.
    Candidates must be admitted before they can be evaluated.
    
LAW 02: Candidates reference Workspace Content.
    Every candidate references exactly one Workspace Content revision.
    
LAW 03: Admission never scores candidates.
    Scoring belongs to future evaluation phases, not admission.
    
LAW 04: Admission never selects candidates.
    Selection belongs to competition phases, not admission.
    
LAW 05: Admission preserves provenance.
    All provenance information must be preserved through admission.
    
LAW 06: Admission preserves ownership.
    External ownership of source content is never transferred.
    
LAW 07: Admission is deterministic.
    Same inputs always produce same admission outcomes.
    
LAW 08: Admission is replayable.
    Admission can be reconstructed from external references only.
    
LAW 09: Candidate Pools contain only admitted candidates.
    Non-admitted candidates never appear in pools.
    
LAW 10: Candidate Pools perform no ordering.
    Pool ordering belongs to future competition phases.
    
LAW 11: No evaluation occurs in admission phase.
    Evaluation is a separate, later phase.
    
LAW 12: No runtime behavior in admission semantics.
    Admission is purely semantic; runtime belongs to execution layer.
"""

ADMISSION_LAWS = (
    "Admission precedes evaluation",
    "Candidates reference Workspace Content",
    "Admission never scores Candidates",
    "Admission never selects Candidates",
    "Admission preserves provenance",
    "Admission preserves ownership",
    "Admission is deterministic",
    "Admission is replayable",
    "Candidate Pools contain only admitted Candidates",
    "Candidate Pools perform no ordering",
    "No evaluation occurs in admission phase",
    "No runtime behavior in admission semantics",
)


# =============================================================================
# INVARIANTS
# =============================================================================

"""
INVARIANTS for Workspace Candidate Admission and Intake.

These are properties that must always hold true. They are NOT optional.

INV-001: Every Candidate references one Content revision.
INV-002: Every Candidate has one owner (external).
INV-003: Every Candidate has one provenance chain.
INV-004: Every admission decision is explicit.
INV-005: Rejected Candidates never appear in Candidate Pools.
INV-006: Admission never mutates Workspace Content.
INV-007: Replay reconstructs identical Candidates.
INV-008: Candidate identity is immutable.
"""

SYSTEM_INVARIANTS = (
    "Every Candidate references one Content revision",
    "Every Candidate has one owner (external)",
    "Every Candidate has one provenance chain",
    "Every admission decision is explicit",
    "Rejected Candidates never appear in Candidate Pools",
    "Admission never mutates Workspace Content",
    "Replay reconstructs identical Candidates",
    "Candidate identity is immutable",
)


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "WorkspaceCandidateIdentity",
    "WorkspaceCandidateRevision",
    "WorkspaceCandidateReference",
    "WorkspaceCandidateFingerprint",
    "WorkspaceCandidateDigest",

    # Taxonomy enums
    "WorkspaceCandidateKind",
    "WorkspaceCandidateState",
    "WorkspaceEligibility",
    "WorkspaceCandidateStatus",
    "WorkspaceCandidateValidity",
    "DuplicateAssessment",
    "WorkspaceAuthorityKind",

    # Context and scope types
    "WorkspaceCandidateContext",
    "WorkspaceCandidateScope",
    "WorkspaceCandidateValidityInfo",

    # Admission types
    "WorkspaceAdmissionRequest",
    "WorkspaceCandidateConstraint",
    "WorkspaceCandidateDependency",
    "WorkspaceAdmissionValidation",
    "WorkspaceAdmissionDecision",

    # Candidate type
    "WorkspaceCandidate",

    # Duplicate semantics
    "WorkspaceCandidateEquivalence",
    "WorkspaceCandidateDuplicate",

    # Pool types
    "WorkspaceCandidatePool",

    # Invalidation, suspension, restoration
    "WorkspaceCandidateInvalidation",
    "WorkspaceCandidateSuspension",
    "WorkspaceCandidateRestoration",

    # Expiration
    "WorkspaceCandidateExpiration",

    # Provenance and ownership
    "WorkspaceCandidateProvenance",
    "WorkspaceCandidateOwnership",

    # Authority
    "WorkspaceCandidateAuthority",

    # Lifecycle, history, lineage
    "WorkspaceCandidateLifecycle",
    "WorkspaceCandidateHistory",
    "WorkspaceCandidateLineage",

    # Constants
    "ADMISSION_LAWS",
    "SYSTEM_INVARIANTS",
]