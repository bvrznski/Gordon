# Identity Tension Model
# =======================

"""
Immutable identity tension model for representing tensions between identity components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityTension:
    """
    Immutable representation of an identity tension.
    
    A tension represents a non-terminal unresolved pressure between identity elements.
    Unlike conflicts, tensions are not necessarily contradictions but represent
    pressures that may need attention or resolution.
    
    PROPERTIES:
        • tension_id: Unique identifier for this tension
        • category: Tension type (IdentityTensionKind.*)
        • involved_components: Identity components under tension
        • source_pressure: What is causing the pressure
        • potential_resolution: How this could be resolved
        • confidence: Confidence in tension assessment (0.0 to 1.0)
    """
    
    tension_id: str
    """Unique identifier for this identity tension."""
    
    category: str = ""
    """Tension type (IdentityTensionKind.*)."""
    
    involved_components: Tuple[str, ...] = field(default_factory=tuple)
    """Identity component IDs under pressure."""
    
    source_pressure: str = ""
    """What is causing the pressure or tension."""
    
    potential_resolution: str = ""
    """How this tension could potentially be resolved."""
    
    confidence: float = 1.0
    """Confidence in tension assessment (0.0 to 1.0)."""