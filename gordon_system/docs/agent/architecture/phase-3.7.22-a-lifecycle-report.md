# Gordon Lifecycle Report
## Phase 3.7.22-A Architecture Acceptance Audit

### Lifecycle Abstraction Location

**File**: `src/agent/components/core/lifecycle/__init__.py`

### States

```python
class LifecycleState(Enum):
    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
```

### Valid Transitions

```python
TRANSITIONS: Dict[LifecycleState, List[LifecycleState]] = {
    LifecycleState.CREATED: [
        LifecycleState.INITIALIZING,
        LifecycleState.FAILED,
    ],
    LifecycleState.INITIALIZING: [
        LifecycleState.READY,
        LifecycleState.FAILED,
    ],
    LifecycleState.READY: [
        LifecycleState.STARTING,
        LifecycleState.STOPPED,
        LifecycleState.FAILED,
    ],
    LifecycleState.STARTING: [
        LifecycleState.RUNNING,
        LifecycleState.STOPPING,
        LifecycleState.FAILED,
    ],
    LifecycleState.RUNNING: [
        LifecycleState.STOPPING,
        LifecycleState.FAILED,
    ],
    LifecycleState.STOPPING: [
        LifecycleState.STOPPED,
        LifecycleState.FAILED,
    ],
    LifecycleState.STOPPED: [
        LifecycleState.STARTING,  # Allow restart
        LifecycleState.FAILED,
    ],
    LifecycleState.FAILED: [],  # Terminal state
}
```

### Ownership

- **Controller**: `LifecycleController` manages transitions
- **Entity**: `EntityWithLifecycle` base class for lifecycle-managed entities
- **Locking**: Uses threading.Lock for thread-safe operations
- **Events**: Tracks all lifecycle events with timestamps and source/target states

### Lifecycle Controller Responsibilities

```python
class LifecycleController:
    def __init__(self, entity_id: EntityId) -> None:
        self._entity_id = entity_id
        self._state = LifecycleState.CREATED
        self._lock = threading.Lock()
        self._events: List[LifecycleEvent] = []
    
    @property def state(self) -> LifecycleState
    @property def failure_cause(self) -> Optional[Exception]
    @property def events(self) -> List[LifecycleEvent]
    
    async def initialize() -> None   # CREATED → INITIALIZING
    async def ready() -> None        # INITIALIZING → READY
    async def start() -> None        # READY → STARTING → RUNNING
    async def stop() -> None         # RUNNING → STOPPING → STOPPED
    async def shutdown() -> None     # Any state → STOPPED
```

### EntityWithLifecycle Base Class

```python
class EntityWithLifecycle:
    def __init__(self, entity_id: Optional[EntityId] = None) -> None:
        self._entity_id = entity_id or EntityId(str(uuid.uuid4()))
        self._controller = LifecycleController(self._entity_id)
    
    @property def state(self) -> LifecycleState
    @property def entity_id(self) -> EntityId
    
    async def initialize() -> None
    async def start() -> None
    async def stop() -> None
    async def shutdown() -> None
```

### Callbacks

Lifecycle events are recorded but not externally callable callbacks.
Events can be retrieved via `controller.events` for inspection.

### Validation

```python
def _validate_transition(self, target: LifecycleState) -> None:
    """Validate that a transition to the target state is allowed."""
    current = self.state
    
    # Idempotent operations - same state is always valid
    if current == target:
        return
    
    with self._lock:
        allowed = TRANSITIONS.get(current, [])
    
    if target not in allowed:
        raise LifecycleError(
            f"Invalid transition from {current.value} to {target.value}",
            from_state=current.value,
            to_state=target.value
        )
```

### Centralized Lifecycle Semantics

✅ VERIFIED: All lifecycle semantics are centralized in `lifecycle/__init__.py`.
The transitions dictionary is the single source of truth.