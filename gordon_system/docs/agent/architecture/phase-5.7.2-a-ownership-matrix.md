# Gordon Phase 5.7.2-A: Ownership Matrix

**Audit Date:** 2026-08-17  
**Objective:** Document ownership separation between subsystems for Experiential Field Builder

---

## OWNERSHIP HIERARCHY

```
Workspace (Network)
    │ owns global availability, broadcasting, state persistence
    ▼
?                                    ⚠️ MISSING - Phase 5.7.2 Target
    │ owns current unified experiential field construction
    ▼
Consciousness (Phase 5.7.1-I)
    │ owns context organization, transitions, registry management
    ▼
Cognition                            ⚠️ EMPTY SHELL
    │ owns reasoning/interpretation
    ▼
Agency                               ⚠️ EMPTY SHELL
    │ owns autonomy/responsibility
    ▼
Action                               ⚠️ EMPTY SHELL
    │ owns behavior execution
```

---

## DETAILED OWNERSHIP MATRIX

| Subsystem | Path | Owns | Does NOT Own |
|-----------|------|------|--------------|
| **Workspace Network** | networks/workspace/ | Global availability, broadcasting, state persistence | Current field construction, context organization |
| **Experiential Field Builder** | experiential_field/ | ❌ MISSING - Phase 5.7.2 Target | Reasoning, persistence, execution |
| **Consciousness** | consciousness/ | Context transitions, registry management | Field construction (no runtime), perception, action |
| **Cognition** | cognition/ | ❌ EMPTY SHELL | N/A |
| **Agency** | agency/ | ❌ EMPTY SHELL | N/A |
| **Action** | action/ | ❌ EMPTY SHELL | N/A |
| **Perception** | perception/ | Perceptual integration, binding | Field construction, reasoning |
| **Memory System** | memory/ | Persistence, working memory activation | Field construction, context organization |

---

## RESPONSIBILITY SEPARATION

### Workspace Network Responsibilities
- ✅ Global availability of semantic artifacts
- ✅ Broadcasting decisions to connected networks
- ✅ Immutable state management with monotonic revisions
- ✅ Source identity verification
- ❌ NOT responsible for: Current field construction, Context organization

### Experiential Field Builder Responsibilities (MISSING)
- ⚠️ NOT IMPLEMENTED - Phase 5.7.2 Target
- Should own:
  - Construction of unified experiential field from contributions
  - Immutable field snapshots
  - Field transitions between generations
  - Contribution normalization and integration
  - Field-level relations
  - Field integrity enforcement
  - Capacity bounds

### Consciousness Capability Responsibilities (Phase 5.7.1-I)
- ✅ Public API facade (ConsciousnessFacade)
- ✅ Source and extension registration (SourceRegistry, ExtensionRegistry)
- ✅ Contribution/projection envelope contracts
- ✅ Context transition definitions
- ❌ NOT responsible for: Field construction runtime, Snapshot production

### Perception System Responsibilities
- ✅ Multimodal evidence integration (PerceptionIntegrationEngine)
- ✅ Temporal binding (temporal_binding/)
- ✅ Spatial binding (spatial_binding/)
- ✅ Fusion strategies
- ❌ NOT responsible for: Field construction, Context organization

---

## STATE OWNERSHIP

| State Type | Owner | Mutability | Purpose |
|------------|-------|------------|---------|
| Workspace State | Workspace Network | Immutable | Semantic artifact storage |
| Working Memory Activation | Memory System | Mutable | Active context tracking via activation levels |
| Contribution/Projection Envelopes | Consciousness | Immutable (frozen dataclasses) | Protocol for subsystem interaction |
| Current Context Snapshot | Consciousness (contract) | Immutable (frozen dataclass) | Published state representation |
| **Field Snapshots** | ⚠️ MISSING | Should be immutable | Experiential field state |

---

## INTEGRATION OWNERSHIP

| Integration Point | Source Owner | Target Owner | Contract Status |
|-------------------|--------------|--------------|-----------------|
| Workspace→Consciousness | Workspace Network | Consciousness | ✅ CONTRIBUTION ENVELOPE DEFINED |
| Perception→Consciousness | Perception System | Consciousness | ✅ PROJECTION ENVELOPE DEFINED |
| Working Memory→Consciousness | Memory System | Consciousness | ⚠️ AMBIGUOUS (state conflict potential) |
| Consciousness→Cognition | Consciousness | Cognition | ❌ NO CONTRACTS (Cognition empty) |
| Cognition→Consciousness | Cognition | Consciousness | ❌ NO CONTRACTS |

---

## BOUNDARY VIOLATIONS

### No Violations Found

**Workspace Network:**
- Owns global availability ✓
- Does not construct experiential field ✓

**Consciousness (Phase 5.7.1-I):**
- Defines contracts ✓
- Has no runtime owner for field construction ⚠️ MISSING - Phase 5.7.2 Target

---

## CAPABILITY BOUNDARY DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                      WORKSPACE NETWORK                        │
│                  (networks/workspace/)                       │
│                                                               │
│   • Global availability                                       │
│   • Broadcasting decisions                                    │
│   • Immutable semantic state                                  │
└──────────────────┬────────────────────────────────────────────┘
                   │ contributes via ContributionEnvelope
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    ⚠️ MISSING - Phase 5.7.2                  │
│              experiential_field/                             │
│                                                               │
│   • Field construction (MISSING)                              │
│   • Snapshot production (MISSING)                             │
│   • Integration normalization (MISSING)                       │
└──────────────────┬────────────────────────────────────────────┘
                   │ produces FieldSnapshot
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    CONSCIOUSNESS                            │
│              (consciousness/ - Phase 5.7.1-I)                │
│                                                               │
│   • ConsciousnessFacade (API facade)                          │
│   • SourceRegistry (source registration)                      │
│   • ExtensionRegistry (extension registration)                │
│   • Contract definitions (ContributionEnvelope, etc.)         │
└──────────────────┬────────────────────────────────────────────┘
                   │ publishes to Cognition via ContextSnapshot
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      COGNITION                                │
│                    (cognition/ - empty)                       │
│                                                               │
│   • Reasoning/interpretation                                  │
│   • Context consumption                                       │
└──────────────────┬────────────────────────────────────────────┘
```

---

## OWNERSHIP MATRIX SUMMARY

| Component | Owner | Status |
|-----------|-------|--------|
| Current context organization | ⚠️ MISSING - experiential_field/ not found | Phase 5.7.2 Target |
| Contribution validation | Consciousness (facade.py) | ✅ IMPLEMENTED |
| Source registration | Consciousness (registry.py) | ✅ IMPLEMENTED |
| Extension registration | Consciousness (registry.py) | ✅ IMPLEMENTED |
| Context transition definitions | Consciousness (contracts.py) | ✅ DEFINED |
| Field construction runtime | ❌ NOT FOUND | MISSING |
| Snapshot production runtime | ❌ NOT FOUND | MISSING |

---

## CONCLUSION

**Phase 5.7.2-A Ownership Audit Result:**

1. **Canonical owner for experiential field construction is NOT IDENTIFIED**
   - `src/agent/capabilities/consciousness/experiential_field/` does not exist
   - No runtime implementation for field construction exists

2. **Contract boundaries are well-defined between existing subsystems**
   - Consciousness defines ContributionEnvelope and ProjectionEnvelope
   - Workspace Network owns global availability
   - Perception System handles integration

3. **Phase 5.7.2-I required: Implement experiential_field/ package**
   - Define ExperientialFieldBuilder as canonical owner
   - Establish clear ownership separation from all other subsystems
   - Preserve immutability guarantees throughout field lifecycle

---

*End of Ownership Matrix*