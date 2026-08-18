# Incentive Analysis - Phase 7.43
# ===============================

"""
Canonical Incentive Analysis definitions.

Incentive analysis evaluates:
    - Strategic incentives
    - Cooperative incentives
    - Competitive incentives
    - Deviation incentives
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class IncentiveIdentity:
    """Unique identity for an incentive."""
    
    identity: str  # Unique identifier


@dataclass(frozen=True)
class IncentiveAnalysis:
    """
    Analysis of incentives in a game.
    
    An incentive analysis includes:
        - Identity
        - Incentive model
        - Incentive alignment metrics
        - Deviation risks
        - Provenance
    """
    
    # Identity
    analysis_identity: str                  # Unique identifier
    
    # Incentive model
    incentive_model: str                    # Type of incentives (e.g., "strategic", "cooperative")
    
    # Alignment metrics
    incentive_alignment: Dict[str, float] = {}  # Agent -> alignment score
    
    # Deviation risk
    deviation_risk: Dict[str, float] = {}       # Agent -> risk of deviation
    
    # Confidence
    confidence: float = 1.0                 # Overall confidence in analysis
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_game_id: Optional[str] = None    # Source game for this analysis
    
    @classmethod
    def create(
        cls,
        incentive_model: str,
        source_game_id: Optional[str] = None,
    ) -> IncentiveAnalysis:
        """Create a new incentive analysis."""
        return cls(
            analysis_identity=f"incentive_analysis:{uuid.uuid4().hex[:16]}",
            incentive_model=incentive_model,
            source_game_id=source_game_id,
        )


@dataclass(frozen=True)
class IncentiveManagement:
    """
    Management of incentives over time.
    
    Incentive management includes:
        - Identity
        - Current incentive model
        - Alignment metrics
        - Deviation risks
        - Provenance
    """
    
    # Identity
    management_identity: str                # Unique identifier
    
    # Incentive model
    incentive_model: str                    # Type of incentives managed
    
    # Alignment
    incentive_alignment: Dict[str, float] = {}  # Agent -> alignment score
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_incentive_id: Optional[str] = None  # If derived from another
    
    @classmethod
    def create(
        cls,
        incentive_model: str,
        source_incentive_id: Optional[str] = None,
    ) -> IncentiveManagement:
        """Create new incentive management."""
        return cls(
            management_identity=f"incentive_mgmt:{uuid.uuid4().hex[:16]}",
            incentive_model=incentive_model,
            source_incentive_id=source_incentive_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "IncentiveIdentity",
    "IncentiveAnalysis",
    "IncentiveManagement",
]
