# Core Temporal Package - Phase 3.16
# ===================================

"""
Core Temporal Infrastructure for Gordon Core.

This package provides the essential temporal infrastructure components:
    * Timers - Time-based execution triggers
    * Deadlines - Absolute time constraints for operations
    * Timeouts - Duration limits for operations
    * Backoff - Exponential backoff algorithms for retries
"""

from .timer import Timer, TimerHandle, TimerState

__all__ = [
    "Timer",
    "TimerHandle",
    "TimerState",
]