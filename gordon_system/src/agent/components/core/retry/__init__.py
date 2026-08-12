# Core Retry Architecture (Phase 3.7.10)
# =======================================

"""
Core retry architecture for Phase 3.7.10.

Retry is separate from rollback, restart, and recovery:
    - Operation retry: Try the same operation again
    - Task retry: Retry entire task  
    - Transport retry: Lower-level retry (e.g., network)
    - Service-client retry: Client-side retry

Important: There must be one owner for each retry scope. Avoid nested
retry layers acting on the same operation.
"""

from .policy import RetryPolicy, RetryClassification, IdempotencyClass
from .budget import RetryBudget, RetryBudgetManager
from .backoff import BackoffStrategy, BackoffPolicy
from .coordinator import RetryCoordinator

__all__ = [
    # Policy and classification
    "RetryPolicy",
    "RetryClassification",
    "IdempotencyClass",
    
    # Budget management
    "RetryBudget",
    "RetryBudgetManager",
    
    # Backoff strategies
    "BackoffStrategy",
    "BackoffPolicy",
    
    # Coordination
    "RetryCoordinator",
]