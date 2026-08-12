# Configuration Validation Module
# ===============================
"""
Configuration value validation stages.

Provides:
- Type validation
- Semantic validation
- Cross-field validation
- Cross-domain validation

Phase 3.7.14: Configuration, Policy, Feature Flags & Runtime Reconfiguration
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    Tuple,
)
import time


# =============================================================================
# Validation Results
# =============================================================================

@dataclass(frozen=True)
class ValidationResult:
    """Result of a validation stage."""
    stage: str  # e.g., "type", "semantic", "cross-field"
    success: bool
    errors: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ValidationReport:
    """
    Complete validation report.
    
    Contains results from all validation stages.
    """
    schema_id: str
    configuration_version: int
    overall_valid: bool
    type_validation: ValidationResult
    semantic_validation: ValidationResult
    cross_field_validation: Optional[ValidationResult] = None
    cross_domain_validation: Optional[ValidationResult] = None
    validated_at: float = field(default_factory=time.monotonic)
    
    @property
    def error_count(self) -> int:
        total = len(self.type_validation.errors)
        if self.semantic_validation:
            total += len(self.semantic_validation.errors)
        if self.cross_field_validation:
            total += len(self.cross_field_validation.errors)
        if self.cross_domain_validation:
            total += len(self.cross_domain_validation.errors)
        return total


# =============================================================================
# Validation Stages
# =============================================================================

class TypeValidator:
    """Type validation stage."""
    
    def validate(
        self,
        data: Dict[str, Any],
        schema_fields: Dict[str, type]
    ) -> ValidationResult:
        """
        Validate that values match their expected types.
        
        Args:
            data: Configuration data to validate
            schema_fields: Mapping of field name to expected type
            
        Returns:
            ValidationResult with any type errors
        """
        errors = []
        
        for path, expected_type in schema_fields.items():
            value = self._get_value(data, path)
            
            if value is None:
                continue  # Optional fields can be None
            
            if not isinstance(value, expected_type):
                errors.append(
                    f"Type error at {path}: expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
        
        return ValidationResult(
            stage="type",
            success=len(errors) == 0,
            errors=tuple(errors)
        )
    
    def _get_value(self, data: Dict[str, Any], path: str) -> Optional[Any]:
        """Get a value from nested dict using dot-notation path."""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value


class SemanticValidator:
    """
    Semantic validation stage.
    
    Validates domain-specific constraints and business rules.
    """
    
    def __init__(self, validators: Optional[Dict[str, Any]] = None):
        """
        Initialize with custom semantic validators.
        
        Args:
            validators: Mapping of field path to validator function
                       Validator function takes (value) -> bool
        """
        self._validators = validators or {}
    
    def validate(
        self,
        data: Dict[str, Any],
        domain_rules: Optional[Dict[str, str]] = None
    ) -> ValidationResult:
        """
        Validate semantic constraints.
        
        Args:
            data: Configuration data to validate
            domain_rules: Optional domain-specific rules
            
        Returns:
            ValidationResult with any semantic errors
        """
        errors = []
        
        # Apply custom validators
        for path, validator_fn in self._validators.items():
            value = self._get_value(data, path)
            
            if value is None:
                continue  # Optional fields can be None
            
            if not validator_fn(value):
                errors.append(
                    f"Semantic validation failed at {path}: "
                    f"value {value!r} does not satisfy constraint"
                )
        
        return ValidationResult(
            stage="semantic",
            success=len(errors) == 0,
            errors=tuple(errors)
        )
    
    def _get_value(self, data: Dict[str, Any], path: str) -> Optional[Any]:
        """Get a value from nested dict using dot-notation path."""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value


class CrossFieldValidator:
    """
    Cross-field validation stage.
    
    Validates relationships between fields (e.g., minimum <= maximum).
    """
    
    def __init__(self, cross_field_rules: Optional[Dict[str, Any]] = None):
        """
        Initialize with cross-field rules.
        
        Args:
            cross_field_rules: Rules like:
                {
                    "min_max": {"fields": ["min", "max"], "rule": "min <= max"}
                }
        """
        self._rules = cross_field_rules or {}
    
    def validate(
        self,
        data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate cross-field relationships.
        
        Args:
            data: Configuration data to validate
            
        Returns:
            ValidationResult with any cross-field errors
        """
        errors = []
        
        # Example rules - can be extended based on domain needs
        for rule_name, rule_config in self._rules.items():
            if not self._evaluate_rule(rule_name, rule_config, data):
                errors.append(
                    f"Cross-field validation failed: {rule_name}"
                )
        
        return ValidationResult(
            stage="cross-field",
            success=len(errors) == 0,
            errors=tuple(errors)
        )
    
    def _evaluate_rule(
        self,
        rule_name: str,
        rule_config: Dict[str, Any],
        data: Dict[str, Any]
    ) -> bool:
        """Evaluate a cross-field rule."""
        if rule_name == "min_max":
            min_val = data.get("min")
            max_val = data.get("max")
            
            if min_val is not None and max_val is not None:
                return min_val <= max_val
        
        # Default: pass
        return True


class CrossDomainValidator:
    """
    Cross-domain validation stage.
    
    Validates relationships between different configuration domains.
    """
    
    def __init__(self, domain_rules: Optional[Dict[str, Any]] = None):
        """
        Initialize with cross-domain rules.
        
        Args:
            domain_rules: Rules for cross-domain validation
        """
        self._rules = domain_rules or {}
    
    def validate(
        self,
        data_by_domain: Dict[str, Dict[str, Any]]
    ) -> ValidationResult:
        """
        Validate cross-domain relationships.
        
        Args:
            data_by_domain: Mapping of domain name to domain config
            
        Returns:
            ValidationResult with any cross-domain errors
        """
        errors = []
        
        # Example rule: feature requires dependency enabled
        if "feature_flags" in data_by_domain and "capabilities" in data_by_domain:
            flags = data_by_domain["feature_flags"]
            caps = data_by_domain["capabilities"]
            
            # Check for any flag that requires a capability
            for key, value in flags.items():
                if isinstance(value, dict):
                    requires_cap = value.get("requires_capability")
                    if requires_cap and requires_cap not in caps:
                        errors.append(
                            f"Cross-domain validation failed: "
                            f"feature {key} requires capability '{requires_cap}' which is not defined"
                        )
        
        return ValidationResult(
            stage="cross-domain",
            success=len(errors) == 0,
            errors=tuple(errors)
        )


# =============================================================================
# Full Validation Pipeline
# =============================================================================

class ConfigurationValidator:
    """
    Complete configuration validation pipeline.
    
    Runs all validation stages and aggregates results.
    """
    
    def __init__(
        self,
        type_fields: Optional[Dict[str, type]] = None,
        semantic_validators: Optional[Dict[str, Any]] = None,
        cross_field_rules: Optional[Dict[str, Any]] = None,
        domain_rules: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with validation rules.
        
        Args:
            type_fields: Expected types per field path
            semantic_validators: Validator functions per field path
            cross_field_rules: Cross-field relationship rules
            domain_rules: Cross-domain relationship rules
        """
        self._type_fields = type_fields or {}
        self._type_validator = TypeValidator()
        self._semantic_validator = SemanticValidator(semantic_validators)
        self._cross_field_validator = CrossFieldValidator(cross_field_rules)
        self._cross_domain_validator = CrossDomainValidator(domain_rules)
    
    def validate(
        self,
        data: Dict[str, Any],
        schema_id: str,
        version: int
    ) -> ValidationReport:
        """
        Run all validation stages.
        
        Args:
            data: Configuration data to validate
            schema_id: Schema identifier for report tracking
            version: Configuration version
            
        Returns:
            Complete validation report
        """
        type_result = self._type_validator.validate(data, self._type_fields)
        semantic_result = self._semantic_validator.validate(
            data,
            domain_rules=None
        )
        
        # Cross-field and cross-domain may not always be applicable
        cross_field_result = None
        if isinstance(data, dict) and len(data) > 0:
            cross_field_result = self._cross_field_validator.validate(data)
        
        # For now, cross-domain requires domain-separated data
        cross_domain_result = ValidationResult(
            stage="cross-domain",
            success=True,
            errors=()
        )
        
        overall_valid = (
            type_result.success and 
            semantic_result.success and
            (cross_field_result is None or cross_field_result.success) and
            cross_domain_result.success
        )
        
        return ValidationReport(
            schema_id=schema_id,
            configuration_version=version,
            overall_valid=overall_valid,
            type_validation=type_result,
            semantic_validation=semantic_result,
            cross_field_validation=cross_field_result,
            cross_domain_validation=cross_domain_result,
            validated_at=time.monotonic()
        )


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # Results
    "ValidationResult",
    "ValidationReport",
    
    # Stages
    "TypeValidator",
    "SemanticValidator",
    "CrossFieldValidator",
    "CrossDomainValidator",
    
    # Pipeline
    "ConfigurationValidator",
]