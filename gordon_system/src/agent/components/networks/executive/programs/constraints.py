# Executive Constraint Set
# =========================

"""
Executive Constraint Set - Immutable dataclass describing constraints on executive programs.

Constraints define what must be satisfied for a program to operate correctly.
They represent boundaries that the program's behavior must respect.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveConstraintSet:
    """
    Collection of constraints that must be satisfied for an ExecutiveProgram.
    
    Constraints define bounded limits on program operation:
        - Policy constraints: Rules about what may/may not be done
        - Safety constraints: Limits to prevent harmful behavior
        - Resource constraints: Budgets and capacity limits
        - Temporal constraints: Time bounds for completion
        - User constraints: Preferences and restrictions from users
        - Execution constraints: Requirements for valid execution
        - Workspace constraints: Bounds on workspace usage
        - Attention constraints: Limits on attention allocation
        - Memory constraints: Bounds on memory consumption
    
    Constraint properties:
        - Immutable: No in-place modification
        - Bounded: All have capacity limits
        - Reference-based: Constraints reference external constraint definitions,
          not contain them directly
    """
    
    # Identity and revisioning
    constraint_set_id: str = "exec_constraints_initial"
    """Unique identifier for this constraint set."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Policy constraints - rules about behavior
    policy_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of policy constraints (e.g., 'must-not-override-user', 'must-log-actions')."""
    
    max_policy_constraints: int = 50
    """Maximum policy constraints allowed."""
    
    # Safety constraints - prevent harmful behavior
    safety_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of safety constraints (e.g., 'cannot-exceed-resource-budget', 'must-fail-safe')."""
    
    max_safety_constraints: int = 30
    """Maximum safety constraints allowed."""
    
    # Resource constraints - budget and capacity limits
    resource_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of resource constraints (e.g., 'max-execution-time', 'max-memory-usage')."""
    
    max_resource_constraints: int = 40
    """Maximum resource constraints allowed."""
    
    # Temporal constraints - time bounds
    temporal_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of temporal constraints (e.g., 'must-complete-in-1hour', 'deadline:2025-01-01')."""
    
    max_temporal_constraints: int = 20
    """Maximum temporal constraints allowed."""
    
    # User constraints - user preferences and restrictions
    user_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of user constraints (e.g., 'must-not-disturb', 'priority:high')."""
    
    max_user_constraints: int = 30
    """Maximum user constraints allowed."""
    
    # Execution constraints - valid execution requirements
    execution_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of execution constraints (e.g., 'must-use-authoritative-data', 'must-validate-inputs')."""
    
    max_execution_constraints: int = 30
    """Maximum execution constraints allowed."""
    
    # Workspace constraints - workspace usage bounds
    workspace_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of workspace constraints (e.g., 'max-workspace-entries', 'workspace-isolation')."""
    
    max_workspace_constraints: int = 20
    """Maximum workspace constraints allowed."""
    
    # Attention constraints - focus allocation limits
    attention_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of attention constraints (e.g., 'max-concurrent-tasks', 'attention-budget')."""
    
    max_attention_constraints: int = 15
    """Maximum attention constraints allowed."""
    
    # Memory constraints - memory usage bounds
    memory_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of memory constraints (e.g., 'max-memory-references', 'memory-retention-period')."""
    
    max_memory_constraints: int = 25
    """Maximum memory constraints allowed."""
    
    # Planning constraints - planning requirements
    planning_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of planning constraints (e.g., 'must-plan-ahead', 'plan-verification-required')."""
    
    max_planning_constraints: int = 20
    """Maximum planning constraints allowed."""
    
    # Reasoning constraints - reasoning requirements
    reasoning_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of reasoning constraints (e.g., 'must-validate-assumptions', 'reasoning-trace-required')."""
    
    max_reasoning_constraints: int = 20
    """Maximum reasoning constraints allowed."""
    
    # Violation tracking
    constraint_violations: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of violated constraints (empty if all satisfied)."""
    
    violation_count: int = 0
    """Number of constraint violations."""
    
    @classmethod
    def initial(cls) -> ExecutiveConstraintSet:
        """
        Create an initial empty constraint set.
        
        Returns:
            New constraint set with empty collections
        """
        return cls()
    
    def add_policy_constraint(self, constraint_id: str) -> ExecutiveConstraintSet:
        """Add a policy constraint if capacity allows."""
        if len(self.policy_constraints) >= self.max_policy_constraints:
            return self  # At capacity
        return dataclass_replace(
            self,
            policy_constraints=self.policy_constraints + (constraint_id,),
        )
    
    def add_safety_constraint(self, constraint_id: str) -> ExecutiveConstraintSet:
        """Add a safety constraint if capacity allows."""
        if len(self.safety_constraints) >= self.max_safety_constraints:
            return self  # At capacity
        return dataclass_replace(
            self,
            safety_constraints=self.safety_constraints + (constraint_id,),
        )
    
    def has_violations(self) -> bool:
        """Check if any constraints are violated."""
        return self.violation_count > 0
    
    def get_violated_constraint_ids(self) -> Tuple[str, ...]:
        """Get IDs of all violated constraints."""
        return self.constraint_violations


@dataclass(frozen=True)
class ExecutiveControlPolicy:
    """
    Semantic policy for how executive organization should proceed.
    
    A control policy is NOT:
        - Implementation logic or algorithms
        - Runtime execution behavior
        - Action selection mechanism
    
    A control policy IS:
        - A semantic description of organizational rules
        - Immutable data describing HOW to organize cognition
        - Applied BY ExecutiveProgram instances
    
    Policy examples:
        - Priority-based activation: Higher priority programs get resources first
        - Fair-share scheduling: Resources distributed evenly among active programs
        - Preemptive interruption: High-priority programs can interrupt lower ones
        - Non-interruptible: Once started, must complete or fail naturally
        - Timeout-based: Programs automatically interrupted after time limit
    
    Policy properties:
        - Immutable: No in-place modification
        - Bounded: Limited number of rules
        - Deterministic: Same inputs produce same outputs
    """
    
    # Identity and revisioning
    policy_id: str = "exec_policy_initial"
    """Unique identifier for this control policy."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Policy kind - determines behavior type
    policy_kind: str = "priority-based"
    """
    Kind of policy ('priority-based', 'fair-share', 'preemptive',
                   'non-interruptible', 'timeout-based').
    """
    
    # Activation rules
    activation_priority_threshold: int = 0
    """Minimum priority to be activated."""
    
    max_concurrent_programs: int = 10
    """Maximum programs that can be active simultaneously."""
    
    # Scheduling rules
    scheduling_kind: str = "round-robin"
    """Scheduling algorithm ('round-robin', 'priority-first', 'fifo')."""
    
    time_slice_seconds: float = 60.0
    """Time slice for round-robin scheduling."""
    
    # Interruption rules
    interruptible: bool = True
    """Whether programs following this policy can be interrupted."""
    
    max_interrupt_priority_diff: int = 25
    """Max priority difference required to interrupt."""
    
    # Resource allocation
    default_resource_budget: float = 1.0
    """Default resource allocation (0.0 to 1.0)."""
    
    max_resource_increase: float = 0.5
    """Maximum resource increase per request."""
    
    # Timeout rules
    default_timeout_seconds: float = 3600.0
    """Default timeout for programs following this policy."""
    
    allow_timeout_extension: bool = False
    """Whether timeouts can be extended."""
    
    max_extensions: int = 3
    """Maximum timeout extensions allowed."""
    
    # Priority rules
    priority_increment: int = 10
    """Amount to increment priority when rescheduling."""
    
    priority_decrement: int = 5
    """Amount to decrement priority after timeout."""
    
    @classmethod
    def initial(cls) -> ExecutiveControlPolicy:
        """
        Create an initial control policy.
        
        Returns:
            New policy with default values
        """
        return cls(
            policy_id="exec_policy_initial",
            policy_kind="priority-based",
        )
    
    def is_interrupt_allowed(self, interrupting_priority: int, target_priority: int) -> bool:
        """
        Check if an interruption from one priority to another is allowed.
        
        Args:
            interrupting_priority: Priority of the program wanting to interrupt
            target_priority: Priority of the current active program
            
        Returns:
            True if interruption is allowed by this policy
        """
        if not self.interruptible:
            return False
        
        priority_diff = interrupting_priority - target_priority
        return priority_diff > self.max_interrupt_priority_diff


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
    "ExecutiveConstraintSet",
    "ExecutiveControlPolicy",
)