"""Gordon Agent Loading Exceptions.

Phase 3.7.31-I: Agent Component Loading Architecture
====================================================

Typed failure exceptions for loading operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# =============================================================================
# BASE EXCEPTIONS
# =============================================================================


@dataclass(frozen=True)
class AgentLoadError(Exception):
    """Base exception for all loading errors.
    
    This is the top-level exception type. All other loading exceptions
    inherit from it.
    """
    load_id: str = ""
    """Load operation ID."""
    
    message: str = ""
    """Error message."""
    
    primary_cause: Optional[str] = None
    """Primary underlying cause if known."""
    
    secondary_failures: List[str] = field(default_factory=list)
    """Secondary failures that occurred."""
    
    rollback_status: str = "unknown"
    """Status of any rollback attempt."""
    
    retry_eligible: bool = False
    """Whether the operation can be retried."""
    
    diagnostics_reference: Optional[str] = None
    """Reference to diagnostic record if available."""
    
    def __str__(self) -> str:
        base = f"{type(self).__name__}: {self.message}"
        details = []
        
        if self.primary_cause:
            details.append(f"primary_cause={self.primary_cause}")
        if self.secondary_failures:
            details.append(f"secondary_failures={len(self.secondary_failures)}")
        if self.rollback_status != "unknown":
            details.append(f"rollback_status={self.rollback_status}")
        if self.diagnostics_reference:
            details.append(f"diagnostics={self.diagnostics_reference}")
        
        if details:
            return f"{base} ({'; '.join(details)})"
        return base


@dataclass(frozen=True)
class LoadRequestError(AgentLoadError):
    """Error in the load request itself."""
    pass


@dataclass(frozen=True)
class DescriptorDiscoveryError(AgentLoadError):
    """Error discovering component descriptors."""
    source_path: Optional[str] = None
    """Path where discovery failed."""
    
    @property
    def is_timeout(self) -> bool:
        """Check if this was a timeout during discovery."""
        return "timeout" in self.message.lower()


@dataclass(frozen=True)
class DescriptorImportError(AgentLoadError):
    """Error importing a descriptor module."""
    module_path: Optional[str] = None
    """Module that failed to import."""
    
    @property
    def is_security_violation(self) -> bool:
        """Check if this was a security-related import failure."""
        return "security" in self.message.lower() or "unauthorized" in self.message.lower()


@dataclass(frozen=True)
class DescriptorParseError(AgentLoadError):
    """Error parsing descriptor metadata."""
    source_path: Optional[str] = None
    """Path of descriptor that failed to parse."""


@dataclass(frozen=True)
class DescriptorValidationError(AgentLoadError):
    """Error validating descriptor contract."""
    component_id: Optional[str] = None
    """Component ID if known."""
    
    invalid_field: Optional[str] = None
    """Field that failed validation if known."""
    
    @property
    def is_duplicate(self) -> bool:
        """Check if this was a duplicate component ID error."""
        return "duplicate" in self.message.lower()


@dataclass(frozen=True)
class DuplicateComponentError(AgentLoadError):
    """Multiple descriptors found with same component ID."""
    duplicate_ids: List[str] = field(default_factory=list)
    """List of conflicting descriptor IDs."""


@dataclass(frozen=True)
class DependencyResolutionError(AgentLoadError):
    """Error resolving dependencies between components."""
    pass


@dataclass(frozen=True)
class DependencyCycleError(DependencyResolutionError):
    """Required dependency cycle detected."""
    edge_types: List[str] = field(default_factory=list)
    """Types of edges in the cycle (required/optional)."""
    
    cycle_path: List[str] = field(default_factory=list)
    """Ordered component IDs forming the cycle."""
    
    @property
    def is_release_blocking(self) -> bool:
        """Required dependency cycles are release blocking."""
        return True


@dataclass(frozen=True)
class MissingDependencyError(DependencyResolutionError):
    """A required dependency could not be found."""
    depending_component: Optional[str] = None
    """Component that depends on the missing one if known."""
    
    missing_id: str = ""
    """Component ID or capability ID that was missing."""


@dataclass(frozen=True)
class CapabilityResolutionError(AgentLoadError):
    """Error resolving required capabilities to providers."""
    pass


@dataclass(frozen=True)
class AmbiguousCapabilityProviderError(CapabilityResolutionError):
    """Multiple providers satisfy a capability but policy requires ambiguity resolution."""
    provider_ids: List[str] = field(default_factory=list)
    """List of potential provider component IDs."""
    
    capability_id: str = ""
    """Capability ID that has ambiguous providers."""
    
    @property
    def is_policy_error(self) -> bool:
        """Ambiguity is a policy error when explicit resolution is required."""
        return True


@dataclass(frozen=True)
class LoadPhaseError(AgentLoadError):
    """Error related to loading phases."""
    phase: Optional[str] = None
    """Phase where error occurred if known."""


@dataclass(frozen=True)
class LoadPlanError(AgentLoadError):
    """Error in load plan generation or validation."""
    pass


@dataclass(frozen=True)
class StaleLoadPlanError(LoadPlanError):
    """Load plan is stale and must be regenerated."""
    config_generation: int = 0
    """Current configuration generation number."""
    
    plan_generation: int = 0
    """Configuration generation when plan was created."""


@dataclass(frozen=True)
class ImplementationImportError(AgentLoadError):
    """Error importing component implementation."""
    symbol: Optional[str] = None
    """Symbol if specific import failed."""
    
    import_path: str = ""
    """Path that failed to import."""
    
    @property
    def is_unauthorized(self) -> bool:
        """Check if this was an unauthorized import attempt."""
        return "unauthorized" in self.message.lower()


@dataclass(frozen=True)
class FactoryResolutionError(AgentLoadError):
    """Error resolving component factory."""
    component_id: str = ""
    """Component ID if known."""
    
    factory_path: Optional[str] = None
    """Factory path that failed to resolve."""


@dataclass(frozen=True)
class ComponentConstructionError(AgentLoadError):
    """Error constructing a component instance."""
    factory_path: Optional[str] = None
    """Factory path if known."""
    
    component_id: str = ""
    """Component being constructed."""
    
    @property
    def is_required_failure(self) -> bool:
        """Check if this was a required component failure."""
        return True


@dataclass(frozen=True)
class LoadCancellationError(AgentLoadError):
    """Loading operation was cancelled."""
    cancellation_reason: Optional[str] = None
    """Reason for cancellation if known."""


@dataclass(frozen=True)
class LoadTimeoutError(AgentLoadError):
    """Loading operation timed out."""
    phase: Optional[str] = None
    """Phase where timeout occurred if known."""
    
    timeout_seconds: float = 0.0
    """Timeout that was reached."""


@dataclass(frozen=True)
class LoadRollbackError(AgentLoadError):
    """Error during loading rollback."""
    rollback_operation: str = "unknown"
    """Operation being rolled back."""
    
    @property
    def is_primary_failure(self) -> bool:
        """Check if this replaced the primary failure (shouldn't happen)."""
        return False


@dataclass(frozen=True)
class LoadSecurityError(AgentLoadError):
    """Security violation during loading."""
    security_category: str = "unclassified"
    """Category of security issue."""
    
    @property
    def is_release_blocking(self) -> bool:
        """Security violations are always release blocking."""
        return True


@dataclass(frozen=True)
class LoadInternalError(AgentLoadError):
    """Unexpected internal error in loading system."""
    traceback_reference: Optional[str] = None
    """Reference to full traceback if available."""
    
    @property
    def is_retryable(self) -> bool:
        """Internal errors may be retryable depending on context."""
        return False