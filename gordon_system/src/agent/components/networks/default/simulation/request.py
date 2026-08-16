# Simulation Request Models
# =========================

"""
Immutable models for simulation and counterfactual requests.

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

SimulationRequestId = str
"""Unique identifier for a simulation request."""

CounterfactualRequestId = str
"""Unique identifier for a counterfactual request."""

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
# SIMULATION PURPOSE - Canonical purpose representation (imported from enums)
# =============================================================================

class SimulationPurposeKind:
    FUTURE_EXPLORATION = "future_exploration"
    ACTION_CONSEQUENCE_EXPLORATION = "action_consequence_exploration"
    PLAN_EVALUATION = "plan_evaluation"
    RISK_EXPLORATION = "risk_exploration"
    OPPORTUNITY_EXPLORATION = "opportunity_exploration"
    HYPOTHESIS_EXPLORATION = "hypothesis_exploration"
    STATE_TRAJECTORY_EXPLORATION = "state_trajectory_exploration"
    DECISION_SUPPORT = "decision_support"
    FAILURE_ALTERNATIVE_ANALYSIS = "failure_alternative_analysis"
    SUCCESS_ALTERNATIVE_ANALYSIS = "success_alternative_analysis"
    COUNTERFACTUAL_REVIEW = "counterfactual_review"
    CAUSAL_HYPOTHESIS_TEST = "causal_hypothesis_test"
    NARRATIVE_POSSIBILITY = "narrative_possibility"
    IDENTITY_FUTURE_PROJECTION = "identity_future_projection"
    CREATIVE_SCENARIO_GENERATION = "creative_scenario_generation"
    RESOURCE_OUTCOME_EXPLORATION = "resource_outcome_exploration"
    GENERAL_SIMULATION = "general_simulation"


# =============================================================================
# SIMULATION SUBJECT - What is being simulated
# =============================================================================

class SimulationSubjectKind:
    CURRENT_STATE = "current_state"
    ACTION = "action"
    DECISION = "decision"
    PLAN = "plan"
    OBJECTIVE = "objective"
    TASK = "task"
    EXECUTION_THREAD = "execution_thread"
    EXECUTION_CYCLE = "execution_cycle"
    INTERNAL_EPISODE = "internal_episode"
    INTERNAL_THOUGHT = "internal_thought"
    SYSTEM_STATE = "system_state"
    ENVIRONMENT_STATE = "environment_state"
    MEMORY = "memory"
    IDENTITY_STATE = "identity_state"
    NARRATIVE = "narrative"
    RELATIONSHIP = "relationship"
    RESOURCE_STATE = "resource_state"
    FAILURE = "failure"
    SUCCESS = "success"
    HYPOTHESIS = "hypothesis"
    GENERAL_SITUATION = "general_situation"


# =============================================================================
# SIMULATION SCOPE - Bounded constraints on simulation
# =============================================================================

@dataclass(frozen=True, slots=True)
class SimulationScope:
    """
    Immutable scope constraints for a simulation episode.
    
    Scope prevents one simulation from becoming unbounded by imposing
    explicit limits on resources and evidence.
    """
    
    # Scenario limits
    maximum_scenario_count: int = 10
    """Maximum number of scenarios allowed."""
    
    maximum_trajectory_depth: int = 20
    """Maximum depth of any trajectory."""
    
    maximum_branch_factor: int = 3
    """Maximum branches from any single scenario state."""
    
    # Event and state limits
    maximum_event_count: int = 100
    """Maximum total events across all scenarios."""
    
    maximum_state_count: int = 200
    """Maximum total simulated states across all scenarios."""
    
    # Assumption and intervention limits
    maximum_assumptions: int = 25
    """Maximum assumptions in a simulation."""
    
    maximum_interventions: int = 25
    """Maximum interventions in a simulation."""
    
    maximum_alternatives: int = 50
    """Maximum alternatives considered."""
    
    # Capability request limits
    maximum_capability_requests: int = 10
    """Maximum capability requests allowed."""
    
    # Result size limits
    maximum_result_size_bytes: int = 1048576  # 1 MB
    """Maximum total result size in bytes."""
    
    maximum_context_references: int = 20
    """Maximum context references allowed."""
    
    maximum_child_episodes: int = 5
    """Maximum child episodes derived from this simulation."""
    
    # Recursion limits
    maximum_recursion_depth: int = 3
    """Maximum recursive simulation depth."""
    
    temporal_horizon_seconds: float = 86400.0  # 24 hours
    """Maximum temporal horizon in seconds."""
    
    semantic_horizon: int = 10
    """Maximum semantic steps in trajectory."""
    
    # Fidelity constraints
    permitted_state_dimensions: Tuple[str, ...] = field(default_factory=tuple)
    """Permitted state dimensions (empty = all)."""
    
    excluded_state_dimensions: Tuple[str, ...] = field(default_factory=tuple)
    """Excluded state dimensions."""
    
    required_fidelity: float = 0.5
    """Required minimum fidelity (0.0 to 1.0)."""
    
    confidence_threshold: float = 0.5
    """Minimum confidence threshold for products."""
    
    require_factuality_labels: bool = True
    """If true, all products must have factuality labels."""
    
    require_model_limitations: bool = True
    """If true, all limitations must be explicitly recorded."""
    
    @classmethod
    def surface_level(cls) -> SimulationScope:
        """Create a scope for shallow simulation."""
        return cls(
            maximum_scenario_count=3,
            maximum_trajectory_depth=5,
            maximum_branch_factor=2,
            maximum_event_count=20,
            maximum_state_count=40,
            maximum_assumptions=10,
            maximum_interventions=10,
            maximum_alternatives=15,
            temporal_horizon_seconds=3600.0,  # 1 hour
        )
    
    @classmethod
    def standard_level(cls) -> SimulationScope:
        """Create a scope for normal simulation."""
        return cls(
            maximum_scenario_count=10,
            maximum_trajectory_depth=20,
            maximum_branch_factor=3,
            maximum_event_count=100,
            maximum_state_count=200,
            maximum_assumptions=25,
            maximum_interventions=25,
            maximum_alternatives=50,
            temporal_horizon_seconds=86400.0,  # 24 hours
        )
    
    @classmethod
    def deep_level(cls) -> SimulationScope:
        """Create a scope for thorough simulation."""
        return cls(
            maximum_scenario_count=25,
            maximum_trajectory_depth=50,
            maximum_branch_factor=5,
            maximum_event_count=500,
            maximum_state_count=1000,
            maximum_assumptions=50,
            maximum_interventions=50,
            maximum_alternatives=100,
            maximum_recursion_depth=5,
            temporal_horizon_seconds=604800.0,  # 7 days
        )


# =============================================================================
# SIMULATION BASELINE - Starting point for simulation
# =============================================================================

@dataclass(frozen=True, slots=True)
class SimulationBaseline:
    """
    Immutable baseline representing the starting state or trajectory.
    
    The baseline is never mutated during simulation; alternatives are
    constructed relative to it.
    """
    
    kind: str  # SimulationBaselineKind.*
    """The canonical baseline kind."""
    
    source_id: Optional[str] = None
    """ID reference to the source entity (if applicable)."""
    
    summary: str = ""
    """Brief description of the baseline state."""
    
    source_revision: int = 1
    """Source system revision number at baseline time."""
    
    confidence: float = 0.5
    """Confidence in the baseline representation (0.0 to 1.0)."""
    
    completeness: str = "partial"
    """Completeness status ('complete', 'sufficient', 'partial')."""
    
    temporal_position_utc: Optional[datetime] = None
    """Temporal position of the baseline."""
    
    provenance: str = "canonical"
    """Provenance reference for the baseline."""
    
    @classmethod
    def current_state(
        cls,
        state_id: str,
        confidence: float = 0.8,
        completeness: str = "sufficient",
    ) -> SimulationBaseline:
        """Create a current-state baseline."""
        return cls(
            kind="current_state_projection",
            source_id=state_id,
            summary="Current observed state",
            confidence=confidence,
            completeness=completeness,
        )
    
    @classmethod
    def expected_outcome(cls, outcome_id: str) -> SimulationBaseline:
        """Create an expected-outcome baseline."""
        return cls(
            kind="expected_outcome",
            source_id=outcome_id,
            summary="Expected outcome based on plans",
        )


# =============================================================================
# SIMULATION ASSUMPTION - Explicit assumptions in simulation
# =============================================================================

@dataclass(frozen=True, slots=True)
class SimulationAssumption:
    """
    Immutable representation of an explicit assumption.
    
    Assumptions define what remains fixed versus variable in a simulation.
    """
    
    assumption_id: str
    """Unique identifier for this assumption."""
    
    proposition: str
    """The assumed proposition (human-readable)."""
    
    source: Optional[str] = None
    """Source of the assumption (reference to context or memory)."""
    
    confidence: float = 0.5
    """Confidence in this assumption (0.0 to 1.0)."""
    
    kind: str = "fixed"
    """Assumption kind (SimulationAssumptionKind.*)."""
    
    mutability: str = "immutable"
    """Mutability constraint ('immutable', 'conditional', 'variable')."""
    
    scenario_applicabilities: Tuple[str, ...] = field(default_factory=tuple)
    """Scenario IDs where this assumption applies."""
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this assumption."""
    
    contradicting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence contradicting this assumption."""
    
    provenance: str = "canonical"
    """Provenance reference for the assumption."""
    
    @classmethod
    def create(
        cls,
        proposition: str,
        kind: str = "fixed",
        confidence: float = 0.5,
    ) -> SimulationAssumption:
        """Create a new assumption with auto-generated ID."""
        return cls(
            assumption_id=f"assumption_{proposition.replace(' ', '_')[:32]}",
            proposition=proposition,
            kind=kind,
            confidence=confidence,
        )


# =============================================================================
# SIMULATION INTERVENTION - Hypothetical modifications to baseline
# =============================================================================

@dataclass(frozen=True, slots=True)
class SimulationIntervention:
    """
    Immutable representation of a hypothetical modification.
    
    An intervention represents an explicit change to the baseline that is
    being explored. It is NEVER applied to actual state.
    """
    
    intervention_id: str
    """Unique identifier for this intervention."""
    
    kind: str  # SimulationInterventionKind.*
    """The canonical intervention kind."""
    
    target_id: Optional[str] = None
    """ID of the target entity (if applicable)."""
    
    prior_value_or_condition: str = ""
    """Prior state before the intervention."""
    
    hypothetical_value_or_condition: str = ""
    """Hypothetical state after the intervention."""
    
    effective_point_utc: Optional[datetime] = None
    """When in the simulation timeline the intervention takes effect."""
    
    confidence: float = 0.5
    """Confidence in this intervention's validity (0.0 to 1.0)."""
    
    provenance: str = "canonical"
    """Provenance reference for the intervention."""
    
    reversibility: str = "unknown"
    """Reversibility assessment ('reversible', 'irreversible', 'unknown')."""
    
    compatibility_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints that must hold after this intervention."""
    
    @classmethod
    def create_action_change(
        cls,
        action_id: str,
        prior_action: str,
        hypothetical_action: str,
    ) -> SimulationIntervention:
        """Create an action-change intervention."""
        return cls(
            intervention_id=f"intervention_{action_id}",
            kind="action_changed",
            target_id=action_id,
            prior_value_or_condition=prior_action,
            hypothetical_value_or_condition=hypothetical_action,
        )
    
    @classmethod
    def create_event_removed(cls, event_id: str) -> SimulationIntervention:
        """Create an event-removal intervention."""
        return cls(
            intervention_id=f"intervention_{event_id}",
            kind="event_removed",
            target_id=event_id,
            prior_value_or_condition="occurred",
            hypothetical_value_or_condition="prevented",
        )


# =============================================================================
# SIMULATION CONSTRAINTS - Bounded constraints for simulation
# =============================================================================

@dataclass(frozen=True, slots=True)
class SimulationConstraints:
    """
    Immutable set of constraints that must hold during simulation.
    
    Invalid or contradictory constraints are reported but do not prevent
    simulation if the simulation model allows it.
    """
    
    invariants: Tuple[str, ...] = field(default_factory=tuple)
    """Invariants that must hold throughout simulation."""
    
    prohibited_states: Tuple[str, ...] = field(default_factory=tuple)
    """States that must never occur."""
    
    permitted_actions: Tuple[str, ...] = field(default_factory=tuple)
    """Actions that are allowed (empty = all allowed)."""
    
    resource_bounds: Tuple[str, ...] = field(default_factory=tuple)
    """Resource bounds (e.g., 'memory < 1GB', 'time < 30s')."""
    
    policy_bounds: Tuple[str, ...] = field(default_factory=tuple)
    """Policy constraints that must be satisfied."""
    
    temporal_bounds: Tuple[str, ...] = field(default_factory=tuple)
    """Temporal constraints (e.g., 'no time travel', 'forward_only')."""
    
    causal_restrictions: Tuple[str, ...] = field(default_factory=tuple)
    """Causal restrictions (e.g., 'cause_before_effect')."""
    
    identity_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Identity-related constraints."""
    
    safety_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Safety-critical constraints."""
    
    environment_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Environmental constraints."""
    
    model_fidelity_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Model fidelity requirements for validity."""
    
    @classmethod
    def permissive(cls) -> SimulationConstraints:
        """Create a permissive constraint set (minimum constraints)."""
        return cls()
    
    @classmethod
    def standard(cls) -> SimulationConstraints:
        """Create a standard constraint set."""
        return cls(
            temporal_bounds=("forward_only",),
            causal_restrictions=("cause_before_effect",),
        )
    
    @classmethod
    def strict(cls) -> SimulationConstraints:
        """Create a strict constraint set."""
        return cls(
            invariants=("conservation_of_mass", "causality_preserved"),
            prohibited_states=("inconsistent_state",),
            temporal_bounds=("forward_only", "no_time_travel"),
            causal_restrictions=(
                "cause_before_effect",
                "local_causality",
            ),
        )


# =============================================================================
# SIMULATION REQUEST - Main request type
# =============================================================================

@dataclass(frozen=True, slots=True)
class SimulationRequest:
    """
    Immutable request to perform one bounded simulation episode.
    
    The request is semantic - it contains references to data but does not
    contain live objects or runtime handles. It defines WHAT should be
    simulated, not HOW the simulation should be implemented.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • purpose: What kind of simulation is being requested
        • subject: What is being simulated
        • scope: Bounded constraints on the simulation
        • context_id: Reference to InternalContext revision
        • baseline: Starting state or trajectory
        • assumptions: Explicit assumptions about the situation
        • interventions: Hypothetical modifications to explore
        • constraints: Constraints that must hold
        
    BOUNDEDNESS:
        Every limit is explicit. Overflow must be recorded.
    
    NOT RESPONSIBLE FOR:
        - Executing simulation algorithms
        - Allocating runtime resources
        - Scheduling execution
        - Storing persistent results
    """
    
    # Identity and metadata
    request_id: SimulationRequestId
    """Unique identifier for this request."""
    
    purpose: str  # SimulationPurposeKind.*
    """What kind of simulation is being requested."""
    
    subject: str  # SimulationSubjectKind.*
    """What is being simulated."""
    
    scope: SimulationScope
    """Bounded constraints on the simulation."""
    
    # Context binding
    context_id: InternalContextId
    """Reference to InternalContext revision."""
    
    context_revision: int = 1
    """Context version at request time."""
    
    baseline: SimulationBaseline
    """Starting state or trajectory for simulation."""
    
    assumptions: Tuple[SimulationAssumption, ...] = field(default_factory=tuple)
    """Explicit assumptions about the situation."""
    
    interventions: Tuple[SimulationIntervention, ...] = field(default_factory=tuple)
    """Hypothetical modifications to explore."""
    
    constraints: SimulationConstraints
    """Constraints that must hold during simulation."""
    
    # Request parameters
    requested_scenario_count: int = 3
    """Number of scenarios requested."""
    
    requested_horizon_seconds: float = 86400.0  # 24 hours
    """Temporal horizon in seconds."""
    
    expected_products: FrozenSet[str] = field(default_factory=frozenset)
    """Product kinds expected from this simulation."""
    
    # Origin tracking
    originating_episode_id: Optional[InternalEpisodeId] = None
    """ID of parent episode if derived from one."""
    
    originating_thought_ids: Tuple[InternalThoughtId, ...] = field(
        default_factory=tuple
    )
    """Thought IDs that triggered this request."""
    
    requested_by: str = "DEFAULT_NETWORK"
    """Who/what made the request (SimulationRequester.*)."""
    
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
        purpose: str,
        subject: str,
        context_id: str,
        baseline: SimulationBaseline,
        scope: Optional[SimulationScope] = None,
        assumptions: Tuple[SimulationAssumption, ...] = (),
        interventions: Tuple[SimulationIntervention, ...] = (),
        constraints: Optional[SimulationConstraints] = None,
        request_id: Optional[str] = None,
    ) -> SimulationRequest:
        """
        Create a new simulation request with default metadata.
        
        Args:
            purpose: The purpose of this simulation
            subject: What is being simulated
            context_id: Reference to InternalContext revision
            baseline: Starting state or trajectory
            scope: Optional scope (default = standard_level())
            assumptions: Assumptions about the situation
            interventions: Hypothetical modifications to explore
            constraints: Constraints that must hold
            request_id: Optional explicit ID (auto-generated if None)
            
        Returns:
            New SimulationRequest instance with valid metadata
        """
        return cls(
            request_id=request_id or f"simulation_request_{id(baseline)}",
            purpose=purpose,
            subject=subject,
            context_id=context_id,
            baseline=baseline,
            scope=scope or SimulationScope.standard_level(),
            assumptions=assumptions,
            interventions=interventions,
            constraints=constraints or SimulationConstraints.permissive(),
        )
    
    def can_produce_product(self, product_kind: str) -> bool:
        """Check if this request is allowed to produce a given product kind."""
        return not self.expected_products or product_kind in self.expected_products
    
    def exceeds_scope_limits(
        self,
        scenario_count: int,
        event_count: int,
        state_count: int,
    ) -> Tuple[str, ...]:
        """
        Check if counts exceed scope limits.
        
        Args:
            scenario_count: Number of scenarios generated
            event_count: Number of events in all scenarios
            state_count: Number of states in all scenarios
            
        Returns:
            List of exceeded limits (empty if within bounds)
        """
        violations = []
        scope = self.scope
        
        if scenario_count > scope.maximum_scenario_count:
            violations.append("scenario_limit_exceeded")
        if event_count > scope.maximum_event_count:
            violations.append("event_limit_exceeded")
        if state_count > scope.maximum_state_count:
            violations.append("state_limit_exceeded")
        
        return tuple(violations)


# =============================================================================
# COUNTERFACTUAL REQUEST - Request for counterfactual analysis
# =============================================================================

@dataclass(frozen=True, slots=True)
class CounterfactualRequest:
    """
    Immutable request to perform one bounded counterfactual analysis episode.
    
    A counterfactual explicitly distinguishes baseline facts from modified
    antecedents and evaluates how outcomes might differ.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • purpose: What kind of counterfactual analysis is being requested
        • subject: What the counterfactual is about
        • scope: Bounded constraints on the analysis
        • baseline_trajectory_or_outcome: The actual trajectory or outcome
        • changed_antecedents: What antecedents are modified
        • preserved_antecedents: What antecedents remain unchanged
        • interventions: Specific modifications being tested
        
    NOT RESPONSIBLE FOR:
        - Executing counterfactual algorithms
        - Determining causal certainty
        - Mutating any state
    """
    
    # Identity and metadata
    request_id: CounterfactualRequestId
    """Unique identifier for this request."""
    
    purpose: str  # SimulationPurposeKind.COUNTERFACTUAL_REVIEW or similar
    """What kind of counterfactual analysis is being requested."""
    
    subject: str  # SimulationSubjectKind.*
    """What the counterfactual is about."""
    
    scope: SimulationScope
    """Bounded constraints on the analysis."""
    
    # Context binding
    context_id: InternalContextId
    """Reference to InternalContext revision."""
    
    context_revision: int = 1
    """Context version at request time."""
    
    baseline_trajectory_or_outcome: str
    """The actual trajectory or outcome being analyzed (ID reference)."""
    
    changed_antecedents: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of antecedents that are modified in the counterfactual."""
    
    preserved_antecedents: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of antecedents that remain unchanged."""
    
    interventions: Tuple[SimulationIntervention, ...] = field(default_factory=tuple)
    """Specific interventions being tested."""
    
    counterfactual_target: Optional[str] = None
    """The target outcome or relation being compared."""
    
    distance_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints on how much the counterfactual may differ."""
    
    causal_assumptions: Tuple[SimulationAssumption, ...] = field(
        default_factory=tuple
    )
    """Causal assumptions underlying the comparison."""
    
    requested_alternatives: int = 5
    """Number of alternative scenarios requested."""
    
    expected_products: FrozenSet[str] = field(default_factory=frozenset)
    """Product kinds expected from this analysis."""
    
    # Origin tracking
    originating_episode_id: Optional[InternalEpisodeId] = None
    """ID of parent episode if derived from one."""
    
    originating_thought_ids: Tuple[InternalThoughtId, ...] = field(
        default_factory=tuple
    )
    """Thought IDs that triggered this request."""
    
    requested_by: str = "DEFAULT_NETWORK"
    """Who/what made the request (CounterfactualRequester.*)."""
    
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
        baseline_trajectory_or_outcome: str,
        changed_antecedents: Tuple[str, ...],
        context_id: str,
        purpose: str = SimulationPurposeKind.COUNTERFACTUAL_REVIEW,
        subject: str = SimulationSubjectKind.GENERAL_SITUATION,
        scope: Optional[SimulationScope] = None,
        interventions: Tuple[SimulationIntervention, ...] = (),
        causal_assumptions: Tuple[SimulationAssumption, ...] = (),
        request_id: Optional[str] = None,
    ) -> CounterfactualRequest:
        """
        Create a new counterfactual request.
        
        Args:
            baseline_trajectory_or_outcome: The actual outcome being analyzed
            changed_antecedents: Antecedents modified in the counterfactual
            context_id: Reference to InternalContext revision
            purpose: What kind of analysis is requested
            subject: What the counterfactual is about
            scope: Optional scope (default = standard_level())
            interventions: Specific modifications being tested
            causal_assumptions: Causal assumptions underlying comparison
            request_id: Optional explicit ID
            
        Returns:
            New CounterfactualRequest instance
        """
        return cls(
            request_id=request_id or f"counterfactual_request_{id(baseline_trajectory_or_outcome)}",
            purpose=purpose,
            subject=subject,
            context_id=context_id,
            baseline_trajectory_or_outcome=baseline_trajectory_or_outcome,
            changed_antecedents=changed_antecedents,
            scope=scope or SimulationScope.standard_level(),
            interventions=interventions,
            causal_assumptions=causal_assumptions,
        )


# =============================================================================
# SIMULATION PRODUCT KINDS - Use enums module for product kinds
# =============================================================================

# Product kinds are defined in gordon_system.src.agent.networks.default.simulation.enums
# and imported via:
#     from gordon_system.src.agent.networks.default.simulation.enums import SimulationProductKind


# =============================================================================
# SIMULATION REQUESTER KINDS - Use enums module for requester kinds
# =============================================================================

# Requester kinds are defined in gordon_system.src.agent.networks.default.simulation.enums
# and imported via:
#     from gordon_system.src.agent.networks.default.simulation.enums import SimulationRequesterKind


# =============================================================================
# SIMULATION PROPOSAL KINDS - Use enums module for proposal kinds
# =============================================================================

# Proposal kinds are defined in gordon_system.src.agent.networks.default.simulation.enums
# and imported via:
#     from gordon_system.src.agent.networks.default.simulation.enums import SimulationProposalKind
