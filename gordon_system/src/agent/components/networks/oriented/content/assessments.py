# Oriented Network Assessment Content Types - Phase 4.7.3
# =======================================================

"""
Assessment content types for the Oriented Network.

Assessment Content represents semantic evaluations without runtime computation.
Assessments are observations, not algorithms.

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-011: AssessmentContent evaluates OrientationContent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from enum import Enum

from gordon_system.src.agent.components.networks.oriented.content.base import (
    BaseContent,
    ContentIdentity,
)


# =============================================================================
# ASSESSMENT TYPE ENUMERATIONS
# =============================================================================

class AssessmentType(Enum):
    """
    Canonical assessment types for Oriented Network content.
    """
    
    PROGRESS = "progress"
    ALIGNMENT = "alignment"
    CONFIDENCE = "confidence"
    RISK = "risk"
    RECOVERY = "recovery"
    COMPLETION = "completion"
    DRIFT = "drift"


# =============================================================================
# ASSESSMENT CONTENT TYPES
# =============================================================================

@dataclass(frozen=True)
class ProgressAssessment(BaseContent):
    """
    Assessment of progress toward a target.
    
    SEMANTIC ROLE:
        - Describes semantic progress evaluation
        - Never performs runtime computation
        
    OWNERSHIP CONTRACT:
        - Owns: None (assessment description only)
        - References: Target orientation being assessed
    """
    
    assessment_type: AssessmentType = field(default=AssessmentType.PROGRESS, init=False)
    value: float = 0.0
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> ProgressAssessment:
        return cls(identity=identity)


@dataclass(frozen=True)
class AlignmentAssessment(BaseContent):
    """
    Assessment of alignment with goals/objectives.
    
    SEMANTIC ROLE:
        - Describes semantic alignment evaluation
        - Never performs runtime computation
        
    OWNERSHIP CONTRACT:
        - Owns: None (assessment description only)
        - References: Target orientation being assessed
    """
    
    assessment_type: AssessmentType = field(default=AssessmentType.ALIGNMENT, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> AlignmentAssessment:
        return cls(identity=identity)


@dataclass(frozen=True)
class ConfidenceAssessment(BaseContent):
    """
    Assessment of confidence level.
    
    SEMANTIC ROLE:
        - Describes semantic confidence evaluation
        - Never performs runtime computation
        
    OWNERSHIP CONTRACT:
        - Owns: None (assessment description only)
        - References: Target orientation being assessed
    """
    
    assessment_type: AssessmentType = field(default=AssessmentType.CONFIDENCE, init=False)
    value: float = 0.5
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> ConfidenceAssessment:
        return cls(identity=identity)


@dataclass(frozen=True)
class RiskAssessment(BaseContent):
    """
    Assessment of risk level.
    
    SEMANTIC ROLE:
        - Describes semantic risk evaluation
        - Never performs runtime computation
        
    OWNERSHIP CONTRACT:
        - Owns: None (assessment description only)
        - References: Target orientation being assessed
    """
    
    assessment_type: AssessmentType = field(default=AssessmentType.RISK, init=False)
    value: float = 0.5
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> RiskAssessment:
        return cls(identity=identity)


@dataclass(frozen=True)
class RecoveryAssessment(BaseContent):
    """
    Assessment of recovery capability.
    
    SEMANTIC ROLE:
        - Describes semantic recovery evaluation
        - Never performs runtime computation
        
    OWNERSHIP CONTRACT:
        - Owns: None (assessment description only)
        - References: Target orientation being assessed
    """
    
    assessment_type: AssessmentType = field(default=AssessmentType.RECOVERY, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> RecoveryAssessment:
        return cls(identity=identity)


@dataclass(frozen=True)
class CompletionAssessment(BaseContent):
    """
    Assessment of completion status.
    
    SEMANTIC ROLE:
        - Describes semantic completion evaluation
        - Never performs runtime computation
        
    OWNERSHIP CONTRACT:
        - Owns: None (assessment description only)
        - References: Target orientation being assessed
    """
    
    assessment_type: AssessmentType = field(default=AssessmentType.COMPLETION, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> CompletionAssessment:
        return cls(identity=identity)


@dataclass(frozen=True)
class DriftAssessment(BaseContent):
    """
    Assessment of drift from expected behavior.
    
    SEMANTIC ROLE:
        - Describes semantic drift evaluation
        - Never performs runtime computation
        
    OWNERSHIP CONTRACT:
        - Owns: None (assessment description only)
        - References: Target orientation being assessed
    """
    
    assessment_type: AssessmentType = field(default=AssessmentType.DRIFT, init=False)
    value: float = 0.0
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> DriftAssessment:
        return cls(identity=identity)


__all__ = [
    "AssessmentType",
    # Specific assessment types
    "ProgressAssessment",
    "AlignmentAssessment",
    "ConfidenceAssessment",
    "RiskAssessment",
    "RecoveryAssessment",
    "CompletionAssessment",
    "DriftAssessment",
]