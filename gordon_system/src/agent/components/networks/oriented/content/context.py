# Oriented Network Context Content Types - Phase 4.7.3
# ======================================================

"""
Context content types for the Oriented Network.

Context Content describes semantic surroundings that shape orientation.
Context provides framing without determining orientation semantics.

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-025: Context influences Orientation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
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
# CONTEXT TYPE ENUMERATIONS
# =============================================================================

class ContextType(Enum):
    """
    Canonical context types for Oriented Network content.
    """
    
    MISSION = "mission"
    GOAL = "goal"
    OBJECTIVE = "objective"
    TASK = "task"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    ENVIRONMENTAL = "environmental"
    RECOVERY = "recovery"
    CONSTRAINT = "constraint"
    EVALUATION = "evaluation"


# =============================================================================
# CONTEXT CONTENT TYPES
# =============================================================================

@dataclass(frozen=True)
class MissionContext(BaseContent):
    """
    Context for Mission-oriented orientation.
    
    SEMANTIC ROLE:
        - Describes surrounding conditions for mission orientation
        - Never owns the mission itself
        
    OWNERSHIP CONTRACT:
        - Owns: None (context description only)
        - References: External Mission entity
        - Never owns: Mission implementations, runtime execution
    """
    
    context_type: ContextType = field(default=ContextType.MISSION, init=False)
    mission_id: str = ""
    """Referenced Mission identifier"""
    
    semantic_domain: str = ""
    """Domain context (e.g., 'finance', 'healthcare')"""
    
    @classmethod
    def create(cls, identity: ContentIdentity, mission_id: str) -> MissionContext:
        return cls(identity=identity, mission_id=mission_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "mission_id": self.mission_id,
            "semantic_domain": self.semantic_domain,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MissionContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            mission_id=data.get("mission_id", ""),
            semantic_domain=data.get("semantic_domain", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class GoalContext(BaseContent):
    """
    Context for Goal-oriented orientation.
    
    SEMANTIC ROLE:
        - Describes surrounding conditions for goal orientation
        - Never owns the goal itself
    """
    
    context_type: ContextType = field(default=ContextType.GOAL, init=False)
    goal_id: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, goal_id: str) -> GoalContext:
        return cls(identity=identity, goal_id=goal_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "goal_id": self.goal_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoalContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            goal_id=data.get("goal_id", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ObjectiveContext(BaseContent):
    """
    Context for Objective-oriented orientation.
    
    SEMANTIC ROLE:
        - Describes surrounding conditions for objective orientation
        - Never owns the objective itself
    """
    
    context_type: ContextType = field(default=ContextType.OBJECTIVE, init=False)
    objective_id: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, objective_id: str) -> ObjectiveContext:
        return cls(identity=identity, objective_id=objective_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "objective_id": self.objective_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ObjectiveContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            objective_id=data.get("objective_id", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class TaskContext(BaseContent):
    """
    Context for Task-oriented orientation.
    
    SEMANTIC ROLE:
        - Describes surrounding conditions for task orientation
        - Never owns the task itself
    """
    
    context_type: ContextType = field(default=ContextType.TASK, init=False)
    task_id: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, task_id: str) -> TaskContext:
        return cls(identity=identity, task_id=task_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "task_id": self.task_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            task_id=data.get("task_id", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class OperationalContext(BaseContent):
    """
    Context for operational orientation.
    
    SEMANTIC ROLE:
        - Describes operational conditions affecting orientation
        - Never owns operational state
    """
    
    context_type: ContextType = field(default=ContextType.OPERATIONAL, init=False)
    operational_state: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, operational_state: str) -> OperationalContext:
        return cls(identity=identity, operational_state=operational_state)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "operational_state": self.operational_state,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OperationalContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            operational_state=data.get("operational_state", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class StrategicContext(BaseContent):
    """
    Context for strategic orientation.
    
    SEMANTIC ROLE:
        - Describes strategic conditions affecting orientation
        - Never owns strategic state
    """
    
    context_type: ContextType = field(default=ContextType.STRATEGIC, init=False)
    strategy_id: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, strategy_id: str) -> StrategicContext:
        return cls(identity=identity, strategy_id=strategy_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "strategy_id": self.strategy_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StrategicContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            strategy_id=data.get("strategy_id", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class EnvironmentalContext(BaseContent):
    """
    Context for environmental orientation.
    
    SEMANTIC ROLE:
        - Describes external environment affecting orientation
        - Never owns environmental state
    """
    
    context_type: ContextType = field(default=ContextType.ENVIRONMENTAL, init=False)
    environmental_state: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, environmental_state: str) -> EnvironmentalContext:
        return cls(identity=identity, environmental_state=environmental_state)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "environmental_state": self.environmental_state,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EnvironmentalContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            environmental_state=data.get("environmental_state", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class RecoveryContext(BaseContent):
    """
    Context for recovery orientation.
    
    SEMANTIC ROLE:
        - Describes recovery conditions affecting orientation
        - Never owns recovery state
    """
    
    context_type: ContextType = field(default=ContextType.RECOVERY, init=False)
    recovery_state: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, recovery_state: str) -> RecoveryContext:
        return cls(identity=identity, recovery_state=recovery_state)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "recovery_state": self.recovery_state,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecoveryContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            recovery_state=data.get("recovery_state", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ConstraintContext(BaseContent):
    """
    Context for constraint-related orientation.
    
    SEMANTIC ROLE:
        - Describes constraint conditions affecting orientation
        - Never owns constraints themselves
    """
    
    context_type: ContextType = field(default=ContextType.CONSTRAINT, init=False)
    constraint_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def create(cls, identity: ContentIdentity, constraint_ids: Tuple[str, ...]) -> ConstraintContext:
        return cls(identity=identity, constraint_ids=constraint_ids)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "constraint_ids": self.constraint_ids,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConstraintContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            constraint_ids=tuple(data.get("constraint_ids", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class EvaluationContext(BaseContent):
    """
    Context for evaluation-related orientation.
    
    SEMANTIC ROLE:
        - Describes evaluation conditions affecting orientation
        - Never owns evaluation state
    """
    
    context_type: ContextType = field(default=ContextType.EVALUATION, init=False)
    evaluation_state: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, evaluation_state: str) -> EvaluationContext:
        return cls(identity=identity, evaluation_state=evaluation_state)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "context_type": self.context_type.value,
            "evaluation_state": self.evaluation_state,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvaluationContext:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            evaluation_state=data.get("evaluation_state", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


__all__ = [
    "ContextType",
    # Context content types
    "MissionContext",
    "GoalContext",
    "ObjectiveContext",
    "TaskContext",
    "OperationalContext",
    "StrategicContext",
    "EnvironmentalContext",
    "RecoveryContext",
    "ConstraintContext",
    "EvaluationContext",
]