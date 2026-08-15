# Gordon Executive Decision Evidence - Phase 4.4.10A
# ====================================================

"""
Decision Evidence and Justification System.

This module defines the evidence and justification system for Executive Decisions.
Evidence records the semantic basis supporting the decision. Justification
explains why the Executive Network accepted the commitment.


EVIDENCE OVERVIEW
=================

    Evidence is immutable. It is referenced, never duplicated.
    
    Evidence types:
        - Observations
        - Predictions
        - Measurements
        - Analyses
        - Reasoning Results
        - Policies
        - Security Assessments
        - User Requests
        - Historical Experience

ARCHITECTURAL LAWS
==================

E-021: Evidence shall be referenced, never embedded as mutable runtime state.
E-022: Justification shall describe semantic rationale, never implementation details.
"""

from dataclasses import dataclass, field
from typing import Tuple
from enum import Enum


# =============================================================================
# EVIDENCE SOURCES - Origin types for evidence
# =============================================================================

class EvidenceSource(Enum):
    """
    Source categories for decision evidence.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    OBSERVATION = "observation"
    """Direct observation of system state."""
    
    PREDICTION = "prediction"
    """Predictive analysis or forecast."""
    
    MEASUREMENT = "measurement"
    """Quantitative measurement data."""
    
    ANALYSIS = "analysis"
    """Analytical result from processing."""
    
    REASONING_RESULT = "reasoning_result"
    """Semantic conclusion from reasoning."""
    
    POLICY = "policy"
    """Policy constraint or guidance."""
    
    SECURITY_ASSESSMENT = "security_assessment"
    """Security evaluation or audit."""
    
    USER_REQUEST = "user_request"
    """Request from external user or system."""
    
    HISTORICAL_EXPERIENCE = "historical_experience"
    """Past experience from similar situations."""


# =============================================================================
# EVIDENCE KINDS - Evidence categories
# =============================================================================

class EvidenceKind(Enum):
    """
    Categories of evidence for decisions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    OBSERVATION = "observation"
    """Verifiable factual information."""
    
    ANALYSIS = "analysis"
    """Analysis or inference from facts."""
    
    PREDICTION = "prediction"
    """Forecast or prediction about future states."""
    
    POLICY = "policy"
    """Policy-based constraint or guidance."""
    
    SECURITY_ASSESSMENT = "security_assessment"
    """Security-related assessment."""


# =============================================================================
# DECISION EVIDENCE - Semantic support record
# =============================================================================

@dataclass(frozen=True)
class DecisionEvidence:
    """
    Record of semantic evidence supporting an Executive Decision.
    
    Evidence records the semantic basis that supported the decision. Evidence
    remains immutable and is referenced, never duplicated.
    
    Runtime-neutral: Yes
    Executable: No
    
    Examples:
        - Observations about system state
        - Predictions from analysis
        - Measurements confirming conditions
        - Analyses supporting conclusions
        
    Example:
        >>> evidence = DecisionEvidence(
        ...     source=EvidenceSource.OBSERVATION,
        ... )
    """
    
    source: EvidenceSource = EvidenceSource.OBSERVATION
    """Origin of the evidence."""
    
    kind: EvidenceKind = EvidenceKind.OBSERVATION
    """Category of evidence."""
    
    reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of supporting evidence artifacts."""
    
    confidence: float = 1.0
    """Confidence level in this evidence (0.0 to 1.0)."""
    
    @property
    def is_evidence(self) -> bool:
        """Return True for all evidence records."""
        return True
    
    def has_reference(self, reference_id: str) -> bool:
        """
        Check if a specific reference is part of this evidence.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return reference_id in self.reference_ids


# =============================================================================
# DECISION JUSTIFICATION - Semantic rationale record
# =============================================================================

@dataclass(frozen=True)
class DecisionJustification:
    """
    Record of semantic justification for an Executive Decision commitment.
    
    Justification explains why the Executive Network accepted the commitment.
    It is structured and records semantic rationale, not implementation details.
    
    Runtime-neutral: Yes
    Executable: No
    
    Typical elements:
        - Supporting goals
        - Supporting strategy
        - Supporting evidence
        - Governing policies
        - Architectural constraints
        - Expected benefits
        - Accepted risks
        - Rejected alternatives
        - Decision assumptions
        
    Example:
        >>> justification = DecisionJustification(
        ...     supporting_goals=("goal_abc123",),
        ... )
    """
    
    supporting_goals: Tuple[str, ...] = field(default_factory=tuple)
    """Goals supported by this decision."""
    
    supporting_strategy: str = ""
    """Strategy supported by this decision."""
    
    supporting_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs supporting the decision."""
    
    governing_policies: Tuple[str, ...] = field(default_factory=tuple)
    """Policies that govern or support this decision."""
    
    architectural_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints that affect the decision."""
    
    expected_benefits: Tuple[str, ...] = field(default_factory=tuple)
    """Expected outcomes if commitment is honored."""
    
    accepted_risks: Tuple[str, ...] = field(default_factory=tuple)
    """Risks acknowledged in making this commitment."""
    
    rejected_alternatives: Tuple[str, ...] = field(default_factory=tuple)
    """Alternatives considered and rejected."""
    
    decision_assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions underlying the justification."""
    
    @property
    def is_justification(self) -> bool:
        """Return True for all justification records."""
        return True
    
    def has_supporting_goal(self, goal_id: str) -> bool:
        """Check if a specific goal is supported by this justification."""
        return goal_id in self.supporting_goals


# =============================================================================
# EVIDENCE AND JUSTIFICATION VALIDATION - Validation utilities
# =============================================================================

class EvidenceValidation:
    """
    Static validation utilities for DecisionEvidence and DecisionJustification.
    
    Runtime-neutral: Yes
    Executable: No
    
    All methods are pure and deterministic.
    """
    
    @staticmethod
    def is_valid_source(source: EvidenceSource) -> bool:
        """Validate that an evidence source is valid."""
        return isinstance(source, EvidenceSource)
    
    @staticmethod
    def is_valid_kind(kind: EvidenceKind) -> bool:
        """Validate that an evidence kind is valid."""
        return isinstance(kind, EvidenceKind)
    
    @staticmethod
    def is_valid_confidence(confidence: float) -> bool:
        """Validate that a confidence level is in range [0.0, 1.0]."""
        return isinstance(confidence, (int, float)) and 0.0 <= confidence <= 1.0