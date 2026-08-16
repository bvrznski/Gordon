# Workspace Content Semantics - Phase 4.6.2
# ==========================================

"""
Canonical Workspace Content definitions.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - External time providers only
    - External identity providers only
    - Bounded collections
    - Semantic-time preservation

SEMANTIC MODEL OVERVIEW
=======================

Workspace Content represents a bounded, immutable semantic projection of
externally owned cognitive information. It preserves:

    Identity      - Deterministic, replayable reference
    Revision      - Explicit versioning (no in-place mutation)
    Ownership     - Always external to Workspace
    Provenance    - Complete origin chain preserved
    Meaning       - Never changes without explicit revision

Workspace Content is NOT:
    - Memory or Working Memory
    - Knowledge, belief, or decision
    - Action, plan, or reasoning
    - Runtime artifact (no execution, no time acquisition)
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Tuple, Optional, Dict, Set
from enum import Enum


# =============================================================================
# IDENTITY TYPES - Immutable references
# =============================================================================

WorkspaceContentIdentity = str
"""Unique identifier for a workspace content instance.

Must be:
    - Deterministically derived or externally supplied
    - Replayable (same input produces same output)
    - Never generated internally (no UUIDs, timestamps)

Examples: Content hash, source system ID with context prefix.
"""


WorkspaceContentRevision = int
"""
Monotonically increasing revision number for content.

Revision rules:
    - Revision 1 is initial creation
    - Each semantic change requires a new revision
    - Meaning change always requires revision
    - Identity + Revision = unique artifact reference

No in-place mutation allowed. Create new revision instead.
"""


WorkspaceContentReference = str
"""
Immutable reference to Workspace Content.

Format: "identity@revision"
Examples:
    "content_abc123@1"
    "insight_from_reasoning@5"

Used for linking without ownership.
"""


# =============================================================================
# DIGEST AND FINGERPRINT TYPES - Semantic integrity
# =============================================================================

WorkspaceContentDigest = str
"""
Cryptographic or deterministic digest of semantic content.

Purpose: Verify integrity, detect changes, ensure replayability.

Rules:
    - Derived from semantic representation (not runtime state)
    - Must be deterministic (same input = same output)
    - Never use timestamps, UUIDs, or random values in calculation

Examples: SHA-256 hash, Merkle root of content tree.
"""


WorkspaceContentFingerprint = str
"""
Short fingerprint for quick identification and comparison.

Purpose: Fast lookup, duplicate detection, indexing.

Rules:
    - Always deterministically derived from identity
    - May be shorter than full digest
    - Must be stable across runs (same input = same output)

Examples: First 8 characters of digest, hash prefix.
"""


# =============================================================================
# CONTENT KINDS TAXONOMY
# =============================================================================

class WorkspaceContentKind(Enum):
    """
    Canonical categories of semantic content for the workspace.

    This taxonomy is extensible. New kinds may be added as subclasses or
    through configuration without modifying core semantics.

    Semantic meaning: The kind determines how content is processed,
    evaluated, and broadcast.
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
# CONTENT CONTEXT TYPES
# =============================================================================

class TaskContext(Enum):
    """
    Context types related to task execution.
    """

    PLANNING_PHASE = "planning_phase"
    EXECUTION_PHASE = "execution_phase"
    MONITORING_PHASE = "monitoring_phase"
    RECOVERY_PHASE = "recovery_phase"


class GoalContext(Enum):
    """
    Context types related to goal management.
    """

    FORMULATION = "formulation"
    PROPAGATION = "propagation"
    TRACKING = "tracking"
    ASSESSMENT = "assessment"


class DecisionContext(Enum):
    """
    Context types related to decision processes.
    """

    INFORMATION_GATHERING = "information_gathering"
    ALTERNATIVE_GENERATION = "alternative_generation"
    EVALUATION_AND_SELECTION = "evaluation_and_selection"
    COMMITMENT = "commitment"
    REVIEW = "review"


class ReasoningContext(Enum):
    """
    Context types related to reasoning processes.
    """

    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    CRITICAL = "critical"


class PlanningContext(Enum):
    """
    Context types related to planning processes.
    """

    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    TEMPORAL = "temporal"
    RESOURCE_ALLOCATION = "resource_allocation"


class ExecutiveContext(Enum):
    """
    Context types related to executive functions.
    """

    COORDINATION = "coordination"
    SUPERVISION = "supervision"
    ALLOCATION = "allocation"
    MONITORING = "monitoring"


class AttentionContext(Enum):
    """
    Context types related to attention mechanisms.
    """

    SELECTION = "selection"
    SUPPRESSION = "suppression"
    ENHANCEMENT = "enhancement"
    SWITCHING = "switching"


class MotivationContext(Enum):
    """
    Context types related to motivation systems.
    """

    GOAL_PRIORITY = "goal_priority"
    RESOURCE_ALLOCATION = "resource_allocation"
    EFFORT_REGULATION = "effort_regulation"


class TemporalContext(Enum):
    """
    Context types related to time management.
    """

    PAST_REFERENCE = "past_reference"
    PRESENT_ASSESSMENT = "present_assessment"
    FUTURE_PROJECTION = "future_projection"


class SpatialContext(Enum):
    """
    Context types related to spatial reasoning.
    """

    LOCATION_REFERENCING = "location_referencing"
    PATH_PLANNING = "path_planning"
    RELATIONAL_SPATIAL = "relational_spatial"


class EnvironmentalContext(Enum):
    """
    Context types related to environment state.
    """

    EXTERNAL_ENVIRONMENT = "external_environment"
    INTERNAL_STATE = "internal_state"
    RESOURCE_AVAILABILITY = "resource_availability"


class IdentityContext(Enum):
    """
    Context types related to identity maintenance.
    """

    CONSISTENCY = "consistency"
    COHERENCE = "coherence"
    DEVELOPMENT = "development"


class PerceptualContext(Enum):
    """
    Context types related to perception processing.
    """

    INPUT_ACQUISITION = "input_acquisition"
    PREPROCESSING = "preprocessing"
    INTEGRATION = "integration"


class OperationalContext(Enum):
    """
    Context types related to operational state.
    """

    INITIALIZATION = "initialization"
    ACTIVE_OPERATIONS = "active_operations"
    SHUTDOWN = "shutdown"


@dataclass(frozen=True, slots=True)
class WorkspaceContentContext:
    """
    Immutable context for workspace content.

    Context provides semantic framing without embedding runtime objects.
    It describes the circumstances and conditions surrounding content.

    ARCHITECTURAL INVARIANTS:
        CC-INV-001: Context never becomes part of content identity
        CC-INV-002: Context is never executable
        CC-INV-003: Context has no runtime time acquisition

    NOT RESPONSIBLE FOR:
        - Runtime state embedding
        - Time-based evaluation
        - External system interaction
    """

    # Source information
    source_network: str = ""
    """Network that originated the content."""

    source_package: str = ""
    """Package within the source network."""

    source_artifact_id: Optional[str] = None
    """Reference to original artifact (NOT ownership)."""

    correlation_id: str = ""
    """Correlation ID for tracing across systems."""

    causation_id: Optional[str] = None
    """Causation chain reference (if applicable)."""

    # Context classification
    task_context: Optional[TaskContext] = None
    """Task-related context if applicable."""

    goal_context: Optional[GoalContext] = None
    """Goal-related context if applicable."""

    decision_context: Optional[DecisionContext] = None
    """Decision-related context if applicable."""

    reasoning_context: Optional[ReasoningContext] = None
    """Reasoning-related context if applicable."""

    planning_context: Optional[PlanningContext] = None
    """Planning-related context if applicable."""

    executive_context: Optional[ExecutiveContext] = None
    """Executive-related context if applicable."""

    attention_context: Optional[AttentionContext] = None
    """Attention-related context if applicable."""

    motivation_context: Optional[MotivationContext] = None
    """Motivation-related context if applicable."""

    temporal_context: Optional[TemporalContext] = None
    """Temporal-related context if applicable."""

    spatial_context: Optional[SpatialContext] = None
    """Spatial-related context if applicable."""

    environmental_context: Optional[EnvironmentalContext] = None
    """Environmental-related context if applicable."""

    identity_context: Optional[IdentityContext] = None
    """Identity-related context if applicable."""

    perceptual_context: Optional[PerceptualContext] = None
    """Perceptual-related context if applicable."""

    operational_context: Optional[OperationalContext] = None
    """Operational-related context if applicable."""

    # Additional context fields
    semantic_domain: str = ""
    """Domain of semantic content (e.g., 'finance', 'healthcare')."""

    audience_type: Tuple[str, ...] = field(default_factory=tuple)
    """Types of consumers this content is intended for."""

    relevance_score: float = 0.5
    """Relevance assessment without runtime time acquisition."""

    @classmethod
    def from_reflection(cls, thought_id: str = "") -> WorkspaceContentContext:
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
    def from_executive(cls, correlation_id: str) -> WorkspaceContentContext:
        """
        Create context from Executive coordination.

        Args:
            correlation_id: Correlation ID from executive

        Returns:
            New WorkspaceContentContext instance
        """
        return cls(
            source_network="EXECUTIVE_NETWORK",
            source_package="coordination",
            correlation_id=correlation_id,
            executive_context=ExecutiveContext.COORDINATION,
        )

    @classmethod
    def for_planning(cls, task_id: str) -> WorkspaceContentContext:
        """Create context for planning content."""
        return cls(
            source_network="DEFAULT_NETWORK",
            source_package="planning",
            correlation_id=f"plan_{task_id}",
            task_context=TaskContext.PLANNING_PHASE,
            planning_context=PlanningContext.STRATEGIC,
        )

    @classmethod
    def for_decision(cls, decision_id: str) -> WorkspaceContentContext:
        """Create context for decision content."""
        return cls(
            source_network="EXECUTIVE_NETWORK",
            source_package="decisions",
            correlation_id=f"dec_{decision_id}",
            decision_context=DecisionContext.EVALUATION_AND_SELECTION,
        )

    @classmethod
    def for_reasoning(cls, reasoning_id: str) -> WorkspaceContentContext:
        """Create context for reasoning content."""
        return cls(
            source_network="DEFAULT_NETWORK",
            source_package="reasoning",
            correlation_id=f"reason_{reasoning_id}",
            reasoning_context=ReasoningContext.DEDUCTIVE,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentScope:
    """
    Immutable scope specification for workspace content.

    Scope defines which systems may receive and how the content is processed.
    It is independent of runtime state and execution.

    ARCHITECTURAL INVARIANTS:
        CS-INV-001: Scope never determines broadcast delivery (runtime does)
        CS-INV-002: Scope never acquires runtime time
        CS-INV-003: Scope is always bounded

    NOT RESPONSIBLE FOR:
        - Runtime broadcast execution
        - Target capability mutation
        - Time-based scope evaluation
    """

    # Consumer scope
    target_audiences: Tuple[str, ...] = field(default_factory=tuple)
    """Audience kinds eligible to consume this content."""

    minimum_confidence: float = 0.5
    """Minimum confidence threshold for consumers (0.0-1.0)."""

    broadcast_depth: int = 3
    """Maximum depth of broadcast propagation (bounded, max 10)."""

    disclosure_level: str = "internal_only"
    """Disclosure classification (public, internal, restricted)."""

    # Authority scope
    authority_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints on which authorities may process this content."""

    # Privacy scope
    privacy_classification: str = "internal_only"
    """Privacy classification for disclosure control."""

    # Visibility scope
    visibility_limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Specific systems or networks that may see this content."""

    # Accessibility scope
    accessibility_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for accessibility."""

    # Broadcast eligibility
    broadcast_eligible: bool = True
    """Whether this content is eligible for broadcast."""

    @classmethod
    def for_general_workspace(cls) -> WorkspaceContentScope:
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
    def for_executive_review(cls) -> WorkspaceContentScope:
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
    def for_public(cls) -> WorkspaceContentScope:
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


@dataclass(frozen=True, slots=True)
class WorkspaceContentValidity:
    """
    Immutable validity information for workspace content.

    Validity assesses whether the content meets canonical requirements.
    It is semantic only and does not require runtime evaluation.

    ARCHITECTURAL INVARIANTS:
        CV-INV-001: Validity is independent of runtime state
        CV-INV-002: Invalid content may still be broadcast (with warning)
        CV-INV-003: Validity never implies truth

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
    """Whether this content meets semantic requirements."""

    validity_state: str = "valid"
    """Detailed validity state (see VALIDITY STATES)."""

    validation_errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation errors (if any)."""

    validity_threshold: float = 0.8
    """Minimum confidence threshold for validity assessment."""

    # Verification status
    verified: bool = False
    """Whether this content has been externally verified."""

    verification_source: Optional[str] = None
    """Reference to verification source (if verified)."""

    # Temporal validity
    is_stale: bool = False
    """Whether validity may have expired."""

    is_superseded: bool = False
    """Whether newer revision supersedes this one."""

    # Conflict detection
    has_conflicts: bool = False
    """Whether this content conflicts with other valid content."""

    conflicting_content_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to conflicting content (if any)."""

    @classmethod
    def valid(cls) -> WorkspaceContentValidity:
        """
        Create a valid state.

        Returns:
            Validity indicating content meets all requirements.
        """
        return cls(
            is_valid=True,
            validity_state="valid",
            validation_errors=(),
            verified=False,
        )

    @classmethod
    def invalid(cls, errors: Tuple[str, ...]) -> WorkspaceContentValidity:
        """
        Create an invalid state with errors.

        Args:
            errors: List of validation error messages

        Returns:
            Validity indicating content fails requirements.
        """
        return cls(
            is_valid=False,
            validity_state="invalid",
            validation_errors=errors,
            verified=False,
        )

    @classmethod
    def provisional(cls) -> WorkspaceContentValidity:
        """Create a provisional validity state."""
        return cls(
            is_valid=True,
            validity_state="provisional",
            validation_errors=(),
            verified=False,
            validity_threshold=0.5,
        )

    @classmethod
    def superseded(cls, replacement_ref: str) -> WorkspaceContentValidity:
        """
        Create a superseded state.

        Args:
            replacement_ref: Reference to the replacing content

        Returns:
            Validity indicating this is replaced.
        """
        return cls(
            is_valid=False,
            validity_state="superseded",
            validation_errors=(),
            verified=False,
            is_superseded=True,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentFreshness:
    """
    Immutable freshness assessment for workspace content.

    Freshness measures temporal relevance without internal time acquisition.
    It uses semantic time references instead of runtime timestamps.

    ARCHITECTURAL INVARIANTS:
        CF-INV-001: Freshness never requires current time
        CF-INV-002: Freshness is independent of validity
        CF-INV-003: Stale content may still be valid

    FRESHNESS STATES:
        fresh       - Recently created, high relevance
        recent      - Within acceptable time window
        aging       - Approaching staleness threshold
        stale       - May have reduced relevance
        expired     - Past expiration point
        unknown     - Freshness cannot be determined
    """

    # Temporal references (semantic time)
    created_at_ref: str = ""
    """Reference to semantic-time when content was created."""

    expires_at_ref: Optional[str] = None
    """Reference to semantic-time when content expires (if known)."""

    freshness_threshold_ref: Optional[str] = None
    """Reference to threshold for staleness assessment."""

    # Freshness state
    freshness_state: str = "fresh"
    """Detailed freshness state (see FRESHNESS STATES)."""

    is_fresh: bool = True
    """Whether this content is considered fresh."""

    is_stale: bool = False
    """Whether content has become stale."""

    is_expired: bool = False
    """Whether content has expired."""

    # Time-based metrics
    relative_age_ref: Optional[str] = None
    """Reference to how age compares to similar content."""

    estimated_duration_ref: Optional[str] = None
    """Reference to expected validity duration."""

    @classmethod
    def eternal(cls) -> WorkspaceContentFreshness:
        """
        Create an eternal freshness (no expiration).

        Returns:
            Freshness that never becomes stale or expired.
        """
        return cls(
            created_at_ref="semantic_time_origin",
            expires_at_ref=None,
            freshness_state="fresh",
            is_fresh=True,
        )

    @classmethod
    def time_bounded(cls, created_at: str, expires_at: str) -> WorkspaceContentFreshness:
        """
        Create a time-bounded freshness.

        Args:
            created_at: Semantic time reference of creation
            expires_at: Semantic time reference of expiration

        Returns:
            Freshness with explicit expiration.
        """
        return cls(
            created_at_ref=created_at,
            expires_at_ref=expires_at,
            freshness_state="fresh",
            is_fresh=True,
        )

    @classmethod
    def stale(cls) -> WorkspaceContentFreshness:
        """Create a stale freshness state."""
        return cls(
            created_at_ref="semantic_time_origin",
            freshness_state="stale",
            is_fresh=False,
            is_stale=True,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentVisibility:
    """
    Immutable visibility specification for workspace content.

    Visibility specifies who may see the content. It is independent from
    accessibility (whether one can access what they can see).

    ARCHITECTURAL INVARIANTS:
        CV-INV-001: Visibility never implies accessibility
        CV-INV-002: Visibility never requires runtime time
        CV-INV-003: Hidden content may still be accessible to some

    VISIBILITY STATES:
        private     - Visible only to originator
        restricted  - Visible only to specified entities
        shared      - Visible to multiple consumers
        global      - Visible to all eligible systems
        confidential - Visible only under specific conditions
        classified  - Visible only with clearance
        public      - Visible without restriction
    """

    # Visibility state
    visibility_state: str = "internal_only"
    """Detailed visibility state (see VISIBILITY STATES)."""

    visibility_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Entities or systems that may see this content."""

    visibility_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Additional constraints on visibility."""

    # Access control
    requires_authz: bool = False
    """Whether authorization is required for visibility."""

    authz_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Authorization requirements if applicable."""

    # Classification
    security_classification: str = "unclassified"
    """Security classification level."""

    policy_classification: str = "internal_only"
    """Policy-based classification."""

    # Special visibility states
    is_private: bool = False
    """Whether content is private to originator."""

    is_hidden: bool = False
    """Whether content is currently hidden."""

    @classmethod
    def for_public(cls) -> WorkspaceContentVisibility:
        """
        Create a public visibility specification.

        Returns:
            Visibility suitable for global distribution.
        """
        return cls(
            visibility_state="public",
            security_classification="unclassified",
        )

    @classmethod
    def for_internal_only(cls, audiences: Tuple[str, ...] = ()) -> WorkspaceContentVisibility:
        """
        Create an internal-only visibility specification.

        Args:
            audiences: Specific audience types that may see this content

        Returns:
            Visibility restricted to internal consumers.
        """
        return cls(
            visibility_state="internal_only",
            visibility_scope=audiences or ("working_memory", "reasoning"),
            security_classification="unclassified",
        )

    @classmethod
    def for_confidential(cls, authorized_audiences: Tuple[str, ...]) -> WorkspaceContentVisibility:
        """
        Create a confidential visibility specification.

        Args:
            authorized_audiences: Only these audiences may see the content

        Returns:
            Visibility with restricted access.
        """
        return cls(
            visibility_state="confidential",
            visibility_scope=authorized_audiences,
            requires_authz=True,
            authz_requirements=("confidential clearance",),
            security_classification="confidential",
        )

    @classmethod
    def hidden(cls) -> WorkspaceContentVisibility:
        """Create a hidden visibility state."""
        return cls(
            visibility_state="hidden",
            is_hidden=True,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentAccessibility:
    """
    Immutable accessibility specification for workspace content.

    Accessibility defines whether one can access the content they can see.
    It does NOT imply broadcast eligibility.

    ARCHITECTURAL INVARIANTS:
        CA-INV-001: Accessibility never implies visibility
        CA-INV-002: Accessibility never requires runtime evaluation
        CA-INV-003: Restricted accessibility may still be accessible

    ACCESSIBILITY STATES:
        accessible      - Can be accessed without restrictions
        restricted      - Access subject to conditions
        deferred        - Access postponed until conditions met
        blocked         - Access explicitly prevented
        conditional     - Access dependent on external conditions
        unknown         - Accessibility cannot be determined
    """

    # Accessibility state
    accessibility_state: str = "accessible"
    """Detailed accessibility state (see ACCESSIBILITY STATES)."""

    accessibility_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for access."""

    is_accessible: bool = True
    """Whether this content is accessible."""

    is_restricted: bool = False
    """Whether access is restricted."""

    is_blocked: bool = False
    """Whether access is explicitly blocked."""

    is_deferred: bool = False
    """Whether access is deferred."""

    # Access control
    requires_authz: bool = False
    """Whether authorization is required for access."""

    authz_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Authorization requirements if applicable."""

    # Resource constraints
    resource_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Resource requirements for access."""

    @classmethod
    def fully_accessible(cls) -> WorkspaceContentAccessibility:
        """
        Create a fully accessible specification.

        Returns:
            Accessibility with no restrictions.
        """
        return cls(
            accessibility_state="accessible",
            is_accessible=True,
        )

    @classmethod
    def restricted(cls, conditions: Tuple[str, ...]) -> WorkspaceContentAccessibility:
        """
        Create a restricted accessibility specification.

        Args:
            conditions: Conditions that must be met for access

        Returns:
            Accessibility with required conditions.
        """
        return cls(
            accessibility_state="restricted",
            accessibility_conditions=conditions,
            is_accessible=True,
            is_restricted=True,
        )

    @classmethod
    def blocked(cls) -> WorkspaceContentAccessibility:
        """Create a blocked accessibility state."""
        return cls(
            accessibility_state="blocked",
            is_blocked=True,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentAvailability:
    """
    Immutable availability specification for workspace content.

    Availability defines whether the content is currently available.
    It is semantic and does not require runtime evaluation.

    ARCHITECTURAL INVARIANTS:
        CA-INV-001: Availability never requires current time
        CA-INV-002: Unavailable content may become available later
        CA-INV-003: Archived content remains semantically valid

    AVAILABILITY STATES:
        available           - Currently accessible and usable
        temporarily_unavailable - Temporarily inaccessible
        withheld            - Intentionally made unavailable
        pending             - Awaiting availability conditions
        retired             - No longer in active use
        archived            - Preserved but not actively used
    """

    # Availability state
    availability_state: str = "available"
    """Detailed availability state (see AVAILABILITY STATES)."""

    is_available: bool = True
    """Whether this content is available."""

    is_temporarily_unavailable: bool = False
    """Whether temporarily unavailable."""

    is_withheld: bool = False
    """Whether intentionally withheld."""

    is_pending: bool = False
    """Whether pending availability conditions."""

    is_retired: bool = False
    """Whether retired from active use."""

    is_archived: bool = False
    """Whether archived for preservation."""

    # Temporal information
    available_from_ref: Optional[str] = None
    """Semantic time when content became or will become available."""

    unavailable_until_ref: Optional[str] = None
    """Semantic time when unavailable status will end (if known)."""

    # Special availability
    is_temporary: bool = False
    """Whether availability is temporary by design."""

    @classmethod
    def available(cls) -> WorkspaceContentAvailability:
        """
        Create an available specification.

        Returns:
            Availability indicating content is accessible.
        """
        return cls(
            availability_state="available",
            is_available=True,
        )

    @classmethod
    def temporarily_unavailable(cls, until_ref: str) -> WorkspaceContentAvailability:
        """
        Create a temporarily unavailable specification.

        Args:
            until_ref: Semantic time when availability will resume

        Returns:
            Availability indicating temporary unavailability.
        """
        return cls(
            availability_state="temporarily_unavailable",
            is_available=False,
            is_temporarily_unavailable=True,
            unavailable_until_ref=until_ref,
            is_temporary=True,
        )

    @classmethod
    def archived(cls) -> WorkspaceContentAvailability:
        """Create an archived availability state."""
        return cls(
            availability_state="archived",
            is_archived=True,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentOwnership:
    """
    Immutable ownership information for workspace content.

    Ownership preserves external source withoutWorkspace ever becoming
    the owner. This is a PROJECTION of ownership, not acquisition.

    ARCHITECTURAL INVARIANTS:
        CO-INV-001: Workspace NEVER owns represented artifacts
        CO-INV-002: Ownership references are external only
        CO-INV-003: Ownership never changes implicitly

    OWNERSHIP PRINCIPLES:
        - Original source always preserved
        - Transfer history tracked explicitly
        - No ownership assumption by Workspace
        - Provenance includes ownership lineage
    """

    # Authoritative ownership
    authoritative_owner: str = "unknown"
    """The true owner of the represented artifact."""

    originating_capability: str = ""
    """Capability that originated this content projection."""

    originating_artifact_ref: Optional[str] = None
    """Reference to original artifact (NOT ownership transfer)."""

    # Ownership history
    ownership_history: Tuple[str, ...] = field(default_factory=tuple)
    """Explicit ownership transfers (original first)."""

    ownership_revision: int = 1
    """Revision of ownership information."""

    # Transfer policy
    ownership_transfer_policy: str = "none"
    """Policy for ownership transfer (none, documented, verified)."""

    # Constraints
    ownership_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints on ownership representation."""

    @classmethod
    def from_source(
        cls,
        source_network: str,
        source_artifact_ref: Optional[str],
    ) -> WorkspaceContentOwnership:
        """
        Create ownership from source information.

        Args:
            source_network: Network that owns the artifact
            source_artifact_ref: Reference to the artifact

        Returns:
            Ownership with source preserved.
        """
        return cls(
            authoritative_owner=source_network,
            originating_capability="unknown",
            originating_artifact_ref=source_artifact_ref,
        )

    @classmethod
    def from_reflection(cls, thought_id: str) -> WorkspaceContentOwnership:
        """Create ownership for reflection-originated content."""
        return cls(
            authoritative_owner="DEFAULT_NETWORK",
            originating_capability="reflection",
            originating_artifact_ref=f"thought_{thought_id}",
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentAuthority:
    """
    Immutable authority information for workspace content.

    Authority defines who may create, modify, approve, or withdraw
    the content. It is separate from ownership.

    ARCHITECTURAL INVARIANTS:
        CA-INV-001: Authority never implies ownership
        CA-INV-002: Ownership never implies authority
        CA-INV-003: Multiple authorities may apply

    AUTHORITY TYPES:
        creation      - Who may create the content
        revision      - Who may modify or update
        approval      - Who may approve for workspace admission
        publication   - Who may publish or broadcast
        withdrawal    - Who may withdraw or invalidate
        invalidation  - Who may declare content invalid
        retirement    - Who may retire from active use
    """

    # Authority types
    creation_authority: Tuple[str, ...] = field(default_factory=tuple)
    """Who may create this content."""

    revision_authority: Tuple[str, ...] = field(default_factory=tuple)
    """Who may modify or update this content."""

    approval_authority: Tuple[str, ...] = field(default_factory=tuple)
    """Who may approve for workspace admission."""

    publication_authority: Tuple[str, ...] = field(default_factory=tuple)
    """Who may publish or broadcast this content."""

    withdrawal_authority: Tuple[str, ...] = field(default_factory=tuple)
    """Who may withdraw this content."""

    invalidation_authority: Tuple[str, ...] = field(default_factory=tuple)
    """Who may invalidate this content."""

    retirement_authority: Tuple[str, ...] = field(default_factory=tuple)
    """Who may retire this content from active use."""

    # Authority verification
    authority_verified: bool = False
    """Whether authority has been verified."""

    verification_authorities: Tuple[str, ...] = field(default_factory=tuple)
    """Authorities that verified the authority information."""

    @classmethod
    def for_workspace_content(cls) -> WorkspaceContentAuthority:
        """
        Create authority for standard workspace content.

        Returns:
            Authority with workspace-specific rules.
        """
        return cls(
            creation_authority=("originating_capability",),
            revision_authority=("original_authority", "verified_reviewer"),
            approval_authority=("workspace_admission_authority",),
            publication_authority=("workspace_broadcast_authority",),
            withdrawal_authority=("original_authority", "workspace_admin"),
            invalidation_authority=("workspace_verification_authority",),
        )

    @classmethod
    def for_public_content(cls) -> WorkspaceContentAuthority:
        """Create authority for public content."""
        return cls(
            creation_authority=("any",),
            revision_authority=("publicly_verified",),
            approval_authority=(),
            publication_authority=("any",),
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentProvenance:
    """
    Immutable provenance tracking for workspace content.

    Provenance preserves the complete origin chain. It is fundamental
    to semantic integrity and trustworthiness.

    ARCHITECTURAL INVARIANTS:
        CP-INV-001: Every content has complete provenance
        CP-INV-002: Provenance cannot be lost or modified
        CP-INV-003: Provenance is always replayable

    PROVENANCE COMPONENTS:
        - Origin: Where content came from
        - Generation chain: Transformations applied
        - Validation history: Verifications performed
        - Dependencies: Required artifacts
        - Constraints: Limiting factors
    """

    # Origin
    origin: str = "unknown"
    """Original source of the content."""

    originating_capability: Optional[str] = None
    """Capability that generated this content."""

    originating_artifact_ref: Optional[str] = None
    """Reference to original artifact (NOT ownership)."""

    originating_revision: int = 1
    """Revision of the origin artifact."""

    # Generation chain
    generation_chain: Tuple[str, ...] = field(default_factory=tuple)
    """Chain of transformations (oldest first)."""

    transformation_history: Tuple[str, ...] = field(default_factory=tuple)
    """Detailed history of all transformations."""

    # Validation history
    validation_history: Tuple[str, ...] = field(default_factory=tuple)
    """History of validations performed."""

    verification_chain: Tuple[str, ...] = field(default_factory=tuple)
    """Chain of verifications performed."""

    # Dependencies
    semantic_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic artifacts this content depends on."""

    required_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    """Required artifacts for interpretation."""

    optional_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    """Optional artifacts for enhanced understanding."""

    # Constraints
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints on interpretation or use."""

    assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions underlying the content."""

    # Evidence
    supporting_evidence_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence."""

    @classmethod
    def from_reflection(cls, thought_id: str) -> WorkspaceContentProvenance:
        """
        Create provenance from reflection generation.

        Args:
            thought_id: ID of the reflection artifact

        Returns:
            Provenance with reflection lineage.
        """
        return cls(
            origin="DEFAULT_NETWORK",
            originating_capability="reflection",
            originating_artifact_ref=f"thought_{thought_id}",
            generation_chain=(f"thought_generation_{thought_id}",),
            validation_history=("semantic_validation", "consistency_check"),
        )

    @classmethod
    def from_executive(cls, request_id: str) -> WorkspaceContentProvenance:
        """
        Create provenance from Executive request.

        Args:
            request_id: ID of the executive request

        Returns:
            Provenance with executive lineage.
        """
        return cls(
            origin="EXECUTIVE_NETWORK",
            originating_capability="coordination",
            originating_artifact_ref=f"request_{request_id}",
            generation_chain=(f"request_processing_{request_id}",),
            validation_history=("authority_check", "policy_review"),
        )

    @classmethod
    def from_external_source(cls, source: str) -> WorkspaceContentProvenance:
        """
        Create provenance for externally sourced content.

        Args:
            source: External source identifier

        Returns:
            Provenance with external origin.
        """
        return cls(
            origin=source,
            originating_capability="external",
            constraints=("external_source", "verified_origin"),
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentConstraint:
    """
    Immutable constraint specification for workspace content.

    Constraints limit how content may be used or interpreted.
    They are semantic and do not require runtime enforcement.

    ARCHITECTURAL INVARIANTS:
        C-INV-001: Constraints never guarantee compliance
        C-INV-002: Constraints are always explicit
        C-INV-003: Violated constraints may still be broadcast

    CONSTRAINT TYPES:
        privacy       - Privacy or disclosure restrictions
        security      - Security classification requirements
        policy        - Policy or procedure requirements
        ownership     - Ownership-related limitations
        consumer      - Consumer-specific restrictions
        scope         - Scope of application
        time          - Temporal limitations
        dependency    - Dependency constraints
        resource      - Resource availability constraints
    """

    # Constraint types
    privacy_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Privacy or disclosure restrictions."""

    security_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Security classification requirements."""

    policy_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Policy or procedure requirements."""

    ownership_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Ownership-related limitations."""

    consumer_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Consumer-specific restrictions."""

    scope_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Scope of application constraints."""

    time_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Temporal limitations."""

    dependency_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Dependency constraints."""

    resource_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Resource availability constraints."""

    # Constraint enforcement
    is_enforceable: bool = False
    """Whether constraints are enforceable in practice."""

    violation_severity: str = "warning"
    """Severity when constraint may be violated (info, warning, error)."""

    @classmethod
    def for_internal_content(cls) -> WorkspaceContentConstraint:
        """
        Create constraints for internal workspace content.

        Returns:
            Constraints appropriate for internal use.
        """
        return cls(
            privacy_constraints=("internal_only",),
            security_constraints=("unclassified",),
        )

    @classmethod
    def for_confidential_content(cls) -> WorkspaceContentConstraint:
        """Create constraints for confidential content."""
        return cls(
            privacy_constraints=("confidential", "need_to_know"),
            security_constraints=("confidential_classification",),
            is_enforceable=True,
            violation_severity="error",
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentDependency:
    """
    Immutable dependency specification for workspace content.

    Dependencies represent required artifacts for proper interpretation
    or use of this content. No resolution occurs at semantic level.

    ARCHITECTURAL INVARIANTS:
        CD-INV-001: Dependencies never get resolved semantically
        CD-INV-002: Missing dependencies don't invalidate content
        CD-INV-003: Dependencies are always explicit references

    DEPENDENCY TYPES:
        semantic      - Semantic artifacts this depends on
        required      - Must be present for interpretation
        optional      - Enhance understanding if present
        contextual    - Context needed for proper meaning
        assumption    - Assumptions underlying content
    """

    # Dependency types
    semantic_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic artifacts this depends on."""

    required_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies required for interpretation."""

    optional_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies that enhance understanding."""

    contextual_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Context needed for proper meaning."""

    assumption_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions underlying the content."""

    # Dependency resolution
    dependencies_resolved: bool = False
    """Whether all required dependencies are present."""

    missing_dependency_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to missing required dependencies."""

    @classmethod
    def from_context(
        cls,
        semantic_deps: Tuple[str, ...] = (),
        required: Tuple[str, ...] = (),
    ) -> WorkspaceContentDependency:
        """
        Create dependency from context.

        Args:
            semantic_deps: Semantic artifacts this depends on
            required: Required dependencies for interpretation

        Returns:
            Dependency specification.
        """
        return cls(
            semantic_dependencies=semantic_deps,
            required_dependencies=required,
            dependencies_resolved=len(required) == 0,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentAssumption:
    """
    Immutable assumption record for workspace content.

    Assumptions are explicit beliefs or premises underlying the content.
    They must be preserved and cannot be changed implicitly.

    ARCHITECTURAL INVARIANTS:
        CA-INV-001: Assumptions are always explicit
        CA-INV-002: Assumptions never change without revision
        CA-INV-003: Assumption changes require new content

    ASSUMPTION TYPES:
        factual       - Factual premises assumed true
        contextual    - Context assumed to hold
        temporal      - Temporal conditions assumed
        causal        - Causal relationships assumed
        logical       - Logical assumptions made
    """

    # Assumption details
    assumption_text: str = ""
    """The explicit assumption statement."""

    assumption_type: str = "factual"
    """Type of assumption (see ASSUMPTION TYPES)."""

    confidence_level: float = 0.5
    """Confidence in this assumption (0.0-1.0)."""

    # Assumption metadata
    source_ref: Optional[str] = None
    """Reference to source of this assumption."""

    justification: Optional[str] = None
    """Justification for making this assumption."""

    # Dependencies on assumptions
    depends_on_assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Other assumptions this depends on."""

    contradicts_assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions this contradicts (if any)."""

    @classmethod
    def create(
        cls,
        text: str,
        assumption_type: str = "factual",
        confidence: float = 0.5,
    ) -> WorkspaceContentAssumption:
        """
        Create an assumption record.

        Args:
            text: The explicit assumption statement
            assumption_type: Type of assumption
            confidence: Confidence level in the assumption

        Returns:
            New assumption record.
        """
        return cls(
            assumption_text=text,
            assumption_type=assumption_type,
            confidence_level=confidence,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentEvidence:
    """
    Immutable evidence record for workspace content.

    Evidence supports or challenges the validity of content.
    Evidence remains externally owned and referenced.

    ARCHITECTURAL INVARIANTS:
        CE-INV-001: Evidence is always external to content
        CE-INV-002: Evidence references are never ownership transfers
        CE-INV-003: Evidence may be supporting or challenging

    EVIDENCE TYPES:
        supporting    - Supports the content's validity
        challenging   - Challenges the content's validity
        contextual    - Provides context for interpretation
        contradictory - Directly contradicts the content
    """

    # Evidence details
    evidence_ref: str = ""
    """Reference to evidence artifact (NOT ownership)."""

    evidence_type: str = "supporting"
    """Type of evidence (see EVIDENCE TYPES)."""

    relevance: float = 0.5
    """Relevance of this evidence (0.0-1.0)."""

    strength: float = 0.5
    """Strength of this evidence (0.0-1.0)."""

    # Evidence metadata
    source_ref: Optional[str] = None
    """Reference to original evidence source."""

    quality_score: float = 0.5
    """Quality assessment of the evidence."""

    is_verified: bool = False
    """Whether this evidence has been verified."""

    @classmethod
    def supporting(cls, ref: str) -> WorkspaceContentEvidence:
        """
        Create a supporting evidence record.

        Args:
            ref: Reference to supporting evidence

        Returns:
            Evidence that supports the content.
        """
        return cls(
            evidence_ref=ref,
            evidence_type="supporting",
            relevance=1.0,
            strength=1.0,
        )

    @classmethod
    def challenging(cls, ref: str) -> WorkspaceContentEvidence:
        """
        Create a challenging evidence record.

        Args:
            ref: Reference to challenging evidence

        Returns:
            Evidence that challenges the content.
        """
        return cls(
            evidence_ref=ref,
            evidence_type="challenging",
            relevance=1.0,
        )


@dataclass(frozen=True, slots=True)
class WorkspaceContentJustification:
    """
    Immutable justification record for workspace content.

    Justification provides rationale, support, and explanation for
    the content's validity and meaning.

    ARCHITECTURAL INVARIANTS:
        CJ-INV-001: Justification never replaces evidence
        CJ-INV-002: Justification is always explicit
        CJ-INV-003: Missing justification doesn't invalidate content

    JUSTIFICATION COMPONENTS:
        rationale     - Why this content makes sense
        support       - What backs up the content
        reason        - The logical basis
        explanation   - How to understand it
        evidence_refs - References to supporting evidence
        assumptions   - Underlying assumptions
        constraints   - Limiting factors
    """

    # Justification components
    rationale: str = ""
    """Rationale for this content."""

    support: Tuple[str, ...] = field(default_factory=tuple)
    """Supporting information or facts."""

    reason: Optional[str] = None
    """The logical basis for the content."""

    explanation: Optional[str] = None
    """How to understand this content."""

    # Evidence references
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence."""

    # Assumptions and constraints
    underlying_assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions underlying the justification."""

    constraints_applied: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints that were considered."""

    @classmethod
    def from_rationale(cls, rationale: str) -> WorkspaceContentJustification:
        """
        Create a justification from a rationale.

        Args:
            rationale: The explanation or reasoning

        Returns:
            Justification with the provided rationale.
        """
        return cls(
            rationale=rationale,
        )

    @classmethod
    def from_evidence(cls, evidence_refs: Tuple[str, ...]) -> WorkspaceContentJustification:
        """
        Create a justification based on evidence.

        Args:
            evidence_refs: References to supporting evidence

        Returns:
            Justification citing the evidence.
        """
        return cls(
            rationale="Evidence-based justification",
            evidence_references=evidence_refs,
        )


# =============================================================================
# WORKSPACE CONTENT - PRIMARY SEMANTIC ARTIFACT
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceContent:
    """
    Immutable semantic content projection for workspace availability.

    This is a bounded projection of source artifact semantics. It does NOT
    own or replace the source artifact - it merely references and projects
    its relevant semantic aspects for global cognitive availability.

    ARCHITECTURAL INVARIANTS:
        WC-INV-001: Source ownership preserved (this is only a projection)
        WC-INV-002: No runtime dependencies in semantic artifacts
        WC-INV-003: Bounded collections only
        WC-INV-004: Identity is deterministic and replayable
        WC-INV-005: Revision never implies change of meaning
        WC-INV-006: Ownership never changes implicitly

    NOT RESPONSIBLE FOR:
        - Runtime broadcast delivery
        - Target capability execution
        - Working Memory mutation
        - Policy enforcement
        - Security enforcement
        - Time acquisition
        - UUID generation

    SEMANTIC FIELDS:
        identity              - Unique identifier (deterministic)
        revision              - Version number (monotonic)
        kind                  - Category of semantic content
        summary               - Brief description
        semantic_description  - Detailed semantic content
        payload_ref           - Reference to full payload
        source_ref            - Reference to original artifact
        ownership             - External ownership information
        authority             - Authority constraints
        context               - Semantic context
        scope                 - Broadcast eligibility
        validity              - Validation state
        freshness             - Temporal relevance
        visibility            - Who may see this content
        accessibility         - Whether it can be accessed
        availability          - Whether currently available
        confidence            - Confidence in the content
        uncertainty           - Uncertainty about the content
        constraints           - Limiting factors
        dependencies          - Required artifacts
        assumptions           - Underlying assumptions
        evidence              - Supporting evidence
        justification         - Rationale and explanation
        provenance            - Origin chain
    """

    # Identity and revision - no defaults must come first
    content_id: WorkspaceContentIdentity
    """Unique identifier for this content instance."""

    revision: WorkspaceContentRevision = 1
    """Monotonically increasing revision number."""

    # Kind - has no default but comes after revision (which has a default)
    # In dataclasses, all fields with defaults must come after fields without defaults
    # Since revision has a default (=1), kind must also have one.
    # We use a sentinel value that gets replaced during validation or class construction
    kind: str = "unknown"  # WorkspaceContentKind.*
    """Canonical category of semantic content."""

    # Core semantic representation - these have defaults but come after required fields
    summary: Optional[str] = None
    """Brief summary for diagnostics (not replacement)."""

    semantic_description: Tuple[str, ...] = field(default_factory=tuple)
    """Typed semantic assertions from source artifact."""

    payload_ref: Optional[str] = None
    """Reference to full semantic payload (NOT ownership)."""

    # Source and provenance - these have defaults but come after required fields
    digest: Optional[WorkspaceContentDigest] = None
    """Cryptographic or deterministic digest of semantic content."""

    fingerprint: Optional[WorkspaceContentFingerprint] = None
    """Short fingerprint for quick identification."""

    source_artifact_ref: Optional[str] = None
    """Reference to original source artifact (NOT ownership)."""

    # Ownership - default factory but comes after required fields
    ownership: WorkspaceContentOwnership = field(
        default_factory=WorkspaceContentOwnership
    )
    """External ownership information."""

    authority: WorkspaceContentAuthority = field(
        default_factory=WorkspaceContentAuthority.for_workspace_content
    )
    """Authority constraints for creation and modification."""

    # Context - default factory but comes after required fields
    context: WorkspaceContentContext = field(
        default_factory=WorkspaceContentContext
    )
    """Semantic context without runtime embedding."""

    scope: WorkspaceContentScope = field(
        default_factory=WorkspaceContentScope.for_general_workspace
    )
    """Broadcast eligibility and target scope."""

    # Validity - default factory but comes after required fields
    validity: WorkspaceContentValidity = field(
        default_factory=WorkspaceContentValidity.valid
    )
    """Validation state."""

    freshness: WorkspaceContentFreshness = field(
        default_factory=WorkspaceContentFreshness.eternal
    )
    """Temporal relevance without internal time acquisition."""

    visibility: WorkspaceContentVisibility = field(
        default_factory=WorkspaceContentVisibility.for_internal_only
    )
    """Who may see this content."""

    accessibility: WorkspaceContentAccessibility = field(
        default_factory=WorkspaceContentAccessibility.fully_accessible
    )
    """Whether it can be accessed by viewers."""

    availability: WorkspaceContentAvailability = field(
        default_factory=WorkspaceContentAvailability.available
    )
    """Whether currently available for use."""

    confidence_level: float = 0.5
    """Confidence in the content's validity (0.0-1.0)."""

    confidence_source: Optional[str] = None
    """Source of confidence assessment (if known)."""

    confidence_method: str = "heuristic"
    """Method used for confidence assessment."""

    uncertainty_level: float = 0.5
    """Uncertainty about the content (0.0-1.0)."""

    uncertainty_type: str = "unknown"
    """Type of uncertainty (ambiguous, estimated, conflicting, etc.)."""

    constraints: WorkspaceContentConstraint = field(
        default_factory=WorkspaceContentConstraint.for_internal_content
    )
    """Limiting factors on use or interpretation."""

    dependencies: WorkspaceContentDependency = field(
        default_factory=WorkspaceContentDependency.from_context
    )
    """Required artifacts for proper interpretation."""

    assumptions: Tuple[WorkspaceContentAssumption, ...] = field(default_factory=tuple)
    """Explicit underlying assumptions."""

    evidence: Tuple[WorkspaceContentEvidence, ...] = field(default_factory=tuple)
    """Supporting or challenging evidence."""

    justification: Optional[WorkspaceContentJustification] = None
    """Rationale and explanation for the content."""

    provenance: WorkspaceContentProvenance = field(
        default_factory=lambda: WorkspaceContentProvenance()
    )
    """Origin chain without runtime dependencies."""

    @classmethod
    def create_insight(
        cls,
        content_id: str,
        semantic_claim: str,
        source_artifact_ref: Optional[str] = None,
    ) -> WorkspaceContent:
        """
        Create an insight content projection.

        Args:
            content_id: External or deterministically derived identity
            semantic_claim: The semantic assertion
            source_artifact_ref: Reference to original artifact (if any)

        Returns:
            New WorkspaceContent instance (kind=INSIGHT)
        """
        return cls(
            content_id=content_id,
            kind="insight",
            semantic_description=(semantic_claim,),
            source_artifact_ref=source_artifact_ref,
            context=WorkspaceContentContext.from_reflection(content_id),
            scope=WorkspaceContentScope.for_general_workspace(),
            validity=WorkspaceContentValidity.valid(),
            confidence_level=0.7,
        )

    @classmethod
    def create_concern(
        cls,
        content_id: str,
        description: str,
        source_artifact_ref: Optional[str] = None,
    ) -> WorkspaceContent:
        """
        Create a concern content projection.

        Args:
            content_id: External or deterministically derived identity
            description: The concern description
            source_artifact_ref: Reference to original artifact (if any)

        Returns:
            New WorkspaceContent instance (kind=CONCERN)
        """
        return cls(
            content_id=content_id,
            kind="concern",
            semantic_description=(description,),
            source_artifact_ref=source_artifact_ref,
            context=WorkspaceContentContext.from_reflection(content_id),
            scope=WorkspaceContentScope.for_executive_review(),
            validity=WorkspaceContentValidity.valid(),
        )

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> WorkspaceContent:
        """
        Create WorkspaceContent from a dictionary.

        This is for serialization/deserialization. The content must be
        deterministically derived to maintain invariants.

        Args:
            data: Dictionary representation

        Returns:
            New WorkspaceContent instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not isinstance(data, dict):
            raise ValueError("WorkspaceContent.from_dict expects a dictionary")

        # Required fields
        content_id = data.get("content_id")
        if not isinstance(content_id, str) or not content_id:
            raise ValueError("WorkspaceContent requires 'content_id' string field")

        kind = data.get("kind")
        if not isinstance(kind, str) or not kind:
            raise ValueError("WorkspaceContent requires 'kind' string field")

        # Optional fields with defaults
        revision = int(data.get("revision", 1))
        if revision < 1:
            raise ValueError("Revision must be >= 1")

        return cls(
            content_id=content_id,
            revision=revision,
            kind=kind,
            summary=data.get("summary"),
            semantic_description=tuple(str(x) for x in data.get("semantic_description", []) or []),
            payload_ref=data.get("payload_ref"),
            source_artifact_ref=data.get("source_artifact_ref"),
            context=WorkspaceContentContext(**data.get("context", {}) or {}),
            scope=WorkspaceContentScope(**data.get("scope", {}) or {}),
            validity=WorkspaceContentValidity(**data.get("validity", {}) or {}),
            freshness=WorkspaceContentFreshness(**data.get("freshness", {}) or {}),
            visibility=WorkspaceContentVisibility(**data.get("visibility", {}) or {}),
            accessibility=WorkspaceContentAccessibility(**data.get("accessibility", {}) or {}),
            availability=WorkspaceContentAvailability(**data.get("availability", {}) or {}),
            confidence_level=float(data.get("confidence_level", 0.5)),
            uncertainty_level=float(data.get("uncertainty_level", 0.5)),
        )

    def to_dict(self) -> Dict[str, object]:
        """
        Convert to dictionary representation.

        Returns:
            Dictionary suitable for serialization
        """
        return {
            "content_id": self.content_id,
            "revision": self.revision,
            "kind": self.kind,
            "summary": self.summary,
            "semantic_description": list(self.semantic_description),
            "payload_ref": self.payload_ref,
            "source_artifact_ref": self.source_artifact_ref,
            "context": vars(self.context) if self.context else {},
            "scope": vars(self.scope) if self.scope else {},
            "validity": vars(self.validity) if self.validity else {},
            "freshness": vars(self.freshness) if self.freshness else {},
            "visibility": vars(self.visibility) if self.visibility else {},
            "accessibility": vars(self.accessibility) if self.accessibility else {},
            "availability": vars(self.availability) if self.availability else {},
            "confidence_level": self.confidence_level,
            "uncertainty_level": self.uncertainty_level,
        }

    def with_revision(self, new_revision: int) -> WorkspaceContent:
        """
        Create a copy with a new revision number.

        This is the canonical way to represent a semantic change.
        No in-place mutation occurs.

        Args:
            new_revision: The new revision number (must be > current)

        Returns:
            New WorkspaceContent instance with updated revision
        """
        if new_revision <= self.revision:
            raise ValueError(f"New revision {new_revision} must be > current {self.revision}")

        return replace(self, revision=new_revision)

    def is_equivalent_to(self, other: WorkspaceContent) -> bool:
        """
        Check if this content is equivalent to another.

        Two contents are equivalent if they have the same identity
        and revision. Semantic equivalence is not assessed here -
        that requires comparing all fields.

        Args:
            other: Another WorkspaceContent instance

        Returns:
            True if this and other have same identity and revision
        """
        return (
            self.content_id == other.content_id
            and self.revision == other.revision
        )


# =============================================================================
# UTILITY FUNCTIONS - Content manipulation without runtime dependencies
# =============================================================================

def generate_content_identity(
    source_network: str,
    source_artifact_ref: str,
    semantic_hash: str,
) -> WorkspaceContentIdentity:
    """
    Generate a deterministic content identity.

    This function produces the same output for the same inputs, enabling
    replayability and verification without runtime state.

    Args:
        source_network: The network that owns the artifact
        source_artifact_ref: Reference to the original artifact
        semantic_hash: Hash of the semantic content

    Returns:
        Deterministic identity string in format:
        "{source_network}:{source_artifact_ref}@{semantic_hash[:16]}"
    """
    short_hash = semantic_hash[:16] if len(semantic_hash) >= 16 else semantic_hash
    return f"{source_network}:{source_artifact_ref}@{short_hash}"


def generate_content_digest(semantic_payload: str) -> WorkspaceContentDigest:
    """
    Generate a deterministic content digest.

    This function produces the same digest for the same semantic payload,
    enabling integrity verification without runtime state.

    Note: In production, this would use SHA-256 or similar cryptographic
    hash. For now, we return a deterministic representation.

    Args:
        semantic_payload: The semantic content to hash

    Returns:
        Deterministic digest string
    """
    # Placeholder for cryptographic hash implementation
    # In production: hashlib.sha256(semantic_payload.encode()).hexdigest()
    return f"digest_{len(semantic_payload)}_{hash(semantic_payload) & 0xFFFFFFFF:08x}"


def generate_content_fingerprint(content_id: WorkspaceContentIdentity) -> WorkspaceContentFingerprint:
    """
    Generate a short fingerprint for a content identity.

    Args:
        content_id: The full content identity

    Returns:
        Short fingerprint string (typically first 8-16 characters)
    """
    return content_id[:12] if len(content_id) >= 12 else content_id


# =============================================================================
# CONTENT LIFECYCLE STATES
# =============================================================================

class WorkspaceContentLifecycle(Enum):
    """
    Semantic lifecycle states for workspace content.

    These are semantic states, not runtime state. They describe the
    logical progression of a content artifact through its existence.

    LIFECYCLE TRANSITIONS:
        Created       -> Referenced      (Source system creates content)
        Referenced    -> Projected       (Workspace projects content)
        Projected     -> Revised         (New revision created)
        Revised       -> Restricted      (Access limited by authority)
        Restricted    -> Visible         (Authority allows visibility)
        Visible       -> Archived        (Content preserved but inactive)
        Visible       -> Withdrawn       (Retracted by authority)
        Withdrawn     -> Invalidated     (Declared invalid)

    ARCHITECTURAL INVARIANTS:
        CL-INV-001: Lifecycle is semantic, not runtime
        CL-INV-002: States are mutually exclusive
        CL-INV-003: Transitions must be explicit

    NOT RESPONSIBLE FOR:
        - Runtime state transitions
        - Time-based expiration
        - External system interaction
    """

    # Initial states
    CREATED = "created"
    """Content has been created but not yet projected."""

    REFERENCED = "referenced"
    """Content has been referenced by source system."""

    PROJECTED = "projected"
    """Content is projected into workspace context."""

    # Active states
    REVISION_INITIATED = "revision_initiated"
    """New revision being prepared."""

    REVISING = "revising"
    """Content is in the process of being revised."""

    REVISED = "revised"
    """Content has been revised with new semantics."""

    RESTRICTED = "restricted"
    """Access is restricted by authority."""

    VISIBLE = "visible"
    """Content is visible to eligible consumers."""

    # Inactive states
    ARCHIVED = "archived"
    """Content preserved but not actively used."""

    WITHDRAWN = "withdrawn"
    """Retracted by authorized entity."""

    INVALIDATED = "invalidated"
    """Declared semantically invalid."""

    EXPIRED = "expired"
    """Semantic expiration reached."""

    SUPERSDED = "superseded"
    """Replaced by newer revision."""

    TERMINATED = "terminated"
    """Permanently removed from active lifecycle."""


# =============================================================================
# CONTENT METADATA
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceContentMetadata:
    """
    Immutable metadata for workspace content.

    Metadata provides administrative and operational information
    about the content without affecting its semantic meaning.

    ARCHITECTURAL INVARIANTS:
        CM-INV-001: Metadata never affects content validity
        CM-INV-002: Metadata is always bounded
        CM-INV-003: Metadata has no runtime dependencies
    """

    # Administrative metadata
    labels: Tuple[str, ...] = field(default_factory=tuple)
    """Labels for categorization and search."""

    annotations: Dict[str, str] = field(default_factory=dict)
    """Annotations providing additional context."""

    priority_reference: Optional[str] = None
    """Reference to priority level or system."""

    salience_reference: Optional[str] = None
    """Reference to salience assessment."""

    # Task and goal relevance (references only)
    task_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to relevant tasks."""

    goal_relevance_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to relevant goals."""

    # Classification
    privacy_classification: str = "internal_only"
    """Privacy classification level."""

    security_classification: str = "unclassified"
    """Security classification level."""

    policy_classification: str = "standard"
    """Policy classification level."""

    @classmethod
    def for_high_priority(cls, priority_ref: str) -> WorkspaceContentMetadata:
        """
        Create metadata with high priority reference.

        Args:
            priority_ref: Reference to priority system or level

        Returns:
            Metadata with high priority designation.
        """
        return cls(
            labels=("high_priority",),
            priority_reference=priority_ref,
        )

    @classmethod
    def for_executive(cls) -> WorkspaceContentMetadata:
        """Create metadata suitable for executive review."""
        return cls(
            labels=("executive_review", "high_priority"),
            security_classification="internal_only",
        )


# =============================================================================
# CONTENT KIND REGISTRY - Extensible kind registration
# =============================================================================

class WorkspaceContentKindRegistry:
    """
    Registry of content kinds for extensibility.

    This class provides a mechanism for registering new content kinds
    while maintaining canonical categories.

    ARCHITECTURAL INVARIANTS:
        CKR-INV-001: Canonical kinds cannot be removed
        CKR-INV-002: Registered kinds must have unique identifiers
        CKR-INV-003: Registry lookup has no runtime dependencies

    EXTENSIBILITY RULES:
        - Canonical kinds (in WorkspaceContentKind) are immutable
        - Custom kinds can be registered for external systems
        - Kind validation is semantic, not runtime-based
    """

    _custom_kinds: Set[str] = set()

    @classmethod
    def register_custom_kind(cls, kind_id: str) -> bool:
        """
        Register a custom content kind.

        Args:
            kind_id: Unique identifier for the new kind

        Returns:
            True if registration succeeded, False if already registered

        Raises:
            ValueError: If kind_id is empty or contains invalid characters
        """
        if not isinstance(kind_id, str) or not kind_id:
            raise ValueError("Kind ID must be a non-empty string")

        # Validate identifier format (alphanumeric and underscore only)
        if not all(c.isalnum() or c == "_" for c in kind_id):
            raise ValueError("Kind ID must contain only alphanumeric characters and underscores")

        if kind_id in cls._custom_kinds:
            return False

        cls._custom_kinds.add(kind_id)
        return True

    @classmethod
    def unregister_custom_kind(cls, kind_id: str) -> bool:
        """
        Unregister a custom content kind.

        Args:
            kind_id: Identifier of the kind to remove

        Returns:
            True if unregistration succeeded, False if not registered
        """
        if kind_id in cls._custom_kinds:
            cls._custom_kinds.remove(kind_id)
            return True
        return False

    @classmethod
    def is_custom_kind(cls, kind_id: str) -> bool:
        """Check if a kind ID is a custom registered kind."""
        return kind_id in cls._custom_kinds

    @classmethod
    def get_all_kinds(cls) -> Tuple[str, ...]:
        """
        Get all known kind identifiers.

        Returns:
            Tuple of all canonical and custom kind identifiers
        """
        canonical = [kind.value for kind in WorkspaceContentKind]
        return tuple(canonical + list(cls._custom_kinds))


# =============================================================================
# CONTENT VALIDATION
# =============================================================================

class WorkspaceContentValidator:
    """
    Validator for WorkspaceContent instances.

    This class provides validation logic without runtime dependencies.
    It checks semantic requirements, not runtime state.

    ARCHITECTURAL INVARIANTS:
        CWV-INV-001: Validation never requires runtime state
        CWV-INV-002: Validation results are deterministic
        CWV-INV-003: Invalid content may still be broadcast (with warning)

    VALIDATION RULES:
        - Identity must be non-empty string
        - Kind must be a known canonical or registered kind
        - Revision must be >= 1
        - Collections must be bounded
        - Confidence and uncertainty must be in [0.0, 1.0]
    """

    MAX_COLLECTION_SIZE = 1000

    @classmethod
    def validate_identity(cls, identity: str) -> bool:
        """Validate that an identity string is valid."""
        if not isinstance(identity, str):
            return False
        if len(identity) == 0:
            return False
        if len(identity) > 256:
            return False
        return True

    @classmethod
    def validate_kind(cls, kind: str) -> bool:
        """Validate that a kind string is valid."""
        if not isinstance(kind, str):
            return False
        if len(kind) == 0:
            return False
        if kind in WorkspaceContentKindRegistry.get_all_kinds():
            return True
        # Check against enum values
        try:
            WorkspaceContentKind(kind)
            return True
        except ValueError:
            pass
        return False

    @classmethod
    def validate_revision(cls, revision: int) -> bool:
        """Validate that a revision number is valid."""
        if not isinstance(revision, int):
            return False
        if revision < 1:
            return False
        return True

    @classmethod
    def validate_confidence(cls, confidence: float) -> bool:
        """Validate that a confidence value is in range [0.0, 1.0]."""
        if not isinstance(confidence, (int, float)):
            return False
        return 0.0 <= confidence <= 1.0

    @classmethod
    def validate_uncertainty(cls, uncertainty: float) -> bool:
        """Validate that an uncertainty value is in range [0.0, 1.0]."""
        if not isinstance(uncertainty, (int, float)):
            return False
        return 0.0 <= uncertainty <= 1.0

    @classmethod
    def validate_content(cls, content: WorkspaceContent) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate a WorkspaceContent instance.

        Args:
            content: The content to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not cls.validate_identity(content.content_id):
            errors.append("Invalid content_id")

        if not cls.validate_kind(content.kind):
            errors.append(f"Invalid kind: {content.kind}")

        if not cls.validate_revision(content.revision):
            errors.append(f"Invalid revision: {content.revision}")

        if not cls.validate_confidence(content.confidence_level):
            errors.append(f"Invalid confidence_level: {content.confidence_level}")

        if not cls.validate_uncertainty(content.uncertainty_level):
            errors.append(f"Invalid uncertainty_level: {content.uncertainty_level}")

        # Check bounded collections
        semantic_count = len(content.semantic_description)
        if semantic_count > cls.MAX_COLLECTION_SIZE:
            errors.append(f"semantic_description exceeds max size ({semantic_count} > {cls.MAX_COLLECTION_SIZE})")

        assumption_count = len(content.assumptions)
        if assumption_count > cls.MAX_COLLECTION_SIZE:
            errors.append(f"assumptions exceeds max size ({assumption_count} > {cls.MAX_COLLECTION_SIZE})")

        evidence_count = len(content.evidence)
        if evidence_count > cls.MAX_COLLECTION_SIZE:
            errors.append(f"evidence exceeds max size ({evidence_count} > {cls.MAX_COLLECTION_SIZE})")

        is_valid = len(errors) == 0
        return is_valid, tuple(errors)


# =============================================================================
# CONTENT COMPARISON AND EQUALITY
# =============================================================================

def content_identity_hash(content_id: str) -> int:
    """
    Generate a hash for a content identity.

    This provides deterministic hashing without runtime time acquisition.
    The same input always produces the same output.

    Args:
        content_id: The content identity string

    Returns:
        Integer hash value
    """
    # Deterministic hash (same as Python's hash() but stable)
    h = 0
    for c in content_id:
        h = ((h << 5) - h + ord(c)) & 0xFFFFFFFFFFFFFFFF
    return h if h < 2**63 else h - 2**64


def content_equality(content1: WorkspaceContent, content2: WorkspaceContent) -> bool:
    """
    Check if two contents are equal based on identity and revision.

    Two contents with the same identity and revision are considered
    semantically equivalent. All other fields may differ due to
    external time or state providers.

    Args:
        content1: First content instance
        content2: Second content instance

    Returns:
        True if identity and revision match
    """
    return (
        content1.content_id == content2.content_id
        and content1.revision == content2.revision
    )