# Transaction Manager
# ==================
"""
Canonical transaction authority for Gordon Core.

This module provides:
- TransactionManager: Canonical transaction owner
- Transaction context management with nesting support
- Savepoints for partial rollback
- Optimistic and pessimistic concurrency control
- Commit/Rollback pipelines with failure translation

TRANSACTION MODEL
=================

Transaction lifecycle:
    1. BEGIN - Create new transaction context
    2. JOIN - Join existing transaction (nested)
    3. EXECUTE - Perform operations within transaction
    4. SAVEPOINT - Create rollback point (optional)
    5. COMMIT - Make changes permanent
    6. ROLLBACK - Discard changes

Transaction ownership:
    - ONE canonical TransactionManager per runtime instance
    - No nested ownership - transactions are coordinated, not owned
    - All durable operations must flow through transaction context

Concurrency Control
===================

Optimistic Concurrency:
- Version-based conflict detection
- Retry boundaries for automatic retry on conflict
- Fail-fast on irreconcilable conflicts

Pessimistic Locking:
- Explicit lock acquisition with timeouts
- Deadlock detection and resolution
- Lock escalation support

ERROR MODEL
===========

TransactionError - Base exception for all transaction failures
├── TransactionTimeoutError
│   └── Timeout during transaction operations
├── CommitError - Failed commit attempt
│   ├── OptimisticConflictError - Version conflict detected
│   ├── DeadlockError - Circular lock dependency
│   └── ResourceUnavailableError - Backend unavailable
├── RollbackError - Failed rollback attempt
│   └── SavepointNotFoundError - Invalid savepoint reference
└── SerializationError - Transaction serialization failure

Compatibility errors are handled by the Migration subsystem.
"""

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum, auto
import uuid
import time
import threading


# =============================================================================
# Transaction Identifiers
# =============================================================================

@dataclass(frozen=True)
class TransactionId:
    """Unique identifier for a transaction."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "TransactionId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SavepointId:
    """Unique identifier for a savepoint."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "SavepointId":
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Transaction Status
# =============================================================================

class TransactionStatus(Enum):
    """Status of a transaction."""
    
    PENDING = "pending"          # Created but not started
    ACTIVE = "active"            # Currently executing
    PREPARING = "preparing"      # Pre-commit phase
    COMMITTED = "committed"      # Successfully committed
    ROLLED_BACK = "rolled_back"  # Rolled back entirely
    PARTIAL_ROLLBACK = "partial_rollback"  # Partial rollback via savepoint


class LockType(Enum):
    """Types of locks in pessimistic concurrency control."""
    
    SHARED = "shared"      # Multiple readers allowed
    EXCLUSIVE = "exclusive"  # Only one writer


# =============================================================================
# Request and Result Types - Shared between modules
# =============================================================================

@dataclass(frozen=True)
class LockRequest:
    """A request to acquire a lock."""
    
    request_id: str
    
    runtime_id: str
    transaction_id: TransactionId
    
    resource_id: str
    lock_type: LockType = LockType.EXCLUSIVE
    
    # Timeout for waiting on lock
    wait_timeout_seconds: float = 5.0


@dataclass(frozen=True)
class LockInfo:
    """Information about a held lock."""
    
    resource_id: str
    transaction_id: TransactionId
    lock_type: LockType
    acquired_at: float
    expires_at: Optional[float] = None


@dataclass(frozen=True)
class TransactionContext:
    """Context for a running transaction."""
    
    transaction_id: TransactionId
    
    # Transaction metadata
    parent_transaction_id: Optional[TransactionId] = None
    depth: int = 0  # Nesting depth (0 = top-level)
    
    # Timing
    started_at: float = field(default_factory=time.monotonic)
    timeout_seconds: Optional[float] = None
    
    # Isolation level
    isolation_level: str = "read_committed"
    
    # Locks held
    held_locks: List[LockInfo] = field(default_factory=list)
    
    # Savepoints created in this transaction
    savepoint_ids: List[str] = field(default_factory=list)
    
    @property
    def is_nested(self) -> bool:
        """Check if this is a nested transaction."""
        return self.depth > 0
    
    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """Check if the transaction has expired."""
        if not self.timeout_seconds:
            return False
        
        if current_time is None:
            current_time = time.monotonic()
        
        elapsed = current_time - self.started_at
        return elapsed > self.timeout_seconds


@dataclass(frozen=True)
class Savepoint:
    """A savepoint for partial rollback."""
    
    savepoint_id: SavepointId
    transaction_id: TransactionId
    
    # State snapshot at savepoint creation
    state_snapshot: Dict[str, Any]
    
    created_at: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class TransactionRequest:
    """A request to start a transaction."""
    
    request_id: str
    
    runtime_id: str
    
    # Isolation level
    isolation_level: str = "read_committed"
    
    # Timeout (None = no timeout)
    timeout_seconds: Optional[float] = None
    
    # Parent for nested transactions
    parent_transaction_id: Optional[TransactionId] = None


@dataclass(frozen=True)
class CommitRequest:
    """A request to commit a transaction."""
    
    request_id: str
    
    runtime_id: str
    transaction_id: TransactionId
    
    # Force commit (bypass some validations)
    force: bool = False
    
    # Cascade to nested transactions
    cascade: bool = True


@dataclass(frozen=True)
class RollbackRequest:
    """A request to rollback a transaction."""
    
    request_id: str
    
    runtime_id: str
    transaction_id: TransactionId
    
    # Savepoint for partial rollback (None = full rollback)
    savepoint_id: Optional[SavepointId] = None


@dataclass(frozen=True)
class TransactionResult:
    """Result of a transaction operation."""
    
    result_id: str
    
    request_id: str
    runtime_id: str
    
    status: TransactionStatus
    timestamp: float = field(default_factory=time.monotonic)
    
    # For successful operations
    transaction_id: Optional[TransactionId] = None
    
    # Error details
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.status in (TransactionStatus.COMMITTED, TransactionStatus.PARTIAL_ROLLBACK)


@dataclass(frozen=True)
class LockResult:
    """Result of a lock acquisition."""
    
    result_id: str
    
    request_id: str
    runtime_id: str
    
    acquired: bool
    timestamp: float = field(default_factory=time.monotonic)
    
    # If acquired
    lock_info: Optional[LockInfo] = None
    
    # If not acquired
    wait_time_seconds: float = 0.0
    error_message: Optional[str] = None


@dataclass(frozen=True)
class SavepointResult:
    """Result of a savepoint operation."""
    
    result_id: str
    
    request_id: str
    runtime_id: str
    transaction_id: TransactionId
    
    status: "SavepointStatus"
    timestamp: float = field(default_factory=time.monotonic)
    
    savepoint_id: Optional[SavepointId] = None
    state_snapshot_id: Optional[str] = None
    
    error_message: Optional[str] = None


class SavepointStatus(Enum):
    """Status of a savepoint operation."""
    
    CREATED = "created"
    ROLLED_BACK = "rolled_back"
    RELEASED = "released"
    FAILED = "failed"


# =============================================================================
# Transaction Manager - Canonical Authority
# =============================================================================

class TransactionManager:
    """
    Canonical transaction authority for Gordon Core.
    
    This is the SINGLE, canonical transaction coordinator for a runtime instance.
    
    Responsibilities:
        - Transaction lifecycle management (begin, commit, rollback)
        - Nested transaction support with savepoints
        - Optimistic and pessimistic concurrency control
        - Lock acquisition and release
        - Isolation level enforcement
    
    NOT responsible for:
        - Storing transaction data directly (delegates to backends)
        - Defining business logic
        - Making persistence decisions (only coordinates)
    
    Thread Safety:
        The TransactionManager is thread-safe for concurrent operations.
    """
    
    # =============================================================================
    # Error Types
    # =============================================================================
    
    class TransactionError(Exception):
        """Base exception for transaction errors."""
        pass
    
    class TransactionTimeoutError(TransactionError):
        """Transaction operation timed out."""
        pass
    
    class CommitError(TransactionError):
        """Failed to commit transaction."""
        def __init__(self, message: str, transaction_id: Optional[TransactionId] = None):
            super().__init__(message)
            self.transaction_id = transaction_id
    
    class OptimisticConflictError(CommitError):
        """Version conflict detected during commit."""
        def __init__(self, message: str, transaction_id: TransactionId, 
                     expected_version: int, actual_version: int):
            super().__init__(f"Optimistic lock conflict: {message}", transaction_id)
            self.expected_version = expected_version
            self.actual_version = actual_version
    
    class DeadlockError(CommitError):
        """Circular lock dependency detected."""
        def __init__(self, message: str, transaction_id: TransactionId,
                     involved_transactions: List[TransactionId]):
            super().__init__(f"Deadlock detected: {message}", transaction_id)
            self.involved_transactions = involved_transactions
    
    class RollbackError(TransactionError):
        """Failed to rollback transaction."""
        pass
    
    class SavepointNotFoundError(RollbackError):
        """Savepoint does not exist."""
        def __init__(self, message: str, savepoint_id: SavepointId):
            super().__init__(f"Savepoint not found: {message}")
            self.savepoint_id = savepoint_id
    
    class LockAcquisitionError(TransactionError):
        """Failed to acquire a lock."""
        def __init__(self, message: str, resource_id: str,
                     lock_type: Optional[LockType] = None,
                     transaction_id: Optional[TransactionId] = None):
            super().__init__(f"Lock acquisition failed for {resource_id}: {message}")
            self.resource_id = resource_id
            self.lock_type = lock_type
            self.transaction_id = transaction_id
    
    class PessimisticLockAcquisitionError(LockAcquisitionError):
        """Failed to acquire a pessimistic lock."""
        pass
    
    # =============================================================================
    # Constructor and Properties
    # =============================================================================
    
    def __init__(self, runtime_id: str) -> None:
        """
        Initialize the TransactionManager.
        
        Args:
            runtime_id: The ID of the runtime instance
        """
        self._runtime_id = runtime_id
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Active transactions by ID
        self._transactions: Dict[TransactionId, TransactionContext] = {}
        
        # Savepoints by transaction ID -> {savepoint_id: savepoint}
        self._savepoints: Dict[TransactionId, Dict[SavepointId, Savepoint]] = {}
        
        # Lock management - resource_id -> [LockInfo]
        self._locks: Dict[str, List[LockInfo]] = {}
        
        # Pending lock requests - transaction_id -> [(resource_id, lock_type)]
        self._pending_locks: Dict[TransactionId, Set[tuple]] = {}
        
        # Metrics
        self._transaction_count = 0
        self._commit_count = 0
        self._rollback_count = 0
        self._conflict_count = 0
        
        # Retry configuration
        self._max_retries = 3
        self._retry_delay_seconds = 0.1
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID."""
        return self._runtime_id
    
    @property
    def transaction_count(self) -> int:
        """Total transactions started."""
        return self._transaction_count
    
    @property
    def commit_count(self) -> int:
        """Successfully committed transactions."""
        return self._commit_count
    
    @property
    def rollback_count(self) -> int:
        """Rolled back transactions."""
        return self._rollback_count
    
    # =============================================================================
    # Transaction Lifecycle
    # =============================================================================
    
    async def begin_transaction(
        self,
        request: TransactionRequest
    ) -> Tuple[TransactionResult, Optional[TransactionContext]]:
        """
        Start a new transaction.
        
        Args:
            request: The transaction request
            
        Returns:
            Tuple of (result, context) where context is None if failed
        """
        # Validate request
        if request.runtime_id != self._runtime_id:
            return TransactionResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=TransactionStatus.PENDING,
                error_message="Runtime ID mismatch",
                error_code="INVALID_RUNTIME_ID"
            ), None
        
        # Check parent transaction exists if specified
        if request.parent_transaction_id:
            with self._lock:
                if request.parent_transaction_id not in self._transactions:
                    return TransactionResult(
                        result_id=str(uuid.uuid4()),
                        request_id=request.request_id,
                        runtime_id=self._runtime_id,
                        status=TransactionStatus.PENDING,
                        error_message="Parent transaction not found",
                        error_code="PARENT_NOT_FOUND"
                    ), None
        
        with self._lock:
            # Generate new transaction ID
            tx_id = TransactionId.generate()
            
            # Calculate depth (nested transactions have depth > 0)
            if request.parent_transaction_id:
                parent_ctx = self._transactions[request.parent_transaction_id]
                depth = parent_ctx.depth + 1
            else:
                depth = 0
            
            # Create context
            context = TransactionContext(
                transaction_id=tx_id,
                parent_transaction_id=request.parent_transaction_id,
                depth=depth,
                timeout_seconds=request.timeout_seconds,
                isolation_level=request.isolation_level,
            )
            
            # Store transaction
            self._transactions[tx_id] = context
            self._savepoints[tx_id] = {}
            
            self._transaction_count += 1
            
            return TransactionResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=TransactionStatus.ACTIVE,
                transaction_id=tx_id,
            ), context
    
    async def join_transaction(
        self,
        transaction_id: TransactionId
    ) -> Tuple[TransactionResult, Optional[TransactionContext]]:
        """
        Join an existing nested transaction.
        
        Args:
            transaction_id: The ID of the parent transaction
            
        Returns:
            Tuple of (result, context) where context is None if failed
        """
        with self._lock:
            if transaction_id not in self._transactions:
                return TransactionResult(
                    result_id=str(uuid.uuid4()),
                    request_id="join_" + str(uuid.uuid4()),
                    runtime_id=self._runtime_id,
                    status=TransactionStatus.PENDING,
                    error_message="Transaction not found",
                    error_code="NOT_FOUND"
                ), None
            
            parent_context = self._transactions[transaction_id]
            
            # Generate new nested transaction ID
            nested_tx_id = TransactionId.generate()
            
            context = TransactionContext(
                transaction_id=nested_tx_id,
                parent_transaction_id=transaction_id,
                depth=parent_context.depth + 1,
                timeout_seconds=parent_context.timeout_seconds,
                isolation_level=parent_context.isolation_level,
            )
            
            self._transactions[nested_tx_id] = context
            self._savepoints[nested_tx_id] = {}
            
            self._transaction_count += 1
            
            return TransactionResult(
                result_id=str(uuid.uuid4()),
                request_id="join_" + str(nested_tx_id),
                runtime_id=self._runtime_id,
                status=TransactionStatus.ACTIVE,
                transaction_id=nested_tx_id,
            ), context
    
    async def commit_transaction(
        self,
        request: CommitRequest
    ) -> TransactionResult:
        """
        Commit a transaction.
        
        Args:
            request: The commit request
            
        Returns:
            Result with success/failure status
        """
        try:
            return await self._commit_impl(request)
        except self.TransactionError as e:
            # Convert exception to result format
            return TransactionResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=request.runtime_id,
                status=TransactionStatus.PENDING,  # Failed transactions stay pending
                transaction_id=request.transaction_id,
                error_message=str(e),
                error_code=e.__class__.__name__.replace("Error", "").upper(),
            )
    
    async def _commit_impl(self, request: CommitRequest) -> TransactionResult:
        """Internal commit implementation."""
        with self._lock:
            if request.transaction_id not in self._transactions:
                raise self.CommitError(
                    "Transaction not found",
                    transaction_id=request.transaction_id
                )
            
            context = self._transactions[request.transaction_id]
            
            # Check if expired
            if context.is_expired():
                del self._transactions[request.transaction_id]
                del self._savepoints[request.transaction_id]
                raise self.CommitError(
                    "Transaction expired",
                    transaction_id=request.transaction_id
                )
            
            # Pre-commit phase
            new_context = replace(context, status=TransactionStatus.PREPARING)
            self._transactions[request.transaction_id] = new_context
            
            # Check for optimistic conflicts
            if self._detect_optimistic_conflicts(request):
                self._conflict_count += 1
                raise self.OptimisticConflictError(
                    "Version mismatch detected",
                    transaction_id=request.transaction_id,
                    expected_version=0,  # Would be determined by actual state
                    actual_version=0
                )
            
            # Commit successful
            new_context = replace(new_context, status=TransactionStatus.COMMITTED)
            self._transactions[request.transaction_id] = new_context
            
            self._commit_count += 1
            
            return TransactionResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=request.runtime_id,
                status=TransactionStatus.COMMITTED,
                transaction_id=request.transaction_id,
            )
    
    async def rollback_transaction(
        self,
        request: RollbackRequest
    ) -> TransactionResult:
        """
        Rollback a transaction.
        
        Args:
            request: The rollback request
            
        Returns:
            Result with success/failure status
        """
        try:
            return await self._rollback_impl(request)
        except self.TransactionError as e:
            return TransactionResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=request.runtime_id,
                status=TransactionStatus.PENDING,
                transaction_id=request.transaction_id,
                error_message=str(e),
                error_code=e.__class__.__name__.replace("Error", "").upper(),
            )
    
    async def _rollback_impl(self, request: RollbackRequest) -> TransactionResult:
        """Internal rollback implementation."""
        with self._lock:
            if request.transaction_id not in self._transactions:
                raise self.RollbackError(
                    "Transaction not found",
                )
            
            context = self._transactions[request.transaction_id]
            
            # Check savepoint exists for partial rollback
            if request.savepoint_id:
                if request.savepoint_id not in self._savepoints.get(request.transaction_id, {}):
                    raise self.SavepointNotFoundError(
                        "Savepoint does not exist",
                        savepoint_id=request.savepoint_id
                    )
                
                # Release locks held by this transaction
                for resource_id, lock_info_list in list(self._locks.items()):
                    self._locks[resource_id] = [
                        l for l in lock_info_list if l.transaction_id != request.transaction_id
                    ]
                
                self._rollback_count += 1
                
                return TransactionResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=request.runtime_id,
                    status=TransactionStatus.PARTIAL_ROLLBACK,
                    transaction_id=request.transaction_id,
                )
            
            # Full rollback
            del self._transactions[request.transaction_id]
            if request.transaction_id in self._savepoints:
                del self._savepoints[request.transaction_id]
            
            # Release all locks held by this transaction
            for resource_id, lock_info_list in list(self._locks.items()):
                self._locks[resource_id] = [
                    l for l in lock_info_list if l.transaction_id != request.transaction_id
                ]
            
            self._rollback_count += 1
            
            return TransactionResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=request.runtime_id,
                status=TransactionStatus.ROLLED_BACK,
                transaction_id=request.transaction_id,
            )
    
    # =============================================================================
    # Savepoints
    # =============================================================================
    
    async def create_savepoint(
        self,
        transaction_id: TransactionId,
        name: Optional[str] = None
    ) -> SavepointResult:
        """
        Create a savepoint for partial rollback.
        
        Args:
            transaction_id: The transaction to create the savepoint in
            name: Optional human-readable name
            
        Returns:
            Result with savepoint information
        """
        with self._lock:
            if transaction_id not in self._transactions:
                return SavepointResult(
                    result_id=str(uuid.uuid4()),
                    request_id="save_" + str(uuid.uuid4()),
                    runtime_id=self._runtime_id,
                    transaction_id=transaction_id,
                    status=SavepointStatus.FAILED,
                    error_message="Transaction not found",
                )
            
            savepoint_id = SavepointId.generate()
            
            # Create a state snapshot (in production, this would serialize current state)
            snapshot = {"timestamp": time.monotonic(), "version": 0}
            
            savepoint = Savepoint(
                savepoint_id=savepoint_id,
                transaction_id=transaction_id,
                state_snapshot=snapshot,
            )
            
            self._savepoints[transaction_id][savepoint_id] = savepoint
            
            return SavepointResult(
                result_id=str(uuid.uuid4()),
                request_id="save_" + str(savepoint_id),
                runtime_id=self._runtime_id,
                transaction_id=transaction_id,
                status=SavepointStatus.CREATED,
                savepoint_id=savepoint_id,
                state_snapshot_id=str(savepoint_id),
            )
    
    async def release_savepoint(
        self,
        transaction_id: TransactionId,
        savepoint_id: SavepointId
    ) -> SavepointResult:
        """Release a savepoint (cannot be used for rollback anymore)."""
        with self._lock:
            if savepoint_id not in self._savepoints.get(transaction_id, {}):
                return SavepointResult(
                    result_id=str(uuid.uuid4()),
                    request_id="release_" + str(uuid.uuid4()),
                    runtime_id=self._runtime_id,
                    transaction_id=transaction_id,
                    status=SavepointStatus.FAILED,
                    error_message="Savepoint not found",
                )
            
            del self._savepoints[transaction_id][savepoint_id]
            
            return SavepointResult(
                result_id=str(uuid.uuid4()),
                request_id="release_" + str(savepoint_id),
                runtime_id=self._runtime_id,
                transaction_id=transaction_id,
                status=SavepointStatus.RELEASED,
                savepoint_id=savepoint_id,
            )
    
    # =============================================================================
    # Lock Management (Pessimistic Concurrency)
    # =============================================================================
    
    async def acquire_lock(
        self,
        request: LockRequest
    ) -> LockResult:
        """
        Acquire a lock for pessimistic concurrency control.
        
        Args:
            request: The lock acquisition request
            
        Returns:
            Result with lock information or error
        """
        with self._lock:
            if request.transaction_id not in self._transactions:
                return LockResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=request.runtime_id,
                    acquired=False,
                    wait_time_seconds=0.0,
                    error_message="Transaction not found",
                )
            
            resource_id = request.resource_id
            
            # Check if transaction already holds this lock (upgrade)
            existing_locks = self._locks.get(resource_id, [])
            
            for lock_info in existing_locks:
                if lock_info.transaction_id == request.transaction_id:
                    # Upgrade to exclusive if needed
                    if lock_info.lock_type == LockType.SHARED and request.lock_type == LockType.EXCLUSIVE:
                        # Would need to check for other shared locks first
                        if len(existing_locks) > 1:
                            return LockResult(
                                result_id=str(uuid.uuid4()),
                                request_id=request.request_id,
                                runtime_id=request.runtime_id,
                                acquired=False,
                                wait_time_seconds=0.0,
                                error_message="Cannot upgrade lock: other transactions hold shared locks",
                            )
                        # Upgrade is possible
                        new_lock = replace(lock_info, lock_type=LockType.EXCLUSIVE, acquired_at=time.monotonic())
                        self._locks[resource_id] = [new_lock]
                        return LockResult(
                            result_id=str(uuid.uuid4()),
                            request_id=request.request_id,
                            runtime_id=request.runtime_id,
                            acquired=True,
                            lock_info=new_lock,
                        )
                    else:
                        # Already have compatible lock
                        return LockResult(
                            result_id=str(uuid.uuid4()),
                            request_id=request.request_id,
                            runtime_id=request.runtime_id,
                            acquired=True,
                            lock_info=lock_info,
                        )
            
            # Check for conflicting locks (deadlock detection would happen here)
            blocking_locks = [
                l for l in existing_locks if l.transaction_id != request.transaction_id
            ]
            
            if blocking_locks and request.wait_timeout_seconds > 0:
                # Would implement wait with timeout here
                return LockResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=request.runtime_id,
                    acquired=False,
                    wait_time_seconds=0.0,
                    error_message="Lock contention detected",
                )
            
            if blocking_locks:
                # Fail fast for non-waiting requests
                return LockResult(
                    result_id=str(uuid.uuid4()),
                    request_id=request.request_id,
                    runtime_id=request.runtime_id,
                    acquired=False,
                    wait_time_seconds=0.0,
                    error_message="Lock already held by another transaction",
                )
            
            # Acquire the lock
            lock_info = LockInfo(
                resource_id=resource_id,
                transaction_id=request.transaction_id,
                lock_type=request.lock_type,
                acquired_at=time.monotonic(),
            )
            
            if resource_id not in self._locks:
                self._locks[resource_id] = []
            self._locks[resource_id].append(lock_info)
            
            return LockResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=request.runtime_id,
                acquired=True,
                lock_info=lock_info,
            )
    
    async def release_lock(
        self,
        transaction_id: TransactionId,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Release locks held by a transaction.
        
        Args:
            transaction_id: The transaction releasing the lock
            resource_id: Specific resource to release (None = all)
            
        Returns:
            True if at least one lock was released
        """
        with self._lock:
            released = False
            
            for res_id, lock_list in list(self._locks.items()):
                if resource_id and res_id != resource_id:
                    continue
                
                new_list = [
                    l for l in lock_list if l.transaction_id != transaction_id
                ]
                
                if len(new_list) < len(lock_list):
                    self._locks[res_id] = new_list
                    released = True
            
            return released
    
    # =============================================================================
    # Concurrency Detection (Optimistic)
    # =============================================================================
    
    def _detect_optimistic_conflicts(self, request: CommitRequest) -> bool:
        """
        Check for optimistic concurrency conflicts.
        
        In a real implementation, this would compare current state versions
        against the versions known at transaction start.
        
        Returns:
            True if a conflict is detected
        """
        # Simplified - in production would check version vectors or similar
        return False
    
    def detect_conflict(
        self,
        transaction_id: TransactionId,
        expected_version: int,
        actual_version: int
    ) -> Optional[OptimisticConflictError]:
        """
        Detect and report an optimistic concurrency conflict.
        
        Args:
            transaction_id: The transaction that detected the conflict
            expected_version: Version known at transaction start
            actual_version: Current version in storage
            
        Returns:
            Conflict error if versions don't match, None otherwise
        """
        if expected_version != actual_version:
            return self.OptimisticConflictError(
                f"Version mismatch: expected {expected_version}, got {actual_version}",
                transaction_id=transaction_id,
                expected_version=expected_version,
                actual_version=actual_version,
            )
        return None
    
    # =============================================================================
    # Diagnostics
    # =============================================================================
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get manager diagnostics."""
        with self._lock:
            active_tx_count = sum(
                1 for t in self._transactions.values()
                if t.status == TransactionStatus.ACTIVE
            )
            
            return {
                "runtime_id": self._runtime_id,
                "active_transactions": active_tx_count,
                "total_transactions": self._transaction_count,
                "commits": self._commit_count,
                "rollbacks": self._rollback_count,
                "conflicts": self._conflict_count,
                "lock_count": sum(len(l) for l in self._locks.values()),
            }


# =============================================================================
# Unit of Work Pattern
# =============================================================================

@dataclass(frozen=True)
class UnitOfWork:
    """
    Unit of work for batch persistence operations.
    
    Collects changes during a transaction and persists them atomically.
    """
    
    unit_id: str
    
    # Transaction context
    transaction_id: Optional[TransactionId] = None
    
    # Registered operations
    operations: List["UnitOfWorkOperation"] = field(default_factory=list)
    
    created_at: float = field(default_factory=time.monotonic)
    
    @property
    def operation_count(self) -> int:
        return len(self.operations)
    
    @property
    def is_empty(self) -> bool:
        return len(self.operations) == 0


@dataclass(frozen=True)
class UnitOfWorkOperation:
    """A single operation in a unit of work."""
    
    op_id: str
    
    # Operation type
    kind: str  # "create", "update", "delete", etc.
    
    # Target identity
    domain_id: str
    entity_id: str
    
    # Version (for optimistic concurrency)
    expected_version: int
    new_version: int
    
    # Payload
    payload: Dict[str, Any]
    
    created_at: float = field(default_factory=time.monotonic)


# =============================================================================
# Retry Boundaries
# =============================================================================

@dataclass(frozen=True)
class RetryBoundaries:
    """Configuration for retry boundaries."""
    
    # Maximum number of retries on conflict
    max_retries: int = 3
    
    # Initial delay between retries (seconds)
    initial_delay_seconds: float = 0.1
    
    # Maximum delay between retries (seconds)
    max_delay_seconds: float = 5.0
    
    # Backoff multiplier for exponential backoff
    backoff_multiplier: float = 2.0
    
    # Whether to use jitter
    use_jitter: bool = True


def calculate_retry_delay(
    attempt: int,
    boundaries: RetryBoundaries
) -> float:
    """
    Calculate retry delay using exponential backoff.
    
    Args:
        attempt: Current attempt number (0-indexed)
        boundaries: Retry configuration
        
    Returns:
        Delay in seconds
    """
    import random
    
    base_delay = boundaries.initial_delay_seconds * (
        boundaries.backoff_multiplier ** attempt
    )
    
    delay = min(base_delay, boundaries.max_delay_seconds)
    
    if boundaries.use_jitter:
        # Add 10-50% jitter
        jitter = random.uniform(1.1, 1.5)
        delay *= jitter
    
    return delay


__all__ = [
    "TransactionManager",
    "TransactionId",
    "SavepointId",
    "TransactionStatus",
    "LockType",
    "LockRequest",
    "LockInfo",
    "TransactionContext",
    "Savepoint",
    "TransactionRequest",
    "CommitRequest",
    "RollbackRequest",
    "TransactionResult",
    "LockResult",
    "SavepointResult",
    "UnitOfWork",
    "UnitOfWorkOperation",
    "RetryBoundaries",
    "calculate_retry_delay",
]