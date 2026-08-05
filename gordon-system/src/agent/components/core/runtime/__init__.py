# Core Runtime Package
# ====================

"""
Core runtime infrastructure for Phase 3.7.25-R Model Runtime Architecture.

This package provides:
- Model lifecycle management (load, unload, warm-up, execution)
- Compute orchestration (CPU/GPU scheduling, resource allocation)
- Inference infrastructure (queues, batching, KV cache management)
- Resource accounting and monitoring

Architecture Boundaries:
- Does NOT own cognition, reasoning, planning
- Does NOT own prompt construction or memory semantics
- Does NOT own capability routing (handled by providers)

Runtime owns:
- Model lifecycle
- Inference execution
- Runtime allocation
- Compute scheduling
- Model loading/unloading
- GPU ownership
- Batching queues
- Runtime compatibility
- Inference monitoring
"""

from .model_registry import (
    ModelRegistry,
    ModelDescriptor,
    ModelIdentity,
    ModelStatus,
    RegistrationError,
)

from .compute_scheduler import (
    ComputeScheduler,
    ComputeResource,
    ComputeAllocation,
    SchedulingPolicy,
    ResourceExhaustedError,
)

from .inference_queue import (
    InferenceQueue,
    InferenceRequest,
    InferenceResponse,
    BatchConfig,
    QueueTimeoutError,
    RequestCancelledError,
)

from .model_loader import (
    ModelLoader,
    LoadResult,
    UnloadResult,
    LoadingState,
    UnsupportedModelError,
)

from .resource_allocator import (
    ResourceAllocator,
    VRAMTracker,
    RAMTracker,
    ResourceLease,
    ResourceState,
    ResourceError,
)

from .monitoring import (
    RuntimeMonitor,
    InferenceMetrics,
    QueueMetrics,
    ResourceMetrics,
    HealthStatus,
)

__all__ = [
    # Model Registry
    "ModelRegistry",
    "ModelDescriptor",
    "ModelIdentity",
    "ModelStatus",
    "RegistrationError",
    # Compute Scheduler
    "ComputeScheduler",
    "ComputeResource",
    "ComputeAllocation",
    "SchedulingPolicy",
    "ResourceExhaustedError",
    # Inference Queue
    "InferenceQueue",
    "InferenceRequest",
    "InferenceResponse",
    "BatchConfig",
    "QueueTimeoutError",
    "RequestCancelledError",
    # Model Loader
    "ModelLoader",
    "LoadResult",
    "UnloadResult",
    "LoadingState",
    "UnsupportedModelError",
    # Resource Allocator
    "ResourceAllocator",
    "VRAMTracker",
    "RAMTracker",
    "ResourceLease",
    "ResourceState",
    "ResourceError",
    # Monitoring
    "RuntimeMonitor",
    "InferenceMetrics",
    "QueueMetrics",
    "ResourceMetrics",
    "HealthStatus",
]