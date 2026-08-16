# Reward Network - Evidence State
# ================================

"""
Evidence state module.

Constructs immutable aggregate state containing all evidence, graph,
confidence, uncertainty, hierarchy, and temporal information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional

from .evidence import RewardEvidence
from .graph import RewardEvidenceGraph


@dataclass(frozen=True, slots=True)
class RewardEvidenceState:
    """
    Immutable aggregate state of evidence processing.

    Contains all evidence items, the evidence graph, confidence and uncertainty
    information, hierarchy levels, temporal partitions, trace information,
    findings, and limitations.

    STATE PROPERTIES:
        • evidences: All reward evidence items
        • graph: The evidence relationship graph
        • confidence: Overall confidence in evidence set
        • uncertainty: Overall uncertainty in evidence set
        • hierarchy: Hierarchical structure of evidence
        • timescales: Temporal partitions
        • trace: Processing trace for provenance
        • findings: Key findings from processing
        • limitations: Known limitations

    STATE INVARIANTS:
        • State is immutable once constructed
        • Evidence list and graph are consistent
        • Confidence and uncertainty remain independent
        • Provenance is preserved throughout

    STATE LAWS:
        STATE-LAW-001: Exactly one canonical RewardEvidenceState exists
        STATE-LAW-002: RewardEvidenceState is immutable
        STATE-LAW-003: RewardEvidenceState preserves hierarchy
        STATE-LAW-004: RewardEvidenceState preserves temporal partitions
        STATE-LAW-005: RewardEvidenceState preserves confidence
        STATE-LAW-006: RewardEvidenceState preserves uncertainty
        STATE-LAW-007: RewardEvidenceState preserves provenance
        STATE-LAW-008: RewardEvidenceState preserves findings and limitations
    """

    state_id: str
    """Unique identifier for this evidence state."""

    evidences: Tuple[RewardEvidence, ...]
    """All reward evidence items."""

    graph: Optional[RewardEvidenceGraph] = None
    """The evidence relationship graph (optional)."""

    confidence: float = 0.5
    """Overall confidence in the evidence set (0.0 to 1.0)."""

    uncertainty: float = 0.0
    """Overall uncertainty in the evidence set (0.0 to 1.0)."""

    hierarchy: Tuple[Tuple[str, int], ...] = field(default_factory=tuple)
    """Hierarchical structure of evidence (evidence_id, level)."""

    timescales: Tuple[str, ...] = field(default_factory=tuple)
    """Temporal partitions in the evidence."""

    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Processing trace for provenance."""

    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from processing."""

    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this state."""

    @property
    def evidence_count(self) -> int:
        """Get count of evidence items."""
        return len(self.evidences)

    @property
    def has_graph(self) -> bool:
        """Check if a graph is present."""
        return self.graph is not None

    @classmethod
    def create(
        cls,
        state_id: str,
        evidences: Tuple[RewardEvidence, ...],
        graph: Optional[RewardEvidenceGraph] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.0,
        hierarchy: Tuple[Tuple[str, int], ...] = tuple(),
        timescales: Tuple[str, ...] = tuple(),
        trace: Tuple[str, ...] = tuple(),
        findings: Tuple[str, ...] = tuple(),
        limitations: Tuple[str, ...] = tuple(),
    ) -> RewardEvidenceState:
        """
        Create a new evidence state.

        Args:
            state_id: Unique identifier for this evidence state
            evidences: All reward evidence items
            graph: The evidence relationship graph (optional)
            confidence: Overall confidence in the evidence set
            uncertainty: Overall uncertainty in the evidence set
            hierarchy: Hierarchical structure of evidence
            timescales: Temporal partitions in the evidence
            trace: Processing trace for provenance
            findings: Key findings from processing
            limitations: Known limitations

        Returns:
            New RewardEvidenceState instance
        """
        return cls(
            state_id=state_id,
            evidences=evidences,
            graph=graph,
            confidence=confidence,
            uncertainty=uncertainty,
            hierarchy=tuple(sorted(hierarchy, key=lambda x: (x[0], x[1]))),
            timescales=tuple(sorted(set(timescales))),
            trace=trace,
            findings=findings,
            limitations=limitations,
        )


def build_evidence_state(
    state_id: str,
    evidences: Tuple[RewardEvidence, ...],
) -> RewardEvidenceState:
    """
    Build a basic evidence state from evidences.

    Creates a state with default values for optional fields.

    Args:
        state_id: Unique identifier for this evidence state
        evidences: All reward evidence items

    Returns:
        Basic RewardEvidenceState instance
    """
    return RewardEvidenceState.create(
        state_id=state_id,
        evidences=evidences,
        confidence=0.5,
        uncertainty=0.0,
    )