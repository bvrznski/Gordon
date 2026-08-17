# Perception Projection - Shared Contracts
# ==========================================

"""
Shared contracts for the Perception Projection System.

Projection is the outer semantic publication layer of the Perception System.
It exposes validated perceptual artifacts to consumers without exposing internal complexity.
"""

from .identity import (
    PerceptionProjectionIdentity,
    ProjectionKind,
)

from .scope import (
    PerceptionProjectionScope,
    TemporalScope,
    SpatialScope,
    ModalityScope,
    ArtifactScope,
)

from .request import (
    PerceptionProjectionRequest,
    ProjectionUpdateMode,
    ConflictVisibility,
    AmbiguityVisibility,
    MissingEvidenceVisibility,
)

from .context import (
    ConsumerKind,
    PerceptionProjectionConsumerContract,
    PerceptionProjectionContext,
)

from .result import (
    PerceptionProjectionResult,
    ProjectionStatus,
    ProjectionSelectionRecord,
    SelectionStatus,
    FilterKind,
    PerceptionProjectionFilterRecord,
    LimitationKind,
    PerceptionProjectionLimitation,
)

__all__ = [
    "PerceptionProjectionIdentity",
    "ProjectionKind",
    "PerceptionProjectionScope",
    "TemporalScope",
    "SpatialScope",
    "ModalityScope",
    "ArtifactScope",
    "PerceptionProjectionRequest",
    "ProjectionUpdateMode",
    "ConflictVisibility",
    "AmbiguityVisibility",
    "MissingEvidenceVisibility",
    "ConsumerKind",
    "PerceptionProjectionConsumerContract",
    "PerceptionProjectionContext",
    "PerceptionProjectionResult",
    "ProjectionStatus",
    "ProjectionSelectionRecord",
    "SelectionStatus",
    "FilterKind",
    "PerceptionProjectionFilterRecord",
    "LimitationKind",
    "PerceptionProjectionLimitation",
]