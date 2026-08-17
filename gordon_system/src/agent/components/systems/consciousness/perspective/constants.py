# Gordon Phase 5.7.6-I: Perspective Engine - Constants
# ===============================================================================
"""
Canonical constants for the Perspective Engine.

Defines perspective type values, state values, and other configuration
parameters that remain fixed across all perspective operations.
"""

from __future__ import annotations

from typing import Tuple


# =============================================================================
# PERSPECTIVE TYPES
# =============================================================================

PERSPECTIVE_TYPE_SELF = "self"
"""Self-perspective: Gordon's current first-person reference frame."""

PERSPECTIVE_TYPE_EXTERNAL_OBSERVER = "external_observer"
"""External observer perspective: third-party observation of the system."""

PERSPECTIVE_TYPE_SIMULATED = "simulated"
"""Simulated perspective: hypothetical or alternate state simulation."""

PERSPECTIVE_TYPE_HYPOTHETICAL = "hypothetical"
"""Hypothetical perspective: counterfactual reasoning context."""

VALID_PERSPECTIVE_TYPES: Tuple[str, ...] = (
    PERSPECTIVE_TYPE_SELF,
    PERSPECTIVE_TYPE_EXTERNAL_OBSERVER,
    PERSPECTIVE_TYPE_SIMULATED,
    PERSPECTIVE_TYPE_HYPOTHETICAL,
)
"""All valid perspective types."""


# =============================================================================
# ENGINE STATES
# =============================================================================

PERSPECTIVE_STATE_INITIALIZING = "initializing"
"""Engine is initializing."""

PERSPECTIVE_STATE_ACTIVE = "active"
"""Engine is active and processing perspective changes."""

PERSPECTIVE_STATE_TRANSITIONING = "transitioning"
"""Engine is in a transition state."""

PERSPECTIVE_STATE_SUSPENDED = "suspended"
"""Engine is temporarily suspended."""

PERSPECTIVE_STATE_TERMINATED = "terminated"
"""Engine has been terminated."""


# =============================================================================
# TRANSFORMATION TYPES
# =============================================================================

TRANSFORM_TYPE_SELF_TO_EXTERNAL = "self_to_external"
"""Transform from self-perspective to external observer."""

TRANSFORM_TYPE_EXTERNAL_TO_SELF = "external_to_self"
"""Transform from external observer back to self."""

TRANSFORM_TYPE_SIMULATED_TO_SELF = "simulated_to_self"
"""Transform simulated perspective to real self."""

TRANSFORM_TYPE_HYPOTHETICAL_TO_SELF = "hypothetical_to_self"
"""Transform hypothetical counterfactual to actual self."""

VALID_TRANSFORMATION_TYPES: Tuple[str, ...] = (
    TRANSFORM_TYPE_SELF_TO_EXTERNAL,
    TRANSFORM_TYPE_EXTERNAL_TO_SELF,
    TRANSFORM_TYPE_SIMULATED_TO_SELF,
    TRANSFORM_TYPE_HYPOTHETICAL_TO_SELF,
)
"""All valid transformation types."""


# =============================================================================
# SELF-REFERENCE KINDS
# =============================================================================

SELF_REFERENCE_KIND_AGENT = "agent"
"""Reference to the executing agent."""

SELF_REFERENCE_KIND_EXECUTING_CONTEXT = "executing_context"
"""Reference to the current execution context."""

SELF_REFERENCE_KIND_INTERNAL_ACTOR = "internal_actor"
"""Reference to internal actor within the system."""

VALID_SELF_REFERENCE_KINDS: Tuple[str, ...] = (
    SELF_REFERENCE_KIND_AGENT,
    SELF_REFERENCE_KIND_EXECUTING_CONTEXT,
    SELF_REFERENCE_KIND_INTERNAL_ACTOR,
)
"""All valid self-reference kinds."""


# =============================================================================
# TRANSITION KINDS
# =============================================================================

TRANSITION_KIND_INITIALIZATION = "initialization"
"""Perspective initialization."""

TRANSITION_KIND_VIEWPOINT_SHIFT = "viewpoint_shift"
"""Viewpoint or perspective type change."""

TRANSITION_KIND_OBSERVER_UPDATE = "observer_update"
"""Observer state update without full transition."""

TRANSITION_KIND_INTERRUPTION = "interruption"
"""Temporary interruption of current perspective."""

TRANSITION_KIND_RESUME = "resume"
"""Resume from interruption."""

TRANSITION_KIND_DEGRADATION = "degradation"
"""Perspective degradation mode activation."""


# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

MAX_PERSPECTIVE_TYPES: int = 10
"""Maximum number of perspective types to track in diagnostics."""

MAX_TRANSFORMATIONS_PER_GENERATION: int = 50
"""Maximum transformations allowed per context generation."""

DEFAULT_SNAPSHOT_HISTORY_SIZE: int = 1000
"""Default size for snapshot history replay buffer."""

DEFAULT_OBSERVER_CAPACITY: int = 100
"""Default maximum concurrent conscious items for observer."""

TRUST_LEVELS: Tuple[str, ...] = ("low", "medium", "high")
"""Valid trust level values."""

PRIVACY_LEVELS: Tuple[str, ...] = ("internal", "restricted", "confidential")
"""Valid privacy level values."""


# =============================================================================
# METRICS CONSTANTS
# =============================================================================

METRIC_TRANSITION_COUNT = "transitions_total"
"""Metric: total perspective transitions."""

METRIC_TRANSFORMATION_COUNT = "transformations_total"
"""Metric: total viewpoint transformations."""

METRIC_SNAPSHOTS_PUBLISHED = "snapshots_published"
"""Metric: number of snapshots published."""

METRIC_INVALID_TRANSITIONS = "invalid_transitions"
"""Metric: count of rejected transitions."""

METRIC_AVERAGE_LATENCY_MS = "average_transition_latency_ms"
"""Metric: average transition latency in milliseconds."""

METRIC_OBSERVER_CHANGES = "observer_changes"
"""Metric: number of observer state changes."""


# =============================================================================
# SCHEMA VERSION
# =============================================================================

SCHEMA_VERSION: str = "5.7.6"
"""Current schema version for perspective snapshots."""