# Explanation Construction - Phase 7.14
# ======================================

"""
Explanation construction for explanatory reasoning.

Canonical explanation construction:
    Reasoning Results -> Evidence Collection -> Claim Organization ->
    Justification Construction -> Explanation Model -> Validation -> Publication

Construction remains deterministic.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ConstructionIdentity:
    """
    Immutable identity for an explanation construction process.
    """
    
    semantic_identity: str                    # Stable identity across runs
    construction_number: int = 1              # For repeated constructions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, construction_number: int = 1) -> ConstructionIdentity:
        """Create a new construction identity."""
        return cls(
            semantic_identity=semantic_identity,
            construction_number=construction_number,
        )


@dataclass(frozen=True)
class ExplanationStrategy:
    """
    Strategy for constructing an explanation.
    
    Strategies determine:
        - Evidence weighting
        - Claim organization
        - Narrative structure
        - Validation approach
    """
    
    # Identity
    strategy_id: str                          # Unique identifier
    
    # Type
    strategy_type: str = "default"            # What kind of strategy?
    
    # Parameters
    evidence_weight: float = 1.0              # How much weight for evidence?
    claim_priority_order: Tuple[str, ...] = () # Priority of claims


@dataclass(frozen=True)
class ExplanationConstruction:
    """
    Construction process and result for an explanation.
    
    Canonical construction flow:
        Reasoning Results -> Evidence Collection -> Claim Organization ->
        Justification Construction -> Explanation Model -> Validation -> Publication
    
    Every stage remains independently observable.
    """
    
    # Identity
    construction_id: str                      # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Strategy used
    explanation_strategy: ExplanationStrategy
    
    # Resulting model (if completed)
    resulting_model: Optional[Dict[str, Any]] = None  # The constructed explanation
    
    # Process tracking
    evidence_collected_count: int = 0         # How much evidence?
    claims_organized_count: int = 0           # How many claims?
    justifications_constructed_count: int = 0 # How many justifications?
    
    # Process timestamps
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate construction duration."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        return time.time() - self.started_at_utc
    
    @property
    def is_completed(self) -> bool:
        """Check if construction completed."""
        return self.resulting_model is not None
    
    @classmethod
    def create(
        cls,
        explanation_strategy: ExplanationStrategy,
        semantic_identity: str,
        evidence_collected_count: int = 0,
        claims_organized_count: int = 0,
        justifications_constructed_count: int = 0,
    ) -> "ExplanationConstruction":
        """Create a new construction record."""
        return cls(
            construction_id=f"construction:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            explanation_strategy=explanation_strategy,
            evidence_collected_count=evidence_collected_count,
            claims_organized_count=claims_organized_count,
            justifications_constructed_count=justifications_constructed_count,
            started_at_utc=time.time(),
        )
    
    def with_result(self, model: Dict[str, Any]) -> "ExplanationConstruction":
        """Return a completed construction record."""
        return dataclass_replace(
            self,
            resulting_model=model,
            completed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ConstructionIdentity",
    "ExplanationStrategy",
    "ExplanationConstruction",
]