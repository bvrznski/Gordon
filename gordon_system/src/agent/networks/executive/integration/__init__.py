# Executive Network Integration Package
# =====================================

"""
Executive Network integration contracts for Phase 4.4.1.

This package defines how the Executive Network interfaces with other systems:
    - Core (runtime mechanics)
    - Execution (semantic progression)
    - Planning (plan generation)
    - Reasoning (semantic conclusion computation)
    - Decision (decision computation)
    - Action Selection (action candidate selection)
    - Alerting Network (exogenous attention)
    - Focusing Network (endogenous attention)
    - Default Network (internally generated cognition)
    - Motivation (drive state representation)
    - Working Memory (active content maintenance)
    - Workspace (admission and broadcast)
    - Memory (durable records)
    - Monitoring (repeated observation)
    - Policy (rules and constraints)
    - Security (authentication and authorization)
    - Communication (message preparation and delivery)

INTEGRATION PRINCIPLES:
======================

1. CONSUME PROJECTIONS, NOT IMPLEMENTATIONS
   The Executive Network consumes immutable projections from external systems.
   It never depends on concrete implementations.

2. PRODUCE PROPOSALS, NOT COMMANDS
   Executive outputs are proposals that downstream systems may accept or reject.
   They are not binding commands.

3. NO DIRECT INVOCATION
   The Executive Network never directly invokes other systems.
   It communicates through contracts and external coordination.

4. ASYMMETRICAL INTEGRATION
   External systems depend on the Executive for high-level coordination,
   but the Executive does NOT control their internal operation.
"""

from typing import Protocol, Any, Optional, List, Set, Tuple, Dict

# =============================================================================
# IMPORT FOUNDATIONAL TYPES FROM PARENT PACKAGE
# =============================================================================

from gordon_system.src.agent.networks.executive import (
    ExecutiveNetworkId,
    ExecutiveStateReference,
    ExecutiveContextReference,
    ExecutiveTaskSetReference,
    ExecutiveRequestReference,
    ExecutiveResultReference,
    ExecutiveProductReference,
    ExecutiveProposalReference,
    ExecutiveOutcomeReference,
    ExecutiveContinuationReference,
    ExecutiveAuthorityReference,
)

# =============================================================================
# CORE INTEGRATION CONTRACT
# =============================================================================


class CoreIntegrationContract(Protocol):
    """
    Contract for integration with Core (runtime mechanics).
    
    Core provides:
        - Runtime activation status
        - Service health information
        
    The Executive Network consumes:
        - Whether the system is running
        - Available services and their states
    
    The Executive Network does NOT:
        - Control Core lifecycle
        - Activate or deactivate Core services
        - Own runtime mechanics
    """
    
    @property
    def is_runtime_active(self) -> bool:
        """Is the Core runtime currently active?"""
        ...
    
    @property
    def available_services(self) -> Tuple[str, ...]:
        """IDs of currently available Core services."""
        ...


# =============================================================================
# EXECUTION INTEGRATION CONTRACT
# =============================================================================


class ExecutionIntegrationContract(Protocol):
    """
    Contract for integration with Execution (semantic progression).
    
    Execution provides:
        - Active thread information
        - Current loop and cycle state
        
    The Executive Network consumes:
        - Thread progress updates
        - Cycle completion status
    
    The Executive Network does NOT:
        - Control thread lifecycle
        - Select loops or cycles
        - Own semantic progression mechanics
    """
    
    @property
    def active_thread_id(self) -> Optional[str]:
        """ID of the currently active ExecutionThread."""
        ...
    
    @property
    def current_cycle_info(self) -> Dict[str, Any]:
        """Information about the current execution cycle."""
        ...


# =============================================================================
# PLANNING INTEGRATION CONTRACT
# =============================================================================


class PlanningIntegrationContract(Protocol):
    """
    Contract for integration with Planning (plan generation).
    
    The Executive Network may:
        - Request planning when plans are needed
        - Assess whether existing plans remain valid
        - Identify plan conflicts
    
    The Executive Network does NOT:
        - Generate detailed plans
        - Own plan structure or dependencies
        - Execute planning algorithms
    """
    
    def request_planning(
        self,
        objective: str,
        constraints: Tuple[str, ...],
    ) -> None:
        """Request Planning to generate a new plan."""
        ...
    
    def assess_plan_validity(self, plan_id: str) -> bool:
        """Assess whether a plan is still valid given current state."""
        ...


# =============================================================================
# REASONING INTEGRATION CONTRACT
# =============================================================================


class ReasoningIntegrationContract(Protocol):
    """
    Contract for integration with Reasoning (semantic conclusion computation).
    
    The Executive Network may:
        - Request reasoning when conclusions are needed
        - Assess reasoning sufficiency
        - Identify reasoning conflicts
    
    The Executive Network does NOT:
        - Perform inference directly
        - Own reasoning algorithms
        - Compute semantic conclusions
    """
    
    def request_reasoning(
        self,
        question: str,
        constraints: Tuple[str, ...],
    ) -> None:
        """Request Reasoning to compute semantic conclusions."""
        ...
    
    def assess_sufficiency(self, reasoning_id: str) -> bool:
        """Assess whether reasoning is sufficient for decision."""
        ...


# =============================================================================
# DECISION INTEGRATION CONTRACT
# =============================================================================


class DecisionIntegrationContract(Protocol):
    """
    Contract for integration with Decision (decision computation).
    
    The Executive Network may:
        - Declare when decisions are required
        - Assess decision readiness
        - Interpret decision outcomes
    
    The Executive Network does NOT:
        - Compute decisions directly
        - Own decision algorithms
        - Make final decisions without authority
    """
    
    def declare_decision_required(
        self,
        decision_scope: str,
        constraints: Tuple[str, ...],
    ) -> None:
        """Declare that a decision is required."""
        ...
    
    def assess_readiness(self, decision_id: str) -> bool:
        """Assess whether a decision is ready to be made."""
        ...


# =============================================================================
# ACTION SELECTION INTEGRATION CONTRACT
# =============================================================================


class ActionSelectionIntegrationContract(Protocol):
    """
    Contract for integration with Action Selection (action candidate selection).
    
    The Executive Network may:
        - Define action-selection constraints
        - Request action candidates
        - Interpret selected actions
    
    The Executive Network does NOT:
        - Select actions directly
        - Own action competition algorithms
        - Execute selected actions
    """
    
    def request_action_candidates(
        self,
        constraints: Tuple[str, ...],
    ) -> None:
        """Request admissible action candidates."""
        ...
    
    def set_selection_constraints(
        self,
        constraint_ids: Tuple[str, ...],
    ) -> None:
        """Set constraints for action selection."""
        ...


# =============================================================================
# ACTION EXECUTION INTEGRATION CONTRACT
# =============================================================================


class ActionExecutionIntegrationContract(Protocol):
    """
    Contract for integration with Action Execution (runtime action performance).
    
    The Executive Network may:
        - Receive execution results
        - Update strategy based on outcomes
    
    The Executive Network does NOT:
        - Execute actions directly
        - Own runtime execution mechanics
        - Call tools or services directly
    """
    
    def receive_execution_result(
        self,
        action_id: str,
        result: Dict[str, Any],
    ) -> None:
        """Receive notification of an action's execution result."""
        ...


# =============================================================================
# ALERTING INTEGRATION CONTRACT
# =============================================================================


class AlertingIntegrationContract(Protocol):
    """
    Contract for integration with Alerting Network (exogenous attention).
    
    The Executive Network may:
        - Consume alerting assessments
        - Evaluate executive relevance of alerts
        - Recommend task-set interruption if needed
    
    The Executive Network does NOT:
        - Detect raw signals itself
        - Perform Alerting computation
        - Equate alerting demand with executive priority automatically
    """
    
    def consume_alert(self, alert_id: str) -> Dict[str, Any]:
        """Consume an alert from the Alerting Network."""
        ...
    
    def assess_relevance(
        self,
        alert_assessment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assess executive relevance of an alert assessment."""
        ...


# =============================================================================
# FOCUSING INTEGRATION CONTRACT
# =============================================================================


class FocusingIntegrationContract(Protocol):
    """
    Contract for integration with Focusing Network (endogenous attention).
    
    The Executive Network may:
        - Recommend focus stabilization or switching
        - Specify executive relevance of targets
        - Request attention review
    
    The Executive Network does NOT:
        - Directly set focus
        - Mutate focus state
        - Perform focus competition
    """
    
    def request_focus_review(
        self,
        current_targets: Tuple[str, ...],
        required_by_task_set: bool,
    ) -> None:
        """Request Focusing to review attention allocation."""
        ...
    
    def recommend_focus_stabilization(self, target_id: str) -> None:
        """Recommend stabilizing focus on a specific target."""
        ...


# =============================================================================
# DEFAULT NETWORK INTEGRATION CONTRACT
# =============================================================================


class DefaultNetworkIntegrationContract(Protocol):
    """
    Contract for integration with Default Network (internally generated cognition).
    
    The Executive Network may:
        - Request reflection, simulation, or counterfactual analysis
        - Consume Default Network products
        - Interpret those products within executive state
    
    The Executive Network does NOT:
        - Duplicate Default Network functionality
        - Perform internally oriented cognition itself
    """
    
    def request_reflection(
        self,
        subject: str,
        scope: Tuple[str, ...],
    ) -> None:
        """Request reflection on a specific subject."""
        ...
    
    def receive_internal_product(self, product_id: str) -> Dict[str, Any]:
        """Receive an internally generated cognitive product."""
        ...


# =============================================================================
# MOTIVATION INTEGRATION CONTRACT
# =============================================================================


class MotivationIntegrationContract(Protocol):
    """
    Contract for integration with Motivation (drive state representation).
    
    The Executive Network may:
        - Consume motivational projections
        - Assess compatibility of control effort
        - Integrate effort cost into strategy review
    
    The Executive Network does NOT:
        - Fabricate motivation
        - Overwrite drive state
        - Treat motivation as executive priority automatically
    """
    
    def consume_motivation_projection(
        self,
        projection_id: str,
    ) -> Dict[str, Any]:
        """Consume a motivational projection."""
        ...
    
    def assess_justification(self, effort_cost: float) -> bool:
        """Assess whether control effort is justified by motivation."""
        ...


# =============================================================================
# WORKING MEMORY INTEGRATION CONTRACT
# =============================================================================


class WorkingMemoryIntegrationContract(Protocol):
    """
    Contract for integration with Working Memory (actively maintained content).
    
    The Executive Network may:
        - Recommend Working Memory maintenance
        - Request item refresh
        - Identify required task-set content
    
    The Executive Network does NOT:
        - Store items directly
        - Pin or evict items directly
        - Mutate Working Memory capacity
    """
    
    def request_item_maintenance(
        self,
        item_id: str,
        priority_boost: float = 0.0,
    ) -> None:
        """Request that a working memory item be maintained."""
        ...
    
    def consume_working_memory_projection(
        self,
        projection_id: str,
    ) -> Dict[str, Any]:
        """Consume a Working Memory projection."""
        ...


# =============================================================================
# WORKSPACE INTEGRATION CONTRACT
# =============================================================================


class WorkspaceIntegrationContract(Protocol):
    """
    Contract for integration with the shared Workspace.
    
    The Executive Network may:
        - Consume workspace projections
        - Recommend workspace admission
        - Assess relevance of globally available information
    
    The Executive Network does NOT:
        - Self-admit content
        - Broadcast directly
        - Mutate workspace state
    """
    
    def consume_workspace_projection(
        self,
        projection_id: str,
    ) -> Dict[str, Any]:
        """Consume a Workspace projection."""
        ...
    
    def recommend_admission(self, candidate_id: str) -> None:
        """Recommend that an item be admitted to the workspace."""
        ...


# =============================================================================
# MEMORY INTEGRATION CONTRACT
# =============================================================================


class MemoryIntegrationContract(Protocol):
    """
    Contract for integration with Memory (durable semantic records).
    
    The Executive Network may:
        - Consume prior outcomes and strategies
        - Produce memory update proposals
        - Request historical evidence
    
    The Executive Network does NOT:
        - Write or retrieve directly
        - Own durable storage mechanics
    """
    
    def request_memory_evidence(
        self,
        query: Dict[str, Any],
    ) -> None:
        """Request relevant memory records."""
        ...
    
    def propose_memory_update(self, update_id: str) -> None:
        """Propose a memory record for storage."""
        ...


# =============================================================================
# MONITORING INTEGRATION CONTRACT
# =============================================================================


class MonitoringIntegrationContract(Protocol):
    """
    Contract for integration with Monitoring (repeated observation).
    
    The Executive Network may:
        - Identify what should be monitored
        - Interpret monitoring results
        - Produce MonitoringProposals
    
    The Executive Network does NOT:
        - Poll or sleep directly
        - Create timers or threads
        - Own monitoring cadence
    """
    
    def identify_monitoring_target(
        self,
        target: str,
        criteria: Tuple[str, ...],
    ) -> None:
        """Identify something that should be monitored."""
        ...
    
    def interpret_monitoring_result(
        self,
        result_id: str,
    ) -> Dict[str, Any]:
        """Interpret a monitoring result within executive context."""
        ...


# =============================================================================
# POLICY INTEGRATION CONTRACT
# =============================================================================


class PolicyIntegrationContract(Protocol):
    """
    Contract for integration with Policy (rules and constraints).
    
    The Executive Network may:
        - Consume policy projections
        - Assess policy applicability
        - Identify policy conflicts
    
    The Executive Network does NOT:
        - Create or override policy
        - Interpret policy authority
        - Grant exceptions
    """
    
    def consume_policy_projection(
        self,
        projection_id: str,
    ) -> Dict[str, Any]:
        """Consume a policy projection."""
        ...
    
    def assess_applicability(self, rule_id: str) -> bool:
        """Assess whether a rule applies to current context."""
        ...


# =============================================================================
# SECURITY INTEGRATION CONTRACT
# =============================================================================


class SecurityIntegrationContract(Protocol):
    """
    Contract for integration with Security (authentication and authorization).
    
    The Executive Network may:
        - Identify when security review is required
        - Preserve security constraints
        - Produce SecurityReviewProposals
    
    The Executive Network does NOT:
        - Grant access or change credentials
        - Create principals
        - Bypass policy
    """
    
    def identify_security_requirement(
        self,
        action: str,
    ) -> None:
        """Identify that a security review is required."""
        ...
    
    def receive_security_decision(
        self,
        decision_id: str,
        permitted: bool,
    ) -> None:
        """Receive a security authorization decision."""
        ...


# =============================================================================
# COMMUNICATION INTEGRATION CONTRACT
# =============================================================================


class CommunicationIntegrationContract(Protocol):
    """
    Contract for integration with Communication (message preparation and delivery).
    
    The Executive Network may:
        - Determine when communication is required
        - Specify executive constraints on messages
        - Produce CommunicationContentProposals
    
    The Executive Network does NOT:
        - Send messages directly
        - Select transport mechanisms
        - Disclose restricted internal content
    """
    
    def determine_communication_required(
        self,
        intent: str,
    ) -> None:
        """Determine that communication is required."""
        ...
    
    def produce_message_content_proposal(
        self,
        message_id: str,
    ) -> Dict[str, Any]:
        """Produce a proposal for message content."""
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    # Foundational types (re-exported)
    "ExecutiveNetworkId",
    "ExecutiveStateReference",
    "ExecutiveContextReference",
    "ExecutiveTaskSetReference",
    "ExecutiveRequestReference",
    "ExecutiveResultReference",
    "ExecutiveProductReference",
    "ExecutiveProposalReference",
    "ExecutiveOutcomeReference",
    "ExecutiveContinuationReference",
    "ExecutiveAuthorityReference",
    
    # Integration contracts
    "CoreIntegrationContract",
    "ExecutionIntegrationContract",
    "PlanningIntegrationContract",
    "ReasoningIntegrationContract",
    "DecisionIntegrationContract",
    "ActionSelectionIntegrationContract",
    "ActionExecutionIntegrationContract",
    "AlertingIntegrationContract",
    "FocusingIntegrationContract",
    "DefaultNetworkIntegrationContract",
    "MotivationIntegrationContract",
    "WorkingMemoryIntegrationContract",
    "WorkspaceIntegrationContract",
    "MemoryIntegrationContract",
    "MonitoringIntegrationContract",
    "PolicyIntegrationContract",
    "SecurityIntegrationContract",
    "CommunicationIntegrationContract",
)