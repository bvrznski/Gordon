# Core Runtime Monitoring Infrastructure
# ======================================

"""
Production-grade runtime health, integrity & self-monitoring for Phase 3.7.11-I.

Provides:
- Canonical HealthManager (single authority for health)
- Canonical IntegrityManager (single authority for integrity)  
- Canonical DiagnosticsManager (single authority for diagnostics)
- Canonical RuntimeObservationCoordinator (orchestrates monitoring pipeline)
- Canonical HealthVerifier (independent health verification)
- Canonical IntegrityVerifier (independent integrity verification)
- Immutable models for all monitoring artifacts
- Heartbeat supervision and Watchdog systems
- Runtime invariants verification
- Runtime truth publication system
- Self-monitoring capabilities

Architecture Overview:
    RuntimeObservationCoordinator
        ├── HealthManager (health evaluation, aggregation, snapshots)
        ├── IntegrityManager (invariant evaluation, integrity verification)
        ├── DiagnosticsManager (diagnostic report generation)
        ├── HealthVerifier (independent health verification)
        ├── IntegrityVerifier (independent integrity verification)
        ├── HeartbeatManager (heartbeat supervision, loss detection)
        └── WatchdogSystem (progress monitoring, anomaly detection)

Invariants Enforced:
1. Exactly one HealthManager per runtime instance
2. Exactly one IntegrityManager per runtime instance
3. Exactly one DiagnosticsManager per runtime instance
4. Health is independent of Integrity
5. Health is independent of Readiness
6. Integrity is independent of Availability
7. Runtime truth is immutable and observational
8. Monitoring never mutates unrelated subsystem state
"""

# Import models from submodules (these will be available in the module namespace)
from .health import (
    # Models
    HealthCheck,
    HealthObservation,
    HealthMeasurement,
    HealthEvaluation,
    HealthReport,  # Added
    HealthSnapshot,  # Added
    HealthHistoryEntry,  # Added
    HealthFinding,
    # Status enums
    HealthStatus,
    Severity,
    HealthDomain,
    HealthEventType,
)

from .integrity import (
    # Runtime Observer Authority
    RuntimeObserver,
    
    # Models
    IntegrityCheck,
    IntegrityFinding,
    IntegrityViolation,
    IntegrityEvaluation,
    IntegritySnapshot,
    IntegrityReport,
    IntegrityHistoryEntry,
    # Status enums  
    IntegrityStatus,
    Severity as IntegritySeverity,
    IntegrityDomain,
    IntegrityEventType,
)

from .heartbeat import (
    HeartbeatManager,
    HeartbeatSource,
    Watchdog,
    WatchdogPolicy,
    WatchdogConfig,
    WatchdogEventType,
    WatchdogEvent,
)

from ..runtime_state.runtime_truth import (
    RuntimeTruth,
    RuntimeTruthSnapshot,
    RuntimeTruthVersion,
    RuntimeTruthPublisher,
)

from .events import (
    # Base event
    RuntimeMonitoringEvent,
    # Event types
    MonitoringEventType,
    EventSeverity,
    HealthChanged,
    HealthDegraded,
    HealthRecovered,
    IntegrityVerified,
    IntegrityViolationDetected,
    RuntimeTruthUpdated,
    HeartbeatLost,
    HeartbeatRestored,
    WatchdogTriggered,
    WatchdogCleared,
    RuntimeAnomalyDetected,
    EventAggregator,
)

from .diagnostics import (
    # Diagnostic states
    DiagnosticState,
    
    # Evidence model
    DiagnosticEvidence,
    
    # Cause model
    DiagnosticCause,
    
    # Report model  
    DiagnosticReport,
    
    # Authorities
    DiagnosticsManager,
    HealthVerifier,
    IntegrityVerifier,
)

# Import authorities last (they depend on models being defined first)
from .health import HealthManager
from .integrity import IntegrityManager, RuntimeObserver
from .diagnostics import DiagnosticsManager, HealthVerifier, IntegrityVerifier

# Coordinator depends on managers being defined first
from .runtime_observation import RuntimeObservationCoordinator

__all__ = [
    # Runtime Observer Authority
    "RuntimeObserver",
    
    # Canonical authorities
    "HealthManager",
    "IntegrityManager", 
    "DiagnosticsManager",
    "RuntimeObservationCoordinator",
    "HealthVerifier",
    "IntegrityVerifier",
    
    # Diagnostic states and models
    "DiagnosticState",
    "DiagnosticEvidence",
    "DiagnosticCause",
    "DiagnosticReport",
    
    # Health models
    "HealthCheck",
    "HealthObservation",
    "HealthMeasurement",
    "HealthEvaluation",
    "HealthStatus",
    "HealthFinding",
    "Severity",
    "HealthDomain",
    "HealthEventType",
    
    # Integrity models
    "IntegrityCheck",
    "IntegrityFinding", 
    "IntegrityViolation",
    "IntegrityEvaluation",
    "IntegrityStatus",
    "IntegritySnapshot",
    "IntegrityReport",
    "IntegrityHistoryEntry",
    "IntegritySeverity",
    "IntegrityDomain",
    "IntegrityEventType",
    
    # Heartbeat & Watchdog
    "HeartbeatManager",
    "HeartbeatSource",
    "Watchdog",
    "WatchdogPolicy",
    "WatchdogConfig",
    "WatchdogEventType",
    "WatchdogEvent",
    
    # Runtime truth
    "RuntimeTruth",
    "RuntimeTruthSnapshot", 
    "RuntimeTruthVersion",
    "RuntimeTruthPublisher",
    
    # Events
    "MonitoringEventType",
    "EventSeverity",
    "RuntimeMonitoringEvent",
    "HealthChanged",
    "HealthDegraded",
    "HealthRecovered",
    "IntegrityVerified",
    "IntegrityViolationDetected",
    "RuntimeTruthUpdated",
    "HeartbeatLost",
    "HeartbeatRestored",
    "WatchdogTriggered",
    "WatchdogCleared",
    "RuntimeAnomalyDetected",
    "EventAggregator",
]

# Expose canonical authorities as singleton factories
def create_health_manager(runtime_id: str) -> HealthManager:
    """Create a new HealthManager instance."""
    return HealthManager(runtime_id=runtime_id)

def create_integrity_manager(runtime_id: str) -> IntegrityManager:
    """Create a new IntegrityManager instance."""
    return IntegrityManager(runtime_id=runtime_id)

def create_diagnostics_manager(runtime_id: str) -> DiagnosticsManager:
    """Create a new DiagnosticsManager instance."""
    return DiagnosticsManager(runtime_id=runtime_id)

def create_health_verifier(runtime_id: str) -> HealthVerifier:
    """Create a new HealthVerifier instance."""
    return HealthVerifier(runtime_id=runtime_id)

def create_integrity_verifier(runtime_id: str) -> IntegrityVerifier:
    """Create a new IntegrityVerifier instance."""
    return IntegrityVerifier(runtime_id=runtime_id)

def create_runtime_observer(runtime_id: str) -> RuntimeObserver:
    """Create a new RuntimeObserver instance."""
    return RuntimeObserver(runtime_id=runtime_id)

def create_runtime_observation_coordinator(
    runtime_id: str,
    health_manager: HealthManager,
    integrity_manager: IntegrityManager
) -> RuntimeObservationCoordinator:
    """Create a new RuntimeObservationCoordinator instance."""
    return RuntimeObservationCoordinator(
        runtime_id=runtime_id,
        health_manager=health_manager,
        integrity_manager=integrity_manager
    )

def create_heartbeat_manager(runtime_id: str) -> HeartbeatManager:
    """Create a new HeartbeatManager instance."""
    return HeartbeatManager(runtime_id=runtime_id)
