# Default Network Memory Integration
# ==================================

"""
Canonical memory-integration layer for the Default Network.

This module establishes bounded, runtime-neutral coordination of memory-related
semantic products while preserving clear ownership boundaries:

MEMORY INTEGRATION (Default Network):
    - Coordinates memory projections
    - Assesses relevance and freshness
    - Identifies associations, links, conflicts, gaps
    - Proposes consolidations, abstractions, updates
    - Produces advisory products

AUTHORITATIVE MEMORY CAPABILITY (External):
    - Storage
    - Retrieval
    - Indexing
    - Consolidation (authoritative)
    - Retention policy
    - Deletion
    - Source validation

The two remain strictly separated. Memory Integration coordinates evidence,
it does not own storage or retrieval mechanics.

CURRENT STATUS:
    Phase 4.3.9 is under development. Not all modules are implemented.
    Core models are available; some projections and products need completion.

EXPORTS (current):
    - MemoryIntegrationRequest
    - MemoryIntegrationSourceReference  
    - MemoryProjectionReference
    - MemoryRecordProjection
    - MemoryIntegrationPurpose, MemoryIntegrationSubject, MemoryIntegrationScope
    - MemoryIntegrationEpisode
    - MemoryIntegrationPlan
    - MemoryRelevanceAssessment
    - MemoryFreshnessAssessment
    - MemoryIntegrationConfig
    - MemoryIntegrationState
    - StateTransition, StateSnapshot, HistoryEntry
    - DefaultMemInvariant (architectural invariants)
"""

from __future__ import annotations

from typing import Tuple, FrozenSet, Optional

# =============================================================================
# VERSION AND METADATA
# =============================================================================

__version__ = "1.0.0"
"""Memory Integration layer version."""

__all__: Tuple[str, ...] = (
    # Core models
    "MemoryIntegrationRequest",
    "MemoryIntegrationSourceReference",
    
    # Projection models  
    "MemoryProjectionReference",
    "MemoryRecordProjection",
    
    # Subject/Scope/Purpose (enums)
    "MemoryIntegrationPurposeKind",
    "MemoryIntegrationSubjectKind",
    
    # Episode and Plan
    "MemoryIntegrationEpisode",
    "MemoryIntegrationPlan",
    
    # Assessment models
    "MemoryRelevanceAssessment",
    "MemoryFreshnessAssessment",
    
    # State models
    "MemoryIntegrationStateKind",
    "MemoryIntegrationState",
    "StateTransitionKind",
    "StateTransition",
    "StateSnapshot",
    "HistoryEntry",
    
    # Configuration
    "MemoryIntegrationConfig",
    
    # Validation
    "DefaultMemInvariant",
)


# =============================================================================
# IMPORTS - Only existing modules
# =============================================================================

# Core request models
from .request import (
    MemoryIntegrationRequest,
    MemoryIntegrationSourceReference,
)

# Projection models  
from .projection import MemoryRecordProjection
from .request import MemoryProjectionReference

# Subject/purpose/scope enums are defined in separate files but we'll export
# them from the main module once they're fully implemented.
from .subject import MemoryIntegrationSubject, MemoryIntegrationSubjectKind
from .purpose import MemoryIntegrationPurpose, MemoryIntegrationPurposeKind
from .scope import MemoryIntegrationScope

# Episode and Plan models
from .episode import MemoryIntegrationEpisode
from .plan import MemoryIntegrationPlan, CoordinationStepKind

# Assessment models
from .relevance import (
    MemoryRelevanceAssessment,
    MemoryFreshnessAssessment,
)

# State and history models  
from .state.model import (
    MemoryIntegrationState,
    MemoryIntegrationStateKind,
    StateTransition,
    StateTransitionKind,
    StateSnapshot,
    HistoryEntry,
)

# Configuration
from .configuration import MemoryIntegrationConfig

# Validation/architecture
from .validation.architecture import DefaultMemInvariant


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES (for missing modules)
# =============================================================================

# These will be implemented in future phases

class FactualityClass:
    """Placeholder for factuality classification."""
    OBSERVED = "observed"
    RECORDED = "recorded"
    REPORTED = "reported"
    INFERRED = "inferred"
    SIMULATED = "simulated"
    COUNTERFACTUAL = "counterfactual"
    HYPOTHETICAL = "hypothetical"
    PREDICTED = "predicted"


class ReconstructionClassification:
    """Placeholder for reconstruction classification."""
    DIRECT_RECORD = "direct_record"
    SUMMARIZED_RECORD = "summarized_record"
    RECONSTRUCTED_RECORD = "reconstructed_record"
    INFERRED_RECONSTRUCTION = "inferred_reconstruction"
    HYPOTHETICAL_RECONSTRUCTION = "hypothetical_reconstruction"


class MemoryKind:
    """Placeholder for memory kind classifications."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    AUTOBIOGRAPHICAL = "autobiographical"
    PROCEDURAL = "procedural"
    WORKING_MEMORY_REFERENCE = "working_memory_reference"
    PROSPECTIVE = "prospective"
    ASSOCIATIVE = "associative"
    RELATIONAL = "relational"
    CONTEXTUAL = "contextual"
    SYSTEM_HISTORY = "system_history"
    EXTERNAL_KNOWLEDGE_REFERENCE = "external_knowledge_reference"
    UNKNOWN = "unknown"


class AssociationKind:
    """Placeholder for association kinds."""
    SEMANTIC_SIMILARITY = "semantic_similarity"
    TEMPORAL_PROXIMITY = "temporal_proximity"
    CAUSAL_HYPOTHESIS = "causal_hypothesis"
    SHARED_SUBJECT = "shared_subject"
    SHARED_OBJECTIVE = "shared_objective"


class ProposalOperation:
    """Placeholder for proposal operations."""
    ADD_RECORD = "add_record"
    ADD_LINK = "add_link"
    REVISE_CONFIDENCE = "revise_confidence"
    MARK_SUPERSEDED = "mark_superseded"


# =============================================================================
# EXPORT ENUMERATIONS
# =============================================================================

FactualityClass = FactualityClass
ReconstructionClassification = ReconstructionClassification  
MemoryKind = MemoryKind
AssociationKind = AssociationKind
ProposalOperation = ProposalOperation

# Note: These will be fully implemented in Phase 4.3.9 completion