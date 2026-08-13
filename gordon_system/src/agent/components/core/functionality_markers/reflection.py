# Functionality Marker Reflection - Phase 3.13.1
# ================================================

"""
Reflection support for Core Functionality Markers.

This module provides utilities to discover, analyze, and inventory components
based on their functionality markers.
"""

import inspect
import importlib
from typing import TypeVar, Generic, Callable, Any
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
        self._by_marker: dict[type, list[type]] = defaultdict(list)
        
        # Maps component class -> marker class
        self._by_component: dict[type, type] = {}
        
        # All discovered components
        self._all_components: set[type] = set()
    
    def add_component(self, component_class: type, marker_class: type) -> None:
        """Add a component with its primary marker."""
        if not issubclass(marker_class, CoreFunctionality):
            raise ValueError(
                f"Marker {marker_class} must inherit from CoreFunctionality"
            )
        
        self._by_marker[marker_class].append(component_class)
        self._by_component[component_class] = marker_class
        self._all_components.add(component_class)
    
    def get_components(self, marker_class: type) -> list[type]:
        """Get all components for a specific marker."""
        return list(self._by_marker.get(marker_class, []))
    
    def get_marker(self, component_class: type) -> type | None:
        """Get the primary marker for a component."""
        return self._by_component.get(component_class)
    
    @property
    def markers(self) -> list[type]:
        """Get all marker classes with components."""
        return list(self._by_marker.keys())
    
    @property
    def total_components(self) -> int:
        """Total number of discovered components."""
        return len(self._all_components)
    
    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about the inventory."""
        return {
            "total_markers": len(self.markers),
            "total_components": self.total_components,
            "components_by_marker": {
                marker.__name__: len(comps)
                for marker, comps in self._by_marker.items()
            },
        }


# =============================================================================
# DISCOVERY ENGINE - Auto-discover components by marker
# =============================================================================


def discover_components_in_module(
    module: Any, 
    inventory: MarkerInventory,
    predicate: Callable[[type], bool] | None = None
) -> list[type]:
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
    
    discovered: list[type] = []
    
    for name in dir(module):
        obj = getattr(module, name)
        
        # Must be a class
        if not inspect.isclass(obj):
            continue
        
        # Skip ABCs from marker module itself
        if hasattr(obj, '__abstractmethods__') and obj.__module__.startswith('gordon_system.src.agent.components.core.functionality_markers'):
            continue
            
        # Check for marker inheritance
        marker = None
        for base in obj.__mro__:
            if (
                base.__module__.startswith('gordon_system.src.agent.components.core.functionality_markers')
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
    exclude_patterns: tuple[str, ...] = ("test", "conftest")
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


# =============================================================================
# VALIDATION - Check for marker correctness
# =============================================================================


def validate_marker_usage(component_class: type) -> tuple[bool, list[str]]:
    """
    Validate that a component has correct marker usage.
    
    Returns:
        (is_valid, errors)
    """
    errors: list[str] = []
    
    # Get all markers in MRO
    markers_found = []
    for base in component_class.__mro__:
        if (
            base != CoreFunctionality 
            and issubclass(base, CoreFunctionality)
        ):
            markers_found.append(base)
    
    # Must have exactly one primary marker
    if len(markers_found) == 0:
        errors.append(
            f"Component {component_class.__name__} has no functionality marker. "
            "All Core components must inherit from exactly one marker class."
        )
    elif len(markers_found) > 1:
        # Multiple markers found - check for inheritance chain
        if not _is_marker_inheritance_chain(markers_found):
            errors.append(
                f"Component {component_class.__name__} has multiple unrelated markers: "
                f"{[m.__name__ for m in markers_found]}. "
                "A component may have only one primary marker."
            )
    
    return len(errors) == 0, errors


def _is_marker_inheritance_chain(markers: list[type]) -> bool:
    """
    Check if markers form a valid inheritance chain (not multiple parents).
    
    A valid inheritance chain means all markers are in the same line of descent.
    Multiple independent marker inheritance is invalid.
    """
    if len(markers) <= 1:
        return True
    
    # Get the primary marker (closest to the class)
    primary = markers[0]
    
    # Check if other markers are base classes
    for marker in markers[1:]:
        if not issubclass(primary, marker):
            return False
    
    return True


def validate_repository(inventory: MarkerInventory) -> dict[str, Any]:
    """
    Validate the entire repository's marker usage.
    
    Returns:
        Validation report with findings and recommendations
    """
    findings = []
    
    for component in inventory._all_components:
        is_valid, errors = validate_marker_usage(component)
        
        if not is_valid:
            findings.append({
                "component": f"{component.__module__}.{component.__name__}",
                "errors": errors,
                "severity": "error",
            })
    
    # Check for orphaned components (no primary marker)
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
        "valid_count": len(inventory._all_components) - len(findings),
        "invalid_count": len(findings),
        "orphans_count": len(orphans),
        "findings": findings,
        "recommendations": _generate_recommendations(findings, orphans),
    }


def _generate_recommendations(
    findings: list[dict], 
    orphans: list[type]
) -> list[str]:
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
    "MarkerInventory",
    "discover_components_in_module",
    "discover_components_in_package", 
    "validate_marker_usage",
    "validate_repository",
]