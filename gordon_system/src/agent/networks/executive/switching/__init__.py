# Executive Network Switching Module
# ===================================

"""
Canonical executive switching semantic architecture for Phase 4.4.8.

Executive Switching is defined as:
    An authority-aware semantic transition from one accepted executive
    configuration, subject, target, Program, Task Set, strategy, goal emphasis,
    response configuration, or control focus to another.

A switch must define:
    - what is changing
    - what remains stable  
    - why the switch is justified
    - what evidence supports it
    - what authority is required
    - what continuity must be preserved
    - what costs and risks exist
    - how the previous configuration may be restored
    - how the switch outcome will be evaluated

OWNERSHIP:
    The Executive Network owns switching assessments and proposals.
    It does NOT own ExecutionThread or ExecutionLoop mechanics.

AUTHORITY:
    Every switch identifies authority. Potential kinds include:
        EXECUTIVE_NETWORK_INTERNAL, EXECUTIVE_AUTHORITY,
        PROGRAM_AUTHORITY, TASK_SET_AUTHORITY, GOAL_AUTHORITY, etc.
"""

from __future__ import annotations

# Core switching contracts
from gordon_system.src.agent.networks.executive.switching.subject import (
    ExecutiveSwitchSubject,
    SwitchSubjectKind,
)

from gordon_system.src.agent.networks.executive.switching.target import (
    ExecutiveSwitchTarget,
    SwitchTargetKind,
)

from gordon_system.src.agent.networks.executive.switching.source import (
    ExecutiveSwitchSourceReference,
    SwitchSourceKind,
)

from gordon_system.src.agent.networks.executive.switching.purpose import (
    ExecutiveSwitchPurpose,
    SwitchPurposeKind,
)

from gordon_system.src.agent.networks.executive.switching.kind import (
    ExecutiveSwitchKind,
    SwitchKindType,
)

from gordon_system.src.agent.networks.executive.switching.scope import (
    ExecutiveSwitchScope,
)

from gordon_system.src.agent.networks.executive.switching.direction import (
    ExecutiveSwitchDirection,
)

from gordon_system.src.agent.networks.executive.switching.trigger import (
    ExecutiveSwitchTrigger,
)

from gordon_system.src.agent.networks.executive.switching.blocker import (
    ExecutiveSwitchBlocker,
)

from gordon_system.src.agent.networks.executive.switching.readiness import (
    ExecutiveSwitchReadinessAssessment,
)

from gordon_system.src.agent.networks.executive.switching.eligibility import (
    ExecutiveSwitchEligibilityAssessment,
)

from gordon_system.src.agent.networks.executive.switching.cost import (
    ExecutiveSwitchCostAssessment,
)

from gordon_system.src.agent.networks.executive.switching.benefit import (
    ExecutiveSwitchBenefitAssessment,
)

from gordon_system.src.agent.networks.executive.switching.risk import (
    ExecutiveSwitchRiskAssessment,
)

from gordon_system.src.agent.networks.executive.switching.reversibility import (
    ExecutiveSwitchReversibility,
)

from gordon_system.src.agent.networks.executive.switching.continuity import (
    ExecutiveSwitchContinuityAssessment,
    ExecutiveContinuityPreservationPlan,
)

from gordon_system.src.agent.networks.executive.switching.persistence import (
    ExecutiveSwitchPersistence,
)

from gordon_system.src.agent.networks.executive.switching.cooldown import (
    ExecutiveSwitchCooldownAssessment,
)

# Quality control
from gordon_system.src.agent.networks.executive.switching.premature import (
    PrematureSwitchAssessment,
)

from gordon_system.src.agent.networks.executive.switching.delayed import (
    DelayedSwitchAssessment,
)

from gordon_system.src.agent.networks.executive.switching.oscillation import (
    ExecutiveSwitchOscillationAssessment,
)

from gordon_system.src.agent.networks.executive.switching.reversal import (
    ExecutiveSwitchReversalAssessment,
    ExecutiveSwitchReversalProposal,
)

# Preparation and proposal
from gordon_system.src.agent.networks.executive.switching.preparation import (
    ExecutiveSwitchPreparation,
)

from gordon_system.src.agent.networks.executive.switching.proposal import (
    ExecutiveSwitchProposal,
)

from gordon_system.src.agent.networks.executive.switching.acceptance import (
    ExecutiveSwitchAcceptance,
    ExecutiveSwitchDecisionReference,
)

# Outcome assessment
from gordon_system.src.agent.networks.executive.switching.outcome import (
    ExecutiveSwitchOutcomeAssessment,
)

__all__ = [
    # Core contracts
    "ExecutiveSwitchSubject",
    "SwitchSubjectKind",
    "ExecutiveSwitchTarget",
    "SwitchTargetKind",
    "ExecutiveSwitchSourceReference",
    "SwitchSourceKind",
    "ExecutiveSwitchPurpose",
    "SwitchPurposeKind",
    "ExecutiveSwitchKind",
    "SwitchKindType",
    "ExecutiveSwitchScope",
    "ExecutiveSwitchDirection",
    "ExecutiveSwitchTrigger",
    "ExecutiveSwitchBlocker",
    # Assessments
    "ExecutiveSwitchReadinessAssessment",
    "ExecutiveSwitchEligibilityAssessment",
    "ExecutiveSwitchCostAssessment",
    "ExecutiveSwitchBenefitAssessment",
    "ExecutiveSwitchRiskAssessment",
    "ExecutiveSwitchReversibility",
    "ExecutiveSwitchContinuityAssessment",
    "ExecutiveContinuityPreservationPlan",
    "ExecutiveSwitchPersistence",
    "ExecutiveSwitchCooldownAssessment",
    # Quality control
    "PrematureSwitchAssessment",
    "DelayedSwitchAssessment",
    "ExecutiveSwitchOscillationAssessment",
    "ExecutiveSwitchReversalAssessment",
    "ExecutiveSwitchReversalProposal",
    # Proposal components
    "ExecutiveSwitchPreparation",
    "ExecutiveSwitchProposal",
    "ExecutiveSwitchAcceptance",
    "ExecutiveSwitchDecisionReference",
    "ExecutiveSwitchOutcomeAssessment",
]