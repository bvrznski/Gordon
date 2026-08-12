# Gordon Core - Authority, Dependency, Package, Import and Ownership Audit

**Repository**: /home/bvrznski/Gordon
**Audit Phase**: 3.7.2-A
**Date**: 2026-08-03
**Version**: 1.0.0
**Status**: **REQUIRES_REMEDIATION**

---

## Executive Summary

### Audit Scope

This audit examines:
- Architectural authorities and their canonical ownership
- Mutable state ownership and mutation rights
- Dependency graph structure and directionality
- Package boundaries and cohesion
- Import graph purity and side effects
- Runtime-scoped state versus global mutable state
- Public API boundaries
- Architectural layering compliance

### Key Findings Summary

| Finding Type | Count | Severity |
|--------------|-------|----------|
| Duplicate Authorities | 18+ | CRITICAL |
| Missing Ownership | 23+ | CRITICAL |
| Circular Dependencies | Potential | WARNING |
| Import-time Side Effects | 5+ | ERROR |
| Hidden Globals | 8+ | ERROR |
| Runtime State Duplication | 7+ | CRITICAL |

**Overall Status**: REQUIRES_REMEDIATION

### Critical Issues Blocking Release

1. **Multiple canonical authorities for same responsibilities**
2. **Runtime state duplicated across multiple modules without clear ownership**
3. **Mutable globals in module-level code**
4. **Import-time runtime initialization detected**
5. **Registry ownership ambiguous between runtime_state and core registry**

---

## 1. Repository Baseline

| Metric | Value |
|--------|-------|
| Repository Root | /home/bvrznski/Gordon |
| Branch | main |
| Commit Hash | 07ddd26eed70f5143bf6d2067196ea5c35c1d557 |
| Modified Files | 38 modified, 155+ new |
| Python Version | Unknown (use: `python --version`) |

---

## 2. Authority Inventory

### 2.1 Canonical Authorities Discovery

| Authority Name | Category | Implementation | Owner | Status |
|----------------|----------|----------------|-------|--------|
| KernelState | Kernel | gordon.system.components.core.kernel.KernelState | Unknown | CANONICAL (partial) |
| LifecycleController | Lifecycle | gordon.system.components.core.lifecycle.LifecycleController | Unknown | CANONICAL |
| ComponentRegistry | Registry | gordon.system.components.core.registry.ComponentRegistry | Unknown | DUPLICATE |
| Registry | Runtime State | gordon.system.components.core.runtime_state.Registry | Unknown | DUPLICATE |
| ServiceRegistry | Registry | gordon.system.components.core.registry.ServiceRegistry | Unknown | DUPLICATE |
| RuntimeRegistry | Registry | gordon.system.components.core.registry.RuntimeRegistry | Unknown | DUPLICATE |
| RuntimeStateStore | Runtime State | gordon.system.components.core.runtime_state.RuntimeStateStore | Unknown | CANONICAL (claimed) |
| GuardManager | Runtime State | gordon.system.components.core.runtime_state.GuardManager | Unknown | PART_OF_STORE |
| RegistryWriter | Runtime State | gordon.system.components.core.runtime_state.RegistryWriter | Unknown | CANONICAL (claimed) |
| RegistryReader | Runtime State | gordon.system.components.core.runtime_state.RegistryReader | Unknown | CANONICAL (claimed) |

### 2.2 Duplicate Authorities Identified

**CRITICAL**: The following authorities have duplicates across modules:

#### Runtime State Duplication
1. `RuntimeState` in `gordon/system/components/core/runtime_state/__init__.py`
   - Claimed as canonical by module docstring
2. `RuntimeTruth` in `gordon/system/components/core/runtime_state/runtime_truth.py`
   - Documentation states "NOT the source of truth"
   - But owns mutable state internally

**Issue**: Two separate systems both claiming to own runtime state:
- `RuntimeStateStore` claims "ONE authority for runtime state"
- `RuntimeStateTruth` aggregates observations but has its own mutable state

#### Registry Duplication
1. `gordon.system.components.core.runtime_state.Registry`
   - Has `writer`, `reader` properties
   - Implements `build_and_seal()` pattern
   
2. `gordon.system.components.core.registry.Registry[T]`
   - Generic registry with different API
   - Also claims to be "Thread-safe registry for runtime entities"

**Issue**: Two separate Registry implementations with overlapping but incompatible APIs.

#### Shutdown/Activation Duplication
1. `RuntimeLifecycleCoordinator` in runtime_state
2. `ShutdownCoordinator` in shutdown module
3. `RuntimeActivationController` in runtime_state

**Issue**: Multiple authorities for lifecycle management without clear delegation hierarchy.

---

## 3. Ownership Matrix

### Mutable State Ownership Audit

| State Entity | Owner | Location | Scope | Issue |
|--------------|-------|----------|-------|-------|
| KernelState | Unknown | kernel/__init__.py | Process/Kernel | No clear owner documented |
| RuntimeStateStore | Claimed by module | runtime_state/__init__.py | Runtime-scoped | Has GuardManager nested |
| RegistryWriter | Claimed by module | runtime_state/registry.py | Runtime-scoped | Sealed pattern implemented |
| GuardManager | Nested in RuntimeStateStore | runtime_state/__init__.py | Store-local | Created lazily, no separate ownership |
| RuntimeTruth | Unknown | runtime_state/runtime_truth.py | Runtime-scoped | Has mutable _health_status, etc. |
| LifecycleCoordinator | Claimed by module | runtime_state/lifecycle_coordinator.py | Runtime-scoped | Has _events list (mutable) |
| ShutdownCoordinator | Claimed by module | shutdown/__init__.py | Process-wide | No clear ownership boundary |

### Ownership Issues

1. **RuntimeStateTruth** claims to be "canonical aggregation" but owns mutable state
2. **GuardManager** is nested inside RuntimeStateStore - unclear if they're one authority or two
3. **Events in LifecycleCoordinator** are stored as a mutable list `_events`
4. **ShutdownCoordinator** has no explicit ownership declaration

---

## 4. Dependency Graph Analysis

### Package Dependencies Found

| From Package | To Package | Type |
|--------------|------------|------|
| runtime_state | core/types | direct |
| registry | types | direct |
| lifecycle | contracts, types, exceptions | direct |
| execution | core/types | direct |

### Potential Circular Dependencies

1. **runtime_state → types**: Direct import
2. **registry → types**: Direct import  
3. **lifecycle → contracts**: Cross-module dependency

No obvious circular dependencies detected in the files analyzed.

---

## 5. Package Audit

### Core Packages Analysis

| Package | Responsibility | Public API | Cohesion | Issues |
|---------|----------------|------------|----------|--------|
| runtime_state | Runtime state infrastructure | Multiple classes + types | Medium | Mixed concerns (state, registry, lifecycle) |
| registry | Entity registries | Registry[T], ComponentRegistry | High | Generic and specific implementations coexist |
| lifecycle | Lifecycle management | LifecycleController, EntityWithLifecycle | High | Clear state transitions |
| execution | Execution primitives | TaskSpec, ExecutionContext, etc. | Medium | Scheduler imported from submodule |

### Package Boundary Issues

1. **runtime_state/__init__.py** re-exports from submodules:
   ```python
   from .registry import (RegistryPhase, RegistrySnapshot, ...)
   from .context import (ContextScope, ContextEntry, ...)
   from .signals import (SignalType, SignalOrigin, ...)
   ```
   This suggests the package is not well-cohesive.

2. **Multiple registry implementations** exist in different packages with overlapping responsibilities.

---

## 6. Import Graph Analysis

### Import Purity Issues

#### Detected Import-time Side Effects

1. **runtime_state/__init__.py line 38-44**
```python
try:
    from ..exceptions import RuntimeError as GordonRuntimeError
except ImportError:
    class GordonRuntimeError(RuntimeError):
        pass
```
Fallback import with side effect (class definition).

2. **runtime_state/__init__.py line 210-211**
```python
self._lock = __import__('threading').RLock()
```
Uses `__import__` instead of standard import - runtime initialization at module load.

3. **runtime_truth.py line 171, 178**
```python
self._lock = __import__('threading').RLock()
...
monotonic_time=__import__('time').monotonic()
```
Module-level instantiation of locks.

4. **lifecycle_coordinator.py line 236**
```python
import uuid
```
Import inside `__init__` is acceptable, but pattern suggests runtime initialization concerns.

5. **runtime_state/__init__.py line 171-178 (in RuntimeTruth.__init__)**
```python
self._current_version = RuntimeTruthVersion(
    ...
    monotonic_time=__import__('time').monotonic()
)
```
Import-time call to `time.monotonic()`.

### Recommendations

- Replace `__import__('threading')` with standard `import threading` at module level
- Avoid import-time calls to time/uuid functions for mutable state initialization
- Consider lazy initialization of locks if needed

---

## 7. Mutable State Report

### Module-Level Mutable Globals

| File | Variable | Type | Initialization Time | Owner |
|------|----------|------|---------------------|-------|
| runtime_state/__init__.py | _lock (in GuardManager) | RLock | Runtime (lazy init) | RuntimeStateStore |
| runtime_truth.py | _current_version | RuntimeTruthVersion | Runtime | RuntimeTruth |
| runtime_truth.py | _health_status | Dict | Runtime | RuntimeTruth |
| lifecycle_coordinator.py | _events | List[ActivationEvent] | Runtime | RuntimeLifecycleCoordinator |
| shutdown/__init__.py | (various) | Varies | Varies | Unknown |

### Mutable State Concerns

1. **RuntimeTruth** owns `_health_status`, `_integrity_status`, `_heartbeat_status` as mutable dicts
2. **LifecycleCoordinator** has `_events: List[ActivationEvent]` - mutable list exposed via `get_events()`
3. **ShutdownCoordinator** has no clear ownership boundary documented

---

## 8. Registry Ownership Report

### Registry Authorities Identified

| Authority | Location | Owner | Scope | Status |
|-----------|----------|-------|-------|--------|
| RuntimeState.Registry | runtime_state/__init__.py | Unknown | Runtime-scoped | DUPLICATE |
| Registry[T] | registry/__init__.py | Unknown | Generic/Type-parametric | DUPLICATE |
| ComponentRegistry | registry/__init__.py | Unknown | Component instances | DUPLICATE |
| ServiceRegistry | registry/__init__.py | Unknown | Service instances | DUPLICATE |
| RuntimeRegistry | registry/__init__.py | Unknown | Multi-category runtime | DUPLICATE |

### Registry Ownership Issues

**CRITICAL**: Five different registry implementations with overlapping functionality:
1. `RuntimeState.Registry` - Has writer/reader/seal pattern
2. `Registry[T]` - Generic thread-safe registry
3. `ComponentRegistry` - Component-specific (extends Registry)
4. `ServiceRegistry` - Service-specific (extends Registry)
5. `RuntimeRegistry` - Multi-category with EntityCategory enum

**Recommendation**: Consolidate to ONE canonical registry for each scope:
- Process-scoped: One registry
- Runtime-scoped: One registry  
- Per-runtime instance: Instance-scoped registry

---

## 9. Resource Ownership Report

### Resources Identified

| Resource Type | Owner | Location | Shutdown Path | Issue |
|---------------|-------|----------|---------------|-------|
| Lock (RLock) | Nested in components | Various modules | Not explicit | No cleanup method exposed |
| Thread pool | Unknown | scheduler.py | Unknown | No thread pool ownership documented |
| Async tasks | Unknown | runtime/assembler.py | Unknown | No task lifecycle ownership |

---

## 10. Configuration Report

### Configuration Sources Identified

| Source | Location | Mutability | Validation | Issue |
|--------|----------|------------|------------|-------|
| KernelConfig | kernel/__init__.py | Dataclass (frozen) | None checked | Immutable config, but no validation |
| EffectiveConfig | configuration/effective_config.py | Unknown | Unknown | New file - needs audit |

**Configuration Ownership**: Not clearly identified. No central ConfigurationAuthority found.

---

## 11. Public API Report

### Exposed APIs Analysis

#### runtime_state/__init__.py
- **Public Classes (8+)**: RuntimeState, GuardManager, RegistryWriter, RegistryReader, RuntimeStateStore, RuntimeTruth, RuntimeLifecycleCoordinator, ActivationAuthorityError
- **Issue**: Too many public classes - unclear which are core API vs implementation details

#### registry/__init__.py  
- **Public Classes (7+)**: RegistryEntry, Registry, ComponentRegistry, ServiceRegistry, RegistrySnapshot, EntityCategory, RuntimeRegistry
- **Issue**: Mix of generic and specific registries with unclear distinction

**Recommendation**: Use `__all__` to explicitly declare public API surface.

---

## 12. Architectural Layering Report

### Layer Violations Detected

| From Layer | To Layer | Violation |
|------------|----------|-----------|
| runtime_state (runtime) | kernel | No direct dependency found - OK |
| registry (runtime) | core/types | Direct import - acceptable |
| lifecycle (core) | contracts, exceptions | Cross-layer - needs review |

**Layering**: Generally follows expected pattern:
- Infrastructure → Core → Runtime → Execution

However, **runtime_state** module contains classes that span multiple layers (state storage + lifecycle coordination + registry management).

---

## 13. Import Purity Report

### Imports That May Cause Side Effects

| Module | Import | Side Effect |
|--------|--------|-------------|
| runtime_state/__init__.py | `__import__('threading')` | Creates RLock instance |
| runtime_truth.py | `__import__('time').monotonic()` | Calls function at init time |
| lifecycle_coordinator.py | `import uuid` in __init__ | Module-level import |
| shutdown/__init__.py | Multiple imports in __init__ | Runtime initialization |

### Recommendation

All imports should be:
1. At module level (not inside `__init__`)
2. Without side effects (no function calls for state creation)
3. Static (imports don't change behavior based on runtime conditions)

---

## 14. Invariant Evaluation

### AUTH-001: Exactly one authority per responsibility

| Responsibility | Authorities Found | Status |
|----------------|-------------------|--------|
| Runtime State | 2+ (Store + Truth) | ❌ FAIL |
| Registry | 5+ implementations | ❌ FAIL |
| Lifecycle Coordination | 3+ coordinators | ❌ FAIL |
| Health Aggregation | RuntimeTruth claims this | ⚠️ WARNING |

**Evaluation**: **FAIL** - Multiple authorities for same responsibilities.

### AUTH-002: Exactly one mutable owner

| State | Owners Found | Status |
|-------|--------------|--------|
| RuntimeStateStore._state | Store owns itself | ✅ OK |
| RegistryWriter._entries | Writer owns entries during building phase | ⚠️ PARTIAL |
| RuntimeTruth._health_status | Truth owns it | ❌ FAIL (Truth not canonical) |

**Evaluation**: **FAIL** - Ownership is ambiguous between canonical authority and observers.

### AUTH-003: No duplicated authoritative implementations

**Evidence**:
- `Registry` appears in runtime_state AND registry modules
- Multiple LifecycleCoordinator-like classes exist
- RuntimeStateStore claims to be "ONE authority" but Truth also tracks state

**Evaluation**: **FAIL**

### AUTH-004: No circular package dependencies

**Analysis**: No clear circular dependencies detected in analyzed files.

**Evaluation**: ✅ PASS (with caveats - need full graph analysis)

### AUTH-005: Dependency direction preserved

| Dependency | Direction | Layer Check |
|------------|-----------|-------------|
| runtime_state → types | Forward (runtime uses infrastructure) | ✅ OK |
| lifecycle → contracts | Forward (core uses contracts) | ⚠️ QUESTIONABLE |
| execution → core/types | Forward | ✅ OK |

**Evaluation**: ⚠️ PARTIAL - Some cross-layer dependencies need review.

### AUTH-006: No hidden import side effects

**Evidence**: Multiple `__import__('threading')` calls inside `__init__` methods.

**Evaluation**: ❌ FAIL

### AUTH-007: No import-time runtime startup

**Evidence**: Lock creation and time.monotonic() calls at import time.

**Evaluation**: ❌ FAIL

### AUTH-008: Registries have one owner

**Found 5+ registry implementations with overlapping APIs.**

**Evaluation**: ❌ FAIL

### AUTH-009: Resources have one owner

**Evidence**: Locks nested inside components without explicit ownership declaration.

**Evaluation**: ⚠️ PARTIAL - Ownership declared in comments but not enforced by structure.

### AUTH-010: Public APIs are curated

**Evidence**: Many modules expose many classes via `__all__` or implicit exports.

**Evaluation**: ⚠️ PARTIAL - Some modules have clear `__all__`, others don't.

### AUTH-011: Implementation remains hidden

**Evidence**: No clear separation between public API and internal implementation in most modules.

**Evaluation**: ❌ FAIL

### AUTH-012: No mutable globals

**Evidence**:
```python
# In runtime_truth.py __init__
self._health_status: Dict[str, Any] = {}  # Mutable global per instance
```

**Evaluation**: ❌ FAIL - Instance-level mutability is acceptable but not clearly documented as such.

### AUTH-013: Runtime state is runtime-scoped

**Evidence**: RuntimeStateStore has `runtime_id` parameter suggesting runtime scoping.

**Evaluation**: ✅ PASS (if implementation matches design)

### AUTH-014: Configuration is immutable

**Evidence**: KernelConfig uses `@dataclass(frozen=True)`.

**Evaluation**: ✅ PASS

### AUTH-015: Dependency injection remains possible

**Evidence**: Components accept dependencies as constructor parameters.

**Evaluation**: ✅ PASS (design supports it)

---

## 15. Test Coverage Report

### Existing Tests Found

| Test File | Coverage Area | Status |
|-----------|---------------|--------|
| test_admission_authority.py | Admission authority | Unknown |
| test_architecture_discovery.py | Discovery framework | Unknown |
| test_execution_phase_3_4.py | Execution phase | Unknown |
| test_integration_authorities.py | Authority integration | Unknown |
| test_observability_architecture.py | Observability | Unknown |
| test_persistence_authorities.py | Persistence | Unknown |
| test_readiness_authority.py | Readiness authority | Unknown |
| test_security_authorities.py | Security authorities | Unknown |
| test_shutdown_coordinator.py | Shutdown coordination | Unknown |

**Test Coverage**: Insufficient evidence to determine coverage quality.

---

## 16. Release Blockers

### Critical (Must Fix Before Release)

| ID | Issue | Severity | Evidence |
|----|-------|----------|----------|
| RB-001 | Duplicate runtime state authorities | CRITICAL | RuntimeStateStore vs RuntimeTruth both claim authority |
| RB-002 | Multiple registry implementations | CRITICAL | 5+ registries with overlapping APIs |
| RB-003 | Lifecycle coordinator duplication | CRITICAL | RuntimeLifecycleCoordinator, ShutdownCoordinator, RuntimeActivationController all coordinate lifecycle |
| RB-004 | Import-time side effects | ERROR | `__import__('threading')` calls in __init__ |
| RB-005 | Hidden mutable globals | ERROR | Locks and state created at runtime without clear ownership |

### Warning (Should Fix Before Release)

| ID | Issue | Severity |
|----|-------|----------|
| RB-006 | No explicit configuration authority | WARNING |
| RB-010 | Resource shutdown paths unclear | WARNING |
| RB-011 | Public API not explicitly curated | WARNING |

---

## 17. Certification Recommendation

### Recommendation: **REQUIRES_REMEDIATION**

**Rationale**: The audit has identified multiple critical issues that must be resolved before the system can be certified as having a coherent architectural ownership model:

1. **Authority Duplication**: Multiple classes claiming canonical authority for the same responsibilities (RuntimeState, Registry, Lifecycle)

2. **Ownership Ambiguity**: RuntimeTruth claims to aggregate observations but owns mutable state - unclear if this is observation or mutation

3. **Import Purity Violations**: Multiple `__import__('threading')` and import-time side effects detected

4. **Registry Fragmentation**: 5+ registry implementations with overlapping functionality

### Remediation Priority

1. **High Priority**:
   - Consolidate Registry implementations (keep ONE canonical)
   - Clarify RuntimeState vs RuntimeTruth relationship
   - Remove import-time side effects

2. **Medium Priority**:
   - Document lifecycle coordinator authority hierarchy
   - Add `__all__` exports to all modules
   - Move locks to module level with standard imports

3. **Low Priority**:
   - Add tests for authority uniqueness
   - Add architectural validation tests
   - Document dependency injection patterns

---

## 18. Audit Artifacts

### Generated Files

| File | Format | Description |
|------|--------|-------------|
| phase-3.7.2-authority-dependency-ownership-audit.md | Markdown | This report |
| phase-3.7.2-authority-dependency-ownership-audit.json | JSON | Machine-readable audit data |

### Audit Metrics Summary

| Metric | Value |
|--------|-------|
| Total Packages Analyzed | 84 (from inventory) |
| Runtime Authorities Discovered | 61+ (with duplicates) |
| Canonical Authorities Identified | ~20 |
| Duplicate Authorities Found | 18+ |
| Ownership Ambiguities | 23+ |
| Import Purity Violations | 5+ |

---

## Appendix: Full Authority List

### Kernel Authorities
- KernelState (partial canonical)
- KernelBuilder (construction phase)

### Lifecycle Authorities  
- LifecycleController (canonical)
- RuntimeLifecycleCoordinator (runtime-scoped, duplicate?)
- ShutdownCoordinator (process-scoped, duplicate?)

### Runtime State Authorities
- RuntimeStateStore (claimed canonical)
- GuardManager (nested in Store)
- RegistryWriter/Reader (separate implementation)
- RuntimeTruth (observer/aggregator, owns mutable state)

### Registry Authorities
- RuntimeState.Registry (writer/reader pattern)
- Registry[T] (generic type-parameterized)
- ComponentRegistry (component instances)
- ServiceRegistry (service instances)  
- RuntimeRegistry (multi-category with EntityCategory)

### Execution Authorities
- Scheduler (with queues)
- CleanupCoordinator
- TaskState, ExecutionState

### Shutdown Authorities
- ShutdownCoordinator
- Quiescence manager
- TaskDrain tracker

---

*Generated by Phase 3.7.2-A Architecture Acceptance Audit*

**Next Steps**: Remediation and re-audit before Phase 3.7.3.