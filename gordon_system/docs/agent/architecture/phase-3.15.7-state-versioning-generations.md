# Gordon Phase 3.15.7: State Versioning & Generations

**Phase Status:** Production Implementation  
**Date:** August 2026  
**Version:** 3.15.7  
**Canonical Location:** `/src/agent/components/core/state/versioning/`

---

## Executive Summary

Phase 3.15.7 establishes the canonical architecture governing state versioning and generations throughout Gordon Core:

- **One Canonical Versioning Architecture**: Single source of truth for all state evolution tracking
- **Identity, Version, Generation Distinction**: Three separate dimensions never interchangeable
- **Deterministic Progression**: No skipped versions, no duplicate generations
- **Lineage Integrity**: Every version/generation tracks its origin and predecessor

This phase extends:

* Phase 3.15.1 — Core State Foundations  
* Phase 3.15.2 — State Identity, Scope & Ownership  
* Phase 3.15.3 — Immutable & Mutable State Semantics  
* Phase 3.15.4 — Runtime State Hierarchy  
* Phase 3.15.5 — State Transitions & Transition Validation  
* Phase 3.15.6 — State Snapshots & Views  

---

## Architectural Principles

### Core Distinctions

| Concept | Answers | Never Changes |
|---------|---------|---------------|
| **Identity** | Which state aggregate is this? | Mutation, transition, update, snapshot creation |
| **Version** | Which revision of this aggregate? | Runtime restart, component recreation |
| **Generation** | Which lifetime/epoch epoch does this belong to? | Version changes within same generation |

### Immutability

- All versioning artifacts are immutable once created
- No direct mutation - only successor creation through canonical APIs
- History remains append-only (never modify existing entries)

---

## Version Identity Architecture

### VersionIdentity

```python
@dataclass(frozen=True, order=True)
class VersionIdentity:
    value: str           # Unique identifier with sequence info
    sequence: int        # 0 for initial, incrementing successors
    aggregate_id: Optional[str]
```

**Properties:**
- Deterministic from sequence number
- No two versions share the same ID within a generation
- Immutable once created

---

## Generation Identity Architecture

### GenerationIdentity

```python
@dataclass(frozen=True, order=True)
class GenerationIdentity:
    value: str      # Unique identifier with epoch info
    epoch: int      # 0 for initial, incrementing on restart
```

**Properties:**
- Monotonically increasing (epoch-based)
- Stale generations rejected for mutations
- Changes only on: runtime restart, component recreation, migration

---

## Version Progression Model

### Lineage Rules

1. **Initial Version**: sequence=0, no predecessor
2. **Successor Rule**: successor.sequence = predecessor.sequence + 1
3. **No Gaps**: All sequences within generation must be consecutive
4. **One Successor**: Each mutation produces exactly one successor version

### Example Lineage

```
Aggregate: "my-aggregate"
Generation: 0

Version 0 (initial)
    ↓ (transition A)
Version 1 → (transition B)  
    ↓
Version 2 → (transition C)
    ↓
... and so on
```

---

## Generation Progression Model

### Lineage Rules

1. **Initial Generation**: epoch=0, no predecessor
2. **Successor Rule**: successor.epoch = predecessor.epoch + 1
3. **No Gaps**: All epochs must be consecutive within runtime lineage
4. **Stale Detection**: Generations older than current are rejected

### Stale Detection

```python
def is_stale(self, current_epoch: int) -> bool:
    return self.epoch < current_epoch
```

---

## Version vs Generation Relationship

| Action | Version Change? | Generation Change? |
|--------|-----------------|-------------------|
| Normal mutation | Yes (+1) | No |
| Runtime restart | Restart from 0 | Yes (+1) |
| Component recreation | Restart from 0 | Yes (+1) |
| Migration | May restart | Yes (+1) |
| Recovery (same runtime) | Yes (+1) | No |

**Policy**: Versions always increment within a generation. On generation change, version numbering restarts at 0.

---

## Lineage Integrity Validation

### Version Lineage Validation

```python
def validate_add_version(self, new_version: BaseStateVersion) -> VersionValidationResult:
    # Check aggregate ID matches
    # Check sequence is consecutive (no gaps)
    # Check predecessor matches latest version in lineage
    # Check generation matches current generation
```

**Outcomes:**
- VALID - All checks passed
- LINEAGE_INTEGRITY_VIOLATED - Some validation failed

### Generation Lineage Validation

```python
def validate_add_generation(self, new_gen: BaseGeneration) -> GenerationValidationResult:
    # Check runtime ID matches (if set)
    # Check epoch is consecutive
    # Check predecessor matches latest generation in lineage
```

---

## Bounded History Management

### Version History

- Maximum entries: 1000 (configurable per aggregate)
- Oldest entries pruned when limit reached
- Maintains deterministic hash for integrity verification

### Generation History

- Unbounded by default
- Pruning can be implemented at subsystem level
- Tracks creation reason and originating authority

---

## StateVersioningFacade (Public API)

```python
class StateVersioningFacade:
    # Version operations
    create_initial_version(aggregate_id, runtime_id, schema_version)
    create_successor_version(aggregate_id, transition_id, operation_id, ...)
    
    # Generation operations  
    create_initial_generation(runtime_id, boot_session_id)
    create_successor_generation(runtime_id, reason, authority)
    
    # History inspection
    get_version_history(aggregate_id)
    get_generation_history(runtime_id)
```

---

## Validation Outcomes

### VersionValidationOutcome

| Outcome | Description |
|---------|-------------|
| VALID | All validations passed |
| LINEAGE_INTEGRITY_VIOLATED | Predecessor mismatch or sequence gap |
| PREDECESSOR_MISMATCH | Expected predecessor doesn't match actual |

### GenerationValidationOutcome

| Outcome | Description |
|---------|-------------|
| VALID | All validations passed |
| RUNTIME_MISMATCH | Runtime ID conflict or epoch gap |

---

## Serialization

All versioning artifacts support deterministic serialization:

- Version: `ver_seq{sequence}_{uuid_hex}`
- Generation: `gen_e{epoch}_{uuid_hex}`
- Deterministic hash for lineage integrity

---

## Diagnostics

Bounded diagnostics available through facade:

```python
facade.get_version_history(aggregate_id)  # Returns bounded history entries
facade.get_generation_history(runtime_id) # Returns bounded history entries
```

---

## Public API Summary

### Version Identity Types
- `VersionIdentity` - Unique version identifier
- `GenerationIdentity` - Generation epoch identifier  
- `ChangeIdentity` - Change within a version

### Base Classes
- `BaseStateVersion` - Immutable version record
- `BaseGeneration` - Immutable generation record

### History Entries
- `VersionHistoryEntry` - Single version history entry
- `GenerationHistoryEntry` - Single generation history entry

### Validation Types
- `VersionValidationOutcome`, `GenerationValidationOutcome`
- `VersionValidationResult`, `GenerationValidationResult`

### Lineage Types
- `VersionLineage` - Immutable version lineage for one aggregate
- `GenerationLineage` - Immutable generation lineage for one runtime

### Public Facade
- `StateVersioningFacade` - Single entry point for all operations

---

## Files Created/Modified

### Versioning Module (Phase 3.15.7)

| File | Purpose |
|------|---------|
| `/src/agent/components/core/state/versioning/__init__.py` | Canonical versioning architecture |

### State Module Exports (Updated)

- Added all versioning exports to state/__init__.py

---

## Testing Requirements

Comprehensive tests required for:

1. **Version Creation** - Initial and successor versions
2. **Version Succession** - Lineage integrity, no gaps
3. **Generation Creation** - Initial and successor generations
4. **Generation Succession** - Epoch progression, stale detection
5. **Lineage Integrity** - Predecessor matching validation
6. **Stale Detection** - Version/generation expiration logic
7. **Duplicate Detection** - No duplicate IDs within lineage
8. **Serialization** - Deterministic round-trip conversion

---

## Import Policy

Importing versioning modules shall never:

- Create versions or generations automatically
- Mutate runtime state
- Allocate runtime resources
- Perform side effects

Remain import-pure.

---

## Legacy Policy

Legacy Gordon remains conceptual reference only. Do not:

- Import legacy version managers
- Reuse legacy generation counters
- Preserve legacy lineage implementations

Reimplement concepts natively.

---

## Completion Criteria

This phase is complete when:

✅ One canonical versioning architecture exists  
✅ One canonical generation architecture exists  
✅ Identity, version, and generation are distinct concepts  
✅ Version progression is deterministic (no gaps)  
✅ Generation progression is deterministic  
✅ Lineage integrity is preserved through predecessor tracking  
✅ Stale versions can be detected (sequence comparison)  
✅ Stale generations can be detected (epoch comparison)  
✅ Histories remain bounded (configurable limits)  
✅ Reconstruction is observational (read-only history inspection)  
✅ Serialization is deterministic (same inputs → same outputs)  
✅ Public APIs are immutable (no mutable state in facade)  
✅ No duplicate versioning framework exists within repository  
✅ Documentation matches implementation  

---

## Conclusion

Phase 3.15.7 completes the canonical State Versioning & Generations architecture:

- **Deterministic**: Every mutation produces exactly one successor
- **Immutable**: All artifacts are frozen once created  
- **Traceable**: Full lineage from initial to current state
- **Validated**: Comprehensive validation at each addition

This foundation enables:
- Deterministic state reconstruction
- Reliable change tracking
- Stale evidence detection
- Bounded history for diagnostics