# Dialectical Construction Contracts - Phase 7.17
# ================================================

"""
Canonical Argument Construction and Counterargument Analysis Contracts.

Argument construction follows a deterministic pipeline from evidence to publication.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ArgumentConstruction:
    """
    A deterministic argument construction process.

    Pipeline flow:
        Evidence -> Claim Construction -> Premise Identification ->
        Support Analysis -> Argument Publication -> Validation -> Publication

    All stages remain explicit and traceable.
    """

    # Identity
    construction_id: str                    # Unique identifier

    # Construction strategy (how was the argument built?)
    construction_strategy: str              # e.g., "deductive", "evidential", "inference_to_best_explanation"

    # Resulting argument
    resulting_argument: Dict[str, Any]      # The constructed argument

    # Diagnostics
    diagnostics: Tuple[Dict[str, Any], ...] = ()

    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None

    # Provenance
    source_evidence: Tuple[Dict[str, Any], ...] = ()
    origin_context: str = "unknown"

    @property
    def duration_seconds(self) -> float:
        """Calculate construction duration."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        return time.time() - self.started_at_utc

    @classmethod
    def create(
        cls,
        construction_strategy: str,
        resulting_argument: Dict[str, Any],
        source_evidence: Optional[List[Dict[str, Any]]] = None,
        origin_context: str = "unknown",
    ) -> ArgumentConstruction:
        """Create a new argument construction record."""
        return cls(
            construction_id=f"argument_construction:{uuid.uuid4().hex[:16]}",
            construction_strategy=construction_strategy,
            resulting_argument=resulting_argument,
            source_evidence=tuple(source_evidence or []),
            origin_context=origin_context,
        )

    def with_diagnostic(self, diagnostic: Dict[str, Any]) -> ArgumentConstruction:
        """Add a diagnostic to the record."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + (diagnostic,),
        )

    def complete(self) -> ArgumentConstruction:
        """Mark construction as completed."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )


@dataclass(frozen=True)
class CounterArgumentAnalysis:
    """
    Analysis of a counterargument against an argument.

    Evaluates:
        - Logical weaknesses
        - Unsupported assumptions
        - Missing evidence
        - Alternative interpretations
        - Constraint violations
        - Boundary conditions

    Analysis remains explicit and traceable.
    """

    # Identity
    analysis_id: str                        # Unique identifier

    # Challenged argument
    challenged_argument: Dict[str, Any]     # The original argument being analyzed

    # Counterargument details
    counterargument: Dict[str, Any]         # The counterargument being applied

    # Justification (why is this a valid criticism?)
    justification: str                      # Explanation of the analysis

    # Supporting evidence for the counterargument
    supporting_evidence: Tuple[Dict[str, Any], ...] = ()

    # Timing
    analyzed_at_utc: float = field(default_factory=time.time)

    # Provenance
    origin_context: str = "unknown"

    @classmethod
    def create(
        cls,
        challenged_argument: Dict[str, Any],
        counterargument: Dict[str, Any],
        justification: str,
        supporting_evidence: Optional[List[Dict[str, Any]]] = None,
        origin_context: str = "unknown",
    ) -> CounterArgumentAnalysis:
        """Create a new counterargument analysis record."""
        return cls(
            analysis_id=f"counterargument_analysis:{uuid.uuid4().hex[:16]}",
            challenged_argument=challenged_argument,
            counterargument=counterargument,
            justification=justification,
            supporting_evidence=tuple(supporting_evidence or []),
            origin_context=origin_context,
        )

    def with_supporting_evidence(self, evidence: Dict[str, Any]) -> CounterArgumentAnalysis:
        """Add supporting evidence to the analysis."""
        return dataclass_replace(
            self,
            supporting_evidence=self.supporting_evidence + (evidence,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ArgumentConstruction",
    "CounterArgumentAnalysis",
]