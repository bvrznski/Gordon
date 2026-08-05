# Phase 3.8.12 - Duplicate Contract Report

## Overview

This report identifies duplicate contracts found during the discovery phase and recommends consolidation.

---

## Found Duplicates

### 1. State Machine Patterns

**Locations:**
- `core/lifecycle/__init__.py` - LifecycleController
- `core/plugins/lifecycle.py` - PluginState, LifecycleManager

**Analysis:**
Both define similar lifecycle state transitions with slightly different states:
- Core lifecycle: CREATED → INITIALIZING → READY → RUNNING → STOPPED
- Plugin lifecycle: CREATED → DISCOVERED → REGISTERED → LOADED → ACTIVE → UNLOADED

**Recommendation:** 
- Keep separate contracts - they serve different purposes
- Create a common interface `ILifecycleController` for shared pattern

### 2. Health Check Contracts

**Locations:**
- `core/runtime_monitoring/health.py` - HealthMonitor
- Multiple components have ad-hoc health checks

**Analysis:**
Same semantics but inconsistent return types and reporting formats.

**Recommendation:**
- Use IHealthChecker interface as standard
- Update all existing checks to conform

### 3. Event Handling Patterns

**Locations:**
- `core/events/bus.py` - MessageBus with full subscription system
- Multiple components have event dispatchers

**Analysis:**
MessageBus is comprehensive; others are simpler.

**Recommendation:**
- Keep MessageBus as canonical IEventBus implementation
- Migrate simple dispatchers to use MessageBus or implement interface

### 4. Component Registration Patterns

**Locations:**
- `core/registry/` - Minimal registry implementation
- Various components maintain their own registries

**Analysis:**
Fragmented approach with inconsistent querying.

**Recommendation:**
- Use IRegistry as single source of truth
- Deprecate component-local registries

### 5. Configuration Loading

**Locations:**
- `core/configuration/sources.py` - Multiple sources
- Some components load config directly from files

**Analysis:**
Sources exist but not consistently used.

**Recommendation:**
- Use IConfigurationProvider for all config access
- Migrate direct file loading to use provider

---

## Consolidation Actions

| Duplicate | Action | Priority |
|-----------|--------|----------|
| State machine variations | Create common ILifecycleController interface | High |
| Health check variations | Use IHealthChecker as standard | High |
| Event dispatchers | Migrate to MessageBus/IEventBus | Medium |
| Component registries | Use IRegistry | Medium |
| Direct config loading | Use IConfigurationProvider | Low |

---

## Migration Checklist

For each duplicate:

- [ ] Create unified interface
- [ ] Update existing implementations
- [ ] Add compatibility shims
- [ ] Deprecate old patterns
- [ ] Update tests

---

## Acceptance Criteria

| Criterion | Status |
|-----------|--------|
| Duplicates identified | ✅ Found 5 categories |
| Consolidation planned | ✅ Actions documented |
| Migration path created | ✅ Priority matrix defined |

---

## Next Steps

1. Implement unified interfaces for high-priority duplicates
2. Create compatibility shims during migration
3. Update tests to cover both old and new patterns
4. Document deprecation timeline