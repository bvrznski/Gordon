# Oriented Network Constraint Coordination
# =========================================

"""
Constraint Coordination for Phase 4.7.5

SEMANTIC ROLE:
    - Coordinates orientation toward externally owned Constraint concepts
    - Never owns Constraint enforcement
    - Establishes semantic relationships between Orientation and Constraints

OWNERSHIP CONTRACT:
    - Owns: None (coordination reference only)
    - References: External Constraint entity
    - Never owns: Constraint enforcement, runtime implementation

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-001: The Oriented Network coordinates intentional orientation.
        It never owns intentional artefacts.
    ORIENTED-COORDINATION-LAW-007: Constraints remain externally authoritative.
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
# CONSTRAINT COORDINATION TYPES
# =============================================================================

class ConstraintType(str, Enum):
    """Types of constraints."""
    
    HARD = "hard"
    """Hard constraint - must be satisfied"""
    
    SOFT = "soft"
    """Soft constraint - should be satisfied if possible"""
    
    POLICY = "policy"
    """Policy constraint - organizational policy"""
    
    REQUIREMENT = "requirement"
    """Functional or non-functional requirement"""
    
    DEPENDENCY = "dependency"
    """Dependency that must be satisfied"""
    
    PREFERENCE = "preference"
    """User/system preference"""
    
    RISK = "risk"
    """Risk to avoid or mitigate"""


class ConstraintCoordinationStatus(str, Enum):
    """Constraint coordination status indicators."""
    
    ACTIVE = "active"
    """Currently coordinated and enforced"""
    
    INACTIVE = "inactive"
    """Exists but not currently active"""
    
    SUSPENDED = "suspended"
    """Temporarily paused"""
    
    CANDIDATE = "candidate"
    """Proposed constraint"""
    
    HISTORICAL = "historical"
    """Previously coordinated, now archived"""


# =============================================================================
# CONSTRAINT COORDINATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class ConstraintCoordination(BaseCoordinator):
    """
    Coordination contract for Constraint orientation.
    
    SEMANTIC ROLE:
        - Coordinates orientation toward externally owned Constraint concepts
        - Never owns Constraint enforcement
        - Establishes semantic relationships between Orientation and Constraints
        
    OWNERSHIP CONTRACT:
        - Owns: None (coordination reference only)
        - References: External Constraint entity
        - Never owns: Constraint enforcement, runtime implementation
        
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-007: Constraints remain externally authoritative.
    """
    
    # =============================================================================
    # COORDINATION FIELDS
    # =============================================================================
    
    identity: str = field(default="constraint_coordination")
    """Unique semantic identifier for this coordination"""
    
    owner: CoordinationOwner = field(default="oriented_network")
    """Architectural owner of the coordinated concept"""
    
    authority: str = field(default="semantic")
    """Source of authority for this coordination"""
    
    # =============================================================================
    # CONSTRAINT SPECIFIC FIELDS
    # =============================================================================
    
    constraint_id: Optional[str] = None
    """Identifier for the externally owned Constraint"""
    
    constraint_type: ConstraintType = field(default=ConstraintType.HARD)
    """Type of constraint (hard, soft, policy, etc.)"""
    
    status: ConstraintCoordinationStatus = field(default=ConstraintCoordinationStatus.ACTIVE)
    """Current coordination status"""
    
    active: bool = True
    """Whether this constraint is currently enforced"""
    
    affects_orientation: Tuple[str, ...] = field(default_factory=tuple)
    """Orientations affected by this constraint (if known)"""
    
    influences_task_selection: Tuple[str, ...] = field(default_factory=tuple)
    """Tasks influenced by this constraint (if known)"""
    
    priority: float = field(default=0.5)
    """Constraint priority (0.0-1.0) - higher means more important"""
    
    severity: str = field(default="medium")
    """Violation severity (low, medium, high, critical)"""
    
    # =============================================================================
    # CONSTRUCTION AND VALIDATION
    # =============================================================================
    
    def __post_init__(self) -> None:
        """Validate constraint coordination on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid ConstraintCoordination:\n{error_list}"
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
            "coordination_type": "constraint",
            "constraint_id": self.constraint_id,
            "constraint_type": self.constraint_type.value,
            "status": self.status.value,
            "active": self.active,
            "affects_orientation": list(self.affects_orientation),
            "influences_task_selection": list(self.influences_task_selection),
            "priority": self.priority,
            "severity": self.severity,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConstraintCoordination:
        """Create instance from dictionary."""
        return cls(
            identity=data.get("identity", "constraint_coordination"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=data.get("authority", "semantic"),
            owner=data.get("owner", "oriented_network"),
            constraint_id=data.get("constraint_id"),
            constraint_type=ConstraintType(data.get("constraint_type", ConstraintType.HARD.value)),
            status=ConstraintCoordinationStatus(data.get("status", ConstraintCoordinationStatus.ACTIVE.value)),
            active=data.get("active", True),
            affects_orientation=tuple(data.get("affects_orientation", [])),
            influences_task_selection=tuple(data.get("influences_task_selection", [])),
            priority=float(data.get("priority", 0.5)),
            severity=data.get("severity", "medium"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate constraint coordination."""
        errors = []
        
        if not self.identity:
            errors.append("identity is required")
        
        if self.revision < 1:
            errors.append("revision must be >= 1")
        
        if self.version < 1:
            errors.append("version must be >= 1")
        
        if not (0.0 <= self.priority <= 1.0):
            errors.append("priority must be between 0.0 and 1.0")
        
        return len(errors) == 0, tuple(errors)
    
    @property
    def references(self) -> Tuple[str, ...]:
        """Return explicit references to externally owned concepts."""
        refs = []
        if self.constraint_id:
            refs.append(f"constraint:{self.constraint_id}")
        for orientation in self.affects_orientation:
            refs.append(f"orientation:{orientation}")
        for task in self.influences_task_selection:
            refs.append(f"task:{task}")
        return tuple(refs)
    
    @property
    def hierarchy(self) -> Dict[str, Any]:
        """
        Return the semantic hierarchy representation.
        
        Constraints operate at the boundary level, influencing all other levels.
        """
        return {
            "level": 5,
            "name": "Constraint",
            "description": "Boundary conditions that influence Orientation",
            "parent": None,
            "children": [],
            "affects_levels": [0, 1, 2, 3, 4],  # Affects all levels
        }


__all__ = [
    "ConstraintType",
    "ConstraintCoordinationStatus",
    "ConstraintCoordination",
]