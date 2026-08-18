# Dialectical Consensus - Phase 7.17
# ==================================

"""
Canonical Consensus Discovery Contract.

Consensus identifies:
    - Shared assumptions
    - Shared evidence
    - Shared mechanisms
    - Shared conclusions
    - Remaining disagreement
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ConsensusDiscovery:
    """
    A consensus discovery process.

    Consensus identifies:
        - Shared assumptions (what do all participants accept?)
        - Shared evidence (what evidence is uncontested?)
        - Shared mechanisms (what causal processes are agreed upon?)
        - Shared conclusions (where do arguments converge?)
        - Remaining disagreement (what remains disputed?)

    Consensus remains explicit and traceable.
    """

    # Identity
    consensus_id: str                       # Unique identifier

    # Participating arguments
    participating_arguments: Tuple[str, ...]  # Argument IDs involved

    # Shared elements
    shared_assumptions: Tuple[Dict[str, Any], ...] = ()
    shared_evidence: Tuple[Dict[str, Any], ...] = ()
    shared_mechanisms: Tuple[Dict[str, Any], ...] = ()
    shared_conclusions: Tuple[Dict[str, Any], ...] = ()

    # Remaining disagreements
    remaining_disagreements: Tuple[Dict[str, Any], ...] = ()

    # Confidence in consensus (0.0 to 1.0)
    confidence: float = 0.0

    # Timing
    discovered_at_utc: float = field(default_factory=time.time)

    # Provenance
    origin_context: str = "unknown"

    @classmethod
    def create(
        cls,
        participating_arguments: List[str],
        origin_context: str = "unknown",
    ) -> ConsensusDiscovery:
        """Create a new consensus discovery record."""
        return cls(
            consensus_id=f"consensus_discovery:{uuid.uuid4().hex[:16]}",
            participating_arguments=tuple(participating_arguments),
            origin_context=origin_context,
        )

    def with_shared_assumption(self, assumption: Dict[str, Any]) -> ConsensusDiscovery:
        """Add a shared assumption."""
        return dataclass_replace(
            self,
            shared_assumptions=self.shared_assumptions + (assumption,),
        )

    def with_shared_evidence(self, evidence: Dict[str, Any]) -> ConsensusDiscovery:
        """Add shared evidence."""
        return dataclass_replace(
            self,
            shared_evidence=self.shared_evidence + (evidence,),
        )

    def with_shared_mechanism(self, mechanism: Dict[str, Any]) -> ConsensusDiscovery:
        """Add a shared mechanism."""
        return dataclass_replace(
            self,
            shared_mechanisms=self.shared_mechanisms + (mechanism,),
        )

    def with_shared_conclusion(self, conclusion: Dict[str, Any]) -> ConsensusDiscovery:
        """Add a shared conclusion."""
        return dataclass_replace(
            self,
            shared_conclusions=self.shared_conclusions + (conclusion,),
        )

    def with_remaining_disagreement(self, disagreement: Dict[str, Any]) -> ConsensusDiscovery:
        """Record a remaining disagreement."""
        return dataclass_replace(
            self,
            remaining_disagreements=self.remaining_disagreements + (disagreement,),
        )

    def with_confidence(self, confidence: float) -> ConsensusDiscovery:
        """Set the consensus confidence level."""
        return dataclass_replace(
            self,
            confidence=max(0.0, min(1.0, confidence)),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ConsensusDiscovery",
]