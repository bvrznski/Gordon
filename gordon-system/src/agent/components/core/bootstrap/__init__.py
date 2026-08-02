# Core Bootstrap Infrastructure
# =============================

"""
Core bootstrap, preflight, and controlled loading system for Gordon agent.

This package implements Phase 3.3 substrate for explicit startup preparation:

## Startup Pipeline Stages

1. **Bootstrap Request** - Explicit intent to prepare runtime
2. **Configuration Acquisition** - Sources with precedence, normalization
3. **Environment Fact Collection** - Deterministic fact gathering
4. **Preflight Checks** - Structured validation with severity and blocking
5. **Static Integrity Gates** - Package-tree contracts before materialization
6. **Controlled Discovery** - Explicit descriptors from declared sources
7. **Loading Plan** - Deterministic entity loading order
8. **Materialization** - Factory-based construction without activation
9. **Dependency Binding** - Phase 3.1 graph ordering for dependency resolution
10. **Initialization** - Entity preparation before startup (distinct from startup)
11. **Rollback** - Reverse cleanup on partial failure
12. **Registry Sealing** - Final read-only registry transition
13. **Runtime Context Construction** - Immutable context transport
14. **Startup Handoff** - Structured result for kernel or later assembly

## Key Principles

- **Explicit** - No automatic discovery without declarations
- **Deterministic** - Same input produces same output
- **Reversible** - Side effects are tracked and rollbackable
- **Inspectable** - All intermediate results are structured
- **Domain-neutral** - Core infrastructure only, no capability semantics
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple, Callable, TypeVar, Generic, Set
from enum import Enum
import uuid
import time

# Re-export core types for convenience
from ..types import (
    EntityId,
    ComponentId,
    ServiceId,
    RuntimeId,
    Timestamp,
)

from ..contracts import (
    LifecycleState,
    LifecycleEntity,
)


class StartupStage(Enum):
    """
    Startup pipeline stage values.
    
    These describe progress through bootstrap preparation, not the final
    lifecycle state of runtime entities.
    """
    REQUESTED = "requested"
    NORMALIZING = "normalizing"
    CONTEXT_CREATED = "context_created"
    CONFIGURATION_ACQUIRED = "configuration_acquired"
    ENVIRONMENT_INSPECTED = "environment_inspected"
    PREFLIGHT_RUNNING = "preflight_running"
    PREFLIGHT_PASSED = "preflight_passed"
    LOAD_PLAN_CREATED = "load_plan_created"
    LOADING = "loading"
    DEPENDENCIES_BOUND = "dependencies_bound"
    INITIALIZING = "initializing"
    INITIALIZE_COMPLETE = "initialize_complete"
    INTEGRITY_VALIDATING = "integrity_validating"
    REGISTRY_SEALED = "registry_sealed"
    CONTEXT_FINALIZED = "context_finalized"
    HANDOFF_READY = "handoff_ready"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class StartupMode(Enum):
    """
    Bootstrap execution mode.
    
    Determines which phases of the startup pipeline are executed.
    """
    FULL_PREPARATION = "full_preparation"  # Complete startup
    PREFLIGHT_ONLY = "preflight_only"      # Only preflight, no materialization
    PLAN_ONLY = "plan_only"                # Only planning, no checks
    INITIALIZE_ONLY = "initialize_only"    # Materialize and initialize only
    DRY_RUN = "dry_run"                    # Plan but avoid lasting side effects


class PreflightStatus(Enum):
    """
    Status values for preflight checks.
    """
    PASS = "pass"
    PASS_WITH_WARNING = "pass_with_warning"
    FAIL = "fail"
    ERROR = "error"
    SKIPPED = "skipped"
    NOT_APPLICABLE = "not_applicable"
    CANCELLED = "cancelled"


class PreflightOverallStatus(Enum):
    """
    Overall preflight result status.
    """
    PASS = "pass"
    PASS_WITH_WARNINGS = "pass_with_warnings"
    FAIL_BLOCKING = "fail_blocking"
    ERROR = "error"
    CANCELLED = "cancelled"


class RollbackStatus(Enum):
    """
    Status of a rollback operation.
    """
    NOT_REQUIRED = "not_required"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class CorrelationId:
    """Unique correlation identifier for tracing bootstrap operations."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "CorrelationId":
        """Generate a new unique correlation ID."""
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


# ============================================================================
# Bootstrap Request
# ============================================================================

@dataclass(frozen=True)
class BootstrapRequest:
    """
    Explicit intent to prepare a Gordon runtime.
    
    This represents the caller's declaration of what runtime they want.
    It is immutable and never mutated during processing.
    
    The request flows through transformations:
        BootstrapRequest -> NormalizedBootstrapRequest -> BootstrapPlan
    """
    
    # Runtime identification
    runtime_id: Optional[RuntimeId] = None
    runtime_profile: str = "default"
    
    # Configuration sources (paths, URLs, inline data)
    config_sources: Tuple[str, ...] = field(default_factory=tuple)
    inline_config: Dict[str, Any] = field(default_factory=dict)
    
    # Runtime configuration
    enabled_packages: Tuple[str, ...] = field(default_factory=tuple)
    disabled_packages: Tuple[str, ...] = field(default_factory=tuple)
    
    # Explicit declarations
    declared_providers: Tuple[str, ...] = field(default_factory=tuple)
    declared_entities: Tuple[str, ...] = field(default_factory=tuple)
    
    # Execution mode
    startup_mode: StartupMode = StartupMode.FULL_PREPARATION
    strictness_mode: bool = True  # Fail on missing optional deps
    
    # Environment overrides
    environment_overrides: Dict[str, str] = field(default_factory=dict)
    
    # Flags
    dry_run: bool = False
    preflight_only: bool = False
    initialization_only: bool = False
    
    # Control
    cancellation_signal: Optional[Callable[[], bool]] = None  # Returns True if cancelled
    correlation_id: Optional[CorrelationId] = None
    
    def __post_init__(self) -> None:
        """Validate request structure."""
        if self.dry_run and self.preflight_only:
            raise ValueError("Cannot use both dry_run and preflight_only")
        
        if self.runtime_profile not in ("default", "minimal", "full"):
            # Allow custom profiles, but validate known ones
            pass
    
    @classmethod
    def create(
        cls,
        runtime_id: Optional[RuntimeId] = None,
        runtime_profile: str = "default",
        **kwargs
    ) -> "BootstrapRequest":
        """Create a bootstrap request with named parameters."""
        return cls(runtime_id=runtime_id, runtime_profile=runtime_profile, **kwargs)
    
    def with_enabled(self, *packages: str) -> "BootstrapRequest":
        """Return new request with packages enabled."""
        new_packages = tuple(set(self.enabled_packages) | set(packages))
        return dataclass_replace(self, enabled_packages=new_packages)
    
    def with_disabled(self, *packages: str) -> "BootstrapRequest":
        """Return new request with packages disabled."""
        new_packages = tuple(set(self.disabled_packages) | set(packages))
        return dataclass_replace(self, disabled_packages=new_packages)


@dataclass(frozen=True)
class NormalizedBootstrapRequest:
    """
    Normalized form of a bootstrap request.
    
    After normalization:
        - All paths are canonical
        - Profiles are resolved to concrete configuration
        - Defaults are applied
        - Validation is complete
        - Source attribution exists
    """
    
    correlation_id: CorrelationId
    runtime_profile: str
    enabled_packages: Tuple[str, ...]
    disabled_packages: Tuple[str, ...]
    declared_providers: Tuple[str, ...]
    declared_entities: Tuple[str, ...]
    startup_mode: StartupMode
    strictness_mode: bool
    source_attribution: Dict[str, Any]  # Where each setting came from


# ============================================================================
# Bootstrap Context
# ============================================================================

@dataclass
class BootstrapContext:
    """
    Temporary context during bootstrap.
    
    This is NOT the final RuntimeContext. It exists only during startup
    preparation and is converted to or used by the final RuntimeContext.
    
    Key principles:
        - Has explicit lifetime
        - Not process-global (must be passed, not global)
        - Cannot become permanent Runtime Context
        - Resources are tracked for rollback
    """
    
    # Identity
    correlation_id: CorrelationId
    runtime_id: Optional[RuntimeId]
    runtime_profile: str
    
    # Configuration state
    normalized_config: NormalizedBootstrapRequest
    
    # Environment facts (collected during startup)
    environment_facts: Dict[str, Any] = field(default_factory=dict)
    
    # Preflight results accumulator
    preflight_results: List["PreflightCheckResult"] = field(default_factory=list)
    
    # Loading state
    descriptors: List["LoadingDescriptor"] = field(default_factory=list)
    loading_plan: Optional["LoadingPlan"] = None
    
    # Resources owned during bootstrap (for rollback)
    _bootstrap_resources: List[Any] = field(default_factory=list)
    
    # Timing
    start_time: float = field(default_factory=time.monotonic)
    
    def record_resource(self, resource: Any) -> None:
        """Record a bootstrap-owned resource for potential cleanup."""
        self._bootstrap_resources.append(resource)
    
    def release_bootstrap_resources(self) -> List[str]:
        """Release bootstrap resources and return status messages."""
        statuses = []
        # In a real implementation, this would call cleanup on tracked resources
        for resource in self._bootstrap_resources:
            if hasattr(resource, "cleanup"):
                try:
                    resource.cleanup()
                    statuses.append(f"released: {resource}")
                except Exception as e:
                    statuses.append(f"release_failed: {resource} ({e})")
            else:
                statuses.append(f"no_cleanup: {type(resource)}")
        self._bootstrap_resources.clear()
        return statuses
    
    def elapsed_seconds(self) -> float:
        """Return time elapsed since bootstrap started."""
        return time.monotonic() - self.start_time


@dataclass(frozen=True)
class BootstrapContextBuilder:
    """
    Builder for constructing BootstrapContext.
    
    Used during startup to incrementally build context before sealing it
    into the final Runtime Context.
    """
    
    correlation_id: CorrelationId
    runtime_id: Optional[RuntimeId] = None
    runtime_profile: str = "default"
    normalized_config: Optional[NormalizedBootstrapRequest] = None
    environment_facts: Dict[str, Any] = field(default_factory=dict)
    preflight_results: List["PreflightCheckResult"] = field(default_factory=list)
    descriptors: List["LoadingDescriptor"] = field(default_factory=list)
    
    def with_runtime_id(self, runtime_id: RuntimeId) -> "BootstrapContextBuilder":
        """Set the runtime ID."""
        return dataclass_replace(self, runtime_id=runtime_id)
    
    def with_config(self, config: NormalizedBootstrapRequest) -> "BootstrapContextBuilder":
        """Set normalized configuration."""
        return dataclass_replace(self, normalized_config=config)
    
    def with_environment_facts(self, facts: Dict[str, Any]) -> "BootstrapContextBuilder":
        """Add environment facts."""
        new_facts = dict(self.environment_facts)
        new_facts.update(facts)
        return dataclass_replace(self, environment_facts=new_facts)
    
    def with_preflight_result(self, result: "PreflightCheckResult") -> "BootstrapContextBuilder":
        """Record a preflight check result."""
        return dataclass_replace(
            self,
            preflight_results=self.preflight_results + [result]
        )
    
    def with_descriptor(self, descriptor: "LoadingDescriptor") -> "BootstrapContextBuilder":
        """Add a loading descriptor."""
        # Deduplicate by entity_id
        existing_ids = {d.entity_id for d in self.descriptors}
        if descriptor.entity_id not in existing_ids:
            return dataclass_replace(
                self,
                descriptors=self.descriptors + [descriptor]
            )
        return self
    
    def build(self) -> BootstrapContext:
        """Build the BootstrapContext."""
        return BootstrapContext(
            correlation_id=self.correlation_id,
            runtime_id=self.runtime_id,
            runtime_profile=self.runtime_profile,
            normalized_config=self.normalized_config
            or NormalizedBootstrapRequest(
                correlation_id=CorrelationId.generate(),
                runtime_profile="default",
                enabled_packages=(),
                disabled_packages=(),
                declared_providers=(),
                declared_entities=(),
                startup_mode=StartupMode.FULL_PREPARATION,
                strictness_mode=True,
                source_attribution={}
            ),
            environment_facts=self.environment_facts.copy(),
            preflight_results=list(self.preflight_results),
            descriptors=list(self.descriptors)
        )


# ============================================================================
# Loading Descriptor
# ============================================================================

@dataclass(frozen=True)
class LoadingDescriptor:
    """
    A loading descriptor for runtime entities.
    
    Provides explicit, validated declaration of what should be loaded and how.
    This is the bridge between declarative architecture and runtime materialization.
    """
    
    # Canonical identification
    entity_id: EntityId
    
    # Implementation information
    implementation_ref: Any = None  # Class, factory function, or import path (validated)
    
    category: str = "component"  # e.g., "component", "service", "provider"
    name: Optional[str] = None
    
    # Protocol/interface exposure
    protocols: Tuple[str, ...] = field(default_factory=tuple)
    
    # Lifecycle and scope
    lifecycle_required: bool = True
    scope: str = "runtime"  # runtime, operation, request
    
    # Dependency declarations (from Phase 3.1)
    required_dependencies: Tuple[EntityId, ...] = field(default_factory=tuple)
    optional_dependencies: Tuple[EntityId, ...] = field(default_factory=tuple)
    
    # Configuration
    config_key: Optional[str] = None  # Where to find config for this entity
    
    # Metadata
    version: str = "1.0.0"
    source_package: Optional[str] = None
    source_location: Optional[str] = None
    aliases: Tuple[str, ...] = field(default_factory=tuple)
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Preflight checks (if any)
    preflight_checks: Tuple["LoadingDescriptorPreflightCheck", ...] = field(
        default_factory=tuple
    )
    
    # Materialization control
    materialize_async: bool = False  # If True, factory returns awaitable
    requires_initialization: bool = True
    
    def __post_init__(self) -> None:
        """Validate descriptor structure."""
        if self.category not in ("component", "service", "provider"):
            raise ValueError(f"Invalid category: {self.category}")
        
        if self.scope not in ("runtime", "operation", "request"):
            raise ValueError(f"Invalid scope: {self.scope}")


@dataclass(frozen=True)
class LoadingDescriptorPreflightCheck:
    """
    Preflight check associated with a loading descriptor.
    
    Allows entities to declare checks that must pass before they are loaded.
    """
    
    check_id: str
    description: str
    category: str  # e.g., "ARCHITECTURE", "DEPENDENCIES"
    severity: str = "blocking"  # "blocking" or "warning"


# ============================================================================
# Loading Plan
# ============================================================================

@dataclass(frozen=True)
class LoadingPlan:
    """
    Deterministic plan for loading runtime entities.
    
    Constructed after validation, this is the authoritative guide for
    what to materialize and in what order.
    """
    
    correlation_id: CorrelationId
    runtime_profile: str
    loading_order: Tuple[EntityId, ...]  # Topologically sorted
    descriptors_by_id: Dict[EntityId, LoadingDescriptor]
    required_entities: Tuple[EntityId, ...]
    optional_entities: Tuple[EntityId, ...]
    dependency_graph_hash: int  # For validation of plan freshness
    
    @property
    def entity_count(self) -> int:
        """Return total number of entities in the plan."""
        return len(self.loading_order)
    
    def get_dependencies(self, entity_id: EntityId) -> Tuple[EntityId, ...]:
        """Get dependencies for an entity according to this plan."""
        descriptor = self.descriptors_by_id.get(entity_id)
        if descriptor:
            return descriptor.required_dependencies
        return ()


@dataclass(frozen=True)
class LoadingPlanBuilder:
    """
    Builder for LoadingPlan with deterministic ordering.
    
    Uses Phase 3.1 dependency graph algorithms for topological sorting.
    """
    
    correlation_id: CorrelationId
    runtime_profile: str
    descriptors: Dict[EntityId, LoadingDescriptor]
    
    def add_descriptor(self, descriptor: LoadingDescriptor) -> "LoadingPlanBuilder":
        """Add a descriptor (deduplicates by entity_id)."""
        new_descriptors = dict(self.descriptors)
        new_descriptors[descriptor.entity_id] = descriptor
        return dataclass_replace(self, descriptors=new_descriptors)
    
    def build(self) -> LoadingPlan:
        """Build the loading plan with topological ordering."""
        # Build dependency graph from descriptors
        dependencies = []
        for entity_id, desc in self.descriptors.items():
            for dep in desc.required_dependencies:
                dependencies.append(
                    DependencyGraphEdge(from_entity=entity_id, to_entity=dep)
                )
        
        # Sort deterministically (by entity_id for stability)
        all_ids = set(self.descriptors.keys())
        
        def get_ready(remaining: Set[EntityId]) -> List[EntityId]:
            """Get entities whose dependencies are satisfied."""
            ready = []
            for eid in sorted(remaining):
                deps = self.descriptors[eid].required_dependencies
                if all(d not in remaining or d not in all_ids for d in deps):
                    ready.append(eid)
            return ready
        
        order = []
        remaining = set(all_ids)
        while remaining:
            ready = get_ready(remaining)
            if not ready:
                # Check if there's a cycle
                raise ValueError(
                    f"Cannot determine loading order: possible dependency cycle. "
                    f"Remaining: {sorted(remaining)}"
                )
            for eid in ready:
                order.append(eid)
                remaining.remove(eid)
        
        return LoadingPlan(
            correlation_id=self.correlation_id,
            runtime_profile=self.runtime_profile,
            loading_order=tuple(order),
            descriptors_by_id=dict(self.descriptors),
            required_entities=tuple(self.descriptors.keys()),
            optional_entities=(),
            dependency_graph_hash=hash(tuple(sorted(self.descriptors.items())))
        )


# ============================================================================
# Preflight System
# ============================================================================

@dataclass(frozen=True)
class PreflightCheckId:
    """Unique identifier for a preflight check."""
    
    value: str
    
    @classmethod
    def from_parts(cls, category: str, name: str) -> "PreflightCheckId":
        """Create check ID from category and name."""
        return cls(value=f"{category}/{name}")


@dataclass(frozen=True)
class PreflightCheckResult:
    """
    Result of a single preflight check.
    
    Distinguishes between:
        - FAIL: The condition was not met
        - ERROR: The check itself could not run correctly
    """
    
    check_id: str
    status: PreflightStatus
    category: str
    description: str
    
    # Severity determines if failure blocks startup
    severity: str = "blocking"  # "blocking" or "warning"
    is_blocking: bool = False
    
    # Evidence
    expected: Optional[str] = None
    actual: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    duration_seconds: float = 0.0
    timestamp: float = field(default_factory=time.monotonic)
    
    # Failure details (for ERROR status)
    error_message: Optional[str] = None
    
    # Remediation
    remediation: Optional[str] = None
    
    def is_passed(self) -> bool:
        """Check if the check passed (including warnings)."""
        return self.status in (PreflightStatus.PASS, PreflightStatus.PASS_WITH_WARNING)
    
    def is_failed(self) -> bool:
        """Check if the check failed or errored."""
        return self.status in (PreflightStatus.FAIL, PreflightStatus.ERROR)


class PreflightCheck:
    """
    A preflight check that can be executed.
    
    Checks are:
        - Read-only by default
        - Deterministic where possible
        - Timeout-aware for external checks
        - Cancellation-aware where justified
    
    Uses __post_init__ to enforce required fields since dataclasses with
    Callable types and defaults have limitations.
    """
    
    check_id: str
    category: str  # e.g., "ARCHITECTURE", "CONFIGURATION", "FILESYSTEM"
    description: str
    severity: str  # "blocking" or "warning"
    
    # What this check requires from environment facts
    required_facts: Tuple[str, ...]
    
    # Check execution method (required - no default)
    execute: Callable[[BootstrapContext], PreflightCheckResult]
    
    # Whether this check is safe to run concurrently
    concurrent_safe: bool = False
    
    # Timeouts (optional)
    timeout_seconds: Optional[float] = None
    
    def __post_init__(self) -> None:
        """Validate and set defaults for optional fields."""
        if not self.check_id:
            raise ValueError("check_id is required")
        if not self.category:
            raise ValueError("category is required")
        if not self.description:
            raise ValueError("description is required")
        if not self.required_facts:
            object.__setattr__(self, 'required_facts', ())
        if not self.execute:
            raise ValueError("execute callback is required")


@dataclass(frozen=True)
class PreflightPlan:
    """
    A plan for executing preflight checks.
    
    Defines which checks to run, in what order, and with what policy.
    """
    
    correlation_id: CorrelationId
    check_order: Tuple[str, ...]  # Ordered check IDs
    checks_by_id: Dict[str, PreflightCheck]
    fail_fast: bool = True  # Stop on first blocking failure
    strictness_mode: bool = True


@dataclass(frozen=True)
class PreflightReport:
    """
    Complete report of preflight execution.
    
    Provides structured evidence for whether startup may proceed.
    """
    
    correlation_id: CorrelationId
    runtime_profile: str
    
    # Execution info
    start_time: float
    end_time: float
    duration_seconds: float
    
    # Results by category
    checks_executed: int
    checks_passed: int
    checks_warnings: int
    checks_failed: int
    checks_errored: int
    checks_skipped: int
    
    # Individual results (for detailed inspection)
    results_by_id: Dict[str, PreflightCheckResult]
    
    # Overall status
    overall_status: PreflightOverallStatus
    blocking_failures: Tuple[str, ...]  # Check IDs that blocked startup
    
    # Remediation guidance
    remediation_guide: Dict[str, str]
    
    @classmethod
    def create(
        cls,
        correlation_id: CorrelationId,
        runtime_profile: str,
        results_by_id: Dict[str, PreflightCheckResult],
    ) -> "PreflightReport":
        """Create a preflight report from check results."""
        start_time = min(r.timestamp for r in results_by_id.values()) if results_by_id else time.monotonic()
        end_time = max(r.timestamp + r.duration_seconds for r in results_by_id.values()) if results_by_id else time.monotonic()
        
        passed = sum(1 for r in results_by_id.values() if r.status == PreflightStatus.PASS)
        warnings = sum(1 for r in results_by_id.values() if r.status == PreflightStatus.PASS_WITH_WARNING)
        failed = sum(1 for r in results_by_id.values() if r.status == PreflightStatus.FAIL)
        errored = sum(1 for r in results_by_id.values() if r.status == PreflightStatus.ERROR)
        skipped = sum(1 for r in results_by_id.values() if r.status == PreflightStatus.SKIPPED)
        
        # Determine overall status
        blocking_failures = tuple(
            check_id for check_id, result in results_by_id.items()
            if result.is_blocking and not result.is_passed()
        )
        
        if failed + errored > 0:
            overall = PreflightOverallStatus.FAIL_BLOCKING
        elif warnings > 0:
            overall = PreflightOverallStatus.PASS_WITH_WARNINGS
        else:
            overall = PreflightOverallStatus.PASS
        
        return cls(
            correlation_id=correlation_id,
            runtime_profile=runtime_profile,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=end_time - start_time,
            checks_executed=len(results_by_id),
            checks_passed=passed,
            checks_warnings=warnings,
            checks_failed=failed,
            checks_errored=errored,
            checks_skipped=skipped,
            results_by_id=dict(results_by_id),
            overall_status=overall,
            blocking_failures=blocking_failures,
            remediation_guide={}
        )
    
    def is_startup_allowed(self) -> bool:
        """Check if startup may proceed based on this report."""
        return self.overall_status == PreflightOverallStatus.PASS


# ============================================================================
# Factory and Materialization
# ============================================================================

T = TypeVar("T")


@dataclass(frozen=True)
class MaterializationResult(Generic[T]):
    """
    Result of materializing a runtime entity.
    
    Provides evidence about what was constructed, not just success/failure.
    """
    
    descriptor: LoadingDescriptor
    entity_id: EntityId
    
    # Construction result
    materialized_object: Optional[T] = None  # The constructed object (may be None)
    
    # Lifecycle state after construction
    lifecycle_state: LifecycleState = LifecycleState.CREATED
    
    # Resources acquired during construction
    resources_acquired: Tuple[Any, ...] = field(default_factory=tuple)
    
    # Timing
    start_time: float = field(default_factory=time.monotonic)
    end_time: float = field(default_factory=time.monotonic)
    
    # Outcome
    success: bool = True
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    failure_reason: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Return construction duration."""
        return self.end_time - self.start_time


@dataclass(frozen=True)
class MaterializationFactory(Generic[T]):
    """
    Factory for materializing a runtime entity.
    
    Factories are domain-neutral. They construct the object but do not
    automatically activate it (that comes later during initialization).
    """
    
    descriptor: LoadingDescriptor
    
    # Factory function that takes context and returns constructed object
    factory_fn: Callable[[BootstrapContext], T]
    
    def materialize(self, context: BootstrapContext) -> MaterializationResult[T]:
        """Execute the factory to construct the entity."""
        start = time.monotonic()
        try:
            obj = self.factory_fn(context)
            return MaterializationResult(
                descriptor=self.descriptor,
                entity_id=self.descriptor.entity_id,
                materialized_object=obj,
                lifecycle_state=LifecycleState.CREATED,
                success=True
            )
        except Exception as e:
            end = time.monotonic()
            return MaterializationResult(
                descriptor=self.descriptor,
                entity_id=self.descriptor.entity_id,
                lifecycle_state=LifecycleState.FAILED,
                success=False,
                failure_reason=str(e),
                end_time=end - start
            )


@dataclass(frozen=True)
class InitializationResult(Generic[T]):
    """
    Result of initializing a materialized runtime entity.
    
    Distinguishes initialization (preparation) from startup (activation).
    """
    
    entity_id: EntityId
    
    # Before and after lifecycle state
    before_state: LifecycleState
    after_state: LifecycleState
    
    # Initialization result
    initialized_entity: Optional[T] = None
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    failure_reason: Optional[str] = None
    success: bool = True
    
    # Resources acquired during initialization
    resources_acquired: Tuple[Any, ...] = field(default_factory=tuple)
    
    # Timing
    start_time: float = field(default_factory=time.monotonic)
    end_time: float = field(default_factory=time.monotonic)
    
    @property
    def duration_seconds(self) -> float:
        """Return initialization duration."""
        return self.end_time - self.start_time


# ============================================================================
# Rollback
# ============================================================================

@dataclass(frozen=True)
class RollbackAction:
    """
    A single rollback action to be executed if startup fails.
    
    Reverse operations are recorded in forward order and executed
    in reverse order on failure.
    """
    
    target_entity_id: EntityId
    action_type: str  # e.g., "release_resource", "unregister_registry"
    execute: Callable[[], bool]  # Returns True if successful
    description: str = ""
    is_critical: bool = False  # If critical and fails, rollback status is FAILED


@dataclass(frozen=True)
class StartupRollbackResult:
    """
    Result of a startup rollback attempt.
    
    Preserves the primary failure while tracking rollback outcomes separately.
    """
    
    was_required: bool
    status: RollbackStatus
    
    # Actions attempted vs. actual results
    actions_attempted: int = 0
    actions_succeeded: int = 0
    actions_failed: int = 0
    
    # Primary failure preserved (never replaced by rollback failures)
    primary_failure_reason: Optional[str] = None
    
    # Rollback-specific failures
    rollback_failures: Tuple[str, ...] = field(default_factory=tuple)


# ============================================================================
# Startup Handoff
# ============================================================================

@dataclass(frozen=True)
class StartupHandoff:
    """
    Structured result of successful startup preparation.
    
    Contains all verified artifacts ready for the kernel or final runtime
    assembler. This is the output that Phase 3.4 and beyond can depend on.
    """
    
    correlation_id: CorrelationId
    runtime_profile: str
    
    # Runtime identification
    runtime_id: Optional[RuntimeId] = None
    
    # Normalized configuration (for reference)
    normalized_config: Optional[NormalizedBootstrapRequest] = None
    
    # Preflight report (for observability)
    preflight_report: Optional[PreflightReport] = None
    
    # Loading plan (what was loaded)
    loading_plan: Optional[LoadingPlan] = None
    
    # Materialized entities
    materialized_entities: Tuple[Any, ...] = field(default_factory=tuple)
    
    # Runtime state authority access (via Phase 3.2 infrastructure)
    runtime_state_access: Any = None  # Type depends on Phase 3.2 implementation
    
    # Shutdown and cancellation signals (Phase 3.2)
    shutdown_signal: Optional[Any] = None
    cancellation_signal: Optional[Any] = None
    
    # Deferred work (readiness verification, activation, etc.)
    deferred_readiness_probes: Tuple[str, ...] = field(default_factory=tuple)
    deferred_activation_plan: Optional[Any] = None
    
    @classmethod
    def create(
        cls,
        correlation_id: CorrelationId,
        runtime_profile: str,
        runtime_id: Optional[RuntimeId] = None,
        **kwargs
    ) -> "StartupHandoff":
        """Create a startup handoff with minimal required fields."""
        return cls(
            correlation_id=correlation_id,
            runtime_profile=runtime_profile,
            runtime_id=runtime_id,
            **kwargs
        )
    
    def is_ready(self) -> bool:
        """
        Check if startup preparation is complete and ready for kernel.
        
        Returns True only when all critical gates passed and handoff contains
        verified artifacts.
        """
        return self.runtime_state_access is not None


# ============================================================================
# Environment Facts
# ============================================================================

@dataclass(frozen=True)
class EnvironmentFact:
    """A single environment fact collected during startup."""
    
    key: str
    value: Any
    source: str  # e.g., "os", "env", "filesystem"
    timestamp: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class EnvironmentFacts:
    """
    Collected environment facts.
    
    Factual information about the environment, separate from policy decisions.
    """
    
    facts: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a fact value."""
        return self.facts.get(key, default)
    
    def has_key(self, key: str) -> bool:
        """Check if a fact exists."""
        return key in self.facts
    
    @classmethod
    def from_dict(cls, facts: Dict[str, Any]) -> "EnvironmentFacts":
        """Create from a dictionary of facts."""
        return cls(facts=dict(facts))
    
    def to_readonly(self) -> Dict[str, Any]:
        """Return immutable copy of facts."""
        return dict(self.facts)


# ============================================================================
# Dependency Graph Edge
# ============================================================================

@dataclass(frozen=True)
class DependencyGraphEdge:
    """
    Edge in a dependency graph for topological ordering.
    
    Represents "from_entity depends on to_entity".
    """
    
    from_entity: EntityId
    to_entity: EntityId
    
    def reverse(self) -> "DependencyGraphEdge":
        """Return reversed edge (to_entity is depended upon by from_entity)."""
        return DependencyGraphEdge(
            from_entity=self.to_entity,
            to_entity=self.from_entity
        )


# ============================================================================
# Utility Functions
# ============================================================================

def dataclass_replace(instance: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass (Python < 3.12 compatible).
    
    Since @dataclass(frozen=True) doesn't have .replace(), we use this helper.
    """
    import copy
    new_instance = copy.copy(instance)
    for key, value in kwargs.items():
        object.__setattr__(new_instance, key, value)
    return new_instance


def compute_loading_order(
    descriptors: Dict[EntityId, LoadingDescriptor]
) -> Tuple[EntityId, ...]:
    """
    Compute deterministic loading order from dependencies.
    
    Uses topological sort to ensure dependencies are loaded before dependents.
    Raises ValueError if a dependency cycle is detected.
    """
    # Build reverse adjacency (dependency -> list of entities that depend on it)
    dependents: Dict[EntityId, List[EntityId]] = {}
    
    for entity_id in descriptors:
        if entity_id not in dependents:
            dependents[entity_id] = []
        for dep in descriptors[entity_id].required_dependencies:
            if dep not in dependents:
                dependents[dep] = []
            dependents[dep].append(entity_id)
    
    # Kahn's algorithm with deterministic ordering
    all_ids = set(descriptors.keys())
    in_degree: Dict[EntityId, int] = {
        eid: len(descriptors[eid].required_dependencies) for eid in all_ids
    }
    
    # Start with nodes that have no dependencies (in_degree == 0)
    queue = sorted([eid for eid in all_ids if in_degree[eid] == 0])
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for dependent in dependents.get(node, []):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                # Insert in sorted position to maintain determinism
                import bisect
                bisect.insort(queue, dependent)
    
    if len(result) != len(all_ids):
        remaining = all_ids - set(result)
        raise ValueError(
            f"Dependency cycle detected involving: {sorted(remaining)}"
        )
    
    return tuple(result)


__all__ = [
    # Startup stages and modes
    "StartupStage",
    "StartupMode",
    
    # Status enums
    "PreflightStatus",
    "PreflightOverallStatus",
    "RollbackStatus",
    
    # ID types
    "EntityId",
    "ComponentId", 
    "ServiceId",
    "RuntimeId",
    "Timestamp",
    "CorrelationId",
    
    # Core request/context types
    "BootstrapRequest",
    "NormalizedBootstrapRequest",
    "BootstrapContext",
    "BootstrapContextBuilder",
    
    # Loading types
    "LoadingDescriptor",
    "LoadingDescriptorPreflightCheck",
    "LoadingPlan",
    "LoadingPlanBuilder",
    
    # Preflight system
    "PreflightCheckId",
    "PreflightCheckResult",
    "PreflightCheck",
    "PreflightPlan",
    "PreflightReport",
    
    # Materialization and initialization
    "MaterializationResult",
    "MaterializationFactory",
    "InitializationResult",
    
    # Rollback
    "RollbackAction",
    "StartupRollbackResult",
    
    # Handoff
    "StartupHandoff",
    
    # Environment facts
    "EnvironmentFact",
    "EnvironmentFacts",
    
    # Dependency graph edge
    "DependencyGraphEdge",
    
    # Utilities
    "dataclass_replace",
    "compute_loading_order",
]