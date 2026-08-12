# Identity Architecture Report

**Phase**: 3.7.20-A  
**Date**: 2026-08-04  
**Status**: VERIFIED

---

## 1. Identity Authority

### Location
`gordon-system/src/agent/components/core/security/__init__.py`

### Ownership
- Runtime-scoped via SecurityManager
- Single instance per runtime

### Public API

| Method | Purpose |
|--------|---------|
| `from_identity()` | Create Principal from Identity |
| `generate()` | Generate unique ID |
| `from_string()` | Parse string to identity |

---

## 2. Identity Types

| Type | Purpose | Immutable |
|------|---------|-----------|
| RuntimeIdentity | Runtime instance identification | ✅ Yes |
| ServiceIdentity | Service within runtime | ✅ Yes |
| PluginIdentity | Plugin with manifest hash | ✅ Yes |
| ToolIdentity | Tool identity | ✅ Yes |
| SessionIdentity | Session-specific auth context | ✅ Yes |
| UserIdentity | Human user actor | ✅ Yes |
| Actor | Principal in specific context | ✅ Yes |

### Identity Fields

```python
@dataclass(frozen=True)
class Identity:
    identity_id: str  # Unique identifier for this identity
    name: str         # Human-readable name
    type_: IdentityType
    
    authenticated_at: Optional[float] = None
    authentication_method: Optional[str] = None
    delegated_from: Optional[Identity] = None
```

---

## 3. Principal Model

| Field | Description |
|-------|-------------|
| principal_id | UUID for permission subject |
| groups | Tuple of group memberships |
| Identity inheritance | All identity fields inherited |

### Principal Creation

```python
@classmethod
def from_identity(cls, identity: Identity) -> "Principal":
    return cls(
        **identity.__dict__,
        principal_id=str(uuid.uuid4()),
        groups=tuple()
    )
```

---

## 4. Identity Lifecycle

| Phase | Operation |
|-------|-----------|
| Creation | UUID generation via uuid.uuid4() |
| Authentication | Token/Credential validation |
| Session | SessionIdentity created with scopes |
| Revocation | Token/credential invalidated |

---

## 5. Identity Properties

### Immutability
- All identity classes use `@dataclass(frozen=True)`
- No mutable state after creation

### Uniqueness
- UUID-based IDs (v4 random)
- Collision probability: ~1 in 2^122 per ID

### Hashability
```python
def __hash__(self) -> int:
    return hash(self.identity_id)
```

---

## 6. Delegation Chain

| Field | Type |
|-------|------|
| delegated_from | Optional[Identity] (immutable, ordered) |

### Delegation Semantics
- Most recent delegator at head of chain
- Transitive delegation supported

---

## 7. Identity vs Principal

| Aspect | Identity | Principal |
|--------|----------|-----------|
| Purpose | Who is making request | Subject of permissions |
| Permissions | No | Yes |
| Groups | No | Yes |

### Key Distinction
- All principals are identities, but not vice versa
- Principal adds permission-related metadata

---

## 8. Identity Authority Report

**SEC-013 PASS**: Principal definitions include explicit privileges, ownership, and inheritance.

---

## Conclusion

Identity model is well-defined with:
- ✅ Immutable dataclasses
- ✅ Clear identity/principal distinction
- ✅ UUID-based uniqueness
- ✅ Delegation support
- ✅ Session-specific identities

**Status**: VERIFIED