# Phase 3.15.8: State Consistency & Concurrency Architecture

## Executive Summary

Phase 3.15.8 establishes the canonical architecture governing state consistency and concurrent state access throughout the Gordon Core.

This phase extends:
- **Phase 3.15.1** — Core State Foundations
- **Phase 3.15.2** — State Identity, Scope & Ownership  
- **Phase 3.15.3** — Immutable & Mutable State Semantics
- **Phase 3.15.4** — Runtime State Hierarchy
- **Phase 3.15.5** — State Transitions & Transition Validation
- **Phase 3.15.6** — State Snapshots & Views
- **Phase 3.15.7** — State Versioning & Generations

This phase defines the state-level concurrency model and does **not** define the Core concurrency framework itself. Thread scheduling, executors, synchronization primitives, structured concurrency, and worker architecture belong to **Phase 3.20 — Core Concurrency & Synchronization Architecture**.

---

## Architectural Principles

The state consistency architecture guarantees:

| Principle | Description |
|-----------|-------------|
| **Explicit Ownership** | Exactly one authority may mutate a mutable state aggregate. Multiple concurrent readers are permitted. Multiple concurrent observers are permitted. Multiple concurrent snapshots are permitted. Concurrent mutation by multiple owners is prohibited. |
| **Deterministic Mutations** | All mutations follow deterministic behavior based on ownership, version lineage, and generation lineage. |
| **Version Consistency** | Version changes maintain strict lineage. Stale versions are rejected, not silently overwritten. |
| **Generation Consistency** | Generation changes indicate ownership transitions. Stale generations are detected before applying mutations. |
| **Bounded Contention** | Contention is detected with retry budgets and timeout handling. No silent starvation. |
| **Runtime Isolation** | State aggregates respect runtime boundaries. Cross-runtime access requires policy authorization. |
| **Reproducible Behavior** | Conflicts, validations, and visibility checks produce deterministic results independent of execution order. |
| **Observable Conflicts** | All conflicts produce structured results with detailed findings for debugging and resolution. |

---

## Consistency Model

### State Consistency Classes

Each mutable aggregate declares its consistency guarantees at creation time:

| Class | Description | Use Case |
|-------|-------------|----------|
| `STRONG` | All reads see all prior writes; immediate visibility | Critical system state that requires strict consistency |
| `VERSION_CONSISTENT` | Reads see state at a specific version | Version-bound queries with known snapshot point |
| `TRANSACTIONAL` | Read snapshot from committed transaction | Multi-state operations requiring ACID semantics |
| `EVENTUAL` | Writes propagate with eventual convergence | Distributed caches, async processing |
| `SNAPSHOT` | Consistent snapshot view at capture time | Audit trails, backups, read replicas |
| `READ_ONLY` | No mutations allowed, always consistent | Historical records, configuration views |
| `BEST_EFFORT` | Best attempt, no consistency guarantees | Diagnostic data, non-critical metrics |

### Consistency Guarantees

Every mutable aggregate must declare its consistency guarantees:

1. **CONS-001**: Every mutable aggregate declares exactly one consistency model
2. **CONS-002**: Consistency models are immutable once set
3. **CONS-003**: Readers observe only valid states per the declared model
4. **CONS-004**: Mutations preserve the declared consistency guarantees

---

## Ownership Model

### Single Writer Principle

Exactly one authority may mutate a mutable state aggregate:

```python
# Each aggregate has exactly one owner
class StateAggregate:
    owner_id: OwnerId  # The single authoritative owner
    version_sequence: int  # Version lineage
    generation_epoch: int  # Generation lineage
    
    def mutate(self, expected_generation: ExpectedGeneration):
        """Mutate only if generation matches current owner's epoch"""
```

### Concurrent Readers

Multiple concurrent readers are permitted without conflicts:

- Immutable snapshots provide consistent views
- Views respect version boundaries
- No reader blocks writer (unless exclusive isolation level)

### Mutation Authority

- **Owner Exclusive**: Only the owner may mutate
- **Runtime Local**: Mutations within runtime scope
- **Process Local**: Mutations within process boundary

---

## Optimistic Concurrency Control

### Expected Version

```python
@dataclass(frozen=True)
class ExpectedVersion:
    """Expected version for optimistic concurrency control."""
    value: int           # The expected version sequence number
    strict: bool = True  # Whether this is a strict check
    
    @classmethod
    def match(cls, version_sequence: int) -> "ExpectedVersion":
        """Create an expected version that must match the given version."""
        return cls(value=version_sequence, strict=True)
    
    @classmethod
    def at_least(cls, version_sequence: int) -> "ExpectedVersion":
        """Create an expected version that must be >= the given version."""
        return cls(value=version_sequence, strict=False)
```

### Expected Generation

```python
@dataclass(frozen=True)
class ExpectedGeneration:
    """Expected generation for optimistic concurrency control."""
    value: int           # The expected generation epoch number
    strict: bool = True  # Whether this is a strict check
    
    @classmethod
    def match(cls, epoch: int) -> "ExpectedGeneration":
        """Create an expected generation that must match the given epoch."""
        return cls(value=epoch, strict=True)
```

### Validation Rules

**OCC-VER-001**: Expected version must match current version for success  
**OCC-VER-002**: Version mismatch results in conflict (not silent overwrite)  
**OCC-VER-003**: Expected version may be None (no version tracking)  

**OCC-GEN-001**: Expected generation must match current generation  
**OCC-GEN-002**: Stale generations are rejected (not silently overwritten)  
**OCC-GEN-003**: Generation changes indicate ownership change  

---

## Conflict Detection

### Conflict Types

| Type | Description | Resolution Policy |
|------|-------------|-------------------|
| `VERSION_MISMATCH` | Expected version doesn't match current | REJECT |
| `GENERATION_MISMATCH` | Expected generation doesn't match current | REJECT |
| `OWNERSHIP_CONFLICT` | Ownership has changed since observation | REJECT |
| `TRANSITION_CONFLICT` | State invariants would be violated | REJECT |
| `HIERARCHY_CONFLICT` | Parent-child hierarchy would be invalid | REJECT |
| `RUNTIME_CONFLICT` | Runtime isolation would be violated | REJECT |
| `RESTORATION_CONFLICT` | Restoration would overwrite newer state | REJECT |
| `MIGRATION_CONFLICT` | Migration would lose data | REJECT |

### Conflict Detection Result

```python
@dataclass(frozen=True)
class ConflictResult:
    """Structured result of conflict detection."""
    conflict_detected: bool
    conflict_type: Optional[ConflictType] = None
    detected_at_utc: float = field(default_factory=_time_module.monotonic)
    findings: Tuple[str, ...] = field(default_factory=tuple)
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    
    @classmethod
    def version_conflict(
        cls, expected_version: int, actual_version: int
    ) -> "ConflictResult":
        """Create a version mismatch conflict result."""
        return cls(
            conflict_detected=True,
            conflict_type=ConflictType.VERSION_MISMATCH,
            findings=(f"Version mismatch: expected {expected_version}, got {actual_version}",),
            expected_value=str(expected_version),
            actual_value=str(actual_version),
        )
```

---

## Conflict Resolution

### Resolution Policies

| Policy | Description | When to Use |
|--------|-------------|-------------|
| `REJECT` | Reject the mutation, return error | Version conflicts (no data loss acceptable) |
| `RETRY` | Retry with current state (with backoff) | Transient contention, distributed systems |
| `REVALIDATE` | Revalidate with updated context | Context-dependent operations |
| `RECONCILE` | Attempt to merge changes automatically | Mergeable operations (dictionaries, sets) |
| `MERGE` | Explicitly merge mutation with current state | Conflicting updates can be combined |
| `COMPENSATE` | Execute compensating actions for rollback | Multi-step operations requiring ACID |
| `ESCALATE` | Escalate to higher authority for resolution | Unknown conflict requiring human intervention |

### Retry Policy

```python
@dataclass(frozen=True)
class RetryPolicy:
    """Retry configuration for conflict resolution."""
    max_attempts: int = 1                      # Maximum retry attempts (including initial)
    initial_backoff_seconds: float = 0.0       # Initial delay before first retry
    backoff_multiplier: float = 2.0            # Exponential backoff multiplier
    max_backoff_seconds: Optional[float] = None  # Maximum delay between retries
    
    def calculate_delay(self, attempt_number: int) -> float:
        """Calculate delay before the given retry attempt (0-indexed)."""
        if attempt_number <= 0:
            return 0.0
        
        # Exponential backoff
        delay = self.initial_backoff_seconds * (
            self.backoff_multiplier ** (attempt_number - 1)
        )
        
        # Apply cap
        if self.max_backoff_seconds is not None:
            delay = min(delay, self.max_backoff_seconds)
        
        return delay
```

---

## Visibility Model

### Visibility Levels

| Level | Description | Access Control |
|-------|-------------|----------------|
| `PRIVATE` | Only the owner may observe | Owner-only access |
| `OWNER_VISIBLE` | Owner and designated observers | Explicit authorization |
| `SUBSYSTEM_VISIBLE` | All entities in same subsystem | Subsystem membership |
| `RUNTIME_VISIBLE` | All within same runtime instance | Runtime membership |
| `DIAGNOSTIC` | Read-only diagnostic access | Diagnostic role |
| `PUBLIC` | External visibility (with restrictions) | Public exposure with filtering |

### Visibility Rules

**VIS-001**: Every state aggregate has a primary visibility level  
**VIS-002**: Visibility does not imply mutation authority  
**VIS-003**: Visibility may be restricted by runtime/session isolation  

```python
def check_visibility(
    self,
    state_id: str,
    observer_identity: str,
    visibility_level: VisibilityLevel,
    runtime_id: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Verify that the observer has visibility to the state.
    
    Returns:
        (allowed: bool, reason: Optional[str])
    """
    if visibility_level == VisibilityLevel.PRIVATE:
        # Only owner may observe
        return False, "private_state_only_visible_to_owner"
    
    if visibility_level == VisibilityLevel.RUNTIME_VISIBLE:
        # Must be in same runtime
        pass  # Validation handled by caller
    
    return True, None
```

---

## Isolation Model

### Isolation Levels

| Level | Description | Scope |
|-------|-------------|-------|
| `ISOLATED` | No shared access; exclusive ownership | Exclusive to owner |
| `SHARED_READ` | Multiple readers, single writer | Concurrent observation allowed |
| `OWNER_EXCLUSIVE` | Owner-only access (no concurrent observers) | Single access point |
| `RUNTIME_LOCAL` | Bound to runtime instance | Runtime scope |
| `PROCESS_LOCAL` | Bound to process boundary | Process scope |
| `DISTRIBUTED` | Distributed system scope | Cross-process, cross-host |
| `EXTERNAL_READ_ONLY` | External source, read-only locally | Remote observation |

### Isolation Rules

**ISO-001**: Every operation has an explicit isolation level  
**ISO-002**: Isolation is enforced at all access points  
**ISO-003**: Cross-isolation operations require policy authorization  

```python
def verify_isolation(
    self,
    state_runtime_id: Optional[str],
    observer_runtime_id: Optional[str],
) -> Tuple[bool, Optional[str]]:
    """
    Verify isolation boundaries are respected.
    
    Returns:
        (allowed: bool, reason: Optional[str])
    """
    if state_runtime_id is not None and observer_runtime_id is not None:
        if state_runtime_id != observer_runtime_id:
            return False, f"isolation_violation: state in {state_runtime_id}, observer in {observer_runtime_id}"
    
    return True, None
```

---

## Atomic State Operations

### Status Codes

| Status | Description |
|--------|-------------|
| `PENDING` | Operation initialized but not yet validated |
| `VALIDATED` | All validations passed, ready to commit |
| `COMMITTED` | Operation committed successfully |
| `REJECTED` | Rejected due to conflict or validation failure |
| `ROLLED_BACK` | Rolled back after partial execution |

### Atomic Result

```python
@dataclass(frozen=True)
class AtomicOperationResult:
    """Result of an atomic state operation."""
    status: AtomicOperationStatus
    
    started_at_utc: float = field(default_factory=_time_module.monotonic)
    completed_at_utc: Optional[float] = None
    
    resulting_version_sequence: Optional[int] = None
    resulting_generation: Optional[int] = None
    
    conflict_result: Optional[ConflictResult] = None
    findings: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def is_success(self) -> bool:
        """Check if operation succeeded."""
        return self.status == AtomicOperationStatus.COMMITTED
    
    @classmethod
    def committed(
        cls,
        version_sequence: int,
        generation: int,
        findings: Tuple[str, ...] = (),
    ) -> "AtomicOperationResult":
        """Create a committed result."""
        return cls(
            status=AtomicOperationStatus.COMMITTED,
            resulting_version_sequence=version_sequence,
            resulting_generation=generation,
            completed_at_utc=_time_module.monotonic(),
            findings=findings,
        )
```

### Atomic Visibility

**ATOMIC-001**: Every operation has exactly one final status  
**ATOMIC-002**: Committed implies atomic visibility  
**ATOMIC-003**: Rejected/RolledBack implies no state change  

Observers shall **never** observe:
- Half-completed transitions
- Partially validated mutations
- Incomplete ownership transfers
- Incomplete version updates

---

## Concurrency Facade (Public API)

### StateConcurrencyFacade

```python
class StateConcurrencyFacade:
    """
    Canonical facade for state concurrency operations.
    
    Supports optimistic concurrency, conflict detection, and visibility
    management without exposing synchronization primitives.
    """
    
    def validate_version(
        self, expected: ExpectedVersion, current_sequence: int
    ) -> Tuple[bool, Optional[ConflictResult]]:
        """Validate that the expected version matches the current version."""
    
    def validate_generation(
        self, expected: ExpectedGeneration, current_epoch: int
    ) -> Tuple[bool, Optional[ConflictResult]]:
        """Validate that the expected generation matches the current generation."""
    
    def detect_conflict(
        self,
        expected_version: Optional[ExpectedVersion],
        expected_generation: Optional[ExpectedGeneration],
        current_version_sequence: int,
        current_generation: int,
    ) -> ConflictResult:
        """Detect conflicts before applying a mutation."""
    
    def check_visibility(
        self,
        state_id: str,
        observer_identity: str,
        visibility_level: VisibilityLevel,
        runtime_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Verify that the observer has visibility to the state."""
    
    def verify_isolation(
        self,
        state_runtime_id: Optional[str],
        observer_runtime_id: Optional[str],
    ) -> Tuple[bool, Optional[str]]:
        """Verify isolation boundaries are respected."""
    
    def resolve_conflict(
        self,
        conflict_result: ConflictResult,
        retry_policy: Optional[RetryPolicy] = None,
        current_state_version: Optional[int] = None,
        current_state_generation: Optional[int] = None,
    ) -> AtomicOperationResult:
        """Apply resolution policy for a detected conflict."""
```

###Facade Invariants

**FACADE-001**: All operations are pure (no side effects)  
**FACADE-002**: No synchronization primitives exposed  
**FACADE-003**: Results are deterministic and reproducible  

---

## Import Policy

Importing consistency modules shall never:

- Execute mutations
- Create runtime state
- Acquire synchronization primitives
- Start background workers
- Allocate runtime resources

Remain **import-pure**.

---

## Legacy Policy

Legacy Gordon remains conceptual reference only. Do **not**:

- Import legacy locking systems
- Reuse legacy synchronization managers
- Preserve legacy concurrency helpers
- Introduce compatibility adapters

Extract concepts only. Reimplement natively.

---

## Testing Strategy

### Unit Tests

Implement comprehensive tests covering:

| Test Category | Coverage |
|---------------|----------|
| Optimistic concurrency | Expected version/generation checks |
| Version conflicts | Stale read detection |
| Generation conflicts | Ownership change detection |
| Ownership conflicts | Unauthorized mutation rejection |
| Conflict detection | All conflict types |
| Conflict resolution | Policy-driven handling |
| Retry policy | Backoff and budgeting |
| Visibility rules | Access control enforcement |
| Isolation rules | Boundary enforcement |
| Immutable observations | No partial state exposure |
| Consistency guarantees | Per-aggregate guarantees |

### Test Doubles

Use deterministic test doubles:

- Mock version generators (fixed sequences)
- Mock time source (monotonic clock)
- Fixed conflict resolution policies
- Predictable retry delays

Do **not** require actual multithreading. Behavioral concurrency semantics shall be verified independently of execution framework.

---

## Integration Points

Phase 3.15.8 integrates with:

| Phase | Integration Point |
|-------|-------------------|
| 3.15.1 | State identity and ownership foundation |
| 3.15.2 | Scope and visibility boundaries |
| 3.15.3 | Immutable/mutable state semantics |
| 3.15.4 | Runtime hierarchy constraints |
| 3.15.5 | Transition validation (version/generation checks) |
| 3.15.6 | Snapshot consistency classifications |
| 3.15.7 | Versioning and generation lineage |

Phase 3.20 (Concurrency Framework) shall **consume** these contracts rather than redefining them.

---

## Relationship to Phase 3.20

**Phase 3.15.8**: State-level concurrency model  
- Defines what constitutes a valid concurrent operation
- Establishes conflict detection and resolution policies
- Specifies visibility and isolation rules

**Phase 3.20**: Execution-level concurrency framework  
- Implements thread scheduling and executors  
- Provides synchronization primitives (mutexes, semaphores, etc.)
- Manages worker architecture and structured concurrency

Phase 3.20 consumes Phase 3.15.8 contracts as **validation rules**, not as implementation details.

---

## Public API Export Summary

### Phase 3.15.8 Exports:

```python
__all__ = [
    # CONSISTENCY MODELS (Phase 3.15.8)
    "ConsistencyModel",
    
    # OPTIMISTIC CONCURRENCY CONTROL (Phase 3.15.8)
    "ExpectedVersion",
    "ExpectedGeneration",
    
    # CONFLICT DETECTION & RESOLUTION (Phase 3.15.8)
    "ConflictType",
    "ConflictResolutionPolicy",
    "RetryPolicy",
    "ConflictResult",
    "AtomicOperationStatus",
    "AtomicOperationResult",
    
    # VISIBILITY & ISOLATION (Phase 3.15.8)
    "VisibilityLevel",
    "IsolationLevel",
    
    # PUBLIC API (Phase 3.15.8)
    "StateConcurrencyFacade",
]
```

---

## Completion Criteria

This phase is complete only when:

- [x] One canonical state consistency model exists
- [x] One canonical conflict model exists  
- [x] Ownership remains the basis for mutation
- [x] Optimistic concurrency is fully defined
- [x] Version and generation conflicts are detected
- [x] Conflict resolution is policy-driven
- [x] Immutable observations never expose partial mutations
- [x] Visibility and isolation rules are explicit
- [x] State-level concurrency contracts are independent of implementation mechanisms
- [x] No synchronization framework implemented in this phase (Phase 3.20)
- [x] Architecture ready for integration with Phase 3.20
- [ ] Documentation matches implementation
- [ ] Validation succeeds where executable

---

## References

- **Phase 3.15.1**: Core State Foundations
- **Phase 3.15.2**: State Identity, Scope & Ownership
- **Phase 3.15.3**: Immutable & Mutable State Semantics
- **Phase 3.15.4**: Runtime State Hierarchy
- **Phase 3.15.5**: State Transitions & Transition Validation
- **Phase 3.15.6**: State Snapshots & Views
- **Phase 3.15.7**: State Versioning & Generations
- **Phase 3.20** (Future): Core Concurrency & Synchronization Architecture

---

*Generated: Phase 3.15.8 — State Consistency & Concurrency Architecture*