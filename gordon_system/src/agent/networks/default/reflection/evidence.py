# Reflection Evidence Models
# ==========================

"""
Immutable models for reflection evidence, contradictions, and product tracking.

ARCHITECTURAL PRINCIPLES:
    - Evidence is immutable and bounded
    - Contradictions remain visible (never silently resolved)
    - Products reference supporting evidence or record insufficient support
    - No runtime dependencies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# EVIDENCE CATEGORIES
# =============================================================================

class EvidenceCategory:
    """
    Canonical categories of reflection evidence.
    
    Every piece of evidence must have a category that determines
    how it should be evaluated and weighted.
    """
    
    # Source activity
    SOURCE_ACTIVITY = "source_activity"
    """Raw semantic activity from the subject."""
    
    OBJECTIVE = "objective"
    """Objective or goal information."""
    
    PLAN = "plan"
    """Plan or intended sequence of actions."""
    
    DECISION = "decision"
    """Decision and its rationale."""
    
    OUTCOME = "outcome"
    """Actual outcome or result."""
    
    FAILURE = "failure"
    """Failure event or unexpected result."""
    
    SUCCESS = "success"
    """Success event or expected result."""
    
    # Contextual
    ASSUMPTION = "assumption"
    """Explicit or inferred assumption."""
    
    CONSTRAINT = "constraint"
    """Constraint that influenced activity."""
    
    MEMORY = "memory"
    """Memory projection or retrieval."""
    
    IDENTITY = "identity"
    """Identity state projection."""
    
    NARRATIVE = "narrative"
    """Narrative context projection."""
    
    PREDICTION = "prediction"
    """Predictive model result."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """Internal thought from the reflection subject."""
    
    # Feedback
    ACTION_FEEDBACK = "action_feedback"
    """Feedback on actions taken."""
    
    PARTICIPANT_FEEDBACK = "participant_feedback"
    """Feedback from participants."""
    
    WORKSPACE_FEEDBACK = "workspace_feedback"
    """Feedback from conscious workspace."""
    
    POLICY = "policy"
    """Policy constraint or rule applied."""
    
    # Analysis results
    CONTRADICTION = "contradiction"
    """Detected contradiction."""
    
    PATTERN = "pattern"
    """Detected pattern."""
    
    UNKNOWN = "unknown"
    """Evidence category cannot be determined."""


# =============================================================================
# REFLECTION EVIDENCE ITEM
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionEvidence:
    """
    Immutable evidence item collected during reflection.
    
    Evidence is used to support or challenge reflective products.
    Every piece of evidence must preserve its source and quality metrics.
    
    PROPERTIES:
        • evidence_id: Unique identifier
        • category: What type of evidence (EvidenceCategory.*)
        • source_id: Reference to original source
        • source_revision: Source revision at capture time
        • summary: Brief description
        • content_references: Where to find detailed content
        • confidence: Quality assessment (0.0 to 1.0)
        • relevance: Relevance to reflection subject (0.0 to 1.0)
        • freshness: Temporal relevance indicator
        
    BOUNDEDNESS:
        Evidence must be bounded by scope limits.
    
    NOT RESPONSIBLE FOR:
        - Mutating source data
        - Creating runtime tasks
        - Allocating memory for full content
    """
    
    evidence_id: str
    """Unique identifier for this evidence item."""
    
    category: str  # EvidenceCategory.*
    """The category of this evidence."""
    
    source_id: Optional[str] = None
    """Reference to the original source (memory ID, thought ID, etc.)."""
    
    source_revision: int = 1
    """Source system revision at time of capture."""
    
    summary: str = ""
    """Brief description of the evidence."""
    
    content_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to detailed content (not full payloads)."""
    
    confidence: float = 0.5
    """Confidence in this evidence (0.0 to 1.0)."""
    
    relevance: float = 0.5
    """Relevance to the reflection subject (0.0 to 1.0)."""
    
    freshness: str = "unknown"  # EvidenceFreshness.*
    """Temporal freshness indicator."""
    
    provenance: Optional[str] = None
    """Provenance reference (how this evidence was obtained)."""
    
    @classmethod
    def from_memory(
        cls,
        memory_id: str,
        summary: str = "",
        confidence: float = 0.5,
        relevance: float = 0.5,
    ) -> ReflectionEvidence:
        """Create evidence from a memory projection."""
        return cls(
            evidence_id=f"evidence_mem_{memory_id[-12:]}",
            category=EvidenceCategory.MEMORY,
            source_id=memory_id,
            summary=summary,
            confidence=confidence,
            relevance=relevance,
        )
    
    @classmethod
    def from_thought(
        cls,
        thought_id: str,
        summary: str = "",
        confidence: float = 0.5,
        relevance: float = 0.5,
    ) -> ReflectionEvidence:
        """Create evidence from an internal thought."""
        return cls(
            evidence_id=f"evidence_thought_{thought_id[-12:]}",
            category=EvidenceCategory.INTERNAL_THOUGHT,
            source_id=thought_id,
            summary=summary,
            confidence=confidence,
            relevance=relevance,
        )
    
    @classmethod
    def from_pattern(
        cls,
        pattern_id: str,
        summary: str = "",
        confidence: float = 0.7,
        relevance: float = 0.8,
    ) -> ReflectionEvidence:
        """Create evidence describing a detected pattern."""
        return cls(
            evidence_id=f"evidence_pat_{pattern_id[-12:]}",
            category=EvidenceCategory.PATTERN,
            source_id=pattern_id,
            summary=summary,
            confidence=confidence,
            relevance=relevance,
        )
    
    def to_reference(self) -> str:
        """Return a reference string for this evidence."""
        return f"{self.category}:{self.evidence_id}"


# =============================================================================
# REFLECTION CONTRADICTION
# =============================================================================

class ContradictionCategory:
    """
    Canonical categories of contradiction.
    
    A contradiction represents conflicting information that must
    remain visible until resolved by an authorized semantic process.
    """
    
    EVIDENCE_CONFLICT = "evidence_conflict"
    """Conflicting evidence items."""
    
    OBJECTIVE_CONFLICT = "objective_conflict"
    """Conflicting objectives or goals."""
    
    PLAN_CONFLICT = "plan_conflict"
    """Conflicting plans or strategies."""
    
    IDENTITY_CONFLICT = "identity_conflict"
    """Conflict with identity model."""
    
    NARRATIVE_CONFLICT = "narrative_conflict"
    """Conflict with narrative continuity."""
    
    MEMORY_CONFLICT = "memory_conflict"
    """Conflict between memory items."""
    
    PREDICTION_CONFLICT = "prediction_conflict"
    """Conflict between prediction and outcome."""
    
    POLICY_CONFLICT = "policy_conflict"
    """Conflict with policy constraints."""
    
    OUTCOME_CONFLICT = "outcome_conflict"
    """Conflicting outcome interpretations."""
    
    SELF_ASSESSMENT_CONFLICT = "self_assessment_conflict"
    """Internal conflict in self-assessment."""


@dataclass(frozen=True, slots=True)
class ReflectionContradiction:
    """
    Record of a contradiction detected during reflection.
    
    Contradictions are NEVER silently resolved. They remain visible
    for later resolution by authorized processes.
    
    PROPERTIES:
        • contradiction_id: Unique identifier
        • category: What type of conflict (ContradictionCategory.*)
        • description: Human-readable explanation
        • evidence_ids: IDs of conflicting evidence items
        • severity: "blocking" or "non-blocking"
        • resolution_status: How the conflict will be handled
        
    BOUNDEDNESS:
        Contradictions must be bounded and recorded, not hidden.
    """
    
    contradiction_id: str
    """Unique identifier for this contradiction."""
    
    category: str  # ContradictionCategory.*
    """The type of conflict."""
    
    description: str
    """Human-readable explanation of the contradiction."""
    
    evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of conflicting evidence items."""
    
    severity: str = "non-blocking"
    """Impact level: 'blocking' or 'non-blocking'"""
    
    resolution_status: str = "unresolved"
    """How this will be handled (unresolved, acknowledged, deferred)"""
    
    confidence: float = 0.5
    """Confidence that the contradiction is real."""
    
    @classmethod
    def evidence_conflict(
        cls,
        evidence_a_id: str,
        evidence_b_id: str,
        description: str,
    ) -> ReflectionContradiction:
        """Create an evidence conflict contradiction."""
        return cls(
            contradiction_id=f"contradiction_{evidence_a_id[-8:]}_{evidence_b_id[-8:]}",
            category=ContradictionCategory.EVIDENCE_CONFLICT,
            description=description,
            evidence_ids=(evidence_a_id, evidence_b_id),
        )
    
    @classmethod
    def blocking(
        cls,
        category: str,
        description: str,
        evidence_ids: Tuple[str, ...] = (),
    ) -> ReflectionContradiction:
        """Create a blocking contradiction."""
        return cls(
            contradiction_id=f"contradiction_{category[-8:]}",
            category=category,
            description=description,
            evidence_ids=evidence_ids,
            severity="blocking",
        )
    
    @classmethod
    def non_blocking(
        cls,
        category: str,
        description: str,
        evidence_ids: Tuple[str, ...] = (),
    ) -> ReflectionContradiction:
        """Create a non-blocking contradiction."""
        return cls(
            contradiction_id=f"contradiction_{category[-8:]}",
            category=category,
            description=description,
            evidence_ids=evidence_ids,
            severity="non-blocking",
        )
    
    @classmethod
    def from_assumptions(
        cls,
        assumption_a_id: str,
        assumption_b_id: str,
        conflict_description: str,
    ) -> ReflectionContradiction:
        """Create a contradiction from conflicting assumptions."""
        return cls(
            contradiction_id=f"contradiction_{assumption_a_id[-8:]}_{assumption_b_id[-8:]}",
            category=ContradictionCategory.IDENTITY_CONFLICT,
            description=(
                f"Assumptions conflict: {conflict_description}\n"
                f"A: {assumption_a_id}, B: {assumption_b_id}"
            ),
            evidence_ids=(assumption_a_id, assumption_b_id),
        )