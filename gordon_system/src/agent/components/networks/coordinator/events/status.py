# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Status Enumeration - Lifecycle State of Events

This module defines the canonical status states that events can occupy
through their lifecycle from creation to archival.
"""

from enum import Enum, unique


@unique
class CognitiveEventStatus(Enum):
    """
    Canonical enumeration of cognitive event statuses.
    
    Every event transitions through one or more status values during its lifecycle:
    OCCURRED -> VALIDATED -> PUBLISHED -> ARCHIVED
    
    Revisions create new events; they don't modify existing ones.
    
    EVENT STATUS LAWS (STATUS-LAW)
    ------------------------------
    STATUS-LAW-001: Every event has exactly one current status
    STATUS-LAW-002: Status transitions follow the defined lifecycle
    STATUS-LAW-003: Published events never mutate
    STATUS-LAW-004: Historical statuses remain inspectable
    STATUS-LAW-005: Invalid states are explicit
    """
    
    OCCURRED = "occurred"
    """Event has been created but not yet validated."""
    
    VALIDATED = "validated"
    """Event has passed validation and is ready for publication."""
    
    PUBLISHED = "published"
    """Event is published and available for consumers."""
    
    SUPERSEDED = "superseded"
    """Event has been replaced by a revision. The original event remains in history."""
    
    HISTORICAL = "historical"
    """Event has been archived into historical records."""
    
    INVALID = "invalid"
    """Event failed validation and is rejected."""
    
    ARCHIVED = "archived"
    """Event has been moved to long-term archival storage."""
    
    UNKNOWN = "unknown"
    """Fallback for unrecognized or uninitialized status."""


def get_status_from_name(name: str) -> "CognitiveEventStatus":
    """
    Convert a string name to its corresponding CognitiveEventStatus.
    
    Args:
        name: The string identifier of the status
        
    Returns:
        The corresponding CognitiveEventStatus enum value
        
    Raises:
        ValueError: If no matching status is found
    """
    try:
        return CognitiveEventStatus(name)
    except ValueError:
        raise ValueError(
            f"Unknown event status name: '{name}'. "
            f"Valid statuses: {[status.value for status in CognitiveEventStatus]}"
        )


def get_status_name(status: "CognitiveEventStatus") -> str:
    """
    Convert a CognitiveEventStatus to its string identifier.
    
    Args:
        status: The CognitiveEventStatus enum value
        
    Returns:
        The string identifier of the status
    """
    return status.value


class StatusTransitionValidator:
    """
    Validates allowed transitions between event statuses.
    
    Event status transitions follow strict rules to maintain consistency:
    
    Valid Transition Paths:
    ----------------------
    1. Normal Lifecycle: OCCURRED -> VALIDATED -> PUBLISHED -> ARCHIVED
    
    2. Revision Path: PUBLISHED -> SUPERSEDED (creates new revision)
    
    3. Error Path: Any state -> INVALID (validation failure)
    
    4. Historical Path: Any published state -> HISTORICAL
    
    TRANSITION LAWS
    ---------------
    TRANS-LAW-001: OCCURRED may transition to VALIDATED or INVALID
    TRANS-LAW-002: VALIDATED may transition to PUBLISHED or INVALID
    TRANS-LAW-003: PUBLISHED may transition to ARCHIVED, SUPERSEDED, HISTORICAL, or INVALID
    TRANS-LAW-004: SUPERSEDED may transition to ARCHIVED, HISTORICAL, or INVALID
    TRANS-LAW-005: HISTORICAL is terminal; no further transitions allowed
    TRANS-LAW-006: INVALID is terminal; no further transitions allowed
    TRANS-LAW-007: ARCHIVED may transition to HISTORICAL or INVALID
    """
    
    # Valid transitions from each status
    _VALID_TRANSITIONS = {
        CognitiveEventStatus.OCCURRED: {CognitiveEventStatus.VALIDATED, CognitiveEventStatus.INVALID},
        CognitiveEventStatus.VALIDATED: {CognitiveEventStatus.PUBLISHED, CognitiveEventStatus.INVALID},
        CognitiveEventStatus.PUBLISHED: {CognitiveEventStatus.ARCHIVED, CognitiveEventStatus.SUPERSEDED,
                                          CognitiveEventStatus.HISTORICAL, CognitiveEventStatus.INVALID},
        CognitiveEventStatus.SUPERSEDED: {CognitiveEventStatus.ARCHIVED, CognitiveEventStatus.HISTORICAL,
                                           CognitiveEventStatus.INVALID},
        CognitiveEventStatus.HISTORICAL: set(),  # Terminal state
        CognitiveEventStatus.INVALID: set(),     # Terminal state
        CognitiveEventStatus.ARCHIVED: {CognitiveEventStatus.HISTORICAL, CognitiveEventStatus.INVALID},
        CognitiveEventStatus.UNKNOWN: set(),
    }
    
    @classmethod
    def is_valid_transition(cls, from_status: "CognitiveEventStatus", to_status: "CognitiveEventStatus") -> bool:
        """
        Check if a status transition is allowed.
        
        Args:
            from_status: The current status
            to_status: The target status
            
        Returns:
            True if the transition is valid, False otherwise
        """
        return to_status in cls._VALID_TRANSITIONS.get(from_status, set())
    
    @classmethod
    def validate_transition(cls, from_status: "CognitiveEventStatus", to_status: "CognitiveEventStatus") -> bool:
        """
        Validate a status transition and raise if invalid.
        
        Args:
            from_status: The current status
            to_status: The target status
            
        Returns:
            True if the transition is valid
            
        Raises:
            ValueError: If the transition is not allowed
        """
        if cls.is_valid_transition(from_status, to_status):
            return True
        
        raise ValueError(
            f"Invalid status transition from '{from_status.value}' to '{to_status.value}'. "
            f"Valid transitions from {from_status.value}: {[s.value for s in cls._VALID_TRANSITIONS.get(from_status, set())]}"
        )
    
    @classmethod
    def is_terminal(cls, status: "CognitiveEventStatus") -> bool:
        """
        Check if a status is terminal (no further transitions allowed).
        
        Args:
            status: The status to check
            
        Returns:
            True if the status is terminal
        """
        return len(cls._VALID_TRANSITIONS.get(status, set())) == 0
    
    @classmethod
    def get_terminal_statuses(cls) -> set["CognitiveEventStatus"]:
        """
        Get all terminal status values.
        
        Returns:
            Set of terminal CognitiveEventStatus values
        """
        return {status for status in CognitiveEventStatus 
                if cls.is_terminal(status)}