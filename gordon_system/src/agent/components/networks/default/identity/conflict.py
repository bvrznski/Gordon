# Identity Conflict Model
# =======================

"""
Immutable identity conflict model for representing conflicts between identity components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityConflict:
    """
    Immutable representation of an identity conflict.
    
    PROPERTIES:
        • conflict_id: Unique identifier for this conflict
        • category: Conflict type (IdentityConflictKind.*)
        • involved_aspects: Identity aspects that are in conflict
        • evidence: Evidence supporting the conflict
        • severity: Conflict severity (0.0 to 1.0)
        • confidence: Confidence in conflict assessment (0.0 to 1.0)
        • authority_implications: What authority is affected
        • blocking_status: Whether this blocks progress
    """
    
    conflict_id: str
    """Unique identifier for this identity conflict."""
    
    category: str = ""
    """Conflict type (IdentityConflictKind.*)."""
    
    involved_aspects: Tuple[str, ...] = field(default_factory=tuple)
    """Identity aspect IDs that are in conflict."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting the existence of this conflict."""
    
    severity: float = 0.5
    """Conflict severity (0.0 to 1.0)."""
    
    confidence: float = 1.0
    """Confidence in conflict assessment (0.0 to 1.0)."""
    
    authority_implications: str = ""
    """What authority is affected by this conflict."""
    
    blocking_status: bool = False
    """Whether this conflict blocks further progress."""