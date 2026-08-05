# Core Communication Coordinator
# =============================

"""
Canonical CommunicationCoordinator for orchestrating all communication authorities.

This is ONE authority for:
- Orchestration (coordinating EventBus, MessageRouter, SignalManager)
- Communication lifecycle (startup, shutdown, health monitoring)
- Communication diagnostics (aggregating metrics from all authorities)
- Communication health (overall system health based on all components)

The Coordinator NEVER:
- Owns runtime state
- Performs business logic
- Mutates communication artifacts

It only coordinates and monitors the underlying communication infrastructure.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import threading
import time

from .event_bus import EventBus, EventBusConfig, get_event_bus
from .message_router import MessageRouter, MessageRouterConfig, RoutingPolicy, RouteResult
from .signal_manager import SignalManager, SignalManagerConfig


# =============================================================================
# COORDINATOR CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class CoordinatorConfig:
    """Configuration for CommunicationCoordinator."""
    
    runtime_id: str = "default"
    
    # Component configurations
    event_bus_config: Optional[EventBusConfig] = None
    message_router_config: Optional[MessageRouterConfig] = None
    signal_manager_config: Optional[SignalManagerConfig] = None
    
    # Behavior settings
    start_components_automatically: bool = True
    enable_diagnostics: bool = True


# =============================================================================
# COMMUNICATION STATE
# =============================================================================

class CommunicationState:
    """Runtime state of the communication system."""
    
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


# =============================================================================
# CANONICAL COMMUNICATION COORDINATOR
# =============================================================================

class CommunicationCoordinator:
    """
    Canonical CommunicationCoordinator for the runtime.
    
    This is THE ONE authority that coordinates all communication infrastructure:
    - EventBus (events)
    - MessageRouter (messages)
    - SignalManager (signals)
    
    Invariants maintained:
        1. Exactly one Coordinator per runtime (enforced by caller)
        2. Coordinates but does not own the underlying authorities
        3. Diagnostics are aggregated, not computed
        4. Lifecycle transitions are coordinated, not performed
    """
    
    def __init__(self, config: Optional[CoordinatorConfig] = None):
        self._config = config or CoordinatorConfig()
        
        self._lock = threading.RLock()
        
        # State tracking
        self._state = CommunicationState.CREATED
        
        # Underlying authorities (created lazily)
        self._event_bus: Optional[EventBus] = None
        self._message_router: Optional[MessageRouter] = None
        self._signal_manager: Optional[SignalManager] = None
        
        # Statistics
        self._start_time_utc: Optional[float] = None
        self._stop_time_utc: Optional[float] = None
        self._total_messages_routed = 0
        self._total_events_published = 0
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this coordinator serves."""
        return self._config.runtime_id
    
    @property
    def state(self) -> str:
        """Get current communication state."""
        with self._lock:
            return self._state
    
    # -------------------------------------------------------------------------
    # LIFECYCLE MANAGEMENT
    # -------------------------------------------------------------------------
    
    async def start(self) -> None:
        """
        Start all communication authorities.
        
        Transition: CREATED -> STARTING -> RUNNING
        
        Raises:
            RuntimeError: If already started or starting failed
        """
        with self._lock:
            if self._state != CommunicationState.CREATED:
                raise RuntimeError(
                    f"Cannot start: current state is {self._state}"
                )
            
            self._state = CommunicationState.STARTING
            self._start_time_utc = time.time()
        
        try:
            # Initialize underlying authorities
            with self._lock:
                if self._event_bus is None:
                    event_config = self._config.event_bus_config or EventBusConfig(
                        runtime_id=self._config.runtime_id
                    )
                    self._event_bus = EventBus(event_config)
                
                if self._message_router is None:
                    router_config = self._config.message_router_config or MessageRouterConfig(
                        runtime_id=self._config.runtime_id
                    )
                    self._message_router = MessageRouter(router_config)
                
                if self._signal_manager is None:
                    signal_config = self._config.signal_manager_config or SignalManagerConfig(
                        runtime_id=self._config.runtime_id
                    )
                    self._signal_manager = SignalManager(signal_config)
            
            with self._lock:
                self._state = CommunicationState.RUNNING
            
        except Exception as e:
            with self._lock:
                self._state = CommunicationState.FAILED
                self._stop_time_utc = time.time()
            raise
    
    async def stop(self) -> None:
        """
        Stop all communication authorities gracefully.
        
        Transition: RUNNING -> STOPPING -> STOPPED
        
        Raises:
            RuntimeError: If not running when attempting to stop
        """
        with self._lock:
            if self._state != CommunicationState.RUNNING:
                raise RuntimeError(
                    f"Cannot stop: current state is {self._state}"
                )
            
            self._state = CommunicationState.STOPPING
        
        try:
            # All authorities are already initialized, just update state
            pass
            
        finally:
            with self._lock:
                self._state = CommunicationState.STOPPED
                self._stop_time_utc = time.time()
    
    async def restart(self) -> None:
        """Restart all communication authorities."""
        await self.stop()
        await self.start()
    
    # -------------------------------------------------------------------------
    # COMMUNICATION API (delegates to underlying authorities)
    # -------------------------------------------------------------------------
    
    def publish_event(
        self,
        envelope: Any,  # EventEnvelope
    ) -> bool:
        """
        Publish an event through the EventBus.
        
        Args:
            envelope: The event to publish
            
        Returns:
            True if published successfully
        """
        with self._lock:
            if not self._event_bus:
                raise RuntimeError("EventBus not initialized")
            
            result = self._event_bus.publish(envelope)
            self._total_events_published += 1
            return result
    
    def subscribe_to_events(
        self,
        subscriber_id: str,
        event_types: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Subscribe to events via the EventBus.
        
        Args:
            subscriber_id: Who is subscribing
            event_types: Types of events to receive
            
        Returns:
            Subscription ID
        """
        with self._lock:
            if not self._event_bus:
                raise RuntimeError("EventBus not initialized")
            
            return self._event_bus.subscribe(subscriber_id, event_types or [], **kwargs)
    
    def route_message(
        self,
        envelope: Any,  # MessageEnvelope
        policy: Optional[RoutingPolicy] = None,
    ) -> tuple:
        """
        Route a message through the MessageRouter.
        
        Args:
            envelope: The message to route
            policy: Optional routing overrides
            
        Returns:
            Tuple of (result, targets)
        """
        with self._lock:
            if not self._message_router:
                raise RuntimeError("MessageRouter not initialized")
            
            result = self._message_router.route(envelope, policy)
            self._total_messages_routed += 1
            return result
    
    def publish_signal(
        self,
        envelope: Any,  # SignalEnvelope
    ) -> bool:
        """
        Publish a signal through the SignalManager.
        
        Args:
            envelope: The signal to publish
            
        Returns:
            True if published successfully
        """
        with self._lock:
            if not self._signal_manager:
                raise RuntimeError("SignalManager not initialized")
            
            return self._signal_manager.publish(envelope)
    
    # -------------------------------------------------------------------------
    # DIAGNOSTICS API
    # -------------------------------------------------------------------------
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics from all authorities."""
        with self._lock:
            result = {
                "runtime_id": self._config.runtime_id,
                "state": self._state,
                "start_time_utc": self._start_time_utc,
                "stop_time_utc": self._stop_time_utc,
                "uptime_seconds": (
                    (time.time() - self._start_time_utc) 
                    if self._start_time_utc else None
                ),
                "total_messages_routed": self._total_messages_routed,
                "total_events_published": self._total_events_published,
            }
            
            # Add authority-specific stats
            if self._event_bus:
                result["event_bus"] = self._event_bus.get_statistics()
            
            if self._message_router:
                result["message_router"] = self._message_router.get_statistics()
            
            if self._signal_manager:
                result["signal_manager"] = self._signal_manager.get_statistics()
            
            return result
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall communication health status.
        
        Returns a combined view of all authority health statuses.
        """
        with self._lock:
            authorities = {}
            all_healthy = True
            
            if self._event_bus:
                bus_health = self._event_bus.get_health_status()
                authorities["event_bus"] = bus_health
                if bus_health.get("status") != "healthy":
                    all_healthy = False
            
            if self._message_router:
                router_health = self._message_router.get_health_status()
                authorities["message_router"] = router_health
                if router_health.get("status") != "healthy":
                    all_healthy = False
            
            if self._signal_manager:
                signal_health = self._signal_manager.get_health_status()
                authorities["signal_manager"] = signal_health
                if signal_health.get("status") != "healthy":
                    all_healthy = False
            
            return {
                "overall_status": "healthy" if all_healthy else "degraded",
                "state": self._state,
                "authorities": authorities,
            }
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get detailed diagnostic information.
        
        Includes:
        - Statistics from all authorities
        - Current state
        - Performance metrics
        """
        return {
            **self.get_statistics(),
            "health": self.get_health_status(),
            "timestamp_utc": time.time(),
        }


__all__ = [
    # Config types
    "CoordinatorConfig",
    
    # State
    "CommunicationState",
    
    # Core authority
    "CommunicationCoordinator",
]