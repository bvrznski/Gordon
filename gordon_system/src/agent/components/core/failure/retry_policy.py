# Retry Policy Module
# ===================

"""
Retry policy authority for Phase 3.7.10 failure recovery.

This module implements:

- Bounded retry budgets per failure
- Exponential backoff strategies with jitter
- Idempotency validation before retry
- Retry exhaustion tracking
- Storm prevention across multiple failures

Key principles:
    - One canonical retry-policy authority
    - Budgets are bounded (no unlimited retries)
    - Backoff is deterministic under test
    - Non-idempotent operations rejected without protection
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import time
import random


# =============================================================================
# Retry Budget Configuration
# =============================================================================

@dataclass(frozen=True)
class RetryBudget:
    """
    Budget configuration for retry operations.
    
    Args:
        budget_id: Unique identifier for this budget
        max_attempts: Maximum retry attempts allowed
        total_duration_seconds: Total time budget for retries
        per_attempt_timeout_seconds: Timeout per retry attempt
        
        backoff_base_seconds: Base delay for exponential backoff
        backoff_max_seconds: Maximum delay cap
        jitter_enabled: Whether to add randomness to delays
        
        scope: Entities affected (for scoped budgets)
    """
    
    budget_id: str
    
    max_attempts: int = 3
    total_duration_seconds: float = 120.0
    per_attempt_timeout_seconds: Optional[float] = None
    
    backoff_base_seconds: float = 1.0
    backoff_max_seconds: float = 60.0
    jitter_enabled: bool = True
    
    scope: List[str] = field(default_factory=list)


class RetryBudgetExhausted(Exception):
    """Raised when retry budget is exhausted."""
    
    def __init__(self, budget_id: str, attempts_used: int, max_attempts: int):
        self.budget_id = budget_id
        self.attempts_used = attempts_used
        self.max_attempts = max_attempts
        super().__init__(
            f"Retry budget {budget_id} exhausted: "
            f"{attempts_used}/{max_attempts} attempts"
        )


# =============================================================================
# Backoff Strategy
# =============================================================================

class BackoffStrategy(Enum):
    """Backoff strategies for retry delays."""
    
    CONSTANT = "constant"              # Fixed delay each time
    LINEAR = "linear"                  # Linear increase: base, 2*base, 3*base...
    EXPONENTIAL = "exponential"        # Exponential: base, 2*base, 4*base...
    CAPPED_EXPONENTIAL = "capped_expontial"  # Exponential with max cap
    POLICY_DEFINED = "policy_defined"  # Use policy-specified formula


@dataclass(frozen=True)
class BackoffResult:
    """
    Result of a backoff calculation.
    
    Args:
        delay_seconds: How long to wait before retrying
        attempt_number: Which retry this will be (1-indexed)
        strategy_used: Which backoff strategy was applied
    """
    
    delay_seconds: float
    attempt_number: int
    strategy_used: BackoffStrategy


class RetryBackoffCalculator:
    """
    Calculates retry delays using various backoff strategies.
    
    Under test, jitter can be disabled for deterministic results.
    """
    
    def __init__(
        self,
        base_seconds: float = 1.0,
        max_seconds: float = 60.0,
        strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    ):
        """
        Initialize the backoff calculator.
        
        Args:
            base_seconds: Base delay for calculations
            max_seconds: Maximum delay cap
            strategy: Which backoff strategy to use
        """
        self._base = base_seconds
        self._max = max_seconds
        self._strategy = strategy
    
    def calculate_delay(
        self,
        attempt_number: int,
        jitter_enabled: bool = True,
        random_provider: Optional[Any] = None
    ) -> BackoffResult:
        """
        Calculate the delay for a given attempt number.
        
        Args:
            attempt_number: Which retry this is (1-indexed)
            jitter_enabled: Whether to add randomness
            random_provider: Optional random provider for deterministic tests
            
        Returns:
            BackoffResult with delay and metadata
        """
        actual_random = random_provider or random
        
        if self._strategy == BackoffStrategy.CONSTANT:
            base_delay = self._base
        elif self._strategy == BackoffStrategy.LINEAR:
            base_delay = self._base * attempt_number
        elif self._strategy in (BackoffStrategy.EXPONENTIAL, 
                                 BackoffStrategy.CAPPED_EXPONENTIAL):
            base_delay = self._base * (2 ** (attempt_number - 1))
        else:  # POLICY_DEFINED or unknown
            base_delay = self._base
        
        # Apply max cap
        capped_delay = min(base_delay, self._max)
        
        # Add jitter if enabled and not in test mode with fixed random
        delay = capped_delay
        if jitter_enabled:
            # Jitter: add up to 50% randomness
            jitter_range = delay * 0.5
            delay = delay + actual_random.uniform(-jitter_range, jitter_range)
        
        return BackoffResult(
            delay_seconds=max(0.0, delay),
            attempt_number=attempt_number,
            strategy_used=self._strategy
        )


# =============================================================================
# Idempotency Validation
# =============================================================================

class RetryIdempotency(Enum):
    """
    Idempotency status of an operation.
    
    Determines whether retry is safe without additional protection.
    """
    
    IDEMPOTENT = "idempotent"              # Safe to retry directly
    IDEMPOTENT_WITH_KEY = "idempotent_with_key"  # Safe with deduplication key
    COMPENSATABLE = "compensatable"        # Can use compensation protocol
    NON_IDEMPOTENT = "non_idempotent"      # Requires protection before retry
    UNKNOWN = "unknown"                    # Cannot determine safely


@dataclass(frozen=True)
class IdempotencyValidation:
    """
    Result of idempotency validation.
    
    Args:
        status: IDEMPOTENT, COMPENSATABLE, or NON_IDEMPOTENT
        requires_compensation: Whether compensation is required
        deduplication_key: Key for deduplication (if applicable)
        protection_required: Additional protection needed
    """
    
    status: RetryIdempotency
    requires_compensation: bool = False
    deduplication_key: Optional[str] = None
    protection_required: Optional[str] = None


class IdempotencyValidator:
    """
    Validates whether operations are safe to retry.
    """
    
    def __init__(self) -> None:
        """Initialize the validator."""
        self._known_idempotent_patterns: Dict[str, RetryIdempotency] = {
            "get": RetryIdempotency.IDEMPOTENT,
            "read": RetryIdempotency.IDEMPOTENT,
            "fetch": RetryIdempotency.IDEMPOTENT,
            "query": RetryIdempotency.IDEMPOTENT,
            "select": RetryIdempotency.IDEMPOTENT,
        }
    
    def validate_operation(
        self,
        operation_type: str,
        operation_data: Optional[Dict[str, Any]] = None
    ) -> IdempotencyValidation:
        """
        Validate whether an operation is safe to retry.
        
        Args:
            operation_type: Type of operation (e.g., "create", "update", "delete")
            operation_data: Additional operation context
            
        Returns:
            IdempotencyValidation result
        """
        op_lower = operation_type.lower()
        
        # Check known patterns
        for pattern, status in self._known_idempotent_patterns.items():
            if pattern in op_lower:
                return IdempotencyValidation(status=status)
        
        # Default: unknown without context
        return IdempotencyValidation(
            status=RetryIdempotency.UNKNOWN,
            protection_required="deduplication_or_compensation"
        )


# =============================================================================
# Retry Budget Manager
# =============================================================================

@dataclass(frozen=True)
class RetryBudgetState:
    """
    Current state of a retry budget.
    
    Args:
        budget_id: Which budget this tracks
        attempts_remaining: How many retries left
        duration_remaining_seconds: Time remaining in budget
        
        last_retry_at: When the last retry occurred
        first_retry_at: When the first retry occurred
        
        is_exhausted: Whether budget is exhausted
    """
    
    budget_id: str
    
    attempts_remaining: int
    duration_remaining_seconds: float
    
    last_retry_at: Optional[float] = None
    first_retry_at: Optional[float] = None
    
    is_exhausted: bool = False


class RetryBudgetManager:
    """
    Manages retry budgets per failure or operation.
    
    Ensures retries are bounded and prevents exhaustion.
    """
    
    def __init__(
        self,
        default_budget: Optional[RetryBudget] = None
    ):
        """Initialize the budget manager."""
        self._default_budget = default_budget or RetryBudget(
            budget_id="default",
            max_attempts=3,
            total_duration_seconds=120.0
        )
        
        # Per-budget state: budget_id -> BudgetState
        self._budget_states: Dict[str, RetryBudgetState] = {}
        self._retry_counts: Dict[str, int] = {}  # budget_id -> attempt count
    
    def get_or_create_budget(self, budget_id: str) -> RetryBudget:
        """Get or create a retry budget by ID."""
        if budget_id in self._budget_states:
            state = self._budget_states[budget_id]
            return RetryBudget(
                budget_id=budget_id,
                max_attempts=state.attempts_remaining + (self._retry_counts.get(budget_id, 0)),
                total_duration_seconds=max(0.0, state.duration_remaining_seconds),
                scope=state.last_retry_at and [budget_id] or []
            )
        return self._default_budget
    
    def acquire_retry(
        self,
        budget_id: str,
        current_time: Optional[float] = None
    ) -> Tuple[bool, RetryBudgetState]:
        """
        Try to acquire a retry slot from the budget.
        
        Args:
            budget_id: Which budget to use
            current_time: Current timestamp (None = now)
            
        Returns:
            Tuple of (acquired, state_after_attempt)
        """
        if budget_id not in self._budget_states:
            # Initialize with default budget
            default_state = RetryBudgetState(
                budget_id=budget_id,
                attempts_remaining=self._default_budget.max_attempts,
                duration_remaining_seconds=self._default_budget.total_duration_seconds,
                first_retry_at=None,
                last_retry_at=None,
                is_exhausted=False
            )
            self._budget_states[budget_id] = default_state
        
        state = self._budget_states[budget_id]
        
        if state.is_exhausted:
            return False, state
        
        now = current_time or time.time()
        
        # Check duration budget
        elapsed = (now - state.first_retry_at) if state.first_retry_at else 0.0
        remaining_duration = self._default_budget.total_duration_seconds - elapsed
        
        if remaining_duration <= 0:
            exhausted_state = replace(state, is_exhausted=True)
            self._budget_states[budget_id] = exhausted_state
            return False, exhausted_state
        
        # Check attempt budget
        if state.attempts_remaining <= 0:
            exhausted_state = replace(state, is_exhausted=True)
            self._budget_states[budget_id] = exhausted_state
            return False, exhausted_state
        
        # Acquire the retry slot
        new_attempts = max(0, state.attempts_remaining - 1)
        
        if budget_id not in self._retry_counts:
            self._retry_counts[budget_id] = 0
        self._retry_counts[budget_id] += 1
        
        new_state = RetryBudgetState(
            budget_id=budget_id,
            attempts_remaining=new_attempts,
            duration_remaining_seconds=remaining_duration,
            first_retry_at=state.first_retry_at or now,
            last_retry_at=now,
            is_exhausted=(new_attempts == 0)
        )
        
        self._budget_states[budget_id] = new_state
        return True, new_state
    
    def release_budget(self, budget_id: str) -> bool:
        """Release a retry budget (e.g., on success)."""
        if budget_id in self._budget_states:
            del self._budget_states[budget_id]
        if budget_id in self._retry_counts:
            del self._retry_counts[budget_id]
        return True
    
    def get_budget_state(self, budget_id: str) -> Optional[RetryBudgetState]:
        """Get the current state of a budget."""
        return self._budget_states.get(budget_id)


# =============================================================================
# Retry Policy Authority
# =============================================================================

@dataclass(frozen=True)
class RetryPolicy:
    """
    Complete retry policy for an operation.
    
    Args:
        policy_id: Unique identifier
        max_attempts: Maximum retry attempts
        backoff_strategy: Which backoff strategy to use
        
        idempotency_required: Whether idempotency must be validated
        compensation_required: Compensation protocol required for non-idempotent
        
        stateless: Whether operation is stateless (no side effects)
    """
    
    policy_id: str
    
    max_attempts: int = 3
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    
    idempotency_required: bool = True
    compensation_required: Optional[str] = None
    
    stateless: bool = False


class RetryPolicyManager:
    """
    Canonical retry-policy authority for Phase 3.7.10.
    
    This is the single canonical authority for all retry decisions:
        - Budget validation before retry
        - Backoff calculation with jitter support
        - Idempotency validation
        - Storm prevention across failures
    """
    
    def __init__(
        self,
        default_budget: Optional[RetryBudget] = None
    ):
        """Initialize the policy manager."""
        self._budget_manager = RetryBudgetManager(default_budget)
        self._backoff_calculator = RetryBackoffCalculator()
        self._idempotency_validator = IdempotencyValidator()
        
        # Global storm prevention
        self._retry_counts: Dict[str, int] = {}  # operation_id -> count
        self._last_retries: Dict[str, float] = {}  # operation_id -> timestamp
    
    def can_retry(
        self,
        policy: RetryPolicy,
        budget_id: str,
        current_time: Optional[float] = None
    ) -> Tuple[bool, List[str]]:
        """
        Check if retry is allowed under the policy.
        
        Args:
            policy: The retry policy to check against
            budget_id: Which budget to use
            current_time: Current timestamp (None = now)
            
        Returns:
            Tuple of (can_retry, list_of_reasons_if_not)
        """
        reasons = []
        
        # Check budget
        can_acquire, _ = self._budget_manager.acquire_retry(budget_id, current_time)
        if not can_acquire:
            reasons.append("retry_budget_exhausted")
        
        return len(reasons) == 0, reasons
    
    def calculate_backoff(
        self,
        policy: RetryPolicy,
        attempt_number: int,
        jitter_enabled: Optional[bool] = None
    ) -> BackoffResult:
        """
        Calculate the backoff delay for a retry attempt.
        
        Args:
            policy: The retry policy (provides strategy)
            attempt_number: Which retry this is (1-indexed)
            jitter_enabled: Whether to add jitter (None = use policy default)
            
        Returns:
            BackoffResult with calculated delay
        """
        actual_jitter = (
            jitter_enabled 
            if jitter_enabled is not None 
            else policy.backoff_strategy != BackoffStrategy.CONSTANT
        )
        
        self._backoff_calculator._strategy = policy.backoff_strategy
        
        return self._backoff_calculator.calculate_delay(
            attempt_number=attempt_number,
            jitter_enabled=actual_jitter
        )
    
    def validate_idempotency(
        self,
        operation_type: str,
        operation_data: Optional[Dict[str, Any]] = None
    ) -> IdempotencyValidation:
        """
        Validate idempotency of an operation.
        
        Args:
            operation_type: Type of operation to check
            operation_data: Additional operation context
            
        Returns:
            IdempotencyValidation result
        """
        return self._idempotency_validator.validate_operation(
            operation_type, operation_data
        )
    
    def record_retry_attempt(
        self,
        operation_id: str,
        current_time: Optional[float] = None
    ) -> int:
        """Record a retry attempt for storm prevention."""
        now = current_time or time.time()
        
        if operation_id not in self._retry_counts:
            self._retry_counts[operation_id] = 0
        
        self._retry_counts[operation_id] += 1
        self._last_retries[operation_id] = now
        
        return self._retry_counts[operation_id]
    
    def check_retry_storm(
        self,
        operation_id: str,
        time_window_seconds: float = 60.0,
        max_attempts_in_window: int = 5
    ) -> bool:
        """
        Check if a retry storm is occurring for an operation.
        
        Returns True if storm detected (retry should be suppressed).
        """
        now = time.time()
        
        if operation_id not in self._last_retries:
            return False
        
        last_retry = self._last_retries[operation_id]
        
        # Check if attempts within window exceed threshold
        elapsed = now - last_retry
        if elapsed > time_window_seconds:
            # Window expired, reset
            self._retry_counts[operation_id] = 0
            return False
        
        return self._retry_counts[operation_id] >= max_attempts_in_window


# =============================================================================
# Export aliases for backward compatibility
# =============================================================================

from dataclasses import replace

__all__ = [
    "RetryBudget",
    "RetryBudgetExhausted",
    
    "BackoffStrategy",
    "BackoffResult",
    "RetryBackoffCalculator",
    
    "RetryIdempotency",
    "IdempotencyValidation",
    "IdempotencyValidator",
    
    "RetryBudgetState",
    "RetryBudgetManager",
    
    "RetryPolicy",
    "RetryPolicyManager",
]