# Stakeholder Management - Phase 7.49
# ====================================

"""
Stakeholder analysis and management for moral reasoning.

MORAL-LAW-001: Every Moral Session possesses one immutable Semantic Identity
STAKEHOLDER-LAW-001: Every Stakeholder shall possess one explicit identity
STAKEHOLDER-LAW-002: Stakeholder interests shall remain explicit
STAKEHOLDER-LAW-003: Expected impacts shall remain explicit
STAKEHOLDER-LAW-004: Stakeholder provenance shall remain complete
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class StakeholderType(Enum):
    """Types of stakeholders."""
    
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    COMMUNITY = "community"
    FUTURE_GENERATION = "future_generation"
    ENVIRONMENTAL = "environmental"
    ANIMAL = "animal"


@dataclass(frozen=True)
class StakeholderImpact:
    """
    Impact on a stakeholder from an action.
    
    Contains both benefits and harms with confidence levels.
    """
    impact_id: str
    stakeholder_id: str
    impact_type: str  # benefit, harm, neutral
    description: str
    magnitude: float = 0.5  # 0-1 scale
    certainty: float = 1.0  # 0-1 confidence level


@dataclass(frozen=True)
class StakeholderAnalysis:
    """
    Complete analysis of a stakeholder in moral reasoning.
    
    STAKEHOLDER-LAW-005: Stakeholder revisions shall preserve history
    STAKEHOLDER-LAW-006: No ethically affected stakeholder shall be silently omitted
    STAKEHOLDER-LAW-007: Stakeholder Models shall remain independently inspectable
    
    A stakeholder analysis includes:
        - Identity and role
        - Interests and values at stake
        - Expected impacts (positive and negative)
        - Vulnerability assessment
        - Relative moral weight
    """
    
    # Identity
    analysis_id: str
    semantic_identity: str  # Links to session
    
    # Stakeholder info
    stakeholder_id: str
    name: str
    stakeholder_type: StakeholderType
    
    # Interests (what the stakeholder values)
    interests: List[str]
    
    # Expected impacts
    positive_impacts: Tuple[StakeholderImpact, ...] = field(default_factory=tuple)
    negative_impacts: Tuple[StakeholderImpact, ...] = field(default_factory=tuple)
    
    # Vulnerability (higher = more ethical consideration needed)
    vulnerable: bool = False
    
    # Moral weight (0-1 scale for decision weighting)
    moral_weight: float = 0.5
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def total_impact(self) -> float:
        """Calculate net impact (positive - negative)."""
        pos_sum = sum(i.magnitude for i in self.positive_impacts)
        neg_sum = sum(i.magnitude for i in self.negative_impacts)
        return pos_sum - neg_sum
    
    @property
    def impact_count(self) -> int:
        """Total number of impacts."""
        return len(self.positive_impacts) + len(self.negative_impacts)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        stakeholder_id: str,
        name: str,
        stakeholder_type: StakeholderType = StakeholderType.INDIVIDUAL,
        interests: Optional[List[str]] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> StakeholderAnalysis:
        """Create a new stakeholder analysis."""
        return cls(
            analysis_id=f"stakeholder_analysis:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            stakeholder_id=stakeholder_id,
            name=name,
            stakeholder_type=stakeholder_type,
            interests=interests or [],
            source_descriptor_id=source_descriptor_id,
            created_at_utc=time.time(),
        )
    
    def with_positive_impact(self, impact: StakeholderImpact) -> StakeholderAnalysis:
        """Add a positive impact."""
        return dataclass_replace(
            self,
            positive_impacts=self.positive_impacts + (impact,),
        )
    
    def with_negative_impact(self, impact: StakeholderImpact) -> StakeholderAnalysis:
        """Add a negative impact."""
        return dataclass_replace(
            self,
            negative_impacts=self.negative_impacts + (impact,),
        )


@dataclass(frozen=True)
class StakeholderSet:
    """
    Complete set of stakeholders for moral reasoning.
    
    This is the Moral Set's stakeholder component as per MORAL-LAW-002.
    All stakeholders must be explicitly identified and analyzed.
    """
    
    # Identity
    set_id: str
    
    # Stakeholders (tuple for immutability)
    analyses: Tuple[StakeholderAnalysis, ...]
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @property
    def count(self) -> int:
        """Number of stakeholders."""
        return len(self.analyses)
    
    @property
    def vulnerable_stakeholders(self) -> List[StakeholderAnalysis]:
        """List vulnerable stakeholders."""
        return [a for a in self.analyses if a.vulnerable]
    
    @classmethod
    def create(
        cls,
        analyses: Optional[List[StakeholderAnalysis]] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> StakeholderSet:
        """Create a new stakeholder set."""
        return cls(
            set_id=f"stakeholder_set:{uuid.uuid4().hex[:16]}",
            analyses=tuple(analyses or []),
            source_descriptor_id=source_descriptor_id,
            created_at_utc=time.time(),
        )
    
    def add_analysis(self, analysis: StakeholderAnalysis) -> StakeholderSet:
        """Add a stakeholder analysis."""
        return dataclass_replace(
            self,
            analyses=self.analyses + (analysis,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StakeholderType",
    "StakeholderImpact",
    "StakeholderAnalysis",
    "StakeholderSet",
]