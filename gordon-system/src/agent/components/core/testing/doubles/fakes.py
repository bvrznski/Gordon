# Fakes - Testing Infrastructure
# ==========================================
"""
Fake implementations for working but simplified code paths.

Fakes are fully functional implementations that:
- Work correctly for test scenarios
- Simulate real behavior but with simplified internals
- Are deterministic and fast
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import time


@dataclass(frozen=True)
class FakeConfig:
    """Configuration for a fake instance."""
    
    name: str
    default_response: Optional[Any] = None
    auto_save: bool = True  # Automatically persist changes
    
    @classmethod
    def persistent(cls, name: str) -> "FakeConfig":
        """Create a fake with automatic persistence."""
        return cls(name=name, auto_save=True)
    
    @classmethod
    def transient(cls, name: str) -> "FakeConfig" :
        """Create a fake that doesn't persist."""
        return cls(name=name, auto_save=False)


class Fake:
    """
    Base class for fake implementations.
    
    Fakes are working implementations simplified for testing:
    - InMemoryRepository: Fake database
    - FakeClock: Deterministic time
    - FakeScheduler: Predictable scheduling
    - FakeNetwork: Simulated network behavior
    """
    
    def __init__(self, config: Optional[FakeConfig] = None):
        """Initialize the fake."""
        self._config = config or FakeConfig(name=self.__class__.__name__)
        self._created_at = time.time()
    
    @property
    def name(self) -> str:
        """Get the fake's name."""
        return self._config.name
    
    @property
    def is_persistent(self) -> bool:
        """Check if this fake persists changes."""
        return self._config.auto_save
    
    @property
    def age_seconds(self) -> float:
        """Get how long this fake has been active."""
        return time.time() - self._created_at


class InMemoryRepository(Fake):
    """
    A fake in-memory repository for testing.
    
    Provides:
    - CRUD operations without database
    - Deterministic behavior
    - Query filtering
    - No external dependencies
    
    Usage:
        repo = InMemoryRepository()
        
        # Add entities
        user = User(id=1, name="Alice")
        repo.add(user)
        
        # Get by ID
        found = repo.get(User, 1)
        assert found == user
        
        # Query with filter
        all_users = repo.list(User)
    """
    
    def __init__(self, config: Optional[FakeConfig] = None):
        """Initialize the in-memory repository."""
        super().__init__(config or FakeConfig.persistent("memory_repo"))
        self._entities: Dict[str, List[Any]] = {}
        self._next_ids: Dict[str, int] = {}
    
    def _get_key(self, entity_type: type) -> str:
        """Get the storage key for an entity type."""
        return entity_type.__name__.lower()
    
    def add(self, entity: Any) -> None:
        """Add an entity to the repository."""
        key = self._get_key(type(entity))
        
        if key not in self._entities:
            self._entities[key] = []
            self._next_ids[key] = 1
        
        # Set ID if not present
        if not hasattr(entity, "id") or getattr(entity, "id", None) is None:
            entity.id = self._next_ids[key]
            self._next_ids[key] += 1
        
        self._entities[key].append(entity)
    
    def get(self, entity_type: type, entity_id: Any) -> Optional[Any]:
        """Get an entity by ID."""
        key = self._get_key(entity_type)
        
        for entity in self._entities.get(key, []):
            if getattr(entity, "id", None) == entity_id:
                return entity
        
        return None
    
    def list(self, entity_type: type) -> List[Any]:
        """List all entities of a type."""
        key = self._get_key(entity_type)
        return list(self._entities.get(key, []))
    
    def remove(self, entity: Any) -> bool:
        """Remove an entity from the repository."""
        key = self._get_key(type(entity))
        
        if key not in self._entities:
            return False
        
        try:
            self._entities[key].remove(entity)
            return True
        except ValueError:
            return False
    
    def clear(self, entity_type: Optional[type] = None) -> None:
        """Clear entities, optionally for a specific type."""
        if entity_type is None:
            self._entities.clear()
            self._next_ids.clear()
        else:
            key = self._get_key(entity_type)
            self._entities.pop(key, [])
            self._next_ids.pop(key, 0)


class FakeClock(Fake):
    """
    A deterministic fake clock for testing time-dependent code.
    
    Usage:
        clock = FakeClock(initial_time=1000.0)
        
        # Get current time (returns controlled value)
        now = clock.now()
        
        # Advance time
        clock.advance(10.0)  # +10 seconds
        
        # Time passes but clock only changes when we tell it to
    """
    
    def __init__(self, initial_time: Optional[float] = None):
        """Initialize the fake clock."""
        super().__init__(FakeConfig(name="fake_clock"))
        self._current_time = initial_time or time.time()
        self._original_time_fn = time.time
    
    @property
    def current_time(self) -> float:
        """Get the current fake time."""
        return self._current_time
    
    def now(self) -> float:
        """Return the current fake time (replacement for time.time)."""
        return self._current_time
    
    def advance(self, seconds: float) -> None:
        """Advance the clock by the given number of seconds."""
        self._current_time += seconds
    
    def set(self, timestamp: float) -> None:
        """Set the clock to a specific timestamp."""
        self._current_time = timestamp
    
    def elapsed_since(self, start_time: float) -> float:
        """Calculate elapsed time since a starting point."""
        return self._current_time - start_time


class FakeScheduler(Fake):
    """
    A deterministic fake scheduler for testing scheduled tasks.
    
    Usage:
        scheduler = FakeScheduler()
        
        # Schedule tasks
        task_id = scheduler.schedule(
            delay=5.0,
            callback=lambda: print("Hello")
        )
        
        # Run pending tasks
        scheduler.run_pending()  # Runs only when time is right
        
        # Advance clock to trigger scheduled tasks
    """
    
    def __init__(self, config: Optional[FakeConfig] = None):
        """Initialize the fake scheduler."""
        super().__init__(config or FakeConfig(name="fake_scheduler"))
        self._tasks: Dict[str, ScheduledTask] = {}
        self._task_counter = 0
    
    @dataclass
    class ScheduledTask:
        """A scheduled task."""
        
        task_id: str
        run_at: float
        callback: Any
        recurring: bool = False
        interval_seconds: Optional[float] = None
    
    def schedule(
        self,
        delay: float,
        callback: Any,
        recurring: bool = False,
        interval_seconds: Optional[float] = None,
    ) -> str:
        """Schedule a task to run after delay seconds."""
        self._task_counter += 1
        task_id = f"task_{self._task_counter}"
        
        task = self.ScheduledTask(
            task_id=task_id,
            run_at=time.time() + delay,
            callback=callback,
            recurring=recurring,
            interval_seconds=interval_seconds,
        )
        
        self._tasks[task_id] = task
        return task_id
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
    
    def run_pending(self, current_time: Optional[float] = None) -> List[str]:
        """Run all pending tasks and return their IDs."""
        executed = []
        now = current_time or time.time()
        
        for task_id, task in list(self._tasks.items()):
            if task.run_at <= now:
                try:
                    task.callback()
                    executed.append(task_id)
                except Exception:
                    pass
                
                # Reschedule recurring tasks
                if task.recurring and task.interval_seconds is not None:
                    task.run_at = now + task.interval_seconds
                else:
                    del self._tasks[task_id]
        
        return executed
    
    def pending_count(self) -> int:
        """Get the number of pending tasks."""
        return len(self._tasks)
    
    def next_run_time(self) -> Optional[float]:
        """Get the time of the next scheduled task."""
        if not self._tasks:
            return None
        
        return min(task.run_at for task in self._tasks.values())


class FakeNetwork(Fake):
    """
    A fake network layer for testing without real network calls.
    
    Usage:
        network = FakeNetwork()
        
        # Configure responses
        network.stub_get("/api/users", [1, 2, 3])
        network.stub_post("/api/users", {"id": 4}, status=201)
        
        # Make requests (returns stubbed data)
        result = network.get("/api/users")
    """
    
    def __init__(self, config: Optional[FakeConfig] = None):
        """Initialize the fake network."""
        super().__init__(config or FakeConfig(name="fake_network"))
        self._get_stubs: Dict[str, Any] = {}
        self._post_stubs: Dict[str, Any] = {}
        self._call_log: List[Dict[str, Any]] = []
    
    def stub_get(self, path: str, response: Any, status: int = 200) -> None:
        """Stub a GET request."""
        self._get_stubs[path] = {"response": response, "status": status}
    
    def stub_post(
        self,
        path: str,
        response: Any,
        status: int = 201,
        expected_body: Optional[Any] = None,
    ) -> None:
        """Stub a POST request."""
        self._post_stubs[path] = {
            "response": response,
            "status": status,
            "expected_body": expected_body,
        }
    
    def get(self, path: str) -> Dict[str, Any]:
        """Fake GET request."""
        self._call_log.append({"method": "GET", "path": path})
        
        if path in self._get_stubs:
            stub = self._get_stubs[path]
            return {"body": stub["response"], "status": stub["status"]}
        
        return {"body": None, "status": 404}
    
    def post(self, path: str, body: Any = None) -> Dict[str, Any]:
        """Fake POST request."""
        self._call_log.append({"method": "POST", "path": path, "body": body})
        
        if path in self._post_stubs:
            stub = self._post_stubs[path]
            
            # Check expected body if provided
            if stub["expected_body"] is not None and body != stub["expected_body"]:
                return {"body": None, "status": 400}
            
            return {"body": stub["response"], "status": stub["status"]}
        
        return {"body": None, "status": 404}
    
    def call_count(self) -> int:
        """Get total number of network calls."""
        return len(self._call_log)
    
    def clear(self) -> None:
        """Clear all stubs and logs."""
        self._get_stubs.clear()
        self._post_stubs.clear()
        self._call_log.clear()