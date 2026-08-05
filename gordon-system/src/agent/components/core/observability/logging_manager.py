# Core Logging Manager
# ====================

"""
Structured logging infrastructure for Gordon runtime.

This module provides:
- LoggingManager: Canonical authority for structured logging
- LogRecord formatting and routing to sinks
- Bounded history with retention policies
- Sampling and filtering capabilities

Logging is OBSERVATIONAL - it never changes runtime behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum, auto
import threading
import time
import uuid

from .models import (
    LogRecord,
    LogContext,
    LogMetadata,
    LogLevel,
    create_log,
)


# =============================================================================
# SAMPLING POLICIES
# =============================================================================

class SamplingPolicy(Enum):
    """Sampling strategy for logs."""
    
    ALWAYS = "always"           # Log everything
    NEVER = "never"             # Log nothing (except CRITICAL)
    PROBABILISTIC = "probabilistic"  # Random sampling with rate
    ADAPTIVE = "adaptive"       # Adjust based on load/error rates
    ERROR_PRIORITY = "error_priority"  # All errors + sampled others
    PERFORMANCE_PRIORITY = "performance_priority"  # Low overhead, only high-value logs


@dataclass
class SamplingConfig:
    """Configuration for sampling behavior."""
    
    policy: SamplingPolicy = SamplingPolicy.ALWAYS
    
    # For probabilistic sampling (0.0 - 1.0)
    sample_rate: float = 1.0  # 1.0 = 100%, 0.1 = 10%
    
    # For adaptive sampling
    min_sample_rate: float = 0.001  # Don't go below this rate
    max_sample_rate: float = 1.0    # Never sample above this
    
    # Rate limiting (logs per second)
    max_logs_per_second: int = 1000
    burst_size: int = 100


# =============================================================================
# LOG SINK INTERFACE
# =============================================================================

class LogSink(ABC):
    """
    Interface for log sinks.
    
    Sinks receive formatted logs and deliver them to their destination.
    They must be:
        - Thread-safe where applicable
        - Non-blocking where possible
        - Graceful in failure scenarios
    
    Usage:
        class MySink(LogSink):
            def emit(self, record: LogRecord) -> bool:
                # Emit the log
                return True
            
            async def close(self) -> None:
                # Cleanup resources
                pass
    """
    
    @abstractmethod
    def emit(self, record: LogRecord) -> bool:
        """
        Emit a log record to this sink.
        
        Args:
            record: The log record to emit
            
        Returns:
            True if emitted successfully, False otherwise
        """
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close the sink and release resources."""
        ...
    
    @property
    @abstractmethod
    def is_closed(self) -> bool:
        """Check if sink is closed."""
        ...


# =============================================================================
# FORMATTERS
# =============================================================================

class LogFormatter(ABC):
    """Interface for log formatters."""
    
    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """
        Format a log record for output.
        
        Args:
            record: The log record to format
            
        Returns:
            Formatted string representation
        """
        ...
    
    @property
    @abstractmethod
    def format_type(self) -> str:
        """Return formatter type name."""
        ...


@dataclass
class PlainTextFormatter(LogFormatter):
    """Simple plain text log formatter."""
    
    include_timestamp: bool = True
    include_level: bool = True
    include_source: bool = True
    include_context: bool = False
    
    @property
    def format_type(self) -> str:
        return "plain_text"
    
    def format(self, record: LogRecord) -> str:
        """Format as human-readable plain text."""
        parts = []
        
        if self.include_timestamp:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", 
                             time.localtime(record.metadata.timestamp_utc))
            parts.append(f"[{ts}]")
        
        if self.include_level:
            parts.append(f"[{record.level.name}]")
        
        if self.include_source and record.metadata.source_module:
            source = record.metadata.source_module
            if record.metadata.source_function:
                source += f".{record.metadata.source_function}"
            parts.append(f"({source})")
        
        # Add correlation info if available
        ctx_parts = []
        if self.include_context and record.context.correlation_id:
            ctx_parts.append(f"correlation={record.context.correlation_id}")
        if self.include_context and record.context.trace_id:
            ctx_parts.append(f"trace={record.context.trace_id[:8]}")
        
        message = record.message
        
        # Add payload info
        if record.payload:
            payload_str = ", ".join(f"{k}={v}" for k, v in record.payload.items())
            if record.context.correlation_id is None:  # Only add separator if no correlation info
                message += f" | {payload_str}"
            else:
                message += f", {payload_str}"
        
        result = " ".join(parts) + " - " + message
        
        if ctx_parts:
            result += " [" + ", ".join(ctx_parts) + "]"
        
        return result


@dataclass
class JsonFormatter(LogFormatter):
    """JSON log formatter for machine consumption."""
    
    include_timestamp: bool = True
    include_level: bool = True
    
    @property
    def format_type(self) -> str:
        return "json"
    
    def format(self, record: LogRecord) -> str:
        """Format as JSON string."""
        import json
        
        data = {
            "timestamp_utc": record.metadata.timestamp_utc,
            "monotonic_time": record.metadata.monotonic_time,
            "event_id": record.event_id,
            "level": record.level.name if hasattr(record.level, 'name') else str(record.level),
            "message": record.message,
            "context": {
                "runtime_id": record.context.runtime_id,
                "correlation_id": record.context.correlation_id,
                "trace_id": record.context.trace_id,
                "span_id": record.context.span_id,
                "entity_id": record.context.entity_id,
                "task_id": record.context.task_id,
            },
            "metadata": {
                "source_module": record.metadata.source_module,
            }
        }
        
        if record.payload:
            data["payload"] = record.payload
        
        return json.dumps(data, default=str)


# =============================================================================
# LOGGING MANAGER
# =============================================================================

class LoggingManager:
    """
    Canonical authority for structured logging.
    
    Provides:
        - Structured log records with full context
        - Multiple sink support (fan-out)
        - Sampling and filtering
        - Bounded history with retention
    
    INVAR: Logging is observational - it never changes runtime behavior.
    INVAR: Exactly one LoggingManager exists per runtime.
    
    Usage:
        # Create manager
        manager = LoggingManager(
            sampling_config=SamplingConfig(policy=SamplingPolicy.ALWAYS)
        )
        
        # Add sinks
        manager.add_sink(ConsoleSink())
        manager.add_sink(FileSink("logs/app.log"))
        
        # Log messages
        manager.info("Task started", task_id="abc")
        manager.error("Task failed", exception=e, task_id="abc")
        
        # Or use directly with LogRecord
        record = create_log(LogLevel.INFO, "Message")
        manager.emit(record)
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
        sampling_config: Optional[SamplingConfig] = None,
        max_history: int = 10000,
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        self._sampling_config = sampling_config or SamplingConfig()
        
        # Internal state
        self._lock = threading.RLock()
        
        # Sinks - can be multiple (fan-out)
        self._sinks: List[LogSink] = []
        
        # History with bounded size
        self._history: List[LogRecord] = []
        self._max_history = max(max_history, 100)  # Minimum buffer size
        
        # Statistics
        self._total_emitted = 0
        self._total_dropped = 0
        
        # Active spans for correlation
        self._active_spans: Dict[str, LogRecord] = {}
        
        # Formatters by type
        self._formatters: Dict[str, LogFormatter] = {}
        
        # Register default formatters
        self.register_formatter(PlainTextFormatter())
        self.register_formatter(JsonFormatter())
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    @property
    def history_size(self) -> int:
        """Return current history buffer size."""
        with self._lock:
            return len(self._history)
    
    @property
    def total_emitted(self) -> int:
        """Return total logs emitted (including dropped)."""
        with self._lock:
            return self._total_emitted
    
    @property
    def total_dropped(self) -> int:
        """Return total logs dropped due to sampling or buffer full."""
        with self._lock:
            return self._total_dropped
    
    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    
    def register_formatter(self, formatter: LogFormatter) -> "LoggingManager":
        """
        Register a formatter for log output.
        
        Args:
            formatter: The formatter to register
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            self._formatters[formatter.format_type] = formatter
        return self
    
    def get_formatter(self, format_type: str) -> Optional[LogFormatter]:
        """Get a registered formatter by type."""
        with self._lock:
            return self._formatters.get(format_type)
    
    def set_sampling_policy(self, policy: SamplingPolicy) -> "LoggingManager":
        """
        Set the sampling policy.
        
        Args:
            policy: New sampling policy
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            self._sampling_config.policy = policy
        return self
    
    def set_sample_rate(self, rate: float) -> "LoggingManager":
        """
        Set the sample rate for probabilistic sampling.
        
        Args:
            rate: Sample rate (0.0 - 1.0)
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            if not 0.0 <= rate <= 1.0:
                raise ValueError("Sample rate must be between 0.0 and 1.0")
            self._sampling_config.sample_rate = rate
        return self
    
    # ------------------------------------------------------------------
    # Sinks
    # ------------------------------------------------------------------
    
    def add_sink(self, sink: LogSink) -> "LoggingManager":
        """
        Add a log sink to receive emitted logs.
        
        Args:
            sink: The sink to add
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            self._sinks.append(sink)
        return self
    
    def remove_sink(self, sink: LogSink) -> "LoggingManager":
        """
        Remove a log sink.
        
        Args:
            sink: The sink to remove
            
        Returns:
            Self for method chaining
        """
        with self._lock:
            if sink in self._sinks:
                self._sinks.remove(sink)
        return self
    
    def clear_sinks(self) -> "LoggingManager":
        """Remove all sinks."""
        with self._lock:
            self._sinks.clear()
        return self
    
    # ------------------------------------------------------------------
    # Core Logging Methods
    # ------------------------------------------------------------------
    
    def _should_sample(self, level: LogLevel) -> bool:
        """
        Check if a log at this level should be sampled.
        
        Args:
            level: Log severity level
            
        Returns:
            True if the log should be emitted
        """
        policy = self._sampling_config.policy
        
        # Critical logs are always sampled
        if level in (LogLevel.CRITICAL,):
            return True
        
        # Never samples everything
        if policy == SamplingPolicy.NEVER:
            return False
        
        # Always samples everything
        if policy == SamplingPolicy.ALWAYS:
            return True
        
        # Error priority: all errors + sampled others
        if policy == SamplingPolicy.ERROR_PRIORITY:
            if level.is_error:
                return True
            import random
            return random.random() < self._sampling_config.sample_rate
        
        # Performance priority: low overhead
        class SamplingPerformancePriority(Enum):
            LOW_OVERHEAD = "low_overhead"
        
        if policy == SamplingPolicy.PERFORMANCE_PRIORITY:
            # Only log INFO and above, with reduced rate
            if level.priority >= LogLevel.INFO.priority:
                import random
                return random.random() < (self._sampling_config.sample_rate * 0.5)
            return False
        
        # Default: probabilistic
        import random
        return random.random() < self._sampling_config.sample_rate
    
    def emit(self, record: LogRecord) -> bool:
        """
        Emit a log record.
        
        This is the primary entry point for logging. The record will be:
            1. Checked against sampling policy
            2. Added to history buffer
            3. Emitted to all registered sinks
        
        Args:
            record: Log record to emit
            
        Returns:
            True if log was emitted, False if dropped due to sampling
        """
        with self._lock:
            # Check sampling
            if not self._should_sample(record.level):
                self._total_emitted += 1
                self._total_dropped += 1
                return False
            
            # Update history (bounded)
            self._history.append(record)
            
            # Enforce max size - remove oldest entries
            while len(self._history) > self._max_history:
                old = self._history.pop(0)
                del old  # Allow GC to collect
            
            self._total_emitted += 1
        
        # Emit to sinks (outside lock for non-blocking behavior)
        success = True
        for sink in list(self._sinks):
            try:
                if not sink.emit(record):
                    success = False
            except Exception:
                # Don't let a failed sink prevent other emissions
                continue
        
        return success
    
    def emit_sync(self, record: LogRecord) -> bool:
        """
        Emit a log record synchronously.
        
        This blocks until all sinks have processed the log. Use this
        when you need guaranteed delivery (e.g., before shutdown).
        
        Args:
            record: Log record to emit
            
        Returns:
            True if all sinks accepted the log
        """
        with self._lock:
            # Check sampling
            if not self._should_sample(record.level):
                self._total_emitted += 1
                self._total_dropped += 1
                return False
            
            # Update history
            self._history.append(record)
            
            while len(self._history) > self._max_history:
                self._history.pop(0)
            
            self._total_emitted += 1
        
        # Sync emit to all sinks
        success = True
        for sink in list(self._sinks):
            try:
                if not sink.emit(record):
                    success = False
            except Exception:
                success = False
        
        return success
    
    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------
    
    def trace(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log a TRACE-level message."""
        record = create_log(LogLevel.TRACE, message, runtime_id=self._runtime_id, **payload)
        return self.emit(record)
    
    def debug(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log a DEBUG-level message."""
        record = create_log(LogLevel.DEBUG, message, runtime_id=self._runtime_id, **payload)
        return self.emit(record)
    
    def info(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log an INFO-level message."""
        record = create_log(LogLevel.INFO, message, runtime_id=self._runtime_id, **payload)
        return self.emit(record)
    
    def notice(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log a NOTICE-level message."""
        record = create_log(LogLevel.NOTICE, message, runtime_id=self._runtime_id, **payload)
        return self.emit(record)
    
    def warning(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log a WARNING-level message."""
        record = create_log(LogLevel.WARNING, message, runtime_id=self._runtime_id, **payload)
        return self.emit(record)
    
    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        **payload
    ) -> bool:
        """Log an ERROR-level message."""
        if exception is not None:
            payload["exception_type"] = type(exception).__name__
            payload["exception_message"] = str(exception)
        
        record = create_log(LogLevel.ERROR, message, runtime_id=self._runtime_id, **payload)
        return self.emit(record)
    
    def critical(
        self,
        message: str,
        **payload
    ) -> bool:
        """Log a CRITICAL-level message."""
        record = create_log(LogLevel.CRITICAL, message, runtime_id=self._runtime_id, **payload)
        return self.emit(record)
    
    # ------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------
    
    def get_recent_logs(self, limit: int = 100) -> List[LogRecord]:
        """
        Get recent log records.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of most recent logs (newest last)
        """
        with self._lock:
            return list(self._history[-limit:])
    
    def get_logs_by_level(self, level: LogLevel) -> List[LogRecord]:
        """Get all logs at a specific severity level."""
        with self._lock:
            return [r for r in self._history if r.level == level]
    
    def get_logs_by_source(self, source_module: str) -> List[LogRecord]:
        """Get all logs from a specific source module."""
        with self._lock:
            return [
                r for r in self._history
                if r.metadata.source_module == source_module
            ]
    
    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    
    async def close(self) -> None:
        """Close the manager and all sinks."""
        import asyncio
        
        # Flush history to sinks one final time
        with self._lock:
            records = list(self._history)
        
        for record in records:
            for sink in list(self._sinks):
                try:
                    await sink.emit(record)
                except Exception:
                    pass
        
        # Close all sinks
        tasks = [sink.close() for sink in list(self._sinks)]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# =============================================================================
# CONSOLE SINK (Built-in)
# =============================================================================

class ConsoleSink(LogSink):
    """Log sink that outputs to console/terminal."""
    
    def __init__(
        self,
        formatter: Optional[LogFormatter] = None,
        level_threshold: LogLevel = LogLevel.TRACE
    ) -> None:
        self._formatter = formatter or PlainTextFormatter()
        self._level_threshold = level_threshold
        self._is_closed = False
    
    def emit(self, record: LogRecord) -> bool:
        """Emit log to console."""
        if self._is_closed:
            return False
        
        # Check threshold
        if record.level.priority < self._level_threshold.priority:
            return True  # Drop silently
        
        try:
            formatted = self._formatter.format(record)
            print(formatted, flush=True)
            return True
        except Exception:
            # Don't fail on console output errors
            return False
    
    async def close(self) -> None:
        """Close the sink."""
        self._is_closed = True
    
    @property
    def is_closed(self) -> bool:
        return self._is_closed


# =============================================================================
# MEMORY SINK (Built-in)
# =============================================================================

class MemorySink(LogSink):
    """
    Log sink that stores logs in memory.
    
    Useful for testing or temporary storage before exporting.
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        formatter: Optional[LogFormatter] = None
    ) -> None:
        import threading
        
        self._max_size = max(max_size, 100)
        self._formatter = formatter or PlainTextFormatter()
        self._lock = threading.RLock()
        
        self._logs: List[LogRecord] = []
        self._is_closed = False
    
    def emit(self, record: LogRecord) -> bool:
        """Store log in memory buffer."""
        if self._is_closed:
            return False
        
        with self._lock:
            self._logs.append(record)
            
            # Enforce size limit
            while len(self._logs) > self._max_size:
                self._logs.pop(0)
        
        return True
    
    async def close(self) -> None:
        """Close the sink."""
        self._is_closed = True
    
    @property
    def is_closed(self) -> bool:
        return self._is_closed
    
    @property
    def log_count(self) -> int:
        """Return number of logs stored."""
        with self._lock:
            return len(self._logs)
    
    def get_logs(self, limit: int = 1000) -> List[LogRecord]:
        """
        Get stored logs.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of stored log records
        """
        with self._lock:
            return list(self._logs[-limit:])
    
    def get_formatted_logs(self, limit: int = 1000) -> List[str]:
        """Get formatted logs as strings."""
        with self._lock:
            return [self._formatter.format(r) for r in self._logs[-limit:]]


# =============================================================================
# FAKE SINK FOR TESTING
# =============================================================================

class FakeSink(LogSink):
    """
    Test sink that collects logs without output.
    
    Useful for testing logging behavior without console output.
    """
    
    def __init__(self) -> None:
        import threading
        
        self._lock = threading.RLock()
        self._emitted: List[LogRecord] = []
        self._is_closed = False
    
    def emit(self, record: LogRecord) -> bool:
        """Store log without output."""
        if self._is_closed:
            return False
        
        with self._lock:
            self._emitted.append(record)
        
        return True
    
    async def close(self) -> None:
        """Close the sink."""
        self._is_closed = True
    
    @property
    def is_closed(self) -> bool:
        return self._is_closed
    
    def get_emitted(self) -> List[LogRecord]:
        """Get all emitted logs."""
        with self._lock:
            return list(self._emitted)
    
    def clear(self) -> None:
        """Clear all collected logs."""
        with self._lock:
            self._emitted.clear()


__all__ = [
    "SamplingPolicy",
    "SamplingConfig",
    "LogSink",
    "LogFormatter",
    "PlainTextFormatter",
    "JsonFormatter",
    "LoggingManager",
    "ConsoleSink",
    "MemorySink",
    "FakeSink",
]