# Knowledge Evidence - Phase 5.4
# ==============================

"""
Knowledge Evidence: Traceable evidence from other systems supporting knowledge artifacts.

Evidence is what grounds semantic claims in Gordon's knowledge system. It always
originates from Perception, Memory, Reasoning, Learning, or external systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# EVIDENCE KINDS - Types of evidence sources
# =============================================================================


class EvidenceKind(Enum):
    """
    Kinds of evidence in Gordon's knowledge system.
    
    Defines the origin and nature of evidence supporting semantic claims.
    """
    
    # Perception-based evidence
    PERCEPTION_OBSERVATION = "perception_observation"     # Direct perception
    PERCEPTION_TRANSFORMATION = "perception_transformation"  # Processed perception
    
    # Memory-based evidence
    MEMORY_RECOLLECTION = "memory_recollection"           # Recalled experience
    MEMORY_PATTERN = "memory_pattern"                     # Recognized pattern from memory
    
    # Reasoning-based evidence
    REASONING_DEDUCTION = "reasoning_deduction"           # Deductive inference
    REASONING_INDUCTION = "reasoning_induction"           # Inductive inference
    REASONING_ANALOGY = "reasoning_analogy"               # Analogical reasoning
    
    # Learning-based evidence
    LEARNING_GENERALIZATION = "learning_generalization"   # Generalized pattern
    LEARNING_ABNORMALITY = "learning_abnormality"         # Detected anomaly
    
    # External evidence
    EXTERNAL_SOURCE = "external_source"                   # External knowledge base
    VERIFICATION = "verification"                         # External verification
    
    # Unknown origin
    UNKNOWN = "unknown"


# =============================================================================
# EVIDENCE MODEL - Canonical evidence structure
# =============================================================================


@dataclass(frozen=True)
class KnowledgeEvidence:
    """
    Canonical representation of evidence in Gordon's knowledge system.
    
    Evidence provides the foundation for semantic claims. Every piece of evidence
    is traceable to its source and preserves its confidence and limitations.
    
    Fields:
        evidence_identity:     Unique identifier for this evidence
        source_system:         System that generated this evidence
        source_reference:      Reference to the source artifact
        evidence_kind:         Type of evidence
        confidence:            Confidence in this evidence (0.0-1.0)
        uncertainty:           Uncertainty about this evidence
        limitations:           Known limitations of this evidence
        revision:              Revision number for traceability
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity and metadata (required)
    evidence_identity: str            # Unique ID for this evidence
    
    # Source information (required)
    source_system: str                # e.g., "perception", "memory"
    source_reference: str             # Reference to source artifact
    
    # Evidence type
    evidence_kind: EvidenceKind = EvidenceKind.UNKNOWN
    
    # Quality metrics (required)
    confidence: float = 0.5           # Confidence in this evidence (0.0-1.0)
    uncertainty: float = 0.5          # Uncertainty about this evidence
    
    # Limitations and context
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Lifecycle tracking
    revision: int = 1                 # Revision number for traceability
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if evidence has minimal required data."""
        return (
            len(self.evidence_identity) > 0 and
            len(self.source_system) > 0 and
            len(self.source_reference) > 0
        )
    
    @classmethod
    def create(
        cls,
        source_system: str,
        source_reference: str,
        evidence_kind: EvidenceKind = EvidenceKind.UNKNOWN,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
        limitations: Optional[List[str]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeEvidence":
        """
        Create a new piece of evidence.
        
        Args:
            source_system: System that generated this evidence
            source_reference: Reference to the source artifact
            evidence_kind: Type of evidence
            confidence: Confidence in this evidence (0.0-1.0)
            uncertainty: Uncertainty about this evidence
            limitations: Known limitations (optional)
            provenance: Origin tracking data (optional)
        """
        return cls(
            evidence_identity=f"evidence:{uuid.uuid4().hex[:16]}",
            source_system=source_system,
            source_reference=source_reference,
            evidence_kind=evidence_kind,
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            limitations=tuple(limitations or []),
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "revision": 1,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to dictionary for serialization."""
        return {
            "evidence_identity": self.evidence_identity,
            "source_system": self.source_system,
            "source_reference": self.source_reference,
            "evidence_kind": self.evidence_kind.value if self.evidence_kind else None,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeEvidence":
        """Create evidence from dictionary."""
        kind_value = data.get("evidence_kind", "unknown")
        try:
            evidence_kind = EvidenceKind(kind_value)
        except ValueError:
            evidence_kind = EvidenceKind.UNKNOWN
        
        return cls(
            evidence_identity=data.get("evidence_identity", str(uuid.uuid4())),
            source_system=data.get("source_system", ""),
            source_reference=data.get("source_reference", ""),
            evidence_kind=evidence_kind,
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            limitations=tuple(data.get("limitations", [])),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# EVIDENCE CHAIN
# =============================================================================


class EvidenceChain:
    """
    Represents a chain of evidence from origin to current use.
    
    Tracks the full provenance path of evidence through the system.
    """
    
    def __init__(
        self,
        initial_evidence: Optional[KnowledgeEvidence] = None,
    ):
        """Initialize with optional starting evidence."""
        self._chain: List[KnowledgeEvidence] = []
        if initial_evidence:
            self.add(initial_evidence)
    
    def add(self, evidence: KnowledgeEvidence) -> "EvidenceChain":
        """Add evidence to the chain."""
        self._chain.append(evidence)
        return self
    
    @property
    def length(self) -> int:
        """Get the length of the evidence chain."""
        return len(self._chain)
    
    @property
    def origin(self) -> Optional[KnowledgeEvidence]:
        """Get the first (original) evidence in the chain."""
        return self._chain[0] if self._chain else None
    
    @property
    def current(self) -> Optional[KnowledgeEvidence]:
        """Get the most recent evidence in the chain."""
        return self._chain[-1] if self._chain else None
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convert chain to list of dictionaries."""
        return [e.to_dict() for e in self._chain]
    
    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "EvidenceChain":
        """Create evidence chain from list of evidence dictionaries."""
        chain = cls()
        for item in data:
            evidence = KnowledgeEvidence.from_dict(item)
            chain.add(evidence)
        return chain
    
    def validate_chain(self) -> Tuple[bool, List[str]]:
        """
        Validate the evidence chain.
        
        Checks that each link preserves provenance and quality metrics.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        if len(self._chain) == 0:
            issues.append("Empty evidence chain")
            return False, issues
        
        # Check each link
        for i, evidence in enumerate(self._chain):
            if not evidence.is_valid:
                issues.append(f"Invalid evidence at position {i}")
            
            # Check confidence-uncertainty balance
            total = evidence.confidence + evidence.uncertainty
            if not (0.8 <= total <= 1.2):
                issues.append(
                    f"Confidence-uncertainty imbalance in link {i}: {total:.2f}"
                )
        
        return len(issues) == 0, issues


__all__ = [
    "EvidenceKind",
    "KnowledgeEvidence",
    "EvidenceChain",
]