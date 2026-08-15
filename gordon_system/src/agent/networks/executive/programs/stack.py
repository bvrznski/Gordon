# Executive Control Stack
# ========================

"""
Executive Control Stack - Immutable dataclass representing nested executive programs.

The control stack represents semantic frames of program ownership, not function calls.
It shows the hierarchical relationship between programs during execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveControlStack:
    """
    Nested executive programs represented as a stack of frames.
    
    The control stack is NOT:
        - A runtime call stack with return addresses
        - An execution trace or history
        - A list of active threads
    
    The control stack IS:
        - A semantic representation of nested program ownership
        - Bounded by maximum depth to prevent unbounded nesting
        - Revisioned for deterministic reconstruction
    
    Stack operations:
        - PUSH: Add a new frame (e.g., when delegating or nesting)
        - POP: Remove top frame (e.g., when returning from delegation)
        - PEEK: View top frame without removing
        - SWAP: Replace top frame with another
    
    Example stack (bottom to top):
        [0] Main Conversation Program
            |
            v PUSH
        [1] Answer Question Program
            |
            v PUSH
        [2] Reason Program
            |
            v PUSH
        [3] Retrieve Evidence Program
            |
            v POP
        [2] Reason Program (continues)
    """
    
    # Identity and revisioning
    stack_id: str = "exec_stack_initial"
    """Unique identifier for this control stack."""
    
    program_id: str = "exec_program_initial"
    """ID of the program that owns this stack."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    revision: int = 1
    """Current revision number (strictly monotonic)."""
    
    # Stack frames - ordered from bottom to top
    frame_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of stack frames in order from bottom to top."""
    
    max_depth: int = 20
    """Maximum stack depth allowed."""
    
    # Active frame - currently executing program
    active_frame_id: Optional[str] = None
    """ID of the currently active frame (top of stack)."""
    
    # History tracking
    push_count: int = 0
    """Number of PUSH operations performed."""
    
    pop_count: int = 0
    """Number of POP operations performed."""
    
    swap_count: int = 0
    """Number of SWAP operations performed."""
    
    @classmethod
    def initial(
        cls,
        stack_id: str = "exec_stack_initial",
        program_id: str = "exec_program_initial",
    ) -> ExecutiveControlStack:
        """
        Create an initial empty control stack.
        
        Args:
            stack_id: Unique identifier for this stack
            program_id: ID of the owning program
            
        Returns:
            New stack with no frames
        """
        return cls(
            stack_id=stack_id,
            program_id=program_id,
        )
    
    def push(self, frame_id: str) -> ExecutiveControlStack:
        """
        Push a new frame onto the stack.
        
        Args:
            frame_id: ID of the frame to add
            
        Returns:
            New stack with the frame added (if capacity allows)
        """
        if len(self.frame_ids) >= self.max_depth:
            return self  # At capacity
        
        return dataclass_replace(
            self,
            frame_ids=self.frame_ids + (frame_id,),
            active_frame_id=frame_id,
            push_count=self.push_count + 1,
            revision=self.revision + 1,
        )
    
    def pop(self) -> ExecutiveControlStack:
        """
        Pop the top frame from the stack.
        
        Returns:
            New stack with top frame removed
        """
        if not self.frame_ids:
            return self  # Empty stack
        
        new_frames = self.frame_ids[:-1]
        new_active = new_frames[-1] if new_frames else None
        
        return dataclass_replace(
            self,
            frame_ids=new_frames,
            active_frame_id=new_active,
            pop_count=self.pop_count + 1,
            revision=self.revision + 1,
        )
    
    def peek(self) -> Optional[str]:
        """
        Get the top frame ID without modifying the stack.
        
        Returns:
            ID of top frame, or None if empty
        """
        if not self.frame_ids:
            return None
        return self.frame_ids[-1]
    
    def swap(self, new_frame_id: str) -> ExecutiveControlStack:
        """
        Replace the top frame with a new one.
        
        Args:
            new_frame_id: ID of the replacement frame
            
        Returns:
            New stack with top frame replaced (if stack not empty)
        """
        if not self.frame_ids:
            return self  # Empty stack
        
        new_frames = self.frame_ids[:-1] + (new_frame_id,)
        
        return dataclass_replace(
            self,
            frame_ids=new_frames,
            active_frame_id=new_frame_id,
            swap_count=self.swap_count + 1,
            revision=self.revision + 1,
        )
    
    def get_frame_at_depth(self, depth: int) -> Optional[str]:
        """
        Get the frame ID at a specific depth.
        
        Args:
            depth: 0 = bottom of stack
            
        Returns:
            Frame ID at that depth, or None if invalid
        """
        if depth < 0 or depth >= len(self.frame_ids):
            return None
        return self.frame_ids[depth]
    
    def is_empty(self) -> bool:
        """Check if the stack is empty."""
        return len(self.frame_ids) == 0
    
    def get_depth(self) -> int:
        """Get current stack depth."""
        return len(self.frame_ids)


@dataclass(frozen=True)
class ExecutiveProgramFrame:
    """
    A single frame in an ExecutiveControlStack.
    
    A program frame contains:
        - Program reference: The program at this level
        - Activation state: Whether it's currently active
        - Priority: Its priority level
        - Parent: The program that created/delegated to this one
        - Children: Programs this one has created
        - Continuation: How to resume if suspended
        - Suspension reason: Why it was suspended (if applicable)
        - Resume conditions: What must happen to resume
    """
    
    # Identity and ownership
    frame_id: str = "exec_frame_initial"
    """Unique identifier for this frame."""
    
    program_id: str = "exec_program_initial"
    """ID of the program at this stack level."""
    
    parent_program_id: Optional[str] = None
    """ID of the program that created this one (for delegation)."""
    
    # Activation state
    is_active: bool = False
    """Whether this frame's program is currently active."""
    
    activation_time_utc: float = 0.0
    """When this frame became active."""
    
    deactivation_time_utc: Optional[float] = None
    """When this frame was deactivated (if suspended)."""
    
    # Priority and ordering
    priority: int = 50
    """Priority level for this program."""
    
    order: int = 0
    """Position in ordered list of child programs."""
    
    # Continuation - how to resume if suspended
    continuation_kind: str = "resume-from-suspension"
    """
    Kind of continuation:
        'resume-from-suspension' - Resume from saved state
        'restart' - Start fresh
        'skip-to-subsequent' - Skip this program entirely
        'fallback-to-parent' - Return to parent program
    """
    
    # Suspension info (if suspended)
    is_suspended: bool = False
    """Whether this frame is currently suspended."""
    
    suspension_reason: Optional[str] = None
    """Reason for suspension (e.g., 'interrupted-by-higher-priority')."""
    
    # Resume conditions - what must happen to resume
    resume_condition_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of conditions that must be met before resuming."""
    
    # Children programs created by this program
    child_program_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of child programs created by this program."""
    
    max_children: int = 10
    """Maximum children allowed."""
    
    # Provenance
    created_by: str = "executive_network"
    """Who/what created this frame."""
    
    created_at_utc: float = 0.0
    """When frame was created (seconds since epoch)."""
    
    @classmethod
    def initial(
        cls,
        frame_id: str = "exec_frame_initial",
        program_id: str = "exec_program_initial",
    ) -> ExecutiveProgramFrame:
        """
        Create an initial program frame.
        
        Args:
            frame_id: Unique identifier for this frame
            program_id: ID of the program at this level
            
        Returns:
            New inactive, non-suspended frame with default values
        """
        return cls(
            frame_id=frame_id,
            program_id=program_id,
            priority=50,
        )
    
    def activate(self, at_utc: float) -> ExecutiveProgramFrame:
        """Create a new frame marked as active."""
        return dataclass_replace(
            self,
            is_active=True,
            activation_time_utc=at_utc,
            deactivation_time_utc=None,
        )
    
    def suspend(self, reason: str, at_utc: float) -> ExecutiveProgramFrame:
        """
        Create a new frame marked as suspended.
        
        Args:
            reason: Reason for suspension
            at_utc: Suspension timestamp
            
        Returns:
            New suspended frame with deactivation time set
        """
        return dataclass_replace(
            self,
            is_suspended=True,
            is_active=False,
            deactivation_time_utc=at_utc,
            suspension_reason=reason,
        )
    
    def resume(self, at_utc: float) -> ExecutiveProgramFrame:
        """Create a new frame marked as resumed."""
        return dataclass_replace(
            self,
            is_suspended=False,
            is_active=True,
            activation_time_utc=at_utc,
            deactivation_time_utc=None,
            suspension_reason=None,
        )
    
    def add_child(self, child_program_id: str) -> ExecutiveProgramFrame:
        """
        Add a child program to this frame.
        
        Args:
            child_program_id: ID of the child program
            
        Returns:
            New frame with child added (if capacity allows)
        """
        if len(self.child_program_ids) >= self.max_children:
            return self  # At capacity
        
        return dataclass_replace(
            self,
            child_program_ids=self.child_program_ids + (child_program_id,),
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
    "ExecutiveControlStack",
    "ExecutiveProgramFrame",
)