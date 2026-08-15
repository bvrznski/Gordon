# Executive Goal Bindings
# ========================

"""
Executive Goal Binding - Immutable dataclass describing how goals are bound to programs.

A goal binding represents a goal reference along with metadata about its relationship
to the owning program, including activation state, ownership, priority, and satisfaction criteria.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveGoalBinding:
    """
    Binding that associates a goal with an ExecutiveProgram, along with metadata.
    
    A goal binding contains:
        - Goal reference: The goal being bound (reference only, not content)
        - Activation state: Whether the goal is currently active
        - Ownership: Which program owns this binding
        - Priority: Relative importance within the program
        - Dependency: Dependencies on other goals
        - Satisfaction criteria: How success is determined
        - Confidence: How well the goal is formed
        - Provenance: Where this binding came from
    
    Goal bindings are owned by ExecutiveProgram instances and never exist independently.
    """
    
    # Identity and ownership
    binding_id: str = "exec_goal_binding_initial"
    """Unique identifier for this binding."""
    
    program_id: str = "exec_program_initial"
    """ID of the program that owns this binding."""
    
    goal_reference_id: str = "exec_goal_ref_initial"
    """Reference to the actual goal (owned by Goal Network, referenced here)."""
    
    # Activation state
    is_active: bool = False
    """Whether this goal is currently being pursued."""
    
    activation_time_utc: float = 0.0
    """When this goal became active (seconds since epoch)."""
    
    deactivation_time_utc: Optional[float] = None
    """When this goal was deactivated, if applicable."""
    
    # Priority and ordering
    priority: int = 50
    """Priority level within the program (higher = more urgent)."""
    
    order: int = 0
    """Position in ordered goal list."""
    
    # Dependencies - other goals that must be satisfied first
    dependency_goal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of goals that must be completed before this one can proceed."""
    
    # Satisfaction criteria
    satisfaction_criteria_met: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of satisfied satisfaction criteria."""
    
    satisfaction_percentage: float = 0.0
    """Progress toward satisfaction (0.0 to 1.0)."""
    
    # Confidence and quality
    confidence_class: str = "unknown"
    """Confidence in goal formation ('low', 'medium', 'high', 'certain')."""
    
    consistency_class: str = "valid"
    """Consistency classification."""
    
    completeness_class: str = "partial"
    """Completeness classification."""
    
    # Provenance
    created_by: str = "executive_network"
    """Who/what created this binding."""
    
    created_at_utc: float = 0.0
    """When binding was created (seconds since epoch)."""
    
    source_ref_id: Optional[str] = None
    """Reference to source that triggered goal (e.g., user request, system event)."""
    
    @classmethod
    def initial(
        cls,
        binding_id: str = "exec_goal_binding_initial",
        program_id: str = "exec_program_initial",
        goal_reference_id: str = "exec_goal_ref_initial",
    ) -> ExecutiveGoalBinding:
        """
        Create an initial goal binding.
        
        Args:
            binding_id: Unique identifier for this binding
            program_id: ID of the owning program
            goal_reference_id: Reference to the goal
            
        Returns:
            New inactive goal binding with default values
        """
        return cls(
            binding_id=binding_id,
            program_id=program_id,
            goal_reference_id=goal_reference_id,
            is_active=False,
            priority=50,
            order=0,
            confidence_class="unknown",
            completeness_class="partial",
        )
    
    def activate(self, at_utc: float) -> ExecutiveGoalBinding:
        """
        Create a new binding with the goal activated.
        
        Args:
            at_utc: Activation timestamp
            
        Returns:
            New binding with is_active=True and activation_time_utc set
        """
        return dataclass_replace(
            self,
            is_active=True,
            activation_time_utc=at_utc,
            deactivation_time_utc=None,
        )
    
    def deactivate(self, at_utc: float) -> ExecutiveGoalBinding:
        """
        Create a new binding with the goal deactivated.
        
        Args:
            at_utc: Deactivation timestamp
            
        Returns:
            New binding with is_active=False and deactivation_time_utc set
        """
        return dataclass_replace(
            self,
            is_active=False,
            deactivation_time_utc=at_utc,
        )
    
    def advance_satisfaction(self, criteria_id: str) -> ExecutiveGoalBinding:
        """
        Mark a satisfaction criterion as met.
        
        Args:
            criteria_id: ID of the satisfied criterion
            
        Returns:
            New binding with the criterion added to satisfied list
        """
        if criteria_id in self.satisfaction_criteria_met:
            return self  # Already satisfied
        return dataclass_replace(
            self,
            satisfaction_criteria_met=self.satisfaction_criteria_met + (criteria_id,),
            satisfaction_percentage=len(self.satisfaction_criteria_met) / max(
                len(self.satisfaction_criteria_met) + 1, 1
            ),
        )
    
    def update_priority(self, new_priority: int) -> ExecutiveGoalBinding:
        """
        Create a new binding with updated priority.
        
        Args:
            new_priority: New priority level
            
        Returns:
            New binding with updated priority
        """
        return dataclass_replace(self, priority=new_priority)


@dataclass(frozen=True)
class ExecutiveCommitmentBinding:
    """
    Binding that associates a commitment with an ExecutiveProgram.
    
    A commitment represents an obligation - something the program commits to achieving.
    Unlike goals which may be abandoned, commitments are binding and require explicit
    abandonment via authority decision.
    
    Commitment bindings contain:
        - Commitment reference: The actual commitment (external ownership)
        - Authority that established this commitment
        - Activation state
        - Expiration conditions
        - Interruption policy for this commitment
        - Resumption policy
        - Provenance information
    """
    
    # Identity and ownership
    binding_id: str = "exec_commitment_binding_initial"
    """Unique identifier for this binding."""
    
    program_id: str = "exec_program_initial"
    """ID of the program that owns this binding."""
    
    commitment_reference_id: str = "exec_commitment_ref_initial"
    """Reference to the actual commitment (owned by Commitment Network, referenced here)."""
    
    # Authority
    authority_id: Optional[str] = None
    """ID of authority that established this commitment."""
    
    granted_at_utc: float = 0.0
    """When authority was granted (seconds since epoch)."""
    
    # Activation state
    is_active: bool = False
    """Whether this commitment is currently binding."""
    
    activation_time_utc: float = 0.0
    """When commitment became active."""
    
    deactivation_time_utc: Optional[float] = None
    """When commitment was deactivated, if applicable."""
    
    # Expiration
    expires_at_utc: Optional[float] = None
    """When this commitment expires (if ever)."""
    
    expiration_reason: Optional[str] = None
    """Reason for expiration if expired."""
    
    # Interruption policy - can this commitment be interrupted?
    interruption_policy_id: str = "interruptible"
    """ID of interruption policy ('non-interruptible', 'preemptive', etc.)."""
    
    interruptable_by_priority_above: Optional[int] = None
    """Interrupt only if new priority is above this value."""
    
    # Resumption policy - how to resume after interruption?
    resumption_policy_id: str = "resume-from-suspension"
    """ID of resumption policy ('restart', 'resume-from-suspension', etc.)."""
    
    # Provenance
    created_by: str = "executive_network"
    """Who/what created this binding."""
    
    created_at_utc: float = 0.0
    """When binding was created (seconds since epoch)."""
    
    @classmethod
    def initial(
        cls,
        binding_id: str = "exec_commitment_binding_initial",
        program_id: str = "exec_program_initial",
        commitment_reference_id: str = "exec_commitment_ref_initial",
    ) -> ExecutiveCommitmentBinding:
        """
        Create an initial commitment binding.
        
        Args:
            binding_id: Unique identifier for this binding
            program_id: ID of the owning program
            commitment_reference_id: Reference to the commitment
            
        Returns:
            New inactive commitment binding with default values
        """
        return cls(
            binding_id=binding_id,
            program_id=program_id,
            commitment_reference_id=commitment_reference_id,
            is_active=False,
            interruption_policy_id="interruptible",
        )
    
    def activate(self, at_utc: float) -> ExecutiveCommitmentBinding:
        """Create a new binding with the commitment activated."""
        return dataclass_replace(
            self,
            is_active=True,
            activation_time_utc=at_utc,
            deactivation_time_utc=None,
        )
    
    def deactivate(self, at_utc: float) -> ExecutiveCommitmentBinding:
        """Create a new binding with the commitment deactivated."""
        return dataclass_replace(
            self,
            is_active=False,
            deactivation_time_utc=at_utc,
        )
    
    def expire(self, reason: str, at_utc: float) -> ExecutiveCommitmentBinding:
        """
        Create a new binding marking this commitment as expired.
        
        Args:
            reason: Reason for expiration
            at_utc: Expiration timestamp
            
        Returns:
            New binding with expiration set
        """
        return dataclass_replace(
            self,
            expires_at_utc=at_utc,
            expiration_reason=reason,
            is_active=False,
            deactivation_time_utc=at_utc,
        )
    
    def make_non_interruptible(self) -> ExecutiveCommitmentBinding:
        """Create a new binding with non-interruptible policy."""
        return dataclass_replace(
            self,
            interruption_policy_id="non-interruptible",
            interruptable_by_priority_above=None,
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def dataclass_replace(instance: object, **kwargs) -> object:
    """
    Helper to replace fields in an immutable dataclass instance.
    
    This is a simple implementation for when we can't use the built-in
    dataclasses.replace due to compatibility concerns.
    
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
    "ExecutiveGoalBinding",
    "ExecutiveCommitmentBinding",
)