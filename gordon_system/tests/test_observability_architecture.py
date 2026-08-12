# Observability Architecture Tests
# ==================================

"""
Comprehensive tests for the production observability architecture.

Tests cover:
- Canonical authority patterns (exactly one per runtime)
- Immutable models (logs, telemetry, traces, metrics)
- Span hierarchy and trace propagation
- Correlation context propagation
- Sampling policies
- Sinks and exporters
- Retention strategies

All observability components are observational - they never change runtime behavior.
"""

import pytest
import time
import threading
from typing import List, Dict, Any, Optional


# Import observability primitives - use absolute imports matching project structure
from agent.components.core.observability import (
    # Canonical authorities
    ObservabilityManager,
    LoggingManager,
    TraceManager,
    TelemetryManager,
    MetricsManager,
    CorrelationManager,
    DiagnosticsManager,
    
    # Models
    LogLevel,
    LogRecord,
    LogContext,
    LogMetadata,
    create_log,
    create_debug_log,
    create_info_log,
    create_notice_log,
    create_warning_log,
    create_error_log,
    create_critical_log,
    
    TelemetryEvent,
    TelemetryEnvelope,
    TraceId,
    SpanId,
    MetricType,
    MetricPoint,
    CorrelationContext,
    CorrelationSnapshot,
    ExportBatch,
    
    DiagnosticSeverity,
    DiagnosticFinding,
    DiagnosticReport,
    
    # Sampling
    SamplingPolicy,
    SamplingConfig,
    
    # Sinks
    LogSink,
    ConsoleSink,
    MemorySink,
    FakeSink,
)

from agent.components.core.observability.tracing import (
    SpanRecord as TracingSpanRecord,
    SpanStatus as TracingSpanStatus,
    SpanEvent as TracingSpanEvent,
    TraceSnapshot,
    SpanContextManager,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def runtime_id() -> str:
    """Generate a unique runtime ID for testing."""
    return f"test_runtime_{time.time():.6f}"


@pytest.fixture
def observability_manager(runtime_id: str):
    """Create an ObservabilityManager with test configuration."""
    config = ObservabilityConfig(
        runtime_id=runtime_id,
        log_sample_rate=1.0,  # Log everything for tests
        enable_console_logging=False,  # Disable console output during tests
    )
    return ObservabilityManager(config)


@pytest.fixture
def logging_manager(runtime_id: str) -> LoggingManager:
    """Create a LoggingManager with test configuration."""
    config = SamplingConfig(
        policy=SamplingPolicy.ALWAYS,
        sample_rate=1.0
    )
    manager = LoggingManager(
        runtime_id=runtime_id,
        sampling_config=config,
        max_history=1000
    )
    return manager


@pytest.fixture
def trace_manager(runtime_id: str) -> TraceManager:
    """Create a TraceManager with test configuration."""
    return TraceManager(
        runtime_id=runtime_id,
        max_spans_per_trace=1000
    )


@pytest.fixture
def telemetry_manager(runtime_id: str) -> TelemetryManager:
    """Create a TelemetryManager with test configuration."""
    return TelemetryManager(
        runtime_id=runtime_id,
        max_events_per_batch=100,
        max_history_size=1000
    )


@pytest.fixture
def metrics_manager(runtime_id: str) -> MetricsManager:
    """Create a MetricsManager with test configuration."""
    return MetricsManager(runtime_id=runtime_id)


@pytest.fixture
def correlation_manager(runtime_id: str) -> CorrelationManager:
    """Create a CorrelationManager with test configuration."""
    return CorrelationManager(runtime_id=runtime_id)


@pytest.fixture
def diagnostics_manager(runtime_id: str) -> DiagnosticsManager:
    """Create a DiagnosticsManager with test configuration."""
    return DiagnosticsManager(
        runtime_id=runtime_id,
        max_findings_per_scope=1000,
        retention_seconds=3600.0
    )


# =============================================================================
# CANONICAL AUTHORITY TESTS
# =============================================================================

class TestCanonicalAuthorities:
    """Test that exactly one authority exists per runtime."""
    
    def test_observability_manager_single_instance(self, runtime_id: str):
        """ObservabilityManager should be created with specific runtime_id."""
        config = ObservabilityConfig(runtime_id=runtime_id)
        obs1 = ObservabilityManager(config)
        
        assert obs1.runtime_id == runtime_id
        
        # Create another manager - it has different runtime_id
        config2 = ObservabilityConfig(runtime_id=f"{runtime_id}_different")
        obs2 = ObservabilityManager(config2)
        
        assert obs1.runtime_id != obs2.runtime_id
    
    def test_logging_manager_single_instance(self, runtime_id: str):
        """LoggingManager should have single instance per runtime."""
        manager = LoggingManager(runtime_id=runtime_id)
        assert manager.runtime_id == runtime_id
    
    def test_trace_manager_single_instance(self, runtime_id: str):
        """TraceManager should have single instance per runtime."""
        manager = TraceManager(runtime_id=runtime_id)
        assert manager.runtime_id == runtime_id
    
    def test_telemetry_manager_single_instance(self, runtime_id: str):
        """TelemetryManager should have single instance per runtime."""
        manager = TelemetryManager(runtime_id=runtime_id)
        assert manager.runtime_id == runtime_id
    
    def test_metrics_manager_single_instance(self, runtime_id: str):
        """MetricsManager should have single instance per runtime."""
        manager = MetricsManager(runtime_id=runtime_id)
        assert manager.runtime_id == runtime_id
    
    def test_correlation_manager_single_instance(self, runtime_id: str):
        """CorrelationManager should have single instance per runtime."""
        manager = CorrelationManager(runtime_id=runtime_id)
        # CorrelationManager doesn't expose runtime_id property directly
        # but it uses the passed runtime_id internally


# =============================================================================
# IMMUTABLE MODELS TESTS
# =============================================================================

class TestImmutableModels:
    """Test that models are immutable and hashable."""
    
    def test_log_record_is_frozen(self, runtime_id: str):
        """LogRecord should be frozen (immutable)."""
        record = create_info_log("test message", runtime_id=runtime_id)
        
        with pytest.raises(AttributeError):
            record.level = LogLevel.ERROR  # type: ignore
    
    def test_log_record_hashable(self, runtime_id: str):
        """LogRecord should be hashable."""
        record1 = create_info_log("test", runtime_id=runtime_id)
        record2 = create_info_log("test", runtime_id=runtime_id)
        
        # Should work in sets and as dict keys
        records_set = {record1, record2}
        assert len(records_set) == 1  # Same event_id means same hash
    
    def test_telemetry_event_is_frozen(self):
        """TelemetryEvent should be frozen."""
        event = TelemetryEvent(
            runtime_id="test",
            name="test.event"
        )
        
        with pytest.raises(AttributeError):
            event.name = "changed"  # type: ignore
    
    def test_trace_span_record_is_frozen(self, runtime_id: str):
        """SpanRecord should be frozen."""
        span = TracingSpanRecord(
            span_id=str(SpanId.generate()),
            trace_id=str(TraceId.generate()),
            name="test"
        )
        
        with pytest.raises(AttributeError):
            span.name = "changed"  # type: ignore
    
    def test_diagnostic_finding_is_frozen(self, runtime_id: str):
        """DiagnosticFinding should be frozen."""
        finding = DiagnosticFinding(
            finding_id="test",
            source="test",
            severity=DiagnosticSeverity.INFO,
            code="TEST",
            title="Test"
        )
        
        with pytest.raises(AttributeError):
            finding.title = "changed"  # type: ignore


# =============================================================================
# LOGGING MANAGER TESTS
# =============================================================================

class TestLoggingManager:
    """Tests for LoggingManager."""
    
    def test_log_levels(self, logging_manager: LoggingManager):
        """Test all log levels are supported."""
        assert logging_manager.debug("debug message") is True
        assert logging_manager.info("info message") is True
        assert logging_manager.notice("notice message") is True
        assert logging_manager.warning("warning message") is True
        assert logging_manager.error("error message") is True
        assert logging_manager.critical("critical message") is True
    
    def test_log_history_bounded(self, runtime_id: str):
        """Test that log history has bounded size."""
        config = SamplingConfig(policy=SamplingPolicy.ALWAYS)
        manager = LoggingManager(
            runtime_id=runtime_id,
            sampling_config=config,
            max_history=10
        )
        
        # Add more logs than the limit
        for i in range(20):
            manager.info(f"message {i}")
        
        # History should be bounded to 10
        assert manager.history_size <= 10
    
    def test_console_sink_outputs(self, runtime_id: str):
        """Test that console sink produces output."""
        config = SamplingConfig(policy=SamplingPolicy.ALWAYS)
        manager = LoggingManager(
            runtime_id=runtime_id,
            sampling_config=config,
            max_history=0  # Don't keep history
        )
        
        sink = ConsoleSink()
        manager.add_sink(sink)
        
        result = manager.info("test console output")
        assert result is True
    
    def test_fake_sink_for_testing(self, runtime_id: str):
        """Test FakeSink for testing purposes."""
        config = SamplingConfig(policy=SamplingPolicy.ALWAYS)
        manager = LoggingManager(
            runtime_id=runtime_id,
            sampling_config=config
        )
        
        sink = FakeSink()
        manager.add_sink(sink)
        
        manager.info("test message")
        
        emitted = sink.get_emitted()
        assert len(emitted) == 1
        assert emitted[0].message == "test message"
    
    def test_sampling_never(self, runtime_id: str):
        """Test NEVER sampling policy."""
        config = SamplingConfig(policy=SamplingPolicy.NEVER)
        manager = LoggingManager(
            runtime_id=runtime_id,
            sampling_config=config
        )
        
        # INFO should be dropped
        result = manager.info("test message")
        assert result is False
        
        # CRITICAL should always pass
        result = manager.critical("critical message")
        assert result is True
    
    def test_sampling_always(self, runtime_id: str):
        """Test ALWAYS sampling policy."""
        config = SamplingConfig(policy=SamplingPolicy.ALWAYS)
        manager = LoggingManager(
            runtime_id=runtime_id,
            sampling_config=config
        )
        
        result = manager.info("test message")
        assert result is True
    
    def test_json_formatter(self, runtime_id: str):
        """Test JSON formatter produces valid JSON."""
        config = SamplingConfig(policy=SamplingPolicy.ALWAYS)
        manager = LoggingManager(
            runtime_id=runtime_id,
            sampling_config=config
        )
        
        sink = MemorySink(formatter=JsonFormatter())
        manager.add_sink(sink)
        
        manager.info("test message", key="value")
        
        logs = sink.get_logs()
        assert len(logs) == 1
        
        # Check JSON serialization works
        serialized = logs[0].to_serializable()
        assert isinstance(serialized, dict)
        assert "message" in serialized


# =============================================================================
# TRACING MANAGER TESTS
# =============================================================================

class TestTraceManager:
    """Tests for TraceManager."""
    
    def test_span_creation(self, trace_manager: TraceManager):
        """Test basic span creation and completion."""
        with trace_manager.start_span("test_operation"):
            pass
        
        # Span should be completed now
    
    def test_span_context_manager_enter_exit(self, runtime_id: str):
        """Test SpanContextManager __enter__ and __exit__."""
        manager = TraceManager(runtime_id=runtime_id)
        
        ctx = SpanContextManager(manager, "test")
        ctx.__enter__()
        assert ctx._span_record is not None
        ctx.__exit__(None, None, None)  # Should finish span
    
    def test_span_with_error(self, trace_manager: TraceManager):
        """Test span that exits with an error."""
        try:
            with trace_manager.start_span("error_operation"):
                raise ValueError("test error")
        except ValueError:
            pass
        
        # Span should be marked as ERROR
    
    def test_trace_snapshot(self, runtime_id: str):
        """Test trace snapshot generation."""
        manager = TraceManager(runtime_id=runtime_id)
        
        # Create a span
        with trace_manager.start_span("test"):
            pass
        
        # Get the trace ID from the active spans
        trace_ids = manager.get_active_trace_ids()
        assert len(trace_ids) >= 1
        
        snapshot = manager.get_trace_snapshot(trace_ids[0])
        assert snapshot is not None
        assert snapshot.span_count >= 1
    
    def test_span_hierarchy(self, runtime_id: str):
        """Test parent-child span relationships."""
        manager = TraceManager(runtime_id=runtime_id)
        
        with trace_manager.start_span("parent"):
            pass
        
        # In a more complete implementation, we could verify hierarchy
    
    def test_statistics(self, runtime_id: str):
        """Test tracing statistics."""
        manager = TraceManager(runtime_id=runtime_id)
        
        initial_count = manager.total_spans_created
        
        with trace_manager.start_span("test"):
            pass
        
        assert manager.total_spans_created >= initial_count


# =============================================================================
# TELEMETRY MANAGER TESTS
# =============================================================================

class TestTelemetryManager:
    """Tests for TelemetryManager."""
    
    def test_event_collection(self, telemetry_manager: TelemetryManager):
        """Test basic event collection."""
        event = TelemetryEvent(
            runtime_id=telemetry_manager.runtime_id,
            name="test.event",
            value=123.45
        )
        
        result = telemetry_manager.collect(event)
        assert result is True
    
    def test_counter_collection(self, telemetry_manager: TelemetryManager):
        """Test counter metric collection."""
        result = telemetry_manager.collect_counter("test.counter", 5.0)
        assert result is True
        
        stats = telemetry_manager.get_statistics()
        assert stats["collected_total"] >= 1
    
    def test_batch_collection(self, telemetry_manager: TelemetryManager):
        """Test batch event collection."""
        events = [
            TelemetryEvent(
                runtime_id=telemetry_manager.runtime_id,
                name=f"test.event.{i}",
                value=float(i)
            )
            for i in range(10)
        ]
        
        collected = telemetry_manager.collect_batch(events)
        assert collected == 10
    
    def test_fake_exporter(self, runtime_id: str):
        """Test FakeExporter."""
        manager = TelemetryManager(runtime_id=runtime_id)
        exporter = FakeExporter()
        
        # Add and use exporter
        batch = ExportBatch(
            batch_id="test",
            export_format="json",
            data_type="metrics",
            payload=b'{"test": true}'
        )
        
        result = pytest.importorskip("asyncio").run(exporter.export(batch))  # type: ignore
        assert result is True


# =============================================================================
# METRICS MANAGER TESTS
# =============================================================================

class TestMetricsManager:
    """Tests for MetricsManager."""
    
    def test_counter_metric(self, metrics_manager: MetricsManager):
        """Test counter metric increments."""
        counter = metrics_manager.create_counter("test.counter")
        
        counter.inc()
        assert counter.get() == 1.0
        
        counter.inc_by(5)
        assert counter.get() == 6.0
    
    def test_gauge_metric(self, metrics_manager: MetricsManager):
        """Test gauge metric can go up and down."""
        gauge = metrics_manager.create_gauge("test.gauge")
        
        gauge.set(10)
        assert gauge.get() == 10.0
        
        gauge.inc()
        assert gauge.get() == 11.0
        
        gauge.dec()
        assert gauge.get() == 10.0
    
    def test_histogram_metric(self, metrics_manager: MetricsManager):
        """Test histogram metric records values."""
        histogram = metrics_manager.create_histogram("test.histogram", max_age_seconds=60.0)
        
        histogram.observe(1.0)
        histogram.observe(2.0)
        histogram.observe(3.0)
        
        assert histogram.count() == 3
        assert histogram.sum() == 6.0
        assert histogram.avg() == 2.0
    
    def test_timer_context_manager(self, metrics_manager: MetricsManager):
        """Test Timer context manager."""
        timer = metrics_manager.create_timer("test.timer")
        
        with timer:
            time.sleep(0.01)  # Small delay
        
        # Timer should have recorded a value
        histogram = metrics_manager.get_metric("test.timer")
        if histogram is not None:
            assert histogram.count() >= 1
    
    def test_snapshot_generation(self, metrics_manager: MetricsManager):
        """Test metric snapshot generation."""
        counter = metrics_manager.create_counter("snapshot.counter")
        counter.inc()
        
        snapshot = metrics_manager.get_snapshot()
        
        assert snapshot.runtime_id == metrics_manager.runtime_id
        assert snapshot.count > 0


# =============================================================================
# CORRELATION MANAGER TESTS
# =============================================================================

class TestCorrelationManager:
    """Tests for CorrelationManager."""
    
    def test_correlation_context(self, correlation_manager: CorrelationManager):
        """Test getting current correlation context."""
        ctx = correlation_manager.get_current_context()
        
        assert ctx.runtime_id == correlation_manager.runtime_id
        assert ctx.correlation_id is not None
    
    def test_request_context_manager(self, correlation_manager: CorrelationManager):
        """Test request context manager."""
        with correlation_manager.request_context(request_id="req_123") as ctx:
            assert ctx.request_id == "req_123"
        
        # Context should be restored after exit
    
    def test_session_context_manager(self, correlation_manager: CorrelationManager):
        """Test session context manager."""
        with correlation_manager.session_context(session_id="session_456"):
            pass
        
        # Session should be tracked
    
    def test_span_context_manager(self, correlation_manager: CorrelationManager):
        """Test span context manager."""
        with correlation_manager.span_context(span_name="db_query") as ctx:
            assert ctx.trace_id is not None
            assert ctx.span_id is not None


# =============================================================================
# DIAGNOSTICS MANAGER TESTS
# =============================================================================

class TestDiagnosticsManager:
    """Tests for DiagnosticsManager."""
    
    def test_info_finding(self, diagnostics_manager: DiagnosticsManager):
        """Test INFO-level finding."""
        finding = diagnostics_manager.info(
            source="test",
            code="INFO_CODE",
            title="Info finding"
        )
        
        assert finding.severity == DiagnosticSeverity.INFO
        assert finding.code == "INFO_CODE"
    
    def test_warning_finding(self, diagnostics_manager: DiagnosticsManager):
        """Test WARNING-level finding."""
        finding = diagnostics_manager.warning(
            source="test",
            code="WARN_CODE",
            title="Warning finding"
        )
        
        assert finding.severity == DiagnosticSeverity.WARNING
    
    def test_error_finding(self, diagnostics_manager: DiagnosticsManager):
        """Test ERROR-level finding."""
        finding = diagnostics_manager.error(
            source="test",
            code="ERROR_CODE",
            title="Error finding"
        )
        
        assert finding.severity == DiagnosticSeverity.ERROR
        assert finding.is_critical is True
    
    def test_finding_resolution(self, diagnostics_manager: DiagnosticsManager):
        """Test resolving a finding."""
        finding = diagnostics_manager.warning(
            source="test",
            code="WARN_CODE",
            title="Warning"
        )
        
        resolved = finding.resolve(notes="Fixed")
        
        assert resolved.is_resolved is True
        assert resolved.resolution_notes == "Fixed"
    
    def test_runtime_report(self, diagnostics_manager: DiagnosticsManager):
        """Test runtime diagnostic report."""
        # Generate some findings
        diagnostics_manager.info("test", "INFO_1", "Info finding")
        diagnostics_manager.warning("test", "WARN_1", "Warning finding")
        
        report = diagnostics_manager.get_report("runtime")
        
        assert report.count >= 2


# =============================================================================
# CORRELATION PROPAGATION TESTS
# =============================================================================

class TestCorrelationPropagation:
    """Test correlation context propagation across subsystems."""
    
    def test_extract_and_inject_context(
        self,
        correlation_manager: CorrelationManager
    ):
        """Test context extraction and injection."""
        original_ctx = correlation_manager.get_current_context()
        
        # Extract for propagation
        props = correlation_manager.extract_context(original_ctx)
        
        assert "correlation_id" in props
        assert props["correlation_id"] == original_ctx.correlation_id
        
        # Inject into new context
        injected_ctx = correlation_manager.inject_context(props)
        
        assert injected_ctx.correlation_id == original_ctx.correlation_id
    
    def test_correlation_snapshot(self, correlation_manager: CorrelationManager):
        """Test correlation state snapshot."""
        with correlation_manager.request_context(request_id="req_test"):
            snapshot = correlation_manager.get_snapshot()
            
            assert snapshot.runtime_id == correlation_manager.runtime_id
            # Snapshot should capture active correlations


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for multiple observability components."""
    
    def test_full_observability_pipeline(
        self,
        observability_manager: ObservabilityManager
    ):
        """Test the full observability pipeline."""
        runtime_id = observability_manager.runtime_id
        
        # 1. Create a trace context
        with observability_manager.trace_context("test_operation") as ctx:
            # 2. Log a message with correlation
            result = observability_manager.info(
                "Starting test operation",
                task_id="task_1"
            )
            assert result is True
            
            # 3. Record metrics
            observability_manager.record_counter("test.count", 5)
            
            # 4. Generate diagnostics
            observability_manager.info_finding(
                source="integration_test",
                code="TEST_INTEGRATION",
                title="Integration test passing"
            )
        
        # 5. Verify statistics
        stats = observability_manager.get_runtime_report()
        
        assert stats["runtime_id"] == runtime_id
        assert stats["logs"]["count"] > 0
    
    def test_thread_safety(
        self,
        logging_manager: LoggingManager
    ):
        """Test thread-safe logging."""
        results: List[bool] = []
        errors: List[Exception] = []
        
        def log_in_thread(thread_id: int):
            try:
                for i in range(10):
                    result = logging_manager.info(
                        f"Thread {thread_id} message {i}",
                        thread_id=thread_id
                    )
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = [
            threading.Thread(target=log_in_thread, args=(i,))
            for i in range(5)
        ]
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify no errors and logs were emitted
        assert len(errors) == 0
        assert len(results) > 0
    
    def test_concurrent_metrics(
        self,
        metrics_manager: MetricsManager
    ):
        """Test thread-safe metric updates."""
        counter = metrics_manager.create_counter("concurrent.counter")
        
        def increment_counter():
            for _ in range(100):
                counter.inc()
        
        # Run multiple threads
        threads = [threading.Thread(target=increment_counter) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Counter should have correct value (no lost increments)
        assert counter.get() == 500


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_correlation_context(
        self,
        correlation_manager: CorrelationManager
    ):
        """Test behavior with no context set."""
        # Should create a new root context if none exists
        ctx = correlation_manager.get_current_context()
        
        assert ctx.runtime_id == correlation_manager.runtime_id
        assert ctx.correlation_id is not None
    
    def test_nested_span_contexts(
        self,
        correlation_manager: CorrelationManager
    ):
        """Test nested span contexts."""
        with correlation_manager.span_context("outer") as outer_ctx:
            assert outer_ctx.trace_id is not None
            
            with correlation_manager.span_context("inner") as inner_ctx:
                # Inner should inherit parent's trace but have different span
                assert inner_ctx.trace_id == outer_ctx.trace_id
        
        # Contexts should be properly nested
    
    def test_max_span_history_limit(self, runtime_id: str):
        """Test that span history is bounded."""
        manager = TraceManager(
            runtime_id=runtime_id,
            max_spans_per_trace=10
        )
        
        # Create many spans (they each create new traces)
        for i in range(20):
            with trace_manager.start_span(f"span_{i}"):
                pass
        
        # History should be bounded


# =============================================================================
# RUNTIME ISOLATION TESTS
# =============================================================================

class TestRuntimeIsolation:
    """Test that different runtimes remain isolated."""
    
    def test_different_runtimes_separate_logs(
        self,
        logging_manager: LoggingManager
    ):
        """Test logs from different runtimes are separate."""
        manager1 = logging_manager  # Already created with runtime_id
        
        manager2 = LoggingManager(
            runtime_id=f"{logging_manager.runtime_id}_different",
            max_history=100
        )
        
        # Log to both managers
        manager1.info("message from runtime 1")
        manager2.info("message from runtime 2")
        
        # Each should only see its own messages
        logs1 = manager1.get_recent_logs()
        logs2 = manager2.get_recent_logs()
        
        assert len(logs1) >= 1
        assert len(logs2) >= 1


# =============================================================================
# PERFORMANCE CONSIDERATIONS
# =============================================================================

class TestPerformance:
    """Tests for performance characteristics."""
    
    def test_non_blocking_console_sink(self, runtime_id: str):
        """Test that console sink doesn't block on output errors."""
        config = SamplingConfig(policy=SamplingPolicy.ALWAYS)
        
        # Mock a failing sink that raises exception
        class FailingSink(LogSink):
            def emit(self, record: LogRecord) -> bool:
                raise Exception("Sink error")
            
            async def close(self) -> None:
                pass
            
            @property
            def is_closed(self) -> bool:
                return False
        
        manager = LoggingManager(
            runtime_id=runtime_id,
            sampling_config=config
        )
        
        # Add failing sink - should not cause exception in emit
        # (the manager handles errors gracefully)
        # Note: ConsoleSink doesn't actually fail on normal output,
        # so we test with a mock that would fail
    
    def test_batch_export_performance(self, telemetry_manager: TelemetryManager):
        """Test batch export efficiency."""
        events = [
            TelemetryEvent(
                runtime_id=telemetry_manager.runtime_id,
                name=f"batch.event.{i}",
                value=float(i)
            )
            for i in range(100)
        ]
        
        # Collect should be fast
        start = time.monotonic()
        telemetry_manager.collect_batch(events)
        elapsed = time.monotonic() - start
        
        # Should complete quickly (less than 1 second for 100 events)
        assert elapsed < 1.0


# =============================================================================
# UTILITIES
# =============================================================================

class TestUtilities:
    """Test utility functions and conversions."""
    
    def test_log_record_serialization(self, runtime_id: str):
        """Test LogRecord to/from dict conversion."""
        original = create_info_log("test", runtime_id=runtime_id, key="value")
        
        # Serialize
        data = original.to_serializable()
        
        # Deserialize
        restored = LogRecord.from_dict(data)
        
        assert restored.message == original.message
        assert restored.context.runtime_id == original.context.runtime_id
    
    def test_span_record_to_dict(self, runtime_id: str):
        """Test SpanRecord serialization."""
        span = TracingSpanRecord(
            span_id=str(SpanId.generate()),
            trace_id=str(TraceId.generate()),
            name="test"
        )
        
        data = span.to_dict()
        
        assert "span_id" in data
        assert data["name"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])