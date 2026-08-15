# Executive Control Objectives and Agenda
# ========================================

"""
Executive Control Objectives - Immutable dataclasses for semantic control objectives.

These define WHY the Executive Network controls cognition at any given moment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveControlObjective:
    """
    Represents why the Executive Network currently controls cognition.
    
    Control objectives describe the semantic purpose of executive control:
        - Solve a specific task
        - Answer a user query
        - Recover from failure
        - Suspend or switch programs
        - Monitor system state
        - Verify results
        - Plan future actions
        - Explain reasoning
    
    Objective properties:
        - Immutable: No in-place modification
        - Bounded: Limited number of objectives per program
        - Priority-ranked: Higher priority objectives get resources first
    """
    
    # Identity and ownership
    objective_id: str = "exec_objective_initial"
    """Unique identifier for this objective."""
    
    program_id: str = "exec_program_initial"
    """ID of the program that owns this objective."""
    
    # Objective type - what is being pursued?
    objective_type: str = "general"
    """
    Type of objective:
        'solve_task' - Solve a specific task
        'answer_user' - Answer a user query
        'recover' - Recover from failure state
        'suspend' - Suspend current activity
        'switch_program' - Switch between programs
        'monitor' - Monitor system state
        'verify' - Verify correctness of results
        'plan' - Create or refine a plan
        'explain' - Explain reasoning or actions
        'evaluate' - Evaluate options or outcomes
        'coordinate' - Coordinate multiple subtasks
        'maintain' - Maintain current state
    """
    
    # Objective details
    objective_description: str = ""
    """Human-readable description of the objective."""
    
    priority: int = 50
    """Priority level (higher = more urgent)."""
    
    order: int = 0
    """Position in ordered objective list."""
    
    # Status
    is_active: bool = False
    """Whether this objective is currently active."""
    
    activation_time_utc: float = 0.0
    """When this objective became active."""
    
    completion_time_utc: Optional[float] = None
    """When this objective was completed, if applicable."""
    
    # Dependencies - other objectives that must be achieved first
    dependency_objective_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of dependent objectives that must complete first."""
    
    # Constraints on achieving this objective
    constraint_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of constraints that apply to this objective."""
    
    # Success criteria
    success_criteria_met: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of satisfied success criteria."""
    
    progress_percentage: float = 0.0
    """Progress toward completion (0.0 to 1.0)."""
    
    @classmethod
    def initial(
        cls,
        objective_id: str = "exec_objective_initial",
        program_id: str = "exec_program_initial",
    ) -> ExecutiveControlObjective:
        """
        Create an initial control objective.
        
        Args:
            objective_id: Unique identifier for this objective
            program_id: ID of the owning program
            
        Returns:
            New inactive objective with default values
        """
        return cls(
            objective_id=objective_id,
            program_id=program_id,
            priority=50,
            order=0,
        )
    
    def activate(self, at_utc: float) -> ExecutiveControlObjective:
        """Create a new objective marked as active."""
        return dataclass_replace(
            self,
            is_active=True,
            activation_time_utc=at_utc,
        )
    
    def complete(self, at_utc: float, criteria_id: str) -> ExecutiveControlObjective:
        """
        Mark this objective as completed.
        
        Args:
            at_utc: Completion timestamp
            criteria_id: ID of the satisfied success criterion
            
        Returns:
            New objective with completion status set
        """
        return dataclass_replace(
            self,
            is_active=False,
            completion_time_utc=at_utc,
            progress_percentage=1.0,
            success_criteria_met=self.success_criteria_met + (criteria_id,),
        )
    
    def update_progress(self, new_progress: float) -> ExecutiveControlObjective:
        """
        Update the progress percentage.
        
        Args:
            new_progress: New progress value (0.0 to 1.0)
            
        Returns:
            New objective with updated progress
        """
        return dataclass_replace(
            self,
            progress_percentage=max(0.0, min(1.0, new_progress)),
        )


@dataclass(frozen=True)
class ExecutiveControlAgenda:
    """
    Ordered semantic objectives for an ExecutiveProgram.
    
    An agenda is NOT:
        - An execution queue (it doesn't specify HOW to execute)
        - A list of actions
        - A task plan
    
    An agenda IS:
        - An ordered collection of control objectives
        - Defines WHAT should be pursued and in what order
        - Bounded by capacity limits
        - Revisioned for deterministic reconstruction
    
    Agenda properties:
        - Immutable: No in-place modification
        - Ordered: Objectives have priority rank
        - Bounded: Maximum number of objectives
        - Semantic: Describes organization, not execution
    """
    
    # Identity and revisioning
    agenda_id: str = "exec_agenda_initial"
    """Unique identifier for this agenda."""
    
    program_id: str = "exec_program_initial"
    """ID of the program that owns this agenda."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    revision: int = 1
    """Current revision number (strictly monotonic)."""
    
    # Objectives - ordered by priority
    objective_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of objectives in order of priority."""
    
    max_objectives: int = 50
    """Maximum objectives allowed in this agenda."""
    
    # Active objective - which one currently has focus?
    active_objective_id: Optional[str] = None
    """ID of the currently active objective (if any)."""
    
    # Completed objectives
    completed_objective_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of objectives that have been completed."""
    
    # Pending objectives
    pending_objective_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of objectives that are pending activation."""
    
    # Creation and modification timestamps
    created_at_utc: float = 0.0
    """When agenda was created (seconds since epoch)."""
    
    last_modified_at_utc: float = 0.0
    """When agenda was last modified (seconds since epoch)."""
    
    @classmethod
    def initial(
        cls,
        agenda_id: str = "exec_agenda_initial",
        program_id: str = "exec_program_initial",
    ) -> ExecutiveControlAgenda:
        """
        Create an initial empty agenda.
        
        Args:
            agenda_id: Unique identifier for this agenda
            program_id: ID of the owning program
            
        Returns:
            New agenda with empty collections
        """
        return cls(
            agenda_id=agenda_id,
            program_id=program_id,
        )
    
    def add_objective(self, objective_id: str, priority: int = 50) -> ExecutiveControlAgenda:
        """
        Add an objective to the agenda.
        
        Args:
            objective_id: ID of the objective to add
            priority: Priority level for this objective
            
        Returns:
            New agenda with the objective added (if capacity allows)
        """
        if len(self.objective_ids) >= self.max_objectives:
            return self  # At capacity
        
        # Insert in priority order
        new_ids = list(self.objective_ids)
        insert_pos = 0
        for i, existing_id in enumerate(new_ids):
            # For simplicity, just append for now
            pass
        new_ids.append(objective_id)
        
        return dataclass_replace(
            self,
            objective_ids=tuple(new_ids),
            last_modified_at_utc=0.0,  # Would need actual timestamp in real use
            revision=self.revision + 1,
        )
    
    def remove_objective(self, objective_id: str) -> ExecutiveControlAgenda:
        """
        Remove an objective from the agenda.
        
        Args:
            objective_id: ID of the objective to remove
            
        Returns:
            New agenda with the objective removed (if present)
        """
        if objective_id not in self.objective_ids:
            return self  # Not found
        
        new_ids = tuple(id for id in self.objective_ids if id != objective_id)
        return dataclass_replace(
            self,
            objective_ids=new_ids,
            last_modified_at_utc=0.0,  # Would need actual timestamp
            revision=self.revision + 1,
        )
    
    def set_active_objective(self, objective_id: str) -> ExecutiveControlAgenda:
        """
        Set the active objective.
        
        Args:
            objective_id: ID of the objective to activate
            
        Returns:
            New agenda with updated active objective
        """
        if objective_id not in self.objective_ids:
            return self  # Not found
        
        return dataclass_replace(
            self,
            active_objective_id=objective_id,
            last_modified_at_utc=0.0,  # Would need actual timestamp
            revision=self.revision + 1,
        )
    
    def mark_completed(self, objective_id: str) -> ExecutiveControlAgenda:
        """
        Mark an objective as completed.
        
        Args:
            objective_id: ID of the completed objective
            
        Returns:
            New agenda with updated state
        """
        if objective_id not in self.objective_ids:
            return self  # Not found
        
        new_completed = self.completed_objective_ids + (objective_id,)
        new_pending = tuple(
            id for id in self.pending_objective_ids
            if id != objective_id
        )
        
        return dataclass_replace(
            self,
            completed_objective_ids=new_completed,
            pending_objective_ids=new_pending,
            active_objective_id=None,
            last_modified_at_utc=0.0,  # Would need actual timestamp
            revision=self.revision + 1,
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
    "ExecutiveControlObjective",
    "ExecutiveControlAgenda",
)