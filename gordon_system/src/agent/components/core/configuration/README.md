# Configuration & Dependency Management

## Overview

This package implements Phase 3.8.4: Configuration & Dependency Management for Gordon Core.

The canonical configuration and dependency management subsystem provides:

1. **Configuration** - Declarative runtime intent, immutable schemas, source precedence
2. **Dependency Injection** - Explicit dependencies, service lifetime management, graph validation

## Architecture Principles

### Core Laws

- **Configuration is declarative** - No execution semantics
- **One canonical owner** - Single authority per responsibility
- **Schemas precede values** - Type safety first
- **Immutability by default** - Values immutable unless reloadable
- **Documented purposes** - Every config has documented intent
- **No hidden configuration** - All sources explicit
- **No global mutable state** - State confined to scopes
- **Backend-independent contracts** - Configuration agnostic of source
- **Validation precedes consumption** - Errors fail fast
- **Configuration changes are observable** - Audit trail maintained

### Architecture Boundaries

```
┌─────────────────────────────────────────────────────────┐
│                    COMPOSITION ROOT                     │
│  (KernelBuilder, StartupCoordinator)                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐     ┌─────────────────────┐      │
│  │ Configuration    │<────┤ Dependency          │      │
│  │ Authority        │     │ Injection System    │      │
│  └────────┬─────────┘     └─────────┬───────────┘      │
│           │                         │                  │
│  ┌────────┴─────────┐     ┌────────┴────────────┐      │
│  │ Schema Registry  │     │ Service Registry    │      │
│  └────────┬─────────┘     └─────────────────────┘      │
│           │                                             │
│  ┌────────┴──────────────────────────────────────┐      │
│  │ Provider Registry (Sources)                   │      │
│  └───────────────────────────────────────────────┘      │
│                                                         │
└─────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │    Runtime      │
                    │   Execution     │
                    └─────────────────┘
```

## Module Structure

### types.py - Core Type Definitions

Shared type definitions that avoid circular imports:

- `RuntimeId`, `ConfigurationId`, `ConfigurationVersion` - Identity types
- `PrecedenceLevel`, `PrecedenceRule`, `PrecedenceModel` - Source ordering
- `SourceType` - Configuration source enumerations
- `SchemaField`, `DomainSchema`, `FieldType` - Schema definitions
- `SchemaConflictType`, `SchemaRegistryId`, `SchemaRegistration` - Conflict detection

### __init__.py - Canonical Authority

Main module with canonical authorities:

- **EffectiveConfiguration** - Immutable configuration snapshot with content digest
- **SchemaRegistry** - Schema registration and conflict detection
- **ConfigurationAuthority** - Single source of truth for all configuration operations

### sources.py - Source Protocol & Registry

Configuration source implementations:

- `ConfigurationSourceProtocol` - Interface for all sources
- `BuiltinDefaultsSource`, `ProfileDefaultsSource` - Default providers
- `ConfigFileSource` - File loading (JSON/YAML)
- `EnvironmentVariablesSource` - Environment variable access
- `CommandLineArgumentsSource` - CLI argument parsing
- `RuntimeOverridesSource` - Runtime-provided overrides
- `ConfigurationProviderRegistry` - Source registration and precedence

### services.py - Dependency Injection Framework

Service registry and dependency injection:

- **Lifetime** - Singleton, Scoped, Transient policies
- **ServiceDescriptor** - Service contract and implementation description
- **DependencyGraph** - Graph representation with cycle detection
- **ServiceRegistry** - Central service registry
- **DependencyResolver** - Resolution engine with caching
- **ServiceScope** - Scoped lifetime management

## Core Abstractions

### ConfigurationDomain

A configuration domain represents a coherent set of related settings:

```python
@dataclass(frozen=True)
class ConfigurationDomain:
    domain_id: str  # e.g., "kernel", "runtime"
    owner: Optional[str]
    version: int
    fields: Dict[str, type]  # name -> expected type
    defaults: Dict[str, Any]
    mutability_class: str  # STATIC, RUNTIME_MUTABLE
    restart_required: bool
```

### SchemaField

A schema field defines a configuration value:

```python
@dataclass(frozen=True)
class SchemaField:
    name: str
    field_type: FieldType  # STRING, INTEGER, FLOAT, BOOLEAN, LIST, DICT, ENUM
    required: bool = False
    default: Any = None
    description: Optional[str]
    
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[Tuple[str, ...]] = None
    
    mutability: str  # RUNTIME_MUTABLE, STATIC
    restart_required: bool = False
    sensitive: bool = False
```

### EffectiveConfiguration

The authoritative configuration with source attribution:

```python
@dataclass(frozen=True)
class EffectiveConfiguration:
    runtime_id: str
    config_id: str
    version: int
    content_digest: str  # SHA256 of effective values
    
    domains: Dict[str, Dict[str, Any]]
    sources: Dict[str, Tuple[ConfigurationSourceId, ...]]  # field -> source attribution
    
    schema_versions: Dict[str, ConfigurationVersion]
    
    created_at: float
    warnings: Tuple[str, ...]
    deprecations: Tuple[str, ...]
```

### ServiceDescriptor

Describes a service for dependency injection:

```python
@dataclass(frozen=True)
class ServiceDescriptor:
    contract_type: type  # The interface/service contract
    implementation_type: Optional[type] = None  # Concrete class
    factory_function: Optional[Callable[[Any], Any]] = None  # Factory
    lifetime_policy: LifetimePolicy = field(...)
```

## Precedence Model

Configuration sources are ordered by precedence (lower value = higher priority):

| Level | Source Type | Priority |
|-------|-------------|----------|
| 0 | BUILTIN_DEFAULTS | Lowest |
| 10 | PROFILE_DEFAULTS | |
| 20 | CONFIG_FILES | |
| 30 | ENVIRONMENT_VARS | |
| 40 | COMMAND_LINE_ARGS | |
| 50 | RUNTIME_OVERRIDES | |
| 100 | EMERGENCY_OVERRIDES | Highest |

## Usage Example

### Configuration Setup

```python
from gordon.system.components.core.configuration import (
    ConfigurationAuthority,
    BuiltinDefaultsSource,
    EnvironmentVariablesSource,
)

# Create authority
authority = ConfigurationAuthority(runtime_id="my-runtime-123")

# Register sources
authority.load_sources((
    BuiltinDefaultsSource({"app.name": "Gordon", "log.level": "INFO"}),
    EnvironmentVariablesSource(prefix="GORDON_"),
))

# Resolve configuration
config = authority.resolve_configuration()

# Access values
app_name = config.get("default", "app.name")
```

### Service Registration

```python
from gordon.system.components.core.configuration import (
    ServiceRegistry,
    ServiceDescriptor,
    LifetimePolicy,
)

# Create registry
registry = ServiceRegistry()

# Register services
registry.register(ServiceDescriptor(
    contract_type=MyServiceInterface,
    implementation_type=MyServiceImpl,
    lifetime_policy=LifetimePolicy(Lifetime.SINGLETON)
))

# Resolve services
resolver = DependencyResolver(registry)
result = resolver.resolve(my_service_id)

if result.success:
    service_instance = result.instance
```

## Failure Model

Typed exceptions for error handling:

- `ConfigurationError` - Base configuration error
- `SchemaError` - Schema validation errors
- `ValidationError` - Value validation errors
- `MissingConfigurationError` - Required config missing
- `InvalidConfigurationError` - Invalid value format
- `CompatibilityError` - Version/compatibility issues
- `DuplicateRegistrationError` - Service already registered
- `DependencyResolutionError` - Resolution failure

## Testing Strategy

### Unit Tests

- Schema validation (type, range, allowed values)
- Nested schema composition
- Precedence resolution
- Immutability enforcement
- Version tracking
- Cycle detection in dependency graphs

### Integration Tests

- End-to-end configuration loading
- Source precedence ordering
- Service graph construction
- Lifetime policy enforcement

## Future Enhancements

1. **Reload Framework** - Hot-reconfiguration for eligible sections
2. **Profile Management** - Named profiles with inheritance
3. **Remote Configuration** - Fetch from remote sources
4. **Secret Integration** - Secret provider integration
5. **Audit Logging** - Complete audit trail of changes
6. **Compatibility Checks** - Version compatibility validation

## References

- Phase 3.8.4.1: Configuration Foundations
- Phase 3.8.4.2: Configuration Providers & Validation
- Phase 3.8.4.3: Dependency Injection & Lifetimes
- Phase 3.8.4.4: Composition Root
- Phase 3.8.4.5: Runtime Integration