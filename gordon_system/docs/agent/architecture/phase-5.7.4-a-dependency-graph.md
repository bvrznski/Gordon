# Gordon Phase 5.7.4-A: Dependency Graph

**Audit Date:** 2026-08-17  
**Auditor:** Automated Architecture Analysis System  
**Scope:** Dependencies of Temporal Context Engine with other consciousness components

---

## 1. DEPENDENCY DIRECTION ANALYSIS

### Current Dependencies (Without Temporal Context)

```
┌─────────────────────────────────────────────────────────────────────┐
│                   CURRENT ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐        ┌──────────────────┐                  │
│  │ Experiential     │        │ Intentional      │                  │
│  │ Field (5.7.2)    │        │ Context (5.7.3)  │                  │
│  │                  │        │                  │                  │
│  │ - EF Builder     │        │ - IC Engine      │                  │
│  │ - EF Snapshots   │───────►│ - IC Snapshots   │                  │
│  │ - EF Transitions │        │ - IC Transitions │                  │
│  └──────────────────┘        └──────────────────┘                  │
│                                                                     │
│  Current: Direct EF → IC references                                │
│  Missing: Canonical Temporal Context between EF and IC             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Required Dependencies (With Temporal Context)

```
┌─────────────────────────────────────────────────────────────────────┐
│                 REQUIRED ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐   │
│  │ Experiential     │    │ Temporal Context │    │ Intentional  │   │
│  │ Field (5.7.2)    │◄──►│ Engine (5.7.4)   │───►│ Context      │   │
│  │                  │Retention│              │Presentatn│        │   │
│  │ - EF Snapshots   │    │ - Retention      │    │ - IC Engine  │   │
│  │ - EF Transitions │    │ - Presentation   │    │ - IC         │   │
│  └──────────────────┘    │ - Protention     │    │              │   │
│                          └──────────────────┘    └──────────────┘   │
│                                                                     │
│  Required: Temporal Context mediates EF ↔ IC interactions          │
│            - Retains references to previous EF states              │
│            - Represents current context                            │
│            - Maintains expectations for next state                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. CURRENT DEPENDENCIES

### Experiential Field → Intentional Context (Direct)

| Dependency | Direction | Current Implementation |
|------------|-----------|------------------------|
| EF Snapshot ID → IC Reference | One-way | ✅ `temporal_context_reference` in contracts.py |
| EF Generation → IC Tracking | One-way | ⚠️ Derived, not canonical |

### Missing Dependencies

| Dependency | Required Owner | Status |
|------------|---------------|--------|
| Temporal Continuity Authority | Temporal Context Engine | ❌ MISSING |
| Retention of Previous States | Temporal Context Engine | ❌ MISSING |
| Presentation of Current State | Temporal Context Engine | ❌ MISSING |
| Protention of Next Expectations | Temporal Context Engine | ❌ MISSING |

---

## 3. INTEGRATION DEPENDENCIES

### With External Systems

| System | Dependency Direction | Status |
|--------|---------------------|--------|
| Memory System | Reference only (no ownership) | ✅ SEPARATED |
| Working Memory | Reference only (no ownership) | ✅ SEPARATED |
| Perception System | Input references only | ✅ SEPARATED |

### With Consciousness Phases

| Phase | Dependency Direction | Status |
|-------|---------------------|--------|
| Experiential Field (5.7.2) | Input → Temporal Context | ❌ MISSING |
| Intentional Context (5.7.3) | Input/Output ↔ Temporal Context | ❌ MISSING |
| Reasoning (5.7.8) | Output from Temporal Context | ✅ SEPARATED |
| Planning (5.7.8) | Output from Temporal Context | ✅ SEPARATED |

---

## 4. DATA FLOW ANALYSIS

### Without Temporal Context (Current)

```
EF Snapshot → IC Reference (direct)
  - No canonical retention
  - No canonical presentation  
  - No canonical protention
```

### With Temporal Context (Required)

```
EF Snapshot → Retention → Presentation → Protention → Next EF
  Canonical continuity maintained across generations
```

---

## 5. DEPENDENCY CONCLUSION

### Critical Missing Dependencies

| Dependency | Status |
|------------|--------|
| EF ↔ Temporal Context | ❌ MISSING |
| IC ↔ Temporal Context | ❌ MISSING |
| Temporal Continuity Authority | ❌ MISSING |

### Integration Readiness

| Aspect | Status |
|--------|--------|
| Experiential Field integration | ⚠️ DERIVED_ONLY (direct references) |
| Intentional Context integration | ⚠️ DERIVED_ONLY (direct references) |
| Canonical temporal authority | ❌ NOT_IMPLEMENTED |

---

*End of Dependency Graph*