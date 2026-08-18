# Precedent Analysis - Phase 7.47 Part 1
# =======================================

"""
Precedent Contract.

Precedent analysis evaluates:
    - binding precedents
    - persuasive precedents
    - jurisdiction compatibility
    - precedent conflicts
    - precedent hierarchy
    - interpretation stability

Precedents remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class Precedent:
    """
    A legal precedent (prior court decision).
    
    A precedent includes:
        - Case identification and citation
        - Holding and reasoning
        - Jurisdiction compatibility
        - Hierarchical position
    
    Precedents guide interpretation of current law.
    """
    
    # Identity
    precedent_id: str                         # Unique identifier
    
    # Case information
    case_name: str                          # Name of the case
    citation: str                           # Legal citation (e.g., 550 U.S. 470)
    court: str                              # Which court decided?
    
    # Content
    holding: str = ""                       # The legal rule established
    reasoning: str = ""                     # Court's reasoning
    key_facts: Tuple[str, ...] = ()         # Important facts
    
    # Status
    decision_date_utc: float = field(default_factory=time.time)
    is_binding_in_jurisdiction: bool = False  # Is this binding?
    
    # Hierarchy (lower = higher authority)
    hierarchical_position: int = 0
    
    # Compatibility
    compatible_jurisdictions: Tuple[str, ...] = ()  # Where does it apply?
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        case_name: str,
        citation: str,
        court: str,
        holding: str,
        jurisdiction_id: Optional[str] = None,
    ) -> Precedent:
        """Create a new precedent."""
        return cls(
            precedent_id=f"precedent:{uuid.uuid4().hex[:16]}",
            case_name=case_name,
            citation=citation,
            court=court,
            holding=holding,
            decision_date_utc=time.time(),
            compatible_jurisdictions=tuple([jurisdiction_id] if jurisdiction_id else []),
        )


@dataclass(frozen=True)
class PrecedentAnalysis:
    """
    Analysis of applicable precedents for a legal question.
    
    Includes identification of relevant precedents and
    assessment of their applicability to the current case.
    """
    
    # Identity
    analysis_id: str                          # Unique identifier
    
    # Input
    legal_question: str                       # Question being analyzed
    factual_context: Dict[str, Any] = field(default_factory=dict)  # Facts
    
    # Analysis results
    binding_precedents: Tuple[Precedent, ...] = ()
    persuasive_precedents: Tuple[Precedent, ...] = ()
    
    # Assessment
    precedent_conflicts_detected: bool = False
    interpretation_stability: Optional[str] = None  # e.g., "stable", "contested"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        legal_question: str,
        factual_context: Optional[Dict[str, Any]] = None,
    ) -> PrecedentAnalysis:
        """Create a new precedent analysis."""
        return cls(
            analysis_id=f"precedent_analysis:{uuid.uuid4().hex[:16]}",
            legal_question=legal_question,
            factual_context=factual_context or {},
        )
    
    def with_binding_precedents(self, precedents: List[Precedent]) -> PrecedentAnalysis:
        """Return a copy with updated binding precedents."""
        return dataclass_replace(
            self,
            binding_precedents=tuple(precedents),
        )
    
    def with_persuasive_precedents(self, precedents: List[Precedent]) -> PrecedentAnalysis:
        """Return a copy with updated persuasive precedents."""
        return dataclass_replace(
            self,
            persuasive_precedents=tuple(precedents),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "Precedent",
    "PrecedentAnalysis",
]