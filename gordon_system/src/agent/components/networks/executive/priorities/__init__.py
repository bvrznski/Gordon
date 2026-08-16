# Executive Priorities Package
# ============================

"""
Executive Priorities - Canonical semantic architecture for priority assessments,
dimensions, ordering, and comparison in Phase 4.4.4.

This package implements priority as bounded executive assessment of relative claim
on limited executive control under the current context.
"""

from __future__ import annotations

from gordon_system.src.agent.networks.executive.priorities.assessment import (
    ExecutivePriorityAssessment,
)
from gordon_system.src.agent.networks.executive.priorities.level import (
    ExecutivePriorityLevel,
)
from gordon_system.src.agent.networks.executive.priorities.ordering import (
    ExecutivePriorityOrdering,
    ExecutivePriorityRelation,
)

__all__: tuple[str, ...] = (
    "ExecutivePriorityAssessment",
    "ExecutivePriorityLevel",
    "ExecutivePriorityOrdering",
    "ExecutivePriorityRelation",
)