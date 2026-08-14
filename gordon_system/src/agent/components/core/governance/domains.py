# Runtime Governance Domains
# ==========================

"""
Governance domains - specialized areas of governance responsibility.

Each domain has:
- Authority: Explicit authorization to govern its area
- Ownership: Clear ownership of artifacts
- Policies: Domain-specific policies
- Diagnostics: Domain-specific observability
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum, auto
import uuid
import time


# =============================================================================
# BASE DOMAIN INTERFACE
# =============================================================================

@dataclass(frozen=True)
class GovernanceDomain:
    """
    Base class for governance domains.
    
    Every domain must have authority, ownership, policies, and diagnostics.
    """
    
    domain_id: str
    name: str
    description: str
    scope: str  # Runtime, service, component, etc.
    enabled: bool = True
    
    @property
    def domain_type(self) -> str:
        """Return the type of governance domain."""
        return self.__class__.__name__
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for a domain."""
        return f"governance_domain_{uuid.uuid4().hex[:12]}"


# =============================================================================
# RUNTIME GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class RuntimeGovernanceDomain(GovernanceDomain):
    """
    Governance domain for runtime behavior.
    
    Supervises:
    - Runtime lifecycle transitions
    - Runtime state consistency
    - Runtime resource allocation
    - Cross-domain coordination
    """
    
    def __init__(self):
        super().__init__(
            domain_id="runtime_governance",
            name="Runtime Governance Domain",
            description="Governs runtime-level behavior and cross-cutting concerns",
            scope="runtime",
        )


# =============================================================================
# RESOURCE GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class ResourceGovernanceDomain(GovernanceDomain):
    """
    Governance domain for resource management.
    
    Supervises:
    - CPU utilization
    - Memory consumption
    - I/O bandwidth
    - Network capacity
    """
    
    max_cpu_percent: float = 90.0
    max_memory_percent: float = 85.0
    max_io_mbps: float = 1000.0
    max_network_mbps: float = 100.0
    
    def __init__(self):
        super().__init__(
            domain_id="resource_governance",
            name="Resource Governance Domain",
            description="Governs resource allocation and utilization",
            scope="runtime",
        )


# =============================================================================
# EXECUTION GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class ExecutionGovernanceDomain(GovernanceDomain):
    """
    Governance domain for execution control.
    
    Supervises:
    - Task execution ordering
    - Execution concurrency limits
    - Execution timeouts
    - Execution priority
    """
    
    max_concurrent_executions: int = 100
    default_timeout_seconds: float = 30.0
    max_execution_depth: int = 10
    
    def __init__(self):
        super().__init__(
            domain_id="execution_governance",
            name="Execution Governance Domain",
            description="Governs execution behavior and constraints",
            scope="runtime",
        )


# =============================================================================
# LIFECYCLE GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class LifecycleGovernanceDomain(GovernanceDomain):
    """
    Governance domain for lifecycle management.
    
    Supervises:
    - Component startup/shutdown ordering
    - Health check compliance
    - State transitions
    - Graceful degradation
    """
    
    def __init__(self):
        super().__init__(
            domain_id="lifecycle_governance",
            name="Lifecycle Governance Domain",
            description="Governs component lifecycle transitions",
            scope="runtime",
        )


# =============================================================================
# CONFIGURATION GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class ConfigurationGovernanceDomain(GovernanceDomain):
    """
    Governance domain for configuration management.
    
    Supervises:
    - Configuration validation
    - Configuration drift detection
    - Configuration rollback
    - Configuration versioning
    """
    
    def __init__(self):
        super().__init__(
            domain_id="configuration_governance",
            name="Configuration Governance Domain",
            description="Governs configuration management and validation",
            scope="runtime",
        )


# =============================================================================
# SECURITY GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class SecurityGovernanceDomain(GovernanceDomain):
    """
    Governance domain for security controls.
    
    Supervises:
    - Authentication and authorization
    - Access control policies
    - Data protection
    - Security policy compliance
    """
    
    auth_required: bool = True
    encryption_required: bool = True
    audit_enabled: bool = True
    
    def __init__(self):
        super().__init__(
            domain_id="security_governance",
            name="Security Governance Domain",
            description="Governs security controls and compliance",
            scope="runtime",
        )


# =============================================================================
# COMMUNICATION GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class CommunicationGovernanceDomain(GovernanceDomain):
    """
    Governance domain for communication patterns.
    
    Supervises:
    - Message delivery guarantees
    - Timeout policies
    - Retry limits
    - Circuit breaker state
    """
    
    max_retries: int = 3
    default_timeout_seconds: float = 5.0
    circuit_breaker_threshold: float = 0.1
    
    def __init__(self):
        super().__init__(
            domain_id="communication_governance",
            name="Communication Governance Domain",
            description="Governs communication patterns and reliability",
            scope="runtime",
        )


# =============================================================================
# PERSISTENCE GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class PersistenceGovernanceDomain(GovernanceDomain):
    """
    Governance domain for persistence operations.
    
    Supervises:
    - Transaction integrity
    - Data consistency
    - Backup compliance
    - Recovery procedures
    """
    
    max_transaction_duration_seconds: float = 30.0
    max_concurrent_transactions: int = 100
    
    def __init__(self):
        super().__init__(
            domain_id="persistence_governance",
            name="Persistence Governance Domain",
            description="Governs persistence operations and data integrity",
            scope="runtime",
        )


# =============================================================================
# RECOVERY GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class RecoveryGovernanceDomain(GovernanceDomain):
    """
    Governance domain for recovery operations.
    
    Supervises:
    - Failure detection
    - Automatic recovery attempts
    - Manual intervention triggers
    - Recovery plan execution
    """
    
    auto_recovery_enabled: bool = True
    max_recovery_attempts: int = 3
    recovery_timeout_seconds: float = 60.0
    
    def __init__(self):
        super().__init__(
            domain_id="recovery_governance",
            name="Recovery Governance Domain",
            description="Governs failure recovery and restoration",
            scope="runtime",
        )


# =============================================================================
# DEPLOYMENT GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class DeploymentGovernanceDomain(GovernanceDomain):
    """
    Governance domain for deployment operations.
    
    Supervises:
    - Deployment validation
    - Rollback procedures
    - Version compatibility
    - Deployment windows
    """
    
    canary_enabled: bool = False
    max_canary_instances: int = 1
    
    def __init__(self):
        super().__init__(
            domain_id="deployment_governance",
            name="Deployment Governance Domain",
            description="Governs deployment operations and validation",
            scope="runtime",
        )


# =============================================================================
# CAPABILITY GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class CapabilityGovernanceDomain(GovernanceDomain):
    """
    Governance domain for capability management.
    
    Supervises:
    - Capability registration
    - Capability authorization
    - Capability deprecation
    - Capability replacement
    """
    
    def __init__(self):
        super().__init__(
            domain_id="capability_governance",
            name="Capability Governance Domain",
            description="Governs capability lifecycle and authorization",
            scope="runtime",
        )


# =============================================================================
# SERVICE GOVERNANCE DOMAIN
# =============================================================================

@dataclass(frozen=True)
class ServiceGovernanceDomain(GovernanceDomain):
    """
    Governance domain for service management.
    
    Supervises:
    - Service discovery
    - Load balancing
    - Health monitoring
    - Service termination
    """
    
    max_service_instances: int = 10
    health_check_interval_seconds: float = 5.0
    
    def __init__(self):
        super().__init__(
            domain_id="service_governance",
            name="Service Governance Domain",
            description="Governs service lifecycle and availability",
            scope="runtime",
        )


# =============================================================================
# DOMAINS REGISTRY
# =============================================================================

class GovernanceDomainsRegistry:
    """Registry of all governance domains."""
    
    _domains: Dict[str, GovernanceDomain] = {}
    
    def __init__(self):
        self._register_default_domains()
    
    def _register_default_domains(self) -> None:
        """Register default domain instances."""
        domains = [
            RuntimeGovernanceDomain(),
            ResourceGovernanceDomain(),
            ExecutionGovernanceDomain(),
            LifecycleGovernanceDomain(),
            ConfigurationGovernanceDomain(),
            SecurityGovernanceDomain(),
            CommunicationGovernanceDomain(),
            PersistenceGovernanceDomain(),
            RecoveryGovernanceDomain(),
            DeploymentGovernanceDomain(),
            CapabilityGovernanceDomain(),
            ServiceGovernanceDomain(),
        ]
        
        for domain in domains:
            self._domains[domain.domain_id] = domain
    
    def get_domain(self, domain_id: str) -> Optional[GovernanceDomain]:
        """Get a domain by its ID."""
        return self._domains.get(domain_id)
    
    def get_all_domains(self) -> List[GovernanceDomain]:
        """Get all registered domains."""
        return list(self._domains.values())
    
    def enable_domain(self, domain_id: str) -> bool:
        """Enable a domain."""
        if domain_id in self._domains:
            # Note: dataclass is frozen, so we'd need to replace it
            # This is simplified for the example
            return True
        return False
    
    def disable_domain(self, domain_id: str) -> bool:
        """Disable a domain."""
        if domain_id in self._domains:
            return True
        return False


__all__ = [
    "GovernanceDomain",
    "RuntimeGovernanceDomain",
    "ResourceGovernanceDomain",
    "ExecutionGovernanceDomain",
    "LifecycleGovernanceDomain",
    "ConfigurationGovernanceDomain",
    "SecurityGovernanceDomain",
    "CommunicationGovernanceDomain",
    "PersistenceGovernanceDomain",
    "RecoveryGovernanceDomain",
    "DeploymentGovernanceDomain",
    "CapabilityGovernanceDomain",
    "ServiceGovernanceDomain",
    "GovernanceDomainsRegistry",
]