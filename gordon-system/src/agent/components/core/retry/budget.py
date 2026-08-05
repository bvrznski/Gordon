# Retry Budget
# ============

"""
Retry budget management for Phase 3.7.10.

Budgets prevent:
    - Endless retry loops
    - Retry storms that overwhelm systems
    - Unbounded resource consumption during failures

Each budget defines limits by scope (operation, task, service, component).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time


@dataclass(frozen=True)
class RetryBudget:
    """
    A retry budget for a specific scope.
    
    Args:
        budget_id: Unique identifier
        
        scope: What this budget limits (operation, task, service, component, etc.)
        
        max_attempts: Maximum attempts allowed
        consumed_attempts: How many have been used
        remaining_attempts: How many are left
        
        window_seconds: Time window for counting attempts
        
        last_reset_at: When the budget was last reset
    """
    
    budget_id: str
    
    scope: str  # operation, task, service, component
    
    max_attempts: int = 3
    consumed_attempts: int = 0
    
    window_seconds: float = 60.0
    
    first_attempt_at: Optional[float] = None
    last_attempt_at: Optional[float] = None
    
    @property
    def remaining_attempts(self) -> int:
        """Calculate remaining attempts."""
        return max(0, self.max_attempts - self.consumed_attempts)
    
    @property
    def exhausted(self) -> bool:
        """Check if budget is exhausted."""
        return self.remaining_attempts <= 0
    
    def can_attempt(self, now: Optional[float] = None) -> bool:
        """
        Check if an attempt is allowed within this budget.
        
        Args:
            now: Current time (uses monotonic time if not provided)
            
        Returns:
            True if attempt is permitted
        """
        current_time = now or time.monotonic()
        
        # Clean old attempts outside the window
        if self.first_attempt_at is not None:
            window_start = current_time - self.window_seconds
            if self.first_attempt_at < window_start:
                # Reset window (simplified)
                self.consumed_attempts = 0
                self.first_attempt_at = current_time
        
        # Check budget exhaustion
        if self.exhausted:
            return False
        
        return True
    
    def consume_attempt(self, now: Optional[float] = None) -> None:
        """Record that an attempt was made."""
        current_time = now or time.monotonic()
        
        self.consumed_attempts += 1
        
        if self.first_attempt_at is None:
            self.first_attempt_at = current_time
        
        self.last_attempt_at = current_time


@dataclass
class RetryBudgetManager:
    """
    Manage retry budgets across different scopes.
    
    Provides:
        - Budget lookup by scope
        - Global budget limits
        - Budget reset on recovery
    
    Usage:
        manager = RetryBudgetManager()
        
        # Get budget for a task
        budget = manager.get_budget("task_123", "task")
        
        if budget.can_attempt():
            await attempt_retry()
            budget.consume_attempt()
    """
    
    _budgets: Dict[str, RetryBudget] = field(default_factory=dict)
    _global_max_attempts: int = 10
    _window_seconds: float = 60.0
    
    def get_budget(self, scope_id: str, scope_type: str) -> RetryBudget:
        """
        Get or create a budget for the given scope.
        
        Args:
            scope_id: Unique identifier for the scope (e.g., task ID)
            scope_type: Type of scope (operation, task, service, component)
            
        Returns:
            The retry budget for this scope
        """
        key = f"{scope_type}:{scope_id}"
        
        if key not in self._budgets:
            self._budgets[key] = RetryBudget(
                budget_id=key,
                scope=scope_type,
                max_attempts=min(3, self._global_max_attempts),
                window_seconds=self._window_seconds
            )
        
        return self._budgets[key]
    
    def consume_global_attempt(self) -> bool:
        """Consume a global attempt. Returns False if exhausted."""
        # Simplified - would track global counter
        return True
    
    def reset_budget(self, scope_id: str, scope_type: str) -> None:
        """Reset budget for a specific scope."""
        key = f"{scope_type}:{scope_id}"
        if key in self._budgets:
            del self._budgets[key]
    
    def snapshot(self) -> Dict[str, Any]:
        """Get an immutable snapshot of budget state."""
        return {
            "total_budgets": len(self._budgets),
            "global_max_attempts": self._global_max_attempts,
        }