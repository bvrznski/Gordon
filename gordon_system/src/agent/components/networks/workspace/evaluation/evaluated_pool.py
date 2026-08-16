# Evaluated Workspace Candidate Pool
# ====================================

"""
Canonical definition of EvaluatedWorkspaceCandidatePool.

This module provides the semantic artifact representing a collection of evaluated
candidates after Phase 4.6.4 evaluation.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - External time providers only
    - Bounded collections
    - Semantic-time preservation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

# =============================================================================
# POOL TYPES
# =============================================================================

EvaluatedWorkspaceCandidatePoolIdentity = str
"""Unique identifier for an evaluated candidate pool."""

EvaluatedWorkspaceCandidatePoolRevision = int
"""Monotonically increasing revision number for pools."""

EvaluatedWorkspaceCandidatePoolReference = str
"""
Immutable reference to Evaluated Workspace Candidate Pool.

Format: "identity@revision"
Examples:
    "pool_abc123@1"
    "evaluated_candidates_q4@5"
"""


# =============================================================================
# EVALUATED CANDIDATE POOL
# =============================================================================

@dataclass(frozen=True, slots=True)
class EvaluatedWorkspaceCandidatePool:
    """
    Immutable collection of evaluated Workspace Candidates.
    
    This is the terminal artifact of Phase 4.6.4 evaluation pipeline.
    
    CONSUMER INPUTS (Phase 4.6.5 Competition):
        EvaluatedWorkspaceCandidatePool
                ↓
        Competition Request
                ↓
        Frontier filtering
                ↓
        Winner Selection
    
    ARCHITECTURAL INVARIANTS:
        EWCP-INV-001: Pool is immutable and replayable
        EWCP-INV-002: Pool preserves all evaluated Candidates
        EWCP-INV-003: Pool has no runtime state
    """
    
    identity: EvaluatedWorkspaceCandidatePoolIdentity
    """Unique identifier for this pool."""
    
    revision: EvaluatedWorkspaceCandidatePoolRevision
    """Pool revision number."""
    
    # Candidates in the pool
    candidates: Tuple[str, ...]
    """References to evaluated candidates (identity@revision strings)."""
    
    # Metadata
    total_candidates_evaluated: int
    """Total number of candidates evaluated."""
    
    evaluation_context_ref: str = ""
    """Reference to evaluation context used."""
    
    # Semantic time
    semantic_time_ref: str = ""
    """Semantic time when pool was created."""
    
    provenance_ref: str = ""
    """Reference to evaluation provenance chain."""
    
    @property
    def candidate_count(self) -> int:
        """Number of candidates in this pool."""
        return len(self.candidates)
    
    @property
    def has_candidates(self) -> bool:
        """Whether any candidates exist in the pool."""
        return len(self.candidates) > 0


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    "EvaluatedWorkspaceCandidatePoolIdentity",
    "EvaluatedWorkspaceCandidatePoolRevision",
    "EvaluatedWorkspaceCandidatePoolReference",
    "EvaluatedWorkspaceCandidatePool",
]