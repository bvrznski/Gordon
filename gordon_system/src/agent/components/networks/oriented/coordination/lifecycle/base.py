# Oriented Network Coordination Lifecycle Base Interface
# ======================================================

"""
Base interface for coordination lifecycle states (Phase 4.7.5)

SEMANTIC LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-031: Behavioural phases shall consume coordination 
        contracts rather than redefine them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from enum import Enum


# =============================================================================
# LIFECYCLE STATES PER COORDINATED CONCEPT
# =============================================================================

class PurposeLifecycleState(str, Enum):
    """Purpose lifecycle state indicators."""
    
    CANDIDATE = "candidate"
    """Proposed but not yet adopted"""
    
    ACTIVE = "active"
    """Currently oriented toward"""
    
    SUSPENDED = "suspended"
    """Temporarily paused"""
    
    COMPLETED = "completed"
    """Semantic satisfaction achieved"""
    
    ABANDONED = "abandoned"
    """Intentionally dropped"""
    
    HISTORICAL = "historical"
    """Previously active, now archived"""


class MissionLifecycleState(str, Enum):
    """Mission lifecycle state indicators."""
    
    CANDIDATE = "candidate"
    """Proposed mission orientation"""
    
    ACTIVE = "active"
    """Currently organized around"""
    
    SUSPENDED = "suspended"
    """Paused, may be resumed"""
    
    COMPLETED = "completed"
    """Mission objectives fulfilled"""
    
    ABANDONED = "abandoned"
    """No longer relevant"""
    
    HISTORICAL = "historical"
    """Archived mission state"""


class GoalLifecycleState(str, Enum):
    """Goal lifecycle state indicators."""
    
    CANDIDATE = "candidate"
    """Proposed goal target"""
    
    ACTIVE = "active"
    """Actively pursued"""
    
    SUSPENDED = "suspended"
    """Temporarily paused"""
    
    BLOCKED = "blocked"
    """Cannot proceed due to constraints"""
    
    COMPLETED = "completed"
    """Goal achievement verified"""
    
    ABANDONED = "abandoned"
    """No longer prioritized"""
    
    HISTORICAL = "historical"
    """Previously active, now archived"""


class ObjectiveLifecycleState(str, Enum):
    """Objective lifecycle state indicators."""
    
    CANDIDATE = "candidate"
    """Proposed intermediate target"""
    
    ACTIVE = "active"
    """Currently pursued"""
    
    SUSPENDED = "suspended"
    """Temporarily paused"""
    
    COMPLETED = "completed"
    """Objective achieved"""
    
    ABANDONED = "abandoned"
    """No longer relevant"""
    
    HISTORICAL = "historical"
    """Archived objective state"""


class TaskLifecycleState(str, Enum):
    """Task lifecycle state indicators."""
    
    CANDIDATE = "candidate"
    """Proposed executable action"""
    
    ACTIVE = "active"
    """Currently executed"""
    
    SUSPENDED = "suspended"
    """Paused execution"""
    
    BLOCKED = "blocked"
    """Cannot proceed"""
    
    COMPLETED = "completed"
    """Task finished"""
    
    CANCELLED = "cancelled"
    """Execution stopped"""
    
    HISTORICAL = "historical"
    """Previously active, now archived"""


# =============================================================================
# BASE LIFECYCLE STATE INTERFACE
# =============================================================================

@dataclass(frozen=True)
class BaseLifecycleState(ABC):
    """
    Abstract base class for coordination lifecycle states.
    
    ARCHITECTURAL PRINCIPLES:
        BC-INV-001: Lifecycle state never owns intentional artefacts
        BC-INV-002: Lifecycle state is deeply immutable (frozen dataclass)
        BC-INV-003: Lifecycle state possesses stable semantic identity
        
    SEMANTIC LAWS (Phase 4.7.5):
        ORIENTED-COORDINATION-LAW-031: Behavioural phases shall consume coordination 
            contracts rather than redefine them.
    """
    
    identity: str = field(default="unnamed_lifecycle")
    """Unique semantic identifier for this lifecycle state"""
    
    revision: int = field(default=1)
    """Semantic revision number (starts at 1)"""
    
    version: int = field(default=1)
    """Schema version for compatibility"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize lifecycle state to dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseLifecycleState:
        """
        Create lifecycle state from dictionary.
        
        Args:
            data: Dictionary produced by to_dict()
            
        Returns:
            New instance of the lifecycle type
        """
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate lifecycle state against semantic requirements.
        
        Returns:
            (is_valid, list_of_errors) tuple
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def current_state(self) -> str:
        """Return the current lifecycle state."""
        raise NotImplementedError
    
    def __post_init__(self) -> None:
        """Validate lifecycle on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid {self.__class__.__name__} lifecycle:\n{error_list}"
            )


# =============================================================================
# COORDINATION LIFECYCLE TRANSITIONS
# =============================================================================

class LifecycleTransition(Enum):
    """Lifecycle state transition types."""
    
    # General transitions
    ADOPT = "adopt"
    """Adopt from candidate to active"""
    
    SUSPEND = "suspend"
    """Suspend active state temporarily"""
    
    RESUME = "resume"
    """Resume suspended state"""
    
    COMPLETE = "complete"
    """Mark as completed (semantic satisfaction)"""
    
    ABANDON = "abandon"
    """Intentionally drop the concept"""
    
    REJECT = "reject"
    """Reject candidate without adoption"""
    
    # Goal-specific transitions
    BLOCK = "block"
    """Block goal from proceeding"""
    
    UNBLOCK = "unblock"
    """Unblock previously blocked goal"""
    
    # Task-specific transitions  
    CANCEL = "cancel"
    """Cancel task execution"""


__all__ = [
    # Lifecycle state enums
    "PurposeLifecycleState",
    "MissionLifecycleState",
    "GoalLifecycleState",
    "ObjectiveLifecycleState",
    "TaskLifecycleState",
    # Base interface
    "BaseLifecycleState",
    # Transitions
    "LifecycleTransition",
]