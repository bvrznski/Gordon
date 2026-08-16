# Oriented Network Orientation Content Types - Phase 4.7.3
# ========================================================

"""
Orientation content types for the Oriented Network.

Orientation Content represents immutable cognitive representations owned by
the Oriented Network subsystem.

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-011: Orientation Content owns semantic Orientation representations only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from enum import Enum

from gordon_system.src.agent.components.networks.oriented.content.base import (
    BaseContent,
    ContentIdentity,
)


# =============================================================================
# ORIENTATION TYPE ENUMERATIONS
# =============================================================================

class OrientationType(Enum):
    """
    Canonical orientation types for Oriented Network content.
    """
    
    CURRENT = "current"
    DESIRED = "desired"
    CANDIDATE = "candidate"
    HISTORICAL = "historical"
    SUSPENDED = "suspended"
    RECOVERED = "recovered"


# =============================================================================
# ORIENTATION CONTENT TYPES
# =============================================================================

@dataclass(frozen=True)
class CurrentOrientation(BaseContent):
    """
    The current orientation state.
    
    SEMANTIC ROLE:
        - Represents current orientation at a point in time
        - Never represents runtime execution
        
    OWNERSHIP CONTRACT:
        - Owns: None (orientation description only)
        - References: Goal, objective, task references
    """
    
    orientation_type: OrientationType = field(default=OrientationType.CURRENT, init=False)
    state_description: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, state_description: str) -> CurrentOrientation:
        return cls(identity=identity, state_description=state_description)


@dataclass(frozen=True)
class DesiredOrientation(BaseContent):
    """
    The desired orientation state.
    
    SEMANTIC ROLE:
        - Represents target/orientation to achieve
        - Never represents runtime execution
        
    OWNERSHIP CONTRACT:
        - Owns: None (orientation description only)
        - References: Goal, objective references
    """
    
    orientation_type: OrientationType = field(default=OrientationType.DESIRED, init=False)
    state_description: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, state_description: str) -> DesiredOrientation:
        return cls(identity=identity, state_description=state_description)


@dataclass(frozen=True)
class CandidateOrientation(BaseContent):
    """
    A candidate orientation under consideration.
    
    SEMANTIC ROLE:
        - Represents potential orientation
        - Never represents runtime execution
        
    OWNERSHIP CONTRACT:
        - Owns: None (orientation description only)
        - References: Goal, objective references
    """
    
    orientation_type: OrientationType = field(default=OrientationType.CANDIDATE, init=False)
    confidence: float = 0.5
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> CandidateOrientation:
        return cls(identity=identity)


@dataclass(frozen=True)
class HistoricalOrientation(BaseContent):
    """
    A historical orientation state.
    
    SEMANTIC ROLE:
        - Represents past orientation for reference
        - Never represents runtime execution
        
    OWNERSHIP CONTRACT:
        - Owns: None (orientation description only)
        - References: Goal, objective references
    """
    
    orientation_type: OrientationType = field(default=OrientationType.HISTORICAL, init=False)
    timestamp: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, timestamp: str) -> HistoricalOrientation:
        return cls(identity=identity, timestamp=timestamp)


@dataclass(frozen=True)
class SuspendedOrientation(BaseContent):
    """
    A suspended orientation state.
    
    SEMANTIC ROLE:
        - Represents temporarily paused orientation
        - Never represents runtime execution
        
    OWNERSHIP CONTRACT:
        - Owns: None (orientation description only)
        - References: Goal, objective references
    """
    
    orientation_type: OrientationType = field(default=OrientationType.SUSPENDED, init=False)
    reason: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, reason: str) -> SuspendedOrientation:
        return cls(identity=identity, reason=reason)


@dataclass(frozen=True)
class RecoveredOrientation(BaseContent):
    """
    A recovered orientation state.
    
    SEMANTIC ROLE:
        - Represents restored orientation
        - Never represents runtime execution
        
    OWNERSHIP CONTRACT:
        - Owns: None (orientation description only)
        - References: Goal, objective references
    """
    
    orientation_type: OrientationType = field(default=OrientationType.RECOVERED, init=False)
    recovery_source: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, recovery_source: str) -> RecoveredOrientation:
        return cls(identity=identity, recovery_source=recovery_source)


__all__ = [
    "OrientationType",
    # Orientation content types
    "CurrentOrientation",
    "DesiredOrientation",
    "CandidateOrientation",
    "HistoricalOrientation",
    "SuspendedOrientation",
    "RecoveredOrientation",
]