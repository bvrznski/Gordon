# Deductive Lemma - Phase 7.1
# ============================

"""
Canonical Deductive Lemma Contract.

Lemmas are reusable proofs that can be referenced in subsequent deductions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DeductiveLemma:
    """
    A reusable deductive proof (lemma).
    
    A lemma contains:
        - Identity and provenance tracking
        - The supporting validated proof
        - Applicability conditions
        - Dependencies (what this lemma requires)
    
    Lemmas preserve their original proofs; they never replace canonical proofs.
    """
    
    # Identity
    lemma_id: str                           # Unique lemma identifier
    
    # Supporting proof
    supporting_proof: str                   # The validated proof that this is based on
    
    # Applicability conditions
    applicability_conditions: Tuple[str, ...] = ()  # When can this be applied?
    
    # Dependencies (what premises/assumptions are needed)
    dependencies: Tuple[str, ...] = ()      # Required supporting elements
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    validated_at_utc: Optional[float] = None  # When was this proof validated?
    origin_artifact: Optional[str] = None   # Where did this lemma come from?
    
    @property
    def is_applicable(self) -> bool:
        """Check if the lemma appears applicable in current context."""
        return len(self.applicability_conditions) == 0
    
    @classmethod
    def create(
        cls,
        supporting_proof: str,
        applicability_conditions: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        origin_artifact: Optional[str] = None,
    ) -> DeductiveLemma:
        """Create a new deductive lemma."""
        return cls(
            lemma_id=f"deductive_lemma:{uuid.uuid4().hex[:16]}",
            supporting_proof=supporting_proof,
            applicability_conditions=tuple(applicability_conditions or []),
            dependencies=tuple(dependencies or []),
            origin_artifact=origin_artifact,
        )
    
    def with_condition(self, condition: str) -> DeductiveLemma:
        """Return a copy with an additional applicability condition."""
        return dataclass_replace(
            self,
            applicability_conditions=self.applicability_conditions + (condition,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DeductiveLemma",
]