# Hypothetical Diagnostics - Phase 7.15 Part 2
# =============================================

"""
Canonical Diagnostic Contract.

Diagnostics provide operational insights into hypothetical reasoning performance.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DiagnosticType(Enum):
    """Types of diagnostics."""
    
    HYPOTHESIS_GEN = "hypothesis_generation"  # Generation performance
    ASSUMPTION_ANALYSIS = "assumption_analysis"  # Assumption tracking
    SPACE_EXPANSION = "space_expansion"       # Possibility space growth
    SCENARIO_COVERAGE = "scenario_coverage"   # Scenario diversity
    VALIDATION_RATE = "validation_rate"       # Validation performance


@dataclass(frozen=True)
class HypotheticalDiagnostics:
    """
    Diagnostic metrics for hypothetical reasoning.
    
    Diagnostics remain independent and inspectable at all times.
    """
    
    # Identity
    diagnostics_id: str                       # Unique identifier
    
    # Metrics by category
    hypothesis_generation_metrics: Dict[str, Any] = field(default_factory=dict)
    assumption_analysis_metrics: Dict[str, Any] = field(default_factory=dict)
    space_expansion_metrics: Dict[str, Any] = field(default_factory=dict)
    scenario_coverage_metrics: Dict[str, Any] = field(default_factory=dict)
    validation_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.end_time_utc:
            return self.end_time_utc - self.start_time_utc
        return time.time() - self.start_time_utc
    
    @classmethod
    def create(
        cls,
        hypothesis_metrics: Optional[Dict[str, Any]] = None,
        assumption_metrics: Optional[Dict[str, Any]] = None,
        space_metrics: Optional[Dict[str, Any]] = None,
        scenario_metrics: Optional[Dict[str, Any]] = None,
        validation_metrics: Optional[Dict[str, Any]] = None,
    ) -> HypotheticalDiagnostics:
        """Create a new diagnostics record."""
        return cls(
            diagnostics_id=f"diagnostics:{uuid.uuid4().hex[:16]}",
            hypothesis_generation_metrics=hypothesis_metrics or {},
            assumption_analysis_metrics=assumption_metrics or {},
            space_expansion_metrics=space_metrics or {},
            scenario_coverage_metrics=scenario_metrics or {},
            validation_metrics=validation_metrics or {},
        )


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Complete diagnostics record for a reasoning session.
    
    Allows independent inspection of reasoning quality and performance.
    """
    
    # Identity
    record_id: str                            # Unique identifier
    
    # Session reference
    reasoning_session_id: str                 # Which session?
    
    # Diagnostics
    diagnostic_sessions: Tuple[HypotheticalDiagnostics, ...] = ()  # All diagnostics
    
    @property
    def total_diagnostics(self) -> int:
        """Return number of diagnostic sessions."""
        return len(self.diagnostic_sessions)
    
    @classmethod
    def create(
        cls,
        reasoning_session_id: str,
        diagnostic_sessions: Optional[List[HypotheticalDiagnostics]] = None,
    ) -> DiagnosticsRecord:
        """Create a new diagnostics record."""
        return cls(
            record_id=f"diag_record:{uuid.uuid4().hex[:16]}",
            reasoning_session_id=reasoning_session_id,
            diagnostic_sessions=tuple(diagnostic_sessions or []),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DiagnosticType",
    "HypotheticalDiagnostics",
    "DiagnosticsRecord",
]