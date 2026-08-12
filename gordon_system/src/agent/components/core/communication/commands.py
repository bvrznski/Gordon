# Core Command Contracts
# =====================

"""
Command contracts for requests to perform operations.

Commands represent:
- State-changing operations with one authoritative handler
- Single responsibility per command type
- Explicit identity and payload types
- Idempotency support where required

Command semantics:
- Commands request work, they don't describe facts
- Each command has exactly one authoritative handler by default
- Fan-out fan-in requires explicit design
- Retry only for idempotent commands
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Protocol
from enum import Enum
import time


class CommandResultType(Enum):
    """Types of command results."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"  # Some work completed before failure
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class CommandId:
    """Unique identifier for a command."""
    value: str
    
    @classmethod
    def generate(cls) -> "CommandId":
        import uuid
        return cls(value=f"cmd_{uuid.uuid4().hex[:16]}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CommandMetadata:
    """Immutable metadata for commands."""
    command_type: str  # e.g., "task.create", "service.start"
    
    source_id: Optional[str] = None
    runtime_id: Optional[str] = None
    
    timestamp_utc: float = field(default_factory=time.time)
    monotonic_time: float = field(default_factory=time.monotonic)
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    priority: int = 0  # Lower = higher priority
    deadline_utc: Optional[float] = None
    
    idempotency_key: Optional[str] = None
    
    security_context: Dict[str, Any] = field(default_factory=dict)
    
    def with_correlation(self, corr_id: str) -> "CommandMetadata":
        return CommandMetadata(
            command_type=self.command_type,
            source_id=self.source_id,
            runtime_id=self.runtime_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            correlation_id=corr_id,
            causation_id=self.causation_id,
            priority=self.priority,
            deadline_utc=self.deadline_utc,
            idempotency_key=self.idempotency_key,
            security_context=dict(self.security_context),
        )
    
    def with_causation(self, cause_id: str) -> "CommandMetadata":
        return CommandMetadata(
            command_type=self.command_type,
            source_id=self.source_id,
            runtime_id=self.runtime_id,
            timestamp_utc=self.timestamp_utc,
            monotonic_time=self.monotonic_time,
            correlation_id=self.correlation_id,
            causation_id=cause_id,
            priority=self.priority,
            deadline_utc=self.deadline_utc,
            idempotency_key=self.idempotency_key,
            security_context=dict(self.security_context),
        )


@dataclass(frozen=True)
class Command:
    """
    Base class for command contracts.
    
    Commands request work that may change state. They are NOT facts - they
    are requests to do something.
    
    Invariants:
        - One logical responsibility per command type
        - One authoritative handler by default
        - Explicit identity
        - Idempotency where required
    """
    
    command_id: CommandId
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: CommandMetadata = field(default_factory=CommandMetadata)
    
    @property
    def is_idempotent(self) -> bool:
        """Check if this command is idempotent (can be safely retried)."""
        return self.metadata.idempotency_key is not None
    
    @classmethod
    def create(
        cls,
        command_type: str,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        priority: int = 0,
        deadline_utc: Optional[float] = None,
        idempotency_key: Optional[str] = None,
    ) -> "Command":
        """Create a new command with default values."""
        metadata = CommandMetadata(
            command_type=command_type,
            correlation_id=correlation_id,
            causation_id=causation_id,
            priority=priority,
            deadline_utc=deadline_utc,
            idempotency_key=idempotency_key,
        )
        return cls(
            command_id=CommandId.generate(),
            payload=dict(payload or {}),
            metadata=metadata,
        )


class CommandHandler(Protocol):
    """Protocol for command handlers."""
    
    async def __call__(self, command: Command) -> "CommandResult":
        """Handle a command and return result."""
        ...


@dataclass(frozen=True)
class CommandResult:
    """
    Result of a command execution.
    
    Commands may or may not produce results. The result includes:
    - Success/failure status
    - Optional payload with result data
    - Error information if failed
    """
    
    command_id: CommandId
    
    success: bool
    result_type: CommandResultType = CommandResultType.SUCCESS
    
    result_payload: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    # Execution context
    handler_id: Optional[str] = None
    execution_time_ms: float = 0.0
    
    @classmethod
    def success(
        cls,
        command_id: CommandId,
        result_payload: Optional[Dict[str, Any]] = None,
        handler_id: Optional[str] = None,
        execution_time_ms: float = 0.0,
    ) -> "CommandResult":
        return cls(
            command_id=command_id,
            success=True,
            result_type=CommandResultType.SUCCESS,
            result_payload=dict(result_payload or {}),
            handler_id=handler_id,
            execution_time_ms=execution_time_ms,
        )
    
    @classmethod
    def failure(
        cls,
        command_id: CommandId,
        error_message: str,
        error_type: Optional[str] = None,
        partial_success: bool = False,
        handler_id: Optional[str] = None,
    ) -> "CommandResult":
        result_type = (
            CommandResultType.PARTIAL
            if partial_success
            else CommandResultType.FAILURE
        )
        return cls(
            command_id=command_id,
            success=False,
            result_type=result_type,
            error_message=error_message,
            error_type=error_type,
            handler_id=handler_id,
        )
    
    @classmethod
    def cancelled(cls, command_id: CommandId) -> "CommandResult":
        return cls(
            command_id=command_id,
            success=False,
            result_type=CommandResultType.CANCELLED,
            error_message="Command was cancelled",
        )
    
    @classmethod
    def timeout(cls, command_id: CommandId) -> "CommandResult":
        return cls(
            command_id=command_id,
            success=False,
            result_type=CommandResultType.TIMEOUT,
            error_message="Command execution timed out",
        )


class CommandHandlerRegistry:
    """
    Registry for command handlers.
    
    Each command type maps to exactly one handler by default (canonical
    single-handler semantics).
    """
    
    def __init__(self):
        self._lock = None  # Lazy import
        self._handlers: Dict[str, CommandHandler] = {}
        self._command_types: Dict[str, str] = {}  # command_type -> handler_id
    
    def _get_lock(self):
        import threading
        if self._lock is None:
            self._lock = threading.RLock()
        return self._lock
    
    def register(
        self,
        command_type: str,
        handler: CommandHandler,
        handler_id: Optional[str] = None,
    ) -> str:
        """
        Register a handler for a command type.
        
        Args:
            command_type: The command type to handle
            handler: Async callable that processes the command
            handler_id: Optional identifier for this handler
            
        Returns:
            Handler ID
            
        Raises:
            DuplicateHandlerError: If already registered
        """
        lock = self._get_lock()
        with lock:
            if command_type in self._handlers:
                raise DuplicateHandlerError(
                    f"Command type '{command_type}' already has a handler"
                )
            
            h_id = handler_id or f"handler_{len(self._handlers)}"
            self._handlers[h_id] = handler
            self._command_types[command_type] = h_id
            
            return h_id
    
    def unregister(self, command_type: str) -> bool:
        """Remove a command handler."""
        lock = self._get_lock()
        with lock:
            if command_type not in self._command_types:
                return False
            
            handler_id = self._command_types.pop(command_type)
            del self._handlers[handler_id]
            return True
    
    def get_handler(self, command_type: str) -> Optional[CommandHandler]:
        """Get handler for a command type."""
        lock = self._get_lock()
        with lock:
            handler_id = self._command_types.get(command_type)
            if handler_id is None:
                return None
            return self._handlers.get(handler_id)
    
    def has_handler(self, command_type: str) -> bool:
        """Check if a command type has a registered handler."""
        return command_type in self._command_types
    
    def get_all_handlers(self) -> Dict[str, CommandHandler]:
        """Get all registered handlers."""
        lock = self._get_lock()
        with lock:
            return dict(self._handlers)


class DuplicateHandlerError(Exception):
    """Raised when trying to register a duplicate handler."""
    pass


# =============================================================================
# BUILT-IN COMMAND TYPES (canonical examples)
# =============================================================================

@dataclass(frozen=True)
class ShutdownCommand(Command):
    """Request graceful shutdown of runtime or component."""
    
    target_scope: str = "runtime"  # runtime, component, service
    reason: Optional[str] = None


@dataclass(frozen=True)
class RestartCommand(Command):
    """Request restart of runtime or component."""
    
    target_scope: str = "runtime"
    force: bool = False
    delay_seconds: float = 0.0


@dataclass(frozen=True)
class CancelTaskCommand:
    """Request cancellation of a task.
    
    This class does NOT inherit from Command to avoid dataclass field ordering
    issues. Instead, it provides its own complete contract structure.
    """
    
    # Identity (required first)
    command_id: CommandId
    task_id: str  # Task to be cancelled
    
    # Optional fields with defaults
    reason: Optional[str] = "cancelled"
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: CommandMetadata = field(default_factory=CommandMetadata)
    
    @classmethod
    def create(cls, task_id: str) -> "CancelTaskCommand":
        """Create a CancelTaskCommand with default values."""
        return cls(task_id=task_id, reason="cancelled", command_id=CommandId.generate())


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Types
    "CommandResultType",
    
    # Identities
    "CommandId",
    
    # Metadata
    "CommandMetadata",
    
    # Contracts
    "Command",
    "CommandHandler",
    
    # Results
    "CommandResult",
    
    # Registry
    "CommandHandlerRegistry",
    "DuplicateHandlerError",
    
    # Built-in commands
    "ShutdownCommand",
    "RestartCommand",
    "CancelTaskCommand",
]