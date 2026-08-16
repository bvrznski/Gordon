# Oriented Network

**Phase 4.7.1: Scaffold, Legacy Retirement, Architectural Foundation**

## Canonical Definition

The OrientedNetwork is Gordon's cognitive coordination network responsible for
maintaining persistent intentional orientation toward active Goals, objectives,
tasks, constraints, missions, and externally directed cognition.

It coordinates independent cognitive capabilities while preserving strict ownership
boundaries. The subsystem maintains semantic orientation without owning the
cognitive algorithms themselves.

## Architectural Role

- **Layer**: Cognitive Network Layer
- **Responsibility**: Orientation coordination (not implementation)
- **Boundary**: Coordinates cognition; never owns it

## Package Status

| Field | Value |
|-------|-------|
| Name | oriented |
| Display Name | Oriented Network |
| Phase | 4.7.1 |
| Status | scaffold |

## What This Phase Implements

This is the scaffold phase:

- Canonical package structure and metadata
- Minimal public API with stable imports
- Configuration scaffold (no behavioral parameters)
- State scaffold (no semantic content)
- Error root type for future extensions
- Abstract base class for lifecycle contracts

## What Remains Deferred

Future phases will implement:

- Phase 4.7.2: Orientation Content, Context, Scope, Horizon
- Phase 4.7.3: Activation, Engagement, and Orientation Modes
- Phase 4.7.4: Goal, Objective, Task, and Constraint Coordination
- Phase 4.7.5: Executive, Strategy, Planning, Reasoning, and Decision Integration
- Phase 4.7.6: Attention, Alerting, Focusing, Motivation, and Salience Coordination
- Phase 4.7.7: Working Memory, Workspace, and Context Availability Integration
- Phase 4.7.8: Cognitive Load, Capacity, and Resource Request Semantics
- And more... (see docs/agent/architecture/networks/oriented/roadmap.md)

## Why Not Migrate the Legacy Package?

The Oriented Network was constructed from scratch according to Gordon's current
architecture. The previous Directed and Task Positive Network artifacts were used
only to identify concepts and migration requirements.

**Legacy names retired:**
- `directed`
- `Directed Network`
- `Task Positive Network`
- `TPN`

## Compatibility Policy

This phase establishes the canonical package identity. Any compatibility aliases
for legacy names are isolated in a separate module and have removal criteria.

## Public API (Phase 4.7.1)

```python
from gordon_system.src.agent.components.networks.oriented import (
    OrientedNetwork,
    BaseOrientedNetwork,
    OrientedNetworkConfiguration,
    OrientedNetworkState,
    OrientedNetworkError,
)
```

See `__init__.py` for the complete export list.

## Architecture Laws

- **ORIENTED-NETWORK-LAW-001**: The Oriented Network owns intentional orientation.
- **ORIENTED-NETWORK-LAW-002**: The Oriented Network coordinates cognition; never implements it.
- **ORIENTED-NETWORK-LAW-003**: Configuration is deeply immutable.
- **ORIENTED-NETWORK-LAW-004**: State is deeply immutable.
- **ORIENTED-NETWORK-LAW-005**: No cognitive capability implementation in this phase.

See `architecture.md` for the complete architectural constitution.