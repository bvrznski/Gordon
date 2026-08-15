# Executive Flexibility Status Enumerations
# ===========================================

"""
Canonical status enumerations for cognitive flexibility, stability, rigidity,
instability, and balance assessments.

These are typed bounded sets of valid statuses used throughout the Executive
Network's adaptation infrastructure.
"""

from __future__ import annotations

from enum import Enum


class FlexibilityStatus(Enum):
    """
    Status of executive flexibility assessment.
    
    Canonical definition:
        Cognitive Flexibility is the bounded executive capacity to revise,
        suspend, replace, restore, or reconfigure an active executive
        organization when supplied evidence indicates that the current
        organization is no longer the most appropriate admissible configuration.
    """
    INSUFFICIENT = "insufficient"
    """Flexibility capacity is insufficient for current demands."""
    
    LIMITED = "limited"
    """Limited flexibility capacity available."""
    
    ADEQUATE = "adequate"
    """Adequate flexibility capacity for current demands."""
    
    HIGH = "high"
    """High flexibility capacity available."""
    
    EXCESSIVE = "excessive"
    """Excessive flexibility - potential for instability."""
    
    UNSTABLE = "unstable"
    """Unstable flexibility state - rapid changes detected."""
    
    UNKNOWN = "unknown"
    """Flexibility status cannot be determined."""


class StabilityStatus(Enum):
    """
    Status of executive stability assessment.
    
    Canonical definition:
        Executive Stability is the bounded capacity to maintain a valid
        executive organization despite transient noise, temporary uncertainty,
        weak competing signals, and non-material fluctuations.
    
    Stability is NOT rigidity - rigidity is maladaptive inability to revise.
    """
    INSUFFICIENT = "insufficient"
    """Stability insufficient for current demands."""
    
    FRAGILE = "fragile"
    """Stability is fragile and may collapse easily."""
    
    ADEQUATE = "adequate"
    """Adequate stability for current demands."""
    
    STRONG = "strong"
    """Strong stability - valid organization well maintained."""
    
    EXCESSIVE = "excessive"
    """Excessive stability - potential for rigidity."""
    
    RIGID = "rigid"
    """Rigid state detected - maladaptive inability to revise."""
    
    UNKNOWN = "unknown"
    """Stability status cannot be determined."""


class RigidityStatus(Enum):
    """
    Status of executive rigidity assessment.
    
    Canonical definition:
        Executive Rigidity is the maladaptive inability or refusal to revise
        an executive configuration despite sufficient evidence, authority,
        and opportunity for justified reconfiguration.
    
    Rigidity is NOT stability - stability maintains valid organization.
    Rigidity preserves INVALID organization.
    """
    FLEXIBLE = "flexible"
    """Flexibility observed - no rigidity."""
    
    APPROPRIATELY_STABLE = "appropriately_stable"
    """Appropriately stable, not rigid."""
    
    MARGINALLY_RIGID = "marginally_rigid"
    """Slightly rigid but still responsive to evidence."""
    
    RIGID = "rigid"
    """Rigidity detected - difficulty revising executive configuration."""
    
    SEVERELY_RIGID = "severely_rigid"
    """Severe rigidity - minimal responsiveness to evidence."""
    
    UNKNOWN = "unknown"
    """Rigidity status cannot be determined."""


class InstabilityStatus(Enum):
    """
    Status of executive instability assessment.
    
    Canonical definition:
        Executive Instability is excessive or poorly justified reconfiguration
        of the executive organization.
    """
    STABLE = "stable"
    """Executive organization is stable."""
    
    MINOR_INSTABILITY = "minor_instability"
    """Minor instability detected - transient fluctuations."""
    
    UNSTABLE = "unstable"
    """Unstable executive organization."""
    
    SEVERELY_UNSTABLE = "severely_unstable"
    """Severely unstable executive organization."""
    
    FRAGMENTED = "fragmented"
    """Executive organization is fragmented."""
    
    UNKNOWN = "unknown"
    """Instability status cannot be determined."""


class BalanceStatus(Enum):
    """
    Status of stability-flexibility balance assessment.
    """
    APPROPRIATE_STABILITY = "appropriate_stability"
    """Balance favoring appropriate stability."""
    
    APPROPRIATE_FLEXIBILITY = "appropriate_flexibility"
    """Balance favoring appropriate flexibility."""
    
    STABILITY_BIASED = "stability_biased"
    """Balance biased toward stability (potential for rigidity)."""
    
    FLEXIBILITY_BIASED = "flexibility_biased"
    """Balance biased toward flexibility (potential for instability)."""
    
    RIGID = "rigid"
    """Rigid state - no flexibility."""
    
    UNSTABLE = "unstable"
    """Unstable state - excessive flexibility."""
    
    CONFLICTED = "conflicted"
    """Conflicting signals detected - cannot determine balance."""
    
    CONTEXT_DEPENDENT = "context_dependent"
    """Balance appropriate for current context."""
    
    UNKNOWN = "unknown"
    """Balance status cannot be determined."""


def get_all_statuses() -> dict[str, list[str]]:
    """
    Return all valid statuses by category.
    
    This is used for validation and serialization.
    """
    return {
        "flexibility": [s.value for s in FlexibilityStatus],
        "stability": [s.value for s in StabilityStatus],
        "rigidity": [s.value for s in RigidityStatus],
        "instability": [s.value for s in InstabilityStatus],
        "balance": [s.value for s in BalanceStatus],
    }


__all__ = [
    "FlexibilityStatus",
    "StabilityStatus",
    "RigidityStatus",
    "InstabilityStatus",
    "BalanceStatus",
    "get_all_statuses",
]