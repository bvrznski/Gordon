# Oriented Network Task Coordination
# ===================================

"""
Task Coordination for Phase 4.7.5

SEMANTIC ROLE:
    - Coordinates orientation toward externally owned Task concepts
    - Never owns Task implementation
    - Establishes semantic relationships between Orientation and Task

OWNERSHIP CONTRACT:
    - Owns: None (coordination reference only)
    - References: External Task entity
    - Never owns: Task implementations, runtime execution

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-001: The Oriented Network coordinates intentional orientation.
        It never owns intentional artefacts.
    ORIENTED-COORDINATION-LAW-004: Tasks remain externally authoritative.
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
# TASK COORDINATION STATUS
# =============================================================================

class TaskCoordinationStatus(str, Enum):
    """Task coordination status indicators."""
    
    ACTIVE = "active"
    """Currently coordinated and engaged"""
    
    INACTIVE = "inactive"
    """Exists but not currently active"""
    
    SUSPENDED = "suspended"
    """Temporarily paused, may be resumed"""
    
    BLOCKED = "blocked"
    """Cannot proceed due to external dependency"""
    
    CANDIDATE = "candidate"
    """Proposed but not yet adopted"""
    
    HISTORICAL = "historical"
    """Previously coordinated, now archived"""


# =============================================================================
# TASK COORDINATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class TaskCoordination(BaseCoordinator):
    """
    Coordination contract for Task orientation.
    
    SEMANTIC ROLE:
        - Coordinates orientation toward externally owned Task concepts
        - Never owns Task implementation
        - Establishes semantic relationships between Orientation and Task
        
    OWNERSHIP CONTRACT:
        - Owns: None (coordination reference only)
        - References: External Task entity
        - Never owns: Task implementations, runtime execution
        
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-004: Tasks remain externally authoritative.
    """
    
    # =============================================================================
    # COORDINATION FIELDS
    # =============================================================================
    
    identity: str = field(default="task_coordination")
    """Unique semantic identifier for this coordination"""
    
    owner: CoordinationOwner = field(default="oriented_network")
    """Architectural owner of the coordinated concept"""
    
    authority: str = field(default="semantic")
    """Source of authority for this coordination"""
    
    # =============================================================================
    # TASK SPECIFIC FIELDS
    # =============================================================================
    
    task_id: Optional[str] = None
    """Identifier for the externally owned Task"""
    
    task_context: Dict[str, Any] = field(default_factory=dict)
    """Contextual information about the task"""
    
    relationship_type: str = field(default="coordinates")
    """Type of coordination relationship"""
    
    active: bool = True
    """Whether this task is currently coordinated"""
    
    status: TaskCoordinationStatus = field(default=TaskCoordinationStatus.ACTIVE)
    """Current coordination status"""
    
    derived_from: Optional[str] = None
    """Objective that this task derives from (if known)"""
    
    depends_on: Tuple[str, ...] = field(default_factory=tuple)
    """Tasks that must complete before this one can proceed"""
    
    contributes_to: Optional[str] = None
    """Objective that this task contributes to (if known)"""
    
    # =============================================================================
    # CONSTRUCTION AND VALIDATION
    # =============================================================================
    
    def __post_init__(self) -> None:
        """Validate task coordination on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid TaskCoordination:\n{error_list}"
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
            "coordination_type": "task",
            "task_id": self.task_id,
            "task_context": self.task_context,
            "relationship_type": self.relationship_type,
            "active": self.active,
            "status": self.status.value,
            "derived_from": self.derived_from,
            "depends_on": list(self.depends_on),
            "contributes_to": self.contributes_to,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskCoordination:
        """Create instance from dictionary."""
        return cls(
            identity=data.get("identity", "task_coordination"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=data.get("authority", "semantic"),
            owner=data.get("owner", "oriented_network"),
            task_id=data.get("task_id"),
            task_context=data.get("task_context", {}),
            relationship_type=data.get("relationship_type", "coordinates"),
            active=data.get("active", True),
            status=TaskCoordinationStatus(data.get("status", TaskCoordinationStatus.ACTIVE.value)),
            derived_from=data.get("derived_from"),
            depends_on=tuple(data.get("depends_on", [])),
            contributes_to=data.get("contributes_to"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate task coordination."""
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
        if self.task_id:
            refs.append(f"task:{self.task_id}")
        if self.derived_from:
            refs.append(f"objective:{self.derived_from}")
        for dependency in self.depends_on:
            refs.append(f"task:{dependency}")
        if self.contributes_to:
            refs.append(f"objective:{self.contributes_to}")
        return tuple(refs)
    
    @property
    def hierarchy(self) -> Dict[str, Any]:
        """
        Return the semantic hierarchy representation.
        
        Task is at level 4 of the intentional hierarchy (the lowest level).
        """
        return {
            "level": 4,
            "name": "Task",
            "description": "Executable cognitive unit derived from Objectives",
            "parent": "Objective",
            "children": [],
        }


__all__ = [
    "TaskCoordinationStatus",
    "TaskCoordination",
]