# Mermaid Security Architecture Diagram

**Phase**: 3.7.20-A  
**Date**: 2026-08-04

---

## Security Architecture Flow

```mermaid
flowchart TD
    subgraph "External Actors"
        A[User/Actor]
        B[Remote Client]
    end
    
    subgraph "Entry Points"
        EP1[API Gateway]
        EP2[RPC Endpoint]
        EP3[Internal Services]
    end
    
    subgraph "Security Authority Layer"
        SM[SecurityManager]
        
        AM["AuthenticationManager"]
        TM["TrustManager"]
        AZM["AuthorizationManager"]
        CM["SecurityCapabilityManager"]
        SEM["SecretManager"]
        AUDIT["SecurityAuditManager"]
        PM["PolicyManager"]
    end
    
    A --> EP1
    B --> EP2
    EP3 --> SM
    
    SM --> AM
    SM --> TM
    SM --> AZM
    SM --> CM
    SM --> SEM
    SM --> AUDIT
    SM --> PM
    
    subgraph "Identity Resolution"
        ID[Identity Registry]
    end
    
    AM --> ID
    ID -->|authenticated| AM
    
    subgraph "Trust Evaluation"
        TE[Trust Assessment]
    end
    
    TM --> TE
    TE -->|trust_level| TM
    
    subgraph "Authorization Engine"
        AE[Policy Evaluation]
    end
    
    AZM --> AE
    AE -->|policy_match| AZM
    
    subgraph "Capability Resolution"
        CR[Capability Registry]
    end
    
    CM --> CR
    CR -->|has_cap| CM
    
    subgraph "Secret Store"
        SS[(Encrypted Secret Storage)]
    end
    
    SEM --> SS
    SS -->|encrypted| SEM
    
    subgraph "Audit Trail"
        AT[Audit Records]
    end
    
    AUDIT --> AT
    AT -->|chain_link| AUDIT
    
    subgraph "Policy Registry"
        PR[Policy Database]
    end
    
    PM --> PR
    PR -->|policy_match| PM
```

---

## Identity Flow

```mermaid
flowchart TD
    Actor -->|request| ID_RESOLUTION["Identity Resolution"]
    ID_RESOLUTION -->|check_credentials| AUTH["Authentication"]
    AUTH -->|success| TOKEN_ISSUE["Token Issued"]
    AUTH -->|fail| AUDIT_FAIL["Audit: Auth Failed"]
    
    TOKEN_ISSUE -->|include_token| CLIENT["Return to Client"]
    
    subgraph "Trust Evaluation (Separate)"
        TE[Trust Manager]
        TE -->|assess| TRUST_LEVEL
    end
    
    subgraph "Authorization (Independent)"
        AZE[Authorization Engine]
        AZE -->|check_policy| AUTHZ_DECISION
    end
    
    CLIENT -->|with_token| SECURE_REQUEST["Secure Request"]
    SECURE_REQUEST --> AUTH
    SECURE_REQUEST --> TE
    SECURE_REQUEST --> AZE
```

---

## Trust Boundary Model

```mermaid
flowchart TD
    subgraph "External Zone"
        U[User Input]
        R[Remote Requests]
    end
    
    subgraph "Trust Boundary 1: External to Runtime"
        EB1["Boundary: Authentication Required"]
    end
    
    U --> EB1
    R --> EB1
    
    subgraph "Runtime Zone"
        RT[Runtime Core]
    end
    
    EB1 -->|authenticated| RT
    
    subgraph "Trust Boundary 2: Runtime to Plugins"
        EB2["Boundary: Plugin Load Permission"]
    end
    
    RT --> EB2
    EB2 -->|plugin_load| PLUGINS[Plugin Host]
    
    subgraph "Trust Boundary 3: Plugins to Providers"
        EB3["Boundary: Provider Access Permission"]
    end
    
    PLUGINS --> EB3
    EB3 -->|provider_access| PROVIDERS[External Providers]
    
    subgraph "Trust Boundary 4: All to Secrets"
        EB4["Boundary: Secret Store (Encrypted)"]
    end
    
    RT --> EB4
    PLUGINS --> EB4
    PROVIDERS --> EB4
    
    EB4 -->|encrypted_access| SECRETS[(Secrets)]
```

---

## Authentication Flow

```mermaid
flowchart TD
    START[Authentication Request] --> CHECK_AUTH_METHOD["Check Auth Method"]
    
    CHECK_AUTH_METHOD -->|LOCAL| LOCAL_AUTH["Local Credential Check"]
    CHECK_AUTH_METHOD -->|TOKEN| TOKEN_AUTH["Token Validation"]
    CHECK_AUTH_METHOD -->|API_KEY| API_AUTH["API Key Verification"]
    CHECK_AUTH_METHOD -->|SERVICE| SERVICE_AUTH["Service Credentials"]
    CHECK_AUTH_METHOD -->|CERTIFICATE| CERT_AUTH["Certificate Chain"]
    
    LOCAL_AUTH --> HASH_COMPARE["Compare Salted Hash"]
    HASH_COMPARE -->|match| ISSUE_TOKEN["Issue Session Token"]
    HASH_COMPARE -->|fail| FAIL1["Fail: Invalid Credentials"]
    
    TOKEN_AUTH --> VERIFY_TOKEN["Verify Token Signature"]
    VERIFY_TOKEN -->|valid| ISSUER_CHECK["Check Audience"]
    ISSUER_CHECK -->|match| ISSUE_TOKEN
    ISSUER_CHECK -->|mismatch| FAIL2["Fail: Wrong Audience"]
    VERIFY_TOKEN -->|invalid| FAIL3["Fail: Token Expired/Revoked"]
    
    API_AUTH --> HASH_VERIFY["Verify Hash Match"]
    HASH_VERIFY -->|match| ISSUE_TOKEN
    HASH_VERIFY -->|fail| FAIL4["Fail: Invalid API Key"]
    
    SERVICE_AUTH --> SECRET_COMPARE["Timing-Safe Comparison"]
    SECRET_COMPARE -->|match| ISSUE_TOKEN
    SECRET_COMPARE -->|fail| FAIL5["Fail: Invalid Secret"]
    
    CERT_AUTH --> VALIDATE_CERT["Validate Certificate Chain"]
    VALIDATE_CERT -->|valid| ISSUE_TOKEN
    VALIDATE_CERT -->|invalid| FAIL6["Fail: Certificate Error"]
    
    ISSUE_TOKEN --> SUCCESS["Authentication Success"]
    FAIL1 --> END1[Return Failure]
    FAIL2 --> END2[Return Failure]
    FAIL3 --> END3[Return Failure]
    FAIL4 --> END4[Return Failure]
    FAIL5 --> END5[Return Failure]
    FAIL6 --> END6[Return Failure]
```

---

## Authorization Flow

```mermaid
flowchart TD
    START[Authorization Request] --> CHECK_AUTH["Principal Authenticated?"]
    
    CHECK_AUTH -->|No| DENY1["Deny: Not Authenticated"]
    CHECK_AUTH -->|Yes| EVAL_TRUST["Evaluate Trust Level"]
    
    EVAL_TRUST --> AUDIT_ONLY[Audit Only - No Decision Impact]
    AUDIT_ONLY --> APPLY_POLICIES["Apply Registered Policies"]
    
    APPLY_POLICIES --> CHECK_DENY_POLICY["Policy Match = DENY?"]
    CHECK_DENY_POLICY -->|Yes| DENY2["Deny: Policy Explicitly Denied"]
    CHECK_DENY_POLICY -->|No| CHECK_ALLOW_POLICY["Policy Match = ALLOW?"]
    
    CHECK_ALLOW_POLICY -->|No| DENY3["Deny: No Matching Allow Policy"]
    CHECK_ALLOW_POLICY -->|Yes| CHECK_OWNERSHIP["Ownership Required?"]
    
    CHECK_OWNERSHIP -->|Yes, Invalid| DENY4["Deny: Ownership Verification Failed"]
    CHECK_OWNERSHIP -->|No/Valid| GRANT_AUTH["Grant Authorization"]
    
    DENY1 --> AUDIT_DENY[Audit Record]
    DENY2 --> AUDIT_DENY
    DENY3 --> AUDIT_DENY
    DENY4 --> AUDIT_DENY
    GRANT_AUTH --> AUDIT_GRANT[Audit Record]
    
    AUDIT_DENY --> END_FAIL[Return Deny]
    AUDIT_GRANT --> END_SUCCESS[Return Allow]