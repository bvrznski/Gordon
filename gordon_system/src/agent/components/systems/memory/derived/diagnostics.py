# Derived Memory Diagnostics - Phase 5.1.6 Canonical Implementation
# ================================================================
"""
Diagnostics: Runtime diagnostic information for derivations.

Purpose:
    Provide diagnostic information about derivation execution and health.
    
Diagnostic Categories:
    - Validation diagnostics (what failed, why)
    - Execution timing diagnostics
    - Resource usage diagnostics
    - Error tracking
    
Diagnostics Laws:
    DIAGNOSTICS-LAW-001: Diagnostics remain inspectable
    DIAGNOSTICS-LAW-002: Diagnostics preserve provenance
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# DERIVATION DIAGNOSTIC - A single diagnostic record
# =============================================================================


@dataclass(frozen=True)
class DerivationDiagnostic:
    """
    A single diagnostic record for a derivation.
    
    Fields:
        diagnostic_id:       Unique identifier for this diagnostic
        timestamp_utc:       When this diagnostic was recorded
        
        # Context
        derivation_id:       Which derivation?
        kind_:               What kind of derivation?
        
        # Diagnostic info
        severity:            critical / warning / info / debug
        category:            validation, timing, resource, error, etc.
        message:             Human-readable description
        
        # Details (for programmatic access)
        details:             Additional diagnostic data as dict
        
    Diagnostics Laws:
        DIAGNOSTICS-LAW-001: Diagnostics remain inspectable
    """
    
    diagnostic_id: str                      # Unique ID for this record
    
    timestamp_utc: float                    # When recorded
    
    # Context
    derivation_id: str                      # Which derivation?
    kind_: str                              # What kind of derivation?
    
    # Diagnostic info
    severity: str = "info"                  # critical, warning, info, debug
    category: str = "general"               # validation, timing, resource, error
    message: Optional[str] = None           # Human-readable description
    
    # Details (programmatic)
    details: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# DERIVATION DIAGNOSTIC BUILDER - Mutable builder for diagnostics
# =============================================================================


class DerivationDiagnosticBuilder:
    """
    Mutable builder for constructing diagnostic records.
    
    Allows step-by-step construction before producing an immutable record.
    """
    
    def __init__(
        self,
        derivation_id: str,
        kind_: str,
    ):
        """Initialize the builder."""
        self._diagnostic_id = f"diag:{uuid.uuid4().hex[:12]}"
        self._timestamp_utc = time.time()
        
        # Context
        self._derivation_id = derivation_id
        self._kind_ = kind_
        
        # Info
        self._severity = "info"
        self._category = "general"
        self._message: Optional[str] = None
        
        # Details
        self._details: Dict[str, Any] = {}
    
    def set_severity(self, severity: str) -> "DerivationDiagnosticBuilder":
        """Set the diagnostic severity."""
        valid_severities = ("critical", "warning", "info", "debug")
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity: {severity}")
        self._severity = severity
        return self
    
    def set_category(self, category: str) -> "DerivationDiagnosticBuilder":
        """Set the diagnostic category."""
        self._category = category
        return self
    
    def set_message(self, message: str) -> "DerivationDiagnosticBuilder":
        """Set the human-readable message."""
        self._message = message
        return self
    
    def add_detail(self, key: str, value: Any) -> "DerivationDiagnosticBuilder":
        """Add a detail to the diagnostic."""
        self._details[key] = value
        return self
    
    def build(self) -> DerivationDiagnostic:
        """
        Build an immutable DerivationDiagnostic from this builder.
        
        Returns:
            New DerivationDiagnostic with all settings applied
        """
        import uuid
        return DerivationDiagnostic(
            diagnostic_id=self._diagnostic_id,
            timestamp_utc=self._timestamp_utc,
            derivation_id=self._derivation_id,
            kind_=self._kind_,
            severity=self._severity,
            category=self._category,
            message=self._message,
            details=dict(self._details),
        )


# =============================================================================
# DERIVATION DIAGNOSTICS - Collection of diagnostic records
# =============================================================================


@dataclass(frozen=True)
class DerivationDiagnostics:
    """
    Collection of diagnostic records for a derivation.
    
    Fields:
        diagnostics_id:      Unique identifier for this collection
        derivation_id:       Which derivation?
        
        # Diagnostics content
        records:             Individual diagnostic records
        errors:              Error-level diagnostics
        warnings:            Warning-level diagnostics
        
        # Timing
        start_time_utc:      When did monitoring start?
        end_time_utc:        When did monitoring end?
        
    Diagnostics Laws:
        DIAGNOSTICS-LAW-001: Diagnostics remain inspectable
    """
    
    diagnostics_id: str                     # Unique ID for this collection
    
    derivation_id: str                      # Which derivation?
    
    # Content
    records: Tuple[DerivationDiagnostic, ...]  # All diagnostic records
    
    # Categorized
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timing
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: float = field(default_factory=time.time)


# =============================================================================
# DERIVATION DIAGNOSTICS BUILDER - Mutable builder for diagnostics collection
# =============================================================================


class DerivationDiagnosticsBuilder:
    """
    Mutable builder for constructing diagnostic collections.
    
    Allows incremental aggregation before producing immutable collection.
    """
    
    def __init__(self, derivation_id: str):
        """Initialize the builder."""
        self._diagnostics_id = f"diags:{uuid.uuid4().hex[:12]}"
        self._derivation_id = derivation_id
        
        # Records
        self._records: List[DerivationDiagnostic] = []
        
        # Timing
        self._start_time_utc = time.time()
        self._end_time_utc = time.time()
    
    def add_record(self, record: DerivationDiagnostic) -> "DerivationDiagnosticsBuilder":
        """Add a diagnostic record."""
        self._records.append(record)
        return self
    
    def add_error(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> "DerivationDiagnosticsBuilder":
        """Add an error-level diagnostic."""
        import uuid
        record = DerivationDiagnostic(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:12]}",
            timestamp_utc=time.time(),
            derivation_id=self._derivation_id,
            kind_="unknown",
            severity="error",
            category="error",
            message=message,
            details=dict(details) if details else {},
        )
        self._records.append(record)
        return self
    
    def add_warning(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> "DerivationDiagnosticsBuilder":
        """Add a warning-level diagnostic."""
        import uuid
        record = DerivationDiagnostic(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:12]}",
            timestamp_utc=time.time(),
            derivation_id=self._derivation_id,
            kind_="unknown",
            severity="warning",
            category="warning",
            message=message,
            details=dict(details) if details else {},
        )
        self._records.append(record)
        return self
    
    def update_end_time(self, end_time: float = None) -> "DerivationDiagnosticsBuilder":
        """Update the end time."""
        self._end_time_utc = end_time or time.time()
        return self
    
    def build(self) -> DerivationDiagnostics:
        """
        Build an immutable DerivationDiagnostics from this builder.
        
        Returns:
            New DerivationDiagnostics with all settings applied
        """
        # Extract errors and warnings as separate tuples
        errors = tuple(
            r.message or "" for r in self._records if r.severity == "error"
        )
        warnings = tuple(
            r.message or "" for r in self._records if r.severity == "warning"
        )
        
        return DerivationDiagnostics(
            diagnostics_id=self._diagnostics_id,
            derivation_id=self._derivation_id,
            records=tuple(self._records),
            errors=errors,
            warnings=warnings,
            start_time_utc=self._start_time_utc,
            end_time_utc=self._end_time_utc,
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Diagnostic record
    "DerivationDiagnostic",
    
    # Builder
    "DerivationDiagnosticBuilder",
    
    # Diagnostics collection
    "DerivationDiagnostics",
    
    # Collection builder
    "DerivationDiagnosticsBuilder",
]