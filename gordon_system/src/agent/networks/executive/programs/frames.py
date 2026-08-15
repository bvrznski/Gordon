# Executive Program Frames
# ========================

"""
Executive Program Frames - Immutable dataclass for executive program frame references.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveProgramFrame:
    """
    A single frame in an ExecutiveControlStack representing a program's ownership level.
    
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


__all__: Tuple[str, ...] = (
    "ExecutiveProgramFrame",
)