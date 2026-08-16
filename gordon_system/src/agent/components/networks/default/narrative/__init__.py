# Narrative Coordination Package
# ==============================

"""
Canonical narrative coordination layer for the Default Network.

This package implements bounded, immutable coordination of internally generated
narrative cognition. It provides:

    • Immutable request models (NarrativeRequest, scope, purpose, subject)
    • Episode specialization (NarrativeEpisode reusing InternalEpisode)
    • Planning support (declarative plan steps)
    • Capability contracts (request/result boundaries)
    • Source references with factuality classification
    • Narrative structures (events, sequences, relations, participants)
    • Interpretive structures (themes, tensions, gaps, conflicts, claims)
    • Assessment models (continuity, coherence, confidence, completeness)
    • Revision lineage and proposal semantics
    • Products integrated with InternalThought
    • Outcomes and continuation recommendations

ARCHITECTURAL PRINCIPLES:
    1. Narrative coordination is distinct from narrative construction
    2. All contracts are deeply immutable
    3. No runtime references in domain models
    4. All bounds are explicit and bounded
    5. State transitions are semantic records, not runtime actions

ARCHITECTURAL BOUNDARIES:
    • Does NOT implement narrative construction algorithms (outsourced to capabilities)
    • Does NOT mutate memory, identity, or other systems
    • Does NOT schedule execution or allocate resources
    • Does NOT own runtime progression (ExecutionLoop does that)

CANONICAL DEFINITION:
    A narrative is a bounded, structured semantic account that organizes selected
    events, states, participants, objectives, decisions, consequences,
    interpretations, and unresolved relations into a temporally and meaningfully
    coherent representation.

PHASE: 4.3.7
"""

from __future__ import annotations

# Version information
from .__meta__ import (
    __version__,
    __author__,
    __description__,
)

# Import core models
from .request import (
    NarrativeRequest,
    NarrativeRequestId,
)
from .purpose import NarrativePurpose
from .subject import NarrativeSubject
from .scope import NarrativeScope

# Source references and factuality
from .source_reference import NarrativeSourceReference, FactualityClassification

# Episode specialization
from .episode import NarrativeEpisode

# Planning
from .plan import NarrativePlan, NarrativeStepKind, NarrativePlanStep

# Coordination state
from .state.model import NarrativeCoordinationState

# Capability contracts (imported from contracts package)
from .contracts.narrative import (
    NarrativeCapabilityRequest,
    NarrativeCapabilityResult,
)

# Enums (re-exports for convenience)
from .enums import (
    # Purpose kinds
    NarrativePurposeKind,
    # Subject kinds
    NarrativeSubjectKind,
    # Source kinds
    SourceKind,
    # Event kinds
    NarrativeEventKind,
    # Relation kinds
    NarrativeRelationKind,
    # Perspective kinds
    NarrativePerspectiveKind,
    # Temporal relation kinds
    TemporalRelationKind,
    # Product kinds
    NarrativeProductKind,
    # Outcome kinds
    NarrativeOutcomeKind,
    # Continuation kinds
    NarrativeContinuationKind,
    # Gap kinds
    NarrativeGapKind,
    # Conflict kinds
    NarrativeConflictKind,
)

# Core narrative structures
from .event import (
    NarrativeEvent,
    EventTemporalPosition,
)
from .sequence import NarrativeSequence, SequenceOrderRelation
from .relation import NarrativeRelation
from .participant import NarrativeParticipant
from .perspective import NarrativePerspective, PerspectiveBias

# Temporal models
from .temporal import (
    NarrativeTemporalScope,
    NarrativeTimeReference,
    NarrativeTemporalRelation,
)

# Interpretive structures
from .theme import NarrativeTheme
from .tension import NarrativeTension
from .gap import NarrativeGap
from .conflict import NarrativeConflict
from .claim import NarrativeClaim
from .interpretation import NarrativeInterpretation

# Assessment models
from .continuity import NarrativeContinuityAssessment
from .coherence import NarrativeCoherenceAssessment
from .confidence import NarrativeConfidence
from .completeness import NarrativeCompleteness

# Revision and lineage
from .revision import (
    NarrativeRevision,
    RevisionKind,
)

# Products and outcomes
from .product import (
    NarrativeProduct,
)
from .outcome import (
    NarrativeOutcome,
)
from .continuation import (
    NarrativeContinuation,
)

# Proposals (for integration with other systems)
from .proposal import (
    MemoryIntegrationProposal,
    IdentityReviewProposal,
)

# Configuration
from .configuration import (
    NarrativeCoordinationConfig,
)

# Exceptions
from .exceptions import (
    NarrativeCoordinationError,
    InvalidNarrativeRequest,
    InvalidNarrativePurpose,
    InvalidNarrativeSubject,
    InvalidNarrativeScope,
    NarrativeFactualityViolation,
    NarrativePlanInvalid,
    NarrativeBranchLimitExceeded,
    NarrativeRecursionLimitExceeded,
)

# Expose all public API items
__all__ = [
    # Version and authorship
    "__version__",
    "__author__",
    "__description__",
    
    # Core models
    "NarrativeRequest",
    "NarrativeRequestId",
    "NarrativePurpose",
    "NarrativeSubject",
    "NarrativeScope",
    "NarrativeSourceReference",
    "FactualityClassification",
    "NarrativeEpisode",
    
    # Planning
    "NarrativePlan",
    "NarrativeStepKind",
    "NarrativePlanStep",
    
    # State
    "NarrativeCoordinationState",
    
    # Capability contracts
    "NarrativeCapabilityRequest",
    "NarrativeCapabilityResult",
    
    # Enums (re-exported from enums module)
    "NarrativePurposeKind",
    "NarrativeSubjectKind",
    "SourceKind",
    "NarrativeEventKind",
    "NarrativeRelationKind",
    "NarrativePerspectiveKind",
    "TemporalRelationKind",
    "NarrativeProductKind",
    "NarrativeOutcomeKind",
    "NarrativeContinuationKind",
    "NarrativeGapKind",
    "NarrativeConflictKind",
    
    # Core structures
    "NarrativeEvent",
    "EventTemporalPosition",
    "NarrativeSequence",
    "SequenceOrderRelation",
    "NarrativeRelation",
    "NarrativeParticipant",
    "NarrativePerspective",
    "PerspectiveBias",
    
    # Temporal models
    "NarrativeTemporalScope",
    "NarrativeTimeReference",
    "NarrativeTemporalRelation",
    
    # Interpretive structures
    "NarrativeTheme",
    "NarrativeTension",
    "NarrativeGap",
    "NarrativeConflict",
    "NarrativeClaim",
    "NarrativeInterpretation",
    
    # Assessment models
    "NarrativeContinuityAssessment",
    "NarrativeCoherenceAssessment",
    "NarrativeConfidence",
    "NarrativeCompleteness",
    
    # Revision and lineage
    "NarrativeRevision",
    "RevisionKind",
    
    # Products and outcomes
    "NarrativeProduct",
    "NarrativeOutcome",
    "NarrativeContinuation",
    
    # Proposals
    "MemoryIntegrationProposal",
    "IdentityReviewProposal",
    
    # Configuration
    "NarrativeCoordinationConfig",
    
    # Exceptions
    "NarrativeCoordinationError",
    "InvalidNarrativeRequest",
    "InvalidNarrativePurpose",
    "InvalidNarrativeSubject",
    "InvalidNarrativeScope",
    "NarrativeFactualityViolation",
    "NarrativePlanInvalid",
    "NarrativeBranchLimitExceeded",
    "NarrativeRecursionLimitExceeded",
]