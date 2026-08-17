# Knowledge Justification - Phase 5.4
# ===================================

"""
Knowledge Justification: Explanations for semantic commitments.

Justifications provide the reasoning behind why a belief is held, tracing back
to supporting evidence and logical derivation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# JUSTIFICATION KINDS - Types of justification reasoning
# =============================================================================


class JustificationKind(Enum):
    """
    Kinds of justification reasoning.
    
    Defines the type of reasoning that supports a semantic commitment.
    """
    
    # Deductive reasoning
    DEDUCTIVE = "deductive"           # Logical deduction from premises
    
    # Inductive reasoning
    INDUCTIVE = "inductive"           # Generalization from observations
    
    # Abductive reasoning
    ABDUCTIVE = "abductive"           # Best explanation inference
    
    # Analogical reasoning
    ANALOGICAL = "analogical"         # Reasoning by analogy
    
    # Causal reasoning
    CAUSAL = "causal"                 # Cause-effect reasoning
    
    # Statistical reasoning
    STATISTICAL = "statistical"       # Statistical inference
    
    # Expert judgment
    EXPERT_JUDGMENT = "expert_judgment"  # Authority-based justification
    
    # Unknown origin
    UNKNOWN = "unknown"


# =============================================================================
# JUSTIFICATION MODEL - Canonical justification structure
# =============================================================================


@dataclass(frozen=True)
class KnowledgeJustification:
    """
    Canonical representation of a justification in Gordon's knowledge system.
    
    A justification explains why a semantic commitment (belief) is held,
    tracing back to supporting evidence and logical derivation.
    
    Fields:
        justification_identity:  Unique identifier for this justification
        belief_reference:        Reference to the justified belief
        supporting_evidence:     Evidence directly supporting this justification
        supporting_relations:    Relations supporting the inference
        counter_arguments:       Known counter-arguments
        confidence:              Confidence in this justification (0.0-1.0)
        uncertainty:             Uncertainty about this justification
        revision:                Revision number for traceability
        provenance:              Origin tracking with timestamps and sources
    """
    
    # Identity and metadata (required)
    justification_identity: str       # Unique ID for this justification
    
    # Target belief reference
    belief_reference: str             # Reference to the justified belief
    
    # Evidence and reasoning support
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    supporting_relations: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)  # (relation_kind, target_id)
    
    # Counter-arguments
    counter_arguments: Tuple[str, ...] = field(default_factory=tuple)
    
    # Quality metrics (required)
    confidence: float = 0.5           # Confidence in this justification (0.0-1.0)
    uncertainty: float = 0.5          # Uncertainty about this justification
    
    # Justification details
    kind: JustificationKind = JustificationKind.UNKNOWN
    reasoning_steps: Tuple[str, ...] = field(default_factory=tuple)  # Step descriptions
    
    # Lifecycle tracking
    revision: int = 1                 # Revision number for traceability
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if justification has minimal required data."""
        return (
            len(self.justification_identity) > 0 and
            len(self.belief_reference) > 0
        )
    
    @property
    def net_support_ratio(self) -> float:
        """
        Calculate the net support ratio.
        
        Returns:
            Positive value means net support, negative means counter-evidence
        """
        supporting = len(self.supporting_evidence)
        countering = len(self.counter_arguments)
        total = supporting + countering
        if total == 0:
            return 0.0
        return (supporting - countering) / total
    
    @classmethod
    def create(
        cls,
        belief_reference: str,
        supporting_evidence: Optional[List[str]] = None,
        supporting_relations: Optional[List[Tuple[str, str]]] = None,
        counter_arguments: Optional[List[str]] = None,
        kind: JustificationKind = JustificationKind.UNKNOWN,
        reasoning_steps: Optional[List[str]] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeJustification":
        """
        Create a new justification.
        
        Args:
            belief_reference: Reference to the justified belief
            supporting_evidence: Evidence directly supporting (optional)
            supporting_relations: Relations supporting inference (optional)
            counter_arguments: Known counter-arguments (optional)
            kind: Kind of reasoning
            reasoning_steps: Step-by-step reasoning (optional)
            confidence: Confidence in this justification (0.0-1.0)
            uncertainty: Uncertainty about this justification
            provenance: Origin tracking data (optional)
        """
        return cls(
            justification_identity=f"justification:{uuid.uuid4().hex[:16]}",
            belief_reference=belief_reference,
            supporting_evidence=tuple(supporting_evidence or []),
            supporting_relations=tuple(supporting_relations or []),
            counter_arguments=tuple(counter_arguments or []),
            kind=kind,
            reasoning_steps=tuple(reasoning_steps or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "revision": 1,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert justification to dictionary for serialization."""
        return {
            "justification_identity": self.justification_identity,
            "belief_reference": self.belief_reference,
            "supporting_evidence": list(self.supporting_evidence),
            "supporting_relations": [list(r) for r in self.supporting_relations],
            "counter_arguments": list(self.counter_arguments),
            "kind": self.kind.value if self.kind else None,
            "reasoning_steps": list(self.reasoning_steps),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeJustification":
        """Create justification from dictionary."""
        kind_value = data.get("kind", "unknown")
        try:
            kind = JustificationKind(kind_value)
        except ValueError:
            kind = JustificationKind.UNKNOWN
        
        return cls(
            justification_identity=data.get("justification_identity", str(uuid.uuid4())),
            belief_reference=data.get("belief_reference", ""),
            supporting_evidence=tuple(data.get("supporting_evidence", [])),
            supporting_relations=tuple(tuple(r) for r in data.get("supporting_relations", [])),
            counter_arguments=tuple(data.get("counter_arguments", [])),
            kind=kind,
            reasoning_steps=tuple(data.get("reasoning_steps", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# JUSTIFICATION BUILDER
# =============================================================================


class JustificationBuilder:
    """
    Builds and validates justifications for semantic commitments.
    
    Ensures justifications are logically sound and properly supported.
    """
    
    def __init__(
        self,
        minimum_supporting_evidence: int = 1,
        maximum_counter_ratio: float = 0.5,
    ):
        """
        Initialize the builder.
        
        Args:
            minimum_supporting_evidence: Minimum evidence required
            maximum_counter_ratio: Maximum ratio of counter-arguments allowed
        """
        self._min_supporting = minimum_supporting_evidence
        self._max_counter_ratio = maximum_counter_ratio
    
    def validate_justification(
        self,
        justification: KnowledgeJustification,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a justification.
        
        Args:
            justification: The justification to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Rule 1: Must have identity
        if not justification.justification_identity or len(justification.justification_identity) == 0:
            issues.append("Missing justification identity")
        
        # Rule 2: Must reference a belief
        if not justification.belief_reference or len(justification.belief_reference) == 0:
            issues.append("Missing belief reference")
        
        # Rule 3: Confidence must be in valid range
        if not (0.0 <= justification.confidence <= 1.0):
            issues.append(f"Invalid confidence: {justification.confidence}")
        
        # Rule 4: Uncertainty must be in valid range
        if not (0.0 <= justification.uncertainty <= 1.0):
            issues.append(f"Invalid uncertainty: {justification.uncertainty}")
        
        # Rule 5: Must have minimum supporting evidence for strong confidence
        if (
            justification.confidence > 0.7 and
            len(justification.supporting_evidence) < self._min_supporting
        ):
            issues.append(
                f"High-confidence justification lacks supporting evidence: "
                f"{len(justification.supporting_evidence)} < {self._min_supporting}"
            )
        
        # Rule 6: Counter-argument ratio should not exceed maximum
        total = len(justification.supporting_evidence) + len(justification.counter_arguments)
        if total > 0:
            counter_ratio = len(justification.counter_arguments) / total
            if counter_ratio > self._max_counter_ratio:
                issues.append(
                    f"Counter-argument ratio {counter_ratio:.2f} exceeds maximum "
                    f"{self._max_counter_ratio}"
                )
        
        return len(issues) == 0, issues
    
    def build_deductive_justification(
        cls,
        belief_reference: str,
        premises: List[str],
        conclusion_step: str,
        confidence: float = 0.95,
    ) -> KnowledgeJustification:
        """
        Build a deductive justification.
        
        Args:
            belief_reference: Reference to the justified belief
            premises: Supporting evidence/premises
            conclusion_step: Description of the logical step to conclusion
            confidence: Confidence in the deduction
            
        Returns:
            A new deductive justification
        """
        return KnowledgeJustification.create(
            belief_reference=belief_reference,
            supporting_evidence=premises,
            kind=JustificationKind.DEDUCTIVE,
            reasoning_steps=[f"Premise: {p}" for p in premises] + [conclusion_step],
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )


__all__ = [
    "JustificationKind",
    "KnowledgeJustification",
    "JustificationBuilder",
]