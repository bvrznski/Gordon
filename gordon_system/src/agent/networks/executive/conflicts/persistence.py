# Executive Conflict Persistence Model
# =====================================

"""
Types for assessing how persistent an executive conflict is.

Persistence measures how long a conflict has persisted or is expected
to persist, not its temporal bounds in absolute time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictPersistenceClass:
    """
    Persistence classes for executive conflicts.
    """
    
    TRANSIENT = "transient"
    SHORT_LIVED = "short_lived"
    PERSISTENT = "persistent"
    RECURRING = "recurring"
    ESCALATING = "escalating"
    STABLE = "stable"
    DECLINING = "declining"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutiveConflictPersistence:
    """
    Structured assessment of executive conflict persistence.
    """
    
    persistence_class: str
    duration_cycles: int = 0
    last_resolved_cycle: int = -1
    mitigation_attempts: int = 0
    failed_mitigations: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = (
    "ExecutiveConflictPersistenceClass",
    "ExecutiveConflictPersistence",
)