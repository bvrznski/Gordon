# ForCore Classification Policy - Phase 3.13.6
# ==============================================

"""
Core Internal Functionality Classification Framework.

This module provides the classification policy, decision framework,
and canonical responsibility taxonomy for determining which classes
should use the `ForCore` marker.

PHILOSOPHY:
-----------
The `ForCore` marker indicates that a class primarily exists to provide
functionality required by Core itself as Gordon's runtime operating system.

A class is NOT ForCore if its primary recipient would be better served by:
- ForExecution (task scheduling, concurrency, cancellation)
- ForEntrypoint (bootstrap, initialization, config loading)  
- ForArchitecture (dependency analysis, topology mapping)
- ForNetworks (stream publication, message delivery, serialization)
- ForCapabilities (cognition, learning, memory, motivation)
- ForSystems (perception, consciousness, memory storage)

DECISION PROCESS:
-----------------
1. Confirm canonical owner (must be Core package)
2. Identify primary responsibility
3. Identify primary recipient of public contract
4. Apply the "disappearance test":
   If this class disappeared, would the primary capability lost be
   a generic Core mechanism? If yes → ForCore.
5. Document evidence and rationale

CLASSIFICATION EVIDENCE:
------------------------
- Source path
- Public contract (methods, properties)
- Base classes
- Dependencies
- Dependents/callers
- Registration behavior
- Lifecycle ownership

TYPED FINDINGS:
---------------
FORCORE_ASSIGNED_BY_LOCATION_ONLY    - Only package placement supports ForCore
FORCORE_PRIMARY_RECIPIENT_MISMATCH   - Class serves another recipient primarily  
FORCORE_INTERFACE_MISMATCH           - Public interface doesn't match ForCore semantics
FORCORE_DEPENDENCY_VIOLATION         - Depends on concrete semantic implementations
FORCORE_DOCUMENTATION_MISMATCH       - Documentation claims don't match implementation
FORCORE_REGISTRY_MISMATCH            - Registry registration is inconsistent
FORCORE_REFLECTION_MISMATCH          - Reflection metadata is inconsistent
FORCORE_PACKAGE_MISMATCH             - Package doesn't match responsibility profile
FORCORE_ROLE_CONFLICT                - Multiple conflicting responsibilities
FORCORE_SEMANTIC_CONTAMINATION       - Semantic behavior leaks into ForCore class
FORCORE_MULTIPLE_RESPONSIBILITIES    - Class serves multiple recipients equally
FORCORE_SPLIT_REQUIRED               - Should be split into separate classes
FORCORE_UNJUSTIFIED_EXEMPTION        - Exempted but shouldn't be
FORCORE_MISSING_CLASSIFICATION       - Missing primary marker
FORCORE_METACLASS_CONFLICT           - Metaclass integration has issues
FORCORE_MRO_CHANGE                   - MRO would change with new inheritance
FORCORE_REGISTRATION_SIDE_EFFECT     - Registration behavior would change

CLASSIFICATION STATUSES:
------------------------
CONFIRMED_FOR_CORE      - Evidence supports ForCore classification
MIGRATED_TO_FOR_CORE    - Previously classified, now migrated to ForCore
ALREADY_VALID           - Already correctly classified as ForCore
SHOULD_USE_ANOTHER_MARKER - Evidence supports different marker
EXEMPT                  - Exempt from Functionality classification
FUNCTIONALITY_NEUTRAL   - Generic base without primary recipient
AMBIGUOUS               - Evidence supports multiple recipients
SPLIT_REQUIRED          - Class should be split before classification
MIGRATION_DEFERRED      - Should be classified but deferred for now
INVALID                 - Invalid classification decision
INSUFFICIENT_EVIDENCE   - Not enough evidence to decide

RESPONSIBILITY PROFILES:
------------------------
Each profile defines expected characteristics:

CORE_SERVICE_PROFILE:
    Expected: Service base or abstract service with Core-internal contract
    Required: Interface, registry integration, lifecycle participation
    Examples: CoreServiceBase, AbstractService, ServiceRegistry

CORE_REGISTRY_PROFILE:
    Expected: Registry for Core-owned entities
    Required: Registration validation, snapshot support, reflection
    Examples: FunctionalityRegistry, ComponentRegistry

CORE_LIFECYCLE_PROFILE:
    Expected: Lifecycle state machine or transition graph
    Required: State transitions, ownership model, persistence support
    Examples: ThreadLifecycleState, CycleTransitionGraph

CORE_COMPOSITION_PROFILE:
    Expected: Composition roots or dependency binding
    Required: Provider resolution, contract binding, validation
    Examples: ServiceComposer, DependencyBinder

CORE_INTEGRITY_PROFILE:
    Expected: Invariant validator or integrity coordinator
    Required: Validation rules, result contracts, audit trail
    Examples: CoreIntegrityValidator, InvariantChecker

CORE_CONFIGURATION_PROFILE:
    Expected: Configuration loading or validation
    Required: Immutable config, schema validation, generation
    Examples: ConfigLoader, SchemaValidator

CORE_RESOURCE_PROFILE:
    Expected: Resource allocation or capacity management
    Required: Lease model, quota enforcement, reclaim logic
    Examples: ResourceManager, ResourcePool

CORE_SECURITY_PROFILE:
    Expected: Authorization framework or policy evaluator
    Required: Policy rules, scope model, audit logging
    Examples: AuthorizationPolicy, ScopeEvaluator

CORE_RELIABILITY_PROFILE:
    Expected: Recovery coordinator or retry framework
    Required: Budget model, action planning, escalation logic
    Examples: RecoveryCoordinator, RetryBudget

CORE_PERSISTENCE_PROFILE:
    Expected: Serialization contract or checkpoint manager
    Required: Snapshot support, schema versioning, migration
    Examples: SnapshotManager, PersistenceAdapter

CORE_RUNTIME_PROFILE:
    Expected: Runtime context or state infrastructure
    Required: Context propagation, state storage, transitions
    Examples: RuntimeContext, StateStore

CORE_DEPENDENCY_PROFILE:
    Expected: Dependency resolution or graph management
    Required: Cycle detection, validation, health tracking
    Examples: DependencyResolver, CycleDetector
"""

from abc import ABC, abstractmethod
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
from enum import Enum

if TYPE_CHECKING:
    from .registry import FunctionalityRegistry


# =============================================================================
# CLASSIFICATION EVIDENCE MODEL
# =============================================================================


@dataclass(frozen=True, order=True)
class ClassificationEvidence:
    """
    Single piece of evidence supporting a classification decision.
    
    Each evidence item must be:
    - Concrete (specific file, line, or code reference)
    - Relevant (directly supports the classification)
    - Verifiable (can be checked by another reviewer)
    """
    
    source: str  # File path or description
    type: str  # e.g., "inheritance", "interface", "usage"
    details: str  # Specific evidence content
    strength: float = 1.0  # Confidence weight 0.0-1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source": self.source,
            "type": self.type,
            "details": self.details,
            "strength": self.strength,
        }


# =============================================================================
# CLASSIFICATION DECISION
# =============================================================================


class ClassificationDecision(Enum):
    """Classification decision outcome."""
    
    CONFIRMED_FOR_CORE = "confirmed_for_core"
    MIGRATED_TO_FOR_CORE = "migrated_to_for_core"
    ALREADY_VALID = "already_valid"
    SHOULD_USE_ANOTHER_MARKER = "should_use_another_marker"
    EXEMPT = "exempt"
    FUNCTIONALITY_NEUTRAL = "functionality_neutral"
    AMBIGUOUS = "ambiguous"
    SPLIT_REQUIRED = "split_required"
    MIGRATION_DEFERRED = "migration_deferred"
    INVALID = "invalid"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


# =============================================================================
# CLASSIFICATION RECORD
# =============================================================================


@dataclass(frozen=True)
class ClassificationRecord:
    """
    Complete record of a classification decision.
    
    This is the primary output artifact for Phase 3.13.6.
    Each record must include:
    - Full class identification (qualified name, source path)
    - Current and proposed classification
    - Evidence and rationale
    - Responsibility profile
    - Integration boundaries
    """
    
    qualified_name: str  # Fully qualified class name
    source_path: str     # Source file location
    
    # Ownership info
    canonical_owner: str
    implementation_kind: str  # e.g., "class", "abstract", "protocol"
    
    # Classification state
    current_primary_functionality: Optional[str]
    proposed_primary_functionality: Optional[str]  # "ForCore" or other marker name
    
    # Decision evidence
    classification_source: str  # Where classification came from
    classification_rationale: str  # Human-readable justification
    evidence: Tuple[ClassificationEvidence, ...]
    
    # Classification details
    responsibility_profile: Optional[str]
    secondary_roles: Tuple[str, ...] = field(default_factory=tuple)
    integration_boundaries: Tuple[str, ...] = field(default_factory=tuple)
    
    # Visibility and type info
    public_or_internal: str  # "public" or "internal"
    is_abstract: bool
    is_protocol: bool
    is_mixin: bool
    is_nested: bool
    
    # Metadata
    registered: bool
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    
    # Consistency checks
    package_consistency: str  # "consistent", "mismatch", "justified"
    interface_consistency: str  # "satisfied", "missing", "exceeded"
    documentation_consistency: str  # "matches", "mismatch", "unverified"
    
    # Migration info
    migration_required: bool
    split_candidate: bool
    
    # Findings (issues detected)
    findings: Tuple[str, ...] = field(default_factory=tuple)
    
    # Final status
    status: ClassificationDecision
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "qualified_name": self.qualified_name,
            "source_path": self.source_path,
            "canonical_owner": self.canonical_owner,
            "implementation_kind": self.implementation_kind,
            "current_primary_functionality": self.current_primary_functionality,
            "proposed_primary_functionality": self.proposed_primary_functionality,
            "classification_source": self.classification_source,
            "classification_rationale": self.classification_rationale,
            "evidence": [e.to_dict() for e in self.evidence],
            "responsibility_profile": self.responsibility_profile,
            "secondary_roles": list(self.secondary_roles),
            "integration_boundaries": list(self.integration_boundaries),
            "public_or_internal": self.public_or_internal,
            "is_abstract": self.is_abstract,
            "is_protocol": self.is_protocol,
            "is_mixin": self.is_mixin,
            "is_nested": self.is_nested,
            "registered": self.registered,
            "dependencies": list(self.dependencies),
            "package_consistency": self.package_consistency,
            "interface_consistency": self.interface_consistency,
            "documentation_consistency": self.documentation_consistency,
            "migration_required": self.migration_required,
            "split_candidate": self.split_candidate,
            "findings": list(self.findings),
            "status": self.status.value,
        }


# =============================================================================
# CLASSIFICATION FRAMEWORK
# =============================================================================


class ClassificationFramework(ABC):
    """
    Abstract classification framework for Core classes.
    
    Concrete implementations must provide:
    - Evidence collection methods
    - Decision logic
    - Record generation
    """
    
    @abstractmethod
    def classify(
        self,
        qualified_name: str,
        source_path: str,
        current_marker: Optional[str],
        **kwargs: Any
    ) -> ClassificationRecord:
        """
        Classify a class and return the decision record.
        
        Args:
            qualified_name: Fully qualified class name
            source_path: Source file location
            current_marker: Current primary marker if any
            **kwargs: Additional classification-relevant data
            
        Returns:
            ClassificationRecord with complete decision evidence
        """
        ...
    
    @abstractmethod
    def is_forcore(self, record: ClassificationRecord) -> bool:
        """Check if a record's status indicates ForCore classification."""
        return False
    
    @abstractmethod
    def get_responsibility_profiles(self) -> Dict[str, str]:
        """Get available responsibility profile definitions."""
        return {}


# =============================================================================
# CANONICAL RESPONSIBILITY TAXONOMY
# =============================================================================


CANONICAL_RESPONSIBILITIES = {
    # Core runtime infrastructure
    "runtime_context": (
        "Core-owned context management and state storage",
        ["runtime", "state"],
    ),
    "runtime_state_store": (
        "Canonical state persistence for Core lifecycle",
        ["runtime", "persistence", "state"],
    ),
    
    # Core lifecycle authority
    "lifecycle_authority": (
        "Lifecycle transition validation and coordination",
        ["lifecycle", "validation", "coordination"],
    ),
    "lifecycle_state_machine": (
        "Canonical state machine for entities",
        ["lifecycle", "state_machine"],
    ),
    
    # Core composition infrastructure
    "composition_root": (
        "Dependency binding and component assembly",
        ["composition", "dependency", "assembly"],
    ),
    "service_composer": (
        "Service instance creation and wiring",
        ["composition", "services"],
    ),
    
    # Core services
    "core_service_base": (
        "Abstract base for Core-owned services",
        ["services", "base"],
    ),
    
    # Core registries
    "functionality_registry": (
        "Canonical registry for Functionality metadata",
        ["registry", "functionality"],
    ),
    "component_registry": (
        "Registry for Core components",
        ["registry", "components"],
    ),
    
    # Core configuration
    "configuration_contract": (
        "Immutable configuration contracts and validation",
        ["configuration", "contracts"],
    ),
    
    # Core integrity
    "integrity_coordinator": (
        "Invariant validation and repository integrity",
        ["integrity", "validation"],
    ),
    
    # Core dependencies
    "dependency_resolver": (
        "Runtime dependency resolution and cycle detection",
        ["dependency", "resolution"],
    ),
    
    # Core resources
    "resource_manager": (
        "Resource allocation, leasing, and capacity management",
        ["resources", "management"],
    ),
    
    # Core synchronization
    "synchronization_primitives": (
        "Locks, barriers, signals for Core coordination",
        ["synchronization", "primitives"],
    ),
    
    # Core reliability
    "recovery_coordinator": (
        "Generic recovery planning and budget management",
        ["reliability", "recovery"],
    ),
    
    # Core persistence
    "persistence_contract": (
        "Serialization contracts and checkpoint infrastructure",
        ["persistence", "serialization"],
    ),
    
    # Core security
    "authorization_framework": (
        "Core authorization policies and scope validation",
        ["security", "authorization"],
    ),
    
    # Core diagnostics
    "diagnostic_coordinator": (
        "Generic diagnostic collection and reporting",
        ["diagnostics", "observability"],
    ),
}


# =============================================================================
# DECISION HELPER FUNCTIONS
# =============================================================================


def primary_recipient_test(
    class_name: str,
    public_contract: List[str],
    dependents: List[str],
) -> Tuple[str, str]:
    """
    Apply the primary recipient test.
    
    Args:
        class_name: Class name being classified
        public_contract: List of methods/properties exposed publicly
        dependents: List of classes that depend on this one
        
    Returns:
        Tuple of (recipient_type, justification)
    """
    # Check for patterns indicating primary recipient
    
    execution_indicators = ["scheduler", "executor", "cancellation", "timeout"]
    entrypoint_indicators = ["bootstrap", "main", "entry", "startup"]
    architecture_indicators = ["architectural", "dependency.*analysis", "topology"]
    networks_indicators = ["network", "stream.*publication", "message.*delivery"]
    capabilities_indicators = ["capability", "cognition", "learning", "memory.*operation"]
    systems_indicators = ["system", "perception", "consciousness", "persistence.*adapter"]
    
    for indicator in execution_indicators:
        if any(indicator in name.lower() for name in [class_name] + public_contract):
            return ("execution", f"Class {class_name} serves execution layer")
    
    for indicator in entrypoint_indicators:
        if any(indicator in name.lower() for name in [class_name] + public_contract):
            return ("entrypoint", f"Class {class_name} serves entry point bootstrap")
    
    # Check dependents
    core_dependents = sum(
        1 for d in dependents if "core" in d.lower() and "system" not in d.lower()
    )
    if core_dependents > len(dependents) * 0.7:
        return ("core", f"Class {class_name} primarily serves Core (70%+ dependents are Core)")
    
    return ("core", f"Class {class_name} primarily serves Core infrastructure")


def disappearance_test(
    class_name: str,
    primary_capabilites: List[str],
) -> Tuple[bool, str]:
    """
    Apply the "disappearance test".
    
    If this class disappeared, would the primary capability lost be
    a generic Core mechanism?
    
    Args:
        class_name: Class name being evaluated
        primary_capabilites: List of capabilities provided by this class
        
    Returns:
        Tuple of (is_core_justified, justification)
    """
    core_capabilities = [
        "runtime state management",
        "lifecycle coordination",
        "dependency resolution",
        "configuration loading",
        "registry maintenance",
        "synchronization primitives",
        "resource allocation",
        "persistence contracts",
        "security framework",
    ]
    
    for cap in primary_capabilites:
        if any(core_cap in cap.lower() for core_cap in core_capabilities):
            return (True, f"Capability '{cap}' is a Core-internal mechanism")
    
    return (False, f"No Core-internal capability found in {class_name}")


def create_classification_record(
    qualified_name: str,
    source_path: str,
    canonical_owner: str = "Core",
    implementation_kind: str = "class",
    current_marker: Optional[str] = None,
    proposed_marker: Optional[str] = "ForCore",
    classification_source: str = "manual_analysis",
    rationale: str = "",
    evidence: Optional[List[ClassificationEvidence]] = None,
    responsibility_profile: Optional[str] = None,
    public_or_internal: str = "public",
    is_abstract: bool = False,
    is_protocol: bool = False,
    is_mixin: bool = False,
    is_nested: bool = False,
    migration_required: bool = True,
    split_candidate: bool = False,
    findings: Optional[List[str]] = None,
) -> ClassificationRecord:
    """
    Create a new classification record.
    
    This is the primary output function for Phase 3.13.6.
    """
    if evidence is None:
        evidence = []
    if findings is None:
        findings = []
    
    # Determine status based on proposed marker and analysis
    if proposed_marker == "ForCore":
        if current_marker == "ForCore":
            status = ClassificationDecision.ALREADY_VALID
        else:
            status = ClassificationDecision.CONFIRMED_FOR_CORE
    elif proposed_marker is None:
        status = ClassificationDecision.EXEMPT
    elif proposed_marker in ["Execution", "Entrypoint"]:
        status = ClassificationDecision.SHOULD_USE_ANOTHER_MARKER
    else:
        status = ClassificationDecision.AMBIGUOUS
    
    return ClassificationRecord(
        qualified_name=qualified_name,
        source_path=source_path,
        canonical_owner=canonical_owner,
        implementation_kind=implementation_kind,
        current_primary_functionality=current_marker,
        proposed_primary_functionality=proposed_marker,
        classification_source=classification_source,
        classification_rationale=rationale,
        evidence=tuple(evidence),
        responsibility_profile=responsibility_profile,
        public_or_internal=public_or_internal,
        is_abstract=is_abstract,
        is_protocol=is_protocol,
        is_mixin=is_mixin,
        is_nested=is_nested,
        migration_required=migration_required,
        split_candidate=split_candidate,
        findings=tuple(findings) if isinstance(findings, list) else tuple(),
        status=status,
    )


__all__ = [
    "ClassificationEvidence",
    "ClassificationDecision",
    "ClassificationRecord",
    "ClassificationFramework",
    "CANONICAL_RESPONSIBILITIES",
    "primary_recipient_test",
    "disappearance_test",
    "create_classification_record",
]
