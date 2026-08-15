# Executive Network Override Module
# =================================

"""
Canonical executive override assessment and proposal for Phase 4.4.8.

Executive Override is an authority-safe mechanism to address:
    - Prepotent responses that conflict with policy
    - Persistent Programs despite critical error
    - Task Sets blocking mandatory commitment
    - Severe perseveration
    - Dangerous or unauthorized action candidates
    - Premature completion declarations
    - Switching required by authority
    - Counterproductive control configuration

Every override must include:
    - Overridden subject
    - Reason
    - Evidence
    - Severity
    - Authority
    - Scope
    - Duration
    - Release conditions
    - Restoration conditions
    - Expected side effects
    - Provenance

Override authority is explicit and cannot be granted by priority or confidence.
"""

from __future__ import annotations

# Core override contracts
from gordon_system.src.agent.networks.executive.override.assessment import (
    ExecutiveOverrideAssessment,
)

from gordon_system.src.agent.networks.executive.override.proposal import (
    ExecutiveOverrideProposal,
)

from gordon_system.src.agent.networks.executive.override.authority import (
    OverrideAuthorityRequirement,
)

__all__ = [
    "ExecutiveOverrideAssessment",
    "ExecutiveOverrideProposal",
    "OverrideAuthorityRequirement",
]