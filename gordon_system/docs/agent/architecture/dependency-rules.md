# Gordon Dependency Rules

## Overview

Dependency rules define which packages can import from which other packages and in what contexts.

## Layer Ordering

```
Layer 0: Architecture    (dependency definitions)
Layer 1: Capabilities    (behaviors)
Layer 2: Components      (infrastructure)
Layer 3: Systems         (runtime services)
```

**Rule:** Dependencies flow downward; higher layers may not depend on lower layers.

## Allowed Dependencies

### Architecture Layer

```
architecture/ → (none)     # Pure definitions, no dependencies
```

### Capabilities Layer

```
capabilities/ → architecture/
capabilities/ → components/   # For execution infrastructure
```

### Components Layer

```
components/core/ → systems/      # For system services
components/core/ → (none)       # Pure infrastructure
```

### Systems Layer

```
systems/ → (none)             # Base infrastructure
```

## Import Rules by Package

### Architecture Packages

| Package | Can Import From | Cannot Import From |
|---------|-----------------|-------------------|
| architecture/ | None | All runtime layers |
| capability_map/ | None | Runtime layers, non-architectural packages |
| dependency_graph/ | None | Runtime layers, implementation packages |
| ownership/ | None | Runtime layers, implementation packages |
| topology/ | None | Runtime layers, implementation packages |

### Capabilities Packages

| Package | Can Import From | Cannot Import From |
|---------|-----------------|-------------------|
| capabilities/action/ | architecture/, components/core/ | systems/, other capabilities/ |
| capabilities/agency/ | architecture/, components/core/ | systems/, other capabilities/ |
| capabilities/cognition/ | architecture/, components/core/ | systems/, other capabilities/ |
| capabilities/creativity/ | architecture/, components/core/ | systems/, other capabilities/ |
| capabilities/evolution/ | architecture/, components/core/, systems/memory/ | runtime state, other capabilities/ |
| capabilities/knowledge/ | architecture/, components/core/, systems/memory/ | systems/perception/, other capabilities/ |
| capabilities/learning/ | architecture/, components/core/ | systems/, other capabilities/ |
| capabilities/motivation/ | architecture/, components/core/ | systems/, other capabilities/ |
| capabilities/personality/ | architecture/, components/core/ | systems/, other capabilities/ |

### Components Packages

| Package | Can Import From | Cannot Import From |
|---------|-----------------|-------------------|
| components/core/engine/ | architecture/, systems/ | capabilities/, runtime state |
| components/core/executor/ | architecture/, systems/ | capabilities/ |
| components/core/manager/ | architecture/, systems/ | capabilities/ |

### Systems Packages

| Package | Can Import From | Cannot Import From |
|---------|-----------------|-------------------|
| systems/memory/ | architecture/, None | All other layers |
| systems/perception/ | architecture/, None | All other layers |

## Dependency Direction Matrix

```
            to:
            arch    capa    comp    sys
from:  arch    -       -       -       -
       capa    ✓       -       ✓       -
       comp    ✓       -       -       ✓
       sys     ✓       -       ✓       -
```

Legend:
- `✓` = Allowed dependency direction (from → to)
- `-` = No self-dependency

## Forbidden Dependencies

### Vertical Violations

```
❌ components/ → capabilities/
❌ systems/ → capabilities/
❌ systems/ → architecture/
```

### Horizontal Violations

```
❌ Same-layer dependencies without explicit delegation
❌ Cross-capability dependencies (capabilities must be independent)
```

### Runtime vs. Architecture Violations

```
❌ Implementation code in architecture layer
❌ Runtime state in __tree__.py or __meta__.py
```

## Dependency Resolution Order

1. **Architecture** - Load first, defines structure
2. **Capabilities** - Load second, uses architecture definitions
3. **Components** - Load third, provides infrastructure to capabilities
4. **Systems** - Load last, provides runtime services

## Circular Dependencies

Circular dependencies are forbidden. If A depends on B:
- B cannot depend on A
- No path from B back to A exists in the dependency graph

## Dependency Invariants

1. Every import has an explicit architectural justification
2. All dependencies are downward-facing (higher → lower)
3. No runtime code appears in architecture layer imports
4. Dependencies form a directed acyclic graph (DAG)

## Validation

Dependency rules are validated by:
- Static analysis of import statements
- Graph traversal to detect cycles
- Layer boundary checks on each import