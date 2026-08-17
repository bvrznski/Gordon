# Gordon Phase 5.7.2-A: Mermaid Diagrams

**Audit Date:** 2026-08-17  
**Purpose:** Visual diagrams for architecture audit

---

## PACKAGE ARCHITECTURE DIAGRAM

```mermaid
graph TB
    subgraph "src/agent/capabilities/"
        conscious[consciousness/] --> facade[ConsciousnessFacade]
        conscious --> registry[RegistryManager]
        conscious --> contracts[Contract Definitions]
        
        experiential_field[experiential_field/] 
        experiential_field_style[style experiential_field fill:#f9f,stroke:#333,stroke-dasharray: 5 5]
        experiential_field_label[label="⚠️ MISSING - Phase 5.7.2 Target"]
        
        conscious --> experiential_field
    end
    
    subgraph "src/agent/components/systems/"
        workspace[networks/workspace/] --> global[Global Availability]
        perception[perception/] --> integration[PerceptionIntegrationEngine]
        memory[memory/] --> persistence[Persistence]
    end
    
    facade -->|creates requests| experiential_field
    experiential_field -->|produces snapshots| CurrentContextSnapshot
    
    style conscious fill:#9f6,stroke:#333
    style experiential_field_label fill:#f96,stroke:#333,stroke-width:2px
    style facade fill:#69f,stroke:#333
```

---

## FIELD CONSTRUCTION PIPELINE DIAGRAM

```mermaid
graph TB
    subgraph "External Systems"
        Workspace[Workspace Network]
        Perception[Perception System]
    end
    
    subgraph "Consciousness Facade (Phase 5.7.1-I)"
        SubmitC[submit_contribution()]
        SourceVal[source validation]
        ExpCheck[expiration check]
    end
    
    subgraph "Experiential Field Builder (MISSING - Phase 5.7.2 Target)"
        Normalizer[normalize_contribution()]
        Dedup[deduplicate_content()]
        Integrator[integrate_into_field()]
        TransitionAuth[transition_authority()]
        SnapshotMgr[snapshot_manager()]
    end
    
    subgraph "Output"
        CurrentSnapshot[CurrentContextSnapshot]
    end
    
    Workspace --> SubmitC
    Perception --> SubmitC
    
    SubmitC --> SourceVal
    SourceVal --> ExpCheck
    ExpCheck --> Normalizer
    Normalizer --> Dedup
    Dedup --> Integrator
    Integrator --> TransitionAuth
    TransitionAuth --> SnapshotMgr
    SnapshotMgr --> CurrentSnapshot
    
    style Workspace fill:#9f6,stroke:#333
    style Perception fill:#9f6,stroke:#333
    style SubmitC fill:#fc6,stroke:#333
    style SourceVal fill:#fc6,stroke:#333
    style ExpCheck fill:#fc6,stroke:#333
    
    Normalizer_label[normalize_contribution()]
    Dedup_label[deduplicate_content()]
    Integrator_label[integrate_into_field()]
    TransitionAuth_label[transition_authority()]
    SnapshotMgr_label[snapshot_manager()]
    
    style Normalizer_label fill:#f96,stroke:#333
    style Dedup_label fill:#f96,stroke:#333
    style Integrator_label fill:#f96,stroke:#333
    style TransitionAuth_label fill:#f96,stroke:#333
    style SnapshotMgr_label fill:#f96,stroke:#333
    
    CurrentSnapshot[CurrentContextSnapshot]
```

---

## OWNERSHIP GRAPH DIAGRAM

```mermaid
graph LR
    Workspace[Workspace Network] -->|owns: global availability| WState[Global State]
    
    EXF[Experiential Field Builder - MISSING] -->|owns: field construction| FState[Field State]
    EXF -->|owns: snapshots| SHist[Snapshot History]
    EXF -->|owns: transitions| TLog[Transition Log]
    
    Consciousness[Consciousness (Phase 5.7.1-I)] -->|owns: contracts| CContracts[Contract Definitions]
    
    Perception[Perception System] -->|owns: integration| PState[Integrated Percepts]
    
    Memory[Memory System] -->|owns: persistence| MState[Memory State]
    
    WState -->|contributes via ContributionEnvelope| Consciousness
    PState -->|projects via ProjectionEnvelope| Consciousness
    MState -->|activates WorkingMemory| Consciousness
    
    Consciousness -->|creates field construction requests| EXF
    FState -->|published as snapshot| Consciousness
    
    style Workspace fill:#9f6,stroke:#333
    style Consciousness fill:#f96,stroke:#333
    style Perception fill:#9f6,stroke:#333
    style Memory fill:#9f6,stroke:#333
```

---

## DEPENDENCY GRAPH DIAGRAM

```mermaid
graph LR
    A[Workspace Network] --> B[ContributionEnvelope Contract]
    C[Perception System] --> D[ProjectionEnvelope Contract]
    E[Memory System] --> F[WorkingMemory State]
    
    G[Consciousness] --> H[Source Registry]
    G --> I[Extension Registry]
    G --> J[Contract Definitions]
    
    K[Experiential Field Builder - MISSING] --> L[FieldBuilder Runtime]
    K --> M[SnapshotManager]
    K --> N[TransitionAuthority]
    
    B -->|used by| K
    D -->|used by| K
    F -->|used by| K
    
    style A fill:#9f6,stroke:#333
    style C fill:#9f6,stroke:#333
    style E fill:#9f6,stroke:#333
    style G fill:#f96,stroke:#333
    style K fill:#ccc,stroke:#333,stroke-dasharray:5 5
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
    
    CF->>CF: validate_source(source_id)
    CF->>CF: check_expiration(freshness_utc)
    
    Note over EXF: Phase 5.7.2-I - Runtime Implementation Required
    EXF->>EXF: normalize_contribution(envelope)
    EXF->>EXF: deduplicate_content(content_hash)
    EXF->>EXF: integrate_into_field_state(element)
    
    Note over SM,CS: Transition & Publication
    EXF->>SM: request_transition(current_generation)
    SM->>SM: create_snapshot(field_elements, new_generation)
    SM->>CS: publish(CurrentContextSnapshot)
    
    CS->>CS: generation += 1
    CS->>CS: previous_generation = current_generation
    
    Note over WS,PE: Next cycle starts with updated snapshot
```

---

## TRANSITION PIPELINE DIAGRAM

```mermaid
graph TB
    subgraph "Request"
        R1[Transition requested]
    end
    
    subgraph "Validation (Phase 5.7.1-I)"
        V1[Check pending transitions?]
    end
    
    subgraph "Runtime Transition Phase (MISSING - Phase 5.7.2 Target)"
        T1[Prepare new generation state]
        T2[Atomic commit to snapshot manager]
        T3[Increment generation number]
        T4[Publish to Cognition]
    end
    
    R1 --> V1
    V1 -- No pending --> T1
    T1 --> T2
    T2 --> T3
    T3 --> T4
    
    T1_label[T1: Prepare new generation state]
    T2_label[T2: Atomic commit to snapshot manager]
    T3_label[T3: Increment generation number]
    T4_label[T4: Publish to Cognition]
    
    style T1_label fill:#f96,stroke:#333
    style T2_label fill:#f96,stroke:#333
    style T3_label fill:#f96,stroke:#333
    style T4_label fill:#f96,stroke:#333
```

---

## CAPACITY POLICY DIAGRAM

```mermaid
graph TB
    subgraph "Input"
        C[Contributions to Process]
    end
    
    subgraph "Capacity Check (MISSING - Phase 5.7.2 Target)"
        CS[Current Field Size]
        BC[Exceeds Max Field Size?]
    end
    
    subgraph "Decision (MISSING - Phase 5.7.2 Target)"
        A[Add to Field]
        T[Truncate Oldest]
    end
    
    C --> CS
    CS --> BC
    BC -- NO --> A
    BC -- YES --> T
    T --> A
    
    A_label[Add to Field]
    T_label[Truncate Oldest (LRU)]
    
    style A_label fill:#f96,stroke:#333
    style T_label fill:#f96,stroke:#333
```

---

## CONCLUSION

The diagrams show:
- ✅ Contract definitions and validation flow in Phase 5.7.1-I
- ⚠️ Missing runtime implementation for field construction (Phase 5.7.2 Target)
- ❌ No runtime for transition authority, snapshot manager, normalizer, integrator

Phase 5.7.2-I must implement the experiential_field/ package to complete the architecture.

---

*End of Mermaid Diagrams*