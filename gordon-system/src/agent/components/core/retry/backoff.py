# Retry Backoff Strategy
# ======================

"""
Backoff strategies for retry delays in Phase 3.7.10.

Strategies:
    - NONE: No delay between retries
    - FIXED: Fixed delay each time
    - LINEAR: Linear backoff (base, 2*base, 3*base...)
    - EXPONENTIAL: Exponential backoff (base, base^2, base^3...)
    - SERVER_DIRECTED: Use server-supplied delay
    - ADAPTIVE: Learn from system feedback

Each strategy includes:
    - Base delay
    - Maximum delay cap  
    - Jitter for preventing thundering herd
"""

from dataclasses import dataclass, field
from enum import Enum, auto
import time
import random
from typing import Optional, List


@dataclass(frozen=True)
class BackoffDelay:
    """
    A calculated backoff delay.
    
    Args:
        delay_seconds: How long to wait
        jitter_applied: Whether jitter was applied
        next_delay_estimate: Estimated delay for next retry (if known)
    """
    
    delay_seconds: float
    jitter_applied: bool = False
    next_delay_estimate: Optional[float] = None


class BackoffStrategy(Enum):
    """Backoff strategies."""
    
    NONE = "none"
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    SERVER_DIRECTED = "server_directed"
    ADAPTIVE = "adaptive"


@dataclass(frozen=True)
class BackoffPolicy:
    """
    Backoff policy configuration.
    
    Args:
        strategy: Which backoff strategy to use
        base_delay_seconds: Starting delay
        max_delay_seconds: Maximum delay cap
        jitter_enabled: Whether to add randomness
    """
    
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    
    jitter_enabled: bool = True


class BackoffCalculator:
    """
    Calculate backoff delays based on policy.
    
    Usage:
        calculator = BackoffCalculator(
            BackoffPolicy(strategy=BackoffStrategy.EXPONENTIAL)
        )
        
        # Get delay for attempt 1, 2, 3...
        for attempt in range(1, 4):
            delay = calculator.calculate_delay(attempt)
            await asyncio.sleep(delay.delay_seconds)
    """
    
    def __init__(self, policy: BackoffPolicy) -> None:
        """Initialize the backoff calculator."""
        self._policy = policy
        self._attempt_count = 0
    
    @property
    def attempt_count(self) -> int:
        """Get current attempt count."""
        return self._attempt_count
    
    def calculate_delay(self, attempt: Optional[int] = None) -> BackoffDelay:
        """
        Calculate the backoff delay for the given attempt.
        
        Args:
            attempt: Which attempt number (1-based), or uses internal counter
            
        Returns:
            BackoffDelay with delay_seconds and jitter info
        """
        if attempt is not None:
            self._attempt_count = attempt
        
        base = self._policy.base_delay_seconds
        max_delay = self._policy.max_delay_seconds
        
        # Calculate raw delay based on strategy
        if self._policy.strategy == BackoffStrategy.NONE:
            delay = 0.0
        
        elif self._policy.strategy == BackoffStrategy.FIXED:
            delay = base
        
        elif self._policy.strategy == BackoffStrategy.LINEAR:
            delay = base * self._attempt_count
        
        elif self._policy.strategy == BackoffStrategy.EXPONENTIAL:
            delay = base * (2 ** (self._attempt_count - 1))
        
        else:  # SERVER_DIRECTED or ADAPTIVE
            delay = base
        
        # Cap at maximum
        delay = min(delay, max_delay)
        
        # Apply jitter if enabled
        jitter_applied = False
        if self._policy.jitter_enabled and delay > 0:
            jitter_factor = random.uniform(0.5, 1.5)  # +/- 50%
            delay *= jitter_factor
            jitter_applied = True
        
        return BackoffDelay(delay_seconds=delay, jitter_applied=jitter_applied)
    
    def reset(self) -> None:
        """Reset attempt counter."""
        self._attempt_count = 0
    
    def get_remaining_delays(self, max_attempts: int) -> List[float]:
        """
        Get delays for all remaining attempts.
        
        Args:
            max_attempts: Total number of attempts allowed
            
        Returns:
            List of delay values (without jitter)
        """
        base = self._policy.base_delay_seconds
        max_delay = self._policy.max_delay_seconds
        
        if self._policy.strategy == BackoffStrategy.NONE:
            return [0.0] * max_attempts
        
        elif self._policy.strategy == BackoffStrategy.FIXED:
            return [base] * max_attempts
        
        elif self._policy.strategy == BackoffStrategy.LINEAR:
            return [
                min(base * (i + 1), max_delay)
                for i in range(self._attempt_count, max_attempts)
            ]
        
        else:  # EXPONENTIAL or similar
            return [
                min(base * (2 ** i), max_delay)
                for i in range(self._attempt_count - 1, max_attempts - 1)
            ]