# Executive Network Flexibility Module
# =====================================

"""
Canonical cognitive flexibility, stability, rigidity, and instability definitions.

This module implements Phase 4.4.8 semantic architecture for:
- Cognitive flexibility: bounded capacity to revise executive organization when
  evidence indicates current configuration is no longer the most appropriate.
- Executive stability: bounded capacity to maintain valid executive organization
  despite noise, uncertainty, or weak competing signals.
- Executive rigidity: maladaptive inability or refusal to revise executive
  organization despite sufficient evidence and authority for justified change.

This phase establishes the semantic architecture through which the Executive
Network determines whether the current executive organization should:
    persist, stabilize, relax, suspend, resume, switch,
    partially reconfigure, replace one active component,
    inhibit one candidate, gate one transition, release one obsolete response,
    prevent perseveration, prevent premature switching,
    preserve continuity during reconfiguration,
    restore a previously suspended executive configuration.

The purpose is to preserve an appropriate balance between:
    stability: maintaining valid executive organization long enough to make progress
    flexibility: replacing invalid executive organization when evidence justifies change

This phase may assess, prepare, and propose switching or inhibition.
It must not:
    - mutate an ExecutionThread
    - replace an active ExecutionLoop
    - select or start an ExecutionCycle
    - directly switch the Focusing Network
    - directly inhibit an action
    - directly block communication
    - directly replace an Executive Program without valid authority
    - directly revise externally owned goals, commitments, strategies, plans,
      decisions, or policies
    - execute runtime preemption

OWNERSHIP:
    The Executive Network owns flexibility assessments and proposals.
    It does NOT own ExecutionThread switching or concrete action state.

AUTHORITY:
    Every switch or inhibition must identify authority.
    Potential kinds: EXECUTIVE_NETWORK_INTERNAL, EXECUTIVE_AUTHORITY,
    PROGRAM_AUTHORITY, TASK_SET_AUTHORITY, GOAL_AUTHORITY, etc.
"""

from __future__ import annotations

# Core definitions
from gordon_system.src.agent.networks.executive.flexibility.assessment import (
    ExecutiveFlexibilityAssessment,
    ExecutiveStabilityAssessment,
    ExecutiveRigidityAssessment,
    ExecutiveInstabilityAssessment,
)

from gordon_system.src.agent.networks.executive.flexibility.balance import (
    StabilityFlexibilityBalance,
    BalanceKind,
)

# Update status imports to include new balance kind
from gordon_system.src.agent.networks.executive.flexibility.status import (
    FlexibilityStatus,
    StabilityStatus,
    RigidityStatus,
    InstabilityStatus,
    BalanceStatus,
)

__all__ = [
    # Assessments
    "ExecutiveFlexibilityAssessment",
    "ExecutiveStabilityAssessment",
    "ExecutiveRigidityAssessment",
    "ExecutiveInstabilityAssessment",
    # Balance
    "StabilityFlexibilityBalance",
    "BalanceKind",
    # Status enums
    "FlexibilityStatus",
    "StabilityStatus",
    "RigidityStatus",
    "InstabilityStatus",
    "BalanceStatus",
]
