# Core Integrity Package
# ======================

"""
Core integrity validation infrastructure for Gordon agent.

This package provides:
- Runtime structural integrity checks
- Named invariants with explicit conditions
- Integrity plans (FAST, STANDARD, DEEP, SHUTDOWN, RECOVERY)
- Invariant evaluation and reporting
"""

from . import runtime as _runtime

# Re-export key types from runtime module
from .runtime import (
    RuntimeInvariant,
    InvariantResult,
    IntegrityPlan,
    IntegrityReport,
    RuntimeInvariants,
    RuntimeIntegrityValidator,
)

__all__ = [
    # Runtime integrity
    "RuntimeInvariant",
    "InvariantResult",
    "IntegrityPlan",
    "IntegrityReport",
    "RuntimeInvariants",
    "RuntimeIntegrityValidator",
]

# Import runtime module for access to all new types
runtime = _runtime