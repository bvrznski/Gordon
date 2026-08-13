# Retry Policy Module
# ===================
"""
Retry policy module for Phase 3.7.10 failure recovery.

This module re-exports retry budget management from the canonical location
(core.retry.budget) and adds additional policy types.

Key principles:
    - One canonical retry-policy authority
    - Budgets are bounded (no unlimited retries)
    - Backoff is deterministic under test
    - Non-idempotent operations rejected without protection

Canonical Location: core/retry/budget.py
"""

# Re-export from canonical location to maintain single source of truth
from ..retry.budget import (
    RetryBudget,
    RetryBudgetManager,
)

__all__ = [
    "RetryBudget",
    "RetryBudgetManager",
]