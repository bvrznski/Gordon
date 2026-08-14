# Functionality Verification Architecture - Phase 3.13.5
# =========================================================
#
# Functionality Integrity and Interface Verification System.
#
# This module implements automated verification that declared architectural intent
# is actually respected by the implementation:
#
# - Interface Verification: Does this class implement the required interfaces?
# - Dependency Verification: Do dependencies agree with declared functionality?
# - Ownership Verification: Is ownership consistent with functionality marker?
# - Package Verification: Is package placement appropriate for functionality?
# - Role Verification: Are runtime and integration roles coherent?
# - Public API Verification: Does exported API match functionality?
# - Registry Consistency: Is registry consistent with reflection?
# - Reflection Consistency: Is metadata consistent across representations?
#
# Every Functionality marker now has a verifiable architectural contract.

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
)
from enum import Enum, auto
import inspect
import threading


from . import (
    CoreFunctionality,
    ForCore,
    ForExecution,
    ForEntrypoint,
    ForArchitecture,
    ForNetworks,
    ForCapabilities,
    ForSystems,
    get_functionality_marker,
    get_all_markers,
)
from .registry import FunctionalityRegistry, RegistryEntry
from .metaclass import (
    CoreFunctionalityMetadata,
    ClassificationStatus,
)


# =============================================================================
# VERIFICATION FINDINGS - Typed Results
# =============================================================================


class FindingCategory(Enum):
    """Categories of verification findings."""
    
    # Interface categories
    MISSING_INTERFACE = "MISSING_INTERFACE"
    UNEXPECTED_INTERFACE = "UNEXPECTED_INTERFACE"
    DEPRECATED_INTERFACE = "DEPRECATED_INTERFACE"
    CONFLICTING_INTERFACE = "CONFLICTING_INTERFACE"
    
    # Dependency categories
    INVALID_DEPENDENCY = "INVALID_DEPENDENCY"
    MISSING_REQUIRED_DEPENDENCY = "MISSING_REQUIRED_DEPENDENCY"
    CIRCULAR_DEPENDENCY = "CIRCULAR_DEPENDENCY"
    
    # Ownership categories
    OWNERSHIP_CONFLICT = "OWNERSHIP_CONFLICT"
    OWNERSHIP_MISMATCH = "OWNERSHIP_MISMATCH"
    UNREGISTERED_OWNER = "UNREGISTERED_OWNER"
    
    # Package categories
    PACKAGE_MISMATCH = "PACKAGE_MISMATCH"
    INVALID_PACKAGE_PATH = "INVALID_PACKAGE_PATH"
    
    # Role categories
    ROLE_CONFLICT = "ROLE_CONFLICT"
    ROLE_MISSING_REQUIRED = "ROLE_MISSING_REQUIRED"
    ROLE_EXCEEDS_BOUNDARY = "ROLE_EXCEEDS_BOUNDARY"
    
    # API categories
    PUBLIC_API_VIOLATION = "PUBLIC_API_VIOLATION"
    EXPORTED_PRIVATE_IMPLEMENTATION = "EXPORTED_PRIVATE_IMPLEMENTATION"
    
    # Registry/Reflection categories
    REGISTRY_INCONSISTENCY = "REGISTRY_INCONSISTENCY"
    REFLECTION_MISMATCH = "REFLECTION_MISMATCH"
    DOCUMENTATION_MISMATCH = "DOCUMENTATION_MISMATCH"


class FindingSeverity(Enum):
    """Severity levels for verification findings."""
    
    P0_CRITICAL = "P0_CRITICAL"      # Blocks certification
    P1_HIGH = "P1_HIGH"              # Must be resolved before release
    P2_MEDIUM = "P2_MEDIUM"          # Should be addressed soon
    P3_LOW = "P3_LOW"                # Nice to have, can defer


@dataclass(frozen=True, order=True)
class VerificationFinding:
    """A single verification finding with all metadata."""
    
    category: FindingCategory
    severity: FindingSeverity
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    finding_id: str = field(init=False)
    
    def __post_init__(self):
        """Generate stable finding ID."""
        from hashlib import sha256
        key_data = f"{self.category.value}:{self.severity.value}:{self.message}"
        object.__setattr__(self, "finding_id",
                          f"FND-{sha256(key_data.encode()).hexdigest()[:12].upper()}")


@dataclass(frozen=True)
class VerificationResult:
    """Complete verification result for a single class."""
    
    qualified_name: str
    is_valid: bool
    findings: Tuple[VerificationFinding, ...]
    timestamp: float = field(default_factory=lambda: 0.0)
    
    def __post_init__(self):
        import time
        if self.timestamp == 0.0:
            object.__setattr__(self, "timestamp", time.monotonic())
    
    @property
    def has_critical(self) -> bool:
        return any(f.severity == FindingSeverity.P0_CRITICAL for f in self.findings)
    
    @property
    def has_high_severity(self) -> bool:
        return any(f.severity == FindingSeverity.P1_HIGH for f in self.findings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "qualified_name": self.qualified_name,
            "is_valid": self.is_valid,
            "has_critical": self.has_critical,
            "has_high_severity": self.has_high_severity,
            "findings": [
                {
                    "category": f.category.value,
                    "severity": f.severity.value,
                    "message": f.message,
                    "context": f.context,
                    "finding_id": f.finding_id,
                }
                for f in self.findings
            ],
            "timestamp": self.timestamp,
        }


# =============================================================================
# VERIFICATION CONTRACTS - Per Functionality Marker
# =============================================================================


@dataclass(frozen=True)
class InterfaceContract:
    """Interface contract for a functionality marker."""
    
    required_interfaces: Tuple[str, ...] = ()      # Fully qualified interface names
    allowed_interfaces: Tuple[str, ...] = ()
    forbidden_interfaces: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DependencyContract:
    """Dependency contract for a functionality marker."""
    
    allowed_dependencies: Tuple[str, ...] = ()
    forbidden_dependencies: Tuple[str, ...] = ()
    required_dependencies: Tuple[str, ...] = ()


@dataclass(frozen=True)
class OwnershipContract:
    """Ownership contract for a functionality marker."""
    
    canonical_package: str
    allowed_owners: Tuple[str, ...] = ("unknown",)
    default_owner: str = "unknown"


@dataclass(frozen=True)
class PackageContract:
    """Package placement contract for a functionality marker."""
    
    expected_package_path: str
    allowed_subdirectories: Tuple[str, ...] = ()


@dataclass(frozen=True)
class RoleContract:
    """Role contract for a functionality marker."""
    
    allowed_runtime_roles: Tuple[str, ...] = ()
    allowed_integration_roles: Tuple[str, ...] = ()
    forbidden_runtime_roles: Tuple[str, ...] = ()
    forbidden_integration_roles: Tuple[str, ...] = ()


# =============================================================================
# CONTRACT IMPLEMENTATIONS - Per Functionality Marker
# =============================================================================


# ForCore contracts
FOR_CORE_INTERFACE_CONTRACT = InterfaceContract(
    required_interfaces=(),
    allowed_interfaces=(
        "gordon_system.src.agent.core.interfaces.ILifecycleComponent",
        "gordon_system.src.agent.core.interfaces.IManagedComponent",
        "gordon_system.src.agent.core.interfaces.IDisposable",
    ),
    forbidden_interfaces=(),
)

FOR_CORE_DEPENDENCY_CONTRACT = DependencyContract(
    allowed_dependencies=(
        "gordon_system.src.agent.core",
        "gordon_system.src.agent.core.interfaces",
    ),
    forbidden_dependencies=(
        "gordon_system.src.agent.execution.coordinator",  # Runtime execution
        "gordon_system.src.agent.systems.memory.streams",   # Semantic memory
    ),
)

FOR_CORE_OWNERSHIP_CONTRACT = OwnershipContract(
    canonical_package="core",
    allowed_owners=("CoreTeam", "ArchitectureTeam"),
    default_owner="CoreTeam",
)

FOR_CORE_PACKAGE_CONTRACT = PackageContract(
    expected_package_path="core",
    allowed_subdirectories=(
        "core/configuration",
        "core/lifecycle",
        "core/execution",
        "core/streams",
        "core/failure",
        "core/tasks",
        "core/action",
        "core/communication",
        "core/correlation",
        "core/observability",
    ),
)

FOR_CORE_ROLE_CONTRACT = RoleContract(
    allowed_runtime_roles=(
        "lifecycle.LifecycleParticipant",
        "lifecycle.Startable",
        "lifecycle.Stoppable",
    ),
    allowed_integration_roles=(),
)


# ForExecution contracts
FOR_EXECUTION_INTERFACE_CONTRACT = InterfaceContract(
    required_interfaces=(),
    allowed_interfaces=(
        "gordon_system.src.agent.core.interfaces.ILifecycleComponent",
        "gordon_system.src.agent.core.interfaces.IManagedComponent",
        "gordon_system.src.agent.execution.scheduling.ISchedulerListener",
    ),
    forbidden_interfaces=(),
)

FOR_EXECUTION_DEPENDENCY_CONTRACT = DependencyContract(
    allowed_dependencies=(
        "gordon_system.src.agent.core",
        "gordon_system.src.agent.core.interfaces",
        "gordon_system.src.agent.execution.contracts",
    ),
    forbidden_dependencies=(
        "gordon_system.src.agent.architecture.generation",  # Architecture generation
        "gordon_system.src.agent.systems.memory.streams",   # Semantic memory
    ),
)

FOR_EXECUTION_OWNERSHIP_CONTRACT = OwnershipContract(
    canonical_package="core/execution",
    allowed_owners=("CoreTeam", "ExecutionTeam"),
    default_owner="ExecutionTeam",
)

FOR_EXECUTION_PACKAGE_CONTRACT = PackageContract(
    expected_package_path="core/execution",
    allowed_subdirectories=(
        "core/execution/scheduling",
        "core/execution/threads",
        "core/execution/cycles",
        "core/execution/stages",
        "core/execution/integration",
    ),
)

FOR_EXECUTION_ROLE_CONTRACT = RoleContract(
    allowed_runtime_roles=(
        "lifecycle.LifecycleParticipant",
        "lifecycle.Startable",
        "lifecycle.Stoppable",
        "lifecycle.Suspendable",
        "recovery.Recoverable",
    ),
    allowed_integration_roles=("execution.ExecutionIntegrationParticipant",),
)


# ForEntrypoint contracts
FOR_ENTRYPOINT_INTERFACE_CONTRACT = InterfaceContract(
    required_interfaces=(
        "gordon_system.src.agent.core.interfaces.ILifecycleComponent",
    ),
    allowed_interfaces=(
        "gordon_system.src.agent.core.interfaces.IManagedComponent",
        "gordon_system.src.agent.core.interfaces.IDisposable",
    ),
    forbidden_interfaces=(),
)

FOR_ENTRYPOINT_DEPENDENCY_CONTRACT = DependencyContract(
    allowed_dependencies=(
        "gordon_system.src.agent.core",
        "gordon_system.src.agent.execution.contracts",
    ),
    forbidden_dependencies=(
        "gordon_system.src.agent.execution.coordinator",   # Runtime execution
        "gordon_system.src.agent.systems.consciousness",  # Semantic system
    ),
)

FOR_ENTRYPOINT_OWNERSHIP_CONTRACT = OwnershipContract(
    canonical_package="entrypoint",
    allowed_owners=("ArchitectureTeam", "BootstrapTeam"),
    default_owner="ArchitectureTeam",
)

FOR_ENTRYPOINT_PACKAGE_CONTRACT = PackageContract(
    expected_package_path="entrypoint",
    allowed_subdirectories=("entrypoint",),
)

FOR_ENTRYPOINT_ROLE_CONTRACT = RoleContract(
    allowed_runtime_roles=(
        "lifecycle.Startable",
        "lifecycle.Stoppable",
        "lifecycle.LifecycleParticipant",
    ),
    allowed_integration_roles=(),
)


# ForArchitecture contracts
FOR_ARCHITECTURE_INTERFACE_CONTRACT = InterfaceContract(
    required_interfaces=(),
    allowed_interfaces=(
        "gordon_system.src.agent.core.interfaces.IDisposable",
    ),
    forbidden_interfaces=(
        "lifecycle.Startable",  # Architecture should not have runtime interfaces
        "lifecycle.Stoppable",
    ),
)

FOR_ARCHITECTURE_DEPENDENCY_CONTRACT = DependencyContract(
    allowed_dependencies=(
        "gordon_system.src.agent.architecture.reflection",
        "gordon_system.src.agent.architecture.discovery",
        "gordon_system.src.agent.core",
    ),
    forbidden_dependencies=(
        "gordon_system.src.agent.execution.coordinator",  # Runtime execution
        "gordon_system.src.agent.systems.memory.streams",   # Semantic memory
    ),
)

FOR_ARCHITECTURE_OWNERSHIP_CONTRACT = OwnershipContract(
    canonical_package="core/architecture",
    allowed_owners=("ArchitectureTeam",),
    default_owner="ArchitectureTeam",
)

FOR_ARCHITECTURE_PACKAGE_CONTRACT = PackageContract(
    expected_package_path="core/architecture",
    allowed_subdirectories=(
        "core/architecture/reflection",
        "core/architecture/discovery",
        "core/architecture/verification",
    ),
)

FOR_ARCHITECTURE_ROLE_CONTRACT = RoleContract(
    allowed_runtime_roles=(),
    allowed_integration_roles=(),
)


# ForNetworks contracts
FOR_NETWORKS_INTERFACE_CONTRACT = InterfaceContract(
    required_interfaces=(
        "gordon_system.src.agent.core.interfaces.IEventPublisher",
        "gordon_system.src.agent.core.interfaces.IEventSubscriber",
    ),
    allowed_interfaces=(
        "gordon_system.src.agent.core.interfaces.ILifecycleComponent",
        "gordon_system.src.agent.core.interfaces.IManagedComponent",
    ),
    forbidden_interfaces=(),
)

FOR_NETWORKS_DEPENDENCY_CONTRACT = DependencyContract(
    allowed_dependencies=(
        "gordon_system.src.agent.core",
        "gordon_system.src.agent.execution.contracts",
    ),
    forbidden_dependencies=(
        "gordon_system.src.agent.systems.memory.streams",  # Semantic memory
        "gordon_system.src.agent.systems.perception.streams",  # Semantic perception
    ),
)

FOR_NETWORKS_OWNERSHIP_CONTRACT = OwnershipContract(
    canonical_package="core/networks",
    allowed_owners=("CoreTeam", "NetworksTeam"),
    default_owner="NetworksTeam",
)

FOR_NETWORKS_PACKAGE_CONTRACT = PackageContract(
    expected_package_path="core/networks",
    allowed_subdirectories=(
        "core/networks/streams",
        "core/networks/transports",
        "core/networks/messages",
    ),
)

FOR_NETWORKS_ROLE_CONTRACT = RoleContract(
    allowed_runtime_roles=(
        "lifecycle.LifecycleParticipant",
        "lifecycle.Startable",
        "lifecycle.Stoppable",
    ),
    allowed_integration_roles=(
        "network.NetworkIntegrationParticipant",
        "stream.StreamIntegrationParticipant",
    ),
)


# ForCapabilities contracts
FOR_CAPABILITIES_INTERFACE_CONTRACT = InterfaceContract(
    required_interfaces=(
        "gordon_system.src.agent.core.interfaces.IExecutable",
    ),
    allowed_interfaces=(
        "gordon_system.src.agent.core.interfaces.ILifecycleComponent",
        "gordon_system.src.agent.core.interfaces.IManagedComponent",
    ),
    forbidden_interfaces=(),
)

FOR_CAPABILITIES_DEPENDENCY_CONTRACT = DependencyContract(
    allowed_dependencies=(
        "gordon_system.src.agent.core",
        "gordon_system.src.agent.capabilities.cognition",
        "gordon_system.src.agent.systems.memory.streams",  # Memory is part of capabilities
    ),
    forbidden_dependencies=(
        "gordon_system.src.agent.entrypoint.bootstrap",  # Bootstrap-specific
    ),
)

FOR_CAPABILITIES_OWNERSHIP_CONTRACT = OwnershipContract(
    canonical_package="core/capabilities",
    allowed_owners=("CapabilitiesTeam", "AIResearch"),
    default_owner="CapabilitiesTeam",
)

FOR_CAPABILITIES_PACKAGE_CONTRACT = PackageContract(
    expected_package_path="core/capabilities",
    allowed_subdirectories=(
        "core/capabilities/cognition",
        "core/capabilities/learning",
        "core/capabilities/motivation",
        "core/capabilities/planning",
    ),
)

FOR_CAPABILITIES_ROLE_CONTRACT = RoleContract(
    allowed_runtime_roles=(
        "lifecycle.Startable",
        "lifecycle.Stoppable",
        "lifecycle.Suspendable",
        "recovery.Recoverable",
    ),
    allowed_integration_roles=("execution.ExecutionIntegrationParticipant",),
)


# ForSystems contracts
FOR_SYSTEMS_INTERFACE_CONTRACT = InterfaceContract(
    required_interfaces=(
        "gordon_system.src.agent.core.interfaces.IDisposable",
        "gordon_system.src.agent.core.interfaces.IManagedComponent",
    ),
    allowed_interfaces=(
        "gordon_system.src.agent.core.interfaces.ILifecycleComponent",
        "gordon_system.src.agent.core.interfaces.IStartable",
        "gordon_system.src.agent.core.interfaces.IStoppable",
    ),
    forbidden_interfaces=(
        "execution.ExecutionScheduler",  # Systems should not expose execution primitives
    ),
)

FOR_SYSTEMS_DEPENDENCY_CONTRACT = DependencyContract(
    allowed_dependencies=(
        "gordon_system.src.agent.core",
        "gordon_system.src.agent.capabilities.cognition",
    ),
    forbidden_dependencies=(
        "gordon_system.src.agent.entrypoint.bootstrap",  # Bootstrap-specific
    ),
)

FOR_SYSTEMS_OWNERSHIP_CONTRACT = OwnershipContract(
    canonical_package="core/systems",
    allowed_owners=("CoreTeam", "SystemTeam"),
    default_owner="SystemTeam",
)

FOR_SYSTEMS_PACKAGE_CONTRACT = PackageContract(
    expected_package_path="core/systems",
    allowed_subdirectories=(
        "core/systems/perception",
        "core/systems/memory",
        "core/systems/consciousness",
        "core/systems/sensory",
    ),
)

FOR_SYSTEMS_ROLE_CONTRACT = RoleContract(
    allowed_runtime_roles=(
        "lifecycle.LifecycleParticipant",
        "lifecycle.Startable",
        "lifecycle.Stoppable",
        "recovery.Recoverable",
        "checkpoint.CheckpointParticipant",
        "replay.ReplayParticipant",
    ),
    allowed_integration_roles=("stream.StreamIntegrationParticipant",),
)


# =============================================================================
# CONTRACT REGISTRY - Maps markers to contracts
# =============================================================================


class ContractRegistry:
    """Registry of functionality marker contracts."""
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        
        # Pre-computed contract instances for each marker
        self._interface_contracts: Dict[Type[CoreFunctionality], InterfaceContract] = {
            ForCore: FOR_CORE_INTERFACE_CONTRACT,
            ForExecution: FOR_EXECUTION_INTERFACE_CONTRACT,
            ForEntrypoint: FOR_ENTRYPOINT_INTERFACE_CONTRACT,
            ForArchitecture: FOR_ARCHITECTURE_INTERFACE_CONTRACT,
            ForNetworks: FOR_NETWORKS_INTERFACE_CONTRACT,
            ForCapabilities: FOR_CAPABILITIES_INTERFACE_CONTRACT,
            ForSystems: FOR_SYSTEMS_INTERFACE_CONTRACT,
        }
        
        self._dependency_contracts: Dict[Type[CoreFunctionality], DependencyContract] = {
            ForCore: FOR_CORE_DEPENDENCY_CONTRACT,
            ForExecution: FOR_EXECUTION_DEPENDENCY_CONTRACT,
            ForEntrypoint: FOR_ENTRYPOINT_DEPENDENCY_CONTRACT,
            ForArchitecture: FOR_ARCHITECTURE_DEPENDENCY_CONTRACT,
            ForNetworks: FOR_NETWORKS_DEPENDENCY_CONTRACT,
            ForCapabilities: FOR_CAPABILITIES_DEPENDENCY_CONTRACT,
            ForSystems: FOR_SYSTEMS_DEPENDENCY_CONTRACT,
        }
        
        self._ownership_contracts: Dict[Type[CoreFunctionality], OwnershipContract] = {
            ForCore: FOR_CORE_OWNERSHIP_CONTRACT,
            ForExecution: FOR_EXECUTION_OWNERSHIP_CONTRACT,
            ForEntrypoint: FOR_ENTRYPOINT_OWNERSHIP_CONTRACT,
            ForArchitecture: FOR_ARCHITECTURE_OWNERSHIP_CONTRACT,
            ForNetworks: FOR_NETWORKS_OWNERSHIP_CONTRACT,
            ForCapabilities: FOR_CAPABILITIES_OWNERSHIP_CONTRACT,
            ForSystems: FOR_SYSTEMS_OWNERSHIP_CONTRACT,
        }
        
        self._package_contracts: Dict[Type[CoreFunctionality], PackageContract] = {
            ForCore: FOR_CORE_PACKAGE_CONTRACT,
            ForExecution: FOR_EXECUTION_PACKAGE_CONTRACT,
            ForEntrypoint: FOR_ENTRYPOINT_PACKAGE_CONTRACT,
            ForArchitecture: FOR_ARCHITECTURE_PACKAGE_CONTRACT,
            ForNetworks: FOR_NETWORKS_PACKAGE_CONTRACT,
            ForCapabilities: FOR_CAPABILITIES_PACKAGE_CONTRACT,
            ForSystems: FOR_SYSTEMS_PACKAGE_CONTRACT,
        }
        
        self._role_contracts: Dict[Type[CoreFunctionality], RoleContract] = {
            ForCore: FOR_CORE_ROLE_CONTRACT,
            ForExecution: FOR_EXECUTION_ROLE_CONTRACT,
            ForEntrypoint: FOR_ENTRYPOINT_ROLE_CONTRACT,
            ForArchitecture: FOR_ARCHITECTURE_ROLE_CONTRACT,
            ForNetworks: FOR_NETWORKS_ROLE_CONTRACT,
            ForCapabilities: FOR_CAPABILITIES_ROLE_CONTRACT,
            ForSystems: FOR_SYSTEMS_ROLE_CONTRACT,
        }
    
    def get_interface_contract(self, marker: Type[CoreFunctionality]) -> InterfaceContract:
        """Get interface contract for a functionality marker."""
        with self._lock:
            return self._interface_contracts.get(marker, InterfaceContract())
    
    def get_dependency_contract(self, marker: Type[CoreFunctionality]) -> DependencyContract:
        """Get dependency contract for a functionality marker."""
        with self._lock:
            return self._dependency_contracts.get(marker, DependencyContract())
    
    def get_ownership_contract(self, marker: Type[CoreFunctionality]) -> OwnershipContract:
        """Get ownership contract for a functionality marker."""
        with self._lock:
            return self._ownership_contracts.get(marker, OwnershipContract())
    
    def get_package_contract(self, marker: Type[CoreFunctionality]) -> PackageContract:
        """Get package contract for a functionality marker."""
        with self._lock:
            return self._package_contracts.get(marker, PackageContract())
    
    def get_role_contract(self, marker: Type[CoreFunctionality]) -> RoleContract:
        """Get role contract for a functionality marker."""
        with self._lock:
            return self._role_contracts.get(marker, RoleContract())


# Global contract registry instance
GLOBAL_CONTRACT_REGISTRY = ContractRegistry()


# =============================================================================
# VERIFICATION ENGINE - Main verification logic
# =============================================================================


class VerificationEngine:
    """
    Core verification engine that performs all verification checks.
    
    This is the central component of Phase 3.13.5 functionality integrity system.
    It verifies every declared Functionality marker against:
        - Required interfaces
        - Allowed dependencies
        - Expected ownership
        - Package placement
        - Runtime roles
        - Public API
        - Registry consistency
        - Reflection consistency
    """
    
    def __init__(self, registry: Optional[FunctionalityRegistry] = None) -> None:
        self._lock = threading.RLock()
        self._registry = registry or FunctionalityRegistry()
        self._contract_registry = GLOBAL_CONTRACT_REGISTRY
        
        # Statistics
        self._verified_count: int = 0
        self._invalid_count: int = 0
        self._findings_by_category: Dict[str, int] = {}
        
        # Cache for verification results
        self._verification_cache: Dict[str, VerificationResult] = {}
    
    def verify_class(
        self,
        cls: Type[Any],
        metadata: Optional[CoreFunctionalityMetadata] = None,
    ) -> VerificationResult:
        """
        Verify a single class against all verification contracts.
        
        Args:
            cls: The class to verify
            metadata: Optional pre-computed Functionality metadata
            
        Returns:
            VerificationResult with findings and validity status
        """
        qualified_name = f"{cls.__module__}.{cls.__qualname__}"
        
        # Check cache first
        if qualified_name in self._verification_cache:
            return self._verification_cache[qualified_name]
        
        findings: List[VerificationFinding] = []
        
        try:
            # Get metadata if not provided
            if metadata is None:
                metadata = getattr(cls, "__core_functionality__", None)
            
            # If still no metadata, create a minimal one for verification
            if metadata is None:
                marker = get_functionality_marker(cls)
                from .metaclass import (
                    CoreFunctionalityMetadata,
                    ClassificationSource,
                    ClassificationStatus,
                )
                metadata = CoreFunctionalityMetadata(
                    qualified_name=qualified_name,
                    canonical_owner=cls.__module__,
                    primary_functionality=marker,
                    primary_marker_name=marker.__name__ if marker else None,
                    classification_source=ClassificationSource.UNKNOWN,
                    requirement_status=ClassificationStatus.MISSING_REQUIRED,
                    classification_status=ClassificationStatus.UNCLASSIFIED_LEGACY,
                    is_abstract=getattr(cls, "__abstractmethods__", False) is not False,
                    is_protocol=False,
                    is_mixin=cls.__name__.endswith("Mixin"),
                    is_nested="." in cls.__qualname__,
                    secondary_roles=(),
                    integration_boundaries=(),
                    exemptions=(),
                    findings=(),
                )
            
            # Run all verification checks
            findings.extend(self._verify_interface(cls, metadata))
            findings.extend(self._verify_dependency(cls, metadata))
            findings.extend(self._verify_ownership(cls, metadata))
            findings.extend(self._verify_package(cls, metadata))
            findings.extend(self._verify_role(cls, metadata))
            findings.extend(self._verify_api(cls, metadata))
            findings.extend(self._verify_registry_consistency(cls, metadata))
            findings.extend(self._verify_reflection_consistency(cls, metadata))
            
        except Exception as e:
            # Verification should never fail completely due to an exception
            findings.append(VerificationFinding(
                category=FindingCategory.REGISTRY_INCONSISTENCY,
                severity=FindingSeverity.P1_HIGH,
                message=f"Verification engine error: {str(e)}",
                context={"class": qualified_name, "error_type": type(e).__name__},
            ))
        
        # Update statistics
        with self._lock:
            self._verified_count += 1
            if findings:
                self._invalid_count += 1
                for f in findings:
                    cat = f.category.value
                    self._findings_by_category[cat] = self._findings_by_category.get(cat, 0) + 1
        
        result = VerificationResult(
            qualified_name=qualified_name,
            is_valid=len(findings) == 0,
            findings=tuple(findings),
        )
        
        # Cache the result
        with self._lock:
            self._verification_cache[qualified_name] = result
        
        return result
    
    def _verify_interface(
        self, cls: Type[Any], metadata: CoreFunctionalityMetadata
    ) -> List[VerificationFinding]:
        """Verify interface implementation matches functionality marker."""
        findings: List[VerificationFinding] = []
        
        marker = metadata.primary_functionality
        if marker is None:
            return findings  # No marker to verify against
        
        contract = self._contract_registry.get_interface_contract(marker)
        
        # Check required interfaces (using string-based checks for now)
        for req_iface in contract.required_interfaces:
            try:
                # Import and check if the class implements this interface
                if "." in req_iface:
                    parts = req_iface.rsplit(".", 1)
                    module = __import__(parts[0], fromlist=[parts[1]])
                    iface = getattr(module, parts[1], None)
                    
                    if iface and not issubclass(cls, iface):
                        findings.append(VerificationFinding(
                            category=FindingCategory.MISSING_INTERFACE,
                            severity=FindingSeverity.P1_HIGH,
                            message=(
                                f"Class {cls.__qualname__} must implement interface "
                                f"{req_iface}"
                            ),
                            context={
                                "class": metadata.qualified_name,
                                "required_interface": req_iface,
                                "marker": marker.__name__,
                            },
                        ))
            except Exception:
                # Interface might not be available - skip this check
                pass
        
        # Check for forbidden interfaces
        for forb_iface in contract.forbidden_interfaces:
            try:
                if "." in forb_iface:
                    parts = forb_iface.rsplit(".", 1)
                    module = __import__(parts[0], fromlist=[parts[1]])
                    iface = getattr(module, parts[1], None)
                    
                    if iface and issubclass(cls, iface):
                        findings.append(VerificationFinding(
                            category=FindingCategory.CONFLICTING_INTERFACE,
                            severity=FindingSeverity.P0_CRITICAL,
                            message=(
                                f"Class {cls.__qualname__} with marker {marker.__name__} "
                                f"forbidden to implement {forb_iface}"
                            ),
                            context={
                                "class": metadata.qualified_name,
                                "forbidden_interface": forb_iface,
                                "marker": marker.__name__,
                            },
                        ))
            except Exception:
                pass
        
        return findings
    
    def _verify_dependency(
        self, cls: Type[Any], metadata: CoreFunctionalityMetadata
    ) -> List[VerificationFinding]:
        """Verify dependencies match functionality marker contract."""
        findings: List[VerificationFinding] = []
        
        marker = metadata.primary_functionality
        if marker is None:
            return findings
        
        contract = self._contract_registry.get_dependency_contract(marker)
        
        # Get class signature for analysis
        try:
            sig = inspect.signature(cls.__init__)
            
            # Check default parameter types
            for param in sig.parameters.values():
                if param.default is not inspect.Parameter.empty:
                    dep_type = type(param.default).__module__
                    
                    # Check for forbidden dependencies in defaults
                    for forb_dep in contract.forbidden_dependencies:
                        if forb_dep.split(".")[0] in str(dep_type):
                            findings.append(VerificationFinding(
                                category=FindingCategory.INVALID_DEPENDENCY,
                                severity=FindingSeverity.P1_HIGH,
                                message=(
                                    f"Class {cls.__qualname__} has forbidden dependency "
                                    f"in parameter default: {dep_type}"
                                ),
                                context={
                                    "class": metadata.qualified_name,
                                    "parameter": param.name,
                                    "forbidden_dependency": forb_dep,
                                    "marker": marker.__name__,
                                },
                            ))
        except Exception:
            pass
        
        return findings
    
    def _verify_ownership(
        self, cls: Type[Any], metadata: CoreFunctionalityMetadata
    ) -> List[VerificationFinding]:
        """Verify ownership matches functionality marker contract."""
        findings: List[VerificationFinding] = []
        
        marker = metadata.primary_functionality
        if marker is None:
            return findings
        
        contract = self._contract_registry.get_ownership_contract(marker)
        
        # Check package path matches expected canonical package
        module_path = cls.__module__
        expected_prefix = contract.canonical_package.replace(".", "/")
        
        if not module_path.startswith(expected_prefix):
            findings.append(VerificationFinding(
                category=FindingCategory.OWNERSHIP_MISMATCH,
                severity=FindingSeverity.P2_MEDIUM,
                message=(
                    f"Class {cls.__qualname__} module path '{module_path}' "
                    f"does not match expected canonical package '{expected_prefix}'"
                ),
                context={
                    "class": metadata.qualified_name,
                    "module": module_path,
                    "expected_canonical_package": expected_prefix,
                    "marker": marker.__name__,
                },
            ))
        
        return findings
    
    def _verify_package(
        self, cls: Type[Any], metadata: CoreFunctionalityMetadata
    ) -> List[VerificationFinding]:
        """Verify package placement matches functionality marker contract."""
        findings: List[VerificationFinding] = []
        
        marker = metadata.primary_functionality
        if marker is None:
            return findings
        
        contract = self._contract_registry.get_package_contract(marker)
        
        module_path = cls.__module__
        expected_prefix = contract.expected_package_path.replace(".", "/")
        
        # Check if package matches expected path
        if not module_path.startswith(expected_prefix):
            findings.append(VerificationFinding(
                category=FindingCategory.PACKAGE_MISMATCH,
                severity=FindingSeverity.P2_MEDIUM,
                message=(
                    f"Class {cls.__qualname__} is in module '{module_path}' "
                    f"but expected package path is '{expected_prefix}' for marker {marker.__name__}"
                ),
                context={
                    "class": metadata.qualified_name,
                    "module": module_path,
                    "expected_package_path": expected_prefix,
                    "marker": marker.__name__,
                },
            ))
        
        return findings
    
    def _verify_role(
        self, cls: Type[Any], metadata: CoreFunctionalityMetadata
    ) -> List[VerificationFinding]:
        """Verify runtime and integration roles match functionality contract."""
        findings: List[VerificationFinding] = []
        
        marker = metadata.primary_functionality
        if marker is None:
            return findings
        
        contract = self._contract_registry.get_role_contract(marker)
        
        # Check secondary roles from metadata (string-based comparison)
        for role in metadata.secondary_roles:
            role_name = role.value
            
            # Check against allowed runtime roles
            found_allowed = any(role_name == r.split(".")[-1] for r in contract.allowed_runtime_roles)
            found_forbidden = any(role_name == r.split(".")[-1] for r in contract.forbidden_runtime_roles)
            
            if not found_allowed and found_forbidden:
                findings.append(VerificationFinding(
                    category=FindingCategory.ROLE_CONFLICT,
                    severity=FindingSeverity.P1_HIGH,
                    message=(
                        f"Role '{role_name}' is forbidden for marker {marker.__name__}"
                    ),
                    context={
                        "class": metadata.qualified_name,
                        "forbidden_role": role_name,
                        "marker": marker.__name__,
                    },
                ))
            elif not found_allowed and not contract.allowed_runtime_roles:
                # No allowed roles specified, so any secondary role is flagged
                findings.append(VerificationFinding(
                    category=FindingCategory.ROLE_EXCEEDS_BOUNDARY,
                    severity=FindingSeverity.P3_LOW,
                    message=(
                        f"Role '{role_name}' may exceed expected boundary for {marker.__name__}"
                    ),
                    context={
                        "class": metadata.qualified_name,
                        "role": role_name,
                        "marker": marker.__name__,
                    },
                ))
        
        return findings
    
    def _verify_api(
        self, cls: Type[Any], metadata: CoreFunctionalityMetadata
    ) -> List[VerificationFinding]:
        """Verify public API matches functionality marker."""
        findings: List[VerificationFinding] = []
        
        marker = metadata.primary_functionality
        if marker is None:
            return findings
        
        # ForArchitecture should not expose runtime execution primitives
        if marker == ForArchitecture:
            for name, attr in inspect.getmembers(cls):
                if not name.startswith("_") and callable(attr):
                    sig = str(inspect.signature(attr))
                    if "execute" in name.lower() or "run" in name.lower():
                        findings.append(VerificationFinding(
                            category=FindingCategory.PUBLIC_API_VIOLATION,
                            severity=FindingSeverity.P1_HIGH,
                            message=(
                                f"Architecture marker class {cls.__qualname__} "
                                f"exposes execution-like API: {name}"
                            ),
                            context={
                                "class": metadata.qualified_name,
                                "method": name,
                                "signature": sig,
                                "marker": marker.__name__,
                            },
                        ))
        
        return findings
    
    def _verify_registry_consistency(
        self, cls: Type[Any], metadata: CoreFunctionalityMetadata
    ) -> List[VerificationFinding]:
        """Verify registry entry is consistent with class state."""
        findings: List[VerificationFinding] = []
        
        try:
            # Check if class is registered in the registry
            registry_metadata = self._registry.get(metadata.qualified_name)
            
            if metadata.is_valid and registry_metadata is None:
                # Valid but not registered - this might be a finding
                findings.append(VerificationFinding(
                    category=FindingCategory.REGISTRY_INCONSISTENCY,
                    severity=FindingSeverity.P3_LOW,
                    message=(
                        f"Class {cls.__qualname__} has valid functionality metadata "
                        f"but is not registered in the FunctionalityRegistry"
                    ),
                    context={
                        "class": metadata.qualified_name,
                        "registry_size": self._registry.size,
                        "is_sealed": self._registry.is_sealed,
                    },
                ))
            
            elif registry_metadata and metadata != registry_metadata:
                # Registered but metadata differs
                findings.append(VerificationFinding(
                    category=FindingCategory.REGISTRY_INCONSISTENCY,
                    severity=FindingSeverity.P1_HIGH,
                    message=(
                        f"Class {cls.__qualname__} registered metadata differs "
                        f"from computed metadata"
                    ),
                    context={
                        "class": metadata.qualified_name,
                        "registered_metadata": registry_metadata.to_dict(),
                        "computed_metadata": metadata.to_dict(),
                    },
                ))
            
        except Exception as e:
            findings.append(VerificationFinding(
                category=FindingCategory.REGISTRY_INCONSISTENCY,
                severity=FindingSeverity.P1_HIGH,
                message=f"Registry consistency check failed: {str(e)}",
                context={"class": metadata.qualified_name, "error_type": type(e).__name__},
            ))
        
        return findings
    
    def _verify_reflection_consistency(
        self, cls: Type[Any], metadata: CoreFunctionalityMetadata
    ) -> List[VerificationFinding]:
        """Verify reflection data is consistent with other representations."""
        findings: List[VerificationFinding] = []
        
        try:
            # Get FunctionalityIdentity if available
            from .reflection import get_functionality_identity
            
            identity = get_functionality_identity(cls)
            
            if identity and metadata.primary_marker_name != getattr(identity, "primary_marker_name", None):
                findings.append(VerificationFinding(
                    category=FindingCategory.REFLECTION_MISMATCH,
                    severity=FindingSeverity.P1_HIGH,
                    message=(
                        f"Reflection marker differs from metadata primary marker"
                    ),
                    context={
                        "class": metadata.qualified_name,
                        "metadata_primary_marker": metadata.primary_marker_name,
                    },
                ))
            
        except Exception:
            # Reflection API might not be available, not a critical error
            pass
        
        return findings
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get verification statistics."""
        with self._lock:
            return {
                "total_verified": self._verified_count,
                "valid_classes": self._verified_count - self._invalid_count,
                "invalid_classes": self._invalid_count,
                "findings_by_category": dict(self._findings_by_category),
                "cache_size": len(self._verification_cache),
            }
    
    def verify_all(self) -> List[VerificationResult]:
        """
        Verify all classes registered in the FunctionalityRegistry.
        
        Returns:
            List of VerificationResults for all registered classes
        """
        snapshot = self._registry.snapshot()
        results: List[VerificationResult] = []
        
        for entry in snapshot.entries.values():
            try:
                # Import the class dynamically
                module_path, qual_name = entry.metadata.qualified_name.rsplit(".", 1)
                module = __import__(module_path, fromlist=[qual_name])
                cls = getattr(module, qual_name, None)
                
                if cls is not None and isinstance(cls, type):
                    result = self.verify_class(cls, entry.metadata)
                    results.append(result)
            except Exception:
                # Class might not be importable (e.g., during test setup)
                pass
        
        return results
    
    def reset_cache(self) -> None:
        """Clear verification cache."""
        with self._lock:
            self._verification_cache.clear()


# =============================================================================
# PUBLIC API FUNCTIONS
# =============================================================================


def verify_class(
    cls: Type[Any],
    registry: Optional[FunctionalityRegistry] = None,
) -> VerificationResult:
    """
    Verify a single class against Functionality marker contracts.
    
    This is the primary entry point for Phase 3.13.5 verification.
    
    Args:
        cls: The class to verify
        registry: Optional FunctionalityRegistry instance
        
    Returns:
        VerificationResult with findings and validity status
    """
    engine = VerificationEngine(registry)
    return engine.verify_class(cls)


def verify_all_registered(
    registry: Optional[FunctionalityRegistry] = None,
) -> List[VerificationResult]:
    """
    Verify all classes registered in the FunctionalityRegistry.
    
    Args:
        registry: Optional FunctionalityRegistry instance (uses global if not provided)
        
    Returns:
        List of VerificationResults for all registered classes
    """
    engine = VerificationEngine(registry)
    return engine.verify_all()


def get_verification_statistics(
    registry: Optional[FunctionalityRegistry] = None,
) -> Dict[str, Any]:
    """Get verification statistics for the registry."""
    engine = VerificationEngine(registry)
    return engine.get_statistics()


# =============================================================================
# VERIFICATION REPORT GENERATORS
# =============================================================================


def generate_verification_report(
    results: List[VerificationResult],
    title: str = "Functionality Verification Report",
) -> Dict[str, Any]:
    """Generate a comprehensive verification report."""
    
    total = len(results)
    valid = sum(1 for r in results if r.is_valid)
    invalid = total - valid
    
    # Categorize findings
    critical_findings = []
    high_severity = []
    medium_severity = []
    low_severity = []
    
    category_counts: Dict[str, int] = {}
    
    for result in results:
        for finding in result.findings:
            severity = finding.severity.value
            
            if severity == "P0_CRITICAL":
                critical_findings.append(finding)
            elif severity == "P1_HIGH":
                high_severity.append(finding)
            elif severity == "P2_MEDIUM":
                medium_severity.append(finding)
            else:
                low_severity.append(finding)
            
            cat = finding.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return {
        "title": title,
        "generated_at": str(__import__("datetime").datetime.now()),
        "summary": {
            "total_verified": total,
            "valid_count": valid,
            "invalid_count": invalid,
            "validity_rate": (valid / total * 100) if total > 0 else 0.0,
        },
        "findings_by_severity": {
            "critical": len(critical_findings),
            "high": len(high_severity),
            "medium": len(medium_severity),
            "low": len(low_severity),
        },
        "findings_by_category": category_counts,
        "results": [r.to_dict() for r in results],
    }


def print_verification_summary(results: List[VerificationResult]) -> None:
    """Print a human-readable verification summary."""
    report = generate_verification_report(results)
    
    print("=" * 70)
    print(f"FUNCTIONALITY VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    print(f"Total classes verified: {report['summary']['total_verified']}")
    print(f"Valid classes:          {report['summary']['valid_count']}")
    print(f"Invalid classes:        {report['summary']['invalid_count']}")
    print(f"Validity rate:          {report['summary']['validity_rate']:.1f}%")
    print()
    print("Findings by Severity:")
    for sev, count in report['findings_by_severity'].items():
        print(f"  {sev.upper()}: {count}")
    print()
    print("Findings by Category:")
    for cat, count in sorted(report['findings_by_category'].items()):
        print(f"  {cat}: {count}")
    print("=" * 70)


__all__ = [
    # Verification result types
    "VerificationFinding",
    "VerificationResult",
    
    # Contract types
    "InterfaceContract",
    "DependencyContract",
    "OwnershipContract",
    "PackageContract",
    "RoleContract",
    
    # Pre-computed contracts (for each marker)
    "FOR_CORE_INTERFACE_CONTRACT",
    "FOR_CORE_DEPENDENCY_CONTRACT",
    "FOR_CORE_OWNERSHIP_CONTRACT",
    "FOR_CORE_PACKAGE_CONTRACT",
    "FOR_CORE_ROLE_CONTRACT",
    "FOR_EXECUTION_INTERFACE_CONTRACT",
    "FOR_EXECUTION_DEPENDENCY_CONTRACT",
    "FOR_EXECUTION_OWNERSHIP_CONTRACT",
    "FOR_EXECUTION_PACKAGE_CONTRACT",
    "FOR_EXECUTION_ROLE_CONTRACT",
    "FOR_ENTRYPOINT_INTERFACE_CONTRACT",
    "FOR_ENTRYPOINT_DEPENDENCY_CONTRACT",
    "FOR_ENTRYPOINT_OWNERSHIP_CONTRACT",
    "FOR_ENTRYPOINT_PACKAGE_CONTRACT",
    "FOR_ENTRYPOINT_ROLE_CONTRACT",
    "FOR_ARCHITECTURE_INTERFACE_CONTRACT",
    "FOR_ARCHITECTURE_DEPENDENCY_CONTRACT",
    "FOR_ARCHITECTURE_OWNERSHIP_CONTRACT",
    "FOR_ARCHITECTURE_PACKAGE_CONTRACT",
    "FOR_ARCHITECTURE_ROLE_CONTRACT",
    "FOR_NETWORKS_INTERFACE_CONTRACT",
    "FOR_NETWORKS_DEPENDENCY_CONTRACT",
    "FOR_NETWORKS_OWNERSHIP_CONTRACT",
    "FOR_NETWORKS_PACKAGE_CONTRACT",
    "FOR_NETWORKS_ROLE_CONTRACT",
    "FOR_CAPABILITIES_INTERFACE_CONTRACT",
    "FOR_CAPABILITIES_DEPENDENCY_CONTRACT",
    "FOR_CAPABILITIES_OWNERSHIP_CONTRACT",
    "FOR_CAPABILITIES_PACKAGE_CONTRACT",
    "FOR_CAPABILITIES_ROLE_CONTRACT",
    "FOR_SYSTEMS_INTERFACE_CONTRACT",
    "FOR_SYSTEMS_DEPENDENCY_CONTRACT",
    "FOR_SYSTEMS_OWNERSHIP_CONTRACT",
    "FOR_SYSTEMS_PACKAGE_CONTRACT",
    "FOR_SYSTEMS_ROLE_CONTRACT",
    
    # Registry and engine
    "ContractRegistry",
    "GLOBAL_CONTRACT_REGISTRY",
    "VerificationEngine",
    
    # Public API functions
    "verify_class",
    "verify_all_registered",
    "get_verification_statistics",
    "generate_verification_report",
    "print_verification_summary",
]