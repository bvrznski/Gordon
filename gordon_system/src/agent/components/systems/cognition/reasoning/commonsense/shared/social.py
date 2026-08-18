# Social Intuition - Phase 7.45
# =============================

"""
Canonical social intuition contracts for Commonsense Reasoning.

Social intuition evaluates:
- Intentions, attention, ownership
- Personal space, turn taking, cooperation
- Social expectations
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# SOCIAL INTUITION IDENTITY
# =============================================================================

@dataclass(frozen=True)
class SocialIntuitionIdentity:
    """
    Immutable identity for a social intuition.
    """
    
    semantic_identity: str                    # Stable identity across runs
    context_hash: str                         # Hash of context that triggered this
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, context_hash: str) -> SocialIntuitionIdentity:
        """Create a new social intuition identity."""
        return cls(
            semantic_identity=semantic_identity,
            context_hash=context_hash,
        )


# =============================================================================
# SOCIAL EXPECTATION
# =============================================================================

@dataclass(frozen=True)
class SocialExpectation:
    """
    A social expectation inferred through intuition.
    
    Each expectation includes:
        - What is expected
        - Who is involved
        - Context where it applies
        - Confidence estimate
    """
    
    expectation_id: str                       # Unique identifier
    expected_behavior: str                    # e.g., "person will take turn speaking"
    involved_agents: List[str] = field(default_factory=list)  # Agent IDs involved
    context_conditions: List[str] = field(default_factory=list)  # When does this apply?
    
    confidence: float = 0.5                   # Confidence in this inference
    
    @classmethod
    def create(
        cls,
        expectation_id: str,
        expected_behavior: str,
        involved_agents: Optional[List[str]] = None,
        context_conditions: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> SocialExpectation:
        """Create a new social expectation."""
        return cls(
            expectation_id=expectation_id,
            expected_behavior=expected_behavior,
            involved_agents=involved_agents or [],
            context_conditions=context_conditions or [],
            confidence=confidence,
        )


# =============================================================================
# SOCIAL INTUITION MODEL
# =============================================================================

@dataclass(frozen=True)
class SocialIntuitionModel:
    """
    Model representing a social intuition.
    
    Each model includes:
        - The inferred social relationship/expectation
        - Supporting observations (behavioral, contextual)
        - Expected validity conditions
        - Confidence estimate
    
    Social intuitions remain explicit and inspectable.
    """
    
    # Identity
    intuition_id: str                         # Unique intuition identifier
    semantic_identity: str                    # Semantic identity of this intuition type
    
    # Inferred expectations
    inferred_expectations: List[str] = field(default_factory=list)
    
    # Support
    supporting_observations: Tuple[str, ...] = field(default_factory=tuple)  # Behavioral evidence
    context_hash: str                         # Hash of context that triggered this
    
    # Validity and confidence
    expected_validity_conditions: List[str] = field(default_factory=list)
    confidence: float = 0.5
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        inferred_expectations: List[str],
        supporting_observations: Tuple[str, ...],
        context_hash: str,
        expected_validity_conditions: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> SocialIntuitionModel:
        """Create a new social intuition model."""
        return cls(
            intuition_id=f"social_intuition:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            inferred_expectations=inferred_expectations,
            supporting_observations=supporting_observations,
            context_hash=context_hash,
            expected_validity_conditions=expected_validity_conditions or [],
            confidence=confidence,
        )
    
    def get_expectation(self, behavior: str) -> Optional[str]:
        """Find a specific expectation by behavior description."""
        for exp in self.inferred_expectations:
            if behavior in exp:
                return exp
        return None


# =============================================================================
# SOCIAL COMMONSENSE RECORD
# =============================================================================

@dataclass(frozen=True)
class SocialCommonsense:
    """
    Record of social commonsense inference.
    
    Each record includes:
        - The social intuition model itself
        - Contextual evaluation
        - Confidence assessment
        - Provenance tracking
    
    This is the primary contract for accessing social intuitions during reasoning.
    """
    
    # Identity
    record_id: str                            # Unique record identifier
    semantic_identity: str                    # Semantic identity of this record
    
    # Social data
    social_intuition: SocialIntuitionModel    # The actual intuition
    
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
        social_intuition: SocialIntuitionModel,
        context_compatible: bool,
        effective_confidence: float = 0.5,
    ) -> SocialCommonsense:
        """Create a new social commonsense record."""
        return cls(
            record_id=f"social_commonsense:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            social_intuition=social_intuition,
            context_compatible=context_compatible,
            effective_confidence=effective_confidence,
        )


# =============================================================================
# SOCIAL INTUITION TYPES
# =============================================================================

class SocialIntuitionType(Enum):
    """Types of social intuitions."""
    
    INTENTION = "intention"                   # Agent has a goal/intent
    ATTENTION = "attention"                   # Agent is attending to something
    OWNERSHIP = "ownership"                   # Agent owns this object
    PERSONAL_SPACE = "personal_space"         # Spatial boundaries respected
    TURN_TAKING = "turn_taking"               # Fair turn distribution expected
    COOPERATION = "cooperation"               # Agents cooperate towards goals
    SOCIAL_EXPECTATION = "social_expectation" # General social norms


# =============================================================================
# SOCIAL TRACE
# =============================================================================

@dataclass(frozen=True)
class SocialTrace:
    """
    Complete trace of social intuition through reasoning.
    
    A trace contains:
        - Original social intuition model
        - All contexts it was applied in
        - Validation results
        - Confidence evolution
    """
    
    # Identity
    trace_id: str                             # Unique trace identifier
    
    # Social data
    social_intuition: SocialIntuitionModel    # The original intuition
    
    # Application history
    applications: List[Tuple[str, float]] = field(default_factory=list)
    
    # Validation history
    validations: List[Tuple[bool, Optional[str], float]] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, social_intuition: SocialIntuitionModel) -> SocialTrace:
        """Create a new social trace."""
        return cls(
            trace_id=f"social_trace:{uuid.uuid4().hex[:16]}",
            social_intuition=social_intuition,
        )


__all__ = [
    "SocialIntuitionIdentity",
    "SocialExpectation",
    "SocialIntuitionModel",
    "SocialCommonsense",
    "SocialIntuitionType",
    "SocialTrace",
]