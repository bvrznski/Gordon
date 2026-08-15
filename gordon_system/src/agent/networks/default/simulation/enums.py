# Simulation Coordination - Canonical Vocabulary
# ================================================

"""
Canonical enum types and value sets for simulation and counterfactual coordination.

ARCHITECTURAL PRINCIPLES:
    - Immutable enum values
    - Deterministic ordering where applicable
    - Bounded sets (no unbounded expansion)
    - No runtime dependencies
"""

from __future__ import annotations

from typing import Tuple


# =============================================================================
# SIMULATION PURPOSE KINDS - Canonical categories of simulation intent
# =============================================================================

class SimulationPurposeKind:
    """
    Canonical purpose kinds for simulation episodes.
    
    Each purpose defines expected context requirements, allowed product kinds,
    completion rules, and confidence thresholds.
    """
    
    # Future exploration
    FUTURE_EXPLORATION = "future_exploration"
    """Explore possible future states and outcomes."""
    
    # Action and decision consequences
    ACTION_CONSEQUENCE_EXPLORATION = "action_consequence_exploration"
    """Explore potential consequences of actions or decisions."""
    
    PLAN_EVALUATION = "plan_evaluation"
    """Evaluate proposed plans under simulated conditions."""
    
    RISK_EXPLORATION = "risk_exploration"
    """Identify and assess potential risks in scenarios."""
    
    OPPORTUNITY_EXPLORATION = "opportunity_exploration"
    """Identify and assess potential opportunities in scenarios."""
    
    HYPOTHESIS_EXPLORATION = "hypothesis_exploration"
    """Test causal hypotheses through scenario exploration."""
    
    STATE_TRAJECTORY_EXPLORATION = "state_trajectory_exploration"
    """Explore possible state transitions and trajectories."""
    
    DECISION_SUPPORT = "decision_support"
    """Support decision-making by exploring alternatives."""
    
    FAILURE_ALTERNATIVE_ANALYSIS = "failure_alternative_analysis"
    """Analyze alternative outcomes that could have resulted from failures."""
    
    SUCCESS_ALTERNATIVE_ANALYSIS = "success_alternative_analysis"
    """Analyze alternative outcomes that could have resulted from successes."""
    
    COUNTERFACTUAL_REVIEW = "counterfactual_review"
    """Review how outcomes might differ under different antecedents."""
    
    CAUSAL_HYPOTHESIS_TEST = "causal_hypothesis_test"
    """Test causal hypotheses through controlled counterfactuals."""
    
    NARRATIVE_POSSIBILITY = "narrative_possibility"
    """Explore narrative possibilities and alternative interpretations."""
    
    IDENTITY_FUTURE_PROJECTION = "identity_future_projection"
    """Project identity-relevant future states and outcomes."""
    
    CREATIVE_SCENARIO_GENERATION = "creative_scenario_generation"
    """Generate novel scenario combinations for exploration."""
    
    RESOURCE_OUTCOME_EXPLORATION = "resource_outcome_exploration"
    """Explore resource-constrained outcome scenarios."""
    
    GENERAL_SIMULATION = "general_simulation"
    """General simulation without specific purpose focus."""
    
    @classmethod
    def all_purposes(cls) -> Tuple[str, ...]:
        """Return all valid purpose kinds."""
        return (
            cls.FUTURE_EXPLORATION,
            cls.ACTION_CONSEQUENCE_EXPLORATION,
            cls.PLAN_EVALUATION,
            cls.RISK_EXPLORATION,
            cls.OPPORTUNITY_EXPLORATION,
            cls.HYPOTHESIS_EXPLORATION,
            cls.STATE_TRAJECTORY_EXPLORATION,
            cls.DECISION_SUPPORT,
            cls.FAILURE_ALTERNATIVE_ANALYSIS,
            cls.SUCCESS_ALTERNATIVE_ANALYSIS,
            cls.COUNTERFACTUAL_REVIEW,
            cls.CAUSAL_HYPOTHESIS_TEST,
            cls.NARRATIVE_POSSIBILITY,
            cls.IDENTITY_FUTURE_PROJECTION,
            cls.CREATIVE_SCENARIO_GENERATION,
            cls.RESOURCE_OUTCOME_EXPLORATION,
            cls.GENERAL_SIMULATION,
        )
    
    @classmethod
    def requires_risk_assessment(cls, purpose: str) -> bool:
        """Check if purpose typically requires risk assessment."""
        return purpose in {
            cls.RISK_EXPLORATION,
            cls.ACTION_CONSEQUENCE_EXPLORATION,
            cls.FAILURE_ALTERNATIVE_ANALYSIS,
        }
    
    @classmethod
    def requires_outcome_evaluation(cls, purpose: str) -> bool:
        """Check if purpose typically requires outcome evaluation."""
        return purpose in {
            cls.PLAN_EVALUATION,
            cls.DECISION_SUPPORT,
            cls.SUCCESS_ALTERNATIVE_ANALYSIS,
        }


# =============================================================================
# SIMULATION SUBJECT KINDS - What is being simulated
# =============================================================================

class SimulationSubjectKind:
    """
    Canonical subject kinds for simulation.
    
    Each subject kind has distinct context requirements and simulation patterns.
    """
    
    CURRENT_STATE = "current_state"
    """Simulate possible futures from the current state."""
    
    ACTION = "action"
    """Simulate possible consequences of a specific action."""
    
    DECISION = "decision"
    """Simulate possible outcomes of a decision point."""
    
    PLAN = "plan"
    """Simulate possible execution trajectories of a plan."""
    
    OBJECTIVE = "objective"
    """Simulate progress toward or away from an objective."""
    
    TASK = "task"
    """Simulate task execution and potential deviations."""
    
    EXECUTION_THREAD = "execution_thread"
    """Simulate alternative paths in an execution thread."""
    
    EXECUTION_CYCLE = "execution_cycle"
    """Simulate variations within an execution cycle."""
    
    INTERNAL_EPISODE = "internal_episode"
    """Simulate alternative coordination patterns."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """Simulate thought evolution and alternatives."""
    
    SYSTEM_STATE = "system_state"
    """Simulate system-level state transitions."""
    
    ENVIRONMENT_STATE = "environment_state"
    """Simulate environmental changes and responses."""
    
    MEMORY = "memory"
    """Simulate memory-based projections and recall variations."""
    
    IDENTITY_STATE = "identity_state"
    """Simulate identity-related future states."""
    
    NARRATIVE = "narrative"
    """Simulate narrative alternatives and interpretations."""
    
    RELATIONSHIP = "relationship"
    """Simulate relationship dynamics and evolution."""
    
    RESOURCE_STATE = "resource_state"
    """Simulate resource-constrained scenarios."""
    
    FAILURE = "failure"
    """Simulate failure modes and recovery paths."""
    
    SUCCESS = "success"
    """Simulate success conditions and sustaining factors."""
    
    HYPOTHESIS = "hypothesis"
    """Simulate hypothesis-driven exploration."""
    
    GENERAL_SITUATION = "general_situation"
    """General simulation without specific subject focus."""
    
    @classmethod
    def all_subjects(cls) -> Tuple[str, ...]:
        """Return all valid subject kinds."""
        return (
            cls.CURRENT_STATE,
            cls.ACTION,
            cls.DECISION,
            cls.PLAN,
            cls.OBJECTIVE,
            cls.TASK,
            cls.EXECUTION_THREAD,
            cls.EXECUTION_CYCLE,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.SYSTEM_STATE,
            cls.ENVIRONMENT_STATE,
            cls.MEMORY,
            cls.IDENTITY_STATE,
            cls.NARRATIVE,
            cls.RELATIONSHIP,
            cls.RESOURCE_STATE,
            cls.FAILURE,
            cls.SUCCESS,
            cls.HYPOTHESIS,
            cls.GENERAL_SITUATION,
        )
    
    @classmethod
    def requires_execution_context(cls, subject: str) -> bool:
        """Check if subject typically needs execution context."""
        return subject in {
            cls.EXECUTION_THREAD,
            cls.EXECUTION_CYCLE,
            cls.ACTION,
            cls.DECISION,
            cls.PLAN,
            cls.TASK,
        }
    
    @classmethod
    def requires_memory_context(cls, subject: str) -> bool:
        """Check if subject typically needs memory context."""
        return subject in {
            cls.MEMORY,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.NARRATIVE,
            cls.IDENTITY_STATE,
        }


# =============================================================================
# SIMULATION FACTUALITY CLASSIFICATION - Evidence quality markers
# =============================================================================

class SimulationFactuality:
    """
    Canonical factuality classifications for simulation products.
    
    Every source and product must be classified to prevent confusion between
    simulated and observed states.
    """
    
    OBSERVED = "observed"
    """Directly observed or measured state."""
    
    REPORTED = "reported"
    """Reported by external sources (not independently verified)."""
    
    INFERRED = "inferred"
    """Inferred from evidence but not directly observed."""
    
    PREDICTED = "predicted"
    """Predicted based on patterns and models."""
    
    SIMULATED = "simulated"
    """Generated through simulation coordination."""
    
    COUNTERFACTUAL = "counterfactual"
    """Generated through counterfactual analysis."""
    
    HYPOTHETICAL = "hypothetical"
    """Hypothetical construct without specific evidence base."""
    
    UNKNOWN = "unknown"
    """Factual status cannot be determined."""
    
    @classmethod
    def is_simulated(cls, factuality: str) -> bool:
        """Check if factuality represents simulated content."""
        return factuality in {cls.SIMULATED, cls.COUNTERFACTUAL}
    
    @classmethod
    def is_not_observed(cls, factuality: str) -> bool:
        """Check if factuality is NOT directly observed."""
        return factuality not in {cls.OBSERVED}


# =============================================================================
# SIMULATION BASELINE KINDS - Starting points for simulation
# =============================================================================

class SimulationBaselineKind:
    """
    Canonical baseline kinds for simulations.
    
    Baselines represent the starting state or trajectory against which scenarios
    are constructed and compared.
    """
    
    CURRENT_STATE_PROJECTION = "current_state_projection"
    """Projection of current state into future conditions."""
    
    OBSERVED_OUTCOME = "observed_outcome"
    """Historically observed outcome as baseline."""
    
    EXPECTED_OUTCOME = "expected_outcome"
    """Expected outcome based on plans or predictions."""
    
    PLAN_STATE = "plan_state"
    """State defined by an active plan."""
    
    ACTION_STATE = "action_state"
    """State resulting from a specific action."""
    
    MEMORY_DERIVED_STATE = "memory_derived_state"
    """State inferred from memory content."""
    
    NARRATIVE_STATE = "narrative_state"
    """State defined by current narrative structure."""
    
    IDENTITY_STATE = "identity_state"
    """State required for identity consistency."""
    
    HYPOTHETICAL_STATE = "hypothetical_state"
    """Hypothetical starting point for exploration."""
    
    PRIOR_SIMULATION_RESULT = "prior_simulation_result"
    """Result from a previous simulation as baseline."""
    
    @classmethod
    def all_baseline_kinds(cls) -> Tuple[str, ...]:
        """Return all valid baseline kinds."""
        return (
            cls.CURRENT_STATE_PROJECTION,
            cls.OBSERVED_OUTCOME,
            cls.EXPECTED_OUTCOME,
            cls.PLAN_STATE,
            cls.ACTION_STATE,
            cls.MEMORY_DERIVED_STATE,
            cls.NARRATIVE_STATE,
            cls.IDENTITY_STATE,
            cls.HYPOTHETICAL_STATE,
            cls.PRIOR_SIMULATION_RESULT,
        )


# =============================================================================
# SIMULATION ASSUMPTION KINDS - Types of assumptions
# =============================================================================

class SimulationAssumptionKind:
    """
    Canonical assumption kinds for simulations.
    
    Assumptions define what remains fixed versus variable in a simulation.
    """
    
    FIXED = "fixed"
    """Must remain unchanged; foundational premise."""
    
    VARIABLE = "variable"
    """May vary across scenarios."""
    
    DEFAULT = "default"
    """Default value used when not specified otherwise."""
    
    CONDITIONAL = "conditional"
    """Assumed only if certain conditions hold."""
    
    CONTESTED = "contested"
    """Disputed or uncertain; may affect confidence."""
    
    UNKNOWN = "unknown"
    """Unknown assumption that may need investigation."""
    
    @classmethod
    def all_assumption_kinds(cls) -> Tuple[str, ...]:
        """Return all valid assumption kinds."""
        return (
            cls.FIXED,
            cls.VARIABLE,
            cls.DEFAULT,
            cls.CONDITIONAL,
            cls.CONTESTED,
            cls.UNKNOWN,
        )
    
    @classmethod
    def is_fixed(cls, kind: str) -> bool:
        """Check if assumption kind represents a fixed constraint."""
        return kind == cls.FIXED
    
    @classmethod
    def is_variable(cls, kind: str) -> bool:
        """Check if assumption kind represents a variable parameter."""
        return kind == cls.VARIABLE


# =============================================================================
# SIMULATION INTERVENTION KINDS - Types of modifications
# =============================================================================

class SimulationInterventionKind:
    """
    Canonical intervention kinds for simulations.
    
    Interventions represent explicit hypothetical modifications to the baseline.
    """
    
    ACTION_CHANGED = "action_changed"
    """A different action was taken."""
    
    DECISION_CHANGED = "decision_changed"
    """A different decision was made."""
    
    EVENT_REMOVED = "event_removed"
    """An event that occurred was prevented."""
    
    EVENT_ADDED = "event_added"
    """An additional event occurred."""
    
    VALUE_CHANGED = "value_changed"
    """A numerical or categorical value changed."""
    
    CONSTRAINT_CHANGED = "constraint_changed"
    """A constraint was relaxed, tightened, or removed."""
    
    RESOURCE_CHANGED = "resource_changed"
    """Resource allocation or availability changed."""
    
    TIMING_CHANGED = "timing_changed"
    """Timing or sequence of events changed."""
    
    ORDER_CHANGED = "order_changed"
    """Order or priority of actions changed."""
    
    STATE_REPLACED = "state_replaced"
    """State was replaced by alternative state."""
    
    POLICY_CHANGED = "policy_changed"
    """Policy or rule changed."""
    
    ASSUMPTION_CHANGED = "assumption_changed"
    """Assumption that was fixed is now variable or vice versa."""
    
    DEPENDENCY_CHANGED = "dependency_changed"
    """Dependency between events or states changed."""
    
    UNKNOWN = "unknown"
    """Intervention type cannot be determined."""
    
    @classmethod
    def all_intervention_kinds(cls) -> Tuple[str, ...]:
        """Return all valid intervention kinds."""
        return (
            cls.ACTION_CHANGED,
            cls.DECISION_CHANGED,
            cls.EVENT_REMOVED,
            cls.EVENT_ADDED,
            cls.VALUE_CHANGED,
            cls.CONSTRAINT_CHANGED,
            cls.RESOURCE_CHANGED,
            cls.TIMING_CHANGED,
            cls.ORDER_CHANGED,
            cls.STATE_REPLACED,
            cls.POLICY_CHANGED,
            cls.ASSUMPTION_CHANGED,
            cls.DEPENDENCY_CHANGED,
            cls.UNKNOWN,
        )


# =============================================================================
# SIMULATION PRODUCT KINDS - Types of simulation products
# =============================================================================

class SimulationProductKind:
    """
    Canonical product kinds generated through simulation.
    
    Products are semantic results that may be integrated with InternalThought.
    """
    
    SCENARIO = "scenario"
    """Complete scenario definition."""
    
    TRAJECTORY = "trajectory"
    """Ordered sequence of states and events."""
    
    SIMULATED_STATE = "simulated_state"
    """Simulated state snapshot."""
    
    SIMULATED_EVENT = "simulated_event"
    """Simulated event or transition."""
    
    CONSEQUENCE = "consequence"
    """Identified consequence of a scenario."""
    
    RISK = "risk"
    """Identified risk in scenarios."""
    
    OPPORTUNITY = "opportunity"
    """Identified opportunity in scenarios."""
    
    ALTERNATIVE = "alternative"
    """Alternative path or outcome identified."""
    
    COUNTERFACTUAL = "counterfactual"
    """Counterfactual analysis result."""
    
    CAUSAL_HYPOTHESIS = "causal_hypothesis"
    """Causal hypothesis supported by simulation."""
    
    DIVERGENCE = "divergence"
    """Divergence point in counterfactual analysis."""
    
    ROBUSTNESS_ASSESSMENT = "robustness_assessment"
    """Robustness assessment of scenarios."""
    
    UNCERTAINTY = "uncertainty"
    """Identified uncertainty in simulation."""
    
    MODEL_LIMITATION = "model_limitation"
    """Known limitation of the simulation model."""
    
    QUESTION = "question"
    """Open question raised by simulation."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """Simulation completed without meaningful product."""
    
    @classmethod
    def all_product_kinds(cls) -> Tuple[str, ...]:
        """Return all valid product kinds."""
        return (
            cls.SCENARIO,
            cls.TRAJECTORY,
            cls.SIMULATED_STATE,
            cls.SIMULATED_EVENT,
            cls.CONSEQUENCE,
            cls.RISK,
            cls.OPPORTUNITY,
            cls.ALTERNATIVE,
            cls.COUNTERFACTUAL,
            cls.CAUSAL_HYPOTHESIS,
            cls.DIVERGENCE,
            cls.ROBUSTNESS_ASSESSMENT,
            cls.UNCERTAINTY,
            cls.MODEL_LIMITATION,
            cls.QUESTION,
            cls.NO_MEANINGFUL_RESULT,
        )
    
    @classmethod
    def is_hypothesis(cls, product_kind: str) -> bool:
        """Check if product kind represents a hypothesis (not yet validated)."""
        return product_kind in {
            cls.CAUSAL_HYPOTHESIS,
            cls.QUESTION,
            cls.DIVERGENCE,
        }
    
    @classmethod
    def is_assessment(cls, product_kind: str) -> bool:
        """Check if product kind represents an assessment."""
        return product_kind in {
            cls.RISK,
            cls.OPPORTUNITY,
            cls.ROBUSTNESS_ASSESSMENT,
            cls.UNCERTAINTY,
            cls.MODEL_LIMITATION,
        }


# =============================================================================
# SIMULATION OUTCOME KINDS - Terminal results of simulation
# =============================================================================

class SimulationOutcomeKind:
    """
    Canonical outcome kinds for simulation episodes.
    
    Outcomes represent what the simulation episode produced, not runtime commands.
    """
    
    # Successful outcomes
    SCENARIOS_PRODUCED = "scenarios_produced"
    """Valid scenarios were generated."""
    
    TRAJECTORIES_PRODUCED = "trajectories_produced"
    """Valid trajectories were generated."""
    
    CONSEQUENCES_IDENTIFIED = "consequences_identified"
    """Material consequences were identified."""
    
    RISKS_IDENTIFIED = "risks_identified"
    """Material risks were identified."""
    
    OPPORTUNITIES_IDENTIFIED = "opportunities_identified"
    """Material opportunities were identified."""
    
    COUNTERFACTUALS_PRODUCED = "counterfactuals_produced"
    """Valid counterfactual analyses were produced."""
    
    CAUSAL_EVIDENCE_PRODUCED = "causal_evidence_produced"
    """Causal evidence was gathered."""
    
    ALTERNATIVES_COMPARED = "alternatives_compared"
    """Alternatives were compared and assessed."""
    
    # Partial outcomes
    PARTIALLY_COMPLETED = "partially_completed"
    """Some simulation steps completed but not all."""
    
    INSUFFICIENT_CONTEXT = "insufficient_context"
    """Context did not meet minimum requirements."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """Simulation completed without meaningful result."""
    
    # Failure states
    MODEL_UNAVAILABLE = "model_unavailable"
    """Required simulation model was unavailable."""
    
    MODEL_INAPPLICABLE = "model_inapplicable"
    """Required simulation model is inapplicable to subject."""
    
    UNRESOLVED = "unresolved"
    """Simulation could not resolve key questions."""
    
    FAILED = "failed"
    """Terminated without valid outcome."""
    
    CANCELLED = "cancelled"
    """Terminated before completion."""
    
    EXPIRED = "expired"
    """Terminated due to expiration."""
    
    @classmethod
    def all_outcomes(cls) -> Tuple[str, ...]:
        """Return all valid outcome kinds."""
        return (
            cls.SCENARIOS_PRODUCED,
            cls.TRAJECTORIES_PRODUCED,
            cls.CONSEQUENCES_IDENTIFIED,
            cls.RISKS_IDENTIFIED,
            cls.OPPORTUNITIES_IDENTIFIED,
            cls.COUNTERFACTUALS_PRODUCED,
            cls.CAUSAL_EVIDENCE_PRODUCED,
            cls.ALTERNATIVES_COMPARED,
            cls.PARTIALLY_COMPLETED,
            cls.INSUFFICIENT_CONTEXT,
            cls.NO_MEANINGFUL_RESULT,
            cls.MODEL_UNAVAILABLE,
            cls.MODEL_INAPPLICABLE,
            cls.UNRESOLVED,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
        )
    
    @classmethod
    def is_success(cls, outcome: str) -> bool:
        """Check if outcome kind represents successful simulation."""
        return outcome in {
            cls.SCENARIOS_PRODUCED,
            cls.TRAJECTORIES_PRODUCED,
            cls.CONSEQUENCES_IDENTIFIED,
            cls.RISKS_IDENTIFIED,
            cls.OPPORTUNITIES_IDENTIFIED,
            cls.COUNTERFACTUALS_PRODUCED,
            cls.CAUSAL_EVIDENCE_PRODUCED,
            cls.ALTERNATIVES_COMPARED,
        }
    
    @classmethod
    def is_terminal(cls, outcome: str) -> bool:
        """Check if outcome kind represents terminal state."""
        return outcome in {
            cls.SCENARIOS_PRODUCED,
            cls.TRAJECTORIES_PRODUCED,
            cls.CONSEQUENCES_IDENTIFIED,
            cls.RISKS_IDENTIFIED,
            cls.OPPORTUNITIES_IDENTIFIED,
            cls.COUNTERFACTUALS_PRODUCED,
            cls.CAUSAL_EVIDENCE_PRODUCED,
            cls.ALTERNATIVES_COMPARED,
            cls.PARTIALLY_COMPLETED,
            cls.INSUFFICIENT_CONTEXT,
            cls.NO_MEANINGFUL_RESULT,
            cls.MODEL_UNAVAILABLE,
            cls.MODEL_INAPPLICABLE,
            cls.UNRESOLVED,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
        }


# =============================================================================
# SIMULATION CONTINUATION KINDS - Advisory recommendations
# =============================================================================

class SimulationContinuationKind:
    """
    Canonical continuation kinds for simulation episodes.
    
    Continuation recommendations are advisory. They do NOT schedule execution.
    """
    
    COMPLETE = "complete"
    """Simulation completed successfully."""
    
    CONTINUE_CURRENT_SCENARIO = "continue_current_scenario"
    """Continue processing current scenario."""
    
    GENERATE_ADDITIONAL_SCENARIO = "generate_additional_scenario"
    """Generate more scenarios for coverage."""
    
    EXPAND_TRAJECTORY = "expand_trajectory"
    """Expand trajectory depth or breadth."""
    
    REFINE_ASSUMPTIONS = "refine_assumptions"
    """Refine assumptions and rerun simulation."""
    
    REQUEST_CONTEXT_REFRESH = "request_context_refresh"
    """Refresh context binding with updated projections."""
    
    REQUEST_MODEL = "request_model"
    """Request a specific simulation model."""
    
    WAIT_FOR_CAPABILITY = "wait_for_capability"
    """Wait for capability result."""
    
    COMPARE_SCENARIOS = "compare_scenarios"
    """Compare existing scenarios before proceeding."""
    
    DERIVE_COUNTERFactual = "derive_counterfactual"
    """Derive counterfactual analysis from current results."""
    
    REQUEST_REASONING_REVIEW = "request_reasoning_review"
    """Request reasoning capability to review simulation products."""
    
    REQUEST_REFLECTION = "request_reflection"
    """Request reflection on simulation results."""
    
    SUBMIT_WORKSPACE_CANDIDATE = "submit_workspace_candidate"
    """Submit workspace candidate for further consideration."""
    
    REQUEST_EXECUTION_TASK = "request_execution_task"
    """Request an ExecutionTask for persistent coordination."""
    
    SUSPEND = "suspend"
    """Suspend processing, may resume later."""
    
    FAIL = "fail"
    """Mark as failed with error."""
    
    CANCEL = "cancel"
    """Cancel the simulation episode."""
    
    @classmethod
    def all_continuation_kinds(cls) -> Tuple[str, ...]:
        """Return all valid continuation kinds."""
        return (
            cls.COMPLETE,
            cls.CONTINUE_CURRENT_SCENARIO,
            cls.GENERATE_ADDITIONAL_SCENARIO,
            cls.EXPAND_TRAJECTORY,
            cls.REFINE_ASSUMPTIONS,
            cls.REQUEST_CONTEXT_REFRESH,
            cls.REQUEST_MODEL,
            cls.WAIT_FOR_CAPABILITY,
            cls.COMPARE_SCENARIOS,
            cls.DERIVE_COUNTERFactual,
            cls.REQUEST_REASONING_REVIEW,
            cls.REQUEST_REFLECTION,
            cls.SUBMIT_WORKSPACE_CANDIDATE,
            cls.REQUEST_EXECUTION_TASK,
            cls.SUSPEND,
            cls.FAIL,
            cls.CANCEL,
        )
    
    @classmethod
    def is_terminal(cls, kind: str) -> bool:
        """Check if continuation kind represents terminal state."""
        return kind in {
            cls.COMPLETE,
            cls.FAIL,
            cls.CANCEL,
        }
    
    @classmethod
    def requires_external_action(cls, kind: str) -> bool:
        """Check if continuation kind requires external coordination."""
        return kind in {
            cls.REQUEST_CONTEXT_REFRESH,
            cls.WAIT_FOR_CAPABILITY,
            cls.DERIVE_COUNTERFactual,
            cls.REQUEST_REASONING_REVIEW,
            cls.REQUEST_REFLECTION,
            cls.SUBMIT_WORKSPACE_CANDIDATE,
            cls.REQUEST_EXECUTION_TASK,
        }


# =============================================================================
# SIMULATION MODEL LIMITATION KINDS
# =============================================================================

class SimulationModelLimitationKind:
    """
    Canonical limitation kinds that affect simulation confidence.
    
    Every material limitation must affect confidence or completeness assessment.
    """
    
    OUT_OF_DISTRIBUTION = "out_of_distribution"
    """Request falls outside model's training distribution."""
    
    INSUFFICIENT_CONTEXT = "insufficient_context"
    """Context does not provide adequate information."""
    
    UNSUPPORTED_DOMAIN = "unsupported_domain"
    """Domain is not supported by the simulation model."""
    
    LOW_FIDELITY = "low_fidelity"
    """Model fidelity is insufficient for required precision."""
    
    MISSING_DYNAMICS = "missing_dynamics"
    """Critical dynamics are not modeled."""
    
    UNKNOWN_VARIABLE = "unknown_variable"
    """Unknown variable may significantly affect results."""
    
    CAUSAL_MODEL_WEAK = "causal_model_weak"
    """Causal model lacks sufficient support."""
    
    TEMPORAL_LIMIT = "temporal_limit"
    """Temporal horizon exceeds model capabilities."""
    
    RESOURCE_LIMIT = "resource_limit"
    """Computational resources limit simulation scope."""
    
    INCONSISTENT_INPUT = "inconsistent_input"
    """Input contains contradictory information."""
    
    UNKNOWN = "unknown"
    """Limitation cannot be determined."""
    
    @classmethod
    def all_limitation_kinds(cls) -> Tuple[str, ...]:
        """Return all valid limitation kinds."""
        return (
            cls.OUT_OF_DISTRIBUTION,
            cls.INSUFFICIENT_CONTEXT,
            cls.UNSUPPORTED_DOMAIN,
            cls.LOW_FIDELITY,
            cls.MISSING_DYNAMICS,
            cls.UNKNOWN_VARIABLE,
            cls.CAUSAL_MODEL_WEAK,
            cls.TEMPORAL_LIMIT,
            cls.RESOURCE_LIMIT,
            cls.INCONSISTENT_INPUT,
            cls.UNKNOWN,
        )


# =============================================================================
# SIMULATION BRANCHING LIMITS
# =============================================================================

class SimulationBranchingLimit:
    """
    Canonical branching limits for simulation.
    
    These prevent unbounded scenario generation through explicit bounds.
    """
    
    MAXIMUM_SCENARIOS = "maximum_scenarios"
    """Maximum number of scenarios allowed."""
    
    MAXIMUM_BRANCHES_PER_SCENARIO = "maximum_branches_per_scenario"
    """Maximum branches from any single scenario state."""
    
    MAXIMUM_TRAJECTORY_DEPTH = "maximum_trajectory_depth"
    """Maximum depth of trajectory states."""
    
    MAXIMUM_TOTAL_STATES = "maximum_total_states"
    """Maximum total simulated states across all scenarios."""
    
    MAXIMUM_TOTAL_EVENTS = "maximum_total_events"
    """Maximum total simulated events across all scenarios."""
    
    MAXIMUM_ALTERNATIVE_INTERVENTIONS = "maximum_alternative_interventions"
    """Maximum alternative interventions considered per scenario."""
    
    MAXIMUM_NESTED_COUNTERFACTUALS = "maximum_nested_counterfactuals"
    """Maximum counterfactual nesting depth."""
    
    MAXIMUM_CHILD_EPISODES = "maximum_child_episodes"
    """Maximum child episodes derived from this simulation."""
    
    @classmethod
    def all_limit_kinds(cls) -> Tuple[str, ...]:
        """Return all valid branching limit kinds."""
        return (
            cls.MAXIMUM_SCENARIOS,
            cls.MAXIMUM_BRANCHES_PER_SCENARIO,
            cls.MAXIMUM_TRAJECTORY_DEPTH,
            cls.MAXIMUM_TOTAL_STATES,
            cls.MAXIMUM_TOTAL_EVENTS,
            cls.MAXIMUM_ALTERNATIVE_INTERVENTIONS,
            cls.MAXIMUM_NESTED_COUNTERFACTUALS,
            cls.MAXIMUM_CHILD_EPISODES,
        )


# =============================================================================
# SIMULATION REQUESTER KINDS
# =============================================================================

class SimulationRequesterKind:
    """
    Canonical requester kinds for simulation requests.
    """
    
    DEFAULT_NETWORK = "default_network"
    REFLECTION_COORDINATOR = "reflection_coordinator"
    PLANNING_COORDINATOR = "planning_coordinator"
    EXECUTION_THREAD = "execution_thread"
    EXTERNAL_API = "external_api"
    TEST_SYSTEM = "test_system"


# =============================================================================
# SIMULATION COUNTERFACTUAL DISTANCE KINDS
# =============================================================================

class SimulationCounterfactualDistanceKind:
    """
    Canonical distance components for counterfactual analysis.
    """
    
    CHANGED_ANTECEDENT_COUNT = "changed_antecedent_count"
    """Number of antecedents that differ."""
    
    SEMANTIC_MAGNITUDE = "semantic_magnitude"
    """Semantic magnitude of changes."""
    
    TEMPORAL_DISTANCE = "temporal_distance"
    """Temporal distance from baseline."""
    
    STATE_DIVERGENCE = "state_divergence"
    """State divergence point count."""
    
    POLICY_DIVERGENCE = "policy_divergence"
    """Policy divergence points."""
    
    ACTION_DIVERGENCE = "action_divergence"
    """Action divergence points."""
    
    CAUSAL_MODEL_DEVIATION = "causal_model_deviation"
    """Causal model deviation score."""


# =============================================================================
# SIMULATION OUTCOME STATUS KINDS
# =============================================================================

class SimulationOutcomeStatus:
    """
    Canonical status kinds for simulation outcomes.
    """
    
    COMPLETE = "complete"
    """Simulation completed successfully."""
    
    PARTIAL = "partial"
    """Simulation partially completed."""
    
    INSUFFICIENT = "insufficient"
    """Insufficient context or data."""
    
    FAILED = "failed"
    """Simulation failed to complete."""
    
    CANCELLED = "cancelled"
    """Simulation was cancelled."""
    
    EXPIRED = "expired"
    """Simulation expired before completion."""


# =============================================================================
# SIMULATION CONFIDENCE LEVELS
# =============================================================================

class SimulationConfidenceLevel:
    """
    Canonical confidence levels for simulation results.
    """
    
    LOW = 0.3
    """Low confidence - requires further validation."""
    
    MEDIUM = 0.6
    """Medium confidence - generally reliable."""
    
    HIGH = 0.85
    """High confidence - well-supported."""
    
    CERTAIN = 0.95
    """Near certainty - strongly supported."""
