# Deployment Core Abstractions
# ============================

"""
Phase 3.8.10 - Canonical Core Abstractions for Deployment & Operations

This module defines the canonical exception hierarchy and core interfaces
for the Deployment, Operations & Lifecycle Infrastructure.

ARCHITECTURAL PRINCIPLES:
    - All exceptions extend CoreError or appropriate base classes
    - Exceptions preserve cause chains for debugging
    - Structured error data provides actionable information
    - Error types map to failure modes in deployment workflows
"""

from typing import (
    Optional, List, Dict, Any, Callable, Protocol, runtime_checkable
)
from dataclasses import dataclass, field
from enum import Enum, auto
import time
import uuid

from ..exceptions import CoreError


# =============================================================================
# DEPLOYMENT EXCEPTION HIERARCHY
# =============================================================================


class DeploymentError(CoreError):
    """Base exception for all deployment-related errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        deployment_id: Optional[str] = None,
        stage: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.deployment_id = deployment_id
        self.stage = stage


class InstallationError(DeploymentError):
    """Raised when installation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        component: Optional[str] = None,
        phase: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="installation", cause=cause)
        self.component = component
        self.phase = phase


class ConfigurationError(DeploymentError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        config_key: Optional[str] = None,
        profile: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="configuration", cause=cause)
        self.config_key = config_key
        self.profile = profile


class LifecycleError(DeploymentError):
    """Raised when lifecycle transition is invalid."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        from_state: Optional[str] = None,
        to_state: Optional[str] = None,
        component: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="lifecycle", cause=cause)
        self.from_state = from_state
        self.to_state = to_state
        self.component = component


class UpgradeError(DeploymentError):
    """Raised when upgrade operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        from_version: Optional[str] = None,
        to_version: Optional[str] = None,
        step_failed: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="upgrade", cause=cause)
        self.from_version = from_version
        self.to_version = to_version
        self.step_failed = step_failed


class RollbackError(DeploymentError):
    """Raised when rollback operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        original_deployment_id: Optional[str] = None,
        failed_step: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="rollback", cause=cause)
        self.original_deployment_id = original_deployment_id
        self.failed_step = failed_step


class EnvironmentError(DeploymentError):
    """Raised when environment operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        environment_name: Optional[str] = None,
        provision_step: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="environment", cause=cause)
        self.environment_name = environment_name
        self.provision_step = provision_step


class InstallationWorkflowError(DeploymentError):
    """Raised when installation workflow fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        step_failed: Optional[str] = None,
        rollback_available: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="workflow", cause=cause)
        self.step_failed = step_failed
        self.rollback_available = rollback_available


class BootstrapError(DeploymentError):
    """Raised when bootstrap fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        phase_failed: Optional[str] = None,
        partial_success: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="bootstrap", cause=cause)
        self.phase_failed = phase_failed
        self.partial_success = partial_success


class ReadinessError(DeploymentError):
    """Raised when readiness check fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        readiness_check: Optional[str] = None,
        required_value: Optional[Any] = None,
        actual_value: Optional[Any] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="readiness", cause=cause)
        self.readiness_check = readiness_check
        self.required_value = required_value
        self.actual_value = actual_value


class EnvironmentCompatibilityError(DeploymentError):
    """Raised when environment compatibility check fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        artifact_type: Optional[str] = None,
        environment_type: Optional[str] = None,
        missing_requirements: Optional[List[str]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="compatibility", cause=cause)
        self.artifact_type = artifact_type
        self.environment_type = environment_type
        self.missing_requirements = missing_requirements or []


class ServiceManagementError(DeploymentError):
    """Raised when service management operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        service_id: Optional[str] = None,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="service", cause=cause)
        self.service_id = service_id
        self.operation = operation


class MonitoringError(DeploymentError):
    """Raised when monitoring operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        metric_name: Optional[str] = None,
        probe_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="monitoring", cause=cause)
        self.metric_name = metric_name
        self.probe_name = probe_name


class DiagnosticsError(DeploymentError):
    """Raised when diagnostics operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        diagnostic_code: Optional[str] = None,
        diagnostic_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="diagnostics", cause=cause)
        self.diagnostic_code = diagnostic_code
        self.diagnostic_type = diagnostic_type


class ProvisioningError(DeploymentError):
    """Raised when provisioning operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        provision_step: Optional[str] = None,
        resource_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="provisioning", cause=cause)
        self.provision_step = provision_step
        self.resource_id = resource_id


class OperationalOrchestrationError(DeploymentError):
    """Raised when operational orchestration fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        workflow_name: Optional[str] = None,
        stage_failed: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="orchestration", cause=cause)
        self.workflow_name = workflow_name
        self.stage_failed = stage_failed


class InfrastructureGovernanceError(DeploymentError):
    """Raised when infrastructure governance fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        policy_name: Optional[str] = None,
        violation_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, deployment_id="governance", cause=cause)
        self.policy_name = policy_name
        self.violation_type = violation_type


# =============================================================================
# LIFECYCLE MODEL
# =============================================================================


class LifecycleState(Enum):
    """Canonical lifecycle states for components and services."""
    
    # Installation states
    UNINSTALLED = "uninstalled"       # Not installed
    INSTALLING = "installing"         # Currently being installed
    INSTALLED = "installed"           # Installed but not started
    
    # Provisioning states  
    PROVISIONING = "provisioning"     # Resources being provisioned
    PROVISIONED = "provisioned"       # Resources available
    
    # Runtime states
    STOPPED = "stopped"               # Stopped but configured
    STARTING = "starting"             # Currently starting
    RUNNING = "running"               # Running normally
    DEGRADED = "degraded"             # Running with issues
    
    # Upgrade/maintenance states
    UPGRADING = "upgrading"           # Currently being upgraded
    MAINTENANCE = "maintenance"       # In maintenance mode
    DRAINING = "draining"             # Draining connections before shutdown
    
    # Shutdown states
    STOPPING = "stopping"             # Currently stopping
    TERMINATED = "terminated"         # Fully terminated
    FAILED = "failed"                 # Failed during operation


class LifecycleTransition(Enum):
    """Canonical lifecycle transitions."""
    
    INSTALL = "install"
    UNINSTALL = "uninstall"
    PROVISION = "provision"
    DEPROVISION = "deprovision"
    START = "start"
    STOP = "stop"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    MAINTENANCE_ENTER = "maintenance_enter"
    MAINTENANCE_EXIT = "maintenance_exit"
    RESTART = "restart"


@dataclass(frozen=True)
class LifecycleTransitionRequest:
    """Request to perform a lifecycle transition."""
    
    transition: LifecycleTransition
    source_state: LifecycleState
    target_state: LifecycleState
    
    component_id: str
    version: Optional[str] = None
    config_profile: Optional[str] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class LifecycleTransitionResult:
    """Result of a lifecycle transition."""
    
    success: bool
    transition: LifecycleTransition
    
    from_state: Optional[LifecycleState] = None
    to_state: Optional[LifecycleState] = None
    
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


# =============================================================================
# LIFECYCLE HOOKS
# =============================================================================


class LifecycleHook(Enum):
    """Lifecycle hook points for extensibility."""
    
    # Installation hooks
    BEFORE_INSTALL = "before_install"
    AFTER_INSTALL = "after_install"
    INSTALL_ROLLBACK = "install_rollback"
    
    # Provisioning hooks
    BEFORE_PROVISION = "before_provision"
    AFTER_PROVISION = "after_provision"
    PROVISION_ROLLBACK = "provision_rollback"
    
    # Runtime hooks
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"
    
    # Upgrade hooks
    BEFORE_UPGRADE = "before_upgrade"
    AFTER_UPGRADE = "after_upgrade"
    UPGRADE_ROLLBACK = "upgrade_rollback"
    
    # Health hooks
    HEALTH_CHECK = "health_check"
    HEALTH_FAIL = "health_fail"
    HEALTH_RECOVER = "health_recover"


@dataclass(frozen=True)
class LifecycleHookEvent:
    """Event emitted during lifecycle transitions."""
    
    hook: LifecycleHook
    component_id: str
    state: LifecycleState
    
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# DEPLOYMENT ARTIFACTS
# =============================================================================


class ArtifactType(Enum):
    """Types of deployment artifacts."""
    
    PACKAGE = "package"           # Installable package (wheel, tarball, etc.)
    CONTAINER = "container"       # Container image
    BINARY = "binary"             # Executable binary
    SCRIPT = "script"             # Installation script
    CONFIGURATION = "configuration"  # Configuration files
    METADATA = "metadata"         # Version and dependency metadata


@dataclass(frozen=True)
class ArtifactVersion:
    """Immutable artifact version with semantic versioning."""
    
    major: int
    minor: int
    patch: int
    
    prerelease: Optional[str] = None
    build_metadata: Optional[str] = None
    
    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            base += f"-{self.prerelease}"
        if self.build_metadata:
            base += f"+{self.build_metadata}"
        return base


@dataclass(frozen=True)
class DeploymentArtifact:
    """Immutable deployment artifact with metadata."""
    
    artifact_id: str
    name: str
    version: ArtifactVersion
    
    artifact_type: ArtifactType
    uri: str                      # Location (file, URL, registry path)
    
    checksum: Optional[str] = None  # SHA256 or similar
    size_bytes: int = 0
    created_at_utc: float = field(default_factory=time.time)
    
    dependencies: List[str] = field(default_factory=list)
    requirements: Dict[str, str] = field(default_factory=dict)  # pkg -> version
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_uri(cls, uri: str, artifact_type: ArtifactType) -> "DeploymentArtifact":
        """Create artifact reference from URI."""
        return cls(
            artifact_id=f"artifact_{uuid.uuid4().hex[:12]}",
            name=uri.split("/")[-1].split(".")[0],
            version=ArtifactVersion(major=0, minor=1, patch=0),
            artifact_type=artifact_type,
            uri=uri
        )


# =============================================================================
# DEPLOYMENT PLANS
# =============================================================================


class DeploymentAction(Enum):
    """Actions in a deployment plan."""
    
    DOWNLOAD = "download"
    VERIFY = "verify"
    INSTALL = "install"
    CONFIGURE = "configure"
    PROVISION = "provision"
    START = "start"
    HEALTH_CHECK = "health_check"
    ROLLBACK = "rollback"
    UPGRADE = "upgrade"
    DRAIN = "drain"
    STOP = "stop"


@dataclass(frozen=True)
class DeploymentStep:
    """A single step in a deployment plan."""
    
    step_id: str
    action: DeploymentAction
    
    target_artifact: Optional[str] = None  # artifact_id
    component_id: Optional[str] = None
    config_profile: Optional[str] = None
    
    dependencies: List[str] = field(default_factory=list)  # step_ids that must complete first
    timeout_seconds: float = 300.0
    can_rollback: bool = True
    
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeploymentPlan:
    """Immutable deployment plan with steps and constraints."""
    
    plan_id: str
    name: str
    description: str
    
    version_from: ArtifactVersion
    version_to: ArtifactVersion
    
    environment_name: str
    config_profile: Optional[str] = None
    
    steps: List[DeploymentStep] = field(default_factory=list)
    
    created_at_utc: float = field(default_factory=time.time)
    timeout_seconds: float = 3600.0  # Default 1 hour
    
    @property
    def is_valid(self) -> bool:
        """Check if plan has valid structure."""
        if not self.steps:
            return False
        
        step_ids = {s.step_id for s in self.steps}
        
        # Check all dependencies exist
        for step in self.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    return False
        
        return True
    
    def get_execution_order(self) -> List[DeploymentStep]:
        """Get steps in dependency order (topological sort)."""
        visited = set()
        result: List[DeploymentStep] = []
        
        def visit(step: DeploymentStep):
            if step.step_id in visited:
                return
            visited.add(step.step_id)
            
            for dep_id in step.dependencies:
                dep_step = next((s for s in self.steps if s.step_id == dep_id), None)
                if dep_step:
                    visit(dep_step)
            
            result.append(step)
        
        for step in self.steps:
            visit(step)
        
        return result


# =============================================================================
# CONFIGURATION PROFILES
# =============================================================================


class ConfigurationLayer(Enum):
    """Configuration layers with precedence order."""
    
    DEFAULTS = "defaults"           # Lowest precedence
    GLOBAL = "global"
    ENVIRONMENT = "environment"     # e.g., development, production
    OVERRIDE = "override"           # Highest precedence


@dataclass(frozen=True)
class ConfigurationOption:
    """A single configuration option with metadata."""
    
    name: str
    value_type: str               # Python type name
    
    default_value: Any
    required: bool = False
    
    description: Optional[str] = None
    environment_variable: Optional[str] = None
    secret: bool = False          # True if contains sensitive data
    
    validation_regex: Optional[str] = None
    allowed_values: Optional[List[Any]] = None


@dataclass(frozen=True)
class ConfigurationProfile:
    """Configuration profile with layered settings."""
    
    profile_id: str
    name: str
    description: str
    
    environment_name: str
    
    # Layered configuration (higher index = higher precedence)
    layers: Dict[ConfigurationLayer, Dict[str, Any]]
    
    options: List[ConfigurationOption] = field(default_factory=list)
    
    created_at_utc: float = field(default_factory=time.time)
    version: int = 1
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with layer precedence."""
        for layer in reversed(list(ConfigurationLayer)):
            if layer in self.layers and key in self.layers[layer]:
                return self.layers[layer][key]
        return default
    
    def is_set(self, key: str) -> bool:
        """Check if a configuration option is explicitly set."""
        return self.get(key, None) is not None


# =============================================================================
# RUNTIME ENVIRONMENTS
# =============================================================================


class EnvironmentType(Enum):
    """Types of runtime environments."""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    OFFLINE = "offline"
    CONTAINER = "container"
    GPU = "gpu"
    DISTRIBUTED = "distributed"


@dataclass(frozen=True)
class EnvironmentResource:
    """A resource available in an environment."""
    
    resource_id: str
    name: str
    resource_type: str
    
    total_capacity: float
    available_capacity: float
    
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeEnvironment:
    """Runtime environment definition with resources and constraints."""
    
    environment_id: str
    name: str
    environment_type: EnvironmentType
    
    # Resources
    resources: List[EnvironmentResource]
    
    # Configuration
    config_profile: Optional[str] = None
    
    # Constraints
    min_memory_mb: int = 512
    max_memory_mb: int = 65536
    min_cores: int = 1
    max_cores: int = 32
    
    # Labels for selection
    labels: Dict[str, str] = field(default_factory=dict)
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_memory_mb(self) -> int:
        """Get total memory in MB."""
        return sum(r.total_capacity for r in self.resources 
                   if r.resource_type == "memory")
    
    @property
    def total_cores(self) -> int:
        """Get total CPU cores."""
        return sum(int(r.total_capacity) for r in self.resources 
                   if r.resource_type == "cpu")


# =============================================================================
# SERVICE DEFINITIONS
# =============================================================================


class ServiceState(Enum):
    """Service lifecycle states."""
    
    UNREGISTERED = "unregistered"
    REGISTERING = "registering"
    REGISTERED = "registered"
    
    STARTING = "starting"
    RUNNING = "running"
    
    DRAINING = "draining"
    STOPPING = "stopping"
    STOPPED = "stopped"


class HealthStatus(Enum):
    """Service health status."""
    
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class ServiceDependency:
    """A dependency of this service on another."""
    
    service_id: str
    required: bool = True           # If False, service can start without it
    
    health_check_required: bool = True  # Must be healthy before starting


@dataclass(frozen=True)
class ServiceHealthCheck:
    """Health check configuration for a service."""
    
    endpoint: Optional[str] = None      # HTTP endpoint
    command: Optional[str] = None       # Shell command
    interval_seconds: float = 30.0
    timeout_seconds: float = 5.0
    
    healthy_threshold: int = 2
    unhealthy_threshold: int = 3


@dataclass(frozen=True)
class ServiceDefinition:
    """Complete service definition with metadata and configuration."""
    
    service_id: str
    name: str
    version: str
    
    # Lifecycle
    state: ServiceState = ServiceState.UNREGISTERED
    
    # Resources
    memory_mb: int = 256
    cores: float = 1.0
    
    # Dependencies
    dependencies: List[ServiceDependency] = field(default_factory=list)
    
    # Health monitoring
    health_check: Optional[ServiceHealthCheck] = None
    
    # Configuration
    config_profile: Optional[str] = None
    
    # Restart policy
    restart_policy: str = "on_failure"  # always, on_failure, never
    
    # Labels for discovery
    labels: Dict[str, str] = field(default_factory=dict)
    
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    stopped_at_utc: Optional[float] = None


# =============================================================================
# DEPLOYMENT RESULTS (defined before DeploymentManager protocol for reference)
# =============================================================================

@dataclass(frozen=True)
class DeploymentResult:
    """Result of a deployment operation."""
    
    success: bool
    deployment_id: str
    
    version_deployed: ArtifactVersion
    environment_name: str
    
    steps_executed: int = 0
    steps_succeeded: int = 0
    steps_failed: int = 0
    
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


@dataclass(frozen=True)
class RollbackResult:
    """Result of a rollback operation."""
    
    success: bool
    rollback_id: str
    
    version_restored_to: ArtifactVersion
    from_version: ArtifactVersion
    
    steps_executed: int = 0
    steps_succeeded: int = 0
    steps_failed: int = 0
    
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


@dataclass(frozen=True)
class UpgradeResult:
    """Result of an upgrade operation."""
    
    success: bool
    upgrade_id: str
    
    from_version: ArtifactVersion
    to_version: ArtifactVersion
    
    migration_applied: int = 0
    config_migrated: int = 0
    services_restarted: int = 0
    
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


@dataclass(frozen=True)
class DeploymentStatus:
    """Current deployment status."""
    
    version: ArtifactVersion
    state: str  # e.g., "active", "rolling_back", "failed"
    
    active: bool
    healthy: bool
    
    last_deployment_id: Optional[str] = None
    last_rollback_id: Optional[str] = None
    
    deployment_timestamp_utc: Optional[float] = None
    health_check_timestamp_utc: Optional[float] = None


@dataclass(frozen=True)
class HealthCheckResult:
    """Result of a system health check."""
    
    overall_status: str  # "healthy", "degraded", "unhealthy"
    
    components: Dict[str, str]  # component_id -> status
    
    duration_seconds: float = 0.0
    issues: List[Dict[str, Any]] = field(default_factory=list)


# =============================================================================
# DEPLOYMENT MANAGER - ABSTRACT INTERFACE
# =============================================================================


@runtime_checkable
class DeploymentManager(Protocol):
    """
    Protocol for deployment managers.
    
    The canonical authority for all deployment operations in Gordon Core.
    
    Architecture Boundary:
        - One canonical deployment manager per runtime instance
        - All deployments flow through this manager
        - No direct deployment logic elsewhere in the codebase
    
    Contract:
        - Deployments are deterministic (same inputs = same outputs)
        - Rollback is always possible and deterministic
        - Deployment state is persisted and observable
    """
    
    @property
    def current_version(self) -> ArtifactVersion:
        """Get the currently deployed version."""
        ...
    
    async def deploy(
        self,
        artifact: DeploymentArtifact,
        environment: RuntimeEnvironment,
        config_profile: Optional[ConfigurationProfile] = None,
        plan: Optional[DeploymentPlan] = None
    ) -> DeploymentResult:
        """
        Deploy a new version.
        
        Args:
            artifact: The artifact to deploy
            environment: Target runtime environment
            config_profile: Configuration profile to use
            plan: Custom deployment plan (uses default if None)
            
        Returns:
            DeploymentResult with outcome and metadata
            
        Raises:
            DeploymentError: If deployment fails
        """
        ...
    
    async def rollback(
        self,
        to_version: Optional[ArtifactVersion] = None,
        reason: str = "manual_rollback"
    ) -> RollbackResult:
        """
        Rollback to a previous version.
        
        Args:
            to_version: Target version (None = previous version)
            reason: Reason for rollback
            
        Returns:
            RollbackResult with outcome and metadata
            
        Raises:
            RollbackError: If rollback fails
        """
        ...
    
    async def upgrade(
        self,
        from_version: ArtifactVersion,
        to_version: ArtifactVersion,
        config_profile: Optional[ConfigurationProfile] = None
    ) -> UpgradeResult:
        """
        Perform an incremental upgrade.
        
        Args:
            from_version: Current version
            to_version: Target version
            config_profile: Configuration profile (uses current if None)
            
        Returns:
            UpgradeResult with outcome and metadata
            
        Raises:
            UpgradeError: If upgrade fails
        """
        ...
    
    async def get_deployment_status(self) -> DeploymentStatus:
        """Get current deployment status."""
        ...
    
    async def health_check(self) -> HealthCheckResult:
        """Perform system health check."""
        ...
    
    def snapshot(self) -> Dict[str, Any]:
        """Get an immutable snapshot of deployment state."""
        ...


# =============================================================================
# LIFECYCLE MANAGER - ABSTRACT INTERFACE
# =============================================================================


@runtime_checkable
class LifecycleManager(Protocol):
    """
    Protocol for lifecycle managers.
    
    Canonical authority for all component/service lifecycle transitions.
    """
    
    async def get_state(self, component_id: str) -> LifecycleState:
        """Get current state of a component."""
        ...
    
    async def transition(
        self,
        request: LifecycleTransitionRequest
    ) -> LifecycleTransitionResult:
        """
        Perform a lifecycle transition.
        
        Args:
            request: Transition request with source and target states
            
        Returns:
            Result with success status and duration
            
        Raises:
            LifecycleError: If transition is invalid or fails
        """
        ...
    
    async def register_hook(
        self,
        hook: LifecycleHook,
        handler: Callable[[LifecycleHookEvent], Any]
    ) -> str:
        """Register a lifecycle hook handler. Returns handler_id."""
        ...
    
    async def unregister_hook(self, handler_id: str) -> bool:
        """Unregister a lifecycle hook handler."""
        ...
    
    def snapshot(self) -> Dict[str, Any]:
        """Get an immutable snapshot of lifecycle state."""
        ...


# =============================================================================
# CONFIGURATION MANAGER - ABSTRACT INTERFACE
# =============================================================================


@runtime_checkable
class ConfigurationLoader(Protocol):
    """Protocol for configuration loaders."""
    
    async def load_profile(
        self,
        profile_name: str,
        environment_name: Optional[str] = None
    ) -> ConfigurationProfile:
        """Load a configuration profile."""
        ...
    
    async def validate_profile(
        self,
        profile: ConfigurationProfile
    ) -> bool:
        """Validate a configuration profile."""
        ...
    
    def list_profiles(self) -> List[str]:
        """List available configuration profiles."""
        ...


# =============================================================================
# ENVIRONMENT MANAGER - ABSTRACT INTERFACE
# =============================================================================


@runtime_checkable
class EnvironmentValidator(Protocol):
    """Protocol for environment validators."""
    
    async def validate_environment(
        self,
        environment: RuntimeEnvironment
    ) -> bool:
        """Validate that an environment meets requirements."""
        ...
    
    async def check_compatibility(
        self,
        artifact: DeploymentArtifact,
        environment: RuntimeEnvironment
    ) -> bool:
        """Check if artifact is compatible with environment."""
        ...


@runtime_checkable
class InstallationManager(Protocol):
    """Protocol for installation managers."""
    
    async def install(
        self,
        artifact: DeploymentArtifact,
        environment: RuntimeEnvironment,
        config_profile: Optional[ConfigurationProfile] = None
    ) -> "InstallationResult":
        ...
    
    async def uninstall(
        self,
        artifact_id: str,
        environment_name: str
    ) -> "UninstallResult":
        ...


# =============================================================================
# INSTALLATION RESULTS (defined after InstallationManager protocol for forward refs)
# =============================================================================

@dataclass(frozen=True)
class InstallationResult:
    """Result of an installation operation."""
    
    success: bool
    installation_id: str
    
    version_installed: ArtifactVersion
    component_count: int = 0
    
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


@dataclass(frozen=True)
class UninstallResult:
    """Result of an uninstall operation."""
    
    success: bool
    uninstall_id: str
    
    components_removed: int = 0
    
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Exception hierarchy
    "DeploymentError",
    "InstallationError",
    "ConfigurationError",
    "LifecycleError",
    "UpgradeError",
    "RollbackError",
    "EnvironmentError",
    "ServiceManagementError",
    "MonitoringError",
    "DiagnosticsError",
    "ProvisioningError",
    "OperationalOrchestrationError",
    "InfrastructureGovernanceError",
    
    # Lifecycle model
    "LifecycleState",
    "LifecycleTransition",
    "LifecycleTransitionRequest",
    "LifecycleTransitionResult",
    
    # Lifecycle hooks
    "LifecycleHook",
    "LifecycleHookEvent",
    
    # Artifacts
    "ArtifactType",
    "ArtifactVersion",
    "DeploymentArtifact",
    
    # Plans
    "DeploymentAction",
    "DeploymentStep",
    "DeploymentPlan",
    
    # Configuration
    "ConfigurationLayer",
    "ConfigurationOption",
    "ConfigurationProfile",
    
    # Environments
    "EnvironmentType",
    "EnvironmentResource",
    "RuntimeEnvironment",
    
    # Services
    "ServiceState",
    "HealthStatus",
    "ServiceDependency",
    "ServiceHealthCheck",
    "ServiceDefinition",
    
    # Results (defined before interfaces)
    "DeploymentResult",
    "RollbackResult",
    "UpgradeResult",
    "DeploymentStatus",
    "HealthCheckResult",
    
    # Manager interfaces
    "DeploymentManager",
    "LifecycleManager",
    "ConfigurationLoader",
    "EnvironmentValidator",
    "InstallationManager",
    
    # Installation results
    "InstallationResult",
    "UninstallResult",
]