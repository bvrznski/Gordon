# Default Network

**Canonical Name:** `DefaultNetwork`  
**Category:** Network  
**Phase:** 4.3.1  
**Status:** SCAFFOLD COMPLETE

## Overview

The Default Network is Gordon's internally oriented cognitive coordination network.
It becomes relevant when processing is driven primarily by internally available
context rather than immediate externally driven demand.

### Neuroscience Analogy (Descriptive Only)

The Default Network corresponds conceptually to the brain's **Default Mode Network (DMN)**,
which is active during rest, daydreaming, and internally focused thought. This is
provided as descriptive context only - the canonical implementation name remains
`DefaultNetwork`.

## Architectural Role

The Default Network coordinates internally oriented cognitive processes that do not
require immediate external action. It answers:

> **Which internally oriented cognitive processes should currently be coordinated,
> combined, emphasized, or proposed?**

### What it DOES:
- Coordinate memory-driven association and reactivation
- Propose reflection and self-referential processing
- Generate prospective/counterfactual simulations
- Integrate narrative continuity
- Resurface and incubate unresolved goals
- Coordinate spontaneous internally generated cognition

### What it does NOT do:
- **NOT** determine when execution physically runs (Runtime's responsibility)
- **NOT** decide which worker or accelerator should execute (Scheduling's responsibility)
- **NOT** determine which thread should be scheduled (Thread management's responsibility)
- **NOT** persist state to Memory (Memory's responsibility)
- **NOT** determine what becomes conscious (Consciousness's responsibility)
- **NOT** authorize external action (Action's responsibility)

## Public API

```python
from gordon_system.src.agent.networks.default import DefaultNetwork, DefaultInput, DefaultOutput

# Create a network instance
network = DefaultNetwork.create()

# Process inputs and get proposals
inputs = (
    DefaultInput(...),  # Your input data here
)

result = network.assess(inputs)
```

### Main Components:

| Component | Purpose |
|-----------|---------|
| `DefaultNetwork` | Primary orchestration class |
| `DefaultInput` | Immutable input contract |
| `DefaultOutput` | Semantic output proposal/assessment |
| `DefaultProposalSet` | Complete set of proposals from one assessment |
| `DefaultNetworkConfig` | Immutable semantic configuration |

## Core Principles

### 1. Semantic Computation Only
The Default Network is a **semantic computational component**. It produces and consumes
immutable semantic values (proposals, assessments) - not runtime commands.

### 2. No Runtime Machinery
- No thread spawning
- No loop execution
- No resource allocation
- No scheduler interaction
- No blocking I/O operations

### 3. No System Ownership
The Default Network does NOT own or mutate:
- Memory state
- Consciousness state  
- Action authorization
- Execution scheduling
- Runtime resources

### 4. Bounded State
All state is explicitly bounded and finite. No unbounded data structures.

## Inputs (Immutable & Bounded)

The network receives projections from other systems as immutable inputs:

| Input Type | Purpose |
|-----------|---------|
| `DefaultInput` | Single input unit for assessment |
| `DefaultInputBatch` | Collection of inputs for collective processing |
| `DefaultProvenance` | Provenance tracking without runtime references |

### Semantic Input Sources:
- Memory projections (autobiographical, associative)
- Consciousness projections (current focus, attentional state)
- Cognition projections (active reasoning, predictions)
- Goal projections (unresolved goals, priorities)

## Outputs (Proposals & Assessments)

The network emits proposals that other systems may consider:

| Output Type | Purpose |
|-------------|---------|
| `InternalAttentionProposal` | Coordinated internal attention patterns |
| `AssociationProposal` | Memory-driven associative activation candidates |
| `MemoryReactivationProposal` | Memories to reactivate for integration |
| `ReflectionProposal` | Self-referential processing candidates |
| `SimulationProposal` | Prospective/counterfactual simulation scenarios |
| `NarrativeIntegrationProposal` | Narrative continuity proposals |
| `UnresolvedGoalProposal` | Goal resurfacing and incubation candidates |
| `ContextReintegrationProposal` | Background context recombination |

### Important: Proposals ARE NOT Commands
Outputs are **semantic proposals** that other systems may consider. They do NOT:
- Command execution
- Authorize action
- Allocate resources

## Activation Model

Activation represents the degree of internally oriented processing that is relevant:

- **0.0** = No internal processing needed (external demand only)
- **1.0** = Maximum internally oriented processing appropriate

Activation is computed from:
- Memory-driven associative pressure
- Reflection demand
- Simulation requirements
- Narrative integration needs
- Unresolved goal activity

### Important: Activation ≠ Runtime State
Network activation does NOT mean:
- CPU utilization
- Thread priority
- GPU allocation

## Configuration (Semantic Only)

Configuration contains only semantic network parameters:

| Configuration | Purpose |
|---------------|---------|
| `ActivationThresholds` | When to activate internal processing |
| `AssociationConfig` | Associative memory strength bounds |
| `NarrativeConfig` | Narrative maintenance parameters |
| `ReflectionConfig` | Reflection processing thresholds |
| `SimulationConfig` | Simulation generation limits |
| `GoalConfig` | Goal resurfacing parameters |

Configuration is immutable and validated at construction.

## Boundary Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Integration/Composition                   │
│              (knows both Core and DefaultNetwork)           │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┴──────────────┐
         │                        │
┌────────▼─────────┐    ┌────────▼────────────┐
│   Runtime/Core   │    │  DefaultNetwork     │
│ (mechanics)      │◄───┤ (semantics)         │
└──────────────────┘    └─────────────────────┘
```

### The Rule:
- **Runtime/Core** knows mechanics (scheduling, resources, execution)
- **DefaultNetwork** knows semantics (proposals, assessments, coordination)
- **Integration** knows both and composes them

## Testing

```python
# Run tests
pytest gordon_system/tests/test_default_network_4_3_1.py -v
```

### Test Categories:
- Import structure tests (verify no Core dependency)
- Immutability tests (frozen dataclasses)
- Validation tests (input/output bounds)
- Health state tests
- Diagnostics collection tests

## Future Phases

Phase 4.3.1 establishes the scaffold. Future phases will add:

| Phase | Focus |
|-------|-------|
| 4.3.2 | Algorithm implementations |
| 4.3.3 | Performance optimization |
| 4.3.4 | Integration with Runtime |

## Files

```
gordon_system/src/agent/networks/default/
├── __init__.py         # Package exports (DefaultNetwork)
├── __meta__.py         # Package metadata
├── __tree__.py         # Architecture tree navigation
├── types.py            # Core type definitions
├── config.py           # Semantic configuration
├── state.py            # Bounded computational state
├── inputs.py           # Immutable input contracts
├── outputs.py          # Semantic output proposals
├── activation.py       # Activation model
├── policy.py           # Semantic policy decisions
├── ports.py            # Network-facing semantic ports
├── diagnostics.py      # Bounded diagnostic records
├── health.py           # Health state definitions
├── validation.py       # Input/output validation
├── exceptions.py       # Semantic exceptions
└── network.py          # Main orchestration (DefaultNetwork)
```

## License

MIT - Gordon AI Research