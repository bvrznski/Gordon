# Internal Context Package
# =========================

"""
Canonical InternalContext model for Gordon's Default Network.

This module provides immutable, bounded, revisioned projections of information
available to internally generated cognitive coordination.

ARCHITECTURAL PRINCIPLES:
    - InternalContext is a projection, not an authoritative data store
    - InternalContext is immutable (deeply frozen)
    - InternalContext is bounded (no unbounded growth)
    - Every projection preserves its source owner and revision
    - Context completeness and confidence remain distinct
    - Semantic conflicts are never silently erased
    - InternalContext does not own Working Memory, persistent Memory,
      Execution entities, or runtime mechanisms

PUBLIC API:
    Core Model:
        - InternalContext: Main aggregate (immutable canonical model)
        - InternalContextId: Stable identifier for context instances
        
    Request and Configuration:
        - InternalContextRequest: Description of what context to assemble
        - InternalContextConfig: Immutable configuration for assembly
        
    Projections:
        - MemoryContextProjection
        - IdentityContextProjection
        - ObjectiveContextProjection
        - CommitmentContextProjection
        - NarrativeContextProjection
        - PredictiveContextProjection
        - WorkspaceContextProjection
        - WorkingMemoryContextProjection
        - ExecutionContextProjection
        - AttentionContextProjection
        - AffectContextProjection
        - ConcernContextProjection
        - ResourceContextProjection
        
    Composition:
        - InternalContextCompleteness: Structured completeness assessment
        - InternalContextConfidence: Structured confidence assessment
        - InternalContextFreshness: Structured freshness assessment
        - InternalContextConflict: Conflict records with categorization
        
    Assembly and Validation:
        - InternalContextAssembler: Deterministic composition engine
        - InternalContextValidator: Validation logic
        
    Serialization and State:
        - InternalContextSnapshot: Serialization-ready immutable snapshot

ARCHITECTURAL INVARIANTS:
    DEFAULT-CONTEXT-INV-001 through DEFAULT-CONTEXT-INV-020 (see module docs)

PHASE: 4.3.2
"""

from __future__ import annotations

# Module version and authorship
from .__meta__ import (
    __version__,
    __author__,
    __description__,
)

# Import core model
from .context import (
    InternalContext,
    InternalContextId,
    MemoryContextProjection,
    IdentityContextProjection,
    ObjectiveContextProjection,
    CommitmentContextProjection,
    NarrativeContextProjection,
    PredictiveContextProjection,
    WorkspaceContextProjection,
    WorkingMemoryContextProjection,
    ExecutionContextProjection,
    AttentionContextProjection,
    AffectContextProjection,
    ConcernContextProjection,
    ResourceContextProjection,
)

# Import enums for public API exposure
from .enums import (
    InternalContextPurpose,
    ContextCompleteness,
    ContextConfidence,
    ContextFreshness,
    ContextConflictCategory,
    ContextTransitionType,
    ProjectionKind,
    InternalContextScope,
    ContextSubjectId,
    ContextTemporalHorizon,
    ContextCapacity,
    OverflowBehavior,
)

# Import request and configuration
from .request import (
    InternalContextRequest,
    InternalContextRequestId,
)
from .configuration import (
    InternalContextConfig,
)

# Import composition models
from .composition.completeness import (
    InternalContextCompleteness,
)
from .composition.confidence import (
    InternalContextConfidence,
)
from .composition.freshness import (
    InternalContextFreshness,
)
from .composition.conflicts import (
    InternalContextConflict,
    ContextConflictId,
)

# Import provenance
from .provenance.provenance import (
    InternalContextProvenance,
)

# Import state types
from .state.snapshot import (
    InternalContextSnapshot,
)
from .state.transition import (
    InternalContextTransition,
    ContextTransitionId,
)
from .state.history import (
    InternalContextHistory,
)

# Import validation
from .validation.context import (
    InternalContextValidator,
    ValidationReport,
)

# Import assembler (the main composition engine)
from .assembler import (
    InternalContextAssembler,
)

# Expose all public API items
__all__ = [
    # Version and authorship
    "__version__",
    "__author__",
    "__description__",
    
    # Core model
    "InternalContext",
    "InternalContextId",
    
    # Projection contracts
    "MemoryContextProjection",
    "IdentityContextProjection",
    "ObjectiveContextProjection",
    "CommitmentContextProjection",
    "NarrativeContextProjection",
    "PredictiveContextProjection",
    "WorkspaceContextProjection",
    "WorkingMemoryContextProjection",
    "ExecutionContextProjection",
    "AttentionContextProjection",
    "AffectContextProjection",
    "ConcernContextProjection",
    "ResourceContextProjection",
    
    # Request and configuration
    "InternalContextRequest",
    "InternalContextRequestId",
    "InternalContextConfig",
    
    # Composition models
    "InternalContextCompleteness",
    "InternalContextConfidence",
    "InternalContextFreshness",
    "InternalContextConflict",
    "ContextConflictId",
    "InternalContextProvenance",
    
    # State types
    "InternalContextSnapshot",
    "InternalContextTransition",
    "ContextTransitionId",
    "InternalContextHistory",
    
    # Validation
    "InternalContextValidator",
    "ValidationReport",
    
    # Assembler
    "InternalContextAssembler",
    
    # Enums and canonical vocabulary
    "InternalContextPurpose",
    "ContextCompleteness",
    "ContextConfidence",
    "ContextFreshness",
    "ContextConflictCategory",
    "ContextTransitionType",
    "ProjectionKind",
    "InternalContextScope",
    "ContextSubjectId",
    "ContextTemporalHorizon",
    "ContextCapacity",
    "OverflowBehavior",
]