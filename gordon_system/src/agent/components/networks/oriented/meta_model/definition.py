# Oriented Network Semantic Concept Definitions
# =============================================

"""
Semantic concept definitions for the Canonical Orientation Meta-Model.

Every canonical concept has exactly one definition in the meta-model.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OrientationDefinition:
    """
    Semantic concept definition with exact specification.
    
    Every canonical concept has exactly one definition in the meta-model.
    """
    
    name: str
    """The unique canonical identifier for this concept."""
    
    canonical_definition: str
    """The single authoritative semantic definition."""
    
    owner_type: str = "external"
    """The explicit owner of this concept."""
    
    parent_concept: str | None = None
    """Optional parent in the semantic hierarchy (if any)."""
    
    is_root_concept: bool = False
    """Indicates if this is a foundational root concept."""
    
    def validate_canonical(self) -> bool:
        """Validate that this definition follows canonical principles."""
        return bool(
            self.name and 
            self.canonical_definition and 
            self.owner_type
        )