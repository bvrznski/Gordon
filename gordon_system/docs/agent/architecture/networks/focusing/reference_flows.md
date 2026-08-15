# Reference Flows — Focusing Network Behavioral Examples

**Status:** Phase 4.2.10 Draft  
**Date:** August 14, 2026  
**Network:** Focusing Network  
**Purpose:** Demonstrate how the Focusing Network participates in Gordon without owning behavior

---

## Table of Contents

1. [Introduction](#introduction)
2. [Canonical Authority Chain](#canonical-authority-chain)
3. [Conversation Focus Flow](#conversation-focus-flow)
4. [Task Execution Focus Flow](#task-execution-focus-flow)
5. [Alert-Driven Reorientation Flow](#alert-driven-reorientation-flow)
6. [Focus Release Flow](#focus-release-flow)
7. [Stale Assessment Rejection Flow](#stale-assessment-rejection-flow)
8. [Resource Pressure Adaptation Flow](#resource-pressure-adaptation-flow)

---

## Introduction

This document provides canonical behavioral reference flows for the Focusing Network.

**Purpose:** Show how the Focusing Network computes focus recommendations and how those
recommendations participate in Gordon's behavior without owning it.

**Key Principle:** The Focusing Network produces *assessments* (computational estimates).
It never produces *commands* (behavioral decisions).

```
Source systems
    ↓ provide immutable projections
FocusingNetwork
    ↓ computes FocusAssessment (advisory)
Authority (Executive/Attention)
    ↓ accepts, modifies, defers, or rejects
Execution
    ↓ interprets semantic consequences
Core
    ↓ performs runtime mechanics
```

---

## Canonical Authority Chain

Every flow must follow this model:

1. **Source systems** provide immutable projections to the Focusing Network
2. **FocusingNetwork** computes a `FocusAssessment` (purely computational)
3. **Authority** (Executive or Attention Capability) interprets and decides
4. **Execution** receives semantic consequences
5. **Core** performs runtime mechanics

### Focusing May Produce:

| Item | Description |
|------|-------------|
| Primary target recommendation | Which target deserves most attention |
| Alternative targets | Secondary options if primary is unavailable |
| Priority estimate | How strongly this target should be focused |
| Competition evidence | Evidence from competing candidates |
| Suppression recommendations | Which targets should be suppressed |
| Precision recommendation | What precision level is appropriate |
| Persistence recommendations | How long to maintain focus |
| Bias recommendations | Modality bias for perception/preference |
| Resource demand estimates | Computational budget needed |
| Confidence | Evidential reliability of assessment |
| Explanation | Human-readable rationale |

### Focusing Must NOT Produce:

| Forbidden Item | Ownership belongs to |
|----------------|---------------------|
| Thread activation | Core runtime |
| Thread suspension | Core runtime |
| Loop replacement | Execution layer |
| Cycle selection | Execution layer |
| Scheduler priority | Core scheduler |
| CPU/GPU allocation | Resource Manager |
| Working Memory mutation | Working Memory module |
| Perception biasing | Perception module |

---

## Conversation Focus Flow

### Scenario

A `ConversationThread` is active. The participant asks a complex question that
requires interpretation before a response can be produced.

Initial candidates:

- Current participant input
- Conversation objective
- Unresolved prior question
- Delegated child Task result
- Candidate response
- Unrelated internal reflection

### Expected Focusing Behavior

1. **Prioritize** the current participant input (highest goal relevance)
2. **Maintain** conversation objective as persistent secondary context
3. **Suppress** unrelated internal reflection
4. **Recommend** sufficient precision for reference resolution
5. **Retain** unresolved commitments in secondary focus
6. **Produce** explainable target ranking

### Flow Details

```
Step 1: Executive Projection (immutable)
    projection_id = proj_001, revision = 5
    active_objectives = ["conversation_obj_7"]
    current_commitment = {"target_ids": ["conv_focus_target"], "strength": 0.85}
    
Step 2: Focusing Network Assessment
    candidates = [
        FocusCandidate(target="current_input"),
        FocusCandidate(target="conversation_continuity"),
        FocusCandidate(target="internal_maintenance")
    ]
    
    Priority Assessed:
        - current_input: 0.92 (high goal relevance)
        - conversation_continuity: 0.78 (persistence value)
        - internal_maintenance: 0.31 (low priority)
        
    Competition Analysis:
        - current_input has no strong competitors
        - conversation_continuity is compatible with input
        
    Suppression Recommendation:
        - internal_maintenance: SHOULD_SUPPRESS = true
    
    FocusAssessment Output:
        primary_target = "current_input"
        secondary_targets = ["conversation_continuity"]
        deferred_targets = ["internal_maintenance"]
        precision_recommendation = 0.85
        confidence = 0.91
        
Step 3: Executive Decision (authoritative)
    decision_kind = ACCEPT_FOCUS_RECOMMENDATION
    accepted_targets = ["current_input", "conversation_continuity"]
    
Step 4: Execution Consequence
    ConversationLoop will select InterpretationCycle
    
Step 5: Core Consequence
    Thread continues on same Loop, Cycle changes to InterpretationCycle
```

### Invariants Demonstrated

- `FOCUS-FLOW-INV-001`: Every behavioral effect requires authority outside FocusingNetwork
- `FOCUS-FLOW-INV-002`: FocusAssessment is immutable (advisory only)
- `FOCUS-FLOW-INV-003`: Applied assessment matches expected projection revision
- `FOCUS-FLOW-INV-004`: FocusingNetwork never selects a Thread
- `FOCUS-FLOW-INV-005`: FocusingNetwork never selects a Loop
- `FOCUS-FLOW-INV-006`: FocusingNetwork never selects a Cycle

### Anti-Pattern Contrast

**INCORRECT (FORBIDDEN):**
```python
# ❌ This is forbidden - Focusing as Executive
def conversation_handler(self, message):
    assessment = self.focusing.assess(message)
    if assessment.primary_target == "interpret":
        # This is behavior, not computation!
        self.loop.select(InterpretationCycle())  # ❌ Execution owns loops
```

**CORRECT:**
```python
# ✓ Correct - Focusing as computational advisor
def conversation_handler(self, message):
    projection = self.executive.create_projection(...)
    assessment = self.focusing.assess(message, projection)
    
    # Executive decides, Focusing only computes
    decision = self.executive.evaluate_assessment(assessment, projection)
    
    if decision.kind == "accept_recommendation":
        # Execution interprets the accepted decision
        self.execution.apply_focus_commitment(decision.accepted_targets)
```

---

## Task Execution Focus Flow

### Scenario

A `TaskThread` has an accepted plan and one executable next action.

Potential targets:

- Current plan step (executable)
- Future plan steps (not yet ready)
- Task evaluation (when appropriate)
- Unrelated monitoring alert
- Documentation reference

### Expected Assessment

1. **Current executable step** becomes primary (highest priority)
2. **Task objective** remains secondary persistent context
3. **Future steps** remain deferred until dependencies resolve
4. **Evaluation** receives readiness only after execution evidence exists
5. **Precision** reflects action risk and reversibility
6. **Computational budget** reflects expected complexity

### Flow Details

```
Step 1: Executive Projection
    projection_id = proj_002, revision = 3
    active_objectives = ["task_obj_execution"]
    current_commitment = {"target_ids": ["plan_step_5"], "strength": 0.9}
    
Step 2: Focusing Network Assessment
    candidates = [
        FocusCandidate(target="current_plan_step"),
        FocusCandidate(target="future_plan_steps"),
        FocusCandidate(target="evaluation")
    ]
    
    Priority:
        - current_plan_step: 0.89 (executable, high relevance)
        - future_plan_steps: 0.35 (deferred, not yet relevant)
        - evaluation: 0.42 (waiting for execution evidence)
        
    FocusAssessment Output:
        primary_target = "current_plan_step"
        secondary_targets = ["task_objective"]
        deferred_targets = ["future_plan_steps", "evaluation"]
        precision_recommendation = 0.75
        confidence = 0.87
        
Step 3: Executive Decision
    decision_kind = ACCEPT_FOCUS_RECOMMENDATION
    
Step 4: Execution Consequence
    TaskLoop will select ActionCycle (not a specific Cycle instance)
    
Step 5: Core Consequence
    One bounded ActionCycle executes
    After completion, loop advances to EvaluationCycle on next advancement
```

### Anti-Pattern Contrast

**INCORRECT (FORBIDDEN):**
```python
# ❌ Focusing selecting the cycle - this is execution authority
def execute_task(self):
    assessment = self.focusing.assess()
    if assessment.primary_target == "action":
        # ❌ FocusingNetwork cannot select cycles!
        return ActionCycle(...)
```

**CORRECT:**
```python
# ✓ Correct - Execution selects the cycle based on accepted focus
def execute_task(self):
    projection = self.executive.create_projection(...)
    assessment = self.focusing.assess(projection)
    
    # Executive accepts or modifies
    decision = self.executive.evaluate_assessment(assessment, projection)
    
    if decision.kind == "accept_recommendation":
        # Execution interprets the focus commitment
        # and selects appropriate cycles
        self.loop.advance()
```

---

## Alert-Driven Reorientation Flow

### Scenario A: Moderate Alert, Strong Focus

A high-value coding task is near completion. An external message produces
moderate Alerting demand.

**Inputs:**

Focusing evidence:
- High goal relevance for current task
- High completion proximity
- High switching cost
- High focus stability

Alerting projection:
- Moderate demand
- Non-critical
- Deferrable

**Expected Focusing Assessment:**

1. **Preserve** current task target (primary)
2. **Represent** alert as competing candidate (secondary or deferred)
3. **Recommend deferral** or secondary maintenance
4. **Explain** switching cost and commitment strength

### Scenario B: Critical Alert Overrides Focus

A critical safety or system-integrity signal appears.

**Inputs:**

Focusing evidence:
- Current commitment high

Alerting projection:
- Critical demand
- Strong safety relevance
- High confidence

**Expected Focusing Assessment:**

1. **Recognize** substantial competing exogenous demand
2. **Reduce persistence recommendation** for current target
3. **Estimate switching cost**
4. **Preserve original target** as resumable context
5. **Recommend reassessment or release**
6. **Avoid** emitting an interruption command

### Flow Details (Scenario B)

```
Step 1: Alerting Assessment Projection (external)
    alert_assessment = {
        "alert_level": CRITICAL,
        "safety_relevance": 0.98,
        "urgency": "immediate",
        "source": "system_monitor"
    }
    
Step 2: Executive Projection for Focusing
    projection_id = proj_003, revision = 10
    active_objectives = ["critical_safety_obj"]
    current_commitment = {"target_ids": ["task_target"], "strength": 0.95}
    
Step 3: Focusing Network Assessment
    candidates = [
        FocusCandidate(target="task_target"),
        FocusCandidate(target="alert_target")
    ]
    
    Priority:
        - task_target: 0.72 (still relevant, but interruptible)
        - alert_target: 0.96 (critical safety demand)
        
    Suppression Recommendation:
        - task_target: SHOULD_SUPPRESS = true
        - Reason: Critical alert demand exceeds persistence
        
    FocusAssessment Output:
        primary_target = "alert_target"
        secondary_targets = []
        suppression_targets = ["task_target"]
        confidence = 0.89
        
Step 4: Executive Decision
    decision_kind = ACCEPT_FOCUS_RECOMMENDATION
    
Step 5: Execution Consequence
    Current Thread yields or suspends at valid semantic boundary
    Recovery or monitoring work becomes runnable
    
Step 6: Core Consequence
    Runtime preemption or scheduling change occurs
```

### Invariants Demonstrated

- `FOCUS-FLOW-INV-008`: Alerting evidence does not automatically override focus
- `FOCUS-FLOW-INV-014`: Focusing recommendations do not mutate Working Memory

---

## Focus Release Flow

### Scenario

The current target has completed or lost relevance.

**Expected Focusing Behavior:**

1. **Lower persistence**
2. **Recommend release**
3. **Preserve completion evidence**
4. **Rank any next candidate separately**
5. **Avoid automatically activating the next target**

### Flow Details

```
Step 1: Executive Projection
    projection_id = proj_004, revision = 8
    
Step 2: Focusing Network Assessment
    candidates = [
        FocusCandidate(target="completed_task"),  # Now low priority
        FocusCandidate(target="next_available")
    ]
    
    Priority:
        - completed_task: 0.15 (low relevance after completion)
        - next_available: 0.68 (ready for attention)
        
    FocusAssessment Output:
        primary_target = "next_available"  # Not automatically activated!
        secondary_targets = []
        release_recommendation = ["completed_task"]
        confidence = 0.82
        
Step 3: Executive Decision
    decision_kind = ACCEPT_FOCUS_RECOMMENDATION
    
Step 4: Execution Consequence
    Focus commitment released from completed_task
    Next_available becomes the active focus target
    
Step 5: Core Consequence
    Thread state updated to reflect new focus
```

---

## Stale Assessment Rejection Flow

### Scenario

The Focusing Network evaluates projection revision 10.

The Executive objective state advances to revision 11 before the assessment is used.

**Expected Sequence:**

```
Step 1: Focusing receives projection (revision 10)
    projection_id = proj_010, revision = 10
    
Step 2: Assessment computed
    FocusAssessment references revision 10
    
Step 3: Executive state advances to revision 11
    new_projection.projection_revision = 11
    
Step 4: Assessment application attempted
    FocusAssessmentApplicationResult:
        is_valid = False
        is_stale = True
        validation_errors = ["Projection revision mismatch"]
        action_taken = "deferred"
        
Step 5: Outcome
    - Assessment retained as historical evidence
    - New assessment requested
    - No stale assessment affects Execution
```

### Anti-Pattern Contrast

**INCORRECT (FORBIDDEN):**
```python
# ❌ Stale application - no revision check
def process_assessment(assessment, current_projection):
    # Missing revision validation!
    self.apply_focus_commitment(assessment)
```

**CORRECT:**
```python
# ✓ Correct - revision validation before application
def process_assessment(assessment, current_projection):
    if assessment.revision != current_projection.projection_revision:
        result = FocusAssessmentApplicationResult.stale(
            expected_revision=current_projection.projection_revision,
            actual_revision=assessment.revision,
            reason="Projection state advanced during assessment"
        )
        return result
    # Assessment is fresh, apply it
    return self.apply_focus_commitment(assessment)
```

---

## Resource Pressure Adaptation Flow

### Scenario

The preferred target is computationally expensive. Available resource projection
is constrained.

**Expected Focusing Behavior:**

1. **Preserve semantic priority**
2. **Reduce recommended precision or bandwidth when acceptable**
3. **Identify minimum viable allocation**
4. **Expose degradation risks**
5. **Suggest deferral when resource constraints make processing ineffective**
6. **Never allocate resources directly**

### Flow Details

```
Step 1: Resource Projection (from Core)
    available_threads = 2
    max_cpu_percent = 50.0  # Reduced from normal 80%
    
Step 2: Focusing Network Assessment
    candidates = [
        FocusCandidate(target="expensive_computation")
    ]
    
    Precision Estimation:
        - base_precision: 0.95 (would be full precision)
        - bandwidth_recommendation: MODERATE (reduced due to constraints)
        
    Resource Demand Estimate:
        - recommended_budget: 1.0 (full demand)
        - constrained_budget: 0.5 (limited by resource projection)
        
    FocusAssessment Output:
        primary_target = "expensive_computation"
        precision_recommendation = 0.75  # Reduced
        allocation_recommendation = {
            "budget_ratio": 0.5,
            "minimum_viable": {"precision": 0.6, "bandwidth": 50}
        }
        confidence = 0.85
        
Step 3: Executive Decision
    decision_kind = ACCEPT_WITH_MODIFICATION
    
Step 4: Execution Consequence
    Task executes with reduced precision and budget
    
Step 5: Core Consequence
    Runtime allocates resources according to reduced budget
```

---

## Summary

This document provides canonical reference flows demonstrating:

| Flow | Focusing Role | Authority Role | Execution Role |
|------|---------------|----------------|----------------|
| Conversation Focus | Compute target ranking | Accept/reject recommendation | Select InterpretationCycle |
| Task Execution | Estimate priority per step | Evaluate against policy | Select ActionCycle |
| Alert Reorientation | Compare demands, assess switch cost | Decide interruption | Suspend/yield thread |
| Focus Release | Recommend release of completed focus | Approve release | Update commitment state |
| Stale Assessment | Compute assessment | Validate revision match | Defer if stale |
| Resource Pressure | Estimate resource needs | Accept modified budget | Allocate reduced resources |

---

## See Also

- `docs/agent/architecture/networks/focusing/behavioral_examples.md`
- `docs/agent/architecture/networks/focusing/example_antipatterns.md`
- `examples/networks/focusing/` (executable examples)