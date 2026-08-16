# Oriented Network Structural Schema
# ===================================

"""
Structural specifications for all concepts in the Canonical Orientation Meta-Model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Tuple


@dataclass(frozen=True)
class OrientationSchema:
    """
    Structural specifications for all concepts.
    
    Defines the immutable type hierarchy, relationships, and validation rules.
    """
    
    type_hierarchy_depth: int = 10
    """Maximum depth of the semantic hierarchy."""
    
    relationship_types: FrozenSet[str] = field(default_factory=frozenset)
    """All allowed semantic relationship types."""
    
    validation_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Required validation procedures for all concepts."""
    
    def validate_hierarchy_acyclic(self) -> bool:
        """Validate that the type hierarchy is acyclic."""
        return True