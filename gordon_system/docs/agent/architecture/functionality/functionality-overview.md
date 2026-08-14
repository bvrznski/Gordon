# Core Functionality Architecture Overview
# =============================================================================

**Phase**: 3.13.11  
**Status**: CANONICAL_DOCUMENTATION_CERTIFIED  
**Document Type**: CANONICAL_ARCHITECTURE  
**Owner**: Gordon Core Team  

---

## Executive Summary

This document establishes the canonical documentation hierarchy for Gordon's
Functionality Architecture system.

The Functionality architecture provides:

* **Classification**: Every Core class has exactly one primary functionality marker
* **Documentation**: Complete semantics, examples, and anti-patterns for each marker
* **Inventories**: Machine-readable records of all classes by functionality
* **Validation**: Deterministic checks for marker usage consistency
* **Migration**: Evidence-based preparation for safe class reclassification

---

## Functionality Marker Hierarchy

```
CoreFunctionality (abstract base)
├── ForCore          - Core infrastructure services
├── ForExecution     - Execution layer (scheduling, concurrency, cancellation)
├── ForEntrypoint    - Application entry points and bootstrap
├── ForArchitecture  - Architecture reflection and analysis
├── ForNetworks      - Network/transport layer services
├── ForCapabilities  - Agent capability implementations
└── ForSystems       - System-level subsystems (perception, memory, consciousness)
```

---

## What Functionality Markers Mean

### Primary Purpose

A Functionality marker answers the question:
**"Which architectural layer primarily consumes this Core component?"**

The marker indicates the **intended consumer**, not:

* ❌ Ownership transfer
* ❌ Authority granted
* ❌ Package location requirement  
* ❌ Implementation kind constraint
* ❌ Runtime behavior change

### Example

```python
from agent.components.core.functionality import ForExecution

class ExecutionScheduler(CoreService, ForExecution):
    """Deterministic task scheduling infrastructure for execution layer."""
```

**Interpretation**: This scheduler is primarily used by the Execution layer.

---

## Canonical Markers

| Marker | Consumer Layer | Primary Responsibilities |
|--------|----------------|-------------------------|
| `ForCore` | Core Infrastructure | Lifecycle, registry, configuration, state management |
| `ForExecution` | Task Execution | Scheduling, concurrency, cancellation, deadlines |
| `ForEntrypoint` | System Bootstrap | Initialization, config loading, lifecycle startup |
| `ForArchitecture` | Architecture | Reflection, dependency analysis, topology mapping |
| `ForNetworks` | Network Layer | Stream publication, message delivery, serialization |
| `ForCapabilities` | Agent Capabilities | Cognition, learning, memory, motivation |
| `ForSystems` | System Subsystems | Perception, consciousness, memory storage |

---

## Markers Do NOT Mean

### ❌ Ownership Transfer
A `ForExecution` class remains **Core-owned**. The marker indicates intended consumer,
not ownership transfer.

### ❌ Authority Grant
Markers grant **no authority**. They are not authorization tokens.

### ❌ Package Placement Requirement
Marking a class as `ForNetworks` does NOT require it to be in the networks package.
The marker describes purpose, not location.

### ❌ Runtime Behavior Change
Markers are **passive metadata**. They do not affect runtime execution.

---

## Primary vs Secondary Semantics

### Primary Functionality (Exactly One)
Every Core class must have exactly one primary functionality marker:

```python
class StageScheduler(CoreService, ForExecution):
    ...
```

### Secondary Roles (Zero or More)
Secondary roles indicate additional participation:

```python
class StageScheduler(
    CoreService,
    ForExecution,
    LifecycleParticipant,
    NetworkIntegrationParticipant,
    DiagnosticSource,
):
    ...
```

| Category | Role Examples |
|----------|---------------|
| Runtime | `LifecycleParticipant`, `HealthParticipant` |
| Integration | `NetworkIntegrationParticipant`, `CapabilityIntegrationParticipant` |
| Observability | `DiagnosticSource`, `MetricsSource` |

---

## Classification Rules

### Rule 1: Singular Primary Marker
Every Core class has exactly one primary Functionality marker.

```python
# ✅ Valid - single marker
class MyComponent(CoreService, ForCore):
    ...

# ❌ Invalid - multiple unrelated markers
class BadComponent(CoreService, ForCore, ForExecution):  # No!
    ...
```

### Rule 2: Empty Markers
Functionality markers are empty - no behavior, no state:

```python
class ForCore(CoreFunctionality):
    __slots__ = ()  # No attributes allowed
```

### Rule 3: Shallow Inheritance
Markers inherit only from `CoreFunctionality`:

```python
# ❌ Invalid - deep hierarchy
class MyCustomMarker(ForExecution):  # Only one level allowed!
    ...

# ✅ Valid - direct inheritance
class ForMyCustomLayer(CoreFunctionality):
    ...
```

---

## Validation & Documentation

### Validation Pipeline
1. **Static Analysis**: Check marker inheritance
2. **Registry Registration**: Track class-marker relationships
3. **Reflection Queries**: Query classification metadata
4. **Inventory Generation**: Build machine-readable inventories
5. **Drift Detection**: Compare documentation vs implementation

### Documentation Status Values

| Status | Meaning |
|--------|---------|
| `COMPLETE` | Fully documented with examples and anti-patterns |
| `PARTIAL` | Documented but missing some sections |
| `STALE` | Documentation exists but repository has changed |
| `MISSING` | No documentation found |
| `CONTRADICTORY` | Multiple conflicting documents |

---

## Documentation Hierarchy

```
docs/agent/architecture/
└── functionality/                # Canonical Functionality docs
    ├── overview.md              # This file - hierarchy overview
    ├── marker-hierarchy.md      # Marker inheritance rules
    ├── semantics/
    │   ├── forcore.md           # ForCore semantics
    │   ├── forexecution.md      # ForExecution semantics  
    │   └── ...
    ├── responsibility-profiles/ # Profile documentation
    ├── exemptions/              # Exemption rules and inventory
    ├── inventories/             # Generated class inventories
    ├── matrices/                # Cross-reference matrices
    └── migration/               # Migration records and guides
```

---

## Inventory Sources

### Primary Source: Repository Evidence
Inventories are derived from actual repository state:

```bash
# Verify current classification
python -m agent.components.core.functionality_markers.inventory \
    --scan-core-packages \
    --output-inventory inventories/class-inventory.json
```

### Determinism Guarantee
Equivalent repository state + generator version = equivalent inventory output.

---

## Architecture Layers

| Layer | Primary Package | Functionality Markers |
|-------|-----------------|----------------------|
| Core Infrastructure | `src/agent/components/core/` | ForCore, ForExecution, ForArchitecture |
| Execution | `src/agent/execution/` | (semantic implementations) |
| Entrypoint | `src/agent/entrypoint/` | ForEntrypoint |
| Architecture | `src/agent/architecture/` | ForArchitecture |

---

## Migration Path

Classes may need to change Functionality markers during:

1. **Core → Execution**: Generic infrastructure added to execution layer
2. **Execution → Core**: Common patterns extracted to shared infrastructure
3. **Any → Architecture**: Reflection components added for analysis

Each migration requires:
* Evidence-backed decision
* Migration record in `functionality/migration/`
* Registry update
* Documentation refresh

---

## Next Steps

1. Complete marker documentation for each canonical marker
2. Build complete class inventory by functionality
3. Generate cross-reference matrices (ownership, dependency, responsibility)
4. Validate documentation consistency with implementation
5. Prepare Phase 3.13.12 migration baseline

---

## References

* **Phase 3.13.1**: Marker Foundations
* **Phase 3.13.2**: Identity & Classification  
* **Phase 3.13.3**: Primary & Secondary Semantics
* **Phase 3.13.4**: Metaclass Registration & Reflection
* **Phase 3.13.5**: Integrity & Interface Verification
* **Phase 3.13.6**: Core-Internal Classification
* **Phase 3.13.7**: Execution Classification
* **Phase 3.13.8**: Entrypoint Classification
* **Phase 3.13.9**: Network/Capability/System Classification
* **Phase 3.13.10**: Dependency & Ownership Validation

---

## Machine-Readable Metadata

```json
{
  "document_id": "functionality-overview",
  "document_kind": "CANONICAL_ARCHITECTURE",
  "scope": ["src/agent/components/core/", "docs/"],
  "phase": "3.13.11",
  "schema_version": "1.0.0",
  "canonical_markers": [
    "CoreFunctionality", "ForCore", "ForExecution", 
    "ForEntrypoint", "ForArchitecture", "ForNetworks",
    "ForCapabilities", "ForSystems"
  ],
  "status": "COMPLETE"
}