# Internal Episode Outcome Model
# =============================

"""
Outcome model for internal episode coordination.

Outcomes represent the terminal result of episode coordination. They remain
proposals or bounded results and do NOT directly mutate source systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


InternalEpisodeOutcomeId = str
"""Unique identifier for an episode outcome."""


@dataclass(frozen=True, slots=True)
class InternalEpisodeOutcome:
    """
    Immutable terminal result of an internal episode coordination.
    
    Outcomes remain proposals or bounded results. They do NOT directly mutate
    source systems - that happens in separate coordination layers.
    
    OUTCOME KINDS:
        • insight_produced: Valid insight produced
        • context_integrated: Context successfully updated
        • hypothesis_produced: New hypothesis or prediction produced
        • scenarios_produced: Scenario set completed (for simulation)
        • contradiction_identified: Contradiction detected and recorded
        • concern_refined: Unresolved concern clarified or structured
        • narrative_update_proposed: Narrative update proposed (not applied)
        • identity_update_proposed: Identity update proposed (not applied)
        • memory_update_proposed: Memory update proposed (not applied)
        • workspace_candidate_produced: Workspace candidate prepared for submission
        • follow_up_recommended: Follow-up episode recommended
        • no_meaningful_result: Episode completed but produced no meaningful result
        • insufficient_context: Context did not meet minimum requirements
        • partially_completed: Some steps completed but not all
        
    PROPERTIES:
        • outcome_id: Unique identifier for this outcome
        • episode_id: Which episode produced this outcome
        • kind: What type of result (InternalOutcomeKind.*)
        • status: Validation status (proposed, validated, rejected, pending)
        
    BOUNDEDNESS:
        • summary: Brief text summary instead of unlimited content
        • result_references: References to results (not full payloads)
        • evidence_references: References to supporting evidence
        
    NOT RESPONSIBLE FOR:
        • Directly mutating memory, identity, or workspace
        • Creating runtime tasks or threads
        • Scheduling further processing
    """
    
    # Identity and reference
    outcome_id: InternalEpisodeOutcomeId
    """Unique identifier for this outcome."""
    
    episode_id: str
    """ID of the episode that produced this outcome."""
    
    kind: str  # InternalOutcomeKind.*
    """What type of result this is."""
    
    status: str = "proposed"  # InternalOutcomeStatus.*
    """Validation status of this outcome."""
    
    # Content (bounded)
    summary: str
    """Brief text summary of the result (not unlimited content)."""
    
    result_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to result artifacts (not full payloads)."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence items."""
    
    # Quality assessment
    confidence: float = 0.5
    """Confidence level in the outcome (0.0 to 1.0)."""
    
    completeness: str = "partial"  # InternalOutcomeStatus.*
    """Completeness of this outcome."""
    
    # Continuation recommendation
    continuation: Optional[InternalEpisodeContinuation] = None
    """Advisory recommendation for what to do next."""
    
    # Proposals (bounded)
    proposals: Tuple[InternalEpisodeProposal, ...] = field(default_factory=tuple)
    """Any suggested actions (not applied mutations)."""
    
    created_at_utc: str = ""
    """When this outcome was produced."""
    
    provenance: Optional[str] = None
    """Provenance reference (where this outcome type is documented)."""
    
    @classmethod
    def create(
        cls,
        outcome_id: str,
        episode_id: str,
        kind: str,
        summary: str,
        confidence: float = 0.5,
        completeness: str = "partial",
    ) -> InternalEpisodeOutcome:
        """
        Create a new episode outcome.
        
        Args:
            outcome_id: Unique identifier for this outcome
            episode_id: ID of the episode that produced this outcome
            kind: What type of result (InternalOutcomeKind.*)
            summary: Brief text summary of the result
            confidence: Confidence level (0.0 to 1.0)
            completeness: Completeness status
            
        Returns:
            New InternalEpisodeOutcome instance
        """
        return cls(
            outcome_id=outcome_id,
            episode_id=episode_id,
            kind=kind,
            status="proposed",
            summary=summary,
            confidence=confidence,
            completeness=completeness,
        )
    
    def is_success(self) -> bool:
        """Check if this outcome represents success."""
        return self.status == "validated" and InternalOutcomeKind.is_success(self.kind)
    
    def is_terminal(self) -> bool:
        """Check if this outcome represents a terminal episode state."""
        return InternalOutcomeKind.is_terminal(self.kind)


@dataclass(frozen=True, slots=True)
class InternalEpisodeProposal:
    """
    Suggested action from an episode outcome.
    
    A proposal is NOT an applied mutation. Every proposal must identify
    the intended owner and the requested change.
    """
    
    # Identity
    proposal_id: str
    """Unique identifier for this proposal."""
    
    # Intended recipient
    intended_owner: str
    """Who should apply this proposal (system or module name)."""
    
    requested_change: str
    """What change is being proposed."""
    
    # Evidence
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence."""
    
    confidence: float = 0.5
    """Confidence in the proposal (0.0 to 1.0)."""
    
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Constraints or conditions for applying this proposal."""
    
    provenance: Optional[str] = None
    """Provenance reference (where this proposal type is documented)."""
    
    authorization_required: bool = False
    """Whether explicit authorization is required to apply."""


@dataclass(frozen=True, slots=True)
class InternalEpisodeContinuation:
    """
    Advisory continuation recommendation from an episode.
    
    These are NOT runtime commands. They are semantic coordination guidance
    that must be interpreted by a higher-level coordinator or ExecutionLoop.
    """
    
    kind: str  # ContinuationKind.*
    """Advisory recommendation type."""
    
    confidence: float = 0.5
    """Confidence in this recommendation (0.0 to 1.0)."""
    
    reason: Optional[str] = None
    """Human-readable explanation of the recommendation."""
    
    next_action_id: Optional[str] = None
    """ID for a proposed follow-up action or episode."""
    
    context_refresh_required: bool = False
    """Whether a context refresh is recommended before continuing."""
    
    @classmethod
    def complete(cls) -> InternalEpisodeContinuation:
        """Create a COMPLETE recommendation."""
        return cls(kind="complete", confidence=1.0, reason="Episode completed successfully")
    
    @classmethod
    def continue_(cls, next_step_id: str) -> InternalEpisodeContinuation:
        """Create a CONTINUE recommendation."""
        return cls(
            kind="continue",
            confidence=0.9,
            reason="Continue with current plan and context",
            next_action_id=next_step_id,
        )
    
    @classmethod
    def wait_for_input(cls) -> InternalEpisodeContinuation:
        """Create a WAIT_FOR_INPUT recommendation."""
        return cls(
            kind="wait_for_input",
            confidence=0.5,
            reason="Required projected information is unavailable",
        )
    
    @classmethod
    def suspend(cls, reason: Optional[str] = None) -> InternalEpisodeContinuation:
        """Create a SUSPEND recommendation."""
        return cls(
            kind="suspend",
            confidence=0.8,
            reason=reason or "Processing paused for resource management",
        )
    
    @classmethod
    def fail(cls, failure_reason: str) -> InternalEpisodeContinuation:
        """Create a FAIL recommendation."""
        return cls(
            kind="fail",
            confidence=1.0,
            reason=f"Episode failed: {failure_reason}",
        )