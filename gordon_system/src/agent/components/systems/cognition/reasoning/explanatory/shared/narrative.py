# Narrative Construction - Phase 7.14
# =====================================

"""
Narrative construction for explanatory reasoning.

Narratives organize:
    - Chronology
    - Causality
    - Support
    - Exceptions
    - Uncertainty

Narratives remain explicit and inspectable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class NarrativeIdentity:
    """
    Immutable identity for an explanatory narrative.
    """
    
    semantic_identity: str                    # Stable identity across runs
    narrative_number: int = 1                 # For repeated narratives
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, narrative_number: int = 1) -> NarrativeIdentity:
        """Create a new narrative identity."""
        return cls(
            semantic_identity=semantic_identity,
            narrative_number=narrative_number,
        )


@dataclass(frozen=True)
class NarrativeStep:
    """
    A single step in an explanatory narrative.
    
    Each step represents:
        - An event or claim
        - Its temporal position
        - Causal relationships to other steps
    """
    
    # Identity
    step_id: str                              # Unique identifier
    
    # Content
    claim: str                                # What happened?
    timestamp_utc: float                      # When did it happen?
    
    # Relationships
    causal_predecessors: Tuple[str, ...] = () # What caused this?
    supports: Tuple[str, ...] = ()            # What does this support?
    
    # Uncertainty
    confidence: float = 1.0                   # Confidence in the step


@dataclass(frozen=True)
class NarrativeConstruction:
    """
    Narrative construction for an explanation.
    
    Evaluates:
        - Logical flow
        - Causal flow
        - Temporal flow
        - Semantic coherence
        - Explanatory completeness
    """
    
    # Identity
    narrative_id: str                         # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Participating claims
    participating_claims: Tuple[str, ...]
    
    # Narrative structure
    narrative_steps: Tuple[NarrativeStep, ...]
    
    # Metrics
    step_count: int = 0                       # Total steps
    total_duration_seconds: float = 0.0       # Time span covered
    
    # Quality metrics
    coherence_score: float = 0.5              # How coherent is the narrative?
    causal_completeness: float = 0.5          # Are all causes explained?
    
    @classmethod
    def create(
        cls,
        participating_claims: List[str],
        steps: List[NarrativeStep],
        coherence_score: float = 0.5,
    ) -> "NarrativeConstruction":
        """Create a new narrative construction."""
        step_tuple = tuple(steps)
        
        # Calculate duration
        timestamps = [s.timestamp_utc for s in step_tuple]
        duration = max(timestamps) - min(timestamps) if timestamps else 0.0
        
        return cls(
            narrative_id=f"narrative:{uuid.uuid4().hex[:16]}",
            semantic_identity=participating_claims[0] if participating_claims else "unknown",
            participating_claims=tuple(participating_claims),
            narrative_steps=step_tuple,
            step_count=len(step_tuple),
            total_duration_seconds=duration,
            coherence_score=coherence_score,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "NarrativeIdentity",
    "NarrativeStep",
    "NarrativeConstruction",
]