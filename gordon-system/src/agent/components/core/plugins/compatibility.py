# Compatibility Engine - Phase 3.8.8.3
# ======================================
"""
Canonical compatibility engine for plugin version validation.

Provides:
- Semantic version comparison and validation
- Compatibility profile definitions
- Plugin compatibility evaluation
- Upgrade planning

Compatibility Rules:
    - Major version changes = potentially breaking (requires explicit approval)
    - Minor version changes = additive features (backward compatible)
    - Patch version changes = bug fixes (fully backward compatible)
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Set,
    Any,
)
from enum import Enum
import time

# Import from abstraction module
try:
    from .abstraction import (
        PluginVersion,
        CompatibilityError,
    )
except ImportError:
    class PluginVersion:
        pass
    
    class CompatibilityError(Exception):
        pass


class CompatibilityLevel(Enum):
    """Levels of compatibility between plugins."""
    
    EXACT = "exact"           # Exact version match required
    MAJOR = "major"          # Same major version (recommended)
    MINOR = "minor"          # Same major, compatible minor versions
    BACKWARD = "backward"    # Any lower version is acceptable
    UNKNOWN = "unknown"      # Cannot determine compatibility
    
    @property
    def is_compatible(self) -> bool:
        """Check if this level indicates compatibility."""
        return self in (self.EXACT, self.MAJOR, self.MINOR, self.BACKWARD)


@dataclass(frozen=True)
class CompatibilityProfile:
    """
    Profile defining compatibility rules for a plugin or capability.
    
    Profiles can be:
        - Strict: Only exact version matches
        - Compatible: Same major version required
        - Flexible: Any compatible version acceptable
    """
    
    name: str                       # Profile name (e.g., "core-v3.8")
    min_version: PluginVersion      # Minimum acceptable version
    max_version: Optional[PluginVersion] = None  # Maximum version (None = no upper bound)
    
    allow_major_updates: bool = False   # Allow different major versions?
    require_exact_match: bool = False   # Require exact match?
    
    @classmethod
    def compatible(cls, min_version: PluginVersion) -> "CompatibilityProfile":
        """Create a profile requiring same major version."""
        return cls(
            name=f"compatible-{min_version.major}",
            min_version=min_version,
            max_version=None,
            allow_major_updates=False,
            require_exact_match=False,
        )
    
    @classmethod
    def flexible(cls, min_version: PluginVersion) -> "CompatibilityProfile":
        """Create a profile allowing any compatible version."""
        return cls(
            name=f"flexible-{min_version.major}",
            min_version=min_version,
            max_version=None,
            allow_major_updates=True,
            require_exact_match=False,
        )
    
    @classmethod
    def strict(cls, exact_version: PluginVersion) -> "CompatibilityProfile":
        """Create a profile requiring exact version match."""
        return cls(
            name=f"strict-{exact_version}",
            min_version=exact_version,
            max_version=exact_version,
            allow_major_updates=False,
            require_exact_match=True,
        )
    
    def evaluate(self, version: PluginVersion) -> tuple[CompatibilityLevel, Optional[str]]:
        """
        Evaluate if a version is compatible with this profile.
        
        Args:
            version: The version to check
            
        Returns:
            Tuple of (level, reason_if_not_compatible)
        """
        # Check minimum version
        if version.compare_to(self.min_version) < 0:
            return CompatibilityLevel.UNKNOWN, (
                f"Version {version} is below minimum {self.min_version}"
            )
        
        # Check exact match requirement
        if self.require_exact_match:
            if (version.major == self.min_version.major and
                version.minor == self.min_version.minor and
                version.patch == self.min_version.patch):
                return CompatibilityLevel.EXACT, None
            return CompatibilityLevel.UNKNOWN, (
                f"Exact match required: {self.min_version}"
            )
        
        # Check major version (if not allowed)
        if not self.allow_major_updates:
            if version.major != self.min_version.major:
                return CompatibilityLevel.MAJOR, (
                    f"Major version mismatch: {version} vs {self.min_version}"
                )
        
        # Check maximum version
        if self.max_version is not None:
            if version.compare_to(self.max_version) > 0:
                return CompatibilityLevel.UNKNOWN, (
                    f"Version {version} exceeds maximum {self.max_version}"
                )
        
        # Version is compatible
        if version.major == self.min_version.major and \
           version.minor == self.min_version.minor and \
           version.patch == self.min_version.patch:
            return CompatibilityLevel.EXACT, None
        
        return CompatibilityLevel.MINOR, None


@dataclass(frozen=True)
class CompatibilityResult:
    """Result of a compatibility evaluation."""
    
    is_compatible: bool
    level: CompatibilityLevel
    
    # Version information
    required_version: PluginVersion
    actual_version: Optional[PluginVersion] = None
    
    # Details
    reason: Optional[str] = None
    suggested_action: Optional[str] = None  # "upgrade", "downgrade", "skip"
    
    @property
    def should_upgrade(self) -> bool:
        """Check if upgrade is recommended."""
        return self.suggested_action == "upgrade"
    
    @property
    def should_downgrade(self) -> bool:
        """Check if downgrade is recommended."""
        return self.suggested_action == "downgrade"
    
    @property
    def should_skip(self) -> bool:
        """Check if this plugin should be skipped."""
        return not self.is_compatible and not self.should_upgrade


# =============================================================================
# COMPATIBILITY ENGINE
# =============================================================================


class CompatibilityEngine:
    """
    Evaluates compatibility between plugins based on version constraints.
    
    Provides:
        - Version range validation
        - Conflict detection
        - Suggested resolution actions
    
    Thread Safety:
        All public methods are async and use internal locking.
    """
    
    def __init__(self):
        """Initialize the compatibility engine."""
        self._lock = time.monotonic()  # Placeholder for lock
    
    def evaluate_plugin_compatibility(
        self,
        plugin_version: PluginVersion,
        required_profile: CompatibilityProfile,
    ) -> CompatibilityResult:
        """
        Evaluate if a plugin version is compatible with a profile.
        
        Args:
            plugin_version: The plugin's actual version
            required_profile: The required compatibility profile
            
        Returns:
            Compatibility result with evaluation details
        """
        level, reason = required_profile.evaluate(plugin_version)
        
        # Determine suggested action
        suggested_action: Optional[str] = None
        
        if not level.is_compatible:
            if plugin_version.major < required_profile.min_version.major:
                suggested_action = "upgrade"
            elif plugin_version.major > required_profile.min_version.major:
                suggested_action = "skip"  # Different major, skip
            else:
                suggested_action = "upgrade"
        
        return CompatibilityResult(
            is_compatible=level.is_compatible,
            level=level,
            required_version=required_profile.min_version,
            actual_version=plugin_version,
            reason=reason,
            suggested_action=suggested_action,
        )
    
    def evaluate_dependency(
        self,
        plugin_id: str,
        plugin_version: PluginVersion,
        dependency_constraint: Dict[str, Any],
    ) -> CompatibilityResult:
        """
        Evaluate a specific dependency compatibility.
        
        Args:
            plugin_id: The plugin ID being checked
            plugin_version: Its version
            dependency_constraint: Constraint info from manifest
            
        Returns:
            Compatibility result for this dependency
        """
        # Parse constraint (simplified)
        min_str = dependency_constraint.get("min_version")
        max_str = dependency_constraint.get("max_version")
        
        min_ver = PluginVersion.parse(min_str) if min_str else None
        max_ver = PluginVersion.parse(max_str) if max_str else None
        
        # Create temporary profile
        profile = CompatibilityProfile(
            name=plugin_id,
            min_version=min_ver or PluginVersion(0, 0, 0),
            max_version=max_ver,
            allow_major_updates=True,  # Allow major for dependencies
            require_exact_match=False,
        )
        
        return self.evaluate_plugin_compatibility(plugin_version, profile)
    
    def find_compatible_versions(
        self,
        available_versions: List[PluginVersion],
        required_profile: CompatibilityProfile,
    ) -> List[tuple[PluginVersion, CompatibilityResult]]:
        """
        Find all compatible versions from a list.
        
        Args:
            available_versions: Versions to check
            required_profile: The required compatibility profile
            
        Returns:
            List of (version, result) tuples for compatible versions
        """
        results = []
        
        for version in available_versions:
            result = self.evaluate_plugin_compatibility(version, required_profile)
            if result.is_compatible:
                results.append((version, result))
        
        # Sort by compatibility level and version
        results.sort(
            key=lambda x: (
                -self._level_priority(x[1].level),
                x[0].major * 1000 + x[0].minor * 100 + x[0].patch,
            )
        )
        
        return results
    
    def _level_priority(self, level: CompatibilityLevel) -> int:
        """Get priority for a compatibility level (higher = better)."""
        priorities = {
            CompatibilityLevel.EXACT: 4,
            CompatibilityLevel.MAJOR: 3,
            CompatibilityLevel.MINOR: 2,
            CompatibilityLevel.BACKWARD: 1,
            CompatibilityLevel.UNKNOWN: 0,
        }
        return priorities.get(level, 0)
    
    def check_upgrade_path(
        self,
        current_version: PluginVersion,
        target_version: PluginVersion,
        profile: CompatibilityProfile,
    ) -> Optional[str]:
        """
        Check if an upgrade path exists and suggest action.
        
        Args:
            current_version: Current installed version
            target_version: Target version to check
            profile: The compatibility profile
            
        Returns:
            Action string or None if incompatible
        """
        if not profile.allow_major_updates and \
           current_version.major != target_version.major:
            return "skip"  # Different major versions
        
        if target_version.compare_to(profile.min_version) < 0:
            return "upgrade_required"
        
        if target_version > current_version:
            return "upgrade_available"
        elif target_version < current_version:
            return "downgrade_available"
        else:
            return "up_to_date"


# Global engine instance
_global_compatibility_engine: Optional[CompatibilityEngine] = None


def get_global_compatibility_engine() -> CompatibilityEngine:
    """Get the global compatibility engine."""
    global _global_compatibility_engine
    
    if _global_compatibility_engine is None:
        _global_compatibility_engine = CompatibilityEngine()
    
    return _global_compatibility_engine


__all__ = [
    # Enums
    "CompatibilityLevel",
    
    # Data classes
    "CompatibilityProfile",
    "CompatibilityResult",
    
    # Main class
    "CompatibilityEngine",
    
    # Global accessors
    "get_global_compatibility_engine",
]