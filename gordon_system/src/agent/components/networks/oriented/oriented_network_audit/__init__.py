"""
Oriented Network Audit Subsystem

A production-quality, deterministic, explainable, replayable,
provenance-preserving audit system for directed cognitive networks.

This subsystem continuously validates the integrity of Gordon's
directed cognitive networks without owning or mutating them.
"""

from .__meta__ import (
    __title__,
    __version__,
    __author__,
    __email__,
    __description__,
    __license__,
)

from .config import AuditConfig, DEFAULT_AUDIT_CONFIG
from .constants import (
    AUDIT_SEVERITY_CRITICAL,
    AUDIT_SEVERITY_HIGH,
    AUDIT_SEVERITY_MEDIUM,
    AUDIT_SEVERITY_LOW,
    AUDIT_SEVERITY_INFO,
    FINDING_KIND_STRUCTURE,
    FINDING_KIND_TOPOLOGY,
    FINDING_KIND_SEMANTIC,
    FINDING_KIND_CONNECTIVITY,
    RECOMMENDATION_REMOVE_EDGE,
    RECOMMENDATION_ADD_EDGE,
    RECOMMENDATION_VERIFY_EDGE,
    RECOMMENDATION_VERIFY_NODE,
    RECOMMENDATION_REBUILD_SUBGRAPH,
    RECOMMENDATION_MERGE_DUPLICATES,
    RECOMMENDATION_BREAK_CYCLE,
    RECOMMENDATION_VERIFY_CAUSAL_CHAIN,
    RECOMMENDATION_VERIFY_HIERARCHY,
    RECOMMENDATION_REQUEST_HUMAN_REVIEW,
)

from .enums import (
    AuditSeverity,
    FindingKind,
    RecommendationKind,
    AuditStatus,
    HealthStatus,
)

from .exceptions import (
    AuditError,
    AuditConfigError,
    AuditExecutionError,
    AuditValidationError,
)

from .interfaces import (
    IGraphAdapter,
    IAuditor,
    IReportBuilder,
)

from .models import (
    GraphReference,
    GraphSnapshot,
    AuditRequest,
    AuditSession,
    Finding,
    StructuralFinding,
    SemanticFinding,
    TopologyFinding,
    ConnectivityFinding,
    GraphMetrics,
    AuditRecommendation,
    AuditReport,
    AuditHealth,
    AuditStatistics,
)

from .factories import (
    create_graph_snapshot,
    create_audit_request,
    create_audit_session,
    create_structural_finding,
    create_semantic_finding,
    create_topology_finding,
    create_connectivity_finding,
    create_recommendation,
    create_audit_report,
)

from .subsystem import OrientedNetworkAuditSubsystem

__all__ = [
    # Meta
    "__title__",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__license__",
    # Config & Constants
    "AuditConfig",
    "DEFAULT_AUDIT_CONFIG",
    "AUDIT_SEVERITY_CRITICAL",
    "AUDIT_SEVERITY_HIGH",
    "AUDIT_SEVERITY_MEDIUM",
    "AUDIT_SEVERITY_LOW",
    "AUDIT_SEVERITY_INFO",
    "FINDING_KIND_STRUCTURE",
    "FINDING_KIND_TOPOLOGY",
    "FINDING_KIND_SEMANTIC",
    "FINDING_KIND_CONNECTIVITY",
    "RECOMMENDATION_REMOVE_EDGE",
    "RECOMMENDATION_ADD_EDGE",
    "RECOMMENDATION_VERIFY_EDGE",
    "RECOMMENDATION_VERIFY_NODE",
    "RECOMMENDATION_REBUILD_SUBGRAPH",
    "RECOMMENDATION_MERGE_DUPLICATES",
    "RECOMMENDATION_BREAK_CYCLE",
    "RECOMMENDATION_VERIFY_CAUSAL_CHAIN",
    "RECOMMENDATION_VERIFY_HIERARCHY",
    "RECOMMENDATION_REQUEST_HUMAN_REVIEW",
    # Enums
    "AuditSeverity",
    "FindingKind",
    "RecommendationKind",
    "AuditStatus",
    "HealthStatus",
    # Exceptions
    "AuditError",
    "AuditConfigError",
    "AuditExecutionError",
    "AuditValidationError",
    # Interfaces
    "IGraphAdapter",
    "IAuditor",
    "IReportBuilder",
    # Models
    "GraphReference",
    "GraphSnapshot",
    "AuditRequest",
    "AuditSession",
    "Finding",
    "StructuralFinding",
    "SemanticFinding",
    "TopologyFinding",
    "ConnectivityFinding",
    "GraphMetrics",
    "AuditRecommendation",
    "AuditReport",
    "AuditHealth",
    "AuditStatistics",
    # Factories
    "create_graph_snapshot",
    "create_audit_request",
    "create_audit_session",
    "create_structural_finding",
    "create_semantic_finding",
    "create_topology_finding",
    "create_connectivity_finding",
    "create_recommendation",
    "create_audit_report",
    # Subsystem
    "OrientedNetworkAuditSubsystem",
]