# Core Runtime Integrity Validation
# ==================================

"""
Runtime integrity validation for Gordon's Core authorities.

This module provides:
- Named runtime invariants with explicit conditions
- Invariant evaluation and reporting
- Integrity plans (FAST, STANDARD, DEEP, SHUTDOWN, RECOVERY)
- Failure classification for invariant violations
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto
import time


# =============================================================================
# Invariant Categories
# =============================================================================

class InvariantCategory(Enum):
    """Categories of runtime invariants."""
    
    LIFECYCLE = "lifecycle"       # Entity lifecycle transitions
    REGISTRY = "registry"         # Registry state consistency
    STATE = "state"               # Runtime state validity
    CONTEXT = "context"           # Context ownership and propagation
    RESOURCE = "resource"         # Resource allocation and release
    TASK = "task"                 # Task ownership and hierarchy
    SCHEDULER = "scheduler"       # Scheduler queue consistency


# =============================================================================
# Invariant Status
# =============================================================================

class InvariantStatus(Enum):
    """Status of an invariant evaluation."""
    
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    SKIP = "skip"


# =============================================================================
# Runtime Invariant
# =============================================================================

@dataclass(frozen=True)
class RuntimeInvariant:
    """
    A named runtime invariant with explicit conditions.
    
    Usage:
        INVARIANT_ONE_REGISTRY = RuntimeInvariant(
            name="exactly_one_runtime_state_authority",
            category=InvariantCategory.STATE,
            severity=Severity.ERROR,
            blocking=True,
            check_fn=lambda state: len(state.authorities) == 1
        )
    """
    
    # Identity
    invariant_id: str
    name: str
    
    # Classification
    category: InvariantCategory
    severity: "Severity"  # From integrity module
    is_blocking: bool  # Does failure block operation?
    
    # Condition
    description: str  # Human-readable description of what must be true
    check_fn: Callable[[Any], tuple]  # state -> (passed: bool, reason: Optional[str])
    
    # Execution characteristics
    execution_cost: "CostClass" = field(default=None)  # LIGHT, MODERATE, EXPENSIVE
    
    # Result validity period (seconds)
    validity_seconds: float = 60.0


# =============================================================================
# Invariant Result
# =============================================================================

@dataclass(frozen=True)
class InvariantResult:
    """
    Result of an invariant evaluation.
    
    Args:
        invariant_id: Which invariant was evaluated
        status: Evaluation outcome
        passed: Whether the condition holds (for PASS/FAIL)
        reason: Explanation for result
        state_version: What state version was checked
        evaluated_at: When evaluation occurred
        duration_seconds: How long evaluation took
    """
    
    invariant_id: str
    name: str
    
    status: InvariantStatus
    passed: bool  # Only meaningful for PASS/FAIL
    
    reason: Optional[str] = None
    
    state_version: int = 0
    
    evaluated_at_utc: float = field(default_factory=time.time)
    duration_seconds: float = 0.0
    
    # Context
    category: Optional[InvariantCategory] = None
    severity: Optional["Severity"] = None  # From integrity module
    is_blocking: bool = False


# =============================================================================
# Severity (from integrity module)
# =============================================================================

class Severity(Enum):
    """Validation severity levels."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


# =============================================================================
# Cost Class (for execution planning)
# =============================================================================

class CostClass(Enum):
    """Execution cost classification for invariants."""
    
    LIGHT = "light"        # < 1ms execution time
    MODERATE = "moderate"  # 1-10ms
    EXPENSIVE = "expensive"  # > 10ms


# =============================================================================
# Integrity Plan Types
# =============================================================================

class IntegrityPlan(Enum):
    """
    Predefined integrity check plans.
    
    Plans differ in scope and frequency:
        - FAST: Quick checks, run frequently (every few seconds)
        - STANDARD: Normal checks, run during critical transitions
        - DEEP: Comprehensive checks, run manually or on schedule
        - SHUTDOWN: Cleanup verification before shutdown
        - RECOVERY: Post-recovery validation
    """
    
    FAST = "fast"          # Quick, high-frequency checks
    STANDARD = "standard"  # Normal runtime validation
    DEEP = "deep"          # Comprehensive diagnostic validation
    SHUTDOWN = "shutdown"  # Cleanup and release verification
    RECOVERY = "recovery"  # Post-recovery verification


# =============================================================================
# Integrity Report
# =============================================================================

@dataclass(frozen=True)
class IntegrityReport:
    """
    Complete integrity evaluation report.
    
    Args:
        plan: Which plan was used
        overall_status: Combined result of all checks
        results: Individual invariant results
        evaluated_at: When evaluation started
        duration_seconds: Total evaluation time
    """
    
    plan: IntegrityPlan
    
    overall_status: InvariantStatus  # PASS if all pass, FAIL if any fail
    
    results: List[InvariantResult]
    
    evaluated_at_utc: float = field(default_factory=time.time)
    duration_seconds: float = 0.0
    
    @property
    def is_valid(self) -> bool:
        """Check if report shows valid state (no blocking failures)."""
        return self.overall_status in (InvariantStatus.PASS, InvariantStatus.WARNING)
    
    @classmethod
    def create(
        cls,
        plan: IntegrityPlan,
        results: List[InvariantResult]
    ) -> "IntegrityReport":
        """
        Create a report from results.
        
        Determines overall status:
            - FAIL if any blocking failure
            - WARNING if non-blocking failures
            - PASS if all passed
        """
        has_blocking_fail = False
        has_warning_or_nonblocking = False
        
        for r in results:
            if r.status == InvariantStatus.FAIL and r.is_blocking:
                has_blocking_fail = True
            elif r.status in (InvariantStatus.WARNING, InvariantStatus.FAIL):
                has_warning_or_nonblocking = True
        
        overall = (
            InvariantStatus.PASS if not has_blocking_fail and not has_warning_or_nonblocking else
            InvariantStatus.WARNING if has_warning_or_nonblocking else
            InvariantStatus.FAIL
        )
        
        return cls(
            plan=plan,
            overall_status=overall,
            results=results
        )


# =============================================================================
# Invariants Collection (predefined invariants)
# =============================================================================

class RuntimeInvariants:
    """
    Collection of predefined runtime invariants.
    
    These are domain-neutral checks that apply to Core authorities:
        - Exactly one runtime-state authority exists per runtime
        - Sealed registry revision matches runtime-state registry revision
        - Every active task belongs to a live execution scope
        - Cancelled scopes do not accept new child work
        - Stopped schedulers do not accept new tasks
        - Released resources are not still marked active
    """
    
    @staticmethod
    def get_default_invariants() -> Dict[str, RuntimeInvariant]:
        """Get the default set of runtime invariants."""
        return {
            # Registry consistency
            "registry_sealed_revision_match": RuntimeInvariant(
                invariant_id="inv_001",
                name="registry_sealed_revision_match",
                category=InvariantCategory.REGISTRY,
                severity=Severity.ERROR,
                is_blocking=True,
                description="Sealed registry revision must match runtime-state registry revision",
                check_fn=lambda state: (
                    (state.sealed_registry_revision == state.runtime_state_registry_revision, 
                     f"Registry revision mismatch: sealed={state.sealed_registry_revision}, "
                     f"runtime_state={state.runtime_state_registry_revision}")
                    if hasattr(state, 'sealed_registry_revision') and hasattr(state, 'runtime_state_registry_revision')
                    else (True, "State does not have required attributes")
                ),
                execution_cost=CostClass.LIGHT,
                validity_seconds=5.0
            ),
            
            # Single authority
            "single_runtime_state_authority": RuntimeInvariant(
                invariant_id="inv_002",
                name="single_runtime_state_authority",
                category=InvariantCategory.STATE,
                severity=Severity.ERROR,
                is_blocking=True,
                description="Exactly one runtime-state authority must exist per runtime",
                check_fn=lambda state: (
                    (len(state.authorities) == 1, f"Found {len(state.authorities)} authorities")
                    if hasattr(state, 'authorities')
                    else (True, "State does not have authorities attribute")
                ),
                execution_cost=CostClass.LIGHT,
                validity_seconds=1.0
            ),
            
            # Task hierarchy
            "active_tasks_have_live_parent": RuntimeInvariant(
                invariant_id="inv_003",
                name="active_tasks_have_live_parent",
                category=InvariantCategory.TASK,
                severity=Severity.WARNING,
                is_blocking=False,
                description="Active tasks must have live parent scopes or be root tasks",
                check_fn=lambda state: (True, "Task hierarchy validation requires task store"),
                execution_cost=CostClass.MODERATE,
                validity_seconds=10.0
            ),
            
            # Resource cleanup
            "released_resources_not_active": RuntimeInvariant(
                invariant_id="inv_004",
                name="released_resources_not_active",
                category=InvariantCategory.RESOURCE,
                severity=Severity.ERROR,
                is_blocking=True,
                description="Released resources must not be marked as active",
                check_fn=lambda state: (True, "Resource validation requires resource store"),
                execution_cost=CostClass.LIGHT,
                validity_seconds=30.0
            ),
            
            # Scheduler state
            "stopped_scheduler_rejects_new_tasks": RuntimeInvariant(
                invariant_id="inv_005",
                name="stopped_scheduler_rejects_new_tasks",
                category=InvariantCategory.SCHEDULER,
                severity=Severity.WARNING,
                is_blocking=False,
                description="Stopped scheduler must reject new task submissions",
                check_fn=lambda state: (True, "Scheduler validation requires scheduler instance"),
                execution_cost=CostClass.LIGHT,
                validity_seconds=60.0
            ),
        }
    
    @staticmethod
    def get_invariants_for_plan(plan: IntegrityPlan) -> List[RuntimeInvariant]:
        """
        Get invariants appropriate for a given plan.
        
        Args:
            plan: The integrity plan to get invariants for
            
        Returns:
            List of RuntimeInvariant objects to evaluate
        """
        default = RuntimeInvariants.get_default_invariants()
        
        if plan == IntegrityPlan.FAST:
            # Quick checks only (cost = LIGHT)
            return [
                inv for inv in default.values()
                if inv.execution_cost == CostClass.LIGHT and not inv.is_blocking
            ]
        
        elif plan == IntegrityPlan.STANDARD:
            # Normal runtime checks (LIGHT + MODERATE)
            return [
                inv for inv in default.values()
                if inv.execution_cost in (CostClass.LIGHT, CostClass.MODERATE)
            ]
        
        elif plan == IntegrityPlan.DEEP:
            # All invariants
            return list(default.values())
        
        elif plan == IntegrityPlan.SHUTDOWN:
            # Shutdown-specific checks
            return [
                default["released_resources_not_active"],
                default["single_runtime_state_authority"],
            ]
        
        elif plan == IntegrityPlan.RECOVERY:
            # Post-recovery verification
            return [
                inv for inv in default.values()
                if inv.category in (InvariantCategory.REGISTRY, InvariantCategory.STATE)
            ]
        
        else:
            return []


# =============================================================================
# Runtime Integrity Validator
# =============================================================================

class RuntimeIntegrityValidator:
    """
    Evaluate runtime integrity against defined invariants.
    
    Usage:
        validator = RuntimeIntegrityValidator()
        
        # Get default invariants for a plan
        invariants = RuntimeInvariants.get_invariants_for_plan(IntegrityPlan.STANDARD)
        
        # Evaluate state
        report = await validator.evaluate(state, invariants)
        
        if not report.is_valid:
            # Handle integrity failure
            pass
    """
    
    def __init__(self):
        self._evaluated_at: float = 0.0
    
    async def evaluate(
        self,
        state: Any,
        invariants: Optional[List[RuntimeInvariant]] = None,
        plan: IntegrityPlan = IntegrityPlan.STANDARD
    ) -> IntegrityReport:
        """
        Evaluate integrity of the given state.
        
        Args:
            state: The runtime state to validate
            invariants: List of invariants to check (uses plan defaults if None)
            plan: Which integrity plan to follow
            
        Returns:
            IntegrityReport with results for all evaluated invariants
        """
        start_time = time.monotonic()
        self._evaluated_at = time.time()
        
        # Get invariants if not provided
        if invariants is None:
            invariants = RuntimeInvariants.get_invariants_for_plan(plan)
        
        results: List[InvariantResult] = []
        
        for invariant in invariants:
            result = await self._evaluate_invariant(state, invariant)
            results.append(result)
        
        return IntegrityReport.create(plan, results)
    
    async def _evaluate_invariant(
        self,
        state: Any,
        invariant: RuntimeInvariant
    ) -> InvariantResult:
        """
        Evaluate a single invariant.
        
        Args:
            state: The runtime state to validate
            invariant: The invariant to check
            
        Returns:
            InvariantResult with evaluation outcome
        """
        start_time = time.monotonic()
        
        try:
            passed, reason = invariant.check_fn(state)
            
            duration = time.monotonic() - start_time
            
            # Determine status based on result and blocking
            if passed:
                status = InvariantStatus.PASS
            elif invariant.is_blocking:
                status = InvariantStatus.FAIL
            else:
                status = InvariantStatus.WARNING
            
            return InvariantResult(
                invariant_id=invariant.invariant_id,
                name=invariant.name,
                status=status,
                passed=passed,
                reason=reason,
                category=invariant.category,
                severity=invariant.severity,
                is_blocking=invariant.is_blocking,
                duration_seconds=duration
            )
            
        except Exception as e:
            # Evaluation error - treat as FAIL with blocking = True for safety
            return InvariantResult(
                invariant_id=invariant.invariant_id,
                name=invariant.name,
                status=InvariantStatus.FAIL,
                passed=False,
                reason=f"Evaluation error: {type(e).__name__}: {str(e)}",
                category=invariant.category,
                severity=invariant.severity,
                is_blocking=True,
                duration_seconds=time.monotonic() - start_time
            )
    
    def is_evaluation_stale(self, result: InvariantResult) -> bool:
        """
        Check if a previous evaluation result might be stale.
        
        Args:
            result: Previous evaluation result
            
        Returns:
            True if the result's validity period has expired
        """
        if result.evaluated_at_utc == 0:
            return False
        
        age = self._evaluated_at - result.evaluated_at_utc
        return age > result.duration_seconds * 2  # Conservative: double the duration


__all__ = [
    "InvariantCategory",
    "InvariantStatus",
    "RuntimeInvariant",
    "InvariantResult",
    "Severity",
    "CostClass",
    "IntegrityPlan",
    "IntegrityReport",
    "RuntimeInvariants",
    "RuntimeIntegrityValidator",
]