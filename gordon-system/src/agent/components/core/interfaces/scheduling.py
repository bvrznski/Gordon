# Core Scheduling Interface
# ==========================

"""
Core scheduling interface - defines contracts for task scheduling.

This interface allows different scheduling strategies (fixed rate, cron,
relative timing) while providing a consistent way to schedule and manage tasks.

ARCHITECTURAL PRINCIPLES:
- Scheduling is decoupled from execution
- Multiple scheduler implementations possible
- Tasks are scheduled by ID, not by implementation
"""

from typing import Protocol, Optional, List, Callable, Any, Dict
from dataclasses import dataclass, field
from enum import Enum
import time


class ScheduleType(Enum):
    """Types of scheduling patterns."""
    ONCE = "once"          # Execute once at a specific time
    FIXED_RATE = "fixed-rate"  # Execute periodically with fixed interval
    CRON = "cron"              # Cron-style schedule (specific times)
    DELAYED = "delayed"        # Execute once after a delay


@dataclass(frozen=True)
class Schedule:
    """
    A schedule defines when and how often a task should run.
    
    Args:
        schedule_id: Unique identifier for this schedule
        schedule_type: The type of scheduling pattern
        cron_expression: Cron-style expression (for CRON type)
        interval_seconds: Interval in seconds (for FIXED_RATE)
        start_time_utc: When to first execute (Unix timestamp)
        end_time_utc: When to stop scheduling (optional, Unix timestamp)
        max_runs: Maximum number of executions (None = unlimited)
    """
    schedule_id: str
    schedule_type: ScheduleType
    
    # Timing parameters
    cron_expression: Optional[str] = None  # e.g., "0 * * * *" for hourly
    interval_seconds: Optional[float] = None
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: Optional[float] = None
    max_runs: Optional[int] = None
    
    def is_valid(self) -> bool:
        """Check if this schedule has valid parameters."""
        if self.schedule_type == ScheduleType.CRON and not self.cron_expression:
            return False
        if self.schedule_type == ScheduleType.FIXED_RATE and not self.interval_seconds:
            return False
        if self.start_time_utc < time.time():
            # Allow past start times for immediate execution
            pass
        return True
    
    def next_execution_after(self, current_time: float) -> Optional[float]:
        """Calculate the next execution time after current_time."""
        # Simplified - in production would parse cron expressions properly
        if self.schedule_type == ScheduleType.FIXED_RATE:
            if self.interval_seconds is None:
                return None
            # Find next multiple of interval after current_time
            elapsed = current_time - self.start_time_utc
            next_offset = ((elapsed // self.interval_seconds) + 1) * self.interval_seconds
            return self.start_time_utc + next_offset
        
        elif self.schedule_type == ScheduleType.ONCE:
            if self.end_time_utc and current_time >= self.end_time_utc:
                return None
            return max(self.start_time_utc, current_time)
        
        else:
            # Default: return start time if within bounds
            if self.end_time_utc and current_time >= self.end_time_utc:
                return None
            return max(self.start_time_utc, current_time)


@dataclass(frozen=True)
class ScheduledTask:
    """
    A task that has been scheduled for execution.
    
    Args:
        task_id: The ID of the task being scheduled
        schedule: The schedule defining when to run
        status: Current scheduling status
        next_execution: Unix timestamp of next execution (if scheduled)
        last_execution: Unix timestamp of last execution (if executed)
        runs_completed: Number of times task has run
    """
    task_id: str
    schedule: Schedule
    status: str = "pending"  # pending, running, completed, failed, cancelled
    next_execution: Optional[float] = None
    last_execution: Optional[float] = None
    runs_completed: int = 0


class IScheduler(Protocol):
    """
    Interface for the scheduler - coordinates task scheduling.
    
    The scheduler is responsible for:
        - Accepting new task schedules
        - Calculating next execution times
        - Maintaining schedule state
        - Notifying when tasks should run
    
    Note: The scheduler does NOT execute tasks - it only manages
    WHEN they should be executed. The executor handles HOW.
    """
    
    @property
    def scheduler_id(self) -> str:
        """Get the unique ID of this scheduler."""
        ...
    
    async def start(self) -> None:
        """Start the scheduler and begin processing schedules."""
        ...
    
    async def stop(self) -> None:
        """Stop the scheduler and cancel pending tasks."""
        ...
    
    async def schedule(
        self,
        task_id: str,
        schedule: Schedule,
    ) -> ScheduledTask:
        """
        Schedule a task for execution.
        
        Args:
            task_id: The ID of the task to schedule
            schedule: The schedule definition
            
        Returns:
            The created scheduled task with status info
        """
        ...
    
    async def unschedule(self, task_id: str) -> bool:
        """
        Cancel a scheduled task.
        
        Args:
            task_id: The ID of the task to cancel
            
        Returns:
            True if task was scheduled and cancelled
        """
        ...
    
    async def reschedule(
        self,
        task_id: str,
        new_schedule: Schedule,
    ) -> ScheduledTask:
        """
        Update an existing schedule.
        
        Args:
            task_id: The ID of the task to reschedule
            new_schedule: The new schedule definition
            
        Returns:
            The updated scheduled task
        """
        ...
    
    async def get_scheduled_tasks(self) -> List[ScheduledTask]:
        """Get all currently scheduled tasks."""
        ...
    
    async def get_next_execution(self, task_id: str) -> Optional[float]:
        """Get the next execution time for a task (if scheduled)."""
        ...


class ISchedulerListener(Protocol):
    """
    Interface for components that want to be notified about scheduling events.
    
    Listeners can:
        - Monitor when tasks are scheduled
        - Track task execution starts/stops
        - React to schedule changes
    """
    
    async def on_task_scheduled(self, scheduled_task: ScheduledTask) -> None:
        """Called when a new task is scheduled."""
        ...
    
    async def on_task_executing(self, scheduled_task: ScheduledTask) -> None:
        """Called when a task is about to execute."""
        ...
    
    async def on_task_completed(
        self,
        scheduled_task: ScheduledTask,
        execution_time_ms: float,
    ) -> None:
        """
        Called after a task completes successfully.
        
        Args:
            scheduled_task: The task that completed
            execution_time_ms: How long it took in milliseconds
        """
        ...
    
    async def on_task_failed(
        self,
        scheduled_task: ScheduledTask,
        error_message: str,
    ) -> None:
        """
        Called when a scheduled task fails.
        
        Args:
            scheduled_task: The task that failed
            error_message: Description of the failure
        """
        ...
    
    async def on_schedule_changed(self, scheduled_task: ScheduledTask) -> None:
        """Called when a schedule is modified."""
        ...


class SchedulingError(Exception):
    """Raised when scheduling operations fail."""
    pass


class DuplicateScheduleError(SchedulingError):
    """Raised when trying to schedule an already-scheduled task."""
    
    def __init__(self, task_id: str):
        super().__init__(f"Task {task_id} is already scheduled")
        self.task_id = task_id


class UnknownScheduleError(SchedulingError):
    """Raised when referencing a non-existent schedule."""
    
    def __init__(self, task_id: str):
        super().__init__(f"No schedule found for task {task_id}")
        self.task_id = task_id


__all__ = [
    "ScheduleType",
    "Schedule",
    "ScheduledTask",
    "IScheduler",
    "ISchedulerListener",
    "SchedulingError",
    "DuplicateScheduleError",
    "UnknownScheduleError",
]