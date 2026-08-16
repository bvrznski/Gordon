# Gordon Cognitive Architecture - Phase 4.11.1
# ===========================================

"""
Coordination Network Core Contract Models
========================================

Canonical immutable data models for coordination contracts.
All models are deeply frozen to ensure deterministic behavior and thread safety.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Import CoordinatedNetworkKind from enums for core_membership()
# Note: Using forward reference since both modules are in same package
from .enums import CoordinatedNetworkKind


# =============================================================================
# SEMANTIC TIME REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SemanticTimeReference:
    """
    Reference to a point in semantic time.
    
    Unlike wall-clock time, semantic time represents meaningful coordination
    boundaries that are stable across runs.
    """
    cycle_id: str = ""
    """Identifier for the coordination cycle."""
    
    step_index: int = 0
    """Index of this reference within the cycle."""


# =============================================================================
# NETWORK IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkIdentity:
    """
    Immutable identity for a coordinated network.
    
    IDENTITY-INV-001: Identity is immutable (deeply frozen)
    IDENTITY-INV-002: Identity has no runtime references
    IDENTITY-LAW-001: Kind is stable across projections
    IDENTITY-LAW-002: Instance identity distinguishes simultaneous instances
    
    COORD-LAW-036: Network kind is stable and versioned
    """
    network_kind: str  # CoordinatedNetworkKind.*
    """Canonical kind of the coordinated network."""
    
    semantic_name: str = "unnamed"
    """Human-readable name for identification."""
    
    instance_identity: str = ""
    """Unique identity distinguishing simultaneous instances."""
    
    network_contract_version: str = "1.0.0"
    """Contract version for this network type."""
    
    projection_contract_version: str = "1.0.0"
    """Projection contract version expected by coordination."""
    
    capability_profile_identity: str = ""
    """Identity of the capability profile."""
    
    authority: str = "peer"
    """Authority level (peer, supervisor, etc.)"""
    
    provenance_ref: Optional[str] = None
    """Reference to identity provenance record."""


# =============================================================================
# COORDINATION REQUEST IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationRequestIdentity:
    """
    Immutable identity for a coordination request.
    
    COORD-ID-INV-001: Request identity is immutable
    COORD-ID-INV-002: Identity is generated deterministically from content
    """
    cycle_id: str
    """Identifier of the coordination cycle."""
    
    sequence_index: int = 0
    """Index within the cycle for ordering."""
    
    def __str__(self) -> str:
        return f"coord-request:{self.cycle_id}:{self.sequence_index}"


# =============================================================================
# COORDINATION CYCLE IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationCycleIdentity:
    """
    Immutable identity for a coordination cycle.
    
    COORD-CYCLE-ID-INV-001: Cycle identity is immutable
    COORD-CYCLE-ID-INV-002: Identity has no runtime references
    
    CYCLE-LAW-001: Every CoordinationCycle possesses stable identity
    """
    cycle_id: str = ""
    """Unique identifier for the cycle."""
    
    sequence_index: int = 0
    """Sequence index within a coordination epoch."""
    
    @classmethod
    def from_epoch(cls, epoch: str) -> CoordinationCycleIdentity:
        """
        Create a cycle identity from an epoch string.
        
        Args:
            epoch: Epoch identifier (e.g., timestamp-based or sequence-based)
            
        Returns:
            A new CoordinationCycleIdentity instance
        """
        return cls(cycle_id=epoch, sequence_index=0)

    def __str__(self) -> str:
        return f"coord-cycle:{self.cycle_id}:{self.sequence_index}"


# =============================================================================
# COORDINATION STATE IDENTITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationStateIdentity:
    """
    Immutable identity for a coordination state.
    
    STATE-ID-INV-001: State identity is immutable
    STATE-ID-INV-002: Identity matches its source cycle
    
    STATE-LAW-001: Exactly one CoordinationState exists per CoordinationCycle
    """
    state_id: str = ""
    """Unique identifier for the state."""
    
    cycle_ref: str = ""
    """Reference to the source coordination cycle."""
    
    revision: int = 1
    """Revision number of this state."""
    
    @classmethod
    def from_cycle(cls, cycle_identity: CoordinationCycleIdentity) -> CoordinationStateIdentity:
        """
        Create a state identity from a cycle identity.
        
        Args:
            cycle_identity: The source coordination cycle identity
            
        Returns:
            A new CoordinationStateIdentity instance
        """
        return cls(
            state_id=f"state-{cycle_identity.cycle_id}",
            cycle_ref=str(cycle_identity),
            revision=1,
        )


# =============================================================================
# COORDINATION MEMBERSHIP
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationMembership:
    """
    Immutable membership model for coordination.
    
    COORD-MEM-INV-001: Membership is immutable (deeply frozen)
    COORD-MEM-INV-002: Membership has no runtime references
    
    MEMBERSHIP-LAW-001: Core membership consists of exactly ten networks
    MEMBERSHIP-LAW-003: Membership shall be explicit
    """
    membership_identity: str = "core:1.0.0"
    """Identity for this membership configuration."""
    
    required_network_kinds: tuple[str, ...] = field(default_factory=tuple)
    """Required network kinds (as strings from CoordinatedNetworkKind)."""
    
    optional_extension_members: tuple[NetworkIdentity, ...] = ()
    """Optional extension members."""
    
    membership_policy: str = "strict"
    """Policy for handling missing/failed memberships."""
    
    contract_version: str = "1.0.0"
    """Contract version for this membership model."""
    
    revision: int = 1
    """Revision number of the membership configuration."""
    
    provenance_ref: Optional[str] = None
    """Reference to membership provenance record."""
    
    @classmethod
    def core_membership(cls) -> CoordinationMembership:
        """
        Create the canonical core membership with all ten coordinated networks.
        
        Returns:
            A new CoordinationMembership instance with core networks
        """
        return cls(
            membership_identity="core:1.0.0",
            required_network_kinds=tuple(kind.name for kind in CoordinatedNetworkKind),
            optional_extension_members=(),
            membership_policy="strict",
            contract_version="1.0.0",
            revision=1,
        )


# =============================================================================
# NETWORK PROJECTION BASE CONTRACT
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkProjection:
    """
    Base immutable projection contract for coordination-facing network state.
    
    PROJECTION-INV-001: Projection is immutable (deeply frozen)
    PROJECTION-INV-002: Projection has no runtime references
    PROJECTION-LAW-001: Every coordinated network exposes exactly one projection
    PROJECTION-LAW-007: Projections expose coordination-facing state only
    
    This is the canonical base projection. Network-specific projections may extend
    this with additional typed fields.
    
    COORD-LAW-037: All projection inputs are immutable
    """
    identity: CoordinationRequestIdentity
    """Unique identity for this projection."""
    
    network_identity: NetworkIdentity
    """Identity of the source network."""
    
    projection_revision: int = 1
    """Revision number of this projection."""
    
    network_revision: int = 1
    """Current revision of the source network state."""
    
    status: str = "nominal"
    """Network coordination status (from NetworkCoordinationStatus)."""
    
    availability_state: str = "available"
    """Network availability state (from NetworkAvailabilityState)."""
    
    readiness_state: str = "unknown"
    """Network readiness state (from NetworkReadinessState)."""
    
    participation_preference: str = "participate"
    """Network's preferred participation role."""
    
    capabilities: tuple[str, ...] = ()
    """Canonical capability identifiers available from this network."""
    
    requirements: tuple[str, ...] = ()
    """Canonical requirement identifiers needed by this network."""
    
    constraints: tuple[str, ...] = ()
    """Active coordination-facing constraints."""
    
    dependencies: tuple[str, ...] = ()
    """Dependencies on other networks or external state."""
    
    transition_intentions: tuple[str, ...] = ()
    """Declared transition intentions (not executable)."""
    
    semantic_state_references: tuple[str, ...] = ()
    """References to internal semantic state (no runtime objects)."""
    
    confidence: float = 0.5
    """Confidence in projection accuracy (0.0 to 1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about the projection (0.0 to 1.0)."""
    
    semantic_time_ref: Optional[SemanticTimeReference] = None
    """Reference to semantic time for this projection."""
    
    provenance_ref: Optional[str] = None
    """Reference to projection provenance record."""


# =============================================================================
# CANONICAL COORDINATED NETWORK PROJECTIONS
# =============================================================================

@dataclass(frozen=True, slots=True)
class AlertingNetworkProjection(NetworkProjection):
    """
    Alerting Network projection with alert-specific fields.
    
    ALERT-PROJ-INV-001: Projection is immutable
    ALERT-PROJ-LAW-001: Projections do not contain alert-generation logic
    
    COORD-LAW-038: Network projections preserve ownership boundaries
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Alerting-specific references (no runtime objects)
    alert_state_reference: Optional[str] = None
    """Reference to alert state (not the state itself)."""
    
    alert_level: int = 0
    """Alert level (numeric, not executable)."""
    
    interruption_status: str = "none"
    """Interruption status string."""
    
    vigilance_state_reference: Optional[str] = None
    """Reference to vigilance state."""
    
    acknowledgement_requirements: tuple[str, ...] = ()
    """Acknowledgement requirements for alerts."""
    
    alert_transition_intentions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DefaultNetworkProjection(NetworkProjection):
    """
    Default Network projection with default-mode-specific fields.
    
    DEFAULT-PROJ-INV-001: Projection is immutable
    DEFAULT-PROJ-LAW-001: Projections do not activate/deactivate processing
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Default-specific references (no runtime objects)
    default_mode_state_reference: Optional[str] = None
    """Reference to default mode state."""
    
    internally_directed_activity_reference: Optional[str] = None
    """Reference to internally directed activity state."""
    
    mode_transition_status: str = "stable"
    """Mode transition status string."""
    
    interruption_constraints: tuple[str, ...] = ()
    """Interruption constraints."""
    
    continuation_requirements: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ExecutiveNetworkProjection(NetworkProjection):
    """
    Executive Network projection with executive-specific fields.
    
    EXEC-PROJ-INV-001: Projection is immutable
    EXEC-PROJ-LAW-001: Projections do not contain executable directives
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Executive-specific references (no runtime objects)
    executive_state_reference: Optional[str] = None
    """Reference to executive state."""
    
    pending_evaluation_references: tuple[str, ...] = ()
    """References to pending evaluations."""
    
    directive_references: tuple[str, ...] = ()
    """References to directives (not the directives themselves)."""
    
    authorization_requirements: tuple[str, ...] = ()
    """Authorization requirements for decisions."""
    
    unresolved_executive_dependencies: tuple[str, ...] = ()
    """Unresolved dependencies for executive operations."""
    
    executive_transition_intentions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FocusingNetworkProjection(NetworkProjection):
    """
    Focusing Network projection with focus-specific fields.
    
    FOCUS-PROJ-INV-001: Projection is immutable
    FOCUS-PROJ-LAW-001: Projections do not select/maintain focus
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Focusing-specific references (no runtime objects)
    focus_state_reference: Optional[str] = None
    """Reference to focus state."""
    
    focal_target_references: tuple[str, ...] = ()
    """References to focal targets."""
    
    focus_capacity: float = 1.0
    """Current focus capacity (0.0 to 1.0)."""
    
    focus_transition_status: str = "stable"
    """Focus transition status string."""
    
    executive_authorization_requirements: tuple[str, ...] = ()
    """Executive authorization requirements for focus."""
    
    workspace_requirements: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class OrientedNetworkProjection(NetworkProjection):
    """
    Oriented Network projection with orientation-specific fields.
    
    ORIENT-PROJ-INV-001: Projection is immutable
    ORIENT-PROJ-LAW-001: Projections do not select/modify orientation targets
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Oriented-specific references (no runtime objects)
    orientation_state_reference: Optional[str] = None
    """Reference to orientation state."""
    
    target_references: tuple[str, ...] = ()
    """References to orientation targets."""
    
    orientation_transition_status: str = "stable"
    """Orientation transition status string."""
    
    sensorimotor_requirements: tuple[str, ...] = ()
    """Sensorimotor requirements for orientation."""
    
    alerting_requirements: tuple[str, ...] = ()
    """Alerting-related orientation requirements."""
    
    focusing_dependencies: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PredictiveNetworkProjection(NetworkProjection):
    """
    Predictive Network projection with predictive-specific fields.
    
    PRED-PROJ-INV-001: Projection is immutable
    PRED-PROJ-LAW-001: Projections do not contain implementation objects
    
    COORD-LAW-039: Predictive network projections preserve semantic boundaries
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Predictive-specific references (no runtime objects)
    predictive_state_reference: Optional[str] = None
    """Reference to predictive state."""
    
    prediction_landscape_reference: Optional[str] = None
    """Reference to prediction landscape."""
    
    prediction_error_state_reference: Optional[str] = None
    """Reference to prediction error state."""
    
    precision_landscape_reference: Optional[str] = None
    """Reference to precision landscape."""
    
    belief_state_reference: Optional[str] = None
    """Reference to belief state."""
    
    world_model_reference: Optional[str] = None
    """Reference to world model."""
    
    predictive_completion_status: str = "partial"
    """Predictive completion status string."""
    
    missing_observation_requirements: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RewardNetworkProjection(NetworkProjection):
    """
    Reward Network projection with reward-specific fields.
    
    REWARD-PROJ-INV-001: Projection is immutable
    REWARD-PROJ-LAW-001: Projections do not collapse multidimensional reward
    
    COORD-LAW-040: Reward network projections preserve semantic boundaries
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Reward-specific references (no runtime objects)
    reward_evidence_state_reference: Optional[str] = None
    """Reference to reward evidence state."""
    
    reward_landscape_reference: Optional[str] = None
    """Reference to reward landscape."""
    
    temporal_reward_state_reference: Optional[str] = None
    """Reference to temporal reward state."""
    
    multi_domain_reward_state_reference: Optional[str] = None
    """Reference to multi-domain reward state."""
    
    evaluation_status: str = "pending"
    """Evaluation status string."""
    
    required_outcome_references: tuple[str, ...] = ()
    """Required outcome references for reward computation."""
    
    unresolved_reward_conflicts: tuple[str, ...] = ()
    """Unresolved reward conflicts."""
    
    expected_reward_availability: str = "unknown"
    """Expected reward availability status."""
    
    realized_reward_availability: str = "unknown"
    """Realized reward availability status."""


@dataclass(frozen=True, slots=True)
class SalienceNetworkProjection(NetworkProjection):
    """
    Salience Network projection with salience-specific fields.
    
    SALIENCE-PROJ-INV-001: Projection is immutable
    SALIENCE-PROJ-LAW-001: Projections do not rank/select candidates
    
    COORD-LAW-041: Salience network projections preserve semantic boundaries
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Salience-specific references (no runtime objects)
    salience_state_reference: Optional[str] = None
    """Reference to salience state."""
    
    salience_landscape_reference: Optional[str] = None
    """Reference to salience landscape."""
    
    candidate_references: tuple[str, ...] = ()
    """References to salience candidates."""
    
    urgency_summary: str = "normal"
    """Urgency summary string."""
    
    competition_state_reference: Optional[str] = None
    """Reference to competition state."""
    
    unresolved_salience_dependencies: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SensorimotorNetworkProjection(NetworkProjection):
    """
    Sensorimotor Network projection with sensorimotor-specific fields.
    
    SENSORIMOTOR-PROJ-INV-001: Projection is immutable
    SENSORIMOTOR-PROJ-LAW-001: Projections do not contain motor commands
    
    COORD-LAW-042: Sensorimotor network projections preserve semantic boundaries
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Sensorimotor-specific references (no runtime objects)
    sensorimotor_state_reference: Optional[str] = None
    """Reference to sensorimotor state."""
    
    feasibility_state_reference: Optional[str] = None
    """Reference to feasibility state."""
    
    action_preparation_references: tuple[str, ...] = ()
    """References to action preparations."""
    
    outcome_references: tuple[str, ...] = ()
    """References to action outcomes."""
    
    execution_readiness: str = "unknown"
    """Execution readiness status string."""
    
    environmental_constraint_references: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class WorkspaceNetworkProjection(NetworkProjection):
    """
    Workspace Network projection with workspace-specific fields.
    
    WORKSPACE-PROJ-INV-001: Projection is immutable
    WORKSPACE-PROJ-LAW-001: Projections do not admit/evict/reorder content
    
    COORD-LAW-043: Workspace network projections preserve semantic boundaries
    """
    # Base projection fields are inherited from NetworkProjection
    
    # Workspace-specific references (no runtime objects)
    workspace_state_reference: Optional[str] = None
    """Reference to workspace state."""
    
    capacity_state: float = 1.0
    """Current workspace capacity (0.0 to 1.0)."""
    
    admission_state_reference: Optional[str] = None
    """Reference to admission state."""
    
    shared_content_references: tuple[str, ...] = ()
    """References to shared content."""
    
    pending_admission_requirements: tuple[str, ...] = ()
    """Pending admission requirements."""
    
    workspace_transition_status: str = "stable"
    """Workspace transition status string."""


# =============================================================================
# NETWORK CAPABILITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkCapability:
    """
    Immutable capability model for coordination.
    
    CAPABILITY-INV-001: Capability is immutable (deeply frozen)
    CAPABILITY-INV-002: Capability has no runtime references
    
    CAPABILITY-LAW-001: Capabilities are declarative
    CAPABILITY-LAW-002: Capabilities possess stable identity
    """
    capability_identity: str = ""
    """Unique identifier for this capability."""
    
    capability_kind: str = ""
    """Kind of the capability (from CapabilityKind enum)."""
    
    provider_network: NetworkIdentity | None = None
    """Network that provides this capability."""
    
    output_contract_ref: Optional[str] = None
    """Reference to the output contract (not the contract itself)."""
    
    contract_version: str = "1.0.0"
    """Contract version for this capability."""
    
    availability_state: str = "available"
    """Availability state of this capability."""
    
    semantic_scope_ref: Optional[str] = None
    """Reference to semantic scope (not the scope itself)."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this capability."""
    
    provenance_ref: Optional[str] = None
    """Reference to capability provenance record."""


# =============================================================================
# NETWORK REQUIREMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkRequirement:
    """
    Immutable requirement model for coordination.
    
    REQUIREMENT-INV-001: Requirement is immutable (deeply frozen)
    REQUIREMENT-INV-002: Requirement has no runtime references
    
    REQUIREMENT-LAW-001: Requirements remain explicit
    REQUIREMENT-LAW-006: Requirements never invoke providers
    """
    requirement_identity: str = ""
    """Unique identifier for this requirement."""
    
    requesting_network: NetworkIdentity | None = None
    """Network that requires this capability."""
    
    required_capability_ref: Optional[str] = None
    """Reference to the required capability (not the capability itself)."""
    
    provider_constraint_ref: Optional[str] = None
    """Reference to any constraint on the provider."""
    
    requirement_strength: str = "required"
    """Strength of this requirement (from RequirementStrength enum)."""
    
    requirement_scope_ref: Optional[str] = None
    """Reference to requirement scope."""
    
    satisfaction_policy: str = "all_or_nothing"
    """Policy for satisfying this requirement."""
    
    semantic_deadline_ref: Optional[str] = None
    """Reference to semantic deadline (not the deadline itself)."""
    
    provenance_ref: Optional[str] = None
    """Reference to requirement provenance record."""


# =============================================================================
# REQUIREMENT SATISFACTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class RequirementSatisfaction:
    """
    Immutable satisfaction model for requirements.
    
    SATISFACTION-INV-001: Satisfaction is immutable (deeply frozen)
    SATISFACTION-INV-002: Satisfaction has no runtime references
    
    SATISFACTION-LAW-001: Satisfied status remains explicit
    """
    requirement_ref: str = ""
    """Reference to the satisfied requirement."""
    
    satisfying_capability_refs: tuple[str, ...] = ()
    """References to capabilities that satisfy this requirement."""
    
    status: str = "unknown"
    """Satisfaction status (from SatisfactionStatus enum)."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this satisfaction."""
    
    confidence: float = 0.5
    """Confidence in this satisfaction record."""
    
    uncertainty: float = 0.5
    """Uncertainty about this satisfaction record."""
    
    provenance_ref: Optional[str] = None
    """Reference to satisfaction provenance record."""


# =============================================================================
# COORDINATION CONSTRAINT
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationConstraint:
    """
    Immutable constraint model for coordination.
    
    CONSTRAINT-INV-001: Constraint is immutable (deeply frozen)
    CONSTRAINT-INV-002: Constraint has no runtime references
    
    CONSTRAINT-LAW-001: Constraints remain explicit
    CONSTRAINT-LAW-005: Constraints shall never execute policy
    """
    constraint_identity: str = ""
    """Unique identifier for this constraint."""
    
    source_network_ref: Optional[str] = None
    """Reference to the source network (not the network itself)."""
    
    target_scope_ref: Optional[str] = None
    """Reference to the affected scope."""
    
    constraint_kind: str = "unknown"
    """Kind of constraint (from ConstraintKind enum)."""
    
    severity: str = "warning"
    """Severity level of this constraint."""
    
    condition_ref: Optional[str] = None
    """Reference to the condition (not the condition itself)."""
    
    affected_capabilities: tuple[str, ...] = ()
    """Capabilities affected by this constraint."""
    
    affected_transitions: tuple[str, ...] = ()
    """Transitions affected by this constraint."""
    
    compatibility_effect: str = "neutral"
    """Effect on compatibility."""
    
    semantic_time_ref: Optional[SemanticTimeReference] = None
    """Reference to semantic time for this constraint."""
    
    provenance_ref: Optional[str] = None
    """Reference to constraint provenance record."""


# =============================================================================
# COORDINATION DEPENDENCY
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationDependency:
    """
    Immutable dependency model for coordination.
    
    DEPENDENCY-INV-001: Dependency is immutable (deeply frozen)
    DEPENDENCY-INV-002: Dependency has no runtime references
    
    DEPENDENCY-LAW-001: Dependencies remain typed
    DEPENDENCY-LAW-002: Dependencies remain directed
    """
    dependency_identity: str = ""
    """Unique identifier for this dependency."""
    
    dependent_ref: Optional[str] = None
    """Reference to the dependent element."""
    
    prerequisite_ref: Optional[str] = None
    """Reference to the prerequisite element."""
    
    dependency_kind: str = "depends_on"
    """Kind of dependency (from DependencyKind enum)."""
    
    strength: float = 1.0
    """Strength of this dependency (0.0 to 1.0)."""
    
    satisfaction_state: str = "unsatisfied"
    """Current satisfaction state."""
    
    semantic_scope_ref: Optional[str] = None
    """Reference to semantic scope."""
    
    provenance_ref: Optional[str] = None
    """Reference to dependency provenance record."""


# =============================================================================
# TRANSITION INTENTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class TransitionIntention:
    """
    Immutable transition intention model.
    
    TRANSITION-INTENTION-INV-001: Intention is immutable (deeply frozen)
    TRANSITION-INTENTION-INV-002: Intention has no runtime references
    
    TRANSITION-LAW-001: Transition intentions remain declarative
    """
    intention_identity: str = ""
    """Unique identifier for this transition intention."""
    
    source_network_ref: Optional[str] = None
    """Reference to the source network."""
    
    source_state_ref: Optional[str] = None
    """Reference to the source state."""
    
    target_state_ref: Optional[str] = None
    """Reference to the target state."""
    
    transition_kind: str = "unknown"
    """Kind of transition (from TransitionKind enum)."""
    
    prerequisites: tuple[str, ...] = ()
    """Prerequisites for this transition."""
    
    blocking_constraints: tuple[str, ...] = ()
    """Constraints that block this transition."""
    
    required_acknowledgements: tuple[str, ...] = ()
    """Acknowledgements required before transition."""
    
    confidence: float = 0.5
    """Confidence in this intention."""
    
    uncertainty: float = 0.5
    """Uncertainty about this intention."""
    
    semantic_time_ref: Optional[SemanticTimeReference] = None
    """Reference to semantic time for this intention."""
    
    provenance_ref: Optional[str] = None
    """Reference to intention provenance record."""


# =============================================================================
# NETWORK INTERACTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkInteraction:
    """
    Immutable interaction relation model.
    
    INTERACTION-INV-001: Interaction is immutable (deeply frozen)
    INTERACTION-INV-002: Interaction has no runtime references
    
    INTERACTION-LAW-001: Interactions remain typed
    INTERACTION-LAW-002: Interaction direction remains explicit
    """
    interaction_identity: str = ""
    """Unique identifier for this interaction."""
    
    source_ref: Optional[str] = None
    """Reference to the source element."""
    
    target_ref: Optional[str] = None
    """Reference to the target element."""
    
    relation_kind: str = "unknown"
    """Kind of relationship (from InteractionRelation enum)."""
    
    confidence: float = 0.5
    """Confidence in this interaction."""
    
    uncertainty: float = 0.5
    """Uncertainty about this interaction."""
    
    provenance_ref: Optional[str] = None
    """Reference to interaction provenance record."""


# =============================================================================
# NETWORK READINESS
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkReadiness:
    """
    Immutable readiness model for a network.
    
    READINESS-INV-001: Readiness is immutable (deeply frozen)
    READINESS-INV-002: Readiness has no runtime references
    
    READINESS-LAW-001: Readiness remains operation-specific
    READINESS-LAW-007: Readiness shall never invoke networks
    """
    network_identity_ref: str = ""
    """Reference to the network identity."""
    
    readiness_state: str = "unknown"
    """Readiness state (from NetworkReadinessState enum)."""
    
    operation_ref: Optional[str] = None
    """Reference to the target operation."""
    
    satisfied_requirements: tuple[str, ...] = ()
    """Satisfied requirements for this operation."""
    
    unsatisfied_requirements: tuple[str, ...] = ()
    """Unsatisfied requirements."""
    
    active_constraints: tuple[str, ...] = ()
    """Active constraints affecting readiness."""
    
    blocking_dependencies: tuple[str, ...] = ()
    """Dependencies that block participation."""
    
    confidence: float = 0.5
    """Confidence in this readiness record."""
    
    uncertainty: float = 0.5
    """Uncertainty about this readiness record."""
    
    provenance_ref: Optional[str] = None
    """Reference to readiness provenance record."""


# =============================================================================
# NETWORK AVAILABILITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkAvailability:
    """
    Immutable availability model for a network.
    
    AVAILABILITY-INV-001: Availability is immutable (deeply frozen)
    AVAILABILITY-INV-002: Availability has no runtime references
    
    AVAILABILITY-LAW-001: Availability is capability-specific
    AVAILABILITY-LAW-005: Availability shall never probe services
    """
    network_identity_ref: str = ""
    """Reference to the network identity."""
    
    availability_state: str = "unknown"
    """Availability state (from NetworkAvailabilityState enum)."""
    
    available_capabilities: tuple[str, ...] = ()
    """Capabilities that are available."""
    
    unavailable_capabilities: tuple[str, ...] = ()
    """Capabilities that are unavailable."""
    
    degradation_reasons: tuple[str, ...] = ()
    """Reasons for degraded availability."""
    
    confidence: float = 0.5
    """Confidence in this availability record."""
    
    uncertainty: float = 0.5
    """Uncertainty about this availability record."""
    
    provenance_ref: Optional[str] = None
    """Reference to availability provenance record."""


# =============================================================================
# NETWORK PARTICIPATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkParticipation:
    """
    Immutable participation model for a network.
    
    PARTICIPATION-INV-001: Participation is immutable (deeply frozen)
    PARTICIPATION-INV-002: Participation has no runtime references
    
    PARTICIPATION-LAW-001: Participation is cycle-specific
    PARTICIPATION-LAW-005: Participation evaluation remains deterministic
    """
    network_identity_ref: str = ""
    """Reference to the network identity."""
    
    participation_role: str = "unknown"
    """Participation role (from ParticipationRole enum)."""
    
    participation_reason: Optional[str] = None
    """Reason for this participation role."""
    
    provided_capabilities: tuple[str, ...] = ()
    """Capabilities provided by this network."""
    
    requested_capabilities: tuple[str, ...] = ()
    """Capabilities requested from other networks."""
    
    confidence: float = 0.5
    """Confidence in this participation record."""
    
    uncertainty: float = 0.5
    """Uncertainty about this participation record."""
    
    provenance_ref: Optional[str] = None
    """Reference to participation provenance record."""


# =============================================================================
# COORDINATION CONFLICT
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationConflict:
    """
    Immutable conflict model for coordination.
    
    CONFLICT-INV-001: Conflict is immutable (deeply frozen)
    CONFLICT-INV-002: Conflict has no runtime references
    
    CONFLICT-LAW-001: Conflicts shall be classified
    CONFLICT-LAW-003: Conflict ownership remains explicit
    """
    conflict_identity: str = ""
    """Unique identifier for this conflict."""
    
    conflict_kind: str = "unknown"
    """Kind of conflict (from ConflictKind enum)."""
    
    participating_references: tuple[str, ...] = ()
    """References to conflicting parties."""
    
    severity: str = "warning"
    """Severity level of the conflict."""
    
    structural_or_cognitive: str = "unknown"
    """Whether this is structural or cognitive."""
    
    blocking_status: str = "non_blocking"
    """Whether this conflict blocks coordination."""
    
    resolvability: str = "external_authority"
    """Which authority should resolve this."""
    
    owning_resolution_network_ref: Optional[str] = None
    """Reference to the network that owns resolution."""
    
    confidence: float = 0.5
    """Confidence in this conflict record."""
    
    uncertainty: float = 0.5
    """Uncertainty about this conflict record."""
    
    provenance_ref: Optional[str] = None
    """Reference to conflict provenance record."""


# =============================================================================
# COORDINATION COMPATIBILITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationCompatibility:
    """
    Immutable compatibility model for coordination.
    
    COMPATIBILITY-INV-001: Compatibility is immutable (deeply frozen)
    COMPATIBILITY-INV-002: Compatibility has no runtime references
    
    COMPATIBILITY-LAW-001: Compatibility remains explicit
    COMPATIBILITY-LAW-007: Compatibility shall never imply semantic agreement
    """
    compatibility_status: str = "unknown"
    """Compatibility status (from CompatibilityStatus enum)."""
    
    compatible_participants: tuple[str, ...] = ()
    """Participants that are compatible."""
    
    incompatible_participants: tuple[str, ...] = ()
    """Participants that are incompatible."""
    
    contract_mismatches: tuple[str, ...] = ()
    """Contract version mismatches found."""
    
    revision_mismatches: tuple[str, ...] = ()
    """Semantic revision mismatches found."""
    
    unsatisfied_requirements: tuple[str, ...] = ()
    """Requirements that could not be satisfied."""
    
    active_conflicts: tuple[str, ...] = ()
    """Active conflicts affecting compatibility."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this compatibility assessment."""
    
    confidence: float = 0.5
    """Confidence in this compatibility record."""
    
    uncertainty: float = 0.5
    """Uncertainty about this compatibility record."""
    
    provenance_ref: Optional[str] = None
    """Reference to compatibility provenance record."""


# =============================================================================
# COORDINATION POLICY
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationPolicy:
    """
    Immutable policy contract for coordination.
    
    POLICY-INV-001: Policy is immutable (deeply frozen)
    POLICY-INV-002: Policy has no runtime references
    
    POLICY-LAW-001: Policy contains data and declarative strategy only
    """
    policy_identity: str = ""
    """Unique identifier for this policy."""
    
    core_membership_required: bool = True
    """Whether core membership is required."""
    
    optional_member_handling: str = "allow"
    """How to handle optional members."""
    
    projection_freshness_threshold: int = 0
    """Maximum allowed projection age (0 means no limit)."""
    
    requirement_satisfaction_policy: str = "all_required"
    """Policy for satisfying requirements."""
    
    cycle_classification_policy: str = "strict"
    """Policy for cycle classification."""
    
    compatibility_checking_mode: str = "deep"
    """Mode for compatibility checking."""
    
    structural_conflict_handling: str = "report_only"
    """How to handle structural conflicts."""
    
    degraded_participation_policy: str = "allow"
    """Policy for degraded participation."""
    
    plan_construction_order: str = "topological"
    """Order for plan construction."""
    
    deterministic_seeding: bool = True
    """Whether deterministic ordering is enforced."""
    
    finding_severity_threshold: str = "warning"
    """Minimum severity to record as a finding."""
    
    validation_strictness: str = "high"
    """Level of validation strictness."""
    
    provenance_ref: Optional[str] = None
    """Reference to policy provenance record."""


# =============================================================================
# COORDINATION PLAN
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationPlan:
    """
    Immutable plan model for coordination.
    
    PLAN-INV-001: Plan is immutable (deeply frozen)
    PLAN-INV-002: Plan has no runtime references
    
    PLAN-LAW-001: Plans remain declarative
    PLAN-LAW-007: Plans shall never contain executable tasks
    """
    plan_identity: str = ""
    """Unique identifier for this plan."""
    
    cycle_ref: Optional[str] = None
    """Reference to the target coordination cycle."""
    
    participants: tuple[NetworkIdentity, ...] = ()
    """Participating networks."""
    
    required_capabilities: tuple[str, ...] = ()
    """Required capabilities for this plan."""
    
    satisfied_requirements: tuple[str, ...] = ()
    """Satisfied requirements."""
    
    unsatisfied_requirements: tuple[str, ...] = ()
    """Unsatisfied requirements."""
    
    dependency_layers: tuple[tuple[str, ...], ...] = ()
    """Dependency layers (ordered groups)."""
    
    synchronization_barriers: tuple[str, ...] = ()
    """Synchronization barriers in the plan."""
    
    transition_prerequisites: tuple[str, ...] = ()
    """Prerequisites for transitions."""
    
    blocked_operations: tuple[str, ...] = ()
    """Operations that are blocked."""
    
    deferred_operations: tuple[str, ...] = ()
    """Operations that are deferred."""
    
    fallback_conditions: tuple[str, ...] = ()
    """Fallback conditions if plan fails."""
    
    completion_conditions: tuple[str, ...] = ()
    """Conditions for successful completion."""
    
    findings: tuple[str, ...] = ()
    """Findings from plan construction."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this plan."""
    
    provenance_ref: Optional[str] = None
    """Reference to plan provenance record."""


# =============================================================================
# COORDINATION CYCLE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationCycle:
    """
    Immutable cycle model for coordination.
    
    CYCLE-INV-001: Cycle is immutable (deeply frozen)
    CYCLE-INV-002: Cycle has no runtime references
    
    CYCLE-LAW-001: Every CoordinationCycle possesses stable identity
    CYCLE-LAW-006: Cycles remain immutable
    """
    cycle_identity: CoordinationCycleIdentity = field(default_factory=CoordinationCycleIdentity)
    """Identity of this coordination cycle."""
    
    request_references: tuple[str, ...] = ()
    """References to requests in this cycle."""
    
    membership_ref: Optional[str] = None
    """Reference to the active membership configuration."""
    
    participants: tuple[NetworkIdentity, ...] = ()
    """Participating networks in this cycle."""
    
    projections: tuple[NetworkProjection, ...] = ()
    """Projections provided by participants."""
    
    requirement_satisfactions: tuple[RequirementSatisfaction, ...] = ()
    """Requirement satisfactions in this cycle."""
    
    readiness_states: tuple[NetworkReadiness, ...] = ()
    """Readiness states of participants."""
    
    availability_states: tuple[NetworkAvailability, ...] = ()
    """Availability states of participants."""
    
    compatibility_ref: Optional[str] = None
    """Reference to compatibility assessment."""
    
    dependency_graph_ref: Optional[str] = None
    """Reference to the dependency graph."""
    
    constraint_graph_ref: Optional[str] = None
    """Reference to the constraint graph."""
    
    transition_graph_ref: Optional[str] = None
    """Reference to the transition graph."""
    
    interaction_graph_ref: Optional[str] = None
    """Reference to the interaction graph."""
    
    conflicts: tuple[CoordinationConflict, ...] = ()
    """Conflicts detected in this cycle."""
    
    plan_reference: Optional[str] = None
    """Reference to the coordination plan."""
    
    semantic_time_ref: Optional[SemanticTimeReference] = None
    """Reference to semantic time for this cycle."""
    
    provenance_ref: Optional[str] = None
    """Reference to cycle provenance record."""


# =============================================================================
# COORDINATION STATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationState:
    """
    Immutable aggregate state model for coordination.
    
    STATE-INV-001: State is immutable (deeply frozen)
    STATE-INV-002: State has no runtime references
    
    STATE-LAW-001: Exactly one CoordinationState exists per CoordinationCycle
    STATE-LAW-002: CoordinationState remains immutable
    """
    state_identity: CoordinationStateIdentity = field(default_factory=CoordinationStateIdentity)
    """Identity of this coordination state."""
    
    cycle_ref: Optional[str] = None
    """Reference to the source coordination cycle."""
    
    plan_ref: Optional[str] = None
    """Reference to the coordination plan."""
    
    membership_ref: Optional[str] = None
    """Reference to the active membership configuration."""
    
    projections: tuple[NetworkProjection, ...] = ()
    """All projections in this state."""
    
    participation: tuple[NetworkParticipation, ...] = ()
    """Participation records for all participants."""
    
    readiness: tuple[NetworkReadiness, ...] = ()
    """Readiness states for all participants."""
    
    availability: tuple[NetworkAvailability, ...] = ()
    """Availability states for all participants."""
    
    capability_index: tuple[str, ...] = ()
    """Indexed capabilities across networks."""
    
    requirement_satisfactions: tuple[RequirementSatisfaction, ...] = ()
    """Requirement satisfactions."""
    
    dependency_graph_ref: Optional[str] = None
    """Reference to the dependency graph."""
    
    constraint_graph_ref: Optional[str] = None
    """Reference to the constraint graph."""
    
    transition_graph_ref: Optional[str] = None
    """Reference to the transition graph."""
    
    interaction_graph_ref: Optional[str] = None
    """Reference to the interaction graph."""
    
    compatibility_ref: Optional[str] = None
    """Reference to compatibility assessment."""
    
    conflicts: tuple[CoordinationConflict, ...] = ()
    """Detected conflicts."""
    
    correlations: tuple[str, ...] = ()
    """Correlations between requests and responses."""
    
    confidence: CoordinationConfidence | None = None
    """Coordination confidence record."""
    
    uncertainty: CoordinationUncertainty | None = None
    """Coordination uncertainty record."""
    
    findings: tuple[CoordinationFinding, ...] = ()
    """Findings from coordination."""
    
    limitations: tuple[CoordinationLimitation, ...] = ()
    """Limitations on this state."""
    
    trace: tuple[str, ...] = ()
    """Trace of coordination events."""
    
    semantic_time_ref: Optional[SemanticTimeReference] = None
    """Reference to semantic time for this state."""
    
    provenance_ref: Optional[str] = None
    """Reference to state provenance record."""


# =============================================================================
# COORDINATION CONFIDENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationConfidence:
    """
    Immutable confidence model for coordination.
    
    CONFIDENCE-INV-001: Confidence is immutable (deeply frozen)
    CONFIDENCE-INV-002: Confidence has no runtime references
    """
    projection_completeness_confidence: float = 0.5
    """Confidence in projection completeness."""
    
    projection_freshness_confidence: float = 0.5
    """Confidence in projection freshness."""
    
    membership_confidence: float = 0.5
    """Confidence in membership configuration."""
    
    requirement_correlation_confidence: float = 0.5
    """Confidence in requirement correlations."""
    
    graph_construction_confidence: float = 0.5
    """Confidence in graph construction."""
    
    compatibility_confidence: float = 0.5
    """Confidence in compatibility assessment."""
    
    provenance_confidence: float = 0.5
    """Confidence in provenance tracking."""
    
    @classmethod
    def from_parts(
        cls,
        projection_completeness: float = 0.5,
        projection_freshness: float = 0.5,
        membership: float = 0.5,
        requirement_correlation: float = 0.5,
        graph_construction: float = 0.5,
        compatibility: float = 0.5,
        provenance: float = 0.5,
    ) -> CoordinationConfidence:
        """Create a confidence record from individual components."""
        return cls(
            projection_completeness_confidence=projection_completeness,
            projection_freshness_confidence=projection_freshness,
            membership_confidence=membership,
            requirement_correlation_confidence=requirement_correlation,
            graph_construction_confidence=graph_construction,
            compatibility_confidence=compatibility,
            provenance_confidence=provenance,
        )


# =============================================================================
# COORDINATION UNCERTAINTY
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationUncertainty:
    """
    Immutable uncertainty model for coordination.
    
    UNCERTAINTY-INV-001: Uncertainty is immutable (deeply frozen)
    UNCERTAINTY-INV-002: Uncertainty has no runtime references
    
    UNCERTAINTY-LAW-001: Uncertainty shall not be computed as 1 - confidence
    """
    projection_uncertainty: float = 0.5
    """Uncertainty about projections."""
    
    membership_uncertainty: float = 0.5
    """Uncertainty about membership configuration."""
    
    readiness_uncertainty: float = 0.5
    """Uncertainty about readiness states."""
    
    availability_uncertainty: float = 0.5
    """Uncertainty about availability states."""
    
    dependency_uncertainty: float = 0.5
    """Uncertainty about dependencies."""
    
    constraint_uncertainty: float = 0.5
    """Uncertainty about constraints."""
    
    transition_uncertainty: float = 0.5
    """Uncertainty about transitions."""
    
    correlation_uncertainty: float = 0.5
    """Uncertainty about correlations."""
    
    compatibility_uncertainty: float = 0.5
    """Uncertainty about compatibility."""
    
    @classmethod
    def from_parts(
        cls,
        projection: float = 0.5,
        membership: float = 0.5,
        readiness: float = 0.5,
        availability: float = 0.5,
        dependency: float = 0.5,
        constraint: float = 0.5,
        transition: float = 0.5,
        correlation: float = 0.5,
        compatibility: float = 0.5,
    ) -> CoordinationUncertainty:
        """Create an uncertainty record from individual components."""
        return cls(
            projection_uncertainty=projection,
            membership_uncertainty=membership,
            readiness_uncertainty=readiness,
            availability_uncertainty=availability,
            dependency_uncertainty=dependency,
            constraint_uncertainty=constraint,
            transition_uncertainty=transition,
            correlation_uncertainty=correlation,
            compatibility_uncertainty=compatibility,
        )


# =============================================================================
# COORDINATION RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationResult:
    """
    Immutable result model for coordination.
    
    RESULT-INV-001: Result is immutable (deeply frozen)
    RESULT-INV-002: Result has no runtime references
    
    RESULT-LAW-001: Results remain descriptive
    """
    request_identity_ref: Optional[str] = None
    """Reference to the source coordination request."""
    
    cycle_ref: Optional[str] = None
    """Reference to the coordination cycle."""
    
    plan_ref: Optional[str] = None
    """Reference to the coordination plan."""
    
    state_ref: Optional[str] = None
    """Reference to the coordination state."""
    
    findings: tuple[CoordinationFinding, ...] = ()
    """Findings from coordination."""
    
    limitations: tuple[CoordinationLimitation, ...] = ()
    """Limitations on this result."""
    
    trace: tuple[str, ...] = ()
    """Trace of coordination events."""
    
    status: str = "unknown"
    """Overall coordination status."""
    
    provenance_ref: Optional[str] = None
    """Reference to result provenance record."""


# =============================================================================
# COORDINATION FINDING
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationFinding:
    """
    Immutable finding model for coordination.
    
    FINDING-INV-001: Finding is immutable (deeply frozen)
    FINDING-INV-002: Finding has no runtime references
    
    FINDING-LAW-001: Findings shall be typed
    """
    finding_code: str = ""
    """Code for this finding type."""
    
    severity: str = "warning"
    """Severity level of this finding."""
    
    subject_refs: tuple[str, ...] = ()
    """References to affected subjects."""
    
    message_params: tuple[str, ...] = ()
    """Parameters for the finding message."""
    
    blocking_status: str = "non_blocking"
    """Whether this finding blocks coordination."""
    
    owning_authority_ref: Optional[str] = None
    """Reference to the authority that owns resolution."""
    
    provenance_ref: Optional[str] = None
    """Reference to finding provenance record."""


# =============================================================================
# COORDINATION LIMITATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationLimitation:
    """
    Immutable limitation model for coordination.
    
    LIMITATION-INV-001: Limitation is immutable (deeply frozen)
    LIMITATION-INV-002: Limitation has no runtime references
    
    LIMITATION-LAW-001: Limitations remain explicit
    """
    limitation_code: str = ""
    """Code for this limitation type."""
    
    affected_scope_ref: Optional[str] = None
    """Reference to affected scope."""
    
    consequence: str = "unknown"
    """Consequence of this limitation."""
    
    recoverability: str = "unknown"
    """Whether this can be recovered."""
    
    related_findings: tuple[str, ...] = ()
    """Related findings."""
    
    provenance_ref: Optional[str] = None
    """Reference to limitation provenance record."""


# =============================================================================
# COORDINATION TRACE EVENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationTraceEvent:
    """
    Immutable trace event model for coordination.
    
    TRACE-INV-001: Trace is immutable (deeply frozen)
    TRACE-INV-002: Trace has no runtime references
    
    TRACE-LAW-001: Trace events shall be structural
    """
    event_code: str = ""
    """Code for this trace event."""
    
    stage: str = "unknown"
    """Stage of the coordination pipeline."""
    
    subject_refs: tuple[str, ...] = ()
    """References to affected subjects."""
    
    input_refs: tuple[str, ...] = ()
    """Input references for this event."""
    
    output_refs: tuple[str, ...] = ()
    """Output references from this event."""
    
    finding_refs: tuple[str, ...] = ()
    """Related findings."""
    
    policy_ref: Optional[str] = None
    """Reference to active policy."""
    
    semantic_time_ref: Optional[SemanticTimeReference] = None
    """Reference to semantic time for this event."""
    
    provenance_ref: Optional[str] = None
    """Reference to trace provenance record."""


# =============================================================================
# CANONICAL NETWORK KIND TO PROJECTION MAPPING
# =============================================================================

def get_projection_for_kind(kind_name: str) -> type[NetworkProjection]:
    """
    Get the projection class for a given network kind name.
    
    Args:
        kind_name: The canonical network kind name
        
    Returns:
        The corresponding NetworkProjection subclass
        
    Raises:
        ValueError: If the kind name is not recognized
    """
    mapping = {
        "ALERTING": AlertingNetworkProjection,
        "DEFAULT": DefaultNetworkProjection,
        "EXECUTIVE": ExecutiveNetworkProjection,
        "FOCUSING": FocusingNetworkProjection,
        "ORIENTED": OrientedNetworkProjection,
        "PREDICTIVE": PredictiveNetworkProjection,
        "REWARD": RewardNetworkProjection,
        "SALIENCE": SalienceNetworkProjection,
        "SENSORIMOTOR": SensorimotorNetworkProjection,
        "WORKSPACE": WorkspaceNetworkProjection,
    }
    
    try:
        return mapping[kind_name]
    except KeyError:
        raise ValueError(f"Unknown network kind for projection: {kind_name}")
