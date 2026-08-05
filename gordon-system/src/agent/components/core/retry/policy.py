# Retry Policy
# ============

"""
Retry policy for Phase 3.7.10.

The policy determines:
    - Whether a retry is permitted
    - Which retry action to use (immediate, backoff-based, etc.)
    - Maximum attempts allowed
    - Backoff strategy and parameters

Retry must be separate from rollback, restart, and recovery.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional


@dataclass(frozen=True)
class RetryClassification:
    """
    Classification of an operation for retry purposes.
    
    Args:
        idempotency_class: Can the operation be safely retried?
        has_side_effects: Does the operation have side effects?
        unknown_outcome: Is the outcome uncertain after failure?
        
        max_attempts: How many times can we try?
        backoff_strategy: What backoff strategy to use
    """
    
    idempotency_class: "IdempotencyClass"
    has_side_effects: bool = False
    unknown_outcome: bool = False
    
    max_attempts: int = 3
    backoff_strategy: str = "exponential"  # exponential, linear, fixed


class IdempotencyClass(Enum):
    """
    Idempotency classification for retry decisions.
    
    - IDEMPOTENT: Same result regardless of how many times executed (safe to retry)
    - DEDUPLICATED: Has unique ID, duplicates ignored by system
    - COMPENSATABLE: Effects can be reversed through compensation
    - NON_IDEMPOTENT: Cannot safely retry without verification
    """
    
    IDEMPOTENT = "idempotent"
    DEDUPLICATED = "deduplicated"
    COMPENSATABLE = "compensatable"
    NON_IDEMPOTENT = "non_idempotent"


@dataclass(frozen=True)
class RetryPolicy:
    """
    A retry policy for a specific operation or scope.
    
    Args:
        policy_id: Unique identifier
        max_attempts: Maximum retry attempts allowed
        
        backoff_base_seconds: Base delay between retries
        backoff_max_seconds: Maximum delay cap
        jitter_factor: Randomness multiplier (0.0-1.0)
        
        failure_kinds_retriable: Which failure kinds are retryable
        timeout_per_attempt_seconds: Timeout per attempt
        
        budget_scope: Scope of budget (operation, task, service, etc.)
    """
    
    policy_id: str
    
    max_attempts: int = 3
    
    backoff_base_seconds: float = 1.0
    backoff_max_seconds: float = 60.0
    jitter_factor: float = 0.1
    
    failure_kinds_retriable: List[str] = field(default_factory=lambda: [
        "transient",
        "timeout", 
        "temporary_unavailable"
    ])
    
    timeout_per_attempt_seconds: Optional[float] = None
    
    budget_scope: str = "operation"  # operation, task, service, component


class BackoffStrategy(Enum):
    """Backoff strategies for retry delays."""
    
    NONE = "none"              # No delay between retries
    FIXED = "fixed"            # Fixed delay each time
    LINEAR = "linear"          # Linear backoff (base, 2*base, 3*base...)
    EXPONENTIAL = "exponential"  # Exponential backoff (base, base^2, base^3...)
    SERVER_DIRECTED = "server_directed"  # Use server-supplied delay
    ADAPTIVE = "adaptive"      # Learn from system feedback


@dataclass(frozen=True)
class BackoffPolicy:
    """
    Backoff policy for retry delays.
    
    Args:
        strategy: Which backoff strategy to use
        
        base_delay_seconds: Starting delay
        max_delay_seconds: Maximum delay cap
        jitter_enabled: Whether to add randomness
        clock: Clock source (for deterministic testing)
    """
    
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    jitter_enabled: bool = True