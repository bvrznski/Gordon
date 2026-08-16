# Executive Network Contracts Package
# ====================================

"""
Executive Network contract definitions for Phase 4.4.1.

This package contains the canonical contracts that define the interface
between the Executive Network and other systems.
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
# CONTRACT: EXECUTIVE NETWORK
# =============================================================================


class ExecutiveNetworkContract(Protocol):
    """
    Protocol defining the Executive Network interface.
    
    This is the authoritative contract for all ExecutiveNetwork implementations.
    """
    
    @property
    def network_id(self) -> ExecutiveNetworkId:
        """Unique identifier for this Network instance."""
        ...
    
    def evaluate(
        self,
        context: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], "ExecutiveContinuationKind"]:
        """
        Evaluate the current executive state and produce products.
        
        Args:
            context: External context projections (immutable)
            
        Returns:
            Tuple of (products dict, continuation recommendation)
        """
        ...
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current executive state."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE STATE
# =============================================================================


class ExecutiveStateContract(Protocol):
    """
    Protocol for executive state operations.
    
    Defines how external systems can query and interact with
    executive state without directly accessing implementation details.
    """
    
    @property
    def state_id(self) -> ExecutiveStateReference:
        """Unique identifier for this state."""
        ...
    
    @property
    def revision(self) -> int:
        """Current revision number."""
        ...
    
    @property
    def active_task_set(self) -> Optional[ExecutiveTaskSetReference]:
        """Reference to the currently active task set."""
        ...
    
    def get_active_goals(self) -> Tuple[str, ...]:
        """Get IDs of currently active goals."""
        ...
    
    def get_active_commitments(self) -> Tuple[str, ...]:
        """Get IDs of currently active commitments."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE CONTEXT
# =============================================================================


class ExecutiveContextContract(Protocol):
    """
    Protocol for executive context information.
    
    Context is the external environment in which the Executive
    network operates - not owned by the Executive, but consumed.
    """
    
    @property
    def context_id(self) -> ExecutiveContextReference:
        """Unique identifier for this context."""
        ...
    
    @property
    def timestamp_utc(self) -> float:
        """When this context was captured."""
        ...
    
    @property
    def active_thread_id(self) -> Optional[str]:
        """ID of the currently active ExecutionThread."""
        ...
    
    @property
    def execution_cycle_info(self) -> Dict[str, Any]:
        """Information about the current execution cycle."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE TASK SET
# =============================================================================


class ExecutiveTaskSetContract(Protocol):
    """
    Protocol for executive task set operations.
    
    A task set is a collection of related goals, rules, and constraints
    that define an executive program.
    """
    
    @property
    def task_set_id(self) -> ExecutiveTaskSetReference:
        """Unique identifier for this task set."""
        ...
    
    @property
    def active_objective(self) -> Optional[str]:
        """The primary objective of this task set."""
        ...
    
    @property
    def applicable_rules(self) -> Tuple[str, ...]:
        """Rules that apply to this task set."""
        ...
    
    @property
    def constraints(self) -> Tuple[str, ...]:
        """Constraints that must be satisfied."""
        ...
    
    @property
    def active_strategy(self) -> Optional[str]:
        """The current strategy being applied."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE REQUEST
# =============================================================================


class ExecutiveRequestContract(Protocol):
    """
    Protocol for executive requests.
    
    Requests are external inputs that ask the Executive to perform
    some evaluation or computation.
    """
    
    @property
    def request_id(self) -> ExecutiveRequestReference:
        """Unique identifier for this request."""
        ...
    
    @property
    def request_kind(self) -> str:
        """Kind of request (e.g., 'evaluate_state', 'request_continuation')."""
        ...
    
    @property
    def timestamp_utc(self) -> float:
        """When the request was created."""
        ...
    
    def get_payload(self) -> Dict[str, Any]:
        """Get the request payload."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE RESULT
# =============================================================================


class ExecutiveResultContract(Protocol):
    """
    Protocol for executive results.
    
    Results are the outputs of executive evaluation.
    """
    
    @property
    def result_id(self) -> ExecutiveResultReference:
        """Unique identifier for this result."""
        ...
    
    @property
    def request_id(self) -> Optional[ExecutiveRequestReference]:
        """ID of the request this result responds to (if any)."""
        ...
    
    @property
    def products(self) -> Tuple[str, ...]:
        """Product IDs produced by this result."""
        ...
    
    @property
    def continuation_kind(self) -> str:
        """Recommended continuation behavior."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE PRODUCT
# =============================================================================


class ExecutiveProductContract(Protocol):
    """
    Protocol for executive products.
    
    Products are the semantic outputs of executive evaluation - proposals,
    assessments, and recommendations.
    """
    
    @property
    def product_id(self) -> ExecutiveProductReference:
        """Unique identifier for this product."""
        ...
    
    @property
    def product_kind(self) -> str:
        """Kind of product (e.g., 'task_set_proposal', 'conflict_assessment')."""
        ...
    
    @property
    def content(self) -> Dict[str, Any]:
        """Product content."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE PROPOSAL
# =============================================================================


class ExecutiveProposalContract(Protocol):
    """
    Protocol for executive proposals.
    
    Proposals are suggestions that downstream systems may accept or reject.
    They are NOT binding commands.
    """
    
    @property
    def proposal_id(self) -> ExecutiveProposalReference:
        """Unique identifier for this proposal."""
        ...
    
    @property
    def proposal_kind(self) -> str:
        """Kind of proposal (e.g., 'task_set_activation')."""
        ...
    
    @property
    def target_system(self) -> str:
        """System that should act on this proposal."""
        ...
    
    @property
    def recommended_action(self) -> Dict[str, Any]:
        """Recommended action for the target system."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE OUTCOME
# =============================================================================


class ExecutiveOutcomeContract(Protocol):
    """
    Protocol for executive outcomes.
    
    Outcomes represent terminal results of executive evaluation.
    """
    
    @property
    def outcome_id(self) -> ExecutiveOutcomeReference:
        """Unique identifier for this outcome."""
        ...
    
    @property
    def outcome_kind(self) -> str:
        """Kind of outcome (e.g., 'task_set_established', 'conflict_identified')."""
        ...
    
    @property
    def timestamp_utc(self) -> float:
        """When the outcome was produced."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE CONTINUATION
# =============================================================================


class ExecutiveContinuationContract(Protocol):
    """
    Protocol for executive continuation recommendations.
    
    Continuations are advisory - downstream systems decide whether to apply them.
    """
    
    @property
    def continuation_id(self) -> ExecutiveContinuationReference:
        """Unique identifier for this continuation."""
        ...
    
    @property
    def continuation_kind(self) -> str:
        """Kind of continuation (e.g., 'continue_assessment', 'wait_for_result')."""
        ...
    
    @property
    def justification(self) -> Tuple[str, ...]:
        """Reasoning behind this continuation recommendation."""
        ...


# =============================================================================
# CONTRACT: EXECUTIVE AUTHORITY
# =============================================================================


class ExecutiveAuthorityContract(Protocol):
    """
    Protocol for executive authority information.
    
    Authority is external to the Executive Network - it determines
    whether proposals should be applied.
    """
    
    @property
    def authority_id(self) -> ExecutiveAuthorityReference:
        """Unique identifier for this authority."""
        ...
    
    @property
    def can_accept_proposals(self) -> bool:
        """Whether this authority may accept executive proposals."""
        ...
    
    @property
    def can_reject_proposals(self) -> bool:
        """Whether this authority may reject executive proposals."""
        ...
    
    @property
    def decision_history(self) -> Tuple[str, ...]:
        """History of decisions made by this authority."""
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
    
    # Contract protocols
    "ExecutiveNetworkContract",
    "ExecutiveStateContract",
    "ExecutiveContextContract",
    "ExecutiveTaskSetContract",
    "ExecutiveRequestContract",
    "ExecutiveResultContract",
    "ExecutiveProductContract",
    "ExecutiveProposalContract",
    "ExecutiveOutcomeContract",
    "ExecutiveContinuationContract",
    "ExecutiveAuthorityContract",
)