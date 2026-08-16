# Temporal Alignment - Phase 5.2.2
# ================================

"""
Temporal Alignment: Establishes comparable semantic timing across evidence streams.

Temporal alignment maps timestamps from different sources into a common
semantic time reference frame.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# TEMPORAL ALIGNMENT - Time-based evidence mapping
# =============================================================================


@dataclass(frozen=True)
class TemporalAlignment:
    """
    Alignment of temporal references across evidence streams.
    
    Fields:
        alignment_identity:      Unique identifier for this alignment
        source_artifacts:        Which artifacts are being aligned?
        source_time_domains:     Time domains of each source (e.g., "wall_clock", "monotonic")
        acquisition_times:       Original acquisition timestamps
        observed_times:          Observed times from the evidence
        aligned_times:           Aligned semantic time values
        latency_estimates:       Estimated processing latencies
        ordering_constraints:    Temporal ordering relationships between sources
        missing_intervals:       Periods where evidence was not available
        residual_error:          Residual error after alignment (seconds)
        confidence:              Confidence in the alignment
        uncertainty:             Known limitations of this alignment
    """
    
    alignment_identity: str             # Unique ID
    
    source_artifacts: Tuple[str, ...]  # Artifact IDs being aligned
    
    source_time_domains: Tuple[str, ...]  # e.g., "wall_clock", "monotonic", "process_local"
    
    acquisition_times: Tuple[float, ...]  # Original timestamps (seconds since epoch)
    observed_times: Tuple[float, ...]     # Observed times from evidence
    aligned_times: Tuple[float, ...]      # Aligned semantic times
    
    latency_estimates: Dict[str, float] = field(default_factory=dict)  # source -> estimated_latency
    
    ordering_constraints: Tuple["PerceptualOrderingConstraint", ...] = field(default_factory=tuple)
    
    missing_intervals: Tuple[Tuple[float, float], ...] = field(default_factory=tuple)  # (start, end) pairs
    
    residual_error: float = 0.0         # Seconds of residual error
    confidence: float = 0.5            # Alignment confidence (0.0-1.0)
    uncertainty: float = 0.3          # Alignment uncertainty (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Alignment history
    
    @property
    def is_aligned(self) -> bool:
        """Check if all sources are aligned."""
        return len(self.aligned_times) > 0 and self.residual_error < 1.0  # Within 1 second
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alignment to dictionary."""
        return {
            "alignment_identity": self.alignment_identity,
            "source_artifacts": list(self.source_artifacts),
            "source_time_domains": list(self.source_time_domains),
            "acquisition_times": list(self.acquisition_times),
            "observed_times": list(self.observed_times),
            "aligned_times": list(self.aligned_times),
            "latency_estimates": dict(self.latency_estimates),
            "ordering_constraints": [c.to_dict() for c in self.ordering_constraints],
            "missing_intervals": [list(i) for i in self.missing_intervals],
            "residual_error": self.residual_error,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }
    
    @classmethod
    def create(
        cls,
        artifact_ids: List[str],
        time_domain: str = "wall_clock",
        acquisition_times: Optional[List[float]] = None,
        aligned_times: Optional[List[float]] = None,
    ) -> "TemporalAlignment":
        """Create a new temporal alignment."""
        return cls(
            alignment_identity=f"temporal:{uuid.uuid4().hex[:16]}",
            source_artifacts=tuple(artifact_ids),
            source_time_domains=(time_domain,) * len(artifact_ids) if artifact_ids else (),
            acquisition_times=tuple(acquisition_times or []),
            observed_times=tuple(acquisition_times or []),  # Observed = acquisition
            aligned_times=tuple(aligned_times or (acquisition_times or [])),
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemporalAlignment":
        """Create alignment from dictionary."""
        return cls(
            alignment_identity=data.get("alignment_identity", str(uuid.uuid4())),
            source_artifacts=tuple(data.get("source_artifacts", [])),
            source_time_domains=tuple(data.get("source_time_domains", ["wall_clock"])),
            acquisition_times=tuple(data.get("acquisition_times", [])),
            observed_times=tuple(data.get("observed_times", [])),
            aligned_times=tuple(data.get("aligned_times", [])),
            latency_estimates=dict(data.get("latency_estimates", {})),
            missing_intervals=tuple(
                tuple(i) for i in data.get("missing_intervals", [])
            ),
            residual_error=float(data.get("residual_error", 0.0)),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.3)),
        )


# =============================================================================
# PERCEPTUAL ORDERING CONSTRAINT - Temporal relationship between events
# =============================================================================


@dataclass(frozen=True)
class PerceptualOrderingConstraint:
    """
    Ordering constraint between two perceptual events.
    
    Fields:
        constraint_identity:     Unique identifier for this constraint
        source_a:                First event ID
        source_b:                Second event ID
        ordering_relation:       How are these related temporally?
        tolerance_seconds:       Temporal tolerance for SIMULTANEOUS relation
        confidence:              Confidence in this ordering
    """
    
    constraint_identity: str            # Unique ID
    
    source_a: str                      # First event
    source_b: str                      # Second event
    
    ordering_relation: str = "ORDER_UNKNOWN"  # See OrderingRelation enum
    
    tolerance_seconds: float = 0.1     # Tolerance for simultaneity
    
    confidence: float = 0.5           # Confidence in ordering (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # History
    
    @property
    def is_before(self) -> bool:
        """Check if source_a occurs before source_b."""
        return self.ordering_relation == "BEFORE"
    
    @property
    def is_after(self) -> bool:
        """Check if source_a occurs after source_b."""
        return self.ordering_relation == "AFTER"
    
    @property
    def is_simultaneous(self) -> bool:
        """Check if events are simultaneous within tolerance."""
        return self.ordering_relation in ("SIMULTANEOUS_WITHIN_TOLERANCE",)
    
    @classmethod
    def before(cls, source_a: str, source_b: str) -> "PerceptualOrderingConstraint":
        """Create a constraint where A occurs before B."""
        return cls(
            constraint_identity=f"order:{uuid.uuid4().hex[:16]}",
            source_a=source_a,
            source_b=source_b,
            ordering_relation="BEFORE",
            confidence=0.95,
        )
    
    @classmethod
    def simultaneous(
        cls,
        source_a: str,
        source_b: str,
        tolerance: float = 0.1,
    ) -> "PerceptualOrderingConstraint":
        """Create a constraint where events are simultaneous."""
        return cls(
            constraint_identity=f"order:{uuid.uuid4().hex[:16]}",
            source_a=source_a,
            source_b=source_b,
            ordering_relation="SIMULTANEOUS_WITHIN_TOLERANCE",
            tolerance_seconds=tolerance,
            confidence=0.9,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert constraint to dictionary."""
        return {
            "constraint_identity": self.constraint_identity,
            "source_a": self.source_a,
            "source_b": self.source_b,
            "ordering_relation": self.ordering_relation,
            "tolerance_seconds": self.tolerance_seconds,
            "confidence": self.confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptualOrderingConstraint":
        """Create constraint from dictionary."""
        return cls(
            constraint_identity=data.get("constraint_identity", str(uuid.uuid4())),
            source_a=data.get("source_a", ""),
            source_b=data.get("source_b", ""),
            ordering_relation=data.get("ordering_relation", "ORDER_UNKNOWN"),
            tolerance_seconds=float(data.get("tolerance_seconds", 0.1)),
            confidence=float(data.get("confidence", 0.5)),
        )