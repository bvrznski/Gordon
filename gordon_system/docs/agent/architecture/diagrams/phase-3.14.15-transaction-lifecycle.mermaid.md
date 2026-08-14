# Phase 3.14.15: Transaction Lifecycle Diagram

```mermaid
stateDiagram-v2
    [*] --> Created
    
    state Created {
        [*] --> Validated : validation_passed()
    }
    
    state Validated {
        [*] --> Admitted : admission_granted()
    }
    
    state Admitted {
        [*] --> Executing : execution_started()
    }
    
    state Executing {
        [*] --> Verifying : execution_completed()
    }
    
    state Verifying {
        [*] --> Committed : consistency_verified()
        Failed --> [*]
        RolledBack --> [*]
    }
    
    state Committed {
        [*] --> Certified : commitment_durable()
    }
    
    state Certified {
        [*] --> Closed
    }
    
    Created: Transaction defined\nNot yet validated
    Validated: Validation passed\nReady for admission
    Admitted: Admission control granted\nMay execute
    Executing: Active execution in progress
    Verifying: Post-execution verification required
    Committed: Consistency verified\nCommitted to state
    Certified: Durable\nCertification complete
    Closed: Transaction lifecycle complete
    
    note right of Created
        Alternative terminal states:
        - FAILED: Irrecoverable failure
        - ABORTED: Explicitly aborted
        - CANCELLED: External cancellation
        - ROLLED_BACK: Rollback completed
    end note
    
    note left of Committed
        Commitment requires:
        1. Successful validation
        2. Successful execution
        3. Successful consistency verification
        4. Authority verification
        
        Partial commitment is prohibited.
    end note
```

---

## Transaction Lifecycle States

| State | Description |
|-------|-------------|
| `CREATED` | Transaction defined, not yet validated |
| `VALIDATED` | Validation passed, ready for admission |
| `ADMITTED` | Admission control granted, may execute |
| `EXECUTING` | Active execution in progress |
| `VERIFYING` | Post-execution consistency verification |
| `COMMITTED` | Consistency verified, committed to state |
| `CERTIFIED` | Durable, certification complete |
| `CLOSED` | Transaction lifecycle complete |

## Terminal States

| State | Description |
|-------|-------------|
| `FAILED` | Irrecoverable failure |
| `ABORTED` | Explicitly aborted by authority |
| `CANCELLED` | External cancellation request |
| `ROLLED_BACK` | Rollback completed successfully |

---

## Key Principles

1. **Transactions coordinate multiple architectural operations** into a single consistent unit of work
2. **Transactions preserve architectural integrity**
3. **Transactions never redefine ownership**
4. **Transactions never redefine authority**
5. **Every Transaction possesses exactly one owner (System)**