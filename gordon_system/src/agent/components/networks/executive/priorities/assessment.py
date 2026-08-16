# Executive Priority Assessment
# =============================

"""
Executive Priority Assessment - Immutable dataclass describing priority assessments.

Priority is defined as a bounded executive assessment of the relative claim that one
goal, commitment, decision requirement, or Executive Program has on limited executive
control under the current context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutivePriorityAssessment:
    """
    Immutable priority assessment for a subject (goal, commitment, program).
    
    This assessment remains decomposable into evidence dimensions - it is NOT
    reduced to a single opaque score.
    
    Priority is distinct from:
        - Urgency (how quickly attention/action may be required)
        - Importance (consequence magnitude, enduring value)
        - Salience (significance or attention demand)
        - Motivation (drive, reward, aversion)
        - Focus (current endogenous attentional selection)
        - Scheduler priority (runtime mechanics)
    """
    
    # Identity
    assessment_id: str = "exec_priority_assessment_initial"
    """Unique identifier for this assessment."""
    
    subject_type: str = "goal"
    """Type of subject being assessed (goal, commitment, program)."""
    
    subject_id: str = "subject_initial"
    """ID of the subject being assessed."""
    
    # Priority level
    level: str = "normal"
    """Priority level (dormant, background, low, normal, elevated, high, critical, blocking, mandatory_review)."""
    
    ordering_class: str = "comparable"
    """How this item compares to others (comparable, incomparable, tied)."""
    
    # Evidence dimensions
    urgency_assessment: Optional[str] = None
    """Urgency assessment reference."""
    
    importance_assessment: Optional[str] = None
    """Importance assessment reference."""
    
    relevance_assessment: Optional[str] = None
    """Relevance to current context."""
    
    feasibility_assessment: Optional[str] = None
    """Feasibility assessment."""
    
    persistence_assessment: Optional[str] = None
    """Persistence assessment (should this remain active despite difficulty)."""
    
    # Pressure assessments
    commitment_pressure: str = "low"
    """Pressure from commitments."""
    
    risk_pressure: str = "neutral"
    """Risk-based pressure."""
    
    opportunity_pressure: str = "neutral"
    """Opportunity-based pressure."""
    
    dependency_pressure: str = "none"
    """Pressure from dependencies."""
    
    policy_pressure: str = "none"
    """Policy-imposed pressure."""
    
    security_pressure: str = "none"
    """Security-imposed pressure."""
    
    # External evidence
    motivational_support: Optional[str] = None
    """Motivational support projection reference (external)."""
    
    attentional_support: Optional[str] = None
    """Attentional support projection reference (external)."""
    
    supporting_evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence."""
    
    opposing_evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to opposing evidence."""
    
    conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Identified priority conflicts."""
    
    # Quality metrics
    confidence: float = 0.5
    """Confidence in this assessment (0.0 to 1.0)."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this assessment."""
    
    provenance: str = "executive_network"
    """Source of this assessment."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "ExecutivePriorityAssessment",
)