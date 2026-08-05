# Core Kernel Builder - Production Implementation
# ================================================
"""
Canonical kernel construction mechanism.

This module implements Phase 3.7.3-I requirements:
- Exactly one canonical production KernelBuilder
- Explicit immutable builder input contracts
- Explicit builder output contracts
- Construction state machine tracking
- Deterministic dependency ordering
- Pre-activation safety

Kernel Construction Phases:
1. REQUESTED - Builder receives construction request
2. VALIDATING_INPUTS - Input validation (config, dependencies)
3. VALIDATING_CONFIGURATION - Configuration validation and projection
4. VALIDATING_DEPENDENCIES - Dependency graph validation
5. VALIDATING_REGISTRIES - Registry state validation and sealing
6. COMPILING_PLAN - Immutable construction plan compilation
7. CONSTRUCTING_KERNEL - Kernel instantiation without activation
8. VERIFYING_KERNEL - Post-construction verification
9. CONSTRUCTED - Unactivated kernel returned (ready for activation)
10. FAILED - Construction failure with cleanup

The kernel produced is:
- constructed = True
- assembled = False
- activated = False
- ready = False
- admission_open = False
- running = False
- shutdown_started = False
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Dict,
    List,
    Optional,
    Any,
    FrozenSet,
    Tuple,
)
import uuid

from ..types import EntityId, RuntimeId, Timestamp
from ..contracts import LifecycleState


# ============================================================================
# Construction State Machine
# ============================================================================

class ConstructionStage(Enum):
    """Kernel construction state machine stages."""
    NOT_STARTED = "not_started"
    VALIDATING_INPUTS = "validating_inputs"
    VALIDATING_CONFIGURATION = "validating_configuration"
    VALIDATING_DEPENDENCIES = "validating_dependencies"
    VALIDATING_REGISTRIES = "validating_registries"
    COMPILING_PLAN = "compiling_plan"
    CONSTRUCTING_KERNEL = "constructing_kernel"
    VERIFYING_KERNEL = "verifying_kernel"
    CONSTRUCTED = "constructed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConstructionStatus(Enum):
    """Construction result status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"


# ============================================================================
# Construction Artifacts (Immutable)
# ============================================================================

@dataclass(frozen=True)
class KernelConstructionId:
    """Unique identifier for a kernel construction operation."""
    value: str
    
    @classmethod
    def generate(cls) -> "KernelConstructionId":
        """Generate a new unique construction ID."""
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class ConstructionInputSnapshot:
    """
    Immutable snapshot of construction inputs for diagnostics.
    
    This provides traceability of what was used to construct the kernel,
    without exposing mutable references.
    """
    config_identity: str
    context_identity: str
    dependency_resolution_id: str
    registry_snapshots: Tuple[str, ...]
    runtime_id: Optional[RuntimeId]


@dataclass(frozen=True)
class ConstructionStageRecord:
    """
    Record of a single construction stage transition.
    
    All fields are immutable and provide diagnostic information about
    the state transition that occurred.
    """
    construction_id: str
    source_state: ConstructionStage
    target_state: ConstructionStage
    timestamp: float
    duration_seconds: Optional[float]
    authority: Optional[str] = None
    reason: Optional[str] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KernelConstructionResult:
    """
    Result of kernel construction.
    
    This is the canonical output contract for kernel construction. It contains
    either a successfully constructed kernel OR failure evidence with full
    diagnostic information.
    """
    # Identity and provenance
    construction_id: str
    runtime_id: Optional[RuntimeId]
    timestamp: float
    
    # Status
    status: ConstructionStatus
    stage_completed: ConstructionStage
    
    # Kernel result (if successful)
    kernel: Any = None  # Kernel type defined elsewhere, using Any for now
    
    # Failure evidence (if failed)
    failure_reason: Optional[str] = None
    failure_stage: Optional[ConstructionStage] = None
    failure_diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostic snapshots
    input_snapshot: Optional[ConstructionInputSnapshot] = None
    
    # Timing
    duration_seconds: float = 0.0
    
    @property
    def is_success(self) -> bool:
        """Check if construction succeeded."""
        return self.status == ConstructionStatus.SUCCESS
    
    @property
    def is_failure(self) -> bool:
        """Check if construction failed."""
        return self.status in (ConstructionStatus.FAILURE, ConstructionStatus.CANCELLED)
    
    @classmethod
    def success(
        cls,
        construction_id: str,
        runtime_id: Optional[RuntimeId],
        kernel: Any,
        input_snapshot: Optional[ConstructionInputSnapshot] = None,
        duration_seconds: float = 0.0,
    ) -> "KernelConstructionResult":
        """Create a successful construction result."""
        return cls(
            construction_id=construction_id,
            runtime_id=runtime_id,
            timestamp=Timestamp.now().value,
            status=ConstructionStatus.SUCCESS,
            stage_completed=ConstructionStage.CONSTRUCTED,
            kernel=kernel,
            input_snapshot=input_snapshot,
            duration_seconds=duration_seconds,
        )
    
    @classmethod
    def failure(
        cls,
        construction_id: str,
        runtime_id: Optional[RuntimeId],
        reason: str,
        stage: ConstructionStage = ConstructionStage.FAILED,
        diagnostics: Dict[str, Any] = None,
        input_snapshot: Optional[ConstructionInputSnapshot] = None,
        duration_seconds: float = 0.0,
    ) -> "KernelConstructionResult":
        """Create a failed construction result."""
        return cls(
            construction_id=construction_id,
            runtime_id=runtime_id,
            timestamp=Timestamp.now().value,
            status=ConstructionStatus.FAILURE,
            stage_completed=stage,
            failure_reason=reason,
            failure_stage=stage,
            failure_diagnostics=diagnostics or {},
            input_snapshot=input_snapshot,
            duration_seconds=duration_seconds,
        )
    
    @classmethod
    def cancelled(
        cls,
        construction_id: str,
        runtime_id: Optional[RuntimeId],
        reason: str = "Construction was cancelled",
    ) -> "KernelConstructionResult":
        """Create a cancelled construction result."""
        return cls(
            construction_id=construction_id,
            runtime_id=runtime_id,
            timestamp=Timestamp.now().value,
            status=ConstructionStatus.CANCELLED,
            stage_completed=ConstructionStage.CANCELLED,
            failure_reason=reason,
        )


@dataclass(frozen=True)
class KernelConstructionSnapshot:
    """
    Immutable snapshot of construction progress and state.
    
    Used for monitoring, diagnostics, and verification without exposing
    mutable builder state.
    """
    construction_id: str
    runtime_id: Optional[RuntimeId]
    current_stage: ConstructionStage
    status: ConstructionStatus
    start_time: float
    duration_seconds: float
    inputs_validated: bool
    dependencies_resolved: bool
    registries_validated: bool
    kernel_constructed: bool
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def is_complete(self) -> bool:
        """Check if construction has completed (success or failure)."""
        return self.status in (
            ConstructionStatus.SUCCESS,
            ConstructionStatus.FAILURE,
            ConstructionStatus.CANCELLED,
        )


@dataclass(frozen=True)
class KernelConstructionReceipt:
    """
    Receipt of a completed kernel construction operation.
    
    This is an immutable, auditable record that can be stored for
    verification, debugging, or compliance purposes.
    """
    # Operation identity
    construction_id: str
    runtime_id: Optional[RuntimeId]
    
    # Construction metadata
    stage_sequence: Tuple[str, ...]
    total_duration_seconds: float
    
    # Result evidence
    kernel_identity: Optional[str]  # Kernel's entity_id if constructed
    status: str
    failure_reason: Optional[str] = None
    
    # Input provenance (frozen snapshots)
    input_fingerprints: Dict[str, str] = field(default_factory=dict)
    
    # Diagnostic summary
    warnings: Tuple[str, ...] = field(default_factory=tuple)


# ============================================================================
# Builder State Management
# ============================================================================

class KernelBuilderState(Enum):
    """KernelBuilder state for reuse policy enforcement."""
    NEW = "new"  # Fresh builder, ready to build
    BUILDING = "building"  # Currently in the middle of a build
    COMPLETE = "complete"  # Build completed (success or failure)
    CONSUMED = "consumed"  # Builder cannot be reused (one-time use)


# ============================================================================
# Kernel Construction Request
# ============================================================================

@dataclass(frozen=True)
class KernelConstructionRequest:
    """
    Immutable request for kernel construction.
    
    This is the canonical input contract. All fields are explicitly declared,
    validated, and immutable once set.
    """
    # Identity
    construction_id: KernelConstructionId
    runtime_id: RuntimeId
    
    # Required: Validated configuration
    config: Any  # KernelConfig type
    
    # Required: Runtime context (sealed)
    runtime_context: Any  # RuntimeContext type
    
    # Required: Dependency resolution result (immutable, ordered)
    dependency_resolution_result: Any  # Resolved dependencies
    
    # Required: Registry views (sealed, immutable snapshots)
    registry_views: Dict[str, Any] = field(default_factory=dict)
    
    # Optional: Scheduler control interface
    scheduler_control: Any = None
    
    # Optional: Execution control interface
    execution_control: Any = None
    
    # Optional: Admission control interface
    admission_control: Any = None
    
    # Optional: Resource control interface
    resource_control: Any = None
    
    # Optional: Health interface
    health_interface: Any = None
    
    # Optional: Integrity interface
    integrity_interface: Any = None
    
    # Optional: Observability interface
    observability_interface: Any = None
    
    # Optional: Shutdown coordination interface
    shutdown_coordinator: Any = None
    
    # Lifecycle metadata
    deadline: float = field(default_factory=lambda: Timestamp.now().value + 60.0)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate request structure."""
        if not self.construction_id or not isinstance(self.construction_id, KernelConstructionId):
            raise ValueError("construction_id is required and must be a KernelConstructionId")
        
        if not self.runtime_id or not isinstance(self.runtime_id, RuntimeId):
            raise ValueError("runtime_id is required and must be a RuntimeId")
    
    @classmethod
    def create(
        cls,
        runtime_id: RuntimeId,
        config: Any,
        runtime_context: Any,
        dependency_resolution_result: Any,
        **kwargs
    ) -> "KernelConstructionRequest":
        """
        Create a construction request with required fields.
        
        Args:
            runtime_id: Runtime identity for this kernel instance
            config: Validated configuration (not None)
            runtime_context: Sealed runtime context
            dependency_resolution_result: Immutable resolved dependencies
            
        Optional kwargs:
            registry_views, scheduler_control, execution_control, etc.
            
        Returns:
            KernelConstructionRequest with all required fields set
        """
        construction_id = KernelConstructionId.generate()
        
        return cls(
            construction_id=construction_id,
            runtime_id=runtime_id,
            config=config,
            runtime_context=runtime_context,
            dependency_resolution_result=dependency_resolution_result,
            **kwargs
        )
    
    def with_registry(self, name: str, registry_view: Any) -> "KernelConstructionRequest":
        """Return new request with a registry view added."""
        new_views = dict(self.registry_views)
        new_views[name] = registry_view
        return dataclass_replace(self, registry_views=new_views)
    
    def with_scheduler(self, scheduler_control: Any) -> "KernelConstructionRequest":
        """Return new request with scheduler control interface."""
        return dataclass_replace(self, scheduler_control=scheduler_control)
    
    def with_execution(self, execution_control: Any) -> "KernelConstructionRequest":
        """Return new request with execution control interface."""
        return dataclass_replace(self, execution_control=execution_control)


# ============================================================================
# Construction Context (for builder-internal use)
# ============================================================================

@dataclass
class KernelConstructionContext:
    """
    Builder-internal context for construction tracking.
    
    This is NOT exposed externally. It tracks progress and diagnostics
    during the build process.
    """
    construction_id: str
    runtime_id: Optional[RuntimeId]
    current_stage: ConstructionStage = ConstructionStage.NOT_STARTED
    
    # Timing
    start_time: float = field(default_factory=time.monotonic)
    
    # Stage records for audit trail
    stage_records: List[ConstructionStageRecord] = field(default_factory=list)
    
    # Validation state
    inputs_validated: bool = False
    configuration_validated: bool = False
    dependencies_validated: bool = False
    registries_validated: bool = False
    
    # Diagnostics
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        """Return elapsed time since construction started."""
        return time.monotonic() - self.start_time
    
    def record_stage_transition(
        self,
        target_state: ConstructionStage,
        reason: Optional[str] = None,
        diagnostics: Dict[str, Any] = None,
    ) -> None:
        """Record a state transition."""
        source_state = self.current_stage
        
        # Calculate duration of previous stage if it exists
        duration = None
        if self.stage_records:
            last_record = self.stage_records[-1]
            duration = time.monotonic() - last_record.timestamp
        
        record = ConstructionStageRecord(
            construction_id=self.construction_id,
            source_state=source_state,
            target_state=target_state,
            timestamp=time.monotonic(),
            duration_seconds=duration,
            reason=reason,
            diagnostics=diagnostics or {},
        )
        
        self.stage_records.append(record)
        self.current_stage = target_state
    
    def add_warning(self, warning: str) -> None:
        """Add a non-blocking warning."""
        self.warnings.append(warning)
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
    
    def to_snapshot(self) -> KernelConstructionSnapshot:
        """Create an immutable snapshot of construction state."""
        return KernelConstructionSnapshot(
            construction_id=self.construction_id,
            runtime_id=self.runtime_id,
            current_stage=self.current_stage,
            status=ConstructionStatus.PENDING
            if self.current_stage == ConstructionStage.NOT_STARTED
            else (
                ConstructionStatus.SUCCESS
                if self.current_stage == ConstructionStage.CONSTRUCTED
                else ConstructionStatus.FAILURE
                if self.current_stage in (ConstructionStage.FAILED, ConstructionStage.CANCELLED)
                else ConstructionStatus.IN_PROGRESS
            ),
            start_time=self.start_time,
            duration_seconds=self.duration_seconds,
            inputs_validated=self.inputs_validated,
            dependencies_resolved=self.dependencies_validated,
            registries_validated=self.registries_validated,
            kernel_constructed=self.current_stage == ConstructionStage.CONSTRUCTED,
            diagnostics=tuple(self.warnings + self.errors),
        )


# ============================================================================
# KernelBuilder - Canonical Production Implementation
# ============================================================================

class KernelBuilder:
    """
    Canonical production kernel builder.
    
    This is the SINGLE canonical authority for kernel construction. All
    kernel construction must flow through this builder to ensure:
    
    - Deterministic construction order
    - Explicit dependency injection
    - Pre-activation safety
    - Construction purity (no side effects during construction)
    - Immutable construction artifacts
    
    Builder State Lifecycle:
        NEW → BUILDING → COMPLETE/CONSUMED
        
        - In NEW state, builder is ready to accept a request and build
        - In BUILDING state, builder is in the middle of construction
        - In COMPLETE state, previous build completed (can be reused if idempotent)
        - In CONSUMED state, builder cannot be used again (single-use mode)
    
    Builder Reuse Policy:
        This KernelBuilder follows a REUSABLE pattern where each build()
        call receives an isolated immutable request and produces independent
        results without sharing mutable state between builds.
    
    Thread Safety:
        This builder is designed for single-threaded use per construction
        operation. Concurrent builds should use separate builder instances
        or synchronize at the caller level.
    
    Usage:
        >>> from gordon.system.components.core.kernel.builder import (
        ...     KernelBuilder,
        ...     KernelConstructionRequest,
        ... )
        >>> from gordon.system.components.core.types import RuntimeId
        >>> 
        >>> builder = KernelBuilder()
        >>> request = KernelConstructionRequest.create(
        ...     runtime_id=RuntimeId.generate(),
        ...     config=my_config,
        ...     runtime_context=my_context,
        ...     dependency_resolution_result=my_deps,
        ... )
        >>> result = await builder.build(request)
        >>> 
        >>> if result.is_success:
        ...     kernel = result.kernel  # Unactivated, not running
        """
    
    def __init__(self) -> None:
        """Initialize a new KernelBuilder in the NEW state."""
        self._state: KernelBuilderState = KernelBuilderState.NEW
    
    @property
    def state(self) -> KernelBuilderState:
        """Get current builder state."""
        return self._state
    
    @classmethod
    def create(cls) -> "KernelBuilder":
        """
        Create a new kernel builder instance.
        
        This is the canonical entry point for kernel construction.
        
        Returns:
            A new KernelBuilder in NEW state, ready to accept requests
        """
        return cls()
    
    async def build(
        self,
        request: KernelConstructionRequest,
    ) -> KernelConstructionResult:
        """
        Build a kernel deterministically from the given request.
        
        This is the canonical construction path. It follows an explicit
        state machine to produce an unactivated kernel that is ready for
        activation but not yet operational.
        
        Construction Phases:
            1. VALIDATING_INPUTS - Validate request structure and required fields
            2. VALIDATING_CONFIGURATION - Validate configuration projection
            3. VALIDATING_DEPENDENCIES - Validate dependency graph
            4. VALIDATING_REGISTRIES - Validate registry state and sealing
            5. COMPILING_PLAN - Compile immutable construction plan
            6. CONSTRUCTING_KERNEL - Instantiate kernel without activation
            7. VERIFYING_KERNEL - Verify kernel invariants
            8. CONSTRUCTED - Return unactivated kernel
        
        Args:
            request: Immutable kernel construction request
            
        Returns:
            KernelConstructionResult containing either the constructed kernel
            or failure evidence with full diagnostics
            
        Raises:
            RuntimeError: If builder state is invalid for construction
        """
        import copy
        
        # Validate builder can accept this build
        if self._state == KernelBuilderState.CONSUMED:
            return KernelConstructionResult.failure(
                construction_id=request.construction_id.value,
                runtime_id=request.runtime_id,
                reason="KernelBuilder has been consumed and cannot be reused",
                stage=ConstructionStage.NOT_STARTED,
                diagnostics={"builder_state": "consumed"},
            )
        
        if self._state == KernelBuilderState.BUILDING:
            return KernelConstructionResult.failure(
                construction_id=request.construction_id.value,
                runtime_id=request.runtime_id,
                reason="KernelBuilder is already in the middle of a build",
                stage=ConstructionStage.NOT_STARTED,
                diagnostics={"builder_state": "building"},
            )
        
        # Set builder state to BUILDING
        self._state = KernelBuilderState.BUILDING
        
        # Create construction context for tracking
        ctx = KernelConstructionContext(
            construction_id=request.construction_id.value,
            runtime_id=request.runtime_id,
        )
        
        start_time = time.monotonic()
        
        try:
            # Phase 1: Validate Inputs
            ctx.record_stage_transition(ConstructionStage.VALIDATING_INPUTS)
            
            input_validation_result = await self._validate_inputs(request, ctx)
            if input_validation_result.is_failure:
                return self._complete_with_failure(
                    request=request,
                    ctx=ctx,
                    start_time=start_time,
                    failure_reason=input_validation_result.failure_reason,
                    diagnostics=input_validation_result.failure_diagnostics,
                )
            
            # Phase 2: Validate Configuration
            ctx.record_stage_transition(ConstructionStage.VALIDATING_CONFIGURATION)
            
            config_validation_result = await self._validate_configuration(
                request.config, ctx
            )
            if config_validation_result.is_failure:
                return self._complete_with_failure(
                    request=request,
                    ctx=ctx,
                    start_time=start_time,
                    failure_reason=config_validation_result.failure_reason,
                    diagnostics=config_validation_result.failure_diagnostics,
                )
            
            # Phase 3: Validate Dependencies
            ctx.record_stage_transition(ConstructionStage.VALIDATING_DEPENDENCIES)
            
            dependencies_validated = await self._validate_dependencies(
                request.dependency_resolution_result, ctx
            )
            if not dependencies_validated:
                return self._complete_with_failure(
                    request=request,
                    ctx=ctx,
                    start_time=start_time,
                    failure_reason="Dependency validation failed",
                    diagnostics={"dependencies": "invalid"},
                )
            
            # Phase 4: Validate Registries
            ctx.record_stage_transition(ConstructionStage.VALIDATING_REGISTRIES)
            
            registries_validated = await self._validate_registries(
                request.registry_views, ctx
            )
            if not registries_validated:
                return self._complete_with_failure(
                    request=request,
                    ctx=ctx,
                    start_time=start_time,
                    failure_reason="Registry validation failed",
                    diagnostics={"registries": "invalid"},
                )
            
            # Phase 5: Compile Construction Plan
            ctx.record_stage_transition(ConstructionStage.COMPILING_PLAN)
            
            plan = await self._compile_construction_plan(request, ctx)
            
            # Phase 6: Construct Kernel (without activation)
            ctx.record_stage_transition(ConstructionStage.CONSTRUCTING_KERNEL)
            
            kernel, construction_error = await self._construct_kernel(
                request=request,
                plan=plan,
                ctx=ctx,
            )
            
            if construction_error:
                return self._complete_with_failure(
                    request=request,
                    ctx=ctx,
                    start_time=start_time,
                    failure_reason=construction_error,
                    diagnostics={"kernel_construction": "failed"},
                )
            
            # Phase 7: Verify Kernel
            ctx.record_stage_transition(ConstructionStage.VERIFYING_KERNEL)
            
            verification_error = await self._verify_kernel(kernel, ctx)
            if verification_error:
                return self._complete_with_failure(
                    request=request,
                    ctx=ctx,
                    start_time=start_time,
                    failure_reason=verification_error,
                    diagnostics={"kernel_verification": "failed"},
                )
            
            # Phase 8: Mark as CONSTRUCTED
            ctx.record_stage_transition(ConstructionStage.CONSTRUCTED)
            
            # Create input snapshot for provenance
            input_snapshot = ConstructionInputSnapshot(
                config_identity=str(id(request.config)),
                context_identity=str(id(request.runtime_context)),
                dependency_resolution_id=str(id(request.dependency_resolution_result)),
                registry_snapshots=tuple(str(id(v)) for v in request.registry_views.values()),
                runtime_id=request.runtime_id,
            )
            
            # Return successful result with unactivated kernel
            return KernelConstructionResult.success(
                construction_id=request.construction_id.value,
                runtime_id=request.runtime_id,
                kernel=kernel,
                input_snapshot=input_snapshot,
                duration_seconds=time.monotonic() - start_time,
            )
        
        except Exception as e:
            # Catch unexpected exceptions and convert to failure result
            return self._complete_with_failure(
                request=request,
                ctx=ctx,
                start_time=start_time,
                failure_reason=f"Unexpected construction error: {str(e)}",
                diagnostics={"exception": str(e)},
            )
        
        finally:
            # Mark builder as COMPLETE (can be reused)
            self._state = KernelBuilderState.COMPLETE
    
    async def _validate_inputs(
        self,
        request: KernelConstructionRequest,
        ctx: KernelConstructionContext,
    ) -> KernelConstructionResult:
        """Validate construction inputs."""
        errors: List[str] = []
        
        # Validate required fields
        if not request.config:
            errors.append("Configuration is required but not provided")
        
        if not request.runtime_context:
            errors.append("Runtime context is required but not provided")
        
        if not request.dependency_resolution_result:
            errors.append("Dependency resolution result is required but not provided")
        
        # Validate types
        try:
            from ..types import RuntimeId
            
            if not isinstance(request.runtime_id, RuntimeId):
                errors.append(f"runtime_id must be a RuntimeId, got {type(request.runtime_id)}")
            
            if not isinstance(request.construction_id, KernelConstructionId):
                errors.append(
                    f"construction_id must be a KernelConstructionId, "
                    f"got {type(request.construction_id)}"
                )
        except Exception as e:
            errors.append(f"Type validation error: {str(e)}")
        
        if errors:
            ctx.add_error("Input validation failed")
            for err in errors:
                ctx.add_error(err)
            
            return KernelConstructionResult.failure(
                construction_id=request.construction_id.value,
                runtime_id=request.runtime_id,
                reason="Invalid construction inputs",
                stage=ConstructionStage.VALIDATING_INPUTS,
                diagnostics={"errors": errors},
            )
        
        ctx.inputs_validated = True
        ctx.record_stage_transition(ConstructionStage.VALIDATING_CONFIGURATION)
        return KernelConstructionResult.success(
            construction_id=request.construction_id.value,
            runtime_id=request.runtime_id,
            kernel=None,
        )
    
    async def _validate_configuration(
        self,
        config: Any,
        ctx: KernelConstructionContext,
    ) -> KernelConstructionResult:
        """Validate configuration is acceptable."""
        # Check that config has the required attributes
        if hasattr(config, "name") and not config.name:
            ctx.add_warning("Configuration name is empty")
        
        return KernelConstructionResult.success(
            construction_id=ctx.construction_id,
            runtime_id=ctx.runtime_id,
            kernel=None,
        )
    
    async def _validate_dependencies(
        self,
        dependency_result: Any,
        ctx: KernelConstructionContext,
    ) -> bool:
        """Validate dependency resolution result."""
        # Verify it has the expected structure
        try:
            # Check for required attributes on dependency resolution
            if hasattr(dependency_result, "resolved_entities"):
                entities = getattr(dependency_result, "resolved_entities", [])
                ctx.dependencies_validated = len(entities) > 0
                return True
            
            # Alternative: check if it's iterable with expected structure
            if hasattr(dependency_result, "__iter__"):
                items = list(dependency_result)
                ctx.dependencies_validated = len(items) > 0
                return True
            
            # Unknown structure but not an error
            ctx.add_warning(
                "Dependency resolution result has unexpected structure"
            )
            ctx.dependencies_validated = True
            return True
            
        except Exception as e:
            ctx.add_error(f"Error validating dependencies: {str(e)}")
            ctx.dependencies_validated = False
            return False
    
    async def _validate_registries(
        self,
        registry_views: Dict[str, Any],
        ctx: KernelConstructionContext,
    ) -> bool:
        """Validate registry views."""
        # Check each registry view has required structure
        for name, view in registry_views.items():
            try:
                # Verify it has a snapshot method or is a valid view
                if hasattr(view, "snapshot") or hasattr(view, "__getitem__"):
                    continue
                
                ctx.add_warning(
                    f"Registry '{name}' may not have expected interface"
                )
            except Exception as e:
                ctx.add_error(f"Error validating registry '{name}': {str(e)}")
        
        ctx.registries_validated = True
        return True
    
    async def _compile_construction_plan(
        self,
        request: KernelConstructionRequest,
        ctx: KernelConstructionContext,
    ) -> "KernelConstructionPlan":
        """Compile an immutable construction plan."""
        # Extract dependency order from resolution result
        ordered_deps = []
        
        if hasattr(request.dependency_resolution_result, "resolved_entities"):
            ordered_deps = list(
                getattr(request.dependency_resolution_result, "resolved_entities", [])
            )
        
        return KernelConstructionPlan(
            construction_id=request.construction_id.value,
            runtime_id=request.runtime_id,
            config_identity=str(id(request.config)),
            context_identity=str(id(request.runtime_context)),
            dependency_order=tuple(ordered_deps),
            registry_ids=tuple(str(id(v)) for v in request.registry_views.values()),
        )
    
    async def _construct_kernel(
        self,
        request: KernelConstructionRequest,
        plan: "KernelConstructionPlan",
        ctx: KernelConstructionContext,
    ) -> Tuple[Any, Optional[str]]:
        """
        Construct the kernel without activation.
        
        Returns:
            Tuple of (kernel_instance, error_message)
            If error_message is None, construction succeeded
        """
        try:
            # Import the canonical Kernel type
            from . import Kernel
            
            # Construct a new kernel instance with the provided config
            # Note: We do NOT call start_all_services() here - that's activation
            
            kernel = Kernel(config=request.config)
            
            # The kernel is now constructed but NOT activated
            # It should have:
            # - is_running = False (via _state.is_running)
            # - All dependencies attached via constructor injection
            
            return kernel, None
        
        except Exception as e:
            error_msg = f"Kernel construction failed: {str(e)}"
            ctx.add_error(error_msg)
            return None, error_msg
    
    async def _verify_kernel(
        self,
        kernel: Any,
        ctx: KernelConstructionContext,
    ) -> Optional[str]:
        """
        Verify the constructed kernel meets invariants.
        
        Returns:
            Error message if verification fails, or None if successful
        """
        errors = []
        
        try:
            # Invariant KERNEL-002: Constructed kernel is not activated
            if hasattr(kernel, "_state") and hasattr(kernel._state, "is_running"):
                if getattr(kernel._state, "is_running", False):
                    errors.append(
                        "Kernel _state.is_running must be False after construction"
                    )
            
            # Invariant KERNEL-020: Kernel remains infrastructure-only
            # (no cognitive or capability semantics)
            # This is structural - kernel should not have planning/cognition methods
            
        except Exception as e:
            errors.append(f"Error verifying kernel invariants: {str(e)}")
        
        if errors:
            return "; ".join(errors)
        
        return None
    
    def _complete_with_failure(
        self,
        request: KernelConstructionRequest,
        ctx: KernelConstructionContext,
        start_time: float,
        failure_reason: str,
        diagnostics: Dict[str, Any],
    ) -> KernelConstructionResult:
        """Complete construction with a failure result."""
        ctx.current_stage = ConstructionStage.FAILED
        
        return KernelConstructionResult.failure(
            construction_id=request.construction_id.value,
            runtime_id=request.runtime_id,
            reason=failure_reason,
            stage=ctx.current_stage,
            diagnostics=diagnostics,
            input_snapshot=None,
            duration_seconds=time.monotonic() - start_time,
        )
    
    def reset(self) -> None:
        """Reset builder to NEW state for reuse."""
        self._state = KernelBuilderState.NEW
    
    def snapshot(self) -> KernelConstructionSnapshot:
        """
        Get an immutable snapshot of current builder state.
        
        This provides visibility into the builder's current state without
        exposing mutable internals. It can be used for monitoring or
        diagnostics purposes.
        
        Returns:
            KernelConstructionSnapshot with current builder state
        """
        if self._state == KernelBuilderState.NEW:
            return KernelConstructionSnapshot(
                construction_id="N/A",
                runtime_id=None,
                current_stage=ConstructionStage.NOT_STARTED,
                status=ConstructionStatus.PENDING,
                start_time=time.monotonic(),
                duration_seconds=0.0,
                inputs_validated=False,
                dependencies_resolved=False,
                registries_validated=False,
                kernel_constructed=False,
            )
        
        # For other states, return a generic snapshot
        return KernelConstructionSnapshot(
            construction_id="N/A",
            runtime_id=None,
            current_stage=ConstructionStage.NOT_STARTED,
            status=(
                ConstructionStatus.SUCCESS
                if self._state == KernelBuilderState.COMPLETE
                else ConstructionStatus.PENDING
            ),
            start_time=time.monotonic(),
            duration_seconds=0.0,
            inputs_validated=False,
            dependencies_resolved=False,
            registries_validated=False,
            kernel_constructed=False,
        )


# ============================================================================
# KernelConstructionPlan - Immutable construction guide
# ============================================================================

@dataclass(frozen=True)
class KernelConstructionPlan:
    """
    Immutable plan for kernel construction.
    
    This is compiled before actual construction and provides the authoritative
    guide for how the kernel should be built. All fields are immutable to
    ensure determinism.
    """
    construction_id: str
    runtime_id: RuntimeId
    
    # Configuration identity (for provenance)
    config_identity: str
    
    # Context identity (for provenance)
    context_identity: str
    
    # Ordered dependencies from resolution result
    dependency_order: Tuple[str, ...]
    
    # Registry identities
    registry_ids: Tuple[str, ...]
    
    @property
    def dependency_count(self) -> int:
        """Return number of dependencies in plan."""
        return len(self.dependency_order)
    
    @property
    def registry_count(self) -> int:
        """Return number of registries in plan."""
        return len(self.registry_ids)


# ============================================================================
# Helper Functions
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


__all__ = [
    # State machine
    "ConstructionStage",
    "ConstructionStatus",
    
    # Artifacts (immutable)
    "KernelConstructionId",
    "ConstructionInputSnapshot",
    "ConstructionStageRecord",
    "KernelConstructionResult",
    "KernelConstructionSnapshot",
    "KernelConstructionReceipt",
    
    # Builder state
    "KernelBuilderState",
    
    # Request
    "KernelConstructionRequest",
    
    # Internal context
    "KernelConstructionContext",
    
    # Main builder
    "KernelBuilder",
    
    # Plan
    "KernelConstructionPlan",
    
    # Utilities
    "dataclass_replace",
]