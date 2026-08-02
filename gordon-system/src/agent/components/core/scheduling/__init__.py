# Core Scheduling Primitives
# ==========================

"""
Core runtime scheduling primitives for recurring/simple tasks.

This module provides simplified scheduling for:
- Recurring task execution (cron-like patterns)
- Simple priority-based scheduling without dependencies
- Basic task lifecycle management

Note: The authoritative scheduler with full dependency tracking is in
the `execution` module. This module provides simpler scheduling primitives.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum


class RecurringTaskState(Enum):
    """Recurring task states."""
    
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"


@dataclass(frozen=True)
class RecurringTaskSpec:
    """
    Specification for a recurring scheduled task.
    
    Usage:
        # Simple recurring task
        spec = RecurringTaskSpec(
            name="backup_task",
            task_fn=perform_backup,
            interval_seconds=3600  # Every hour
        )
        
        # Schedule with executor
        scheduler.schedule_recurring(spec)
    """
    
    name: str  # Task identifier
    task_fn: Callable[[], Any]  # Async or sync function to execute
    interval_seconds: float = 3600.0  # Time between executions
    initial_delay_seconds: float = 0.0  # Delay before first execution
    max_runs: Optional[int] = None  # Stop after this many runs (None = forever)
    priority: int = 100  # Lower = higher priority


@dataclass
class RecurringTaskHandle:
    """Handle for managing a running recurring task."""
    
    spec: RecurringTaskSpec
    state: RecurringTaskState = RecurringTaskState.PENDING
    
    _task: Optional[Any] = None  # asyncio.Task reference
    _run_count: int = 0
    _lock: Any = field(default_factory=lambda: asyncio.Lock())
    
    async def start(self) -> None:
        """Start the recurring task."""
        async with self._lock:
            if self.state == RecurringTaskState.RUNNING:
                return
            self.state = RecurringTaskState.RUNNING
    
    async def stop(self) -> None:
        """Stop the recurring task."""
        async with self._lock:
            self.state = RecurringTaskState.STOPPED


class SimpleScheduler:
    """
    Simple in-process scheduler for recurring tasks.
    
    Provides basic scheduling without dependency tracking.
    For full task execution with dependencies, use execution.Scheduler.
    
    Usage:
        scheduler = SimpleScheduler()
        
        spec = RecurringTaskSpec(
            name="health_check",
            task_fn=check_health,
            interval_seconds=60
        )
        
        handle = scheduler.schedule_recurring(spec)
    """
    
    def __init__(self) -> None:
        self._tasks: Dict[str, RecurringTaskHandle] = {}
        self._lock: Any = asyncio.Lock()
    
    async def schedule_recurring(self, spec: RecurringTaskSpec) -> RecurringTaskHandle:
        """Schedule a recurring task."""
        handle = RecurringTaskHandle(spec=spec)
        async with self._lock:
            self._tasks[spec.name] = handle
        return handle
    
    async def cancel(self, name: str) -> bool:
        """Cancel a scheduled recurring task."""
        async with self._lock:
            if name in self._tasks:
                await self._tasks[name].stop()
                del self._tasks[name]
                return True
            return False
    
    def get_task(self, name: str) -> Optional[RecurringTaskHandle]:
        """Get handle for a scheduled task."""
        return self._tasks.get(name)
    
    async def start_all(self) -> None:
        """Start all scheduled tasks."""
        async with self._lock:
            for handle in self._tasks.values():
                await handle.start()
    
    async def stop_all(self) -> None:
        """Stop all scheduled tasks."""
        async with self._lock:
            for handle in self._tasks.values():
                await handle.stop()


__all__ = [
    "RecurringTaskState",
    "RecurringTaskSpec",
    "RecurringTaskHandle",
    "SimpleScheduler",
]