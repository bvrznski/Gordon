# Oriented Network Constraint Content Types - Phase 4.7.3
# =========================================================

"""
Constraint content types for the Oriented Network.

Constraint Content represents boundary conditions without runtime enforcement.
Constraints remain immutable and describe semantic limitations.

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-026: Constraints influence Orientation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from enum import Enum

from gordon_system.src.agent.components.networks.oriented.content.base import (
    BaseContent,
    ContentIdentity,
    ContentAuthority,
)


# =============================================================================
# CONSTRAINT TYPE ENUMERATIONS
# =============================================================================

class ConstraintType(Enum):
    """
    Canonical constraint types for Oriented Network content.
    """
    
    HARD = "hard"
    SOFT = "soft"
    REQUIREMENT = "requirement"
    POLICY = "policy"
    DEPENDENCY = "dependency"
    RISK = "risk"


# =============================================================================
# CONSTRAINT CONTENT TYPES
# =============================================================================

@dataclass(frozen=True)
class HardConstraint(BaseContent):
    """
    A hard (absolute) constraint.
    
    SEMANTIC ROLE:
        - Describes absolute boundary conditions
        - Never enforces constraints at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (constraint description only)
        - References: Affected orientation targets
    """
    
    constraint_type: ConstraintType = field(default=ConstraintType.HARD, init=False)
    description: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, description: str) -> HardConstraint:
        return cls(identity=identity, description=description)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "constraint_type": self.constraint_type.value,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HardConstraint:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            description=data.get("description", ""),
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
class SoftConstraint(BaseContent):
    """
    A soft (preferred but not absolute) constraint.
    
    SEMANTIC ROLE:
        - Describes preferred boundary conditions
        - Never enforces constraints at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (constraint description only)
        - References: Affected orientation targets
    """
    
    constraint_type: ConstraintType = field(default=ConstraintType.SOFT, init=False)
    preference_level: float = 0.5
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> SoftConstraint:
        return cls(identity=identity)


@dataclass(frozen=True)
class RequirementConstraint(BaseContent):
    """
    A constraint that represents a requirement.
    
    SEMANTIC ROLE:
        - Describes semantic necessity as a boundary
        - Never enforces requirements at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (constraint description only)
        - References: Required conditions
    """
    
    constraint_type: ConstraintType = field(default=ConstraintType.REQUIREMENT, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> RequirementConstraint:
        return cls(identity=identity)


@dataclass(frozen=True)
class PolicyConstraint(BaseContent):
    """
    A constraint that represents a policy.
    
    SEMANTIC ROLE:
        - Describes policy-based boundaries
        - Never enforces policies at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (constraint description only)
        - References: Affected orientation targets
    """
    
    constraint_type: ConstraintType = field(default=ConstraintType.POLICY, init=False)
    policy_source: str = ""
    
    @classmethod
    def create(cls, identity: ContentIdentity, policy_source: str) -> PolicyConstraint:
        return cls(identity=identity, policy_source=policy_source)


@dataclass(frozen=True)
class DependencyConstraint(BaseContent):
    """
    A constraint that represents a dependency.
    
    SEMANTIC ROLE:
        - Describes semantic dependencies as boundaries
        - Never enforces dependencies at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (constraint description only)
        - References: Dependent entities
    """
    
    constraint_type: ConstraintType = field(default=ConstraintType.DEPENDENCY, init=False)
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> DependencyConstraint:
        return cls(identity=identity)


@dataclass(frozen=True)
class RiskConstraint(BaseContent):
    """
    A constraint that represents a risk condition.
    
    SEMANTIC ROLE:
        - Describes risk-based boundaries
        - Never enforces risk mitigation at runtime
        
    OWNERSHIP CONTRACT:
        - Owns: None (constraint description only)
        - References: Affected orientation targets
    """
    
    constraint_type: ConstraintType = field(default=ConstraintType.RISK, init=False)
    risk_level: float = 0.5
    
    @classmethod
    def create(cls, identity: ContentIdentity) -> RiskConstraint:
        return cls(identity=identity)


__all__ = [
    "ConstraintType",
    # Specific constraint types
    "HardConstraint",
    "SoftConstraint",
    "RequirementConstraint",
    "PolicyConstraint",
    "DependencyConstraint",
    "RiskConstraint",
]