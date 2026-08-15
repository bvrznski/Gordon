# Focusing Network

**Status:** 🟢 **ARCHITECTURAL FREEZE COMPLETE (v1.0.0)**  
**Phase:** 4.2.7 - 4.2.14  
**Last Updated:** August 14, 2026

---

## Overview

The Focusing Network is Gordon's endogenous attention-policy computation network. It determines what deserves sustained attention, how strongly, for how long, with what precision, and under which constraints - without executing actions or owning cognition itself.

### Freeze Status

> **ARCHITECTURAL FREEZE** - The Focusing Network architecture is stable and frozen as of August 14, 2026. All public contracts, ownership boundaries, dependency graph, and computational pipeline are immutable unless changed through formal architectural revision.

---

## Architecture

```
External Systems (Attention, Executive, etc.)
    ↓ (depend on contracts)
Focusing Contracts (interfaces only)
    ↓
Focusing Network (orchestration + models)
    ↓
Internal Subsystems (delegated algorithms)
```

### Responsibilities

The Focusing Network owns:

- Endogenous attentional computation
- Goal-directed priority estimation
- Focus competition analysis
- Suppression estimation
- Precision estimation
- Persistence estimation
- Computational budgeting recommendations
- Attentional bias recommendations
- Confidence estimation
- Explainable FocusAssessment production

The Focusing Network does NOT own:

- Behavioral policy (Executive Layer)
- Planning (Planning Capability)
- Reasoning (Reasoning Capability)
- Execution (Execution Layer)
- Thread/Loop/Cycle management (Core Runtime)

---

## Package Structure

```
focusing/
├── __init__.py              # Main exports (Phase 4.2.7-4.2.9)
├── __meta__.py              # Version metadata (v1.0.0)
├── __tree__.py              # Architecture tree
├── enums.py                 # Enumerations
├── constants.py             # Default values and bounds
├── configuration.py         # Immutable configuration
├── protocol.py              # Protocol definitions
├── models.py                # Data models (Phase 4.2.2)
├── pipeline.py              # Pipeline executor (Phase 4.2.7)
├── network.py               # Main orchestration (Phase 4.2.7)
└── diagnostics.py           # Diagnostics infrastructure

Subsystems:
├── contracts/               # Interface contracts (Phase 4.2.8)
├── executive/               # Executive interaction contracts (Phase 4.2.9)
└── [algorithmic modules]    # Delegated computation
```

---

## Public API

### Core Contracts

| Contract | Description |
|----------|-------------|
| `FocusingNetwork` | Main network entry point |
| `ExecutiveFocusProjection` | Executive input projections |
| `FocusAssessment` | Advisory computational assessment |

### Data Models

- `FocusTarget`, `FocusCandidate` - Immutable focus representations
- `PriorityDescriptor`, `RelevanceDescriptor`, etc. - Assessment descriptors
- `FocusState`, `FocusingNetworkState` - State containers
- `StateTransition`, `FocusSnapshot` - Transition tracking

### Enums

- `FocusModality` - Attention modality types
- `FocusSource` - Target origin types
- `PriorityLevel` - Priority classification
- `PrecisionBandwidth` - Bandwidth allocation levels
- `PersistenceMode` - Focus maintenance strategies

---

## Integration Points

The Focusing Network integrates with:

| System | Integration Point |
|--------|-------------------|
| Alerting Network | Exogenous signal coordination |
| Attention Capability | Focus selection from recommendations |
| Executive Layer | Objective projections and commitment decisions |
| Planning Capability | Plan step priority estimation |
| Reasoning Capability | Reasoning output focus estimation |
| Working Memory | WM item priority estimation |
| Perception | Perceptual target priority estimation |

---

## Documentation

| Document | Purpose |
|----------|---------|
| [Reference Flows](reference_flows.md) | Behavioral reference patterns |
| [Phase 4.2.13 Certification](../phase-4.2.13-certification-report.md) | Previous certification report |
| [Phase 4.2.14 Freeze](../phase-4.2.14-architectural-freeze.md) | This freeze declaration |

---

## Version Information

- **Package Version:** 1.0.0
- **Contracts Version:** 1.0.0
- **Architecture Phase:** 4.2.7 - 4.2.14
- **Status:** STABLE (architectural freeze)

---

## Extension Policy

The Focusing Network supports additive-only extension through:

- New priority computation models
- New precision estimation algorithms
- New competition resolution strategies
- New diagnostics and tracing capabilities

See [Phase 4.2.14 Freeze](../phase-4.2.14-architectural-freeze.md) for complete extension guidelines.

---

**Last Updated:** August 14, 2026  
**Architectural Status:** FROZEN v1.0.0