# Experimental Reasoning - Diagnostics
# =====================================

"""
Canonical Diagnostic contracts.

Diagnostics provide diagnostic information about experimental reasoning processes.
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
    A single diagnostic record for experimental reasoning.
    
    Includes the diagnostic category, severity, message, and context.
    """
    
    # Identity
    diagnostic_id: str                          # Unique identifier
    
    # Diagnostic details
    category: str = "general"                   # e.g., "design", "intervention", "measurement"
    level: str = "info"                         # "debug", "info", "warning", "error"
    message: str = ""                           # Human-readable diagnostic message
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context data
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_error(self) -> bool:
        """Check if this is an error-level diagnostic."""
        return self.level == "error"
    
    @property
    def is_warning(self) -> bool:
        """Check if this is a warning-level diagnostic."""
        return self.level == "warning"


@dataclass(frozen=True)
class DiagnosticsSummary:
    """
    Summary of all diagnostics for an experimental reasoning session.
    
    Includes counts, categories, and timing information.
    """
    
    # Identity
    summary_id: str                             # Unique identifier
    
    # Session info
    experiment_identity: str                    # Related experiment (if any)
    start_time_utc: float = field(default_factory=time.time)  # When diagnostics started
    
    # Diagnostics
    diagnostic_records: Tuple[DiagnosticRecord, ...] = ()
    
    @property
    def total_count(self) -> int:
        """Get total number of diagnostic records."""
        return len(self.diagnostic_records)
    
    @property
    def error_count(self) -> int:
        """Get number of error diagnostics."""
        return sum(1 for d in self.diagnostic_records if d.is_error)
    
    @property
    def warning_count(self) -> int:
        """Get number of warning diagnostics."""
        return sum(1 for d in self.diagnostic_records if d.is_warning)
    
    @property
    def info_count(self) -> int:
        """Get number of info-level diagnostics."""
        return sum(1 for d in self.diagnostic_records if not (d.is_error or d.is_warning))
    
    @property
    def categories(self) -> Dict[str, int]:
        """Get diagnostic counts by category."""
        counts: Dict[str, int] = {}
        for record in self.diagnostic_records:
            counts[record.category] = counts.get(record.category, 0) + 1
        return counts
    
    @classmethod
    def create(
        cls,
        experiment_identity: str = "unknown",
        diagnostics: List[DiagnosticRecord] = None,
    ) -> DiagnosticsSummary:
        """Create a new diagnostics summary."""
        return cls(
            summary_id=f"diagnostics:{uuid.uuid4().hex[:16]}",
            experiment_identity=experiment_identity,
            diagnostic_records=tuple(diagnostics or []),
        )
    
    def merge(self, other: DiagnosticsSummary) -> DiagnosticsSummary:
        """Merge another diagnostics summary into this one."""
        return DiagnosticsSummary(
            summary_id=self.summary_id,
            experiment_identity=self.experiment_identity,
            start_time_utc=min(self.start_time_utc, other.start_time_utc),
            diagnostic_records=self.diagnostic_records + other.diagnostic_records,
        )


@dataclass(frozen=True)
class DiagnosticReport:
    """
    Complete diagnostic report for an experimental reasoning session.
    
    Includes all diagnostics and analysis.
    """
    
    # Identity
    report_id: str                              # Unique identifier
    
    # Session info
    experiment_identity: str                    # Related experiment
    generated_at_utc: float = field(default_factory=time.time)
    
    # Summary statistics
    total_diagnostics: int = 0
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    
    # Diagnostics by category
    diagnostics_by_category: Dict[str, int] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        experiment_identity: str,
        summary: DiagnosticsSummary,
    ) -> DiagnosticReport:
        """Create a diagnostic report from a summary."""
        return cls(
            report_id=f"diag_report:{uuid.uuid4().hex[:16]}",
            experiment_identity=experiment_identity,
            total_diagnostics=summary.total_count,
            errors=summary.error_count,
            warnings=summary.warning_count,
            infos=summary.info_count,
            diagnostics_by_category=summary.categories,
        )


__all__ = [
    "DiagnosticRecord",
    "DiagnosticsSummary",
    "DiagnosticReport",
]