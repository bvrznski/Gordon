# Plausibility Estimation - Phase 7.45
# ====================================

"""
Canonical plausibility contracts for Commonsense Reasoning.

Plausibility evaluates:
- Expected events
- Unexpected events
- Normality
- Rarity
- Exceptionality
- Confidence estimates
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# PLAUSIBILITY IDENTITY
# =============================================================================

@dataclass(frozen=True)
class PlausibilityIdentity:
    """
    Immutable identity for a plausibility analysis.
    """
    
    semantic_identity: str                    # Stable identity across runs
    context_hash: str                         # Hash of context that triggered this
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, context_hash: str) -> PlausibilityIdentity:
        """Create a new plausibility identity."""
        return cls(
            semantic_identity=semantic_identity,
            context_hash=context_hash,
        )


# =============================================================================
# PLAUSIBILITY SCORE
# =============================================================================

@dataclass(frozen=True)
class PlausibilityScore:
    """
    A numerical score for the plausibility of an event.
    
    Each score includes:
        - The plausibility value (0-1)
        - Confidence in the score
        - Supporting evidence
        - Contextual factors
    """
    
    score_id: str                             # Unique identifier
    plausibility_value: float                 # 0.0 to 1.0
    confidence: float = 0.5                   # Confidence in this score
    
    supporting_factors: List[str] = field(default_factory=list)  # Why is it plausible?
    contextual_factors: List[str] = field(default_factory=list)  # Context modifiers
    
    @classmethod
    def create(
        cls,
        score_id: str,
        plausibility_value: float,
        confidence: float = 0.5,
        supporting_factors: Optional[List[str]] = None,
        contextual_factors: Optional[List[str]] = None,
    ) -> PlausibilityScore:
        """Create a new plausibility score."""
        return cls(
            score_id=score_id,
            plausibility_value=min(1.0, max(0.0, plausibility_value)),
            confidence=confidence,
            supporting_factors=supporting_factors or [],
            contextual_factors=contextual_factors or [],
        )


# =============================================================================
# PLAUSIBILITY MODEL
# =============================================================================

@dataclass(frozen=True)
class PlausibilityModel:
    """
    Model representing a plausibility analysis.
    
    Each model includes:
        - The event being analyzed
        - Plausibility estimate
        - Exception handling
        - Confidence estimate
    
    Plausibility analyses remain explicit and inspectable.
    """
    
    # Identity
    plausibility_id: str                      # Unique identifier
    semantic_identity: str                    # Semantic identity of this analysis type
    
    # Event being analyzed
    event_description: str                    # What is being evaluated?
    
    # Plausibility assessment
    plausibility_score: PlausibilityScore     # Numerical score and confidence
    
    # Exception handling
    known_exceptions: List[str] = field(default_factory=list)  # When is it less plausible?
    unexpected_triggers: List[str] = field(default_factory=list)  # What makes it surprising?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        event_description: str,
        plausibility_value: float,
        confidence: float = 0.5,
        known_exceptions: Optional[List[str]] = None,
        unexpected_triggers: Optional[List[str]] = None,
    ) -> PlausibilityModel:
        """Create a new plausibility model."""
        return cls(
            plausibility_id=f"plausibility:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            event_description=event_description,
            plausibility_score=PlausibilityScore.create(
                score_id=f"score:{uuid.uuid4().hex[:8]}",
                plausibility_value=plausibility_value,
                confidence=confidence,
            ),
            known_exceptions=known_exceptions or [],
            unexpected_triggers=unexpected_triggers or [],
        )
    
    @property
    def is_highly_improbable(self) -> bool:
        """Check if the event is highly improbable (low plausibility)."""
        return self.plausibility_score.plausibility_value < 0.1
    
    @property
    def is_expected(self) -> bool:
        """Check if the event is expected (high plausibility)."""
        return self.plausibility_score.plausibility_value > 0.8


# =============================================================================
# PLAUSIBILITY MANAGEMENT RECORD
# =============================================================================

@dataclass(frozen=True)
class PlausibilityManagement:
    """
    Record of plausibility management.
    
    Each record includes:
        - The plausibility model itself
        - Contextual evaluation
        - Confidence assessment
        - Provenance tracking
    
    This is the primary contract for accessing plausibility during reasoning.
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity of this record
    
    # Plausibility data
    plausibility_model: PlausibilityModel     # The actual analysis
    
    # Evaluation
    context_compatible: bool = True           # Is current context compatible?
    
    # Confidence assessment
    effective_confidence: float = 0.5         # Final confidence after evaluation
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        plausibility_model: PlausibilityModel,
        context_compatible: bool,
        effective_confidence: float = 0.5,
    ) -> PlausibilityManagement:
        """Create a new plausibility management record."""
        return cls(
            management_id=f"plausibility_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            plausibility_model=plausibility_model,
            context_compatible=context_compatible,
            effective_confidence=effective_confidence,
        )


# =============================================================================
# PLAUSIBILITY TYPES
# =============================================================================

class PlausibilityType(Enum):
    """Types of plausibility analyses."""
    
    EVENT = "event"                           # Event occurrence
    STATE = "state"                           # State of affairs
    ACTION = "action"                         # Action execution
    TRANSITION = "transition"                 # State transition
    EXCEPTION = "exception"                   # Exception to norms


# =============================================================================
# PLAUSIBILITY TRACE
# =============================================================================

@dataclass(frozen=True)
class PlausibilityTrace:
    """
    Complete trace of plausibility analysis through reasoning.
    
    A trace contains:
        - Original plausibility model
        - All contexts it was applied in
        - Validation results
        - Confidence evolution
    """
    
    # Identity
    trace_id: str                             # Unique trace identifier
    
    # Plausibility data
    plausibility_model: PlausibilityModel     # The original analysis
    
    # Application history
    applications: List[Tuple[str, float]] = field(default_factory=list)
    
    # Validation history
    validations: List[Tuple[bool, Optional[str], float]] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, plausibility_model: PlausibilityModel) -> PlausibilityTrace:
        """Create a new plausibility trace."""
        return cls(
            trace_id=f"plausibility_trace:{uuid.uuid4().hex[:16]}",
            plausibility_model=plausibility_model,
        )


__all__ = [
    "PlausibilityIdentity",
    "PlausibilityScore",
    "PlausibilityModel",
    "PlausibilityManagement",
    "PlausibilityType",
    "PlausibilityTrace",
]