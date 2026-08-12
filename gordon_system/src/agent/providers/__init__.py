# Provider Layer - External Capability Abstraction
# ==================================================
"""
Provider Layer: External capability abstraction for Gordon.

The Provider Layer provides stable, vendor-neutral interfaces to external
capabilities including:
- Language models (LLM)
- Vision-language models (VLM)
- Embedding models
- OCR engines
- Speech recognition (ASR)
- Speech synthesis (TTS)
- Object detection and segmentation
- World models
- External APIs and services

Provider Responsibilities:
- Encapsulate vendor-specific SDKs and transports
- Normalize requests to Gordon-owned types
- Normalize responses to Gordon-owned result types
- Manage provider lifecycle (init, start, stop, shutdown)
- Report health status
- Own resource management (GPU memory, connections, etc.)
- Translate failures into Gordon-owned failure taxonomy

Provider Non-Responsibilities:
- Cognition or reasoning
- Goal setting or planning
- Memory semantics
- Perception interpretation
- Prompt strategy
- Task routing (that belongs to capability-facing layers)
"""

# Re-export core types for convenience
from ..components.core.types import EntityId, Timestamp
from ..components.core.contracts import LifecycleEntity

# Import main provider types and protocols from submodule
from .types import (
    ProviderKind,
    ProviderStatus,
    ProviderIdentity,
    CapabilityDeclaration,
    ProviderConfig,
    Provider,
)

# Import capability protocols
from .capabilities import (
    MessageRole,
    ChatMessage,
    ToolCall,
    ToolFunction,
    ChatCompletionRequest,
    ToolDefinition,
    ToolFunctionDefinition,
    ChatCompletionChoice,
    ChatCompletionUsage,
    ChatCompletionResponse,
    ChatCompletionProvider,
    validate_chat_request,
)

# Re-export exceptions for convenience
from .exceptions import (
    ProviderError,
    ProviderConfigError,
    ProviderAuthenticationError,
    ProviderNotReadyError,
    ProviderUnavailableError,
    ProviderTimeoutError,
    ProviderResourceError,
    ProviderCapabilityError,
    ProviderRequestError,
    ProviderResponseError,
    ProviderRateLimitError,
    ProviderInternalError,
    classify_error,
)

# Re-export registry
from .registry import (
    RegistrationSource,
    ProviderRegistration,
    CapabilityQuery,
    ProviderRegistry,
    get_global_registry,
    clear_global_registry,
)

# Re-export routing module
from .routing import (
    ProviderRouter,
    RoutingResult,
    RoutingConfig,
    RoutingDecision,
    RoutingPolicy,
    CircuitBreaker,
    RateLimiter,
    ProviderPriority,
)

# Re-export streaming module
from .streaming import (
    StreamState,
    StreamOptions,
    CancellationToken,
    StreamContext,
    BackpressureController,
    StreamTimeoutManager,
    StreamEnvelope,
    StreamCancelledError,
    StreamTimeoutError,
    ManagedStream,
    StreamPool,
)

__all__ = [
    # Enums
    "ProviderKind",
    "ProviderStatus",
    "RegistrationSource",
    
    # Data classes
    "ProviderIdentity",
    "CapabilityDeclaration",
    "ProviderConfig",
    "ProviderRegistration",
    "CapabilityQuery",
    
    # Protocols
    "Provider",
    
    # Exceptions
    "ProviderError",
    "ProviderConfigError",
    "ProviderAuthenticationError",
    "ProviderNotReadyError",
    "ProviderUnavailableError",
    "ProviderTimeoutError",
    "ProviderResourceError",
    "ProviderCapabilityError",
    "ProviderRequestError",
    "ProviderResponseError",
    "ProviderRateLimitError",
    "ProviderInternalError",
    "classify_error",
    
    # Registry
    "ProviderRegistry",
    "get_global_registry",
    "clear_global_registry",
    
    # Routing
    "ProviderRouter",
    "RoutingResult",
    "RoutingConfig",
    "RoutingDecision",
    "RoutingPolicy",
    "CircuitBreaker",
    "RateLimiter",
    "ProviderPriority",
    
    # Streaming
    "StreamState",
    "StreamOptions",
    "CancellationToken",
    "StreamContext",
    "BackpressureController",
    "StreamTimeoutManager",
    "StreamEnvelope",
    "StreamCancelledError",
    "StreamTimeoutError",
    "ManagedStream",
    "StreamPool",
    
    # Capability protocols
    "MessageRole",
    "ChatMessage",
    "ToolCall",
    "ToolFunction",
    "ChatCompletionRequest",
    "ToolDefinition",
    "ToolFunctionDefinition",
    "ChatCompletionChoice",
    "ChatCompletionUsage",
    "ChatCompletionResponse",
    "ChatCompletionProvider",
    "validate_chat_request",
]
