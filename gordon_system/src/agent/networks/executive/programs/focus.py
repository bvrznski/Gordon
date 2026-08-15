# Executive Control Focus
# ========================

"""
Executive Control Focus - Immutable dataclass representing which program owns executive resources.

The Executive Control Focus determines which Executive Program currently has control authority,
distinct from the Focusing Network's attention allocation mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveControlFocus:
    """
    Which ExecutiveProgram currently owns executive resources.
    
    Executive Control Focus is NOT:
        - The Focusing Network (which allocates attention)
        - Attention allocation mechanism
        - A runtime state of active threads
    
    Executive Control Focus IS:
        - An explicit identification of the program with authority
        - Bounded to one focus at a time (single program owns resources)
        - Revisioned for deterministic reconstruction
    
    Focus operations:
        - ACQUIRE: One program gains control, others may be suspended
        - RELEASE: Program relinquishes control, focus shifts
        - PREEMPT: Higher priority program takes control from current
        - HOLD: Current program retains focus despite requests
    
    Focus properties:
        - Single owner: Only one program has focus at a time
        - Explicit ownership: Clear record of who owns resources
        - Priority-based: Higher priority can preempt lower
        - Deterministic: Same inputs produce same outputs
    """
    
    # Identity and revisioning
    focus_id: str = "exec_focus_initial"
    """Unique identifier for this control focus."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    revision: int = 1
    """Current revision number (strictly monotonic)."""
    
    # Current focus - which program owns executive resources?
    focused_program_id: Optional[str] = None
    """ID of the currently focused program (None if no focus)."""
    
    # Focus history - recent programs that have held focus
    focus_history_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of programs in recent focus history."""
    
    max_focus_history: int = 50
    """Maximum entries in focus history."""
    
    # Priority tracking
    focused_priority: int = 0
    """Priority of the currently focused program."""
    
    last_priority_diff: int = 0
    """Priority difference from previous focus (for debugging)."""
    
    # Timing information
    focus_acquired_at_utc: Optional[float] = None
    """When current focus was acquired."""
    
    focus_held_duration_seconds: float = 0.0
    """How long the current focus has been held."""
    
    # Focus transitions
    transition_count: int = 0
    """Number of times focus has changed."""
    
    last_transition_kind: Optional[str] = None
    """Kind of last transition (acquire, release, preempt)."""
    
    last_transition_reason: Optional[str] = None
    """Reason for the last transition."""
    
    # Priority-based preemption tracking
    preemptive_transitions: int = 0
    """Number of preemptive transitions."""
    
    cooperative_transitions: int = 0
    """Number of cooperative (non-preemptive) transitions."""
    
    @classmethod
    def initial(cls) -> ExecutiveControlFocus:
        """
        Create an initial focus with no program focused.
        
        Returns:
            New focus with no focused program
        """
        return cls(
            focus_id="exec_focus_initial",
        )
    
    def acquire(self, program_id: str, priority: int, at_utc: float) -> ExecutiveControlFocus:
        """
        Acquire focus for a program.
        
        Args:
            program_id: ID of the program gaining focus
            priority: Priority level of the program
            at_utc: Time when focus was acquired
            
        Returns:
            New focus with updated state
        """
        new_history = self._add_to_history(program_id)
        
        return dataclass_replace(
            self,
            focused_program_id=program_id,
            focused_priority=priority,
            focus_acquired_at_utc=at_utc,
            focus_held_duration_seconds=0.0,
            transition_count=self.transition_count + 1,
            last_transition_kind="acquire",
            last_transition_reason="explicit-acquisition",
            focus_history_ids=new_history,
            revision=self.revision + 1,
        )
    
    def preempt(self, program_id: str, priority: int, at_utc: float) -> ExecutiveControlFocus:
        """
        Preempt current focus with a higher priority program.
        
        Args:
            program_id: ID of the preemption program
            priority: Priority level of the program
            at_utc: Time when preemption occurred
            
        Returns:
            New focus with updated state
        """
        new_history = self._add_to_history(program_id)
        
        return dataclass_replace(
            self,
            focused_program_id=program_id,
            focused_priority=priority,
            focus_acquired_at_utc=at_utc,
            focus_held_duration_seconds=0.0,
            transition_count=self.transition_count + 1,
            last_transition_kind="preempt",
            last_transition_reason=f"preemption-by-priority-{priority}",
            preemptive_transitions=self.preemptive_transitions + 1,
            focus_history_ids=new_history,
            revision=self.revision + 1,
        )
    
    def release(self, at_utc: float) -> ExecutiveControlFocus:
        """
        Release current focus.
        
        Args:
            at_utc: Time when focus was released
            
        Returns:
            New focus with no focused program
        """
        return dataclass_replace(
            self,
            focused_program_id=None,
            focused_priority=0,
            last_transition_kind="release",
            last_transition_reason="explicit-release",
            revision=self.revision + 1,
        )
    
    def update_held_duration(self, at_utc: float) -> ExecutiveControlFocus:
        """
        Update the held duration based on current time.
        
        Args:
            at_utc: Current timestamp
            
        Returns:
            New focus with updated duration (if focused)
        """
        if self.focus_acquired_at_utc is None:
            return self
        
        return dataclass_replace(
            self,
            focus_held_duration_seconds=at_utc - self.focus_acquired_at_utc,
        )
    
    def _add_to_history(self, program_id: str) -> Tuple[str, ...]:
        """Add a program ID to focus history."""
        new_history = (program_id,) + self.focus_history_ids
        if len(new_history) > self.max_focus_history:
            return new_history[:self.max_focus_history]
        return new_history


@dataclass(frozen=True)
class ExecutiveProgramTransition:
    """
    Immutable transition record for an ExecutiveProgram.
    
    A program transition represents a state change in the program's lifecycle,
    recorded for history and debugging purposes.
    """
    
    # Identity
    transition_id: str = "exec_transition_initial"
    """Unique identifier for this transition."""
    
    program_id: str = "exec_program_initial"
    """ID of the program that underwent this transition."""
    
    schema_version: str = "1.0.0"
    """Schema version at time of transition."""
    
    revision_at_transition: int = 1
    """Program revision at time of transition."""
    
    # Timestamps
    occurred_at_utc: float = 0.0
    """When transition occurred (seconds since epoch)."""
    
    # State before and after
    from_state: str = "created"
    """State the program was in before transition."""
    
    to_state: str = "preparing"
    """State the program is in after transition."""
    
    # Transition details
    kind: str = "state_change"
    """
    Kind of transition:
        'activated' - Program activated (CREATED -> PREPARING -> READY -> ACTIVE)
        'suspended' - Program suspended (ACTIVE -> SUSPENDED)
        'interrupted' - Program interrupted by higher priority
        'resumed' - Suspended program resumed
        'completed' - Program completed successfully
        'failed' - Program failed to complete
        'abandoned' - Program was abandoned
        'replaced' - Program replaced by another
        'merged' - Program merged with another
        'split' - Program split into multiple children
        'archived' - Program archived after completion
    """
    
    # Context
    triggered_by: Optional[str] = None
    """What triggered this transition (e.g., 'user_request', 'system_event')."""
    
    reason: Optional[str] = None
    """Reason for the transition."""
    
    priority_at_transition: int = 50
    """Priority of program at time of transition."""
    
    # Result
    success: bool = True
    """Whether the transition was successful."""
    
    error_message: Optional[str] = None
    """Error message if transition failed."""
    
    @classmethod
    def initial(cls) -> ExecutiveProgramTransition:
        """
        Create an initial transition record.
        
        Returns:
            New transition with default values
        """
        return cls(transition_id="exec_transition_initial")


class ExecutiveProgramTransitionKind:
    """
    Class defining valid kinds of program transitions.
    
    These are semantic descriptions of state changes, not implementation logic.
    """
    
    # Lifecycle transitions - forward progress
    CREATED = "created"
    """Initial program creation."""
    
    ACTIVATED = "activated"
    """Program activated for execution."""
    
    SUSPENDED = "suspended"
    """Program suspended (state preserved for resumption)."""
    
    RESUMED = "resumed"
    """Suspended program resumed."""
    
    COMPLETED = "completed"
    """Program completed successfully."""
    
    FAILED = "failed"
    """Program failed to complete."""
    
    ABANDONED = "abandoned"
    """Program was explicitly abandoned."""
    
    # Hierarchy transitions - structural changes
    REPLACED = "replaced"
    """Program replaced by another (same objective)."""
    
    MERGED = "merged"
    """Program merged with another program."""
    
    SPLIT = "split"
    """Program split into multiple child programs."""
    
    DELEGATED = "delegated"
    """Execution delegated to another program."""
    
    TERMINATED = "terminated"
    """Program forcefully terminated (not graceful completion)."""
    
    # Lifecycle transitions - special cases
    PAUSED = "paused"
    """Program paused temporarily (different from suspended)."""
    
    RESUMED_FROM_PAUSE = "resumed_from_pause"
    """Resumed after temporary pause."""
    
    RESTARTED = "restarted"
    """Program restarted from initial state."""
    
    # Priority-based transitions
    PREEMPTED = "preempted"
    """Preempted by higher priority program."""
    
    DEPREEMPTED = "depreepted"
    """Lower priority program reactivated after preemption."""
    
    @classmethod
    def is_lifecycle(cls, kind: str) -> bool:
        """Check if transition kind represents lifecycle progression."""
        return kind in (
            cls.CREATED,
            cls.ACTIVATED,
            cls.COMPLETED,
            cls.FAILED,
            cls.ABANDONED,
        )
    
    @classmethod
    def is_hierarchical(cls, kind: str) -> bool:
        """Check if transition kind represents structural change."""
        return kind in (
            cls.REPLACED,
            cls.MERGED,
            cls.SPLIT,
            cls.DELEGATED,
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def dataclass_replace(instance: object, **kwargs) -> object:
    """
    Helper to replace fields in an immutable dataclass instance.
    
    Args:
        instance: The dataclass instance to copy
        kwargs: Field names and new values
        
    Returns:
        New instance with specified fields replaced
    """
    import dataclasses
    
    if not hasattr(instance, "__dataclass_fields__"):
        raise TypeError(f"{type(instance).__name__} is not a dataclass")
    
    # Get current field values
    field_dict = {f.name: getattr(instance, f.name) for f in dataclasses.fields(instance)}
    
    # Update with new values
    field_dict.update(kwargs)
    
    # Create new instance
    return type(instance)(**field_dict)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveControlFocus",
    "ExecutiveProgramTransition",
    "ExecutiveProgramTransitionKind",
)