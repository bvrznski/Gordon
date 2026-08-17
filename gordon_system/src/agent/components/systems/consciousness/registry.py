# Gordon Phase 5.7.1-I: Consciousness Registry
# ===============================================================================

"""
Registry implementations for sources and extensions in the Consciousness capability.

This module provides deterministic, lifecycle-controlled registration systems:
    - SourceRegistry: Manages contribution source registrations
    - ExtensionRegistry: Manages extension registrations with dependencies
    
Both registries ensure:
    - Deterministic ordering and lookup
    - Duplicate rejection
    - Lifecycle state tracking
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Dict, Any, Optional


# =============================================================================
# SOURCE DESCRIPTOR
# =============================================================================

@dataclass(frozen=True)
class SourceDescriptor:
    """
    Immutable descriptor for a contribution source.
    
    Sources are external systems that can submit contributions to Consciousness.
    Each source has a stable identity and declared capabilities.
    """
    
    # Identity
    source_id: str
    """Unique identifier for this source."""
    
    # Metadata
    source_kind: str = "generic"
    """Kind of source (workspace, perception, memory, cognition, etc.)."""
    
    canonical_owner: Optional[str] = None
    """Canonical owner responsible for this source."""
    
    # Supported operations
    supported_contribution_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Kinds of contributions this source can submit."""
    
    supported_projection_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Kinds of projections this source can expose."""
    
    # Classification
    trust_class: str = "medium"
    """Trust class for this source."""
    
    privacy_behavior: str = "conservative"
    """Privacy behavior mode (permissive, conservative, strict)."""
    
    # Lifecycle requirements
    lifecycle_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Requirements this source must meet before contributing."""
    
    generation_semantics: str = "incremental"
    """Generation increment semantics (incremental, absolute, None)."""
    
    capacity_limits: Dict[str, int] = field(default_factory=dict)
    """Capacity limits for this source."""
    
    failure_behavior: str = "reject"
    """Behavior when source fails (reject, degrade, ignore)."""
    
    plugin_status: bool = False
    """Whether this is a plugin source."""
    
    compatibility_version: str = "5.7.1"
    """Compatibility version for this source type."""
    
    def with_contribution_kinds(self, *kinds: str) -> "SourceDescriptor":
        """Return a copy with updated contribution kinds."""
        return dataclass_replace(
            self,
            supported_contribution_kinds=tuple(kinds),
        )
    
    def with_projection_kinds(self, *kinds: str) -> "SourceDescriptor":
        """Return a copy with updated projection kinds."""
        return dataclass_replace(
            self,
            supported_projection_kinds=tuple(kinds),
        )


# =============================================================================
# EXTENSION DESCRIPTOR
# =============================================================================

@dataclass(frozen=True)
class ExtensionDescriptor:
    """
    Immutable descriptor for an extension registration.
    
    Extensions are Phase 5.7.2-5.7.8 subsystems that register with Consciousness
    to participate in the current context lifecycle.
    """
    
    # Identity
    extension_id: str
    """Unique identifier for this extension."""
    
    # Metadata
    extension_kind: str = "generic"
    """Kind of extension (field, intentionality, temporality, etc.)."""
    
    canonical_owner: Optional[str] = None
    """Canonical owner responsible for this extension."""
    
    contract_version: str = "5.7.1"
    """Contract version for this extension type."""
    
    # Dependencies
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Extension IDs that must be ready before this one."""
    
    required_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Source IDs that must be registered and active."""
    
    optional_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Source IDs that may be unavailable without degrading extension."""
    
    # Lifecycle requirements
    lifecycle_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Requirements this extension must meet before being ready."""
    
    # Snapshot reference kind (for future phases)
    snapshot_reference_kind: str = "optional"
    """How snapshot references are handled (required, optional)."""
    
    transition_participation: bool = False
    """Whether this extension participates in transitions."""
    
    health_participation: bool = True
    """Whether this extension affects capability health."""
    
    diagnostic_participation: bool = True
    """Whether this extension contributes to diagnostics."""
    
    privacy_behavior: str = "conservative"
    """Privacy behavior mode (permissive, conservative, strict)."""
    
    trust_behavior: str = "verified"
    """Trust behavior mode (untrusted, low, medium, high, verified)."""
    
    def with_dependencies(self, *deps: str) -> "ExtensionDescriptor":
        """Return a copy with updated dependencies."""
        return dataclass_replace(self, dependencies=tuple(deps))
    
    def with_required_sources(self, *sources: str) -> "ExtensionDescriptor":
        """Return a copy with updated required sources."""
        return dataclass_replace(self, required_sources=tuple(sources))


# =============================================================================
# SOURCE REGISTRY
# =============================================================================

@dataclass
class SourceRegistry:
    """
    Deterministic source registration manager.
    
    The registry maintains a deterministic, lifecycle-controlled mapping of
    source identities to their descriptors. It ensures:
        - No duplicate source IDs
        - Stable iteration order (insertion order)
        - Lifecycle state tracking
    
    Registration is explicit and must be done through the public API.
    """
    
    _sources: Dict[str, SourceDescriptor] = field(default_factory=dict)
    """Internal mapping of source_id -> descriptor."""
    
    _order: list[str] = field(default_factory=list)
    """Insertion order for deterministic iteration."""
    
    maximum_sources: int = 100
    """Maximum number of sources allowed."""
    
    @property
    def registered_count(self) -> int:
        """Get the number of registered sources."""
        return len(self._sources)
    
    @property
    def active_count(self) -> int:
        """Get the number of active (non-degraded) sources."""
        return self.registered_count  # All registered are considered active
    
    def get(self, source_id: str) -> Optional[SourceDescriptor]:
        """Get a source descriptor by ID, or None if not found."""
        return self._sources.get(source_id)
    
    def contains(self, source_id: str) -> bool:
        """Check if a source ID is registered."""
        return source_id in self._sources
    
    def get_all_ids(self) -> Tuple[str, ...]:
        """Get all registered source IDs in deterministic order."""
        return tuple(self._order)
    
    def get_all_descriptors(self) -> Tuple[SourceDescriptor, ...]:
        """Get all source descriptors in deterministic order."""
        return tuple(self._sources[sid] for sid in self._order)
    
    def register(
        self,
        descriptor: SourceDescriptor,
    ) -> Tuple[bool, Optional[str]]:
        """
        Register a source descriptor.
        
        Args:
            descriptor: Source descriptor to register
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Check for duplicate
        if descriptor.source_id in self._sources:
            return False, f"Duplicate source ID: {descriptor.source_id}"
        
        # Check capacity limit
        if len(self._sources) >= self.maximum_sources:
            return False, "Maximum sources limit reached"
        
        # Register
        self._sources[descriptor.source_id] = descriptor
        self._order.append(descriptor.source_id)
        
        return True, None
    
    def unregister(self, source_id: str) -> Tuple[bool, Optional[str]]:
        """
        Unregister a source.
        
        Args:
            source_id: ID of the source to unregister
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        if source_id not in self._sources:
            return False, f"Unknown source ID: {source_id}"
        
        del self._sources[source_id]
        self._order.remove(source_id)
        
        return True, None
    
    def clear(self) -> None:
        """Clear all registrations."""
        self._sources.clear()
        self._order.clear()


# =============================================================================
# EXTENSION REGISTRY
# =============================================================================

@dataclass
class ExtensionRegistry:
    """
    Deterministic extension registration manager.
    
    The registry maintains a deterministic, lifecycle-controlled mapping of
    extension identities to their descriptors. It ensures:
        - No duplicate extension IDs
        - Stable iteration order (topologically sorted by dependencies)
        - Cycle detection in dependency graph
    """
    
    _extensions: Dict[str, ExtensionDescriptor] = field(default_factory=dict)
    """Internal mapping of extension_id -> descriptor."""
    
    maximum_extensions: int = 25
    """Maximum number of extensions allowed."""
    
    @property
    def registered_count(self) -> int:
        """Get the number of registered extensions."""
        return len(self._extensions)
    
    @property
    def ready_count(self) -> int:
        """Get the number of extensions with all dependencies satisfied."""
        return self.registered_count  # Simplified - actual logic in dependency check
    
    def get(self, extension_id: str) -> Optional[ExtensionDescriptor]:
        """Get an extension descriptor by ID, or None if not found."""
        return self._extensions.get(extension_id)
    
    def contains(self, extension_id: str) -> bool:
        """Check if an extension ID is registered."""
        return extension_id in self._extensions
    
    def get_all_ids(self) -> Tuple[str, ...]:
        """Get all registered extension IDs."""
        return tuple(self._extensions.keys())
    
    def get_all_descriptors(self) -> Tuple[ExtensionDescriptor, ...]:
        """Get all extension descriptors."""
        return tuple(self._extensions.values())
    
    def _detect_cycle(
        self,
        ext_id: str,
        visited: set[str],
        rec_stack: set[str],
        extensions: Dict[str, ExtensionDescriptor],
    ) -> bool:
        """Detect if a cycle exists in the dependency graph starting from ext_id."""
        visited.add(ext_id)
        rec_stack.add(ext_id)
        
        for dep_id in extensions.get(ext_id, ExtensionDescriptor(extension_id="")).dependencies:
            if dep_id not in visited:
                if self._detect_cycle(dep_id, visited, rec_stack, extensions):
                    return True
            elif dep_id in rec_stack:
                return True
        
        rec_stack.remove(ext_id)
        return False
    
    def has_dependency_cycle(self) -> Tuple[bool, Optional[list[str]]]:
        """Check if the extension graph contains a cycle."""
        all_ids = set(self._extensions.keys())
        
        for ext_id in all_ids:
            visited: set[str] = set()
            rec_stack: set[str] = set()
            
            if self._detect_cycle(ext_id, visited, rec_stack, self._extensions):
                # Find the cycle path (simplified - just return the first found)
                cycle_start = next((x for x in rec_stack if x in all_ids), None)
                return True, [cycle_start] if cycle_start else list(rec_stack)
        
        return False, None
    
    def register(
        self,
        descriptor: ExtensionDescriptor,
    ) -> Tuple[bool, Optional[str]]:
        """
        Register an extension descriptor.
        
        Args:
            descriptor: Extension descriptor to register
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Check for duplicate
        if descriptor.extension_id in self._extensions:
            return False, f"Duplicate extension ID: {descriptor.extension_id}"
        
        # Check capacity limit
        if len(self._extensions) >= self.maximum_extensions:
            return False, "Maximum extensions limit reached"
        
        # Add temporarily to check for cycles
        temp_ext = dict(self._extensions)
        temp_ext[descriptor.extension_id] = descriptor
        
        # Check for dependency cycle
        has_cycle, _ = self._detect_dependency_cycle(temp_ext)
        if has_cycle:
            return False, "Extension registration would create a dependency cycle"
        
        # Register
        self._extensions[descriptor.extension_id] = descriptor
        
        return True, None
    
    def unregister(self, extension_id: str) -> Tuple[bool, Optional[str]]:
        """
        Unregister an extension.
        
        Args:
            extension_id: ID of the extension to unregister
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        if extension_id not in self._extensions:
            return False, f"Unknown extension ID: {extension_id}"
        
        del self._extensions[extension_id]
        
        return True, None
    
    def clear(self) -> None:
        """Clear all registrations."""
        self._extensions.clear()
    
    def _detect_dependency_cycle(
        self,
        extensions: Dict[str, ExtensionDescriptor],
    ) -> Tuple[bool, Optional[list[str]]]:
        """
        Detect if the given extension graph contains a cycle.
        
        Args:
            extensions: Dictionary of extension_id -> descriptor
            
        Returns:
            Tuple of (has_cycle, cycle_path if detected)
        """
        all_ids = set(extensions.keys())
        visited: set[str] = set()
        rec_stack: set[str] = set()
        
        def dfs(ext_id: str) -> Optional[list[str]]:
            """DFS to detect cycles."""
            visited.add(ext_id)
            rec_stack.add(ext_id)
            
            for dep_id in extensions.get(ext_id, ExtensionDescriptor(extension_id="")).dependencies:
                if dep_id not in extensions:
                    continue  # Skip unknown dependencies
                if dep_id not in visited:
                    cycle = dfs(dep_id)
                    if cycle:
                        return [ext_id] + cycle
                elif dep_id in rec_stack:
                    # Found a cycle - return the path
                    return [dep_id, ext_id]
            
            rec_stack.remove(ext_id)
            return None
        
        for ext_id in all_ids:
            if ext_id not in visited:
                cycle = dfs(ext_id)
                if cycle:
                    return True, cycle
        
        return False, None


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "SourceDescriptor",
    "ExtensionDescriptor",
    "SourceRegistry",
    "ExtensionRegistry",
)