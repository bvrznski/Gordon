# Knowledge Representations - Symbolic - Phase 6.2
# ================================================

"""
Symbolic representations: Explicit semantic structure for reasoning.

Symbolic representations provide:
    * Explicit entities with clear identity
    * Explicit relations between entities
    * Explicit attributes and properties
    * Explicit constraints on valid configurations
    * Reasoning-capable structure

This is the canonical representation type for reasoning operations in Gordon.
"""

from __future__ import annotations

# Symbolic Representation
from gordon_system.src.agent.components.systems.knowledge.representations.symbolic.representation import (
    SymbolicRepresentation,
)

# Structure definitions
from gordon_system.src.agent.components.systems.knowledge.representations.symbolic.structure import (
    SymbolicStructure,
    SymbolicProjection,
)

# Validation
from gordon_system.src.agent.components.systems.knowledge.representations.symbolic.validation import (
    SymbolicValidation,
)


__all__ = [
    # Core types
    "SymbolicRepresentation",
    
    # Structure
    "SymbolicStructure",
    "SymbolicProjection",
    
    # Validation
    "SymbolicValidation",
]