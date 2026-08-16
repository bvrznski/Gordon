# Oriented Network Goal Coordination
# ===================================

"""
Goal Coordination for Phase 4.7.5

SEMANTIC ROLE:
    - Coordinates orientation toward externally owned Goal concepts
    - Never owns Goal implementation
    - Establishes semantic relationships between Orientation and Goal

OWNERSHIP CONTRACT:
    - Owns: None (coordination reference only)
    - References: External Goal entity
    - Never owns: Goal implementations, runtime execution

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-001: The Oriented Network coordinates intentional orientation.
        It never owns intentional artefacts.
    ORIENTED-COORDINATION-LAW-002: Goals remain externally authoritative.
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
# GOAL COORDINATION STATUS
# =============================================================================

class GoalCoordinationStatus(str, Enum):
    """Goal coordination status indicators."""
    
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
# GOAL COORDINATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class GoalCoordination(BaseCoordinator):
    """
    Coordination contract for Goal orientation.
    
    SEMANTIC ROLE:
        - Coordinates orientation toward externally owned Goal concepts
        - Never owns Goal implementation
        - Establishes semantic relationships between Orientation and Goal
        
    OWNERSHIP CONTRACT:
        - Owns: None (coordination reference only)
        - References: External Goal entity
        - Never owns: Goal implementations, runtime execution
        
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-002: Goals remain externally authoritative.
    """
    
    # =============================================================================
    # COORDINATION FIELDS
    # =============================================================================
    
    identity: str = field(default="goal_coordination")
    """Unique semantic identifier for this coordination"""
    
    owner: CoordinationOwner = field(default="oriented_network")
    """Architectural owner of the coordinated concept"""
    
    authority: str = field(default="semantic")
    """Source of authority for this coordination"""
    
    # =============================================================================
    # GOAL SPECIFIC FIELDS
    # =============================================================================
    
    goal_id: Optional[str] = None
    """Identifier for the externally owned Goal"""
    
    goal_context: Dict[str, Any] = field(default_factory=dict)
    """Contextual information about the goal"""
    
    relationship_type: str = field(default="coordinates")
    """Type of coordination relationship"""
    
    active: bool = True
    """Whether this goal is currently coordinated"""
    
    status: GoalCoordinationStatus = field(default=GoalCoordinationStatus.ACTIVE)
    """Current coordination status"""
    
    contributes_to: Optional[str] = None
    """Mission that this goal contributes to (if known)"""
    
    related_objectives: Tuple[str, ...] = field(default_factory=tuple)
    """Objectives related to this goal"""
    
    related_tasks: Tuple[str, ...] = field(default_factory=tuple)
    """Tasks related to this goal"""
    
    # =============================================================================
    # CONSTRUCTION AND VALIDATION
    # =============================================================================
    
    def __post_init__(self) -> None:
        """Validate goal coordination on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid GoalCoordination:\n{error_list}"
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
            "coordination_type": "goal",
            "goal_id": self.goal_id,
            "goal_context": self.goal_context,
            "relationship_type": self.relationship_type,
            "active": self.active,
            "status": self.status.value,
            "contributes_to": self.contributes_to,
            "related_objectives": list(self.related_objectives),
            "related_tasks": list(self.related_tasks),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoalCoordination:
        """Create instance from dictionary."""
        return cls(
            identity=data.get("identity", "goal_coordination"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=data.get("authority", "semantic"),
            owner=data.get("owner", "oriented_network"),
            goal_id=data.get("goal_id"),
            goal_context=data.get("goal_context", {}),
            relationship_type=data.get("relationship_type", "coordinates"),
            active=data.get("active", True),
            status=GoalCoordinationStatus(data.get("status", GoalCoordinationStatus.ACTIVE.value)),
            contributes_to=data.get("contributes_to"),
            related_objectives=tuple(data.get("related_objectives", [])),
            related_tasks=tuple(data.get("related_tasks", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate goal coordination."""
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
        if self.goal_id:
            refs.append(f"goal:{self.goal_id}")
        if self.contributes_to:
            refs.append(f"mission:{self.contributes_to}")
        for objective in self.related_objectives:
            refs.append(f"objective:{objective}")
        for task in self.related_tasks:
            refs.append(f"task:{task}")
        return tuple(refs)
    
    @property
    def hierarchy(self) -> Dict[str, Any]:
        """
        Return the semantic hierarchy representation.
        
        Goal is at level 2 of the intentional hierarchy (below Mission).
        """
        return {
            "level": 2,
            "name": "Goal",
            "description": "Actively oriented cognitive target requiring specific cognitive work",
            "parent": "Mission",
            "children": ["Objective"],
        }


__all__ = [
    "GoalCoordinationStatus",
    "GoalCoordination",
]