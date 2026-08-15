# Internal Episode Derivation Model
# =================================

"""
Derivation model for internal episode relationships.

Defines how episodes can derive or be derived from other episodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class DerivationKind:
    """
    Categories of episode derivation.
    
    Defines what kind of relationship exists between parent and derived episodes.
    """
    
    # Derivation from parent's result
    INSIGHT = "insight"
    """Derived from a new insight produced by the parent."""
    
    PROPOSAL = "proposal"
    """Derived from a proposal made by the parent."""
    
    UNRESOLVED = "unresolved"
    """Derived to address issues left unresolved by the parent."""
    
    # Derivation for bounded decomposition
    DECOMPOSITION = "decomposition"
    """Parent decomposed its work into child episodes for bounded processing."""
    
    SUBTASK = "subtask"
    """Child handles a specific subtask of the parent's work."""
    
    # Verification and validation
    VALIDATION = "validation"
    """Derived to validate part of parent's result."""
    
    CHALLENGE = "challenge"
    """Derived to challenge or test parent's assumptions."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid derivation kinds."""
        return (
            cls.INSIGHT,
            cls.PROPOSAL,
            cls.UNRESOLVED,
            cls.DECOMPOSITION,
            cls.SUBTASK,
            cls.VALIDATION,
            cls.CHALLENGE,
        )