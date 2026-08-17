# Gordon Phase 5.7.8-I: Conscious Integration - Constants
# ===============================================================================

"""
Integration layer constants and defaults.
"""

from __future__ import annotations

from typing import Tuple


# =============================================================================
# ENGINE IDENTITIES (canonical)
# =============================================================================

ENGINE_ID_EXPERIENTIAL_FIELD = "experiential_field"
"""Experiential Field engine identity."""

ENGINE_ID_INTENTIONAL_CONTEXT = "intentional_context"
"""Intentional Context engine identity."""

ENGINE_ID_TEMPORAL_CONTEXT = "temporal_context"
"""Temporal Context engine identity."""

ENGINE_ID_PRESENCE = "presence"
"""Presence engine identity."""

ENGINE_ID_AWARENESS = "awareness"
"""Awareness engine identity."""

ENGINE_ID_PERSPECTIVE = "perspective"
"""Perspective engine identity."""

ENGINE_ID_SITUATED_WORLD = "situated_world"
"""Situated World engine identity."""

ENGINE_ID_CONSCIOUS_INTEGRATION = "conscious_integration"
"""Conscious Integration engine identity (this layer)."""

ALL_ENGINE_IDS: Tuple[str, ...] = (
    ENGINE_ID_EXPERIENTIAL_FIELD,
    ENGINE_ID_INTENTIONAL_CONTEXT,
    ENGINE_ID_TEMPORAL_CONTEXT,
    ENGINE_ID_PRESENCE,
    ENGINE_ID_AWARENESS,
    ENGINE_ID_PERSPECTIVE,
    ENGINE_ID_SITUATED_WORLD,
    ENGINE_ID_CONSCIOUS_INTEGRATION,
)

# =============================================================================
# REQUIRED ENGINES
# =============================================================================

REQUIRED_ENGINE_IDS: Tuple[str, ...] = (
    ENGINE_ID_EXPERIENTIAL_FIELD,
    ENGINE_ID_PRESENCE,
    ENGINE_ID_PERSPECTIVE,
)
"""Engines required for healthy composite context."""

OPTIONAL_ENGINE_IDS: Tuple[str, ...] = (
    ENGINE_ID_INTENTIONAL_CONTEXT,
    ENGINE_ID_TEMPORAL_CONTEXT,
    ENGINE_ID_AWARENESS,
    ENGINE_ID_SITUATED_WORLD,
)

# =============================================================================
# DEPENDENCY ORDER (canonical linear pipeline)
# =============================================================================

DEPENDENCY_ORDER: Tuple[str, ...] = (
    ENGINE_ID_EXPERIENTIAL_FIELD,
    ENGINE_ID_INTENTIONAL_CONTEXT,
    ENGINE_ID_TEMPORAL_CONTEXT,
    ENGINE_ID_PRESENCE,
    ENGINE_ID_AWARENESS,
    ENGINE_ID_PERSPECTIVE,
    ENGINE_ID_SITUATED_WORLD,
    ENGINE_ID_CONSCIOUS_INTEGRATION,
)
"""Deterministic engine dependency order."""

# =============================================================================
# INTEGRATION STRATA
# =============================================================================

STRATUM_SOURCE_INGESTION = "stratum_source_ingestion"
"""Stratum 1: Collect validated external contributions and projections."""

STRATUM_EXPERIENTIAL_CONSTRUCTION = "stratum_experiential_construction"
"""Stratum 2: Build or obtain committed Experiential Field state."""

STRATUM_INTENTIONAL_TEMPORAL = "stratum_intentional_temporal"
"""Stratum 3: Build or obtain committed Intentional and Temporal state."""

STRATUM_ACCESSIBILITY_ORGANIZATION = "stratum_accessibility_organization"
"""Stratum 4: Build or obtain committed Presence and Awareness state."""

STRATUM_AGENT_RELATIVE = "stratum_agent_relative"
"""Stratum 5: Build or obtain committed Perspective state."""

STRATUM_ENVIRONMENT_ORGANIZATION = "stratum_environment_organization"
"""Stratum 6: Build or obtain committed Situated World state."""

STRATUM_COMPOSITE_VALIDATION = "stratum_composite_validation"
"""Stratum 7: Validate cross-engine references and invariants."""

STRATUM_PARENT_PUBLICATION = "stratum_parent_publication"
"""Stratum 8: Atomically publish the composite Consciousness snapshot."""

ALL_STRATA: Tuple[str, ...] = (
    STRATUM_SOURCE_INGESTION,
    STRATUM_EXPERIENTIAL_CONSTRUCTION,
    STRATUM_INTENTIONAL_TEMPORAL,
    STRATUM_ACCESSIBILITY_ORGANIZATION,
    STRATUM_AGENT_RELATIVE,
    STRATUM_ENVIRONMENT_ORGANIZATION,
    STRATUM_COMPOSITE_VALIDATION,
    STRATUM_PARENT_PUBLICATION,
)

# =============================================================================
# INTEGRATION STATES
# =============================================================================

INTEGRATION_STATE_IDLE = "idle"
"""Integration layer not actively processing."""

INTEGRATION_STATE_COLLECTING_SNAPSHOTS = "collecting_snapshots"
"""Collecting committed engine snapshots or references."""

INTEGRATION_STATE_VALIDATING = "validating"
"""Validating generation alignment and cross-engine invariants."""

INTEGRATION_STATE_COMPOSING = "composing"
"""Building composite snapshot from collected references."""

INTEGRATION_STATE_PUBLISHING = "publishing"
"""Atomically publishing the new parent context generation."""

# =============================================================================
# CONSISTENCY LEVELS
# =============================================================================

CONSISTENCY_LEVEL_STRICT = "strict"
"""All required engines must be available, no staleness allowed."""

CONSISTENCY_LEVEL_BOUNDED_STALENESS = "bounded_staleness"
"""Allowed limited generation lag within policy bounds."""

CONSISTENCY_LEVEL_DEGRADED_COMPATIBLE = "degraded_compatible"
"""Accept degraded states that remain compatible with invariants."""

CONSISTENCY_LEVEL_PARTIAL_OPTIONAL = "partial_optional"
"""Allow missing optional engines with explicit degradation markers."""

CONSISTENCY_LEVEL_RECOVERY_COMPOSITE = "recovery_composite"
"""Accept recovered state with appropriate degradation labels."""

ALL_CONSISTENCY_LEVELS: Tuple[str, ...] = (
    CONSISTENCY_LEVEL_STRICT,
    CONSISTENCY_LEVEL_BOUNDED_STALENESS,
    CONSISTENCY_LEVEL_DEGRADED_COMPATIBLE,
    CONSISTENCY_LEVEL_PARTIAL_OPTIONAL,
    CONSISTENCY_LEVEL_RECOVERY_COMPOSITE,
)

# =============================================================================
# DEGRADATION MODES
# =============================================================================

DEGRADATION_INTENTIONAL_UNAVAILABLE = "intentional_context_unavailable"
DEGRADATION_TEMPORAL_UNAVAILABLE = "temporal_context_unavailable"
DEGRADATION_AWARENESS_UNAVAILABLE = "awareness_unavailable"
DEGRADATION_SITUATED_WORLD_UNAVAILABLE = "situated_world_unavailable"
DEGRADATION_ENGINE_GENERATION_LAG = "engine_generation_lag"
DEGRADATION_UNRESOLVED_REFERENCE = "unresolved_reference"
DEGRADATION_LAST_VALID_RETAINED = "last_valid_context_retained"

# =============================================================================
# TRANSITION TRIGGERS
# =============================================================================

TRIGGER_SOURCE_UPDATE = "source_update"
TRIGGER_FIELD_TRANSITION = "field_transition"
TRIGGER_INTENTIONAL_TRANSITION = "intentional_transition"
TRIGGER_TEMPORAL_TRANSITION = "temporal_transition"
TRIGGER_PRESENCE_TRANSITION = "presence_transition"
TRIGGER_AWARENESS_TRANSITION = "awareness_transition"
TRIGGER_PERSPECTIVE_TRANSITION = "perspective_transition"
TRIGGER_WORLD_TRANSITION = "world_transition"
TRIGGER_ACTION_FEEDBACK = "action_feedback"
TRIGGER_EXPLICIT_REFRESH = "explicit_refresh"
TRIGGER_LIFECYCLE_RESUME = "lifecycle_resume"
TRIGGER_RECOVERY = "recovery"
TRIGGER_CONTINUITY_REBUILD = "continuity_rebuild"

# =============================================================================
# DEFAULT TIMEOUTS (seconds)
# =============================================================================

DEFAULT_SNAPSHOT_COLLECTION_TIMEOUT = 5.0
"""Maximum time to wait for engine snapshot collection."""

DEFAULT_VALIDATION_TIMEOUT = 2.0
"""Maximum time to wait for cross-engine validation."""

DEFAULT_COMPOSITION_TIMEOUT = 3.0
"""Maximum time to wait for composite snapshot construction."""