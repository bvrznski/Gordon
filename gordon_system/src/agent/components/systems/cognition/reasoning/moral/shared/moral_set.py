# Moral Set - Phase 7.49
# ======================

"""
Canonical Moral Set.

A Moral Set defines the immutable context for moral reasoning:
- Stakeholders affected by the decision
- Ethical framework being applied
- Known factual context
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto


class EthicalFramework(Enum):
    """Ethical frameworks for moral reasoning."""
    
    DEONTOLOGICAL = "deontological"      # Duty-based (Kantian)
    UTILITARIAN = "utilitarian"          # Consequence-based (Bentham/Mill)
    VIRTUE = "virtue_ethics"             # Character-based (Aristotle)
    CONTRACTUAL = "contractual"          # Social contract (Rawls)
    CARE_ETHICS = "care_ethics"          # Relationship-based
    PLURALIST = "pluralist"              # Multiple principles


@dataclass(frozen=True)
class StakeholderEntry:
    """
    A stakeholder entry in a Moral Set.
    
    Contains:
        - Identity
        - Interests and values
        - Expected impact from the action
        - Relative weight in ethical evaluation
    """
    stakeholder_id: str
    name: str
    role: str
    interests: List[str]
    vulnerable: bool = False
    decision_influence: float = 0.5  # 0-1 scale


@dataclass(frozen=True)
class MoralValue:
    """A moral value being applied."""
    value_id: str
    name: str
    description: str
    priority: int = 0  # Higher is more important


@dataclass(frozen=True)
class EthicalPrinciple:
    """An ethical principle guiding the reasoning."""
    principle_id: str
    name: str
    description: str
    source: Optional[str] = None  # e.g., "Kant", "Rawls"


@dataclass(frozen=True)
class FactualContext:
    """
    Known factual context for moral reasoning.
    
    Each fact includes:
        - Statement
        - Confidence level (0-1)
        - Source information
    """
    fact_id: str
    statement: str
    confidence: float = 1.0
    sources: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MoralSet:
    """
    Immutable set defining moral reasoning context.
    
    A Moral Set contains all information needed for ethical evaluation:
        - Stakeholders (who is affected?)
        - Ethical framework (what principles apply?)
        - Factual context (what are the facts?)
        - Evaluation objectives (what should be assessed?)
    
    MORAL-LAW-001: Every Moral Session possesses one immutable Semantic Identity
    MORAL-LAW-002: Moral Reasoning shall execute over one explicit Moral Set
    
    The set remains immutable during reasoning to preserve determinism.
    """
    
    # Identity
    moral_set_id: str                       # Unique identifier
    semantic_identity: str                  # Stable across runs
    
    # Framework
    ethical_framework: EthicalFramework     # Which framework applies?
    
    # Content
    stakeholders: Tuple[StakeholderEntry, ...]
    values: Tuple[MoralValue, ...]
    principles: Tuple[EthicalPrinciple, ...]
    facts: Tuple[FactualContext, ...]
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def stakeholder_count(self) -> int:
        """Count of stakeholders."""
        return len(self.stakeholders)
    
    @property
    def vulnerable_stakeholders(self) -> List[StakeholderEntry]:
        """List vulnerable stakeholders."""
        return [s for s in self.stakeholders if s.vulnerable]
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        ethical_framework: EthicalFramework = EthicalFramework.PLURALIST,
        stakeholders: Optional[List[StakeholderEntry]] = None,
        values: Optional[List[MoralValue]] = None,
        principles: Optional[List[EthicalPrinciple]] = None,
        facts: Optional[List[FactualContext]] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> MoralSet:
        """Create a new moral set."""
        return cls(
            moral_set_id=f"moral_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            ethical_framework=ethical_framework,
            stakeholders=tuple(stakeholders or []),
            values=tuple(values or []),
            principles=tuple(principles or []),
            facts=tuple(facts or []),
            source_descriptor_id=source_descriptor_id,
            created_at_utc=time.time(),
        )
    
    def with_stakeholders(self, stakeholders: List[StakeholderEntry]) -> MoralSet:
        """Return copy with new stakeholders."""
        return dataclass_replace(
            self,
            stakeholders=tuple(stakeholders),
        )
    
    def add_stakeholder(self, stakeholder: StakeholderEntry) -> MoralSet:
        """Return copy with added stakeholder."""
        return dataclass_replace(
            self,
            stakeholders=self.stakeholders + (stakeholder,),
        )
    
    def add_fact(self, fact: FactualContext) -> MoralSet:
        """Return copy with added fact."""
        return dataclass_replace(
            self,
            facts=self.facts + (fact,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MoralSet",
    "StakeholderEntry",
    "MoralValue",
    "EthicalPrinciple",
    "FactualContext",
    "EthicalFramework",
]