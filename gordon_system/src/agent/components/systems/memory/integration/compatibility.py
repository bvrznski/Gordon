# Compatibility Manager - Phase 5.1.7 Version Compatibility System
# ================================================================

"""
Memory Integration Compatibility: Manages version compatibility between consumers and Memory.

Compatibility ensures that:
    - Consumer and Memory understand each other's contracts
    - Breaking changes are detected before they cause errors
    - Graceful degradation is possible when versions diverge
    - Migration paths are explicit and documented

Compatibility Laws:
    COMPATIBILITY-LAW-001: Compatibility must be explicitly declared
    COMPATIBILITY-LAW-002: Backward compatibility must be versioned
    COMPATIBILITY-LAW-003: Breaking changes require new contract revisions
    COMPATIBILITY-LAW-004: Compatibility evaluation precedes communication
    COMPATIBILITY-LAW-005: Compatibility failures are observable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# COMPATIBILITY STATES - What does compatibility mean?
# =============================================================================


class CompatibilityState(Enum):
    """
    States of compatibility between consumer and Memory.
    
    | State        | Description                                       |
    |--------------|---------------------------------------------------|
    | COMPATIBLE   | Full compatibility, all features work             |
    | DEPRECATED   | Works but some features deprecated                |
    | PARTIAL      | Partial compatibility, limited functionality      |
    | INCOMPATIBLE | Cannot communicate                                |
    """
    
    COMPATIBLE = "compatible"
    DEPRECATED = "deprecated"
    PARTIAL = "partial"
    INCOMPATIBLE = "incompatible"


# =============================================================================
# VERSION CONSTRAINTS
# =============================================================================


@dataclass(frozen=True)
class VersionConstraint:
    """
    Constraint on acceptable versions.
    
    Fields:
        min_version:     Minimum acceptable version (inclusive)
        max_version:     Maximum acceptable version (inclusive)
        exact_version:   If set, only this specific version is accepted
        
        # Validation
        allow_prerelease: Are prereleases allowed?
        allow_dev:       Are dev versions allowed?
    """
    
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    exact_version: Optional[str] = None
    
    allow_prerelease: bool = False
    allow_dev: bool = False


# =============================================================================
# COMPATIBILITY RESULT
# =============================================================================


@dataclass(frozen=True)
class CompatibilityResult:
    """
    Result of a compatibility check.
    
    Fields:
        is_compatible:   Does the consumer meet compatibility requirements?
        state:           What is the compatibility state?
        
        # Version info
        consumer_version: Version of the consumer
        memory_version:  Version expected by Memory
        
        # Details
        message:         Human-readable explanation
        missing_features: Which features are not available?
        deprecated_features: Which features will be removed soon?
    """
    
    is_compatible: bool = True
    state: CompatibilityState = CompatibilityState.COMPATIBLE
    
    consumer_version: str = "unknown"
    memory_version: str = "1.0.0"
    
    message: str = ""
    missing_features: Tuple[str, ...] = field(default_factory=tuple)
    deprecated_features: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# COMPATIBILITY DEFINITION
# =============================================================================


@dataclass(frozen=True)
class CompatibilityDefinition:
    """
    Definition of compatibility requirements for an integration.
    
    Fields:
        integration_type: Which integration is this?
        
        # Version requirements
        min_version:     Minimum required version (major.minor.patch)
        max_version:     Maximum supported version
        
        # Feature requirements
        required_features: Features that must be present
        optional_features: Features that may be missing
        
        # Behavior requirements
        semantic_compatibility: Must preserve semantics?
        deterministic:       Must be deterministic?
    """
    
    integration_type: str                   # e.g., "perception", "workspace"
    
    min_version: str = "1.0.0"
    max_version: str = "999.999.999"
    
    required_features: Tuple[str, ...] = field(default_factory=tuple)
    optional_features: Tuple[str, ...] = field(default_factory=tuple)
    
    semantic_compatibility: bool = True
    deterministic: bool = True


# =============================================================================
# COMPATIBILITY MANAGER
# =============================================================================


class CompatibilityManager:
    """
    Manager for integration compatibility.
    
    Provides version validation, constraint checking,
    and compatibility evaluation between consumers and Memory.
    
    Usage:
        manager = CompatibilityManager()
        result = manager.check_compatibility(
            "perception", 
            consumer_version="1.2.3"
        )
    """
    
    def __init__(self):
        self._definitions: Dict[str, CompatibilityDefinition] = {}
        self._compatibility_cache: Dict[Tuple[str, str], CompatibilityResult] = {}
    
    def register_definition(self, definition: CompatibilityDefinition) -> None:
        """Register a compatibility definition for an integration type."""
        self._definitions[definition.integration_type] = definition
        # Invalidate cache
        self._compatibility_cache.clear()
    
    def check_compatibility(
        self,
        integration_type: str,
        consumer_version: str,
        memory_version: Optional[str] = None
    ) -> CompatibilityResult:
        """
        Check if a consumer is compatible with Memory.
        
        Args:
            integration_type: Which integration to check?
            consumer_version: Version of the consumer
            memory_version:   Version expected by Memory (default: 1.0.0)
            
        Returns:
            CompatibilityResult describing the compatibility state.
        """
        # Check cache first
        cache_key = (integration_type, consumer_version)
        if cache_key in self._compatibility_cache:
            return self._compatibility_cache[cache_key]
        
        # Get definition
        definition = self._definitions.get(integration_type)
        if not definition:
            result = CompatibilityResult(
                is_compatible=False,
                state=CompatibilityState.INCOMPATIBLE,
                consumer_version=consumer_version,
                memory_version=memory_version or "unknown",
                message=f"No compatibility definition for integration: {integration_type}"
            )
            self._compatibility_cache[cache_key] = result
            return result
        
        # Parse versions
        try:
            consumer_parts = self._parse_version(consumer_version)
            min_parts = self._parse_version(definition.min_version)
            max_parts = self._parse_version(definition.max_version)
            
            if memory_version:
                memory_parts = self._parse_version(memory_version)
            else:
                memory_parts = (1, 0, 0)
        except ValueError as e:
            result = CompatibilityResult(
                is_compatible=False,
                state=CompatibilityState.INCOMPATIBLE,
                consumer_version=consumer_version,
                memory_version=memory_version or "unknown",
                message=f"Invalid version string: {str(e)}"
            )
            self._compatibility_cache[cache_key] = result
            return result
        
        # Check range
        is_in_range = (min_parts <= consumer_parts <= max_parts)
        
        if not is_in_range:
            result = CompatibilityResult(
                is_compatible=False,
                state=CompatibilityState.INCOMPATIBLE,
                consumer_version=consumer_version,
                memory_version=f"{memory_parts[0]}.{memory_parts[1]}.{memory_parts[2]}",
                message=f"Consumer version {consumer_version} not in range [{definition.min_version}, {definition.max_version}]"
            )
            self._compatibility_cache[cache_key] = result
            return result
        
        # Check features
        missing_features = []
        for feature in definition.required_features:
            if not self._has_feature(consumer_version, feature):
                missing_features.append(feature)
        
        deprecated_features = []
        
        if missing_features:
            result = CompatibilityResult(
                is_compatible=False,
                state=CompatibilityState.PARTIAL,
                consumer_version=consumer_version,
                memory_version=f"{memory_parts[0]}.{memory_parts[1]}.{memory_parts[2]}",
                message=f"Missing required features: {', '.join(missing_features)}",
                missing_features=tuple(missing_features)
            )
        else:
            result = CompatibilityResult(
                is_compatible=True,
                state=CompatibilityState.COMPATIBLE,
                consumer_version=consumer_version,
                memory_version=f"{memory_parts[0]}.{memory_parts[1]}.{memory_parts[2]}",
                message="Consumer is fully compatible"
            )
        
        self._compatibility_cache[cache_key] = result
        return result
    
    def _parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse a version string into parts."""
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version}")
        
        try:
            return tuple(int(p) for p in parts[:3])
        except ValueError as e:
            raise ValueError(f"Version must be numeric: {version}") from e
    
    def _has_feature(self, version: str, feature: str) -> bool:
        """Check if a version has a specific feature."""
        # Default implementation assumes all features are available
        return True
    
    def get_definition(self, integration_type: str) -> Optional[CompatibilityDefinition]:
        """Get the compatibility definition for an integration type."""
        return self._definitions.get(integration_type)
    
    def list_definitions(self) -> Dict[str, CompatibilityDefinition]:
        """List all registered compatibility definitions."""
        return dict(self._definitions)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def parse_version(version: str) -> Tuple[int, int, int]:
    """
    Parse a version string into components.
    
    Args:
        version: Version string in format "major.minor.patch"
        
    Returns:
        Tuple of (major, minor, patch) integers
        
    Raises:
        ValueError: If version format is invalid
    """
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    
    try:
        return tuple(int(p) for p in parts[:3])
    except ValueError as e:
        raise ValueError(f"Version must be numeric: {version}") from e


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings.
    
    Args:
        v1: First version string
        v2: Second version string
        
    Returns:
        -1 if v1 < v2
         0 if v1 == v2
         1 if v1 > v2
    """
    parts1 = parse_version(v1)
    parts2 = parse_version(v2)
    
    for p1, p2 in zip(parts1, parts2):
        if p1 < p2:
            return -1
        elif p1 > p2:
            return 1
    
    return 0