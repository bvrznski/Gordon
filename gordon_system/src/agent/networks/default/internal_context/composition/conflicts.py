# Internal Context Conflict Model
# ===============================

"""
Conflict records for internal context assembly.

Conflicts are NEVER silently resolved. They are recorded and may influence
confidence or completeness assessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


ContextConflictId = str
"""Unique identifier for a conflict record."""


@dataclass(frozen=True, slots=True)
class InternalContextConflict:
    """
    Record of a semantic conflict detected during context assembly.
    
    Conflicts are NEVER silently resolved. They are recorded and may influence
    confidence or completeness assessment.
    
    CONFLICT CATEGORIES:
        • revision_mismatch: Source projection revisions differ unexpectedly
        • objective_conflict: Conflicting objective statements
        • identity_conflict: Conflicting identity projections
        • memory_conflict: Conflicting memory representations
        • narrative_conflict: Conflicting narrative elements
        • prediction_conflict: Conflicting predictive projections
        • commitment_conflict: Conflicting commitment statements
        • temporal_conflict: Temporal inconsistency
        • provenance_conflict: Incompatible provenance information
        • policy_conflict: Violates active policy constraints
    
    CONFLICT SEVERITY:
        • blocking: Cannot be used until resolved or acknowledged
        • non-blocking: Can proceed but with reduced confidence
    """
    
    conflict_id: ContextConflictId
    """Unique identifier for this conflict."""
    
    category: str  # ContextConflictCategory.*
    """Category of the conflict."""
    
    description: str
    """Description of what conflicts and why."""
    
    severity: str = "non-blocking"
    """Severity level: 'blocking' or 'non-blocking'."""
    
    resolution_status: str = "unresolved"
    """Resolution status: 'unresolved', 'acknowledged', 'deferred'."""
    
    involved_projection_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to projections involved in the conflict."""
    
    @classmethod
    def blocking(
        cls,
        category: str,
        description: str,
        projection_refs: Tuple[str, ...] = (),
    ) -> InternalContextConflict:
        """Create a blocking conflict."""
        return cls(
            conflict_id=f"conflict_{category}_{id(description)}",
            category=category,
            description=description,
            severity="blocking",
            involved_projection_refs=projection_refs,
        )
    
    @classmethod
    def non_blocking(
        cls,
        category: str,
        description: str,
        projection_refs: Tuple[str, ...] = (),
    ) -> InternalContextConflict:
        """Create a non-blocking conflict."""
        return cls(
            conflict_id=f"conflict_{category}_{id(description)}",
            category=category,
            description=description,
            severity="non-blocking",
            involved_projection_refs=projection_refs,
        )
    
    def is_blocking(self) -> bool:
        """Check if this conflict is blocking."""
        return self.severity == "blocking"
    
    def is_resolved(self) -> bool:
        """Check if the conflict has been resolved."""
        return self.resolution_status in ("acknowledged", "resolved")
    
    def to_dict(self) -> dict[str, str | int]:
        """Convert to a dictionary representation."""
        return {
            "conflict_id": self.conflict_id,
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "resolution_status": self.resolution_status,
            "projection_refs_count": len(self.involved_projection_refs),
        }