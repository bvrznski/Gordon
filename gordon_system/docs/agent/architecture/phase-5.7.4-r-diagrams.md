# Gordon Phase 5.7.4-R: Temporal Context Engine Architecture Diagrams

**Diagram Date:** 2026-08-17  
**Phase:** 5.7.4-R Remediation  

---

## PACKAGE ARCHITECTURE

```mermaid
graph TB
    subgraph "Consciousness Capability"
        C["consciousness/"] --> E["experiential_field/"]
        C --> I["intentionality/"]
        C --> T["temporality/"]
        
        T --> T1["__init__.py (exports)"]
        T --> T2["engine.py"]
        T --> T3["types.py"]
        T --> T4["exceptions.py"]
        T --> T5["constants.py"]
        
        subgraph "Temporal Components"
            T2 --> R["Retention Registry"]
            T2 --> P["Presentation Validator"]
            T2 --> Pr["Protention Set"]
            T2 --> CW["Continuity Window Manager"]
            T2 --> S["Snapshot Publisher"]
            T2 --> TA["Transition Authority"]
            
            R --> RR["RetentionRecords (bounded)"]
            P --> PR["PresentationReferences"]
            Pr --> PE["ProtentionExpectations"]
            CW --> CWB["ContinuityWindows"]
            S --> TS["TemporalSnapshots"]
            TA --> TT["TemporalTransitions"]
        end
    end
    
    style T fill:#e1f5ff
    style E fill:#c8e6c9
    style I fill:#c8e6c9
```

---

## TEMPORAL ORGANIZATION MODEL (Husserlian)

```mermaid
graph LR
    subgraph "Consciousness Stream"
        G0["Generation 0"]
        G1["Generation 1"]
        G2["Generation 2"]
        G3["Generation 3"]
        
        G0 -->|"retention"| G1
        G1 -->|"retention"| G2
        G2 -->|"retention"| G3
        
        G1 -.->|present| P1[Presentation]
        G2 -.->|present| P2[Presentation]
        G3 -.->|present| P3[Presentation]
        
        P1 -->|"protention"| E1[Next Context]
        P2 -->|"protention"| E2[Next Context]
        P3 -->|"protention"| E3[Next Context]
    end
    
    style P1 fill:#fff9c4
    style P2 fill:#fff9c4
    style P3 fill:#fff9c4
```

**Legend:**
- **Retention**: References to recently conscious contexts (bounded history)
- **Presentation**: Current conscious context anchor
- **Protention**: Immediate expectations about forthcoming context

---

## CONTINUITY WINDOWS

```mermaid
stateDiagram-v2
    [*] --> ACTIVE
    
    ACTIVE --> PAUSED: pause\(\)
    ACTIVE --> ACTIVE: advance\(\)
    
    PAUSED --> ACTIVE: resume\(\)
    PAUSED --> CLOSED: close\(\)
    
    ACTIVE --> DEGRADED: degrade\(\)
    DEGRADED --> ACTIVE: recover\(\)
    
    state ActiveWindow {
        [*] --> active
        active --> paused: pause()
        active --> closed: close()
        paused --> active: resume()
    }
```

---

## RETENTION - PRESENTATION - PROTENTION

```mermaid
graph LR
    subgraph "Retention (History)"
        R1["Gen N-2"]
        R2["Gen N-1"]
        R3["Gen N (current)"]
        
        R1 --> R2 --> R3
    end
    
    P[Presentation]
    
    subgraph "Protention (Future Expectations)"
        Pr1[Expected Context +1]
        Pr2[Expected Context +2]
    end
    
    R3 -->|references| P
    P -->|expects| Pr1
    P -->|expects| Pr2
    
    style R1 fill:#e3f2fd
    style R2 fill:#bbdefb
    style R3 fill:#90caf9
    style P fill:#fff9c4
    style Pr1 fill:#fce4ec
    style Pr2 fill:#f8bbd0
```

---

## GENERATION TRANSITIONS

```mermaid
sequenceDiagram
    participant EF as Experiential Field
    participant TE as Temporal Context Engine
    participant TS as Snapshot Publisher
    
    Note over EF,TS: Start of Generation N
    EF->>TE: get_current_context()
    TE->>TE: validate_retention_bounds()
    TE->>TE: check_protention_expectations()
    
    Note over EF,TS: Transition Triggered
    EF->>TE: next_context_available(context_N+1)
    TE->>TE: build_new_snapshot(
        retention_refs=[...],
        presentation=context_N+1,
        protentions=[...]
    )
    
    TE->>TS: publish(snapshot=New)
    TS-->>TE: snapshot_id="ts-gen{N+1}"
    
    Note over EF,TS: Generation N+1 Published
```

---

## DEPENDENCY GRAPH

```mermaid
graph TD
    types["types.py"] --> exceptions["exceptions.py"]
    types["types.py"] --> constants["constants.py"]
    
    retention["retention.py"] --> types["types.py"]
    presentation["presentation.py"] --> types["types.py"]
    protention["protention.py"] --> types["types.py"]
    
    continuity_window["continuity_window.py"] --> retention["retention.py"]
    continuity_window["continuity_window.py"] --> presentation["presentation.py"]
    continuity_window["continuity_window.py"] --> protention["protention.py"]
    
    snapshot["snapshot.py"] --> types["types.py"]
    transition["transition.py"] --> types["types.py"]
    
    validator["validator.py"] --> types["types.py"]
    validator["validator.py"] --> retention["retention.py"]
    
    health["health.py"] --> constants["constants.py"]
    diagnostics["diagnostics.py"] --> types["types.py"]
    
    integrity["integrity.py"] --> validator["validator.py"]
    
    engine["engine.py"] -.->|imports all| retention["retention.py"]
    engine["engine.py"] -.->|imports all| presentation["presentation.py"]
    engine["engine.py"] -.->|imports all| protention["protention.py"]
    engine["engine.py"] -.->|imports all| continuity_window["continuity_window.py"]
    engine["engine.py"] -.->|imports all| snapshot["snapshot.py"]
    engine["engine.py"] -.->|imports all| transition["transition.py"]
    engine["engine.py"] -.->|imports all| validator["validator.py"]
    
    __init__["__init__.py"] --> engine["engine.py"]
```

---

## LIFECYCLE INTEGRATION

```mermaid
graph LR
    subgraph "Lifecycle Stages"
        INIT["INIT: Engine Creation"]
        READY["READY: Initialized with EF context"]
        ACTIVE["ACTIVE: Processing transitions"]
        PAUSED["PAUSED: Transitions suspended"]
        CLOSED["CLOSED: Window terminated"]
        DEGRADED["DEGRADED: Continuity failure"]
    end
    
    INIT --> READY
    READY --> ACTIVE
    ACTIVE --> PAUSED
    ACTIVE --> ACTIVE
    PAUSED --> ACTIVE
    ACTIVE --> CLOSED
    ACTIVE --> DEGRADED
    DEGRADED --> ACTIVE
    
    style INIT fill:#e3f2fd
    style READY fill:#c8e6c9
    style ACTIVE fill:#c8e6c9
    style PAUSED fill:#fff9c4
    style CLOSED fill:#ffcdd2
    style DEGRADED fill:#ffccbc
```

---

## DETERMINISM PATTERN

```mermaid
graph LR
    subgraph "Test Context"
        TEST["Test Code"]
        FIXED["time_provider = fixed_time"]
    end
    
    subgraph "Production Context"
        PROD["Production Code"]
        REAL["time_provider = time.time"]
    end
    
    ENGINE["TemporalContextEngine"] -->|uses| FIXED
    ENGINE -->|uses| REAL
    
    TEST -.->|"injects"| ENGINE
    PROD -.->|"uses default"| ENGINE
    
    style FIXED fill:#c8e6c9
    style REAL fill:#e3f2fd
```

---

## TRANSITION AUTHORITY

```mermaid
graph LR
    subgraph "Transition Authority"
        BEGIN["begin_transition()"]
        VALIDATE["validate_transition()"]
        STORE["store_pending()"]
        COMMIT["commit_transition()"]
        ROLLBACK["rollback_transition()"]
    end
    
    USER["Caller"] --> BEGIN
    BEGIN --> VALIDATE
    VALIDATE -->|valid| STORE
    VALIDATE -->|invalid| ROLLBACK
    STORE --> COMMIT
    
    ROLLBACK -->|discard| STORE
    
    style VALIDATE fill:#fff9c4
    style COMMIT fill:#c8e6c9
    style ROLLBACK fill:#ffcdd2
```

---

*End of Diagrams*