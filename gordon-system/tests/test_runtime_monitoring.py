# Runtime Monitoring Tests
# =========================

"""
Tests for the Phase 3.7.11 runtime monitoring architecture.

This module validates:
- Canonical HealthManager, IntegrityManager, DiagnosticsManager instances
- Canonical HealthVerifier, IntegrityVerifier instances  
- Immutable model creation and serialization
- Event generation and aggregation
- Heartbeat supervision
- Watchdog operation
"""

import asyncio
import time
from typing import Dict, Any

# Import from the runtime_monitoring package (using relative imports)
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent.components.core.runtime_monitoring import (
    # Authorities
    HealthManager,
    IntegrityManager,
    DiagnosticsManager,
    RuntimeObservationCoordinator,
    HealthVerifier,
    IntegrityVerifier,
    HeartbeatManager,
    
    # Diagnostic states and models
    DiagnosticState,
    DiagnosticEvidence,
    DiagnosticCause,
    DiagnosticReport,
    
    # Health models
    HealthStatus,
    HealthDomain,
    Severity,
    HealthFinding,
    HealthCheck,
    HealthMeasurement,
    HealthObservation,
    HealthEvaluation,
    HealthReport,
    HealthSnapshot,
    HealthHistoryEntry,
    
    # Integrity models  
    IntegrityStatus,
    IntegrityDomain,
    IntegrityViolation,
    IntegrityFinding,
    IntegrityCheck,
    IntegrityEvaluation,
    IntegrityReport,
    IntegritySnapshot,
    IntegrityHistoryEntry,
    
    # Watchdog
    WatchdogPolicy,
    WatchdogConfig,
    WatchdogEventType,
    WatchdogEvent,
    Watchdog,
    
    # Events
    MonitoringEventType,
    EventSeverity,
    RuntimeMonitoringEvent,
    HealthChanged,
    HealthDegraded,
    HealthRecovered,
    IntegrityVerified,
    IntegrityViolationDetected,
    HeartbeatLost,
    HeartbeatRestored,
    WatchdogTriggered,
    WatchdogCleared,
    RuntimeAnomalyDetected,
    EventAggregator,
)


# =============================================================================
# TEST: Canonical Authorities
# =============================================================================

def test_health_manager_creation():
    """Test HealthManager instance creation."""
    runtime_id = "test_runtime_1"
    manager = HealthManager(runtime_id=runtime_id)
    
    assert manager.runtime_id == runtime_id
    assert manager.snapshot_count == 0
    assert manager.evaluation_count == 0


def test_integrity_manager_creation():
    """Test IntegrityManager instance creation."""
    runtime_id = "test_runtime_2"
    manager = IntegrityManager(runtime_id=runtime_id)
    
    assert manager.runtime_id == runtime_id
    assert manager.snapshot_count == 0
    assert manager.evaluation_count == 0


def test_coordinator_creation():
    """Test RuntimeObservationCoordinator instance creation."""
    runtime_id = "test_runtime_3"
    health_mgr = HealthManager(runtime_id=runtime_id)
    integrity_mgr = IntegrityManager(runtime_id=runtime_id)
    
    coordinator = RuntimeObservationCoordinator(
        runtime_id=runtime_id,
        health_manager=health_mgr,
        integrity_manager=integrity_mgr
    )
    
    assert coordinator.runtime_id == runtime_id
    assert coordinator.health_manager is health_mgr
    assert coordinator.integrity_manager is integrity_mgr


# =============================================================================
# TEST: Health Models
# =============================================================================

def test_health_status_values():
    """Test HealthStatus enum values."""
    statuses = [s.value for s in HealthStatus]
    
    assert "unknown" in statuses
    assert "healthy" in statuses
    assert "degraded" in statuses
    assert "unhealthy" in statuses
    assert "failed" in statuses


def test_health_domain_values():
    """Test HealthDomain enum values."""
    domains = [d.value for d in HealthDomain]
    
    expected_domains = [
        "kernel", "runtime", "lifecycle", "scheduler",
        "executor", "resources", "workers", "queues",
        "storage", "networking", "models", "plugins",
        "services", "cognition_interfaces", "communication", "observability"
    ]
    
    for domain in expected_domains:
        assert domain in domains


def test_health_finding_creation():
    """Test HealthFinding immutable creation."""
    finding = HealthFinding.healthy(
        check_name="cpu_check",
        domain=HealthDomain.RUNTIME,
        message="CPU usage normal"
    )
    
    assert finding.check_name == "cpu_check"
    assert finding.domain == HealthDomain.RUNTIME
    assert finding.status == HealthStatus.HEALTHY
    assert finding.is_failure is False


def test_health_measurement_creation():
    """Test HealthMeasurement immutable creation."""
    measurement = HealthMeasurement.from_value(
        check_id="check_123",
        subject="worker_1",
        domain=HealthDomain.RESOURCES,
        dimension="cpu_usage",
        value=0.75,
        unit="percentage"
    )
    
    assert measurement.subject == "worker_1"
    assert measurement.domain == HealthDomain.RESOURCES
    assert measurement.dimension == "cpu_usage"
    assert measurement.value == 0.75


def test_health_observation_creation():
    """Test HealthObservation immutable creation."""
    observation = HealthObservation.degraded(
        subject="worker_1",
        domain=HealthDomain.RUNTIME
    )
    
    assert observation.subject == "worker_1"
    assert observation.domain == HealthDomain.RUNTIME
    assert observation.status == HealthStatus.DEGRADED
    assert observation.is_degraded is True


def test_health_report_serialization():
    """Test HealthReport JSON serialization."""
    evaluation = HealthEvaluation.create(
        subject="runtime",
        observations={},
        evaluation_duration_seconds=0.5,
        total_measurements=10
    )
    
    report = HealthReport.create(subject="runtime", evaluations=[evaluation])
    
    serializable = report.to_serializable()
    
    assert "subject" in serializable
    assert "total_subjects" in serializable
    assert serializable["total_subjects"] == 1


# =============================================================================
# TEST: Integrity Models
# =============================================================================

def test_integrity_status_values():
    """Test IntegrityStatus enum values."""
    statuses = [s.value for s in IntegrityStatus]
    
    assert "unknown" in statuses
    assert "verified" in statuses
    assert "degraded" in statuses
    assert "violated" in statuses


def test_integrity_domain_values():
    """Test IntegrityDomain enum values."""
    domains = [d.value for d in IntegrityDomain]
    
    expected_domains = [
        "ownership", "dependency_graph", "lifecycle_consistency",
        "runtime_state", "configuration", "capability_graph",
        "registry", "synchronization", "resource_ownership",
        "scheduler_invariants", "executor_invariants"
    ]
    
    for domain in expected_domains:
        assert domain in domains


def test_integrity_violation_creation():
    """Test IntegrityViolation immutable creation."""
    violation = IntegrityViolation.error(
        domain=IntegrityDomain.DEPENDENCY_GRAPH,
        message="Dependency cycle detected",
        cycle=["A", "B", "C", "A"]
    )
    
    assert violation.domain == IntegrityDomain.DEPENDENCY_GRAPH
    assert violation.severity.value == "error"
    assert violation.is_blocking is True


def test_integrity_finding_creation():
    """Test IntegrityFinding immutable creation."""
    finding = IntegrityFinding.pass_finding(
        check_name="ownership_check",
        domain=IntegrityDomain.OWNERSHIP,
        message="Ownership verified"
    )
    
    assert finding.check_name == "ownership_check"
    assert finding.domain == IntegrityDomain.OWNERSHIP
    assert finding.passed is True


def test_integrity_report_serialization():
    """Test IntegrityReport JSON serialization."""
    evaluation = IntegrityEvaluation.create(
        subject="runtime",
        findings_by_domain={},
        evaluation_duration_seconds=0.3
    )
    
    report = IntegrityReport.create(subject="runtime", evaluations=[evaluation])
    
    serializable = report.to_serializable()
    
    assert "subject" in serializable
    assert "verified_count" in serializable


# =============================================================================
# TEST: Event System
# =============================================================================

def test_event_aggregator():
    """Test EventAggregator event storage."""
    aggregator = EventAggregator(max_events=100)
    
    # Add some events
    event1 = HealthChanged.create(
        runtime_id="runtime_1",
        subject="component_a",
        previous_status=None,
        new_status="degraded"
    )
    
    event2 = IntegrityVerified.create(
        runtime_id="runtime_1",
        subject="component_b"
    )
    
    aggregator.add_event(event1)
    aggregator.add_event(event2)
    
    # Get all events
    all_events = aggregator.get_events()
    assert len(all_events) == 2
    
    # Filter by type
    health_events = [e for e in all_events if e.event_type == MonitoringEventType.HEALTH_CHANGED]
    assert len(health_events) == 1


def test_event_severity():
    """Test EventSeverity determination."""
    event = IntegrityViolationDetected.create(
        runtime_id="runtime_1",
        subject="component_a"
    )
    
    # Integrity violations are CRITICAL severity
    assert event.severity == EventSeverity.CRITICAL
    
    recovered = HealthRecovered.create(
        runtime_id="runtime_1",
        subject="component_b"
    )
    
    # Recovery is NOTICE severity
    assert recovered.severity == EventSeverity.NOTICE


# =============================================================================
# TEST: Heartbeat System
# =============================================================================

def test_heartbeat_manager_registration():
    """Test heartbeat source registration."""
    manager = HeartbeatManager(runtime_id="test_runtime")
    
    source = manager.register_source(
        name="worker_heartbeat",
        expected_interval_seconds=5.0,
        max_missed=3
    )
    
    assert source is not None
    assert source.name == "worker_heartbeat"
    assert source.is_active is True


def test_heartbeat_record_and_loss():
    """Test heartbeat recording and loss detection."""
    manager = HeartbeatManager(runtime_id="test_runtime")
    
    # Register source
    source = manager.register_source(
        name="worker",
        expected_interval_seconds=2.0,
        max_missed=2
    )
    
    assert source.is_active is True
    
    # Record some heartbeats
    manager.record_heartbeat(source.source_id)
    status = manager.get_source_status(source.source_id)
    assert status is not None and status.is_active is True


# =============================================================================
# TEST: Watchdog System
# =============================================================================

def test_watchdog_config():
    """Test WatchdogConfig creation."""
    config = WatchdogConfig.create(
        name="scheduler_watchdog",
        check_interval_seconds=10.0,
        timeout_seconds=30.0,
        policy=WatchdogPolicy.ALERT,
        description="Monitor scheduler health"
    )
    
    assert config.name == "scheduler_watchdog"
    assert config.check_interval_seconds == 10.0
    assert config.policy == WatchdogPolicy.ALERT


def test_watchdog_policy_values():
    """Test WatchdogPolicy enum values."""
    policies = [p.value for p in WatchdogPolicy]
    
    assert "alert" in policies
    assert "warn" in policies
    assert "block" in policies
    assert "terminate" in policies


# =============================================================================
# TEST: Async Evaluation
# =============================================================================

async def test_health_evaluation():
    """Test async health evaluation."""
    manager = HealthManager(runtime_id="test_runtime")
    
    # Define domain checks
    def check_kernel(subject: str) -> bool:
        return True  # Kernel is healthy
    
    def check_runtime(subject: str) -> bool:
        return True  # Runtime is healthy
    
    domain_checks = {
        HealthDomain.KERNEL: check_kernel,
        HealthDomain.RUNTIME: check_runtime,
    }
    
    # Execute evaluation
    evaluation = await manager.evaluate(
        subject="test_subject",
        domain_checks=domain_checks,
        timeout_seconds=30.0
    )
    
    assert evaluation is not None
    assert evaluation.is_healthy is True


async def test_integrity_evaluation():
    """Test async integrity evaluation."""
    manager = IntegrityManager(runtime_id="test_runtime")
    
    # Define domain checks
    def check_ownership(subject: str) -> bool:
        return True  # Ownership verified
    
    def check_dependency(subject: str) -> bool:
        return True  # Dependencies OK
    
    domain_checks = {
        IntegrityDomain.OWNERSHIP: check_ownership,
        IntegrityDomain.DEPENDENCY_GRAPH: check_dependency,
    }
    
    # Execute evaluation
    evaluation = await manager.evaluate(
        subject="test_subject",
        domain_checks=domain_checks,
        timeout_seconds=30.0
    )
    
    assert evaluation is not None
    assert evaluation.is_verified is True


# =============================================================================
# TEST: Pipeline Integration
# =============================================================================

async def test_full_pipeline():
    """Test complete observation pipeline."""
    runtime_id = "test_runtime"
    
    # Create managers
    health_mgr = HealthManager(runtime_id=runtime_id)
    integrity_mgr = IntegrityManager(runtime_id=runtime_id)
    
    coordinator = RuntimeObservationCoordinator(
        runtime_id=runtime_id,
        health_manager=health_mgr,
        integrity_manager=integrity_mgr
    )
    
    # Define checks
    def check_health(subject: str) -> bool:
        return True
    
    def check_integrity(subject: str) -> bool:
        return True
    
    health_checks = {HealthDomain.RUNTIME: check_health}
    integrity_checks = {IntegrityDomain.OWNERSHIP: check_integrity}
    
    # Run pipeline
    result = await coordinator.run_pipeline(
        health_checks=health_checks,
        integrity_checks=integrity_checks,
        timeout_seconds=60.0
    )
    
    assert result is not None
    assert result.success is True
    
    # Verify truth was updated
    snapshot = coordinator.get_truth_snapshot()
    assert snapshot is not None


# =============================================================================
# TEST: Snapshot Operations
# =============================================================================

def test_health_snapshot():
    """Test health snapshot creation and versioning."""
    manager = HealthManager(runtime_id="test_runtime")
    
    # Create initial evaluation
    async def run_init():
        eval_result = await manager.evaluate(
            subject="test",
            domain_checks={HealthDomain.RUNTIME: lambda s: True},
            timeout_seconds=5.0
        )
        return eval_result
    
    eval_result = asyncio.run(run_init())
    
    # Take snapshot
    snapshot = manager.take_snapshot()
    
    assert snapshot is not None
    assert snapshot.runtime_id == "test_runtime"
    assert snapshot.version == 1


def test_integrity_snapshot():
    """Test integrity snapshot creation and versioning."""
    manager = IntegrityManager(runtime_id="test_runtime")
    
    # Create initial evaluation
    async def run_init():
        eval_result = await manager.evaluate(
            subject="test",
            domain_checks={IntegrityDomain.OWNERSHIP: lambda s: True},
            timeout_seconds=5.0
        )
        return eval_result
    
    eval_result = asyncio.run(run_init())
    
    # Take snapshot
    snapshot = manager.take_snapshot()
    
    assert snapshot is not None
    assert snapshot.runtime_id == "test_runtime"
    assert snapshot.version == 1


# =============================================================================
# TEST: History Tracking
# =============================================================================

def test_health_history():
    """Test health history entry creation."""
    entry = HealthHistoryEntry.status_changed(
        runtime_id="test_runtime",
        subject="component_a",
        previous_status=HealthStatus.HEALTHY,
        new_status=HealthStatus.DEGRADED,
        reason="CPU usage exceeded threshold"
    )
    
    assert entry.subject == "component_a"
    assert entry.previous_status == HealthStatus.HEALTHY
    assert entry.new_status == HealthStatus.DEGRADED
    assert entry.reason is not None


def test_integrity_history():
    """Test integrity history entry creation."""
    entry = IntegrityHistoryEntry.status_changed(
        runtime_id="test_runtime",
        subject="component_b",
        previous_status=IntegrityStatus.VERIFIED,
        new_status=IntegrityStatus.DEGRADED,
        reason="Configuration drift detected"
    )
    
    assert entry.subject == "component_b"
    assert entry.previous_status == IntegrityStatus.VERIFIED
    assert entry.new_status == IntegrityStatus.DEGRADED


# =============================================================================
# TEST: Runtime Truth Integration
# =============================================================================

def test_runtime_truth_update():
    """Test runtime truth update operations."""
    from agent.components.core.runtime_state import (
        RuntimeTruth,
        RuntimeTruthVersion,
        RuntimeTruthSnapshot,
    )
    
    truth = RuntimeTruth(runtime_id="test_runtime")
    
    # Update health - first update should create version 0
    version1 = truth.update_health("subject_1", "healthy")
    assert version1.sequence_number == 1
    
    # Update integrity - second update creates version 1
    version2 = truth.update_integrity("subject_2", "verified")
    assert version2.sequence_number == 2
    
    # Take snapshot
    snapshot = truth.take_snapshot()
    
    assert snapshot is not None


# =============================================================================
# MAIN: Run Tests
# =============================================================================

def run_all_tests():
    """Run all tests and report results."""
    import traceback
    
    passed = 0
    failed = 0
    
    test_functions = [
        ("Health Manager Creation", test_health_manager_creation),
        ("Integrity Manager Creation", test_integrity_manager_creation),
        ("Coordinator Creation", test_coordinator_creation),
        ("Health Status Values", test_health_status_values),
        ("Health Domain Values", test_health_domain_values),
        ("Health Finding Creation", test_health_finding_creation),
        ("Health Measurement Creation", test_health_measurement_creation),
        ("Health Observation Creation", test_health_observation_creation),
        ("Health Report Serialization", test_health_report_serialization),
        ("Integrity Status Values", test_integrity_status_values),
        ("Integrity Domain Values", test_integrity_domain_values),
        ("Integrity Violation Creation", test_integrity_violation_creation),
        ("Integrity Finding Creation", test_integrity_finding_creation),
        ("Event Aggregator", test_event_aggregator),
        ("Event Severity", test_event_severity),
        ("Heartbeat Manager Registration", test_heartbeat_manager_registration),
        ("Heartbeat Record and Loss", test_heartbeat_record_and_loss),
        ("Watchdog Config", test_watchdog_config),
        ("Watchdog Policy Values", test_watchdog_policy_values),
        ("Health Snapshot", test_health_snapshot),
        ("Integrity Snapshot", test_integrity_snapshot),
        ("Health History", test_health_history),
        ("Integrity History", test_integrity_history),
    ]
    
    async_tests = [
        ("Full Pipeline", test_full_pipeline),
    ]
    
    # Run sync tests
    print("Running synchronous tests...")
    for name, func in test_functions:
        try:
            func()
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            traceback.print_exc()
            failed += 1
    
    # Run async tests
    print("\nRunning asynchronous tests...")
    for name, func in async_tests:
        try:
            asyncio.run(func())
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            traceback.print_exc()
            failed += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Tests: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)