# Oriented Network Strategy Integration Types
# ============================================

"""
Strategy Integration Types for Phase 4.7.6.

OWNERSHIP (Strategy):
    - strategic reasoning
    - long-term strategy
    - strategic adaptation
    
ORIENTED NETWORK ROLE:
    - consumes strategic context
    - never creates strategy
    - references strategic intent

SEMANTIC INTEGRATION LAWS (Phase 4.7.6):
    INTEGRATION-LAW-003: Strategy remains the sole owner of strategic cognition.
    INTEGRATION-LAW-007: Integration never transfers ownership.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional


@dataclass(frozen=True)
class StrategyReference:
    """
    Reference to strategic intent or long-term strategy.
    
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-003: Strategy remains the sole owner of strategic cognition.
        INTEGRATION-LAW-013: Every reference shall be explicit.
    """
    
    identity: str = field(default="unnamed")
    strategy_id: Optional[str] = None
    source: str = "strategy"
    
    def to_dict(self) -> Dict[str, Any]:
        return {"identity": self.identity, "strategy_id": self.strategy_id, "source": self.source}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StrategyReference:
        return cls(
            identity=data.get("identity", "unnamed"),
            strategy_id=data.get("strategy_id"),
            source=data.get("source", "strategy"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        return (len(errors) == 0, tuple(errors))


@dataclass(frozen=True)
class StrategyContext:
    """
    Strategic context information consumed by Oriented Network.
    
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-003: Strategy remains the sole owner of strategic cognition.
    """
    
    identity: str = field(default="unnamed")
    current_strategy: Optional[str] = None
    adaptation_state: str = "stable"
    
    def to_dict(self) -> Dict[str, Any]:
        return {"identity": self.identity, "current_strategy": self.current_strategy, "adaptation_state": self.adaptation_state}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StrategyContext:
        return cls(
            identity=data.get("identity", "unnamed"),
            current_strategy=data.get("current_strategy"),
            adaptation_state=data.get("adaptation_state", "stable"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        return (len(errors) == 0, tuple(errors))


@dataclass(frozen=True)
class StrategyInfluence:
    """
    Strategic influence on orientation.
    
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-003: Strategy remains the sole owner of strategic cognition.
        INTEGRATION-LAW-015: Integration shall never invoke subsystem algorithms.
    """
    
    identity: str = field(default="unnamed")
    influence_type: str = "strategy_emphasis"
    affected_orientation_ids: Tuple[str, ...] = field(default_factory=tuple)
    strength: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "influence_type": self.influence_type,
            "affected_orientation_ids": list(self.affected_orientation_ids),
            "strength": self.strength,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StrategyInfluence:
        return cls(
            identity=data.get("identity", "unnamed"),
            influence_type=data.get("influence_type", "strategy_emphasis"),
            affected_orientation_ids=tuple(data.get("affected_orientation_ids", [])),
            strength=float(data.get("strength", 0.5)),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        return (len(errors) == 0, tuple(errors))


@dataclass(frozen=True)
class StrategyRelationship:
    """
    Semantic relationship between Oriented Network and Strategy.
    
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-003: Strategy remains the sole owner of strategic cognition.
        INTEGRATION-LAW-015: Integration shall never invoke subsystem algorithms.
    """
    
    identity: str = field(default="unnamed")
    orientation_id: str = ""
    strategy_authority: str = "strategy"
    coordination_mode: str = "consume_context"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "orientation_id": self.orientation_id,
            "strategy_authority": self.strategy_authority,
            "coordination_mode": self.coordination_mode,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StrategyRelationship:
        return cls(
            identity=data.get("identity", "unnamed"),
            orientation_id=data.get("orientation_id", ""),
            strategy_authority=data.get("strategy_authority", "strategy"),
            coordination_mode=data.get("coordination_mode", "consume_context"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        return (len(errors) == 0, tuple(errors))


@dataclass(frozen=True)
class StrategyProjection:
    """
    Semantic strategy projection to Oriented Network.
    
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-003: Strategy remains the sole owner of strategic cognition.
    """
    
    identity: str = field(default="unnamed")
    projected_strategy: Optional[str] = None
    projection_type: str = "recommendation"
    
    def to_dict(self) -> Dict[str, Any]:
        return {"identity": self.identity, "projected_strategy": self.projected_strategy, "projection_type": self.projection_type}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StrategyProjection:
        return cls(
            identity=data.get("identity", "unnamed"),
            projected_strategy=data.get("projected_strategy"),
            projection_type=data.get("projection_type", "recommendation"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        return (len(errors) == 0, tuple(errors))


__all__ = [
    "StrategyReference",
    "StrategyContext",
    "StrategyInfluence",
    "StrategyRelationship",
    "StrategyProjection",
]