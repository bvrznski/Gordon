# Internal Episode Evidence Conflict Model
# =========================================

"""
Conflict model for internal episode evidence.

Records conflicts between evidence items without attempting resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


EvidenceConflictId = str
"""Unique identifier for an evidence conflict record."""


@dataclass(frozen=True, slots=True)
class InternalEpisodeEvidenceConflict:
    """
    Record of a detected conflict between evidence items.
    
    Conflicts are NEVER silently resolved. They are recorded and may influence
    confidence or completeness assessment.
    """
    
    # Identity
    conflict_id: EvidenceConflictId
    """Unique identifier for this conflict."""
    
    category: str  # ContextConflictCategory.*
    """Type of conflict detected."""
    
    description: str
    """Human-readable description of the conflict."""
    
    severity: str = "non-blocking"  # "blocking" or "non-blocking"
    """How critical this conflict is."""
    
    evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of evidence items involved in this conflict."""
    
    resolution_status: str = "unresolved"  # "unresolved", "acknowledged", "deferred"
    """Current state of conflict resolution."""
    
    recorded_at_utc: str = ""
    """When the conflict was detected and recorded."""
    
    @classmethod
    def blocking(cls, category: str, description: str) -> InternalEpisodeEvidenceConflict:
        """Create a blocking conflict record."""
        return cls(
            conflict_id=f"conflict_{id(cls)}",
            category=category,
            description=description,
            severity="blocking",
        )
    
    @classmethod
    def non_blocking(cls, category: str, description: str) -> InternalEpisodeEvidenceConflict:
        """Create a non-blocking conflict record."""
        return cls(
            conflict_id=f"conflict_{id(cls)}",
            category=category,
            description=description,
            severity="non-blocking",
        )