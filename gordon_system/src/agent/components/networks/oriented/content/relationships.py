# Oriented Network Relationship Content Types - Phase 4.7.3
# =========================================================

"""
Relationship content types for the Oriented Network.

Relationship Content represents explicit semantic relationships between
content objects without runtime coupling.

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-019: Every relationship shall be explicit
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from enum import Enum

from gordon_system.src.agent.components.networks.oriented.content.base import (
    BaseContent,
    ContentIdentity,
)


# =============================================================================
# RELATIONSHIP TYPE ENUMERATIONS
# =============================================================================

class RelationshipType(Enum):
    """
    Canonical relationship types for Oriented Network content.
    """
    
    GOAL = "goal"
    OBJECTIVE = "objective"
    TASK = "task"
    DEPENDENCY = "dependency"
    CONSTRAINT = "constraint"
    CONTEXT = "context"
    ORIENTATION = "orientation"


# =============================================================================
# RELATIONSHIP CONTENT TYPES
# =============================================================================

@dataclass(frozen=True)
class GoalRelationship(BaseContent):
    """
    A semantic relationship involving a goal.
    
    SEMANTIC ROLE:
        - Describes semantic connection to a goal
        - Never couples at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (relationship description only)
        - References: Related entities
    """
    
    relationship_type: RelationshipType = field(default=RelationshipType.GOAL, init=False)
    target_goal_id: ContentIdentity = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, target_goal_id: ContentIdentity) -> GoalRelationship:
        return cls(identity=identity, target_goal_id=target_goal_id)


@dataclass(frozen=True)
class ObjectiveRelationship(BaseContent):
    """
    A semantic relationship involving an objective.
    
    SEMANTIC ROLE:
        - Describes semantic connection to an objective
        - Never couples at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (relationship description only)
        - References: Related entities
    """
    
    relationship_type: RelationshipType = field(default=RelationshipType.OBJECTIVE, init=False)
    target_objective_id: ContentIdentity = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, target_objective_id: ContentIdentity) -> ObjectiveRelationship:
        return cls(identity=identity, target_objective_id=target_objective_id)


@dataclass(frozen=True)
class TaskRelationship(BaseContent):
    """
    A semantic relationship involving a task.
    
    SEMANTIC ROLE:
        - Describes semantic connection to a task
        - Never couples at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (relationship description only)
        - References: Related entities
    """
    
    relationship_type: RelationshipType = field(default=RelationshipType.TASK, init=False)
    target_task_id: ContentIdentity = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, target_task_id: ContentIdentity) -> TaskRelationship:
        return cls(identity=identity, target_task_id=target_task_id)


@dataclass(frozen=True)
class DependencyRelationship(BaseContent):
    """
    A semantic dependency relationship.
    
    SEMANTIC ROLE:
        - Describes semantic dependency
        - Never couples at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (relationship description only)
        - References: Dependent entities
    """
    
    relationship_type: RelationshipType = field(default=RelationshipType.DEPENDENCY, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> DependencyRelationship:
        return cls(identity=identity)


@dataclass(frozen=True)
class ConstraintRelationship(BaseContent):
    """
    A semantic constraint relationship.
    
    SEMANTIC ROLE:
        - Describes semantic constraint influence
        - Never couples at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (relationship description only)
        - References: Affected entities
    """
    
    relationship_type: RelationshipType = field(default=RelationshipType.CONSTRAINT, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> ConstraintRelationship:
        return cls(identity=identity)


@dataclass(frozen=True)
class ContextRelationship(BaseContent):
    """
    A semantic context relationship.
    
    SEMANTIC ROLE:
        - Describes semantic context connection
        - Never couples at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (relationship description only)
        - References: Related contexts
    """
    
    relationship_type: RelationshipType = field(default=RelationshipType.CONTEXT, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> ContextRelationship:
        return cls(identity=identity)


@dataclass(frozen=True)
class OrientationRelationship(BaseContent):
    """
    A semantic orientation relationship.
    
    SEMANTIC ROLE:
        - Describes semantic orientation connection
        - Never couples at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (relationship description only)
        - References: Related orientations
    """
    
    relationship_type: RelationshipType = field(default=RelationshipType.ORIENTATION, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> OrientationRelationship:
        return cls(identity=identity)


__all__ = [
    "RelationshipType",
    # Specific relationship types
    "GoalRelationship",
    "ObjectiveRelationship",
    "TaskRelationship",
    "DependencyRelationship",
    "ConstraintRelationship",
    "ContextRelationship",
    "OrientationRelationship",
]