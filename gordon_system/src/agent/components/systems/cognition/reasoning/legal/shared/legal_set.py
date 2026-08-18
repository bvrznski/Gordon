# Legal Set - Phase 7.47 Part 1
# ==============================

"""
Canonical Legal Set Contract.

Legal Sets define:
    - applicable jurisdictions
    - known facts
    - legal sources
    - legal constraints
    - requested determinations

Legal Sets remain immutable during reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class LegalSet:
    """
    Immutable container for all legal reasoning inputs.
    
    A Legal Set includes:
        - Jurisdictions to be analyzed
        - Legal sources (statutes, regulations, precedents)
        - Factual context (known facts)
        - Requested determinations (questions to answer)
        - Legal constraints (pre-existing constraints)
    
    Legal Sets remain immutable during reasoning to ensure
    reproducible and traceable legal analyses.
    """
    
    # Identity
    legal_set_id: str                         # Unique identifier
    
    # Jurisdictions
    jurisdictions: Tuple[str, ...]            # Applicable jurisdictions
    
    # Legal sources
    legal_sources: Dict[str, Any] = field(default_factory=dict)  # Source ID -> source data
    
    # Facts
    factual_context: Dict[str, Any] = field(default_factory=dict)  # Known facts
    
    # Requested determinations
    requested_determinations: Tuple[str, ...] = ()   # Questions to answer
    
    # Constraints
    legal_constraints: Tuple[str, ...] = ()          # Pre-existing constraints
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)  # Source tracking
    
    @classmethod
    def create(
        cls,
        jurisdictions: Optional[List[str]] = None,
        factual_context: Optional[Dict[str, Any]] = None,
        requested_determinations: Optional[List[str]] = None,
        legal_sources: Optional[Dict[str, Any]] = None,
        legal_constraints: Optional[List[str]] = None,
    ) -> LegalSet:
        """Create a new legal set."""
        return cls(
            legal_set_id=f"legal_set:{uuid.uuid4().hex[:16]}",
            jurisdictions=tuple(jurisdictions or []),
            factual_context=factual_context or {},
            requested_determinations=tuple(requested_determinations or []),
            legal_sources=legal_sources or {},
            legal_constraints=tuple(legal_constraints or []),
        )
    
    def with_jurisdictions(self, jurisdictions: List[str]) -> LegalSet:
        """Return a copy with updated jurisdictions."""
        return dataclass_replace(
            self,
            jurisdictions=tuple(jurisdictions),
        )
    
    def with_factual_context(self, factual_context: Dict[str, Any]) -> LegalSet:
        """Return a copy with updated factual context."""
        return dataclass_replace(
            self,
            factual_context=factual_context,
        )
    
    def with_requested_determinations(self, determinations: List[str]) -> LegalSet:
        """Return a copy with updated requested determinations."""
        return dataclass_replace(
            self,
            requested_determinations=tuple(determinations),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "LegalSet",
]