# Explanation Diagnostics - Phase 7.14
# =====================================

"""
Diagnostics for explanatory reasoning.

Provides diagnostic information about explanation sessions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DiagnosticRecord:
    """
    A single diagnostic record.
    
    Diagnostics include timing, resource usage, quality metrics, and error details.
    """
    
    # Identity
    diagnostic_id: str                        # Unique identifier
    
    # Timestamps
    recorded_at_utc: float = field(default_factory=time.time)
    
    # Type
    diagnostic_type: str = "info"             # info, warning, error, metric
    
    # Content
    message: str = ""                         # What happened?
    context: Dict[str, Any] = field(default_factory=dict)  # Additional details
    
    @classmethod
    def create(
        cls,
        message: str,
        diagnostic_type: str = "info",
        context: Optional[Dict[str, Any]] = None,
    ) -> "DiagnosticRecord":
        """Create a new diagnostic record."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type=diagnostic_type,
            message=message,
            context=context or {},
        )


@dataclass(frozen=True)
class ExplanationDiagnostics:
    """
    Diagnostics for an explanation session.
    
    Contains timing, quality metrics, and other operational information.
    """
    
    # Identity
    diagnostics_id: str                       # Unique identifier
    
    # Session info
    semantic_identity: str                    # Stable identity across runs
    diagnostic_records: Tuple[DiagnosticRecord, ...]
    
    # Timing summary
    total_duration_seconds: float = 0.0       # Total session duration
    evidence_collection_time: float = 0.0     # Time spent collecting evidence
    reasoning_time: float = 0.0               # Time spent reasoning
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        records: List[DiagnosticRecord],
    ) -> "ExplanationDiagnostics":
        """Create new diagnostics."""
        return cls(
            diagnostics_id=f"expl_diag:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            diagnostic_records=tuple(records),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DiagnosticRecord",
    "ExplanationDiagnostics",
]