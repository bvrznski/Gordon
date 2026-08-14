# Functionality Metaclass Registration & Reflection - Phase 3.13.4
# ================================================================================

"""
Canonical Functionality-Aware Metaclass Integration.

This module implements the canonical class-creation-time mechanism that:

CLASSIFICATION:
    - Detects primary Functionality markers at class creation
    - Resolves complete-MRO marker inheritance
    - Distinguishes direct vs inherited classification
    - Detects conflicts and invalid overrides
    
METADATA:
    - Constructs immutable normalized classification metadata
    - Records classification source, status, and findings
    - Exposes metadata via __core_functionality__ attribute
    
REGISTRY:
    - Registers classes in canonical Functionality registry
    - Enforces uniqueness with stable identities
    - Supports registry sealing for production determinism

PHILOSOPHY:
    - Metaclass is purely observational
    - No runtime activation occurs
    - No ownership transfer occurs  
    - No behavior modification occurs
    
    The metaclass records what the class explicitly declares through inheritance.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from enum import Enum, auto
import threading
import weakref

from . import CoreFunctionality, get_functionality_marker


if TYPE_CHECKING:
    from .registry import FunctionalityRegistry


# =============================================================================
# ENUMERATIONS - Classification Status & Source
# =============================================================================


class ClassificationStatus(Enum):
    """Classification result status."""
    
    VALID_DIRECT = "valid_direct"
    VALID_INHERITED = "valid_inherited"
    VALID_EXEMPT = "valid_exempt"
    FUNCTIONALITY_NEUTRAL = "functionality_neutral"
    UNCLASSIFIED_LEGACY = "unclassified_legacy"
    MIGRATION_PENDING = "migration_pending"
    MISSING_REQUIRED = "missing_required"
    CONFLICTING = "conflicting"
    INVALID_OVERRIDE = "invalid_override"
    INVALID_MARKER = "invalid_marker"
    REGISTRATION_REJECTED = "registration_rejected"


class ClassificationSource(Enum):
    """Where classification information came from."""
    
    DIRECT_MARKER = "direct_marker"
    INHERITED_MARKER = "inherited_marker"
    EXPLICIT_METADATA = "explicit_metadata"
    ENCLOSING_OWNER_DERIVATION = "enclosing_owner_derivation"
    EXEMPTION = "exemption"
    LEGACY_PACKAGE_HINT = "legacy_package_hint"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


class StrictnessMode(Enum):
    """Strictness mode for classification."""
    
    STRICT = "strict"          # Fail on any issues
    MIGRATION = "migration"    # Allow legacy but track findings
    AUDIT_ONLY = "audit_only"  # Collect findings without failing
    TEST = "test"              # Relaxed for test isolation


# =============================================================================
# FINDINGS - Typed Classification Findings
# =============================================================================


@dataclass(frozen=True, order=True)
class Finding:
    """A single classification finding with severity and evidence."""
    
    category: str  # e.g., "MISSING_PRIMARY_FUNCTIONALITY"
    severity: str  # "error", "warning", "info"
    message: str   # Human-readable description
    evidence: Dict[str, Any] = field(default_factory=dict)
    finding_id: str = field(init=False)
    
    def __post_init__(self):
        """Generate stable finding ID."""
        from hashlib import sha256
        key_data = f"{self.category}:{self.message}:{self.evidence}"
        object.__setattr__(self, "finding_id", 
                          f"FND-{sha256(key_data.encode()).hexdigest()[:12].upper()}")


@dataclass(frozen=True)
class ClassificationFindings:
    """Collection of findings with severity aggregation."""
    
    errors: Tuple[Finding, ...]
    warnings: Tuple[Finding, ...]
    infos: Tuple[Finding, ...]
    
    @property
    def has_issues(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def all_findings(self) -> Tuple[Finding, ...]:
        return self.errors + self.warnings + self.infos


# =============================================================================
# EXEMPTIONS - Typed Exemption Model
# =============================================================================


class ExemptionKind(Enum):
    """Categories of exempt classes."""
    
    GENERIC_BASE = "generic_base"
    GENERIC_MIXIN = "generic_mixin"
    INNER_OWNED_MODEL = "inner_owned_model"
    ENUM = "enum"
    EXCEPTION = "exception"
    TYPE_ALIAS = "type_alias"
    CONSTANT_CONTAINER = "constant_container"
    PRIVATE_HELPER = "private_helper"
    TEST_DOUBLE = "test_double"
    GENERATED_CLASS = "generated_class"
    COMPATIBILITY_SHIM = "compatibility_shim"
    IMMUTABLE_VALUE_MODEL = "immutable_value_model"
    PROTOCOL_NEUTRAL = "protocol_neutral"


@dataclass(frozen=True)
class FunctionalityExemption:
    """A typed exemption record."""
    
    kind: ExemptionKind
    reason: str
    declared_by: str  # Module or class that declares the exemption
    source: str       # Where the exemption is defined
    scope: str        # Scope of application (full qualified name pattern)
    expiration_or_removal_condition: Optional[str]
    validation_status: ClassificationStatus
    
    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """Check if exemption has expired."""
        return False  # Default: never expires


# =============================================================================
# SECONDARY ROLES - Extracted from inheritance
# =============================================================================


class SecondaryRole(Enum):
    """Secondary role categories."""
    
    LIFECYCLE = "lifecycle"
    INTEGRATION = "integration"
    RELIABILITY = "reliability"
    OBSERVABILITY = "observability"
    SECURITY = "security"
    PERSISTENCE = "persistence"
    STREAM = "stream"
    EXECUTION = "execution"
    DEPENDENCY = "dependency"


# =============================================================================
# INTEGRATION BOUNDARIES
# =============================================================================


class IntegrationBoundary(Enum):
    """Integration boundary categories."""
    
    EXECUTION = "execution"
    STREAMS = "streams"
    ENTRYPOINT = "entrypoint"
    ARCHITECTURE = "architecture"
    NETWORKS = "networks"
    CAPABILITIES = "capabilities"
    SYSTEMS = "systems"
    LIFECYCLE = "lifecycle"
    PERSISTENCE = "persistence"
    SECURITY = "security"
    OBSERVABILITY = "observability"
    CONTINUITY = "continuity"
    RECOVERY = "recovery"


# =============================================================================
# NORMALIZED FUNCTIONALITY METADATA - Immutable
# =============================================================================


@dataclass(frozen=True)
class CoreFunctionalityMetadata:
    """
    Immutable normalized classification metadata for a class.
    
    This is the single source of truth for Functionality classification.
    All reflection queries return data from this structure.
    """
    
    qualified_name: str  # Fully qualified class name
    canonical_owner: str  # Package/module owner
    
    # Primary classification
    primary_functionality: Optional[Type[CoreFunctionality]]
    primary_marker_name: Optional[str]
    classification_source: ClassificationSource
    
    # Classification status
    requirement_status: ClassificationStatus
    classification_status: ClassificationStatus
    
    # Class properties
    is_abstract: bool
    is_protocol: bool
    is_mixin: bool  # Has mixin characteristics
    is_nested: bool   # Nested within another class
    
    # Extracted metadata
    secondary_roles: Tuple[SecondaryRole, ...]
    integration_boundaries: Tuple[IntegrationBoundary, ...]
    
    # Exemptions and findings
    exemptions: Tuple[FunctionalityExemption, ...]
    findings: Tuple[Finding, ...]
    
    # Schema versioning
    schema_version: str = "1.0.0"
    classification_timestamp: float = field(default_factory=lambda: 0.0)  # Set at creation
    
    def __post_init__(self):
        """Set default timestamp if not provided."""
        import time
        if self.classification_timestamp == 0.0:
            pass  # Use the field's default_factory
    
    @property
    def is_valid(self) -> bool:
        """Check if classification is valid."""
        return (
            self.requirement_status in (ClassificationStatus.VALID_DIRECT, 
                                        ClassificationStatus.VALID_INHERITED,
                                        ClassificationStatus.VALID_EXEMPT)
            and self.classification_status != ClassificationStatus.CONFLICTING
        )
    
    @property
    def has_primary_marker(self) -> bool:
        """Check if class has a primary marker."""
        return self.primary_functionality is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        def serialize_enum(e):
            if isinstance(e, Enum):
                return e.value
            return e
        
        return {
            "qualified_name": self.qualified_name,
            "canonical_owner": self.canonical_owner,
            "primary_functionality": (
                self.primary_functionality.__name__ 
                if self.primary_functionality else None
            ),
            "primary_marker_name": self.primary_marker_name,
            "classification_source": serialize_enum(self.classification_source),
            "requirement_status": serialize_enum(self.requirement_status),
            "classification_status": serialize_enum(self.classification_status),
            "is_abstract": self.is_abstract,
            "is_protocol": self.is_protocol,
            "is_mixin": self.is_mixin,
            "is_nested": self.is_nested,
            "secondary_roles": [serialize_enum(r) for r in self.secondary_roles],
            "integration_boundaries": [serialize_enum(b) for b in self.integration_boundaries],
            "exemptions": [
                {
                    "kind": serialize_enum(e.kind),
                    "reason": e.reason,
                    "declared_by": e.declared_by,
                    "source": e.source,
                    "scope": e.scope,
                }
                for e in self.exemptions
            ],
            "findings": [
                {
                    "category": f.category,
                    "severity": f.severity,
                    "message": f.message,
                    "finding_id": f.finding_id,
                }
                for f in self.findings
            ],
            "schema_version": self.schema_version,
        }


# =============================================================================
# METACLASS INTEGRATION POINT
# =============================================================================


T = TypeVar("T", bound=type)


class FunctionalityMetaclass(ABC):
    """
    Base metaclass for Functionality-aware class creation.
    
    This is the canonical integration point. Concrete implementations
    integrate with existing Core metaclasses.
    
    IMPLEMENTATION NOTE:
        This class should be extended, not used directly.
        It provides hooks that integrate into class creation.
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._registry: Optional["FunctionalityRegistry"] = None
    
    def set_registry(self, registry: "FunctionalityRegistry") -> None:
        """Set the canonical registry for this metaclass instance."""
        with self._lock:
            self._registry = registry
    
    @abstractmethod
    def _classify_class(
        self,
        cls_name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
        strictness_mode: StrictnessMode = StrictnessMode.STRICT
    ) -> Tuple[CoreFunctionalityMetadata, ClassificationFindings]:
        """
        Classify a class at creation time.
        
        Args:
            cls_name: Name of the class being created
            bases: Base classes in MRO order
            namespace: Class namespace dictionary
            strictness_mode: Strictness mode for classification
            
        Returns:
            Tuple of (metadata, findings)
        """
        ...
    
    @abstractmethod
    def _resolve_primary_marker(
        self,
        cls_name: str,
        bases: Tuple[type, ...]
    ) -> Tuple[
        Optional[Type[CoreFunctionality]],  # primary marker or None
        ClassificationSource,               # source of classification
        Tuple[Finding, ...]                 # findings
    ]:
        """
        Resolve the primary Functionality marker from complete MRO.
        
        This is the core algorithm that:
        - Traverses complete MRO (not just direct bases)
        - Detects all canonical markers present
        - Resolves conflicts deterministically
        - Distinguishes direct vs inherited classification
        
        Args:
            cls_name: Name of class being classified
            bases: Tuple of base classes
            
        Returns:
            Tuple of (primary_marker, source, findings)
        """
        ...
    
    @abstractmethod
    def _detect_direct_vs_inherited(
        self,
        cls_name: str,
        direct_bases: Tuple[type, ...],
        mro_markers: Dict[Type[CoreFunctionality], List[str]]  # marker -> list of where found
    ) -> ClassificationSource:
        """
        Determine if classification is direct or inherited.
        
        Args:
            cls_name: Name of class being classified
            direct_bases: Direct base classes (not in MRO order)
            mro_markers: Dict mapping markers to their locations in MRO
            
        Returns:
            ClassificationSource indicating source
        """
        ...
    
    @abstractmethod
    def _check_exemption(
        self,
        cls_name: str,
        module: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any]
    ) -> Optional[FunctionalityExemption]:
        """
        Check if class qualifies for exemption.
        
        Args:
            cls_name: Name of class
            module: Module containing the class
            bases: Base classes
            namespace: Class namespace
            
        Returns:
            Exemption record if applies, None otherwise
        """
        ...
    
    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """
        Called when instantiating the class.
        
        This hook does NOT classify - it just creates instances normally.
        Classification happens during class creation, not instantiation.
        """
        return super().__call__(*args, **kwargs)
    
    def __new__(
        mcs: Type["FunctionalityMetaclass"],
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
        **kwargs: Any
    ) -> type:
        """
        Create a new class with Functionality classification.
        
        This is the METACLASS hook where classification occurs at class creation.
        """
        # Get strictness mode from namespace or environment
        strictness_mode = StrictnessMode.STRICT
        
        # Resolve primary marker and collect findings
        primary_marker, source, resolution_findings = mcs._resolve_primary_marker(
            cls_name=name,
            bases=bases
        )
        
        # Check exemptions
        module = namespace.get("__module__", "unknown")
        exemption = mcs._check_exemption(name, module, bases, namespace)
        
        # Determine classification source (override if exempt)
        if exemption:
            final_source = ClassificationSource.EXEMPTION
            requirement_status = ClassificationStatus.VALID_EXEMPT
            classification_status = ClassificationStatus.VALID_EXEMPT
        else:
            final_source = source
            # Determine requirement and classification status
            if primary_marker is not None:
                if final_source == ClassificationSource.DIRECT_MARKER:
                    requirement_status = ClassificationStatus.VALID_DIRECT
                    classification_status = ClassificationStatus.VALID_DIRECT
                else:
                    requirement_status = ClassificationStatus.VALID_INHERITED
                    classification_status = ClassificationStatus.VALID_INHERITED
            else:
                requirement_status = ClassificationStatus.MISSING_REQUIRED
                classification_status = ClassificationStatus.MISSING_REQUIRED
        
        # Build findings list
        all_findings: List[Finding] = []
        
        # Add resolution findings
        for finding in resolution_findings:
            if finding not in all_findings:
                all_findings.append(finding)
        
        # Check for abstract/protocol/mixin characteristics
        is_abstract = namespace.get("__abstractmethods__", False) is not False
        is_protocol = any(
            hasattr(base, "__origin__") and 
            "typing" in str(type(base).__module__)
            for base in bases
        )
        is_mixin = (
            len(bases) > 0 and
            name.endswith("Mixin") or
            any(getattr(b, "__name__", "").endswith("Mixin") for b in bases)
        )
        
        # Determine nested class status
        is_nested = "." in name
        
        # Extract secondary roles from non-Functionality bases
        secondary_roles: Set[SecondaryRole] = set()
        integration_boundaries: Set[IntegrationBoundary] = set()
        
        for base in bases:
            if not issubclass(base, CoreFunctionality) and base != CoreFunctionality:
                # Check for role indicators
                if hasattr(base, "lifecycle") or name.lower().find("lifecycle") >= 0:
                    secondary_roles.add(SecondaryRole.LIFECYCLE)
                if hasattr(base, "execute") or name.lower().find("execution") >= 0:
                    secondary_roles.add(SecondaryRole.EXECUTION)
        
        # Create metadata
        metadata = CoreFunctionalityMetadata(
            qualified_name=f"{module}.{name}",
            canonical_owner=module,
            primary_functionality=primary_marker,
            primary_marker_name=primary_marker.__name__ if primary_marker else None,
            classification_source=final_source,
            requirement_status=requirement_status,
            classification_status=classification_status,
            is_abstract=is_abstract,
            is_protocol=is_protocol,
            is_mixin=is_mixin,
            is_nested=is_nested,
            secondary_roles=tuple(sorted(secondary_roles, key=lambda r: r.value)),
            integration_boundaries=tuple(sorted(integration_boundaries, key=lambda b: b.value)),
            exemptions=(exemption,) if exemption else (),
            findings=tuple(all_findings),
        )
        
        # Store on class for reflection
        setattr(cls, "__core_functionality__", metadata)
        
        return cls


# =============================================================================
# DEFAULT IMPLEMENTATION - FunctionalityAwareMetaclass
# =============================================================================


class FunctionalityAwareMetaclass(FunctionalityMetaclass):
    """
    Default implementation of Functionality metaclass.
    
    Integrates with Python's metaclass machinery to classify classes at creation.
    """
    
    def _resolve_primary_marker(
        self,
        cls_name: str,
        bases: Tuple[type, ...]
    ) -> Tuple[
        Optional[Type[CoreFunctionality]],
        ClassificationSource,
        Tuple[Finding, ...]
    ]:
        """Resolve primary Functionality marker from complete MRO."""
        # Build complete MRO including the class itself
        all_classes: List[type] = []
        
        # Collect classes from bases
        for base in bases:
            if hasattr(base, "__mro__"):
                all_classes.extend(base.__mro__)
            else:
                all_classes.append(base)
        
        # Add the new class to MRO
        all_classes.append(type(cls_name, bases, {}))
        
        # Find all canonical markers
        marker_counts: Dict[Type[CoreFunctionality], int] = {}
        marker_locations: Dict[Type[CoreFunctionality], List[str]] = {}
        
        for cls in all_classes:
            if hasattr(cls, "__mro__"):
                for base in cls.__mro__:
                    if (
                        base != CoreFunctionality and
                        issubclass(base, CoreFunctionality) and
                        base in _get_canonical_markers()
                    ):
                        marker_counts[base] = marker_counts.get(base, 0) + 1
                        location = f"{base.__module__}.{base.__name__}"
                        if base not in marker_locations:
                            marker_locations[base] = []
                        marker_locations[base].append(location)
        
        findings: List[Finding] = []
        
        # Determine primary marker
        canonical_markers = _get_canonical_markers()
        
        # Count unique non-Canonical markers (direct inheritance from For...)
        direct_marker_count = 0
        for base in bases:
            if (
                base != CoreFunctionality and
                issubclass(base, CoreFunctionality) and
                base in canonical_markers
            ):
                direct_marker_count += 1
        
        # Check for invalid override - descendant adding different marker to classified base
        for base in bases:
            if hasattr(base, "__core_functionality__"):
                base_metadata = getattr(base, "__core_functionality__", None)
                if base_metadata and base_metadata.primary_functionality:
                    # Base has a marker - check if this class adds a different one
                    for marker in canonical_markers:
                        if (
                            any(b == marker for b in bases) and 
                            base_metadata.primary_functionality != marker
                        ):
                            findings.append(Finding(
                                category="INVALID_FUNCTIONALITY_OVERRIDE",
                                severity="error",
                                message=(
                                    f"Class {cls_name} attempts to override primary "
                                    f"Functionality marker of ancestor. This is not allowed."
                                ),
                                evidence={
                                    "class": cls_name,
                                    "ancestor_marker": base_metadata.primary_functionality.__name__,
                                    "attempted_marker": marker.__name__,
                                }
                            ))
                            return None, ClassificationSource.CONFLICTING, tuple(findings)
        
        # Resolve primary based on direct declarations
        if direct_marker_count == 0:
            return None, ClassificationSource.UNKNOWN, tuple(findings)
        elif direct_marker_count == 1:
            # Single direct marker - it's the primary
            for base in bases:
                if (
                    base != CoreFunctionality and
                    issubclass(base, CoreFunctionality) and
                    base in canonical_markers
                ):
                    return base, ClassificationSource.DIRECT_MARKER, tuple(findings)
        else:
            # Multiple direct markers - conflict!
            found_markers = [
                b.__name__ for b in bases
                if b != CoreFunctionality and
                   issubclass(b, CoreFunctionality) and
                   b in canonical_markers
            ]
            findings.append(Finding(
                category="MULTIPLE_PRIMARY_FUNCTIONALITIES",
                severity="error",
                message=(
                    f"Class {cls_name} has multiple primary Functionality markers: "
                    f"{', '.join(found_markers)}"
                ),
                evidence={"markers": found_markers}
            ))
            return None, ClassificationSource.CONFLICTING, tuple(findings)
        
        # Should not reach here
        return None, ClassificationSource.UNKNOWN, tuple(findings)
    
    def _detect_direct_vs_inherited(
        self,
        cls_name: str,
        direct_bases: Tuple[type, ...],
        mro_markers: Dict[Type[CoreFunctionality], List[str]]
    ) -> ClassificationSource:
        """Determine if classification is direct or inherited."""
        # Check if any marker is declared directly in bases
        for base in direct_bases:
            if (
                base != CoreFunctionality and
                issubclass(base, CoreFunctionality) and
                base in _get_canonical_markers()
            ):
                return ClassificationSource.DIRECT_MARKER
        
        # If no direct marker but found in MRO, it's inherited
        if mro_markers:
            return ClassificationSource.INHERITED_MARKER
        
        return ClassificationSource.UNKNOWN
    
    def _check_exemption(
        self,
        cls_name: str,
        module: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any]
    ) -> Optional[FunctionalityExemption]:
        """Check if class qualifies for exemption."""
        # Check for common exempt patterns
        
        # Exception classes
        if any(issubclass(b, Exception) for b in bases):
            return FunctionalityExemption(
                kind=ExemptionKind.EXCEPTION,
                reason="Exception classes are exempt from Functionality classification",
                declared_by=module,
                source="functionality_markers.metaclass._check_exemption",
                scope=f"{module}.{cls_name}",
                expiration_or_removal_condition=None,
                validation_status=ClassificationStatus.VALID_EXEMPT,
            )
        
        # Nested owned models (classes with dots in name or nested within other classes)
        if "." in cls_name:
            return FunctionalityExemption(
                kind=ExemptionKind.INNER_OWNED_MODEL,
                reason="Nested owned model - owned by enclosing class",
                declared_by=module,
                source="functionality_markers.metaclass._check_exemption",
                scope=f"{module}.{cls_name}",
                expiration_or_removal_condition=None,
                validation_status=ClassificationStatus.VALID_EXEMPT,
            )
        
        # Enum classes
        if any("Enum" in str(b) for b in bases):
            return FunctionalityExemption(
                kind=ExemptionKind.ENUM,
                reason="Enum values do not require Functionality classification",
                declared_by=module,
                source="functionality_markers.metaclass._check_exemption",
                scope=f"{module}.{cls_name}",
                expiration_or_removal_condition=None,
                validation_status=ClassificationStatus.VALID_EXEMPT,
            )
        
        # Generic mixins (name ends with Mixin, has multiple bases but no Functionality)
        if cls_name.endswith("Mixin"):
            non_functionality_bases = [
                b for b in bases 
                if not issubclass(b, CoreFunctionality) and b != CoreFunctionality
            ]
            if len(non_functionality_bases) >= 2:
                return FunctionalityExemption(
                    kind=ExemptionKind.GENERIC_MIXIN,
                    reason="Generic mixin - utility class without primary functionality",
                    declared_by=module,
                    source="functionality_markers.metaclass._check_exemption",
                    scope=f"{module}.{cls_name}",
                    expiration_or_removal_condition=None,
                    validation_status=ClassificationStatus.VALID_EXEMPT,
                )
        
        # Abstract classes with no marker
        if namespace.get("__abstractmethods__"):
            return FunctionalityExemption(
                kind=ExemptionKind.GENERIC_BASE,
                reason="Abstract base class - requires implementation by subclasses",
                declared_by=module,
                source="functionality_markers.metaclass._check_exemption",
                scope=f"{module}.{cls_name}",
                expiration_or_removal_condition=None,
                validation_status=ClassificationStatus.FUNCTIONALITY_NEUTRAL,
            )
        
        return None


def _get_canonical_markers() -> Dict[Type[CoreFunctionality], str]:
    """Get mapping of canonical marker classes to their names."""
    from . import (
        ForCore, ForExecution, ForEntrypoint, ForArchitecture,
        ForNetworks, ForCapabilities, ForSystems
    )
    return {
        ForCore: "ForCore",
        ForExecution: "ForExecution", 
        ForEntrypoint: "ForEntrypoint",
        ForArchitecture: "ForArchitecture",
        ForNetworks: "ForNetworks",
        ForCapabilities: "ForCapabilities",
        ForSystems: "ForSystems",
    }


# =============================================================================
# METACLASS INTEGRATION HELPER
# =============================================================================


def integrate_with_existing_metaclass(
    existing_metaclass: Type[type],
    functionality_metaclass: FunctionalityMetaclass = FunctionalityAwareMetaclass()
) -> type:
    """
    Integrate Functionality metaclass with an existing metaclass.
    
    Creates a composite metaclass that delegates to both:
    - The existing metaclass for its responsibilities
    - The Functionality metaclass for classification
    
    Args:
        existing_metaclass: The metaclass to extend
        functionality_metaclass: The Functionality metaclass instance
        
    Returns:
        New composite metaclass type
    """
    
    class CompositeMetaclass(existing_metaclass, FunctionalityAwareMetaclass):  # type: ignore
        """Composite metaclass combining existing and Functionality behavior."""
        
        def __new__(
            mcs,
            name: str,
            bases: Tuple[type, ...],
            namespace: Dict[str, Any],
            **kwargs: Any
        ) -> type:
            """Create class with both existing and Functionality behavior."""
            # Create the class using the MRO's __new__
            cls = super().__new__(mcs, name, bases, namespace, **kwargs)
            
            # Apply Functionality classification
            functionality_metaclass._classify_class(name, bases, namespace)
            
            return cls
        
        def __init__(
            mcs,
            name: str,
            bases: Tuple[type, ...],
            namespace: Dict[str, Any],
            **kwargs: Any
        ) -> None:
            """Initialize with Functionality metaclass registry if available."""
            super().__init__(name, bases, namespace, **kwargs)
            
    return CompositeMetaclass


__all__ = [
    # Enumerations
    "ClassificationStatus",
    "ClassificationSource", 
    "StrictnessMode",
    
    # Findings and Exemptions
    "Finding",
    "ClassificationFindings",
    "ExemptionKind",
    "FunctionalityExemption",
    
    # Roles and Boundaries
    "SecondaryRole",
    "IntegrationBoundary",
    
    # Metadata
    "CoreFunctionalityMetadata",
    
    # Metaclass
    "FunctionalityMetaclass",
    "FunctionalityAwareMetaclass",
    "integrate_with_existing_metaclass",
]