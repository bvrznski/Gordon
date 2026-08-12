# Core Telemetry Manager
# ======================

"""
Telemetry collection and export infrastructure for Gordon.

This module provides:
- TelemetryManager: Canonical authority for telemetry data
- Event collection and batching
- Exporter integration for external systems

Telemetry is OBSERVATIONAL - it never changes runtime behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum, auto
import threading
import time
import uuid
import json

from .models import (
    TelemetryEvent,
    TelemetryEnvelope,
    ExportBatch,
)


# =============================================================================
# EXPORTER INTERFACE
# =============================================================================

class ExporterStatus(Enum):
    """Exporter operational status."""
    
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DRAINING = "draining"
    FAILED = "failed"
    CLOSED = "closed"


class TelemetryExporter(ABC):
    """
    Interface for telemetry exporters.
    
    Exporters are responsible for transporting telemetry data to
    external systems (Prometheus, OpenTelemetry collectors, etc.)
    
    Usage:
        class MyExporter(TelemetryExporter):
            async def export(self, batch: ExportBatch) -> bool:
                # Send to external system
                return True
            
            async def close(self) -> None:
                # Cleanup resources
                pass
    """
    
    @abstractmethod
    async def export(self, batch: ExportBatch) -> bool:
        """
        Export a batch of telemetry data.
        
        Args:
            batch: Batch to export
            
        Returns:
            True if export succeeded, False otherwise
        """
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close the exporter and release resources."""
        ...
    
    @property
    @abstractmethod
    def status(self) -> ExporterStatus:
        """Return current exporter status."""
        ...


# =============================================================================
# TELEMETRY MANAGER
# =============================================================================

class TelemetryManager:
    """
    Canonical authority for telemetry data collection.
    
    Provides:
        - Event collection and batching
        - Multiple exporters support (fan-out)
        - Bounded history with retention
    
    INVAR: Exactly one TelemetryManager exists per runtime.
    INVAR: Telemetry is observational - never changes runtime behavior.
    
    Usage:
        # Create manager (runtime-scoped)
        manager = TelemetryManager(runtime_id="runtime_123")
        
        # Add exporters
        manager.add_exporter(PrometheusExporter())
        manager.add_exporter(FileExporter("telemetry.json"))
        
        # Collect events
        event = TelemetryEvent(
            name="task.duration",
            value=0.123,
            tags={"task_id": "abc"}
        )
        manager.collect(event)
        
        # Export all collected data
        await manager.export_all()
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
        max_events_per_batch: int = 1000,
        max_history_size: int = 10000,
        default_format: str = "json",
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        self._max_events_per_batch = max_events_per_batch
        self._max_history_size = max(max_history_size, 100)
        self._default_format = default_format
        
        # Thread-safe state
        self._lock = threading.RLock()
        
        # Active exporters
        self._exporters: List[TelemetryExporter] = []
        
        # Collected events
        self._events: List[TelemetryEvent] = []
        
        # Statistics
        self._total_collected = 0
        self._total_exported = 0
        self._total_dropped = 0
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    @property
    def total_collected(self) -> int:
        """Return total events collected (including dropped)."""
        with self._lock:
            return self._total_collected
    
    @property
    def total_exported(self) -> int:
        """Return total events successfully exported."""
        with self._lock:
            return self._total_exported
    
    # ------------------------------------------------------------------
    # Exporter Management
    # ------------------------------------------------------------------
    
    async def add_exporter(self, exporter: TelemetryExporter) -> "TelemetryManager":
        """
        Add an exporter to receive telemetry data.
        
        Args:
            exporter: The exporter to add
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            self._exporters.append(exporter)
        return self
    
    async def remove_exporter(self, exporter: TelemetryExporter) -> "TelemetryManager":
        """
        Remove an exporter.
        
        Args:
            exporter: The exporter to remove
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            if exporter in self._exporters:
                self._exporters.remove(exporter)
        return self
    
    async def clear_exporters(self) -> "TelemetryManager":
        """Remove all exporters."""
        with self._lock:
            self._exporters.clear()
        return self
    
    # ------------------------------------------------------------------
    # Event Collection
    # ------------------------------------------------------------------
    
    def collect(
        self,
        event: TelemetryEvent,
        enforce_limits: bool = True,
    ) -> bool:
        """
        Collect a telemetry event.
        
        Args:
            event: Event to collect
            enforce_limits: Whether to drop events when limits exceeded
            
        Returns:
            True if event was collected, False if dropped
        """
        with self._lock:
            # Check history limit
            if enforce_limits and len(self._events) >= self._max_history_size:
                # Drop oldest events
                old = self._events.pop(0)
                del old
                self._total_dropped += 1
            
            self._events.append(event)
            self._total_collected += 1
        
        return True
    
    def collect_batch(
        self,
        events: List[TelemetryEvent],
        enforce_limits: bool = True,
    ) -> int:
        """
        Collect multiple events at once.
        
        Args:
            events: Events to collect
            enforce_limits: Whether to drop events when limits exceeded
            
        Returns:
            Number of events successfully collected
        """
        with self._lock:
            dropped = 0
            for event in events:
                # Check history limit before each addition
                if enforce_limits and len(self._events) >= self._max_history_size:
                    if self._events:
                        old = self._events.pop(0)
                        del old
                        dropped += 1
                
                self._events.append(event)
            
            self._total_collected += len(events)
            self._total_dropped += dropped
        
        return len(events) - dropped
    
    def collect_counter(
        self,
        name: str,
        value: float = 1.0,
        **tags
    ) -> bool:
        """
        Collect a counter metric as telemetry event.
        
        Args:
            name: Metric name
            value: Counter increment
            **tags: Additional tags
            
        Returns:
            True if collected
        """
        event = TelemetryEvent(
            runtime_id=self._runtime_id,
            event_type="metric",
            name=name,
            value=value,
            values={"value": value},
            tags=tags,
            unit="count"
        )
        return self.collect(event)
    
    def collect_gauge(
        self,
        name: str,
        value: float,
        **tags
    ) -> bool:
        """
        Collect a gauge metric as telemetry event.
        
        Args:
            name: Metric name
            value: Gauge value
            **tags: Additional tags
            
        Returns:
            True if collected
        """
        event = TelemetryEvent(
            runtime_id=self._runtime_id,
            event_type="metric",
            name=name,
            value=value,
            values={"value": value},
            tags=tags,
            unit="unitless"
        )
        return self.collect(event)
    
    def collect_histogram_point(
        self,
        name: str,
        value: float,
        percentile: Optional[float] = None,
        **tags
    ) -> bool:
        """
        Collect a histogram metric point.
        
        Args:
            name: Metric name
            value: Histogram value
            percentile: Percentile if this is a percentile (0-100)
            **tags: Additional tags
            
        Returns:
            True if collected
        """
        event = TelemetryEvent(
            runtime_id=self._runtime_id,
            event_type="metric",
            name=f"{name}_p{percentile:.0f}" if percentile else name,
            value=value,
            values={"value": value, "percentile": percentile or 0},
            tags=tags,
            unit="seconds"
        )
        return self.collect(event)
    
    # ------------------------------------------------------------------
    # Batching and Export
    # ------------------------------------------------------------------
    
    def create_batch(self, events: Optional[List[TelemetryEvent]] = None) -> List[TelemetryEnvelope]:
        """
        Create export batches from collected events.
        
        Args:
            events: Events to batch (uses current collection if None)
            
        Returns:
            List of envelope batches ready for export
        """
        with self._lock:
            if events is None:
                events = list(self._events)
            
            batches = []
            for i in range(0, len(events), self._max_events_per_batch):
                batch_events = events[i:i + self._max_events_per_batch]
                
                # Serialize to JSON
                payload_data = [
                    event.to_serializable() for event in batch_events
                ]
                payload = json.dumps(payload_data).encode('utf-8')
                
                envelope = TelemetryEnvelope(
                    envelope_id=str(uuid.uuid4()),
                    timestamp_utc=time.time(),
                    source_component="telemetry",
                    events=list(batch_events),
                    tags={"format": "json"}
                )
                
                batches.append(envelope)
            
            return batches
    
    async def export_all(self) -> int:
        """
        Export all collected telemetry data.
        
        Returns:
            Number of successfully exported events
        """
        with self._lock:
            # Create batch
            envelopes = self.create_batch()
            
            if not envelopes:
                return 0
            
            events_count = sum(len(e.events) for e in envelopes)
            
            # Export to all registered exporters
            success_count = 0
            for exporter in list(self._exporters):
                try:
                    for envelope in envelopes:
                        payload_data = [
                            event.to_serializable() for event in envelope.events
                        ]
                        payload = json.dumps(payload_data).encode('utf-8')
                        
                        batch = ExportBatch(
                            batch_id=str(uuid.uuid4()),
                            timestamp_utc=time.time(),
                            export_format="json",
                            data_type="metrics",
                            payload=payload,
                            source_component=envelope.source_component,
                            tags=dict(envelope.tags)
                        )
                        
                        result = await exporter.export(batch)
                        if result:
                            success_count += len(envelope.events)
                except Exception:
                    # Export failed for this exporter, continue with others
                    continue
            
            self._total_exported += success_count
            
            # Clear events after successful export
            self._events.clear()
            
            return success_count
    
    async def export_with_filter(
        self,
        filter_fn: Optional[callable] = None,
        max_events: int = 1000
    ) -> int:
        """
        Export events with optional filtering.
        
        Args:
            filter_fn: Function to filter events (takes event, returns bool)
            max_events: Maximum events to export
            
        Returns:
            Number of exported events
        """
        with self._lock:
            events = list(self._events)
            
            # Apply filter if provided
            if filter_fn is not None:
                events = [e for e in events if filter_fn(e)]
            
            # Limit events
            events = events[-max_events:]
            
            count = len(events)
            
            if count == 0:
                return 0
            
            # Export to all exporters
            success_count = 0
            for exporter in list(self._exporters):
                try:
                    payload_data = [e.to_serializable() for e in events]
                    payload = json.dumps(payload_data).encode('utf-8')
                    
                    batch = ExportBatch(
                        batch_id=str(uuid.uuid4()),
                        timestamp_utc=time.time(),
                        export_format="json",
                        data_type="metrics",
                        payload=payload,
                        source_component="telemetry"
                    )
                    
                    result = await exporter.export(batch)
                    if result:
                        success_count += count
                except Exception:
                    continue
            
            self._total_exported += success_count
            
            # Remove exported events
            if success_count > 0:
                for _ in range(min(count, len(self._events))):
                    if self._events:
                        self._events.pop(0)
            
            return success_count
    
    # ------------------------------------------------------------------
    # Query and Statistics
    # ------------------------------------------------------------------
    
    def get_event_count(self) -> int:
        """Return current number of collected events."""
        with self._lock:
            return len(self._events)
    
    def get_recent_events(
        self,
        limit: int = 100
    ) -> List[TelemetryEvent]:
        """
        Get most recently collected events.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of recent events (newest last)
        """
        with self._lock:
            return list(self._events[-limit:])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get telemetry statistics."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "collected_total": self._total_collected,
                "exported_total": self._total_exported,
                "dropped_total": self._total_dropped,
                "current_buffer_size": len(self._events),
                "exporter_count": len(self._exporters),
            }
    
    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    
    async def close(self) -> None:
        """Close the manager and all exporters."""
        # Drain remaining events
        await self.export_all()
        
        # Close all exporters
        for exporter in list(self._exporters):
            try:
                await exporter.close()
            except Exception:
                pass
        
        with self._lock:
            self._exporters.clear()


# =============================================================================
# BUILTIN EXPORTERS
# =============================================================================

class FakeExporter(TelemetryExporter):
    """
    Test exporter that collects telemetry without external output.
    
    Useful for testing telemetry behavior.
    """
    
    def __init__(self) -> None:
        import threading
        
        self._lock = threading.RLock()
        self._collected: List[ExportBatch] = []
        self._status = ExporterStatus.ACTIVE
    
    async def export(self, batch: ExportBatch) -> bool:
        """Store batch without external output."""
        if self._status != ExporterStatus.ACTIVE:
            return False
        
        with self._lock:
            self._collected.append(batch)
        
        return True
    
    async def close(self) -> None:
        """Close the exporter."""
        self._status = ExporterStatus.CLOSED
    
    @property
    def status(self) -> ExporterStatus:
        return self._status
    
    def get_collected_batches(self) -> List[ExportBatch]:
        """Get all collected batches."""
        with self._lock:
            return list(self._collected)
    
    def clear(self) -> None:
        """Clear collected batches."""
        with self._lock:
            self._collected.clear()


class NoOpExporter(TelemetryExporter):
    """Exporter that discards all telemetry data."""
    
    def __init__(self) -> None:
        self._status = ExporterStatus.ACTIVE
    
    async def export(self, batch: ExportBatch) -> bool:
        """Discard the batch."""
        return True
    
    async def close(self) -> None:
        """Close the exporter."""
        self._status = ExporterStatus.CLOSED
    
    @property
    def status(self) -> ExporterStatus:
        return self._status


__all__ = [
    "ExporterStatus",
    "TelemetryExporter",
    "TelemetryManager",
    "FakeExporter",
    "NoOpExporter",
]