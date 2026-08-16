"""
Oriented Network Audit Constants

Defines audit severity levels, finding kinds, recommendation kinds,
and other constant values used throughout the audit subsystem.
"""

# =============================================================================
# AUDIT SEVERITY LEVELS
# =============================================================================

AUDIT_SEVERITY_CRITICAL = "critical"
"""
Critical severity - indicates severe structural or semantic damage that
requires immediate attention. The graph may be unusable for cognition.
"""

AUDIT_SEVERITY_HIGH = "high"
"""
High severity - indicates significant problems that will likely affect
cognitive operations. Should be addressed soon.
"""

AUDIT_SEVERITY_MEDIUM = "medium"
"""
Medium severity - indicates notable issues that should be investigated
and corrected. May impact some cognitive operations.
"""

AUDIT_SEVERITY_LOW = "low"
"""
Low severity - indicates minor issues that don't directly affect
functionality but should be reviewed for long-term health.
"""

AUDIT_SEVERITY_INFO = "info"
"""
Informational - indicates observations that may be useful for
understanding graph structure but are not problematic.
"""

# =============================================================================
# FINDING KINDS
# =============================================================================

FINDING_KIND_STRUCTURE = "structural"
"""
Structural findings relate to invalid nodes, edges, or their references.
Examples: dangling references, duplicate IDs, missing identifiers.
"""

FINDING_KIND_TOPOLOGY = "topology"
"""
Topology findings relate to graph structure properties like cycles,
connectivity patterns, and branching anomalies.
"""

FINDING_KIND_SEMANTIC = "semantic"
"""
Semantic findings relate to logical consistency, compatibility, and
meaning preservation in relationships.
"""

FINDING_KIND_CONNECTIVITY = "connectivity"
"""
Connectivity findings relate to graph connectivity properties including
isolated nodes, unreachable components, and missing paths.
"""

# =============================================================================
# RECOMMENDATION KINDS
# =============================================================================

RECOMMENDATION_REMOVE_EDGE = "remove_edge"
"""Remove a specific edge from the graph."""

RECOMMENDATION_ADD_EDGE = "add_edge"
"""Add a new edge to repair or improve connectivity."""

RECOMMENDATION_VERIFY_EDGE = "verify_edge"
"""Verify that an edge exists and is valid before proceeding."""

RECOMMENDATION_VERIFY_NODE = "verify_node"
"""Verify that a node exists and is valid before proceeding."""

RECOMMENDATION_REBUILD_SUBGRAPH = "rebuild_subgraph"
"""Rebuild an entire subgraph component from scratch."""

RECOMMENDATION_MERGE_DUPLICATES = "merge_duplicates"
"""Merge duplicate or equivalent graph components."""

RECOMMENDATION_BREAK_CYCLE = "break_cycle"
"""Break a cycle to restore acyclicity requirements."""

RECOMMENDATION_VERIFY_CAUSAL_CHAIN = "verify_causal_chain"
"""Verify the integrity of causal chains in the graph."""

RECOMMENDATION_VERIFY_HIERARCHY = "verify_hierarchy"
"""Verify hierarchical relationships and constraints."""

RECOMMENDATION_REQUEST_HUMAN_REVIEW = "request_human_review"
"""
Request human review for findings that require judgment calls
or complex context.
"""

# =============================================================================
# DEFAULT VALUES
# =============================================================================

DEFAULT_AUDIT_SEVERITY_THRESHOLD = AUDIT_SEVERITY_MEDIUM
"""Default minimum severity to report findings."""

DEFAULT_AUDIT_MODE = "comprehensive"
"""Default audit mode - comprehensive analysis of all dimensions."""

DEFAULT_RECOMMENDATION_CONFIDENCE = 0.85
"""Default confidence threshold for recommendations."""

# =============================================================================
# METRIC NAMES
# =============================================================================

METRIC_NODE_COUNT = "node_count"
METRIC_EDGE_COUNT = "edge_count"
METRIC_DENSITY = "density"
METRIC_AVG_DEGREE = "avg_degree"
METRIC_DIAMETER = "diameter"
METRIC_AVG_PATH_LENGTH = "avg_path_length"
METRIC_SCC_COUNT = "strongly_connected_components"
METRIC_WCC_COUNT = "weakly_connected_components"
METRIC_CYCLE_COUNT = "cycle_count"
METRIC_MAX_DEPTH = "max_depth"
METRIC_LEAF_COUNT = "leaf_count"
METRIC_ROOT_COUNT = "root_count"

__all__ = [
    # Audit Severity
    "AUDIT_SEVERITY_CRITICAL",
    "AUDIT_SEVERITY_HIGH",
    "AUDIT_SEVERITY_MEDIUM",
    "AUDIT_SEVERITY_LOW",
    "AUDIT_SEVERITY_INFO",
    # Finding Kinds
    "FINDING_KIND_STRUCTURE",
    "FINDING_KIND_TOPOLOGY",
    "FINDING_KIND_SEMANTIC",
    "FINDING_KIND_CONNECTIVITY",
    # Recommendation Kinds
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
    # Default Values
    "DEFAULT_AUDIT_SEVERITY_THRESHOLD",
    "DEFAULT_AUDIT_MODE",
    "DEFAULT_RECOMMENDATION_CONFIDENCE",
    # Metric Names
    "METRIC_NODE_COUNT",
    "METRIC_EDGE_COUNT",
    "METRIC_DENSITY",
    "METRIC_AVG_DEGREE",
    "METRIC_DIAMETER",
    "METRIC_AVG_PATH_LENGTH",
    "METRIC_SCC_COUNT",
    "METRIC_WCC_COUNT",
    "METRIC_CYCLE_COUNT",
    "METRIC_MAX_DEPTH",
    "METRIC_LEAF_COUNT",
    "METRIC_ROOT_COUNT",
]