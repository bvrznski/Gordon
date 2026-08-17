# Temporal Diagnostics - Phase 7.8
# ================================

"""
Canonical Temporal Diagnostics.

Diagnostics provide detailed operational insights into temporal reasoning processes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DiagnosticType(Enum):
    """Types of diagnostics."""
    
    EVENT_ORDERING = "event_ordering"           # Event ordering diagnostics
    INTERVAL_ANALYSIS = "interval_analysis"     # Interval analysis diagnostics
    CONSTRAINT_CHECK = "constraint_check"       # Constraint validation diagnostics
    GRAPH_STRUCTURE = "graph_structure"         # Chronology graph structure
    CONCURRENCY_ISSUE = "concurrency_issue"     # Concurrency-related diagnostics


@dataclass(frozen=True)
class TemporalDiagnostics:
    """
    Diagnostics for temporal reasoning operations.
    
    Provides detailed operational insights into temporal reasoning processes.
    """
    
    # Identity
    diagnostics_id: str                     # Unique diagnostics identifier
    
    # Diagnostic type
    diagnostic_type: DiagnosticType         # What kind of diagnostic?
    
    # Detailed information
    details: Tuple[str, ...] = ()           # Diagnostic details
    
    # Severity (0-1 scale)
    severity: float = 0.0                   # 0.0 = no issue, 1.0 = critical
    
    # Recommendation
    recommendation: Optional[str] = None    # Suggested action
    
    # Provenance
    source_diagnostics_id: Optional[str] = None   # If derived from another check
    origin_context: str = "unknown"               # Where did diagnostics originate?
    
    @property
    def has_details(self) -> bool:
        """Check if detailed information is available."""
        return len(self.details) > 0
    
    @property
    def is_critical(self) -> bool:
        """Check if this diagnostic is critical."""
        return self.severity >= 0.8
    
    @property
    def is_warning(self) -> bool:
        """Check if this diagnostic is a warning."""
        return 0.3 <= self.severity < 0.8


@dataclass(frozen=True)
class TemporalDiagnosticsIdentity:
    """
    Immutable identity for temporal diagnostics.
    
    Allows replay and verification of diagnostic results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    diagnostics_number: int = 1               # For repeated checks
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, diagnostics_number: int = 1) -> TemporalDiagnosticsIdentity:
        """Create a new temporal diagnostics identity."""
        return cls(
            semantic_identity=semantic_identity,
            diagnostics_number=diagnostics_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TemporalDiagnostics",
    "TemporalDiagnosticsIdentity",
    "DiagnosticType",
]