# Auditing Domain - Governance Subsystem

"""
Auditing: Governance history maintenance for Memory.

The auditing domain:
    
    - Records every governance decision
    - Maintains immutable audit history
    - Preserves provenance and timestamps
    - Supports inspection of all decisions
    
Audit Laws:

    AUDIT-LAW-001: Every governance evaluation produces an audit record
    AUDIT-LAW-002: Audit history is immutable
    AUDIT-LAW-003: Audit records preserve provenance
    AUDIT-LAW-004: Audit records preserve timestamps
    AUDIT-LAW-005: Audit records preserve supporting evidence
    AUDIT-LAW-006: Audit is append-only
    AUDIT-LAW-007: Audit history remains inspectable
    AUDIT-LAW-008: Audit behavior remains deterministic

Audit Records Include:
    
    - Evaluation type (integrity, compliance, certification)
    - Timestamp of evaluation
    - Evidence supporting decisions
    - Source artifacts involved
    - Revision ID at time of evaluation
    
Anti-Patterns Rejected:
    
    - Mutable audit logs
    - Hidden audit records
    - Non-deterministic auditing
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


# =============================================================================
# AUDIT RECORD - Immutable governance history entry
# =============================================================================


@dataclass(frozen=True)
class AuditRecord:
    """
    An immutable audit record for a governance decision.
    
    Every governance evaluation produces an audit record that can be:
        - Inspected by authorized parties
        - Traced back to original artifacts
        - Verified through evidence records
        
    Fields:
        audit_id:         Unique identifier for this audit record
        event_type:       Type of governance event (integrity_check, etc.)
        timestamp_utc:    When the event occurred
        details:          Event-specific information
        evidence_ids:     IDs of evidence records created
        revision_id:      Memory system revision at time of event
    """
    
    audit_id: str                           # Unique identifier
    event_type: str                         # Type of governance event
    timestamp_utc: float                   # When event occurred
    
    details: Dict[str, Any]                # Event-specific information
    evidence_ids: Tuple[str, ...] = field(default_factory=tuple)  # Evidence IDs
    revision_id: str = ""                  # Memory system revision
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit record to dictionary representation."""
        return {
            "audit_id": self.audit_id,
            "event_type": self.event_type,
            "timestamp_utc": self.timestamp_utc,
            "details": dict(self.details),
            "evidence_ids": list(self.evidence_ids),
            "revision_id": self.revision_id,
        }


# =============================================================================
# AUDIT LOG - Immutable audit history
# =============================================================================


@dataclass(frozen=True)
class AuditLog:
    """
    An immutable audit log containing all governance events.
    
    The audit log is append-only and cannot be modified once created.
    
    Fields:
        log_id:           Unique identifier for this log
        entries:          All audit records in order
        start_time_utc:   When logging started
        end_time_utc:     When logging ended
        
    Properties:
        entry_count:      Total number of audit entries
        event_types:      Set of all event types recorded
        is_complete:      Whether the log represents a complete evaluation
    """
    
    log_id: str                             # Unique identifier
    entries: Tuple[AuditRecord, ...]       # All audit records in order
    
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: float = field(default_factory=time.time)
    
    @property
    def entry_count(self) -> int:
        """Get total number of audit entries."""
        return len(self.entries)
    
    @property
    def event_types(self) -> Tuple[str, ...]:
        """Get set of all event types recorded."""
        return tuple(set(e.event_type for e in self.entries))
    
    def get_events_by_type(self, event_type: str) -> Tuple[AuditRecord, ...]:
        """Get all entries of a specific event type."""
        return tuple(e for e in self.entries if e.event_type == event_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary representation."""
        return {
            "log_id": self.log_id,
            "entry_count": len(self.entries),
            "event_types": list(self.event_types),
            "start_time_utc": self.start_time_utc,
            "end_time_utc": self.end_time_utc,
            "entries": [e.to_dict() for e in self.entries],
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AuditRecord",
    "AuditLog",
]