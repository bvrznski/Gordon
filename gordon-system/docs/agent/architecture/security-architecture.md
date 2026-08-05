# Phase 3.7.16-I: Security Architecture Documentation

## Overview

This document describes the production implementation of security, trust boundaries,
authorization, and runtime protection for the Gordon autonomous cognitive agent.

---

## Canonical Security Pipeline

```mermaid
flowchart TD
    A[Actor] --> B["Identity Resolution"]
    B --> C["Authentication"]
    C --> D["Trust Evaluation"]
    D --> E["Authorization"]
    E --> F["Policy Evaluation"]
    F --> G["Capability Resolution"]
    G --> H["Ownership Verification"]
    H --> I["Boundary Enforcement"]
    I --> J["Secure Execution"]
    J --> K["Audit"]
    K --> L["Post-Action Verification"]
```

### Pipeline Steps

1. **Identity Resolution**: Determine who is making the request
2. **Authentication**: Verify identity through credentials/tokens
3. **Trust Evaluation**: Assess trust level (independent from authorization)
4. **Authorization**: Check if principal can perform action on resource
5. **Policy Evaluation**: Apply registered policies to decision
6. **Capability Resolution**: Verify runtime can technically perform action
7. **Ownership Verification**: Confirm principal owns the resource (if applicable)
8. **Boundary Enforcement**: Ensure crossing trust boundaries is authorized
9. **Secure Execution**: Perform action with proper isolation
10. **Audit**: Record immutable event for compliance/forensics
11. **Post-Action Verification**: Verify outcome and log results

---

## Core Security Authorities

```mermaid
graph TB
    subgraph "SecurityManager (Orchestrator)"
        SM[SecurityManager]
    end
    
    subgraph "Core Authorities"
        AM["AuthenticationManager"]
        TM["TrustManager"]
        AZM["AuthorizationManager"]
        CM["CapabilityManager"]
        SEM["SecretManager"]
        AUDITM["SecurityAuditManager"]
    end
    
    SM --> AM
    SM --> TM
    SM --> AZM
    SM --> CM
    SM --> SEM
    SM --> AUDITM
```

### Authority Responsibilities

| Authority | Responsibility |
|-----------|----------------|
| SecurityManager | Overall orchestration and policy lifecycle |
| AuthenticationManager | Identity verification, credential/token management |
| TrustManager | Trust relationships, scoring, revocation |
| AuthorizationManager | Permission evaluation, authorization decisions |
| CapabilityManager | Runtime capabilities, grants, leases |
| SecretManager | Secret storage, rotation, secure deletion |
| SecurityAuditManager | Immutable audit records, event logging |

**Invariant**: Exactly one canonical instance per runtime.

---

## Identity Model

```mermaid
flowchart LR
    Identity --> Principal
    Identity --> SessionIdentity
    
    Principal --> Actor
    SessionIdentity --> Actor
    
    subgraph "Identity Types"
        ID1[Runtime]
        ID2[Service]
        ID3[Plugin]
        ID4[Tool]
        ID5[Session]
        ID6[User]
        ID7[Actor]
    end
    
    Identity -.->|is-a| ID1
    Principal -.->|specializes| ID2
```

### Identity Types

- **Runtime**: Runtime instance identity
- **Service**: Service within runtime
- **Plugin**: Plugin identity with manifest hash
- **Tool**: Tool identity with vendor/version
- **Session**: Session-specific authentication context
- **User**: Human user actor
- **Actor**: Principal acting in context

**Key Principle**: Identity proves WHO, NOT trust or authorization.

---

## Trust Model (Independent from Authorization)

```mermaid
flowchart TD
    A[Identity Proven] --> B{Authentication?}
    B -->|Success| C[Trust Assessment]
    C --> D[Trust Level Assigned]
    
    E[Authorization Check] -.->|INDEPENDENT| C
    
    D --> F[Decision: Allow/Deny/Conditional]
```

### Trust Levels

- **UNTRUSTED** (0.0) - Explicitly untrusted
- **UNKNOWN** (0.3) - No assessment yet
- **VERIFIED** (0.5) - Identity verified, no extra trust
- **TRUSTED** (0.75) - Trusted for some operations
- **HIGHLY_TRUSTED** (1.0) - Fully trusted operator

### Trust Evidence Types

- IDENTITY_VERIFIED
- CREDENTIAL_VALID
- TOKEN_VALID
- CERTIFICATE_VALID
- SOURCE_AUTHENTICATED
- BEHAVIOR_HISTORY_GOOD
- PRIVILEGE_LEVEL_HIGH

---

## Authorization Model

```mermaid
flowchart TD
    A[Authorization Request] --> B{Principal Authenticated?}
    B -->|No| FAIL1[Deny: Not Authenticated]
    B -->|Yes| C[Check Trust Level]
    
    C --> D[Apply Policies]
    D --> E{Policy Match?}
    E -->|DENY| FAIL2[Deny: Policy Denied]
    E -->|ALLOW| F{Ownership Required?}
    F -->|Yes, Invalid| FAIL3[Deny: Ownership Failed]
    F -->|No/Valid| G[Authorize]
    
    FAIL1 -.->|"Record in Audit"| AUDIT[Audit Record]
    FAIL2 -.->|"Record in Audit"| AUDIT
    FAIL3 -.->|"Record in Audit"| AUDIT
    G -->|"Record in Audit"| AUDIT
```

### Authorization Steps

1. Verify principal is authenticated
2. Assess trust level (audit only, doesn't affect decision)
3. Apply registered policies
4. Check ownership if required
5. Record result in audit trail

**Invariant**: Authorization does NOT imply capability.

---

## Capability Model (Separate from Authorization)

```mermaid
flowchart TD
    A[Principal Request] --> B{Has Capability Grant?}
    B -->|No| DENY_CAP[Deny: No Capability]
    B -->|Yes| C{Lease Expired?}
    
    C -->|Yes| DENY_LEASE[Deny: Lease Expired]
    C -->|No| D{Revoked?}
    
    D -->|Yes| DENY_REVOKED[Deny: Revoked]
    D -->|No| ALLOW_CAP[Allow: Capability Valid]
```

### Capability Lifecycle

1. Register capability with runtime
2. Grant to principal (optional expiration)
3. Issue lease for temporary access
4. Revoke if needed (immediately invalidates)

**Invariant**: Having a capability does NOT mean you can use it - that requires authorization.

---

## Secret Management

```mermaid
flowchart LR
    subgraph "Secret Manager"
        STORE[Store Secret]
        RETRIEVE[Retrieve Secret]
        ROTATE[Rotate Secret]
        DELETE[Delete Secret]
    end
    
    STORE --> ENCRYPT["Encrypted Storage Adapter"]
    RETRIEVE --> DECRYPT["Decryption Layer"]
    
    ENCRYPT --> DB[(Encrypted Store)]
    DECRYPT --> DB
    
    AUDIT["Audit Log"] -.->|All Access| STORE
    AUDIT -.->|All Access| RETRIEVE
```

### Secret Operations

- **Store**: Encrypt with Fernet before saving
- **Retrieve**: Decrypt on retrieval (audit logged)
- **Rotate**: Create new version, preserve history
- **Delete**: Secure deletion from storage

**Invariant**: Raw secrets NEVER exposed in diagnostics.

---

## Audit Trail

```mermaid
flowchart LR
    R1[Audit Record 1] --> R2[Audit Record 2]
    R2 --> R3[Audit Record 3]
    R3 --> R4[Audit Record 4]
    
    subgraph "Integrity Chain"
        R1 -.->|chain link| R2
        R2 -.->|chain link| R3
        R3 -.->|chain link| R4
    end
    
    VERIFY["Verify Integrity"] -.->|Check chain| R1
```

### Audit Record Fields

- `record_id`: Unique identifier
- `event_type`: Authentication/Authorization/Capability/etc.
- `timestamp`: Monotonic timestamp
- `principal_id`: Subject of event
- `action`: Permission attempted
- `resource`: Target resource
- `outcome`: Success/failure/granted/denied
- `previous_record_id`: Chain link to previous record

**Invariant**: Records are immutable once recorded.

---

## Sandbox Policies

```mermaid
flowchart TD
    subgraph "Sandbox Modes"
        STRICT[Sandbox Mode: STRICT]
        PERMISSIVE[Sandbox Mode: PERMISSIVE]
        MONITOR[Sandbox Mode: MONITOR]
    end
    
    STRICT -->|Only allow listed| ALLOW_FS[Filesystem Allowed Paths]
    STRICT -->|Block not listed| BLOCK_NET[Network Blocked by Default]
    
    PERMISSIVE -->|Allow all except| DENY_LIST[Denied List]
    
    MONITOR -->|Log everything| LOG_ALL[Logger - No Blocking]
```

### Sandbox Policy Components

- **Subjects**: Which principals this applies to
- **Filesystem**: Allowed/denied paths
- **Network**: Allowed/denied endpoints
- **Process**: Allowed/denied commands
- **Mode**: STRICT, PERMISSIVE, or MONITOR

---

## Privilege Domains

```mermaid
graph TD
    subgraph "Privilege Domains"
        OPERATOR[Operator Domain]
        RUNTIME[Runtime Domain]
        KERNEL[Kernel Domain]
        PLUGIN[Plugin Domain]
        PROVIDER[Provider Domain]
        TOOL[Tool Domain]
        MODEL[Model Domain]
        SERVICE[Service Domain]
    end
    
    OPERATOR -->|Highest Level| 100
    SERVICE -->|Lowest Level| 0
```

### Privilege Levels

- **Operator** (80-100): Full system control
- **Runtime** (60-79): Runtime management
- **Kernel** (40-59): Kernel-level operations
- **Plugin** (20-39): Plugin execution
- **Provider** (10-19): Provider access
- **Tool** (0-9): Tool invocation

---

## Trust Boundaries

```mermaid
flowchart TD
    subgraph "Internal Runtime"
        A[Actor] --> B["Runtime Boundary"]
    end
    
    B --> C["Plugin Boundary"]
    C --> D["Provider Boundary"]
    D --> E["OS Interface"]
    E --> F["Filesystem"]
    F --> G["Network"]
    
    subgraph "External"
        H[User Input]
        I[Model Output]
    end
```

### Boundary Crossings Require Authorization

| From | To | Action Required |
|------|-----|-----------------|
| Runtime | Plugin | PLUGIN_LOAD |
| Runtime | Provider | NET_OUTBOUND |
| Plugin | Filesystem | FS_READ/FS_WRITE |
| Network | Runtime | NET_INBOUND |

---

## Permission Categories

```mermaid
flowchart TD
    subgraph "Runtime Administration"
        RS[Runtime Start]
        RSTP[Runtime Stop]
        RRST[Runtime Restart]
    end
    
    subgraph "Configuration"
        CRD[Config Read]
        CWR[Config Write]
        CREL[Config Reload]
    end
    
    subgraph "Filesystem"
        FSRD[FS Read]
        FSWR[FS Write]
        FSDEL[FS Delete]
        FSEX[FS Execute]
        FSMN[FS Mount]
        FSTP[FS Temporary]
    end
    
    subgraph "Networking"
        NETO[Net Outbound]
        NETI[Net Inbound]
        NETPRV[Net Provider]
        NETL[Net Localhost]
        NETR[Net Remote]
    end
    
    subgraph "Process Creation"
        PROCC[Proc Create]
        PROCX[Proc Execute]
        PROCK[Proc Kill]
    end
```

---

## Integration with Gordon Runtime

```mermaid
flowchart TD
    subgraph "Gordon Runtime"
        CORE_RUNTIME[Gordon Core Runtime]
        
        subgraph "Security Module"
            SM[SecurityManager]
            AM["AuthenticationManager"]
            TM["TrustManager"]
            AZM["AuthorizationManager"]
            CM["CapabilityManager"]
            SEM["SecretManager"]
            AUDIT["SecurityAuditManager"]
        end
        
        CORE_RUNTIME -->|uses| SM
        SM --> AM
        SM --> TM
        SM --> AZM
        SM --> CM
        SM --> SEM
        SM --> AUDIT
    end
    
    subgraph "External Systems"
        KMS[KMS for encryption keys]
        VAULT[Vault for secrets]
    end
    
    SEM -.->|uses| KMS
    SEM -.->|optionally| VAULT
```

---

## Security Invariants

1. Exactly one canonical instance per runtime
2. All decisions are immutable once made
3. No implicit trust exists
4. Authentication is independent of authorization
5. Trust is independent of authorization
6. Authorization does NOT imply capability
7. Capabilities and permissions are immutable artifacts
8. Secrets are never exposed in diagnostics
9. Audit records are immutable

---

## Testing Strategy

```mermaid
flowchart TD
    TEST_IDENTITY[Identity Model Tests]
    TEST_AUTH[Test Authentication Primitives]
    TEST_TRUST[Test Trust Manager]
    TEST_AUTHZ[Test Authorization Manager]
    TEST_CAP[Test Capability Manager]
    TEST_SECRET[Test Secret Manager]
    TEST_AUDIT[Test Audit Manager]
    TEST_INTEGRATION[Test Full Pipeline]
    
    TEST_IDENTITY --> VERIFY
    TEST_AUTH --> VERIFY
    TEST_TRUST --> VERIFY
    TEST_AUTHZ --> VERIFY
    TEST_CAP --> VERIFY
    TEST_SECRET --> VERIFY
    TEST_AUDIT --> VERIFY
    TEST_INTEGRATION --> VERIFY
    
    subgraph "Verification"
        VERIFY["All Tests Pass?"]
    end
```

---

## Migration Path

### Phase 3.7.16-I Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Identity Models | ✅ Complete | Immutable, hashable dataclasses |
| Authentication Manager | ✅ Complete | Provider-based, credential hashing |
| Trust Manager | ✅ Complete | Independent from authorization |
| Authorization Manager | ✅ Complete | Policy-based with grants |
| Capability Manager | ✅ Complete | Separate from authorization |
| Secret Manager | ✅ Complete | Encrypted storage, audit logging |
| Audit Manager | ✅ Complete | Chain-linked immutable records |
| Sandbox Policies | ✅ Complete | Strict/Permissive/Monitor modes |
| Privilege Domains | ✅ Complete | Explicit levels per domain |
| Trust Boundaries | ✅ Complete | Boundary crossing tracking |

---

## API Examples

### Authentication Flow

```python
from gordon_system.src.agent.components.core.security import (
    SecurityManager, AuthMethod, AuthenticationRequest
)

# Create security manager
security = SecurityManager(runtime_id="runtime-1")

# Authenticate request
request = AuthenticationRequest(
    principal_id="user-123",
    credential_hash="hashed-value",
    method=AuthMethod.LOCAL
)

success, principal_id, identity = await security.authenticate(request)
```

### Authorization Flow

```python
from gordon_system.src.agent.components.core.security import Permission

# Check authorization
authorized, reason = await security.authorize(
    principal_id="user-123",
    action=Permission.FS_READ,
    resource="/home/user/file.txt"
)

if authorized:
    # Perform action with capability verification
    has_cap = await security.check_capability("user-123", "fs:read")
```

### Secret Management

```python
# Store encrypted secret
descriptor = await security.secret_manager.store_secret(
    name="api-key",
    value="my-secret-api-key"
)

# Retrieve (automatically decrypted)
value = await security.secret_manager.retrieve_secret(descriptor.secret_id)

# Audit snapshot (never includes secrets!)
snapshot = security.secret_manager.get_secret_snapshot()
```

---

## Deployment Considerations

1. **KMS Integration**: Production should integrate with KMS for encryption key management
2. **Secrets Vault**: Consider integrating with HashiCorp Vault or AWS Secrets Manager
3. **Audit Sink**: Configure external audit logging (e.g., SIEM integration)
4. **Monitoring**: Set up alerts for privilege escalation attempts, sandbox violations

---

## Security Audit Events

| Event Type | Description |
|------------|-------------|
| `auth:succeeded` | Successful authentication |
| `auth:failed` | Failed authentication attempt |
| `authz:granted` | Authorization granted |
| `authz:denied` | Authorization denied |
| `capability:granted` | Capability granted to principal |
| `capability:revoked` | Capability revoked |
| `trust:changed` | Trust level changed |
| `trust:revoked` | Trust revoked |
| `secret:accessed` | Secret accessed (audited) |
| `plugin:loaded` | Plugin loaded successfully |
| `plugin:rejected` | Plugin rejected |
| `sandbox:violation` | Sandbox policy violation |
| `policy:violation` | Policy violation detected |
| `privilege:escalation-attempt` | Privilege escalation attempt |

---

**Document Version**: 1.0.0  
**Implemented Phase**: 3.7.16-I  
**Last Updated**: 2025-08-03