"""Duplicate and hidden authority detection.

Phase 3.7.2: Authority, Dependency, Package, Import, and Ownership Architecture
==============================================================================

This module provides detection capabilities for:

1. Duplicate authorities - multiple implementations claiming the same responsibility
2. Hidden authorities - authority-like behavior in unexpected places (globals, singletons)
3. Service locators - unrestricted access patterns that bypass explicit dependency declaration
4. Architecture conflicts - incompatible authority relationships
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum
import time

import ast


# =============================================================================
# DUPLICATE AUTHORITY MODELS
# =============================================================================


class DuplicateAuthorityType(Enum):
    """Types of duplicate authorities."""
    
    SAME_ID_DIFFERENT_IMPL = "same_id_different_impl"
    DIFFERENT_IDS_SAME_RESPONSIBILITY = "different_ids_same_responsibility"
    OVERLAPPING_STATE_DOMAINS = "overlapping_state_domains"
    INDEPENDENT_MUTATION_OWNERS = "independent_mutation_owners"
    
    # Hidden authority types
    MODULE_GLOBAL_AUTHORITY = "module_global_authority"
    SINGLETON_INSTANCE_AUTHORITY = "singleton_instance_authority"
    CACHE_BASED_AUTHORITY = "cache_based_authority"
    DEPRECATED_COMPATIBILITY_ALIAS = "deprecated_compatibility_alias"


@dataclass(frozen=True)
class DuplicateAuthorityFinding:
    """A finding about a duplicate authority."""
    
    finding_id: str
    finding_type: DuplicateAuthorityType
    
    # The conflicting authorities
    first_authority_id: str
    first_implementation: str
    second_authority_id: Optional[str] = None
    second_implementation: Optional[str] = None
    
    # Evidence
    evidence: str = ""
    
    # Severity
    severity: str = "warning"  # info, warning, critical, error
    
    # Remediation guidance
    remediation: Optional[str] = None
    
    # Resolution status
    resolved: bool = False
    resolution_notes: Optional[str] = None


@dataclass(frozen=True)
class AuthorityConflict:
    """A conflict between authority implementations."""
    
    conflict_id: str
    conflict_type: str  # DUPLICATE, CONFLICTING_RESPONSIBILITIES, etc.
    
    # Involved authorities
    involved_authorities: Tuple[str, ...]
    
    # The conflicting aspect
    conflicting_aspect: str
    
    # Severity
    severity: str = "error"
    
    # Resolution
    resolved: bool = False
    resolution_strategy: Optional[str] = None


# =============================================================================
# HIDDEN AUTHORITY MODELS
# =============================================================================


class HiddenAuthorityKind(Enum):
    """Kinds of hidden authorities."""
    
    MODULE_GLOBAL_SINGLETON = "module_global_singleton"
    CLASS_VARIABLE_SINGLETON = "class_variable_singleton"
    DEFAULT_ARGUMENT_SINGLETON = "default_argument_singleton"
    CACHE_DECORATOR_SINGLETON = "cache_decorator_singleton"
    METACLASS_REGISTERED_SINGLETON = "metaclass_registered_singleton"
    THREAD_LOCAL_AUTHORITY = "thread_local_authority"
    CONTEXT_VAR_AUTHORITY = "context_var_authority"
    LATE_BOUND_GLOBAL = "late_bound_global"
    
    # Service locator patterns
    STRING_BASED_GETTER = "string_based_getter"
    DYNAMIC_REGISTRY_LOOKUP = "dynamic_registry_lookup"


@dataclass(frozen=True)
class HiddenAuthorityFinding:
    """A finding about a hidden authority."""
    
    finding_id: str
    
    # Location of the hidden authority
    module_path: str
    line_number: Optional[int] = None
    symbol_name: Optional[str] = None
    
    # What kind of hidden authority
    hidden_kind: HiddenAuthorityKind
    
    # Evidence
    evidence: str = ""
    
    # Severity
    severity: str = "warning"
    
    # Recommendation
    recommendation: Optional[str] = None


# =============================================================================
# SERVICE LOCATOR MODELS
# =============================================================================


class ServiceLocatorPattern(Enum):
    """Types of service locator patterns."""
    
    STRING_BASED_GETTER = "string_based_getter"
    TYPE_BASED_RESOLVER = "type_based_resolver"
    GLOBAL_CONTAINER_ACCESS = "global_container_access"
    DYNAMIC_CONTEXT_LOOKUP = "dynamic_context_lookup"
    IMPLICIT_SINGLETON_ACCESS = "implicit_singleton_access"


@dataclass(frozen=True)
class ServiceLocatorFinding:
    """A finding about service locator pattern usage."""
    
    finding_id: str
    
    # Location
    module_path: str
    line_number: Optional[int] = None
    symbol_name: Optional[str] = None
    
    # Pattern detected
    pattern_type: ServiceLocatorPattern
    
    # Details
    details: str = ""
    
    # Severity
    severity: str = "warning"
    
    # Recommendation
    recommendation: Optional[str] = None


# =============================================================================
# DETECTION RESULTS
# =============================================================================


@dataclass(frozen=True)
class DuplicateAuthorityReport:
    """Complete report of duplicate authority detection."""
    
    runtime_id: str
    detected_at: float
    
    # Findings
    duplicate_authorities: Tuple[DuplicateAuthorityFinding, ...]
    
    # Summary statistics
    total_duplicates: int
    critical_count: int
    warning_count: int
    info_count: int


@dataclass(frozen=True)
class HiddenAuthorityReport:
    """Complete report of hidden authority detection."""
    
    runtime_id: str
    detected_at: float
    
    # Findings
    hidden_authorities: Tuple[HiddenAuthorityFinding, ...]
    
    # Summary statistics
    total_hidden: int
    critical_count: int
    warning_count: int


@dataclass(frozen=True)
class ServiceLocatorReport:
    """Complete report of service locator detection."""
    
    runtime_id: str
    detected_at: float
    
    # Findings
    service_locators: Tuple[ServiceLocatorFinding, ...]
    
    # Summary statistics
    total_service_locators: int
    critical_count: int
    warning_count: int


# =============================================================================
# DETECTOR CLASSES
# =============================================================================


class DuplicateAuthorityDetector:
    """
    Detects duplicate authority implementations in the system.
    
    Rules for detection:
        1. Same responsibility, multiple mutable owners = DUPLICATE
        2. Same authority ID, different implementations = CONFLICT
        3. Different IDs owning same state domain = OVERLAP
        4. Compatibility alias with independent state = ILLEGAL
        
    Detection is done by comparing authority descriptors or analyzing
    the actual code for patterns that suggest hidden duplication.
    """
    
    def __init__(self) -> None:
        """Initialize the duplicate detector."""
        self._findings: List[DuplicateAuthorityFinding] = []
    
    def detect_from_descriptors(
        self,
        descriptors: Tuple[Dict[str, Any], ...]
    ) -> DuplicateAuthorityReport:
        """
        Detect duplicates from authority descriptors.
        
        Args:
            descriptors: List of authority descriptor dictionaries
            
        Returns:
            Report with all duplicate findings
        """
        findings: List[DuplicateAuthorityFinding] = []
        
        # Group by responsibility to find duplicate authorities
        responsibility_map: Dict[str, List[Dict[str, Any]]] = {}
        for desc in descriptors:
            resp = desc.get("responsibility", "")
            if resp not in responsibility_map:
                responsibility_map[resp] = []
            responsibility_map[resp].append(desc)
        
        # Check for duplicates
        for responsibility, owners in responsibility_map.items():
            if len(owners) > 1:
                # Multiple implementations claim the same responsibility
                finding_id = f"DA-{responsibility[:20]}"
                findings.append(DuplicateAuthorityFinding(
                    finding_id=finding_id,
                    finding_type=DuplicateAuthorityType.DIFFERENT_IDS_SAME_RESPONSIBILITY,
                    first_authority_id=owners[0].get("authority_id", "unknown"),
                    first_implementation=owners[0].get("implementation_identity", "unknown"),
                    second_authority_id=owners[1].get("authority_id", "unknown"),
                    second_implementation=owners[1].get("implementation_identity", "unknown"),
                    evidence=f"Multiple implementations claim responsibility: {responsibility}",
                    severity="critical",
                    remediation=(
                        f"Merge or delegate one authority to own '{responsibility}'. "
                        "Other implementations should be delegates, not independent authorities."
                    )
                ))
        
        return DuplicateAuthorityReport(
            runtime_id="",
            detected_at=time.monotonic(),
            duplicate_authorities=tuple(findings),
            total_duplicates=len(findings),
            critical_count=sum(1 for f in findings if f.severity == "critical"),
            warning_count=sum(1 for f in findings if f.severity == "warning"),
            info_count=sum(1 for f in findings if f.severity == "info")
        )
    
    def detect_from_code(
        self,
        module_path: str
    ) -> Tuple[DuplicateAuthorityFinding, ...]:
        """
        Detect duplicate authorities by analyzing Python code.
        
        This is a static analysis pass that looks for:
            - Multiple classes with similar names in same module
            - Singleton patterns (instance(), get_instance())
            - Global mutable state
        
        Args:
            module_path: Path to the module file
            
        Returns:
            Tuple of duplicate findings
        """
        # Placeholder for static code analysis
        return ()
    
    def _check_module_level_singletons(
        self,
        tree: ast.Module,
        module_path: str,
        findings: List[HiddenAuthorityFinding]
    ) -> None:
        """Check for module-level singleton patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        
                        # Check if it's a singleton pattern
                        if (name.startswith("_instance") or 
                            name.endswith("instance") or 
                            name == "instance"):
                            
                            findings.append(HiddenAuthorityFinding(
                                finding_id=f"HM-{hash(name)}",
                                module_path=module_path,
                                line_number=node.lineno,
                                symbol_name=name,
                                hidden_kind=HiddenAuthorityKind.MODULE_GLOBAL_SINGLETON,
                                evidence=f"Module-level singleton detected: {name}",
                                severity="critical",
                                recommendation=(
                                    f"Remove the module-level '{name}' singleton. "
                                    "If needed, inject as a dependency or use runtime-scoped instantiation."
                                )
                            ))


class HiddenAuthorityDetector:
    """
    Detects hidden authority behavior that may not be apparent from
    public APIs.
    
    Hidden authorities are often:
        - Module-level singletons
        - Class variable singletons  
        - Decorator-registered instances
        - Thread-local or context-local state
    
    Detection methods:
        1. AST analysis for singleton patterns
        2. Static analysis of global declarations
        3. Pattern matching for common hidden authority idioms
    """
    
    def __init__(self) -> None:
        """Initialize the hidden authority detector."""
        self._findings: List[HiddenAuthorityFinding] = []
    
    def detect_from_code(
        self,
        module_path: str,
        source_code: str
    ) -> Tuple[HiddenAuthorityFinding, ...]:
        """
        Detect hidden authorities from source code.
        
        Args:
            module_path: Path to the Python module
            source_code: The source code
            
        Returns:
            Tuple of hidden authority findings
        """
        findings: List[HiddenAuthorityFinding] = []
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return ()
        
        # Check for various singleton patterns
        self._check_module_level_singletons(tree, module_path, findings)
        self._check_class_variable_singletons(tree, module_path, findings)
        self._check_default_argument_singletons(tree, module_path, findings)
        
        return tuple(findings)
    
    def _check_module_level_singletons(
        self,
        tree: ast.Module,
        module_path: str,
        findings: List[HiddenAuthorityFinding]
    ) -> None:
        """Check for module-level singleton patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        
                        # Check if it's a singleton pattern
                        if (name.startswith("_instance") or 
                            name.endswith("instance") or 
                            name == "instance"):
                            
                            findings.append(HiddenAuthorityFinding(
                                finding_id=f"HM-{hash(name)}",
                                module_path=module_path,
                                line_number=node.lineno,
                                symbol_name=name,
                                hidden_kind=HiddenAuthorityKind.MODULE_GLOBAL_SINGLETON,
                                evidence=f"Module-level singleton detected: {name}",
                                severity="critical",
                                recommendation=(
                                    f"Remove the module-level '{name}' singleton. "
                                    "If needed, inject as a dependency or use runtime-scoped instantiation."
                                )
                            ))
    
    def _check_class_variable_singletons(
        self,
        tree: ast.Module,
        module_path: str,
        findings: List[HiddenAuthorityFinding]
    ) -> None:
        """Check for class variable singletons."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                name = target.id
                                if name == "instance":
                                    findings.append(HiddenAuthorityFinding(
                                        finding_id=f"HC-{hash(node.name)}",
                                        module_path=module_path,
                                        line_number=node.lineno,
                                        symbol_name=node.name,
                                        hidden_kind=HiddenAuthorityKind.CLASS_VARIABLE_SINGLETON,
                                        evidence=f"Class variable singleton in {node.name}",
                                        severity="warning",
                                        recommendation=(
                                            f"Convert {node.name} to a factory pattern. "
                                            "Return new instances from factory functions."
                                        )
                                    ))
    
    def _check_default_argument_singletons(
        self,
        tree: ast.Module,
        module_path: str,
        findings: List[HiddenAuthorityFinding]
    ) -> None:
        """Check for default argument singleton patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check function defaults
                for default in node.args.defaults:
                    if isinstance(default, ast.Call):
                        if hasattr(default.func, 'id') and default.func.id.endswith('Instance'):
                            findings.append(HiddenAuthorityFinding(
                                finding_id=f"HA-{hash(node.name)}",
                                module_path=module_path,
                                line_number=node.lineno,
                                symbol_name=node.name,
                                hidden_kind=HiddenAuthorityKind.DEFAULT_ARGUMENT_SINGLETON,
                                evidence=f"Default argument singleton detected in {node.name}",
                                severity="warning",
                                recommendation=(
                                    f"Avoid using mutable default arguments in {node.name}. "
                                    "Use None with lazy initialization instead."
                                )
                            ))


class ServiceLocatorDetector:
    """
    Detects service locator patterns that allow unrestricted resolution.
    
    Permitted lookup (narrow, typed):
        - Runtime-scoped
        - Owned
        - Non-mutating
        
    Prohibited lookup (unrestricted):
        - get_service(name: str)  # string-based
        - resolve(type)           # type-based from global container
        - context["key"]          # dynamic dictionary lookup
    """
    
    def __init__(self) -> None:
        """Initialize the service locator detector."""
        self._findings: List[ServiceLocatorFinding] = []
    
    def detect_from_code(
        self,
        module_path: str,
        source_code: str
    ) -> Tuple[ServiceLocatorFinding, ...]:
        """
        Detect service locator patterns from source code.
        
        Args:
            module_path: Path to the Python module
            source_code: The source code
            
        Returns:
            Tuple of service locator findings
        """
        findings: List[ServiceLocatorFinding] = []
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return ()
        
        self._check_get_methods(tree, module_path, findings)
        self._check_dict_lookups(tree, module_path, findings)
        
        return tuple(findings)
    
    def _check_get_methods(
        self,
        tree: ast.Module,
        module_path: str,
        findings: List[ServiceLocatorFinding]
    ) -> None:
        """Check for get() methods that could be service locators."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == "get" or node.name.startswith("get_"):
                    # Check if it's a string-based lookup
                    args = [a.arg for a in node.args.args]
                    if len(args) >= 1 and args[0] == "key":
                        findings.append(ServiceLocatorFinding(
                            finding_id=f"SL-{hash(node.name)}",
                            module_path=module_path,
                            line_number=node.lineno,
                            symbol_name=node.name,
                            pattern_type=ServiceLocatorPattern.STRING_BASED_GETTER,
                            details=(
                                f"'get()' method found with string/key parameter. "
                                "This allows arbitrary lookup without type safety."
                            ),
                            severity="warning",
                            recommendation=(
                                "Replace with typed getter methods or use dependency injection. "
                                "If runtime lookup is needed, restrict to explicit extension points."
                            )
                        ))

    def _check_dict_lookups(
        self,
        tree: ast.Module,
        module_path: str,
        findings: List[ServiceLocatorFinding]
    ) -> None:
        """Check for dictionary-based lookups that could be service locators."""
        # Placeholder - would check for context["key"], registry.get("name"), etc.
        pass


def detect_architecture_issues(
    descriptors: Tuple[Dict[str, Any], ...],
    modules: Dict[str, str]
) -> Tuple[
    DuplicateAuthorityFinding,
    HiddenAuthorityFinding,
    ServiceLocatorFinding
]:
    """
    Detect all architecture issues from descriptors and source code.
    
    Args:
        descriptors: Authority descriptors
        modules: Mapping of module paths to source code
        
    Returns:
        Tuple of (duplicates, hidden, service_locators) findings
    """
    duplicate_detector = DuplicateAuthorityDetector()
    hidden_detector = HiddenAuthorityDetector()
    service_locator_detector = ServiceLocatorDetector()
    
    duplicates = duplicate_detector.detect_from_descriptors(descriptors)
    
    all_hidden: List[HiddenAuthorityFinding] = []
    for module_path, source in modules.items():
        findings = hidden_detector.detect_from_code(module_path, source)
        all_hidden.extend(findings)
    
    all_service_locators: List[ServiceLocatorFinding] = []
    for module_path, source in modules.items():
        findings = service_locator_detector.detect_from_code(module_path, source)
        all_service_locators.extend(findings)
    
    return (
        duplicates.duplicate_authorities,
        tuple(all_hidden),
        tuple(all_service_locators)
    )


__all__ = [
    # Duplicate authority models
    "DuplicateAuthorityType",
    "DuplicateAuthorityFinding",
    "AuthorityConflict",
    
    # Hidden authority models
    "HiddenAuthorityKind",
    "HiddenAuthorityFinding",
    
    # Service locator models
    "ServiceLocatorPattern",
    "ServiceLocatorFinding",
    
    # Reports
    "DuplicateAuthorityReport",
    "HiddenAuthorityReport",
    "ServiceLocatorReport",
    
    # Detectors
    "DuplicateAuthorityDetector",
    "HiddenAuthorityDetector",
    "ServiceLocatorDetector",
    "detect_architecture_issues",
]