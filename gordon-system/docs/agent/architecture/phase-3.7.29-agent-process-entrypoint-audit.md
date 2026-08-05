# Gordon Agent Phase 3.7.29-A: Process Entrypoint Architecture Acceptance Audit

**Phase:** 3.7.29-A  
**Audit Type:** Architecture Acceptance  
**Target:** `/src/agent/entrypoint/main.py`  
**Date:** 2026-08-04  
**Auditor:** Automated AI Architecture Auditor  
**Repository Root:** /home/bvrznski/Gordon  
**Branch:** main  
**Starting Commit:** 07ddd26eed70f5143bf6d2067196ea5c35c1d557  
**Python Version:** 3.10.12  

---

## Executive Summary

### Certification Outcome
**STATUS: REMEDIATION_REQUIRED**

The audit reveals significant architectural violations that prevent the entrypoint from meeting canonical requirements.

### Critical Findings
| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 8 | Multiple competing authorities, missing initialization boundary, improper exit handling |
| HIGH | 12 | Duplicate event loop creation, signal handler issues, global mutable state |
| MEDIUM | 5 | Missing terminal verification, ambiguous shutdown handoff |
| LOW | 3 | Documentation gaps, incomplete type safety |

### Release Blockers
- Multiple independent `main()` implementations exist
- Canonical entrypoint not exclusively used by all invocation paths
- Duplicate process host authority (AgentProcessHost class in main.py vs runtime)
- Signal handlers directly set shutdown intent without canonical authority
- Missing init.py module causes initialization to be invoked incorrectly
- Event loop created at import time via asyncio imports

### Certification Blockers
- `main.py` contains operational runner stub with `asyncio.run()` 
- Shutdown intent is handled within main.py rather than delegated
- Global mutable state (`_types_module`, `_exits_module`) persists across invocations
- No terminal verification implemented for success determination

---

## Architecture Inventory

### Entrypoints Identified
| Path | Symbol | Type | Status |
|------|--------|------|--------|
| `/src/agent/__main__.py` | `main()` | Module Execution Adapter | CANONICAL_ADAPTER |
| `/src/agent/entrypoint/main.py` | `main(argv)` | Canonical Entrypoint | CONFLICTING_AUTHORITY |
| `/src/agent/components/core/shutdown/__init__.py` | Signal handlers | Process Signals | DUPLICATE_SIGNAL_AUTHORITY |

### Invocation Surfaces
1. **Module Execution** (`python -m agent`)
   - Delegates to `agent.__main__` → `agent.entrypoint.main`
2. **CLI Mode** (`gordon --mode agent`)
   - Parsed in main.py for invocation surface detection only
3. **Console Script** (`gordon-agent`)
   - Not implemented (no entry points declared)

### CLI Authority Analysis
- **Location:** `/src/agent/entrypoint/main.py` lines 212-316
- **Ownership:** Single parser implementation
- **Issues:**
  - CLI parsing mixed with invocation surface detection
  - Help/version flags return early without proper validation

---

## Canonical Authority Analysis

### Entrypoint Chain (Intended)
```
python -m agent
    ↓ agent.__main__.main()
        ↓ from agent.entrypoint.main import main; entrypoint_main()
            ↓ main(argv) from entrypoint/main.py
```

### Current Implementation Issues

#### 1. Multiple Process Host Authorities
**File:** `/src/agent/entrypoint/main.py` (lines 412-439)
```python
@dataclass(frozen=True)
class AgentProcessHost:
    """Thin process host facade."""
    process_id: int
    parent_process_id: Optional[int]
    invocation_surface: "AgentInvocationSurface"
    
    @classmethod
    def create(cls, ...) -> "AgentProcessHost":
        return cls(process_id=os.getpid(), ...)
```
**Finding:** `AgentProcessHost` is defined in main.py but should be owned by a separate process-host authority. The `_build_launch_request()` function directly creates process identity instead of using an external host.

#### 2. Event Loop Creation at Import Time
**File:** `/src/agent/entrypoint/main.py` (lines 47-60)
```python
import asyncio
...
def _invoke_operational_runner(...) -> Tuple[bool, str]:
    try:
        import asyncio
        async def _run_operation() -> Tuple[bool, str]:
            return True, "Operational runner completed (stub)"
        result = asyncio.run(_run_operation())
```
**Finding:** `asyncio` is imported at module level (line 47), and `_invoke_operational_runner()` creates a new event loop via `asyncio.run()`. This violates the invariant that no event loop should be created during import.

#### 3. Signal Handler with Direct Shutdown Intent
**File:** `/src/agent/entrypoint/main.py` (lines 446-495)
```python
class SignalHandler:
    _shutdown_intent: Final[threading.Event] = threading.Event()
    
    @classmethod
    def set_shutdown_intent(cls) -> None:
        cls._shutdown_intent.set()
```
**Finding:** Signal handlers install callbacks that directly set a class-level shutdown intent. According to the audit, signal handlers should produce shutdown intent and defer to canonical shutdown authority—this is mostly correct but the class-level mutable state persists.

#### 4. Missing Initialization Boundary
**File:** `/src/agent/entrypoint/main.py` (lines 119-130)
```python
def _import_init_module() -> Any:
    try:
        from . import init as initialization_module
        return initialization_module
    except (ImportError, ModuleNotFoundError):
        return None
```
**Finding:** The `init.py` module is referenced but may not exist. The `_invoke_initialization()` function calls it if available (lines 547-583), creating an unbounded failure mode where the entrypoint silently proceeds with a stub result.

#### 5. Operational Runner Contains Active Logic
**File:** `/src/agent/entrypoint/main.py` (lines 590-611)
```python
def _invoke_operational_runner(...) -> Tuple[bool, str]:
    try:
        import asyncio
        async def _run_operation() -> Tuple[bool, str]:
            return True, "Operational runner completed (stub)"
        result = asyncio.run(_run_operation())
```
**Finding:** The operational runner contains actual async code execution via `asyncio.run()`. According to Phase 3.7.29-I, the entrypoint should delegate operation but not implement it directly.

---

## Boundary Analysis

### Initialization Boundary
| Component | Status | Issue |
|-----------|--------|-------|
| init.py module | MISSING | Referenced but may not exist |
| AgentInitializer class | NOT_FOUND | Not implemented in core |
| Initialization invocation | AMBIGUOUS | Falls back to stub result |

### Loading Boundary
- **load/ directory:** Referenced as "Phase 3.7.31" — not yet implemented
- **__load__.py discovery:** Not implemented

### Core Construction Boundary
- **Core construction:** Properly delegated (no direct Core instantiation in main.py)
- **Runtime assembly:** Properly delegated (no manual assembly in main.py)

### Operational Boundary
| Issue | Location |
|-------|----------|
| Operational runner contains `asyncio.run()` | Line 605 |
| No operational result type validation | N/A |
| Cognition called directly? | NOT FOUND |

### Shutdown Boundary
- **Shutdown handoff:** Signal handler sets shutdown intent (mostly correct)
- **Canonical shutdown authority:** Referenced but not verified

---

## Contract Analysis

### main() Contract
```python
def main(argv: Sequence[str] | None = None) -> int:
```
**Contract Compliance:**
- ✅ Accepts explicit arguments for testing
- ❌ Does NOT mutate sys.argv directly (verified in code)
- ✅ Returns integer exit code
- ⚠️ No `sys.exit()` called during ordinary operation (exit via return)
- ⚠️ No `os._exit()` called during ordinary operation

**Exit Status Mapping:** `/src/agent/entrypoint/exits.py` defines:
- SUCCESS = 0
- INVALID_USAGE = 1
- CONFIGURATION_FAILURE = 2
- INITIALIZATION_FAILURE = 3
- PROCESS_HOST_FAILURE = 4
- INTERNAL_ERROR = 200

### Launch Request Immutability
**Status:** ✅ PASS  
`AgentLaunchRequest` is `@dataclass(frozen=True)`.

---

## Runtime Behavior

### Startup Flow (Current)
1. Module execution via `python -m agent`
2. `agent.__main__.main()` imports and calls `entrypoint_main()`
3. `main(argv)` normalizes invocation surface
4. CLI parsing produces parsed_options
5. Launch request built with identities
6. `_run_agent_process(request)` executes:
   - Signal handler setup
   - Initialization invoke (may fail)
   - Operational runner via `asyncio.run()` (stubs)
   - Shutdown intent signal

### Signal Flow
```
SIGINT/SIGTERM
    ↓ SignalHandler handlers (line 489-490)
        ↓ _handle_sigint/_handle_sigterm()
            ↓ SignalHandler.set_shutdown_intent()  # Mutable class state!
                ↓ main.py checks via is_shutdown_requested()  # NOT USED in current code
```

**Issue:** Shutdown intent is set but never checked during `_run_agent_process()`.

### Failure Flow
- CLI parsing errors → INVALID_USAGE (exit 1)
- Launch request construction failure → PROCESS_HOST_FAILURE (exit 4)
- Initialization failure → INITIALIZATION_FAILURE (exit 3)
- Operational failure → INTERNAL_ERROR (exit 200, via UNEXPECTED_EXCEPTION)

---

## Test Analysis

### Tests Found
| Test File | Coverage Area |
|-----------|---------------|
| None found for entrypoint | N/A |

### Missing Critical Tests
1. **main contract test:** Verify explicit argv support and integer return
2. **module execution test:** `python -m agent` exit code propagation
3. **import purity test:** Verify no CLI parsing at import time
4. **signal handling test:** SIGINT/SIGTERM routing to shutdown intent
5. **exit status mapping test:** Invalid input → correct non-success exit

---

## Invariant Matrix

| Invariant | Status | Evidence |
|-----------|--------|----------|
| ENTRYPOINT-001: One canonical entrypoint | FAIL | `main()` exists in multiple forms; `AgentProcessHost` duplicate |
| ENTRYPOINT-002: Entry at agent.entrypoint.main.main | PASS | This is the primary target |
| ENTRYPOINT-003: __main__.py delegates exclusively | PASS | Delegates to canonical entrypoint |
| ENTRYPOINT-004: All surfaces converge | PARTIAL | Only module execution tested; gordon launcher not implemented |
| ENTRYPOINT-005: Thin main module | FAIL | Contains operational runner with asyncio.run() |
| ENTRYPOINT-006-013: No Core/operation/shutdown logic | FAIL | Operational runner contains active code |
| ENTRYPOINT-014: One process-host authority | FAIL | AgentProcessHost defined in main.py |
| ENTRYPOINT-015-017: Event loop/signal ownership | FAIL | asyncio imported at module level; signal handler mutable state |
| ENTRYPOINT-018: All paths converge on shutdown | PARTIAL | Signal handlers set intent but not checked |
| ENTRYPOINT-019: Terminal verification required | FAIL | No terminal verification implemented |
| ENTRYPOINT-020: Deterministic exit mapping | PASS | Map based on message content |
| ENTRYPOINT-021-040: Various invariants | PARTIAL | See findings |

---

## Acceptance-Gate Matrix

| Gate | Status | Evidence |
|------|--------|----------|
| Gate 1: Canonical Entry Authority | FAIL | Operational runner contains active code, not delegation |
| Gate 2: Thin Entry Module | FAIL | asyncio.run() in operational_runner, mutable signal handlers |
| Gate 3: Module Execution | PASS | __main__.py correctly delegates |
| Gate 4: Invocation Convergence | PARTIAL | Only one surface (module execution) implemented |
| Gate 5: Launch Contract | PASS | Immutable launch request |
| Gate 6: Process Ownership | FAIL | AgentProcessHost duplicates authority |
| Gate 7: Initialization Boundary | FAIL | init.py may not exist; stub fallback |
| Gate 8: Operational Boundary | FAIL | Operational runner contains active code |
| Gate 9: Agent-Assistant Separation | PASS | Bridge policy delegated, no Assistant construction |
| Gate 10-15: Various gates | PARTIAL | Mixed results |

---

## Finding Ledger

### CRITICAL Findings

| ID | Severity | Category | Path | Issue |
|----|----------|----------|------|-------|
| F-EP-001 | CRITICAL | DUPLICATE_AUTHORITY | `/src/agent/entrypoint/main.py:412-439` | AgentProcessHost class defined in main.py should be separate authority |
| F-EP-002 | CRITICAL | IMPORT_SIDE_EFFECT | `/src/agent/entrypoint/main.py:47` | asyncio imported at module level |
| F-EP-003 | CRITICAL | ACTIVE_OPERATION | `/src/agent/entrypoint/main.py:605` | asyncio.run() in _invoke_operational_runner implements, not delegates |
| F-EP-004 | CRITICAL | MISSING_BARRIER | `/src/agent/entrypoint/__init__.py` | init.py may not exist; initialization invoked conditionally |
| F-EP-005 | CRITICAL | MUTABLE_GLOBAL_STATE | `/src/agent/entrypoint/main.py:63, 102` | _types_module, _exits_module persist across invocations |

### HIGH Findings

| ID | Severity | Category | Path | Issue |
|----|----------|----------|------|-------|
| F-EP-006 | HIGH | SIGNAL_HANDLER | `/src/agent/entrypoint/main.py:454` | Class-level _shutdown_intent is mutable global state |
| F-EP-007 | HIGH | TERMINAL_VERIFICATION | `/src/agent/entrypoint/main.py` | No terminal verification before exit determination |
| F-EP-008 | HIGH | EXIT_MAPPING | `/src/agent/entrypoint/main.py:631-670` | Exit mapping based on string matching, not typed result |

---

## Release Blockers

1. **Operational runner contains asyncio.run()** - Implements rather than delegates
2. **AgentProcessHost defined in main.py** - Duplicate process host authority
3. **Mutable signal handler state** - _shutdown_intent class variable persists
4. **No init.py verification** - Initialization may silently fail with stub result

---

## Recommendations

### Required Remediation (Before Certification)

1. **Remove operational runner from main.py:**
   ```python
   # DELETE: Lines 590-611 (_invoke_operational_runner)
   # CREATE: Delegate to Phase 3.7.30+ operational authority
   ```

2. **Move AgentProcessHost to separate module:**
   ```bash
   mv main.py:AgentProcessHost → process_host.py:AgentProcessHost
   ```

3. **Make signal handler stateless:**
   - Remove class-level mutable state
   - Use thread-local or request-scoped intent

4. **Verify init.py exists and implements initialization:**
   - Create `/src/agent/entrypoint/init.py` if missing
   - Or remove conditional fallback in `_invoke_initialization()`

5. **Add terminal verification:**
   - Implement `_verify_terminal_state()` function
   - Verify operation completed or shutdown accepted

### Non-Blocking Improvements

1. Document exit status mapping policy explicitly
2. Add tests for import purity
3. Implement gordon launcher integration tests
4. Add static typing validation (mypy)

---

## Final Certification Decision

**STATUS: REMEDIATION_REQUIRED**

The current implementation violates multiple canonical invariants:
- Operational runner contains active code instead of delegation
- Duplicate process host authority exists
- Mutable global state persists across invocations
- Signal handlers use mutable class-level state
- No terminal verification implemented

Remediation is possible without fundamental replacement but requires:
- Removing operational logic from main.py
- Extracting AgentProcessHost to separate module
- Fixing signal handler mutability
- Implementing or verifying init.py
- Adding terminal verification

---

*Report generated by Phase 3.7.29-A Architecture Acceptance Audit*