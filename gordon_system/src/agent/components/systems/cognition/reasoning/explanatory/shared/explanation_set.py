# Explanation Set - Phase 7.14
# =============================

"""
Explanation Sets define:
    - Supported claims
    - Available evidence
    - Supporting reasoning
    - Assumptions
    - Constraints
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ExplanationSetIdentity:
    """
    Immutable identity for an explanation set.
    
    Allows replay and verification of explanatory analysis.
    """
    
    semantic_identity: str                    # Stable identity across runs
    set_number: int = 1                       # For repeated evaluations
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, set_number: int = 1) -> ExplanationSetIdentity:
        """Create a new explanation set identity."""
        return cls(
            semantic_identity=semantic_identity,
            set_number=set_number,
        )


@dataclass(frozen=True)
class Claim:
    """
    A claim being explained or justified.
    
    Each claim has:
        - Content (what is claimed)
        - Status (supported, challenged, unknown)
        - Source (if applicable)
    """
    
    # Identity
    claim_id: str                             # Unique identifier
    
    # Content
    content: str                              # What is being claimed?
    claim_type: str = "assertion"             # Type of claim
    
    # Status
    status: str = "unknown"                   # supported, challenged, unknown
    confidence: float = 0.5                   # Confidence in the claim


@dataclass(frozen=True)
class ExplanationSet:
    """
    A complete set for explanatory reasoning.
    
    An explanation set contains all available and required information for
    constructing an explanation, including claims, evidence, assumptions,
    and constraints.
    """
    
    # Identity
    explanation_set_id: str                   # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Claims
    participating_claims: Tuple[Claim, ...]   # All claims in the set
    
    # Evidence
    evidence_sources: Tuple[str, ...] = ()    # Sources of evidence
    available_evidence: int = 0               # Number of evidence items
    
    # Scope
    explanation_scope: str = "global"         # What scope is being covered?
    
    # Constraints
    min_supporting_evidence: int = 1          # Minimum support required
    confidence_threshold: float = 0.5         # Threshold for accepting
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def claim_count(self) -> int:
        """Number of claims in the set."""
        return len(self.participating_claims)
    
    @property
    def supported_claim_count(self) -> int:
        """Count of supported claims."""
        return sum(1 for c in self.participating_claims if c.status == "supported")
    
    @classmethod
    def create(
        cls,
        claims: List[Claim],
        semantic_identity: str,
        evidence_sources: Optional[List[str]] = None,
        available_evidence: int = 0,
        explanation_scope: str = "global",
    ) -> "ExplanationSet":
        """Create a new explanation set."""
        return cls(
            explanation_set_id=f"exp_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_claims=tuple(claims),
            evidence_sources=tuple(evidence_sources or []),
            available_evidence=available_evidence,
            explanation_scope=explanation_scope,
        )
    
    def filter_by_status(self, status: str) -> "ExplanationSet":
        """Return a filtered set containing only claims with specified status."""
        filtered = tuple(c for c in self.participating_claims if c.status == status)
        return dataclass_replace(
            self,
            participating_claims=filtered,
            available_evidence=len(filtered),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExplanationSetIdentity",
    "Claim",
    "ExplanationSet",
]