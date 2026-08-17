# Gordon Phase 5.7.2-A: Field Construction Pipeline Diagram

**Audit Date:** 2026-08-17  
**Purpose:** Visualize the field construction pipeline from contributions to snapshots

---

## CURRENT PIPELINE (Phase 5.7.1-I) - INCOMPLETE

```mermaid
graph TB
    subgraph "External Subsystems"
        Workspace[Workspace Network]
        Perception[Perception System]
        WorkingMem[Working Memory]
    end
    
    subgraph "Consciousness (Phase 5.7.1-I)"
        SubmitC[submit_contribution]
        SubmitP[submit_projection]
        SourceVal[Source Validation]
        ExpCheck[Expiration Check]
        RegisterS[Register Source]
    end
    
    Workspace -->|ContributionEnvelope| SubmitC
    Perception -->|ProjectionEnvelope| SubmitP
    
    SubmitC --> SourceVal
    SubmitP --> SourceVal
    SourceVal --> ExpCheck
    ExpCheck --> RegisterS
    
    RegisterS -->|Contracts Defined But No Runtime| Missing[⚠️ MISSING: Field Construction Runtime]
    
    style Workspace fill:#9f6,stroke:#333
    style Perception fill:#9f6,stroke:#333
    style WorkingMem fill:#9f6,stroke:#333
    style Missing fill:#f96,stroke:#333,stroke-dasharray:5 5
```

---

## EXPECTED PIPELINE (Phase 5.7.2-I) - COMPLETE

```mermaid
graph TB
    subgraph "External Subsystems"
        Workspace[Workspace Network]
        Perception[Perception System]
        WorkingMem[Working Memory]
    end
    
    subgraph "Consciousness Facade"
        SubmitC[submit_contribution]
        SubmitP[submit_projection]
    end
    
    subgraph "Experiential Field Builder"
        Normalizer[Normalizer]
        Integrator[Integrator]
        TransitionAuth[Transition Authority]
        SnapshotMgr[Snapshot Manager]
    end
    
    subgraph "Current Context Snapshot"
        CS[CurrentContextSnapshot]
    end
    
    Workspace -->|ContributionEnvelope| SubmitC
    Perception -->|ProjectionEnvelope| SubmitP
    WorkingMem -->|WorkingMemoryState| SubmitC
    
    SubmitC --> Normalizer
    SubmitP --> Integrator
    
    Normalizer --> Integrator
    Integrator --> TransitionAuth
    
    TransitionAuth --> SnapshotMgr
    SnapshotMgr --> CS
    
    style Workspace fill:#9f6,stroke:#333
    style Perception fill:#9f6,stroke:#333
    style WorkingMem fill:#9f6,stroke:#333
    style Normalizer fill:#69f,stroke:#333
    style Integrator fill:#69f,stroke:#333
    style TransitionAuth fill:#69f,stroke:#333
    style SnapshotMgr fill:#69f,stroke:#333
```

---

## CONTRIBUTION FLOW DIAGRAM

```mermaid
sequenceDiagram
    participant WS as Workspace Network
    participant PE as Perception System
    participant CF as ConsciousnessFacade
    participant EXF as ExperientialFieldBuilder
    participant SM as SnapshotManager
    participant CS as CurrentContextSnapshot
    
    Note over WS,PE: Phase 5.7.1-I - Contracts Defined But No Runtime
    WS->>CF: submit_contribution(ContributionEnvelope)
    PE->>CF: submit_projection(ProjectionEnvelope)
    
    CF->>CF: Validate Source
    CF->>CF: Check Expiration
    
    Note over EXF: Phase 5.7.2-I - Runtime Implementation Required
    EXF->>EXF: Normalize contribution
    EXF->>EXF: Deduplicate content
    EXF->>EXF: Integrate into field state
    
    EXF->>SM: request_transition()
    SM->>SM: Create immutable snapshot
    SM->>CS: Publish new generation
    
    Note over CS: Generation incremented, previous generation preserved
```

---

## TRANSITION PIPELINE

```mermaid
graph TB
    subgraph "Input"
        Contributions[Contributions from Subsystems]
    end
    
    subgraph "Processing"
        Validate[Validate Source/Expiration]
        Normalize[Normalize Content]
        Deduplicate[Deduplicate]
        Merge[Merge into Field State]
    end
    
    subgraph "Transition"
        CheckPending[Check Pending Transitions?]
        PrepareNew[Prepare New Generation]
        CommitAtomic[Atomic Commit]
    end
    
    subgraph "Output"
        NewSnapshot[New CurrentContextSnapshot]
        PrevSnapshot[Previous Snapshot Preserved]
    end
    
    Contributions --> Validate
    Validate --> Normalize
    Normalize --> Deduplicate
    Deduplicate --> Merge
    Merge --> CheckPending
    
    CheckPending -- YES --> PrepareNew
    CheckPending -- NO --> CommitAtomic
    
    PrepareNew --> CommitAtomic
    
    CommitAtomic --> NewSnapshot
    CommitAtomic --> PrevSnapshot
    
    style Contributions fill:#f96,stroke:#333
    style Validate fill:#6cf,stroke:#333
    style Normalize fill:#6cf,stroke:#333
    style Deduplicate fill:#6cf,stroke:#333
    style Merge fill:#6cf,stroke:#333
    style CheckPending fill:#fc6,stroke:#333
    style CommitAtomic fill:#69f,stroke:#333,stroke-width:2px
    style NewSnapshot fill:#9f6,stroke:#333
    style PrevSnapshot fill:#9f6,stroke:#333
```

---

## CAPACITY ENFORCEMENT FLOW

```mermaid
graph TB
    subgraph "Input"
        Contributions[Contributions to Process]
    end
    
    subgraph "Capacity Check"
        FieldSize[Current Field Size]
        BoundCheck[Exceeds Max Field Size?]
    end
    
    subgraph "Decision"
        Accept[Add to Field]
        Reject[Reject Contribution]
        Truncate[Truncate Oldest]
    end
    
    Contributions --> FieldSize
    FieldSize --> BoundCheck
    BoundCheck -- NO --> Accept
    BoundCheck -- YES --> Truncate
    Truncate --> Accept
    
    Accept --> FieldSize
    
    style Contributions fill:#f96,stroke:#333
    style FieldSize fill:#fc6,stroke:#333
    style BoundCheck fill:#fc6,stroke:#333
    style Truncate fill:#69f,stroke:#333
```

---

## CONCLUSION

The current pipeline stops at validation:
- ✅ Contribution envelopes defined (ContributionEnvelope, ProjectionEnvelope)
- ✅ Source validation implemented
- ❌ No runtime for field construction
- ❌ No normalization
- ❌ No deduplication
- ❌ No integration
- ❌ No atomic transitions
- ❌ No snapshot production

Phase 5.7.2-I must implement the experiential_field/ package to complete the pipeline with:
1. Normalizer - for contribution standardization
2. Integrator - for merging into field state
3. Transition Authority - for atomic commits
4. Snapshot Manager - for immutable snapshot production