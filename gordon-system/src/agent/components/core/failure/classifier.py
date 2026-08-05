# Failure Classifier
# ==================

"""
Deterministic failure classifier for Phase 3.7.10.

The classifier takes a failure observation and context, then produces
a classification result with:
    - Kind (TRANSIENT, RECOVERABLE, NON_RECOVERABLE, etc.)
    - Severity (INFO through PANIC)
    - Scope of affected entities
    - Retryability assessment
    - Rollback eligibility assessment  
    - Recovery eligibility assessment

Design principles:
    - DETERMINISTIC: Same inputs always produce same outputs
    - NO GUESSING: Unknown outcome must remain explicit, never defaulted
    - INTEGRITY FIRST: Corruption detected -> non-recoverable by ordinary means
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time

from .types import (
    RuntimeFailure,
    FailureKind,
    FailureSeverity,
    FailureDomain,
)


@dataclass(frozen=True)
class FailureClassificationResult:
    """
    Result of failure classification.
    
    Args:
        kind: Determined failure kind (TRANSIENT, RECOVERABLE, etc.)
        severity: Determined severity level
        scope: List of affected entity IDs
        retryability: True = safe to retry, False = unsafe, None = unknown
        rollback_eligibility: True = can rollback, False = cannot, None = unknown
        recovery_eligibility: True = can recover, False = cannot, None = unknown
        containment_requirement: Whether containment must precede recovery
        confidence: 0.0-1.0 confidence in classification
        unresolved_facts: List of facts we couldn't determine
        explanation: Human-readable explanation for the classification
    """
    
    kind: FailureKind = FailureKind.UNKNOWN
    severity: FailureSeverity = FailureSeverity.WARNING
    scope: List[str] = field(default_factory=list)
    
    retryability: Optional[bool] = None
    rollback_eligibility: Optional[bool] = None
    recovery_eligibility: Optional[bool] = None
    
    containment_requirement: bool = False
    
    confidence: float = 0.0
    unresolved_facts: List[str] = field(default_factory=list)
    explanation: str = ""


@dataclass(frozen=True)
class FailureClassificationContext:
    """
    Context for failure classification.
    
    This provides the classifier with additional information that affects
    how a failure should be classified.
    """
    
    # Runtime context
    runtime_id: Optional[str] = None
    current_state_version: int = 0
    
    # Prior failures (for deduplication and pattern recognition)
    recent_failure_count: int = 0
    last_same_kind_failure_utc: Optional[float] = None
    
    # Retry history for this source
    retry_count: int = 0
    restart_count: int = 0
    
    # Budget information
    remaining_retry_budget: int = 3
    remaining_restart_budget: int = 2
    
    # State information
    is_shutdown_requested: bool = False
    integrity_status: str = "unknown"  # healthy, degraded, corrupted, unknown
    
    # Known rollback points
    available_rollbacks: List[str] = field(default_factory=list)
    
    # Generation fencing (for restart/rollback eligibility)
    current_generation: int = 1
    is_stale_generation: bool = False


class FailureClassifier:
    """
    Deterministic failure classifier.
    
    Usage:
        classifier = FailureClassifier()
        
        result = await classifier.classify(
            observation=failure_observation,
            context=classification_context
        )
        
        if result.kind == FailureKind.TRANSIENT and result.retryability is True:
            # Safe to retry
            pass
        
        elif result.rollback_eligibility is True:
            # Can rollback to known prior state
            await initiate_rollback()
        
        else:
            # Escalate or mark as non-recoverable
            await escalate_failure(failure)
    """
    
    def __init__(self) -> None:
        """Initialize the classifier."""
        self._classification_rules = self._build_classification_rules()
    
    def _build_classification_rules(self) -> Dict[str, Any]:
        """Build classification rule mappings."""
        return {
            # Exception type patterns
            "timeout": {
                "kind": FailureKind.TIMEOUT,
                "severity": FailureSeverity.WARNING,
                "retryability": True,
            },
            "connectionerror": {
                "kind": FailureKind.DEPENDENCY,
                "severity": FailureSeverity.ERROR,
                "retryability": True,
            },
            "resourceexhausted": {
                "kind": FailureKind.RESOURCE_EXHAUSTION,
                "severity": FailureSeverity.CRITICAL,
                "retryability": False,  # Needs resource release first
            },
            "corruption": {
                "kind": FailureKind.DATA_CORRUPTION,
                "severity": FailureSeverity.FATAL,
                "retryability": False,
                "rollback_eligibility": True,
                "recovery_eligibility": False,  # Corrupted state cannot be recovered directly
            },
            "integrity": {
                "kind": FailureKind.INTEGRITY,
                "severity": FailureSeverity.CRITICAL,
                "retryability": False,
            },
            "configurationerror": {
                "kind": FailureKind.CONFIGURATION,
                "severity": FailureSeverity.ERROR,
                "retryability": False,  # Needs config change
            },
            "programmingerror": {
                "kind": FailureKind.PROGRAMMING,
                "severity": FailureSeverity.CRITICAL,
                "retryability": False,
                "recovery_eligibility": False,  # Requires code fix
            },
            "fatal": {
                "kind": FailureKind.FATAL,
                "severity": FailureSeverity.FATAL,
                "retryability": False,
                "recovery_eligibility": False,
            },
        }
    
    async def classify(
        self,
        failure: RuntimeFailure,
        context: Optional[FailureClassificationContext] = None
    ) -> FailureClassificationResult:
        """
        Classify a failure and return classification result.
        
        This is the canonical classification entry point. It must be
        deterministic - same inputs always produce same outputs.
        
        Args:
            failure: The failure to classify
            context: Classification context (optional, provides additional info)
            
        Returns:
            ClassificationResult with kind, severity, eligibility assessments
            
        Important: Unknown outcome MUST remain explicit. Do not guess.
        """
        ctx = context or FailureClassificationContext()
        
        # Start building classification result
        kind = self._determine_kind(failure, ctx)
        severity = self._determine_severity(failure, ctx)
        
        # Determine retryability based on kind and context
        retryability = self._evaluate_retryability(kind, failure, ctx)
        
        # Determine rollback eligibility
        rollback_eligibility = self._evaluate_rollback_eligibility(failure, ctx)
        
        # Determine recovery eligibility  
        recovery_eligibility = self._evaluate_recovery_eligibility(
            kind, failure, retryability, rollback_eligibility, ctx
        )
        
        # Build unresolved facts list
        unresolved_facts = []
        if retryability is None:
            unresolved_facts.append("retryability unknown")
        if rollback_eligibility is None:
            unresolved_facts.append("rollback eligibility unknown")
        if recovery_eligibility is None:
            unresolved_facts.append("recovery eligibility unknown")
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            kind, failure, ctx, len(unresolved_facts)
        )
        
        # Build explanation
        explanation = self._build_explanation(failure, kind, retryability, ctx)
        
        return FailureClassificationResult(
            kind=kind,
            severity=severity,
            scope=list(failure.scope),
            retryability=retryability,
            rollback_eligibility=rollback_eligibility,
            recovery_eligibility=recovery_eligibility,
            containment_requirement=failure.containment_requirement,
            confidence=confidence,
            unresolved_facts=unresolved_facts,
            explanation=explanation
        )
    
    def _determine_kind(self, failure: RuntimeFailure, ctx: FailureClassificationContext) -> FailureKind:
        """Determine the failure kind based on exception type and context."""
        # Check explicit kind first (if set by detector)
        if failure.kind != FailureKind.UNKNOWN:
            return failure.kind
        
        # Check exception type patterns
        exc_type = (failure.exception_type or "").lower()
        for pattern, rules in self._classification_rules.items():
            if pattern in exc_type:
                return FailureKind(rules["kind"])
        
        # Derive from message content
        msg_lower = (failure.message or "").lower()
        if "timeout" in msg_lower:
            return FailureKind.TIMEOUT
        if "corrupt" in msg_lower or "corruption" in msg_lower:
            return FailureKind.DATA_CORRUPTION
        if "integrity" in msg_lower:
            return FailureKind.INTEGRITY
        if "configuration" in msg_lower or "config" in msg_lower:
            return FailureKind.CONFIGURATION
        
        # No pattern matched - check integrity status
        if ctx.integrity_status == "corrupted":
            return FailureKind.STATE_CORRUPTION
        
        # Default based on other factors
        if failure.severity in (FailureSeverity.FATAL, FailureSeverity.PANIC):
            return FailureKind.FATAL
        
        if failure.kind == FailureKind.UNKNOWN:
            # We couldn't determine the kind - mark as unknown with explicit note
            pass
        
        return failure.kind
    
    def _determine_severity(self, failure: RuntimeFailure, ctx: FailureClassificationContext) -> FailureSeverity:
        """Determine severity based on impact and context."""
        # Use provided severity if available
        if failure.severity != FailureSeverity.WARNING:
            return failure.severity
        
        # Derive from kind and context
        if failure.kind in (FailureKind.FATAL, FailureKind.PANIC):
            return FailureSeverity.FATAL
        
        if failure.has_integrity_impact:
            return FailureSeverity.CRITICAL
        
        if failure.domain == FailureDomain.MODEL or failure.domain == FailureDomain.GPU:
            # External dependencies can have higher impact
            return FailureSeverity.ERROR
        
        return FailureSeverity.WARNING
    
    def _evaluate_retryability(
        self,
        kind: FailureKind,
        failure: RuntimeFailure,
        ctx: FailureClassificationContext
    ) -> Optional[bool]:
        """
        Evaluate whether this failure is retryable.
        
        Returns:
            True = safe to retry, False = unsafe (will not help), None = unknown
        
        Important rules:
            - Integrity failures are NEVER retryable (data may be corrupted)
            - Unknown side effects are NOT blindly retried
            - Known transient conditions ARE retryable
            - Budget exhaustion makes retry impossible
        """
        # Check explicit flag
        if failure.retryability is not None:
            return failure.retryability
        
        # Integrity corruption cannot be fixed by retrying
        if failure.has_integrity_impact:
            return False
        
        # FATAL and PANIC are never retryable
        if kind in (FailureKind.FATAL, FailureKind.PANIC):
            return False
        
        # Programming errors need code fix, not retry
        if kind == FailureKind.PROGRAMMING:
            return False
        
        # Configuration issues need config change
        if kind == FailureKind.CONFIGURATION:
            return False
        
        # Explicit transient conditions are retryable
        if kind in (FailureKind.TRANSIENT, FailureKind.TIMEOUT):
            return True
        
        # Dependency failures may be retryable
        if kind == FailureKind.DEPENDENCY:
            return True  # May recover when dependency recovers
        
        # Resource exhaustion needs resource release first
        if kind == FailureKind.RESOURCE_EXHAUSTION:
            return False  # Will fail again until resources freed
        
        # Unknown kind - cannot determine retryability safely
        # Return None to force explicit unknown state, not guess
        return None
    
    def _evaluate_rollback_eligibility(
        self,
        failure: RuntimeFailure,
        ctx: FailureClassificationContext
    ) -> Optional[bool]:
        """
        Evaluate whether rollback is eligible for this failure.
        
        Rollback eligibility requires:
            - Known pre-operation state exists (checkpoint/snapshot)
            - State can be restored deterministically
            - No unknown outcome (state must be known to rollback)
            
        Returns:
            True = rollback available, False = no rollback possible, None = unknown
        """
        # Explicit flag takes precedence
        if failure.rollback_eligibility is not None:
            return failure.rollback_eligibility
        
        # If we have unknown outcome, cannot safely roll back
        if failure.unknown_outcome:
            return False
        
        # Integrity corruption may be rollback eligible but requires special handling
        if failure.has_integrity_impact:
            return False  # Need recovery, not simple rollback
        
        # Check if rollback points are available in context
        if ctx.available_rollbacks:
            return True
        
        # Cannot determine without context - mark as unknown
        return None
    
    def _evaluate_recovery_eligibility(
        self,
        kind: FailureKind,
        failure: RuntimeFailure,
        retryability: Optional[bool],
        rollback_eligibility: Optional[bool],
        ctx: FailureClassificationContext
    ) -> Optional[bool]:
        """
        Evaluate whether recovery is eligible for this failure.
        
        Recovery requires:
            - At least one recovery path available (retry, rollback, restart)
            - Budget not exhausted
            - Not in shutdown with no recovery window
            
        Returns:
            True = can attempt recovery, False = cannot recover, None = unknown
        """
        # Explicit flag takes precedence
        if failure.recovery_eligibility is not None:
            return failure.recovery_eligibility
        
        # FATAL and PANIC never recoverable through ordinary means
        if kind in (FailureKind.FATAL, FailureKind.PANIC):
            return False
        
        # Programming error needs code fix
        if kind == FailureKind.PROGRAMMING:
            return False
        
        # Configuration needs manual intervention
        if kind == FailureKind.CONFIGURATION:
            return False
        
        # Check budget
        if ctx.remaining_retry_budget <= 0 and ctx.remaining_restart_budget <= 0:
            return False  # No budget left
        
        # At least one recovery path available?
        has_recovery_path = (
            retryability is True or 
            rollback_eligibility is True or
            kind in (FailureKind.DEPENDENCY, FailureKind.TIMEOUT)  # May recover naturally
        )
        
        if not has_recovery_path:
            return False
        
        # If we have unknown outcome but some recovery path exists, mark as potentially recoverable
        if failure.unknown_outcome:
            return None  # Unknown - cannot declare success without verification
        
        return True
    
    def _calculate_confidence(
        self,
        kind: FailureKind,
        failure: RuntimeFailure,
        ctx: FailureClassificationContext,
        unresolved_count: int
    ) -> float:
        """Calculate classification confidence (0.0-1.0)."""
        # Base confidence from explicit classifications
        base = 0.5
        
        if failure.kind != FailureKind.UNKNOWN:
            base += 0.2
        
        if failure.severity != FailureSeverity.WARNING:
            base += 0.1
        
        # Reduce for unresolved facts
        reduction = unresolved_count * 0.15
        
        return max(0.0, min(1.0, base - reduction))
    
    def _build_explanation(
        self,
        failure: RuntimeFailure,
        kind: FailureKind,
        retryability: Optional[bool],
        ctx: FailureClassificationContext
    ) -> str:
        """Build human-readable explanation for the classification."""
        parts = [
            f"Failure classified as {kind.value}",
            f"Retryability: {'possible' if retryability is True else 'not possible' if retryability is False else 'unknown'}",
            f"Source: {failure.source or 'unknown'}",
        ]
        
        if failure.exception_type:
            parts.append(f"Exception: {failure.exception_type}")
        
        if ctx.integrity_status != "unknown":
            parts.append(f"Integrity status: {ctx.integrity_status}")
        
        return "; ".join(parts)


# =============================================================================
# Failure detection adapters
# =============================================================================

class FailureDetectorProtocol:
    """
    Protocol for failure detectors.
    
    Implementations detect failures in specific subsystems and convert
    them to RuntimeFailure artifacts.
    """
    
    async def detect(self) -> Optional[RuntimeFailure]:
        """Detect a failure if one exists, otherwise return None."""
        raise NotImplementedError


class ExceptionAdapterDetector(FailureDetectorProtocol):
    """
    Detect failures from caught exceptions and convert to RuntimeFailure.
    """
    
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
    
    async def detect(self) -> Optional[RuntimeFailure]:
        """This would actually inspect exception queues in production."""
        # Placeholder for actual detection logic
        return None


class WatchdogDetector(FailureDetectorProtocol):
    """
    Detect watchdog expiry failures.
    """
    
    def __init__(self, runtime_id: str, heartbeat_timeout: float = 30.0) -> None:
        self._runtime_id = runtime_id
        self._heartbeat_timeout = heartbeat_timeout
    
    async def detect(self) -> Optional[RuntimeFailure]:
        """Detect if watchdog expiry occurred."""
        # Placeholder for actual detection logic
        return None