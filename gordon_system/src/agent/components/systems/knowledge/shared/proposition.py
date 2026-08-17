# Knowledge Proposition - Phase 5.4
# ==================================

"""
Knowledge Proposition: Organizes one or more assertions into a coherent semantic claim.

A proposition represents a semantic statement that may later become accepted,
rejected, revised, or remain unknown. Propositions are built from assertions and
serve as the building blocks for beliefs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PROPOSITION STATES - Lifecycle of a proposition
# =============================================================================


class PropositionState(Enum):
    """
    States of proposition lifecycle.
    
    Every proposition shall have an explicit state indicating whether it's
    accepted, rejected, provisional, deprecated, or unknown.
    """
    
    ACCEPTED = "accepted"           # Supported by sufficient evidence
    REJECTED = "rejected"           # Refuted by counter-evidence
    UNKNOWN = "unknown"             # State indeterminate
    PROVISIONAL = "provisional"     # Tentatively accepted pending review
    DEPRECATED = "deprecated"       # Should not be used, but was once valid


# =============================================================================
# PROPOSITION MODEL - Canonical proposition structure
# =============================================================================


@dataclass(frozen=True)
class KnowledgeProposition:
    """
    Canonical representation of a semantic claim composed from assertions.
    
    A proposition organizes one or more assertions into a coherent semantic
    statement that may become part of Gordon's belief system.
    
    Fields:
        proposition_identity:  Unique identifier for this proposition
        assertions:            References to constituent assertions
        statement:             The unified semantic claim
        status:                Current lifecycle state
        supporting_evidence:   Evidence directly supporting this proposition
        counter_evidence:      Evidence contradicting this proposition
        confidence:            Semantic confidence in this proposition (0.0-1.0)
        uncertainty:           Semantic uncertainty about this proposition
        revision:              Revision number for traceability
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity and metadata (required)
    proposition_identity: str         # Unique ID for this proposition
    
    # Constituent assertions
    assertions: Tuple[str, ...] = field(default_factory=tuple)  # Assertion references
    
    # Semantic content (optional - can be synthesized from assertions)
    statement: str = ""
    
    # Lifecycle status (required)
    status: PropositionState = PropositionState.UNKNOWN
    
    # Evidence and justification
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    counter_evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    # Quality metrics (required)
    confidence: float = 0.5           # Semantic confidence (0.0-1.0)
    uncertainty: float = 0.5          # Semantic uncertainty (0.0-1.0)
    
    # Lifecycle tracking
    revision: int = 1                 # Revision number for traceability
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_valid(self) -> bool:
        """Check if proposition has minimal required data."""
        return (
            len(self.proposition_identity) > 0 and
            self.status is not None
        )
    
    @property
    def is_accepted(self) -> bool:
        """Check if proposition has been accepted."""
        return self.status == PropositionState.ACCEPTED
    
    @property
    def is_rejected(self) -> bool:
        """Check if proposition has been rejected."""
        return self.status == PropositionState.REJECTED
    
    @classmethod
    def create(
        cls,
        assertions: Optional[List[str]] = None,
        statement: str = "",
        status: PropositionState = PropositionState.UNKNOWN,
        supporting_evidence: Optional[List[str]] = None,
        counter_evidence: Optional[List[str]] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeProposition":
        """
        Create a new proposition.
        
        Args:
            assertions: References to constituent assertions (optional)
            statement: Unified semantic claim (optional)
            status: Current lifecycle state
            supporting_evidence: Supporting evidence references (optional)
            counter_evidence: Contradicting evidence references (optional)
            confidence: Semantic confidence (0.0-1.0)
            uncertainty: Semantic uncertainty (0.0-1.0)
            provenance: Origin tracking data (optional)
        """
        return cls(
            proposition_identity=f"proposition:{uuid.uuid4().hex[:16]}",
            assertions=tuple(assertions or []),
            statement=statement,
            status=status,
            supporting_evidence=tuple(supporting_evidence or []),
            counter_evidence=tuple(counter_evidence or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "revision": 1,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert proposition to dictionary for serialization."""
        return {
            "proposition_identity": self.proposition_identity,
            "assertions": list(self.assertions),
            "statement": self.statement,
            "status": self.status.value if self.status else None,
            "supporting_evidence": list(self.supporting_evidence),
            "counter_evidence": list(self.counter_evidence),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeProposition":
        """Create proposition from dictionary."""
        status_value = data.get("status", "unknown")
        try:
            status = PropositionState(status_value)
        except ValueError:
            status = PropositionState.UNKNOWN
        
        return cls(
            proposition_identity=data.get("proposition_identity", str(uuid.uuid4())),
            assertions=tuple(data.get("assertions", [])),
            statement=data.get("statement", ""),
            status=status,
            supporting_evidence=tuple(data.get("supporting_evidence", [])),
            counter_evidence=tuple(data.get("counter_evidence", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )
    
    def update_status(
        self,
        new_status: PropositionState,
        confidence_delta: float = 0.0,
        uncertainty_delta: float = 0.0,
    ) -> "KnowledgeProposition":
        """
        Create a revision of this proposition with updated status.
        
        Args:
            new_status: The new lifecycle state
            confidence_delta: Confidence adjustment (-1.0 to +1.0)
            uncertainty_delta: Uncertainty adjustment (-1.0 to +1.0)
        """
        return KnowledgeProposition(
            proposition_identity=self.proposition_identity,
            assertions=self.assertions,
            statement=self.statement,
            status=new_status,
            supporting_evidence=self.supporting_evidence,
            counter_evidence=self.counter_evidence,
            confidence=max(0.0, min(1.0, self.confidence + confidence_delta)),
            uncertainty=max(0.0, min(1.0, self.uncertainty + uncertainty_delta)),
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "status_updated_at_utc": time.time(),
                "previous_status": self.status.value if self.status else None,
                "previous_revision": self.revision,
            },
        )


# =============================================================================
# PROPOSITION BUILDER
# =============================================================================


class PropositionBuilder:
    """
    Builds propositions from collections of assertions.
    
    Aggregates semantic content from multiple assertions into a coherent
    proposition for belief formation.
    """
    
    def __init__(
        self,
        minimum_supporting_assertions: int = 1,
        maximum_conflict_ratio: float = 0.5,
    ):
        """
        Initialize the builder.
        
        Args:
            minimum_supporting_assertions: Minimum assertions to accept
            maximum_conflict_ratio: Maximum ratio of conflicting evidence allowed
        """
        self._minimum_supporting = minimum_supporting_assertions
        self._maximum_conflict = maximum_conflict_ratio
    
    def build_proposition(
        self,
        assertion_ids: List[str],
        statement: str = "",
        supporting_evidence: Optional[List[str]] = None,
        counter_evidence: Optional[List[str]] = None,
    ) -> KnowledgeProposition:
        """
        Build a proposition from assertions.
        
        Args:
            assertion_ids: IDs of assertions to include
            statement: Unified semantic claim (optional)
            supporting_evidence: Supporting evidence references (optional)
            counter_evidence: Contradicting evidence references (optional)
            
        Returns:
            A new proposition with calculated confidence/uncertainty
        """
        num_assertions = len(assertion_ids)
        
        # Calculate base confidence based on assertion count and evidence balance
        supporting_count = len(supporting_evidence or [])
        counter_count = len(counter_evidence or [])
        
        total_evidence = supporting_count + counter_count
        
        if total_evidence > 0:
            # Base confidence on ratio of supporting to total evidence
            base_confidence = supporting_count / total_evidence
        else:
            # Default confidence when no explicit evidence provided
            base_confidence = 0.5
        
        # Adjust for assertion count (more assertions = higher confidence)
        if num_assertions >= self._minimum_supporting:
            assertion_bonus = min(0.2, num_assertions * 0.05)
        else:
            assertion_bonus = -0.1
        
        final_confidence = max(0.0, min(1.0, base_confidence + assertion_bonus))
        
        return KnowledgeProposition(
            proposition_identity=f"proposition:{uuid.uuid4().hex[:16]}",
            assertions=tuple(assertion_ids),
            statement=statement,
            status=PropositionState.PROVISIONAL if final_confidence > 0.5 else PropositionState.UNKNOWN,
            supporting_evidence=tuple(supporting_evidence or []),
            counter_evidence=tuple(counter_evidence or []),
            confidence=final_confidence,
            uncertainty=1.0 - final_confidence,
            provenance={
                "created_at_utc": time.time(),
                "assertion_count": num_assertions,
                "supporting_count": supporting_count,
                "counter_count": counter_count,
                "revision": 1,
            },
        )
    
    def evaluate_proposition(
        self,
        proposition: KnowledgeProposition,
    ) -> Tuple[PropositionState, float]:
        """
        Evaluate a proposition and determine its optimal state.
        
        Args:
            proposition: The proposition to evaluate
            
        Returns:
            (optimal_state, evaluation_confidence)
        """
        supporting_count = len(proposition.supporting_evidence)
        counter_count = len(proposition.counter_evidence)
        
        # Calculate net support ratio
        total = supporting_count + counter_count
        
        if total == 0:
            return PropositionState.UNKNOWN, 0.3
        
        support_ratio = supporting_count / total
        
        # Determine state based on evidence balance
        if support_ratio > 0.7:
            return PropositionState.ACCEPTED, support_ratio
        elif support_ratio < 0.3:
            return PropositionState.REJECTED, 1.0 - support_ratio
        else:
            return PropositionState.PROVISIONAL, support_ratio


__all__ = [
    "PropositionState",
    "KnowledgeProposition",
    "PropositionBuilder",
]