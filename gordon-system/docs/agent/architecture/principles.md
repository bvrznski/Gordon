# Gordon Architecture Principles

## Overview

The Gordon system is built on a set of foundational principles that guide all architectural decisions and implementation choices.

## Core Principles

### 1. Layered Separation

The system is organized into distinct, non-overlapping layers:

```
┌─────────────────────────────────────┐
│         Systems Layer               │
│  (memory, perception)               │
├─────────────────────────────────────┤
│        Components Layer             │
│   (core: engine, executor, manager) │
├─────────────────────────────────────┤
│        Capabilities Layer           │
│   (action, agency, cognition, etc.) │
├─────────────────────────────────────┤
│         Architecture Layer          │
│  (map, graph, ownership, topology)  │
└─────────────────────────────────────┘
```

**Rules:**
- Lower layers may not depend on higher layers
- Each layer provides services to the layer above it
- Dependencies flow downward only

### 2. Explicit Ownership

Every component has:
- **Single owner** - One responsible entity for maintenance and evolution
- **Clear boundaries** - Well-defined public and private interfaces
- **Contractual obligations** - Formalized expectations about behavior

### 3. Declarative Architecture

Architecture is expressed through:
- **Contracts** (`__tree__.py`) - Structural guarantees
- **Metadata** (`__meta__.py`) - Descriptive information
- **Documentation** - Human-readable specifications

No implementation artifacts should appear in architecture layer files.

### 4. Immutable Contracts

Package contracts are:
- **Versioned** - Changes require version updates
- **Validated** - Structure checked against contract
- **Repair-safe** - Can be regenerated without data loss

### 5. Zero Runtime Implementation

Architecture layer contains:
- No executable code
- No algorithms
- No runtime state
- Only declarations and contracts

Implementation begins in Phase 3.

## Design Guidelines

### Consistency
All packages follow the same structural pattern:

```
package/
├── __init__.py      # Empty, for importability
├── __meta__.py      # Declarative metadata
└── __tree__.py      # Structural contract
```

### Completeness
Every package must specify:
- Canonical name
- Architectural layer
- Semantic owner
- Parent package
- Status
- Maturity
- Purpose
- Public API intention
- Documentation reference

### Independence
Packages should:
- Minimize cross-dependencies
- Expose minimal public surface
- Define clear input/output contracts

## Validation Criteria

Architecture is validated against:

1. **Tree consistency** - Parent-child relationships match filesystem
2. **Ownership consistency** - No overlapping ownership boundaries
3. **Dependency consistency** - All dependencies are allowed
4. **Documentation consistency** - Metadata matches documentation