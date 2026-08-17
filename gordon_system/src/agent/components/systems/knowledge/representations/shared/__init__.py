# Knowledge Representations - Shared Contracts - Phase 6.2
# =========================================================

"""
Shared contracts for all representation types in Gordon's Knowledge system.

This module provides foundational data structures used across all representation kinds:
    * Descriptor - Metadata about representations
    * Relation - Semantic relationships between representations
    * Compatibility - Version compatibility tracking
    * Lifecycle - State transition management
    * Provenance - Generation and evolution history
"""

from __future__ import annotations

# Representation Kinds
from gordon_system.src.agent.components.systems.knowledge.representations.shared.descriptor import (
    RepresentationKind,
)

# Lifecycle Management
from gordon_system.src.agent.components.systems.knowledge.representations.shared.lifecycle import (
    RepresentationLifecycleState,
    RepresentationLifecycle,
)

# Provenance Tracking
from gordon_system.src.agent.components.systems.knowledge.representations.shared.provenance import (
    RepresentationProvenance,
)

# Compatibility
from gordon_system.src.agent.components.systems.knowledge.representations.shared.compatibility import (
    RepresentationCompatibilityKind,
    RepresentationCompatibility,
)

# Relations
from gordon_system.src.agent.components.systems.knowledge.representations.shared.relation import (
    RepresentationRelation,
    RepresentationRelationKind,
)


__all__ = [
    # Kinds
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
]