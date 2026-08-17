# Gordon Phase 5.7.5-A: Presence & Awareness Architecture Diagrams

**Diagram Date:** 2026-08-17  
**Phase:** 5.7.5-A Presence & Awareness Audit

---

## PACKAGE ARCHITECTURE

```mermaid
graph TB
    subgraph "Consciousness Capability"
        C["consciousness/"]
        
        C --> E["experiential_field/ ✅ (5.7.2-I)"]
        C --> I["intentionality/ ✅ (5.7.3-I)"]
        C --> T["temporality/ ✅ (5.7.4-I)"]
        C --> P["presence/ ❌ (5.7.5-A MISSING)"]
        
        subgraph "Existing Subpackages"
            E --> EF1["builder.py"]
            E --> EF2["snapshot.py"]
            E --> EF3["transition.py"]
            
            I --> IC1["engine.py"]
            I --> IC2["object.py"]
            I --> IC3["relation.py"]
            
            T --> TC1["engine.py"]
            T --> TC2["retention.py"]
            T --> TC3["presentation.py"]
        end
        
        subgraph "Missing Subpackage"
            P --> P1["engine.py (PENDING)"]
            P --> P2["state.py (PENDING)"]
            P --> P3["admission.py (PENDING)"]
            P --> P4["persistence.py (PENDING)"]
            P --> P5["fading.py (PENDING)"]
            P --> P6["withdrawal.py (PENDING)"]
            P --> P7["snapshot.py (PENDING)"]
        end
    end
    
    style C fill:#e1f5ff
    style E fill:#c8e6c9
    style I fill:#c8e6c9
    style T fill:#c8e6c9
    style P fill:#ffcdd2
```

---

## PRESENCE LIFECYCLE

```mermaid
stateDiagram-v2
    [*] --> CANDIDATE
    
    CANDIDATE --> ADMITTED: PresenceEngine.admit()
    
    ADMITTED --> ACTIVE_PRESENCE: becomes_current_generation
    
    ACTIVE_PRESENCE --> WEAKENING: fading_policy_triggered
    ACTIVE_PRESENCE --> ACTIVE_PRESENCE: no_fading_trigger
    
    WEAKENING --> FADE_IN_PROGRESS: fade_continues
    
    FADE_IN_PROGRESS --> WITHDRAWN: withdrawal_decision_made
    
    WITHDRAWN --> [*]
    
    NOTE right of CANDIDATE
        External proposal
    end note
    
    NOTE left of ACTIVE_PRESENCE
        Consciously accessible
        in current context
    end note
    
    NOTE left of WEAKENING
        Transition state
        (transient)
    end note
    
    NOTE right of FADE_IN_PROGRESS
        Gradually losing
        accessibility
    end note
    
    NOTE left of WITHDRAWN
        No longer consciously
        accessible
    end note
```

---

## ADMISSION PIPELINE

```mermaid
sequenceDiagram
    participant E as ExternalSystem
    participant PE as PresenceEngine
    participant AV as AdmissionValidator
    participant AO as AdmissionOrderer
    
    Note over E,PE: Start of Contribution Submission
    E->>PE: submit_contribution(contribution)
    
    PE->>AV: validate(source_id, freshness, capacity)
    
    alt Valid Contribution
        AV-->>PE: validation_passed
        
        PE->>AO: order_contributions(current_queue, new_contribution)
        
        AO-->>PE: ordered_position
        
        alt Within Capacity
            PE->>PE: add_to_admitted_set(contribution)
            PE->>PE: record_admission_trace(admission_id)
            
            Note over PE: Bounded persistence policy applied
            
            PE-->>E: admission_granted(admission_id)
            
            Note over PE: Admitted content becomes candidate for
                         next generation's presence
            
        else Capacity Full
            PE-->>E: admission_rejected(reason="capacity_exceeded")
        end
        
    else Invalid Contribution
        AV-->>PE: validation_failed(error)
        PE-->>E: admission_rejected(reason=error)
    end
```

---

## ACCESSIBILITY MODEL

```mermaid
graph LR
    subgraph "Experiential Field"
        EF1["Field Content A"]
        EF2["Field Content B"]
        EF3["Field Content C"]
    end
    
    subgraph "Intentional Context"
        IC1["Intends toward A"]
        IC2["Intends toward B"]
    end
    
    subgraph "Temporal Context"
        TC1["Gen N-1 reference"]
        TC2["Gen N reference"]
    end
    
    subgraph "Presence Engine (MISSING)"
        PR_A["Accessible: A?"]
        PR_B["Accessible: B?"]
        PR_C["Accessible: C?"]
        
        PR_A -->|admission_policy| AD_A["Admitted A"]
        PR_B -->|admission_policy| AD_B["Admitted B"]
        PR_C -->|admission_policy| AD_C["Admitted C"]
        
        AD_A -->|persistence_policy| AC_A["Active Presence: A"]
        AD_B -->|persistence_policy| AC_B["Active Presence: B"]
        AD_C -->|fading_policy| FA_C["Fading: C"]
    end
    
    EF1 --> PR_A
    EF2 --> PR_B
    EF3 --> PR_C
    
    IC1 --> PR_A
    IC2 --> PR_B
    
    TC1 --> AC_A
    TC2 --> AC_B
    
    style PR_A fill:#ffccbc
    style PR_B fill:#ffccbc
    style PR_C fill:#ffccbc
    style AD_A fill:#b3e5fc
    style AD_B fill:#b3e5fc
    style AC_A fill:#c8e6c9
    style AC_B fill:#c8e6c9
    style FA_C fill:#ffcdd2
```

---

## TRANSITION PIPELINE

```mermaid
sequenceDiagram
    participant PE as PresenceEngine
    participant SA as StateAuthority
    participant SN as SnapshotPublisher
    
    Note over PE: Start of Transition Request
    
    PE->>SA: begin_transition(current_state)
    
    alt Valid Transition
        SA-->>PE: transition_id, previous_state
        
        PE->>PE: apply_state_changes(
            admitted_contents,
            faded_contents,
            withdrawn_contents
        )
        
        PE->>SN: prepare_snapshot(new_state)
        
        SN->>SN: create_immutable_snapshot()
        
        SN-->>PE: snapshot_id, new_generation
        
        PE->>SA: commit_transition(snapshot_id)
        
        SA-->>PE: transition_committed
        
        Note over PE: New presence state published atomically
                      Previous state preserved for replay
        
    else Invalid Transition
        SA-->>PE: invalid_transition(reason)
        Note over PE: Rollback to previous state
    end
```

---

## DEPENDENCY GRAPH

```mermaid
graph TD
    types["types.py"]
    constants["constants.py"]
    
    state["state.py"] --> types["types.py"]
    state["state.py"] --> constants["constants.py"]
    
    admission["admission.py"] --> state["state.py"]
    admission["admission.py"] --> types["types.py"]
    
    persistence["persistence.py"] --> state["state.py"]
    persistence["persistence.py"] --> constants["constants.py"]
    
    fading["fading.py"] --> state["state.py"]
    fading["fading.py"] --> persistence["persistence.py"]
    
    withdrawal["withdrawal.py"] --> fading["fading.py"]
    withdrawal["withdrawal.py"] --> state["state.py"]
    
    snapshot["snapshot.py"] --> state["state.py"]
    snapshot["snapshot.py"] --> types["types.py"]
    
    transition["transition.py"] --> snapshot["snapshot.py"]
    transition["transition.py"] --> state["state.py"]
    
    engine["engine.py"] -.->|imports all| state["state.py"]
    engine["engine.py"] -.->|imports all| admission["admission.py"]
    engine["engine.py"] -.->|imports all| persistence["persistence.py"]
    engine["engine.py"] -.->|imports all| fading["fading.py"]
    engine["engine.py"] -.->|imports all| withdrawal["withdrawal.py"]
    engine["engine.py"] -.->|imports all| snapshot["snapshot.py"]
    engine["engine.py"] -.->|imports all| transition["transition.py"]
    
    __init__["__init__.py"] --> engine["engine.py"]
    
    style types fill:#e3f2fd
    style constants fill:#c8e6c9
```

---

## PRESENCE STATE MACHINES

### Candidate to Admitted

```mermaid
stateDiagram-v2
    [*] --> CANDIDATE
    
    CANDIDATE --> EVALUATING: admission_request()
    
    EVALUATING --> ADMITTED: validation_passed, capacity_available
    EVALUATING --> REJECTED: validation_failed OR capacity_full
    
    ADMITTED --> [*]
    REJECTED --> [*]
```

### Active to Fading

```mermaid
stateDiagram-v2
    ACTIVE_PRESENCE --> WEAKENING: fading_policy()
    
    WEAKENING --> FADE_PROGRESS: fade_continues
    
    FADE_PROGRESS --> WITHDRAWN: withdrawal_decision()
    
    ACTIVE_PRESENCE --> ACTIVE_PRESENCE: persistence_extended
```

---

## RUNTIME INTEGRATION

```mermaid
graph TB
    subgraph "Experiential Field Builder"
        EF["FieldBuilder"]
        EF -->|produces| EF_SNAPSHOT[Field Snapshot]
    end
    
    subgraph "Intentional Context Engine"
        IC["IC Engine"]
        IC -->|creates| IC_TARGETS[Intentional Targets]
    end
    
    subgraph "Temporal Context Engine"
        TC["TC Engine"]
        TC -->|references| PREV_SNAPS[Previous Snapshots]
    end
    
    subgraph "Presence Engine (MISSING)"
        PR["Presence Engine"]
        
        EF_SNAPSHOT --> PR
        IC_TARGETS --> PR
        PREV_SNAPS --> PR
        
        PR -->|admits into| PR_ADMITTED[Admitted Set]
        PR_ADMITTED -->|maintains| PR_PERSISTENCE[Persistence Policy]
        PR_PERSISTENCE -->|applies fade policy| PR_FADE[Fading System]
        PR_FADE -->|produces| PR_STATE[Presence State]
        
        PR_STATE -->|publishes| PR_SNAPSHOT[Presence Snapshot]
    end
    
    subgraph "ConsciousnessFacade"
        F["Facade"]
        F -->|queries| PR_SNAPSHOT
    end
    
    EF_SNAPSHOT -.->|input to| PR
    IC_TARGETS -.->|input to| PR
    PREV_SNAPS -.->|input to| PR
    
    style PR fill:#ffcdd2
```

---

*End of Diagrams*