# Knowledge Validity - Phase 6.1
# ==============================

"""
Knowledge Validity: Truth and logical soundness assessment for semantic artifacts.

Validity measures whether a claim or assertion is logically correct and
supported by evidence. It differs from truth in that something can be valid
(logically consistent) even if the premises are not factually true.

Components:
    - Validity State: Current validity status (valid, invalid, unknown)
    - Validity Assessment: Evaluation of claims and reasoning
    - Validity Evidence: Supporting evidence for validity claims
    - ValidityEngine: Assessment engine for automatic evaluation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# VALIDITY STATES - Current validity classification
# =============================================================================


class ValidityState(Enum):
    """
    States of validity for semantic artifacts.
    
    Defines the current validity assessment state in Gordon's knowledge system.
    """
    
    VALID = "valid"                       # Logically sound and supported
    INVALID = "invalid"                   # Logically flawed or unsupported
    UNKNOWN = "unknown"                   # Validity not yet assessed
    
    SUSPICIOUS = "suspicious"             # May be invalid, needs verification
    PARTIALLY_VALID = "partially_valid"   # Some aspects valid, others not
    CONDITIONALLY_VALID = "conditionally_valid"  # Valid under certain conditions
    
    DEPRECATED = "deprecated"             # Was valid but superseded


# =============================================================================
# VALIDITY EVIDENCE - Supporting evidence for validity claims
# =============================================================================


class EvidenceKind(Enum):
    """
    Kinds of evidence supporting validity.
    
    Defines categories of evidence that can support or challenge a validity claim.
    """
    
    EMPIRICAL = "empirical"               # Observational evidence
    LOGICAL = "logical"                   # Logical deduction
    CONSISTENCY = "consistency"           # Consistency with other beliefs
    AUTHORITY = "authority"               # Support from authoritative sources
    EXPERIMENTAL = "experimental"         # Experimental verification
    ANALYTICAL = "analytical"             # Mathematical or analytical proof
    
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ValidityEvidence:
    """
    Evidence supporting a validity assessment.
    
    Records the evidence used to support or challenge a validity claim.
    
    Fields:
        evidence_identity:  Unique identifier for this evidence
        kind:               Kind of evidence
        source:             Source of the evidence
        strength:           Strength of the evidence (0.0-1.0)
        relevance:          Relevance to the claim (0.0-1.0)
    """
    
    # Identity and metadata (required)
    evidence_identity: str              # Unique identifier
    
    # Evidence classification
    kind: EvidenceKind = EvidenceKind.UNKNOWN
    
    # Source information
    source: Optional[str] = None        # Evidence source reference
    source_confidence: float = 0.5      # Confidence in the source (0.0-1.0)
    
    # Assessment metrics
    strength: float = 0.5               # Strength of evidence (0.0-1.0)
    relevance: float = 0.5              # Relevance to claim (0.0-1.0)
    
    @property
    def impact_score(self) -> float:
        """Calculate impact score based on strength and relevance."""
        return self.strength * self.relevance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to dictionary for serialization."""
        return {
            "evidence_identity": self.evidence_identity,
            "kind": self.kind.value if hasattr(self.kind, 'value') else str(self.kind),
            "source": self.source,
            "source_confidence": self.source_confidence,
            "strength": self.strength,
            "relevance": self.relevance,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidityEvidence":
        """Create evidence from dictionary."""
        return cls(
            evidence_identity=data.get("evidence_identity", ""),
            kind=EvidenceKind(data.get("kind", "unknown")),
            source=data.get("source"),
            source_confidence=float(data.get("source_confidence", 0.5)),
            strength=float(data.get("strength", 0.5)),
            relevance=float(data.get("relevance", 0.5)),
        )


# =============================================================================
# VALIDITY ASSESSMENT - Evaluation result
# =============================================================================


@dataclass(frozen=True)
class ValidityAssessment:
    """
    Assessment of validity for a semantic artifact.
    
    Records the complete evaluation process and outcome for validity determination.
    
    Fields:
        assessment_identity:  Unique identifier for this assessment
        claim_identity:       Identity of assessed artifact
        state:                Current validity state
        evidence:             Supporting evidence chain
        reasoning:            Reasoning explanation
        confidence:           Assessment confidence (0.0-1.0)
        timestamp_utc:        When assessment was made
    """
    
    # Identity and metadata (required)
    assessment_identity: str            # Unique ID for this assessment
    
    claim_identity: str                 # Identity of assessed artifact
    
    # Assessment results
    state: ValidityState = ValidityState.UNKNOWN
    
    # Evidence and reasoning
    evidence_chain: Tuple[ValidityEvidence, ...] = field(default_factory=tuple)
    reasoning: Optional[str] = None     # Explanation for assessment
    
    # Quality metrics
    confidence: float = 0.5             # Assessment confidence (0.0-1.0)
    
    # Tracking
    timestamp_utc: float = field(default_factory=time.time)
    assessor_type: str = "system"       # Type of assessor (system, user, reasoning)
    assessor_id: str = ""               # ID of assessor
    
    @property
    def is_valid(self) -> bool:
        """Check if assessment has valid data."""
        return (
            len(self.assessment_identity) > 0 and
            len(self.claim_identity) > 0 and
            0.0 <= self.confidence <= 1.0
        )
    
    @property
    def is_assessment_complete(self) -> bool:
        """Check if assessment reached a conclusion."""
        return self.state != ValidityState.UNKNOWN
    
    @classmethod
    def create(
        cls,
        claim_identity: str,
        state: ValidityState = ValidityState.UNKNOWN,
        evidence: Optional[List[ValidityEvidence]] = None,
        reasoning: Optional[str] = None,
        confidence: float = 0.5,
        assessor_type: str = "system",
        assessor_id: str = "",
    ) -> "ValidityAssessment":
        """
        Create a new validity assessment.
        
        Args:
            claim_identity: Identity of artifact being assessed
            state: Validity state result
            evidence: Supporting evidence (optional)
            reasoning: Explanation for assessment (optional)
            confidence: Assessment confidence
            assessor_type: Type of assessor
            assessor_id: ID of assessor
            
        Returns:
            New ValidityAssessment instance
        """
        return cls(
            assessment_identity=f"validity:{uuid.uuid4().hex[:16]}",
            claim_identity=claim_identity,
            state=state,
            evidence_chain=tuple(evidence or []),
            reasoning=reasoning,
            confidence=max(0.0, min(1.0, float(confidence))),
            timestamp_utc=time.time(),
            assessor_type=assessor_type,
            assessor_id=assessor_id,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary for serialization."""
        return {
            "assessment_identity": self.assessment_identity,
            "claim_identity": self.claim_identity,
            "state": self.state.value if hasattr(self.state, 'value') else str(self.state),
            "evidence_chain": [e.to_dict() for e in self.evidence_chain],
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "timestamp_utc": self.timestamp_utc,
            "assessor_type": self.assessor_type,
            "assessor_id": self.assessor_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidityAssessment":
        """Create assessment from dictionary."""
        evidence = []
        for e_data in data.get("evidence_chain", []):
            evidence.append(ValidityEvidence.from_dict(e_data))
        
        return cls(
            assessment_identity=data.get("assessment_identity", ""),
            claim_identity=data.get("claim_identity", ""),
            state=ValidityState(data.get("state", "unknown")),
            evidence_chain=tuple(evidence),
            reasoning=data.get("reasoning"),
            confidence=float(data.get("confidence", 0.5)),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            assessor_type=data.get("assessor_type", "system"),
            assessor_id=data.get("assessor_id", ""),
        )


# =============================================================================
# VALIDITY ENGINE - Assessment engine
# =============================================================================


class ValidityEngine:
    """
    Engine for performing validity assessments.
    
    Provides automated validity evaluation using various assessment strategies.
    """
    
    def __init__(
        self,
        minimum_confidence: float = 0.6,
        require_evidence: bool = True,
    ):
        """
        Initialize the validity engine.
        
        Args:
            minimum_confidence: Minimum confidence for valid status
            require_evidence: Whether evidence is required for validity
        """
        self._minimum_confidence = minimum_confidence
        self._require_evidence = require_evidence
    
    def assess(
        self,
        claim_identity: str,
        claim_content: Any,
        evidence_chain: List[ValidityEvidence],
    ) -> ValidityAssessment:
        """
        Perform a validity assessment.
        
        Args:
            claim_identity: Identity of artifact being assessed
            claim_content: Content of the claim (for analysis)
            evidence_chain: Evidence supporting or challenging the claim
            
        Returns:
            ValidityAssessment with evaluation result
        """
        total_evidence_strength = sum(e.strength for e in evidence_chain)
        total_relevance = sum(e.relevance for e in evidence_chain)
        
        # Calculate confidence based on evidence quality
        if len(evidence_chain) > 0:
            avg_strength = total_evidence_strength / len(evidence_chain)
            avg_relevance = total_relevance / len(evidence_chain)
            confidence = (avg_strength + avg_relevance) / 2
        else:
            confidence = 0.5
        
        # Determine state based on evidence and requirements
        has_sufficient_evidence = (
            total_evidence_strength >= self._minimum_confidence or
            not self._require_evidence
        )
        
        if len(evidence_chain) == 0:
            state = ValidityState.UNKNOWN
        elif has_sufficient_evidence and confidence >= self._minimum_confidence:
            state = ValidityState.VALID
        elif confidence < 0.3:
            state = ValidityState.INVALID
        else:
            state = ValidityState.SUSPICIOUS
        
        # Build reasoning explanation
        reasoning = self._build_reasoning(
            claim_content,
            evidence_chain,
            state,
            confidence,
        )
        
        return ValidityAssessment.create(
            claim_identity=claim_identity,
            state=state,
            evidence=evidence_chain,
            reasoning=reasoning,
            confidence=confidence,
            assessor_type="system",
            assessor_id="validityEngine",
        )
    
    def _build_reasoning(
        self,
        claim_content: Any,
        evidence_chain: List[ValidityEvidence],
        state: ValidityState,
        confidence: float,
    ) -> str:
        """Build explanation string for assessment."""
        if state == ValidityState.UNKNOWN:
            return "Insufficient information to determine validity"
        
        evidence_str = ", ".join(
            f"{e.evidence_identity}({e.kind.value})" 
            for e in evidence_chain[:3]
        )
        
        return (
            f"Assessment: {state.value}. "
            f"Confidence: {confidence:.2f}. "
            f"Evidence: [{evidence_str}]"
        )


__all__ = [
    "ValidityState",
    "EvidenceKind",
    "ValidityEvidence",
    "ValidityAssessment",
    "ValidityEngine",
]