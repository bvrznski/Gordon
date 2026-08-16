# Oriented Network Cross-Model Relationships
# ===========================================

"""
Cross-model relationship specifications for the Canonical Orientation Meta-Model.

These relationships are semantic, not runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RelationshipType(Enum):
    """Types of semantic relationships between model components."""
    
    DERIVATION = "derivation"
    """One component derives from another"""
    
    REFERENCE = "reference"
    """Component references another without ownership"""
    
    DEPENDS_ON = "depends_on"
    """Component depends on another for functionality"""
    
    CONTAINS = "contains"
    """Component contains or owns another"""
    
    PARENT_OF = "parent_of"
    """Parent-child relationship in hierarchy"""
    
    IMPLEMENTS = "implements"
    """Implementation relationship"""
    
    VALIDATES = "validates"
    """Validation relationship"""
    
    SERIALIZES = "serializes"
    """Serialization relationship"""


@dataclass(frozen=True)
class CrossModelRelationship:
    """
    Canonical cross-model semantic relationship.
    
    These relationships describe how different components of the
    meta-model relate to each other semantically, not at runtime.
    """
    
    source: str
    """The source component of the relationship"""
    
    target: str  
    """The target component of the relationship"""
    
    relationship_type: RelationshipType
    """The type of semantic relationship"""
    
    description: str
    """Description of this relationship"""