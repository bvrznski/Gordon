# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Importance Enumeration - Priority Levels for Events

This module defines the canonical importance levels that events may have.
Importance guides downstream consumers but never changes event semantics.
"""

from enum import Enum, unique


@unique
class EventImportance(Enum):
    """
    Canonical enumeration of cognitive event importance levels.
    
    Importance levels guide downstream consumers in:
    - Filtering decisions
    - Processing priority
    - Storage strategy
    - Alerting thresholds
    
    Important: Importance never changes event validity or semantics.
    All published events are equally valid; importance is about relevance,
    not correctness.
    
    EVENT IMPORTANCE LAWS (IMPORTANCE-LAW)
    --------------------------------------
    IMPORTANCE-LAW-001: Every event has exactly one importance level
    IMPORTANCE-LAW-002: Importance never affects event validity
    IMPORTANCE-LAW-003: All published events are semantically valid
    IMPORTANCE-LAW-004: Importance is determined by semantic content
    """
    
    CRITICAL = "critical"
    """Event has maximum importance. Requires immediate attention.
    Examples:
    - System failure detected
    - Goal conflict that blocks progress
    - Security violation
    - Critical constraint violation"""
    
    HIGH = "high"
    """Event has high importance. Should be prioritized in processing.
    Examples:
    - New goal created
    - Major prediction update
    - Decision selected
    - Network recovery completed"""
    
    NORMAL = "normal"
    """Event has normal importance. Processed as part of standard workflow.
    Examples:
    - Routine workspace admission
    - Standard observation recorded
    - Minor salience change
    - Regular memory retrieval"""
    
    LOW = "low"
    """Event has low importance. May be batch-processed or deferred.
    Examples:
    - Background network activity
    - Minor confidence adjustment
    - Trace logging events
    - Diagnostic information"""
    
    BACKGROUND = "background"
    """Event has minimal importance. Only recorded for completeness.
    Examples:
    - Periodic heartbeat events
    - Debug-level events
    - Performance metrics
    - Internal state snapshots"""


def get_importance_from_name(name: str) -> "EventImportance":
    """
    Convert a string name to its corresponding EventImportance.
    
    Args:
        name: The string identifier of the importance level
        
    Returns:
        The corresponding EventImportance enum value
        
    Raises:
        ValueError: If no matching importance is found
    """
    try:
        return EventImportance(name)
    except ValueError:
        raise ValueError(
            f"Unknown event importance name: '{name}'. "
            f"Valid importance levels: {[imp.value for imp in EventImportance]}"
        )


def get_importance_name(importance: "EventImportance") -> str:
    """
    Convert a EventImportance to its string identifier.
    
    Args:
        importance: The EventImportance enum value
        
    Returns:
        The string identifier of the importance level
    """
    return importance.value


class ImportanceClassifier:
    """
    Classifies events by their semantic content and determines importance.
    
    This classifier examines event payload semantics to assign appropriate
    importance levels based on the cognitive significance of the occurrence.
    
    CLASSIFICATION LAWS
    -------------------
    CLASS-LAW-001: Classification is deterministic from semantic content
    CLASS-LAW-002: Same semantics always produce same importance
    CLASS-LAW-003: No randomness in classification
    """
    
    # Critical event kinds (always critical importance)
    _CRITICAL_KINDS = {
        "failure_detected",
        "conflict_detected", 
        "network_degraded",
    }
    
    # High importance event kinds
    _HIGH_KINDS = {
        "goal_created",
        "decision_selected",
        "plan_completed",
        "network_recovered",
        "barrier_released",
        "memory_encoded",
        "learning_started",
    }
    
    # Normal importance event kinds
    _NORMAL_KINDS = {
        "prediction_updated",
        "reward_estimated",
        "attention_shifted",
        "workspace_admission",
        "observation_recorded",
        "synchronization_completed",
        "transition_completed",
    }
    
    @classmethod
    def classify_by_kind(cls, kind: str) -> EventImportance:
        """
        Classify importance based on event kind.
        
        Args:
            kind: The event kind string identifier
            
        Returns:
            The appropriate importance level for this event kind
        """
        if kind in cls._CRITICAL_KINDS:
            return EventImportance.CRITICAL
        elif kind in cls._HIGH_KINDS:
            return EventImportance.HIGH
        elif kind in cls._NORMAL_KINDS:
            return EventImportance.NORMAL
        else:
            # Default to NORMAL for unknown kinds
            return EventImportance.NORMAL
    
    @classmethod
    def classify_event(cls, event_kind: str) -> EventImportance:
        """
        Classify an event by its kind and return importance.
        
        Args:
            event_kind: The CognitiveEventKind name
            
        Returns:
            The appropriate importance level
        """
        return cls.classify_by_kind(event_kind)


def get_default_importance_for_kind(kind: str) -> EventImportance:
    """
    Get the default importance for a given event kind.
    
    This function provides deterministic importance assignment based solely
    on semantic content, not runtime conditions.
    
    Args:
        kind: The event kind string identifier
        
    Returns:
        The default importance level for this event kind
    """
    return ImportanceClassifier.classify_by_kind(kind)