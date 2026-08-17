# Counterfactual Descriptor - Phase 7.6
# =====================================

"""
Canonical Counterfactual Descriptor.

A descriptor exposes counterfactual reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class CounterfactualMode(Enum):
    """Modes of counterfactual reasoning."""
    
    RETROSPECTIVE = "retrospective"      # What would have happened if the past had been different?
    PROSPECTIVE = "prospective"          # What may happen if this action is taken?
    NORMATIVE = "normative"              # What would the world look like if constraints/policies/goals were changed?
    DIAGNOSTIC = "diagnostic"            # Identify failure modes through intervention analysis
    EXPLANATORY = "explanatory"          # Explain observed outcomes through alternative scenarios


class CounterfactualLifecycle(Enum):
    """Counterfactual session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    WORLD_SET_PREPARATION = "world_set_preparation"
    INTERVENTION_SELECTION = "intervention_selection"
    BRANCHING = "branching"
    PROPAGATING = "propagating"
    COMPARING = "comparing"
    VALIDATING = "validating"
    GOVERNANCE_REVIEW = "governance_review"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class CounterfactualDescriptor:
    """
    Descriptor exposing counterfactual reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning mode and goal
        - Lifecycle state
        - Constraints and configuration
        - Provenance tracking
    
    Descriptors allow inspection of what counterfactual reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning classification
    counterfactual_mode: CounterfactualMode   # What kind of counterfactual reasoning?
    reasoning_goal: str                       # What are we trying to evaluate?
    
    # Lifecycle state
    lifecycle_state: CounterfactualLifecycle = CounterfactualLifecycle.CREATED
    
    # Constraints and requirements
    confidence_threshold: float = 0.5         # Minimum confidence for accepting alternative world
    max_alternative_worlds: int = 10          # Maximum alternative worlds to generate
    temporal_scope: Tuple[float, float] = (0.0, float('inf'))  # Time range for evaluation
    intervention_count_limit: int = 5         # Maximum interventions per session
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did counterfactual reasoning originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if counterfactual reasoning completed."""
        return self.lifecycle_state == CounterfactualLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if counterfactual reasoning failed."""
        return self.lifecycle_state == CounterfactualLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        counterfactual_mode: CounterfactualMode = CounterfactualMode.RETROSPECTIVE,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        confidence_threshold: float = 0.5,
    ) -> CounterfactualDescriptor:
        """Create a new counterfactual descriptor."""
        return cls(
            descriptor_id=f"counterfactual:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            counterfactual_mode=counterfactual_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: CounterfactualLifecycle) -> CounterfactualDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == CounterfactualLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class CounterfactualSessionIdentity:
    """
    Immutable identity for a counterfactual session.
    
    Allows replay and verification of counterfactual results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> CounterfactualSessionIdentity:
        """Create a new session identity."""
        return cls(
            semantic_identity=semantic_identity,
            session_number=session_number,
        )


@dataclass(frozen=True)
class WorldSetIdentity:
    """
    Immutable identity for a World Set.
    
    A World Set contains the reference world, alternative worlds, and branching structure
    for a counterfactual analysis session.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    world_set_number: int = 1                 # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, world_set_number: int = 1) -> WorldSetIdentity:
        """Create a new World Set identity."""
        return cls(
            semantic_identity=semantic_identity,
            world_set_number=world_set_number,
        )


@dataclass(frozen=True)
class BranchingStructure:
    """
    Structure of the branching tree for alternative worlds.
    
    Defines how reference world branches into alternative worlds through interventions.
    """
    
    # Root
    root_world: str                           # Reference world identifier
    
    # Branches
    branch_count: int = 0                     # Total number of branches generated
    max_depth: int = 1                        # Maximum branching depth
    
    # Intervention application points
    intervention_points: Tuple[str, ...] = () # World state identifiers where interventions applied
    
    @classmethod
    def create(cls, root_world: str) -> BranchingStructure:
        """Create a new branching structure."""
        return cls(
            root_world=root_world,
            branch_count=0,
            max_depth=1,
        )
    
    def with_branch(self, intervention_point: str, new_depth: int = 1) -> BranchingStructure:
        """Return a copy with an additional branch."""
        return dataclass_replace(
            self,
            branch_count=self.branch_count + 1,
            intervention_points=self.intervention_points + (intervention_point,),
            max_depth=max(self.max_depth, new_depth),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CounterfactualDescriptor",
    "CounterfactualSessionIdentity",
    "WorldSetIdentity",
    "BranchingStructure",
    "CounterfactualMode",
    "CounterfactualLifecycle",
]