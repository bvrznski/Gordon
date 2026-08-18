# Decision Revision - Phase 7.19
# =============================

"""
Canonical Decision Revision Contract.

Decision revisions occur through new evidence, environment changes,
policy changes, constraint violations, or mission updates.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DecisionRevision:
    """
    A revision to a previous decision.
    
    Revisions preserve the original Decision Identity while updating
    the commitment based on new information.
    """
    
    # Identity (stable across revisions)
    revision_identity: str                  # Same as original decision
    
    # Revision info
    revision_id: str                        # Unique revision identifier
    
    # Previous decision state
    previous_decision: str                  # Previous committed option
    
    # Revised decision state
    revised_decision: str                   # New committed option (or None to uncommit)
    
    # Revision reason
    revision_reason: str                    # Why was revision needed?
    
    # Evidence that triggered revision
    triggering_evidence: Tuple[str, ...] = ()  # What new evidence caused this?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_revision(self) -> bool:
        """Check if this is actually a revision (different from previous)."""
        return self.previous_decision != self.revised_decision
    
    @classmethod
    def create(
        cls,
        revision_identity: str,
        previous_decision: str,
        revised_decision: str,
        revision_reason: str = "new_evidence",
        triggering_evidence: Optional[List[str]] = None,
    ) -> DecisionRevision:
        """Create a new decision revision."""
        return cls(
            revision_identity=revision_identity,
            revision_id=f"decision_revision:{uuid.uuid4().hex[:16]}",
            previous_decision=previous_decision,
            revised_decision=revised_decision,
            revision_reason=revision_reason,
            triggering_evidence=tuple(triggering_evidence or []),
        )


@dataclass(frozen=True)
class DecisionRevisionPipeline:
    """
    Pipeline for processing decision revisions.
    
    The pipeline defines how revisions are processed and applied.
    """
    
    # Identity
    pipeline_identity: str                  # Pipeline identifier
    
    # Previous decision (before revision)
    previous_decision: str                  # Option committed before revision
    
    # Revised decision (after revision)
    revised_decision: str                   # Option committed after revision
    
    # Revision strategy used
    revision_strategy: str = "default"      # e.g., "evidence_based", "policy_driven"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        previous_decision: str,
        revised_decision: str,
        revision_strategy: str = "default",
    ) -> DecisionRevisionPipeline:
        """Create a new revision pipeline."""
        return cls(
            pipeline_identity=f"revision_pipeline:{uuid.uuid4().hex[:16]}",
            previous_decision=previous_decision,
            revised_decision=revised_decision,
            revision_strategy=revision_strategy,
        )


__all__ = [
    "DecisionRevision",
    "DecisionRevisionPipeline",
]