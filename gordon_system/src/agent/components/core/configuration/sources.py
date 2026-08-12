# Configuration Sources Module
# ===========================
"""
Configuration source collection and loading system.

Provides:
- Source protocol definitions
- Built-in source implementations
- Source descriptor management
- Deterministic source ordering

Phase 3.8.4: Configuration & Dependency Management
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
import os
import json
import time


# Import types from the dedicated types module to avoid circular imports
from .types import (
    ConfigurationSourceId,
    SourceType,
    ConfigurationSourceDescriptor,
    ConfigurationSourceResult,
    PrecedenceModel,
    PrecedenceRule,
)


# =============================================================================
# Source Protocol (Interface)
# =============================================================================

class ConfigurationSourceProtocol:
    """
    Protocol for configuration sources.
    
    Sources must:
    - Be explicitly registered
    - Expose identity
    - Return immutable raw values
    - Preserve source provenance
    - Avoid mutating effective configuration
    - Remain runtime-scoped
    """
    
    @property
    def source_id(self) -> ConfigurationSourceId:
        """Unique identifier for this source."""
        raise NotImplementedError
    
    @property
    def name(self) -> str:
        """Human-readable name for logging/diagnostics."""
        raise NotImplementedError
    
    @property
    def source_type(self) -> SourceType:
        """Type of configuration source."""
        raise NotImplementedError
    
    @property
    def priority(self) -> int:
        """Priority for precedence ordering (higher = more influential)."""
        raise NotImplementedError
    
    def load(self, runtime_id: Optional[str] = None) -> ConfigurationSourceResult:
        """
        Load configuration from this source.
        
        Args:
            runtime_id: Optional runtime ID for runtime-scoped sources
            
        Returns:
            SourceResult with data and any parsing errors
        """
        raise NotImplementedError
    
    def get_descriptor(self) -> ConfigurationSourceDescriptor:
        """Return a descriptor for this source."""
        return ConfigurationSourceDescriptor(
            id=self.source_id,
            name=self.name,
            source_type=self.source_type,
            precedence_level=self.priority
        )


# =============================================================================
# Built-in Source Implementations
# =============================================================================

@dataclass(frozen=True)
class BuiltinDefaultsSource(ConfigurationSourceProtocol):
    """
    Provides built-in default configuration values.
    
    These are the lowest-priority defaults that can be overridden by all
    other sources. They represent sensible defaults for the system.
    """
    
    _defaults: Dict[str, Any]
    _source_id: ConfigurationSourceId = field(default_factory=ConfigurationSourceId.generate)
    
    @property
    def source_id(self) -> ConfigurationSourceId:
        return self._source_id
    
    @property
    def name(self) -> str:
        return "builtin_defaults"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.BUILTIN_DEFAULTS
    
    @property
    def priority(self) -> int:
        return 1  # Lowest priority
    
    def load(self, runtime_id: Optional[str] = None) -> ConfigurationSourceResult:
        """Load built-in defaults."""
        return ConfigurationSourceResult(
            id=self._source_id,
            data=dict(self._defaults),
            parsed_at=time.monotonic()
        )


@dataclass(frozen=True)
class ProfileDefaultsSource(ConfigurationSourceProtocol):
    """
    Provides profile-specific default configuration.
    
    These override builtin defaults with values appropriate for a specific
    environment profile (development, production, test, etc.).
    """
    
    _profile: str
    _defaults: Dict[str, Any]
    _source_id: ConfigurationSourceId = field(default_factory=ConfigurationSourceId.generate)
    
    @property
    def source_id(self) -> ConfigurationSourceId:
        return self._source_id
    
    @property
    def name(self) -> str:
        return f"profile_defaults:{self._profile}"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.PROFILE_DEFAULTS
    
    @property
    def priority(self) -> int:
        return 10
    
    def load(self, runtime_id: Optional[str] = None) -> ConfigurationSourceResult:
        """Load profile defaults."""
        return ConfigurationSourceResult(
            id=self._source_id,
            data=dict(self._defaults),
            parsed_at=time.monotonic()
        )


@dataclass(frozen=True)
class ConfigFileSource(ConfigurationSourceProtocol):
    """
    Loads configuration from a file.
    
    Supports JSON and YAML formats. Automatically detects format by extension.
    """
    
    _file_path: str
    _source_id: ConfigurationSourceId = field(default_factory=ConfigurationSourceId.generate)
    
    @property
    def source_id(self) -> ConfigurationSourceId:
        return self._source_id
    
    @property
    def name(self) -> str:
        return f"config_file:{self._file_path}"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.CONFIG_FILE
    
    @property
    def priority(self) -> int:
        return 20
    
    def load(self, runtime_id: Optional[str] = None) -> ConfigurationSourceResult:
        """Load configuration from file."""
        try:
            with open(self._file_path, 'r') as f:
                content = f.read()
            
            # Detect format by extension
            if self._file_path.endswith('.json'):
                data = json.loads(content)
            elif self._file_path.endswith(('.yaml', '.yml')):
                import yaml
                data = yaml.safe_load(content) or {}
            else:
                return ConfigurationSourceResult(
                    id=self._source_id,
                    data={},
                    parsed_at=time.monotonic(),
                    errors=(f"Unknown config file format: {self._file_path}",)
                )
            
            if not isinstance(data, dict):
                return ConfigurationSourceResult(
                    id=self._source_id,
                    data={},
                    parsed_at=time.monotonic(),
                    errors=("Config file must contain a JSON object",)
                )
            
            return ConfigurationSourceResult(
                id=self._source_id,
                data=data,
                parsed_at=time.monotonic()
            )
        except FileNotFoundError:
            return ConfigurationSourceResult(
                id=self._source_id,
                data={},
                parsed_at=time.monotonic(),
                errors=(f"Config file not found: {self._file_path}",)
            )
        except json.JSONDecodeError as e:
            return ConfigurationSourceResult(
                id=self._source_id,
                data={},
                parsed_at=time.monotonic(),
                errors=(f"Invalid JSON in config file: {e}",)
            )
        except Exception as e:
            return ConfigurationSourceResult(
                id=self._source_id,
                data={},
                parsed_at=time.monotonic(),
                errors=(f"Error loading config file: {e}",)
            )


@dataclass(frozen=True)
class EnvironmentVariablesSource(ConfigurationSourceProtocol):
    """
    Loads configuration from environment variables.
    
    Supports prefix-based filtering and type conversion.
    """
    
    _prefix: Optional[str] = None
    _convert_types: bool = True
    _source_id: ConfigurationSourceId = field(default_factory=ConfigurationSourceId.generate)
    
    @property
    def source_id(self) -> ConfigurationSourceId:
        return self._source_id
    
    @property
    def name(self) -> str:
        if self._prefix:
            return f"env:{self._prefix}*"
        return "env:*"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.ENVIRONMENT_VAR
    
    @property
    def priority(self) -> int:
        return 30
    
    def load(self, runtime_id: Optional[str] = None) -> ConfigurationSourceResult:
        """Load configuration from environment variables."""
        env_data = {}
        
        for key, value in os.environ.items():
            # Filter by prefix if specified
            if self._prefix and not key.startswith(self._prefix):
                continue
            
            # Remove prefix for the config key
            config_key = key[len(self._prefix):] if self._prefix else key
            
            # Convert type if enabled
            converted_value = value
            if self._convert_types:
                converted_value = _parse_env_value(value)
            
            env_data[config_key] = converted_value
        
        return ConfigurationSourceResult(
            id=self._source_id,
            data=env_data,
            parsed_at=time.monotonic()
        )


@dataclass(frozen=True)
class CommandLineArgumentsSource(ConfigurationSourceProtocol):
    """
    Loads configuration from command-line arguments.
    
    Supports both flag-style (--config=value) and positional arguments.
    """
    
    _args: List[str]
    _source_id: ConfigurationSourceId = field(default_factory=ConfigurationSourceId.generate)
    
    @property
    def source_id(self) -> ConfigurationSourceId:
        return self._source_id
    
    @property
    def name(self) -> str:
        return "command_line_arguments"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.COMMAND_LINE_ARG
    
    @property
    def priority(self) -> int:
        return 40
    
    def load(self, runtime_id: Optional[str] = None) -> ConfigurationSourceResult:
        """Load configuration from command-line arguments."""
        args_data = {}
        
        for arg in self._args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                # Normalize key (remove leading dashes and convert to snake_case)
                config_key = key.lstrip('-').replace('-', '_')
                args_data[config_key] = _parse_env_value(value)
        
        return ConfigurationSourceResult(
            id=self._source_id,
            data=args_data,
            parsed_at=time.monotonic()
        )


@dataclass(frozen=True)
class RuntimeOverridesSource(ConfigurationSourceProtocol):
    """
    Provides runtime-provided configuration overrides.
    
    These are the highest-priority configuration values that can override
    all other sources. Used for dynamic reconfiguration and emergency changes.
    """
    
    _overrides: Dict[str, Any]
    _runtime_id: str
    _source_id: ConfigurationSourceId = field(default_factory=ConfigurationSourceId.generate)
    
    @property
    def source_id(self) -> ConfigurationSourceId:
        return self._source_id
    
    @property
    def name(self) -> str:
        return f"runtime_overrides:{self._runtime_id[:8]}"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.RUNTIME_OVERRIDE
    
    @property
    def priority(self) -> int:
        return 100  # Highest priority
    
    def load(self, runtime_id: Optional[str] = None) -> ConfigurationSourceResult:
        """Load runtime overrides."""
        return ConfigurationSourceResult(
            id=self._source_id,
            data=dict(self._overrides),
            parsed_at=time.monotonic()
        )


# =============================================================================
# Source Registry
# =============================================================================

class ConfigurationProviderRegistry:
    """
    Manages configuration sources and their ordering.
    
    Sources are registered explicitly and ordered by precedence rules.
    """
    
    def __init__(self, precedence_model: Optional[PrecedenceModel] = None):
        self._registry: Dict[str, Any] = {}
        self._precedence_model = precedence_model or PrecedenceModel(rules=())
        self._lock = __import__("threading").Lock()
    
    def register(self, protocol: ConfigurationSourceProtocol) -> str:
        """
        Register a configuration source.
        
        Args:
            protocol: The source protocol to register
            
        Returns:
            The registered source ID string
        """
        descriptor = protocol.get_descriptor()
        
        with self._lock:
            if descriptor.id.value in self._registry:
                raise ValueError(f"Source {descriptor.id} already registered")
            
            self._registry[descriptor.id.value] = {
                'descriptor': descriptor,
                'protocol': protocol
            }
        
        return descriptor.id.value
    
    def unregister(self, source_id: str) -> bool:
        """Unregister a configuration source."""
        with self._lock:
            if source_id in self._registry:
                del self._registry[source_id]
                return True
            return False
    
    def get_source(self, source_id: str) -> Optional[ConfigurationSourceProtocol]:
        """Get a registered source by ID."""
        registered = self._registry.get(source_id)
        if registered:
            return registered['protocol']
        return None
    
    def list_sources(self) -> List[Tuple[str, str]]:
        """
        List all registered sources with their names and types.
        
        Returns:
            List of (name, type_name) tuples
        """
        with self._lock:
            return [
                (r['descriptor'].name, r['descriptor'].source_type.value)
                for r in self._registry.values()
            ]
    
    def get_ordered_sources(self, runtime_id: Optional[str] = None) -> List[Tuple[int, ConfigurationSourceProtocol]]:
        """
        Get sources ordered by precedence.
        
        Returns:
            List of (position, protocol) tuples, lowest position first
        """
        with self._lock:
            sources_with_positions = []
            
            for registered in self._registry.values():
                descriptor = registered['descriptor']
                
                # Determine position based on precedence model
                position = self._precedence_model.get_precedence(descriptor.source_type.value)
                
                sources_with_positions.append((position, registered['protocol']))
            
            # Sort by position (ascending - lower = higher priority)
            sources_with_positions.sort(key=lambda x: x[0])
            
            return sources_with_positions
    
    def load_all(self, runtime_id: Optional[str] = None) -> List[ConfigurationSourceResult]:
        """
        Load all enabled configuration sources.
        
        Args:
            runtime_id: Runtime ID for runtime-scoped sources
            
        Returns:
            List of source results in precedence order
        """
        ordered_sources = self.get_ordered_sources(runtime_id)
        results = []
        
        for position, protocol in ordered_sources:
            result = protocol.load(runtime_id)
            results.append(result)
        
        return results


# =============================================================================
# Helper Functions
# =============================================================================

def _parse_env_value(value: str) -> Any:
    """Parse environment variable string to appropriate type."""
    # Try boolean
    if value.lower() in ('true', 'yes', 'on'):
        return True
    if value.lower() in ('false', 'no', 'off'):
        return False
    
    # Try integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string
    return value


def create_precedence_model_from_profile(profile: str) -> PrecedenceModel:
    """
    Create a precedence model based on environment profile.
    
    Profiles define standard source precedence orders.
    """
    if profile == "production":
        rules = (
            PrecedenceRule(SourceType.BUILTIN_DEFAULTS.value, 1),
            PrecedenceRule(SourceType.PROFILE_DEFAULTS.value, 10),
            PrecedenceRule(SourceType.CONFIG_FILE.value, 20),
            PrecedenceRule(SourceType.ENVIRONMENT_VAR.value, 30),
            PrecedenceRule(SourceType.COMMAND_LINE_ARG.value, 40),
            PrecedenceRule(SourceType.RUNTIME_OVERRIDE.value, 100),
        )
    else:  # development, test
        rules = (
            PrecedenceRule(SourceType.BUILTIN_DEFAULTS.value, 1),
            PrecedenceRule(SourceType.PROFILE_DEFAULTS.value, 5),
            PrecedenceRule(SourceType.CONFIG_FILE.value, 20),
            PrecedenceRule(SourceType.ENVIRONMENT_VAR.value, 30),
            PrecedenceRule(SourceType.COMMAND_LINE_ARG.value, 40),
            PrecedenceRule(SourceType.RUNTIME_OVERRIDE.value, 100),
        )
    
    return PrecedenceModel(rules=rules)


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # Protocol
    "ConfigurationSourceProtocol",
    
    # Sources
    "BuiltinDefaultsSource",
    "ProfileDefaultsSource",
    "ConfigFileSource",
    "EnvironmentVariablesSource",
    "CommandLineArgumentsSource",
    "RuntimeOverridesSource",
    
    # Registry
    "ConfigurationProviderRegistry",
    
    # Helpers
    "create_precedence_model_from_profile",
]