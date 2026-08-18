# Strategic Objective Set - Phase 7.18
# =====================================

"""
Canonical Objective Set for Phase 7.18.

An ObjectiveSet defines long-term objectives, constraints, dependencies,
priorities, and success criteria for strategic reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ObjectivePriority(Enum):
    """Objective priority levels."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ObjectiveConstraintType(Enum):
    """Types of objective constraints."""
    
    RESOURCE = "resource"
    TIME = "time"
    DEPENDENCY = "dependency"
    POLICY = "policy"
    ETHICAL = "ethical"


@dataclass(frozen=True)
class Objective:
    """
    A strategic objective describing a desired future state.
    
    Objectives include:
        - Explicit identity
        - Clear intent statement
        - Priority level
        - Constraints and dependencies
        - Success criteria
        - Provenance tracking
    """
    
    # Identity
    objective_id: str                       # Unique objective identifier
    
    # Objective statement
    intent: str                             # What do we want to achieve?
    
    # Priority
    priority: ObjectivePriority = ObjectivePriority.MEDIUM
    
    # Constraints and dependencies
    constraints: List[str] = field(default_factory=list)   # Hard constraints
    dependencies: List[str] = field(default_factory=list)  # Dependent objectives
    
    # Success criteria
    success_criteria: str = ""              # How do we know it's achieved?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_context: str = "unknown"         # Where did this objective come from?


@dataclass(frozen=True)
class ObjectiveSet:
    """
    A set of objectives for strategic reasoning.
    
    An ObjectiveSet defines:
        - Long-term objectives
        - Constraints (global and per-objective)
        - Dependencies between objectives
        - Priorities for resolution
        - Success criteria for evaluation
    
    ObjectiveSets remain immutable during strategy formation to ensure
    deterministic reasoning outcomes.
    """
    
    # Identity
    objective_set_id: str                   # Unique set identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Participating objectives
    objectives: List[Objective]
    
    # Strategic scope
    strategic_scope: str = "global"         # e.g., "mission", "domain", "task"
    
    # Global constraints
    global_constraints: List[str] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_context: str = "unknown"
    
    @property
    def objective_count(self) -> int:
        """Return the number of objectives in this set."""
        return len(self.objectives)
    
    @property
    def critical_objectives(self) -> List[Objective]:
        """Return objectives with CRITICAL priority."""
        return [o for o in self.objectives if o.priority == ObjectivePriority.CRITICAL]
    
    @property
    def high_priority_objectives(self) -> List[Objective]:
        """Return objectives with HIGH or higher priority."""
        return [o for o in self.objectives 
                if o.priority in (ObjectivePriority.HIGH, ObjectivePriority.CRITICAL)]
    
    @property
    def has_constraints(self) -> bool:
        """Check if this set has any constraints defined."""
        return bool(self.global_constraints or any(o.constraints for o in self.objectives))
    
    def get_objective_by_id(self, objective_id: str) -> Optional[Objective]:
        """Find an objective by its ID."""
        for obj in self.objectives:
            if obj.objective_id == objective_id:
                return obj
        return None
    
    def find_conflicts(self) -> List[Tuple[Objective, Objective, str]]:
        """
        Find potential conflicts between objectives.
        
        Returns a list of (objective1, objective2, conflict_reason) tuples.
        """
        conflicts = []
        
        for i, obj1 in enumerate(self.objectives):
            for obj2 in self.objectives[i + 1:]:
                # Check for conflicting dependencies
                if obj1.objective_id in obj2.dependencies and obj2.objective_id in obj1.dependencies:
                    conflicts.append((obj1, obj2, "mutual_dependency"))
                
                # Check for resource constraints (simplified)
                shared_resources = set(obj1.constraints) & set(obj2.constraints)
                if shared_resources:
                    conflicts.append((obj1, obj2, f"shared_resource:{','.join(shared_resources)}"))
        
        return conflicts
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        objectives: List[Objective],
        strategic_scope: str = "global",
        source_context: str = "unknown",
    ) -> ObjectiveSet:
        """Create a new objective set."""
        return cls(
            objective_set_id=f"objective_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            objectives=list(objectives),
            strategic_scope=strategic_scope,
            source_context=source_context,
            created_at_utc=time.time(),
        )


@dataclass(frozen=True)
class ObjectivePrioritization:
    """
    Result of objective prioritization.
    
    This records the outcome of ordering objectives by priority, including
    the rationale for ordering and any conflicts resolved.
    """
    
    # Identity
    prioritization_id: str
    
    # Input
    objective_set_id: str
    
    # Prioritized order (by index into original objectives list)
    prioritized_order: List[int]
    
    # Rationale for ordering
    priority_rationale: Dict[int, str]  # objective_index -> explanation
    
    # Conflicts resolved
    conflicts_resolved: List[str] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


__all__ = [
    "Objective",
    "ObjectiveSet",
    "ObjectivePrioritization",
    "ObjectivePriority",
    "ObjectiveConstraintType",
]