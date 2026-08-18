# Cooperative Analysis - Phase 7.43
# =================================

"""
Canonical Cooperative Analysis definitions.

Cooperative analysis handles:
    - Collaborative scenario analysis
    - Coalition formation
    - Shared payoffs
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class CooperativeAnalysis:
    """
    Analysis of cooperative interactions.
    
    A cooperative analysis includes:
        - Identity
        - Agents involved
        - Coalition structures
        - Shared payoff potential
        - Provenance
    """
    
    # Identity
    analysis_identity: str                  # Unique identifier
    
    # Participants
    participants: Tuple[str, ...] = ()      # All cooperating agents
    
    # Coalition structure
    coalition_structure: Dict[str, List[str]] = {}  # Agent -> coalition members
    
    # Shared payoff potential
    shared_potential: float = 0.0           # Total cooperative surplus
    
    # Confidence
    confidence: float = 1.0                 # Overall confidence in analysis
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_game_id: Optional[str] = None    # Source game for this analysis
    
    @classmethod
    def create(
        cls,
        participants: List[str],
        source_game_id: Optional[str] = None,
    ) -> CooperativeAnalysis:
        """Create a new cooperative analysis."""
        return cls(
            analysis_identity=f"cooperative_analysis:{uuid.uuid4().hex[:16]}",
            participants=tuple(participants),
            source_game_id=source_game_id,
        )


__all__ = [
    "CooperativeAnalysis",
]
