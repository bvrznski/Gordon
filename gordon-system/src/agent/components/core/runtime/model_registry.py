# Model Registry - Canonical Model Registration Authority
# =========================================================

"""
Model registry for deterministic model registration and discovery.

This module provides:
- Single canonical authority for model registration
- Deterministic model identity management
- Version tracking
- Capability descriptors
- Compatibility validation

Architecture Principle: Exactly ONE model registry exists.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
)
from enum import Enum, auto
import time
import uuid

T = TypeVar("T")


# =============================================================================
# MODEL IDENTITIES AND DESCRIPTORS
# =============================================================================


class ModelStatus(Enum):
    """Status of a model in the registry."""
    
    REGISTERED = "registered"           # Registered but not loaded
    LOADING = "loading"                 # Currently loading
    READY = "ready"                     # Loaded and ready for inference
    UNLOADING = "unloading"             # Currently unloading
    FAILED = "failed"                   # Failed during load/unload
    DEPRECATED = "deprecated"           # Deprecated but still registered


class LoadingState(Enum):
    """Loading state machine states."""
    
    NOT_LOADED = "not_loaded"
    LOADING_STARTED = "loading_started"
    LOADED = "loaded"
    UNLOADING_STARTED = "unloading_started"
    UNLOADED = "unloaded"


@dataclass(frozen=True)
class ModelIdentity:
    """
    Immutable identity of a model.
    
    This is the canonical identifier for a model. All other references
    to this model must use this identity.
    """
    
    model_id: str                       # Unique model identifier
    version: str                        # Version string (e.g., "1.0.0")
    provider_id: Optional[str] = None   # Provider that provides this model
    
    def __hash__(self) -> int:
        return hash((self.model_id, self.version))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModelIdentity):
            return False
        return (self.model_id == other.model_id and 
                self.version == other.version)


@dataclass(frozen=True)
class ModelDescriptor:
    """
    Immutable descriptor for a model.
    
    Contains all operational metadata about a model without exposing
    any runtime state or implementation details.
    """
    
    # Core identification
    model_id: str                       # Unique model identifier
    version: str                        # Version string
    
    # Modality support
    modality: Set[str]                  # Supported modalities (text, image, etc.)
    
    # Context window
    context_window: int                 # Maximum context length in tokens
    
    # Tokenizer info
    tokenizer_id: Optional[str] = None  # Tokenizer identifier if separate
    
    # Quantization
    quantization: Optional[str] = None  # e.g., "4bit", "8bit", "float16"
    
    # Runtime compatibility
    compatible_runtimes: Set[str] = field(default_factory=set)  # llama.cpp, vLLM, etc.
    
    # Memory requirements (in bytes)
    memory_requirements: Optional[int] = None  # Estimated VRAM/RAM needed
    
    # Precision
    precision: str = "float16"          # e.g., "float16", "bfloat16", "int8"
    
    # Device requirements
    device_requirements: Set[str] = field(default_factory=set)  # cuda, rocm, cpu, metal
    
    # Supported capabilities (inference types)
    supported_capabilities: Set[str] = field(default_factory=set)  # chat_completion, embeddings, etc.
    
    def is_compatible_with_runtime(self, runtime_name: str) -> bool:
        """Check if model is compatible with given runtime."""
        return runtime_name in self.compatible_runtimes
    
    def requires_device(self, device_type: str) -> bool:
        """Check if model requires specific device type."""
        return device_type in self.device_requirements


# =============================================================================
# REGISTRATION ERRORS
# =============================================================================


class RegistrationError(Exception):
    """Base exception for registration errors."""
    
    def __init__(self, message: str, model_id: Optional[str] = None):
        super().__init__(message)
        self.model_id = model_id


class DuplicateRegistrationError(RegistrationError):
    """Raised when attempting to register a duplicate model."""
    
    pass


class ModelNotFoundError(RegistrationError):
    """Raised when model is not found in registry."""
    
    pass


# =============================================================================
# MODEL REGISTRY
# =============================================================================


class ModelRegistry:
    """
    Canonical model registration authority.
    
    This is the SINGLE canonical authority for model registration in Gordon.
    All model registration flows must go through this registry.
    
    Responsibilities:
        - Register models with deterministic uniqueness validation
        - Track model lifecycle state (NOT_LOADED, LOADING, READY, etc.)
        - Provide discovery via capability queries
        - Maintain version history
    
    Does NOT:
        - Load/unload models (handled by ModelLoader)
        - Own inference execution
        - Manage compute resources
    
    Invariants:
        - Exactly ONE registry instance exists
        - Registration is deterministic (same model_id + version = same entry)
        - No implicit registration during import
        - Sealed registries cannot be modified
    """
    
    def __init__(self) -> None:
        """Initialize the model registry."""
        self._models: Dict[ModelIdentity, ModelDescriptor] = {}
        self._status_map: Dict[ModelIdentity, ModelStatus] = {}
        self._loading_state_map: Dict[ModelIdentity, LoadingState] = {}
        self._registrations: Dict[str, List[Tuple[ModelIdentity, float]]] = {}  # model_id -> [(version, timestamp)]
        self._sealed = False
        self._lock = __import__("threading").Lock()
    
    @property
    def is_sealed(self) -> bool:
        """Check if registry has been sealed."""
        return self._sealed
    
    def seal(self) -> None:
        """
        Seal the registry to prevent further modifications.
        
        After sealing, no new registrations can be added.
        This is used during runtime activation to ensure
        model registration remains stable during operation.
        """
        with self._lock:
            self._sealed = True
    
    # -------------------------------------------------------------------------
    # Registration (deterministic)
    # -------------------------------------------------------------------------
    
    def register(
        self,
        descriptor: ModelDescriptor,
    ) -> Tuple[bool, Optional[str]]:
        """
        Register a model with the registry.
        
        Args:
            descriptor: Model descriptor containing identity and metadata
            
        Returns:
            Tuple of (success, error_message)
            
        Raises:
            RegistrationError: If registration fails due to validation
        """
        if self._sealed:
            raise RegistrationError(
                f"Cannot register model '{descriptor.model_id}': registry is sealed",
                model_id=descriptor.model_id,
            )
        
        identity = ModelIdentity(
            model_id=descriptor.model_id,
            version=descriptor.version,
            provider_id=descriptor.provider_id,
        )
        
        with self._lock:
            # Check for duplicate registration
            if identity in self._models:
                existing = self._models[identity]
                if existing == descriptor:
                    return True, None  # Re-registration of same model is OK
                raise DuplicateRegistrationError(
                    f"Model '{descriptor.model_id}' version '{descriptor.version}' "
                    f"is already registered",
                    model_id=descriptor.model_id,
                )
            
            # Register the model
            self._models[identity] = descriptor
            self._status_map[identity] = ModelStatus.REGISTERED
            self._loading_state_map[identity] = LoadingState.NOT_LOADED
            
            # Track registration history
            if descriptor.model_id not in self._registrations:
                self._registrations[descriptor.model_id] = []
            self._registrations[descriptor.model_id].append(
                (identity, time.time())
            )
            
            return True, None
    
    def register_model_id(
        self,
        model_id: str,
        version: str,
        descriptor: ModelDescriptor,
    ) -> Tuple[bool, Optional[str]]:
        """
        Register a model with explicit ID and version.
        
        This is the primary registration method that should be used
        in production code to ensure deterministic registration.
        """
        return self.register(descriptor)
    
    # -------------------------------------------------------------------------
    # Lookup (deterministic)
    # -------------------------------------------------------------------------
    
    def get(self, model_id: str, version: Optional[str] = None) -> Optional[ModelDescriptor]:
        """
        Get a model descriptor by ID and optional version.
        
        Args:
            model_id: The model identifier
            version: Optional version string (if None, returns latest)
            
        Returns:
            ModelDescriptor if found, None otherwise
        """
        with self._lock:
            if version is not None:
                identity = ModelIdentity(model_id=model_id, version=version)
                return self._models.get(identity)
            
            # Return latest version
            candidates = [
                (ident, desc) 
                for ident, desc in self._models.items() 
                if ident.model_id == model_id
            ]
            if not candidates:
                return None
            
            # Sort by version and return latest
            candidates.sort(
                key=lambda x: self._parse_version(x[0].version),
                reverse=True,
            )
            return candidates[0][1]
    
    def get_all(self) -> List[Tuple[ModelIdentity, ModelDescriptor]]:
        """
        Get all registered models.
        
        Returns:
            List of (identity, descriptor) tuples
        """
        with self._lock:
            return list(self._models.items())
    
    # -------------------------------------------------------------------------
    # Discovery
    # -------------------------------------------------------------------------
    
    def find_by_capability(
        self,
        capability: str,
    ) -> List[Tuple[ModelIdentity, ModelDescriptor]]:
        """
        Find models that support a specific capability.
        
        Args:
            capability: The capability to search for (e.g., "chat_completion")
            
        Returns:
            List of matching model descriptors
        """
        with self._lock:
            results = []
            for identity, descriptor in self._models.items():
                if capability in descriptor.supported_capabilities:
                    results.append((identity, descriptor))
            return results
    
    def find_by_runtime(
        self,
        runtime_name: str,
    ) -> List[Tuple[ModelIdentity, ModelDescriptor]]:
        """
        Find models compatible with a specific runtime.
        
        Args:
            runtime_name: The runtime name to search for
            
        Returns:
            List of compatible model descriptors
        """
        with self._lock:
            results = []
            for identity, descriptor in self._models.items():
                if descriptor.is_compatible_with_runtime(runtime_name):
                    results.append((identity, descriptor))
            return results
    
    def find_by_device(
        self,
        device_type: str,
    ) -> List[Tuple[ModelIdentity, ModelDescriptor]]:
        """
        Find models that require a specific device type.
        
        Args:
            device_type: The device type (e.g., "cuda", "cpu")
            
        Returns:
            List of model descriptors requiring the device
        """
        with self._lock:
            results = []
            for identity, descriptor in self._models.items():
                if descriptor.requires_device(device_type):
                    results.append((identity, descriptor))
            return results
    
    # -------------------------------------------------------------------------
    # Status management
    # -------------------------------------------------------------------------
    
    def get_status(self, model_id: str, version: Optional[str] = None) -> ModelStatus:
        """
        Get the status of a registered model.
        
        Args:
            model_id: The model identifier
            version: Optional version string
            
        Returns:
            ModelStatus for the requested model
            
        Raises:
            ModelNotFoundError: If model not found
        """
        descriptor = self.get(model_id, version)
        if descriptor is None:
            raise ModelNotFoundError(f"Model '{model_id}' not found", model_id=model_id)
        
        identity = ModelIdentity(
            model_id=descriptor.model_id,
            version=descriptor.version,
        )
        
        with self._lock:
            return self._status_map.get(identity, ModelStatus.REGISTERED)
    
    def set_status(self, model_id: str, version: Optional[str], status: ModelStatus) -> None:
        """
        Set the status of a registered model.
        
        Args:
            model_id: The model identifier
            version: Optional version string
            status: New status to set
            
        Raises:
            ModelNotFoundError: If model not found
        """
        descriptor = self.get(model_id, version)
        if descriptor is None:
            raise ModelNotFoundError(f"Model '{model_id}' not found", model_id=model_id)
        
        identity = ModelIdentity(
            model_id=descriptor.model_id,
            version=descriptor.version,
        )
        
        with self._lock:
            self._status_map[identity] = status
    
    def get_loading_state(self, model_id: str, version: Optional[str] = None) -> LoadingState:
        """
        Get the loading state of a registered model.
        
        Args:
            model_id: The model identifier
            version: Optional version string
            
        Returns:
            LoadingState for the requested model
            
        Raises:
            ModelNotFoundError: If model not found
        """
        descriptor = self.get(model_id, version)
        if descriptor is None:
            raise ModelNotFoundError(f"Model '{model_id}' not found", model_id=model_id)
        
        identity = ModelIdentity(
            model_id=descriptor.model_id,
            version=descriptor.version,
        )
        
        with self._lock:
            return self._loading_state_map.get(identity, LoadingState.NOT_LOADED)
    
    def set_loading_state(self, model_id: str, version: Optional[str], state: LoadingState) -> None:
        """
        Set the loading state of a registered model.
        
        Args:
            model_id: The model identifier
            version: Optional version string
            state: New loading state
            
        Raises:
            ModelNotFoundError: If model not found
        """
        descriptor = self.get(model_id, version)
        if descriptor is None:
            raise ModelNotFoundError(f"Model '{model_id}' not found", model_id=model_id)
        
        identity = ModelIdentity(
            model_id=descriptor.model_id,
            version=descriptor.version,
        )
        
        with self._lock:
            self._loading_state_map[identity] = state
    
    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------
    
    def count(self) -> int:
        """Return total number of registered models."""
        with self._lock:
            return len(self._models)
    
    def count_by_status(self, status: ModelStatus) -> int:
        """Count models in a specific status."""
        with self._lock:
            return sum(1 for s in self._status_map.values() if s == status)
    
    # -------------------------------------------------------------------------
    # Private utilities
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _parse_version(version_str: str) -> Tuple[int, ...]:
        """Parse version string into comparable tuple."""
        parts = []
        for part in version_str.split("."):
            try:
                parts.append(int(part))
            except ValueError:
                break
        return tuple(parts)


# =============================================================================
# GLOBAL REGISTRY ACCESSOR (for convenience)
# =============================================================================


class _GlobalRegistry:
    """Internal global registry accessor for convenience."""
    
    def __init__(self) -> None:
        self._instance: Optional[ModelRegistry] = None
    
    def set_instance(self, instance: ModelRegistry) -> None:
        """Set the global registry instance."""
        if self._instance is not None:
            raise RuntimeError("Global registry already initialized")
        self._instance = instance
    
    @property
    def instance(self) -> ModelRegistry:
        """Get or create the global registry instance."""
        if self._instance is None:
            self._instance = ModelRegistry()
        return self._instance


_global_registry_accessor = _GlobalRegistry()


def get_model_registry() -> ModelRegistry:
    """
    Get the global model registry instance.
    
    Returns:
        The global ModelRegistry instance
    """
    return _global_registry_accessor.instance


def set_model_registry(instance: ModelRegistry) -> None:
    """
    Set the global model registry instance.
    
    Args:
        instance: The ModelRegistry to use as global instance
        
    Raises:
        RuntimeError: If registry already initialized
    """
    _global_registry_accessor.set_instance(instance)


__all__ = [
    # Enums
    "ModelStatus",
    "LoadingState",
    # Dataclasses
    "ModelIdentity",
    "ModelDescriptor",
    # Exceptions
    "RegistrationError",
    "DuplicateRegistrationError",
    "ModelNotFoundError",
    # Registry
    "ModelRegistry",
    # Global accessor
    "get_model_registry",
    "set_model_registry",
]