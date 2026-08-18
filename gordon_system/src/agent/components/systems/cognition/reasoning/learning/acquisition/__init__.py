# Learning Reasoning Acquisition Module - Phase 7.24
# ==================================================

"""
Knowledge acquisition module for Learning Reasoning.

This module provides canonical implementations of knowledge acquisition contracts:

    KnowledgeAcquisition    - Knowledge acquisition with evidence
    AcquisitionPolicy       - Policy governing what can be acquired
    AcquisitionMetrics      - Metrics for evaluating acquisition quality
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class KnowledgeAcquisition:
    """
    A knowledge acquisition with supporting evidence.
    
    Acquisitions record:
        - What was acquired
        - Why it was acquired (evidence)
        - When it was acquired (timing)
        - How confident we are in it
    
    Acquisitions remain explicit; they don't silently modify beliefs.
    """
    
    # Identity
    acquisition_id: str                       # Unique identifier
    
    # Acquisition details
    acquired_knowledge: Dict[str, Any]        # The learned knowledge
    acquisition_type: str                     # What kind of acquisition?
    
    # Evidence
    supporting_evidence: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.5                   # Confidence in the knowledge
    
    # Policy
    acquisition_policy: str = "standard"      # Which policy was used?
    evidence_threshold: float = 0.5           # Minimum confidence threshold
    
    # Timing
    acquired_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    source_descriptor_id: Optional[str] = None   # From which learning session?
    
    @property
    def is_valid(self) -> bool:
        """Check if acquisition meets evidence requirements."""
        return self.confidence >= self.evidence_threshold
    
    @classmethod
    def create(
        cls,
        acquired_knowledge: Dict[str, Any],
        supporting_evidence: List[Dict[str, Any]],
        confidence: float = 0.5,
        acquisition_type: str = "standard",
        provenance: Optional[Dict[str, str]] = None,
    ) -> KnowledgeAcquisition:
        """Create a new knowledge acquisition."""
        return cls(
            acquisition_id=f"acquisition:{uuid.uuid4().hex[:16]}",
            acquired_knowledge=acquired_knowledge,
            supporting_evidence=supporting_evidence,
            confidence=confidence,
            acquisition_type=acquisition_type,
            provenance=provenance or {},
            acquired_at_utc=time.time(),
        )
    
    def with_evidence(self, evidence: Dict[str, Any]) -> KnowledgeAcquisition:
        """Return a copy with additional evidence."""
        new_evidence = list(self.supporting_evidence)
        new_evidence.append(evidence)
        return dataclass_replace(
            self,
            supporting_evidence=new_evidence,
        )


@dataclass(frozen=True)
class AcquisitionPolicy:
    """
    Policy governing knowledge acquisition.
    
    Policies define:
        - What kinds of knowledge can be acquired
        - What evidence is required
        - Confidence thresholds
        - Validation requirements
    """
    
    policy_id: str                            # Unique identifier
    policy_name: str                          # Human-readable name
    allowed_types: List[str]                  # What acquisition types?
    minimum_evidence: int = 1                 # Minimum evidence items needed
    confidence_threshold: float = 0.5         # Minimum confidence
    requires_validation: bool = True          # Must be validated first?
    
    @classmethod
    def strict(cls) -> "AcquisitionPolicy":
        """Create a strict acquisition policy."""
        return cls(
            policy_id="strict_policy",
            policy_name="Strict Policy",
            allowed_types=["acquired", "generalized", "refined"],
            minimum_evidence=3,
            confidence_threshold=0.8,
            requires_validation=True,
        )
    
    @classmethod
    def permissive(cls) -> "AcquisitionPolicy":
        """Create a permissive acquisition policy."""
        return cls(
            policy_id="permissive_policy",
            policy_name="Permissive Policy",
            allowed_types=["acquired", "generalized"],
            minimum_evidence=1,
            confidence_threshold=0.5,
            requires_validation=False,
        )


@dataclass(frozen=True)
class AcquisitionMetrics:
    """
    Metrics for evaluating acquisition quality.
    
    Metrics include:
        - Quantity: How much was acquired?
        - Quality: How well-supported is the knowledge?
        - Novelty: How new is this knowledge?
        - Generalization: Applicability scope
    """
    
    metrics_id: str                           # Unique identifier
    
    # Acquisition metrics
    acquisitions_count: int = 0               # Total acquisitions
    average_confidence: float = 0.5           # Average confidence level
    total_evidence_items: int = 0             # Total evidence across all
    
    # Quality metrics
    valid_acquisitions: int = 0               # Met threshold
    invalid_acquisitions: int = 0             # Below threshold
    
    # Timing metrics
    average_time_per_acquisition: float = 0.0 # Time per acquisition
    
    @classmethod
    def from_acquisitions(cls, acquisitions: List[KnowledgeAcquisition]) -> "AcquisitionMetrics":
        """Calculate metrics from a list of acquisitions."""
        if not acquisitions:
            return cls(metrics_id="empty_metrics")
        
        total_confidence = sum(a.confidence for a in acquisitions)
        total_evidence = sum(len(a.supporting_evidence) for a in acquisitions)
        valid_count = sum(1 for a in acquisitions if a.is_valid)
        
        return cls(
            metrics_id=f"metrics:{uuid.uuid4().hex[:16]}",
            acquisitions_count=len(acquisitions),
            average_confidence=total_confidence / len(acquisitions),
            total_evidence_items=total_evidence,
            valid_acquisitions=valid_count,
            invalid_acquisitions=len(acquisitions) - valid_count,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "KnowledgeAcquisition",
    "AcquisitionPolicy",
    "AcquisitionMetrics",
]