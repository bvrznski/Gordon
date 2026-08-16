# Oriented Network Requirement Content Types - Phase 4.7.3
# ==========================================================

"""
Requirement content types for the Oriented Network.

Requirement Content represents semantic necessity conditions without
runtime implementation or allocation.

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-028: Requirements express semantic necessity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional

from gordon_system.src.agent.components.networks.oriented.content.base import (
    BaseContent,
    ContentIdentity,
    ContentAuthority,
)
from enum import Enum


# =============================================================================
# REQUIREMENT TYPE ENUMERATIONS
# =============================================================================

class RequirementType(Enum):
    """
    Canonical requirement types for Oriented Network content.
    """
    
    ATTENTION = "attention"
    WORKSPACE = "workspace"
    WORKING_MEMORY = "working_memory"
    PLANNING = "planning"
    REASONING = "reasoning"
    EVALUATION = "evaluation"
    SCHEDULER = "scheduler"


# =============================================================================
# REQUIREMENT CONTENT TYPES
# =============================================================================

@dataclass(frozen=True)
class BaseRequirementContent(BaseContent):
    """
    Base class for all requirement content types.
    
    Requirement Content represents semantic necessity conditions.
    Requirements express what must be satisfied without allocating resources.
    """
    
    req_type: RequirementType = RequirementType.ATTENTION
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "req_type": self.req_type.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseRequirementContent:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            req_type=RequirementType(data.get("req_type", RequirementType.ATTENTION.value)),
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
class AttentionRequirement(BaseRequirementContent):
    """
    Requirement for attention capacity.
    
    SEMANTIC ROLE:
        - Describes semantic need for attention
        - Never allocates runtime attention resources
        
    OWNERSHIP CONTRACT:
        - Owns: None (requirement description only)
        - References: Target entities needing attention
    """
    
    req_type: RequirementType = field(default=RequirementType.ATTENTION, init=False)
    focus_target: Optional[ContentIdentity] = None
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> AttentionRequirement:
        return cls(identity=identity)


@dataclass(frozen=True)
class WorkspaceRequirement(BaseRequirementContent):
    """
    Requirement for workspace capacity.
    
    SEMANTIC ROLE:
        - Describes semantic need for workspace
        - Never allocates runtime workspace resources
        
    OWNERSHIP CONTRACT:
        - Owns: None (requirement description only)
        - References: Content needing workspace
    """
    
    req_type: RequirementType = field(default=RequirementType.WORKSPACE, init=False)
    content_size: float = 0.0
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> WorkspaceRequirement:
        return cls(identity=identity)


@dataclass(frozen=True)
class WorkingMemoryRequirement(BaseRequirementContent):
    """
    Requirement for working memory capacity.
    
    SEMANTIC ROLE:
        - Describes semantic need for working memory
        - Never allocates runtime working memory resources
        
    OWNERSHIP CONTRACT:
        - Owns: None (requirement description only)
        - References: Information needing working memory
    """
    
    req_type: RequirementType = field(default=RequirementType.WORKING_MEMORY, init=False)
    item_count: int = 0
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> WorkingMemoryRequirement:
        return cls(identity=identity)


@dataclass(frozen=True)
class PlanningRequirement(BaseRequirementContent):
    """
    Requirement for planning capacity.
    
    SEMANTIC ROLE:
        - Describes semantic need for planning
        - Never allocates runtime planning resources
        
    OWNERSHIP CONTRACT:
        - Owns: None (requirement description only)
        - References: Goals/objectives needing planning
    """
    
    req_type: RequirementType = field(default=RequirementType.PLANNING, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> PlanningRequirement:
        return cls(identity=identity)


@dataclass(frozen=True)
class ReasoningRequirement(BaseRequirementContent):
    """
    Requirement for reasoning capacity.
    
    SEMANTIC ROLE:
        - Describes semantic need for reasoning
        - Never allocates runtime reasoning resources
        
    OWNERSHIP CONTRACT:
        - Owns: None (requirement description only)
        - References: Questions needing reasoning
    """
    
    req_type: RequirementType = field(default=RequirementType.REASONING, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> ReasoningRequirement:
        return cls(identity=identity)


@dataclass(frozen=True)
class EvaluationRequirement(BaseRequirementContent):
    """
    Requirement for evaluation capacity.
    
    SEMANTIC ROLE:
        - Describes semantic need for evaluation
        - Never allocates runtime evaluation resources
        
    OWNERSHIP CONTRACT:
        - Owns: None (requirement description only)
        - References: Content needing evaluation
    """
    
    req_type: RequirementType = field(default=RequirementType.EVALUATION, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> EvaluationRequirement:
        return cls(identity=identity)


@dataclass(frozen=True)
class SchedulerRequirement(BaseRequirementContent):
    """
    Requirement for scheduler capacity.
    
    SEMANTIC ROLE:
        - Describes semantic need for scheduling
        - Never allocates runtime scheduler resources
        
    OWNERSHIP CONTRACT:
        - Owns: None (requirement description only)
        - References: Tasks needing scheduling
    """
    
    req_type: RequirementType = field(default=RequirementType.SCHEDULER, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> SchedulerRequirement:
        return cls(identity=identity)


__all__ = [
    "RequirementType",
    # Specific requirement types
    "AttentionRequirement",
    "WorkspaceRequirement",
    "WorkingMemoryRequirement",
    "PlanningRequirement",
    "ReasoningRequirement",
    "EvaluationRequirement",
    "SchedulerRequirement",
]