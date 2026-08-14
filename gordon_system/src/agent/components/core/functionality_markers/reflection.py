# Functionality Marker Reflection - Phase 3.13.2
# ================================================

"""
Functionality Marker Identity & Classification System.

This module implements the complete Phase 3.13.2 architecture for:

IDENTITY:
    Every Core component possesses exactly one Functionality Identity.
    Identity describes WHY a component exists (architectural consumer).
    
CLASSIFICATION:
    Components are classified by their primary architectural layer:
        - ForCore: Core infrastructure services
        - ForExecution: Execution layer components  
        - ForEntrypoint: Entry point bootstrap components
        - ForArchitecture: Architectural reflection components
        - ForNetworks: Network/transport layer services
        - ForCapabilities: Agent capability implementations
        - ForSystems: System-level subsystems

VALIDATION:
    - Exactly one primary marker per component (uniqueness)
    - Marker inheritance is shallow (only from CoreFunctionality)
    - Repository-wide validation and reporting

The system enables:
    - Deterministic classification of all Core components
    - Repository inventories grouped by functionality
    - Architecture documentation generation
    - Static analysis for architectural violations
"""

import inspect
import importlib
from typing import (
    TypeVar, Generic, Callable, Any,
    Optional, List, Dict, Set, Tuple, cast
)
from collections import defaultdict
from pathlib import Path

from . import CoreFunctionality

T = TypeVar("T")


# =============================================================================
# MARKER INVENTORY - Repository-wide component analysis
# =============================================================================


class MarkerInventory:
    """
    Repository-wide inventory of components organized by functionality marker.
    
    This class enables:
        - Discovery of all components with a specific marker
        - Statistics about marker distribution
        - Validation of marker usage
        - Architecture documentation generation
    """
    
    def __init__(self) -> None:
        # Maps marker class -> list of component classes
        self._by_marker: Dict[type, List[type]] = defaultdict(list)
        
        # Maps component class -> marker class
        self._by_component: Dict[type, type] = {}
        
        # All discovered components
        self._all_components: Set[type] = set()
    
    def add_component(self, component_class: type, marker_class: type) -> None:
        """Add a component with its primary marker."""
        if not issubclass(marker_class, CoreFunctionality):
            raise ValueError(
                f"Marker {marker_class} must inherit from CoreFunctionality"
            )
        
        self._by_marker[marker_class].append(component_class)
        self._by_component[component_class] = marker_class
        self._all_components.add(component_class)
    
    def get_components(self, marker_class: type) -> List[type]:
        """Get all components for a specific marker."""
        return list(self._by_marker.get(marker_class, []))
    
    def get_marker(self, component_class: type) -> Optional[type]:
        """Get the primary marker for a component."""
        return self._by_component.get(component_class)
    
    @property
    def markers(self) -> List[type]:
        """Get all marker classes with components."""
        return list(self._by_marker.keys())
    
    @property
    def total_components(self) -> int:
        """Total number of discovered components."""
        return len(self._all_components)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the inventory."""
        return {
            "total_markers": len(self.markers),
            "total_components": self.total_components,
            "components_by_marker": {
                marker.__name__: len(comps)
                for marker, comps in self._by_marker.items()
            },
        }


def _get_markers() -> Dict[str, type]:
    """
    Lazy loader for marker classes to avoid circular imports.
    
    Returns a dictionary mapping marker names to marker classes.
    """
    from . import (
        ForCore,
        ForExecution,
        ForEntrypoint,
        ForArchitecture,
        ForNetworks,
        ForCapabilities,
        ForSystems,
    )
    return {
        'ForCore': ForCore,
        'ForExecution': ForExecution,
        'ForEntrypoint': ForEntrypoint,
        'ForArchitecture': ForArchitecture,
        'ForNetworks': ForNetworks,
        'ForCapabilities': ForCapabilities,
        'ForSystems': ForSystems,
    }


def _get_consumer_map() -> Dict[type, str]:
    """Get mapping of marker to consumer layer name."""
    markers = _get_markers()
    return {
        markers['ForCore']: "core",
        markers['ForExecution']: "execution",
        markers['ForEntrypoint']: "entrypoint",
        markers['ForArchitecture']: "architecture",
        markers['ForNetworks']: "networks",
        markers['ForCapabilities']: "capabilities",
        markers['ForSystems']: "systems",
    }


# =============================================================================
# FUNCTIONALITY IDENTITY MODEL
# =============================================================================


class FunctionalityIdentity:
    """
    Represents the exact architectural purpose of a Core component.
    
    Every Core class has exactly one Functionality Identity that answers:
        "Which architectural layer does this component primarily support?"
    
    The identity is:
        - Deterministic: Same input produces same output
        - Machine-verifiable: Can be checked programmatically
        - Architectural: Describes purpose, not implementation
        - Non-behavioral: Does not affect runtime execution
    
    Examples:
        class ExecutionScheduler(CoreService, ForExecution):
            pass
        
        identity = FunctionalityIdentity.from_class(ExecutionScheduler)
        assert identity.primary_marker == ForExecution
        assert identity.consumer == "execution"
    
    Classification Philosophy:
        Identity never answers:
            - Who owns it?
            - Where does it execute?
            - What does it compute?
        
        Identity ONLY answers:
            - Which architectural layer consumes this component?
    """
    
    __slots__ = (
        '_component_class',
        '_primary_marker',
        '_all_markers_in_mro'
    )
    
    def __init__(
        self,
        component_class: type,
        primary_marker: Optional[type],
        all_markers_in_mro: Tuple[type, ...]
    ) -> None:
        """
        Initialize a FunctionalityIdentity.
        
        Args:
            component_class: The Core component class
            primary_marker: The primary functionality marker (or None)
            all_markers_in_mro: All markers found in the MRO
        """
        self._component_class = component_class
        self._primary_marker = primary_marker
        self._all_markers_in_mro = all_markers_in_mro
    
    @property
    def component_class(self) -> type:
        """Get the component class."""
        return self._component_class
    
    @property
    def primary_marker(self) -> Optional[type]:
        """Get the primary functionality marker (or None)."""
        return self._primary_marker
    
    @property
    def all_markers_in_mro(self) -> Tuple[type, ...]:
        """Get all markers found in the MRO."""
        return self._all_markers_in_mro
    
    @property
    def identity_name(self) -> str:
        """Get a human-readable name for the functionality."""
        if self._primary_marker is None:
            return "No Functionality Identity"
        return f"For{self._primary_marker.__name__[3:]}"  # Remove 'For' prefix
    
    @property
    def consumer(self) -> str:
        """Get the architectural consumer layer name."""
        markers = _get_markers()
        consumer_map = _get_consumer_map()
        if self._primary_marker is None:
            return "unknown"
        return consumer_map.get(self._primary_marker, "unknown")
    
    def has_single_marker(self) -> bool:
        """Check if component has exactly one primary marker."""
        # Count non-CoreFunctionality markers in MRO  
        non_base_markers = [
            m for m in self._all_markers_in_mro 
            if m != CoreFunctionality and hasattr(m, '__module__') and 'functionality_markers' in m.__module__
        ]
        return len(non_base_markers) == 1
    
    def is_valid(self) -> bool:
        """Check if the identity follows all Phase 3.13.2 rules."""
        # Must have exactly one primary marker
        if self._primary_marker is None:
            return False
        
        # Check for multiple unrelated markers (not inheritance chain)
        non_base_markers = [
            m for m in self._all_markers_in_mro 
            if m != CoreFunctionality and hasattr(m, '__module__') and 'functionality_markers' in m.__module__
        ]
        
        if len(non_base_markers) > 1:
            # Multiple markers - check if it's a valid inheritance chain
            primary = non_base_markers[0]
            for marker in non_base_markers[1:]:
                if not issubclass(primary, marker):
                    return False
        
        return True
    
    def __repr__(self) -> str:
        return f"FunctionalityIdentity(component={self._component_class.__name__}, " \
               f"primary_marker={self._primary_marker.__name__ if self._primary_marker else None})"


# =============================================================================
# IDENTITY RESOLVER
# =============================================================================


def get_functionality_identity(cls: type) -> FunctionalityIdentity:
    """
    Get the FunctionalityIdentity for a class.
    
    This is the canonical way to determine a component's functionality identity.
    
    Args:
        cls: The class to analyze
        
    Returns:
        A FunctionalityIdentity object describing the component's purpose
    """
    # Find all markers in MRO (excluding CoreFunctionality itself)
    markers_in_mro = []
    for base in cls.__mro__:
        if (
            base != CoreFunctionality 
            and issubclass(base, CoreFunctionality)
            and hasattr(base, '__module__')
            and 'functionality_markers' in base.__module__
        ):
            markers_in_mro.append(base)
    
    # Determine primary marker (first non-CoreFunctionality marker in MRO)
    primary_marker = None
    if markers_in_mro:
        primary_marker = markers_in_mro[0]
    
    return FunctionalityIdentity(
        component_class=cls,
        primary_marker=primary_marker,
        all_markers_in_mro=tuple(markers_in_mro)
    )


# =============================================================================
# UNIQUENESS VALIDATION - Enforce exactly one primary marker
# =============================================================================


class UniquenessValidator:
    """
    Validates that each Core component has exactly one primary functionality marker.
    
    This enforces the Phase 3.13.2 uniqueness requirement:
        "Exactly one primary marker shall exist for every Core component."
    """
    
    def __init__(self) -> None:
        self._errors: List[Dict[str, Any]] = []
    
    def validate_class(self, cls: type) -> Tuple[bool, List[str]]:
        """
        Validate a single class for uniqueness.
        
        Returns:
            (is_valid, error_messages)
        """
        errors: List[str] = []
        
        # Find all markers
        markers_in_mro = []
        for base in cls.__mro__:
            if (
                base != CoreFunctionality 
                and issubclass(base, CoreFunctionality)
                and hasattr(base, '__module__')
                and 'functionality_markers' in base.__module__
            ):
                markers_in_mro.append(base)
        
        if len(markers_in_mro) == 0:
            errors.append(
                f"Component {cls.__name__} has no functionality marker. "
                "Every Core component must have exactly one primary marker."
            )
            return False, errors
        
        # Get non-Base markers
        non_base_markers = [m for m in markers_in_mro if m != CoreFunctionality]
        
        if len(non_base_markers) == 0:
            errors.append(
                f"Component {cls.__name__} inherits only from CoreFunctionality. "
                "A component must inherit from exactly one canonical marker class."
            )
            return False, errors
        
        # Check for multiple unrelated markers
        primary_marker = non_base_markers[0]
        if len(non_base_markers) > 1:
            # Check if this is a valid inheritance chain or invalid multiple inheritance
            for additional_marker in non_base_markers[1:]:
                if not issubclass(primary_marker, additional_marker):
                    errors.append(
                        f"Component {cls.__name__} has multiple unrelated markers: "
                        f"{', '.join(m.__name__ for m in non_base_markers)}. "
                        "A component must have exactly one primary marker. "
                        "Marker inheritance (if any) must be a single chain from CoreFunctionality."
                    )
                    return False, errors
        
        # Check for shallow inheritance - markers should only inherit from CoreFunctionality
        for marker in non_base_markers:
            base_classes = [b for b in marker.__bases__ if issubclass(b, CoreFunctionality)]
            if len(base_classes) > 1:
                errors.append(
                    f"Marker {marker.__name__} inherits from multiple markers: "
                    f"{', '.join(b.__name__ for b in base_classes)}. "
                    "Canonical markers shall inherit only from CoreFunctionality."
                )
                return False, errors
        
        return True, []
    
    def validate_repository(self, inventory: 'MarkerInventory') -> Dict[str, Any]:
        """
        Validate entire repository for uniqueness violations.
        
        Returns:
            Validation report with findings
        """
        self._errors = []
        
        for component in inventory._all_components:
            is_valid, errors = self.validate_class(component)
            if not is_valid:
                self._errors.append({
                    "component": f"{component.__module__}.{component.__name__}",
                    "errors": errors,
                    "severity": "error"
                })
        
        return {
            "total_validated": len(inventory._all_components),
            "unique_count": len(inventory._all_components) - len(self._errors),
            "non_unique_count": len(self._errors),
            "findings": self._errors
        }


# =============================================================================
# INHERITANCE VALIDATION - Enforce shallow inheritance rules
# =============================================================================


class InheritanceValidator:
    """
    Validates marker inheritance follows Phase 3.13.2 rules.
    
    Rules enforced:
        1. Markers shall inherit only from CoreFunctionality
        2. No deep hierarchies of markers (max depth: 2)
        3. No behavioral inheritance in markers
    """
    
    MAX_MARKER_DEPTH = 2  # CoreFunctionality -> ForX is max
    
    def validate_marker_hierarchy(self, marker_class: type) -> Tuple[bool, List[str]]:
        """
        Validate a single marker class's inheritance.
        
        Returns:
            (is_valid, error_messages)
        """
        errors: List[str] = []
        
        # Count depth from CoreFunctionality
        depth = 0
        current = marker_class
        while current != CoreFunctionality and hasattr(current, '__bases__'):
            for base in current.__bases__:
                if issubclass(base, CoreFunctionality):
                    depth += 1
                    current = base
                    break
            else:
                break
            
            if depth > self.MAX_MARKER_DEPTH:
                errors.append(
                    f"Marker {marker_class.__name__} exceeds max inheritance depth "
                    f"of {self.MAX_MARKER_DEPTH}. Markers shall inherit only from CoreFunctionality."
                )
                return False, errors
        
        # Check for multiple inheritance from different marker branches
        marker_bases = []
        for base in marker_class.__bases__:
            if issubclass(base, CoreFunctionality) and base != CoreFunctionality:
                marker_bases.append(base)
        
        if len(marker_bases) > 1:
            errors.append(
                f"Marker {marker_class.__name__} inherits from multiple markers: "
                f"{', '.join(b.__name__ for b in marker_bases)}. "
                "Canonical markers shall have single inheritance."
            )
            return False, errors
        
        # Check for behavioral methods in marker
        for name, attr in inspect.getmembers(marker_class):
            if (
                not name.startswith('_') 
                and callable(attr)
                and hasattr(attr, '__func__')
            ):
                errors.append(
                    f"Marker {marker_class.__name__} contains method '{name}'. "
                    "Functionality markers shall be empty - no behavioral methods."
                )
                return False, errors
        
        return True, []
    
    def validate_all_markers(self) -> Dict[str, Any]:
        """Validate all canonical markers."""
        from . import (
            ForCore, ForExecution, ForEntrypoint, 
            ForArchitecture, ForNetworks, ForCapabilities, ForSystems
        )
        
        markers = [
            ForCore, ForExecution, ForEntrypoint,
            ForArchitecture, ForNetworks, ForCapabilities, ForSystems
        ]
        
        results = {}
        for marker in markers:
            is_valid, errors = self.validate_marker_hierarchy(marker)
            results[marker.__name__] = {
                "valid": is_valid,
                "errors": errors
            }
        
        return results


# =============================================================================
# ARCHITECTURAL INTERPRETATION - Map markers to architectural concepts
# =============================================================================


class ArchitecturalInterpreter:
    """
    Provides architectural interpretation of functionality markers.
    
    This enables:
        - Repository navigation by purpose (not location)
        - Architecture documentation generation  
        - AI-assisted code navigation
    """
    
    def _get_arch_props(self) -> Dict[type, Dict[str, Any]]:
        """Get the architecture properties mapping (lazy-loaded)."""
        markers = _get_markers()
        return {
            markers['ForCore']: {
                "layer": "core",
                "consumer": "infrastructure",
                "responsibility": "runtime substrate services",
                "examples": ["Scheduler", "Registry", "StateStore"],
                "repository_path": "src/agent/components/core/*"
            },
            markers['ForExecution']: {
                "layer": "execution",
                "consumer": "task execution",
                "responsibility": "scheduling, concurrency, cancellation",
                "examples": ["ExecutionScheduler", "ThreadManager", "TaskDispatcher"],
                "repository_path": "src/agent/execution/*"
            },
            markers['ForEntrypoint']: {
                "layer": "entrypoint",
                "consumer": "system bootstrap",
                "responsibility": "initialization, configuration loading",
                "examples": ["ApplicationMain", "BootstrapLoader", "ConfigInitializer"],
                "repository_path": "src/agent/entrypoint/*"
            },
            markers['ForArchitecture']: {
                "layer": "architecture",
                "consumer": "reflection and analysis",
                "responsibility": "dependency tracking, topology mapping",
                "examples": ["DependencyInspector", "ReflectionRegistry", "ArchitectureValidator"],
                "repository_path": "src/agent/architecture/reflection/*"
            },
            markers['ForNetworks']: {
                "layer": "networks",
                "consumer": "data transport",
                "responsibility": "stream publication, message delivery",
                "examples": ["StreamRegistry", "TransportLayer", "MessageRouter"],
                "repository_path": "src/agent/components/core/streams/*"
            },
            markers['ForCapabilities']: {
                "layer": "capabilities",
                "consumer": "agent capabilities",
                "responsibility": "cognition, learning, memory operations",
                "examples": ["CognitiveEngine", "LearningModule", "MemoryManager"],
                "repository_path": "src/agent/capabilities/*"
            },
            markers['ForSystems']: {
                "layer": "systems",
                "consumer": "system subsystems",
                "responsibility": "perception, consciousness, memory storage",
                "examples": ["VisionSystem", "MemorySystem", "ConsciousnessStream"],
                "repository_path": "src/agent/systems/*"
            },
        }
    
    def get_architecture_properties(self, marker: type) -> Optional[Dict[str, Any]]:
        """Get architectural properties for a marker."""
        return self._get_arch_props().get(marker)
    
    def interpret_component(self, cls: type) -> Dict[str, Any]:
        """
        Interpret a component's architecture.
        
        Returns:
            Dictionary with architectural interpretation
        """
        identity = get_functionality_identity(cls)
        primary = identity.primary_marker
        
        props = self._get_arch_props().get(primary, {}) if primary else {}
        
        return {
            "component": cls.__name__,
            "module": cls.__module__,
            "functionality": identity.identity_name,
            "primary_marker": primary.__name__ if primary else None,
            "layer": props.get("layer", "unknown"),
            "consumer": props.get("consumer", "unknown"),
            "responsibility": props.get("responsibility", "unknown"),
            "examples": props.get("examples", []),
            "repository_path": props.get("repository_path", "unknown")
        }
    
    def generate_documentation_section(self, marker: type) -> str:
        """Generate documentation section for a marker."""
        props = self._get_arch_props().get(marker)
        if not props:
            return f"No documentation available for {marker.__name__}"
        
        return f"""
## {marker.__name__}

**Layer**: {props['layer']}  
**Consumer**: {props['consumer']}  
**Responsibility**: {props['responsibility']}

### Repository Path
`{props['repository_path']}`

### Examples
- {props['examples'][0] if props['examples'] else 'N/A'}
"""


# =============================================================================
# DISCOVERY FUNCTIONS - Auto-discover components by marker (Phase 3.13.2)
# =============================================================================


def discover_components_in_module(
    module: Any,
    inventory: MarkerInventory,
    predicate: Callable[[type], bool] | None = None
) -> List[type]:
    """
    Discover all classes in a module that have functionality markers.
    
    Args:
        module: The module to scan
        inventory: Inventory to add findings to
        predicate: Optional filter function (class) -> bool
        
    Returns:
        List of discovered component classes
    """
    import types
    
    discovered: List[type] = []
    
    for name in dir(module):
        obj = getattr(module, name)
        
        # Must be a class
        if not inspect.isclass(obj):
            continue
        
        # Skip ABCs from marker module itself
        if hasattr(obj, '__abstractmethods__') and 'functionality_markers' in obj.__module__:
            continue
            
        # Check for marker inheritance
        marker = None
        for base in obj.__mro__:
            if (
                'functionality_markers' in base.__module__
                and issubclass(base, CoreFunctionality)
                and base != CoreFunctionality
            ):
                marker = base
                break
        
        if marker:
            # Apply predicate filter if provided
            if predicate and not predicate(obj):
                continue
                
            inventory.add_component(obj, marker)
            discovered.append(obj)
    
    return discovered


def discover_components_in_package(
    package_path: str,
    inventory: MarkerInventory | None = None,
    exclude_patterns: Tuple[str, ...] = ("test", "conftest")
) -> MarkerInventory:
    """
    Discover all components in a Python package.
    
    Args:
        package_path: Dotted package path (e.g., 'gordon_system.src.agent.components.core')
        inventory: Optional existing inventory to add to
        exclude_patterns: Patterns to exclude from discovery
        
    Returns:
        Complete marker inventory
    """
    if inventory is None:
        inventory = MarkerInventory()
    
    try:
        package = importlib.import_module(package_path)
    except ImportError as e:
        raise ValueError(f"Could not import package {package_path}: {e}")
    
    # Get the package directory
    package_dir = Path(package.__file__).parent
    
    # Recursively discover all submodules
    for path in package_dir.rglob("*.py"):
        if any(exclude in path.name for exclude in exclude_patterns):
            continue
        
        # Convert to dotted path
        rel_path = path.relative_to(package_dir.parent)
        parts = list(rel_path.parts)
        
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        
        if not parts:
            continue
            
        module_name = ".".join(parts).replace("/", ".")
        
        try:
            module = importlib.import_module(module_name)
            discover_components_in_module(module, inventory)
        except (ImportError, SyntaxError):
            # Skip modules that can't be imported
            continue
    
    return inventory


def validate_marker_usage(cls: type) -> Tuple[bool, List[str]]:
    """
    Validate a class's marker usage follows Phase 3.13.2 rules.
    
    Args:
        cls: The class to validate
        
    Returns:
        (is_valid, error_messages)
    """
    errors: List[str] = []
    
    # Check if the class has any markers
    marker = None
    for base in cls.__mro__:
        if (
            'functionality_markers' in base.__module__
            and issubclass(base, CoreFunctionality)
            and base != CoreFunctionality
        ):
            marker = base
            break
    
    if marker is None:
        errors.append(
            f"Component {cls.__name__} has no functionality marker. "
            "Every Core component must have exactly one primary marker."
        )
        return False, errors
    
    # Check for multiple markers (not inheritance chain)
    all_markers = []
    for base in cls.__mro__:
        if (
            'functionality_markers' in base.__module__
            and issubclass(base, CoreFunctionality)
            and base != CoreFunctionality
        ):
            all_markers.append(base)
    
    # Check uniqueness - only one marker should be direct parent (not inheritance)
    non_inheritance_markers = [
        m for m in all_markers 
        if not any(issubclass(other, m) and other != m for other in all_markers)
    ]
    
    if len(non_inheritance_markers) > 1:
        errors.append(
            f"Component {cls.__name__} has multiple primary markers: "
            f"{', '.join(m.__name__ for m in non_inheritance_markers)}. "
            "A component must have exactly one primary marker."
        )
        return False, errors
    
    # Check that marker inherits only from CoreFunctionality
    base_classes = [
        b for b in marker.__bases__ 
        if issubclass(b, CoreFunctionality)
    ]
    
    if len(base_classes) > 1:
        errors.append(
            f"Marker {marker.__name__} inherits from multiple markers: "
            f"{', '.join(b.__name__ for b in base_classes)}. "
            "Canonical markers shall inherit only from CoreFunctionality."
        )
        return False, errors
    
    return True, []


def validate_repository(inventory: MarkerInventory) -> Dict[str, Any]:
    """
    Validate entire repository for marker violations.
    
    Returns:
        Validation report with findings and recommendations
    """
    validator = UniquenessValidator()
    validation_result = validator.validate_repository(inventory)
    
    # Find orphaned components (no primary marker)
    orphans = [
        c for c in inventory._all_components
        if not any(
            issubclass(m, CoreFunctionality) 
            and m != CoreFunctionality 
            for m in c.__mro__
        )
    ]
    
    return {
        "total_validated": len(inventory._all_components),
        "valid_count": len(inventory._all_components) - validation_result["non_unique_count"],
        "invalid_count": validation_result["non_unique_count"],
        "orphans_count": len(orphans),
        "findings": validation_result["findings"],
        "recommendations": _generate_recommendations(validation_result["findings"], orphans)
    }


def _generate_recommendations(
    findings: List[Dict], 
    orphans: List[type]
) -> List[str]:
    """Generate remediation recommendations."""
    recommendations = []
    
    if orphans:
        recommendations.append(
            f"Add markers to {len(orphans)} components without functionality markers."
        )
    
    for finding in findings:
        component = finding["component"]
        for error in finding["errors"]:
            recommendations.append(
                f"{component}: {error.strip()}"
            )
    
    return recommendations


__all__ = [
    "FunctionalityIdentity",
    "get_functionality_identity",
    "UniquenessValidator",
    "InheritanceValidator",
    "ArchitecturalInterpreter",
    # Inventory
    "MarkerInventory",
    "discover_components_in_module",
    "discover_components_in_package",
    "validate_marker_usage",
    "validate_repository",
]
