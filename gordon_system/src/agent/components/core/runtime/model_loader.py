# Model Loader - Loading and Unloading Authority
# ==============================================

"""
Model loader for deterministic model lifecycle management.

This module provides:
- Deterministic model loading/unloading
- Runtime compatibility validation
- Warm-up support
- Health verification

Architecture Principle: Exactly ONE model loader instance exists.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
)
from enum import Enum, auto
import time


# =============================================================================
# LOADING STATES AND RESULTS
# =============================================================================


class LoadingState(Enum):
    """States of model loading lifecycle."""
    
    NOT_REGISTERED = "not_registered"   # Not in registry
    PENDING_LOAD = "pending_load"       # Queued for loading
    LOADING = "loading"                 # Currently loading
    WARMING_UP = "warming_up"           # Warm-up phase
    READY = "ready"                     # Loaded and ready
    UNLOADING = "unloading"             # Currently unloading
    FAILED_LOAD = "failed_load"         # Load failed
    FAILED_WARMUP = "failed_warmup"     # Warm-up failed


@dataclass(frozen=True)
class LoadResult:
    """
    Result of a model loading operation.
    
    Contains all metadata about the loaded model.
    """
    
    model_id: str               # Loaded model ID
    version: str                # Model version
    runtime_name: str           # Runtime used for loading
    
    # Loading metrics
    load_time_ms: float         # Time taken to load
    memory_bytes: int           # Memory allocated
    
    # Verification
    verified: bool = True       # Whether model was verified
    verification_errors: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Check if loading succeeded."""
        return self.verified and len(self.verification_errors) == 0


@dataclass(frozen=True)
class UnloadResult:
    """
    Result of a model unloading operation.
    
    Contains all metadata about the unload operation.
    """
    
    model_id: str               # Unloaded model ID
    version: str                # Model version
    
    # Unloading metrics
    unload_time_ms: float       # Time taken to unload
    memory_freed_bytes: int     # Memory released
    
    cleanup_errors: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Check if unloading succeeded."""
        return len(self.cleanup_errors) == 0


# =============================================================================
# LOADING ERRORS
# =============================================================================


class ModelError(Exception):
    """Base exception for model errors."""
    
    def __init__(self, message: str, model_id: Optional[str] = None):
        super().__init__(message)
        self.model_id = model_id


class UnsupportedModelError(ModelError):
    """Raised when model is not supported by any runtime."""
    
    pass


class RuntimeNotAvailableError(ModelError):
    """Raised when required runtime is unavailable."""
    
    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        required_runtime: Optional[str] = None,
    ):
        super().__init__(message, model_id)
        self.required_runtime = required_runtime


class LoadTimeoutError(ModelError):
    """Raised when loading times out."""
    
    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        timeout_ms: int = 0,
    ):
        super().__init__(message, model_id)
        self.timeout_ms = timeout_ms


class OutOfMemoryError(ModelError):
    """Raised when loading fails due to insufficient memory."""
    
    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        required_bytes: int = 0,
        available_bytes: int = 0,
    ):
        super().__init__(message, model_id)
        self.required_bytes = required_bytes
        self.available_bytes = available_bytes


# =============================================================================
# MODEL LOADER
# =============================================================================


class ModelLoader:
    """
    Canonical model loading authority.
    
    This is the SINGLE canonical authority for model loading in Gordon.
    
    Responsibilities:
        - Load models deterministically from storage
        - Validate runtime compatibility
        - Handle warm-up and health verification
        - Unload models cleanly
    
    Does NOT:
        - Own model registry (uses ModelRegistry)
        - Execute inference
        - Manage compute resources directly
    
    Architecture Invariants:
        - Exactly ONE loader instance exists
        - Loading is deterministic (same inputs = same outputs)
        - No implicit loading during import
    """
    
    def __init__(
        self,
        default_timeout_ms: int = 60000,  # 60 seconds
        warmup_enabled: bool = True,
    ):
        """
        Initialize the model loader.
        
        Args:
            default_timeout_ms: Default load timeout in milliseconds
            warmup_enabled: Whether to perform warm-up after loading
        """
        self._default_timeout_ms = default_timeout_ms
        self._warmup_enabled = warmup_enabled
        
        # Current loads (model_id -> LoadResult)
        self._loaded_models: Dict[str, LoadResult] = {}
        
        # Loading state machine
        self._loading_state: Dict[str, LoadingState] = {}
        
        # Statistics
        self._total_loaded = 0
        self._total_unloaded = 0
        self._total_failed_loads = 0
        
        self._lock = __import__("threading").Lock()
    
    @property
    def loaded_count(self) -> int:
        """Return number of currently loaded models."""
        with self._lock:
            return len(self._loaded_models)
    
    # -------------------------------------------------------------------------
    # Loading (deterministic)
    # -------------------------------------------------------------------------
    
    def load(
        self,
        model_id: str,
        version: str,
        runtime_name: str,
        weights_path: str,
        tokenizer_path: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> LoadResult:
        """
        Load a model into memory.
        
        Args:
            model_id: Model identifier
            version: Model version
            runtime_name: Runtime to use (llama.cpp, vLLM, etc.)
            weights_path: Path to model weights
            tokenizer_path: Optional path to tokenizer files
            timeout_ms: Optional override for load timeout
            
        Returns:
            LoadResult with loading metadata
            
        Raises:
            UnsupportedModelError: If runtime incompatible with model
            RuntimeNotAvailableError: If runtime is unavailable
            LoadTimeoutError: If loading times out
            OutOfMemoryError: If insufficient memory
        """
        timeout_ms = timeout_ms or self._default_timeout_ms
        
        # Determine loading start time
        load_start = time.time()
        
        try:
            # Step 1: Validate model exists and is compatible
            compatibility_result = self._validate_compatibility(
                model_id=model_id,
                version=version,
                runtime_name=runtime_name,
            )
            
            if not compatibility_result["compatible"]:
                raise UnsupportedModelError(
                    f"Model '{model_id}' not compatible with runtime '{runtime_name}'",
                    model_id=model_id,
                ) from compatibility_result.get("error")
            
            # Step 2: Check memory requirements
            required_memory = self._estimate_memory_requirement(model_id, version)
            if not self._check_memory_available(required_memory):
                raise OutOfMemoryError(
                    f"Insufficient memory to load '{model_id}'",
                    model_id=model_id,
                    required_bytes=required_memory,
                    available_bytes=self._get_available_memory(),
                )
            
            # Step 3: Perform loading (simulated)
            self._simulate_loading(model_id, runtime_name, weights_path)
            
            # Calculate load time
            load_time_ms = (time.time() - load_start) * 1000
            
            # Step 4: Optionally warm-up the model
            verification_errors = []
            if self._warmup_enabled:
                try:
                    self._perform_warmup(model_id, runtime_name)
                except Exception as e:
                    verification_errors.append(str(e))
            
            result = LoadResult(
                model_id=model_id,
                version=version,
                runtime_name=runtime_name,
                load_time_ms=load_time_ms,
                memory_bytes=required_memory,
                verified=len(verification_errors) == 0,
                verification_errors=verification_errors,
            )
            
            with self._lock:
                self._loaded_models[model_id] = result
                self._loading_state[model_id] = LoadingState.READY if result.success else LoadingState.FAILED_WARMUP
            
            return result
            
        except OutOfMemoryError:
            raise
        except Exception as e:
            with self._lock:
                self._loading_state[model_id] = LoadingState.FAILED_LOAD
                self._total_failed_loads += 1
            
            if isinstance(e, LoadTimeoutError):
                raise
            
            raise ModelError(
                f"Failed to load model '{model_id}': {e}",
                model_id=model_id,
            ) from e
    
    def _validate_compatibility(
        self,
        model_id: str,
        version: str,
        runtime_name: str,
    ) -> Dict[str, Any]:
        """
        Validate that runtime is compatible with model.
        
        Returns:
            Dict with 'compatible' flag and optional 'error'
        """
        # In production, this would query the ModelRegistry
        return {"compatible": True}
    
    def _estimate_memory_requirement(
        self,
        model_id: str,
        version: str,
    ) -> int:
        """Estimate memory requirements for a model."""
        # Base estimate (in production, would read from registry)
        base_bytes = 512 * 1024 * 1024  # 512 MB base
        
        # Add model-specific adjustments
        if "llama" in model_id.lower():
            return base_bytes + 256 * 1024 * 1024  # +256MB for Llama models
        
        return base_bytes
    
    def _check_memory_available(self, required: int) -> bool:
        """Check if sufficient memory is available."""
        # In production, would check actual system memory
        return True
    
    def _get_available_memory(self) -> int:
        """Get available memory in bytes."""
        # In production, would query system memory
        return 16 * 1024 * 1024 * 1024  # 16 GB estimate
    
    def _simulate_loading(
        self,
        model_id: str,
        runtime_name: str,
        weights_path: str,
    ) -> None:
        """Simulate the loading process."""
        # In production, this would:
        # 1. Load weights from storage
        # 2. Initialize runtime context
        # 3. Configure tokenizer
        pass
    
    def _perform_warmup(
        self,
        model_id: str,
        runtime_name: str,
    ) -> None:
        """Perform warm-up inference."""
        # In production, would run a minimal inference to pre-warm caches
        pass
    
    # -------------------------------------------------------------------------
    # Unloading (deterministic)
    # -------------------------------------------------------------------------
    
    def unload(
        self,
        model_id: str,
        timeout_ms: Optional[int] = None,
    ) -> UnloadResult:
        """
        Unload a model from memory.
        
        Args:
            model_id: Model to unload
            timeout_ms: Optional override for unload timeout
            
        Returns:
            UnloadResult with unloading metadata
        """
        timeout_ms = timeout_ms or self._default_timeout_ms
        
        unload_start = time.time()
        
        try:
            # Step 1: Verify model is loaded
            if model_id not in self._loaded_models:
                return UnloadResult(
                    model_id=model_id,
                    version="",
                    unload_time_ms=(time.time() - unload_start) * 1000,
                    memory_freed_bytes=0,
                )
            
            # Step 2: Get memory to free
            load_result = self._loaded_models.pop(model_id)
            memory_to_free = load_result.memory_bytes
            
            # Step 3: Clean up (simulated)
            self._cleanup_model_resources(model_id)
            
            unload_time_ms = (time.time() - unload_start) * 1000
            
            result = UnloadResult(
                model_id=model_id,
                version=load_result.version,
                unload_time_ms=unload_time_ms,
                memory_freed_bytes=memory_to_free,
            )
            
            with self._lock:
                if model_id in self._loading_state:
                    del self._loading_state[model_id]
            
            return result
            
        except Exception as e:
            return UnloadResult(
                model_id=model_id,
                version="",
                unload_time_ms=(time.time() - unload_start) * 1000,
                memory_freed_bytes=0,
                cleanup_errors=[str(e)],
            )
    
    def _cleanup_model_resources(self, model_id: str) -> None:
        """Clean up resources associated with a model."""
        # In production, would:
        # 1. Release runtime context
        # 2. Free VRAM/RAM
        # 3. Close file handles
        pass
    
    def unload_all(self) -> List[UnloadResult]:
        """
        Unload all currently loaded models.
        
        Returns:
            List of unloading results for each model
        """
        with self._lock:
            return [
                self.unload(model_id)
                for model_id in list(self._loaded_models.keys())
            ]
    
    # -------------------------------------------------------------------------
    # Status queries
    # -------------------------------------------------------------------------
    
    def get_loading_state(self, model_id: str) -> LoadingState:
        """Get the loading state of a model."""
        with self._lock:
            return self._loading_state.get(
                model_id,
                LoadingState.NOT_REGISTERED
            )
    
    def is_loaded(self, model_id: str) -> bool:
        """Check if a model is currently loaded and ready."""
        with self._lock:
            return model_id in self._loaded_models
    
    def get_load_result(self, model_id: str) -> Optional[LoadResult]:
        """Get the load result for a loaded model."""
        with self._lock:
            return self._loaded_models.get(model_id)
    
    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get loader statistics.
        
        Returns:
            Dictionary of loader metrics
        """
        with self._lock:
            return {
                "loaded_count": len(self._loaded_models),
                "total_loaded": self._total_loaded,
                "total_unloaded": self._total_unloaded,
                "total_failed_loads": self._total_failed_loads,
            }


__all__ = [
    # Enums
    "LoadingState",
    # Dataclasses
    "LoadResult",
    "UnloadResult",
    # Exceptions
    "ModelError",
    "UnsupportedModelError",
    "RuntimeNotAvailableError",
    "LoadTimeoutError",
    "OutOfMemoryError",
    # Loader
    "ModelLoader",
]