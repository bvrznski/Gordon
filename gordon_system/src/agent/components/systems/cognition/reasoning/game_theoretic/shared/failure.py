# Game Failure - Phase 7.43
# =======================

"""
Canonical Game Failure definitions.

Failures include:
    - Incomplete games
    - Undefined payoffs
    - Strategy ambiguity
    - Missing equilibria
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Kinds of game failures."""
    
    INCOMPLETE_GAME = "incomplete_game"
    UNDEFINED_PAYOFFS = "undefined_payoffs"
    STRATEGY_AMBIGUITY = "strategy_ambiguity"
    MISSING_EQUILIBRIA = "missing_equilibria"
    CONFLICTING_INCENTIVES = "conflicting_incentives"
    UNSTABLE_EQUILIBRIA = "unstable_equilibria"


@dataclass(frozen=True)
class GameFailure:
    """
    Failure in game-theoretic reasoning.
    
    Failures remain explicit and inspectable.
    """
    
    # Identity
    failure_identity: str                   # Unique identifier
    
    # Kind of failure
    failure_kind: FailureKind               # What type of failure?
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()       # Detailed diagnostic info
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()  # Possible recovery actions
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_session_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind,
        diagnostics: List[str],
        recovery_options: List[str],
        source_session_id: Optional[str] = None,
    ) -> GameFailure:
        """Create a new game failure."""
        return cls(
            failure_identity=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            diagnostics=tuple(diagnostics),
            recovery_options=tuple(recovery_options),
            source_session_id=source_session_id,
        )


__all__ = [
    "GameFailure",
    "FailureKind",
]
