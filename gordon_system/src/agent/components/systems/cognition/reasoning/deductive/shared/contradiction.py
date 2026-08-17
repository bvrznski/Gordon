# Deduction Contradiction - Phase 7.1
# =====================================

"""
Canonical Contradiction Contract.

Contradictions are detected and analyzed during deduction.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DeductionContradiction:
    """
    A contradiction detected during deductive reasoning.
    
    A contradiction contains:
        - Identity and provenance tracking
        - Conflicting premises (A and NOT A)
        - Supporting proofs for each side
        - Diagnostics
    
    Contradictions remain explicit; they do not modify the premises.
    """
    
    # Identity
    contradiction_id: str                   # Unique contradiction identifier
    
    # Conflicting premises
    conflicting_premises: Tuple[str, ...]   # The premises that conflict (e.g., "P", "NOT P")
    
    # Supporting proofs for each side
    supporting_proofs: Tuple[str, ...]      # Proof IDs that lead to these conclusions
    
    # Diagnostics
    contradiction_type: str = "direct"      # direct, indirect, circular, etc.
    root_cause: Optional[str] = None        # What caused this?
    
    # Provenance
    detected_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None  # Which deduction session?
    
    @property
    def premise_count(self) -> int:
        """Count of conflicting premises."""
        return len(self.conflicting_premises)
    
    @classmethod
    def create(
        cls,
        conflicting_premises: List[str],
        supporting_proofs: Optional[List[str]] = None,
        contradiction_type: str = "direct",
        root_cause: Optional[str] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> DeductionContradiction:
        """Create a new contradiction record."""
        return cls(
            contradiction_id=f"contradiction:{uuid.uuid4().hex[:16]}",
            conflicting_premises=tuple(conflicting_premises),
            supporting_proofs=tuple(supporting_proofs or []),
            contradiction_type=contradiction_type,
            root_cause=root_cause,
            source_descriptor_id=source_descriptor_id,
        )


@dataclass(frozen=True)
class ContradictionAnalysis:
    """
    An analysis of a detected contradiction.
    
    Analysis identifies:
        - Minimal conflicting premises
        - Conflicting assumptions
        - Invalid rule applications
        - Missing premises
    
    Analysis remains explicit; it does not modify the reasoning.
    """
    
    # Identity
    analysis_id: str                        # Unique analysis identifier
    
    # Target contradiction
    contradiction: DeductionContradiction   # What was analyzed?
    
    # Conflicting proofs (detailed)
    conflicting_proofs: Tuple[str, ...]     # Full proof records involved
    
    # Root cause identification
    root_cause: Optional[str] = None        # What caused this contradiction?
    contributing_factors: Tuple[str, ...] = ()  # Additional contributing factors
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()   # How to resolve?
    
    # Provenance
    analyzed_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None  # Which deduction session?
    
    @property
    def is_resolvable(self) -> bool:
        """Check if the contradiction appears resolvable."""
        return len(self.recommendations) > 0
    
    @classmethod
    def create(
        cls,
        contradiction: DeductionContradiction,
        conflicting_proofs: Optional[List[str]] = None,
        root_cause: Optional[str] = None,
        contributing_factors: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> ContradictionAnalysis:
        """Create a new contradiction analysis."""
        return cls(
            analysis_id=f"contradiction_analysis:{uuid.uuid4().hex[:16]}",
            contradiction=contradiction,
            conflicting_proofs=tuple(conflicting_proofs or []),
            root_cause=root_cause,
            contributing_factors=tuple(contributing_factors or []),
            recommendations=tuple(recommendations or []),
            source_descriptor_id=source_descriptor_id,
        )
    
    def with_recommendation(self, recommendation: str) -> ContradictionAnalysis:
        """Return a copy with an additional recommendation."""
        return dataclass_replace(
            self,
            recommendations=self.recommendations + (recommendation,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DeductionContradiction",
    "ContradictionAnalysis",
]