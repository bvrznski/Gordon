"""Deployment Architecture - canonical deployment, environment, and infrastructure layer.

Phase 3.29: Deployment, Environment & Infrastructure Architecture
==================================================================

This package provides the canonical infrastructure for:
- Canonical Deployment Architecture
- Environment Management
- Infrastructure Abstraction
- Runtime Deployment Model
- Deployment Descriptors
- Topology Management
- Provisioning & Placement
- Dependency Management
- Policy Enforcement
- Installation Workflows
- Scaling Contracts
- Environment Isolation
- Diagnostics & Health
- Validation & Certification

Architecture Boundary:
---------------------
Deployment is an infrastructure concern. It:

DOES NOT own:
- Core semantics
- Runtime behavior
- State management  
- Communication protocols
- Security policies (enforcement)
- Identity management (ownership)

OWNS:
- Infrastructure provisioning
- Environment selection
- Deployment orchestration
- Resource allocation
- Topology management

CANONICAL ARCHITECTURE COMPONENTS:
- deployment.py - Deployment architecture and contracts
- environment.py - Environment definitions and policies  
- infrastructure.py - Infrastructure abstraction layer
- topology.py - Topology management
- provisioning.py - Provisioning workflows
- descriptors.py - Deployment descriptors (manifests)
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .deployment import (
        DeploymentId,
        DeploymentRecord,
        DeploymentState,
        DeploymentPhase,
        DeploymentContract,
        DeploymentManager,
        DeploymentValidator,
    )
    
    from .environment import (
        EnvironmentType,
        EnvironmentConfig,
        EnvironmentGuarantees,
        EnvironmentRestrictions,
        EnvironmentPolicy,
        EnvironmentRegistry,
    )
    
    from .infrastructure import (
        InfrastructureLayer,
        InfrastructureCapability,
        InfrastructureProfile,
        SubsystemInterface,
        InfrastructureValidator,
    )
    
    from .topology import (
        TopologyType,
        TopologyNode,
        TopologyComponent,
        TopologyConnection,
        TopologyManifest,
    )
    
    from .provisioning import (
        ResourceRequirement,
        PlacementPolicy,
        ProvisioningWorkflow,
        Provisioner,
    )
    
    from .descriptors import (
        RuntimeManifest,
        DeploymentManifest,
        InfrastructureManifest,
        CapabilityManifest,
        DependencyManifest,
        EnvironmentManifest,
        TopologyManifest,
    )
    
    from .policies import (
        PolicyType,
        PlacementPolicy,
        ProvisioningPolicy,
        ResourcePolicy,
        RedundancyPolicy,
        IsolationPolicy,
        ScalingPolicy,
        MaintenancePolicy,
        PolicyEngine,
    )
    
    from .validation import (
        DeploymentValidator,
        InfrastructureValidator,
        EnvironmentValidator,
        TopologyValidator,
    )

__all__ = [
    # Core deployment
    "deployment",
    # Environment management
    "environment",
    # Infrastructure abstraction
    "infrastructure",
    # Topology management  
    "topology",
    # Provisioning
    "provisioning",
    # Descriptors (manifests)
    "descriptors",
    # Policies
    "policies",
    # Validation
    "validation",
]