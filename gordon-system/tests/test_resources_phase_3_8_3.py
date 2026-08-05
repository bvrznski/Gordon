# Core Resources Phase 3.8.3 Tests
# ===================================
"""
Comprehensive tests for Phase 3.8.3 - Canonical Resource Interface Hierarchy,
Provider Architecture, Pooling Subsystem, and Monitoring Layer.

Tests cover:
- Resource interface contracts (Protocol-based)
- Provider architecture (CPU, GPU, Memory, Storage, Network)
- Resource pooling with warm resources
- Health evaluation and monitoring
- Accounting and metrics
"""

import unittest
import time
from typing import Optional

# Phase 3.8.3 imports - relative imports for the test environment
import sys
sys.path.insert(0, 'gordon-system/src')

from agent.components.core.resources.interfaces import (
    ResourceId,
    ResourceDomain,
    ResourceState,
    ResourceCapability,
    ResourceCapabilities,
    ResourceMetadata,
    ResourceHandle,
)

from agent.components.core.resources.pooling import (
    PoolResourceState,
    PoolResourceEntry,
    ResourcePoolConfig,
    PoolAcquisitionResult,
    ResourcePool,
    PoolBackedResource,
    ResourcePoolManager,
)

from agent.components.core.resources.monitoring import (
    HealthState as InterfaceHealthState,
    HealthTransition,
    HealthObservation,
    HealthEvaluator,
    AllocationEvent as InterfaceAllocationEvent,
    AllocationRecord,
    ResourceAccounting,
    MetricPoint,
    ResourceMetrics,
    LogSeverity,
    ResourceEvent,
    ResourceLogger,
    TraceSpan,
    ResourceTracer,
)

from agent.components.core.resources.providers import (
    ProviderType,
    ProviderState,
    ProviderIdentity,
    ProviderConfig,
    CPUResource,
    GPUDevice,
    MemoryResource,
    StorageDevice,
    NetworkInterface,
    CPUProvider,
    GPUProvider,
    MemoryProvider,
    StorageProvider,
    NetworkProvider,
    ProviderRegistry,
)


# =============================================================================
# Test Resource Interfaces
# =============================================================================


class TestResourceInterfaces(unittest.TestCase):
    """Tests for Protocol-based resource interfaces."""

    def test_resource_id_generation(self) -> None:
        """Test ResourceId generation."""
        rid1 = ResourceId.generate()
        rid2 = ResourceId.generate()

        self.assertTrue(str(rid1).startswith("res_"))
        self.assertTrue(str(rid2).startswith("res_"))
        self.assertNotEqual(rid1, rid2)

    def test_resource_domain_creation(self) -> None:
        """Test ResourceDomain creation."""
        domain = ResourceDomain("cpu_cores")
        self.assertEqual(domain.value, "cpu_cores")

    def test_resource_state_enum(self) -> None:
        """Test ResourceState enum values."""
        states = list(ResourceState)
        self.assertIn(ResourceState.AVAILABLE, states)
        self.assertIn(ResourceState.ALLOCATED, states)
        self.assertIn(ResourceState.LEASED, states)

    def test_resource_capability_creation(self) -> None:
        """Test ResourceCapability creation."""
        cap = ResourceCapability(name="cuda", version="12.0")
        self.assertEqual(cap.name, "cuda")
        self.assertEqual(cap.version, "12.0")
        self.assertTrue(cap.enabled)

    def test_resource_capabilities_collection(self) -> None:
        """Test ResourceCapabilities collection."""
        caps = ResourceCapabilities(
            compute=("fp64", "int8"),
            memory=("ecc",),
            io=("nvlink",),
        )
        all_caps = caps.all_capabilities

        self.assertEqual(len(all_caps), 5)
        self.assertTrue(any(c.name == "compute:fp64" for c in all_caps))
        self.assertTrue(any(c.name == "memory:ecc" for c in all_caps))

    def test_resource_metadata_creation(self) -> None:
        """Test ResourceMetadata creation."""
        metadata = ResourceMetadata(
            resource_id="res_123",
            domain="cpu_cores",
            kind="logical_core",
            vendor="system",
        )
        self.assertEqual(metadata.resource_id, "res_123")
        self.assertEqual(metadata.domain, "cpu_cores")

    def test_resource_handle_creation(self) -> None:
        """Test ResourceHandle creation and validation."""
        handle = ResourceHandle(
            handle_id="handle_001",
            resource_id="res_123",
            owner_id="task_456",
            created_at_utc=time.time(),
            expires_at_utc=time.time() + 3600,  # 1 hour
        )

        self.assertTrue(handle.is_valid())
        self.assertTrue(handle.is_valid(owner_id="task_456"))
        self.assertFalse(handle.is_valid(owner_id="wrong_owner"))


# =============================================================================
# Test Pooling Subsystem
# =============================================================================


class TestPoolingSubsystem(unittest.TestCase):
    """Tests for Resource pooling with warm resources."""

    def test_pool_config_creation(self) -> None:
        """Test ResourcePoolConfig creation."""
        config = ResourcePoolConfig(
            pool_id="test_pool",
            domain="cpu_cores",
            min_size=2,
            max_size=100,
            warm_count=5,
        )
        self.assertEqual(config.pool_id, "test_pool")
        self.assertEqual(config.domain, "cpu_cores")

    def test_resource_pool_add_and_acquire(self) -> None:
        """Test adding resources and acquiring from pool."""
        config = ResourcePoolConfig(
            pool_id="cpu_pool",
            domain="cpu_cores",
        )
        pool = ResourcePool(config)

        # Add some resources
        resource1 = pool.add_resource("core_0")
        resource2 = pool.add_resource("core_1")

        self.assertEqual(pool.size, 2)
        self.assertEqual(pool.available_count, 2)

        # Acquire a resource
        result = pool.acquire(owner_id="task_123", priority=1)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.resource)
        self.assertIsNotNone(result.handle)

        self.assertEqual(pool.active_count, 1)
        self.assertEqual(pool.available_count, 1)

    def test_pool_release_resource(self) -> None:
        """Test releasing resources back to pool."""
        config = ResourcePoolConfig(
            pool_id="cpu_pool",
            domain="cpu_cores",
        )
        pool = ResourcePool(config)

        resource = pool.add_resource("core_0")
        result = pool.acquire(owner_id="task_123")

        self.assertTrue(result.success)
        handle = result.handle

        # Release the resource
        released = pool.release(resource, handle, recycle=True)
        self.assertTrue(released)

        self.assertEqual(pool.active_count, 0)
        self.assertEqual(pool.available_count, 1)

    def test_pool_warm_resources(self) -> None:
        """Test warming resources for faster acquisition."""
        config = ResourcePoolConfig(
            pool_id="cpu_pool",
            domain="cpu_cores",
            warm_count=3,
        )
        pool = ResourcePool(config)

        # Add more resources
        for i in range(5):
            pool.add_resource(f"core_{i}")

        # Warm some resources
        warmed = pool.warm_resources(count=2)
        self.assertEqual(len(warmed), 2)

    def test_pool_manager_register_and_discover(self) -> None:
        """Test ResourcePoolManager registration."""
        manager = ResourcePoolManager()

        config1 = ResourcePoolConfig(
            pool_id="cpu_pool_0",
            domain="cpu_cores",
        )
        pool1 = ResourcePool(config1)
        manager.register_pool(pool1)

        config2 = ResourcePoolConfig(
            pool_id="gpu_pool_0",
            domain="gpu_vram_mb",
        )
        pool2 = ResourcePool(config2)
        manager.register_pool(pool2)

        self.assertEqual(len(manager.get_pools_for_domain("cpu_cores")), 1)
        self.assertEqual(len(manager.get_providers_for_type.__func__.__code__.co_varnames), 0)  # Just checking imports work


# =============================================================================
# Test Monitoring Layer
# =============================================================================


class TestMonitoringLayer(unittest.TestCase):
    """Tests for Resource monitoring, health evaluation, and accounting."""

    def test_health_state_enum(self) -> None:
        """Test HealthState enum values."""
        states = list(InterfaceHealthState)
        self.assertIn(InterfaceHealthState.HEALTHY, states)
        self.assertIn(InterfaceHealthState.FAILED, states)

    def test_health_transitions(self) -> None:
        """Test health state transitions."""
        evaluator = HealthEvaluator(resource_id="res_001", domain="cpu_cores")

        # Initial state should be UNKNOWN
        self.assertEqual(evaluator.current_state, InterfaceHealthState.UNKNOWN)

        # Observe metrics and check transition
        transition = evaluator.observe("utilization", 0.5)
        self.assertIsNotNone(transition)

    def test_health_evaluator_evaluate_state(self) -> None:
        """Test health state evaluation logic."""
        evaluator = HealthEvaluator(resource_id="res_001", domain="cpu_cores")

        # Low utilization should be HEALTHY
        evaluator.observe("utilization", 0.3)
        self.assertEqual(evaluator.current_state, InterfaceHealthState.HEALTHY)

        # High utilization should be SATURATED or BUSY
        evaluator.observe("utilization", 0.85)
        state = evaluator.current_state
        self.assertIn(state, [InterfaceHealthState.BUSY, InterfaceHealthState.SATURATED])

    def test_health_observation_creation(self) -> None:
        """Test HealthObservation creation."""
        obs = HealthObservation(
            metric_name="utilization",
            value=0.75,
            threshold=0.9,
            severity="warning",
        )
        self.assertEqual(obs.metric_name, "utilization")
        self.assertEqual(obs.value, 0.75)

    def test_resource_accounting_record_allocation(self) -> None:
        """Test recording allocation events."""
        accounting = ResourceAccounting(runtime_id="runtime_1")

        record = accounting.record_allocation(
            resource_id="res_001",
            domain="cpu_cores",
            owner_id="task_123",
            quantity=4.0,
        )

        self.assertEqual(record.event_type, InterfaceAllocationEvent.CREATED)
        self.assertEqual(record.quantity, 4.0)

    def test_resource_accounting_record_release(self) -> None:
        """Test recording release events."""
        accounting = ResourceAccounting(runtime_id="runtime_1")

        # Record allocation first
        accounting.record_allocation("res_001", "cpu_cores", "task_123", 4.0)

        # Then record release
        record = accounting.record_release(
            resource_id="res_001",
            owner_id="task_123",
            domain="cpu_cores",
            quantity=4.0,
        )

        self.assertEqual(record.event_type, InterfaceAllocationEvent.RELEASED)
        self.assertEqual(record.quantity, -4.0)

    def test_resource_metrics_recording(self) -> None:
        """Test ResourceMetrics recording."""
        metrics = ResourceMetrics()

        # Record allocation latency
        metrics.record_allocation_latency("cpu_cores", 0.015)

        # Record utilization
        metrics.record_utilization("cpu_cores", 0.75)

        # Get metric points
        points = metrics.get_metric("allocation_latency")
        self.assertGreater(len(points), 0)

    def test_resource_logger_emit(self) -> None:
        """Test ResourceLogger event emission."""
        logger = ResourceLogger(runtime_id="runtime_1")

        event = logger.info(
            category="allocation",
            event_type="created",
            message="Resource allocated successfully",
            resource_id="res_001",
            owner_id="task_123",
            domain="cpu_cores",
        )

        self.assertEqual(event.severity, LogSeverity.INFO)
        self.assertEqual(event.category, "allocation")

    def test_resource_logger_get_events(self) -> None:
        """Test getting logged events with filtering."""
        logger = ResourceLogger(runtime_id="runtime_1")

        logger.info("test", "event1", "Message 1")
        logger.warning("test", "event2", "Message 2")
        logger.error("test", "event3", "Message 3")

        # Get all events
        events = logger.get_events()
        self.assertEqual(len(events), 3)

    def test_resource_tracer_spans(self) -> None:
        """Test ResourceTracer span creation and management."""
        tracer = ResourceTracer()

        # Start a span
        span = tracer.start_span(
            name="allocate_resources",
            resource_id="res_001",
            owner_id="task_123",
        )

        self.assertEqual(span.name, "allocate_resources")
        self.assertEqual(span.status, "started")

        # End the span
        ended_span = tracer.end_span(span, status="completed")
        self.assertEqual(ended_span.status, "completed")


# =============================================================================
# Test Provider Architecture
# =============================================================================


class TestProviderArchitecture(unittest.TestCase):
    """Tests for provider architecture and implementations."""

    def test_provider_identity_creation(self) -> None:
        """Test ProviderIdentity creation."""
        identity = ProviderIdentity(
            provider_id="cpu_provider_0",
            provider_type=ProviderType.CPU,
            version="1.0.0",
            hostname="host_0",
        )
        self.assertEqual(identity.provider_id, "cpu_provider_0")
        self.assertEqual(identity.provider_type, ProviderType.CPU)

    def test_provider_config_creation(self) -> None:
        """Test ProviderConfig creation."""
        identity = ProviderIdentity(
            provider_id="test_provider",
            provider_type=ProviderType.MEMORY,
            version="1.0",
        )
        config = ProviderConfig(
            identity=identity,
            enabled=True,
            refresh_interval_seconds=30.0,
        )
        self.assertTrue(config.enabled)

    def test_cpu_provider_discovery(self) -> None:
        """Test CPU provider resource discovery."""
        identity = ProviderIdentity(
            provider_id="cpu_0",
            provider_type=ProviderType.CPU,
            version="1.0",
        )
        config = CPUProviderConfig(identity=identity)
        provider = CPUProvider(config)

        resources = provider.discover_resources()

        self.assertGreater(len(resources), 0)
        resource, metadata = resources[0]
        self.assertIsInstance(resource, CPUResource)
        self.assertEqual(metadata.domain, "cpu_cores")

    def test_gpu_provider_discovery(self) -> None:
        """Test GPU provider resource discovery."""
        identity = ProviderIdentity(
            provider_id="gpu_0",
            provider_type=ProviderType.GPU,
            version="1.0",
        )
        config = GPUProviderConfig(identity=identity, device_ids=[0])
        provider = GPUProvider(config)

        resources = provider.discover_resources()

        self.assertGreater(len(resources), 0)
        resource, metadata = resources[0]
        self.assertIsInstance(resource, GPUDevice)
        self.assertEqual(metadata.domain, "gpu_vram_mb")

    def test_memory_provider_discovery(self) -> None:
        """Test Memory provider resource discovery."""
        identity = ProviderIdentity(
            provider_id="memory_0",
            provider_type=ProviderType.MEMORY,
            version="1.0",
        )
        config = MemoryProviderConfig(identity=identity)
        provider = MemoryProvider(config)

        resources = provider.discover_resources()

        self.assertGreater(len(resources), 0)
        resource, metadata = resources[0]
        self.assertIsInstance(resource, MemoryResource)
        self.assertEqual(metadata.domain, "memory_mb")

    def test_storage_provider_discovery(self) -> None:
        """Test Storage provider resource discovery."""
        identity = ProviderIdentity(
            provider_id="storage_0",
            provider_type=ProviderType.STORAGE,
            version="1.0",
        )
        config = StorageProviderConfig(identity=identity)
        provider = StorageProvider(config)

        resources = provider.discover_resources()

        self.assertGreater(len(resources), 0)
        resource, metadata = resources[0]
        self.assertIsInstance(resource, StorageDevice)
        self.assertEqual(metadata.domain, "storage_gb")

    def test_network_provider_discovery(self) -> None:
        """Test Network provider resource discovery."""
        identity = ProviderIdentity(
            provider_id="network_0",
            provider_type=ProviderType.NETWORK,
            version="1.0",
        )
        config = NetworkProviderConfig(identity=identity)
        provider = NetworkProvider(config)

        resources = provider.discover_resources()

        self.assertGreater(len(resources), 0)
        resource, metadata = resources[0]
        self.assertIsInstance(resource, NetworkInterface)
        self.assertEqual(metadata.domain, "network_mbps")

    def test_provider_registry(self) -> None:
        """Test ProviderRegistry registration and discovery."""
        registry = ProviderRegistry(runtime_id="runtime_1")

        # Create providers
        cpu_identity = ProviderIdentity(
            provider_id="cpu_0",
            provider_type=ProviderType.CPU,
            version="1.0",
        )
        cpu_config = CPUProviderConfig(identity=cpu_identity)
        cpu_provider = CPUProvider(cpu_config)

        # Register
        self.assertTrue(registry.register_provider(cpu_provider))

        # Discover all resources
        discovered = registry.discover_all_resources()
        self.assertIn("cpu_0", discovered)

    def test_provider_health_check(self) -> None:
        """Test provider health checking."""
        identity = ProviderIdentity(
            provider_id="cpu_0",
            provider_type=ProviderType.CPU,
            version="1.0",
        )
        config = CPUProviderConfig(identity=identity)
        provider = CPUProvider(config)

        state, reason = provider.check_provider_health()
        self.assertEqual(state, ProviderState.HEALTHY)
        self.assertIsNone(reason)


# =============================================================================
# Test Integration: Pool + Monitoring
# =============================================================================


class TestPoolMonitoringIntegration(unittest.TestCase):
    """Tests for pool and monitoring integration."""

    def test_pool_with_health_monitoring(self) -> None:
        """Test that pools can integrate with health monitoring."""
        config = ResourcePoolConfig(
            pool_id="test_pool",
            domain="cpu_cores",
        )
        pool = ResourcePool(config)

        # Add resource
        resource = pool.add_resource("core_0")

        # Monitor its state
        snapshot = pool.get_state_snapshot()
        self.assertEqual(snapshot["active_count"], 0)
        self.assertEqual(snapshot["idle_count"], 1)


# =============================================================================
# Test Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling."""

    def test_pool_acquire_from_empty(self) -> None:
        """Test acquiring from an empty pool."""
        config = ResourcePoolConfig(
            pool_id="empty_pool",
            domain="cpu_cores",
        )
        pool = ResourcePool(config)

        result = pool.acquire(owner_id="task_123")
        self.assertFalse(result.success)
        self.assertTrue(result.exhausted)

    def test_pool_release_unknown_resource(self) -> None:
        """Test releasing an unknown resource."""
        config = ResourcePoolConfig(
            pool_id="test_pool",
            domain="cpu_cores",
        )
        pool = ResourcePool(config)

        # Create a fake resource
        class FakeResource:
            resource_id = "unknown"

        result = pool.release(FakeResource(), None, recycle=True)
        self.assertFalse(result)

    def test_accounting_negative_quantity(self) -> None:
        """Test accounting with negative quantity (release)."""
        accounting = ResourceAccounting(runtime_id="runtime_1")

        # Record a release without prior allocation
        record = accounting.record_release(
            resource_id="res_001",
            owner_id="task_123",
            domain="cpu_cores",
            quantity=2.0,
        )

        self.assertEqual(record.quantity, -2.0)
        # Should be capped at 0
        self.assertGreaterEqual(accounting.get_owner_allocation("task_123"), 0)


# =============================================================================
# Test Performance and Concurrency
# =============================================================================


class TestConcurrency(unittest.TestCase):
    """Tests for thread safety."""

    def test_pool_concurrent_access(self) -> None:
        """Test pool operations from multiple threads."""
        import threading

        config = ResourcePoolConfig(
            pool_id="concurrent_pool",
            domain="cpu_cores",
        )
        pool = ResourcePool(config)

        # Add resources
        for i in range(10):
            pool.add_resource(f"core_{i}")

        acquired_count = [0]

        def acquire_and_release():
            result = pool.acquire(owner_id="thread_task")
            if result.success:
                acquired_count[0] += 1
                pool.release(result.resource, result.handle)

        threads = []
        for _ in range(20):
            t = threading.Thread(target=acquire_and_release)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Should have acquired all resources (with recycling)
        self.assertGreater(acquired_count[0], 0)

    def test_accounting_concurrent_operations(self) -> None:
        """Test accounting concurrent operations."""
        import threading

        accounting = ResourceAccounting(runtime_id="runtime_1")

        def record_allocations():
            for i in range(10):
                accounting.record_allocation(
                    resource_id=f"res_{i}",
                    domain="cpu_cores",
                    owner_id="concurrent_task",
                    quantity=1.0,
                )

        threads = []
        for _ in range(5):
            t = threading.Thread(target=record_allocations)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Check final counts
        self.assertEqual(accounting.get_owner_allocation("concurrent_task"), 50.0)


if __name__ == "__main__":
    unittest.main()