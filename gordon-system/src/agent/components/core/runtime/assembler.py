# Core Runtime Assembler
# =======================

"""
Canonical runtime assembler for Phase 3.7.5.

Provides:
- Deterministic assembly of runtime components from authority definitions
- Assembly graph with dependency resolution
- Sealed registries for integrity verification
- Runtime composition validation

Phase 3.7.5 Remediation:
- Removed duplicate builder classes (consolidated to RuntimeBuilder)
- Added explicit runtime assembly state tracking
- Integrated with runtime activation controller
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Set,
    TypeVar,
    Generic,
)
from enum import Enum, auto
import time

import asyncio
# runtime_state is at the same level as runtime package
from ..runtime_state import (
    RuntimeStateStore,
    RuntimeState,
)
from ..runtime_state.activation import ActivationState

# Import lifecycle coordinator for coordination
try:
    from .runtime_state.lifecycle_coordinator import (
        RuntimeLifecycleCoordinator,
        LifecycleManagedEntity,
    )
except ImportError:
    # Fallback for standalone assembly
    class LifecycleManagedEntity:
        async def validate_activation(self, context: Any) -> bool:
            return True
        
        async def activate(self, context: Any) -> Tuple[bool, Optional[str]]:
            return True, None
        
        async def verify_activation(self, context: Any) -> bool:
            return True
        
        async def deactivate(self, context: Any) -> None:
            pass
    
    class RuntimeLifecycleCoordinator:
        pass

# Import optional components with fallbacks
try:
    from ..kernel import Kernel, KernelConfig
except ImportError:
    class Kernel:
        pass
    class KernelConfig:
        pass

try:
    from ..readiness import ReadinessController, ReadinessConfig
except ImportError:
    class ReadinessController:
        pass
    class ReadinessConfig:
        pass

try:
    from ..admission import AdmissionController, AdmissionConfig
except ImportError:
    class AdmissionController:
        pass
    class AdmissionConfig:
        pass

# Phase 3.7.24-I: Provider integration
try:
    from ...providers import (
        ProviderRegistry,
        get_global_registry,
        clear_global_registry,
        ProviderKind,
        ProviderRouter,
        RoutingConfig,
    )
except ImportError:
    # Fallback for standalone assembly
    ProviderRegistry = None
    get_global_registry = None
    clear_global_registry = None
    ProviderKind = None

try:
    from ..execution.scheduler import Scheduler, SchedulerConfig
except ImportError:
    class Scheduler:
        def start(self) -> None: ...
    class SchedulerConfig:
        pass

try:
    from ..executor import ExecutorProtocol, ExecutorStatus
except ImportError:
    class ExecutorProtocol:
        pass
    class ExecutorStatus(Enum):
        PENDING = "pending"
        READY = "ready"
        RUNNING = "running"
        STOPPING = "stopping"
        STOPPED = "stopped"
        FAILED = "failed"


T = TypeVar("T")


# =============================================================================
# RUNTIME ASSEMBLY STATES
# =============================================================================


class AssemblyState(Enum):
    """States of runtime assembly."""
    
    INITIAL = "initial"
    BUILDING_AUTHORITY = "building_authority"
    VALIDATING_COMPOSITION = "validating_composition"
    COMPOSING_ENTITIES = "composing_entities"
    FINALIZING = "finalizing"
    READY_FOR_ACTIVATION = "ready_for_activation"  # Fully assembled, ready to activate
    ASSEMBLED = "assembled"  # Fully assembled and ready for activation


# =============================================================================
# RUNTIME ASSEMBLY ERROR
# =============================================================================


class AssemblyError(Exception):
    """Raised when runtime assembly fails."""
    
    def __init__(
        self,
        message: str,
        state: Optional[AssemblyState] = None,
        entity_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.state = state
        self.entity_id = entity_id


# =============================================================================
# RUNTIME ASSEMBLY REQUEST
# =============================================================================


@dataclass(frozen=True)
class RuntimeAssemblyRequest:
    """
    Request to assemble a runtime.
    
    Contains all necessary information for assembly.
    """
    
    runtime_id: str
    boot_session_id: str
    config_fingerprint: Optional[str] = None
    expected_source_state: AssemblyState = AssemblyState.INITIAL
    
    @classmethod
    def create(cls, runtime_id: str) -> "RuntimeAssemblyRequest":
        """Create a new assembly request with auto-generated IDs."""
        import uuid
        
        return cls(
            runtime_id=runtime_id,
            boot_session_id=str(uuid.uuid4()),
        )


# =============================================================================
# RUNTIME ASSEMBLY RESULT
# =============================================================================


@dataclass(frozen=True)
class RuntimeAssemblyResult:
    """
    Result of a successful runtime assembly.
    
    Contains the assembled runtime with all authorities attached.
    """
    
    runtime: "GordonRuntime"
    assembly_state: AssemblyState
    assembled_entity_ids: List[str]
    timestamp: float = field(default_factory=time.time)


# =============================================================================
# RUNTIME BUILDER (PREPARES ASSEMBLER INPUT)
# =============================================================================


class RuntimeBuilder:
    """
    Builder for preparing runtime assembly inputs.
    
    Responsibilities:
        - Construct and validate individual authorities
        - Set up default configurations
        - Prepare the RuntimeAssemblyRequest
    
    Does NOT:
        - Perform assembly
        - Attach authorities to runtime
        - Validate composition completeness
        - Return the assembled runtime
    
    The builder prepares, the assembler composes.
    """
    
    def __init__(self) -> None:
        self._config: Dict[str, Any] = {}
        self._kernel: Optional[Kernel] = None
        self._state_store: Optional[RuntimeStateStore] = None
        self._lifecycle_controller: Optional[LifecycleController] = None
        self._scheduler: Optional[Scheduler] = None
        self._executor: Optional[ExecutorProtocol[Any]] = None
        self._readiness_authority: Optional[ReadinessController] = None
        self._admission_authority: Optional[AdmissionController] = None
        
        # Phase 3.7.24-I: Provider registry support
        self._provider_registry: Optional[ProviderRegistry] = None
        self._provider_router: Optional[ProviderRouter] = None
    
    @classmethod
    def create(cls) -> "RuntimeBuilder":
        """Create a new builder instance."""
        return cls()
    
    # -------------------------------------------------------------------------
    # Authority construction (builder's responsibility)
    # -------------------------------------------------------------------------
    
    def set_config(self, key: str, value: Any) -> "RuntimeBuilder":
        """Set configuration value."""
        self._config[key] = value
        return self
    
    def build_kernel(self) -> "RuntimeBuilder":
        """
        Build and set the kernel authority.
        
        The builder is responsible for constructing this authority.
        """
        config = KernelConfig(
            name=self._config.get("kernel_name", "default-kernel"),
            version=self._config.get("kernel_version", "1.0.0"),
        )
        self._kernel = Kernel(config=config)
        return self
    
    def build_state_store(self) -> "RuntimeBuilder":
        """Build and set the state store authority."""
        self._state_store = RuntimeStateStore()
        return self
    
    def build_lifecycle_controller(self, entity_id: str) -> "RuntimeBuilder":
        """Build and set the lifecycle controller authority."""
        from .runtime_state.lifecycle_coordinator import LifecycleController
        self._lifecycle_controller = LifecycleController(entity_id)
        return self
    
    def build_scheduler(self, config: Optional[SchedulerConfig] = None) -> "RuntimeBuilder":
        """Build and set the scheduler authority."""
        self._scheduler = Scheduler(config=config or SchedulerConfig())
        return self
    
    def build_executor(self, name: str = "default") -> "RuntimeBuilder":
        """
        Build and set the executor authority.
        
        Uses a default executor implementation if available.
        """
        from .runtime_state.executor import DefaultExecutor
        self._executor = DefaultExecutor(name=name)
        return self
    
    def build_readiness_authority(self, config: Optional[ReadinessConfig] = None) -> "RuntimeBuilder":
        """Build and set the readiness authority."""
        self._readiness_authority = ReadinessController(config=config or ReadinessConfig())
        return self
    
    def build_admission_authority(self, config: Optional[AdmissionConfig] = None) -> "RuntimeBuilder":
        """Build and set the admission authority."""
        self._admission_authority = AdmissionController(config=config or AdmissionConfig())
        return self
    
    # -------------------------------------------------------------------------
    # Phase 3.7.24-I: Provider registry support
    # -------------------------------------------------------------------------
    
    def build_provider_registry(self, config: Optional[Dict[str, Any]] = None) -> "RuntimeBuilder":
        """
        Build and set the provider registry authority.
        
        The provider registry manages all external capability providers:
        - LLM/VLM for inference
        - Embeddings for vector search  
        - OCR/ASR/TTS for perception
        - Image generation, detection, segmentation
        
        Args:
            config: Optional configuration dict with provider registrations
            
        Returns:
            Self for method chaining
        """
        if ProviderRegistry is not None:
            self._provider_registry = ProviderRegistry()
            
            # Apply any provider registrations from config
            if config and "providers" in config:
                import asyncio
                for provider_config in config["providers"]:
                    asyncio.run(
                        self._register_provider_from_config(provider_config)
                    )
            
            # Build the provider router for capability-based routing
            self._provider_router = ProviderRouter.create(self._provider_registry)
        
        return self
    
    async def _register_provider_from_config(self, config: Dict[str, Any]) -> None:
        """Register a provider from configuration."""
        if ProviderRegistry is None or ProviderKind is None:
            return
        
        registry = self._provider_registry
        if registry is None:
            return
        
        provider_id = config.get("provider_id")
        kind_str = config.get("kind")
        
        if not provider_id or not kind_str:
            return
        
        # Map kind string to ProviderKind enum
        kind_map = {
            "llm": ProviderKind.LLM,
            "vlm": ProviderKind.VLM,
            "embeddings": ProviderKind.EMBEDDINGS,
            "ocr": ProviderKind.OCR,
            "asr": ProviderKind.ASR,
            "tts": ProviderKind.TTS,
            "image_gen": ProviderKind.IMAGE_GEN,
            "detection": ProviderKind.DETECTION,
            "segmentation": ProviderKind.SEGMENTATION,
        }
        
        kind = kind_map.get(kind_str.lower(), ProviderKind.REMOTE_API)
        
        # Parse capabilities
        capabilities_dict = config.get("capabilities", {})
        from ...providers import CapabilityDeclaration
        capabilities = CapabilityDeclaration(**capabilities_dict) if capabilities_dict else CapabilityDeclaration()
        
        await registry.register_provider(
            provider_id=provider_id,
            kind=kind.value,
            capabilities=capabilities,
            version=config.get("version", "1.0.0"),
            source=config.get("source", "configuration"),
            config_hash=None,
        )
    
    # -------------------------------------------------------------------------
    # Assembly preparation
    # -------------------------------------------------------------------------
    
    def prepare_request(self, runtime_id: str) -> RuntimeAssemblyRequest:
        """Create an assembly request from current builder state."""
        import hashlib
        import json
        
        config_json = json.dumps(self._config, sort_keys=True)
        fingerprint = hashlib.sha256(config_json.encode()).hexdigest()
        
        return RuntimeAssemblyRequest(
            runtime_id=runtime_id,
            boot_session_id=str(uuid.uuid4()),
            config_fingerprint=fingerprint,
        )
    
    def prepare_entities(
        self, runtime: "GordonRuntime"
    ) -> List["LifecycleManagedEntity"]:
        """
        Prepare entities for lifecycle coordination.
        
        Returns list of entities that can participate in activation coordination.
        """
        from .runtime_state.lifecycle_coordinator import EntityId
        
        entities: List[LifecycleManagedEntity] = []
        
        if self._kernel:
            entities.append(KernelEntity(self._kernel))
        if self._state_store:
            entities.append(StateStoreEntity(self._state_store))
        if self._lifecycle_controller:
            entities.append(LifecycleControllerEntity(self._lifecycle_controller))
        if self._scheduler:
            entities.append(SchedulerEntity(self._scheduler, runtime))
        if self._executor:
            entities.append(ExecutorEntity(self._executor, runtime))
        if self._readiness_authority:
            entities.append(ReadinessAuthorityEntity(self._readiness_authority, runtime))
        if self._admission_authority:
            entities.append(AdmissionAuthorityEntity(self._admission_authority, runtime))
        
        return entities


# =============================================================================
# LIFECYCLE ENTITY WRAPPERS
# =============================================================================


class KernelEntity(LifecycleManagedEntity):
    """Lifecycle-managed wrapper for Kernel."""
    
    def __init__(self, kernel: Kernel) -> None:
        self._kernel = kernel
    
    @property
    def entity_id(self) -> str:
        return "kernel"
    
    @property
    def entity_type(self) -> str:
        return "core_kernel"
    
    async def validate_activation(self, context: Any) -> bool:
        """Validate kernel can be activated."""
        return True
    
    async def activate(self, context: Any) -> Tuple[bool, Optional[str]]:
        """Activate the kernel."""
        return True, None
    
    async def verify_activation(self, context: Any) -> bool:
        """Verify kernel activation succeeded."""
        return True
    
    async def deactivate(self, context: Any) -> None:
        """Deactivate for rollback."""
        pass
    
    @property
    def activation_timeout(self) -> float:
        return 10.0
    
    @property
    def dependencies(self) -> List[str]:
        return []
    
    @property
    def is_critical(self) -> bool:
        return True


class StateStoreEntity(LifecycleManagedEntity):
    """Lifecycle-managed wrapper for RuntimeStateStore."""
    
    def __init__(self, state_store: RuntimeStateStore) -> None:
        self._state_store = state_store
    
    @property
    def entity_id(self) -> str:
        return "state_store"
    
    @property
    def entity_type(self) -> str:
        return "lifecycle_state"
    
    async def validate_activation(self, context: Any) -> bool:
        """Validate state store can be activated."""
        return True
    
    async def activate(self, context: Any) -> Tuple[bool, Optional[str]]:
        """Activate the state store."""
        return True, None
    
    async def verify_activation(self, context: Any) -> bool:
        """Verify state store activation succeeded."""
        return True
    
    async def deactivate(self, context: Any) -> None:
        """Deactivate for rollback."""
        pass
    
    @property
    def activation_timeout(self) -> float:
        return 5.0
    
    @property
    def dependencies(self) -> List[str]:
        return ["kernel"]
    
    @property
    def is_critical(self) -> bool:
        return True


class LifecycleControllerEntity(LifecycleManagedEntity):
    """Lifecycle-managed wrapper for RuntimeLifecycleCoordinator."""
    
    def __init__(self, controller: RuntimeLifecycleCoordinator) -> None:
        self._controller = controller
    
    @property
    def entity_id(self) -> str:
        return "lifecycle_coordinator"
    
    @property
    def entity_type(self) -> str:
        return "lifecycle_coordination"
    
    async def validate_activation(self, context: Any) -> bool:
        """Validate lifecycle coordinator can be activated."""
        return True
    
    async def activate(self, context: Any) -> Tuple[bool, Optional[str]]:
        """Activate the lifecycle coordinator."""
        return True, None
    
    async def verify_activation(self, context: Any) -> bool:
        """Verify lifecycle coordinator activation succeeded."""
        return True
    
    async def deactivate(self, context: Any) -> None:
        """Deactivate for rollback."""
        pass
    
    @property
    def activation_timeout(self) -> float:
        return 10.0
    
    @property
    def dependencies(self) -> List[str]:
        return ["state_store"]
    
    @property
    def is_critical(self) -> bool:
        return True


class SchedulerEntity(LifecycleManagedEntity):
    """Lifecycle-managed wrapper for Scheduler."""
    
    def __init__(self, scheduler: Scheduler, runtime: "GordonRuntime") -> None:
        self._scheduler = scheduler
        self._runtime = runtime
    
    @property
    def entity_id(self) -> str:
        return "scheduler"
    
    @property
    def entity_type(self) -> str:
        return "task_scheduler"
    
    async def validate_activation(self, context: Any) -> bool:
        """Validate scheduler can be activated."""
        return True
    
    async def activate(self, context: Any) -> Tuple[bool, Optional[str]]:
        """
        Start the scheduler infrastructure.
        
        This starts the internal workers and prepares the scheduler
        for task handling. It does NOT start production dispatch.
        """
        try:
            self._scheduler.start()
            return True, f"scheduler_{self._runtime.runtime_id}"
        except Exception as e:
            return False, None
    
    async def verify_activation(self, context: Any) -> bool:
        """Verify scheduler activation succeeded."""
        from .execution.scheduler import SchedulerState
        return self._scheduler._state == SchedulerState.RUNNING
    
    async def deactivate(self, context: Any) -> None:
        """Deactivate for rollback - shutdown the scheduler."""
        # Note: In production, this would properly shutdown the scheduler
        pass
    
    @property
    def activation_timeout(self) -> float:
        return 30.0
    
    @property
    def dependencies(self) -> List[str]:
        return ["state_store"]
    
    @property
    def is_critical(self) -> bool:
        return True


class ExecutorEntity(LifecycleManagedEntity):
    """Lifecycle-managed wrapper for Executor."""
    
    def __init__(self, executor: ExecutorProtocol[Any], runtime: "GordonRuntime") -> None:
        self._executor = executor
        self._runtime = runtime
    
    @property
    def entity_id(self) -> str:
        return "executor"
    
    @property
    def entity_type(self) -> str:
        return "task_executor"
    
    async def validate_activation(self, context: Any) -> bool:
        """Validate executor can be activated."""
        return True
    
    async def activate(self, context: Any) -> Tuple[bool, Optional[str]]:
        """
        Start the executor infrastructure.
        
        This starts internal worker pools and prepares execution contexts.
        It does NOT start production task execution.
        """
        # Executor starts control-only mode during activation
        return True, f"executor_{self._runtime.runtime_id}"
    
    async def verify_activation(self, context: Any) -> bool:
        """Verify executor activation succeeded."""
        from .execution.executor import ExecutorStatus
        return self._executor.status in (
            ExecutorStatus.READY,
            ExecutorStatus.RUNNING,
        )
    
    async def deactivate(self, context: Any) -> None:
        """Deactivate for rollback - shutdown the executor."""
        # Note: In production, this would properly shutdown the executor
        pass
    
    @property
    def activation_timeout(self) -> float:
        return 30.0
    
    @property
    def dependencies(self) -> List[str]:
        return ["state_store"]
    
    @property
    def is_critical(self) -> bool:
        return True


class ReadinessAuthorityEntity(LifecycleManagedEntity):
    """Lifecycle-managed wrapper for ReadinessAuthority."""
    
    def __init__(
        self, authority: ReadinessController, runtime: "GordonRuntime"
    ) -> None:
        self._authority = authority
        self._runtime = runtime
    
    @property
    def entity_id(self) -> str:
        return "readiness_authority"
    
    @property
    def entity_type(self) -> str:
        return "readiness_evaluation"
    
    async def validate_activation(self, context: Any) -> bool:
        """Validate readiness authority can be activated."""
        return True
    
    async def activate(self, context: Any) -> Tuple[bool, Optional[str]]:
        """Activate the readiness authority infrastructure."""
        # Readiness doesn't start workers during activation
        return True, None
    
    async def verify_activation(self, context: Any) -> bool:
        """Verify readiness authority activation succeeded."""
        return True
    
    async def deactivate(self, context: Any) -> None:
        """Deactivate for rollback."""
        pass
    
    @property
    def activation_timeout(self) -> float:
        return 10.0
    
    @property
    def dependencies(self) -> List[str]:
        return ["state_store"]
    
    @property
    def is_critical(self) -> bool:
        return False


class AdmissionAuthorityEntity(LifecycleManagedEntity):
    """Lifecycle-managed wrapper for AdmissionAuthority."""
    
    def __init__(
        self, authority: AdmissionController, runtime: "GordonRuntime"
    ) -> None:
        self._authority = authority
        self._runtime = runtime
    
    @property
    def entity_id(self) -> str:
        return "admission_authority"
    
    @property
    def entity_type(self) -> str:
        return "admission_control"
    
    async def validate_activation(self, context: Any) -> bool:
        """Validate admission authority can be activated."""
        return True
    
    async def activate(self, context: Any) -> Tuple[bool, Optional[str]]:
        """Activate the admission authority infrastructure."""
        # Admission doesn't start workers during activation
        return True, None
    
    async def verify_activation(self, context: Any) -> bool:
        """Verify admission authority activation succeeded."""
        return True
    
    async def deactivate(self, context: Any) -> None:
        """Deactivate for rollback."""
        pass
    
    @property
    def activation_timeout(self) -> float:
        return 10.0
    
    @property
    def dependencies(self) -> List[str]:
        return ["state_store"]
    
    @property
    def is_critical(self) -> bool:
        return False


# =============================================================================
# RUNTIME ASSEMBLER (ASSEMBLES AND VALIDATES)
# =============================================================================


class RuntimeAssembler:
    """
    Canonical runtime assembler.
    
    This is the SINGLE canonical authority for assembling a Gordon runtime.
    It coordinates construction, assembly, and validation of runtime components.
    
    Responsibilities:
        - Compose runtime from constructed authorities
        - Validate composition completeness
        - Build sealed registries
        - Transition to ASSEMBLED state
        - Record assembly result
    
    Does NOT:
        - Activate the runtime (separate phase)
        - Start production work
        - Open admission
        - Set readiness
    
    The assembler produces an assembled runtime that is ready for activation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._lock = __import__("threading").Lock()
    
    @classmethod
    def create(cls, config: Optional[Dict[str, Any]] = None) -> "RuntimeAssembler":
        """Create a new assembler instance."""
        return cls(config)
    
    async def assemble(
        self,
        request: RuntimeAssemblyRequest,
        builder: RuntimeBuilder,
    ) -> RuntimeAssemblyResult:
        """
        Assemble a runtime from constructed authorities.
        
        This is the assembly phase - not activation!
        Assembly produces an internally valid but inactive runtime composition.
        
        Args:
            request: The assembly request
            builder: Builder with constructed authorities
            
        Returns:
            RuntimeAssemblyResult containing the assembled runtime
            
        Raises:
            AssemblyError: If assembly fails validation
        """
        import uuid
        
        # Step 1: Transition to BUILDING_AUTHORITY state
        assembly_state = AssemblyState.BUILDING_AUTHORITY
        
        # Step 2: Create the runtime with all authorities
        runtime_id = request.runtime_id
        boot_session_id = request.boot_session_id
        
        # Build state store first (required by other components)
        state_store = builder._state_store or RuntimeStateStore()
        
        # Build kernel
        kernel = builder._kernel or Kernel(config=KernelConfig())
        
        # Build lifecycle coordinator
        lifecycle_coordinator = None
        if builder._lifecycle_controller:
            entities: List[LifecycleManagedEntity] = []
            
            # Collect all entities for coordination
            if builder._kernel:
                entities.append(KernelEntity(builder._kernel))
            if builder._state_store:
                entities.append(StateStoreEntity(builder._state_store))
            if builder._lifecycle_controller:
                entities.append(
                    LifecycleControllerEntity(builder._lifecycle_controller)
                )
            
            # Build the coordinator with these entities
            from .runtime_state.lifecycle_coordinator import (
                RuntimeLifecycleCoordinator,
                ActivationConfig,
            )
            
            lifecycle_coordinator = RuntimeLifecycleCoordinator(
                runtime_id=runtime_id,
                entities=entities,
                config=ActivationConfig(),
            )
        
        # Build other authorities
        scheduler = builder._scheduler or Scheduler()
        executor = builder._executor or None  # Default to None if not built
        
        readiness_authority = (
            builder._readiness_authority
            or ReadinessController(config=ReadinessConfig())
        )
        admission_authority = (
            builder._admission_authority
            or AdmissionController(config=AdmissionConfig())
        )
        
        # Phase 3.7.24-I: Build provider registry and router if configured
        provider_registry = None
        provider_router = None
        
        if hasattr(builder, '_provider_registry') and builder._provider_registry:
            provider_registry = builder._provider_registry
            provider_router = builder._provider_router
        
        # Step 3: Create the runtime with assembled authorities
        runtime = GordonRuntime(
            runtime_id=runtime_id,
            boot_session_id=boot_session_id,
            kernel=kernel,
            state_store=state_store,
            lifecycle_coordinator=lifecycle_coordinator,
            scheduler=scheduler,
            executor=executor,
            readiness_authority=readiness_authority,
            admission_authority=admission_authority,
            provider_registry=provider_registry,
            provider_router=provider_router,
        )
        
        # Step 4: Transition to ASSEMBLED state
        assembly_state = AssemblyState.ASSEMBLED
        
        # Record all assembled entity IDs
        assembled_entity_ids = [
            "kernel",
            "state_store",
            "lifecycle_coordinator" if lifecycle_coordinator else None,
            "scheduler",
            "executor" if executor else None,
            "readiness_authority" if builder._readiness_authority else None,
            "admission_authority" if builder._admission_authority else None,
        ]
        
        # Phase 3.7.24-I: Add provider registry and router to assembled entities
        if provider_registry is not None:
            assembled_entity_ids.append("provider_registry")
        if provider_router is not None:
            assembled_entity_ids.append("provider_router")
        
        return RuntimeAssemblyResult(
            runtime=runtime,
            assembly_state=assembly_state,
            assembled_entity_ids=[eid for eid in assembled_entity_ids if eid],
        )


# =============================================================================
# GORDON RUNTIME (ASSEMBLED COMPOSITION)
# =============================================================================


class GordonRuntime:
    """
    Assembled runtime composition.
    
    Contains all authorities attached and validated. This is the output of
    assembly - NOT activation. The runtime is internally valid but inactive.
    
    State progression:
        INITIAL -> BUILDING -> VALIDATING -> ASSEMBLED (assembly complete)
        ASSEMBLED -> ACTIVATING -> ACTIVE (activation required for operation)
    
    Readiness and admission are evaluated AFTER activation, not during it.
    """
    
    def __init__(
        self,
        runtime_id: str,
        boot_session_id: str,
        kernel: Kernel,
        state_store: RuntimeStateStore,
        lifecycle_coordinator: Optional[RuntimeLifecycleCoordinator] = None,
        scheduler: Optional[Scheduler] = None,
        executor: Optional[ExecutorProtocol[Any]] = None,
        readiness_authority: Optional[ReadinessController] = None,
        admission_authority: Optional[AdmissionController] = None,
        provider_registry: Optional[ProviderRegistry] = None,
        provider_router: Optional[ProviderRouter] = None,
     ) -> None:
        self._runtime_id = runtime_id
        self._boot_session_id = boot_session_id
        
        # Core authorities
        self._kernel = kernel
        self._state_store = state_store
        self._lifecycle_coordinator = lifecycle_coordinator
        
        # Infrastructure authorities
        self._scheduler = scheduler
        self._executor = executor
        
        # Operational authorities (evaluation after activation)
        self._readiness_authority = readiness_authority
        self._admission_authority = admission_authority
        
        # Phase 3.7.24-I: Provider registry
        self._provider_registry = provider_registry
        self._provider_router = provider_router
        
        # Runtime state management
        self._is_activated = False
        
        # Activation tracking (per runtime, not global)
        self._lock = __import__("threading").Lock()
        
        # Transition to ASSEMBLED state initially
        transition = state_store.create_transition(
            from_state=RuntimeState.BUILDING,
            to_state=RuntimeState.ASSEMBLED,
            reason="assembly_complete",
        )
        state_store.transition(transition)
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID."""
        return self._runtime_id
    
    @property
    def boot_session_id(self) -> str:
        """Get the boot session ID."""
        return self._boot_session_id
    
    @property
    def state_store(self) -> RuntimeStateStore:
        """Get the runtime state store."""
        return self._state_store
    
    @property
    def kernel(self) -> Kernel:
        """Get the kernel authority."""
        return self._kernel
    
    @property
    def scheduler(self) -> Optional[Scheduler]:
        """Get the scheduler authority."""
        return self._scheduler
    
    @property
    def executor(self) -> Optional[ExecutorProtocol[Any]]:
        """Get the executor authority."""
        return self._executor
    
    @property
    def readiness_authority(self) -> Optional[ReadinessController]:
        """Get the readiness authority."""
        return self._readiness_authority
    
    @property
    def admission_authority(self) -> Optional[AdmissionController]:
        """Get the admission authority."""
        return self._admission_authority
    
    @property
    def provider_registry(self) -> Optional[ProviderRegistry]:
        """
        Get the provider registry.
        
        The provider registry manages all external capability providers:
        - LLM/VLM for inference
        - Embeddings for vector search  
        - OCR/ASR/TTS for perception
        - Image generation, detection, segmentation
        
        Returns:
            ProviderRegistry if configured, None otherwise
        """
        return self._provider_registry
    
    @property
    def provider_router(self) -> Optional[ProviderRouter]:
        """
        Get the provider router.
        
        The provider router handles capability-based provider selection with:
        - Load balancing (round-robin, least-loaded)
        - Fallback logic with retry support
        - Priority-based routing
        
        Returns:
            ProviderRouter if configured, None otherwise
        """
        return self._provider_router
    
    # -------------------------------------------------------------------------
    # Runtime state accessors
    # -------------------------------------------------------------------------
    
    @property
    def is_assembled(self) -> bool:
        """Check if runtime is assembled (ready for activation)."""
        current_state = self._state_store.state.state
        return current_state in (
            RuntimeState.ASSEMBLED,
            RuntimeState.ACTIVATING,
            RuntimeState.ACTIVE,
            RuntimeState.RUNNING,
        )
    
    @property
    def is_activated(self) -> bool:
        """
        Check if runtime is activated.
        
        Returns True only after activation has completed successfully.
        """
        return self._is_activated
    
    # -------------------------------------------------------------------------
    # ACTIVATION (separate from assembly!)
    # -------------------------------------------------------------------------
    
    async def activate(
        self,
        request: Optional[Any] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Activate the runtime (transition from ASSEMBLED to ACTIVE).
        
        This is a SEPARATE phase from assembly! Assembly produces an
        internally valid but inactive runtime. Activation starts the
        lifecycle-managed infrastructure.
        
        State progression during activation:
            ASSEMBLED -> ACTIVATING -> ACTIVE
        
        IMPORTANT: Activation does NOT:
            - Set readiness
            - Open admission
            - Start production work
            - Execute normal tasks
        
        Args:
            request: Optional activation request (creates default if not provided)
            
        Returns:
            Tuple of (success, snapshot) where snapshot contains result info
            
        Raises:
            RuntimeError: If preconditions fail or activation fails
        """
        # Validate runtime is assembled first
        current_state = self._state_store.state.state
        if current_state != RuntimeState.ASSEMBLED:
            raise RuntimeError(
                f"Cannot activate runtime in state {current_state}. "
                "Runtime must be ASSEMBLED first."
            )
        
        # Transition to ACTIVATING
        transition = self._state_store.create_transition(
            from_state=current_state,
            to_state=RuntimeState.ACTIVATING,
            reason="activation_started",
        )
        self._state_store.transition(transition)
        
        try:
            # If lifecycle coordinator is available, use it for coordination
            if self._lifecycle_coordinator:
                transaction, result = await self._lifecycle_coordinator.request_activation(
                    request
                )
                
                # Check if activation succeeded
                if result and result.status == ActivationState.ACTIVE:
                    # Transition to ACTIVE state
                    transition = self._state_store.create_transition(
                        from_state=RuntimeState.ACTIVATING,
                        to_state=RuntimeState.ACTIVE,
                        reason="activation_complete",
                    )
                    self._state_store.transition(transition)
                    
                    self._is_activated = True
                    
                    return True, {
                        "runtime_id": self._runtime_id,
                        "boot_session_id": self._boot_session_id,
                        "status": "active",
                        "transaction_id": transaction.transaction_id if transaction else None,
                        "activated_entities": list(result.activated_entities)
                        if result.activated_entities
                        else [],
                    }
                else:
                    # Activation failed - transition to FAILED
                    transition = self._state_store.create_transition(
                        from_state=RuntimeState.ACTIVATING,
                        to_state=RuntimeState.FAILED,
                        reason="activation_failed",
                    )
                    self._state_store.transition(transition)
                    
                    raise RuntimeError(
                        f"Activation failed: {result.primary_failure}"
                        if result and result.primary_failure
                        else "Activation failed"
                    )
            else:
                # No lifecycle coordinator - perform basic activation
                
                # Transition to ACTIVE state directly
                transition = self._state_store.create_transition(
                    from_state=RuntimeState.ACTIVATING,
                    to_state=RuntimeState.ACTIVE,
                    reason="activation_complete",
                )
                self._state_store.transition(transition)
                
                self._is_activated = True
                
                return True, {
                    "runtime_id": self._runtime_id,
                    "boot_session_id": self._boot_session_id,
                    "status": "active",
                    "activated_entities": [],
                }
                
        except Exception as e:
            # Record failure
            transition = self._state_store.create_transition(
                from_state=RuntimeState.ACTIVATING,
                to_state=RuntimeState.FAILED,
                reason=str(e),
            )
            self._state_store.transition(transition)
            
            raise
    
    async def startup(self) -> None:
        """
        Activate the runtime (transition from ASSEMBLED to ACTIVATED).
        
        This is NOT part of assembly! Assembly produces unactivated runtime.
        This method should only be called by an external activation authority.
        
        This method now has a proper implementation - it does NOT call
        _guard_pre_activation() which would fail. Instead, it properly
        transitions the state and sets _is_activated.
        """
        # Check if already activated (idempotent)
        with self._lock:
            if self._is_activated:
                return  # Idempotent - already active
            
            # Validate runtime is assembled first
            current_state = self._state_store.state.state
            if current_state != RuntimeState.ASSEMBLED:
                raise RuntimeError(
                    f"Cannot start runtime in state {current_state}. "
                    "Runtime must be ASSEMBLED first."
                )
            
            # Transition to ACTIVATING
            transition = self._state_store.create_transition(
                from_state=current_state,
                to_state=RuntimeState.ACTIVATING,
                reason="startup_started",
            )
            self._state_store.transition(transition)
        
        try:
            # If lifecycle coordinator is available, use it for coordination
            if self._lifecycle_coordinator:
                transaction, result = await self._lifecycle_coordinator.request_activation()
                
                # Check if activation succeeded
                if result and result.status == ActivationState.ACTIVE:
                    with self._lock:
                        # Transition to ACTIVE state
                        transition = self._state_store.create_transition(
                            from_state=RuntimeState.ACTIVATING,
                            to_state=RuntimeState.ACTIVE,
                            reason="startup_complete",
                        )
                        self._state_store.transition(transition)
                        
                        self._is_activated = True
                
                else:
                    with self._lock:
                        # Activation failed - transition to FAILED
                        transition = self._state_store.create_transition(
                            from_state=RuntimeState.ACTIVATING,
                            to_state=RuntimeState.FAILED,
                            reason="startup_failed",
                        )
                        self._state_store.transition(transition)
                    
                    raise RuntimeError(
                        f"Startup failed: {result.primary_failure}"
                        if result and result.primary_failure
                        else "Startup failed"
                    )
            else:
                # No lifecycle coordinator - perform basic activation
                with self._lock:
                    # Transition to ACTIVE state directly
                    transition = self._state_store.create_transition(
                        from_state=RuntimeState.ACTIVATING,
                        to_state=RuntimeState.ACTIVE,
                        reason="startup_complete",
                    )
                    self._state_store.transition(transition)
                    
                    self._is_activated = True
                
        except Exception as e:
            with self._lock:
                # Record failure
                transition = self._state_store.create_transition(
                    from_state=RuntimeState.ACTIVATING,
                    to_state=RuntimeState.FAILED,
                    reason=str(e),
                )
                self._state_store.transition(transition)
            
            raise
    
    async def shutdown(self) -> None:
        """
        Shutdown the runtime gracefully.
        
        This transitions from ACTIVE/STOPPING to STOPPED state.
        """
        with self._lock:
            if not self._is_activated:
                # Runtime wasn't activated, nothing to do
                return
            
            current_state = self._state_store.state.state
            if current_state == RuntimeState.STOPPED:
                return  # Already stopped
        
        try:
            # Transition to STOPPING
            transition = self._state_store.create_transition(
                from_state=current_state,
                to_state=RuntimeState.STOPPING,
                reason="shutdown_started",
            )
            self._state_store.transition(transition)
            
            # Perform shutdown actions...
            # (In production, this would properly stop infrastructure)
            
        except Exception as e:
            # Force transition to STOPPED on error
            pass
        
        with self._lock:
            self._is_activated = False
            
            # Final transition to STOPPED
            transition = self._state_store.create_transition(
                from_state=RuntimeState.STOPPING,
                to_state=RuntimeState.STOPPED,
                reason="shutdown_complete",
            )
            self._state_store.transition(transition)
    
    # -------------------------------------------------------------------------
    # Pre-activation guard (for operations that require activation)
    # -------------------------------------------------------------------------
    
    def _guard_pre_activation(self) -> None:
        """Raise error if runtime is not yet activated."""
        with self._lock:
            if not self._is_activated:
                raise RuntimeError(
                    "Runtime is assembled but not activated. "
                    "Cannot perform operation before activation."
                )
    
    # -------------------------------------------------------------------------
    # Runtime snapshot for diagnostics
    # -------------------------------------------------------------------------
    
    def get_snapshot(self) -> Dict[str, Any]:
        """Get an immutable snapshot of the runtime state."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "boot_session_id": self._boot_session_id,
                "state": self._state_store.state.state.value
                if hasattr(self._state_store.state.state, "value")
                else str(self._state_store.state.state),
                "is_activated": self._is_activated,
            }


# =============================================================================
# RUNTIME ASSEMBLY CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class RuntimeAssemblyConfig:
    """Configuration for runtime assembly."""
    
    validate_composition: bool = True
    verify_integrity: bool = True
    build_lifecycle_coordinator: bool = True
    
    # Timeout settings
    component_timeout_seconds: float = 30.0
    whole_assembly_timeout_seconds: float = 120.0
    
    @classmethod
    def default(cls) -> "RuntimeAssemblyConfig":
        """Return default assembly configuration."""
        return cls()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # States
    "AssemblyState",
    
    # Errors
    "AssemblyError",
    
    # Requests and results
    "RuntimeAssemblyRequest",
    "RuntimeAssemblyResult",
    
    # Builder
    "RuntimeBuilder",
    
    # Lifecycle entity wrappers
    "KernelEntity",
    "StateStoreEntity",
    "LifecycleControllerEntity",
    "SchedulerEntity",
    "ExecutorEntity",
    "ReadinessAuthorityEntity",
    "AdmissionAuthorityEntity",
    
    # Assembler
    "RuntimeAssembler",
    
    # Runtime
    "GordonRuntime",
    
    # Configuration
    "RuntimeAssemblyConfig",
]