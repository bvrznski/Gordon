# Core Continuity Infrastructure

**Phase:** 3.7.36-I  
**Package:** `src.agent.components.core.continuity`

## Overview

Core continuity infrastructure provides the foundation for checkpoint-based crash recovery.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│ Entrypoint Continuity (when operations occur)      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Core Continuity Facade                             │
│   - inspect_previous_runtime()                      │
│   - create_checkpoint()                             │
│   - restore()                                       │
│   - verify()                                        │
│   - finalize()                                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Continuity Coordinator                             │
│   - Collects fragments from participants            │
│   - Coordinates checkpoint transactions             │
│   - Orchestrates restoration                        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Continuity Participant Contracts                    │
│   - Lifecycle, Scheduler, Action Runtime, etc.      │
└─────────────────────────────────────────────────────┘
```

### Package Structure

```
src/agent/components/core/continuity/
├── __init__.py           # Public API exports
├── contracts.py          # ContinuityParticipant protocol
├── types.py              # Types and enums
├── exceptions.py         # Exception hierarchy
├── config.py             # Configuration
├── facade.py             # Public facade (checkpoint, restore)
├── registry.py           # Participant registration
├── coordinator.py        # Checkpoint/restore coordination
└── README.md             # This file
```

### Key Components

| Component | Responsibility |
|-----------|----------------|
| `ContinuityParticipant` | Protocol for subsystem state capture/restoration |
| `CheckpointFragment` | Immutable captured state with metadata |
| `RestorationResult` | Result of participant restoration |
| `ContinuityFacade` | Public API entry point |
| `ContinuityCoordinator` | Transaction orchestration |

### Ownership Split

- **Entrypoint Continuity**: When operations occur (startup/shutdown/trigger timing)
- **Core Continuity**: How checkpoints, ledgers, restoration work
- **Subsystems**: Own their fragment state semantics

### Usage Example

```python
from src.agent.components.core.continuity import (
    ContinuityFacade,
    ContinuityConfig,
)

config = ContinuityConfig()
facade = ContinuityFacade(config=config)

# Check if recovery is needed
state = await facade.inspect_previous_runtime(request)
if state.is_recovery_needed:
    result = await facade.restore(restore_request)
    
    # Verify restored state before opening admission
    verification = await facade.verify(verification_request)
```

### Architecture Boundaries

Core Continuity owns:
- Checkpoint transaction protocol
- Fragment collection and validation
- Restoration planning and coordination
- Ledger record structure and ordering

Core Continuity does NOT own:
- When continuity operations occur (entrypoint's responsibility)
- Subsystem-specific state semantics
- Live runtime object serialization

### Integration Points

Subsystems participate by implementing `ContinuityParticipant`:

```python
class MySubsystem(ContinuityParticipant):
    @property
    def participant_id(self) -> ParticipantId:
        return ParticipantId("my-subsystem")
    
    async def prepare_checkpoint(...) -> CheckpointFragment:
        # Capture state reference, not live object
    
    async def restore_checkpoint(...) -> RestorationResult:
        # Restore from fragment