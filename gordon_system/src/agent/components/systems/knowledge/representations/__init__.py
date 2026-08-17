# Knowledge Representations - Phase 6.2
# ======================================

"""
Knowledge Representation System: Computational encodings of semantic artifacts.

This module implements the canonical representation architecture specified in
Phase 6.2:

    1. Symbolic Representation - explicit semantics, reasoning, inspection
    2. Vector Representation - continuous semantic geometry, retrieval
    3. Latent Representation - compressed semantic structure, features
    4. Hybrid Representation - integrated symbolic, vector, latent views
    5. External Representation - serialization formats for communication

Semantic identity remains unique and independent from representation.
Representations are replaceable encodings that preserve semantic integrity.

Architectural Invariants:
    - One semantic artifact may have many representations
    - Representations remain replaceable without changing semantics
    - Provenance is preserved across all representation types
    - Lifecycle transitions are tracked independently per representation

This system enables continuous evolution of embedding models, SAE architectures,
serialization formats, and other encoding machinery without invalidating the
semantic identities that higher cognitive systems depend upon.
"""

from __future__ import annotations

# Representation Kinds
from gordon_system.src.agent.components.systems.knowledge.representations.shared.descriptor import (
    RepresentationKind,
)

# Shared Contracts
from gordon_system.src.agent.components.systems.knowledge.representations.shared.lifecycle import (
    RepresentationLifecycleState,
    RepresentationLifecycle,
)

from gordon_system.src.agent.components.systems.knowledge.representations.shared.provenance import (
    RepresentationProvenance,
)

from gordon_system.src.agent.components.systems.knowledge.representations.shared.compatibility import (
    RepresentationCompatibilityKind,
    RepresentationCompatibility,
)

from gordon_system.src.agent.components.systems.knowledge.representations.shared.relation import (
    RepresentationRelation,
    RepresentationRelationKind,
)

# Symbolic Representations
from gordon_system.src.agent.components.systems.knowledge.representations.symbolic.representation import (
    SymbolicRepresentation,
)

from gordon_system.src.agent.components.systems.knowledge.representations.symbolic.structure import (
    SymbolicStructure,
    SymbolicProjection,
)

from gordon_system.src.agent.components.systems.knowledge.representations.symbolic.validation import (
    SymbolicValidation,
)

# Vector Representations
from gordon_system.src.agent.components.systems.knowledge.representations.vector.embedding import (
    EmbeddingSpace,
    VectorDescriptor,
    VectorNeighborhood,
)

from gordon_system.src.agent.components.systems.knowledge.representations.vector.space import (
    VectorSpace,
)

from gordon_system.src.agent.components.systems.knowledge.representations.vector.similarity import (
    SimilarityMetric,
)

# Latent Representations
from gordon_system.src.agent.components.systems.knowledge.representations.latent.representation import (
    LatentRepresentation,
)

from gordon_system.src.agent.components.systems.knowledge.representations.latent.space import (
    LatentSpace,
)

from gordon_system.src.agent.components.systems.knowledge.representations.latent.feature import (
    LatentFeature,
    LatentActivation,
)

# Hybrid Representations
from gordon_system.src.agent.components.systems.knowledge.representations.hybrid.representation import (
    HybridRepresentation,
)

from gordon_system.src.agent.components.systems.knowledge.representations.hybrid.composition import (
    HybridComposition,
)

# External Representations
from gordon_system.src.agent.components.systems.knowledge.representations.external.serialization import (
    ExternalRepresentation,
    SerializationFormat,
)

# Mappings
from gordon_system.src.agent.components.systems.knowledge.representations.mappings.mapping import (
    RepresentationMapping,
)

# Alignment
from gordon_system.src.agent.components.systems.knowledge.representations.alignment.alignment import (
    RepresentationAlignmentRequest,
    RepresentationAlignmentResult,
)

# Translation
from gordon_system.src.agent.components.systems.knowledge.representations.translation.translation import (
    RepresentationTranslation,
)

# Regeneration
from gordon_system.src.agent.components.systems.knowledge.representations.regeneration.regeneration import (
    RepresentationRegenerationRequest,
    RepresentationRegenerationResult,
)

# Cache
from gordon_system.src.agent.components.systems.knowledge.representations.cache.entry import (
    RepresentationCacheEntry,
)

# Health and Governance
from gordon_system.src.agent.components.systems.knowledge.representations.observability.health import (
    RepresentationHealth,
)

from gordon_system.src.agent.components.systems.knowledge.representations.observability.governance import (
    RepresentationGovernance,
)


__all__ = [
    # Representation kinds
    "RepresentationKind",
    
    # Lifecycle
    "RepresentationLifecycleState",
    "RepresentationLifecycle",
    
    # Provenance
    "RepresentationProvenance",
    
    # Compatibility
    "RepresentationCompatibilityKind",
    "RepresentationCompatibility",
    
    # Relations
    "RepresentationRelation",
    "RepresentationRelationKind",
    
    # Symbolic
    "SymbolicRepresentation",
    "SymbolicStructure",
    "SymbolicProjection",
    "SymbolicValidation",
    
    # Vector
    "EmbeddingSpace",
    "VectorDescriptor",
    "VectorNeighborhood",
    "VectorSpace",
    "SimilarityMetric",
    
    # Latent
    "LatentRepresentation",
    "LatentSpace",
    "LatentFeature",
    "LatentActivation",
    
    # Hybrid
    "HybridRepresentation",
    "HybridComposition",
    
    # External
    "ExternalRepresentation",
    "SerializationFormat",
    
    # Mappings
    "RepresentationMapping",
    
    # Alignment
    "RepresentationAlignmentRequest",
    "RepresentationAlignmentResult",
    
    # Translation
    "RepresentationTranslation",
    
    # Regeneration
    "RepresentationRegenerationRequest",
    "RepresentationRegenerationResult",
    
    # Cache
    "RepresentationCacheEntry",
    
    # Health and Governance
    "RepresentationHealth",
    "RepresentationGovernance",
]