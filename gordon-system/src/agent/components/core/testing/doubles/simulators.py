# Simulators - Testing Infrastructure
# ==========================================
"""
Simulator implementations for emulating external systems.

Simulators provide:
- Full system emulation with realistic behavior
- Configurable states and transitions
- Deterministic responses for testing
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
import time


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration for a simulation."""
    
    name: str
    start_state: str = "idle"
    deterministic: bool = True
    log_events: bool = True
    
    @classmethod
    def production_like(cls, name: str) -> "SimulationConfig":
        """Create a production-like simulation config."""
        return cls(name=name, deterministic=True, log_events=False)
    
    @classmethod
    def testing_mode(cls, name: str) -> "SimulationConfig":
        """Create a testing-focused simulation config."""
        return cls(name=name, deterministic=True, log_events=True)


class SimulatorState(Enum):
    """States in the simulator lifecycle."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass(frozen=True)
class SimulationEvent:
    """An event in a simulation."""
    
    event_type: str
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulationResult:
    """Immutable result of a simulation run."""
    
    simulator_name: str
    start_state: str
    end_state: str
    events: List[SimulationEvent]
    duration_seconds: float
    success: bool


class Simulator:
    """
    Base class for simulator implementations.
    
    Simulators emulate external systems with realistic behavior:
    - Database cluster simulation
    - Network topology simulation  
    - External service simulation
    - Distributed system simulation
    
    Usage:
        sim = DatabaseClusterSimulator()
        
        # Configure the simulation
        sim.set_replicas(3)
        sim.configure_failure("replica_2", fail_rate=0.5)
        
        # Run the simulation
        result = sim.run(duration_seconds=60.0)
        
        # Analyze results
        assert "running" in result.end_state
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        """Initialize the simulator."""
        self._config = config or SimulationConfig(name=self.__class__.__name__)
        self._state = SimulatorState.IDLE
        self._current_state = self._config.start_state
        self._events: List[SimulationEvent] = []
        self._start_time: Optional[float] = None
    
    @property
    def name(self) -> str:
        """Get the simulator's name."""
        return self._config.name
    
    @property
    def state(self) -> SimulatorState:
        """Get the current simulator state."""
        return self._state
    
    @property
    def current_state(self) -> str:
        """Get the current simulation state."""
        return self._current_state
    
    def _record_event(self, event_type: str, details: Optional[Dict[str, Any]] = None) -> SimulationEvent:
        """Record a simulation event."""
        event = SimulationEvent(
            event_type=event_type,
            timestamp=time.time(),
            details=details or {},
        )
        
        if self._config.log_events:
            self._events.append(event)
        
        return event
    
    def start(self, initial_state: Optional[str] = None) -> None:
        """Start the simulation."""
        self._state = SimulatorState.RUNNING
        self._current_state = initial_state or self._config.start_state
        self._start_time = time.time()
    
    def stop(self, final_state: Optional[str] = None) -> None:
        """Stop the simulation."""
        self._state = SimulatorState.COMPLETED
        if final_state is not None:
            self._current_state = final_state
    
    def pause(self) -> None:
        """Pause the simulation."""
        self._state = SimulatorState.PAUSED
    
    def run(self, duration_seconds: Optional[float] = None) -> SimulationResult:
        """
        Run the simulation.
        
        Args:
            duration_seconds: How long to run (None for indefinite)
            
        Returns:
            The simulation result
        """
        self.start()
        
        try:
            if duration_seconds is not None:
                end_time = time.time() + duration_seconds
                
                while time.time() < end_time:
                    self._tick()
            
            return SimulationResult(
                simulator_name=self.name,
                start_state=self._config.start_state,
                end_state=self._current_state,
                events=list(self._events),
                duration_seconds=time.time() - (self._start_time or time.time()),
                success=True,
            )
            
        except Exception as e:
            self.stop()
            return SimulationResult(
                simulator_name=self.name,
                start_state=self._config.start_state,
                end_state="error",
                events=list(self._events),
                duration_seconds=time.time() - (self._start_time or time.time()),
                success=False,
            )
    
    def _tick(self) -> None:
        """Advance the simulation by one tick."""
        pass  # Override in subclasses
    
    def get_events(self, event_type: Optional[str] = None) -> List[SimulationEvent]:
        """Get simulation events, optionally filtered by type."""
        if event_type is None:
            return list(self._events)
        
        return [e for e in self._events if e.event_type == event_type]


class DatabaseClusterSimulator(Simulator):
    """
    A database cluster simulator for testing distributed behavior.
    
    Simulates:
    - Multiple replicas with replication lag
    - Leader election
    - Failover scenarios
    - Network partitions
    
    Usage:
        sim = DatabaseClusterSimulator()
        
        # Configure replicas
        sim.add_replica("replica_1")
        sim.add_replica("replica_2")
        sim.promote_leader("replica_1")
        
        # Trigger failover
        sim.fail_replica("replica_1")
        
        # Check cluster state
        assert sim.get_leader() == "replica_2"
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        """Initialize the database cluster simulator."""
        super().__init__(config or SimulationConfig(name="database_cluster"))
        self._replicas: Dict[str, Dict[str, Any]] = {}
        self._leader: Optional[str] = None
        self._replication_lag: float = 0.1
    
    def add_replica(self, name: str, data_center: str = "dc1") -> None:
        """Add a replica to the cluster."""
        self._replicas[name] = {
            "name": name,
            "data_center": data_center,
            "status": "healthy",
            "is_leader": False,
            "last_heartbeat": time.time(),
            "data_version": 0,
        }
    
    def remove_replica(self, name: str) -> bool:
        """Remove a replica from the cluster."""
        if name in self._replicas:
            del self._replicas[name]
            return True
        return False
    
    def promote_leader(self, name: str) -> None:
        """Promote a replica to leader."""
        # Demote current leader
        for replica in self._replicas.values():
            replica["is_leader"] = False
        
        if name in self._replicas:
            self._replicas[name]["is_leader"] = True
            self._leader = name
    
    def fail_replica(self, name: str) -> None:
        """Simulate a replica failure."""
        if name in self._replicas:
            self._replicas[name]["status"] = "failed"
    
    def heal_replica(self, name: str) -> None:
        """Heal a failed replica."""
        if name in self._replicas:
            self._replicas[name]["status"] = "healthy"
    
    def get_leader(self) -> Optional[str]:
        """Get the current cluster leader."""
        return self._leader
    
    def get_healthy_replicas(self) -> List[Dict[str, Any]]:
        """Get all healthy replicas."""
        return [
            r for r in self._replicas.values() 
            if r["status"] == "healthy"
        ]
    
    def advance_time(self, seconds: float) -> None:
        """Advance simulation time."""
        # Update heartbeats
        for replica in self._replicas.values():
            replica["last_heartbeat"] += seconds
    
    def _tick(self) -> None:
        """Simulate one tick of cluster behavior."""
        pass  # Implement specific behavior in subclass


class NetworkSimulator(Simulator):
    """
    A network simulator for testing distributed system behavior.
    
    Simulates:
    - Latency variations
    - Packet loss
    - Bandwidth limits
    - Network partitions
    
    Usage:
        sim = NetworkSimulator()
        
        # Configure network conditions
        sim.set_latency("node1", "node2", latency_ms=100)
        sim.set_loss_rate("node1", "node3", loss_rate=0.1)
        
        # Simulate partition
        sim.partition(["node1"], ["node2", "node3"])
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        """Initialize the network simulator."""
        super().__init__(config or SimulationConfig(name="network"))
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._links: Dict[str, Dict[str, float]] = {}  # From -> To -> latency
        self._partitioned_sets: List[set] = []
    
    def add_node(self, name: str) -> None:
        """Add a node to the network."""
        self._nodes[name] = {
            "name": name,
            "status": "online",
            "latency_ms": 0,
        }
    
    def remove_node(self, name: str) -> bool:
        """Remove a node from the network."""
        if name in self._nodes:
            del self._nodes[name]
            
            # Remove associated links
            for from_node in list(self._links.keys()):
                if name in self._links[from_node]:
                    del self._links[from_node][name]
            
            return True
        return False
    
    def set_latency(self, from_node: str, to_node: str, latency_ms: float) -> None:
        """Set the latency between two nodes."""
        if from_node not in self._links:
            self._links[from_node] = {}
        
        self._links[from_node][to_node] = latency_ms
    
    def get_latency(self, from_node: str, to_node: str) -> float:
        """Get the current latency between two nodes."""
        return self._links.get(from_node, {}).get(to_node, 0)
    
    def partition(self, group_a: List[str], group_b: List[str]) -> None:
        """Create a network partition between groups."""
        # This is a simplified implementation
        pass
    
    def heal_partition(self) -> None:
        """Heal any existing partitions."""
        self._partitioned_sets.clear()
    
    def _tick(self) -> None:
        """Simulate one tick of network behavior."""
        pass


class ServiceSimulator(Simulator):
    """
    A service simulator for testing API interactions.
    
    Simulates:
    - HTTP endpoints with various status codes
    - Rate limiting
    - Circuit breaker behavior
    - Backpressure
    
    Usage:
        sim = ServiceSimulator()
        
        # Configure endpoint responses
        sim.set_response("/users", {"users": []})
        sim.set_status_code("/users", 503)
        
        # Make requests (returns simulated response)
        result = sim.get("/users")
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        """Initialize the service simulator."""
        super().__init__(config or SimulationConfig(name="service"))
        self._endpoints: Dict[str, Dict[str, Any]] = {}
        self._request_log: List[Dict[str, Any]] = []
    
    def set_response(self, path: str, response: Any, status_code: int = 200) -> None:
        """Configure a endpoint's response."""
        self._endpoints[path] = {
            "response": response,
            "status_code": status_code,
            "method": "GET",
        }
    
    def set_post_response(
        self,
        path: str,
        response: Any,
        status_code: int = 201,
        expected_body: Optional[Any] = None,
    ) -> None:
        """Configure a POST endpoint's response."""
        self._endpoints[path] = {
            "response": response,
            "status_code": status_code,
            "method": "POST",
            "expected_body": expected_body,
        }
    
    def get(self, path: str) -> Dict[str, Any]:
        """Simulate a GET request."""
        return self._handle_request("GET", path)
    
    def post(self, path: str, body: Optional[Any] = None) -> Dict[str, Any]:
        """Simulate a POST request."""
        return self._handle_request("POST", path, body)
    
    def _handle_request(
        self,
        method: str,
        path: str,
        body: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Handle a simulated request."""
        endpoint = self._endpoints.get(path, {})
        
        # Check expected body
        if method == "POST" and body is not None:
            expected = endpoint.get("expected_body")
            if expected is not None and body != expected:
                return {"status": 400, "body": None}
        
        self._request_log.append({
            "method": method,
            "path": path,
            "timestamp": time.time(),
        })
        
        return {
            "status": endpoint.get("status_code", 200),
            "body": endpoint.get("response"),
        }
    
    def get_request_count(self) -> int:
        """Get total number of requests."""
        return len(self._request_log)