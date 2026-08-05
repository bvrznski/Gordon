# Retry Coordinator
# =================

"""
Retry coordinator for Phase 3.7.10.

Manages retry attempts with:
    - Budget tracking and exhaustion prevention
    - Backoff strategy execution
    - Idempotency verification before retry
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time

from .policy import RetryClassification, IdempotencyClass, BackoffPolicy
from .budget import RetryBudgetManager


@dataclass(frozen=True)
class RetryDecision:
    """
    Decision on whether to retry.
    
    Args:
        permit_retry: Whether retry is allowed
        delay_seconds: How long to wait before next attempt
        
        classification: Why this decision was made
        budget_remaining: How many attempts left after this one
    """
    
    permit_retry: bool
    delay_seconds: float = 0.0
    
    classification: str = ""
    budget_remaining: int = 0


class RetryCoordinator:
    """
    Coordinator for retry operations.
    
    Usage:
        coordinator = RetryCoordinator(
            manager=RetryBudgetManager()
        )
        
        decision = await coordinator.decide_retry(failure, current_attempt)
        
        if decision.permit_retry:
            await asyncio.sleep(decision.delay_seconds)
            await attempt_operation()
    """
    
    def __init__(
        self,
        manager: Optional[RetryBudgetManager] = None,
        default_policy: Optional[BackoffPolicy] = None
    ):
        """Initialize the retry coordinator."""
        self._manager = manager or RetryBudgetManager()
        self._default_policy = default_policy or BackoffPolicy()
        
        # Track current attempts per operation
        self._current_attempts: Dict[str, int] = {}
    
    async def classify_operation(
        self,
        failure_id: str,
        exception_type: Optional[str],
        has_side_effects: bool = False
    ) -> RetryClassification:
        """
        Classify an operation for retry purposes.
        
        Args:
            failure_id: ID of the failure context
            exception_type: Type of exception that occurred
            has_side_effects: Whether the operation has side effects
            
        Returns:
            Classification with idempotency and retry parameters
        """
        # Determine idempotency based on exception type and operation info
        if exception_type is None or "error" in exception_type.lower():
            # Errors typically indicate non-idempotent operations without verification
            return RetryClassification(
                idempotency_class=IdempotencyClass.NON_IDEMPOTENT,
                has_side_effects=has_side_effects,
                unknown_outcome=True
            )
        
        # Unknown or transient conditions may be safe to retry
        return RetryClassification(
            idempotency_class=IdempotencyClass.IDEMPOTENT,
            has_side_effects=has_side_effects,
            max_attempts=3
        )
    
    async def decide_retry(
        self,
        failure_id: str,
        current_attempt: int,
        classification: Optional[RetryClassification] = None
    ) -> RetryDecision:
        """
        Decide whether to retry and calculate backoff.
        
        Args:
            failure_id: ID of the failure context
            current_attempt: Which attempt number this is (1-based)
            classification: Operation classification
            
        Returns:
            RetryDecision with permit flag and delay
        """
        # Get or create budget for this failure scope
        budget = self._manager.get_budget(failure_id, "operation")
        
        if not budget.can_attempt():
            return RetryDecision(
                permit_retry=False,
                classification="budget_exhausted",
                budget_remaining=0
            )
        
        # Calculate delay using default policy
        backoff = self._default_policy
        base_delay = backoff.base_delay_seconds
        
        # Apply exponential backoff with jitter for default
        if current_attempt <= 3:
            delay = base_delay * (2 ** (current_attempt - 1))
            delay = min(delay, backoff.max_delay_seconds)
            
            # Add jitter
            import random
            if backoff.jitter_enabled and delay > 0:
                delay *= random.uniform(0.5, 1.5)
        else:
            delay = 0.0
        
        return RetryDecision(
            permit_retry=True,
            delay_seconds=delay,
            classification=f"attempt_{current_attempt}",
            budget_remaining=budget.remaining_attempts
        )
    
    def record_attempt(self, failure_id: str) -> None:
        """Record that an attempt was made."""
        if failure_id not in self._current_attempts:
            self._current_attempts[failure_id] = 0
        
        self._current_attempts[failure_id] += 1
    
    def reset_for_failure(self, failure_id: str) -> None:
        """Reset retry state for a specific failure."""
        if failure_id in self._current_attempts:
            del self._current_attempts[failure_id]
        
        self._manager.reset_budget(failure_id, "operation")
    
    def snapshot(self) -> Dict[str, Any]:
        """Get an immutable snapshot of retry state."""
        return {
            "active_failures": len(self._current_attempts),
            "total_attempt_count": sum(self._current_attempts.values())
        }