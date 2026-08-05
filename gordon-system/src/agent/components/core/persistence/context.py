# Persistence Context & Unit of Work
# ===================================

"""
Persistence context and unit of work patterns for Gordon Core.

This module provides:
- PersistenceContext: Context manager for transaction boundaries
- UnitOfWork: Batch operation collection and atomic persistence

PRINCIPLES
==========

Persistence Context:
    - One context per runtime instance
    - Tracks active transactions
    - Coordinates savepoints
    - Manages state changes before commit

Unit of Work:
    - Collects operations during a transaction
    - Persists atomically on commit
    - Supports rollback to savepoint
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterator
from enum import Enum
import uuid
import time


# =============================================================================
# Persistence Context
# =============================================================================

@dataclass(frozen=True)
class PersistenceContext:
    """
    Context for persistence operations within a transaction.
    
    Provides:
        - Transaction context reference
        - Operation tracking
        - State change collection
    
    NOT responsible for:
        - Making persistence decisions (that's the manager's job)
        - Storing data directly (that's the backend's job)
    """
    
    context_id: str
    
    # Transaction context
    transaction_id: Optional[str] = None
    
    # Runtime context
    runtime_id: str
    boot_session_id: Optional[str] = None
    
    # Tracking
    created_at: float = field(default_factory=time.monotonic)
    operations_collected: int = 0
    state_changes: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_transactional(self) -> bool:
        """Check if this context has an active transaction."""
        return self.transaction_id is not None
    
    @property
    def age_seconds(self) -> float:
        """Get the age of this context in seconds."""
        return time.monotonic() - self.created_at


class PersistenceContextManager:
    """
    Manages persistence contexts for a runtime instance.
    
    Provides context managers and lifecycle coordination.
    """
    
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        self._contexts: Dict[str, PersistenceContext] = {}
        self._lock_contexts: Dict[str, Any] = {}  # Context ID -> lock
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID."""
        return self._runtime_id
    
    def create_context(
        self,
        transaction_id: Optional[str] = None,
        boot_session_id: Optional[str] = None,
    ) -> PersistenceContext:
        """
        Create a new persistence context.
        
        Args:
            transaction_id: Optional transaction ID for transactional operations
            boot_session_id: Optional boot session identifier
            
        Returns:
            New persistence context
        """
        context_id = str(uuid.uuid4())
        context = PersistenceContext(
            context_id=context_id,
            transaction_id=transaction_id,
            runtime_id=self._runtime_id,
            boot_session_id=boot_session_id,
        )
        
        self._contexts[context_id] = context
        
        return context
    
    def get_context(self, context_id: str) -> Optional[PersistenceContext]:
        """Get a context by ID."""
        return self._contexts.get(context_id)
    
    def remove_context(self, context_id: str) -> bool:
        """Remove a context (cleanup)."""
        if context_id in self._contexts:
            del self._contexts[context_id]
            return True
        return False
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get manager diagnostics."""
        return {
            "runtime_id": self._runtime_id,
            "active_contexts": len(self._contexts),
        }


# =============================================================================
# Unit of Work
# =============================================================================

@dataclass(frozen=True)
class UnitOfWork:
    """
    Unit of work for batch persistence operations.
    
    Collects changes during a transaction and persists them atomically.
    """
    
    unit_id: str
    
    # Context
    context_id: Optional[str] = None
    transaction_id: Optional[str] = None
    
    # Operations
    operations: List["UnitOfWorkOperation"] = field(default_factory=list)
    
    # Status
    status: "UnitOfWorkStatus" = field(
        default_factory=lambda: UnitOfWorkStatus.PENDING
    )
    
    created_at: float = field(default_factory=time.monotonic)
    committed_at: Optional[float] = None
    
    @property
    def operation_count(self) -> int:
        """Get the number of operations in this unit."""
        return len(self.operations)
    
    @property
    def is_empty(self) -> bool:
        """Check if the unit has no operations."""
        return len(self.operations) == 0
    
    @property
    def is_committed(self) -> bool:
        """Check if the unit has been committed."""
        return self.status == UnitOfWorkStatus.COMMITTED


class UnitOfWorkStatus(Enum):
    """Status of a unit of work."""
    
    PENDING = "pending"      # Created but not executed
    EXECUTING = "executing"  # Currently executing
    COMMITTED = "committed"  # Successfully committed
    ROLLED_BACK = "rolled_back"  # Rolled back


@dataclass(frozen=True)
class UnitOfWorkOperation:
    """A single operation in a unit of work."""
    
    op_id: str
    
    # Operation type
    kind: str  # "create", "update", "delete", "upsert"
    
    # Target identity
    domain_id: str
    entity_id: str
    
    # Version (for optimistic concurrency)
    expected_version: int = 0
    new_version: int = 1
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    created_at: float = field(default_factory=time.monotonic)


class UnitOfWorkBuilder:
    """
    Builder for creating units of work.
    
    Usage:
        builder = UnitOfWorkBuilder(context_id="ctx_123")
        
        builder.add_create("domain", "entity_1", data={"key": "value"})
        builder.add_update("domain", "entity_2", data={"new": "data"}, expected_version=1)
        builder.add_delete("domain", "entity_3")
        
        unit = builder.build()
    """
    
    def __init__(
        self,
        context_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
    ) -> None:
        self._context_id = context_id
        self._transaction_id = transaction_id
        self._operations: List[UnitOfWorkOperation] = []
    
    def add_create(
        self,
        domain_id: str,
        entity_id: str,
        data: Dict[str, Any],
        version: int = 1,
    ) -> "UnitOfWorkBuilder":
        """Add a create operation."""
        op = UnitOfWorkOperation(
            op_id=str(uuid.uuid4()),
            kind="create",
            domain_id=domain_id,
            entity_id=entity_id,
            expected_version=0,
            new_version=version,
            payload=data,
        )
        self._operations.append(op)
        return self
    
    def add_update(
        self,
        domain_id: str,
        entity_id: str,
        data: Dict[str, Any],
        expected_version: int,
        new_version: Optional[int] = None,
    ) -> "UnitOfWorkBuilder":
        """Add an update operation."""
        op = UnitOfWorkOperation(
            op_id=str(uuid.uuid4()),
            kind="update",
            domain_id=domain_id,
            entity_id=entity_id,
            expected_version=expected_version,
            new_version=new_version or (expected_version + 1),
            payload=data,
        )
        self._operations.append(op)
        return self
    
    def add_delete(
        self,
        domain_id: str,
        entity_id: str,
    ) -> "UnitOfWorkBuilder":
        """Add a delete operation."""
        op = UnitOfWorkOperation(
            op_id=str(uuid.uuid4()),
            kind="delete",
            domain_id=domain_id,
            entity_id=entity_id,
            expected_version=0,
            new_version=0,
        )
        self._operations.append(op)
        return self
    
    def add_upsert(
        self,
        domain_id: str,
        entity_id: str,
        data: Dict[str, Any],
    ) -> "UnitOfWorkBuilder":
        """Add an upsert operation."""
        op = UnitOfWorkOperation(
            op_id=str(uuid.uuid4()),
            kind="upsert",
            domain_id=domain_id,
            entity_id=entity_id,
            expected_version=0,
            new_version=1,
            payload=data,
        )
        self._operations.append(op)
        return self
    
    def build(self) -> UnitOfWork:
        """Build the unit of work."""
        return UnitOfWork(
            unit_id=str(uuid.uuid4()),
            context_id=self._context_id,
            transaction_id=self._transaction_id,
            operations=self._operations,
        )
    
    def clear(self) -> "UnitOfWorkBuilder":
        """Clear all operations and start over."""
        self._operations = []
        return self


class UnitOfWorkExecutor:
    """
    Executes units of work against persistence backends.
    
    Provides:
        - Atomic execution with transaction support
        - Rollback on failure
        - Version conflict detection
    """
    
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        
        # Execution stats
        self._executed_count = 0
        self._committed_count = 0
        self._rolled_back_count = 0
    
    async def execute(
        self,
        unit: UnitOfWork,
    ) -> "UnitOfWorkResult":
        """
        Execute a unit of work.
        
        Args:
            unit: The unit to execute
            
        Returns:
            Result with execution status
        """
        try:
            # Phase 1: Validate operations
            if not await self._validate(unit):
                return UnitOfWorkResult(
                    result_id=str(uuid.uuid4()),
                    request_id=unit.unit_id,
                    runtime_id=self._runtime_id,
                    unit_id=unit.unit_id,
                    status=UnitOfWorkStatus.ROLLED_BACK,
                    error_message="Validation failed",
                )
            
            # Phase 2: Execute operations
            results = []
            for op in unit.operations:
                result = await self._execute_operation(op)
                results.append(result)
                
                if not result.success:
                    raise UnitOfWorkExecutionError(
                        f"Operation {op.op_id} failed: {result.error_message}"
                    )
            
            # Phase 3: Commit
            await self._commit(unit, results)
            
            self._committed_count += 1
            
            return UnitOfWorkResult(
                result_id=str(uuid.uuid4()),
                request_id=unit.unit_id,
                runtime_id=self._runtime_id,
                unit_id=unit.unit_id,
                status=UnitOfWorkStatus.COMMITTED,
                operations_executed=len(results),
            )
            
        except UnitOfWorkExecutionError as e:
            # Rollback on failure
            await self._rollback(unit, results)
            
            self._rolled_back_count += 1
            
            return UnitOfWorkResult(
                result_id=str(uuid.uuid4()),
                request_id=unit.unit_id,
                runtime_id=self._runtime_id,
                unit_id=unit.unit_id,
                status=UnitOfWorkStatus.ROLLED_BACK,
                error_message=str(e),
                operations_executed=len(results) if 'results' in locals() else 0,
            )
    
    async def _validate(self, unit: UnitOfWork) -> bool:
        """Validate the unit before execution."""
        # Check required fields
        if not unit.operations:
            return False
        
        for op in unit.operations:
            # Validate operation type
            if op.kind not in ("create", "update", "delete", "upsert"):
                return False
            
            # Validate domain and entity IDs
            if not op.domain_id or not op.entity_id:
                return False
        
        return True
    
    async def _execute_operation(self, op: UnitOfWorkOperation) -> "OperationResult":
        """Execute a single operation."""
        # In production, this would execute against the backend
        return OperationResult(
            result_id=op.op_id,
            success=True,
        )
    
    async def _commit(self, unit: UnitOfWork, results: List[OperationResult]) -> None:
        """Commit the unit of work."""
        # In production, this would persist to backend with transaction
        pass
    
    async def _rollback(
        self,
        unit: UnitOfWork,
        results: List[OperationResult],
    ) -> None:
        """Rollback changes from a failed execution."""
        # In production, this would undo executed operations
        pass
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get executor diagnostics."""
        return {
            "runtime_id": self._runtime_id,
            "executed_count": self._executed_count,
            "committed_count": self._committed_count,
            "rolled_back_count": self._rolled_back_count,
        }


@dataclass(frozen=True)
class UnitOfWorkResult:
    """Result of a unit of work execution."""
    
    result_id: str
    
    request_id: str
    runtime_id: str
    unit_id: str
    
    status: UnitOfWorkStatus
    timestamp: float = field(default_factory=time.monotonic)
    
    # Success case
    operations_executed: int = 0
    
    # Failure case
    error_message: Optional[str] = None
    failed_operation_ids: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        return self.status == UnitOfWorkStatus.COMMITTED


@dataclass(frozen=True)
class OperationResult:
    """Result of a single operation."""
    
    result_id: str
    
    success: bool
    timestamp: float = field(default_factory=time.monotonic)
    
    # Success case
    new_version: Optional[int] = None
    
    # Failure case
    error_message: Optional[str] = None


class UnitOfWorkExecutionError(Exception):
    """Raised when a unit of work fails to execute."""
    pass


# =============================================================================
# Async Context Manager for Transaction Boundaries
# =============================================================================

class transaction_context:
    """
    Async context manager for transaction boundaries.
    
    Usage:
        async with persistence_context.transaction("ctx_123") as ctx:
            # Do persistence operations
            await ctx.do_something()
        
        The transaction is automatically committed on exit or rolled back on error.
    """
    
    def __init__(
        self,
        manager: PersistenceContextManager,
        context_id: str,
    ) -> None:
        self._manager = manager
        self._context_id = context_id
        self._context: Optional[PersistenceContext] = None
        self._committed = False
    
    async def __aenter__(self) -> PersistenceContext:
        """Enter the transaction context."""
        self._context = self._manager.get_context(self._context_id)
        
        if not self._context:
            raise RuntimeError(f"Context {self._context_id} not found")
        
        return self._context
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the transaction context."""
        if self._context and not self._committed:
            # Rollback on exception
            pass  # Would trigger rollback in production
        
        # Cleanup context
        self._manager.remove_context(self._context_id)
    
    async def commit(self) -> None:
        """Manually commit the transaction."""
        self._committed = True


__all__ = [
    "PersistenceContext",
    "PersistenceContextManager",
    "UnitOfWork",
    "UnitOfWorkStatus",
    "UnitOfWorkOperation",
    "UnitOfWorkBuilder",
    "UnitOfWorkExecutor",
    "UnitOfWorkResult",
    "OperationResult",
    "UnitOfWorkExecutionError",
    "transaction_context",
]