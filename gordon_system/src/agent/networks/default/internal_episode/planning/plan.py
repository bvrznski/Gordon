# Internal Episode Plan Model
# ==========================

"""
Plan model for internal episode coordination.

A plan describes what coordination steps are expected without defining how
capabilities implement cognition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


InternalEpisodePlanId = str
"""Unique identifier for an episode plan."""


@dataclass(frozen=True, slots=True)
class InternalEpisodePlan:
    """
    Immutable bounded coordination plan for an internal episode.
    
    The plan describes which coordination steps are expected but does NOT define
    how a capability implements cognition. It's declarative, not procedural.
    
    PROPERTIES:
        • plan_id: Unique identifier
        • episode_id: Which episode this plan coordinates
        • step_definitions: Ordered list of steps to perform
        • dependency_relations: How steps depend on each other
        • optional_step_groups: Steps that may be skipped
        • completion_rules: Conditions for successful completion
        
    BOUNDEDNESS:
        • maximum_steps: Hard limit on number of steps
        • maximum_dependencies: Hard limit on dependencies per step
        • revision: Monotonically increasing revision
        
    NOT RESPONSIBLE FOR:
        • Executing the steps
        • Allocating runtime resources
        • Deciding which capability to use
    """
    
    # Identity
    plan_id: InternalEpisodePlanId
    """Unique identifier for this plan."""
    
    episode_id: str
    """ID of the episode this plan coordinates."""
    
    revision: int = 1
    """Revision number (increases when plan changes)."""
    
    # Plan content
    step_definitions: Tuple[InternalEpisodeStep, ...] = field(default_factory=tuple)
    """Ordered list of coordination steps."""
    
    dependency_relations: Tuple[InternalEpisodeDependency, ...] = field(default_factory=tuple)
    """How steps depend on each other."""
    
    optional_step_groups: Tuple[Tuple[str, ...], ...] = field(default_factory=tuple)
    """Groups of optional steps (at least one must complete)."""
    
    # Completion rules
    maximum_steps: int = 50
    """Maximum number of steps allowed."""
    
    minimum_completion_ratio: float = 1.0
    """Minimum ratio of completed steps required (0.0 to 1.0)."""
    
    @classmethod
    def create(
        cls,
        plan_id: str,
        episode_id: str,
        step_definitions: Tuple[InternalEpisodeStep, ...],
        dependencies: Optional[Tuple[InternalEpisodeDependency, ...]] = None,
    ) -> InternalEpisodePlan:
        """
        Create a new episode plan.
        
        Args:
            plan_id: Unique identifier for this plan
            episode_id: ID of the episode this plan coordinates
            step_definitions: Ordered list of coordination steps
            dependencies: How steps depend on each other (optional)
            
        Returns:
            New InternalEpisodePlan instance
            
        Raises:
            ValueError: If too many steps or invalid dependencies
        """
        if len(step_definitions) > 50:
            raise ValueError("Plan exceeds maximum step count (50)")
        
        return cls(
            plan_id=plan_id,
            episode_id=episode_id,
            revision=1,
            step_definitions=step_definitions,
            dependency_relations=dependencies or (),
        )
    
    def get_step_by_id(self, step_id: str) -> Optional[InternalEpisodeStep]:
        """Get a step definition by its ID."""
        for step in self.step_definitions:
            if step.step_id == step_id:
                return step
        return None
    
    def get_dependencies_for_step(self, step_id: str) -> Tuple[str, ...]:
        """Get IDs of steps that must complete before the given step."""
        result = []
        for dep in self.dependency_relations:
            if dep.target_step_id == step_id and dep.kind in {"requires", "blocks"}:
                result.append(dep.source_step_id)
        return tuple(result)


@dataclass(frozen=True, slots=True)
class InternalEpisodeStepId:
    """Unique identifier for an episode plan step."""
    
    value: str


@dataclass(frozen=True, slots=True)
class InternalEpisodeStep:
    """
    Single coordination step in a plan.
    
    Each step defines what the DefaultNetwork should coordinate, not how
    it's implemented by capabilities.
    """
    
    # Identity
    step_id: InternalEpisodeStepId
    """Unique identifier for this step."""
    
    kind: str  # InternalEpisodeStepKind.*
    """Type of coordination activity."""
    
    # Inputs and outputs
    input_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to inputs needed (evidence IDs, context refs)."""
    
    expected_output_contract: Optional[str] = None
    """Description of expected output (schema reference or constraint)."""
    
    # Dependencies
    depends_on_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Step IDs that must complete before this one."""
    
    may_parallelize_with_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Step IDs that can run concurrently with this one."""
    
    # Metadata
    optional: bool = False
    """Whether this step is optional."""
    
    retry_safe: str = "unknown"  # RetrySafety.*
    """ Whether it's safe to retry if failed."""
    
    side_effects_classified: bool = False
    """Whether side effects have been classified."""
    
    completion_condition: Optional[str] = None
    """Condition that must be true for step to complete."""
    
    provenance: Optional[str] = None
    """Provenance reference (where this step type is documented)."""