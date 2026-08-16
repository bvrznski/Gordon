# Oriented Network Mission Coordination
# ======================================

"""
Mission Coordination for Phase 4.7.5

SEMANTIC ROLE:
    - Coordinates orientation toward externally owned Mission concepts
    - Never owns Mission implementation
    - Establishes semantic relationships between Orientation and Mission

OWNERSHIP CONTRACT:
    - Owns: None (coordination reference only)
    - References: External Mission entity
    - Never owns: Mission implementations, runtime execution

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-001: The Oriented Network coordinates intentional orientation.
        It never owns intentional artefacts.
    ORIENTED-COORDINATION-LAW-005: Mission remains externally authoritative.
    ORIENTED-COORDINATION-LAW-008 through 040: Additional coordination laws

COGNITIVE ARCHITECTURE: PHASE 4.7.5
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional
from enum import Enum

from gordon_system.src.agent.components.networks.oriented.coordination.contracts.base import (
    BaseCoordinator,
    CoordinationOwner,
)


# =============================================================================
# MISSION COORDINATION STATUS
# =============================================================================

class MissionCoordinationStatus(str, Enum):
    """Mission coordination status indicators."""
    
    ACTIVE = "active"
    """Currently coordinated and engaged"""
    
    INACTIVE = "inactive"
    """Exists but not currently active"""
    
    SUSPENDED = "suspended"
    """Temporarily paused, may be resumed"""
    
    CANDIDATE = "candidate"
    """Proposed but not yet adopted"""
    
    HISTORICAL = "historical"
    """Previously coordinated, now archived"""


# =============================================================================
# MISSION COORDINATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class MissionCoordination(BaseCoordinator):
    """
    Coordination contract for Mission orientation.
    
    SEMANTIC ROLE:
        - Coordinates orientation toward externally owned Mission concepts
        - Never owns Mission implementation
        - Establishes semantic relationships between Orientation and Mission
        
    OWNERSHIP CONTRACT:
        - Owns: None (coordination reference only)
        - References: External Mission entity
        - Never owns: Mission implementations, runtime execution
        
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-005: Mission remains externally authoritative.
    """
    
    # =============================================================================
    # COORDINATION FIELDS
    # =============================================================================
    
    identity: str = field(default="mission_coordination")
    """Unique semantic identifier for this coordination"""
    
    owner: CoordinationOwner = field(default="oriented_network")
    """Architectural owner of the coordinated concept"""
    
    authority: str = field(default="semantic")
    """Source of authority for this coordination"""
    
    # =============================================================================
    # MISSION SPECIFIC FIELDS
    # =============================================================================
    
    mission_id: Optional[str] = None
    """Identifier for the externally owned Mission"""
    
    mission_context: Dict[str, Any] = field(default_factory=dict)
    """Contextual information about the mission"""
    
    relationship_type: str = field(default="coordinates")
    """Type of coordination relationship"""
    
    active: bool = True
    """Whether this mission is currently coordinated"""
    
    continuity: str = field(default="pending")
    """Semantic continuity status (pending, established, broken, restored)"""
    
    scope: Optional[str] = None
    """Scope definition for the mission"""
    
    contributes_to: Optional[str] = None
    """Purpose that this mission contributes to (if known)"""
    
    related_goals: Tuple[str, ...] = field(default_factory=tuple)
    """Goals related to this mission"""
    
    # =============================================================================
    # CONSTRUCTION AND VALIDATION
    # =============================================================================
    
    def __post_init__(self) -> None:
        """Validate mission coordination on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid MissionCoordination:\n{error_list}"
            )
    
    # =============================================================================
    # BASE COORDINATOR IMPLEMENTATION
    # =============================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority,
            "owner": self.owner,
            "coordination_type": "mission",
            "mission_id": self.mission_id,
            "mission_context": self.mission_context,
            "relationship_type": self.relationship_type,
            "active": self.active,
            "continuity": self.continuity,
            "scope": self.scope,
            "contributes_to": self.contributes_to,
            "related_goals": list(self.related_goals),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MissionCoordination:
        """Create instance from dictionary."""
        return cls(
            identity=data.get("identity", "mission_coordination"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=data.get("authority", "semantic"),
            owner=data.get("owner", "oriented_network"),
            mission_id=data.get("mission_id"),
            mission_context=data.get("mission_context", {}),
            relationship_type=data.get("relationship_type", "coordinates"),
            active=data.get("active", True),
            continuity=data.get("continuity", "pending"),
            scope=data.get("scope"),
            contributes_to=data.get("contributes_to"),
            related_goals=tuple(data.get("related_goals", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate mission coordination."""
        errors = []
        
        if not self.identity:
            errors.append("identity is required")
        
        if self.revision < 1:
            errors.append("revision must be >= 1")
        
        if self.version < 1:
            errors.append("version must be >= 1")
        
        return len(errors) == 0, tuple(errors)
    
    @property
    def references(self) -> Tuple[str, ...]:
        """Return explicit references to externally owned concepts."""
        refs = []
        if self.mission_id:
            refs.append(f"mission:{self.mission_id}")
        if self.contributes_to:
            refs.append(f"purpose:{self.contributes_to}")
        for goal in self.related_goals:
            refs.append(f"goal:{goal}")
        return tuple(refs)
    
    @property
    def hierarchy(self) -> Dict[str, Any]:
        """
        Return the semantic hierarchy representation.
        
        Mission is at level 1 of the intentional hierarchy (below Purpose).
        """
        return {
            "level": 1,
            "name": "Mission",
            "description": "Major orientation organizing related Goals around a common aim",
            "parent": "Purpose",
            "children": ["Goal"],
        }


__all__ = [
    "MissionCoordinationStatus",
    "MissionCoordination",
]