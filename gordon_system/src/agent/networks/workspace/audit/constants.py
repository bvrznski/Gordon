# Gordon Workspace Network Audit Constants
# ========================================

"""
Core constants used throughout the Workspace Audit subsystem.
"""

from __future__ import annotations

from typing import Tuple, FrozenSet

# =============================================================================
# AUDIT CONFIGURATION CONSTANTS
# =============================================================================

DEFAULT_AUDIT_TIMEOUT_SECONDS: float = 30.0
"""Default timeout for audit sessions in seconds."""

MAX_FINDINGS_PER_AUDIT: int = 1000
"""Maximum number of findings allowed per audit session."""

MIN_CONFIDENCE_THRESHOLD: float = 0.5
"""Minimum confidence threshold for audit findings."""

DEFAULT_SEVERITY_FILTER: Tuple[str, ...] = ("critical", "high", "medium", "low")
"""Default severity levels to include in reports (excluding info)."""

# =============================================================================
# GRAPH VALIDATION CONSTANTS
# =============================================================================

MAX_GRAPH_DEPTH: int = 100
"""Maximum allowed depth for graph traversals."""

MAX_GRAPH_BRANCH_FACTOR: int = 50
"""Maximum branch factor for graph nodes."""

MAX_CYCLE_LENGTH: int = 20
"""Maximum cycle length to detect during graph validation."""

# =============================================================================
# NODE VALIDATION CONSTANTS
# =============================================================================

MIN_NODE_ID_LENGTH: int = 1
"""Minimum identifier length for nodes."""

MAX_NODE_ID_LENGTH: int = 256
"""Maximum identifier length for nodes."""

VALID_ACTIVATION_RANGE: Tuple[float, float] = (0.0, 1.0)
"""Valid range for node activation values."""

VALID_SALIENCE_RANGE: Tuple[float, float] = (0.0, 1.0)
"""Valid range for node salience values."""

# =============================================================================
# EDGE VALIDATION CONSTANTS
# =============================================================================

VALID_EDGE_WEIGHT_RANGE: Tuple[float, float] = (-1.0, 1.0)
"""Valid weight range for edges."""

MIN_EDGE_COUNT_PER_NODE: int = 0
"""Minimum required incoming or outgoing edges per node (except roots/leaves)."""

MAX_EDGES_PER_NODE: int = 1000
"""Maximum allowed edges connected to a single node."""

# =============================================================================
# ACTIVATION VALIDATION CONSTANTS
# =============================================================================

ACTIVATION_DECAY_RATE: float = 0.95
"""Default decay rate for activation values."""

ACTIVATION_PROPAGATION_LIMIT: float = 1.0
"""Maximum propagation of activation through edges."""

# =============================================================================
# SALIENCE VALIDATION CONSTANTS
# =============================================================================

SALIENCE_NORMALIZATION_EPSILON: float = 1e-6
"""Epsilon for floating-point comparison in salience normalization."""

MAX_SALIENCE_GAP: float = 0.5
"""Maximum allowed gap between consecutive salience values."""

# =============================================================================
# SYNCHRONIZATION CONSTANTS
# =============================================================================

DEFAULT_GRAPH_REVISION_INTERVAL_SECONDS: float = 5.0
"""Expected interval between graph revision updates."""

MAX_STALENESS_THRESHOLD_SECONDS: float = 60.0
"""Maximum age for synchronization snapshots before considered stale."""

# =============================================================================
# PROVENANCE VALIDATION CONSTANTS
# =============================================================================

MIN_PROVENANCE_CHAIN_LENGTH: int = 1
"""Minimum required length of provenance chains."""

MAX_PROVENANCE_CHAIN_DEPTH: int = 50
"""Maximum depth allowed in provenance chains."""

# =============================================================================
# LIFECYCLE VALIDATION CONSTANTS
# =============================================================================

VALID_LIFECYCLE_STATES: Tuple[str, ...] = (
    "pending",
    "active",
    "completed",
    "aborted",
    "archived",
)
"""Valid lifecycle states for workspace artifacts."""

MIN_REVISION_GAP: int = 1
"""Minimum gap between consecutive revisions."""

# =============================================================================
# METRICS AND MONITORING CONSTANTS
# =============================================================================

METRICS_RETENTION_COUNT: int = 1000
"""Number of metric records to retain in history."""

AUDIT_HISTORY_CAPACITY: int = 500
"""Maximum number of audit sessions to retain in history."""

HEALTH_CHECK_INTERVAL_SECONDS: float = 1.0
"""Interval between health status checks."""

# =============================================================================
# REPORT CONSTANTS
# =============================================================================

REPORT_TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"
"""ISO 8601 format for report timestamps."""

MAX_REPORT_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
"""Maximum size of audit reports in bytes."""

# =============================================================================
# VALIDATION DOMAINS ENUMERATION
# =============================================================================

AUDIT_VALIDATION_DOMAINS: Tuple[str, ...] = (
    "graph_topology",
    "node_integrity",
    "edge_integrity",
    "activation_consistency",
    "salience_consistency",
    "workspace_occupancy",
    "synchronization",
    "provenance",
    "temporal_consistency",
    "workspace_invariants",
    "duplicate_representations",
    "orphan_representations",
    "stale_representations",
    "resource_utilization",
    "lifecycle_correctness",
)

# =============================================================================
# IMMUTABLE VALID SETS
# =============================================================================

VALID_SEVERITIES: FrozenSet[str] = frozenset(
    ("critical", "high", "medium", "low", "info")
)
"""Immutable set of valid severity values."""

VALID_LIFECYCLE_STATE_SET: FrozenSet[str] = frozenset(VALID_LIFECYCLE_STATES)
"""Immutable set of valid lifecycle states."""

VALID_AUDIT_DOMAINS_SET: FrozenSet[str] = frozenset(AUDIT_VALIDATION_DOMAINS)
"""Immutable set of valid audit validation domains."""