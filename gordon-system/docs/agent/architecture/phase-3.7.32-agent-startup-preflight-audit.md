# Phase 3.7.32-A: Agent Startup Preflight and Compilation Checks

## Architecture Acceptance Audit Report

---

## Audit Identity

| Property | Value |
|----------|-------|
| **Phase** | 3.7.32-A |
| **Audit Type** | Architecture Acceptance |
| **Target** | `/src/agent/entrypoint/check.py` |
| **Date** | 8/5/2026, 8:51:00 AM UTC+2:00 |
| **Auditor** | Automated Audit System |
| **Repository Root** | /home/bvrznski/Gordon/gordon-system |
| **Branch** | main |
| **Starting Commit** | 07ddd26eed70f5143bf6d2067196ea5c35c1d557 |
| **Python Version** | 3.10.12 |
| **Environment** | Linux 6.8, VS Code |
| **Deployment Mode** | Standalone (Source) |

---

## Executive Summary

| Metric | Status |
|--------|--------|
| **Certification** | REMEDIATION_REQUIRED |
| **Confidence** | Medium-High |
| **Critical Findings** | 3 |
| **High Findings** | 5 |
| **Release Blockers** | 2 |
| **Certification Blockers** | 1 |

### Summary

The preflight architecture implements a **canonical authority at `agent.entrypoint.check`** with proper immutable contracts, typed outcomes, and policy models. However, several structural issues prevent full certification:

**Strengths:**
- Single canonical preflight checker (`AgentPreflightChecker`)
- Immutable request/result dataclasses
- Typed outcome enumeration (PASS/PASS_WITH_WARNINGS/BLOCKED/FAILED/CANCELLED/TIMED_OUT)
- Policy-based check execution with deterministic ordering

**Deficiencies:**
- Duplicate bootstrap preflight system exists in `components/core/bootstrap/__init__.py`
- Preflight result staleness validation not fully implemented
- Missing integration with `entrypoint/init.py` for result validation
- No explicit Agent-Assistant separation enforcement at entrypoint level

---

## Architecture Inventory

### Preflight Authorities
| Path | Status | Type |
|------|--------|------|
| `src/agent/entrypoint/check/checker.py:AgentPreflightChecker` | ✅ Active | CANONICAL_PREFLIGHT_AUTHORITY |
| `src/agent/components/core/bootstrap/__init__.py:BootstrapRequest` | ⚠️ Duplicate | DUPLICATE_PREFLIGHT_AUTHORITY |

### Policies
| Path | Status | Type |
|------|--------|------|
| `src/agent/entrypoint/check/policy.py:AgentPreflightPolicy` | ✅ Active | CANONICAL_PREFLIGHT_POLICY |
| `src/agent/entrypoint/check/policy.py:AgentCompilationPolicy` | ✅ Active | CANONICAL_COMPILATION_POLICY |

### Compiler Implementations
| Path | Status | Type |
|------|--------|------|
| `src/agent/entrypoint/check/checker.py:_execute_compilation` | ✅ Active | COMPILER |

### Startup Integration
| Path | Status | Notes |
|------|--------|-------|
| `src/agent/entrypoint/main.py:_invoke_preflight` | ✅ Active | Preflight invoked before initialization |
| `src/agent/entrypoint/init/__init__.py` | ⚠️ Partial | No stale result validation |

---

## Canonical Authority Analysis

### Checker: AgentPreflightChecker
- **Path**: `src/agent/entrypoint/check/checker.py`
- **Status**: ✅ Active
- **Notes**: Single authoritative preflight checker with check() method returning immutable results

### Request Model
- **Path**: `src/agent/entrypoint/check/request.py:AgentPreflightRequest`
- **Status**: ✅ Immutable dataclass
- **Fields**: request_id, launch_identity, process_identity, approved_source_roots, compilation_policy

### Context Model
- **Path**: `src/agent/entrypoint/check/context.py:AgentPreflightContext`
- **Status**: ⚠️ Operation-scoped but not used in execution path

### Staleness Authority
- **Status**: ⚠️ Missing - Result validity check exists but uses only duration, not evidence binding

---

## Compilation Analysis

| Aspect | Status | Notes |
|--------|--------|-------|
| Policy Modes | ✅ 7 modes defined | NONE, TARGETED, CHANGED, COMPONENT_DESCRIPTORS, FULL_AGENT, FULL_GORDON, PACKAGED_ARTIFACT |
| Target Selection | ⚠️ Bounded to 100 files | No manifest-based selection |
| Compilation Safety | ✅ Syntax only | Uses `compile()` with `dont_inherit=True` |
| Output Policy | ⚠️ Default system_pycache | No explicit cleanup policy |

---

## Preflight Result Model Analysis

### AgentPreflightResult
- **Immutability**: ✅ Frozen dataclass
- **Fields**: outcome, execution_id, timing, fingerprints, check_results, blockers, warnings, errors
- **Staleness Validation**: ⚠️ Duration-based only (60s), no evidence binding to launch ID

---

## Static Startup Checks

| Check Type | Status | Notes |
|------------|--------|-------|
| Package Layout | ✅ Implemented | Canonical path validation |
| Metadata | ✅ Implemented | __init__.py, __meta__.py |
| Startup Symbols | ⚠️ Partial | Static inspection only |
| Architecture Boundaries | ⚠️ Missing | No explicit boundary checks |

---

## Environment and Dependency Checks

| Check Type | Status |
|------------|--------|
| Configuration Access | ✅ Implemented |
| Environment Keys | ✅ Implemented |
| Filesystem | ✅ Implemented |
| Executables | ⚠️ Partial - Placeholder only |
| Python Compatibility | ✅ Version check implemented |

---

## Preflight Integration Analysis

### main.py Integration
```python
# Current flow:
preflight_result = _invoke_preflight(launch_request)
if not preflight_result.get("outcome", {}).get("is_success", False):
    # Exit with failure code
    return _map_preflight_failure(preflight_result)

# Proceed to initialization...
```

**Status**: ✅ Preflight executed before initialization

### init.py Integration
- **Status**: ⚠️ Missing - No stale result validation or identity binding check

---

## Agent-Assistant Separation

| Check | Status |
|-------|--------|
| Agent-only mode | ⚠️ Policy defined but not enforced at runtime |
| FULL_GORDON policy | ✅ Defined but requires explicit selection |
| Assistant root exclusion | ❌ Not implemented |

---

## Import-Time Purity Analysis

| Module | Behavior |
|--------|----------|
| `agent.entrypoint.check` | ✅ No active checks at import |
| `agent.entrypoint.check.types` | ✅ Enum definitions only |
| `agent.entrypoint.check.request` | ✅ Dataclass definitions only |
| `agent.entrypoint.check.result` | ✅ Dataclass definitions only |

---

## Mutable Global State Audit

| Location | Status | Type |
|----------|--------|------|
| Module-level globals in check.py | ❌ Issue | DEFAULT_CHECK_REGISTRY, mutable state |
| Checker instance variables | ⚠️ Operation-scoped | Acceptable for single-use instances |

**Note**: `DEFAULT_CHECK_REGISTRY` is a module-level mutable registry that violates the "no global accumulator" principle.

---

## Legacy Paths

| Path | Status | Notes |
|------|--------|-------|
| `src/agent/components/core/bootstrap/__init__.py` | ⚠️ Duplicate | Has its own preflight system |

---

## Test Inventory

| Area | Status |
|------|--------|
| Preflight authority tests | ⚠️ Pending |
| Request immutability tests | ⚠️ Pending |
| Result immutability tests | ⚠️ Pending |
| Compilation safety tests | ⚠️ Pending |
| Staleness validation tests | ⚠️ Missing |

---

## Invariant Matrix

| ID | Status | Evidence |
|----|--------|----------|
| CHECK-001 (One preflight authority) | ❌ FAIL | Duplicate bootstrap preflight exists |
| CHECK-002 (agent.entrypoint.check canonical) | ✅ PASS | Primary path implemented |
| CHECK-003 (Preflight before init) | ✅ PASS | main.py enforces order |
| CHECK-004 (One request per launch) | ✅ PASS | Per-request instantiation |
| CHECK-005 (Immutable request) | ✅ PASS | Frozen dataclass |
| CHECK-006 (Immutable result) | ⚠️ PARTIAL | Frozen but stale validation weak |
| CHECK-049 (No mutable global checker) | ❌ FAIL | DEFAULT_CHECK_REGISTRY is mutable |
| CHECK-052 (No import-time preflight) | ✅ PASS | Module imports only define types |

---

## Acceptance Gate Matrix

| Gate | Status | Blockers |
|------|--------|----------|
| Gate 1: Canonical Preflight Authority | ❌ FAIL | Duplicate bootstrap system |
| Gate 2: Request and Result | ✅ PASS | Immutable contracts |
| Gate 3: Policy | ✅ PASS | Policy models present |
| Gate 4: Compilation | ⚠️ PARTIAL | Bounded but no manifest-based selection |
| Gate 5-10: Various checks | ⚠️ PARTIAL | Some implementations incomplete |
| Gate 12: Startup Integration | ❌ FAIL | init.py has no validation |
| Gate 13: Agent-Assistant Separation | ❌ FAIL | Not enforced at runtime |
| Gate 19: Global-State Safety | ❌ FAIL | Mutable DEFAULT_CHECK_REGISTRY |

---

## Finding Ledger

### CRITICAL Findings

**FINDING-C001**: Multiple preflight authorities
- **Path**: `src/agent/components/core/bootstrap/__init__.py` has its own preflight system
- **Impact**: Violates CHECK-001, may allow bypass of canonical preflight
- **Remediation**: Remove bootstrap preflight or delegate to entrypoint/check

**FINDING-C002**: init.py doesn't validate preflight result
- **Path**: `src/agent/entrypoint/init/__init__.py`
- **Impact**: Initialization can proceed without validating stale results
- **Remediation**: Add result staleness and identity validation to init

**FINDING-C003**: Mutable module-level global state
- **Path**: `src/agent/entrypoint/check.py:DEFAULT_CHECK_REGISTRY`
- **Impact**: Violates CHECK-049, potential for side effects between runs
- **Remediation**: Make registry immutable or operation-scoped

### HIGH Findings

**FINDING-H001**: Staleness validation is duration-only
- **Path**: `src/agent/entrypoint/check/result.py:is_valid_for_launch`
- **Impact**: Results may be accepted after configuration changes
- **Remediation**: Add evidence binding (source fingerprint, config generation)

**FINDING-H002**: Agent-Assistant separation not enforced
- **Path**: Multiple files
- **Impact**: FULL_GORDON may execute without explicit policy
- **Remediation**: Enforce agent-only mode in default configuration

---

## Release Blockers

1. **Duplicate preflight authorities** (CHECK-001)
2. **init.py doesn't validate stale results**
3. **Mutable global registry**

---

## Certification Blockers

1. No formal Agent-Assistant separation enforcement
2. Import-time behavior not fully verified for all modules

---

## Recommendations

### Mandatory Remediation (Before Release)

1. Remove or integrate duplicate bootstrap preflight system
2. Add result staleness validation to init.py with evidence binding
3. Replace mutable DEFAULT_CHECK_REGISTRY with immutable alternative

### Non-Blocking Improvements

1. Implement full manifest-based compilation target selection
2. Add explicit architecture boundary checks
3. Enhance Agent-Assistant separation enforcement

### Test Improvements

1. Add preflight-integration tests
2. Add staleness validation tests
3. Add import-purity tests for all modules

---

## Final Certification

**Status: REMEDIATION_REQUIRED**

The architecture implements a canonical preflight authority at `agent.entrypoint.check` with proper immutable contracts and policy models. However, the following issues prevent certification:

1. **Duplicate preflight system** in bootstrap module may allow bypass
2. **init.py lacks stale result validation**
3. **Mutable global registry** violates state safety principles

After remediation of the three critical blockers, re-certification is recommended.

---

## Audit Validation

| Command | Status |
|---------|--------|
| `git rev-parse --show-toplevel` | ✅ /home/bvrznski/Gordon/gordon-system |
| `python -m compileall src/agent/entrypoint` | ✅ All modules compile successfully |
| `python --version` | ✅ 3.10.12 |

---

*End of Phase 3.7.32-A Audit Report*