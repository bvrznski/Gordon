# Entrypoint Continuity

**Phase:** 3.7.36-I  
**Package:** `src.agent.entrypoint.continuity`

## Overview

Entrypoint continuity owns WHEN continuity operations occur. It orchestrates the integration between process lifecycle events and Core continuity infrastructure.

### Architecture Boundary

```
┌──────────────────────────────┐     ┌─────────────────────────────────┐
│ Entrypoint Continuity        │     │   Core Continuity               │
│                                │     │                                 │
│ WHEN operations occur:         │────►│ HOW they work:                  │
│   - Startup sequencing         │     │   - Checkpoint creation         │
│   - Shutdown finalization      │     │   - Restoration                 │
│   - Signal handling            │     │   - Reconciliation              │
│   - Checkpoint triggers        │     │   - Verification                │
└──────────────────────────────┘     └─────────────────────────────────┘
```

### Responsibility Split

| Entrypoint Continuity | Core Continuity |
|----------------------|-----------------|
| Detects previous runtime state | Manages checkpoint storage |
| Determines if recovery needed | Validates checkpoints |
| Calls restore before admission | Coordinates participant fragments |
| Finalizes during shutdown | Manages ledger records |

### Package Structure

```
src/agent/entrypoint/continuity/
├── __init__.py           # Public API exports
├── facade.py             # Entrypoint-facing operations
└── README.md             # This file
```

### Key Operations

| Operation | When Called | Purpose |
|-----------|-------------|---------|
| `inspect_previous_runtime()` | Process start | Detects if previous run was clean |
| `restore_if_needed()` | Startup, before admission | Restores from checkpoint |
| `request_checkpoint(reason)` | Scheduling/transition | Creates new checkpoint |
| `finalize_shutdown()` | Shutdown completion | Writes shutdown marker |

### Usage Example

```python
from src.agent.entrypoint.continuity import EntrypointContinuityFacade

facade = EntrypointContinuityFacade()

# Process startup sequence
success, prev_info = facade.initialize_runtime(generation_id="gen-123")
state = await facade.inspect_previous_runtime()

if state == "UNCLEAN_SHUTDOWN":
    # Recovery needed - restore before opening admission
    result = await facade.restore_if_needed()
    
# ... runtime runs ...

# Process shutdown sequence
shutdown_result = await facade.finalize_shutdown()
```

### Integration Points

The entrypoint continuity facade is integrated with:

1. **Startup Coordinator**: Calls `restore_if_needed()` before admission opens
2. **Shutdown Coordinator**: Calls `finalize_shutdown()` after components stopped
3. **Signal Handler**: Triggers `request_checkpoint("PRE_SHUTDOWN")` on SIGTERM
4. **Scheduling Service**: Triggers periodic checkpoints via `request_checkpoint()`

### Architecture Constraints

Entrypoint Continuity:
- ✓ Owns timing of operations (when)
- ✓ Detects previous runtime state
- ✓ Orchestrates Core continuity calls
- ✗ Does NOT create checkpoint storage logic
- ✗ Does NOT serialize participant state
- ✗ Does NOT determine what Gordon should remember

### Signal Handling

Signal handlers delegate to entrypoint continuity:

```python
# SIGTERM handler example
def handle_sigterm():
    # Request a final checkpoint
    asyncio.run(facade.request_checkpoint("PRE_SHUTDOWN"))
    
    # Shutdown intent is routed through canonical authority
```

The actual checkpoint creation and storage is delegated to Core Continuity.