# Deployment, Operations & Lifecycle Infrastructure
# ==================================================

"""
Phase 3.8.10 - Deployment, Operations & Lifecycle Infrastructure

This package provides the canonical infrastructure for:
    - Installation and deployment workflows
    - Runtime environment management
    - Configuration and provisioning
    - Service lifecycle management
    - Monitoring, diagnostics and operations
    - Upgrade and rollback operations
    - Operational governance and orchestration

ARCHITECTURAL PRINCIPLES:
    - Deployments are deterministic
    - Runtime environments are reproducible
    - Configuration is explicit and versioned
    - Operational state is observable
    - Lifecycle transitions are controlled
    - Rollback paths are defined
    - Deployment contracts are stable
    - Duplicate deployment logic is prohibited
    - Operational actions are auditable
    - Infrastructure is modular and replaceable

SUBMODULES:
    - core: Canonical abstractions and interfaces
    - installation: Installation workflows and provisioners
    - pipeline: Deployment pipelines, upgrades, rollback & releases
    - services: Service management framework
    - orchestration: Runtime integration & governance
    - monitoring: Monitoring, health and diagnostics

ARCHITECTURE OVERVIEW:
    
    The Deployment Infrastructure is organized into layers:
    
    Layer 1: Core Abstractions (core.py)
        - Exception hierarchy (DeploymentError, InstallationError, etc.)
        - Lifecycle model with states and transitions
        - Artifacts with versioning
        - Plans for deployment and provisioning
        - Configuration profiles
        - Runtime environments
        - Service definitions
    
    Layer 2: Foundational Services (installation.py)
        - InstallationManager for deploying artifacts
        - ConfigurationLoader for loading configuration profiles
        - EnvironmentProvisioner for environment setup
    
    Layer 3: Pipeline & Release Management (pipeline.py)
        - DeploymentPipelineManager for orchestrating deployments
        - ReleaseOrchestrator for managing releases
        - UpgradeManager for version upgrades
        - RollbackManager for rollbacks
        - VerificationManager for deployment verification
    
    Layer 4: Service & Monitoring (services.py)
        - ServiceLifecycleManager for service lifecycle
        - HealthMonitor for health evaluation
        - DiagnosticsRunner for diagnostics execution
        - ServiceOperations for operational utilities
    
    Layer 5: Orchestration & Governance (orchestration.py)
        - DeploymentOrchestrator for cross-stage coordination
        - InfrastructureGovernance for policy enforcement
        - LifecycleCoordinator for lifecycle transitions
        - OperationalAutomation for automated operations

OPERATIONAL MODEL:
    
    Deployments flow through the orchestration layer which coordinates:
        1. Planning phase (create deployment plan)
        2. Validation phase (check policies and constraints)
        3. Execution phase (run pipeline steps)
        4. Verification phase (validate deployment success)
        5. Notification phase (inform stakeholders)

    Rollbacks follow a deterministic path using recorded state:
        1. Identify current version
        2. Determine target version (previous or specified)
        3. Create rollback plan with reverse of deployment steps
        4. Execute plan in dependency order
        5. Verify restored state

EXAMPLE USAGE:
    
    from src.agent.components.core.deployment import (
        DeploymentManager,
        ArtifactVersion,
        RuntimeEnvironment,
        ConfigurationProfile,
        InstallationManager,
        ServiceLifecycleManager,
    )
    
    # Create environment
    environment = RuntimeEnvironment(
        environment_id="prod-1",
        name="production",
        environment_type=None,
        resources=[]
    )
    
    # Load configuration
    loader = ConfigurationLoader()
    config_profile = await loader.load_profile("production", "production")
    
    # Install deployment
    installer = InstallationManager()
    result = await installer.install(artifact, environment, config_profile)
"""

# Import core abstractions
from .core import (
    DeploymentError,
    InstallationError,
    ConfigurationError,
    LifecycleError,
    UpgradeError,
    RollbackError,
    EnvironmentError,
    InstallationWorkflowError,
    BootstrapError,
    ReadinessError,
    EnvironmentCompatibilityError,
    ServiceManagementError,
    MonitoringError,
    DiagnosticsError,
    ProvisioningError,
    OperationalOrchestrationError,
    InfrastructureGovernanceError,
    
    LifecycleState,
    LifecycleTransition,
    LifecycleTransitionRequest,
    LifecycleTransitionResult,
    LifecycleHook,
    LifecycleHookEvent,
    
    ArtifactType,
    ArtifactVersion,
    DeploymentArtifact,
    
    DeploymentAction,
    DeploymentStep,
    DeploymentPlan,
    
    ConfigurationLayer,
    ConfigurationOption,
    ConfigurationProfile,
    
    EnvironmentType,
    EnvironmentResource,
    RuntimeEnvironment,
    
    ServiceState,
    HealthStatus,
    ServiceDependency,
    ServiceHealthCheck,
    ServiceDefinition,
    
    DeploymentResult,
    RollbackResult,
    UpgradeResult,
    DeploymentStatus,
    HealthCheckResult,
    InstallationResult,
    UninstallResult,
    
    DeploymentManager,
    LifecycleManager,
    ConfigurationLoader,
    EnvironmentValidator,
    InstallationManager,
)

# Import pipeline framework
from .pipeline import (
    PipelineStage,
    PipelineStep,
    DeploymentPipeline,
    
    ReleaseStage,
    ReleaseArtifact,
    Release,
    
    UpgradeMode,
    UpgradePlan,
    
    RollbackPlan,
    RollbackExecutionResult,
    
    VerificationType,
    VerificationStep,
    DeploymentVerificationResult,
    
    DeploymentPipelineManager,
    ReleaseOrchestrator,
    UpgradeManager,
    RollbackManager,
    VerificationManager,
)

# Import services framework
from .services import (
    ServiceStateTransition,
    ServiceLifecycleEvent,
    
    HealthProbeResult,
    HealthCheckReport,
    
    ServiceRegistration,
    DependencyGraph,
    
    StartResult,
    ServiceStartRequest,
    ServiceStopRequest,
    
    ServiceLifecycleResult,
    HealthCheckResult as ServiceHealthCheckResult,
    ServiceSnapshot,
    
    ServiceLifecycleManager,
    HealthMonitor,
    DiagnosticsRunner,
    ServiceOperations,
)

# Import orchestration framework
from .orchestration import (
    OrchestrationPhase,
    OrchestrationStep,
    OrchestrationPlan,
    
    PolicyType,
    PolicyResult,
    PolicyRule,
    PolicyEvaluation,
    
    LifecyclePhase,
    LifecycleCoordinatorEvent,
    
    DeploymentOrchestrator,
    InfrastructureGovernance,
    LifecycleCoordinator,
    OperationalAutomation,
    
    MaintenanceWindow,
    DeploymentReport,
)

__all__ = [
    # Core exceptions
    "DeploymentError",
    "InstallationError",
    "ConfigurationError",
    "LifecycleError",
    "UpgradeError",
    "RollbackError",
    "EnvironmentError",
    "InstallationWorkflowError",
    "BootstrapError",
    "ReadinessError",
    "EnvironmentCompatibilityError",
    "ServiceManagementError",
    "MonitoringError",
    "DiagnosticsError",
    "ProvisioningError",
    "OperationalOrchestrationError",
    "InfrastructureGovernanceError",
    
    # Core abstractions
    "LifecycleState",
    "LifecycleTransition",
    "LifecycleTransitionRequest",
    "LifecycleTransitionResult",
    "LifecycleHook",
    "LifecycleHookEvent",
    
    "ArtifactType",
    "ArtifactVersion",
    "DeploymentArtifact",
    
    "DeploymentAction",
    "DeploymentStep",
    "DeploymentPlan",
    
    "ConfigurationLayer",
    "ConfigurationOption",
    "ConfigurationProfile",
    
    "EnvironmentType",
    "EnvironmentResource",
    "RuntimeEnvironment",
    
    "ServiceState",
    "HealthStatus",
    "ServiceDependency",
    "ServiceHealthCheck",
    "ServiceDefinition",
    
    "DeploymentResult",
    "RollbackResult",
    "UpgradeResult",
    "DeploymentStatus",
    "HealthCheckResult",
    "InstallationResult",
    "UninstallResult",
    
    # Manager interfaces
    "DeploymentManager",
    "LifecycleManager",
    "ConfigurationLoader",
    "EnvironmentValidator",
    "InstallationManager",
    
    # Pipeline framework
    "PipelineStage",
    "PipelineStep",
    "DeploymentPipeline",
    
    "ReleaseStage",
    "ReleaseArtifact",
    "Release",
    
    "UpgradeMode",
    "UpgradePlan",
    
    "RollbackPlan",
    "RollbackExecutionResult",
    
    "VerificationType",
    "VerificationStep",
    "DeploymentVerificationResult",
    
    "DeploymentPipelineManager",
    "ReleaseOrchestrator",
    "UpgradeManager",
    "RollbackManager",
    "VerificationManager",
    
    # Services framework
    "ServiceStateTransition",
    "ServiceLifecycleEvent",
    
    "HealthProbeResult",
    "HealthCheckReport",
    
    "ServiceRegistration",
    "DependencyGraph",
    
    "StartResult",
    "ServiceStartRequest",
    "ServiceStopRequest",
    
    "ServiceLifecycleResult",
    "ServiceHealthCheckResult",
    "ServiceSnapshot",
    
    "ServiceLifecycleManager",
    "HealthMonitor",
    "DiagnosticsRunner",
    "ServiceOperations",
    
    # Orchestration framework
    "OrchestrationPhase",
    "OrchestrationStep",
    "OrchestrationPlan",
    
    "PolicyType",
    "PolicyResult",
    "PolicyRule",
    "PolicyEvaluation",
    
    "LifecyclePhase",
    "LifecycleCoordinatorEvent",
    
    "DeploymentOrchestrator",
    "InfrastructureGovernance",
    "LifecycleCoordinator",
    "OperationalAutomation",
    
    "MaintenanceWindow",
    "DeploymentReport",
]