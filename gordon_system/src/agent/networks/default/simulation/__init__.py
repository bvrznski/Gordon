# Simulation and Counterfactual Coordination
# ===========================================

"""
Canonical coordination layer for internally generated simulation and counterfactual cognition.

This package implements:

1. SIMULATION COORDINATION:
   - Simulation requests (what to simulate)
   - Purpose-driven simulation planning
   - Scenario generation and evaluation
   - Bounded trajectory exploration
   - Consequence analysis

2. COUNTERFACTUAL COORDINATION:
   - Counterfactual requests (how alternatives differ)
   - Baseline comparison
   - Divergence measurement
   - Minimal-change analysis
   - Causal relevance assessment

3. ARCHITECTURAL PRINCIPLES:
   - Simulation coordination is distinct from simulation computation
   - All data structures are immutable and deeply frozen
   - No runtime dependencies (no Core, no Execution, no scheduling)
   - Bounded by explicit limits on scenarios, branches, states, events
   - Products never labeled as observed/factual

4. CANONICAL DEFINITIONS:
   
   Simulation:
       A bounded internally generated cognitive undertaking that constructs
       and evaluates possible states, event sequences, trajectories, or outcomes
       under explicit assumptions and constraints.
   
   Counterfactual analysis:
       Evaluates how a represented outcome might differ if antecedent conditions
       were changed.

5. ARCHITECTURAL BOUNDARIES:
   
   DefaultNetwork owns simulation coordination but NOT:
       - World model implementations
       - Imagination algorithms
       - Prediction algorithms
       - Planning algorithms
       - Action selection or execution
       - Memory updates
       - Identity updates

ARCHITECTURAL INVARIANTS:
    DEFAULT-SIM-INV-001: Simulation coordination does not implement simulation algorithms
    DEFAULT-SIM-INV-002: Every simulation belongs to exactly one InternalEpisode
    DEFAULT-SIM-INV-003: Every simulation has one explicit purpose, subject, and bounded scope
    DEFAULT-SIM-INV-004: Every simulation binds to one InternalContext revision at a time
    DEFAULT-SIM-INV-005: Every simulation has an explicit baseline
    DEFAULT-SIM-INV-006: Every assumption is explicit
    DEFAULT-SIM-INV-007: Every intervention is explicit
    DEFAULT-SIM-INV-008: Simulated and counterfactual products are never labeled observed
    DEFAULT-SIM-INV-009: Simulation does not replace SimulationCycle
    DEFAULT-SIM-INV-010: Simulation does not own runtime progression

ARCHITECTURAL LAWS:
    DEFAULT-SIM-LAW-001: A possible state is not an observed state
    DEFAULT-SIM-LAW-002: A simulated outcome is not a prediction unless a predictive contract supports it
    DEFAULT-SIM-LAW-003: A scenario is not a plan
    DEFAULT-SIM-LAW-004: A consequence is not a behavioral command
    DEFAULT-SIM-LAW-005: An intervention modifies the simulated representation, never authoritative state
    DEFAULT-SIM-LAW-006: Assumptions must remain explicit and attributable
    DEFAULT-SIM-LAW-007: Simulation must expose uncertainty and model limitations
    DEFAULT-SIM-LAW-008: Counterfactual divergence may inform causal reasoning but does not establish causality by itself
    DEFAULT-SIM-LAW-009: Scenario branching must remain bounded
    DEFAULT-SIM-LAW-010: Execution owns semantic progression and Core owns runtime mechanics
"""

from __future__ import annotations

# Import all public API types for easy access
from gordon_system.src.agent.networks.default.simulation.request import (
    SimulationRequest,
    CounterfactualRequest,
)
from gordon_system.src.agent.networks.default.simulation.enums import (
    # Purpose kinds
    SimulationPurposeKind,
    # Subject kinds  
    SimulationSubjectKind,
    # Factuality kinds
    SimulationFactuality,
    # Baseline kinds
    SimulationBaselineKind,
    # Assumption kinds
    SimulationAssumptionKind,
    # Intervention kinds
    SimulationInterventionKind,
    # Product kinds
    SimulationProductKind,
    # Outcome kinds
    SimulationOutcomeKind,
    # Continuation kinds
    SimulationContinuationKind,
    # Limitation kinds
    SimulationModelLimitationKind,
    # Branching limits
    SimulationBranchingLimit,
)

__all__ = [
    "SimulationRequest",
    "CounterfactualRequest",
    # Purpose and subject
    "SimulationPurposeKind",
    "SimulationSubjectKind",
    "SimulationFactuality",
    # Baseline and assumptions
    "SimulationBaselineKind",
    "SimulationAssumptionKind",
    "SimulationInterventionKind",
    # Product kinds
    "SimulationProductKind",
    # Outcome and continuation
    "SimulationOutcomeKind",
    "SimulationContinuationKind",
    # Limitations and limits
    "SimulationModelLimitationKind",
    "SimulationBranchingLimit",
]
