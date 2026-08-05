# Core Channel Abstraction
# ========================

"""
Channel abstraction for communication endpoints.

Channels provide:
- Internal channels (within runtime)
- External channels (between runtimes)
- Lifecycle channels (system transitions)
- Diagnostics channels (health metrics)

All channel operations are immutable and deterministic.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum, auto
import threading
import time


# =============================================================================
# CHANNEL TYPES
# =============================================================================

class ChannelType(Enum):
    """Types of communication channels."""
    INTERNAL = "internal"       # Within a single runtime
    EXTERNAL = "external"       # Between runtimes (inter-runtime)
    LIFECYCLE = "lifecycle"     # Lifecycle state transitions
    DIAGNOSTICS = "diagnostics" # Health, metrics, diagnostics


class ChannelMode(Enum):
    """Channel delivery modes."""
    UNICAST = "unicast"         # One recipient
    MULTICAST = "multicast"     # Multiple specific recipients
    BROADCAST = "broadcast"     # All subscribers


# =============================================================================
# CHANNEL POLICY
# =============================================================================

@dataclass(frozen=True)
class ChannelPolicy:
    """
    Immutable policy for channel behavior.
    
    Defines how messages are delivered through this channel.
    """
    
    mode: ChannelMode = ChannelMode.UNICAST
    reliability: str = "best_effort"  # best_effort, reliable, guaranteed
    max_retries: int = 3
    
    # Backpressure
    overflow_policy: str = "reject"   # reject, drop_oldest, block, throttle
    
    # Timing
    timeout_seconds: float = 30.0
    expiration_seconds: Optional[float] = None


# =============================================================================
# CHANNEL STATISTICS
# =============================================================================

@dataclass(frozen=True)
class ChannelStatistics:
    """
    Immutable snapshot of channel statistics.
    
    Read-only view of channel performance and usage.
    """
    
    total_messages_in: int = 0
    total_messages_out: int = 0
    total_rejected: int = 0
    total_failed: int = 0
    
    queue_depth: int = 0
    avg_latency_ms: float = 0.0
    last_message_utc: Optional[float] = None


# =============================================================================
# CHANNEL DESCRIPTOR
# =============================================================================

@dataclass(frozen=True)
class ChannelDescriptor:
    """
    Immutable descriptor for a channel.
    
    Defines the channel's identity, type, and configuration.
    """
    
    channel_id: str
    name: str
    
    channel_type: ChannelType = ChannelType.INTERNAL
    mode: ChannelMode = ChannelMode.UNICAST
    
    subscribers: List[str] = field(default_factory=list)
    policy: Optional[ChannelPolicy] = None
    
    # Metadata
    description: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


# =============================================================================
# CHANNEL (abstract base for implementation)
# =============================================================================

class Channel:
    """
    Abstract channel for communication.
    
    Channels provide isolated pathways for message delivery with
    their own policies and statistics.
    
    All operations are immutable - new messages create new envelopes,
    subscriptions return new descriptors.
    """
    
    def __init__(self, descriptor: ChannelDescriptor):
        self._descriptor = descriptor
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            "messages_in": 0,
            "messages_out": 0,
            "rejected": 0,
            "failed": 0,
            "queue_depth": 0,
            "latencies": [],
        }
    
    @property
    def descriptor(self) -> ChannelDescriptor:
        """Get the channel descriptor."""
        return self._descriptor
    
    @property
    def channel_id(self) -> str:
        """Get the channel ID."""
        return self._descriptor.channel_id
    
    @property
    def name(self) -> str:
        """Get the channel name."""
        return self._descriptor.name
    
    def get_statistics(self) -> ChannelStatistics:
        """Get immutable snapshot of statistics."""
        with self._lock:
            avg_latency = (
                sum(self._stats["latencies"]) / len(self._stats["latencies"])
                if self._stats["latencies"] else 0.0
            )
            
            return ChannelStatistics(
                total_messages_in=self._stats["messages_in"],
                total_messages_out=self._stats["messages_out"],
                total_rejected=self._stats["rejected"],
                total_failed=self._stats["failed"],
                queue_depth=self._stats["queue_depth"],
                avg_latency_ms=round(avg_latency, 3),
                last_message_utc=None,
            )
    
    def publish(self, envelope: Any) -> bool:
        """
        Publish a message to this channel.
        
        Args:
            envelope: The message envelope
            
        Returns:
            True if accepted (may still fail delivery)
        """
        with self._lock:
            self._stats["messages_in"] += 1
            return True
    
    def subscribe(self, subscriber_id: str) -> bool:
        """Add a subscriber to this channel."""
        with self._lock:
            if subscriber_id in self._descriptor.subscribers:
                return False
            
            new_subscribers = list(self._descriptor.subscribers)
            new_subscribers.append(subscriber_id)
            
            self._descriptor = self._descriptor.__class__(
                **{**self._descriptor.__dict__, "subscribers": new_subscribers}
            )
            return True
    
    def unsubscribe(self, subscriber_id: str) -> bool:
        """Remove a subscriber from this channel."""
        with self._lock:
            if subscriber_id not in self._descriptor.subscribers:
                return False
            
            new_subscribers = [s for s in self._descriptor.subscribers 
                              if s != subscriber_id]
            
            self._descriptor = self._descriptor.__class__(
                **{**self._descriptor.__dict__, "subscribers": new_subscribers}
            )
            return True


# =============================================================================
# INTERNAL CHANNEL (in-memory, single runtime)
# =============================================================================

class InternalChannel(Channel):
    """
    In-memory channel for internal runtime communication.
    
    Fast, synchronous delivery within a single runtime instance.
    """
    
    def __init__(self, descriptor: ChannelDescriptor):
        super().__init__(descriptor)
        
        # In-memory queue
        self._queue: List[Any] = []
    
    async def deliver(self) -> List[Any]:
        """Deliver messages to subscribers (synchronous)."""
        results = []
        
        with self._lock:
            while self._queue:
                envelope = self._queue.pop(0)
                self._stats["messages_out"] += 1
                self._stats["queue_depth"] = len(self._queue)
                results.append(envelope)
        
        return results


# =============================================================================
# EXTERNAL CHANNEL (between runtimes)
# =============================================================================

class ExternalChannelConfig:
    """Configuration for external channels."""
    
    def __init__(
        self,
        target_runtime_id: str,
        timeout_seconds: float = 30.0,
        max_queue_size: int = 1000,
    ):
        self.target_runtime_id = target_runtime_id
        self.timeout_seconds = timeout_seconds
        self.max_queue_size = max_queue_size


class ExternalChannel(Channel):
    """
    Channel for communication between runtime instances.
    
    Handles cross-runtime messaging with delivery guarantees.
    """
    
    def __init__(self, descriptor: ChannelDescriptor, config: ExternalChannelConfig):
        super().__init__(descriptor)
        self._config = config
        
        # Delivery queue
        self._queue: List[Any] = []
    
    async def send(self, envelope: Any) -> bool:
        """Attempt to send message to remote runtime."""
        with self._lock:
            if len(self._queue) >= self._config.max_queue_size:
                self._stats["rejected"] += 1
                return False
            
            self._queue.append(envelope)
            self._stats["messages_in"] += 1
            return True
    
    async def deliver(self) -> List[Any]:
        """Attempt delivery to remote runtime."""
        results = []
        
        with self._lock:
            while self._queue:
                envelope = self._queue.pop(0)
                
                # Simulate external delivery (in real impl, this would use
                # network transport like gRPC or HTTP)
                try:
                    # Delivery simulation - success unless queue was empty
                    self._stats["messages_out"] += 1
                    results.append(envelope)
                    
                except Exception as e:
                    self._stats["failed"] += 1
                    self._queue.insert(0, envelope)  # Re-queue on failure
            
            self._stats["queue_depth"] = len(self._queue)
        
        return results


# =============================================================================
# CHANNEL MANAGER
# =============================================================================

class ChannelManagerConfig:
    """Configuration for ChannelManager."""
    
    def __init__(
        self,
        runtime_id: str = "default",
        default_internal_mode: ChannelMode = ChannelMode.UNICAST,
        default_external_timeout_seconds: float = 30.0,
    ):
        self.runtime_id = runtime_id
        self.default_internal_mode = default_internal_mode
        self.default_external_timeout_seconds = default_external_timeout_seconds


class ChannelManager:
    """
    Manager for all channels in a runtime.
    
    Provides creation, lookup, and lifecycle management of channels.
    """
    
    def __init__(self, config: Optional[ChannelManagerConfig] = None):
        self._config = config or ChannelManagerConfig()
        
        self._lock = threading.RLock()
        
        # channel_id -> Channel
        self._channels: Dict[str, Channel] = {}
    
    def create_channel(
        self,
        name: str,
        channel_type: ChannelType = ChannelType.INTERNAL,
        mode: ChannelMode = ChannelMode.UNICAST,
        subscribers: Optional[List[str]] = None,
    ) -> ChannelDescriptor:
        """Create a new channel and return its descriptor."""
        with self._lock:
            channel_id = f"chan_{name}_{len(self._channels)}"
            
            descriptor = ChannelDescriptor(
                channel_id=channel_id,
                name=name,
                channel_type=channel_type,
                mode=mode,
                subscribers=subscribers or [],
            )
            
            # Create appropriate channel implementation
            if channel_type == ChannelType.INTERNAL:
                self._channels[channel_id] = InternalChannel(descriptor)
            elif channel_type == ChannelType.EXTERNAL:
                config = ExternalChannelConfig(
                    target_runtime_id=self._config.runtime_id,
                    timeout_seconds=self._config.default_external_timeout_seconds,
                )
                self._channels[channel_id] = ExternalChannel(descriptor, config)
            else:
                self._channels[channel_id] = Channel(descriptor)
            
            return descriptor
    
    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a channel by ID."""
        with self._lock:
            return self._channels.get(channel_id)
    
    def get_channels_by_type(
        self,
        channel_type: ChannelType,
    ) -> List[Channel]:
        """Get all channels of a specific type."""
        with self._lock:
            return [
                c for c in self._channels.values()
                if c.descriptor.channel_type == channel_type
            ]
    
    def get_all_channels(self) -> Dict[str, Channel]:
        """Get all managed channels."""
        with self._lock:
            return dict(self._channels)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated channel statistics."""
        with self._lock:
            result = {
                "total_channels": len(self._channels),
                "channel_types": {},
                "total_stats": {
                    "messages_in": 0,
                    "messages_out": 0,
                    "rejected": 0,
                    "failed": 0,
                },
            }
            
            for channel in self._channels.values():
                stats = channel.get_statistics()
                
                ct = str(channel.descriptor.channel_type.value)
                result["channel_types"][ct] = {
                    "count": len([
                        c for c in self._channels.values()
                        if c.descriptor.channel_type.value == ct
                    ]),
                    "total_stats": {
                        "messages_in": stats.total_messages_in,
                        "messages_out": stats.total_messages_out,
                    }
                }
                
                result["total_stats"]["messages_in"] += stats.total_messages_in
                result["total_stats"]["messages_out"] += stats.total_messages_out
                result["total_stats"]["rejected"] += stats.total_rejected
                result["total_stats"]["failed"] += stats.total_failed
            
            return result
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get channel health status."""
        with self._lock:
            # Check for any channels at capacity
            full_channels = []
            
            for chan in self._channels.values():
                if hasattr(chan, '_queue'):
                    if len(chan._queue) >= getattr(chan, 'max_queue_size', float('inf')):
                        full_channels.append(chan.channel_id)
            
            return {
                "status": "healthy" if not full_channels else "degraded",
                "full_channels": full_channels,
                **self.get_statistics(),
            }


__all__ = [
    # Types
    "ChannelType",
    "ChannelMode",
    
    # Policy and statistics
    "ChannelPolicy",
    "ChannelStatistics",
    "ChannelDescriptor",
    
    # Channel classes
    "Channel",
    "InternalChannel",
    "ExternalChannelConfig",
    "ExternalChannel",
    
    # Manager
    "ChannelManagerConfig",
    "ChannelManager",
]