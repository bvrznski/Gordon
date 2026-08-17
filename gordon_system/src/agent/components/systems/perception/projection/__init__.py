# Perception Projection - Phase 5.2.4
# ===================================

"""
Perception Projection: The outer semantic publication layer of the Perception System.

Projection is the architectural layer responsible for constructing immutable,
consumer-specific views over validated perceptual artifacts.

It owns:
    - projection requests
    - projection contexts
    - projection scopes
    - projection selection
    - projection filtering
    - projection shaping
    - projection summarization
    - projection snapshots
    - projection streams
    - incremental updates
    - publication contracts
    - projection revisions
    - projection validation
    - projection provenance
    - projection diagnostics

It does NOT own:
    - source Observations
    - Processing transformations
    - Integration artifacts
    - Attention, salience, Workspace state
    - Memory, Knowledge, reasoning
    - Executive control
    - Action
"""

# Shared contracts (common to all projections)
from .shared import (
    PerceptionProjectionIdentity,
    ProjectionKind,
    PerceptionProjectionScope,
    TemporalScope,
    SpatialScope,
    ModalityScope,
    ArtifactScope,
    PerceptionProjectionRequest,
    ProjectionUpdateMode,
    ConflictVisibility,
    AmbiguityVisibility,
    MissingEvidenceVisibility,
    ConsumerKind,
    PerceptionProjectionConsumerContract,
    PerceptionProjectionContext,
    PerceptionProjectionResult,
    ProjectionStatus,
    ProjectionSelectionRecord,
    SelectionStatus,
    FilterKind,
    PerceptionProjectionFilterRecord,
    LimitationKind,
    PerceptionProjectionLimitation,
)

# Per projection domain contracts
from .percept import (
    PerceptProjection,
    PerceptProjectionBuilder,
)

from .scene import (
    SceneProjection,
    ProjectedSceneStructure,
)

from .event import (
    EventProjection,
    EventSequenceProjection,
)

from .workspace import (
    WorkspacePerceptionProjection,
    WorkspacePerceptionChangeSet,
)

# Snapshot, Stream, and Delta projections
from .snapshot import PerceptionSnapshotProjection

from .stream import PerceptionProjectionStream

from .delta import PerceptionProjectionDelta

__all__ = [
    # Shared contracts
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
    # Per projection domain
    "PerceptProjection",
    "PerceptProjectionBuilder",
    "SceneProjection",
    "ProjectedSceneStructure",
    "EventProjection",
    "EventSequenceProjection",
    "WorkspacePerceptionProjection",
    "WorkspacePerceptionChangeSet",
    # Snapshot, Stream, Delta
    "PerceptionSnapshotProjection",
    "PerceptionProjectionStream",
    "PerceptionProjectionDelta",
]