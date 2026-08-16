# Oriented Network Objective Coordination
# ========================================

"""
Objective Coordination for Phase 4.7.5

SEMANTIC ROLE:
    - Coordinates orientation toward externally owned Objective concepts
    - Never owns Objective implementation
    - Establishes semantic relationships between Orientation and Objective

OWNERSHIP CONTRACT:
    - Owns: None (coordination reference only)
    - References: External Objective entity
    - Never owns: Objective implementations, runtime execution

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-001: The Oriented Network coordinates intentional orientation.
        It never owns intentional artefacts.
    ORIENTED-COORDINATION-LAW-003: Objectives remain externally authoritative.
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
# OBJECTIVE COORDINATION STATUS
# =============================================================================

class ObjectiveCoordinationStatus(str, Enum):
    """Objective coordination status indicators."""
    
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
# OBJECTIVE COORDINATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class ObjectiveCoordination(BaseCoordinator):
    """
    Coordination contract for Objective orientation.
    
    SEMANTIC ROLE:
        - Coordinates orientation toward externally owned Objective concepts
        - Never owns Objective implementation
        - Establishes semantic relationships between Orientation and Objective
        
    OWNERSHIP CONTRACT:
        - Owns: None (coordination reference only)
        - References: External Objective entity
        - Never owns: Objective implementations, runtime execution
        
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-003: Objectives remain externally authoritative.
    """
    
    # =============================================================================
    # COORDINATION FIELDS
    # =============================================================================
    
    identity: str = field(default="objective_coordination")
    """Unique semantic identifier for this coordination"""
    
    owner: CoordinationOwner = field(default="oriented_network")
    """Architectural owner of the coordinated concept"""
    
    authority: str = field(default="semantic")
    """Source of authority for this coordination"""
    
    # =============================================================================
    # OBJECTIVE SPECIFIC FIELDS
    # =============================================================================
    
    objective_id: Optional[str] = None
    """Identifier for the externally owned Objective"""
    
    objective_context: Dict[str, Any] = field(default_factory=dict)
    """Contextual information about the objective"""
    
    relationship_type: str = field(default="coordinates")
    """Type of coordination relationship"""
    
    active: bool = True
    """Whether this objective is currently coordinated"""
    
    status: ObjectiveCoordinationStatus = field(default=ObjectiveCoordinationStatus.ACTIVE)
    """Current coordination status"""
    
    contributes_to: Optional[str] = None
    """Goal that this objective contributes to (if known)"""
    
    related_tasks: Tuple[str, ...] = field(default_factory=tuple)
    """Tasks derived from this objective"""
    
    # =============================================================================
    # CONSTRUCTION AND VALIDATION
    # =============================================================================
    
    def __post_init__(self) -> None:
        """Validate objective coordination on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid ObjectiveCoordination:\n{error_list}"
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
            "coordination_type": "objective",
            "objective_id": self.objective_id,
            "objective_context": self.objective_context,
            "relationship_type": self.relationship_type,
            "active": self.active,
            "status": self.status.value,
            "contributes_to": self.contributes_to,
            "related_tasks": list(self.related_tasks),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ObjectiveCoordination:
        """Create instance from dictionary."""
        return cls(
            identity=data.get("identity", "objective_coordination"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=data.get("authority", "semantic"),
            owner=data.get("owner", "oriented_network"),
            objective_id=data.get("objective_id"),
            objective_context=data.get("objective_context", {}),
            relationship_type=data.get("relationship_type", "coordinates"),
            active=data.get("active", True),
            status=ObjectiveCoordinationStatus(data.get("status", ObjectiveCoordinationStatus.ACTIVE.value)),
            contributes_to=data.get("contributes_to"),
            related_tasks=tuple(data.get("related_tasks", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate objective coordination."""
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
        if self.objective_id:
            refs.append(f"objective:{self.objective_id}")
        if self.contributes_to:
            refs.append(f"goal:{self.contributes_to}")
        for task in self.related_tasks:
            refs.append(f"task:{task}")
        return tuple(refs)
    
    @property
    def hierarchy(self) -> Dict[str, Any]:
        """
        Return the semantic hierarchy representation.
        
        Objective is at level 3 of the intentional hierarchy (below Goal).
        """
        return {
            "level": 3,
            "name": "Objective",
            "description": "Intermediate target contributing to Goal achievement",
            "parent": "Goal",
            "children": ["Task"],
        }


__all__ = [
    "ObjectiveCoordinationStatus",
    "ObjectiveCoordination",
]