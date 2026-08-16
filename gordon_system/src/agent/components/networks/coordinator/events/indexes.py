# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Index Types - Keys for Indexing Events

This module defines the canonical index keys used to organize and query events.
"""

from enum import Enum, unique


@unique
class EventIndexKey(Enum):
    """
    Canonical keys for indexing events.
    
    INDEX KEYS (INDEX-LAW)
    ----------------------
    INDEX-LAW-001: Each key identifies a specific event set
    INDEX-LAW-002: Indexes are derived from events, not owners of events
    INDEX-LAW-003: Multiple indexes may reference the same event
    """
    
    BY_IDENTITY = "by_identity"
    """Index events by their unique identity."""
    
    BY_KIND = "by_kind"
    """Index events by their kind/type."""
    
    BY_NETWORK = "by_network"
    """Index events by source network."""
    
    BY_GOAL = "by_goal"
    """Index events by goal identity."""
    
    BY_TASK = "by_task"
    """Index events by task identity."""
    
    BY_EPISODE = "by_episode"
    """Index events by episode identity."""
    
    BY_DOMAIN = "by_domain"
    """Index events by domain."""
    
    BY_IMPORTANCE = "by_importance"
    """Index events by importance level."""
    
    BY_STATUS = "by_status"
    """Index events by current status."""
    
    BY_CORRELATION = "by_correlation"
    """Index events by correlation identity."""
    
    BY_CAUSATION = "by_causation"
    """Index events by causation relationships."""
    
    BY_CYCLE = "by_cycle"
    """Index events by coordination cycle."""
    
    BY_EPOCH = "by_epoch"
    """Index events by epoch."""


def get_index_key_for_query_kind(query_kind: str) -> EventIndexKey | None:
    """
    Get the appropriate index key for a query kind.
    
    Args:
        query_kind: The query kind string
        
    Returns:
        The corresponding EventIndexKey, or None if no direct mapping
    """
    mapping = {
        "EVENT_LOOKUP": EventIndexKey.BY_IDENTITY,
        "EVENTS_BY_KIND": EventIndexKey.BY_KIND,
        "EVENTS_BY_NETWORK": EventIndexKey.BY_NETWORK,
        "EVENTS_BY_GOAL": EventIndexKey.BY_GOAL,
        "EVENTS_BY_TASK": EventIndexKey.BY_TASK,
        "EVENTS_BY_EPISODE": EventIndexKey.BY_EPISODE,
        "EVENTS_BY_DOMAIN": EventIndexKey.BY_DOMAIN,
    }
    
    return mapping.get(query_kind)