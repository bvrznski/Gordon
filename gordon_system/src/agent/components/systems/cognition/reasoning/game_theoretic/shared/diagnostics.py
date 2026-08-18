# Diagnostics - Phase 7.43
# ======================

"""
Canonical Diagnostic Record definitions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DiagnosticRecord:
    """A single diagnostic record."""
    
    record_id: str                          # Unique identifier
    
    timestamp_utc: float                    # When recorded
    severity: str = "info"                  # info, warning, error
    category: str = ""                      # e.g., "equilibrium", "payoff"
    message: str = ""                       # Diagnostic message
    context: Dict[str, Any] = {}            # Additional context


@dataclass(frozen=True)
class Diagnostics:
    """
    Complete diagnostics for a game session.
    
    Diagnostics remain inspectable for debugging and analysis.
    """
    
    # Identity
    diagnostics_identity: str               # Unique identifier
    
    # Records
    records: Tuple[DiagnosticRecord, ...] = ()  # All diagnostic records
    
    # Summary
    error_count: int = 0                    # Count of errors
    warning_count: int = 0                  # Count of warnings
    info_count: int = 0                     # Count of info messages
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_session_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        source_session_id: Optional[str] = None,
    ) -> Diagnostics:
        """Create new diagnostics."""
        return cls(
            diagnostics_identity=f"diagnostics:{uuid.uuid4().hex[:16]}",
            source_session_id=source_session_id,
        )
    
    def add_record(self, record: DiagnosticRecord) -> Diagnostics:
        """Add a diagnostic record."""
        # Update counts
        new_error = self.error_count + (1 if record.severity == "error" else 0)
        new_warning = self.warning_count + (1 if record.severity == "warning" else 0)
        new_info = self.info_count + (1 if record.severity == "info" else 0)
        
        return dataclass_replace(
            self,
            records=self.records + (record,),
            error_count=new_error,
            warning_count=new_warning,
            info_count=new_info,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DiagnosticRecord",
    "Diagnostics",
]
