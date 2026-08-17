# Knowledge Belief System - Phase 6.6
# ======================================

"""
Knowledge Belief System: Gordon's epistemic control layer.

This subsystem manages Gordon's current epistemic commitments - what is currently
accepted as true, what is rejected, what remains uncertain or suspended.

The belief system forms the interface between static semantic knowledge (Assertions)
and dynamic cognition. It determines which semantic claims influence reasoning,
planning, and decision-making at any given moment.

Architecture:
    concepts → assertions → beliefs → reasoning → planning → decision

Key Principles:
    - Beliefs are epistemic commitments to Assertions
    - Acceptance is explicit (ACCEPTED/REJECTED/SUSPENDED)
    - Confidence and uncertainty remain independent metrics
    - Revision history is preserved, never overwritten
    - Dependency propagation maintains provenance
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
from dataclasses import dataclass, field
import uuid
import time


# =============================================================================
# BELIEF STATES - Acceptance states
# =============================================================================


class BeliefAcceptanceState(Enum):
    """
    States of belief acceptance.
    
    Every belief shall have an explicit acceptance state indicating whether it is
    currently accepted, rejected, suspended, or in some other epistemic condition.
    """
    
    ACCEPTED = "accepted"       # Currently held as true
    REJECTED = "rejected"       # Currently held as false
    SUSPENDED = "suspended"     # Withheld judgment, pending more evidence
    CONTESTED = "contested"     # Facing challenge, evaluation in progress
    UNKNOWN = "unknown"         # State indeterminate or not yet evaluated


class BeliefLifecycleState(Enum):
    """
    States of belief lifecycle.
    
    Tracks the evolutionary path of a belief through its existence.
    """
    
    CREATED = "created"          # Initial creation
    EVALUATING = "evaluating"    # Under evaluation for acceptance
    ACTIVE = "active"            # Currently influencing cognition
    SUSPENDED = "suspended"      # Temporarily withheld
    REVISED = "revised"          # Updated from previous state
    SUPERSEDED = "superseded"    # Replaced by newer belief
    ARCHIVED = "archived"        # No longer active but preserved
    INVALID = "invalid"          # Found to be invalid


# =============================================================================
# BELIEF KINDS - Classification by content type
# =============================================================================


class BeliefKind(Enum):
    """
    Kinds of beliefs based on their semantic nature.
    """
    
    EMPIRICAL = "empirical"           # Based on observation
    DEFINITIONAL = " definitional"    # Based on definitions
    MATHEMATICAL = "mathematical"     # Based on mathematical reasoning
    PROCEDURAL = "procedural"         # About how to do things
    SOCIAL = "social"                 # Social norms and conventions
    CAUSAL = "causal"                 # Cause-effect relationships
    TEMPORAL = "temporal"             # Temporal ordering
    PREDICTIVE = "predictive"         # Future predictions
    SELF_MODEL = "self_model"         # About the agent itself
    WORLD_MODEL = "world_model"       # About the external world
    META_COGNITIVE = "meta_cognitive" # About cognition itself
    UNKNOWN = "unknown"               # Kind indeterminate


# =============================================================================
# BASE BELIEF MODEL - Core epistemic commitment
# =============================================================================


@dataclass(frozen=True)
class BaseBelief:
    """
    Base model for a belief representing an epistemic commitment.
    
    Fields:
        belief_identity:     Unique identifier for this belief
        semantic_identity:   Reference to the Assertion's identity
        belief_kind:         Classification of this belief's content
        acceptance_state:    Current acceptance status
        confidence:          Epistemic confidence (0.0-1.0)
        uncertainty:         Epistemic uncertainty (0.0-1.0)
        revision:            Revision number for traceability
        provenance:          Origin tracking with timestamps and sources
        lifecycle_state:     Position in the belief lifecycle
    """
    
    # Identity and metadata (required)
    belief_identity: str
    
    # Reference to semantic content (required)
    semantic_identity: str  # Assertion identity being believed
    
    # Classification
    belief_kind: BeliefKind = BeliefKind.UNKNOWN
    
    # Epistemic state (required)
    acceptance_state: BeliefAcceptanceState = BeliefAcceptanceState.UNKNOWN
    
    # Quality metrics (required)
    confidence: float = 0.5  # Epistemic confidence (0.0-1.0)
    uncertainty: float = 0.5  # Epistemic uncertainty (0.0-1.0)
    
    # Lifecycle tracking
    revision: int = 1
    provenance: Dict[str, Any] = field(default_factory=dict)
    lifecycle_state: BeliefLifecycleState = BeliefLifecycleState.CREATED
    
    @property
    def is_valid(self) -> bool:
        """Check if belief has minimal required data."""
        return (
            len(self.belief_identity) > 0 and
            len(self.semantic_identity) > 0 and
            self.acceptance_state is not None
        )
    
    @property
    def is_accepted(self) -> bool:
        """Check if this belief is currently accepted."""
        return self.acceptance_state == BeliefAcceptanceState.ACCEPTED
    
    @property
    def is_rejected(self) -> bool:
        """Check if this belief has been rejected."""
        return self.acceptance_state == BeliefAcceptanceState.REJECTED
    
    @property
    def is_suspended(self) -> bool:
        """Check if this belief is suspended."""
        return self.acceptance_state == BeliefAcceptanceState.SUSPENDED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert belief to dictionary for serialization."""
        return {
            "belief_identity": self.belief_identity,
            "semantic_identity": self.semantic_identity,
            "belief_kind": self.belief_kind.value if self.belief_kind else None,
            "acceptance_state": self.acceptance_state.value if self.acceptance_state else None,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "revision": self.revision,
            "provenance": dict(self.provenance),
            "lifecycle_state": self.lifecycle_state.value if self.lifecycle_state else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseBelief":
        """Create belief from dictionary."""
        return cls(
            belief_identity=data.get("belief_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            belief_kind=cls._parse_belief_kind(data.get("belief_kind")),
            acceptance_state=cls._parse_acceptance_state(data.get("acceptance_state")),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
            lifecycle_state=cls._parse_lifecycle_state(data.get("lifecycle_state")),
        )
    
    @staticmethod
    def _parse_belief_kind(value: Optional[str]) -> BeliefKind:
        if value is None:
            return BeliefKind.UNKNOWN
        try:
            return BeliefKind(value)
        except ValueError:
            return BeliefKind.UNKNOWN
    
    @staticmethod
    def _parse_acceptance_state(value: Optional[str]) -> BeliefAcceptanceState:
        if value is None:
            return BeliefAcceptanceState.UNKNOWN
        try:
            return BeliefAcceptanceState(value)
        except ValueError:
            return BeliefAcceptanceState.UNKNOWN
    
    @staticmethod
    def _parse_lifecycle_state(value: Optional[str]) -> BeliefLifecycleState:
        if value is None:
            return BeliefLifecycleState.CREATED
        try:
            return BeliefLifecycleState(value)
        except ValueError:
            return BeliefLifecycleState.CREATED


# =============================================================================
# BELIEF ACCEPTANCE DECISION - Acceptance outcome
# =============================================================================


@dataclass(frozen=True)
class BeliefAcceptanceDecision:
    """
    Decision about belief acceptance.
    
    Encapsulates the outcome of an epistemic evaluation determining whether
    a belief candidate should be accepted, rejected, or suspended.
    """
    
    # Identity and metadata
    decision_identity: str
    
    # Evaluated items
    evaluated_assertions: Tuple[str, ...]  # Assertion identities being evaluated
    
    # Decision outcome
    decision: BeliefAcceptanceState
    
    # Justification
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    justification: Optional[str] = None
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if decision has minimal required data."""
        return (
            len(self.decision_identity) > 0 and
            self.decision is not None
        )
    
    @classmethod
    def create_accept(cls, assertion_id: str, evidence_ids: Optional[List[str]] = None) -> "BeliefAcceptanceDecision":
        """Create an acceptance decision."""
        return cls(
            decision_identity=f"decision:{uuid.uuid4().hex[:16]}",
            evaluated_assertions=(assertion_id,),
            decision=BeliefAcceptanceState.ACCEPTED,
            supporting_evidence=tuple(evidence_ids or []),
            provenance={"created_at_utc": time.time()},
        )
    
    @classmethod
    def create_reject(cls, assertion_id: str, justification: str) -> "BeliefAcceptanceDecision":
        """Create a rejection decision."""
        return cls(
            decision_identity=f"decision:{uuid.uuid4().hex[:16]}",
            evaluated_assertions=(assertion_id,),
            decision=BeliefAcceptanceState.REJECTED,
            justification=justification,
            provenance={"created_at_utc": time.time()},
        )
    
    @classmethod
    def create_suspend(cls, assertion_id: str, reason: str) -> "BeliefAcceptanceDecision":
        """Create a suspension decision."""
        return cls(
            decision_identity=f"decision:{uuid.uuid4().hex[:16]}",
            evaluated_assertions=(assertion_id,),
            decision=BeliefAcceptanceState.SUSPENDED,
            justification=reason,
            provenance={"created_at_utc": time.time()},
        )


# =============================================================================
# BELIEF CONFIDENCE - Confidence metrics
# =============================================================================


@dataclass(frozen=True)
class BeliefConfidence:
    """
    Confidence metrics for a belief.
    
    Represents the epistemic confidence in a belief, derived from various
    contributing sources of evidence and reasoning.
    """
    
    # Identity and metadata
    confidence_identity: str
    
    # Contributing sources
    contributing_sources: Tuple[str, ...] = field(default_factory=tuple)  # Source IDs
    
    # Confidence measure (0.0-1.0)
    confidence_measure: float = 0.5
    
    # History of confidence values over time
    confidence_history: Tuple[Tuple[float, int], ...] = field(default_factory=tuple)  # (value, revision)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if confidence has valid data."""
        return (
            len(self.confidence_identity) > 0 and
            0.0 <= self.confidence_measure <= 1.0
        )
    
    @classmethod
    def create(cls, source_ids: Optional[List[str]] = None, measure: float = 0.5) -> "BeliefConfidence":
        """Create a new confidence measurement."""
        return cls(
            confidence_identity=f"confidence:{uuid.uuid4().hex[:16]}",
            contributing_sources=tuple(source_ids or []),
            confidence_measure=max(0.0, min(1.0, float(measure))),
            provenance={"created_at_utc": time.time()},
        )
    
    def update(self, new_measure: float, source_id: Optional[str] = None) -> "BeliefConfidence":
        """Create a revision with updated confidence."""
        new_history = self.confidence_history + ((self.confidence_measure, self.revision),)
        return BeliefConfidence(
            confidence_identity=self.confidence_identity,
            contributing_sources=(
                self.contributing_sources + (source_id,) if source_id else self.contributing_sources
            ),
            confidence_measure=max(0.0, min(1.0, float(new_measure))),
            confidence_history=new_history,
            provenance={
                **self.provenance,
                "updated_at_utc": time.time(),
                "previous_confidence": self.confidence_measure,
            },
        )
    
    @property
    def revision(self) -> int:
        """Get the number of revisions from history length."""
        return len(self.confidence_history)


# =============================================================================
# BELIEF UNCERTAINTY - Uncertainty sources and measures
# =============================================================================


@dataclass(frozen=True)
class BeliefUncertainty:
    """
    Uncertainty metrics for a belief.
    
    Represents epistemic uncertainty, tracking the sources of unresolved
    questions and missing evidence affecting belief confidence.
    """
    
    # Identity and metadata
    uncertainty_identity: str
    
    # Sources of uncertainty
    uncertainty_sources: Tuple[str, ...] = field(default_factory=tuple)  # Source descriptions
    
    # Unresolved questions
    unresolved_questions: Tuple[str, ...] = field(default_factory=tuple)
    
    # Uncertainty measure (0.0-1.0, where higher means more uncertain)
    uncertainty_measure: float = 0.5
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if uncertainty has valid data."""
        return (
            len(self.uncertainty_identity) > 0 and
            0.0 <= self.uncertainty_measure <= 1.0
        )
    
    @classmethod
    def create(cls, source_descriptions: Optional[List[str]] = None, measure: float = 0.5) -> "BeliefUncertainty":
        """Create a new uncertainty measurement."""
        return cls(
            uncertainty_identity=f"uncertainty:{uuid.uuid4().hex[:16]}",
            uncertainty_sources=tuple(source_descriptions or []),
            unresolved_questions=(),
            uncertainty_measure=max(0.0, min(1.0, float(measure))),
            provenance={"created_at_utc": time.time()},
        )
    
    def add_uncertainty_source(self, source: str) -> "BeliefUncertainty":
        """Create a revision with additional uncertainty source."""
        return BeliefUncertainty(
            uncertainty_identity=self.uncertainty_identity,
            uncertainty_sources=self.uncertainty_sources + (source,),
            unresolved_questions=self.unresolved_questions,
            uncertainty_measure=min(1.0, self.uncertainty_measure * 1.1),
            provenance={
                **self.provenance,
                "source_added": source,
                "updated_at_utc": time.time(),
            },
        )
    
    def resolve_uncertainty(self, resolved_source: str) -> "BeliefUncertainty":
        """Create a revision with a resolved uncertainty source."""
        remaining_sources = tuple(s for s in self.uncertainty_sources if s != resolved_source)
        new_measure = max(0.0, self.uncertainty_measure * 0.9) if remaining_sources else 0.0
        return BeliefUncertainty(
            uncertainty_identity=self.uncertainty_identity,
            uncertainty_sources=remaining_sources,
            unresolved_questions=tuple(q for q in self.unresolved_questions if resolved_source not in q),
            uncertainty_measure=new_measure,
            provenance={
                **self.provenance,
                "source_resolved": resolved_source,
                "updated_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF DEPENDENCY - Dependency between beliefs
# =============================================================================


@dataclass(frozen=True)
class BeliefDependency:
    """
    Dependency relationship between beliefs.
    
    Represents how one belief depends on another, forming a graph of
    epistemic dependencies that propagates changes through the system.
    """
    
    # Identity and metadata
    dependency_identity: str
    
    # Dependent belief (the dependent)
    dependent_belief: str  # Belief identity that is dependent
    
    # Supporting belief (what the dependent relies on)
    supporting_belief: str  # Belief identity being depended upon
    
    # Kind of dependency
    dependency_kind: str = "evidence"  # e.g., "evidence", "premise", "context"
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if dependency has valid data."""
        return (
            len(self.dependency_identity) > 0 and
            len(self.dependent_belief) > 0 and
            len(self.supporting_belief) > 0
        )
    
    @classmethod
    def create(cls, dependent_id: str, supporting_id: str, kind: str = "evidence") -> "BeliefDependency":
        """Create a new dependency relationship."""
        return cls(
            dependency_identity=f"dependency:{uuid.uuid4().hex[:16]}",
            dependent_belief=dependent_id,
            supporting_belief=supporting_id,
            dependency_kind=kind,
            provenance={"created_at_utc": time.time()},
        )


# =============================================================================
# BELIEF CONSISTENCY - Consistency evaluation results
# =============================================================================


@dataclass(frozen=True)
class BeliefConsistency:
    """
    Consistency evaluation for a set of beliefs.
    
    Represents the result of evaluating logical, causal, temporal, and other
    consistency relations among beliefs in the belief network.
    """
    
    # Identity and metadata
    consistency_identity: str
    
    # Evaluated beliefs
    evaluated_beliefs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Findings
    findings: Dict[str, Any] = field(default_factory=dict)
    
    # Violations found (if any)
    violations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Consistency score (0.0-1.0, where higher means more consistent)
    consistency_score: float = 1.0
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if consistency evaluation has valid data."""
        return len(self.consistency_identity) > 0 and 0.0 <= self.consistency_score <= 1.0
    
    @classmethod
    def create(cls, belief_ids: Optional[List[str]] = None) -> "BeliefConsistency":
        """Create a new consistency evaluation for beliefs."""
        return cls(
            consistency_identity=f"consistency:{uuid.uuid4().hex[:16]}",
            evaluated_beliefs=tuple(belief_ids or []),
            provenance={"created_at_utc": time.time()},
        )
    
    def add_violation(self, violation: str) -> "BeliefConsistency":
        """Create a revision with an additional consistency violation."""
        new_score = self.consistency_score * 0.9
        return BeliefConsistency(
            consistency_identity=self.consistency_identity,
            evaluated_beliefs=self.evaluated_beliefs,
            findings={
                **self.findings,
                f"violation_{len(self.violations)}": violation,
            },
            violations=self.violations + (violation,),
            consistency_score=new_score,
            provenance={
                **self.provenance,
                "violation_added": violation,
                "updated_at_utc": time.time(),
            },
        )
    
    def update_score(self, new_score: float) -> "BeliefConsistency":
        """Create a revision with updated consistency score."""
        return BeliefConsistency(
            consistency_identity=self.consistency_identity,
            evaluated_beliefs=self.evaluated_beliefs,
            findings=self.findings,
            violations=self.violations,
            consistency_score=max(0.0, min(1.0, float(new_score))),
            provenance={
                **self.provenance,
                "score_updated": new_score,
                "updated_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF SUSPENSION - Suspension information
# =============================================================================


@dataclass(frozen=True)
class BeliefSuspension:
    """
    Information about a suspended belief.
    
    Represents the suspension of a belief without rejecting it, preserving
    history for potential reactivation when more evidence becomes available.
    """
    
    # Identity and metadata
    suspension_identity: str
    
    # Suspended belief reference
    suspended_belief: str  # Belief identity being suspended
    
    # Reason for suspension
    suspension_reason: str
    
    # Expected resolution path or time
    expected_resolution: Optional[str] = None
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if suspension has valid data."""
        return (
            len(self.suspension_identity) > 0 and
            len(self.suspended_belief) > 0 and
            len(self.suspension_reason) > 0
        )
    
    @classmethod
    def create(cls, belief_id: str, reason: str) -> "BeliefSuspension":
        """Create a new suspension record."""
        return cls(
            suspension_identity=f"suspension:{uuid.uuid4().hex[:16]}",
            suspended_belief=belief_id,
            suspension_reason=reason,
            provenance={"created_at_utc": time.time()},
        )
    
    def extend_suspension(self, new_resolution: str) -> "BeliefSuspension":
        """Create a revision extending the expected resolution."""
        return BeliefSuspension(
            suspension_identity=self.suspension_identity,
            suspended_belief=self.suspended_belief,
            suspension_reason=self.suspension_reason,
            expected_resolution=new_resolution,
            provenance={
                **self.provenance,
                "resolution_extended": new_resolution,
                "updated_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF REVISION - Revision history entry
# =============================================================================


@dataclass(frozen=True)
class BeliefRevision:
    """
    Record of a belief revision.
    
    Represents the evolution of a belief from one state to another, preserving
    full history and provenance for traceability and debugging.
    """
    
    # Identity and metadata
    revision_identity: str
    
    # Previous state reference
    previous_revision: Optional[str]  # Reference to prior revision
    
    # Current revision state
    revised_state: Dict[str, Any]
    
    # Reason for revision
    revision_reason: str
    
    # Supporting changes that triggered the revision
    supporting_changes: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if revision has valid data."""
        return (
            len(self.revision_identity) > 0 and
            len(self.revised_state) > 0 and
            len(self.revision_reason) > 0
        )
    
    @classmethod
    def create(cls, belief_id: str, reason: str, new_state: Dict[str, Any]) -> "BeliefRevision":
        """Create a new revision record."""
        return cls(
            revision_identity=f"revision:{uuid.uuid4().hex[:16]}",
            previous_revision=None,
            revised_state=new_state,
            revision_reason=reason,
            provenance={
                "belief_id": belief_id,
                "created_at_utc": time.time(),
            },
        )
    
    def link_to_previous(self, previous_revision: str) -> "BeliefRevision":
        """Link this revision to a previous one in the chain."""
        return BeliefRevision(
            revision_identity=self.revision_identity,
            previous_revision=previous_revision,
            revised_state=self.revised_state,
            revision_reason=self.revision_reason,
            supporting_changes=self.supporting_changes,
            provenance={
                **self.provenance,
                "linked_to_previous": True,
            },
        )


# =============================================================================
# BELIEF STABILITY - Stability metrics
# =============================================================================


@dataclass(frozen=True)
class BeliefStability:
    """
    Stability metrics for a belief.
    
    Represents the accumulated stability of a belief, measuring how resistant
    it is to revision based on its history and supporting evidence.
    """
    
    # Identity and metadata
    stability_identity: str
    
    # Belief reference
    belief: str  # Belief identity being measured
    
    # Stability measure (0.0-1.0, where higher means more stable)
    stability_measure: float = 0.0
    
    # Historical measurements over time
    supporting_history: Tuple[str, ...] = field(default_factory=tuple)  # Evidence/justification IDs
    
    # Confidence in the belief
    confidence: float = 0.5
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if stability measurement has valid data."""
        return (
            len(self.stability_identity) > 0 and
            len(self.belief) > 0 and
            0.0 <= self.stability_measure <= 1.0
        )
    
    @classmethod
    def create(cls, belief_id: str) -> "BeliefStability":
        """Create initial stability measurement for a belief."""
        return cls(
            stability_identity=f"stability:{uuid.uuid4().hex[:16]}",
            belief=belief_id,
            provenance={"created_at_utc": time.time()},
        )
    
    def add_support(self, evidence_id: str) -> "BeliefStability":
        """Create a revision with additional supporting history."""
        return BeliefStability(
            stability_identity=self.stability_identity,
            belief=self.belief,
            stability_measure=min(1.0, self.stability_measure + 0.1),
            supporting_history=self.supporting_history + (evidence_id,),
            confidence=min(1.0, self.confidence * 1.05),
            provenance={
                **self.provenance,
                "support_added": evidence_id,
                "updated_at_utc": time.time(),
            },
        )
    
    def accumulate_stability(self, additional_measure: float) -> "BeliefStability":
        """Create a revision with accumulated stability."""
        return BeliefStability(
            stability_identity=self.stability_identity,
            belief=self.belief,
            stability_measure=min(1.0, self.stability_measure + additional_measure),
            supporting_history=self.supporting_history,
            confidence=self.confidence,
            provenance={
                **self.provenance,
                "stability_accumulated": additional_measure,
                "updated_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF GOVERNANCE - Governance findings
# =============================================================================


@dataclass(frozen=True)
class BeliefGovernance:
    """
    Governance evaluation for beliefs.
    
    Represents the result of evaluating beliefs against governance rules,
    identifying unsupported, stale, redundant, conflicting, or unstable beliefs.
    """
    
    # Identity and metadata
    governance_identity: str
    
    # Evaluated beliefs
    evaluated_beliefs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Findings
    findings: Dict[str, Any] = field(default_factory=dict)
    
    # Violations found (if any)
    violations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Recommendations for action
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if governance evaluation has valid data."""
        return len(self.governance_identity) > 0
    
    @classmethod
    def create(cls, belief_ids: Optional[List[str]] = None) -> "BeliefGovernance":
        """Create a new governance evaluation for beliefs."""
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_beliefs=tuple(belief_ids or []),
            provenance={"created_at_utc": time.time()},
        )
    
    def add_violation(self, violation: str) -> "BeliefGovernance":
        """Create a revision with an additional governance violation."""
        return BeliefGovernance(
            governance_identity=self.governance_identity,
            evaluated_beliefs=self.evaluated_beliefs,
            findings={
                **self.findings,
                f"violation_{len(self.violations)}": violation,
            },
            violations=self.violations + (violation,),
            recommendations=self.recommendations,
            provenance={
                **self.provenance,
                "violation_added": violation,
                "updated_at_utc": time.time(),
            },
        )
    
    def add_recommendation(self, recommendation: str) -> "BeliefGovernance":
        """Create a revision with an additional governance recommendation."""
        return BeliefGovernance(
            governance_identity=self.governance_identity,
            evaluated_beliefs=self.evaluated_beliefs,
            findings=self.findings,
            violations=self.violations,
            recommendations=self.recommendations + (recommendation,),
            provenance={
                **self.provenance,
                "recommendation_added": recommendation,
                "updated_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF VALIDATION - Validation results
# =============================================================================


@dataclass(frozen=True)
class BeliefValidation:
    """
    Validation result for a belief.
    
    Represents the outcome of validating a belief against all applicable
    validation rules, including semantic integrity and consistency checks.
    """
    
    # Identity and metadata
    validation_identity: str
    
    # Validated belief reference
    validated_belief: str  # Belief identity being validated
    
    # Validation outcome
    is_valid: bool = False
    
    # Issues found (if any)
    issues: Tuple[str, ...] = field(default_factory=tuple)
    
    # Validation rules that passed
    passed_rules: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, belief_id: str) -> "BeliefValidation":
        """Create a new validation record."""
        return cls(
            validation_identity=f"validation:{uuid.uuid4().hex[:16]}",
            validated_belief=belief_id,
            provenance={"created_at_utc": time.time()},
        )
    
    def mark_valid(self, rules_passed: Optional[List[str]] = None) -> "BeliefValidation":
        """Mark the belief as valid."""
        return BeliefValidation(
            validation_identity=self.validation_identity,
            validated_belief=self.validated_belief,
            is_valid=True,
            passed_rules=tuple(rules_passed or ["semantic_integrity", "identity"]),
            provenance={
                **self.provenance,
                "validated_at_utc": time.time(),
            },
        )
    
    def mark_invalid(self, issues: List[str]) -> "BeliefValidation":
        """Mark the belief as invalid with specific issues."""
        return BeliefValidation(
            validation_identity=self.validation_identity,
            validated_belief=self.validated_belief,
            is_valid=False,
            issues=tuple(issues),
            passed_rules=self.passed_rules,
            provenance={
                **self.provenance,
                "invalidation_reasons": issues,
                "validated_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF UPDATE - Complete update package
# =============================================================================


@dataclass(frozen=True)
class BeliefUpdate:
    """
    Complete belief update package.
    
    Encapsulates all components of a belief update: the base belief, its
    confidence and uncertainty metrics, dependencies, consistency state,
    and governance evaluation.
    """
    
    # Identity and metadata
    update_identity: str
    
    # Base belief being updated
    belief: BaseBelief
    
    # Supporting metrics
    confidence: BeliefConfidence = field(default_factory=BeliefConfidence.create)
    uncertainty: BeliefUncertainty = field(default_factory=BeliefUncertainty.create)
    
    # Dependencies (if any)
    dependencies: Tuple[BeliefDependency, ...] = field(default_factory=tuple)
    
    # Consistency state
    consistency: Optional[BeliefConsistency] = None
    
    # Governance evaluation
    governance: Optional[BeliefGovernance] = None
    
    # Revision history
    revision: BeliefRevision = field(default_factory=lambda: BeliefRevision.create("unknown", "initial", {}))
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if update package has valid data."""
        return self.belief.is_valid
    
    @classmethod
    def create(
        cls,
        belief_id: str,
        semantic_identity: str,
        acceptance_state: BeliefAcceptanceState = BeliefAcceptanceState.ACCEPTED,
        kind: BeliefKind = BeliefKind.UNKNOWN,
        confidence_measure: float = 0.5,
        uncertainty_measure: float = 0.5,
    ) -> "BeliefUpdate":
        """Create a new belief update package."""
        return cls(
            update_identity=f"update:{uuid.uuid4().hex[:16]}",
            belief=BaseBelief(
                belief_identity=belief_id,
                semantic_identity=semantic_identity,
                belief_kind=kind,
                acceptance_state=acceptance_state,
                confidence=confidence_measure,
                uncertainty=uncertainty_measure,
                provenance={"created_at_utc": time.time()},
            ),
            confidence=BeliefConfidence.create(measure=confidence_measure),
            uncertainty=BeliefUncertainty.create(measure=uncertainty_measure),
            provenance={"created_at_utc": time.time()},
        )


# =============================================================================
# BELIEF DEPENDENCY GRAPH - Complete dependency structure
# =============================================================================


@dataclass(frozen=True)
class BeliefDependencyGraph:
    """
    Complete dependency graph for a set of beliefs.
    
    Represents the full graph of epistemic dependencies, enabling efficient
    propagation of confidence, uncertainty, and belief state changes.
    """
    
    # Identity and metadata
    graph_identity: str
    
    # Participating beliefs (nodes)
    participating_beliefs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Dependency edges
    dependency_edges: Tuple[BeliefDependency, ...] = field(default_factory=tuple)
    
    # Kind of graph (e.g., "evidence", "premise", "causal")
    graph_kind: str = "evidence"
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if dependency graph has valid data."""
        return len(self.graph_identity) > 0
    
    @classmethod
    def create(cls, belief_ids: Optional[List[str]] = None) -> "BeliefDependencyGraph":
        """Create a new dependency graph."""
        return cls(
            graph_identity=f"depgraph:{uuid.uuid4().hex[:16]}",
            participating_beliefs=tuple(belief_ids or []),
            provenance={"created_at_utc": time.time()},
        )
    
    def add_dependency(self, dependency: BeliefDependency) -> "BeliefDependencyGraph":
        """Create a revision with an additional dependency edge."""
        new_beliefs = tuple(set(self.participating_beliefs + (dependency.dependent_belief, dependency.supporting_belief)))
        return BeliefDependencyGraph(
            graph_identity=self.graph_identity,
            participating_beliefs=new_beliefs,
            dependency_edges=self.dependency_edges + (dependency,),
            graph_kind=self.graph_kind,
            provenance={
                **self.provenance,
                "edge_added": f"{dependency.dependent_belief} -> {dependency.supporting_belief}",
                "updated_at_utc": time.time(),
            },
        )
    
    def remove_dependency(self, dependency_id: str) -> "BeliefDependencyGraph":
        """Create a revision with a dependency edge removed."""
        new_edges = tuple(d for d in self.dependency_edges if d.dependency_identity != dependency_id)
        return BeliefDependencyGraph(
            graph_identity=self.graph_identity,
            participating_beliefs=self.participating_beliefs,
            dependency_edges=new_edges,
            graph_kind=self.graph_kind,
            provenance={
                **self.provenance,
                "edge_removed": dependency_id,
                "updated_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF CONFLICT - Conflict between beliefs
# =============================================================================


@dataclass(frozen=True)
class BeliefConflict:
    """
    Conflict representation between beliefs.
    
    Represents a conflict where two or more beliefs disagree about the
    acceptance of related semantic content. Conflicts do not automatically
    resolve; they remain explicit for deliberative resolution.
    """
    
    # Identity and metadata
    conflict_identity: str
    
    # Participating beliefs
    participating_beliefs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Reason for the conflict
    conflict_reason: str
    
    # Scope of the conflict (e.g., "semantic", "causal", "temporal")
    conflict_scope: str = "semantic"
    
    # Resolution status
    resolution_status: str = "pending"  # pending, in_progress, resolved, abandoned
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if conflict has valid data."""
        return (
            len(self.conflict_identity) > 0 and
            len(self.participating_beliefs) >= 2 and
            len(self.conflict_reason) > 0
        )
    
    @classmethod
    def create(cls, belief_ids: List[str], reason: str) -> "BeliefConflict":
        """Create a new conflict between beliefs."""
        return cls(
            conflict_identity=f"conflict:{uuid.uuid4().hex[:16]}",
            participating_beliefs=tuple(belief_ids),
            conflict_reason=reason,
            provenance={"created_at_utc": time.time()},
        )
    
    def mark_resolved(self, resolution: str) -> "BeliefConflict":
        """Mark the conflict as resolved."""
        return BeliefConflict(
            conflict_identity=self.conflict_identity,
            participating_beliefs=self.participating_beliefs,
            conflict_reason=self.conflict_reason,
            conflict_scope=self.conflict_scope,
            resolution_status="resolved",
            provenance={
                **self.provenance,
                "resolution": resolution,
                "resolved_at_utc": time.time(),
            },
        )
    
    def mark_abandoned(self, reason: str) -> "BeliefConflict":
        """Mark the conflict as abandoned without resolution."""
        return BeliefConflict(
            conflict_identity=self.conflict_identity,
            participating_beliefs=self.participating_beliefs,
            conflict_reason=self.conflict_reason,
            conflict_scope=self.conflict_scope,
            resolution_status="abandoned",
            provenance={
                **self.provenance,
                "abandonment_reason": reason,
                "abandoned_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF CONFIDENCE PROPAGATION - Propagation result
# =============================================================================


@dataclass(frozen=True)
class ConfidencePropagation:
    """
    Result of confidence propagation through dependency graph.
    
    Represents how confidence flows from supporting beliefs to dependent beliefs,
    preserving provenance throughout the propagation chain.
    """
    
    # Identity and metadata
    propagation_identity: str
    
    # Source beliefs (origin of confidence)
    source_beliefs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Target beliefs (receivers of confidence)
    target_beliefs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Strategy used for propagation
    propagation_strategy: str = "average"  # e.g., "average", "weighted", "min", "max"
    
    # Resulting confidence measures
    resulting_confidence: Dict[str, float] = field(default_factory=dict)  # belief_id -> confidence
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        source_ids: Optional[List[str]] = None,
        target_ids: Optional[List[str]] = None,
        strategy: str = "average",
    ) -> "ConfidencePropagation":
        """Create a new confidence propagation record."""
        return cls(
            propagation_identity=f"propagation:{uuid.uuid4().hex[:16]}",
            source_beliefs=tuple(source_ids or []),
            target_beliefs=tuple(target_ids or []),
            propagation_strategy=strategy,
            provenance={"created_at_utc": time.time()},
        )
    
    def add_result(self, belief_id: str, confidence: float) -> "ConfidencePropagation":
        """Add a resulting confidence for a belief."""
        return ConfidencePropagation(
            propagation_identity=self.propagation_identity,
            source_beliefs=self.source_beliefs,
            target_beliefs=self.target_beliefs,
            propagation_strategy=self.propagation_strategy,
            resulting_confidence={
                **self.resulting_confidence,
                belief_id: max(0.0, min(1.0, float(confidence))),
            },
            provenance={
                **self.provenance,
                f"result_{belief_id}": confidence,
                "updated_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF UNCERTAINTY PROPAGATION - Propagation result
# =============================================================================


@dataclass(frozen=True)
class UncertaintyPropagation:
    """
    Result of uncertainty propagation through dependency graph.
    
    Represents how uncertainty flows from supporting beliefs to dependent beliefs,
    ensuring that missing evidence increases rather than decreases uncertainty.
    """
    
    # Identity and metadata
    propagation_identity: str
    
    # Sources of uncertainty
    uncertainty_sources: Tuple[str, ...] = field(default_factory=tuple)
    
    # Affected beliefs (receivers of uncertainty)
    affected_beliefs: Tuple[str, ...] = field(default_factory=tuple)
    
    # Strategy used for propagation
    propagation_strategy: str = "accumulate"  # e.g., "accumulate", "max", "average"
    
    # Resulting uncertainty measures
    resulting_uncertainty: Dict[str, float] = field(default_factory=dict)  # belief_id -> uncertainty
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        source_descriptions: Optional[List[str]] = None,
        affected_ids: Optional[List[str]] = None,
        strategy: str = "accumulate",
    ) -> "UncertaintyPropagation":
        """Create a new uncertainty propagation record."""
        return cls(
            propagation_identity=f"uncertainty_prop:{uuid.uuid4().hex[:16]}",
            uncertainty_sources=tuple(source_descriptions or []),
            affected_beliefs=tuple(affected_ids or []),
            propagation_strategy=strategy,
            provenance={"created_at_utc": time.time()},
        )
    
    def add_result(self, belief_id: str, uncertainty: float) -> "UncertaintyPropagation":
        """Add a resulting uncertainty for a belief."""
        return UncertaintyPropagation(
            propagation_identity=self.propagation_identity,
            uncertainty_sources=self.uncertainty_sources,
            affected_beliefs=self.affected_beliefs,
            propagation_strategy=self.propagation_strategy,
            resulting_uncertainty={
                **self.resulting_uncertainty,
                belief_id: max(0.0, min(1.0, float(uncertainty))),
            },
            provenance={
                **self.provenance,
                f"result_{belief_id}": uncertainty,
                "updated_at_utc": time.time(),
            },
        )


# =============================================================================
# BELIEF REVISION STRATEGY - Strategy for revision
# =============================================================================


@dataclass(frozen=True)
class BeliefRevisionStrategy:
    """
    Strategy for revising beliefs.
    
    Represents a policy or algorithm for updating belief states, including
    Bayesian update, evidence accumulation, and other revision methods.
    """
    
    # Identity and metadata
    strategy_identity: str
    
    # Kind of strategy
    strategy_kind: str  # e.g., "bayesian", "evidence_accumulation", "confidence_adjustment"
    
    # Applicability conditions
    applicability: Tuple[str, ...] = field(default_factory=tuple)  # Conditions where strategy applies
    
    # Revision policy details
    revision_policy: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def bayesian_update(cls, prior_confidence: float = 0.5) -> "BeliefRevisionStrategy":
        """Create a Bayesian update strategy."""
        return cls(
            strategy_identity=f"strategy:bayesian:{uuid.uuid4().hex[:16]}",
            strategy_kind="bayesian",
            applicability=("new_evidence_available",),
            revision_policy={"prior_confidence": prior_confidence},
            provenance={"created_at_utc": time.time()},
        )
    
    def applies_to(self, conditions: List[str]) -> bool:
        """Check if this strategy applies to given conditions."""
        if not self.applicability:
            return True  # No restrictions means universally applicable
        return any(c in self.applicability for c in conditions)


# =============================================================================
# BELIEF REVISION RESULT - Outcome of revision
# =============================================================================


@dataclass(frozen=True)
class BeliefRevisionResult:
    """
    Result of a belief revision operation.
    
    Represents the outcome of revising a belief, including changes to confidence,
    uncertainty, acceptance state, and other metrics.
    """
    
    # Identity and metadata
    revision_identity: str
    
    # Previous state
    previous_state: Dict[str, Any]
    
    # Revised state
    revised_state: Dict[str, Any]
    
    # Supporting changes that triggered the revision
    supporting_changes: Tuple[str, ...] = field(default_factory=tuple)
    
    # Changes in metrics
    confidence_change: float = 0.0
    uncertainty_change: float = 0.0
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        previous_state: Dict[str, Any],
        revised_state: Dict[str, Any],
        changes: Optional[List[str]] = None,
    ) -> "BeliefRevisionResult":
        """Create a new revision result."""
        return cls(
            revision_identity=f"revision_result:{uuid.uuid4().hex[:16]}",
            previous_state=previous_state,
            revised_state=revised_state,
            supporting_changes=tuple(changes or []),
            provenance={"created_at_utc": time.time()},
        )
    
    def get_confidence_change(self, previous: float, current: float) -> float:
        """Calculate the confidence change between two values."""
        return current - previous
    
    def get_uncertainty_change(self, previous: float, current: float) -> float:
        """Calculate the uncertainty change between two values."""
        return current - previous


# =============================================================================
# BELIEF STABILITY HISTORY - Historical stability measurements
# =============================================================================


@dataclass(frozen=True)
class BeliefStabilityHistory:
    """
    Historical record of stability measurements for a belief.
    
    Represents how stability has accumulated over time, providing insight into
    the long-term resilience and reliability of a belief.
    """
    
    # Identity and metadata
    history_identity: str
    
    # Belief being measured
    belief: str  # Belief identity
    
    # Historical measurements (revision -> measure)
    historical_measurements: Tuple[Tuple[int, float], ...] = field(default_factory=tuple)
    
    # Trend (increasing, stable, decreasing)
    trend: str = "stable"
    
    # Current confidence
    confidence: float = 0.5
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, belief_id: str) -> "BeliefStabilityHistory":
        """Create a new stability history record."""
        return cls(
            history_identity=f"stability_history:{uuid.uuid4().hex[:16]}",
            belief=belief_id,
            provenance={"created_at_utc": time.time()},
        )
    
    def add_measurement(self, revision: int, measure: float) -> "BeliefStabilityHistory":
        """Add a historical measurement."""
        # Determine trend
        measurements = list(self.historical_measurements)
        if len(measurements) >= 2:
            last_two = [m[1] for m in measurements[-2:]]
            if measure > max(last_two):
                new_trend = "increasing"
            elif measure < min(last_two):
                new_trend = "decreasing"
            else:
                new_trend = "stable"
        else:
            new_trend = self.trend
        
        return BeliefStabilityHistory(
            history_identity=self.history_identity,
            belief=self.belief,
            historical_measurements=self.historical_measurements + ((revision, measure),),
            trend=new_trend,
            confidence=self.confidence,
            provenance={
                **self.provenance,
                f"measurement_{revision}": measure,
                "updated_at_utc": time.time(),
            },
        )
    
    def get_stability_score(self) -> float:
        """Get the current stability score (most recent measurement)."""
        if not self.historical_measurements:
            return 0.0
        return self.historical_measurements[-1][1]


# =============================================================================
# EXPORTS - All public symbols
# =============================================================================

__all__ = [
    # States
    "BeliefAcceptanceState",
    "BeliefLifecycleState",
    "BeliefKind",
    
    # Base model
    "BaseBelief",
    
    # Decision and contracts
    "BeliefAcceptanceDecision",
    
    # Metrics
    "BeliefConfidence",
    "BeliefUncertainty",
    
    # Graph structures
    "BeliefDependency",
    "BeliefDependencyGraph",
    "BeliefConsistency",
    "BeliefConflict",
    
    # State management
    "BeliefSuspension",
    "BeliefRevision",
    "BeliefStability",
    
    # Governance and validation
    "BeliefGovernance",
    "BeliefValidation",
    
    # Update and propagation
    "BeliefUpdate",
    "ConfidencePropagation",
    "UncertaintyPropagation",
    
    # Strategies and results
    "BeliefRevisionStrategy",
    "BeliefRevisionResult",
    
    # History
    "BeliefStabilityHistory",
]