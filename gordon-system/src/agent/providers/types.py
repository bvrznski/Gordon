# Provider Types - Data Models
# =============================
"""
Provider type definitions used throughout the provider layer.

These are Gordon-owned types that providers use to communicate with each other.
"""

from dataclasses import dataclass, field
from typing import Protocol, Any, Optional, Dict, List
from enum import Enum
import abc


class ProviderKind(Enum):
    """Categories of external capability providers."""
    
    # Language models
    LLM = "llm"
    VLM = "vlm"
    
    # Embeddings
    EMBEDDINGS = "embeddings"
    
    # Perception
    OCR = "ocr"
    ASR = "asr"  # Speech recognition
    TTS = "tts"  # Speech synthesis
    
    # Vision
    IMAGE_GEN = "image_gen"
    DETECTION = "detection"
    SEGMENTATION = "segmentation"
    
    # World models
    WORLD_MODEL = "world_model"
    
    # Reranking
    RERANKING = "reranking"
    
    # External services
    REMOTE_API = "remote_api"
    
    # Local runtimes
    LOCAL_RUNTIME = "local_runtime"


class ProviderStatus(Enum):
    """
    Provider lifecycle and health status.
    
    These states represent the provider's operational state independent of
    any specific capability request.
    """
    UNINITIALIZED = "uninitialized"  # Created but not configured
    CONFIGURED = "configured"        # Configuration applied, ready to init
    INITIALIZING = "initializing"    # Setting up resources
    READY = "ready"                  # Initialized and available
    STARTING = "starting"            # Starting connections/threads
    RUNNING = "running"              # Fully operational
    DEGRADED = "degraded"            # Operational with reduced capacity
    STOPPING = "stopping"            # Shutting down gracefully
    STOPPED = "stopped"              # Fully stopped
    FAILED = "failed"                # In unrecoverable error state


@dataclass(frozen=True)
class ProviderIdentity:
    """
    Unique identifier and metadata for a provider instance.
    
    Provider identity is distinct from model identity:
    - provider_id: The adapter instance (e.g., "openai-client-1")
    - model_id: The specific model loaded by that provider (e.g., "gpt-4-turbo")
    """
    provider_id: str
    kind: ProviderKind
    version: str = "1.0.0"
    deployment_id: Optional[str] = None  # For tracking deployments
    model_id: Optional[str] = None       # For models with embedded identity


@dataclass(frozen=True)
class CapabilityDeclaration:
    """
    Declared capabilities of a provider.
    
    This is an explicit contract - providers must not advertise capabilities
    they don't actually support.
    """
    # Core capabilities
    supports_chat_completion: bool = False
    supports_text_generation: bool = False
    supports_embeddings: bool = False
    
    # Multimodal capabilities
    supports_vision: bool = False       # Image + text input
    supports_audio_input: bool = False  # Audio for ASR
    supports_audio_output: bool = False # Audio output for TTS
    supports_image_gen: bool = False    # Text-to-image
    
    # Perception capabilities
    supports_ocr: bool = False
    supports_detection: bool = False
    supports_segmentation: bool = False
    
    # Specialized capabilities
    supports_streaming: bool = False
    supports_tool_calling: bool = False
    supports_structured_output: bool = False
    supports_reranking: bool = False
    
    # Context limits (maximum token count where applicable)
    max_context_tokens: Optional[int] = None


@dataclass(frozen=True)
class ProviderConfig:
    """
    Base configuration for all providers.
    
    This is the minimal configuration that applies to all provider kinds.
    Additional kind-specific configuration extends this base class.
    """
    provider_id: str
    enabled: bool = True
    
    # Resource constraints
    max_concurrent_requests: int = 10
    timeout_seconds: float = 30.0
    
    # Retry policy (provider-local, not global)
    max_retries: int = 3
    retry_backoff_base_seconds: float = 0.5
    
    # Health checks
    health_check_interval_seconds: float = 60.0


class Provider(Protocol):
    """
    Protocol for all provider implementations.
    
    Every provider must implement these core lifecycle and diagnostic methods.
    Capability-specific operations (inference, embeddings, etc.) are defined
    in capability protocols that extend this base protocol.
    """
    
    @property
    def identity(self) -> ProviderIdentity:
        """Return provider identity."""
        ...
    
    @property
    def config(self) -> ProviderConfig:
        """Return provider configuration."""
        ...
    
    @property
    def status(self) -> ProviderStatus:
        """Return current provider status."""
        ...
    
    async def initialize(self, config: Optional[ProviderConfig] = None) -> None:
        """
        Initialize the provider.
        
        Transitions from UNINITIALIZED/CONFIGURED to INITIALIZING.
        Sets up resources but does not start accepting requests yet.
        """
        ...
    
    async def start(self) -> None:
        """
        Start the provider.
        
        Transitions from INITIALIZING to STARTING, then RUNNING.
        Begins accepting and processing requests.
        """
        ...
    
    async def stop(self) -> None:
        """
        Stop the provider gracefully.
        
        Transitions from RUNNING to STOPPING, then STOPPED.
        Completes in-flight requests before shutting down.
        """
        ...
    
    async def shutdown(self) -> None:
        """
        Shutdown the provider permanently.
        
        Forces termination of all operations and releases resources.
        May be called from any state.
        """
        ...
    
    async def health(self) -> Dict[str, Any]:
        """
        Return current health status.
        
        Returns a dictionary with health information including:
        - status: overall health (healthy, degraded, unhealthy)
        - ready: whether the provider can accept requests
        - details: provider-specific health indicators
        
        Raises:
            ProviderNotReadyError: If provider is not ready
            ProviderUnavailableError: If provider is unavailable
        """
        ...
    
    async def get_capabilities(self) -> CapabilityDeclaration:
        """Return declared capabilities of this provider."""
        ...


__all__ = [
    # Enums
    "ProviderKind",
    "ProviderStatus",
    
    # Data classes
    "ProviderIdentity",
    "CapabilityDeclaration",
    "ProviderConfig",
    
    # Protocols
    "Provider",
]