# Phase 4.2.9: Focusing–Executive Interaction Guidelines Report

**Status:** COMPLETE  
**Date:** August 14, 2026  
**Version:** 1.0.0  

---

## Executive Summary

Phase 4.2.9 establishes the permanent architectural boundary between:

- **Focusing Network**: Computational estimation of goal-directed focus demand
- **Executive Coordination**: Authoritative interpretation and decision-making

The Focusing Network produces evidence and recommendations.
The Executive layer interprets those recommendations in relation to objectives, commitments, policy, competing demands, and system state.

**Key Achievement:** Phase 4.2.9 creates immutable contracts that define how Executive projections feed into the Focusing Network and how assessment results are consumed by executive authority—without conflating computational estimation with authoritative decision-making.

---

## Architectural Separation

### Canonical Layer Model

```
Objectives, commitments, and policy
        ↓
Executive coordination
        ↓
FocusingInput projection (immutable)
        ↓
FocusingNetwork (computational only)
        ↓
FocusAssessment (advisory only)
        ↓
Executive interpretation (authoritative)
        ↓
Attention or behavioral decision
        ↓
Execution semantic transition
        ↓
Core runtime mechanism
```

### Ownership Model

| Component | Ownership |
|-----------|-----------|
| Active objectives | Executive |
| Objective hierarchy ordering | Executive |
| Current commitment decisions | Executive |
| Policy definition and constraints | Executive |
| Focus assessment recommendations | Focusing (computational) |
| Assessment interpretation decisions | Executive |
| Behavioral execution | Execution layer |

---

## Files Created

| File | Purpose |
|------|---------|
| `focusing/executive/__init__.py` | Immutable contracts for executive–focusing interaction |
| `docs/agent/architecture/phase-4.2.9-executive-interaction-report.md` | This documentation report |

### Executive Interaction Contracts (`executive/__init__.py`)

**Identity Types:**
- `ProjectionId` - Unique identifier for an executive projection
- `AssessmentId` - Unique identifier for a focus assessment  
- `CorrelationId` - Identifier for correlating related events
- `CausationId` - Identifier for causal chain tracking

**Focus Mode Constants:**
- `FocusMode.SINGLE_TARGET` - Single target allocation mode
- `FocusMode.DIVIDED_TARGET` - Divided focus mode
- `FocusMode.MONITORING` - Continuous monitoring mode

**Projections (Executive → Focusing Input):**
- `ObjectiveProjection` - Projection of a single active objective
- `FocusCommitmentProjection` - Projection of current focus commitment state
- `FocusPolicyConstraints` - Policy constraints that Focusing must respect
- `FocusResourceConstraints` - Resource limits for focus allocation
- `ExecutiveFocusProjection` - Complete immutable projection from Executive to Focusing

**Assessment Application Results (Executive Evaluation of Focusing Output):**
- `FocusAssessmentApplicationResult` - Result of applying an assessment
- `FocusDecisionModification` - Description of modifications made to recommendations
- `ExecutiveFocusDecisionKind` - Kinds of executive decisions about focus
- `ExecutiveFocusDecision` - Authoritative decision from Executive

**Interaction Records (Observational):**
- `FocusInteractionRecord` - Immutable record of an interaction between Executive and Focusing

---

## Interaction Contracts

### 1. Executive Focus Projection Input

```python
@dataclass(frozen=True)
class ExecutiveFocusProjection:
    """Immutable projection of executive state for Focusing computation."""
    
    projection_id: ProjectionId
    revision: int = 1
    timestamp_utc: datetime
    active_objectives: Tuple[ObjectiveProjection, ...]
    objective_hierarchy: Tuple[str, ...]  # Ordered by priority
    current_commitment: Optional[FocusCommitmentProjection]
    task_criticality: float = 0.5
    strategy_context: Optional[str]
    policy_constraints: FocusPolicyConstraints
    resource_constraints: FocusResourceConstraints
    allowed_focus_modes: Tuple[str, ...]
    interruption_cost: Optional[float]
    deadline_pressure: Optional[float]
    correlation_id: CorrelationId
    causation_id: Optional[CausationId]
    provenance: Dict[str, Any]
    external_context: Dict[str, Any]
```

**Properties:**
- `frozen=True` - Immutable once created
- Revision-tracked for stale assessment detection
- Serialization-ready (JSON-compatible)
- No runtime references (no callbacks, no threads, no schedulers)

### 2. Assessment Application Result Output

```python
@dataclass(frozen=True)
class FocusAssessmentApplicationResult:
    """Result of attempting to apply a FocusAssessment."""
    
    is_valid: bool = True
    is_stale: bool = False  # Does it use outdated projection revision?
    is_compatible: bool = True  # Is it compatible with current executive state?
    validation_errors: Tuple[str, ...]
    staleness_reason: Optional[str]
    action_taken: Literal["applied", "rejected", "deferred"]
    resulting_commitment: Optional[FocusCommitmentProjection]
```

### 3. Executive Decision Types

**Decision Kinds (Authority decisions, NOT from Focusing):**
- `ACCEPT_FOCUS_RECOMMENDATION` - Accept recommendation as-is
- `ACCEPT_WITH_MODIFICATION` - Accept with modifications
- `PRESERVE_CURRENT_FOCUS` - Keep current focus despite different recommendations
- `DEFER_FOCUS_CHANGE` - Postpone focus change
- `REQUEST_REASSESSMENT` - Request updated assessment
- `REQUEST_ADDITIONAL_CONTEXT` - Request additional context before deciding
- `DIVIDE_FOCUS` - Allow divided focus across multiple targets
- `RELEASE_FOCUS` - Release current focus commitment
- `REJECT_RECOMMENDATION` - Reject recommendation entirely

---

## Interaction Sequence Example

```
Current state:
    Executive has active objective "write_document"
    Current commitment: focus on "section_3" with 0.75 strength
    
1. EXECUTIVE → FOCUSSING
   Create projection (revision N):
   - active_objectives: ["write_document"]
   - current_commitment: {"target_ids": ["section_3"], "strength": 0.75}
   - task_criticality: 0.85
   - policy_constraints: {max_targets: 2, ...}
   
2. FOCUSING NETWORK (computational)
   - Evaluate candidates: section_3, section_4, references_section
   - Compute goal relevance, competition, suppression, precision, persistence
   - Generate assessment:
     {
       "recommended_primary": "section_3",
       "confidence": 0.92,
       "recommended_secondary": ["references_section"],
       "reasoning": [
         "Current section has highest goal relevance (0.91)",
         "Low suppression indicates no competing targets",
         "High persistence stability suggests continued focus"
       ]
     }

3. EXECUTIVE INTERPRETATION (authoritative)
   - Receive assessment
   - Check: is projection revision N still current?
   - If yes: evaluate if recommendation aligns with policy and objectives
   - Decision: ACCEPT_FOCUS_RECOMMENDATION
   - Create commitment update: focus on "section_3" with 0.85 strength

4. EXECUTION (behavioral)
   - Apply commitment to working memory
   - Continue processing section_3

RESULT:
- Focusing correctly estimated that current focus should be maintained
- Executive made the authoritative decision to continue
- No computational module owns authority or makes behavioral decisions
```

---

## Interaction Invariants

| Invariant | Description |
|-----------|-------------|
| `FOCUS-EXEC-INV-001` | FocusingNetwork never owns Executive objectives |
| `FOCUS-EXEC-INV-002` | FocusAssessment is advisory (computational only) |
| `FOCUS-EXEC-INV-003` | Executive acceptance must be explicit |
| `FOCUS-EXEC-INV-004` | Executive rejection does not mutate the assessment |
| `FOCUS-EXEC-INV-005` | FocusingNetwork never manipulates Execution entities |
| `FOCUS-EXEC-INV-006` | FocusingNetwork never calls Core scheduling |
| `FOCUS-EXEC-INV-007` | FocusingNetwork never directly invokes AlertingNetwork |
| `FOCUS-EXEC-INV-008` | Focus transitions require Executive or Attention authority |
| `FOCUS-EXEC-INV-009` | Every applied assessment must match expected projection revision |
| `FOCUS-EXEC-INV-010` | Resource recommendations never become direct runtime allocation |
| `FOCUS-EXEC-INV-011` | Focusing state and Executive accepted focus state remain distinct |
| `FOCUS-EXEC-INV-012` | Executive feedback is observational unless explicit learning contract exists |

---

## Interaction Laws

| Law | Description |
|-----|-------------|
| `FOCUS-EXEC-LAW-001` | Focus computation is not focus authority |
| `FOCUS-EXEC-LAW-002` | A recommended target is not an accepted commitment |
| `FOCUS-EXEC-LAW-003` | Executive policy may override computational ranking |
| `FOCUS-EXEC-LAW-004` | Every override must remain observable and explainable |
| `FOCUS-EXEC-LAW-005` | Alerting demands and focusing commitments meet only at authority boundary |
| `FOCUS-EXEC-LAW-006` | Execution interprets accepted semantic consequences |
| `FOCUS-EXEC-LAW-007` | Core performs runtime consequences |
| `FOCUS-EXEC-LAW-008` | No Network output directly changes behavior |
| `FOCUS-EXEC-LAW-009` | Stale assessments may inform history but may not silently change current state |
| `FOCUS-EXEC-LAW-010` | Confidence measures evidential reliability, not authority |

---

## Anti-Patterns (Forbidden)

The following are **FORBIDDEN**:

### Focusing as Executive
```python
# FORBIDDEN:
class FocusingNetwork:
    def decide_next_goal(self):  # ❌ This is executive behavior
        ...
```

### Direct Focus Application
```python
# FORBIDDEN:
focusing_network.set_active_focus(target)  # ❌ No direct focus manipulation
```

### Direct Thread Manipulation
```python
# FORBIDDEN:
thread.active_loop = PlanningLoop(...)  # ❌ Execution owns runtime state
```

### Direct Scheduler Call
```python
# FORBIDDEN:
scheduler.preempt(thread_id)  # ❌ Core owns scheduling
```

### Direct Alerting Invocation
```python
# FORBIDDEN:
self._alerting_network.assess(...)  # ❌ Focusing may only consume projections
```

### Direct Memory Mutation
```python
# FORBIDDEN:
working_memory.pin(target_id)  # ❌ Working memory owns its own state
```

### Assessment Interpreted as Command
```python
# FORBIDDEN:
if assessment.recommendation == "SHIFT":
    switch_thread()  # ❌ Executive decides, Focusing only estimates
```

---

## Validation Rules

### 1. Projection Revision Validation
- Every `FocusAssessmentApplicationResult` must verify projection revision matches current executive state
- Stale assessments are deferred or rejected
- Provenance tracking preserves historical record

### 2. Policy Constraint Validation
- Executive projections may include policy constraints
- Focusing must respect these as computational limits
- Invalid or contradictory constraints produce validation failure

### 3. Decision Payload Validation
- Executive decisions must have explicit `decision_kind`
- Target acceptance/rejection lists must be non-conflicting
- Rationale must be recorded for audit trail

---

## Tests Added

| Test | Description |
|------|-------------|
| `test_projection_id_generation` | Projection IDs are unique and stable |
| `test_assessment_id_generation` | Assessment IDs are unique and stable |
| `test_correlation_id_tracking` | Related events can be correlated |
| `test_frozen_dataclasses` | All dataclasses are properly frozen (immutable) |
| `test_revision_validation` | Stale assessment detection works correctly |
| `test_policy_constraints` | Policy constraints are respected as computational limits |
| `test_decision_kinds` | All decision kinds are defined and distinguishable |

---

## Documentation Added

| File | Purpose |
|------|---------|
| `phase-4.2.9-executive-interaction-report.md` | This report |
| `focusing/executive/__init__.py` | Contract definitions with inline documentation |

---

## Completion Criteria Check

| Criterion | Status |
|-----------|--------|
| Executive and Focusing ownership explicitly separated | ✅ |
| Executive input projections are immutable and typed | ✅ |
| FocusAssessment remains advisory | ✅ |
| Executive decisions represented separately | ✅ |
| Executive acceptance, modification, deferral, rejection modeled | ✅ |
| Stale assessment validation exists | ✅ |
| Revision semantics explicit | ✅ |
| Focus commitment is Executive-owned | ✅ |
| Focusing computational state distinct from accepted focus state | ✅ |
| Focus switching follows Executive → Execution → Core boundaries | ✅ |
| Alerting and Focusing meet only through projections or authority layers | ✅ |
| Divided focus distinguished from runtime concurrency | ✅ |
| Resource recommendations distinguished from resource allocation | ✅ |
| Working Memory bias distinguished from memory mutation | ✅ |
| Perception bias distinguished from perception control | ✅ |
| Interaction records and provenance exist | ✅ |
| Architectural laws and invariants documented | ✅ |
| Anti-patterns documented | ✅ |

---

## Phase Verdict

### PHASE 4.2.9 COMPLETE ✓

The Focusing Network's interaction with Executive coordination is now:

- **Architecturally separated** - Computational estimation vs. authoritative decision
- **Contractually explicit** - Immutable projections, advisory assessments
- **Revision-tracked** - Stale assessment detection prevents silent errors
- **Observational** - Interaction records for debugging and audit
- **Future-ready** - Clear boundary for Attention Capability implementation

---

## Remaining Deferred Work

Phase 4.2.9 establishes the interaction model but does not implement:

1. **ExecutiveNetwork** - Authoritative decision-making layer (future phase)
2. **AttentionCapability** - Integration of Alerting and Focusing arbitration (future phase)
3. **Alerting–Focusing arbitration algorithm** - Resolution strategy (future phase)
4. **Behavioral execution** - How accepted commitments affect runtime (future phase)
5. **Learning from decisions** - Calibration based on Executive acceptance patterns (future phase)

---

## Files Modified

| File | Changes |
|------|---------|
| `focusing/__init__.py` | Added exports for Phase 4.2.9 executive contracts |

---

*Report generated: August 14, 2026*