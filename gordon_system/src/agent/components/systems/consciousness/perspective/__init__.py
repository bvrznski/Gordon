# Gordon Phase 5.7.6-I: Perspective Engine - Package
# ===============================================================================
"""
Canonical Perspective Engine package.

The Perspective Engine maintains Gordon's current first-person computational
reference frame, determining reference origin, viewpoint, ownership attribution,
observer continuity, self-reference, and coordinate transformation.

Perspective is an engineering capability that does NOT imply phenomenal
self-awareness.
"""

from __future__ import annotations

from typing import Tuple

# Package metadata
__version__: str = "5.7.6"
"""Package version."""

__title__: str = "perspective_engine"
"""Package title."""

__doc__: str = """
Gordon Phase 5.7.6-I: Perspective Engine

The Perspective Engine establishes Gordon's active computational first-person
reference frame used to organize conscious contents from a self-perspective.

Key responsibilities:
    - Active perspective maintenance (origin, orientation, coordinate system)
    - Observer instance and state management
    - Self-reference tracking within the current perspective  
    - Deterministic viewpoint transformations
    - Immutable perspective snapshot publication
    
Not responsible for:
    - Identity construction or narrative
    - Affective state or personality
    - Memory storage or retrieval
    - Reasoning, planning, or execution
    - World model construction

Integration points:
    - Experiential Field (reference frame context)
    - Intentional Context (observer anchoring)
    - Temporal Context (continuity across generations)
    - Presence & Awareness (conscious accessibility)

See individual modules for detailed documentation.
"""

# Core imports (main API surface)
from gordon.agent.components.systems.consciousnessengine import PerspectiveEngine
from .constants import (
    PERSPECTIVE_TYPE_SELF,
    PERSPECTIVE_TYPE_EXTERNAL_OBSERVER,
    PERSPECTIVE_TYPE_SIMULATED,
    PERSPECTIVE_TYPE_HYPOTHETICAL,
    VALID_PERSPECTIVE_TYPES,
)

# Data types
from gordon.agent.components.systems.consciousnessreference_frame import ReferenceFrame, Orientation, Transformation
from gordon.agent.components.systems.consciousnessobserver import ObserverState, ObserverReference, Observer
from gordon.agent.components.systems.consciousnessself_reference import SelfReference, SelfReferenceValidator
from gordon.agent.components.systems.consciousnesstransformations import (
    TransformationDefinition,
    TransformationResult,
    TransformerEngine,
)
from gordon.agent.components.systems.consciousnesstransitions import TransitionState, TransitionBatch, TransitionLog
from gordon.agent.components.systems.consciousnesssnapshots import PerspectiveSnapshot, SnapshotBatch, SnapshotReplayEngine
from gordon.agent.components.systems.consciousnessvalidator import PerspectiveValidator
from gordon.agent.components.systems.consciousnessdiagnostics import Diagnostics

# Exceptions
from .exceptions import (
    PerspectiveError,
    ReferenceFrameError,
    InvalidReferenceFrame,
    FrameTransformError,
    ObserverError,
    InvalidObserverState,
    ObserverCapacityExceeded,
    TransformationError,
    InvalidTransformationType,
    TransformationConflict,
    TransitionError,
    InvalidTransition,
    TransitionConflict,
    ValidationError,
    InvalidPerspectiveState,
    InvalidSnapshot,
    DiagnosticsError,
    MetricCollectionFailure,
    IntegrityError,
    SnapshotCorruption,
)

__all__: Tuple[str, ...] = (
    # Engine
    "PerspectiveEngine",
    
    # Constants
    "PERSPECTIVE_TYPE_SELF",
    "PERSPECTIVE_TYPE_EXTERNAL_OBSERVER",
    "PERSPECTIVE_TYPE_SIMULATED",
    "PERSPECTIVE_TYPE_HYPOTHETICAL",
    "VALID_PERSPECTIVE_TYPES",
    
    # Data types
    "ReferenceFrame",
    "Orientation", 
    "Transformation",
    "ObserverState",
    "ObserverReference",
    "Observer",
    "SelfReference",
    "SelfReferenceValidator",
    "TransformationDefinition",
    "TransformationResult",
    "TransformerEngine",
    "TransitionState",
    "TransitionBatch",
    "TransitionLog",
    "PerspectiveSnapshot",
    "SnapshotBatch",
    "SnapshotReplayEngine",
    "PerspectiveValidator",
    "Diagnostics",
    
    # Exceptions
    "PerspectiveError",
    "ReferenceFrameError",
    "InvalidReferenceFrame",
    "FrameTransformError",
    "ObserverError",
    "InvalidObserverState",
    "ObserverCapacityExceeded",
    "TransformationError",
    "InvalidTransformationType",
    "TransformationConflict",
    "TransitionError",
    "InvalidTransition",
    "TransitionConflict",
    "ValidationError",
    "InvalidPerspectiveState",
    "InvalidSnapshot",
    "DiagnosticsError",
    "MetricCollectionFailure",
    "IntegrityError",
    "SnapshotCorruption",
)