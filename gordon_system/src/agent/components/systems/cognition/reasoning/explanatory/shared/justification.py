# Justification Analysis - Phase 7.14
# =====================================

"""
Justification analysis for explanatory reasoning.

Justifications include:
    - Logical justification
    - Causal justification
    - Probabilistic justification
    - Empirical justification
    - Structural justification
    - Comparative justification
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class JustificationKind(Enum):
    """Kinds of justifications in explanatory reasoning."""
    
    LOGICAL = "logical"                 # Deductive/inductive support
    CAUSAL = "causal"                   # Cause-effect support
    PROBABILISTIC = "probabilistic"     # Statistical likelihood
    EMPIRICAL = "empirical"             # Observational evidence
    STRUCTURAL = "structural"           # Pattern consistency
    COMPARATIVE = "comparative"         # Comparison to alternatives


@dataclass(frozen=True)
class JustificationIdentity:
    """
    Immutable identity for a justification.
    
    Allows replay and verification of justificatory analysis.
    """
    
    semantic_identity: str                    # Stable identity across runs
    justification_number: int = 1             # For repeated evaluations
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, justification_number: int = 1) -> JustificationIdentity:
        """Create a new justification identity."""
        return cls(
            semantic_identity=semantic_identity,
            justification_number=justification_number,
        )


@dataclass(frozen=True)
class JustificationStep:
    """
    A single reasoning step in a justification.
    
    Each step records:
        - The inference made
        - Supporting premises or evidence
        - Reasoning pattern used
    """
    
    # Identity
    step_id: str                              # Unique identifier
    
    # Inference
    conclusion: str                           # What was inferred?
    premise_ids: Tuple[str, ...] = ()         # Which premises support this?
    
    # Reasoning
    reasoning_pattern: str = "unknown"        # What pattern was used?
    rule_applied: Optional[str] = None        # Specific rule if applicable
    
    # Quality
    confidence: float = 1.0                   # Confidence in the step


@dataclass(frozen=True)
class JustificationAnalysis:
    """
    Justification analysis for an explanation.
    
    Evaluates:
        - Logical support
        - Causal support
        - Probabilistic support
        - Empirical support
        - Structural support
        - Counterfactual support
    
    Justifications remain explicit and inspectable.
    """
    
    # Identity
    justification_id: str                     # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Supported claims
    supported_claims: Tuple[str, ...]         # Which claims are justified?
    
    # Justification graph (step dependencies)
    justification_steps: Tuple[JustificationStep, ...]
    
    # Quality metrics
    total_steps: int = 0                      # Total reasoning steps
    supported_by_logical: int = 0             # Logical justifications
    supported_by_causal: int = 0              # Causal justifications
    supported_by_empirical: int = 0           # Empirical evidence
    
    # Overall assessment
    confidence: float = 0.5                   # Overall justification confidence
    completeness_score: float = 0.0           # How complete is the justification?
    
    @property
    def has_gaps(self) -> bool:
        """Check if there are gaps in justification."""
        return self.completeness_score < 1.0
    
    @classmethod
    def create(
        cls,
        supported_claims: List[str],
        steps: List[JustificationStep],
        confidence: float = 0.5,
    ) -> "JustificationAnalysis":
        """Create a new justification analysis."""
        step_tuple = tuple(steps)
        
        # Count by kind (simplified - in practice would categorize steps)
        logical_count = sum(1 for s in step_tuple if "logical" in s.reasoning_pattern.lower())
        causal_count = sum(1 for s in step_tuple if "causal" in s.reasoning_pattern.lower())
        empirical_count = sum(1 for s in step_tuple if "empirical" in s.reasoning_pattern.lower())
        
        return cls(
            justification_id=f"justification:{uuid.uuid4().hex[:16]}",
            semantic_identity=supported_claims[0] if supported_claims else "unknown",
            supported_claims=tuple(supported_claims),
            justification_steps=step_tuple,
            total_steps=len(step_tuple),
            supported_by_logical=logical_count,
            supported_by_causal=causal_count,
            supported_by_empirical=empirical_count,
            confidence=confidence,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "JustificationIdentity",
    "JustificationStep",
    "JustificationAnalysis",
    "JustificationKind",
]