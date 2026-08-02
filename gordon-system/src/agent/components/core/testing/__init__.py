# Core Testing Utilities
# ======================

"""
Core runtime test utilities.

Provides fake implementations for testing purposes. These are NOT part of
production code and should not be imported by production modules.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FakeLifecycleEntity:
    """
    Fake lifecycle entity for testing.
    
    Tracks state transitions and provides deterministic behavior.
    """
    
    name: str = "fake_entity"
    initial_state: str = "created"
    _state: str = field(default="created")
    transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def state(self) -> str:
        return self._state
    
    async def initialize(self) -> None:
        old = self._state
        self._state = "initializing"
        self.transitions.append({
            "from": old,
            "to": self._state,
            "event": "initialize"
        })
    
    async def start(self) -> None:
        old = self._state
        if old == "ready":
            self._state = "running"
        elif old == "initializing":
            self._state = "ready"
            self.transitions.append({
                "from": old,
                "to": self._state,
                "event": "ready"
            })
        
        self.transitions.append({
            "from": old,
            "to": self._state,
            "event": "start"
        })
    
    async def stop(self) -> None:
        old = self._state
        if old == "running":
            self._state = "stopped"
        self.transitions.append({
            "from": old,
            "to": self._state,
            "event": "stop"
        })
    
    async def shutdown(self) -> None:
        old = self._state
        self._state = "stopped"
        self.transitions.append({
            "from": old,
            "to": self._state,
            "event": "shutdown"
        })


@dataclass
class FakeService:
    """
    Fake service for testing.
    
    Tracks startup/shutdown calls.
    """
    
    service_id: str
    name: str = "fake_service"
    started: bool = False
    stopped: bool = False
    
    async def start(self) -> None:
        self.started = True
    
    async def stop(self) -> None:
        self.stopped = True


@dataclass
class FakeRegistry:
    """
    Fake registry for testing.
    
    Tracks registrations and lookups.
    """
    
    entries: Dict[str, Any] = field(default_factory=dict)
    register_calls: int = 0
    get_calls: int = 0
    
    def register(self, key: str, value: Any) -> bool:
        self.register_calls += 1
        self.entries[key] = value
        return True
    
    def get(self, key: str) -> Optional[Any]:
        self.get_calls += 1
        return self.entries.get(key)
    
    def contains(self, key: str) -> bool:
        return key in self.entries


@dataclass
class FakeObservabilitySink:
    """
    Fake observability sink for testing.
    
    Records all events without outputting them.
    """
    
    events: List[Dict[str, Any]] = field(default_factory=list)
    log_count: int = 0
    
    async def record_event(
        self,
        category: str,
        message: str,
        severity: str = "info",
        **attributes
    ) -> None:
        import time
        self.events.append({
            "timestamp": time.monotonic(),
            "category": category,
            "message": message,
            "severity": severity,
            **attributes
        })
        self.log_count += 1


@dataclass
class FakeScheduler:
    """
    Fake scheduler for testing.
    
    Tracks scheduled tasks without executing them.
    """
    
    scheduled_tasks: List[Dict[str, Any]] = field(default_factory=list)
    run_order: List[str] = field(default_factory=list)
    
    async def schedule(self, task_name: str, priority: int = 0) -> None:
        self.scheduled_tasks.append({
            "name": task_name,
            "priority": priority
        })
    
    async def execute_next(self) -> Optional[str]:
        """Execute next task in order and return its name."""
        if not self.scheduled_tasks:
            return None
        
        task = self.scheduled_tasks.pop(0)
        self.run_order.append(task["name"])
        return task["name"]


__all__ = [
    "FakeLifecycleEntity",
    "FakeService",
    "FakeRegistry",
    "FakeObservabilitySink",
    "FakeScheduler",
]
