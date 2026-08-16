# Oriented Network Reference Content Types - Phase 4.7.3
# =======================================================

"""
Canonical reference content types for the Oriented Network.

Reference Content represents semantic pointers to external cognitive concepts.
These references never own implementations - they only identify and reference.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Versionable and serializable

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-012: Orientation references cognitive artefacts.
        It never owns them.
    ORIENTED-CONTENT-LAW-013 through 018: Reference ownership constraints
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional
from enum import Enum

from gordon_system.src.agent.components.networks.oriented.content.base import (
    BaseContent,
    ContentIdentity,
    ContentRevision,
    ContentVersion,
    ContentAuthority,
    ContentOwner,
)


# =============================================================================
# REFERENCE TYPE ENUMERATIONS
# =============================================================================

class ReferenceType(Enum):
    """
    Canonical reference types for Oriented Network content.
    """
    
    # Primary references
    GOAL = "goal"
    OBJECTIVE = "objective"
    TASK = "task"
    MISSION = "mission"
    PURPOSE = "purpose"
    
    # Supporting references
    CONSTRAINT = "constraint"
    DEPENDENCY = "dependency"
    PLAN = "plan"
    DECISION = "decision"
    
    # System references
    WORKSPACE = "workspace"
    WORKING_MEMORY = "working_memory"
    STRATEGY = "strategy"
    REASONING = "reasoning"
    EVALUATION = "evaluation"


# =============================================================================
# REFERENCE CONTENT BASE CLASS
# =============================================================================

@dataclass(frozen=True)
class BaseReferenceContent(BaseContent):
    """
    Base class for all reference content types.
    
    Reference Content represents semantic pointers to external concepts.
    References never own implementations - they only identify and reference.
    """
    
    ref_type: ReferenceType = ReferenceType.GOAL
    """Type of the referenced concept"""
    
    ref_identity: Optional[ContentIdentity] = None
    """Identity of the referenced content (if known)"""
    
    @property
    def referenced_kind(self) -> str:
        """Return a string description of what this reference points to."""
        return self.ref_type.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "ref_type": self.ref_type.value,
            "ref_identity": self.ref_identity,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseReferenceContent:
        """Create instance from dictionary."""
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            ref_type=ReferenceType(data.get("ref_type", ReferenceType.GOAL.value)),
            ref_identity=data.get("ref_identity"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate reference content."""
        errors = []
        
        if not self.identity:
            errors.append("identity is required")
        
        if self.revision < 1:
            errors.append("revision must be >= 1")
        
        if self.version < 1:
            errors.append("version must be >= 1")
        
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        """Get provenance information."""
        return {
            "created_by": self.owner,
            "derived_from": None,
            "observed_from": None,
            "requested_by": None,
            "validated_by": self.authority.value,
            "approved_by": None,
        }
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        """Get lineage (ancestral chain)."""
        return tuple()


# =============================================================================
# REFERENCE CONTENT TYPES
# =============================================================================

@dataclass(frozen=True)
class GoalReference(BaseReferenceContent):
    """
    Reference to a Goal concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Goal
        - Never owns Goal implementation
        - Represents orientation toward a target
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Goal entity
        - Never owns: Goal implementations, runtime execution
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-CONTENT-LAW-012: Orientation references cognitive artefacts.
            It never owns them.
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.GOAL, init=False)
    goal_id: str = ""
    """Identifier for the referenced Goal"""
    
    priority: float = 0.5
    """Priority level (0.0-1.0) without runtime acquisition"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, goal_id: str) -> GoalReference:
        """Create a new GoalReference."""
        return cls(
            identity=identity,
            goal_id=goal_id,
        )


@dataclass(frozen=True)
class ObjectiveReference(BaseReferenceContent):
    """
    Reference to an Objective concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Objective
        - Never owns Objective implementation
        - Represents orientation toward an operational target
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Objective entity
        - Never owns: Objective implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.OBJECTIVE, init=False)
    objective_id: str = ""
    """Identifier for the referenced Objective"""
    
    contributes_to: Optional[ContentIdentity] = None
    """Goal that this objective contributes to (if known)"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, objective_id: str) -> ObjectiveReference:
        """Create a new ObjectiveReference."""
        return cls(
            identity=identity,
            objective_id=objective_id,
        )


@dataclass(frozen=True)
class TaskReference(BaseReferenceContent):
    """
    Reference to a Task concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Task
        - Never owns Task implementation
        - Represents orientation toward an executable action
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Task entity
        - Never owns: Task implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.TASK, init=False)
    task_id: str = ""
    """Identifier for the referenced Task"""
    
    derived_from: Optional[ContentIdentity] = None
    """Objective that this task derives from (if known)"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, task_id: str) -> TaskReference:
        """Create a new TaskReference."""
        return cls(
            identity=identity,
            task_id=task_id,
        )


@dataclass(frozen=True)
class MissionReference(BaseReferenceContent):
    """
    Reference to a Mission concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Mission
        - Never owns Mission implementation
        - Represents orientation toward a major objective
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Mission entity
        - Never owns: Mission implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.MISSION, init=False)
    mission_id: str = ""
    """Identifier for the referenced Mission"""
    
    contributes_to: Optional[ContentIdentity] = None
    """Purpose that this mission contributes to (if known)"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, mission_id: str) -> MissionReference:
        """Create a new MissionReference."""
        return cls(
            identity=identity,
            mission_id=mission_id,
        )


@dataclass(frozen=True)
class PurposeReference(BaseReferenceContent):
    """
    Reference to a Purpose concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Purpose
        - Never owns Purpose implementation
        - Represents orientation toward a final aim
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Purpose entity
        - Never owns: Purpose implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.PURPOSE, init=False)
    purpose_id: str = ""
    """Identifier for the referenced Purpose"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, purpose_id: str) -> PurposeReference:
        """Create a new PurposeReference."""
        return cls(
            identity=identity,
            purpose_id=purpose_id,
        )


@dataclass(frozen=True)
class ConstraintReference(BaseReferenceContent):
    """
    Reference to a Constraint concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Constraint
        - Never owns Constraint enforcement
        - Represents boundary conditions for orientation
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Constraint entity
        - Never owns: Constraint enforcement, runtime implementation
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.CONSTRAINT, init=False)
    constraint_id: str = ""
    """Identifier for the referenced Constraint"""
    
    affects_orientation: Tuple[ContentIdentity, ...] = field(default_factory=tuple)
    """Orientations affected by this constraint (if known)"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, constraint_id: str) -> ConstraintReference:
        """Create a new ConstraintReference."""
        return cls(
            identity=identity,
            constraint_id=constraint_id,
        )


@dataclass(frozen=True)
class DependencyReference(BaseReferenceContent):
    """
    Reference to a Dependency relationship.
    
    SEMANTIC ROLE:
        - Points to an external Dependency definition
        - Never owns dependency resolution logic
        - Represents semantic requirements
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Dependency entity
        - Never owns: Dependency resolution, runtime implementation
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.DEPENDENCY, init=False)
    dependency_id: str = ""
    """Identifier for the referenced Dependency"""
    
    required_by: Optional[ContentIdentity] = None
    """Entity that requires this dependency (if known)"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, dependency_id: str) -> DependencyReference:
        """Create a new DependencyReference."""
        return cls(
            identity=identity,
            dependency_id=dependency_id,
        )


@dataclass(frozen=True)
class PlanReference(BaseReferenceContent):
    """
    Reference to a Plan concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Plan
        - Never owns planning implementation
        - Represents temporal strategy
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Plan entity
        - Never owns: Planning implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.PLAN, init=False)
    plan_id: str = ""
    """Identifier for the referenced Plan"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, plan_id: str) -> PlanReference:
        """Create a new PlanReference."""
        return cls(
            identity=identity,
            plan_id=plan_id,
        )


@dataclass(frozen=True)
class DecisionReference(BaseReferenceContent):
    """
    Reference to a Decision concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Decision
        - Never owns decision implementation
        - Represents chosen course of action
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Decision entity
        - Never owns: Decision implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.DECISION, init=False)
    decision_id: str = ""
    """Identifier for the referenced Decision"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, decision_id: str) -> DecisionReference:
        """Create a new DecisionReference."""
        return cls(
            identity=identity,
            decision_id=decision_id,
        )


@dataclass(frozen=True)
class WorkspaceReference(BaseReferenceContent):
    """
    Reference to a Workspace concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Workspace
        - Never owns workspace implementation
        - Represents semantic projection context
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Workspace entity
        - Never owns: Workspace implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.WORKSPACE, init=False)
    workspace_id: str = ""
    """Identifier for the referenced Workspace"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, workspace_id: str) -> WorkspaceReference:
        """Create a new WorkspaceReference."""
        return cls(
            identity=identity,
            workspace_id=workspace_id,
        )


@dataclass(frozen=True)
class WorkingMemoryReference(BaseReferenceContent):
    """
    Reference to a Working Memory concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Working Memory
        - Never owns working memory implementation
        - Represents temporary cognitive state
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Working Memory entity
        - Never owns: Working Memory implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.WORKING_MEMORY, init=False)
    memory_id: str = ""
    """Identifier for the referenced Working Memory"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, memory_id: str) -> WorkingMemoryReference:
        """Create a new WorkingMemoryReference."""
        return cls(
            identity=identity,
            memory_id=memory_id,
        )


@dataclass(frozen=True)
class StrategyReference(BaseReferenceContent):
    """
    Reference to a Strategy concept.
    
    SEMANTIC ROLE:
        - Points to an externally owned Strategy
        - Never owns strategy implementation
        - Represents approach to achieving objectives
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Strategy entity
        - Never owns: Strategy implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.STRATEGY, init=False)
    strategy_id: str = ""
    """Identifier for the referenced Strategy"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, strategy_id: str) -> StrategyReference:
        """Create a new StrategyReference."""
        return cls(
            identity=identity,
            strategy_id=strategy_id,
        )


@dataclass(frozen=True)
class ReasoningReference(BaseReferenceContent):
    """
    Reference to a Reasoning process.
    
    SEMANTIC ROLE:
        - Points to an externally owned Reasoning process
        - Never owns reasoning implementation
        - Represents logical inference artifacts
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Reasoning entity
        - Never owns: Reasoning implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.REASONING, init=False)
    reasoning_id: str = ""
    """Identifier for the referenced Reasoning"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, reasoning_id: str) -> ReasoningReference:
        """Create a new ReasoningReference."""
        return cls(
            identity=identity,
            reasoning_id=reasoning_id,
        )


@dataclass(frozen=True)
class EvaluationReference(BaseReferenceContent):
    """
    Reference to an Evaluation process.
    
    SEMANTIC ROLE:
        - Points to an externally owned Evaluation process
        - Never owns evaluation implementation
        - Represents assessment artifacts
        
    OWNERSHIP CONTRACT:
        - Owns: None (reference only)
        - References: External Evaluation entity
        - Never owns: Evaluation implementations, runtime execution
    """
    
    ref_type: ReferenceType = field(default=ReferenceType.EVALUATION, init=False)
    evaluation_id: str = ""
    """Identifier for the referenced Evaluation"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, evaluation_id: str) -> EvaluationReference:
        """Create a new EvaluationReference."""
        return cls(
            identity=identity,
            evaluation_id=evaluation_id,
        )


__all__ = [
    "ReferenceType",
    "BaseReferenceContent",
    # Specific reference types
    "GoalReference",
    "ObjectiveReference",
    "TaskReference",
    "MissionReference",
    "PurposeReference",
    "ConstraintReference",
    "DependencyReference",
    "PlanReference",
    "DecisionReference",
    "WorkspaceReference",
    "WorkingMemoryReference",
    "StrategyReference",
    "ReasoningReference",
    "EvaluationReference",
]