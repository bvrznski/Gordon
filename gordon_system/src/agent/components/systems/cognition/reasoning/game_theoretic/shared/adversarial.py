# Adversarial Analysis - Phase 7.43
# =================================

"""
Canonical Adversarial Analysis definitions.

Adversarial analysis handles:
    - Competitive scenario analysis
    - Opponent modeling
    - Best-response strategies
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class AdversarialAnalysis:
    """
    Analysis of adversarial interactions.
    
    An adversarial analysis includes:
        - Identity
        - Opponents identified
        - Competitive dynamics
        - Best-response strategies
        - Provenance
    """
    
    # Identity
    analysis_identity: str                  # Unique identifier
    
    # Adversaries
    adversaries: Tuple[str, ...] = ()       # List of opponent agents
    
    # Competitive dynamics
    competitive_dynamics: Dict[str, str] = {}  # Agent -> role (competitor, dominant, etc.)
    
    # Best responses
    best_responses: Dict[str, str] = {}        # Agent -> optimal strategy
    
    # Confidence
    confidence: float = 1.0                 # Overall confidence in analysis
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_game_id: Optional[str] = None    # Source game for this analysis
    
    @classmethod
    def create(
        cls,
        adversaries: List[str],
        source_game_id: Optional[str] = None,
    ) -> AdversarialAnalysis:
        """Create a new adversarial analysis."""
        return cls(
            analysis_identity=f"adversarial_analysis:{uuid.uuid4().hex[:16]}",
            adversaries=tuple(adversaries),
            source_game_id=source_game_id,
        )


__all__ = [
    "AdversarialAnalysis",
]
