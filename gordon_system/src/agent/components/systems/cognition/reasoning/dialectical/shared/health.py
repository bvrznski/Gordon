# Dialectical Health - Phase 7.17
# ==============================

"""
Canonical Dialectical Health Contract.

Health metrics describe the state and performance of dialectical processes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DialecticalHealth:
    """
    Health metrics for a dialectical process.

    Metrics include:
        - Arguments analyzed (how many arguments processed?)
        - Counterarguments generated (how many counterarguments considered?)
        - Conflicts identified (how many conflicts found?)
        - Successful syntheses (how many syntheses completed?)
        - Consensus stability (how stable is the consensus?)
        - Validation success (did validation pass?)
    """

    # Identity
    health_id: str                          # Unique identifier

    # Process metrics
    arguments_analyzed: int = 0
    counterarguments_generated: int = 0
    conflicts_identified: int = 0
    successful_syntheses: int = 0
    consensus_stability_score: float = 0.0
    validation_success_count: int = 0

    # Timing
    measured_at_utc: float = field(default_factory=time.time)
    process_duration_seconds: Optional[float] = None

    # Provenance
    origin_context: str = "unknown"

    @property
    def overall_score(self) -> float:
        """Calculate overall health score (0.0 to 1.0)."""
        if self.arguments_analyzed == 0:
            return 0.0
        components = [
            min(1.0, self.counterarguments_generated / max(1, self.arguments_analyzed)),
            min(1.0, self.successful_syntheses / max(1, self.conflicts_identified)) if self.conflicts_identified > 0 else 0.5,
            self.consensus_stability_score,
            min(1.0, self.validation_success_count / max(1, self.arguments_analyzed)),
        ]
        return sum(components) / len(components)

    @classmethod
    def create(
        cls,
        origin_context: str = "unknown",
    ) -> DialecticalHealth:
        """Create a new health record."""
        return cls(
            health_id=f"dialectical_health:{uuid.uuid4().hex[:16]}",
            origin_context=origin_context,
        )

    def with_argument_analyzed(self) -> DialecticalHealth:
        """Record an analyzed argument."""
        return dataclass_replace(
            self,
            arguments_analyzed=self.arguments_analyzed + 1,
        )

    def with_counterargument_generated(self) -> DialecticalHealth:
        """Record a generated counterargument."""
        return dataclass_replace(
            self,
            counterarguments_generated=self.counterarguments_generated + 1,
        )

    def with_conflict_identified(self) -> DialecticalHealth:
        """Record an identified conflict."""
        return dataclass_replace(
            self,
            conflicts_identified=self.conflicts_identified + 1,
        )

    def with_synthesis_complete(self) -> DialecticalHealth:
        """Record a completed synthesis."""
        return dataclass_replace(
            self,
            successful_syntheses=self.successful_syntheses + 1,
        )

    def with_consensus_stability(self, stability: float) -> DialecticalHealth:
        """Set consensus stability score (0.0 to 1.0)."""
        return dataclass_replace(
            self,
            consensus_stability_score=max(0.0, min(1.0, stability)),
        )

    def with_validation_success(self) -> DialecticalHealth:
        """Record a successful validation."""
        return dataclass_replace(
            self,
            validation_success_count=self.validation_success_count + 1,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DialecticalHealth",
]