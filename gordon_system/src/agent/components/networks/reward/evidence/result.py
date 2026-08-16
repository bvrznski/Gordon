# Reward Network - Evidence Result Model
# ======================================

"""
Evidence result model for Phase 4.10.2.

Output contract from the reward evidence engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional

from .evidence import RewardEvidence
from .graph import RewardEvidenceGraph


@dataclass(frozen=True)
class RewardEvidenceResult:
    """
    Result of evidence extraction and processing.

    OUTPUT CONTRACT (Phase 4.10.2):
        • state: Complete RewardEvidenceState with all evidence
        • graph: The evidence relationship graph
        • findings: Key findings from evidence processing
        • limitations: Known limitations
        • trace: Processing trace for provenance
        • status: Success/failure indicator

    The result is immutable and contains only semantic information.
    It does not modify any system state or make executive decisions.
    """

    # Core output
    state_id: str
    """Unique identifier for the evidence state."""

    evidences: Tuple[RewardEvidence, ...] = field(default_factory=tuple)
    """All extracted RewardEvidence items."""

    graph: Optional[RewardEvidenceGraph] = None
    """The evidence relationship graph (optional)."""

    # State summary
    confidence: float = 0.5
    """Overall confidence in the evidence set."""

    uncertainty: float = 0.0
    """Overall uncertainty in the evidence set."""

    evidence_count: int = 0
    """Count of extracted evidence items."""

    # Metadata
    status: str = "success"
    """Processing status (success/failure)."""

    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from processing."""

    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this result."""

    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Processing trace for provenance."""

    @property
    def is_success(self) -> bool:
        """Check if processing succeeded."""
        return self.status == "success"

    @classmethod
    def create(
        cls,
        state_id: str,
        evidences: Tuple[RewardEvidence, ...],
        graph: Optional[RewardEvidenceGraph] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.0,
        status: str = "success",
        findings: Tuple[str, ...] = tuple(),
        limitations: Tuple[str, ...] = tuple(),
        trace: Tuple[str, ...] = tuple(),
    ) -> RewardEvidenceResult:
        """
        Create a new evidence result.

        Args:
            state_id: Unique identifier for the evidence state
            evidences: All extracted RewardEvidence items
            graph: The evidence relationship graph (optional)
            confidence: Overall confidence in the evidence set
            uncertainty: Overall uncertainty in the evidence set
            status: Processing status
            findings: Key findings from processing
            limitations: Known limitations
            trace: Processing trace

        Returns:
            New RewardEvidenceResult instance
        """
        return cls(
            state_id=state_id,
            evidences=evidences,
            graph=graph,
            confidence=confidence,
            uncertainty=uncertainty,
            evidence_count=len(evidences),
            status=status,
            findings=findings,
            limitations=limitations,
            trace=trace,
        )