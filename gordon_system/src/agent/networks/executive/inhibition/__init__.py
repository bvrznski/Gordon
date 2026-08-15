# Executive Network Inhibition Module
# ===================================

"""
Canonical executive inhibition semantic architecture for Phase 4.4.8.

Executive Inhibition is defined as:
    The bounded semantic restriction, withholding, attenuation, gating,
    or suppression proposal applied to an executive or cognitive candidate
    whose activation, selection, continuation, disclosure, or execution
    is currently inadmissible, conflicting, premature, harmful, or
    insufficiently justified.

Inhibition may concern:
    - response candidate
    - action candidate
    - strategy
    - goal activation
    - Program activation
    - Task Set activation
    - decision commitment
    - communication release
    - memory retrieval request
    - focus-switch request
    - completion transition
    - control intensification

Inhibition is NOT:
    - deletion
    - punishment
    - permanent suppression
    - runtime process kill
    - unconditional censorship
    - security authorization
    - policy enforcement
    - action execution

OWNERSHIP:
    The Executive Network owns inhibition assessments and proposals.
    It does NOT own direct blocking of external targets.

AUTHORITY:
    Every inhibition must identify authority. Potential kinds include:
        EXECUTIVE_NETWORK_INTERNAL, EXECUTIVE_AUTHORITY,
        ACTION_AUTHORITY, COMMUNICATION_AUTHORITY, etc.
"""

from __future__ import annotations

# Core inhibition contracts
from gordon_system.src.agent.networks.executive.inhibition.subject import (
    ExecutiveInhibitionSubject,
)

from gordon_system.src.agent.networks.executive.inhibition.target import (
    ExecutiveInhibitionTarget,
)

from gordon_system.src.agent.networks.executive.inhibition.kind import (
    ExecutiveInhibitionKind,
)

from gordon_system.src.agent.networks.executive.inhibition.purpose import (
    ExecutiveInhibitionPurpose,
)

from gordon_system.src.agent.networks.executive.inhibition.intensity import (
    ExecutiveInhibitionIntensity,
)

from gordon_system.src.agent.networks.executive.inhibition.persistence import (
    ExecutiveInhibitionPersistence,
)

from gordon_system.src.agent.networks.executive.inhibition.scope import (
    ExecutiveInhibitionScope,
)

from gordon_system.src.agent.networks.executive.inhibition.eligibility import (
    ExecutiveInhibitionEligibilityAssessment,
)

from gordon_system.src.agent.networks.executive.inhibition.compatibility import (
    ExecutiveInhibitionCompatibilityAssessment,
)

# Assessments and proposals
from gordon_system.src.agent.networks.executive.inhibition.assessment import (
    ExecutiveInhibitionAssessment,
)

from gordon_system.src.agent.networks.executive.inhibition.proposal import (
    ExecutiveInhibitionProposal,
)

from gordon_system.src.agent.networks.executive.inhibition.release import (
    ExecutiveInhibitionReleaseCondition,
    ExecutiveInhibitionReleaseAssessment,
    ExecutiveInhibitionReleaseProposal,
)

__all__ = [
    # Core contracts
    "ExecutiveInhibitionSubject",
    "ExecutiveInhibitionTarget",
    "ExecutiveInhibitionKind",
    "ExecutiveInhibitionPurpose",
    "ExecutiveInhibitionIntensity",
    "ExecutiveInhibitionPersistence",
    "ExecutiveInhibitionScope",
    # Assessments
    "ExecutiveInhibitionEligibilityAssessment",
    "ExecutiveInhibitionCompatibilityAssessment",
    "ExecutiveInhibitionAssessment",
    # Proposals
    "ExecutiveInhibitionProposal",
    # Release
    "ExecutiveInhibitionReleaseCondition",
    "ExecutiveInhibitionReleaseAssessment",
    "ExecutiveInhibitionReleaseProposal",
]