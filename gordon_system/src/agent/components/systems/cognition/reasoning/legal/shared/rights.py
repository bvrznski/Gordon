# Rights Analysis - Phase 7.47 Part 1
# ====================================

"""
Rights Contract.

Rights analysis evaluates:
    - legal rights
    - permissions
    - limitations
    - exceptions
    - waivers
    - protected interests

Rights remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class Right:
    """
    A legal right or permission.
    
    A right includes:
        - Source of the right (statute, regulation, etc.)
        - Protected interests
        - Limitations and exceptions
        - Waiver conditions
    
    Rights define what actors are permitted to do.
    """
    
    # Identity
    right_id: str                             # Unique identifier
    
    # Source
    legal_source_id: str                      # Which source recognizes this?
    source_type: str                          # e.g., "statute", "regulation"
    
    # Content
    description: str = ""                     # What is permitted?
    protected_interests: Tuple[str, ...] = ()  # Interests protected
    
    # Limitations
    limitations: Tuple[str, ...] = ()         # When does the right not apply?
    exceptions: Tuple[str, ...] = ()          # Special cases
    waiver_conditions: Tuple[str, ...] = ()   # When can it be waived?
    
    # Status
    is_active: bool = True                    # Is this right currently active?
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        legal_source_id: str,
        source_type: str,
        description: str,
        protected_interests: Optional[List[str]] = None,
    ) -> Right:
        """Create a new right."""
        return cls(
            right_id=f"right:{uuid.uuid4().hex[:16]}",
            legal_source_id=legal_source_id,
            source_type=source_type,
            description=description,
            protected_interests=tuple(protected_interests or []),
        )


@dataclass(frozen=True)
class RightsAnalysis:
    """
    Analysis of applicable rights for a legal question.
    
    Includes identification of all rights and assessment
    of their applicability to the current case.
    """
    
    # Identity
    analysis_id: str                          # Unique identifier
    
    # Input
    legal_question: str                       # Question being analyzed
    factual_context: Dict[str, Any] = field(default_factory=dict)  # Facts
    
    # Analysis results
    applicable_rights: Tuple[Right, ...] = ()
    
    # Assessment
    rights_violated: Tuple[str, ...] = ()     # Which rights were violated?
    limitations_applied: Tuple[str, ...] = () # Limitations that apply
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        legal_question: str,
        factual_context: Optional[Dict[str, Any]] = None,
    ) -> RightsAnalysis:
        """Create a new rights analysis."""
        return cls(
            analysis_id=f"rights_analysis:{uuid.uuid4().hex[:16]}",
            legal_question=legal_question,
            factual_context=factual_context or {},
        )
    
    def with_applicable_rights(self, rights: List[Right]) -> RightsAnalysis:
        """Return a copy with updated applicable rights."""
        return dataclass_replace(
            self,
            applicable_rights=tuple(rights),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "Right",
    "RightsAnalysis",
]