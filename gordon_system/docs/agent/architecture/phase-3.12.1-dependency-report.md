# Phase 3.12.1 — Dependency Report

**Date:** August 13, 2026  
**Phase:** 3.12.1 - Core Architecture Consolidation  
**Status:** DEPENDENCY_DEFINED

---

## 1. Executive Summary

This report defines the dependency direction principles for Gordon Core architecture.

Dependencies always flow toward reusable infrastructure; never away from it.

---

## 2. Dependency Overview

### 2.1 Dependency Principle

> **Dependencies always flow toward reusable infrastructure.**

```
Semantic Implementations → Core (dependencies)
Core ↛ Semantic Implementations (no reverse dependency)
```

### 2.2 Architecture Layers with Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    SEMANTIC LAYERS                          │
│         Depends ON: Core infrastructure                     │
├─────────────────────────────────────────────────────────────┤
│                      CORE                                   │
│   Runtime, Execution, Streams, Lifecycle, Reflection        │
│         Provides infrastructure to semantic layers          │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Dependency Matrix (Canonical)

| From Layer | To Layer | Dependency Type | Direction |
|------------|----------|-----------------|-----------|
| Semantic Execution | Core Runtime | Uses | → |
| Semantic Streams | Core Streams | Uses | → |
| Semantic Reflection | Core Reflection | Uses | → |
| Semantic Integrity | Core Integrity | Uses | → |

---

## 4. Core Dependencies (Self)

Core components may depend on each other:

| Component | Depends On | Reason |
|-----------|------------|--------|
| Runtime | Resource Manager | Memory/CPU allocation |
| Streams | Storage Interface | Record persistence |
| Lifecycle | State Machine Definitions | State definitions |
| Integrity | Registry | Entity lookup |

---

## 5. Forbidden Dependencies (Anti-Patterns)

### 5.1 Reverse Dependencies

| From Layer | To Layer | Status | Reason |
|------------|----------|--------|--------|
| Core | Semantic Execution | ❌ FORBIDDEN | Violates dependency direction |
| Core | Semantic Streams | ❌ FORBIDDEN | Violates dependency direction |
| Core | Semantic Reflection | ❌ FORBIDDEN | Violates dependency direction |

### 5.2 Circular Dependencies

| Scenario | Status | Reason |
|----------|--------|--------|
| Core ↔ Semantic Execution | ❌ FORBIDDEN | Circular dependency |
| Streams ↔ Stream Publisher | ⚠️ DISCOURAGED | Should use interfaces only |

---

## 6. Dependency Verification

### 6.1 Dependency Checklist

| Check | Status |
|-------|--------|
| Dependencies flow toward Core infrastructure | ✅ |
| No reverse dependencies from Core to semantic | ✅ |
| Circular dependencies absent | ✅ |
| Dependencies through contracts, not implementations | ✅ |

### 6.2 Dependency Invariants

| Invariant ID | Invariant | Status |
|--------------|-----------|--------|
| DI-001 | Dependencies flow toward reusable infrastructure | ✅ |
| DI-002 | Core never depends on semantic implementations | ✅ |
| DI-003 | No circular dependencies | ✅ |

---

## 7. Dependency Patterns

### 7.1 Correct Pattern: Semantic → Core

```python
# Correct: Semantic uses Core through contracts
from src.agent.components.core.lifecycle import (
    ThreadLifecycleState,
)
from src.agent.components.core.streams import (
    StreamId,
)

class MySemanticThread:
    def __init__(self, lifecycle, streams):
        self.lifecycle = lifecycle  # Core infrastructure
        self.streams = streams      # Core infrastructure
    
    async def run(self):
        # Uses Core state machine definitions
        # Uses Core stream transport
```

### 7.2 Correct Pattern: Interface-Based Dependencies

```python
# Correct: Dependencies through interfaces, not implementations
from abc import ABC, abstractmethod
from src.agent.components.core.lifecycle import ThreadLifecycleState

class LifecyclePort(ABC):
    @abstractmethod
    async def commit_transition(self, transition): pass

class MySemanticThread:
    def __init__(self, lifecycle_port: LifecyclePort):
        self.port = lifecycle_port  # Interface dependency
    
    async def run(self):
        # Uses interface, not implementation details
```

---

## 8. Dependency Certification

### 8.1 Criteria for Dependency Certification

Dependencies shall be certified when:

1. Dependencies flow toward reusable infrastructure only
2. Core never depends on semantic implementations
3. No circular dependencies exist
4. Dependencies use interfaces, not concrete implementations

---

**Status:** DEPENDENCY_DEFINED  
**Certification Status:** DEPENDENCY_VALIDATED  
**Next Phase:** 3.12.2 - Implementation Validation