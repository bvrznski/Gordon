# Gordon Workspace Network Audit Enums
# =====================================

"""
Enumeration types used throughout the Workspace Audit subsystem.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet


class AuditSeverity(Enum):
    """
    Severity levels for audit findings.
    
    CRITICAL: Graph unusable, immediate attention required
    HIGH: Significant problems affecting cognitive operations
    MEDIUM: Notable issues requiring investigation
    LOW: Minor issues requiring review
    INFO: Purely observational
    """
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    
    @classmethod
    def from_string(cls, value: str) -> AuditSeverity:
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
    
    @property
    def is_critical(self) -> bool:
        """Check if severity is critical."""
        return self == self.CRITICAL
    
    @property
    def is_high(self) -> bool:
        """Check if severity is high or critical."""
        return self in (self.CRITICAL, self.HIGH)


class FindingKind(Enum):
    """
    Categories of audit findings.
    
    STRUCTURAL: Invalid nodes, edges, or references
    TOPOLOGY: Graph structure properties (cycles, connectivity)
    SEMANTIC: Logical consistency and meaning preservation
    CONNECTIVITY: Reachability and path issues
    VALIDATION: Data validation failures
    INTEGRITY: State integrity violations
    """
    
    STRUCTURAL = "structural"
    TOPOLOGY = "topology"
    SEMANTIC = "semantic"
    CONNECTIVITY = "connectivity"
    VALIDATION = "validation"
    INTEGRITY = "integrity"
    
    @classmethod
    def from_string(cls, value: str) -> FindingKind:
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
    VERIFY_PROVENANCE_CHAIN = "verify_provenance_chain"
    VERIFY_HIERARCHY = "verify_hierarchy"
    REQUEST_HUMAN_REVIEW = "request_human_review"
    VALIDATE_ACTIVATION = "validate_activation"
    VALIDATE_SALIENCE = "validate_salience"
    CHECK_SYNCHRONIZATION = "check_synchronization"
    
    @classmethod
    def from_string(cls, value: str) -> RecommendationKind:
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


class AuditType(Enum):
    """
    Types of audit sessions.
    
    MANUAL: Requested by user/admin
    SCHEDULED: Periodic automated audit
    SNAPSHOT: Based on state snapshot
    INCREMENTAL: Only new/changed items since last audit
    FULL: Complete audit of entire graph
    DIAGNOSTIC: Detailed diagnostic audit with extended checks
    STARTUP: Audit performed at system startup
    SHUTDOWN: Audit performed before system shutdown
    """
    
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    SNAPSHOT = "snapshot"
    INCREMENTAL = "incremental"
    FULL = "full"
    DIAGNOSTIC = "diagnostic"
    STARTUP = "startup"
    SHUTDOWN = "shutdown"


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

VALID_AUDIT_STATUSES: FrozenSet[str] = frozenset(
    status.value for status in AuditStatus
)
"""
Immutable set of valid audit status values.
"""

VALID_HEALTH_STATUSES: FrozenSet[str] = frozenset(
    status.value for status in HealthStatus
)
"""
Immutable set of valid health status values.
"""

VALID_AUDIT_TYPES: FrozenSet[str] = frozenset(
    audit_type.value for audit_type in AuditType
)
"""
Immutable set of valid audit type values.
"""