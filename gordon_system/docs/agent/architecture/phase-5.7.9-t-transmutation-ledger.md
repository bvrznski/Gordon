# Gordon Phase 5.7.9-T: Consciousness Transmutation Ledger

## Executive Summary

This document records all transmutation units for the migration of Gordon's
Consciousness implementation from `src/agent/capabilities/consciousness/` to
`src/agent/components/systems/consciousness/`.

**Transmutation Date**: 2026-08-17  
**Phase**: 5.7.9-T  
**Classification Before**: First-class capability implementation  
**Classification After**: First-class system implementation  

---

## Repository Baseline

| Item | Value |
|------|-------|
| Git Commit Hash | `0f2c03b7c358898d54983ebe403dca43d5e8df40` |
| Working Directory | `/home/bvrznski/Gordon/gordon_system` |
| Repository Status | Clean (all changes committed) |

---

## Pre-Transmutation Inventory

### Source Package: `src/agent/capabilities/consciousness/`

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 246 | Package entry point with imports and exports |
| `config.py` | ? | Configuration classes |
| `constants.py` | ? | Enumerations and constants |
| `contracts.py` | ? | Interface contracts |
| `exceptions.py` | ? | Exception hierarchy |
| `facade.py` | 566 | Public facade class |
| `identities.py` | ? | Identity generators and validators |
| `registry.py` | ? | Registry classes for sources/extensions |
| `types.py` | ? | Type definitions |
| `README.md` | ? | Package documentation |

### Submodules

| Module | Purpose |
|--------|---------|
| `experiential_field/` | Field construction, validation, transitions |
| `intentionality/` | Intentional context implementation |
| `temporality/` | Temporal continuity, retention, protention |
| `presence/` | Presence state and dynamics |
| `perspective/` | Observer perspective and self-reference |
| `situated_world/` | World model and affordance representation |
| `integration/` | Composite context coordination |

---

## Transmutation Units

### Unit 0: System Interface Definition (Already Present)

**Source**: Already at `src/agent/components/systems/consciousness/interfaces.py`  
**Status**: PRE-EXISTING SCAFFOLDING

```python
SYSTEM_ID = "system.consciousness"
CAPABILITY_ID = "capability.consciousness"
```

---

### Unit 1: Core Infrastructure Modules

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/__init__.py` | `systems/consciousness/__init__.py` | All exports |
| `capabilities/consciousness/config.py` | `systems/consciousness/config.py` | ConsciousnessConfiguration |
| `capabilities/consciousness/constants.py` | `systems/consciousness/constants.py` | ContextState, HealthState, etc. |
| `capabilities/consciousness/exceptions.py` | `systems/consciousness/exceptions.py` | All exception classes |
| `capabilities/consciousness/types.py` | `systems/consciousness/types.py` | All type definitions |

**Deprecation Strategy**: Import compatibility layer at old path  
**Removal Criteria**: All consumers migrated to new path

---

### Unit 2: Identity System

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/identities.py` | `systems/consciousness/identities.py` | All identity generators |

---

### Unit 3: Contract System

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/contracts.py` | `systems/consciousness/contracts.py` | All contract classes |

---

### Unit 4: Registry System

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/registry.py` | `systems/consciousness/registry.py` | SourceRegistry, ExtensionRegistry |

---

### Unit 5: Public Facade

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/facade.py` | `systems/consciousness/facade.py` | ConsciousnessFacade |

---

### Unit 6: Experiential Field Module

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/experiential_field/__init__.py` | `systems/consciousness/experiential_field/__init__.py` | All exports |
| `capabilities/consciousness/experiential_field/builder.py` | `systems/consciousness/experiential_field/builder.py` | ExperientialFieldBuilder |
| `capabilities/consciousness/experiential_field/constants.py` | `systems/consciousness/experiential_field/constants.py` | Constants |
| `capabilities/consciousness/experiential_field/integrity.py` | `systems/consciousness/experiential_field/integrity.py` | Integrity enforcer |
| `capabilities/consciousness/experiential_field/normalization.py` | `systems/consciousness/experiential_field/normalization.py` | Normalizer |
| `capabilities/consciousness/experiential_field/ordering.py` | `systems/consciousness/experiential_field/ordering.py` | Ordering |
| `capabilities/consciousness/experiential_field/snapshot.py` | `systems/consciousness/experiential_field/snapshot.py` | ExperientialFieldSnapshot |
| `capabilities/consciousness/experiential_field/transition.py` | `systems/consciousness/experiential_field/transition.py` | FieldTransition |
| `capabilities/consciousness/experiential_field/types.py` | `systems/consciousness/experiential_field/types.py` | ExperientialFieldId, etc. |
| `capabilities/consciousness/experiential_field/validation.py` | `systems/consciousness/experiential_field/validation.py` | Validation types |

---

### Unit 7: Intentionality Module

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/intentionality/__init__.py` | `systems/consciousness/intentionality/__init__.py` | All exports |
| `capabilities/consciousness/intentionality/engine.py` | `systems/consciousness/intentionality/engine.py` | IntentionalContextEngine |
| `capabilities/consciousness/intentionality/object.py` | `systems/consciousness/intentionality/object.py` | IntentionalObject |
| `capabilities/consciousness/intentionality/relation.py` | `systems/consciousness/intentionality/relation.py` | IntentionalRelation |
| `capabilities/consciousness/intentionality/snapshot.py` | `systems/consciousness/intentionality/snapshot.py` | IntentionalContextSnapshot |
| `capabilities/consciousness/intentionality/transition.py` | `systems/consciousness/intentionality/transition.py` | IntentionalTransition |
| `capabilities/consciousness/intentionality/target.py` | `systems/consciousness/intentionality/target.py` | IntentionalTarget |
| `capabilities/consciousness/intentionality/diagnostics.py` | `systems/consciousness/intentionality/diagnostics.py` | Diagnostics snapshot |
| `capabilities/consciousness/intentionality/integrity.py` | `systems/consciousness/intentionality/integrity.py` | IntentionalIntegrityEnforcer |

---

### Unit 8: Temporality Module

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/temporality/__init__.py` | `systems/consciousness/temporality/__init__.py` | All exports |
| `capabilities/consciousness/temporality/constants.py` | `systems/consciousness/temporality/constants.py` | Constants |
| `capabilities/consciousness/temporality/continuity_window.py` | `systems/consciousness/temporality/continuity_window.py` | ContinuityWindow |
| `capabilities/consciousness/temporality/diagnostics.py` | `systems/consciousness/temporality/diagnostics.py` | Diagnostics snapshot |
| `capabilities/consciousness/temporality/engine.py` | `systems/consciousness/temporality/engine.py` | TemporalContextEngine |
| `capabilities/consciousness/temporality/exceptions.py` | `systems/consciousness/temporality/exceptions.py` | Exception classes |
| `capabilities/consciousness/temporality/health.py` | `systems/consciousness/temporality/health.py` | Health snapshot |
| `capabilities/consciousness/temporality/integrity.py` | `systems/consciousness/temporality/integrity.py` | Integrity enforcer |
| `capabilities/consciousness/temporality/presentation.py` | `systems/consciousness/temporality/presentation.py` | Presentation layer |
| `capabilities/consciousness/temporality/protention.py` | `systems/consciousness/temporality/protention.py` | Protention (future anticipation) |
| `capabilities/consciousness/temporality/retention.py` | `systems/consciousness/temporality/retention.py` | Retention (past memory) |
| `capabilities/consciousness/temporality/snapshot.py` | `systems/consciousness/temporality/snapshot.py` | TemporalContextSnapshot |
| `capabilities/consciousness/temporality/transition.py` | `systems/consciousness/temporality/transition.py` | TemporalTransition |
| `capabilities/consciousness/temporality/types.py` | `systems/consciousness/temporality/types.py` | Type definitions |
| `capabilities/consciousness/temporality/validator.py` | `systems/consciousness/temporality/validator.py` | Validator |

---

### Unit 9: Presence Module

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/presence/__init__.py` | `systems/consciousness/presence/__init__.py` | All exports |
| `capabilities/consciousness/presence/admission.py` | `systems/consciousness/presence/admission.py` | Admission control |
| `capabilities/consciousness/presence/constants.py` | `systems/consciousness/presence/constants.py` | Constants |
| `capabilities/consciousness/presence/diagnostics.py` | `systems/consciousness/presence/diagnostics.py` | Diagnostics snapshot |
| `capabilities/consciousness/presence/engine.py` | `systems/consciousness/presence/engine.py` | PresenceEngine |
| `capabilities/consciousness/presence/exceptions.py` | `systems/consciousness/presence/exceptions.py` | Exception classes |
| `capabilities/consciousness/presence/fading.py` | `systems/consciousness/presence/fading.py` | Fading dynamics |
| `capabilities/consciousness/presence/integrity.py` | `systems/consciousness/presence/integrity.py` | Integrity enforcer |
| `capabilities/consciousness/presence/persistence.py` | `systems/consciousness/presence/persistence.py` | Persistence layer |
| `capabilities/consciousness/presence/snapshot.py` | `systems/consciousness/presence/snapshot.py` | PresenceSnapshot |
| `capabilities/consciousness/presence/state.py` | `systems/consciousness/presence/state.py` | PresenceState |
| `capabilities/consciousness/presence/transition.py` | `systems/consciousness/presence/transition.py` | PresenceTransition |

---

### Unit 10: Perspective Module

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/perspective/__init__.py` | `systems/consciousness/perspective/__init__.py` | All exports |
| `capabilities/consciousness/perspective/constants.py` | `systems/consciousness/perspective/constants.py` | Constants |
| `capabilities/consciousness/perspective/diagnostics.py` | `systems/consciousness/perspective/diagnostics.py` | Diagnostics snapshot |
| `capabilities/consciousness/perspective/engine.py` | `systems/consciousness/perspective/engine.py` | PerspectiveEngine |
| `capabilities/consciousness/perspective/exceptions.py` | `systems/consciousness/perspective/exceptions.py` | Exception classes |
| `capabilities/consciousness/perspective/observer.py` | `systems/consciousness/perspective/observer.py` | Observer definition |
| `capabilities/consciousness/perspective/reference_frame.py` | `systems/consciousness/perspective/reference_frame.py` | Reference frame |
| `capabilities/consciousness/perspective/self_reference.py` | `systems/consciousness/perspective/self_reference.py` | Self-reference model |
| `capabilities/consciousness/perspective/snapshots.py` | `systems/consciousness/perspective/snapshots.py` | Perspective snapshots |
| `capabilities/consciousness/perspective/transformations.py` | `systems/consciousness/perspective/transformations.py` | Transformations |
| `capabilities/consciousness/perspective/transitions.py` | `systems/consciousness/perspective/transitions.py` | Perspective transitions |
| `capabilities/consciousness/perspective/validator.py` | `systems/consciousness/perspective/validator.py` | Validator |

---

### Unit 11: Situated World Module

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/situated_world/__init__.py` | `systems/consciousness/situated_world/__init__.py` | All exports |
| `capabilities/consciousness/situated_world/builder.py` | `systems/consciousness/situated_world/builder.py` | WorldBuilder |
| `capabilities/consciousness/situated_world/constants.py` | `systems/consciousness/situated_world/constants.py` | Constants |
| `capabilities/consciousness/situated_world/engine.py` | `systems/consciousness/situated_world/engine.py` | SituatedWorldEngine |
| `capabilities/consciousness/situated_world/exceptions.py` | `systems/consciousness/situated_world/exceptions.py` | Exception classes |
| `capabilities/consciousness/situated_world/models/__init__.py` | `systems/consciousness/situated_world/models/__init__.py` | All model exports |
| `capabilities/consciousness/situated_world/models/affordance.py` | `systems/consciousness/situated_world/models/affordance.py` | Affordance model |
| `capabilities/consciousness/situated_world/models/constraint.py` | `systems/consciousness/situated_world/models/constraint.py` | Constraint model |
| `capabilities/consciousness/situated_world/models/entity.py` | `systems/consciousness/situated_world/models/entity.py` | Entity model |
| `capabilities/consciousness/situated_world/models/relation.py` | `systems/consciousness/situated_world/models/relation.py` | Relation model |
| `capabilities/consciousness/situated_world/snapshot.py` | `systems/consciousness/situated_world/snapshot.py` | SituatedWorldSnapshot |
| `capabilities/consciousness/situated_world/transition.py` | `systems/consciousness/situated_world/transition.py` | WorldTransition |
| `capabilities/consciousness/situated_world/types.py` | `systems/consciousness/situated_world/types.py` | Type definitions |

---

### Unit 12: Integration Module

| Source | Destination | Symbols |
|--------|-------------|---------|
| `capabilities/consciousness/integration/__init__.py` | `systems/consciousness/integration/__init__.py` | All exports |
| `capabilities/consciousness/integration/constants.py` | `systems/consciousness/integration/constants.py` | Constants |
| `capabilities/consciousness/integration/dependencies.py` | `systems/consciousness/integration/dependencies.py` | Dependency graph |
| `capabilities/consciousness/integration/diagnostics.py` | `systems/consciousness/integration/diagnostics.py` | Composite diagnostics snapshot |
| `capabilities/consciousness/integration/health.py` | `systems/consciousness/integration/health.py` | Composite health snapshot |
| `capabilities/consciousness/integration/composition.py` | `systems/consciousness/integration/composition.py` | Composite snapshot builder |
| `capabilities/consciousness/integration/coordinator.py` | `systems/consciousness/integration/coordinator.py` | IntegrationCoordinator |
| `capabilities/consciousness/integration/types.py` | `systems/consciousness/integration/types.py` | Type definitions |
| `capabilities/consciousness/integration/validation.py` | `systems/consciousness/integration/validation.py` | Cross-engine validator |

---

## Consumer Inventory

### Direct Consumers

| File | Imports | Migration Required |
|------|---------|-------------------|
| `tests/test_experiential_field_foundation.py` | ExperientialFieldBuilder, FieldContent, etc. | YES |
| `tests/test_intentional_context_engine.py` | IntentionalContextEngine, etc. | YES |

### Test Migration Strategy

Tests will be migrated from:
- `tests/test_*.py` → `tests/agent/components/systems/consciousness/`

---

## Compatibility Strategy

Temporary compatibility layer at `src/agent/capabilities/consciousness/__init__.py`:

```python
# Deprecated import compatibility - Phase 5.7.9-T migration
from agent.components.systems.consciousness import (
    ConsciousnessFacade,
    ConsciousnessConfiguration,
    ContextState,
    # ... all public exports
)

__all__ = ["ConsciousnessFacade", "ConsciousnessConfiguration", ...]
```

**Deprecation Status**: ACTIVE  
**Migration Target**: All consumers use `agent.components.systems.consciousness`  
**Removal Criteria**: All imports migrated, tests updated

---

## Status Tracking

| Unit | Status | Notes |
|------|--------|-------|
| 0 (System Interface) | PRE-EXISTING | Interfaces.py already in place |
| 1-12 (Core Modules) | PLANNED | Pending file migration |
| Consumer Tests | PENDING | Migration after module move |

---

## Next Steps

1. Create destination package structure
2. Copy core modules to `systems/consciousness/`
3. Update internal imports within each module
4. Create compatibility layer at old path
5. Migrate test files
6. Update capability map metadata
7. Run full regression tests
8. Document final state

---

*End of Transmutation Ledger*