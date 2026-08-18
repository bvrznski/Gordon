# Assumption Management - Phase 7.45
# ====================================

"""
Canonical assumption contracts for Commonsense Reasoning.

Assumptions represent implicit conclusions supported by ordinary experience.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# ASSUMPTION IDENTITY
# =============================================================================

@dataclass(frozen=True)
class AssumptionIdentity:
    """
    Immutable identity for an assumption.
    
    Allows replay and verification of assumptions made during reasoning.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    context_hash: str                         # Hash of supporting context
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, context_hash: str) -> AssumptionIdentity:
        """Create a new assumption identity."""
        return cls(
            semantic_identity=semantic_identity,
            context_hash=context_hash,
        )


# =============================================================================
# SUPPORTING OBSERVATION
# =============================================================================

@dataclass(frozen=True)
class SupportingObservation:
    """
    An observation that supports an assumption.
    
    Each observation includes its source, confidence, and relationship to the assumption.
    """
    
    observation_id: str                       # Unique identifier
    description: str                          # What was observed?
    source_context: Optional[str] = None      # Where did this come from?
    confidence: float = 1.0                   # Confidence in this observation (0-1)
    temporal_offset: float = 0.0              # Seconds relative to current moment
    
    @classmethod
    def create(
        cls,
        observation_id: str,
        description: str,
        source_context: Optional[str] = None,
        confidence: float = 1.0,
        temporal_offset: float = 0.0,
    ) -> SupportingObservation:
        """Create a new supporting observation."""
        return cls(
            observation_id=observation_id,
            description=description,
            source_context=source_context,
            confidence=confidence,
            temporal_offset=temporal_offset,
        )


# =============================================================================
# ASSUMPTION MODEL
# =============================================================================

@dataclass(frozen=True)
class AssumptionModel:
    """
    Model representing an inferred assumption.
    
    Each assumption includes:
        - The inferred statement (what was assumed)
        - Supporting observations (why it's assumed)
        - Expected validity conditions
        - Confidence estimate
        - Provenance tracking
    
    Assumptions remain explicit and inspectable.
    """
    
    # Identity
    assumption_id: str                        # Unique assumption identifier
    semantic_identity: str                    # Semantic identity of the assumption type
    
    # Inferred statement
    inferred_statement: str                   # What is assumed to be true?
    
    # Support
    supporting_observations: Tuple[SupportingObservation, ...]  # Evidence for the assumption
    context_hash: str                         # Hash of context that triggered this
    
    # Validity and confidence
    expected_validity_conditions: List[str] = field(default_factory=list)  # When is this valid?
    confidence: float = 0.5                   # Confidence in the inference (0-1)
    
    # Scope
    applicability_scope: Optional[str] = None  # e.g., "indoor_environment"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        inferred_statement: str,
        supporting_observations: Tuple[SupportingObservation, ...],
        context_hash: str,
        expected_validity_conditions: Optional[List[str]] = None,
        confidence: float = 0.5,
        applicability_scope: Optional[str] = None,
    ) -> AssumptionModel:
        """Create a new assumption model."""
        return cls(
            assumption_id=f"assumption:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            inferred_statement=inferred_statement,
            supporting_observations=supporting_observations,
            context_hash=context_hash,
            expected_validity_conditions=expected_validity_conditions or [],
            confidence=confidence,
            applicability_scope=applicability_scope,
        )
    
    def get_supporting_observation(self, description: str) -> Optional[SupportingObservation]:
        """Find a supporting observation by its description."""
        for obs in self.supporting_observations:
            if obs.description == description:
                return obs
        return None
    
    @property
    def minimum_confidence(self) -> float:
        """Get the minimum confidence from supporting observations."""
        if not self.supporting_observations:
            return 0.0
        return min(obs.confidence for obs in self.supporting_observations)


# =============================================================================
# APPLICABILITY CONDITIONS
# =============================================================================

@dataclass(frozen=True)
class ApplicabilityConditions:
    """
    Conditions under which an assumption is applicable.
    
    These define the boundaries of when an assumption should be used.
    """
    
    condition_id: str                         # Unique identifier
    required_contexts: List[str] = field(default_factory=list)  # Required conditions
    forbidden_contexts: List[str] = field(default_factory=list)  # Conditions that invalidate it
    
    @classmethod
    def create(
        cls,
        condition_id: str,
        required_contexts: Optional[List[str]] = None,
        forbidden_contexts: Optional[List[str]] = None,
    ) -> ApplicabilityConditions:
        """Create new applicability conditions."""
        return cls(
            condition_id=condition_id,
            required_contexts=required_contexts or [],
            forbidden_contexts=forbidden_contexts or [],
        )


# =============================================================================
# ASSUMPTION MANAGEMENT RECORD
# =============================================================================

@dataclass(frozen=True)
class AssumptionManagement:
    """
    Record of assumption management.
    
    Each record includes:
        - The assumption model itself
        - Applicability evaluation
        - Confidence assessment
        - Provenance tracking
    
    This is the primary contract for accessing assumptions during reasoning.
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity of this management record
    
    # Assumption data
    assumption_model: AssumptionModel         # The actual assumption
    
    # Applicability evaluation
    applicability_conditions_met: bool        # Are current conditions applicable?
    
    # Confidence assessment
    effective_confidence: float = 0.5         # Confidence after context evaluation
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        assumption_model: AssumptionModel,
        applicability_conditions_met: bool,
        effective_confidence: float = 0.5,
    ) -> AssumptionManagement:
        """Create a new assumption management record."""
        return cls(
            management_id=f"assumption_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            assumption_model=assumption_model,
            applicability_conditions_met=applicability_conditions_met,
            effective_confidence=effective_confidence,
        )


# =============================================================================
# ASSUMPTION TRACE
# =============================================================================

@dataclass(frozen=True)
class AssumptionTrace:
    """
    Complete trace of an assumption through reasoning.
    
    A trace contains:
        - Original assumption model
        - All context it was applied in
        - Validation results
        - Confidence evolution
    
    Traces remain inspectable for debugging and verification.
    """
    
    # Identity
    trace_id: str                             # Unique trace identifier
    
    # Assumption data
    assumption_model: AssumptionModel         # The original assumption
    
    # Application history
    applications: List[Tuple[str, float]] = field(default_factory=list)  # (context_hash, confidence)
    
    # Validation history
    validations: List[Tuple[bool, Optional[str], float]] = field(default_factory=list)  # (passed, reason, confidence)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, assumption_model: AssumptionModel) -> AssumptionTrace:
        """Create a new assumption trace."""
        return cls(
            trace_id=f"assumption_trace:{uuid.uuid4().hex[:16]}",
            assumption_model=assumption_model,
        )
    
    def record_application(self, context_hash: str, confidence: float) -> None:
        """Record an application of this assumption."""
        self.applications.append((context_hash, confidence))
    
    def record_validation(
        self,
        passed: bool,
        reason: Optional[str] = None,
        confidence: float = 1.0,
    ) -> None:
        """Record a validation result."""
        self.validations.append((passed, reason, confidence))


__all__ = [
    "AssumptionIdentity",
    "SupportingObservation",
    "AssumptionModel",
    "ApplicabilityConditions",
    "AssumptionManagement",
    "AssumptionTrace",
]