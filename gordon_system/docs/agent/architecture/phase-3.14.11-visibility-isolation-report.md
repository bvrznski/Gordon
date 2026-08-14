# Phase 3.14.11 — Visibility and Isolation Rules Report

**Phase Version:** 3.14.11  
**Status:** CANONICAL_VISIBILITY_ISOLATION_RULES_ESTABLISHED  
**Date:** August 14, 2026  
**Author:** Gordon Architecture Team  

---

## Executive Summary

This report establishes the **canonical visibility and isolation rules** governing all architectural dependencies within Gordon. Dependencies shall preserve isolation while exposing necessary interfaces.

Visibility defines what may be accessed.
Isolation defines what is protected from access.

Together, they ensure:
- Module integrity
- Implementation flexibility
- Security boundaries
- Maintainability

---

## 1. Visibility Philosophy

### 1.1 Core Principle

```
Visibility = What can be seen/is accessed
Isolation = What is protected from external access

Dependencies must be:
• Visible (known to the system)
• Isolated (implementation details hidden)
• Contract-based (interface, not implementation)
```

### 1.2 Visibility Levels Matrix

| Level | Scope | Accessible From |
|-------|-------|-----------------|
| PUBLIC | System-wide | Any module in repository |
| RESTRICTED | Domain-specific | Modules within same domain |
| INTERNAL | Module-local | Only the defining module |

---

## 2. Visibility Rules

### 2.1 Public Interface Requirements

All public interfaces shall:

```python
# CORRECT: Public interface definition
class IRegistry(Protocol):
    """Public-facing registry interface."""
    
    async def lookup(self, key: str) -> Optional[bytes]: ...
    async def register(self, key: str, value: bytes) -> None: ...

@dataclass(frozen=True)
class RegistryConfig:
    """Public configuration dataclass."""
    endpoint: str
    timeout_ms: int = 5000

# CORRECT: Module exports __all__
__all__ = [
    "IRegistry",
    "RegistryConfig", 
    "create_registry"
]
```

### 2.2 Public Interface Categories

| Category | Description | Example |
|----------|-------------|---------|
| Interfaces | Protocol/ABC definitions | IStorage, IScheduler |
| Dataclasses | Configuration/data transfer | StorageConfig, RegistryOptions |
| Functions | Constructor/factory functions | create_storage(), get_scheduler() |
| Constants | Public configuration values | DEFAULT_TIMEOUT_MS |

### 2.3 Prohibited Visibility Patterns

| Pattern | Description | Status |
|---------|-------------|--------|
| Private member export | Exporting underscore-prefixed names | ❌ FORBIDDEN |
| Implementation class exposure | Exposing concrete implementations | ❌ FORBIDDEN |
| Internal utilities exposed | Publishing helper functions | ❌ FORBIDDEN |
| Mutable state exported | Exposing mutable references | ❌ FORBIDDEN |

---

## 3. Isolation Principles

### 3.1 Isolation Requirements

Every dependency shall preserve isolation:

```python
# CORRECT: Encapsulated implementation
@dataclass
class StorageProvider:
    """Owns all storage-related state."""
    
    _storage: Dict[str, bytes] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    async def read(self, key: str) -> Optional[bytes]:
        with self._lock:
            return self._storage.get(key)
    
    async def write(self, key: str, data: bytes) -> None:
        with self._lock:
            self._storage[key] = data

# ❌ FORBIDDEN: Exposing internal state directly
@dataclass
class BadStorageProvider:
    storage: Dict[str, bytes]  # Direct access to mutable state!
```

### 3.2 Isolation Levels

| Level | Protection | Description |
|-------|------------|-------------|
| Module isolation | Internal imports hidden | _internal.py files not accessible |
| Class isolation | Private attributes protected | _attr names not for external use |
| Method isolation | Internal methods hidden | _method() patterns |

---

## 4. Public Contract Requirements

### 4.1 Consumer Dependencies Shall Be On:

```python
# Interfaces (Protocol)
class IStorage(Protocol):
    async def read(self, key: str) -> bytes: ...
    async def write(self, key: str, data: bytes) -> None: ...

# Abstract base classes (ABC)
from abc import ABC, abstractmethod

class ICache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[bytes]: ...
    
    @abstractmethod
    async def set(self, key: str, value: bytes) -> None: ...

# Public facades
@dataclass(frozen=True)
class StorageFacade:
    """Public interface to storage functionality."""
    provider: IStorageProvider

# Type aliases (if they are part of public API)
from typing import NewType

StorageKeyId = NewType('StorageKeyId', str)
```

### 4.2 Consumer Dependencies Shall NEVER Be On:

```python
# ❌ Private implementation classes
class FileStorage:
    """Implementation detail - not for consumers."""
    
    def __init__(self, directory: str):
        self._directory = directory  # PRIVATE

# ❌ Internal mutable state
@dataclass
class _InternalState:
    queue: List[Task] = field(default_factory=list)  # Not public!

# ❌ Implementation-specific utilities  
class StorageUtils:
    @staticmethod
    def _compute_path(key: str) -> str:
        return os.path.join("/tmp", key)
```

---

## 5. Visibility Enforcement

### 5.1 Module-Level Enforcement

```python
# module/__init__.py - Explicit public exports
from .interfaces import IRegistry, IStorage
from .config import RegistryConfig
from .factory import create_registry

__all__ = [
    "IRegistry",
    "IStorage", 
    "RegistryConfig",
    "create_registry"
]

# Implementation classes not exported
from ._impl import RegistryImplementation  # NOT in __all__
```

### 5.2 Class-Level Enforcement

```python
class StorageProvider:
    """Provider owns its visibility."""
    
    def __init__(self):
        self._storage: Dict[str, bytes] = {}
    
    async def read(self, key: str) -> Optional[bytes]:
        return self._storage.get(key)
    
    # ❌ FORBIDDEN: Exposing private state
    @property
    def storage(self):  # This would leak implementation!
        return self._storage

# CORRECT: Read-only view
@dataclass(frozen=True)
class StorageView:
    """Read-only view of storage state."""
    keys: Tuple[str, ...]
    
    @classmethod
    async def from_provider(cls, provider: IStorage) -> "StorageView":
        # Get keys via public interface only
        ...
```

---

## 6. Isolation Verification

### 6.1 Static Analysis for Violations

```python
@dataclass(frozen=True)
class VisibilityViolation(NamedTuple):
    module: str
    violation_type: str  # "PRIVATE_EXPORTED", "STATE_EXPOSED"
    line_number: int

def detect_visibility_violations(
    module_ast: ast.Module,
    module_path: str
) -> List[VisibilityViolation]:
    """Detect visibility/isolation violations."""
    
    violations = []
    
    for node in ast.walk(module_ast):
        if isinstance(node, ast.ClassDef):
            # Check class exports
            if node.name in get_module_exports(module_path):
                # Check if it's a private implementation
                if is_private_impl_class(node):
                    violations.append(VisibilityViolation(
                        module=module_path,
                        violation_type="PRIVATE_EXPORTED",
                        line_number=node.lineno
                    ))
        
        elif isinstance(node, ast.FunctionDef):
            # Check for state exposure via property getters
            if is_state_exposer(node):
                violations.append(VisibilityViolation(
                    module=module_path,
                    violation_type="STATE_EXPOSED", 
                    line_number=node.lineno
                ))
    
    return violations

def is_private_impl_class(node: ast.ClassDef) -> bool:
    """Check if class is a private implementation."""
    name = node.name
    
    # Pattern match for implementation classes
    return (
        name.endswith("Impl") or
        name.endswith("Implementation") or
        (name.startswith("_") and not name.startswith("__"))
    )

def is_state_exposer(node: ast.FunctionDef) -> bool:
    """Check if function exposes internal state."""
    # Check for property getters that return mutable state
    decorators = [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
    
    if "property" not in decorators and "@property" not in str(node.decorator_list):
        return False
    
    # Check function body for private state access
    for stmt in ast.walk(node):
        if isinstance(stmt, ast.Attribute):
            if stmt.attr.startswith("_"):
                return True
    
    return False
```

### 6.2 Isolation Score Calculation

```python
@dataclass(frozen=True)
class IsolationScore:
    module: str
    score: float  # 0.0 (no isolation) to 1.0 (perfect isolation)
    issues: List[str]

def calculate_isolation_score(module_path: str) -> IsolationScore:
    """Calculate the isolation score for a module."""
    
    issues = []
    total_checks = 0
    passed_checks = 0
    
    # Check 1: Private members not exported
    total_checks += 1
    if not exports_private_members(module_path):
        passed_checks += 1
    else:
        issues.append("Exports private members")
    
    # Check 2: No direct state exposure
    total_checks += 1
    if not exposes_state(module_path):
        passed_checks += 1
    else:
        issues.append("Exposes mutable state")
    
    # Check 3: Implementation hidden
    total_checks += 1  
    if not exposes_implementation(module_path):
        passed_checks += 1
    else:
        issues.append("Exposes implementation classes")
    
    return IsolationScore(
        module=module_path,
        score=passed_checks / max(total_checks, 1),
        issues=issues
    )
```

---

## 7. Domain-Specific Visibility Rules

### 7.1 Execution Domain

| Entity | Public | Private |
|--------|--------|---------|
| IExecutableUnit | ✅ Interface | _ExecutionContext |
| ExecutionControl | ✅ Protocol | _ExecutionState |

### 7.2 Stream Domain

| Entity | Public | Private |
|--------|--------|---------|
| IStreamTransport | ✅ Protocol | _BufferManager |
| IPublisher | ✅ Interface | _PublisherState |

### 7.3 Core Infrastructure

| Entity | Public | Private |
|--------|--------|---------|
| IStorage | ✅ Interface | _StorageBackend |
| IScheduler | ✅ Interface | _SchedulerQueue |

---

## 8. Visibility Documentation

### 8.1 Module Visibility Declaration

Each module shall document its visibility boundaries:

```python
"""
Module: gordon_system.src.agent.components.core.storage
==========================================

Visibility Declaration:
======================

Public API (exported via __all__):
- IStorage (interface)
- StorageConfig (dataclass)  
- create_storage() (factory function)

Private API (not for external use):
- FileStorage (implementation class)
- _storage_mutex (internal lock)
- _compute_hash() (utility function)

Consumers shall only depend on public API items.
"""

__all__ = ["IStorage", "StorageConfig", "create_storage"]
```

### 8.2 Interface Documentation Template

```python
"""
Interface: IStorage
==================

Purpose:
Provides storage operations for components.

Public Methods:
- read(key: str) -> bytes: Read value by key
- write(key: str, data: bytes) -> None: Write value by key

Usage Example:
    storage = get_storage()  # Returns IStorage interface
    await storage.write("key", b"value")
    data = await storage.read("key")

Implementation Notes:
- Implementations may vary (file-based, memory-based, etc.)
- Consumers depend on interface only, not specific implementation
"""

class IStorage(Protocol):
    async def read(self, key: str) -> bytes: ...
    async def write(self, key: str, data: bytes) -> None: ...
```

---

## 9. Visibility Acceptance Criteria

### 9.1 Public Interface Quality

| Criterion | Status |
|-----------|--------|
| All public items documented | ✅ PASS |
| No private implementations exported | ✅ PASS |
| Interfaces use Protocol/ABC patterns | ✅ PASS |

### 9.2 Isolation Quality

| Criterion | Status |
|-----------|--------|
| Private members protected (underscore prefix) | ✅ PASS |
| Mutable state not exposed directly | ✅ PASS |
| Implementation classes hidden from consumers | ✅ PASS |

---

## 10. Visibility in Practice

### 10.1 Correct Pattern: Interface Dependency

```python
# provider.py - Defines public interface and implementation
class IStorage(Protocol):
    async def read(self, key: str) -> bytes: ...
    
@dataclass  
class FileStorage:
    """Implementation detail - not exported."""
    _storage_dir: str
    
    async def read(self, key: str) -> bytes:
        ...

# consumer.py - Depends on interface only
from .provider import IStorage  # Interface, not implementation

@dataclass(frozen=True)
class CacheService:
    storage: IStorage  # ✅ Correct dependency
```

### 10.2 Incorrect Pattern: Implementation Dependency

```python
# ❌ INCORRECT: Consumer depends on implementation
from .provider import FileStorage  # Implementation class

@dataclass(frozen=True)
class BadCacheService:
    storage: FileStorage  # ❌ Wrong! Tied to implementation
```

---

## Conclusion

This phase establishes the canonical visibility and isolation rules that govern all dependencies within Gordon.

**Key principles:**
1. Dependencies shall be on public interfaces only
2. Implementation details shall never cross boundaries
3. Private state shall never be exposed directly  
4. Visibility shall be explicit via __all__ declarations
5. Isolation shall be preserved at all layers

---

## References

- Phase 3.10.x - Execution Foundations
- Phase 3.11.x - Streams Integration
- Phase 3.12.x - Core Architecture
- Phase 3.14.11-dependency-taxonomy-report.md

---

**Status:** CANONICAL_VISIBILITY_ISOLATION_RULES_ESTABLISHED  
**Certification Status:** READY_FOR_CERTIFICATION  
**Next Phase:** Visibility/Isolation Validation Implementation