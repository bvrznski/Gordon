# Knowledge Authority - Phase 6.1
# ===============================

"""
Knowledge Authority: Source reliability and weight in Gordon's knowledge system.

Authority measures the reliability, expertise, and trustworthiness of sources
that contribute to knowledge artifacts. It enables the system to weight evidence
and reasoning according to source quality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# AUTHORITY LEVELS - Source reliability classification
# =============================================================================


class AuthorityLevel(Enum):
    """
    Levels of source authority.
    
    Defines hierarchical levels of source reliability in Gordon's knowledge system.
    """
    
    PRIMARY_EVIDENCE = "primary_evidence"   # Direct observation or measurement
    PEER_REVIEWED = "peer_reviewed"         # Academic peer-reviewed sources
    EXPERT_CONSENSUS = "expert_consensus"   # Consensus among domain experts
    ESTABLISHED_FACT = "established_fact"  # Well-established common knowledge
    
    SECONDARY_SOURCE = "secondary_source"   # Secondary interpretation
    ANONYMOUS = "anonymous"                 # Anonymous or unverifiable source
    UNVERIFIED = "unverified"               # Unverified claims
    
    UNKNOWN = "unknown"


# =============================================================================
# AUTHORITY SOURCES - Source identity and metadata
# =============================================================================


@dataclass(frozen=True)
class AuthoritySource:
    """
    Identity and metadata for a knowledge source.
    
    Records the origin of knowledge claims and supporting evidence.
    
    Fields:
        source_identity:     Unique identifier for this source
        source_type:         Type of source (person, system, document)
        source_name:         Human-readable name or title
        domain_expertise:    Domain expertise area(s)
        created_at_utc:      When source was first recorded
        metadata:            Additional source information
    """
    
    # Identity and metadata (required)
    source_identity: str                # Unique ID for this source
    
    # Source classification
    source_type: str = "system"         # e.g., "person", "system", "document"
    source_name: Optional[str] = None   # Human-readable name
    
    # Domain expertise
    domain_expertise: Tuple[str, ...] = field(default_factory=tuple)  # Expertise areas
    
    # Tracking
    created_at_utc: float = field(default_factory=time.time)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional info
    
    @property
    def is_valid(self) -> bool:
        """Check if source has valid data."""
        return len(self.source_identity) > 0 and self.source_type != ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert source to dictionary for serialization."""
        return {
            "source_identity": self.source_identity,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "domain_expertise": list(self.domain_expertise),
            "created_at_utc": self.created_at_utc,
            "metadata": dict(self.metadata),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthoritySource":
        """Create source from dictionary."""
        return cls(
            source_identity=data.get("source_identity", str(uuid.uuid4())),
            source_type=data.get("source_type", "system"),
            source_name=data.get("source_name"),
            domain_expertise=tuple(data.get("domain_expertise", [])),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            metadata=dict(data.get("metadata", {})),
        )


# =============================================================================
# AUTHORITY ASSESSMENT - Evaluation of source reliability
# =============================================================================


@dataclass(frozen=True)
class AuthorityAssessment:
    """
    Assessment of source authority and reliability.
    
    Records the evaluation process and outcome for determining source reliability.
    
    Fields:
        assessment_identity:  Unique identifier for this assessment
        source_identity:      Identity of assessed source
        level:                Authority level assigned
        confidence:           Assessment confidence (0.0-1.0)
        evidence:             Evidence supporting assessment
        timestamp_utc:        When assessment was made
    """
    
    # Identity and metadata (required)
    assessment_identity: str            # Unique ID for this assessment
    
    source_identity: str                # Identity of assessed source
    
    # Assessment results
    level: AuthorityLevel = AuthorityLevel.UNKNOWN
    confidence: float = 0.5             # Assessment confidence (0.0-1.0)
    
    # Supporting evidence
    evidence_chain: Tuple[str, ...] = field(default_factory=tuple)  # Evidence refs
    
    # Tracking
    timestamp_utc: float = field(default_factory=time.time)
    assessor_type: str = "system"       # Type of assessor
    assessor_id: str = ""               # ID of assessor
    
    @property
    def is_valid(self) -> bool:
        """Check if assessment has valid data."""
        return (
            len(self.assessment_identity) > 0 and
            len(self.source_identity) > 0 and
            self.level != AuthorityLevel.UNKNOWN and
            0.0 <= self.confidence <= 1.0
        )
    
    @property
    def is_assessment_complete(self) -> bool:
        """Check if assessment reached a conclusion."""
        return self.level != AuthorityLevel.UNKNOWN
    
    @classmethod
    def create(
        cls,
        source_identity: str,
        level: AuthorityLevel = AuthorityLevel.UNKNOWN,
        confidence: float = 0.5,
        evidence: Optional[List[str]] = None,
        assessor_type: str = "system",
        assessor_id: str = "",
    ) -> "AuthorityAssessment":
        """
        Create a new authority assessment.
        
        Args:
            source_identity: Identity of assessed source
            level: Authority level assigned
            confidence: Assessment confidence (0.0-1.0)
            evidence: Supporting evidence references (optional)
            assessor_type: Type of assessor
            assessor_id: ID of assessor
            
        Returns:
            New AuthorityAssessment instance
        """
        return cls(
            assessment_identity=f"authority:{uuid.uuid4().hex[:16]}",
            source_identity=source_identity,
            level=level,
            confidence=max(0.0, min(1.0, float(confidence))),
            evidence_chain=tuple(evidence or []),
            timestamp_utc=time.time(),
            assessor_type=assessor_type,
            assessor_id=assessor_id,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary for serialization."""
        return {
            "assessment_identity": self.assessment_identity,
            "source_identity": self.source_identity,
            "level": self.level.value if hasattr(self.level, 'value') else str(self.level),
            "confidence": self.confidence,
            "evidence_chain": list(self.evidence_chain),
            "timestamp_utc": self.timestamp_utc,
            "assessor_type": self.assessor_type,
            "assessor_id": self.assessor_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthorityAssessment":
        """Create assessment from dictionary."""
        return cls(
            assessment_identity=data.get("assessment_identity", ""),
            source_identity=data.get("source_identity", ""),
            level=AuthorityLevel(data.get("level", "unknown")),
            confidence=float(data.get("confidence", 0.5)),
            evidence_chain=tuple(data.get("evidence_chain", [])),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            assessor_type=data.get("assessor_type", "system"),
            assessor_id=data.get("assessor_id", ""),
        )


# =============================================================================
# AUTHORITY VALIDATOR
# =============================================================================


class AuthorityValidator:
    """
    Validates authority assessments for consistency.
    
    Ensures that authority evaluations are reasonable and consistent.
    """
    
    def __init__(
        self,
        require_evidence_for_high_confidence: bool = True,
        minimum_confidence_threshold: float = 0.3,
    ):
        """
        Initialize the validator.
        
        Args:
            require_evidence_for_high_confidence: Whether evidence required for high confidence
            minimum_confidence_threshold: Minimum acceptable confidence value
        """
        self._require_evidence = require_evidence_for_high_confidence
        self._min_confidence = minimum_confidence_threshold
    
    def validate(self, assessment: AuthorityAssessment) -> Tuple[bool, List[str]]:
        """
        Validate an authority assessment.
        
        Args:
            assessment: Assessment to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Rule 1: Must have valid identity
        if not assessment.assessment_identity or len(assessment.assessment_identity) == 0:
            issues.append("Missing assessment identity")
        
        # Rule 2: Source must be identified
        if not assessment.source_identity or len(assessment.source_identity) == 0:
            issues.append("Missing source identity")
        
        # Rule 3: Must have valid authority level
        if assessment.level == AuthorityLevel.UNKNOWN:
            issues.append("Unknown authority level")
        
        # Rule 4: Confidence must be in range
        if not (0.0 <= assessment.confidence <= 1.0):
            issues.append(f"Invalid confidence: {assessment.confidence}")
        
        # Rule 5: High confidence requires evidence
        if self._require_evidence and assessment.confidence > 0.7:
            if len(assessment.evidence_chain) == 0:
                issues.append("High confidence without supporting evidence")
        
        # Rule 6: Confidence must meet minimum threshold
        if assessment.confidence < self._min_confidence:
            issues.append(f"Confidence below minimum: {assessment.confidence}")
        
        return len(issues) == 0, issues


__all__ = [
    "AuthorityLevel",
    "AuthoritySource",
    "AuthorityAssessment",
    "AuthorityValidator",
]