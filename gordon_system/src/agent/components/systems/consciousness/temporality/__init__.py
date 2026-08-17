# Gordon Phase 5.7.4-I: Temporal Context Engine - Package Init
# ===============================================================================
"""
Temporal Context Engine package for bounded temporal context organization.

The Temporal Context Engine implements an engineering model inspired by Husserl's
retention-presentation-protention structure. It maintains continuity across
successive experiential fields without becoming memory, prediction, planning,
or reasoning.

This is NOT a model of phenomenal consciousness - it is a bounded, deterministic,
immutable temporal organization engine.
"""

from __future__ import annotations

from typing import Tuple

# Core types and exceptions
from .types import (
    TemporalContextType,
)
from .exceptions import (
    ContinuityViolation,
    SnapshotCorruption,
    TransitionFailure,
    InvalidRetentionReference,
    InvalidProtentionExpectation,
    InvalidContinuityWindow,
)

# Constants for configuration
from .constants import (
    MAX_RETENTION_HISTORY,
    MAX_PROTENTION_EXPECTATIONS,
    MAX_CONTINUITY_WINDOW_SIZE,
)
# Retention module - bounded previous-generation context references
from gordon.agent.components.systems.consciousnessretention import (
    RetentionRecord,
    RetentionRegistry,
    RetentionBoundaries,
)

# Presentation module - current Experiential Field reference
from gordon.agent.components.systems.consciousnesspresentation import (
    PresentationReference,
    PresentationValidator,
)

# Protention module - bounded immediate expectation tracking
from gordon.agent.components.systems.consciousnessprotention import (
    ProtentionExpectation,
    ProtentionSet,
    ProtentionBoundaries,
)

# Continuity window module - bounded temporal context organization
from gordon.agent.components.systems.consciousnesscontinuity_window import (
    ContinuityWindow,
    ContinuityWindowManager,
    ContinuityWindowBuilder,
)

# Snapshot module - immutable publications of temporal state
from gordon.agent.components.systems.consciousnesssnapshot import (
    TemporalSnapshot,
    TemporalSnapshotBuilder,
    SnapshotTransition,
)

# Transition module - atomic temporal state changes
from gordon.agent.components.systems.consciousnesstransition import (
    TemporalTransition,
    TransitionAuthority,
    TransitionResult,
)

# Validator module - temporal state validation
from gordon.agent.components.systems.consciousnessvalidator import (
    TemporalValidator,
)

# Engine module - canonical temporal context authority
from gordon.agent.components.systems.consciousnessengine import (
    TemporalContextEngine,
    TemporalDiagnosticsSnapshot,
    TemporalHealthSnapshot,
)

# Diagnostics and health are now exported from engine module

# Integrity module - integrity enforcer for validation
from gordon.agent.components.systems.consciousnessintegrity import (
    TemporalIntegrityEnforcer,
)


__all__: Tuple[str, ...] = (
    # Types and exceptions
    "TemporalContextType",
    "ContinuityViolation",
    "SnapshotCorruption",
    "TransitionFailure",
    "InvalidRetentionReference",
    "InvalidProtentionExpectation",
    "InvalidContinuityWindow",
    
    # Constants
    "MAX_RETENTION_HISTORY",
    "MAX_PROTENTION_EXPECTATIONS",
    "MAX_CONTINUITY_WINDOW_SIZE",
    
    # Core modules
    "RetentionRecord",
    "RetentionRegistry",
    "RetentionBoundaries",
    "PresentationReference",
    "PresentationValidator",
    "ProtentionExpectation",
    "ProtentionSet",
    "ProtentionBoundaries",
    "ContinuityWindow",
    "ContinuityWindowManager",
    "ContinuityWindowBuilder",
    "TemporalSnapshot",
    "TemporalSnapshotBuilder",
    "SnapshotTransition",
    "TemporalTransition",
    "TransitionAuthority",
    "TransitionResult",
    "TemporalValidator",
    
    # Canonical Engine
    "TemporalContextEngine",
)

# =============================================================================
# PACKAGE METADATA
# =============================================================================

__title__: str = "Gordon Temporal Context Engine"
"""Package title."""

__version__: str = "5.7.4-I"
"""Phase and build version."""

__docformat__: str = "google"
"""Documentation format."""