# Compensation Contracts Module
# =============================

"""
Compensation contracts and compensating transaction support for Phase 3.7.10.

This module provides:
    - Compensation contract definitions for rollback operations
    - Compensating transaction patterns for irreversible actions
    - State restoration contracts with validation
    
Key concepts:
    - Every action that can fail needs a compensation (rollback) path
    - Compensation must be idempotent and safe to execute multiple times
    - Compensation should restore system to a known-good state
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Awaitable, Any


# =============================================================================
# Compensation Contract Types
# =============================================================================

@dataclass(frozen=True)
class CompensationContract:
    """
    A contract defining how to compensate for a specific action type.
    
    Args:
        action_type: What type of action this is for (e.g., "CREATE_ENTITY")
        
        compensation_action: The compensating action to execute
        pre_conditions: Conditions that must be true before compensation
        post_conditions: Conditions that must be true after compensation
        
        idempotent: Whether compensation can be safely retried
        timeout_seconds: Maximum time allowed for compensation
    """
    
    contract_id: str
    
    action_type: str
    
    compensation_action: "CompensationAction"
    pre_conditions: List["Condition"] = field(default_factory=list)
    post_conditions: List["Condition"] = field(default_factory=list)
    
    idempotent: bool = True
    timeout_seconds: Optional[float] = None


@dataclass(frozen=True)
class CompensationAction:
    """
    A specific compensating action to execute.
    
    Args:
        action_id: Unique identifier for this action
        
        action_type: Type of compensation (RESTORE, DELETE, REVERT)
        
        target_entity: Entity to apply compensation to
        parameters: Additional parameters for the action
        
        retry_policy: How to retry on failure
    """
    
    action_id: str
    
    action_type: "CompensationType"
    
    target_entity: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    retry_policy: "RetryPolicy" = field(
        default_factory=lambda: RetryPolicy(max_attempts=3, initial_delay_seconds=1.0)
    )


class CompensationType(Enum):
    """Types of compensation actions."""
    
    RESTORE = "restore"            # Restore previous state
    DELETE = "delete"              # Delete the created/modified entity
    REVERT = "revert"              # Revert to a specific version
    COMPENSATE = "compensate"      # Apply compensating action (not exact rollback)
    CANCEL = "cancel"              # Cancel pending operation


# RetryPolicy - Import from canonical execution location
from ..execution import RetryPolicy as _RetryPolicy

# Alias for backward compatibility during transition period
RetryPolicy = _RetryPolicy


# =============================================================================
# Condition Types for Contracts
# =============================================================================

@dataclass(frozen=True)
class Condition:
    """
    A condition that must be satisfied.
    
    Args:
        condition_id: Unique identifier
        
        condition_type: Type of condition (STATE, ENTITY, VERIFIED)
        
        target_entity: Entity to check
        expected_value: Expected state/value
        
        negate: Whether to invert the condition
    """
    
    condition_id: str
    
    condition_type: "ConditionType"
    
    target_entity: Optional[str] = None
    expected_value: Optional[Any] = None
    
    negate: bool = False


class ConditionType(Enum):
    """Types of conditions."""
    
    STATE = "state"               # Entity is in specific state
    ENTITY_EXISTS = "entity_exists"   # Entity must exist (or not)
    VERIFIED = "verified"         # External verification passed
    TIMEOUT_PASSED = "timeout_passed"  # Time since action has passed


# =============================================================================
# State Restoration Contract
# =============================================================================

@dataclass(frozen=True)
class StateRestoreContract:
    """
    A contract for state restoration with validation.
    
    Args:
        restore_id: Unique identifier
        
        target_state_version: State version to restore to
        entities_to_restore: Which entities are affected
        
        verification_required: Whether verification must pass
        timeout_seconds: Maximum time for restoration
        
        on_failure_action: What to do if restoration fails
    """
    
    restore_id: str
    
    target_state_version: int
    entities_to_restore: List[str]
    
    verification_required: bool = True
    timeout_seconds: Optional[float] = None
    
    on_failure_action: "FailureAction" = field(
        default_factory=lambda: FailureAction(escalate=True)
    )


@dataclass(frozen=True)
class FailureAction:
    """
    Action to take if restoration fails.
    
    Args:
        escalate: Whether to escalate to higher authority
        fallback_state: Fallback state if available
        
        notify_on_failure: Who should be notified
    """
    
    escalate: bool = True
    fallback_state: Optional[str] = None
    notify_on_failure: List[str] = field(default_factory=list)


# =============================================================================
# Compensating Transaction
# =============================================================================

@dataclass(frozen=True)
class CompensatingTransaction:
    """
    A transaction with compensating actions for rollback.
    
    Args:
        transaction_id: Unique identifier
        
        actions: Actions in the transaction (in order)
        compensations: Compensating actions (in reverse order)
        
        state_snapshot_before: State before transaction
        state_snapshot_after: State after all actions complete
        
        timeout_seconds: Maximum time for transaction
    """
    
    transaction_id: str
    
    actions: List["TransactionAction"]
    compensations: List[CompensationAction]
    
    state_snapshot_before: Optional[str] = None
    state_snapshot_after: Optional[str] = None
    
    timeout_seconds: Optional[float] = None


@dataclass(frozen=True)
class TransactionAction:
    """
    A single action in a transaction.
    
    Args:
        action_id: Unique identifier
        
        action_type: Type of action
        target_entity: Entity to act on
        
        compensation_action: Compensating action for this
    """
    
    # Required fields first (no defaults)
    action_id: str
    
    # Optional fields with defaults (for dataclass field ordering)
    action_type: str = "unknown"
    target_entity: Optional[str] = None
    compensation_action: Optional[CompensationAction] = None


# =============================================================================
# Compensation Coordinator
# =============================================================================

class CompensationCoordinator:
    """
    Coordinates compensation actions for rollback and recovery.
    
    This is the canonical authority for compensation planning and execution.
    """
    
    def __init__(self) -> None:
        """Initialize the coordinator."""
        self._contracts: Dict[str, CompensationContract] = {}
        self._transactions: Dict[str, CompensatingTransaction] = {}
        
        self._action_handlers: Dict[str, Callable[[CompensationAction], Awaitable[bool]]] = {}
    
    def register_contract(
        self,
        contract: CompensationContract
    ) -> None:
        """Register a compensation contract."""
        self._contracts[contract.contract_id] = contract
    
    def register_action_handler(
        self,
        action_type: str,
        handler: Callable[[CompensationAction], Awaitable[bool]]
    ) -> None:
        """Register a handler for a specific action type."""
        self._action_handlers[action_type] = handler
    
    async def execute_compensation(
        self,
        compensation: CompensationAction
    ) -> bool:
        """
        Execute a compensation action.
        
        Args:
            compensation: The compensation to execute
            
        Returns:
            True if compensation succeeded, False otherwise
        """
        handler = self._action_handlers.get(compensation.action_type.value)
        
        if handler is None:
            return False
        
        try:
            result = await handler(compensation)
            
            if not result and compensation.retry_policy.max_attempts > 1:
                # Retry according to policy
                for _ in range(1, compensation.retry_policy.max_attempts):
                    import asyncio
                    await asyncio.sleep(
                        min(
                            compensation.retry_policy.backoff_seconds,
                            compensation.retry_policy.max_backoff_seconds
                        )
                    )
                    
                    result = await handler(compensation)
                    if result:
                        break
            
            return result
        except Exception:
            return False
    
    async def plan_compensation_for_transaction(
        self,
        transaction: CompensatingTransaction
    ) -> List[CompensationAction]:
        """
        Plan compensation actions for a transaction.
        
        Args:
            transaction: The transaction to create compensation for
            
        Returns:
            Ordered list of compensation actions (in reverse order)
        """
        return list(reversed(transaction.compensations))
    
    def get_compensation_contract(
        self,
        action_type: str
    ) -> Optional[CompensationContract]:
        """Get the contract for a specific action type."""
        for contract in self._contracts.values():
            if contract.action_type == action_type:
                return contract
        return None


# =============================================================================
# Compensation utilities
# =============================================================================

def build_compensating_transaction(
    transaction_id: str,
    actions: List[TransactionAction],
    timeout_seconds: Optional[float] = None
) -> CompensatingTransaction:
    """
    Build a compensating transaction from regular actions.
    
    Each action must have its compensation defined. The transaction
    will have all compensations in reverse order for rollback.
    
    Args:
        transaction_id: ID for the transaction
        actions: Regular actions to include
        timeout_seconds: Maximum time allowed
        
    Returns:
        CompensatingTransaction with all components
    """
    # Create compensations for each action (in reverse)
    compensations = [
        action.compensation_action
        for action in reversed(actions)
    ]
    
    return CompensatingTransaction(
        transaction_id=transaction_id,
        actions=list(actions),
        compensations=compensations,
        timeout_seconds=timeout_seconds
    )


def validate_compensation_plan(
    plan: List[CompensationAction],
    current_state: Dict[str, Any]
) -> bool:
    """
    Validate that a compensation plan is valid for current state.
    
    Args:
        plan: List of compensations to execute
        current_state: Current system state
        
    Returns:
        True if plan can be executed safely
    """
    # Check pre-conditions for each action
    for action in plan:
        if not _check_pre_conditions(action, current_state):
            return False
    
    return True


def _check_pre_conditions(
    action: CompensationAction,
    state: Dict[str, Any]
) -> bool:
    """Check if pre-conditions are satisfied."""
    # For now, assume all pre-conditions pass
    # In production, this would check specific conditions
    return True