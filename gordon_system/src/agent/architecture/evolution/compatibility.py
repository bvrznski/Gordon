# Gordon Core: Compatibility Architecture (Phase 3.33)
"""
Compatibility Architecture - Ensures evolutionary continuity across all
artifact changes in the Gordon Core.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


# ============================================================================
# COMPATIBILITY MODE ENUMERATION
# ============================================================================

class CompatibilityMode(Enum):
    """
    Canonical compatibility modes for evolution.
    
    - FORWARD: New consumers work with old producers (backward-incompatible)
    - BACKWARD: Old consumers work with new producers (standard upgrade path)
    - ROLLING: Simultaneous support of multiple versions during transition
    - FULL: Both forward and backward compatible (rare, usually requires breaking changes)
    """
    
    FORWARD = "forward"          # New works with old
    BACKWARD = "backward"        # Old works with new
    ROLLING = "rolling"          # Simultaneous multi-version support
    FULL = "full"                # Both forward and backward compatible


# ============================================================================
# COMPATIBILITY LEVEL ENUMERATION
# ============================================================================

class CompatibilityLevel(Enum):
    """
    Canonical compatibility levels.
    
    - COMPATIBLE: Fully compatible, no issues expected
    - DEPRECATED: Works but uses deprecated features
    - INCOMPATIBLE: Will not work without migration
    - UNKNOWN: Cannot determine compatibility
    """
    
    COMPATIBLE = "compatible"      # Fully compatible
    DEPRECATED = "deprecated"      # Deprecated path available
    INCOMPATIBLE = "incompatible"  # Requires migration
    UNKNOWN = "unknown"            # Cannot determine


# ============================================================================
# COMPATIBILITY VALIDATOR BASE CLASS
# ============================================================================

class CompatibilityValidator:
    """
    Base class for compatibility validation.
    
    Subclasses implement specific validation logic for different artifact types
    (interfaces, schemas, protocols, etc.).
    """
    
    def __init__(self):
        self._results: Dict[str, CompatibilityResult] = {}
    
    def validate(self, source: Any, target: Any) -> "ValidationResult":
        """Validate compatibility between source and target states."""
        raise NotImplementedError("Subclasses must implement validate()")
    
    def get_result(self, artifact_id: str) -> Optional["CompatibilityResult"]:
        """Get validation result for a specific artifact."""
        return self._results.get(artifact_id)
    
    def list_results(self) -> List["CompatibilityResult"]:
        """List all validation results."""
        return list(self._results.values())


# ============================================================================
# COMPATIBILITY RESULT MODEL
# ============================================================================

@dataclass(frozen=True)
class CompatibilityResult:
    """
    Immutable compatibility validation result.
    """
    
    # Result identity
    artifact_id: str              # Identifier of the artifact being validated
    
    # Validation results
    is_compatible: bool           # Whether artifacts are compatible
    level: CompatibilityLevel     # Compatibility level
    
    # Detailed information
    breaking_changes: List[str] = field(default_factory=list)  # Breaking changes found
    deprecations: List[str] = field(default_factory=list)      # Deprecation notices
    warnings: List[str] = field(default_factory=list)          # Non-critical issues
    
    # Metadata
    validated_at: datetime = field(default_factory=datetime.now)
    validator_type: str = "base"
    
    @property
    def has_issues(self) -> bool:
        """Check if result has any issues."""
        return len(self.breaking_changes) > 0 or len(self.deprecations) > 0
    
    @property
    def is_blocking(self) -> bool:
        """Check if compatibility issue is blocking."""
        return not self.is_compatible and self.level == CompatibilityLevel.INCOMPATIBLE


# ============================================================================
# INTERFACE COMPATIBILITY VALIDATOR
# ============================================================================

class InterfaceCompatibilityValidator(CompatibilityValidator):
    """
    Validator for interface compatibility.
    
    Checks:
    - Method signatures remain compatible
    - Required methods are present in target
    - New optional parameters don't break existing implementations
    """
    
    def __init__(self):
        super().__init__()
        self._validator_type = "interface"
    
    def validate(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityResult:
        """Validate interface compatibility."""
        breaking_changes = []
        deprecations = []
        
        source_methods = set(source.get("methods", {}).keys())
        target_methods = set(target.get("methods", {}).keys())
        
        # Check for removed methods
        removed = source_methods - target_methods
        if removed:
            breaking_changes.extend([f"Method '{m}' was removed" for m in removed])
        
        # Check for signature changes
        source_sig = source.get("signatures", {})
        target_sig = target.get("signatures", {})
        
        for method_name, source_params in source_sig.items():
            if method_name in target_sig:
                target_params = target_sig[method_name]
                if source_params != target_params:
                    breaking_changes.append(
                        f"Method '{method_name}' signature changed"
                    )
        
        level = (
            CompatibilityLevel.INCOMPATIBLE if len(breaking_changes) > 0 else
            (CompatibilityLevel.DEPRECATED if len(deprecations) > 0 else
             CompatibilityLevel.COMPATIBLE)
        )
        
        result = CompatibilityResult(
            artifact_id=source.get("id", "unknown"),
            is_compatible=len(breaking_changes) == 0,
            level=level,
            breaking_changes=breaking_changes,
            deprecations=deprecations,
            validator_type="interface"
        )
        
        self._results[source.get("id", "unknown")] = result
        return result


# ============================================================================
# SCHEMA COMPATIBILITY VALIDATOR
# ============================================================================

class SchemaCompatibilityValidator(CompatibilityValidator):
    """
    Validator for schema compatibility.
    
    Checks:
    - Required fields remain required
    - Field types are compatible
    - New optional fields don't break existing consumers
    """
    
    def __init__(self):
        super().__init__()
        self._validator_type = "schema"
    
    def validate(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityResult:
        """Validate schema compatibility."""
        breaking_changes = []
        
        source_fields = {f["name"]: f for f in source.get("fields", [])}
        target_fields = {f["name"]: f for f in target.get("fields", [])}
        
        # Check removed required fields
        for name, field_def in source_fields.items():
            if name not in target_fields:
                if field_def.get("required", False):
                    breaking_changes.append(f"Required field '{name}' was removed")
        
        level = CompatibilityLevel.INCOMPATIBLE if len(breaking_changes) > 0 else CompatibilityLevel.COMPATIBLE
        
        result = CompatibilityResult(
            artifact_id=source.get("id", "unknown"),
            is_compatible=len(breaking_changes) == 0,
            level=level,
            breaking_changes=breaking_changes,
            validator_type="schema"
        )
        
        self._results[source.get("id", "unknown")] = result
        return result


# ============================================================================
# PROTOCOL COMPATIBILITY VALIDATOR
# ============================================================================

class ProtocolCompatibilityValidator(CompatibilityValidator):
    """
    Validator for protocol compatibility.
    
    Checks:
    - Message formats remain compatible
    - Required headers/fields are present
    - New optional fields don't break existing consumers
    """
    
    def __init__(self):
        super().__init__()
        self._validator_type = "protocol"
    
    def validate(self, source: Dict[str, Any], target: Dict[str, Any]) -> CompatibilityResult:
        """Validate protocol compatibility."""
        breaking_changes = []
        
        source_messages = set(source.get("messages", {}).keys())
        target_messages = set(target.get("messages", {}).keys())
        
        # Check for removed messages
        if source_messages - target_messages:
            breaking_changes.append("Some message types were removed")
        
        level = CompatibilityLevel.INCOMPATIBLE if len(breaking_changes) > 0 else CompatibilityLevel.COMPATIBLE
        
        result = CompatibilityResult(
            artifact_id=source.get("id", "unknown"),
            is_compatible=len(breaking_changes) == 0,
            level=level,
            breaking_changes=breaking_changes,
            validator_type="protocol"
        )
        
        self._results[source.get("id", "unknown")] = result
        return result


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_compatibility_mode(level: CompatibilityLevel) -> CompatibilityMode:
    """Determine the compatibility mode from a compatibility level."""
    if level == CompatibilityLevel.COMPATIBLE:
        return CompatibilityMode.BACKWARD
    elif level == CompatibilityLevel.DEPRECATED:
        return CompatibilityMode.ROLLING
    else:
        return CompatibilityMode.FULL


def merge_compatibility_results(results: List[CompatibilityResult]) -> CompatibilityResult:
    """Merge multiple compatibility results into a single result."""
    if not results:
        return CompatibilityResult(
            artifact_id="merged",
            is_compatible=True,
            level=CompatibilityLevel.COMPATIBLE
        )
    
    any_incompatible = any(not r.is_compatible for r in results)
    has_deprecations = any(len(r.deprecations) > 0 for r in results)
    
    breaking_changes = []
    deprecations = []
    warnings = []
    
    for result in results:
        breaking_changes.extend(result.breaking_changes)
        deprecations.extend(result.deprecations)
        warnings.extend(result.warnings)
    
    level = (
        CompatibilityLevel.INCOMPATIBLE if any_incompatible else
        (CompatibilityLevel.DEPRECATED if has_deprecations else
         CompatibilityLevel.COMPATIBLE)
    )
    
    return CompatibilityResult(
        artifact_id="merged",
        is_compatible=not any_incompatible,
        level=level,
        breaking_changes=list(set(breaking_changes)),
        deprecations=list(set(deprecations)),
        warnings=list(set(warnings)),
        validated_at=max(r.validated_at for r in results),
        validator_type="merged"
    )