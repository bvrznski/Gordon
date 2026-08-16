# Executive State Model
# =====================

"""
Canonical ExecutiveState and ExecutiveContext immutable dataclasses.

These are the core state types for Phase 4.4.2 - the authoritative, bounded,
revisioned semantic representations of executive organization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# EXECUTIVE STATE - THE CORE STATE TYPE
# =============================================================================


@dataclass(frozen=True)
class ExecutiveState:
    """
    The authoritative, bounded, revisioned semantic representation of the
    Executive Network's currently accepted executive organization.
    
    Executive State describes what the Executive Network currently accepts about:
        * its active executive configuration;
        * active task-set references;
        * active goal references;
        * active commitment references;
        * current strategy reference;
        * current executive mode;
        * control-demand summary;
        * control-allocation summary;
        * unresolved conflicts;
        * unresolved decision requirements;
        * inhibition state;
        * switching state;
        * performance summary;
        * error summary;
        * recovery state;
        * pending executive proposals;
        * pending external requests;
        * accepted external decisions;
        * relevant context revision;
        * state revision.
    
    State properties:
        - Immutable: Cannot be modified in place; use transitions to create new states
        - Bounded: All collections have capacity limits
        - Revisioned: Each state has a strictly increasing revision number
        - Deterministic: Identical inputs produce identical outputs
        - Serializable: Can be converted to/from dict for storage/transmission
    
    State NOT owned:
        - Source projections in ExecutiveContext (external ownership)
        - ExecutionThread, Loop, Cycle state (Execution owns these)
        - Working Memory content (Working Memory owns this)
        - Workspace admission state (Workspace owns this)
    
    STATE IS DISTINCT FROM:
        - ExecutiveTaskSet: Task sets are referenced BY state, not embedded
        - ExecutionState: Execution progression is separate from executive organization
        - WorkingMemoryState: Active content is maintained separately
        - GlobalAgentState: State is bounded to executive scope only
    """
    
    # Identity and revisioning
    state_id: str = "exec_state_initial"
    """Unique identifier for this state instance."""
    
    revision: int = 0
    """Current revision number (strictly monotonic)."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Executive mode - semantic, not runtime
    mode: str = "uninitialized"
    """Current executive mode (from ExecutiveMode enum)."""
    
    # Task set references
    active_task_set_id: Optional[str] = None
    """ID of currently active task set (if any)."""
    
    suspended_task_set_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of suspended task sets."""
    
    candidate_task_set_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of candidate task sets for activation."""
    
    # Goal and commitment references
    active_goal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently active goals."""
    
    active_commitment_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently active commitments."""
    
    # Strategy reference
    strategy_id: Optional[str] = None
    """ID of current strategy (if any)."""
    
    # Summary states (bounded views, not full implementations)
    control_state_summary: dict = field(default_factory=dict)
    """Bounded control state summary."""
    
    conflict_state_summary: dict = field(default_factory=dict)
    """Bounded conflict state summary."""
    
    performance_state_summary: dict = field(default_factory=dict)
    """Bounded performance state summary."""
    
    decision_state_summary: dict = field(default_factory=dict)
    """Bounded decision state summary."""
    
    inhibition_state_summary: dict = field(default_factory=dict)
    """Bounded inhibition state summary."""
    
    switching_state_summary: dict = field(default_factory=dict)
    """Bounded switching state summary."""
    
    recovery_state_summary: dict = field(default_factory=dict)
    """Bounded recovery state summary."""
    
    # Pending items
    pending_external_request_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of pending external requests."""
    
    pending_proposal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of pending executive proposals."""
    
    consumed_result_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of consumed external results."""
    
    accepted_authority_decision_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of accepted authority decisions."""
    
    # Context reference (not the full context - just a reference)
    context_reference_id: Optional[str] = None
    """ID of referenced context (if any)."""
    
    context_revision: int = 1
    """Revision of referenced context."""
    
    # State evaluation metrics
    confidence_class: str = "unknown"
    """Classification of state confidence."""
    
    completeness_class: str = "waiting"
    """Classification of state completeness."""
    
    consistency_class: str = "unknown"
    """Classification of state consistency."""
    
    coherence_class: str = "unknown"
    """Classification of state coherence."""
    
    # Metadata
    privacy_classification: str = "internal"
    """Privacy classification of this state."""
    
    provenance_created_by: str = "executive_network"
    """Who/what created this state."""
    
    provenance_created_at_utc: float = 0.0
    """When state was created (seconds since epoch)."""
    
    @property
    def is_terminal(self) -> bool:
        """Check if state is in a terminal mode."""
        return self.mode in ("completed", "failed")
    
    @classmethod
    def initial(cls) -> ExecutiveState:
        """
        Create an initial executive state.
        
        This does NOT inspect runtime environment, load goals, or create task sets.
        It creates a clean starting point with bounded empty collections.
        """
        return cls(
            state_id="exec_state_initial",
            revision=0,
            mode="uninitialized",
            confidence_class="unknown",
            completeness_class="waiting",
            consistency_class="unknown",
            coherence_class="unknown",
        )


# =============================================================================
# EXECUTIVE CONTEXT - BOUNDED PROJECTION
# =============================================================================


@dataclass(frozen=True)
class ExecutiveContext:
    """
    A bounded immutable projection of externally owned and internally derived
    semantic information considered relevant to one Executive Network assessment
    or state transition.
    
    Executive Context may include projections of:
        * current ExecutionThread, Loop, Cycle;
        * current task;
        * current conversation;
        * current objective;
        * current plan;
        * current reasoning state;
        * current decision state;
        * current action outcome;
        * Alerting state;
        * Focusing state;
        * Default Network products;
        * motivational state;
        * Working Memory state;
        * Workspace state;
        * Memory evidence;
        * predictive state;
        * monitoring state;
        * evaluation results;
        * policy constraints;
        * security constraints;
        * communication state;
        * capability availability.
    
    Executive Context is NOT authoritative ownership of source systems.
    It is a bounded, immutable view for one assessment cycle.
    
    Source projections must be:
        - Immutable (no mutable nested structures)
        - Contain only references/summaries (not full objects)
        - Preserve source owner and revision info
        - Respect privacy classifications
    
    Context properties:
        - Immutable: Cannot be modified in place; assemble new context for changes
        - Bounded: All collections have capacity limits
        - Purpose-relative: What's complete depends on the assessment purpose
        - Source-aware: Every projection preserves source information
    """
    
    # Identity and revisioning
    context_id: str = "exec_context_initial"
    """Unique identifier for this context instance."""
    
    revision: int = 1
    """Current revision number (strictly monotonic)."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    purpose: str = "general_executive_assessment"
    """Purpose of this context (determines required projections)."""
    
    subject: str = "general_executive_situation"
    """Subject being assessed in this context."""
    
    max_projections: int = 100
    """Maximum total projections allowed."""
    
    temporal_scope_seconds: float = 60.0
    """Maximum age of projections to be considered fresh."""
    
    # Execution projections (reference only)
    execution_thread_reference_id: Optional[str] = None
    """Reference ID for current thread (if projected)."""
    
    execution_loop_reference_id: Optional[str] = None
    """Reference ID for current loop (if projected)."""
    
    execution_cycle_reference_id: Optional[str] = None
    """Reference ID for current cycle (if projected)."""
    
    # Task projections (reference only)
    task_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for current tasks."""
    
    # Conversation projections (reference only)
    conversation_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for current conversations."""
    
    # Goals and commitments projections
    goal_projection_count: int = 0
    """Number of goal projections included."""
    
    commitment_projection_count: int = 0
    """Number of commitment projections included."""
    
    # Plans and reasoning products (reference only)
    plan_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for plans."""
    
    reasoning_product_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for reasoning products."""
    
    decision_product_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for decision products."""
    
    # Action projections (reference only)
    action_selection_reference_id: Optional[str] = None
    """Reference ID for action selection state."""
    
    action_outcome_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for action outcomes."""
    
    # Network projections (reference only)
    alerting_state_reference_id: Optional[str] = None
    """Reference ID for Alerting state."""
    
    focusing_state_reference_id: Optional[str] = None
    """Reference ID for Focusing state."""
    
    default_network_product_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for Default Network products."""
    
    motivation_state_reference_id: Optional[str] = None
    """Reference ID for Motivation state."""
    
    working_memory_state_reference_id: Optional[str] = None
    """Reference ID for Working Memory state."""
    
    workspace_state_reference_id: Optional[str] = None
    """Reference ID for Workspace state."""
    
    memory_projection_count: int = 0
    """Number of memory projections included."""
    
    predictive_projection_count: int = 0
    """Number of predictive projections included."""
    
    monitoring_projection_count: int = 0
    """Number of monitoring projections included."""
    
    evaluation_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for evaluations."""
    
    # Policy and security constraints (reference only)
    policy_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for policies."""
    
    security_constraint_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for security constraints."""
    
    communication_state_reference_id: Optional[str] = None
    """Reference ID for Communication state."""
    
    capability_registry_reference_id: Optional[str] = None
    """Reference ID for Capability registry."""
    
    # Source references (identifiers only, no full objects)
    source_references: Tuple[str, ...] = field(default_factory=tuple)
    """Identifiers of all sources in this context."""
    
    # Omission tracking
    omitted_sources_count: int = 0
    """Number of sources that could not be included due to bounds."""
    
    omitted_reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Reasons for omissions."""
    
    required_projections_missing: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required projections that are missing."""
    
    # Context evaluation metrics
    confidence_class: str = "unknown"
    """Classification of context confidence."""
    
    completeness_class: str = "partial"
    """Classification of context completeness."""
    
    freshness_class: str = "fresh"
    """Classification of context freshness."""
    
    consistency_class: str = "unknown"
    """Classification of context consistency."""
    
    validity_class: str = "valid"
    """Classification of context validity."""
    
    privacy_classification: str = "internal"
    """Privacy classification of this context."""
    
    provenance_assembled_by: str = "executive_context_assembler"
    """Who/what assembled this context."""
    
    provenance_assembled_at_utc: float = 0.0
    """When context was assembled (seconds since epoch)."""
    
    @classmethod
    def initial(cls) -> ExecutiveContext:
        """
        Create an initial executive context.
        
        This creates a clean starting point with empty collections and minimal
        projections for the current assessment purpose.
        """
        return cls(
            context_id="exec_context_initial",
            revision=1,
            purpose="general_executive_assessment",
            completeness_class="partial",
            freshness_class="fresh",
            confidence_class="unknown",
            consistency_class="unknown",
            validity_class="valid",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveState",
    "ExecutiveContext",
)