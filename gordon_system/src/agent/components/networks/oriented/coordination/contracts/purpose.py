# Oriented Network Purpose Coordination
# ======================================

"""
Purpose Coordination for Phase 4.7.5

SEMANTIC ROLE:
    - Coordinates orientation toward externally owned Purpose concepts
    - Never owns Purpose implementation
    - Establishes semantic relationships between Orientation and Purpose

OWNERSHIP CONTRACT:
    - Owns: None (coordination reference only)
    - References: External Purpose entity
    - Never owns: Purpose implementations, runtime execution

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-001: The Oriented Network coordinates intentional orientation.
        It never owns intentional artefacts.
    ORIENTED-COORDINATION-LAW-006: Purpose remains externally authoritative.
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
# PURPOSE COORDINATION STATUS
# =============================================================================

class PurposeCoordinationStatus(str, Enum):
    """Purpose coordination status indicators."""
    
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
# PURPOSE COORDINATION CONTRACT
# =============================================================================

@dataclass(frozen=True)
class PurposeCoordination(BaseCoordinator):
    """
    Coordination contract for Purpose orientation.
    
    SEMANTIC ROLE:
        - Coordinates orientation toward externally owned Purpose concepts
        - Never owns Purpose implementation
        - Establishes semantic relationships between Orientation and Purpose
        
    OWNERSHIP CONTRACT:
        - Owns: None (coordination reference only)
        - References: External Purpose entity
        - Never owns: Purpose implementations, runtime execution
        
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-006: Purpose remains externally authoritative.
    """
    
    # =============================================================================
    # COORDINATION FIELDS
    # =============================================================================
    
    identity: str = field(default="purpose_coordination")
    """Unique semantic identifier for this coordination"""
    
    owner: CoordinationOwner = field(default="oriented_network")
    """Architectural owner of the coordinated concept"""
    
    authority: str = field(default="semantic")
    """Source of authority for this coordination"""
    
    # =============================================================================
    # PURPOSE SPECIFIC FIELDS
    # =============================================================================
    
    purpose_id: Optional[str] = None
    """Identifier for the externally owned Purpose"""
    
    purpose_context: Dict[str, Any] = field(default_factory=dict)
    """Contextual information about the purpose"""
    
    relationship_type: str = field(default="coordinates")
    """Type of coordination relationship"""
    
    active: bool = True
    """Whether this purpose is currently coordinated"""
    
    continuity: str = field(default="pending")
    """Semantic continuity status (pending, established, broken, restored)"""
    
    relevance: float = field(default=0.5)
    """Relevance score (0.0-1.0)"""
    
    # =============================================================================
    # CONSTRUCTION AND VALIDATION
    # =============================================================================
    
    def __post_init__(self) -> None:
        """Validate purpose coordination on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid PurposeCoordination:\n{error_list}"
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
            "coordination_type": "purpose",
            "purpose_id": self.purpose_id,
            "purpose_context": self.purpose_context,
            "relationship_type": self.relationship_type,
            "active": self.active,
            "continuity": self.continuity,
            "relevance": self.relevance,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PurposeCoordination:
        """Create instance from dictionary."""
        return cls(
            identity=data.get("identity", "purpose_coordination"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=data.get("authority", "semantic"),
            owner=data.get("owner", "oriented_network"),
            purpose_id=data.get("purpose_id"),
            purpose_context=data.get("purpose_context", {}),
            relationship_type=data.get("relationship_type", "coordinates"),
            active=data.get("active", True),
            continuity=data.get("continuity", "pending"),
            relevance=float(data.get("relevance", 0.5)),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate purpose coordination."""
        errors = []
        
        if not self.identity:
            errors.append("identity is required")
        
        if self.revision < 1:
            errors.append("revision must be >= 1")
        
        if self.version < 1:
            errors.append("version must be >= 1")
        
        # Relevance must be between 0 and 1
        if not (0.0 <= self.relevance <= 1.0):
            errors.append("relevance must be between 0.0 and 1.0")
        
        return len(errors) == 0, tuple(errors)
    
    @property
    def references(self) -> Tuple[str, ...]:
        """Return explicit references to externally owned concepts."""
        if self.purpose_id:
            return (f"purpose:{self.purpose_id}",)
        return ()
    
    @property
    def hierarchy(self) -> Dict[str, Any]:
        """
        Return the semantic hierarchy representation.
        
        Purpose is at the highest level of the intentional hierarchy.
        """
        return {
            "level": 0,
            "name": "Purpose",
            "description": "Ultimate aim, highest level semantic justification",
            "children": ["Mission"],
            "parent": None,
        }


__all__ = [
    "PurposeCoordinationStatus",
    "PurposeCoordination",
]