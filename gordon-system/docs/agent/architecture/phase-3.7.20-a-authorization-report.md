# Authorization Report

**Phase**: 3.7.20-A  
**Date**: 2026-08-04  
**Status**: VERIFIED

---

## 1. Authorization Authority

### Location
`gordon-system/src/agent/components/core/security/managers.py` - `AuthorizationManager` (lines 658-872)

### Ownership
- Single instance per runtime via SecurityManager
- Thread-safe with per-principal Lock synchronization

### Public API

| Method | Purpose |
|--------|---------|
| `register_policy()` | Register authorization policy |
| `grant_permission()` | Grant permission to principal |
| `revoke_permission()` | Revoke permission from principal |
| `check_authorization()` | Check if action is authorized |

---

## 2. Permission Model

### Permission Categories

#### Runtime Administration
- RUNTIME_START, RUNTIME_STOP, RUNTIME_RESTART

#### Configuration
- CONFIG_READ, CONFIG_WRITE, CONFIG_RELOAD

#### Filesystem
- FS_READ, FS_WRITE, FS_DELETE, FS_EXECUTE, FS_MOUNT, FS_TEMPORARY

#### Networking
- NET_OUTBOUND, NET_INBOUND, NET_PROVIDER_ACCESS, NET_LOCALHOST, NET_REMOTE

#### Process Creation
- PROC_CREATE, PROC_EXEC, PROC_KILL

#### Plugin Execution
- PLUGIN_LOAD, PLUGIN_UNLOAD, PLUGIN_INVOKE

#### Tool Invocation
- TOOL_REGISTER, TOOL_INVOKE

---

## 3. Policy System

### Policy Types

| Type | Description |
|------|-------------|
| ALLOW | Explicitly permit an action |
| DENY | Explicitly deny an action |
| CONDITIONAL | Permit under specific conditions |
| DELEGATED | Delegation-based policies |
| INHERITED | Inherited from parent domain |
| TEMPORARY | Time-limited policies |

### Policy Matching

```python
def matches(
    self,
    principal_id: str,
    action: Permission,
    resource: str,
    domain: Optional[str] = None
) -> Tuple[PolicyType, Optional[str]]:
    # Check each rule's match criteria
    # First matching rule determines effect
    # Default is DENY when no rules match
```

---

## 4. Authorization Pipeline

### Steps

1. **Verify authentication**: Principal must be authenticated
2. **Evaluate trust**: Assess trust level (audit only, doesn't affect decision)
3. **Apply policies**: Check all registered policies for matches
4. **Check ownership**: Verify resource ownership if required
5. **Record audit**: Log decision with evidence

### Decision Logic

```python
if deny_found:
    return AuthorizationResult(allowed=False, reason="Explicit deny policy matched")
elif not allowed:
    return AuthorizationResult(allowed=False, reason="No matching allow policy")
else:
    # Check ownership if required
    # Grant authorization if all checks pass
```

---

## 5. Trust Independence

### Key Principles
- **Authorization ≠ Trust**: A trusted principal may be denied authorization
- **Explicit Policy**: All permissions must come from explicit policies
- **Deny by Default**: Missing policy = deny (fail-closed)

---

## 6. Ownership Verification

```python
def _verify_ownership(
    self,
    principal_id: str,
    resource: str,
    expected_owner: str
) -> bool:
    return principal_id == expected_owner
```

---

## 7. Security Features

| Feature | Implementation |
|---------|----------------|
| Permission storage | Immutable tuples per principal |
| Policy versioning | Versioned, immutable policies |
| Thread safety | Per-principal Lock synchronization |
| Audit logging | All decisions recorded in audit trail |

---

## Conclusion

**SEC-004 PASS**: Authorization responsibilities are explicit with deny-by-default policy evaluation and clear separation from trust.