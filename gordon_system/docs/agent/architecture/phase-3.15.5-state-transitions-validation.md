# State Transitions & Validation - Phase 3.15.5
# ===============================================

**Phase**: 3.15.5  
**Status**: Draft Implementation  
**Date**: 2026  

## Executive Summary

This phase establishes the canonical architecture for state transitions throughout the Gordon Core. Every mutable state transition is represented explicitly as an immutable record with full lifecycle tracking, validation, and observability.

### Key Achievements

- One canonical transition architecture across the entire Core
- Explicit, deterministic, validated transitions
- Full lifecycle: Request → Validation → Execution → Result → History
- Policy-driven validation with explicit pre/post conditions
- Atomic execution with rollback/compensation support
- Bounded history tracking for diagnostics and auditing

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STATE TRANSITION ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────┘

Transition Lifecycle:

  +-------------+     +------------------+     +------------------+
  |   Request   │ ──> │   Validation     │ ──> │    Execution     │
  +-------------+     +------------------+     +------------------+
         |                    |                        |
         v                    v                        v
  +-------------+     +------------------+     +------------------+
  | Transition  │     │ Findings &       │     │ Result Code      │
  | ID / Policy │     │ Outcome          │     │ State Change     │
  +-------------+     +------------------+     +------------------+
                                                   |
                                                   v
                                            +------------------+
                                            │  History Entry   │
                                            └──────────────────┘

Transition Types:
  - CREATE, INITIALIZE    (Creation transitions)
  - ACTIVATE, DEACTIVATE  (Activation transitions)  
  - PAUSE, RESUME         (Control transitions)
  - REPLACE, UPGRADE      (Replacement transitions)
  - RESTORE, RECONCILE    (Recovery transitions)
  - MIGRATE, RETIRE       (Migration transitions)
  - SHUTDOWN, DELETE      (Termination transitions)

Validation Layers:
  1. Policy validation (source/destination states)
  2. Authority validation (ownership and authorization)
  3. Version/generation validation
  4. Scope compatibility validation
  5. Invariant preservation validation

Recovery Mechanisms:
  - Rollback to previous state on failure
  - Compensation for irreversible operations
  - Retry with exponential backoff
  - Bounded history for diagnostics
```

## Transition Identity and Types

### TransitionType Enum

```python
class TransitionType(Enum):
    # Creation transitions
    CREATE = "create"
    INITIALIZE = "initialize"
    
    # Activation transitions
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    
    # Control transitions  
    PAUSE = "pause"
    RESUME = "resume"
    
    # Replacement transitions
    REPLACE = "replace"
    UPGRADE = "upgrade"
    
    # Recovery transitions
    RESTORE = "restore"
    RECONCILE = "reconcile"
    
    # Migration transitions
    MIGRATE = "migrate"
    RETIRE = "retire"
    
    # Termination transitions
    SHUTDOWN = "shutdown"
    DELETE = "delete"
```

### Transition Request Structure

```python
@dataclass(frozen=True)
class TransitionRequest:
    transition_id: str                      # Unique identifier
    source_state: str                       # Current state before transition
    destination_state: str                  # Target state after transition
    aggregate_id: str                       # Target aggregate ID
    authority: str                          # Who requests the transition
    transition_type: TransitionType         # Type of transition
    created_at_utc: float                   # Timestamp
    expected_version: Optional[Version]     # For validation
    expected_generation: Optional[int]      # For validation
```

## Transition Policies

### Policy Structure

```python
@dataclass(frozen=True)
class TransitionPolicy:
    transition_type: TransitionType
    
    allowed_source_states: Tuple[str, ...]
    allowed_destination_states: Tuple[str, ...]
    
    required_authority_types: Tuple[str, ...]
    timeout_seconds: Optional[float]
    
    retry_policy: TransitionRetryPolicy
    rollback_enabled: bool
    compensation_required: bool
```

### Policy Example

```python
# Create transition policy
policy = TransitionPolicy(
    transition_type=TransitionType.CREATE,
    allowed_source_states=("nonexistent",),
    allowed_destination_states=("created", "initializing"),
    required_authority_types=("exclusive_mutation",),
    timeout_seconds=30.0,
)
```

## Validation Model

### Validation Outcome Enum

```python
class ValidationOutcome(Enum):
    VALID = "valid"
    INVALID_SOURCE = "invalid_source"
    INVALID_DESTINATION = "invalid_destination"
    VERSION_MISMATCH = "version_mismatch"
    GENERATION_MISMATCH = "generation_mismatch"
    AUTHORIZATION_FAILED = "authorization_failed"
    OWNERSHIP_FAILED = "ownership_failed"
    SCOPE_VIOLATION = "scope_violation"
    TIMEOUT_PENDING = "timeout_pending"
    DEPENDENCY_UNREADY = "dependency_unready"
    INVARIANT_VIOLATED = "invariant_violated"
```

### Validation Result Structure

```python
@dataclass(frozen=True)
class ValidationResult:
    outcome: ValidationOutcome
    transition_id: str
    validation_started_at_utc: float
    validation_completed_at_utc: Optional[float]
    findings: Tuple[str, ...]
    
    @property
    def is_valid(self) -> bool:
        return self.outcome == ValidationOutcome.VALID
    
    @property
    def validation_duration_seconds(self) -> Optional[float]:
        if self.validation_completed_at_utc is None:
            return None
        return self.validation_completed_at_utc - self.validation_started_at_utc
```

## Execution Model

### Result Code Enum

```python
class TransitionResultCode(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL_FAILURE = "partial_failure"
    CONFLICT_DETECTED = "conflict_detected"
    TIMEOUT = "timeout"
    ROLLED_BACK = "rolled_back"
```

### Execution Result Structure

```python
@dataclass(frozen=True)
class TransitionExecutionResult:
    transition_id: str
    result_code: TransitionResultCode
    execution_started_at_utc: float
    execution_completed_at_utc: Optional[float]
    
    # For success
    destination_state: Optional[str] = None
    new_version_sequence: int = 0
    
    # For failures
    failure_reason: Optional[str] = None
    partial_commit_status: bool = False
    
    # Recovery
    rollback_performed: bool = False
```

## History Management

### History Entry Structure

```python
@dataclass(frozen=True)
class TransitionHistoryEntry:
    history_sequence: int                   # Monotonic within instance
    transition_id: str
    timestamp_utc: float
    source_state: str
    destination_state: Optional[str]
    initiating_authority: str
    validation_outcome: ValidationOutcome
    execution_result_code: TransitionResultCode
    
    version_before_sequence: int
    generation_before: int
    
    findings: Tuple[str, ...]
    provenance: Dict[str, str]
```

### History Container

```python
@dataclass(frozen=True)
class TransitionHistory:
    aggregate_id: str
    max_entries: int = 1000                 # Configurable bound
    
    def append(self, entry: TransitionHistoryEntry) -> "TransitionHistory":
        """Append new entry, pruning oldest if necessary."""
    
    def get_latest(self) -> Optional[TransitionHistoryEntry]:
        """Get the most recent entry."""
```

## Diagnostics Module

### Metrics Collection

```python
class TransitionMetrics:
    total_executed: int
    successful: int
    failed: int
    partial_failure: int
    validation_rejected: int
    
    rolled_back: int
    compensated: int
    timeout_count: int
    
    conflict_detected: int
    
    # Methods to record events
    def record_success(self) -> "TransitionMetrics"
    def record_failure(self) -> "TransitionMetrics"
```

### Diagnostic Snapshot

```python
@dataclass(frozen=True)
class TransitionDiagnosticsSnapshot:
    metrics: TransitionMetrics
    average_validation_duration_seconds: Optional[float]
    average_execution_duration_seconds: Optional[float]
    
    total_transitions_in_history: int
    recent_transitions: Tuple[str, ...]
```

## Public API

### Factory Pattern

```python
class TransitionFactory:
    """Factory for creating transitions with validation and identity."""
    
    def register_policy(self, policy: TransitionPolicy) -> None
    def get_policy(self, transition_type: TransitionType) -> Optional[TransitionPolicy]
    
    def create_transition_request(
        self,
        source_state: str,
        destination_state: str,
        aggregate_id: str,
        authority: str,
        transition_type: TransitionType,
    ) -> TransitionRequest
    
    def execute_transition(
        self, 
        request: TransitionRequest,
    ) -> TransitionExecutionResult
```

### Validator

```python
class TransitionValidator:
    """Validator for transitions."""
    
    def validate_request(self, request: TransitionRequest) -> ValidationResult:
        """Validate a transition request and return structured findings."""
```

## Rollback & Compensation

### Recovery Modes

- **FULL**: Complete restoration to known state
- **PARTIAL**: Restore only affected components  
- **COMPENSATING**: Apply counteracting actions (not exact rollback)
- **CHECKPOINT**: Restore from named checkpoint

### Compensation Pattern

```python
@dataclass(frozen=True)
class CompensationAction:
    action_id: str
    action_type: CompensationType  # RESTORE, DELETE, REVERT, etc.
    target_entity: Optional[str]
    parameters: Dict[str, Any]
```

## Invariants and Constraints

### Transition Invariants (TRA-INV)

| ID | Invariant Description |
|----|----------------------|
| TRA-001 | Every transition has exactly one unique identifier |
| TRA-002 | Transitions are immutable once created |
| TRA-003 | Source state must be in policy's allowed_source_states |
| TRA-004 | Destination state must be in policy's allowed_destination_states |
| TRA-005 | Version/generation must match expected values (if specified) |
| TRA-006 | Authority must have required authority types |
| TRA-007 | Scope compatibility must be validated |
| TRA-008 | Runtime isolation must be enforced |
| TRA-009 | Invariants must be preserved after transition |
| TRA-010 | Atomicity: either complete or fail without partial state |

### Illegal Transitions (Rejected)

The architecture rejects:

- Invalid source state for the transition type
- Invalid destination state for the transition type  
- Stale versions (version mismatch)
- Stale generations (generation mismatch)
- Unauthorized transitions (authority validation fails)
- Cross-runtime transitions (runtime isolation violation)
- Hierarchy violations
- Ownership violations
- Dependency violations
- Invariant violations
- Cyclic transitions
- Duplicate transitions

## Testing Strategy

### Test Categories

1. **Legal Transitions**: Verify valid state transitions work correctly
2. **Illegal Transitions**: Verify invalid transitions are rejected
3. **Ownership Validation**: Verify ownership is enforced
4. **Authorization**: Verify authorization requirements
5. **Version Conflicts**: Verify version/generation validation
6. **Transition Policies**: Verify policy enforcement
7. **Preconditions**: Verify pre-condition checks
8. **Postconditions**: Verify post-condition checks
9. **Invariant Preservation**: Verify invariants after transition
10. **Rollback**: Verify rollback functionality
11. **Compensation**: Verify compensation actions
12. **Retry**: Verify retry mechanisms
13. **History**: Verify history tracking
14. **Diagnostics**: Verify observability

## Documentation Files

- `phase-3.15.5-state-transitions-validation.md` (this file)
- `src/agent/components/core/state/transitions/__init__.py`
- `src/agent/components/core/state/transitions/diagnostics.py`

## Completion Criteria

This phase is complete when:

- [x] One canonical transition architecture exists
- [x] Transition execution is deterministic
- [x] Every transition is explicitly validated
- [ ] Ownership and authorization are enforced
- [ ] Illegal transitions are rejected
- [ ] Transition policies govern execution
- [ ] Version and generation integrity are preserved
- [ ] Rollback and compensation are explicit
- [ ] Transition history is bounded
- [ ] Diagnostics expose transition behavior without exposing mutable state
- [ ] Public APIs remain immutable
- [ ] No duplicate transition framework exists within the repository
- [ ] Documentation matches implementation
- [ ] Validation succeeds where executable

## Future Work

1. Implement actual transition execution logic (currently stub)
2. Add rollback and compensation handlers
3. Integrate with persistence layer for history storage
4. Implement retry mechanisms with exponential backoff
5. Add more comprehensive policy definitions per subsystem
6. Create concrete executor implementations

## References

- Phase 3.15.1 - Core State Foundations
- Phase 3.15.2 - State Identity, Scope & Ownership
- Phase 3.15.3 - Immutable & Mutable State Semantics
- Phase 3.15.4 - Runtime State Hierarchy