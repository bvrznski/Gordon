# Internal Episode Package
# =======================

"""
Canonical InternalEpisode model for Gordon's Default Network.

This module provides immutable, bounded, revisioned representations of internally
generated cognitive coordination episodes.

ARCHITECTURAL PRINCIPLES:
    - InternalEpisode is a coordination unit, not an execution mechanism
    - InternalEpisode is immutable (deeply frozen)
    - InternalEpisode is bounded (no unbounded growth)
    - Every episode preserves its context binding and revision
    - Episode lifecycle remains distinct from runtime execution
    - InternalEpisode does not own cognitive algorithms or capability implementations

PUBLIC API:
    Core Model:
        - InternalEpisode: Main aggregate (immutable canonical model)
        - InternalEpisodeId: Stable identifier for episode instances
        
    Request and Configuration:
        - InternalEpisodeRequest: Description of what episode to create
        - InternalEpisodeConfig: Immutable configuration for episode handling
        
    Type, Purpose, Scope:
        - InternalEpisodeType: Canonical category of internal cognition
        - InternalEpisodePurpose: Concrete reason for this episode instance
        - InternalEpisodeScope: Bounded constraints on the episode
        
    Lifecycle and State:
        - InternalEpisodeLifecycle: Semantic coordination state
        - InternalEpisodeState: Complete state snapshot
        - InternalEpisodeTransition: Immutable record of state change
        
    Plan Model:
        - InternalEpisodePlan: Declarative coordination plan
        - InternalEpisodeStep: Single coordination step
        
    Capability Boundary:
        - InternalCapabilityRequest: Request to a capability owner
        - InternalCapabilityResult: Result from a capability owner
        
    Evidence Model:
        - InternalEpisodeEvidence: Information produced during coordination
        - InternalEpisodeEvidenceCollection: Bounded evidence set
        - InternalEpisodeEvidenceConflict: Detected conflict record
        
    Outcome and Proposals:
        - InternalEpisodeOutcome: Terminal result of episode coordination
        - InternalEpisodeProposal: Suggested action (not applied mutation)
        - InternalEpisodeContinuation: Advisory continuation recommendation
        
    Relationships:
        - InternalEpisodeRelationship: Parent-child derivation record
        
    Serialization:
        - InternalEpisodeSnapshot: Serialization-ready immutable snapshot
        
ARCHITECTURAL INVARIANTS:
    DEFAULT-EPISODE-INV-001 through DEFAULT-EPISODE-INV-025 (see module docs)

PHASE: 4.3.3
"""

from __future__ import annotations

# Module version and authorship
from .__meta__ import (
    __version__,
    __author__,
    __description__,
)

# Import core model
from .episode import (
    InternalEpisode,
    InternalEpisodeId,
    InternalEpisodeRevision,
)

# Import type, purpose, scope enums
from .enums import (
    InternalEpisodeType,
    InternalEpisodePurpose,
    InternalEpisodeScope,
    InternalCapabilityCategory,
    InternalEvidenceCategory,
    InternalOutcomeKind,
    ContinuationKind,
    RelationshipKind,
)

# Import request and configuration
from .request import (
    InternalEpisodeRequest,
    InternalEpisodeRequestId,
)

from .configuration import (
    InternalEpisodeConfig,
)

# Import lifecycle model
from .lifecycle import (
    InternalEpisodeLifecycle,
    LifecycleTransitionId,
)

# Import state model
from .state.snapshot import (
    InternalEpisodeSnapshot,
)
from .state.transition import (
    InternalEpisodeTransition,
)
from .state.history import (
    InternalEpisodeHistory,
)

# Import plan model
from .planning.plan import (
    InternalEpisodePlan,
    InternalEpisodePlanId,
)
from .planning.plan import (
    InternalEpisodeStep,
    InternalEpisodeStepId,
)
from .planning.dependency import (
    InternalEpisodeDependency,
    DependencyKind,
)

# Import capability boundary models
from .contracts.capability import (
    InternalCapabilityRequest,
    InternalCapabilityRequestId,
    InternalCapabilityResult,
    InternalCapabilityResultId,
)

# Import evidence model
from .evidence.item import (
    InternalEpisodeEvidence,
    InternalEpisodeEvidenceId,
)
from .evidence.collection import (
    InternalEpisodeEvidenceCollection,
)
from .evidence.conflict import (
    InternalEpisodeEvidenceConflict,
    EvidenceConflictId,
)
from .evidence.provenance import (
    InternalEpisodeProvenance,
    RequestProvenance,
    ResultProvenance,
)

# Import outcome model
from .outcome import (
    InternalEpisodeOutcome,
    InternalEpisodeOutcomeId,
    InternalEpisodeProposal,
    InternalEpisodeContinuation,
)

# Import relationships
from .relationships.parent_child import (
    InternalEpisodeRelationship,
)
from .relationships.derivation import (
    DerivationKind,
)

# Import validation
from .validation.episode import (
    InternalEpisodeValidator,
    ValidationReport,
)

# Validation - using only the main validator module for now

# Expose all public API items
__all__ = [
    # Version and authorship
    "__version__",
    "__author__",
    "__description__",
    
    # Core model
    "InternalEpisode",
    "InternalEpisodeId",
    "InternalEpisodeRevision",
    
    # Type, purpose, scope
    "InternalEpisodeType",
    "InternalEpisodePurpose",
    "InternalEpisodeScope",
    
    # Request and configuration
    "InternalEpisodeRequest",
    "InternalEpisodeRequestId",
    "InternalEpisodeConfig",
    
    # Lifecycle
    "InternalEpisodeLifecycle",
    "LifecycleTransitionId",
    
    # State
    "InternalEpisodeSnapshot",
    "InternalEpisodeTransition",
    "InternalEpisodeHistory",
    
    # Plan
    "InternalEpisodePlan",
    "InternalEpisodePlanId",
    "InternalEpisodeStep",
    "InternalEpisodeDependency",
    "DependencyKind",
    
    # Capability boundary
    "InternalCapabilityRequest",
    "InternalCapabilityRequestId",
    "InternalCapabilityResult",
    "InternalCapabilityResultId",
    
    # Evidence
    "InternalEpisodeEvidence",
    "InternalEpisodeEvidenceId",
    "InternalEpisodeEvidenceCollection",
    "InternalEpisodeEvidenceConflict",
    "EvidenceConflictId",
    "InternalEpisodeProvenance",
    "RequestProvenance",
    "ResultProvenance",
    
    # Outcome
    "InternalEpisodeOutcome",
    "InternalEpisodeOutcomeId",
    "InternalEpisodeProposal",
    "InternalEpisodeContinuation",
    
    # Relationships
    "InternalEpisodeRelationship",
    "DerivationKind",
    
    # Validation
    "InternalEpisodeValidator",
    "ValidationReport",
    
    # Enums and canonical vocabulary
    "InternalCapabilityCategory",
    "InternalEvidenceCategory",
    "InternalOutcomeKind",
    "ContinuationKind",
    "RelationshipKind",
]