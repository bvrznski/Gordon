"""Gordon Agent Loading Types.

Phase 3.7.31-I: Agent Component Loading Architecture
====================================================

Immutable type models for loading operations.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import (
    Any,
    Dict,
    FrozenSet,
    List,
    Optional,
    Tuple,
)


# =============================================================================
# LOAD PHASE MODEL
# =============================================================================


class LoadPhase(Enum):
    """Loading phase for component ordering."""
    
    FOUNDATION = "foundation"
    CORE_CONTRACTS = "core_contracts"
    CORE_AUTHORITIES = "core_authorities"
    RUNTIME_INFRASTRUCTURE = "runtime_infrastructure"
    COMMUNICATION = "communication"
    OBSERVABILITY = "observability"
    SECURITY = "security"
    PERSISTENCE = "persistence"
    RESOURCES = "resources"
    SERVICES = "services"
    MODELS = "models"
    MEMORY = "memory"
    PERCEPTION = "perception"
    COGNITION = "cognition"
    SUPERVISION = "supervision"
    BRIDGE = "bridge"
    OPERATIONAL_CONTROLLERS = "operational_controllers"
    OPTIONAL_EXTENSIONS = "optional_extensions"


# =============================================================================
# COMPONENT KIND MODEL
# =============================================================================


class ComponentKind(Enum):
    """Category of component."""
    
    CORE_AUTHORITY = "core_authority"
    INFRASTRUCTURE = "infrastructure"
    SERVICE = "service"
    MODEL = "model"
    MEMORY = "memory"
    PERCEPTION = "perception"
    COGNITION = "cognition"
    SUPERVISION = "supervision"
    BRIDGE = "bridge"
    OPERATIONAL_CONTROLLER = "operational_controller"
    PLUGIN = "plugin"
    TOOL_ADAPTER = "tool_adapter"
    OPTIONAL_EXTENSION = "optional_extension"


# =============================================================================
# DEPENDENCY MODEL
# =============================================================================


class DependencyType(Enum):
    """Type of dependency relationship."""
    
    REQUIRED = "required"
    OPTIONAL = "optional"
    CONFLICT = "conflict"
    CAPABILITY = "capability"


@dataclass(frozen=True)
class DependencyDeclaration:
    """Declaration of a dependency."""
    
    target: str
    dep_type: DependencyType
    version_constraint: Optional[str] = None
    phase_constraint: Optional[LoadPhase] = None
    condition: Optional[str] = None
    
    @property
    def is_required(self) -> bool:
        return self.dep_type == DependencyType.REQUIRED
    
    @property
    def is_optional(self) -> bool:
        return self.dep_type == DependencyType.OPTIONAL
    
    @property
    def is_conflict(self) -> bool:
        return self.dep_type == DependencyType.CONFLICT
    
    @property
    def is_capability(self) -> bool:
        return self.dep_type == DependencyType.CAPABILITY


# =============================================================================
# CAPABILITY MODEL
# =============================================================================


@dataclass(frozen=True)
class CapabilityDeclaration:
    """Declaration of a provided capability."""
    
    name: str
    version: str = "1.0.0"
    scope: Optional[str] = None
    priority: int = 0
    exclusive: bool = False


# =============================================================================
# CONFIGURATION PROJECTION MODEL
# =============================================================================


@dataclass(frozen=True)
class ConfigurationProjection:
    """Narrow projection of configuration for a component."""
    
    schema: str
    source: str = "default"
    path: Tuple[str, ...] = field(default_factory=tuple)
    required_keys: FrozenSet[str] = field(default_factory=frozenset)


# =============================================================================
# LOAD DESCRIPTOR - THE CANONICAL COMPONENT DESCRIPTION
# =============================================================================


@dataclass(frozen=True)
class LoadDescriptor:
    """Immutable description of a component to be loaded."""
    
    component_id: str
    component_kind: ComponentKind
    package_id: str
    implementation_path: str
    load_phase: LoadPhase
    schema_version: str = "1.0.0"
    implementation_symbol: Optional[str] = None
    factory_path: Optional[str] = None
    factory_symbol: Optional[str] = None
    priority: int = 0
    required_dependencies: Tuple[DependencyDeclaration, ...] = field(default_factory=tuple)
    optional_dependencies: Tuple[DependencyDeclaration, ...] = field(default_factory=tuple)
    conflicting_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    required_capabilities: Tuple[CapabilityDeclaration, ...] = field(default_factory=tuple)
    provided_capabilities: Tuple[CapabilityDeclaration, ...] = field(default_factory=tuple)
    required: bool = True
    eager: bool = True
    platform_constraint: Optional[str] = None
    python_version_constraint: Optional[str] = None
    feature_policy: Optional[FrozenSet[str]] = field(default_factory=frozenset)
    cpu_class: Optional[str] = None
    memory_mb: Optional[int] = None
    gpu_required: bool = False
    runtime_scope: str = "runtime"
    lifecycle_scope: str = "agent"
    security_classification: str = "internal"
    integrity_expected: bool = True
    rollback_contract: bool = True
    source_path: Optional[str] = None
    source_line: Optional[int] = None
    
    @property
    def is_optional(self) -> bool:
        return not self.required
    
    @property
    def is_lazy(self) -> bool:
        return not self.eager


# =============================================================================
# LOAD DESCRIPTOR SET - COLLECTION OF DESCRIBED COMPONENTS
# =============================================================================


@dataclass(frozen=True)
class LoadDescriptorSet:
    """Immutable collection of validated load descriptors."""
    
    set_id: str
    request_id: str
    descriptors: Tuple[LoadDescriptor, ...]
    source_roots: Tuple[str, ...]
    included_packages: FrozenSet[str] = field(default_factory=frozenset)
    excluded_packages: FrozenSet[str] = field(default_factory=frozenset)
    rejected_candidates: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    schema_versions: FrozenSet[str] = field(default_factory=frozenset)
    duplicate_findings: Tuple[Tuple[str, Tuple[LoadDescriptor, ...]], ...] = field(default_factory=tuple)
    fingerprint: str = ""
    discovery_diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    validation_diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def size(self) -> int:
        return len(self.descriptors)
    
    @classmethod
    def create(cls, request_id: str, source_roots: Tuple[str, ...],
               descriptors: Tuple[LoadDescriptor, ...] = (), **kwargs) -> "LoadDescriptorSet":
        set_id = "set_" + str(uuid.uuid4())
        return cls(
            set_id=set_id, request_id=request_id,
            source_roots=source_roots, descriptors=descriptors, **kwargs)


# =============================================================================
# LOAD PLAN - DETERMINISTIC CONSTRUCTION ORDER
# =============================================================================


@dataclass(frozen=True)
class LoadPlanEntry:
    """Single entry in a load plan."""
    
    sequence_number: int
    component_id: str
    component_kind: ComponentKind
    phase: LoadPhase
    priority: int
    dependency_ids: Tuple[str, ...]
    implementation_path: str
    required_capability_providers: FrozenSet[str] = field(default_factory=frozenset)
    factory_path: Optional[str] = None
    configuration_projection: Optional[ConfigurationProjection] = None
    runtime_scope: str = "runtime"
    lifecycle_scope: str = "agent"
    required: bool = True
    eager: bool = True
    rollback_contract: bool = True
    
    @property
    def is_optional(self) -> bool:
        return not self.required
    
    @property
    def is_lazy(self) -> bool:
        return not self.eager


@dataclass(frozen=True)
class LoadPlan:
    """Immutable load plan specifying component construction order."""
    
    plan_id: str
    request_id: str
    init_id: Optional[str]
    runtime_id: Optional[str]
    descriptor_set_id: str
    dependency_graph_id: str
    capability_resolution_id: str
    configuration_fingerprint: str
    phases: Tuple[LoadPhase, ...]
    entries: Tuple[LoadPlanEntry, ...]
    required_components: FrozenSet[str] = field(default_factory=frozenset)
    optional_components: FrozenSet[str] = field(default_factory=frozenset)
    skipped_components: FrozenSet[str] = field(default_factory=frozenset)
    lazy_components: FrozenSet[str] = field(default_factory=frozenset)
    provider_selections: FrozenSet[Tuple[str, str]] = field(default_factory=frozenset)
    dependency_evidence: Tuple[str, ...] = field(default_factory=tuple)
    phase_evidence: Tuple[str, ...] = field(default_factory=tuple)
    fingerprint: str = ""
    
    @property
    def size(self) -> int:
        return len(self.entries)
    
    @classmethod
    def create(cls, request_id: str, descriptor_set_id: str, dependency_graph_id: str,
               capability_resolution_id: str, configuration_fingerprint: str,
               phases: Tuple[LoadPhase, ...], entries: Tuple[LoadPlanEntry, ...],
               **kwargs) -> "LoadPlan":
        plan_id = "plan_" + str(uuid.uuid4())
        component_ids = tuple(e.component_id for e in entries)
        required = kwargs.get("required_components", frozenset())
        optional = kwargs.get("optional_components", frozenset())
        skipped = kwargs.get("skipped_components", frozenset())
        lazy = kwargs.get("lazy_components", frozenset())
        
        return cls(
            plan_id=plan_id, request_id=request_id,
            descriptor_set_id=descriptor_set_id,
            dependency_graph_id=dependency_graph_id,
            capability_resolution_id=capability_resolution_id,
            configuration_fingerprint=configuration_fingerprint,
            phases=phases, entries=entries,
            required_components=frozenset(required),
            optional_components=frozenset(optional),
            skipped_components=frozenset(skipped),
            lazy_components=frozenset(lazy), **kwargs)
    
    @classmethod
    def create_default(cls, launch_id: str) -> "LoadPlan":
        """Create a default load plan for testing."""
        return cls.create(
            request_id=f"plan_{launch_id}",
            descriptor_set_id="unknown",
            dependency_graph_id="unknown",
            capability_resolution_id="unknown",
            configuration_fingerprint="default",
            phases=tuple(LoadPhase),
            entries=())


# =============================================================================
# LOAD REQUEST - INPUT TO LOADER
# =============================================================================


@dataclass(frozen=True)
class AgentLoadRequest:
    """Immutable request for component loading."""
    
    plan_id: str
    launch_id: str
    config_fingerprint: str
    safe_mode_enabled: bool = False
    offline_mode_enabled: bool = False
    validation_only: bool = False
    startup_deadline_seconds: float = 30.0
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    @property
    def is_validation_only(self) -> bool:
        return self.validation_only
    
    @property
    def is_safe_mode(self) -> bool:
        return self.safe_mode_enabled
    
    @property
    def is_offline(self) -> bool:
        return self.offline_mode_enabled


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    "LoadPhase", "ComponentKind", "DependencyType", "DependencyDeclaration",
    "CapabilityDeclaration", "ConfigurationProjection", "LoadDescriptor",
    "LoadDescriptorSet", "LoadPlanEntry", "LoadPlan", "AgentLoadRequest"]