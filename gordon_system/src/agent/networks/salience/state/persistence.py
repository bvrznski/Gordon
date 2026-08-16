# Salience Network Persistence State
# ===================================
#
# Canonical implementation of semantic persistence (Phase 4.8.4).
#

"""
Persistence state for semantic continuity expectations.

PERSISTENCE vs DECAY:
    - Persistence: Expected semantic continuity
    - Decay: Expected loss of salience or validity
    
PERSISTENCE CATEGORIES:
    - TRANSIENT: Very short expected lifetime
    - SHORT_LIVED: Brief relevance period
    - SUSTAINED: Moderately long duration
    - PERSISTENT: Long-term significance
    - RECURRENT: Returns periodically
    - DORMANT: Preserved but inactive
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SaliencePersistenceState:
    """
    Canonical semantic persistence representation.
    
    PERSISTENCE Kinds:
        - TRANSIENT: Very short expected lifetime (< 1 time unit)
        - SHORT_LIVED: Brief relevance period (1-3 time units)
        - SUSTAINED: Moderately long duration (4-10 time units)
        - PERSISTENT: Long-term significance (> 10 time units)
        - RECURRENT: Returns periodically
        - DORMANT: Preserved but inactive
    
    PERSISTENCE LAWS:
        - SALIENCE-PERSISTENCE-LAW-001: Persistence describes expected continuity
        - SALIENCE-PERSISTENCE-LAW-002: No runtime history is stored
        - SALIENCE-PERSISTENCE-LAW-003: External time references required for actual computation
    """
    
    kind: str = field(default="unknown")
    """Semantic persistence classification."""
    
    expected_duration: str = field(default="unknown")
    """Expected semantic lifetime category."""
    
    temporal_reference_id: str | None = field(default=None)
    """External time reference where applicable (not computed internally)."""
    
    recurrence_pattern: str = field(default="none")
    """Recurrence pattern if applicable."""