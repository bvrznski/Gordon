# Audit Module - Governance Subsystem

"""
Audit: Immutable governance history maintenance.

This module provides audit functionality for recording governance decisions.
The audit system is append-only and preserves all evaluation evidence.

Audit Laws:

    AUDIT-LAW-001: Every governance evaluation produces an audit record
    AUDIT-LAW-002: Audit history is immutable
    AUDIT-LAW-003: Audit records preserve provenance
    AUDIT-LAW-004: Audit records preserve timestamps
    AUDIT-LAW-005: Audit records preserve supporting evidence
    AUDIT-LAW-006: Audit is append-only
    AUDIT-LAW-007: Audit history remains inspectable
    AUDIT-LAW-008: Audit behavior remains deterministic

Anti-Patterns Rejected:

    - Mutable audit logs
    - Hidden audit records
    - Non-deterministic auditing
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time
import hashlib


# =============================================================================
# AUDIT RECORD - Immutable governance history entry
# =============================================================================


@dataclass(frozen=True)
class AuditRecord:
    """
    An immutable audit record for a governance decision.
    
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
    
    def get_events_by_type(
        self,
        event_type: str,
    ) -> Tuple[AuditRecord, ...]:
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
# AUDIT SERVICE - Manages audit log
# =============================================================================


class AuditService:
    """
    Service for managing governance audit logs.
    
    This service provides methods for recording audit events and retrieving
    audit history. The underlying audit log is immutable - new events are
    appended to create a new log.
    """
    
    _current_log: AuditLog
    
    def __init__(self):
        """Initialize the audit service with an empty log."""
        self._current_log = AuditLog(
            log_id=f"audit:{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}",
            entries=(),
        )
    
    @property
    def current_log(self) -> AuditLog:
        """Get the current audit log (immutable)."""
        return self._current_log
    
    def record_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        evidence_ids: Optional[Tuple[str, ...]] = None,
        revision_id: str = "",
    ) -> AuditRecord:
        """
        Record a new audit event.
        
        This creates a new audit record and returns it. The log is not modified
        in-place; instead, a new log is created with the additional entry.
        
        Args:
            event_type: Type of event (integrity_check, compliance_check, etc.)
            details: Event-specific information
            evidence_ids: Optional IDs of evidence records created
            revision_id: Memory system revision at time of event
            
        Returns:
            New AuditRecord that was added to the log
        """
        record = AuditRecord(
            audit_id=f"audit_record:{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}",
            event_type=event_type,
            timestamp_utc=time.time(),
            details=dict(details),
            evidence_ids=evidence_ids or (),
            revision_id=revision_id,
        )
        
        # Create new log with the additional entry
        self._current_log = AuditLog(
            log_id=self._current_log.log_id,
            entries=self._current_log.entries + (record,),
            start_time_utc=self._current_log.start_time_utc,
            end_time_utc=time.time(),
        )
        
        return record
    
    def get_events_by_type(
        self,
        event_type: str,
    ) -> Tuple[AuditRecord, ...]:
        """Get all audit records of a specific type."""
        return self._current_log.get_events_by_type(event_type)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AuditRecord",
    "AuditLog",
    "AuditService",
]