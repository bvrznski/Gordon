# Oriented Network Coordination Lifecycle Package
# ===============================================

"""
Lifecycle Semantics for Phase 4.7.5

PUBLIC API:
    - BaseLifecycleState: Abstract base for lifecycle states
    - PurposeLifecycleState: Purpose lifecycle state
    - MissionLifecycleState: Mission lifecycle state  
    - GoalLifecycleState: Goal lifecycle state
    - ObjectiveLifecycleState: Objective lifecycle state
    - TaskLifecycleState: Task lifecycle state

COORDINATION LIFECYCLE STATES:

Purpose Lifecycle:
    - Candidate: Proposed but not yet adopted
    - Active: Currently oriented toward
    - Suspended: Temporarily paused
    - Completed: Semantic satisfaction achieved
    - Abandoned: Intentionally dropped
    - Historical: Previously active, now archived

Mission Lifecycle:
    - Candidate: Proposed mission orientation
    - Active: Currently organized around
    - Suspended: Paused, may be resumed
    - Completed: Mission objectives fulfilled
    - Abandoned: No longer relevant
    - Historical: Archived mission state

Goal Lifecycle:
    - Candidate: Proposed goal target
    - Active: Actively pursued
    - Suspended: Temporarily paused
    - Blocked: Cannot proceed due to constraints
    - Completed: Goal achievement verified
    - Abandoned: No longer prioritized
    - Historical: Previously active, now archived

Objective Lifecycle:
    - Candidate: Proposed intermediate target
    - Active: Currently pursued
    - Suspended: Temporarily paused
    - Completed: Objective achieved
    - Abandoned: No longer relevant
    - Historical: Archived objective state

Task Lifecycle:
    - Candidate: Proposed executable action
    - Active: Currently executed
    - Suspended: Paused execution
    - Blocked: Cannot proceed
    - Completed: Task finished
    - Cancelled: Execution stopped
    - Historical: Previously active, now archived

COORDINATION LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-031 through 040: Lifecycle coordination laws
"""

from __future__ import annotations

# =============================================================================
# PHASE 4.7.5: Lifecycle States - Public API
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.coordination.lifecycle.base import (
    BaseLifecycleState,
    PurposeLifecycleState,
    MissionLifecycleState,
    GoalLifecycleState,
    ObjectiveLifecycleState,
    TaskLifecycleState,
    LifecycleTransition,
)

__all__ = [
    # Lifecycle state enums
    "PurposeLifecycleState",
    "MissionLifecycleState",
    "GoalLifecycleState",
    "ObjectiveLifecycleState",
    "TaskLifecycleState",
    # Base interface
    "BaseLifecycleState",
    # Transitions
    "LifecycleTransition",
]
