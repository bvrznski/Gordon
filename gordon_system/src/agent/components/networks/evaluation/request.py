# Gordon Cognitive Architecture - Phase 4.5.5
# Action Evaluation Request
# =========================

"""
Action Evaluation Request type definitions.

This module defines the request types that initiate evaluation of Action Candidates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# ACTION EVALUATION REQUEST ID TYPES
# =============================================================================

EvaluationRequestId = str
"""Unique identifier for an evaluation request."""


# =============================================================================
# ACTION CANDIDATE REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionCandidateReference:
    """
    Reference to an Action Candidate being evaluated.
    
    This is a lightweight reference that preserves identity without embedding
    full candidate data. The actual candidate data comes from the evaluation
    context or external source.
    
    PROPERTIES:
        • candidate_id: Unique identifier for the candidate
        • revision: Candidate revision number (for version tracking)
        • kind: Canonical category of the action
    """
    
    candidate_id: EvaluationRequestId
    """Unique identifier for this candidate."""
    
    revision: int = 1
    """Monotonically increasing revision number."""
    
    kind: str = "unknown"
    """Canonical category of the action (ActionKind.*)."""


# =============================================================================
# ACTION EVALUATION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionEvaluationRequest:
    """
    Request to evaluate a pool of Action Candidates.
    
    This request specifies what candidates to evaluate and under what context.
    It does NOT contain the candidate data itself - that comes from external
    sources or evaluation context.
    
    PROPERTIES:
        • request_id: Unique identifier for this evaluation request
        • revision: Request revision number (for tracking updates)
        • candidate_references: References to candidates being evaluated
        • context_reference: Reference to evaluation context (external source)
        • evaluation_scope: Which dimensions to evaluate
        • priority: Evaluation priority hint (not determinative)
    
    NOT RESPONSIBLE FOR:
        - Storing actual candidate data
        - Making selection decisions
        - Allocating resources
        - Executing actions
    """
    
    request_id: EvaluationRequestId
    """Unique identifier for this evaluation request."""
    
    revision: int = 1
    """Monotonically increasing revision number."""
    
    candidate_references: Tuple[ActionCandidateReference, ...] = field(
        default_factory=tuple
    )
    """References to candidates being evaluated."""
    
    context_reference: str = ""
    """Reference to evaluation context (external source)."""
    
    evaluation_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Dimension names to evaluate. Empty tuple means all dimensions."""
    
    priority: int = 0
    """Evaluation priority hint (-100 to 100, not determinative)."""

    @classmethod
    def from_candidates(
        cls,
        candidates: Tuple[ActionCandidateReference, ...],
        request_id: EvaluationRequestId = "",
    ) -> ActionEvaluationRequest:
        """
        Create an evaluation request from candidate references.
        
        Args:
            candidates: References to candidates being evaluated
            request_id: Optional unique identifier for this request
            
        Returns:
            New ActionEvaluationRequest with the given candidates
        """
        return cls(
            request_id=request_id or "eval_request_default",
            candidate_references=candidates,
        )