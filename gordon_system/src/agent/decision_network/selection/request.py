# Gordon Cognitive Architecture - Phase 4.5.7
# ===========================================
#
"""
Final Action Selection Request types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# ID TYPES
# =============================================================================

FinalActionSelectionRequestId = str
"""Unique identifier for a final action selection request."""

FinalActionSelectionRequestRevision = int
"""Monotonically increasing revision number for a request."""


# =============================================================================
# ACTION SELECTION REQUEST REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionRequestReference:
    """
    Reference to a parent Action Selection Request.
    
    PROPERTIES:
        • selection_request_id: Unique identifier for the selection request
        • revision: Selection request revision number
    """
    
    selection_request_id: str = ""
    """Unique identifier for the selection request."""
    
    revision: int = 1
    """Monotonically increasing revision number."""


# =============================================================================
# ACTION ARBITRATION RESULT REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionArbitrationResultReference:
    """
    Reference to an Arbitration Result.
    
    PROPERTIES:
        • arbitration_result_id: Unique identifier for the arbitration result
        • revision: Arbitration result revision number
    """
    
    arbitration_result_id: str = ""
    """Unique identifier for the arbitration result."""
    
    revision: int = 1
    """Monotonically increasing revision number."""


# =============================================================================
# ACTION SELECTION FRONTIER REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionFrontierReference:
    """
    Reference to an Action Selection Frontier.
    
    PROPERTIES:
        • frontier_id: Unique identifier for the selection frontier
        • revision: Frontier revision number
    """
    
    frontier_id: str = ""
    """Unique identifier for the selection frontier."""
    
    revision: int = 1
    """Monotonically increasing revision number."""


# =============================================================================
# FINAL ACTION SELECTION PURPOSE
# =============================================================================

@dataclass(frozen=True, slots=True)
class FinalActionSelectionPurpose:
    """
    The purpose of a final action selection request.
    
    PROPERTIES:
        • kind: Canonical purpose category
        • description: Human-readable purpose description
        • scope: Bounded scope for this selection
    
    PURPOSE KINDS:
        • SELECT_ONE_ACTION: Select exactly one candidate from frontier
        • SELECT_CONDITIONAL_ACTION: Select a conditional action
        • SELECT_FALLBACK_ACTION: Select fallback when primary unavailable
        • SELECT_SAFEST_ACTION: Choose safest option from frontier
        • SELECT_INFORMATION_ACTION: Select information-gathering action
        • SELECT_RECOVERY_ACTION: Select recovery action
        • SELECT_REVERSIBLE_ACTION: Prefer reversible actions
        • SELECT_USER_CHOSEN_ACTION: Apply user choice to candidate
        • SELECT_AUTHORITY_CHOSEN_ACTION: Apply authority choice
        • CONFIRM_EXISTING_SELECTION: Confirm prior selection is still valid
        • REPLACE_SELECTED_ACTION: Replace current selection
        • REVIEW_SELECTION: Review previous selection context
        • PRODUCE_NO_SELECTION: Explicitly produce no-selection result
        • GENERAL_SELECTION: General purpose selection
    """
    
    kind: str = "SELECT_ONE_ACTION"
    """Canonical purpose category."""
    
    description: str = ""
    """Human-readable purpose description."""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope for this selection (dimension names, etc.)."""


# =============================================================================
# FINAL ACTION SELECTION CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class FinalActionSelectionContext:
    """
    Semantic context for a final action selection request.
    
    Context contains references to related artifacts without embedding them.
    
    PROPERTIES:
        • action_selection_request_reference: Parent selection context
        • arbitration_result_reference: Source of frontier
        • frontier_reference: Candidates being selected from
        • executive_decision_reference: Governing decision (if any)
        • commitment_reference: Active commitments (if any)
        • strategy_reference: Strategy context (if any)
        • plan_reference: Plan context (if any)
        • semantic_time: Semantic time reference for the selection
        • authority_context: Authority context references
    
    CONTEXT REMAINS BOUNDED:
        • Contains only references, not full artifacts
        • No implementation callbacks
        • No runtime state
    """
    
    action_selection_request_reference: ActionSelectionRequestReference | None = None
    """Parent Action Selection Request reference."""
    
    arbitration_result_reference: ActionArbitrationResultReference | None = None
    """Source Arbitration Result reference."""
    
    frontier_reference: ActionSelectionFrontierReference | None = None
    """Action Selection Frontier being consumed."""
    
    executive_decision_reference: str = ""
    """Governing Executive Decision reference."""
    
    commitment_reference: str = ""
    """Active Commitment reference."""
    
    strategy_reference: str = ""
    """Strategy context reference."""
    
    plan_reference: str = ""
    """Plan context reference."""
    
    semantic_time: str = ""
    """Semantic time reference for this selection."""
    
    authority_context: Tuple[str, ...] = field(default_factory=tuple)
    """Authority context references."""


# =============================================================================
# FINAL ACTION SELECTION SCOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class FinalActionSelectionScope:
    """
    Bounded scope for final action selection operations.
    
    Every selection must be explicitly bounded to prevent unbounded
    comparisons and resource consumption.
    
    PROPERTIES:
        • frontier: Which frontiers are permitted (None = any in request)
        • candidate_subset: Which candidates to consider (None = all)
        • permitted_action_classes: Action classes allowed for selection
        • target_scope: Permitted target scope
        • operation_scope: Permitted operation types
        • authority_scope: Authority context scope
        • temporal_scope: Time-bound scope
        • maximum_selections: Maximum number of actions to select (default 1)
    
    BOUNDED BY DESIGN:
        • Never unbounded (uses explicit limits)
        • Capacity overflow is explicit
        • Deterministic coverage when limits reached
    """
    
    frontier: Tuple[str, ...] | None = None
    """Frontier IDs permitted. None means any in request."""
    
    candidate_subset: Tuple[str, ...] | None = None
    """Candidate IDs to consider. None means all in frontier."""
    
    permitted_action_classes: Tuple[str, ...] = field(default_factory=tuple)
    """Action class names allowed for selection."""
    
    target_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Target scopes where actions may be applied."""
    
    operation_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Operation types permitted (read, write, etc.)."""
    
    authority_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Authority IDs to consider."""
    
    temporal_scope: str = ""
    """Temporal scope (e.g., "session", "task", "immediate")."""
    
    maximum_selections: int = 1
    """Maximum number of actions to select in one request."""


# =============================================================================
# FINAL ACTION SELECTION COMPLETION REQUIREMENTS
# =============================================================================

@dataclass(frozen=True, slots=True)
class FinalActionSelectionCompletionRequirements:
    """
    Requirements for selection completion.
    
    PROPERTIES:
        • minimum_completeness: Minimum completeness threshold (0.0 to 1.0)
        • require_all_frontier_candidates_assessed: Whether all must be assessed
        • require_no_unresolved_vetoes: Whether vetoes must be resolved
        • require_tie_resolution: Whether ties must be explicitly resolved
    
    COMPLETENESS LEVELS:
        • 0.0 = no candidates need to be assessed
        • 1.0 = all frontier candidates must be assessed
    """
    
    minimum_completeness: float = 0.5
    """Minimum completeness threshold (0.0 to 1.0)."""
    
    require_all_frontier_candidates_assessed: bool = False
    """Whether all frontier candidates must receive a disposition."""
    
    require_no_unresolved_vetoes: bool = True
    """Whether unresolved vetoes block selection."""
    
    require_tie_resolution: bool = True
    """Whether unresolved ties produce no-selection instead of deferral."""


# =============================================================================
# FINAL ACTION SELECTION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class FinalActionSelectionRequest:
    """
    Request to perform final action selection.
    
    This request specifies what frontier to select from, under what context,
    and with what rules. It does NOT contain the candidate data itself - that
    comes from the frontier referenced in the context.
    
    PROPERTIES:
        • request_id: Unique identifier for this selection request
        • revision: Request revision number (for tracking updates)
        • action_selection_request_reference: Parent selection request
        • arbitration_result_reference: Source of frontier
        • frontier_reference: Candidates to select from
        • purpose: What kind of selection is needed
        • context: Semantic context references
        • scope: Bounded selection scope
        • completion_requirements: How complete must selection be
    
    NOT RESPONSIBLE FOR:
        - Storing actual candidate data (comes from frontier)
        - Evaluating candidates (evaluation is separate phase)
        - Performing arbitration (arbitration constructs frontiers)
        - Allocating resources
        - Executing actions
    
    IMPORTANT LAWS:
        • ACTION-SEL-LAW-003: Selection consumes one exact ActionSelectionFrontier revision.
        • ACTION-SEL-LAW-004: Selection consumes one exact ActionSelectionRequest revision.
        • ACTION-SEL-LAW-005: Selection does not generate, reevaluate, or rearbitrate Candidates silently.
    """
    
    request_id: FinalActionSelectionRequestId
    """Unique identifier for this selection request."""
    
    revision: int = 1
    """Monotonically increasing revision number."""
    
    action_selection_request_reference: ActionSelectionRequestReference | None = None
    """Parent Action Selection Request reference."""
    
    arbitration_result_reference: ActionArbitrationResultReference | None = None
    """Source Arbitration Result reference."""
    
    frontier_reference: ActionSelectionFrontierReference | None = None
    """Action Selection Frontier being consumed."""
    
    purpose: FinalActionSelectionPurpose = field(default_factory=FinalActionSelectionPurpose)
    """What kind of selection is needed."""
    
    context: FinalActionSelectionContext = field(default_factory=FinalActionSelectionContext)
    """Semantic context references."""
    
    scope: FinalActionSelectionScope = field(default_factory=FinalActionSelectionScope)
    """Bounded scope for this selection."""
    
    completion_requirements: FinalActionSelectionCompletionRequirements = field(
        default_factory=FinalActionSelectionCompletionRequirements
    )
    """How complete must the selection be."""
    
    @classmethod
    def from_frontier(
        cls,
        frontier_reference: ActionSelectionFrontierReference,
        request_id: FinalActionSelectionRequestId = "",
    ) -> FinalActionSelectionRequest:
        """
        Create a final action selection request from a frontier reference.
        
        Args:
            frontier_reference: Reference to the frontier to select from
            request_id: Optional unique identifier for this request
            
        Returns:
            New FinalActionSelectionRequest with default settings
        """
        return cls(
            request_id=request_id or "selection_request_default",
            frontier_reference=frontier_reference,
        )