# Configuration Schema Authority Module
# ======================================
"""
Schema registry, composition, and validation system.

Provides:
- Schema registry for authoritative field definitions
- Schema composition from domain schemas
- Schema conflict detection
- Field metadata and semantics

Phase 3.7.14: Configuration, Policy, Feature Flags & Runtime Reconfiguration
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
)
from enum import Enum
import time

from . import (
    SchemaField,
    FieldType,
    DomainSchema,
    ConfigurationSchemaId,
    ConfigurationVersion,
    ValidationError,
    ValidationReport,
)


# =============================================================================
# Schema Registry
# =============================================================================

class SchemaConflictType(Enum):
    """Types of schema conflicts."""
    DUPLICATE_PATH = "duplicate_path"
    INCOMPATIBLE_TYPES = "incompatible_types"
    CONFLICTING_DEFAULTS = "conflicting_defaults"
    CONFLICTING_MUTABILITY = "conflicting_mutability"
    CONFLICTING_OWNERSHIP = "conflicting_ownership"
    CIRCULAR_DERIVED = "circular_derived"


@dataclass(frozen=True)
class SchemaConflict:
    """A schema conflict detected during composition."""
    conflict_type: SchemaConflictType
    path: str
    message: str
    affected_schemas: Tuple[str, ...]


@dataclass(frozen=True)
class SchemaRegistryId:
    """Unique identifier for a schema registry."""
    value: str
    
    @classmethod
    def generate(cls) -> "SchemaRegistryId":
        return cls(value=str(hash(time.monotonic())))
    
    @classmethod
    def from_string(cls, s: str) -> "SchemaRegistryId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SchemaRegistration:
    """A registered schema with metadata."""
    schema_id: ConfigurationSchemaId
    domain_schema: DomainSchema
    registered_at: float = field(default_factory=time.monotonic)
    version: ConfigurationVersion = field(default_factory=lambda: ConfigurationVersion(1, 0, 0))


class SchemaRegistry:
    """
    Registry for configuration schemas.
    
    Provides:
    - Schema registration and retrieval
    - Schema composition with conflict detection
    - Version tracking
    
    Invariants:
    - One schema per domain path
    - No conflicting field definitions
    - Schemas are immutable once registered
    """
    
    def __init__(self):
        self._schemas: Dict[str, SchemaRegistration] = {}
        self._registry_id = SchemaRegistryId.generate()
        self._lock = __import__("threading").Lock()
    
    @property
    def registry_id(self) -> SchemaRegistryId:
        """Get the registry ID."""
        return self._registry_id
    
    def register_schema(
        self,
        domain_id: str,
        fields: Tuple[SchemaField, ...],
        version: Optional[ConfigurationVersion] = None
    ) -> ConfigurationSchemaId:
        """
        Register a schema for a domain.
        
        Args:
            domain_id: Domain identifier (e.g., "kernel", "runtime")
            fields: Schema field definitions
            version: Optional schema version
            
        Returns:
            Registered schema ID
            
        Raises:
            ValueError: If schema conflicts with existing schema
        """
        if not domain_id:
            raise ValueError("domain_id is required")
        
        if not fields:
            raise ValueError("At least one field is required")
        
        if version is None:
            version = ConfigurationVersion(1, 0, 0)
        
        # Check for conflicts
        with self._lock:
            existing = self._schemas.get(domain_id)
            if existing is not None:
                self._check_conflicts(existing.domain_schema, fields, domain_id)
            
            # Create new schema registration
            domain_schema = DomainSchema(
                domain_id=domain_id,
                fields=fields,
                schema_version=version
            )
            
            schema_id = ConfigurationSchemaId.generate()
            registration = SchemaRegistration(
                schema_id=schema_id,
                domain_schema=domain_schema,
                version=version
            )
            
            self._schemas[domain_id] = registration
        
        return schema_id
    
    def _check_conflicts(
        self,
        existing: DomainSchema,
        new_fields: Tuple[SchemaField, ...],
        domain_id: str
    ) -> None:
        """Check for conflicts between existing and new schemas."""
        existing_by_name = {f.name: f for f in existing.fields}
        
        for field in new_fields:
            if field.name in existing_by_name:
                existing_field = existing_by_name[field.name]
                
                # Check type compatibility
                if field.field_type != existing_field.field_type:
                    raise ValueError(
                        f"Schema conflict in {domain_id}.{field.name}: "
                        f"type mismatch (existing: {existing_field.field_type}, new: {field.field_type})"
                    )
                
                # Check mutability
                if field.mutability != existing_field.mutability:
                    raise ValueError(
                        f"Schema conflict in {domain_id}.{field.name}: "
                        f"mutability mismatch (existing: {existing_field.mutability}, new: {field.mutability})"
                    )
    
    def get_schema(self, domain_id: str) -> Optional[DomainSchema]:
        """Get a registered schema by domain ID."""
        registration = self._schemas.get(domain_id)
        if registration:
            return registration.domain_schema
        return None
    
    def get_all_schemas(self) -> Dict[str, DomainSchema]:
        """Get all registered schemas."""
        with self._lock:
            return {
                k: v.domain_schema for k, v in self._schemas.items()
            }
    
    def list_domains(self) -> List[str]:
        """List all domain IDs with registered schemas."""
        with self._lock:
            return list(self._schemas.keys())


# =============================================================================
# Schema Composition
# =============================================================================

@dataclass(frozen=True)
class ComposedSchema:
    """
    A composed schema from multiple domains.
    
    Represents the complete configuration schema for a runtime.
    """
    schema_id: ConfigurationSchemaId
    version: ConfigurationVersion
    domain_schemas: Dict[str, DomainSchema]
    field_map: Dict[str, Tuple[DomainSchema, SchemaField]]  # path -> (domain_schema, field)
    conflicts: Tuple[SchemaConflict, ...] = field(default_factory=tuple)
    created_at: float = field(default_factory=time.monotonic)


class SchemaComposer:
    """
    Composes domain schemas into a single runtime schema.
    
    Detects and reports conflicts during composition.
    """
    
    def __init__(self):
        self._registry = SchemaRegistry()
    
    @property
    def registry(self) -> SchemaRegistry:
        """Get the underlying schema registry."""
        return self._registry
    
    def compose(
        self,
        domain_schemas: Dict[str, DomainSchema]
    ) -> ComposedSchema:
        """
        Compose multiple domain schemas into one.
        
        Args:
            domain_schemas: Mapping of domain_id to DomainSchema
            
        Returns:
            Composed schema with field map and conflict info
        """
        schema_id = ConfigurationSchemaId.generate()
        
        # Merge all domains
        merged_domains = {}
        field_map = {}
        conflicts = []
        
        for domain_id, domain_schema in domain_schemas.items():
            merged_domains[domain_id] = domain_schema
            
            # Map each field by its full path (domain.field)
            for field in domain_schema.fields:
                path = f"{domain_id}.{field.name}"
                
                if path in field_map:
                    existing_domain, existing_field = field_map[path]
                    conflicts.append(SchemaConflict(
                        conflict_type=SchemaConflictType.DUPLICATE_PATH,
                        path=path,
                        message=f"Field {path} exists in both {existing_domain} and {domain_id}",
                        affected_schemas=(existing_domain, domain_id)
                    ))
                else:
                    field_map[path] = (domain_schema, field)
        
        version = self._compute_composed_version(list(domain_schemas.values()))
        
        return ComposedSchema(
            schema_id=schema_id,
            version=version,
            domain_schemas=merged_domains,
            field_map=field_map,
            conflicts=tuple(conflicts),
            created_at=time.monotonic()
        )
    
    def _compute_composed_version(
        self,
        domain_schemas: List[DomainSchema]
    ) -> ConfigurationVersion:
        """Compute the composed schema version from components."""
        # Use highest major, then minor, then patch
        major = max(s.schema_version.major for s in domain_schemas)
        minor = max(s.schema_version.minor for s in domain_schemas)
        patch = max(s.schema_version.patch for s in domain_schemas)
        
        return ConfigurationVersion(major, minor, patch)


# =============================================================================
# Schema Validation Helpers
# =============================================================================

def validate_schema_field(
    field: SchemaField,
    value: Any,
    path: str
) -> Tuple[ValidationError, ...]:
    """
    Validate a single field value against its schema.
    
    Args:
        field: The schema field definition
        value: The value to validate
        path: Dot-notation path for error messages
        
    Returns:
        Tuple of validation errors (empty if valid)
    """
    errors = []
    
    # Type validation
    type_errors = _validate_type(field, value, path)
    errors.extend(type_errors)
    
    # Range validation
    range_errors = _validate_range(field, value, path)
    errors.extend(range_errors)
    
    # Allowed values validation
    allowed_errors = _validate_allowed_values(field, value, path)
    errors.extend(allowed_errors)
    
    return tuple(errors)


def _validate_type(
    field: SchemaField,
    value: Any,
    path: str
) -> Tuple[ValidationError, ...]:
    """Validate value type against field type."""
    if not value and not field.required:
        return ()  # None/null is OK for optional fields
    
    errors = []
    
    expected_types = {
        FieldType.STRING: str,
        FieldType.INTEGER: int,
        FieldType.FLOAT: (int, float),
        FieldType.BOOLEAN: bool,
        FieldType.LIST: list,
        FieldType.DICT: dict,
        FieldType.ENUM: (str, Enum) if isinstance(field.allowed_values, tuple) else str,
    }
    
    expected_type = expected_types.get(field.field_type)
    if expected_type and not isinstance(value, expected_type):
        errors.append(ValidationError(
            path=path,
            message=f"Expected {field.field_type.value}, got {type(value).__name__}",
            value=value
        ))
    
    return tuple(errors)


def _validate_range(
    field: SchemaField,
    value: Any,
    path: str
) -> Tuple[ValidationError, ...]:
    """Validate value is within allowed range."""
    errors = []
    
    if isinstance(value, (int, float)):
        if field.min_value is not None and value < field.min_value:
            errors.append(ValidationError(
                path=path,
                message=f"Value {value} is less than minimum {field.min_value}",
                value=value
            ))
        
        if field.max_value is not None and value > field.max_value:
            errors.append(ValidationError(
                path=path,
                message=f"Value {value} is greater than maximum {field.max_value}",
                value=value
            ))
    
    return tuple(errors)


def _validate_allowed_values(
    field: SchemaField,
    value: Any,
    path: str
) -> Tuple[ValidationError, ...]:
    """Validate value is in allowed values list."""
    errors = []
    
    if field.allowed_values and value not in field.allowed_values:
        errors.append(ValidationError(
            path=path,
            message=f"Value {value} not in allowed values: {field.allowed_values}",
            value=value
        ))
    
    return tuple(errors)


# =============================================================================
# Default Schema Definitions
# =============================================================================

def create_default_domain_schema(
    domain_id: str,
    fields: List[SchemaField],
    version: ConfigurationVersion = ConfigurationVersion(1, 0, 0)
) -> DomainSchema:
    """
    Create a default domain schema with common field types.
    
    Args:
        domain_id: Domain identifier
        fields: List of field definitions
        version: Schema version
        
    Returns:
        DomainSchema instance
    """
    return DomainSchema(
        domain_id=domain_id,
        fields=tuple(fields),
        schema_version=version
    )


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # Registry
    "SchemaConflictType",
    "SchemaConflict",
    "SchemaRegistryId",
    "SchemaRegistration",
    "SchemaRegistry",
    
    # Composition
    "ComposedSchema",
    "SchemaComposer",
    
    # Validation Helpers
    "validate_schema_field",
    "_validate_type",
    "_validate_range",
    "_validate_allowed_values",
    
    # Defaults
    "create_default_domain_schema",
]