# Payoff Analysis - Phase 7.43
# ============================

"""
Canonical Payoff Analysis definitions.

Payoff analysis determines:
    - Individual utility
    - Collective utility
    - Expected payoff
    - Worst-case/best-case payoffs
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class PayoffIdentity:
    """Unique identity for a payoff."""
    
    identity: str  # Unique identifier


@dataclass(frozen=True)
class PayoffAnalysis:
    """
    Analysis of payoffs in a game.
    
    A payoff analysis includes:
        - Identity
        - Payoff model
        - Payoff distribution
        - Expected payoffs
        - Provenance
    """
    
    # Identity
    analysis_identity: str                  # Unique identifier
    
    # Payoff model
    payoff_model: str                       # Type of payoff (e.g., "utility", "regret")
    
    # Payoff distribution
    payoff_distribution: Dict[str, float] = {}  # Agent/strategy -> payoff value
    
    # Expected payoffs
    expected_payoff: Dict[str, float] = {}      # Agent -> expected payoff
    
    # Confidence
    confidence: float = 1.0                 # Overall confidence in analysis
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_game_id: Optional[str] = None    # Source game for this analysis
    
    @classmethod
    def create(
        cls,
        payoff_model: str,
        source_game_id: Optional[str] = None,
    ) -> PayoffAnalysis:
        """Create a new payoff analysis."""
        return cls(
            analysis_identity=f"payoff_analysis:{uuid.uuid4().hex[:16]}",
            payoff_model=payoff_model,
            source_game_id=source_game_id,
        )


@dataclass(frozen=True)
class PayoffManagement:
    """
    Management of payoffs over time.
    
    Payoff management includes:
        - Identity
        - Current payoff model
        - Distribution metrics
        - Expected payoffs
        - Provenance
    """
    
    # Identity
    management_identity: str                # Unique identifier
    
    # Payoff model
    payoff_model: str                       # Type of payoff being managed
    
    # Distribution
    expected_payoff: Dict[str, float] = {}  # Agent -> expected payoff
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_payoff_id: Optional[str] = None  # If derived from another
    
    @classmethod
    def create(
        cls,
        payoff_model: str,
        source_payoff_id: Optional[str] = None,
    ) -> PayoffManagement:
        """Create new payoff management."""
        return cls(
            management_identity=f"payoff_mgmt:{uuid.uuid4().hex[:16]}",
            payoff_model=payoff_model,
            source_payoff_id=source_payoff_id,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "PayoffIdentity",
    "PayoffAnalysis",
    "PayoffManagement",
]