# Consequence Management - Phase 7.49
# ====================================

"""
Consequence analysis and management for moral reasoning.

MORAL-LAW-003: Every ethical conclusion shall reference explicit stakeholders, principles and supporting facts
CONSEQUENCE-LAW-001: Every Consequence Analysis shall possess one explicit identity
CONSEQUENCE-LAW-002: Projected outcomes shall remain explicit
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class Consequence:
    """
    A projected consequence of an action.
    
    CONSEQUENCE-LAW-003: Uncertainty shall remain explicit
    CONSEQUENCE-LAW-004: Consequence provenance shall remain complete
    """
    
    # Identity
    consequence_id: str
    
    # Description
    description: str
    
    # Impact information
    magnitude: float = 0.5  # Strength (0-1)
    direction: str = "neutral"  # "positive", "negative", "neutral"
    
    # Stakeholders affected
    stakeholders_affected: List[str] = field(default_factory=list)
    
    # Uncertainty estimate
    uncertainty: float = 0.1  # 0 = certain, 1 = highly uncertain
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ConsequenceAnalysis:
    """
    Complete analysis of consequences for a moral decision.
    
    CONSEQUENCE-LAW-005: Consequence revisions shall preserve history
    CONSEQUENCE-LAW-006: Significant harms shall never remain undisclosed
    """
    
    # Identity
    analysis_id: str
    
    # Projected outcomes (tuple for immutability)
    positive_outcomes: Tuple[Consequence, ...] = field(default_factory=tuple)
    negative_outcomes: Tuple[Consequence, ...] = field(default_factory=tuple)
    
    # Distribution analysis (who benefits/harms most?)
    distribution_analysis: Optional[str] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def positive_count(self) -> int:
        """Number of positive outcomes."""
        return len(self.positive_outcomes)
    
    @property
    def negative_count(self) -> int:
        """Number of negative outcomes."""
        return len(self.negative_outcomes)
    
    @property
    def total_outcomes(self) -> int:
        """Total number of outcomes."""
        return self.positive_count + self.negative_count
    
    @classmethod
    def create(
        cls,
        source_descriptor_id: Optional[str] = None,
    ) -> ConsequenceAnalysis:
        """Create a new consequence analysis."""
        return cls(
            analysis_id=f"consequence_analysis:{uuid.uuid4().hex[:16]}",
            source_descriptor_id=source_descriptor_id,
            created_at_utc=time.time(),
        )
    
    def with_positive_consequence(self, consequence: Consequence) -> ConsequenceAnalysis:
        """Add a positive outcome."""
        return dataclass_replace(
            self,
            positive_outcomes=self.positive_outcomes + (consequence,),
        )
    
    def with_negative_consequence(self, consequence: Consequence) -> ConsequenceAnalysis:
        """Add a negative outcome."""
        return dataclass_replace(
            self,
            negative_outcomes=self.negative_outcomes + (consequence,),
        )


@dataclass(frozen=True)
class ConsequenceSet:
    """
    Complete set of consequence analyses for moral reasoning.
    
    MORAL-LAW-003: Every ethical conclusion shall reference explicit stakeholders, 
    principles and supporting facts including consequences.
    """
    
    # Identity
    set_id: str
    
    # Analyses (tuple for immutability)
    analyses: Tuple[ConsequenceAnalysis, ...]
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_negative_outcomes(self) -> int:
        """Total negative outcomes across all analyses."""
        return sum(a.negative_count for a in self.analyses)
    
    @classmethod
    def create(
        cls,
        analyses: Optional[List[ConsequenceAnalysis]] = None,
    ) -> ConsequenceSet:
        """Create a new consequence set."""
        return cls(
            set_id=f"consequence_set:{uuid.uuid4().hex[:16]}",
            analyses=tuple(analyses or []),
            created_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "Consequence",
    "ConsequenceAnalysis",
    "ConsequenceSet",
]