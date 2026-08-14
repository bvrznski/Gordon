"""Environment Architecture - environment definitions, contracts, and policies.

Phase 3.29: Deployment, Environment & Infrastructure Architecture
==================================================================

This module provides the canonical infrastructure for:
- Environment type definitions
- Environment guarantees and restrictions
- Environment policy enforcement
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EnvironmentType(Enum):
    """Types of runtime environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    INTEGRATION = "integration"
    STAGING = "staging"
    PRODUCTION = "production"
    SIMULATION = "simulation"
    BENCHMARK = "benchmark"
    RECOVERY = "recovery"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


@dataclass(frozen=True)
class EnvironmentGuarantees:
    """What an environment guarantees."""

    availability: str  # e.g., "99.9%", "best_effort", "none"
    debugging_enabled: bool
    external_connections: bool
    data_isolation: bool
    performance_limits: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class EnvironmentRestrictions:
    """What is prohibited in an environment."""

    no_production_data: bool
    limited_resources: bool
    read_only_access: bool
    external_dependencies_allowed: bool = False


@dataclass(frozen=True)
class EnvironmentPolicy:
    """Deployment policies for an environment."""

    deployment_mode: str  # "manual", "automated", "scheduled"
    rollback_enabled: bool
    validation_required: bool
    health_check_required: bool
    maintenance_window_only: bool = False


@dataclass
class EnvironmentConfig:
    """Configuration for a specific environment."""

    name: str
    environment_type: EnvironmentType
    guarantees: EnvironmentGuarantees
    restrictions: EnvironmentRestrictions
    policy: EnvironmentPolicy
    infrastructure_requirements: Dict[str, Any]
    resource_limits: Optional[Dict[str, Any]] = None

    @classmethod
    def create_development(cls) -> "EnvironmentConfig":
        """Create development environment configuration."""
        return cls(
            name="development",
            environment_type=EnvironmentType.DEVELOPMENT,
            guarantees=EnvironmentGuarantees(
                availability="best_effort",
                debugging_enabled=True,
                external_connections=True,
                data_isolation=False,
            ),
            restrictions=EnvironmentRestrictions(
                no_production_data=True,
                limited_resources=False,
                read_only_access=False,
                external_dependencies_allowed=True,
            ),
            policy=EnvironmentPolicy(
                deployment_mode="manual",
                rollback_enabled=True,
                validation_required=False,
                health_check_required=False,
            ),
            infrastructure_requirements={
                "cpu": {"min": 2, "max": None},
                "memory": {"min": "4GB", "max": None},
                "storage": {"min": "10GB", "max": None},
            },
        )

    @classmethod
    def create_testing(cls) -> "EnvironmentConfig":
        """Create testing environment configuration."""
        return cls(
            name="testing",
            environment_type=EnvironmentType.TESTING,
            guarantees=EnvironmentGuarantees(
                availability="best_effort",
                debugging_enabled=False,
                external_connections=True,
                data_isolation=True,
            ),
            restrictions=EnvironmentRestrictions(
                no_production_data=True,
                limited_resources=False,
                read_only_access=False,
                external_dependencies_allowed=False,
            ),
            policy=EnvironmentPolicy(
                deployment_mode="automated",
                rollback_enabled=True,
                validation_required=True,
                health_check_required=True,
            ),
            infrastructure_requirements={
                "cpu": {"min": 4, "max": None},
                "memory": {"min": "8GB", "max": None},
                "storage": {"min": "20GB", "max": None},
            },
        )

    @classmethod
    def create_staging(cls) -> "EnvironmentConfig":
        """Create staging environment configuration."""
        return cls(
            name="staging",
            environment_type=EnvironmentType.STAGING,
            guarantees=EnvironmentGuarantees(
                availability="99.9%",
                debugging_enabled=False,
                external_connections=True,
                data_isolation=True,
                performance_limits={"latency_max": "100ms"},
            ),
            restrictions=EnvironmentRestrictions(
                no_production_data=False,  # May use production-like data
                limited_resources=True,
                read_only_access=False,
                external_dependencies_allowed=True,
            ),
            policy=EnvironmentPolicy(
                deployment_mode="automated",
                rollback_enabled=True,
                validation_required=True,
                health_check_required=True,
                maintenance_window_only=False,
            ),
            infrastructure_requirements={
                "cpu": {"min": 8, "max": None},
                "memory": {"min": "16GB", "max": None},
                "storage": {"min": "50GB", "max": None},
            },
        )

    @classmethod
    def create_production(cls) -> "EnvironmentConfig":
        """Create production environment configuration."""
        return cls(
            name="production",
            environment_type=EnvironmentType.PRODUCTION,
            guarantees=EnvironmentGuarantees(
                availability="99.95%",
                debugging_enabled=False,
                external_connections=True,
                data_isolation=True,
                performance_limits={"latency_max": "50ms", "throughput_min": 1000},
            ),
            restrictions=EnvironmentRestrictions(
                no_production_data=False,
                limited_resources=True,
                read_only_access=False,
                external_dependencies_allowed=True,
            ),
            policy=EnvironmentPolicy(
                deployment_mode="scheduled",
                rollback_enabled=True,
                validation_required=True,
                health_check_required=True,
                maintenance_window_only=True,
            ),
            infrastructure_requirements={
                "cpu": {"min": 16, "max": None},
                "memory": {"min": "32GB", "max": None},
                "storage": {"min": "100GB", "max": None},
                "network": {"bandwidth_min": "1Gbps"},
            },
        )

    @classmethod
    def create_environment(cls, name: str, env_type: EnvironmentType) -> "EnvironmentConfig":
        """Create environment configuration by type."""
        creators = {
            EnvironmentType.DEVELOPMENT: cls.create_development,
            EnvironmentType.TESTING: cls.create_testing,
            EnvironmentType.STAGING: cls.create_staging,
            EnvironmentType.PRODUCTION: cls.create_production,
        }
        if env_type in creators:
            return creators[env_type]()
        raise ValueError(f"Unsupported environment type: {env_type}")


class EnvironmentRegistry:
    """Registry of available environments."""

    def __init__(self):
        self._environments: Dict[str, EnvironmentConfig] = {}
        self._register_default_environments()

    def _register_default_environments(self) -> None:
        """Register default environment configurations."""
        for env_type in EnvironmentType:
            try:
                config = EnvironmentConfig.create_environment("default", env_type)
                self._environments[env_type.value] = config
            except ValueError:
                pass  # Some types don't have creators yet

    def get_environment(self, name: str) -> Optional[EnvironmentConfig]:
        """Get environment configuration by name."""
        return self._environments.get(name.lower())

    def list_environments(self) -> List[str]:
        """List all registered environment names."""
        return list(self._environments.keys())

    def validate_environment_compatibility(
        self,
        environment: EnvironmentConfig,
        artifact_requirements: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate that an environment can support a deployment.

        Args:
            environment: Target environment configuration
            artifact_requirements: Deployment requirements

        Returns:
            Validation result with compatibility status and issues
        """
        issues = []

        # Check infrastructure requirements
        env_reqs = environment.infrastructure_requirements
        for req_key, req_value in artifact_requirements.get("infrastructure", {}).items():
            if req_key in env_reqs:
                env_min = env_reqs[req_key].get("min")
                if env_min and self._compare_resources(req_value, env_min) < 0:
                    issues.append(
                        f"Artifact requires {req_key}: {req_value}, "
                        f"but environment minimum is {env_min}"
                    )

        return {
            "compatible": len(issues) == 0,
            "environment": environment.name,
            "issues": issues,
        }

    def _compare_resources(self, a: Any, b: Any) -> int:
        """Compare two resource values. Returns -1 if a < b, 0 if equal, 1 if a > b."""
        try:
            # Simple numeric comparison for now
            a_val = float(str(a).replace("GB", "").replace("ms", ""))
            b_val = float(str(b).replace("GB", "").replace("ms", ""))
            return -1 if a_val < b_val else (0 if a_val == b_val else 1)
        except (ValueError, AttributeError):
            # If comparison fails, assume compatible
            return 0


__all__ = [
    "EnvironmentType",
    "EnvironmentGuarantees",
    "EnvironmentRestrictions", 
    "EnvironmentPolicy",
    "EnvironmentConfig",
    "EnvironmentRegistry",
]