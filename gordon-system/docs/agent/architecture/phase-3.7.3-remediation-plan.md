# Phase 3.7.3 Remediation Plan

**Phase**: 3.7.3  
**Date**: August 2, 2026  
**Status**: REMEDIATION PLAN - FOR REVIEW

---

## Executive Summary

Based on detailed analysis of the Phase 3.7.3 audit and repository evidence, this plan identifies:

- **2 findings requiring code changes**
- **5 findings requiring documentation updates**
- **12 findings that are false positives or intentional design**

This document provides concrete implementation steps for the two confirmed issues.

---

## Confirmed Findings Requiring Code Changes

### Issue #1: Type-Safe Context Lookup (HIGH Priority)

**Current State**:
```python
# context/__init__.py line 81-92
def get(self, key: str) -> Optional[Any]:
    """Get a context entry by key."""
    with self._lock:
        return self._entries.get(key)
```

**Problem**: 
- Returns `Optional[Any]` without type safety
- Accepts arbitrary string keys
- No compile-time validation of key types

**Required Fix**:

```python
# Add generic type parameter for type-safe retrieval
from typing import TypeVar, Generic

T = TypeVar("T")

class RuntimeContext:
    def get(self, key: str) -> Optional[Any]:  # Keep existing signature
        """Get entry by string key."""
        with self._lock:
            return self._entries.get(key)
    
    def get_typed(self, key: str, expected_type: type[T]) -> T:
        """
        Get context entry with type validation.
        
        Raises:
            KeyError: If key not found
            TypeError: If value is not of expected type
        """
        with self._lock:
            if key not in self._entries:
                raise KeyError(f"Context key '{key}' not found")
            value = self._entries[key]
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Context entry '{key}' is {type(value).__name__}, "
                    f"expected {expected_type.__name__}"
                )
            return value
```

**Implementation Steps**:
1. Add `get_typed()` method to RuntimeContext class
2. Update all usages of `RuntimeContext.get()` with explicit type checks
3. Document the pattern: "Use get_typed() for runtime-critical dependencies, get() for optional metadata"

---

### Issue #2: BootstrapContext State Schema (HIGH Priority)

**Current State**:
```python
# bootstrap/__init__.py line 278-281
class BootstrapContext:
    environment_facts: Dict[str, Any] = field(default_factory=dict)
    preflight_results: List["PreflightCheckResult"] = field(default_factory=list)
```

**Problem**:
- `environment_facts` uses arbitrary keys without validation
- No schema to define required vs optional facts
- Preflight results list has no validation or bounds checking

**Required Fix**:

```python
# Define environment fact types
@dataclass(frozen=True)
class EnvironmentFactType:
    """Valid environment fact type."""
    name: str
    type_: type
    required: bool = False
    description: str = ""

# Predefined fact types
ENVIRONMENT_FACT_TYPES = {
    "os_version": EnvironmentFactType("os_version", str, True, "Operating system version"),
    "python_version": EnvironmentFactType("python_version", str, True, "Python runtime version"),
    "working_directory": EnvironmentFactType("working_directory", str, True, "Current working directory"),
}

# Add schema validation
@dataclass(frozen=True)
class BootstrapContext:
    # ... existing fields ...
    
    @classmethod
    def create(cls) -> "BootstrapContextBuilder":
        """Create a new context builder with default schema."""
        return BootstrapContextBuilder()

@dataclass(frozen=True)
class ValidatedEnvironmentFacts:
    """Validated environment facts conforming to schema."""
    os_version: str
    python_version: str
    working_directory: str
    # Extend as needed with additional fact types

# Add validation method
def validate_environment_facts(
    raw_facts: Dict[str, Any]
) -> ValidatedEnvironmentFacts:
    """Validate facts against schema, raise error on missing required facts."""
    validated = {}
    for name, fact_type in ENVIRONMENT_FACT_TYPES.items():
        if fact_type.required and name not in raw_facts:
            raise ValueError(f"Missing required environment fact: {name}")
        if name in raw_facts:
            value = raw_facts[name]
            if not isinstance(value, fact_type.type_):
                raise TypeError(
                    f"Environment fact '{name}' expected {fact_type.type_.__name__}, "
                    f"got {type(value).__name__}"
                )
            validated[name] = value
    return ValidatedEnvironmentFacts(**validated)
```

**Implementation Steps**:
1. Define `ENVIRONMENT_FACT_TYPES` mapping with schema definitions
2. Add `validate_environment_facts()` function
3. Create `ValidatedEnvironmentFacts` dataclass
4. Update `BootstrapContext` to use validated facts where applicable

---

## Findings Requiring Documentation Updates

### Issue #3: Construction/Activation Separation (MEDIUM Priority)

**Current State**: 
- Kernel constructor initializes state
- `start_all_services()` activates kernel

**Required Action**: Add explicit documentation of phase boundaries.

```python
class Kernel:
    """
    Core kernel - coordinates runtime infrastructure.
    
    Lifecycle Phases:
        1. CONSTRUCTION: __init__() → Kernel instance (not running)
        2. REGISTRATION: register_service() → Services added to registry
        3. ACTIVATION: start_all_services() → Kernel becomes running
        4. SHUTDOWN: stop_all_services() → Kernel becomes not running
        
    Important: Construction and activation are separate phases.
    A kernel may be constructed but not yet activated.
    """
```

**Status**: Document only, no code changes needed.

---

## Implementation Priority Matrix

| Issue | Severity | Code Changes Required? | Estimated Effort |
|-------|----------|------------------------|------------------|
| Type-safe context lookup | HIGH | ✅ Yes | 2-3 hours |
| BootstrapContext schema | HIGH | ✅ Yes | 3-4 hours |
| Construction/activation docs | MEDIUM | ⚠️ Documentation only | 1 hour |

**Total Estimated Effort**: 6-8 hours

---

## Risk Assessment

### Issue #1: Type-Safe Context Lookup
- **Risk Level**: LOW
- **Impact**: Breaking change for code using `RuntimeContext.get()`
- **Mitigation**: Keep existing signature, add new typed method alongside

### Issue #2: BootstrapContext Schema
- **Risk Level**: MEDIUM
- **Impact**: May require updates to bootstrap pipeline callers
- **Mitigation**: Provide backward-compatible validation wrapper first

---

## Testing Strategy

For each issue:

1. **Unit Tests**:
   - Test `get_typed()` with correct type (returns value)
   - Test `get_typed()` with wrong type (raises TypeError)
   - Test `get_typed()` with missing key (raises KeyError)

2. **Integration Tests**:
   - Validate bootstrap context creation
   - Test validation of environment facts
   - Verify schema evolution works correctly

---

## Acceptance Criteria

### Issue #1: Type-Safe Context Lookup
- [ ] `RuntimeContext.get_typed()` method implemented and tested
- [ ] All internal usages updated to use typed retrieval
- [ ] Documentation updated with pattern guidance
- [ ] No runtime type errors in context lookups

### Issue #2: BootstrapContext Schema
- [ ] Environment fact types defined
- [ ] Validation function implemented
- [ ] Validated facts structure created
- [ ] Bootstrap pipeline uses validated facts
- [ ] Backward compatibility maintained where needed

---

## Rollback Strategy

Both changes are additive:
1. New methods added without modifying existing behavior
2. Existing code continues to work with deprecation warnings (if desired)
3. Migration can happen incrementally per module

---

*End of Phase 3.7.3 Remediation Plan*