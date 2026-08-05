# Phase 3.8.12 - Architecture Decision Records

## Overview

This document records key architectural decisions made during interface design.

---

## ADR 001: Protocol-Based Interfaces

**Status:** ACCEPTED  
**Date:** 2026-08-06

### Problem
Python doesn't have native interface types. We need a way to define behavioral contracts without forcing implementation inheritance.

### Solution
Use `typing.Protocol` for runtime-checkable interfaces:
```python
from typing import Protocol

class IEventBus(Protocol):
    async def publish(self, envelope: EventEnvelope) -> bool:
        ...
```

### Rationale
- Python 3.8+ supports Protocol natively
- Protocol is checked at type time, not runtime
- No inheritance required - duck-typing compatible
- Works with mypy and other type checkers

### Alternatives Considered
1. **abc.ABC** - Requires inheritance, too restrictive
2. **Documentation only** - No type checking possible
3. **Interface classes** - Python 3.8+ Protocol is cleaner

---

## ADR 002: One Responsibility Per Interface

**Status:** ACCEPTED  
**Date:** 2026-08-06

### Problem
Some existing interfaces have too many responsibilities (e.g., MessageBus).

### Solution
Split large interfaces into focused ones:
- `IEventPublisher` - Only publish operations
- `IEventSubscriber` - Only subscribe operations  
- `IEventBus` - Combines both for convenience

### Rationale
- Each interface has a single responsibility
- Consumers depend on the smallest interface they need
- Easier to test and mock individual concerns

---

## ADR 003: Immutable Data Structures

**Status:** ACCEPTED  
**Date:** 2026-08-06

### Problem
Mutable interfaces can cause unexpected side effects in async code.

### Solution
Use frozen dataclasses for all contract data structures:
```python
@dataclass(frozen=True)
class EventEnvelope:
    event_id: str
    timestamp_utc: float
    ...
```

### Rationale
- Thread-safe by default
- Easier reasoning about behavior
- Prevents accidental mutation

---

## ADR 004: Async Methods Only

**Status:** ACCEPTED  
**Date:** 2026-08-06

### Problem
Some interfaces need to support both sync and async implementations.

### Solution
All interface methods are async. Implementations can be:
```python
# Sync implementation using thread pool
async def publish(self, envelope: EventEnvelope) -> bool:
    return await asyncio.get_event_loop().run_in_executor(
        self._thread_pool, 
        lambda: self._do_sync_publish(envelope)
    )
```

### Rationale
- Simpler interface (no sync/async variants)
- Async is more flexible than sync
- Better for distributed systems

---

## ADR 005: No Implementation Dependencies in Interfaces

**Status:** ACCEPTED  
**Date:** 2026-08-06

### Problem
Interfaces importing implementation types creates tight coupling.

### Solution
- Interfaces depend only on Python standard types
- Implementations import interface and extend it
- Use type hints for dependency injection

---

## ADR 006: Versioning by Core Release

**Status:** ACCEPTED  
**Date:** 2026-08-06

### Problem
Interfaces need to be versioned with the system.

### Solution
All interfaces are versioned with core release (currently 3.8.12).

Breaking changes require major version bump.
Non-breaking additions can use minor version.

---

## Decision Log

| ADR | Decision | Date | Status |
|-----|----------|------|--------|
| 001 | Protocol-based interfaces | 2026-08-06 | ACCEPTED |
| 002 | One responsibility per interface | 2026-08-06 | ACCEPTED |
| 003 | Immutable data structures | 2026-08-06 | ACCEPTED |
| 004 | Async methods only | 2026-08-06 | ACCEPTED |
| 005 | No implementation dependencies | 2026-08-06 | ACCEPTED |
| 006 | Versioning by core release | 2026-08-06 | ACCEPTED |

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Architecture decisions documented | ✅ 6 ADRs recorded |
| Rationale provided | ✅ For each decision |
| Alternatives considered | ✅ Documented |

---