# Phase 3.27 — Core Repository, Package & Modular Architecture

**Phase:** 3.27  
**Date:** 2026-08-14  
**Status:** CANONICAL ARCHITECTURE  
**Version:** 1.0.0  

---

## Executive Summary

This phase establishes the **canonical Repository, Package & Modular Architecture** for Gordon Core.

The Gordon repository is not merely a collection of source files.

It is a structured, self-describing architectural system composed of independently verifiable, reusable, composable, and evolvable modules.

### Vision

The repository shall become a living architectural model. Every directory, every package, every module, every interface, every service, every capability, every implementation, every document, every test, every generated artifact shall possess an explicit architectural purpose.

Repository organization shall communicate architecture before any single implementation is examined.

---

## 1. Architecture Philosophy

### 1.1 Core Principles

| Principle | Description |
|-----------|-------------|
| **Explicit** | Every architectural element must have declared ownership and responsibility |
| **Verifiable** | All architectural claims must be machine-verifiable |
| **Deterministic** | Repository structure is fixed; no arbitrary organization |
| **Composable** | Modules combine without side effects through clear interfaces |
| **Evolvable** | Architecture adapts while preserving invariants |

### 1.2 What This Phase Owns

This phase owns the **structure** of the repository, not its behavior:

- Repository topology (where things live)
- Package ownership (who owns what)
- Module boundaries (how code is grouped)
- Dependency direction (what depends on what)
- Layering rules (which layers can depend on which)
- Public vs internal API separation
- Extension points and composition

### 1.3 What This Phase Does NOT Own

This phase NEVER owns:

- Runtime behavior
- Semantic interpretation
- State management
- Execution scheduling
- Business logic implementation

---

## 2. Terminology & Conceptual Distinctions

### 2.1 Canonical Definitions

| Concept | Definition | Responsibility |
|---------|------------|----------------|
| **Repository** | The entire source tree, as a self-describing architectural system | This phase |
| **Workspace** | A logical grouping of packages for development purposes | Development tooling |
| **Package** | A directory containing related modules with one owner and responsibility | Package architecture |
| **Module** | A single unit of code organization (file or package) | Module architecture |
| **Subsystem** | A logical grouping of packages with shared purpose | Subsystem ownership |
| **Component** | A runtime-constructible unit providing capabilities | Runtime ownership |
| **Service** | A canonical authority registered at runtime | Runtime ownership |
| **Capability** | An interface contract defining what can be done | Interface architecture |
| **Interface** | A specification of callable operations | API architecture |
| **Implementation** | Code that satisfies an interface contract | Implementation details |

### 2.2 Key Distinctions

1. **Package ≠ Module**: Package is a packaging unit with ownership; module is a code organization unit.
2. **Repository ≠ Directory**: Repository is an architectural system with rules; directory is a filesystem concept.
3. **Public API ≠ Internal API**: Public APIs are versioned and stable; internal APIs may change freely.
4. **Extension ≠ Plugin**: Extension adds capability within boundaries; plugin replaces/overrides behavior.

---

## 3. Repository Topology

### 3.1 Root Directory Structure

```
/home/bvrznski/Gordon
├── gordon_system/              # Primary implementation workspace
│   ├── docs/                   # Documentation (public API)
│   │   └── agent/architecture/ # Architecture documentation zone
│   ├── src/                    # Source code implementation zone
│   │   └── agent/             # Agent subsystem implementations
│   │       ├── architecture/  # Architecture modules
│   │       ├── components/    # Component implementations
│   │       ├── capabilities/  # Capability definitions
│   │       ├── core/          # Core runtime implementations
│   │       ├── systems/       # System integrations
│   │       └── execution/     # Execution layer implementations
│   └── tests/                  # Test implementations
├── gordon-environment/         # Environment zone (optional)
├── gordon-improver/            # Improver zone (optional)
├── gordon-legacy/              # Legacy code zone (migrating)
├── gordon-modules/             # Module zone (extensibility)
├── gordon-researcher/          # Research zone (experimental)
├── observability/              # Observability artifacts zone
├── recommendations/            # Recommendations zone (generated)
├── reports/                    # Reports zone (generated)
└── validation/                 # Validation results zone
```

### 3.2 Architectural Zones

| Zone | Purpose | Content | Rules |
|------|---------|---------|-------|
| **docs/** | Documentation | Architecture, API, guides | No implementation code |
| **src/** | Implementation | Python source files | Must follow architecture rules |
| **tests/** | Testing | Test implementations | Can access internal APIs for testing |
| **docs/agent/architecture/** | Architecture zone | Phase documents, reports | Canonical architecture definitions |

### 3.3 Topology Invariants

1. Every file in `src/` belongs to exactly one package
2. No cyclic dependencies between packages at same layer
3. Dependencies only flow downward through architectural layers
4. Public APIs are exported from package `__init__.py`
5. Internal APIs never leak across package boundaries

---

## 4. Package Architecture

### 4.1 Package Definition

A **Package** is a directory containing related modules with:

- One explicit owner (team or individual)
- One architectural layer
- One primary responsibility
- Explicit public and internal contracts
- Versioning (when distributed)

### 4.2 Package Structure Template

```
package_name/
├── __init__.py           # Package identity, public API exports
├── __meta__.py           # Package metadata (owner, layer, version)
├── __tree__.py           # Module hierarchy description
├── foundations.py        # Core abstractions and types
├── interfaces.py         # Public interface definitions
├── contracts.py          # Implementation contracts
├── implementations.py    # Concrete implementations
└── __init__.py           # Package exports (public API facade)
```

### 4.3 Package Metadata

Each package shall define:

```python
# package_name/__meta__.py
"""Package metadata for {package_name}."""

__version__ = "1.0.0"
__owner__ = "architecture-team"  # Team or individual responsible
__layer__ = "foundation"         # Architectural layer
__category__ = "implementation"  # implementation, interface, protocol, model
__dependencies__ = []            # Direct dependencies
```

### 4.4 Package Categories

| Category | Purpose | Example |
|----------|---------|---------|
| **Implementation** | Concrete functionality | `state/`, `execution/` |
| **Interface** | Abstract contracts | `interfaces/`, `communication/` |
| **Protocol** | Wire-level specifications | (none yet) |
| **Model** | Data models and types | `types/`, `models/` |
| **Registry** | Entity registries | `registry/` |
| **Facade** | Simplified access layers | `facade/` |
| **Utility** | Shared utilities | `utils/`, `helpers/` |
| **Adapter** | Integration adapters | `adapters/` |

---

## 5. Module Architecture

### 5.1 Module Types

| Type | Purpose | Naming Convention |
|------|---------|-------------------|
| **Implementation** | Concrete logic | `{name}.py`, `{name}/__init__.py` |
| **Interface** | Abstract contracts | `{name}_interface.py`, `interfaces.py` |
| **Protocol** | Wire protocols | `{name}_protocol.py`, `protocols.py` |
| **Model** | Data models | `{name}_model.py`, `models.py` |
| **Registry** | Registry patterns | `registry.py`, `registries.py` |
| **Facade** | Simplified access | `facade.py`, `facade_{name}.py` |
| **Utility** | Shared utilities | `utils.py`, `_internal.py` |
| **Adapter** | Integration adapters | `{name}_adapter.py` |

### 5.2 Module Responsibilities

- **One primary responsibility per module**
- Clear boundaries between modules
- Minimal coupling through interfaces

---

## 6. Architectural Layering

### 6.1 Canonical Layers

```
┌─────────────────────────────────────┐
│    Application Layer (Phase X.X)   │ ← High-level applications
├─────────────────────────────────────┤
│    Integration Layer               │ ← System integrations
├─────────────────────────────────────┤
│    Cognitive Layer                 │ ← Reasoning, planning
├─────────────────────────────────────┤
│    Capability Layer                │ ← Business capabilities
├─────────────────────────────────────┤
│    Runtime Layer                   │ ← Execution runtime
├─────────────────────────────────────┤
│    Infrastructure Layer            │ ← Platform infrastructure
├─────────────────────────────────────┤
│    Core Layer                      │ ← Core runtime primitives
├─────────────────────────────────────┤
│    Foundation Layer                │ └───┐
└─────────────────────────────────────┘     │
                                            │
┌─────────────────────────────────────┐     │
│   Dependencies flow DOWNWARD        │ ◄───┘
└─────────────────────────────────────┘
```

### 6.2 Layer Responsibilities

| Layer | Responsibility | Example Packages |
|-------|----------------|------------------|
| **Foundation** | Core primitives, types, utilities | `types/`, `errors/` |
| **Core** | Runtime infrastructure, lifecycle | `core/`, `runtime/` |
| **Infrastructure** | Platform services, storage, network | (system integrations) |
| **Runtime** | Execution runtime, scheduling | `execution/runtime/` |
| **Capability** | Business capabilities, features | `capabilities/` |
| **Cognitive** | Reasoning, planning, memory | `cognition/`, `memory/` |
| **Application** | High-level applications | (not yet defined) |

### 6.3 Layer Violation Rules

- Higher layers may depend on lower layers
- Lower layers NEVER depend on higher layers
- Same-layer dependencies must be bidirectionally verified

---

## 7. Public API Architecture

### 7.1 Public API Definition

A **Public API** is an interface contract that:

- Is explicitly exported from a package
- Has versioning guarantees
- Follows stability rules
- May not change without version bump

### 7.2 Public API Rules

| Rule | Description |
|------|-------------|
| **Explicit Exports** | Only `__all__` items are public |
| **Version Stability** | Major version changes on breaking changes |
| **Documentation** | Public APIs must be documented |
| **Tests Required** | All public APIs must have tests |

### 7.3 API Ownership

Every public API has:

- Owner (responsible for compatibility)
- Version (current stability level)
- Deprecation policy (when removed)

---

## 8. Internal API Architecture

### 8.1 Internal API Definition

An **Internal API** is an interface contract that:

- Is not exported from a package
- May change without version bump
- Should be documented but not guaranteed stable

### 8.2 Internal API Rules

| Rule | Description |
|------|-------------|
| **Private by default** | Not in `__all__`, starts with `_` |
| **No stability guarantees** | Can change freely |
| **Implementation detail** | Hidden from users |

---

## 9. Dependency Architecture

### 9.1 Dependency Rules

| Rule | Description |
|------|-------------|
| **Layered** | Dependencies flow down through layers |
| **Explicit** | All dependencies must be declared |
| **Acyclic** | No cycles within same layer |
| **Minimal** | Only required dependencies |

### 9.2 Dependency Types

| Type | Direction | Example |
|------|-----------|---------|
| **Interface dependency** | Upward | Implementation depends on interface |
| **Implementation dependency** | Same/Downward | Uses concrete implementation |
| **Protocol dependency** | Horizontal | Wire protocol compatibility |

---

## 10. Composition Architecture

### 10.1 Composition Principles

| Principle | Description |
|-----------|-------------|
| **Preserve boundaries** | Composition doesn't break encapsulation |
| **Explicit wiring** | Dependencies are explicitly configured |
| **Testable** | Composed systems remain testable |

### 10.2 Composition Patterns

- **Package composition**: Combine packages into subsystems
- **Module composition**: Use modules within a package
- **Extension composition**: Add optional functionality

---

## 11. Extension & Plugin Architecture

### 11.1 Extension Points

| Extension Point | Purpose |
|-----------------|---------|
| **Plugins** | Optional capability additions |
| **Extensions** | Behavioral modifications |
| **Adapters** | Integration with external systems |

### 11.2 Extension Rules

- Extensions must not violate Core boundaries
- Extension registration is explicit
- Extension lifecycle is managed

---

## 12. Repository Evolution

### 12.1 Migration Process

1. **Identify** duplicated or misplaced modules
2. **Plan** relocation with dependency updates
3. **Implement** code movement and imports
4. **Update** documentation and reports
5. **Certify** new structure

### 12.2 Deprecation Policy

| Phase | Duration | Action |
|-------|----------|--------|
| **Deprecate** | 1 release | Mark as deprecated, add warning |
| **Maintain** | 3 releases | Keep working, document alternatives |
| **Remove** | After grace | Remove entirely |

---

## 13. Repository Standards

### 13.1 Naming Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Package | `lower_snake_case` | `execution/`, `state/` |
| Module | `lower_snake_case.py` | `lifecycle.py`, `validation.py` |
| Class | `CamelCase` | `LifecycleManager`, `StateValidator` |
| Function | `lower_snake_case` | `validate_state()`, `compute_metrics()` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |

### 13.2 Directory Conventions

- One package per directory
- Clear ownership in each package
- Consistent module organization within packages

---

## 14. Reflection & Inventory

### 14.1 Inventory Systems

| System | Purpose |
|--------|---------|
| **Package inventory** | Track all packages and owners |
| **Module inventory** | Track all modules and responsibilities |
| **Dependency graph** | Visualize and validate dependencies |
| **API inventory** | Track public and internal APIs |

---

## 15. Observability & Diagnostics

### 15.1 Diagnostic Categories

| Category | Purpose |
|----------|---------|
| **Package diagnostics** | Package ownership, dependencies |
| **Dependency diagnostics** | Circular deps, layer violations |
| **API diagnostics** | Public API coverage, stability |

---

## 16. Certification Process

### 16.1 Certification Criteria

1. Repository topology is deterministic
2. All packages have explicit ownership
3. All dependencies are valid and acyclic
4. Layering rules are satisfied
5. Public APIs are properly exported
6. Documentation is complete

---

## 17. Implementation Checklist

### Phase 3.27 Implementation Tasks

- [x] **3.27.1** Repository Foundations - Philosophy, principles, terminology
- [ ] **3.27.2** Repository Topology - Zones, layout, invariants
- [ ] **3.27.3** Package Architecture - Structure, ownership, categories
- [ ] **3.27.4** Module Architecture - Types, responsibilities
- [ ] **3.27.5** Architectural Layering - Layers, rules, violations
- [ ] **3.27.6** Public API Architecture - Exports, versioning
- [ ] **3.27.7** Internal API Architecture - Private contracts
- [ ] **3.27.8** Dependency Architecture - Rules, validation
- [ ] **3.27.9** Module Composition - Patterns, practices
- [ ] **3.27.10** Extension & Plugin Architecture - Extension points
- [ ] **3.27.11** Repository Evolution - Migration strategy
- [ ] **3.27.12** Repository Standards - Naming, conventions
- [ ] **3.27.13** Reflection & Inventory - Discovery systems
- [ ] **3.27.14** Observability & Diagnostics - Validation tools
- [ ] **3.27.15** Refactoring Policies - Automated updates
- [ ] **3.27.16** Repository-wide Migration - Apply to all packages
- [ ] **3.27.17** Audit & Remediation - Validate and fix
- [ ] **3.27.18** Certification - Final verification

---

## 18. References

### Related Phases

| Phase | Description |
|-------|-------------|
| 3.12 | Core Architecture |
| 3.15 | State |
| 3.16 | Time |
| 3.17 | Resources & Compute |
| 3.20 | Concurrency |
| 3.21 | Communication |
| 3.22 | Security |
| 3.23 | Reflection |
| 3.24 | Validation |

### Related Documentation

- `core_architectural_glossary.md` - Terminology and ownership
- `phase-3.12.*` - Core architecture documentation
- `phase-3.26-core-lifecycle-composition-runtime-orchestration.md` - Lifecycle composition

---

*This document is the authoritative repository, package & modular architecture specification for Gordon.*

**Version:** 1.0.0  
**Phase:** 3.27  
**Date:** 2026-08-14  
**Status:** CANONICAL ARCHITECTURE