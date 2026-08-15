# Gordon Focusing Network - Canonical Architectural Specification

**Specification Version:** 1.0.0  
**Phase:** 4.2.15  
**Status:** CANONICAL SPECIFICATION COMPLETE  
**Date:** August 14, 2026  

---

## Table of Contents

1. [Architectural Purpose](#1-architectural-purpose)
2. [Architectural Context](#2-architectural-context)
3. [Ownership](#3-ownership)
4. [Public Contracts](#4-public-contracts)
5. [Computational Pipeline](#5-computational-pipeline)
6. [State Model](#6-state-model)
7. [FocusAssessment Specification](#7-focusassessment-specification)
8. [Interaction Model](#8-interaction-model)
9. [Architectural Laws](#9-architectural-laws)
10. [Invariants](#10-invariants)
11. [Error Semantics](#11-error-semantics)
12. [Explainability](#12-explainability)
13. [Determinism](#13-determinism)
14. [Extensibility](#14-extensibility)
15. [Compatibility](#15-compatibility)
16. [Compliance Requirements](#16-compliance-requirements)

---

## 1. Architectural Purpose

### 1.1 Core Purpose

The **Focusing Network** is the endogenous attention-policy computation network of Gordon. It computes goal-directed attentional recommendations without executing behavioral policy.

**Problem Solved:** The Focusing Network addresses the challenge of determining which computational targets deserve sustained attention, how strongly they should be focused, for how long, with what precision, and under which constraints—without owning the decision-making authority or execution semantics.

**Role within Gordon:** The Focusing Network operates as a computational advisor to the Executive Coordination layer. It provides evidence-based recommendations about focus allocation, which the Executive layer interprets in light of objectives, commitments, policy, and competing demands.

**Relationship to Endogenous Attention:** The Focusing Network constitutes the computational substrate of endogenous attention—the internal, goal-directed allocation of computational resources toward specific targets within Gordon's cognitive architecture.

### 1.2 Architectural Boundary

The Focusing Network occupies this position in Gordon's architectural hierarchy:

```
Core (runtime infrastructure)
    ↓ provides execution substrate
Execution (semantic behavior)
    ↓ coordinates attention and cognition
Capabilities (cognitive functions)
    ↓ provide specialized computation
Attention Capability (attention arbitration)
    ↓ selects from recommendations
Focusing Network (computational estimation)
    ↓ produces assessments
Computational Modules (delegated algorithms)
```

---

## 2. Architectural Context

### 2.1 Hierarchical Position

The Focusing Network occupies this position in Gordon's architectural hierarchy:

```
Core
    ↓ provides runtime infrastructure
Execution
    ↓ coordinates attention and cognition
Capabilities
    ↓ provide cognitive functions
Attention Capability
    ↓ receives focus selections
Focusing Network
    ↓ produces computational assessments
Computational Modules
    ↓ implement algorithms
```

### 2.2 Architectural Boundaries

| Boundary | Direction | Ownership |
|----------|-----------|-----------|
| Core → Focusing | Runtime substrate | Core owns, Focusing consumes |
| Execution → Focusing | Context projection | Execution provides, Focusing receives |
| Capabilities → Focusing | Semantic context | Capabilities provide, Focusing receives |
| Attention Capability ← Focusing | Assessment provision | Focusing produces, Attention selects |
| Computational Modules ↔ Focusing | Algorithm delegation | Focusing orchestrates, modules compute |

---

## 3. Ownership

### 3.1 What the Focusing Network Owns

The Focusing Network permanently owns ONLY:

| Responsibility | Description |
|----------------|-------------|
| **Endogenous attentional computation** | Computing focus recommendations for internal targets without external dependencies |
| **Goal-directed priority estimation** | Estimating how strongly a target should receive attention based on goal alignment |
| **Focus competition analysis** | Analyzing which candidates compete for attention and their relative strength |
| **Suppression estimation** | Recommending which targets should be suppressed to reduce interference |
| **Precision estimation** | Estimating the optimal level of precision/bandwidth allocation for each target |
| **Persistence estimation** | Estimating how long focus should be maintained on a target |
| **Computational budgeting recommendations** | Recommending resource allocation without executing runtime allocation |
| **Attentional bias recommendations** | Computing modality bias for perception/preference modulation |
| **Confidence estimation** | Estimating evidential reliability of computational assessments |
| **Explainable FocusAssessment production** | Producing rationale with each assessment for debugging and audit |

### 3.2 What the Focusing Network Never Owns

The Focusing Network shall NEVER own:

| Forbidden Responsibility | Ownership Belongs To |
|--------------------------|----------------------|
| Behavioral policy | Executive Layer |
| Planning | Planning Capability |
| Reasoning | Reasoning Capability |
| Execution | Execution Layer |
| Thread management | Core Runtime |
| Loop management | Execution Layer |
| Cycle management | Execution Layer |
| Runtime scheduling | Core Scheduler |
| Runtime resource allocation | Resource Manager |
| Executive authority | Executive Layer |
| Working Memory ownership | Working Memory Module |
| Perception ownership | Perception Module |

### 3.3 Ownership Boundary Verification

| Boundary | Verified | Evidence |
|----------|----------|----------|
| Behavioral authority separation | ✅ PASS | No behavioral logic in Focusing modules |
| Runtime dependency separation | ✅ PASS | No runtime infrastructure coupling |
| Working Memory separation | ✅ PASS | Only projections accepted, no mutation |
| Perception separation | ✅ PASS | Only projections used, no biasing |

---

## 4. Public Contracts

### 4.1 Contract Categories

The Focusing Network exposes these contract categories:

#### 4.1.1 Input Contracts (Providers - Network consumes)

| Contract | Purpose | Direction |
|----------|---------|-----------|
| `FocusCandidateProvider` | Supply focus candidates for evaluation | External → Focusing |
| `FocusContextProvider` | Provide execution context information | External → Focusing |
| `FocusStateProvider` | Provide current state views | External → Focusing |
| `ObjectiveProvider` | Provide active objectives | Executive → Focusing |
| `ConfigurationProvider` | Provide runtime-independent configuration | Config system → Focusing |

#### 4.1.2 Output Contracts (Consumers - Network produces)

| Contract | Purpose | Direction |
|----------|---------|-----------|
| `FocusAssessmentConsumer` | Consume focus assessments | Focusing → Attention/Executive |
| `PriorityAssessmentConsumer` | Consume priority data | Focusing → Decision makers |
| `CompetitionAssessmentConsumer` | Consume competition analysis | Focusing → Decision makers |
| `PrecisionAssessmentConsumer` | Consume precision recommendations | Focusing → Resource allocators |
| `PersistenceAssessmentConsumer` | Consume persistence estimates | Focusing → Focus managers |

#### 4.1.3 Context Contracts (Projections - No ownership)

| Contract | Purpose |
|----------|---------|
| `FocusComputationContext` | Complete context with all projections |
| `ExecutionProjection` | Current execution state projection |
| `PolicyProjection` | Active policy constraints projection |
| `ResourceProjection` | Available resources projection |
| `HistoricalProjection` | Past states projection |

#### 4.1.4 State Contracts (Views - Immutable, read-only)

| Contract | Purpose |
|----------|---------|
| `FocusStateView` | View of focus state |
| `PriorityStateView` | View of priority state |
| `PersistenceStateView` | View of persistence state |
| `PrecisionStateView` | View of precision state |

### 4.2 Core Public API

#### 4.2.1 Network Entry Point

```
FocusingNetwork.create(config: Optional[FocusingNetworkConfig]) → FocusingNetwork
FocusingNetwork.assess(candidates, current_targets=None, diagnostics_sink=None) → FocusAssessment
```

**Purpose:** Execute the complete focus assessment pipeline.

**Inputs:**
- `candidates`: Tuple of `FocusCandidate` objects to evaluate
- `current_targets`: Optional tuple of currently focused targets for context
- `diagnostics_sink`: Optional sink for diagnostic event collection

**Outputs:**
- Complete `FocusAssessment` with all computed values

**Ownership:** Network retains no state. All outputs are immutable.

### 4.3 Contract Versioning

| Aspect | Policy |
|--------|--------|
| Current version | 1.0.0 |
| Compatibility policy | Backward compatible (future consumers may add fields) |
| Deprecation policy | Three releases before removal |
| Extension strategy | Additive only (new fields with defaults, new contracts) |

### 4.4 Contract Validation

All contract inputs shall be validated before processing. Validation failures produce `ValidationReport` objects describing:

- Which validation rules were violated
- Which input fields caused violations
- Recommended corrections

---

## 5. Computational Pipeline

### 5.1 Pipeline Architecture

```
FocusCandidates (input)
    ↓
PipelineExecutor (orchestration)
    ↓
Stage 1: Priority Aggregation → PriorityAssessment
    ↓
Stage 2: Relevance Evaluation → RelevanceAssessment
    ↓
Stage 3: Competition Resolution → CompetitionAssessment
    ↓
Stage 4: Suppression Recommendation → SuppressionAssessment
    ↓
Stage 5: Precision Estimation → PrecisionAssessment
    ↓
Stage 6: Persistence Update → PersistenceAssessment
    ↓
Stage 7: Bias Generation → BiasAssessment
    ↓
Stage 8: Resource Budget → AllocationRecommendation
    ↓
Stage 9: Assessment Composition → FocusAssessment (output)
```

### 5.2 Pipeline Stage Specifications

#### 5.2.1 Priority Aggregation

**Purpose:** Estimate goal-directed priority for each candidate.

**Inputs:**
- Tuple of `FocusCandidate` objects
- Context projections (objectives, policy constraints)

**Outputs:**
- `PriorityAssessment` with computed priority values

**Preconditions:**
- All candidates are valid `FocusCandidate` instances
- Context projections are properly structured

**Postconditions:**
- Each candidate has an associated priority estimate
- Priority values are within [0.0, 1.0] range

**Invariants:**
- Same inputs always produce same outputs (determinism)
- No mutable state modified during computation

**Failure Conditions:**
- Invalid input format → Validation error
- Missing context data → Default values applied

#### 5.2.2 Relevance Evaluation

**Purpose:** Evaluate how well each candidate aligns with active objectives.

**Inputs:**
- Candidates with priority assessments
- Current focus targets
- Historical state

**Outputs:**
- `RelevanceAssessment` with alignment scores

**Preconditions:**
- Priority assessments exist for all candidates

**Postconditions:**
- Each candidate has relevance score relative to current objectives

#### 5.2.3 Competition Resolution

**Purpose:** Analyze competition between candidates and identify conflicts.

**Inputs:**
- Candidates with priority and relevance assessments
- Historical focus state

**Outputs:**
- `CompetitionAssessment` with conflict analysis
- `SuppressionAssessment` with suppression recommendations

**Preconditions:**
- Priority and relevance assessments exist for all candidates

#### 5.2.4 Precision Estimation

**Purpose:** Estimate optimal precision/bandwidth allocation for each target.

**Inputs:**
- Candidates with competition analysis
- Resource projections

**Outputs:**
- `PrecisionAssessment` with bandwidth recommendations

#### 5.2.5 Persistence Update

**Purpose:** Estimate how long focus should be maintained on each target.

**Inputs:**
- Candidates with precision assessments
- Historical state transitions

**Outputs:**
- `PersistenceAssessment` with maintenance estimates

#### 5.2.6 Bias Generation

**Purpose:** Compute modality bias for perception/preference modulation.

**Inputs:**
- Candidates with persistence estimates

**Outputs:**
- `BiasAssessment` with modality recommendations

#### 5.2.7 Resource Allocation

**Purpose:** Estimate total resource demand for focus allocation.

**Inputs:**
- All assessment results
- Configuration parameters

**Outputs:**
- `AllocationRecommendation` with budget estimates

#### 5.2.8 Assessment Composition

**Purpose:** Combine all assessments into final `FocusAssessment`.

**Inputs:**
- All individual assessment results
- Pipeline metadata

**Outputs:**
- Complete `FocusAssessment` object

**Invariants:**
- All assessments are included in output
- Assessment ID is unique per computation instance

### 5.3 Context Carriers

#### 5.3.1 ComputationContext

```
ComputationContext(
    config: FocusingNetworkConfig,
    candidates: Tuple[FocusCandidate, ...],
    current_targets: Tuple[FocusTarget, ...],
    history: Tuple[Dict[str, Any], ...],
    computation_id: str,
    timestamp_utc: datetime,
    revision: int,
    diagnostics_sink: Optional[DiagnosticsSink]
)
```

**Purpose:** Immutable context carried through pipeline stages.

**Properties:**
- All fields are immutable (frozen dataclass)
- No runtime references (no callbacks, no threads)

---

## 6. State Model

### 6.1 Computational State

Computational state represents the current values computed during a single assessment cycle.

| Component | Description |
|-----------|-------------|
| `PriorityState` | Priority estimates for all candidates |
| `RelevanceState` | Relevance scores for all candidates |
| `SuppressionState` | Suppression recommendations |
| `PrecisionState` | Precision bandwith recommendations |
| `PersistenceState` | Persistence maintenance estimates |

### 6.2 Persistent State

Persistent state represents the historical record of focus computations.

| Component | Description |
|-----------|-------------|
| `HistoryState` | Sequence of past assessments and transitions |
| `FocusSnapshot` | Point-in-time view of state |

### 6.3 Ephemeral State

Ephemeral state exists only during a single pipeline execution.

| Component | Description |
|-----------|-------------|
| `PipelineState` | Intermediate results at each stage |
| `DiagnosticState` | Events emitted during computation |

### 6.4 Immutable Views

All state views are read-only and frozen:

| View Type | Purpose |
|-----------|---------|
| `FocusStateView` | Read-only access to focus state |
| `PriorityStateView` | Read-only priority data |
| `PersistenceStateView` | Read-only persistence data |

### 6.5 History Semantics

History preserves all previous assessments for:

- Debugging and audit trails
- Pattern analysis over time
- Revision tracking

Each history entry is immutable and timestamped.

### 6.6 Snapshot Semantics

Snapshots capture point-in-time state for:

- State recovery
- Comparison across time
- Debugging historical states

---

## 7. FocusAssessment Specification

### 7.1 Assessment Structure

```
FocusAssessment(
    assessment_id: AssessmentId,
    timestamp_utc: datetime,
    computation_id: str,
    
    # Primary recommendations
    primary_target: Optional[FocusTarget],
    secondary_targets: Tuple[FocusTarget, ...],
    deferred_targets: Tuple[FocusTarget, ...],
    
    # Assessment components
    priority_assessment: PriorityAssessment,
    relevance_assessment: RelevanceAssessment,
    competition_assessment: CompetitionAssessment,
    suppression_assessment: SuppressionAssessment,
    precision_assessment: PrecisionAssessment,
    persistence_assessment: PersistenceAssessment,
    bias_assessment: BiasAssessment,
    allocation_recommendation: AllocationRecommendation,
    
    # Quality metrics
    confidence: float,  # Evidential reliability (0.0 to 1.0)
    is_finite: bool,    # All values are finite numbers
    is_normalized: bool, # Values are within expected ranges
    
    # Rationale and provenance
    explanations: Tuple[AssessmentExplanation, ...],
    provenance: ProvenanceRecord,
    
    # Pipeline metadata
    pipeline_stage_order: Tuple[str, ...],
    elapsed_ms: float
)
```

### 7.2 Required Fields

The following fields MUST be present in every `FocusAssessment`:

| Field | Type | Description |
|-------|------|-------------|
| `assessment_id` | AssessmentId | Unique identifier for this assessment |
| `timestamp_utc` | datetime | When assessment was created |
| `computation_id` | str | Pipeline computation identifier |
| `priority_assessment` | PriorityAssessment | Priority estimation results |
| `confidence` | float | Evidential reliability (0.0 to 1.0) |

### 7.3 Optional Fields

These fields MAY be present with default values:

| Field | Type | Default |
|-------|------|---------|
| `secondary_targets` | Tuple[FocusTarget, ...] | Empty tuple |
| `deferred_targets` | Tuple[FocusTarget, ...] | Empty tuple |
| `explanations` | Tuple[AssessmentExplanation, ...] | Empty tuple |

### 7.4 Assessment Components

#### 7.4.1 PriorityAssessment

```
PriorityAssessment(
    estimated_priority: float,
    priority_components: Tuple[PriorityComponent, ...],
    confidence: Optional[float],
    explanation: PriorityExplanation
)
```

#### 7.4.2 RelevanceAssessment

Relevance assessment for how well each candidate aligns with active objectives.

#### 7.4.3 CompetitionAssessment

```
CompetitionAssessment(
    competition_matrix: Tuple[CompetitionMatrixEntry, ...],
    dominant_candidates: Tuple[FocusTargetId, ...],
    suppressed_candidates: Tuple[FocusTargetId, ...],
    compatibility_score: float
)
```

#### 7.4.4 SuppressionAssessment

Recommendations for which targets should be suppressed.

#### 7.4.5 PrecisionAssessment

```
PrecisionAssessment(
    recommended_bandwidth: float,
    precision_mode: str,
    confidence: Optional[float]
)
```

#### 7.4.6 PersistenceAssessment

```
PersistenceAssessment(
    estimated_duration_seconds: float,
    persistence_mode: str,
    stability_score: float
)
```

#### 7.4.7 BiasAssessment

```
BiasAssessment(
    modality_bias: Dict[str, float],
    confidence: Optional[float]
)
```

#### 7.4.8 AllocationRecommendation

```
AllocationRecommendation(
    estimated_resource_budget: Dict[str, float],
    urgency_ranking: Tuple[FocusTargetId, ...]
)
```

### 7.5 Immutability Guarantees

- `FocusAssessment` is a frozen dataclass
- All nested assessments are frozen dataclasses
- No runtime references (no callbacks, no threads)
- JSON-compatible serialization

---

## 8. Interaction Model

### 8.1 Executive Layer Interaction

```
Executive → Focusing Input:
    - Active objectives
    - Objective hierarchy
    - Current commitment state
    - Policy constraints
    - Resource constraints

Focusing → Executive Output:
    - FocusAssessment (advisory)
    
Executive → Decision:
    - Accept recommendation
    - Accept with modification
    - Preserve current focus
    - Defer change
    - Reject recommendation
```

### 8.2 Attention Capability Interaction

```
Attention Capability ← Focusing:
    - Receives FocusAssessment
    
Attention Capability → Selection:
    - Selects focus from recommendations
    - May modify priority ordering
    
Focusing may receive feedback:
    - Which recommendations were applied
    - Why modifications were made
```

### 8.3 Working Memory Interaction

```
Working Memory → Focusing:
    - Provides WM items as candidates
    - Provides current focus state
    
Focusing → Working Memory:
    - Provides priority estimates for WM items
    - Recommends which items deserve sustained attention
```

### 8.4 Perception Interaction

```
Perception → Focusing:
    - Provides percepts as candidates
    
Focusing → Perception:
    - Estimates priority of perceptual inputs
    - Recommends modality bias for perception
```

### 8.5 Alerting Network Interaction

```
Alerting Network → Executive:
    - Produces alert assessment
    
Executive → Focusing (via projection):
    - Includes alert evidence in projection
    
Focusing → Assessment:
    - Considers alert priority in recommendations
```

---

## 9. Architectural Laws

### 9.1 Computation vs Authority

| Law | Statement |
|-----|-----------|
| **FOCUS-LAW-001** | The Focusing Network computes; it never decides. |
| **FOCUS-LAW-002** | Recommendations are advisory only. |
| **FOCUS-LAW-003** | Authority belongs to Executive Coordination, not computation. |
| **FOCUS-LAW-004** | Behavior belongs to Execution Layer, not Focusing Network. |

### 9.2 Runtime Neutrality

| Law | Statement |
|-----|-----------|
| **FOCUS-LAW-005** | FocusingNetwork never owns runtime infrastructure. |
| **FOCUS-LAW-006** | No direct Core Scheduler interaction allowed. |
| **FOCUS-LAW-007** | No thread manipulation permitted. |
| **FOCUS-LAW-008** | No loop or cycle selection permitted. |

### 9.3 State Management

| Law | Statement |
|-----|-----------|
| **FOCUS-LAW-009** | All inputs and outputs are immutable. |
| **FOCUS-LAW-010** | State transitions produce new instances, not mutate existing state. |
| **FOCUS-LAW-011** | History is preserved but never controls current computation. |

### 9.4 Dependency Constraints

| Law | Statement |
|-----|-----------|
| **FOCUS-LAW-012** | FocusingNetwork depends only on contracts and models. |
| **FOCUS-LAW-013** | No circular dependencies permitted. |
| **FOCUS-LAW-014** | External systems depend on contracts, never implementations. |

### 9.5 Validation

| Law | Statement |
|-----|-----------|
| **FOCUS-LAW-015** | All inputs must be validated before computation. |
| **FOCUS-LAW-016** | Configuration validation is enforced at construction time. |
| **FOCUS-LAW-017** | Output integrity checks are performed before release. |

---

## 10. Invariants

### 10.1 Ownership Invariants

| Invariant ID | Statement | Severity |
|--------------|-----------|----------|
| `OWN-INV-001` | Focusing Network owns only computational recommendations | MUST |
| `OWN-INV-002` | Behavioral authority never resides in Focusing Network | MUST |
| `OWN-INV-003` | Runtime ownership never resides in Focusing Network | MUST |

### 10.2 Immutability Invariants

| Invariant ID | Statement | Severity |
|--------------|-----------|----------|
| `IMM-INV-001` | All public data structures are frozen dataclasses | MUST |
| `IMM-INV-002` | No mutable state is shared across computations | MUST |
| `IMM-INV-003` | Assessment outputs are never mutated after creation | MUST |

### 0.3 Determinism Invariants

| Invariant ID | Statement | Severity |
|--------------|-----------|----------|
| `DET-INV-001` | Same inputs always produce same outputs | MUST |
| `DET-INV-002` | No random number generation in computation | SHOULD |
| `DET-INV-003` | No time-based side effects in pure computation | SHOULD |

### 10.4 Contract Invariants

| Invariant ID | Statement | Severity |
|--------------|-----------|----------|
| `CON-INV-001` | Input contracts are never violated by Focusing Network | MUST |
| `CON-INV-002` | Output contracts always contain required fields | MUST |
| `CON-INV-003` | Versioning policy is respected in all interactions | MUST |

### 10.5 Validation Invariants

| Invariant ID | Statement | Severity |
|--------------|-----------|----------|
| `VAL-INV-001` | Input validation occurs before each pipeline stage | MUST |
| `VAL-INV-002` | Output validation occurs after each pipeline stage | SHOULD |
| `VAL-INV-003` | Configuration is validated before pipeline execution | MUST |

---

## 11. Error Semantics

### 11.1 Invalid Input Handling

When input validation fails:

```
ValidationResult(
    is_valid: bool = False,
    error_messages: Tuple[str, ...],
    invalid_fields: Dict[str, Any]
)
```

**Behavior:**
- Validation errors are reported before computation begins
- Partial inputs may be accepted with defaults where possible
- Complete failure occurs only for critical validation errors

### 11.2 Partial Computation

When some pipeline stages cannot complete:

```
PartialComputationResult(
    completed_stages: Tuple[str, ...],
    failed_stage: Optional[str],
    error_message: Optional[str],
    partial_assessment: Optional[FocusAssessment]
)
```

**Behavior:**
- As much computation as possible is performed
- Partial results are preserved when safe
- Errors do not corrupt valid intermediate state

### 11.3 Uncertainty Handling

When confidence in estimates is low:

```
UncertaintyReport(
    confidence_level: float,
    uncertainty_reasons: Tuple[str, ...],
    recommendation_for_higher_confidence: Optional[str]
)
```

**Behavior:**
- Low-confidence assessments are marked explicitly
- Reasoning explains why confidence is low
- Recommendations may suggest gathering more information

### 11.4 Unsupported Targets

When a target cannot be processed:

```
UnsupportedTargetReport(
    target_id: FocusTargetId,
    reason: str,
    fallback_recommendation: Optional[str]
)
```

**Behavior:**
- Unsupported targets are identified clearly
- Reasoning is provided for why processing failed
- Fallback recommendations may suggest alternatives

### 11.5 Contract Violations

When contract boundaries are violated:

```
ContractViolationReport(
    violation_type: str,
    source_contract: str,
    target_contract: str,
    error_message: str
)
```

**Behavior:**
- Contract violations are treated as failures
- Error messages identify which contracts were involved
- System state remains consistent (no partial changes)

---

## 12. Explainability

### 12.1 Minimum Explainability Guarantees

Every `FocusAssessment` SHALL explain:

| Component | Required Explanation |
|-----------|---------------------|
| **Priority** | Why this priority was assigned; goal alignment evidence |
| **Competition** | Which targets compete and why; dominance analysis |
| **Suppression** | Which targets should be suppressed and why |
| **Precision** | Why this precision level is recommended |
| **Confidence** | What evidential support exists for the assessment |
| **Resource Recommendation** | How much budget is needed and why |

### 12.2 Explanation Structure

```
AssessmentExplanation(
    explanation_id: str,
    component_type: str,  # "priority", "competition", etc.
    rationale: str,
    supporting_evidence: Tuple[ProvenanceRecord, ...],
    confidence_score: float
)
```

### 12.3 Rationale Requirements

Every `AssessmentExplanation` MUST include:

| Field | Description |
|-------|-------------|
| `rationale` | Human-readable explanation of the assessment |
| `supporting_evidence` | Provenance records supporting this assessment |
| `confidence_score` | Confidence in this specific explanation |

### 12.4 Explainability Validation

Explainability is validated as part of output validation:

- All required explanations are present
- Rationales contain substantive reasoning (not empty)
- Supporting evidence references valid provenance records
- Confidence scores are within [0.0, 1.0] range

---

## 13. Determinism

### 13.1 Deterministic Guarantees

| Guarantee | Description |
|-----------|-------------|
| **Input equivalence** | Identical inputs always produce identical outputs |
| **Configuration stability** | Same configuration produces same results |
| **Revision consistency** | Same revision level of projections produces same output |
| **Ordering guarantees** | Pipeline stage ordering is fixed and reproducible |

### 13.2 Non-Deterministic Factors

The following factors may affect determinism:

| Factor | Impact | Mitigation |
|--------|--------|------------|
| `datetime.utcnow()` | Timestamp variations in tests | Parameter injection for testing |
| UUID generation | Different IDs across runs | Use fixed IDs in tests |

### 13.3 Determinism Verification

Conforming implementations SHALL verify:

- Same inputs produce same outputs
- No random number generation in computation
- No external state dependencies (except projections)

---

## 14. Extensibility

### 14.1 Approved Extension Points

| Extension Point | Description |
|-----------------|-------------|
| **Priority Models** | New priority computation algorithms via estimator modules |
| **Relevance Models** | New relevance estimation algorithms |
| **Competition Algorithms** | New competition resolution strategies |
| **Precision Models** | New precision estimation algorithms |
| **Persistence Models** | New persistence maintenance algorithms |

### 14.2 Extension Procedures

To extend the Focusing Network:

1. Implement new estimator class in appropriate module
2. Ensure it follows existing contract interfaces
3. Maintain immutability guarantees
4. Add to `__init__.py` exports if public

### 14.3 Forbidden Modifications

| Modification Type | Approval Required |
|-------------------|-------------------|
| Ownership changes | Major revision with architectural review |
| Dependency direction changes | Major revision with architectural review |
| Public API signature changes (non-additive) | Major revision |
| Computational pipeline reordering | Major revision |
| Contract interface modifications | Major revision |

### 14.4 Extension Validation

New extensions SHALL be validated against:

- Architectural principles
- Ownership boundaries
- Determinism guarantees
- Explainability requirements

---

## 15. Compatibility

### 15.1 Backward Compatibility

| Guarantee | Description |
|-----------|-------------|
| **Public API stability** | Existing method signatures never changed |
| **Field defaults** | New fields always have sensible defaults |
| **Serialization compatibility** | Old state can be loaded into new code |
| **Contract extensibility** | Consumers handle unknown fields gracefully |

### 15.2 Contract Evolution

Minor version changes may add:

- New optional fields with defaults
- New contracts (additive only)
- New estimator implementations

Major version changes may require:

- API signature modifications
- Behavioral changes
- Migration procedures

### 15.3 Deprecation Policy

| Action | Timeline |
|--------|----------|
| Deprecate item | Announce in release notes |
| Maintain backward compatibility | Until next major version |
| Remove deprecated item | After three releases minimum |

### 15.4 Migration Rules

When migrating between versions:

```
MigrationReport(
    source_version: str,
    target_version: str,
    breaking_changes: Tuple[str, ...],
    migration_actions: Tuple[MigrationAction, ...]
)
```

---

## 16. Compliance Requirements

### 16.1 Conforming Implementation Requirements

A conforming implementation SHALL:

| Requirement | Description |
|-------------|-------------|
| **C1** | Implement all required contracts |
| **C2** | Produce immutable assessment outputs |
| **C3** | Validate all inputs before computation |
| **C4** | Maintain determinism for same inputs |
| **C5** | Include explainability with every assessment |
| **C6** | Respect ownership boundaries (no behavioral policy) |
| **C7** | Use frozen dataclasses for all public models |
| **C8** | Follow the canonical pipeline structure |
| **C9** | Emit diagnostic events for all pipeline stages |
| **C10** | Support backward-compatible contract evolution |

### 16.2 Conforming Implementation Restrictions

A conforming implementation SHALL NOT:

| Restriction | Description |
|-------------|-------------|
| **R1** | Implement behavioral policy or execution semantics |
| **R2** | Directly manipulate runtime infrastructure (threads, loops, cycles) |
| **R3** | Own working memory or perception components |
| **R4** | Make executive decisions about attention allocation |
| **R5** | Mutate input data structures during computation |
| **R6** | Introduce forbidden dependencies (Core, Execution, etc.) |

### 16.3 Validation Checklist

Before declaring conformance:

- [ ] All required contracts are implemented
- [ ] All outputs are immutable (frozen dataclasses)
- [ ] Input validation occurs before computation
- [ ] Output validation occurs after computation
- [ ] Determinism is verified for identical inputs
- [ ] Explainability is complete for all assessments
- [ ] Ownership boundaries are maintained
- [ ] Diagnostic events are emitted for all stages

---

## 17. Traceability Matrix

### 17.1 Architectural Glossary References

| Term | Reference |
|------|-----------|
| Core | `core_architectural_glossary.md` |
| Execution | Gordon Architecture Documentation |
| Capabilities | Gordon Architecture Documentation |
| Attention Capability | Future phase specification |

### 17.2 Previous Phase Dependencies

| Phase | Document |
|-------|----------|
| 4.2.2 - Canonical Models | models.py, Phase 4.2.2 report |
| 4.2.3 - Priority Estimators | priority/estimators.py |
| 4.2.4 - Competition Analysis | relevance/competition.py |
| 4.2.7 - Pipeline Integration | pipeline.py, phase-4.2.7-report.md |
| 4.2.8 - Contracts | contracts/, phase-4.2.8-contracts-report.md |
| 4.2.9 - Executive Interaction | executive/__init__.py, phase-4.2.9-executive-interaction-report.md |
| 4.2.10 - Behavioral Examples | examples/, phase-4.2.10-report.md |
| 4.2.13 - Certification | phase-4.2.13-certification-report.md |
| 4.2.14 - Architectural Freeze | phase-4.2.14-architectural-freeze.md |

### 17.3 Contract Version Mapping

| Component | Current Version | Compatibility Policy |
|-----------|-----------------|---------------------|
| FocusAssessment | 1.0.0 | Backward compatible |
| PriorityEstimator | 1.0.0 | Additive only |
| CompetitionAnalyzer | 1.0.0 | Additive only |

---

## 18. Specification Completeness Assessment

### 18.1 Covered Architectural Concepts

| Concept | Status | Section |
|---------|--------|---------|
| Purpose | ✅ Complete | Section 1 |
| Context | ✅ Complete | Section 2 |
| Ownership | ✅ Complete | Section 3 |
| Contracts | ✅ Complete | Section 4 |
| Pipeline | ✅ Complete | Section 5 |
| State Model | ✅ Complete | Section 6 |
| FocusAssessment | ✅ Complete | Section 7 |
| Interaction Model | ✅ Complete | Section 8 |
| Architectural Laws | ✅ Complete | Section 9 |
| Invariants | ✅ Complete | Section 10 |
| Error Semantics | ✅ Complete | Section 11 |
| Explainability | ✅ Complete | Section 12 |
| Determinism | ✅ Complete | Section 13 |
| Extensibility | ✅ Complete | Section 14 |
| Compatibility | ✅ Complete | Section 15 |
| Compliance Requirements | ✅ Complete | Section 16 |

### 18.2 Normative Sections

| Section | Status | Description |
|---------|--------|-------------|
| 3 - Ownership | ✅Normative | Defines what Focusing Network owns/does not own |
| 4 - Public Contracts | ✅Normative | Defines interface contracts and versioning policy |
| 5 - Computational Pipeline | ✅Normative | Defines pipeline stages and transitions |
| 7 - FocusAssessment | ✅Normative | Defines assessment structure and requirements |
| 9 - Architectural Laws | ✅Normative | Defines immutable architectural principles |
| 10 - Invariants | ✅Normative | Defines required invariant conditions |
| 16 - Compliance | ✅Normative | Defines conformance requirements |

### 18.3 Remaining Non-Normative Guidance

The following sections provide guidance but are not normative:

- Implementation examples
- Behavioral reference flows (see `reference_flows.md`)
- Test coverage recommendations
- Performance optimization guidelines

---

## 19. Specification Usage Guidelines

### 19.1 For Python Implementations

A conforming Python implementation SHALL:

- Use frozen dataclasses for all public models
- Implement contracts as abstract base classes or protocols
- Follow the pipeline structure in `pipeline.py`
- Support JSON serialization of all assessments

### 19.2 For C++ Implementations

A conforming C++ implementation SHALL:

- Use immutable data structures (const-correct)
- Implement contract interfaces via virtual methods
- Maintain pipeline stage ordering
- Support serialization to/from JSON-compatible formats

### 19.3 For Rust Implementations

A conforming Rust implementation SHALL:

- Use `#[derive(Clone)]` with `Copy` for small types where appropriate
- Use `Send + Sync` markers for thread safety
- Follow the immutable data pattern
- Support serde-based serialization

### 19.4 For Distributed Implementations

A distributed implementation SHALL:

- Serialize assessments for network transmission
- Preserve provenance information across nodes
- Handle partial failures gracefully
- Maintain deterministic behavior across replicas

---

## Appendix A: Complete File Inventory

### Core Implementation Files

| File | Purpose | Version |
|------|---------|---------|
| `focusing/__init__.py` | Main package exports | 1.0.0 |
| `focusing/models.py` | Immutable data structures | 1.0.0 |
| `focusing/pipeline.py` | Pipeline executor | 1.0.0 |
| `focusing/network.py` | Network orchestration | 1.0.0 |
| `focusing/configuration.py` | Configuration definitions | 1.0.0 |

### Contract Files

| File | Purpose | Version |
|------|---------|---------|
| `contracts/__init__.py` | Package exports | 1.0.0 |
| `contracts/inputs.py` | Provider interfaces | 1.0.0 |
| `contracts/outputs.py` | Consumer interfaces | 1.0.0 |
| `contracts/context.py` | Context projections | 1.0.0 |
| `contracts/state.py` | State views | 1.0.0 |

### Subsystem Files

| File | Purpose |
|------|---------|
| `priority/estimators.py` | Priority computation algorithms |
| `relevance/estimators.py` | Relevance estimation algorithms |
| `relevance/competition.py` | Competition analysis |
| `precision/__init__.py` | Precision estimation |
| `persistence/__init__.py` | Persistence maintenance |
| `bias/__init__.py` | Bias generation |
| `allocation/__init__.py` | Resource allocation recommendations |

---

## Appendix B: Summary Statistics

### Implementation Metrics

| Metric | Count |
|--------|-------|
| Core data structures | 30+ frozen dataclasses |
| Contract interfaces | 25+ interfaces |
| Pipeline stages | 9 stages |
| Assessment components | 8 assessment types |
| Subsystem modules | 6 algorithmic modules |

### Quality Metrics

| Metric | Score |
|--------|-------|
| Immutability guarantees | 10/10 |
| Contract clarity | 9/10 |
| Explainability coverage | 8/10 |
| Determinism guarantees | 9/10 |
| Ownership separation | 10/10 |

---

## Appendix C: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | August 14, 2026 | Initial canonical specification (Phase 4.2.15) |

---

**END OF CANONICAL ARCHITECTURAL SPECIFICATION**

*This document constitutes the definitive architectural specification for the Gordon Focusing Network.*
*All future implementations MUST conform to this specification.*

---

## Phase 4.2.15 Completion Checklist

| Criterion | Status |
|-----------|--------|
| ✅ Specification structure defined | Complete |
| ✅ Architectural purpose documented | Complete |
| ✅ Architectural context mapped | Complete |
| ✅ Ownership normatively defined | Complete |
| ✅ Public contracts specified | Complete |
| ✅ Computational pipeline defined | Complete |
| ✅ State model specified | Complete |
| ✅ FocusAssessment structure defined | Complete |
| ✅ Interaction semantics documented | Complete |
| ✅ Architectural laws collected | Complete |
| ✅ Invariants complete | Complete |
| ✅ Error semantics described | Complete |
| ✅ Explainability requirements specified | Complete |
| ✅ Determinism guarantees defined | Complete |
| ✅ Extensibility points specified | Complete |
| ✅ Compatibility policy documented | Complete |
| ✅ Compliance requirements defined | Complete |

### Phase Verdict

**FOCUSING NETWORK SPECIFICATION COMPLETE**

The canonical architectural specification for the Gordon Focusing Network is complete and ready to serve as the single authoritative reference for all future implementations, regardless of programming language, runtime, or deployment environment.