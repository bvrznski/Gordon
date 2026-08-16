# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Observation Queries
===================

Query models for requesting observations.

QUERY LAWS (from spec)
----------------------
QUERY-LAW-001: Queries shall remain read-only.
QUERY-LAW-002: Query scope shall remain explicit.
QUERY-LAW-003: Historical observations shall remain queryable.
QUERY-LAW-004: Query results shall preserve provenance.
QUERY-LAW-005: Query findings shall remain explicit.
QUERY-LAW-006: Query limitations shall remain explicit.
QUERY-LAW-007: Queries shall remain side-effect free.
QUERY-LAW-008: Query execution shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# =============================================================================
# QUERY TYPES
# =============================================================================

class QueryType(Enum):
    """
    Canonical types of observatory queries.
    
    QUERY-LAW-001: Queries remain read-only.
    QUERY-LAW-002: Query scope remains explicit.
    """
    CURRENT_HEALTH = "current_health"
    """Current health status of the system."""
    
    HEALTH_HISTORY = "health_history"
    """Historical health trends."""
    
    PERFORMANCE_HISTORY = "performance_history"
    """Performance metrics over time."""
    
    ACTIVE_ANOMALIES = "active_anomalies"
    """Currently active anomalies."""
    
    ACTIVE_BOTTLENECKS = "active_bottlenecks"
    """Currently identified bottlenecks."""
    
    TREND_HISTORY = "trend_history"
    """Historical trends in metrics."""
    
    NETWORK_HEALTH = "network_health"
    """Health of individual networks."""
    
    GOAL_HEALTH = "goal_health"
    """Health of goals and objectives."""
    
    UNKNOWN = "unknown"
    """Unknown query type."""


# =============================================================================
# OBSERVATORY QUERY
# =============================================================================

@dataclass(frozen=True, slots=True)
class ObservatoryQuery:
    """
    Immutable query for observatory data.
    
    QUERY-LAW-001: Queries remain read-only (no side effects).
    QUERY-LAW-002: Query scope remains explicit.
    """
    
    query_identity: str
    """Unique identifier for this query."""
    
    query_type: str = "unknown"
    """Type of query (from QueryType)."""
    
    observed_scope: str = ""
    """Scope being queried."""
    
    observation_window: tuple[int, int] = field(default_factory=lambda: (0, 1))
    """Temporal window for the query."""
    
    requested_metrics: tuple[str, ...] = ()
    """Specific metrics to include in results."""
    
    filtering_policy: str = "include_all"
    """Policy for filtering results."""
    
    aggregation_policy: str = "none"
    """Policy for aggregating results."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this query."""
    
    def __post_init__(self):
        """Validate query components."""
        if not self.query_identity:
            raise ValueError("Query identity cannot be empty")
        
        valid_filter_policies = {"include_all", "exclude_unchanged", "only_changes"}
        if self.filtering_policy not in valid_filter_policies:
            raise ValueError(f"Invalid filtering policy: {self.filtering_policy}")
    
    @classmethod
    def create(
        cls,
        query_type: str,
        observed_scope: str = "",
        observation_window: tuple[int, int] = (0, 1),
        requested_metrics: tuple[str, ...] = (),
        filtering_policy: str = "include_all",
        provenance: Optional[dict[str, str]] = None,
    ) -> ObservatoryQuery:
        """
        Create a new observatory query.
        
        Args:
            query_type: Type of query (from QueryType)
            observed_scope: Scope being queried
            observation_window: Temporal window for the query
            requested_metrics: Specific metrics to include
            filtering_policy: Policy for filtering results
            provenance: Optional provenance dictionary
            
        Returns:
            New ObservatoryQuery instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"query:{query_type}:{observed_scope}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            query_identity=f"query:{identity_hash}",
            query_type=query_type,
            observed_scope=observed_scope,
            observation_window=observation_window,
            requested_metrics=requested_metrics,
            filtering_policy=filtering_policy,
            provenance=provenance or {},
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert query to dictionary."""
        return {
            "query_identity": self.query_identity,
            "query_type": self.query_type,
            "observed_scope": self.observed_scope,
            "observation_window": list(self.observation_window),
            "requested_metrics": list(self.requested_metrics),
            "filtering_policy": self.filtering_policy,
            "aggregation_policy": self.aggregation_policy,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObservatoryQuery:
        """Create query from dictionary."""
        return cls(
            query_identity=data["query_identity"],
            query_type=data.get("query_type", "unknown"),
            observed_scope=data.get("observed_scope", ""),
            observation_window=tuple(data.get("observation_window", [0, 1])),
            requested_metrics=tuple(data.get("requested_metrics", [])),
            filtering_policy=data.get("filtering_policy", "include_all"),
            aggregation_policy=data.get("aggregation_policy", "none"),
            provenance=dict(data.get("provenance", {})),
        )