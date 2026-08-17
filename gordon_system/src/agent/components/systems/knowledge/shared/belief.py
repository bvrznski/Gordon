# Knowledge Belief - Phase 5.4
# ============================

"""
Knowledge Belief: Gordon's current semantic commitment.

Beliefs represent Gordon's accepted semantic claims that have been supported
by sufficient evidence and justification. Beliefs remain revisable and are
always evidence-based.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# BELIEF STATES - Lifecycle of a belief
# =============================================================================


class BeliefState(Enum):
    """
    States of belief lifecycle.
    
    Every belief shall have an explicit state indicating its current
    position in the semantic commitment pipeline.
    """
    
    PROVISIONAL = "provisional"     # Tentatively accepted, pending review
    ACCEPTED = "accepted"           # Accepted as supported by evidence
    QUESTIONED = "questioned"       # Facing challenge from new evidence
    REVISED = "revised"             # Updated based on new information
    SUPERSEDED = "superseded"       # Replaced by newer belief
    REJECTED = "rejected"           # Refuted and no longer held
    UNKNOWN = "unknown"             # State indeterminate


# =============================================================================
# BELIEF MODEL - Canonical belief structure
# =============================================================================


@dataclass(frozen=True)
class KnowledgeBelief:
    """
    Canonical representation of a semantic commitment in Gordon's knowledge system.
    
    A belief represents Gordon's current semantic acceptance of a proposition
    that has been supported by evidence and justification. Beliefs remain
    revisable and are always evidence-based.
    
    Fields:
        belief_identity:       Unique identifier for this belief
        supported_propositions: References to propositions this belief supports
        supporting_evidence:   Evidence directly supporting this belief
        counter_evidence:      Evidence contradicting this belief
        confidence:            Semantic confidence in this belief (0.0-1.0)
        uncertainty:           Semantic uncertainty about this belief
        revision:              Revision number for traceability
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity and metadata (required)
    belief_identity: str              # Unique ID for this belief
    
    # Propositions supported by this belief
    supported_propositions: Tuple[str, ...] = field(default_factory=tuple)  # Proposition IDs
    
    # Evidence and justification
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    counter_evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    # Quality metrics (required)
    confidence: float = 0.5           # Semantic confidence (0.0-1.0)
    uncertainty: float = 0.5          # Semantic uncertainty (0.0-1.0)
    
    # Lifecycle tracking
    revision: int = 1                 # Revision number for traceability
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    # State management
    state: BeliefState = BeliefState.PROVISIONAL
    justification_chain: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        """Check if belief has minimal required data."""
        return (
            len(self.belief_identity) > 0 and
            self.state is not None
        )
    
    @property
    def is_accepted(self) -> bool:
        """Check if this belief is currently accepted."""
        return self.state == BeliefState.ACCEPTED
    
    @property
    def is_rejected(self) -> bool:
        """Check if this belief has been rejected."""
        return self.state == BeliefState.REJECTED
    
    @property
    def net_support_ratio(self) -> float:
        """
        Calculate the net support ratio.
        
        Returns:
            Positive value means net support, negative means net contradiction
        """
        supporting = len(self.supporting_evidence)
        counter = len(self.counter_evidence)
        total = supporting + counter
        if total == 0:
            return 0.0
        return (supporting - counter) / total
    
    @classmethod
    def create(
        cls,
        proposition_ids: Optional[List[str]] = None,
        supporting_evidence: Optional[List[str]] = None,
        counter_evidence: Optional[List[str]] = None,
        justification_chain: Optional[List[str]] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
        state: BeliefState = BeliefState.PROVISIONAL,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeBelief":
        """
        Create a new belief.
        
        Args:
            proposition_ids: References to supported propositions (optional)
            supporting_evidence: Evidence directly supporting this belief
            counter_evidence: Evidence contradicting this belief
            justification_chain: References to justifications (optional)
            confidence: Semantic confidence (0.0-1.0)
            uncertainty: Semantic uncertainty (0.0-1.0)
            state: Current lifecycle state
            provenance: Origin tracking data (optional)
        """
        net_support = len(supporting_evidence or []) - len(counter_evidence or [])
        
        return cls(
            belief_identity=f"belief:{uuid.uuid4().hex[:16]}",
            supported_propositions=tuple(proposition_ids or []),
            supporting_evidence=tuple(supporting_evidence or []),
            counter_evidence=tuple(counter_evidence or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            revision=1,
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "net_support": net_support,
                "revision": 1,
            },
            state=state,
            justification_chain=tuple(justification_chain or []),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert belief to dictionary for serialization."""
        return {
            "belief_identity": self.belief_identity,
            "supported_propositions": list(self.supported_propositions),
            "supporting_evidence": list(self.supporting_evidence),
            "counter_evidence": list(self.counter_evidence),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "revision": self.revision,
            "provenance": dict(self.provenance),
            "state": self.state.value if self.state else None,
            "justification_chain": list(self.justification_chain),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeBelief":
        """Create belief from dictionary."""
        state_value = data.get("state", "provisional")
        try:
            state = BeliefState(state_value)
        except ValueError:
            state = BeliefState.PROVISIONAL
        
        return cls(
            belief_identity=data.get("belief_identity", str(uuid.uuid4())),
            supported_propositions=tuple(data.get("supported_propositions", [])),
            supporting_evidence=tuple(data.get("supporting_evidence", [])),
            counter_evidence=tuple(data.get("counter_evidence", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
            state=state,
            justification_chain=tuple(data.get("justification_chain", [])),
        )
    
    def update_state(
        self,
        new_state: BeliefState,
        confidence_delta: float = 0.0,
        uncertainty_delta: float = 0.0,
    ) -> "KnowledgeBelief":
        """
        Create a revision of this belief with updated state.
        
        Args:
            new_state: The new lifecycle state
            confidence_delta: Confidence adjustment (-1.0 to +1.0)
            uncertainty_delta: Uncertainty adjustment (-1.0 to +1.0)
        """
        return KnowledgeBelief(
            belief_identity=self.belief_identity,
            supported_propositions=self.supported_propositions,
            supporting_evidence=self.supporting_evidence,
            counter_evidence=self.counter_evidence,
            confidence=max(0.0, min(1.0, self.confidence + confidence_delta)),
            uncertainty=max(0.0, min(1.0, self.uncertainty + uncertainty_delta)),
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "state_updated_at_utc": time.time(),
                "previous_state": self.state.value if self.state else None,
                "previous_revision": self.revision,
            },
            state=new_state,
            justification_chain=self.justification_chain,
        )
    
    def add_supporting_evidence(
        self,
        evidence_id: str,
    ) -> "KnowledgeBelief":
        """Create a revision with additional supporting evidence."""
        if evidence_id in self.supporting_evidence:
            return self
        
        return KnowledgeBelief(
            belief_identity=self.belief_identity,
            supported_propositions=self.supported_propositions,
            supporting_evidence=self.supporting_evidence + (evidence_id,),
            counter_evidence=self.counter_evidence,
            confidence=min(1.0, self.confidence * 1.05),
            uncertainty=max(0.0, self.uncertainty * 0.95),
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "evidence_added": evidence_id,
                "revised_at_utc": time.time(),
            },
            state=self.state,
            justification_chain=self.justification_chain,
        )


# =============================================================================
# BELIEF VALIDATOR
# =============================================================================


class BeliefValidator:
    """
    Validates beliefs for semantic integrity and consistency.
    
    Ensures beliefs are properly supported and their states are valid.
    """
    
    def __init__(
        self,
        minimum_supporting_evidence: int = 1,
        maximum_counter_ratio: float = 0.5,
    ):
        """
        Initialize the validator.
        
        Args:
            minimum_supporting_evidence: Minimum evidence to accept a belief
            maximum_counter_ratio: Maximum ratio of counter-evidence allowed
        """
        self._min_supporting = minimum_supporting_evidence
        self._max_counter_ratio = maximum_counter_ratio
    
    @property
    def minimum_supporting_evidence(self) -> int:
        """Minimum supporting evidence threshold."""
        return self._min_supporting
    
    def validate(
        self,
        belief: KnowledgeBelief,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a belief for semantic integrity.
        
        Args:
            belief: The belief to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Rule 1: Must have identity
        if not belief.belief_identity or len(belief.belief_identity) == 0:
            issues.append("Missing belief identity")
        
        # Rule 2: Confidence must be in valid range
        if not (0.0 <= belief.confidence <= 1.0):
            issues.append(f"Invalid confidence: {belief.confidence}")
        
        # Rule 3: Uncertainty must be in valid range
        if not (0.0 <= belief.uncertainty <= 1.0):
            issues.append(f"Invalid uncertainty: {belief.uncertainty}")
        
        # Rule 4: Must have minimum supporting evidence for ACCEPTED state
        if (
            belief.state == BeliefState.ACCEPTED and
            len(belief.supporting_evidence) < self._min_supporting
        ):
            issues.append(
                f"ACCEPTED belief lacks minimum supporting evidence: "
                f"{len(belief.supporting_evidence)} < {self._min_supporting}"
            )
        
        # Rule 5: Counter-evidence ratio should not exceed maximum
        total = len(belief.supporting_evidence) + len(belief.counter_evidence)
        if total > 0:
            counter_ratio = len(belief.counter_evidence) / total
            if counter_ratio > self._max_counter_ratio:
                issues.append(
                    f"Counter-evidence ratio {counter_ratio:.2f} exceeds maximum "
                    f"{self._max_counter_ratio}"
                )
        
        # Rule 6: Confidence + uncertainty should sum to approximately 1.0
        total = belief.confidence + belief.uncertainty
        if not (0.8 <= total <= 1.2):
            issues.append(f"Confidence-uncertainty imbalance: {total:.2f}")
        
        return len(issues) == 0, issues
    
    def evaluate_state(
        self,
        belief: KnowledgeBelief,
    ) -> BeliefState:
        """
        Evaluate the optimal state for a belief based on evidence.
        
        Args:
            belief: The belief to evaluate
            
        Returns:
            Optimal belief state
        """
        supporting = len(belief.supporting_evidence)
        counter = len(belief.counter_evidence)
        total = supporting + counter
        
        if total == 0:
            return BeliefState.PROVISIONAL
        
        support_ratio = supporting / total
        
        if support_ratio > 0.8 and belief.confidence > 0.7:
            return BeliefState.ACCEPTED
        elif support_ratio < 0.2 or len(belief.counter_evidence) > supporting:
            return BeliefState.REJECTED
        elif counter > 0:
            return BeliefState.QUESTIONED
        else:
            return BeliefState.PROVISIONAL


__all__ = [
    "BeliefState",
    "KnowledgeBelief",
    "BeliefValidator",
]