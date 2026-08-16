# Oriented Network Coordination Base Interface
# =============================================

"""
Base coordination interface for Phase 4.7.5

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-001: The Oriented Network coordinates intentional orientation.
        It never owns intentional artefacts.

ARCHITECTURAL PRINCIPLES:
    - Base interface for all coordination contracts
    - Immutable contract definitions
    - No runtime execution or scheduling
    - Semantic reference only

COGNITIVE ARCHITECTURE: PHASE 4.7.5
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


# =============================================================================
# COORDINATION OWNERSHIP TYPES
# =============================================================================

CoordinationOwner = str
"""
Architectural owner of a coordinated concept.

Format: "subsystem_name" or "external:<source>"
Examples:
    "oriented_network"
    "goal_system"
    "planning_subsystem"
"""


class CoordinationAuthority(ABC):
    """
    Authority interface for coordination contracts.
    
    Defines what authority owns and controls each coordinated concept.
    
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-010: Ownership shall never overlap.
        ORIENTED-COORDINATION-LAW-013: Every reference shall be explicit.
    """
    
    @property
    @abstractmethod
    def owner(self) -> CoordinationOwner:
        """Return the architectural owner of this coordination."""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def authority(self) -> str:
        """Return the source of authority for this coordination."""
        raise NotImplementedError


# =============================================================================
# BASE COORDINATOR INTERFACE
# =============================================================================

@dataclass(frozen=True)
class BaseCoordinator(ABC):
    """
    Abstract base class for all Oriented Network Coordination contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BC-INV-001: Coordination never owns intentional artefacts
        BC-INV-002: Coordination is deeply immutable (frozen dataclass)
        BC-INV-003: Coordination possesses stable semantic identity
        BC-INV-004: Coordination possesses explicit ownership reference
        
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-001: The Oriented Network coordinates intentional orientation.
            It never owns intentional artefacts.
        ORIENTED-COORDINATION-LAW-002 through 040: Additional coordination laws
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this coordination contract"""
    
    revision: int = field(default=1)
    """Semantic revision number (starts at 1)"""
    
    version: int = field(default=1)
    """Schema version for compatibility"""
    
    owner: CoordinationOwner = field(default="oriented_network")
    """Architectural owner of the coordinated concept"""
    
    authority: str = field(default="semantic")
    """Source of authority for this coordination"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize coordination contract to dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization.
            
        INVARIANT: Serialization must be deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseCoordinator:
        """
        Create coordination contract from dictionary.
        
        Args:
            data: Dictionary produced by to_dict()
            
        Returns:
            New instance of the coordination type
            
        INVARIANT: from_dict(to_dict(x)) == x for valid inputs
        """
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate coordination contract against semantic requirements.
        
        Returns:
            (is_valid, list_of_errors) tuple
            
        INVARIANT: Validation is deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def references(self) -> Tuple[str, ...]:
        """
        Return explicit references to externally owned concepts.
        
        Returns:
            Tuple of reference identifiers (Goal IDs, Objective IDs, etc.)
            
        SEMANTIC LAWS (Phase 4.7.5):
            ORIENTED-COORDINATION-LAW-013: Every reference shall be explicit
            ORIENTED-COORDINATION-LAW-014: Every dependency shall be explicit
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def hierarchy(self) -> Dict[str, Any]:
        """
        Return the semantic hierarchy representation.
        
        Returns:
            Dictionary containing hierarchy information:
                - levels: Mapping of concept to hierarchy level
                - relationships: Parent-child relationships
            
        SEMANTIC LAWS (Phase 4.7.5):
            ORIENTED-COORDINATION-LAW-014: Every dependency shall be explicit
            ORIENTED-COORDINATION-LAW-037: Semantic hierarchy shall remain acyclic
        """
        raise NotImplementedError
    
    def __post_init__(self) -> None:
        """Validate coordination on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid {self.__class__.__name__} coordination:\n{error_list}"
            )


# =============================================================================
# COORDINATION STATUS ENUMS
# =============================================================================

class CoordinationStatus(ABC):
    """
    Coordination status indicators.
    
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-031: Behavioural phases shall consume coordination 
            contracts rather than redefine them.
    """
    
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
    
    @classmethod
    def all_values(cls) -> Tuple[str, ...]:
        """Return all valid status values."""
        return (cls.ACTIVE, cls.INACTIVE, cls.SUSPENDED, cls.CANDIDATE, cls.HISTORICAL)


__all__ = [
    # Types
    "CoordinationOwner",
    # Base interfaces
    "CoordinationAuthority",
    "BaseCoordinator",
    # Status enums
    "CoordinationStatus",
]