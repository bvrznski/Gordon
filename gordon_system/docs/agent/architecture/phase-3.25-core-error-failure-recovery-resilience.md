# Gordon Phase 3.25: Core Error, Failure, Recovery & Resilience Architecture

## Executive Summary

This phase establishes the canonical Error, Failure, Recovery, and Resilience Architecture for the Gordon Core.

**Status**: IMPLEMENTED  
**Phase**: 3.25  
**Date**: 2026-08-14

---

## Architectural Vision

The Gordon runtime shall continue operating correctly despite partial failures.

Failure shall become:
- **detectable** - Failures are discovered through explicit probes
- **classifiable** - Each failure belongs to a canonical category
- **observable** - Failure events are recorded in timeline
- **recoverable** - Recovery policies determine resolution paths
- **reproducible** - Same inputs produce same recovery behavior
- **diagnosable** - Full provenance and context preserved

Recovery shall become:
- **deterministic** - Same failure always produces same recovery plan
- **bounded** - No infinite retry loops or unbounded backoff
- **auditable** - Every action is recorded for compliance
- **explicit** - No implicit recovery decisions

---

## 1. Failure Philosophy

### 1.1 Core Principles

1. **Failure is inevitable** in any sufficiently complex system
2. **Silent failures are unacceptable** - all failures must be observable
3. **Recovery is explicit** - no hidden or implicit recovery mechanisms
4. **Determinism matters** - same failure always yields same outcome
5. **Ownership preserved** - component responsibility never transfers

### 1.2 Failure vs Error vs Exception

| Concept | Definition | Purpose |
|---------|-----------|---------|
| **Fault** | A condition that may lead to failure | Root cause analysis target |
| **Error** | A deviation from expected behavior | Classification and routing |
| **Exception** | Runtime signal of error | Control flow interruption |
| **Failure** | Manifestation of error as observable outcome | Recovery trigger |

### 1.3 Failure Taxonomy

```
Failure
├── Transient (may recover automatically)
│   ├── Timeout
│   ├── Temporary Unavailable
│   └── Network Partition
├── Recoverable (requires explicit recovery)
│   ├── Resource Exhaustion
│   ├── Dependency Failure
│   └── Model Failure
└── Non-recoverable (require shutdown)
    ├── Configuration Error
    ├── Programming Error
    ├── Data Corruption
    └── Security Breach
```

### 1.4 Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| INFO | Informational, no action | Log only |
| NOTICE | Notable event | Monitor |
| WARNING | May need attention | Review |
| ERROR | System impact | Recover |
| CRITICAL | Major impact | Escalate |
| FATAL | Terminal condition | Shutdown |
| PANIC | Emergency shutdown | Immediate |

---

## 2. Recovery Philosophy

### 2.1 Core Principles

1. **One canonical architecture** - no duplicate recovery frameworks
2. **Bounded retries** - always have maximum attempt limits
3. **Explicit policies** - all decisions follow defined rules
4. **State preservation** - rollback never corrupts data
5. **Observability first** - every action is logged

### 2.2 Recovery Strategies

| Strategy | When to Use | Risk Profile |
|----------|-------------|--------------|
| **Retry** | Transient failures, idempotent operations | Low |
| **Restart** | Component-level failures | Medium |
| **Rollback** | State corruption detected | Low-Medium |
| **Replay** | Message/transaction systems | Medium |
| **Compensate** | Distributed transactions | High |
| **Degradation** | Partial failure acceptable | Variable |
| **Failover** | Primary unavailable, backup ready | Medium |

### 2.3 Backoff Strategies

- **Constant**: Fixed delay between retries
- **Linear**: Delay increases by fixed amount each time
- **Exponential**: Delay doubles each retry (recommended default)
- **Jittered Exponential**: Exponential with randomization to prevent thundering herd
- **Bounced**: Alternate between min and max delays

---

## 3. Architecture Components

### 3.1 Error Classification

**ErrorClassifier**: Deterministic error classification system

```python
classifier = get_error_classifier()
kind, recoverable = classifier.classify(exception)
```

Classification rules:
1. Check custom exception type mapping first
2. Check base class hierarchy
3. Apply default rule (RUNTIME / recoverable)

### 3.2 Retry Infrastructure

**RetryPolicy**: Configurable bounded retry with backoff

```python
policy = RetryPolicy(
    max_attempts=3,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
)
```

Key properties:
- `max_attempts`: Hard limit on retry count (prevents infinite loops)
- `backoff_strategy`: Algorithm for delay calculation
- `retryable_exceptions`: Tuple of exception types that qualify

**CircuitBreaker**: Prevents cascading failures

```python
breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=30.0,
))
```

States: CLOSED → OPEN → HALF_OPEN (testing recovery)

### 3.3 Recovery Coordination

**RecoveryCoordinator**: Orchestrates all recovery operations

```python
coordinator = get_recovery_coordinator()

success, result = coordinator.execute_with_retry(
    operation=my_function,
    policy=policy
)
```

---

## 4. Failure Lifecycle

```
Fault Occurrence
        ↓
   Detection (health probes, invariants)
        ↓
Classification (category, severity, recovery eligibility)
        ↓
  Isolation (containment scope established)
        ↓
 Diagnostics (context captured, timeline started)
        ↓
Policy Evaluation (retry policy applied)
        ↓
Recovery Selection (strategy chosen from candidates)
        ↓
Recovery Execution (attempted with backoff)
        ↓
 Validation (recovery verified)
        ↓
Resolution (success or escalation)
        ↓
 Certification (recorded for audit)
        ↓
 Archival (for historical analysis)
```

---

## 5. Fault Domains

| Domain | Scope | Owner | Recovery Capability |
|--------|-------|-------|---------------------|
| Component Fault Domain | Single component | Component owner | Restart, reinitialize |
| Service Fault Domain | Entire service | Service owner | Restart, rollback |
| Runtime Fault Domain | Runtime instance | Runtime team | Full restart |
| Capability Fault Domain | Specific capability | Capability owner | Reinvoke with new state |

---

## 6. Recovery Policies

### 6.1 Retry Policy

```python
RetryPolicy(
    max_attempts=3,
    backoff_strategy=BackoffStrategy.EXPONENTIAL,
    backoff_config=BackoffConfig(
        initial_delay=0.1,
        maximum_delay=60.0,
        multiplier=2.0
    ),
    retryable_exceptions=(TransientError, ConnectionError)
)
```

### 6.2 Degradation Policy

```python
DegradationPolicy(
    enabled=True,
    max_degradation_level=3,
    fallback_implementations={"feature_a": "fallback_implementation"}
)
```

---

## 7. Diagnostics & Observability

### 7.1 Failure Timeline

Records every failure lifecycle event:

- Detection timestamp
- Classification result
- Recovery attempts with timing
- Verification status
- Resolution outcome

### 7.2 Recovery Metrics

- **MTTR**: Mean Time To Recovery (seconds)
- **Retry Success Rate**: Percentage of successful retries
- **Recovery Success Rate**: Percentage of successful recoveries

---

## 8. Migration from Legacy Implementations

All existing failure handling implementations must migrate to the canonical architecture:

| Component | Old Implementation | New Implementation |
|-----------|-------------------|-------------------|
| Exception hierarchy | ad-hoc | GordonError base class |
| Retry logic | per-component | RetryPolicy + RecoveryCoordinator |
| Circuit breaking | none | CircuitBreaker component |
| Backoff strategies | inconsistent | BackoffStrategy enum |

---

## 9. Certification Checklist

- [x] One canonical failure architecture exists
- [x] One canonical recovery architecture exists  
- [x] Failure classification is deterministic
- [x] Fault domains prevent uncontrolled propagation
- [x] Retries are bounded (max attempts enforced)
- [x] Backoff strategies implemented and tested
- [x] Circuit breaker pattern integrated
- [x] Degradation policy defined
- [x] Timeline events recorded for all failures
- [x] Metrics collection operational

---

## 10. Files Created/Modified

### Core Architecture (`gordon_system/src/agent/components/core/failure/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Main module exports and canonical implementation |
| `types.py` | FailureKind, FailureSeverity, RuntimeFailure types |
| `architecture.py` | FailureArtifact, RecoveryPlanner, RecoveryCoordinator |
| `retry_policy.py` | Retry budget management |
| `compensation.py` | Compensation transaction patterns |
| `containment.py` | Fault domain isolation |
| `propagation.py` | Failure propagation rules |

### Documentation (`gordon_system/docs/agent/architecture/`)

| File | Purpose |
|------|---------|
| `phase-3.25-core-error-failure-recovery-resilience.md` | This document |
| `phase-3.25-machine-readable-report.json` | Machine-readable specification |

---

## 11. Conclusion

Phase 3.25 establishes the canonical Error, Failure, Recovery & Resilience Architecture for Gordon.

All subsystems shall use this architecture exclusively. No custom recovery frameworks are permitted.

**Architecture is complete and certified.**