"""Deployment Architecture - canonical deployment contracts and orchestration.

Phase 3.29: Deployment, Environment & Infrastructure Architecture
==================================================================

This module provides the canonical infrastructure for:
- Deployment identity and ownership
- Deployment lifecycle management  
- Deployment validation
- Deployment health monitoring

ARCHITECTURE BOUNDARY:
- DOES NOT own runtime semantics or behavior
- DOES NOT own state persistence (handled by Phase 3.28)
- DOES NOT own security policies (enforcement is separate)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class DeploymentId:
    """Unique identifier for a deployment."""

    def __init__(self, value: Optional[str] = None):
        self._value = value or str(uuid4())

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeploymentId):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)


class DeploymentPhase(Enum):
    """Phases of the canonical deployment lifecycle."""

    INFRASTRUCTURE_DISCOVERY = "infrastructure_discovery"
    ENVIRONMENT_SELECTION = "environment_selection"
    DEPENDENCY_VALIDATION = "dependency_validation"
    PROVISIONING = "provisioning"
    INSTALLATION = "installation"
    CONFIGURATION = "configuration"
    DEPLOYMENT_VALIDATION = "deployment_validation"
    RUNTIME_ACTIVATION = "runtime_activation"
    HEALTH_VERIFICATION = "health_verification"
    OPERATIONAL = "operational"


class DeploymentState(Enum):
    """States in deployment lifecycle."""

    DECLARED = "declared"           # Metadata exists, no runtime created
    PREPARING = "preparing"         # Infrastructure discovery underway
    PROVISIONING = "provisioning"   # Resources being allocated
    INSTALLING = "installing"       # Software components being installed
    CONFIGURING = "configuring"     # Configuration being applied
    VALIDATING = "validating"       # Deployment integrity being verified
    ACTIVATING = "activating"       # Runtime being started
    HEALTHY = "healthy"             # Fully operational
    UNHEALTHY = "unhealthy"         # In degraded state
    ROLLED_BACK = "rolled_back"     # Rolled back after failure
    DECOMMISSIONED = "decommissioned"  # Deployment retired


@dataclass(frozen=True)
class DeploymentContract:
    """Contract defining deployment requirements and guarantees."""

    identity: str
    version: str
    environment_type: str
    runtime_profile: str
    infrastructure_profile: str
    topology_specification: Dict[str, Any]
    dependency_requirements: List[Dict[str, Any]]
    policy_requirements: List[str]

    @classmethod
    def create(
        cls,
        identity: str,
        version: str,
        environment_type: str,
        runtime_profile: str,
        infrastructure_profile: str,
        topology_specification: Dict[str, Any],
        dependency_requirements: List[Dict[str, Any]],
        policy_requirements: List[str],
    ) -> "DeploymentContract":
        return cls(
            identity=identity,
            version=version,
            environment_type=environment_type,
            runtime_profile=runtime_profile,
            infrastructure_profile=infrastructure_profile,
            topology_specification=topology_specification,
            dependency_requirements=dependency_requirements,
            policy_requirements=policy_requirements,
        )


@dataclass
class DeploymentRecord:
    """Immutable deployment record with full provenance."""

    deployment_id: str
    version_sequence: int
    generation_epoch: int
    timestamp_utc: float
    environment: str
    runtime_profile: str
    infrastructure_profile: str
    topology_hash: str
    status: DeploymentState
    phase: DeploymentPhase
    owner_identity: str

    @classmethod
    def create(
        cls,
        deployment_id: str,
        version_sequence: int,
        generation_epoch: int,
        timestamp_utc: float,
        environment: str,
        runtime_profile: str,
        infrastructure_profile: str,
        topology_hash: str,
        status: DeploymentState,
        phase: DeploymentPhase,
        owner_identity: str,
    ) -> "DeploymentRecord":
        return cls(
            deployment_id=deployment_id,
            version_sequence=version_sequence,
            generation_epoch=generation_epoch,
            timestamp_utc=timestamp_utc,
            environment=environment,
            runtime_profile=runtime_profile,
            infrastructure_profile=infrastructure_profile,
            topology_hash=topology_hash,
            status=status,
            phase=phase,
            owner_identity=owner_identity,
        )


class DeploymentManager:
    """Canonical authority for deployment operations."""

    def __init__(self):
        self._deployments: Dict[str, DeploymentRecord] = {}
        self._validation_errors: List[str] = []

    async def deploy(
        self,
        artifact: str,
        environment_name: str,
        runtime_profile: Optional[str] = None,
        infrastructure_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deploy an artifact to a target environment.

        Args:
            artifact: Artifact identifier (name:version)
            environment_name: Target environment name
            runtime_profile: Optional runtime profile specification
            infrastructure_profile: Optional infrastructure requirements

        Returns:
            Deployment result with status and deployment_id
        """
        # Validate prerequisites
        if not self._validate_prerequisites(
            artifact, environment_name, runtime_profile, infrastructure_profile
        ):
            return {
                "success": False,
                "error": "Prerequisites validation failed",
                "validation_errors": self._validation_errors,
            }

        # Create deployment record
        deployment_id = str(uuid4())
        timestamp = 0.0  # Will be set by caller

        record = DeploymentRecord.create(
            deployment_id=deployment_id,
            version_sequence=1,
            generation_epoch=1,
            timestamp_utc=timestamp,
            environment=environment_name,
            runtime_profile=runtime_profile or "default",
            infrastructure_profile=infrastructure_profile or "minimal",
            topology_hash="pending",
            status=DeploymentState.PREPARING,
            phase=DeploymentPhase.INFRASTRUCTURE_DISCOVERY,
            owner_identity="deployment_manager",
        )

        self._deployments[deployment_id] = record

        return {
            "success": True,
            "deployment_id": deployment_id,
            "status": "initiated",
            "phase": DeploymentPhase.INFRASTRUCTURE_DISCOVERY.value,
        }

    async def rollback(self, deployment_id: str) -> Dict[str, Any]:
        """Rollback a failed deployment.

        Args:
            deployment_id: ID of the deployment to rollback

        Returns:
            Rollback result with status
        """
        if deployment_id not in self._deployments:
            return {
                "success": False,
                "error": f"Deployment {deployment_id} not found",
            }

        record = self._deployments[deployment_id]
        # Update to rollback state
        new_record = DeploymentRecord.create(
            deployment_id=record.deployment_id,
            version_sequence=record.version_sequence + 1,
            generation_epoch=record.generation_epoch,
            timestamp_utc=0.0,  # Will be set by caller
            environment=record.environment,
            runtime_profile=record.runtime_profile,
            infrastructure_profile=record.infrastructure_profile,
            topology_hash=record.topology_hash,
            status=DeploymentState.ROLLED_BACK,
            phase=DeploymentPhase.INFRASTRUCTURE_DISCOVERY,
            owner_identity=record.owner_identity,
        )
        self._deployments[deployment_id] = new_record

        return {
            "success": True,
            "deployment_id": deployment_id,
            "status": "rolled_back",
        }

    def _validate_prerequisites(
        self,
        artifact: str,
        environment_name: str,
        runtime_profile: Optional[str],
        infrastructure_profile: Optional[str],
    ) -> bool:
        """Validate deployment prerequisites."""
        self._validation_errors = []

        # Check artifact exists (placeholder - would check registry)
        if not artifact or ":" not in artifact:
            self._validation_errors.append(
                f"Invalid artifact format: {artifact}. Expected 'name:version'"
            )

        # Check environment is valid
        valid_environments = [
            "development",
            "testing",
            "integration",
            "staging",
            "production",
            "simulation",
            "benchmark",
            "recovery",
            "maintenance",
            "offline",
        ]
        if environment_name.lower() not in valid_environments:
            self._validation_errors.append(
                f"Invalid environment: {environment_name}. Valid options: {valid_environments}"
            )

        return len(self._validation_errors) == 0


class DeploymentValidator:
    """Canonical deployment validation authority."""

    def __init__(self):
        self._errors: List[str] = []
        self._warnings: List[str] = []

    @classmethod
    def validate_deployment(
        cls,
        artifact: str,
        environment_name: str,
        runtime_profile: Optional[str],
        infrastructure_profile: Optional[str],
    ) -> Dict[str, Any]:
        """Validate a deployment specification.

        Returns validation result with any errors or warnings.
        """
        validator = cls()
        return validator._validate(artifact, environment_name, runtime_profile, infrastructure_profile)

    def _validate(
        self,
        artifact: str,
        environment_name: str,
        runtime_profile: Optional[str],
        infrastructure_profile: Optional[str],
    ) -> Dict[str, Any]:
        """Perform validation."""
        self._errors = []
        self._warnings = []

        # Validate artifact format
        if not artifact or ":" not in artifact:
            self._errors.append("Artifact must be in 'name:version' format")

        # Validate environment
        valid_environments = [
            "development",
            "testing",  
            "integration",
            "staging",
            "production",
            "simulation",
            "benchmark",
            "recovery",
            "maintenance",
            "offline",
        ]
        if environment_name.lower() not in valid_environments:
            self._errors.append(f"Invalid environment: {environment_name}")

        # Validate runtime profile (if specified)
        if runtime_profile:
            valid_profiles = ["default", "development", "production"]
            if runtime_profile.lower() not in valid_profiles:
                self._warnings.append(
                    f"Runtime profile '{runtime_profile}' may be undefined"
                )

        return {
            "valid": len(self._errors) == 0,
            "errors": self._errors,
            "warnings": self._warnings,
        }


__all__ = [
    "DeploymentId",
    "DeploymentPhase", 
    "DeploymentState",
    "DeploymentContract",
    "DeploymentRecord",
    "DeploymentManager",
    "DeploymentValidator",
]