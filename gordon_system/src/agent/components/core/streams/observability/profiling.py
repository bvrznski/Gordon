# Stream Profiling Layer - Phase 3.11.16
# =======================================

"""
Canonical Stream Profiling implementation.

Profiling is PASSIVE performance measurement:
- It NEVER influences execution flow
- It NEVER changes scheduling decisions
- It ONLY measures and reports resource usage

Supported profiling:
- CPU: CPU time consumption
- Memory: Memory allocation and usage
- Allocations: Object allocation counts
- Throughput: Records processed per second
- Latency: Time between operations
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time

# =============================================================================
# PROFILE MEASUREMENT
# =============================================================================


@dataclass(frozen=True)
class ProfileMeasurement:
    """
    Immutable profiling measurement.
    
    A single measurement of a resource at a point in time.
    """
    
    # Identity
    measurement_id: str             # Unique ID for this measurement
    
    # Timestamp
    timestamp_utc: float            # When measurement was taken
    
    # Resource type
    resource_type: str              # e.g., "cpu", "memory"
    
    # Value
    value: float                    # Measured value
    
    # Stream context
    stream_id: Optional[str] = None     # Which stream?
    component_id: Optional[str] = None  # Which component?
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "measurement_id": self.measurement_id,
            "timestamp_utc": self.timestamp_utc,
            "resource_type": self.resource_type,
            "value": self.value,
            "stream_id": self.stream_id,
            "component_id": self.component_id,
        }


# =============================================================================
# PROFILING RESULT
# =============================================================================


@dataclass(frozen=True)
class ProfilingResult:
    """
    Immutable profiling result for a stream.
    
    Contains all profiling measurements for analysis.
    """
    
    # Identity
    profile_session_id: str         # Session identifier
    
    # Timestamps
    started_at_utc: float           # When profiling began
    ended_at_utc: Optional[float]   # When profiling ended (None if ongoing)
    
    # Stream context
    stream_id: str                  # Which stream?
    
    # Measurements
    measurements: Tuple[ProfileMeasurement, ...] = field(default_factory=tuple)
    
    def __post_init__(self):
        """Post-initialization to set computed fields."""
        pass  # No computed fields needed
    
    def get_measurements_for_resource(
        self,
        resource_type: str
    ) -> Tuple[ProfileMeasurement, ...]:
        """Get measurements for a specific resource type."""
        return tuple(m for m in self.measurements if m.resource_type == resource_type)


# =============================================================================
# CPU PROFILE
# =============================================================================


@dataclass(frozen=True)
class CPUProfile:
    """
    Immutable CPU profiling data.
    
    Contains CPU time measurements for analysis.
    """
    
    # Identity
    profile_id: str                 # Unique ID
    
    # Timestamps
    started_at_utc: float           # When profiling began
    ended_at_utc: float             # When profiling ended
    
    # Stream context
    stream_id: str                  # Which stream?
    
    # CPU time measurements (in seconds)
    user_time_seconds: float        # User CPU time
    system_time_seconds: float      # System CPU time
    total_time_seconds: float       # Total CPU time
    
    # Sample count
    sample_count: int = 0           # Number of samples collected
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "profile_id": self.profile_id,
            "started_at_utc": self.started_at_utc,
            "ended_at_utc": self.ended_at_utc,
            "stream_id": self.stream_id,
            "user_time_seconds": self.user_time_seconds,
            "system_time_seconds": self.system_time_seconds,
            "total_time_seconds": self.total_time_seconds,
            "sample_count": self.sample_count,
        }


# =============================================================================
# MEMORY PROFILE
# =============================================================================


@dataclass(frozen=True)
class MemoryProfile:
    """
    Immutable memory profiling data.
    
    Contains memory allocation measurements for analysis.
    """
    
    # Identity
    profile_id: str                 # Unique ID
    
    # Timestamps
    captured_at_utc: float          # When measurement was taken
    
    # Stream context
    stream_id: str                  # Which stream?
    
    # Memory measurements (in bytes)
    current_bytes: int = 0          # Current memory usage
    peak_bytes: int = 0             # Peak memory usage
    allocated_bytes: int = 0        # Total allocated bytes
    
    # Allocation statistics
    allocation_count: int = 0       # Number of allocations
    deallocation_count: int = 0     # Number of deallocations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "profile_id": self.profile_id,
            "captured_at_utc": self.captured_at_utc,
            "stream_id": self.stream_id,
            "current_bytes": self.current_bytes,
            "peak_bytes": self.peak_bytes,
            "allocated_bytes": self.allocated_bytes,
            "allocation_count": self.allocation_count,
            "deallocation_count": self.deallocation_count,
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_profile_measurement(
    resource_type: str,
    value: float,
    stream_id: Optional[str] = None,
) -> ProfileMeasurement:
    """Create a new profile measurement."""
    return ProfileMeasurement(
        measurement_id=f"prof-{time.monotonic_ns()}-{hash(resource_type) % 1000:04d}",
        timestamp_utc=time.time(),
        resource_type=resource_type,
        value=value,
        stream_id=stream_id,
    )


def create_cpu_profile(
    stream_id: str,
    user_time_seconds: float,
    system_time_seconds: float,
    sample_count: int = 0,
) -> CPUProfile:
    """Create a new CPU profile."""
    now = time.time()
    return CPUProfile(
        profile_id=f"cpu-profile-{time.monotonic_ns()}",
        started_at_utc=now - 60.0,  # Default 1 minute window
        ended_at_utc=now,
        stream_id=stream_id,
        user_time_seconds=user_time_seconds,
        system_time_seconds=system_time_seconds,
        total_time_seconds=user_time_seconds + system_time_seconds,
        sample_count=sample_count,
    )


def create_memory_profile(
    stream_id: str,
    current_bytes: int = 0,
    peak_bytes: int = 0,
) -> MemoryProfile:
    """Create a new memory profile."""
    return MemoryProfile(
        profile_id=f"mem-profile-{time.monotonic_ns()}",
        captured_at_utc=time.time(),
        stream_id=stream_id,
        current_bytes=current_bytes,
        peak_bytes=peak_bytes,
    )


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) 
                      for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Measurements and results
    "ProfileMeasurement",
    "ProfilingResult",
    
    # Profile types
    "CPUProfile",
    "MemoryProfile",
    
    # Factory functions
    "create_profile_measurement",
    "create_cpu_profile",
    "create_memory_profile",
    "dataclass_replace",
]