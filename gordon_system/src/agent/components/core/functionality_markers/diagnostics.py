# Functionality Diagnostics & Observability - Phase 3.13.4
# ===========================================================

"""
Passive observability for Functionality classification.

This module provides:
    - Bounded diagnostics metrics
    - Passive observability hooks
    - Registry statistics and reporting
    - Classification pipeline monitoring
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum, auto
import threading
import time


@dataclass(frozen=True)
class DiagnosticsSnapshot:
    """
    Immutable snapshot of Functionality diagnostics.
    
    Used for monitoring and reporting classification health.
    """
    
    registered_class_count: int
    valid_direct_count: int
    valid_inherited_count: int
    exempt_count: int
    legacy_count: int
    missing_count: int
    conflict_count: int
    rejected_count: int
    
    sealed: bool
    registry_version: int
    schema_version: str
    
    last_failure_category: Optional[str]
    integrity_status: str


@dataclass(frozen=True)
class ClassificationEvent:
    """A single classification event."""
    
    event_type: str  # "created", "classified", "registered", "rejected"
    class_identity: str
    timestamp: float = field(default_factory=time.monotonic)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ObservabilityHook:
    """
    Passive observability hook for classification events.
    
    Does NOT affect classification results - purely informational.
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: List[ClassificationEvent] = []
        self._event_counts: Dict[str, int] = {}
    
    def on_classification_started(self, class_identity: str) -> None:
        """Called when classification begins for a class."""
        with self._lock:
            self._record_event("classification_started", class_identity)
    
    def on_classified(
        self,
        class_identity: str,
        status: str,
        source: str,
        marker: Optional[str] = None
    ) -> None:
        """Called when a class is classified."""
        with self._lock:
            self._record_event("classified", class_identity, {
                "status": status,
                "source": source,
                "marker": marker,
            })
    
    def on_exempted(self, class_identity: str, exemption_kind: str) -> None:
        """Called when a class is exempted."""
        with self._lock:
            self._record_event("exempted", class_identity, {
                "exemption_kind": exemption_kind,
            })
    
    def on_rejected(
        self,
        class_identity: str,
        reason: str,
        findings: Tuple[str, ...]
    ) -> None:
        """Called when a registration is rejected."""
        with self._lock:
            self._record_event("rejected", class_identity, {
                "reason": reason,
                "findings": list(findings),
            })
    
    def on_registry_sealed(self) -> None:
        """Called when registry is sealed."""
        with self._lock:
            self._record_event("registry_sealed", "")
    
    
    def _record_event(
        self,
        event_type: str,
        class_identity: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a classification event."""
        event = ClassificationEvent(
            event_type=event_type,
            class_identity=class_identity,
            timestamp=time.monotonic(),
            metadata=metadata or {},
        )
        self._events.append(event)
        
        # Update counts
        if event_type not in self._event_counts:
            self._event_counts[event_type] = 0
        self._event_counts[event_type] += 1
    
    def get_events(self) -> Tuple[ClassificationEvent, ...]:
        """Get all recorded events."""
        with self._lock:
            return tuple(self._events)
    
    def get_event_counts(self) -> Dict[str, int]:
        """Get event counts by type."""
        with self._lock:
            return dict(self._event_counts)


class DiagnosticsObserver:
    """
    Observer interface for diagnostics updates.
    
    Allows external systems to monitor classification health.
    """
    
    def on_diagnostics_update(self, snapshot: DiagnosticsSnapshot) -> None:
        """Called when diagnostics are updated."""
        pass
    
    def on_classification_event(self, event: ClassificationEvent) -> None:
        """Called when a classification event occurs."""
        pass


class FunctionalityDiagnostics:
    """
    Diagnostics aggregator for Functionality classification.
    
    Provides:
        - Bounded metrics collection
        - Event history
        - Health status reporting
        - Thread-safe access
    
    OBSERVABILITY PRINCIPLE:
        All diagnostics are passive observations.
        They never influence classification results.
    """
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        
        # Counters
        self._registered_count: int = 0
        self._valid_direct_count: int = 0
        self._valid_inherited_count: int = 0
        self._exempt_count: int = 0
        self._legacy_count: int = 0
        self._missing_count: int = 0
        self._conflict_count: int = 0
        self._rejected_count: int = 0
        
        # Registry state
        self._sealed: bool = False
        self._registry_version: int = 0
        
        # Observers
        self._observers: List[DiagnosticsObserver] = []
        
        # Event history (bounded)
        self._event_history: List[ClassificationEvent] = []
        self._max_events: int = 10000
    
    def record_classification(
        self,
        status: str,
        source: Optional[str] = None,
        is_exempt: bool = False,
        is_rejected: bool = False,
    ) -> None:
        """Record a classification result."""
        with self._lock:
            if is_rejected:
                self._rejected_count += 1
                return
            
            if is_exempt:
                self._exempt_count += 1
                return
            
            # Count by status type
            if "valid_direct" in status.lower():
                self._valid_direct_count += 1
            elif "valid_inherited" in status.lower():
                self._valid_inherited_count += 1
            elif "legacy" in status.lower() or "pending" in status.lower():
                self._legacy_count += 1
            elif "missing" in status.lower():
                self._missing_count += 1
            elif "conflicting" in status.lower():
                self._conflict_count += 1
            
            self._registered_count += 1
    
    def register_observer(self, observer: DiagnosticsObserver) -> None:
        """Register a diagnostics observer."""
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
    
    def unregister_observer(self, observer: DiagnosticsObserver) -> None:
        """Unregister a diagnostics observer."""
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
    
    def notify_observers(self, snapshot: DiagnosticsSnapshot) -> None:
        """Notify all observers of a diagnostic update."""
        with self._lock:
            for observer in list(self._observers):
                try:
                    observer.on_diagnostics_update(snapshot)
                except Exception:
                    pass  # Don't let observer errors affect main logic
    
    def snapshot(self) -> DiagnosticsSnapshot:
        """Create an immutable diagnostics snapshot."""
        with self._lock:
            return DiagnosticsSnapshot(
                registered_class_count=self._registered_count,
                valid_direct_count=self._valid_direct_count,
                valid_inherited_count=self._valid_inherited_count,
                exempt_count=self._exempt_count,
                legacy_count=self._legacy_count,
                missing_count=self._missing_count,
                conflict_count=self._conflict_count,
                rejected_count=self._rejected_count,
                sealed=self._sealed,
                registry_version=self._registry_version,
                schema_version="1.0.0",
                last_failure_category=None,
                integrity_status="valid" if not self._sealed else "sealed",
            )
    
    def seal(self) -> None:
        """Mark diagnostics as sealed (no more registrations)."""
        with self._lock:
            self._sealed = True
    
    def reset_for_tests(self) -> None:
        """Reset all counters for testing."""
        with self._lock:
            self._registered_count = 0
            self._valid_direct_count = 0
            self._valid_inherited_count = 0
            self._exempt_count = 0
            self._legacy_count = 0
            self._missing_count = 0
            self._conflict_count = 0
            self._rejected_count = 0
            self._event_history.clear()
            self._sealed = False
    
    @property
    def is_sealed(self) -> bool:
        """Check if diagnostics are sealed."""
        with self._lock:
            return self._sealed


__all__ = [
    # Dataclasses
    "DiagnosticsSnapshot",
    "ClassificationEvent",
    
    # Classes
    "ObservabilityHook",
    "DiagnosticsObserver",
    "FunctionalityDiagnostics",
]