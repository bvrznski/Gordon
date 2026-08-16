# Oriented Network Coherence Model - Phase 4.7.10
# ================================================

"""
Coherence evaluation models and contracts for semantic quality assessment.

SEMANTIC ROLE:
    - Describes semantic compatibility between orientation elements
    - Never resolves inconsistencies
    - Never repairs structures
    
OWNERSHIP CONTRACT:
    - Owns: coherence semantics, relationships, context
    - Never owns: resolution, repair, runtime synchronization

COHERENCE LAWS:
    ORIENTED-COHERENCE-LAW-001 through 006: Coherence semantics and constraints
"""

from __future__ import annotations

# =============================================================================
# COHERENCE MODELS (Part 1)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.coherence.models import (
    OrientationCoherence,
    HighCoherence,
    ModerateCoherence,
    LowCoherence,
    BrokenCoherence,
    UnknownCoherence,
)

# =============================================================================
# COHERENCE CONTRACTS (Part 2)
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.evaluation.coherence.contracts import (
    CoherenceReference,
    CoherenceRelationship,
    CoherenceRequirement,
    CoherenceAuthority,
    CoherenceOwner,
    CoherenceProjection,
)

__all__ = [
    # Coherence Models
    "OrientationCoherence",
    "HighCoherence",
    "ModerateCoherence",
    "LowCoherence",
    "BrokenCoherence",
    "UnknownCoherence",
    # Coherence Contracts
    "CoherenceReference",
    "CoherenceRelationship",
    "CoherenceRequirement",
    "CoherenceAuthority",
    "CoherenceOwner",
    "CoherenceProjection",
]