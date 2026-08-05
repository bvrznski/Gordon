# Capability Model Report

**Phase**: 3.7.20-A  
**Date**: 2026-08-04  
**Status**: VERIFIED

---

## 1. Capability Authority

### Location
`gordon-system/src/agent/components/core/security/managers.py` - `SecurityCapabilityManager` (lines 890-1062)

### Ownership
- Single instance per runtime via SecurityManager
- Thread-safe with Lock synchronization

### Public API

| Method | Purpose |
|--------|---------|
| `register_capability()` | Register a runtime capability |
| `grant_capability()` | Grant capability to principal |
| `revoke_capability()` | Revoke a capability grant |
| `issue_lease()` | Issue time-limited lease |
| `can_use_capability()` | Check if principal can use capability |

---

## 2. Capability Types

### Runtime Capabilities

| Domain | Capability Examples |
|--------|---------------------|
| Filesystem | FS_READ, FS_WRITE, FS_DELETE |
| Network | NET_OUTBOUND, NET_INBOUND, NET_PROVIDER_ACCESS |
| Process | PROC_CREATE, PROC_EXEC, PROC_KILL |

---

## 3. Capability Lifecycle

### Grant Flow

```
1. Register capability with runtime
2. Grant to principal (with optional expiration)
3. Principal attempts to use capability
4. System verifies grant exists and is not expired/revoked
5. Authorization check performed separately
6. Action executed if all checks pass
```

### Lease Flow

```
1. Issue lease for time-limited access
2. Track current renewal count
3. Renewals allowed up to configured limit
4. Expire when duration ends or all renewals used
```

---

## 4. Capability Grant Fields

| Field | Description |
|-------|-------------|
| grant_id | Unique identifier |
| capability_id | Which capability is granted |
| principal_id | Who receives the grant |
| granted_at | Monotonic timestamp |
| expires_at | Optional expiration time |
| conditions | Constraint conditions (tuple of strings) |

---

## 5. Security Features

| Feature | Implementation |
|---------|----------------|
| Immutable grants | Once granted, cannot be modified |
| Time-limited leases | Automatic expiry |
| Revocation support | Immediate invalidation |
| Thread safety | Lock synchronization |

---

## 6. Capability vs Authorization

### Key Distinction
- **Capability**: Technical ability to perform an action
- **Authorization**: Policy permission to use that capability

### Example Scenario
```
User has:
1. Capability: Can read files (technical ability)
2. Authorization: Not permitted to read /etc/shadow (policy)

Result: Cannot read /etc/shadow despite having capability
```

---

## 7. Capability Check Logic

```python
def can_use_capability(
    self,
    principal_id: str,
    capability_id: str
) -> bool:
    # Check grants for this principal
    # Check expiration (if any)
    # Check revocations
    return True/False
```

---

## Conclusion

**SEC-005 PASS**: Least privilege is preserved through explicit capability grants with time limits and revocation support.