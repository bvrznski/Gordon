# Decision Diagnostics - Phase 7.19
# ================================

"""
Canonical Decision Diagnostics Contract.

Diagnostics provide detailed operational insights about decision sessions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DecisionDiagnostics:
    """
    Detailed diagnostics for a decision session.
    
    Diagnostics provide operational insights without modifying decisions.
    """
    
    # Identity
    diagnostics_id: str                     # Unique identifier
    
    # Session context
    evaluated_session: str                  # Session ID being diagnosed
    
    # Performance metrics
    evaluation_duration_seconds: float = 0.0  # How long did evaluation take?
    options_processed_count: int = 0        # Options processed
    utility_calculations_count: int = 0     # Utility calculations performed
    
    # Quality indicators
    data_quality_score: float = 1.0         # Quality of input data (0-1)
    evidence_completeness: float = 1.0      # Completeness of evidence (0-1)
    
    # Warnings
    warnings: Tuple[str, ...] = ()          # Any warnings during evaluation
    
    # Provenance
    recorded_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(cls, evaluated_session: str) -> DecisionDiagnostics:
        """Create new diagnostics for a session."""
        return cls(
            diagnostics_id=f"decision_diagnostics:{uuid.uuid4().hex[:16]}",
            evaluated_session=evaluated_session,
        )
    
    def add_warning(self, warning: str) -> DecisionDiagnostics:
        """Return a copy with an additional warning."""
        new_warnings = list(self.warnings)
        new_warnings.append(warning)
        return dataclass_replace(
            self,
            warnings=tuple(new_warnings),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DecisionDiagnostics",
]