# Spatial Diagnostics - Phase 7.9
# ===============================

"""
Canonical Spatial Diagnostics.

Diagnostics provide detailed information about spatial reasoning execution,
including performance metrics, intermediate results, and error details.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class DiagnosticRecord:
    """
    Individual diagnostic record.
    
    Each record documents one aspect of spatial reasoning diagnostics.
    """
    
    # Identity
    record_id: str                          # Unique identifier
    
    # Record type
    record_type: str                        # e.g., "performance", "warning", "error"
    
    # Timestamp
    timestamp_utc: float                    # When was it recorded?
    
    # Details
    message: str = ""                       # Diagnostic message
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional data
    
    # Source
    source_module: str = ""                 # Which module generated this?


@dataclass(frozen=True)
class SpatialDiagnostics:
    """
    Diagnostics for spatial reasoning execution.
    
    Contains timing, performance, and detailed execution information.
    """
    
    # Identity
    diagnostics_id: str                     # Unique identifier
    
    # Timing info
    total_duration_seconds: float = 0.0     # Total reasoning time
    stages: Dict[str, float] = field(default_factory=dict)  # Per-stage times
    
    # Performance metrics
    entities_processed: int = 0             # Entities handled
    transformations_applied: int = 0        # Transformations executed
    validations_run: int = 0                # Validations performed
    
    # Warnings and errors
    warnings: Tuple[str, ...] = ()          # Warning messages
    errors: Tuple[str, ...] = ()            # Error messages
    
    # Detailed records
    records: Tuple[DiagnosticRecord, ...] = ()
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def has_warnings(self) -> bool:
        """Check if any warnings were recorded."""
        return len(self.warnings) > 0
    
    @property
    def has_errors(self) -> bool:
        """Check if any errors were recorded."""
        return len(self.errors) > 0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> SpatialDiagnostics:
        """Create a new diagnostics record."""
        return cls(
            diagnostics_id=f"diagnostics:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def add_timing(self, stage: str, duration_seconds: float) -> SpatialDiagnostics:
        """Return new diagnostics with timing for a stage."""
        new_stages = dict(self.stages)
        new_stages[stage] = duration_seconds
        return dataclass_replace(
            self,
            stages=new_stages,
            total_duration_seconds=self.total_duration_seconds + duration_seconds,
        )
    
    def add_warning(self, warning: str) -> SpatialDiagnostics:
        """Return new diagnostics with a warning."""
        return dataclass_replace(
            self,
            warnings=self.warnings + (warning,),
        )
    
    def add_error(self, error: str) -> SpatialDiagnostics:
        """Return new diagnostics with an error."""
        return dataclass_replace(
            self,
            errors=self.errors + (error,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SpatialDiagnostics", 
    "DiagnosticRecord",
]