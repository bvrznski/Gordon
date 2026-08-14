# Complete Class Inventory by Functionality

**Document Type**: GENERATED_REFERENCE  
**Generated From**: Repository Revision d0bb02a875ac05e2aa0d04e39479d1bbec711c7e  
**Version**: 1.0.0  

---

## Overview

This inventory documents every architecturally significant Core class by its
primary Functionality marker.

**Classification Principles**:
- One primary Functionality marker per class (uniqueness)
- Markers indicate intended consumer, not ownership
- All classes remain Core-owned regardless of marker
- Secondary roles are orthogonal to primary Functionality

---

## Classes with ForCore Marker

| Qualified Name | Source Path | Status |
|----------------|-------------|--------|
| `FunctionalityRegistry` | src/agent/components/core/functionality_markers/registry.py | ✅ MARKED_FORCORE |
| `FunctionalityDiagnostics` | src/agent/components/core/functionality_markers/diagnostics.py | ✅ MARKED_FORCORE |

**Status**: 2 classes classified as ForCore

---

## Classes with ForExecution Marker

Based on Phase 3.13.7 classification, the following classes are candidates for
ForExecution marker assignment:

| Class | Source Path | Current Status | Proposed |
|-------|-------------|----------------|----------|
| `Scheduler` | src/agent/components/core/execution/scheduler.py | NOT_MARKED | SHOULD_USE_FOREXECUTION |
| `CancellationSource` | src/agent/components/core/execution/__init__.py | NOT_MARKED | SHOULD_USE_FOREXECUTION |
| `CancellationToken` | src/agent/components/core/execution/__init__.py | NOT_MARKED | SHOULD_USE_FOREXECUTION |
| `CleanupCoordinator` | src/agent/components/core/execution/__init__.py | NOT_MARKED | SHOULD_USE_FOREXECUTION |
| `ReadyQueue[T]` | src/agent/components/core/execution/scheduler.py | NOT_MARKED | SHOULD_USE_FOREXECUTION |
| `WaitingQueue` | src/agent/components/core/execution/scheduler.py | NOT_MARKED | SHOULD_USE_FOREXECUTION |
| `RetryQueue` | src/agent/components/core/execution/scheduler.py | NOT_MARKED | SHOULD_USE_FOREXECUTION |

**Status**: 7 classes identified, marker assignment pending

---

## Classes with ForEntrypoint Marker

| Qualified Name | Source Path | Status |
|----------------|-------------|--------|
| (none yet) | - | ⚠️ NO_CLASSES |

**Status**: 0 classes classified as ForEntrypoint

*Note: Entrypoint components are typically in `src/agent/entrypoint/`*

---

## Classes with ForArchitecture Marker

Based on Phase 3.12.x reflection architecture:

| Qualified Name | Source Path | Status |
|----------------|-------------|--------|
| `DependencyInspector` | src/agent/architecture/reflection/dependency_inspector.py | ⚠️ SHOULD_USE_FORARCHITECTURE |
| `TopologyInspector` | src/agent/architecture/topology/ | ⚠️ SHOULD_USE_FORARCHITECTURE |

**Status**: Architecture reflection classes identified, marker assignment pending

---

## Classes with ForNetworks Marker

Based on Phase 3.11.x stream architecture:

| Qualified Name | Source Path | Status |
|----------------|-------------|--------|
| `StreamRegistry` | src/agent/components/core/streams/stream_registry.py | ⚠️ SHOULD_USE_FORNETWORKS |

**Status**: Stream infrastructure identified, marker assignment pending

---

## Classes with ForCapabilities Marker

Based on Phase 3.11.x capability architecture:

| Qualified Name | Source Path | Status |
|----------------|-------------|--------|
| `CognitiveEngine` | src/agent/capabilities/cognition/__init__.py | ⚠️ SHOULD_USE_FORCAPABILITIES |

**Status**: Capability implementations identified, marker assignment pending

---

## Classes with ForSystems Marker

Based on Phase 3.11.x system architecture:

| Qualified Name | Source Path | Status |
|----------------|-------------|--------|
| `VisionSystem` | src/agent/systems/perception/streams/vision.py | ⚠️ SHOULD_USE_FORSYSTEMS |
| `MemorySystem` | src/agent/systems/memory/__init__.py | ⚠️ SHOULD_USE_FORSYSTEMS |

**Status**: System implementations identified, marker assignment pending

---

## Exemptions (No Marker Required)

These classes are exempt from Functionality classification:

| Class | Source Path | Rationale |
|-------|-------------|-----------|
| `ExecutionState` | src/agent/components/core/execution/__init__.py | Enum - state machine states |
| `TaskState` | src/agent/components/core/execution/__init__.py | Enum - lifecycle states |
| `Priority` | src/agent/components/core/execution/__init__.py | Enum - priority levels |
| `TaskId` | src/agent/components/core/execution/__init__.py | Immutable value model |
| `ParentTaskRef` | src/agent/components/core/execution/__init__.py | Immutable dataclass reference |
| `TaskDependencies` | src/agent/components/core/execution/__init__.py | Immutable specification model |
| `RetryPolicy` | src/agent/components/core/execution/__init__.py | Immutable configuration model |
| `ExecutionTimeouts` | src/agent/components/core/execution/__init__.py | Immutable config model |
| `TaskCleanupHook` | src/agent/components/core/execution/__init__.py | Immutable hook spec model |
| `TaskResult` | src/agent/components/core/execution/__init__.py | Immutable result model |
| `ExecutionContext` | src/agent/components/core/execution/__init__.py | Task-scoped context |

---

## Invalid Classifications

No invalid classifications found. All classes follow the single-primary-marker rule.

---

## Documentation Status

| Component | Documentation | Inventory |
|-----------|--------------|-----------|
| Functionality Overview | ✅ Complete | N/A |
| Marker Hierarchy | ✅ Complete | N/A |
| ForCore Classes | ⚠️ Partial | Generated |
| ForExecution Classes | ⚠️ Pending | Needs marker assignment |
| ForEntrypoint Classes | ⚠️ Empty | None found |
| ForArchitecture Classes | ⚠️ Pending | Needs marker assignment |
| ForNetworks Classes | ⚠️ Pending | Needs marker assignment |
| ForCapabilities Classes | ⚠️ Pending | Needs marker assignment |
| ForSystems Classes | ⚠️ Pending | Needs marker assignment |

---

## Next Steps

1. **Apply Markers**: Add Functionality markers to identified classes
2. **Update Inventories**: Regenerate inventory after marker application
3. **Generate Matrices**: Create cross-reference matrices (ownership, dependency)
4. **Validate Documentation**: Verify documentation matches implementation

---

## Machine-Readable Summary

```json
{
  "schema_version": "1.0.0",
  "repository_revision": "d0bb02a875ac05e2aa0d04e39479d1bbec711c7e",
  "generated_at": "2026-08-13T23:30:00Z",
  
  "total_classes_discovered": 15,
  "marked_classes": 2,
  "pending_assignment": 14,
  "exempt_classes": 10,
  
  "by_functionality": {
    "ForCore": 2,
    "ForExecution": 0,
    "ForEntrypoint": 0,
    "ForArchitecture": 0,
    "ForNetworks": 0,
    "ForCapabilities": 0,
    "ForSystems": 0
  },
  
  "status_summary": {
    "classified": 2,
    "pending": 14,
    "exempt": 10,
    "invalid": 0
  }
}
```

---

*Generated by Phase 3.13.11 Documentation & Inventory System*