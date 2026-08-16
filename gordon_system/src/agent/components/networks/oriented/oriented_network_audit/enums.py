"""
Oriented Network Audit Enums

Defines enumeration types used throughout the audit subsystem.
"""

from enum import Enum, auto
from typing import FrozenSet


class AuditSeverity(Enum):
    """
    Severity levels for audit findings.
    
    Critical issues require immediate attention and may render the graph unusable.
    High severity indicates significant problems affecting cognitive operations.
    Medium severity indicates notable issues that should be investigated.
    Low severity indicates minor issues requiring review.
    Info is purely observational.
    """
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    
    @classmethod
    def from_string(cls, value: str) -> "AuditSeverity":
        """Convert a string to an AuditSeverity enum."""
        return cls(value)
    
    @property
    def priority(self) -> int:
        """
        Return numeric priority for severity comparison.
        
        Higher values indicate more severe issues.
        """
        priorities = {
            self.CRITICAL: 5,
            self.HIGH: 4,
            self.MEDIUM: 3,
            self.LOW: 2,
            self.INFO: 1,
        }
        return priorities[self]


class FindingKind(Enum):
    """
    Categories of audit findings.
    
    STRUCTURAL: Invalid nodes, edges, or references
    TOPOLOGY: Graph structure properties (cycles, connectivity)
    SEMANTIC: Logical consistency and meaning preservation
    CONNECTIVITY: Reachability and path issues
    """
    
    STRUCTURAL = "structural"
    TOPOLOGY = "topology"
    SEMANTIC = "semantic"
    CONNECTIVITY = "connectivity"
    
    @classmethod
    def from_string(cls, value: str) -> "FindingKind":
        """Convert a string to a FindingKind enum."""
        return cls(value)


class RecommendationKind(Enum):
    """
    Types of recommendations the audit system can generate.
    
    These are advisory only and never modify the graph directly.
    """
    
    REMOVE_EDGE = "remove_edge"
    ADD_EDGE = "add_edge"
    VERIFY_EDGE = "verify_edge"
    VERIFY_NODE = "verify_node"
    REBUILD_SUBGRAPH = "rebuild_subgraph"
    MERGE_DUPLICATES = "merge_duplicates"
    BREAK_CYCLE = "break_cycle"
    VERIFY_CAUSAL_CHAIN = "verify_causal_chain"
    VERIFY_HIERARCHY = "verify_hierarchy"
    REQUEST_HUMAN_REVIEW = "request_human_review"
    
    @classmethod
    def from_string(cls, value: str) -> "RecommendationKind":
        """Convert a string to a RecommendationKind enum."""
        return cls(value)


class AuditStatus(Enum):
    """
    Status values for audit sessions.
    
    PENDING: Audit has been requested but not started
    RUNNING: Audit is currently executing
    COMPLETED: Audit finished successfully
    FAILED: Audit encountered an error
    CANCELLED: Audit was cancelled before completion
    """
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HealthStatus(Enum):
    """
    Status values for subsystem health components.
    
    HEALTHY: Component is functioning normally
    DEGRADED: Component has issues but can still function
    UNHEALTHY: Component is not functional
    UNKNOWN: Health status cannot be determined
    """
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# =============================================================================
# IMMUTABLE SETS OF VALID VALUES
# =============================================================================

VALID_AUDIT_SEVERITIES: FrozenSet[str] = frozenset(
    severity.value for severity in AuditSeverity
)
"""
Immutable set of valid audit severity values.
"""

VALID_FINDING_KINDS: FrozenSet[str] = frozenset(
    kind.value for kind in FindingKind
)
"""
Immutable set of valid finding kind values.
"""

VALID_RECOMMENDATION_KINDS: FrozenSet[str] = frozenset(
    kind.value for kind in RecommendationKind
)
"""
Immutable set of valid recommendation kind values.
"""

__all__ = [
    "AuditSeverity",
    "FindingKind",
    "RecommendationKind",
    "AuditStatus",
    "HealthStatus",
    "VALID_AUDIT_SEVERITIES",
    "VALID_FINDING_KINDS",
    "VALID_RECOMMENDATION_KINDS",
]