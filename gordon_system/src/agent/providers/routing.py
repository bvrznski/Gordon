# Provider Routing - Capability-Based Selection and Distribution
# ================================================================
"""
Provider routing for dynamic selection and distribution of capability requests.

This module provides:
- ProviderRouter: Route capability requests to appropriate providers
- CircuitBreaker: Prevent cascading failures from unhealthy providers
- RateLimiter: Enforce per-provider request limits
- RoutingPolicy: Define provider selection rules

Key Design Decisions:
- Routing is capability-aware, not model-aware
- Failures are classified for intelligent fallback
- Circuits open only after repeated consecutive failures
- Rate limiting is per-provider, not global
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum
import time
import asyncio
import uuid

from .types import ProviderKind, ProviderStatus, CapabilityDeclaration, ProviderIdentity
from .exceptions import (
    ProviderNotReadyError,
    ProviderUnavailableError,
    ProviderTimeoutError,
    ProviderRateLimitError,
)


class RoutingState(Enum):
    """State of the circuit breaker."""
    CLOSED = "closed"      # Requests pass through
    OPENING = "opening"    # In grace period before opening
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if provider recovered


@dataclass(frozen=True)
class RoutingResult:
    """
    Result of a routing decision.
    
    Args:
        provider_id: The selected provider's ID (or None if no match)
        provider_kind: The kind of the selected provider
        score: Confidence score for this selection (0.0-1.0)
        reason: Human-readable explanation for the selection
    """
    provider_id: Optional[str]
    provider_kind: Optional[str]
    score: float = 0.0
    reason: str = "no match"


@dataclass(frozen=True)
class RoutingConfig:
    """
    Configuration for provider routing.
    
    Args:
        default_timeout_seconds: Default timeout for routed requests
        circuit_breaker_threshold: Failures before circuit opens
        circuit_breaker_recovery_seconds: Time before half-open attempt
        rate_limit_per_provider: Max concurrent requests per provider
    """
    default_timeout_seconds: float = 30.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_recovery_seconds: float = 60.0
    rate_limit_per_provider: int = 10


@dataclass(frozen=True)
class RoutingDecision:
    """
    Decision made by the router for a specific request.
    
    Args:
        provider_id: Selected provider ID
        routed_at: Timestamp of routing decision
        capacity_used: Current concurrent requests for this provider
        circuit_state: State of the circuit breaker
    """
    provider_id: str
    routed_at: float
    capacity_used: int
    circuit_state: RoutingState


class CircuitBreaker:
    """
    Circuit breaker for provider failures.
    
    Prevents cascading failures by temporarily stopping requests to 
    failing providers. Automatically retries after a recovery period.
    
    States:
        CLOSED: Normal operation, requests pass through
        OPENING: In grace period (counting consecutive failures)
        OPEN: Circuit is open, requests fail fast with short-circuit
        HALF_OPEN: Testing if provider recovered
    """
    
    def __init__(
        self,
        threshold: int = 5,
        recovery_seconds: float = 60.0,
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            threshold: Number of consecutive failures before opening
            recovery_seconds: Time in half_open state before closing
        """
        self._threshold = threshold
        self._recovery_seconds = recovery_seconds
        
        # Internal state
        self._state: RoutingState = RoutingState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_start: Optional[float] = None
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> RoutingState:
        """Get current circuit state."""
        return self._state
    
    async def record_success(self) -> None:
        """
        Record a successful request.
        
        Resets failure count and may close the circuit.
        """
        async with self._lock:
            if self._state in (RoutingState.OPENING, RoutingState.HALF_OPEN):
                # Recovery successful
                self._state = RoutingState.CLOSED
                self._failure_count = 0
            elif self._state == RoutingState.OPEN:
                # Transition to half_open for testing
                self._half_open_start = time.monotonic()
                self._state = RoutingState.HALF_OPEN
    
    async def record_failure(self) -> None:
        """
        Record a failed request.
        
        May transition to OPEN state if threshold exceeded.
        """
        async with self._lock:
            now = time.monotonic()
            
            if self._state == RoutingState.OPEN:
                # Check if recovery period has passed
                if (self._last_failure_time is None or 
                    now - self._last_failure_time >= self._recovery_seconds):
                    # Start half_open state for testing
                    self._half_open_start = now
                    self._state = RoutingState.HALF_OPEN
                    return
            
            self._failure_count += 1
            self._last_failure_time = now
            
            if self._state == RoutingState.CLOSED:
                if self._failure_count >= self._threshold:
                    self._state = RoutingState.OPENING
    
    async def can_request(self) -> bool:
        """
        Check if a request can proceed.
        
        Returns:
            True if request should be attempted, False if short-circuited
        """
        async with self._lock:
            if self._state == RoutingState.CLOSED:
                return True
            
            if self._state == RoutingState.OPENING:
                # Still in grace period, fail fast
                return False
            
            if self._state == RoutingState.HALF_OPEN:
                # Check recovery time
                if (self._half_open_start is not None and 
                    time.monotonic() - self._half_open_start >= self._recovery_seconds):
                    # Recovery complete, try request
                    return True
                return False
            
            # OPEN state
            if self._last_failure_time is not None:
                elapsed = time.monotonic() - self._last_failure_time
                if elapsed >= self._recovery_seconds:
                    # Start testing recovery
                    self._half_open_start = time.monotonic()
                    self._state = RoutingState.HALF_OPEN
                    return True
            
            return False
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get detailed state information."""
        async def _get():
            return {
                "state": self._state.value,
                "failure_count": self._failure_count,
                "threshold": self._threshold,
                "last_failure_time": self._last_failure_time,
            }
        
        # For sync access, return defaults
        return {
            "state": self._state.value,
            "failure_count": self._failure_count,
            "threshold": self._threshold,
        }


class RateLimiter:
    """
    Per-provider rate limiter.
    
    Enforces concurrent request limits per provider to prevent
    overwhelming providers with too many simultaneous requests.
    """
    
    def __init__(self, max_concurrent: int = 10):
        """
        Initialize the rate limiter.
        
        Args:
            max_concurrent: Maximum concurrent requests allowed
        """
        self._max_concurrent = max_concurrent
        self._current_count = 0
        self._lock = asyncio.Lock()
    
    @property
    def current_usage(self) -> int:
        """Get current concurrent request count."""
        return self._current_count
    
    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission for a request.
        
        Args:
            timeout: Maximum time to wait for capacity
            
        Returns:
            True if acquired, False if would block (timeout exceeded)
        """
        start_time = time.monotonic()
        
        while True:
            async with self._lock:
                if self._current_count < self._max_concurrent:
                    self._current_count += 1
                    return True
            
            # Check timeout
            elapsed = time.monotonic() - start_time
            if timeout is not None and elapsed >= timeout:
                return False
            
            # Brief wait before retry
            await asyncio.sleep(0.01)
    
    async def release(self) -> None:
        """Release a request slot."""
        async with self._lock:
            if self._current_count > 0:
                self._current_count -= 1
    
    async def __aenter__(self) -> "RateLimiter":
        """Async context manager entry."""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.release()


@dataclass(frozen=True)
class RoutingPolicy:
    """
    Policy for routing decisions.
    
    Args:
        name: Policy identifier
        description: Human-readable policy description
        weight: Priority weight (higher = more preferred)
        constraints: List of constraint callables
        fallback_policy: What to do when no provider matches
    """
    name: str = "default"
    description: Optional[str] = None
    weight: int = 100
    constraints: List[Callable[['ProviderRegistrationInfo'], bool]] = field(default_factory=list)
    fallback_policy: str = "raise_error"


@dataclass(frozen=True)
class ProviderPriority:
    """
    Priority assignment for a provider.
    
    Args:
        provider_id: The provider being prioritized
        priority: Numeric priority (higher = more preferred)
        reason: Human-readable explanation
    """
    provider_id: str
    priority: int = 0
    reason: str = "default"


class ProviderRouter:
    """
    Router for distributing capability requests to appropriate providers.
    
    Features:
    - Capability-based routing (not model-specific)
    - Circuit breaker integration per provider
    - Rate limiting per provider
    - Priority-based selection
    - Health-aware distribution
    
    Usage:
        router = ProviderRouter()
        
        # Add providers with their priorities
        router.add_provider("openai-gpt4", ProviderKind.LLM, priority=10)
        router.add_provider("anthropic-claude", ProviderKind.LLM, priority=5)
        
        # Route a request
        result = await router.route("chat_completion")
    """
    
    def __init__(
        self,
        config: Optional[RoutingConfig] = None,
    ):
        """
        Initialize the provider router.
        
        Args:
            config: Routing configuration (uses defaults if not provided)
        """
        self._config = config or RoutingConfig()
        self._registrations: Dict[str, ProviderRegistrationInfo] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._rate_limiters: Dict[str, RateLimiter] = {}
        self._lock = asyncio.Lock()
    
    def add_provider(
        self,
        provider_id: str,
        kind: ProviderKind,
        capabilities: CapabilityDeclaration,
        priority: int = 0,
        health_score: float = 1.0,
    ) -> None:
        """
        Add a provider to the router.
        
        Args:
            provider_id: Unique identifier for the provider
            kind: Provider kind (LLM, VLM, etc.)
            capabilities: Declared capabilities
            priority: Selection priority (higher = more preferred)
            health_score: Current health score (0.0-1.0)
        """
        async def _add():
            async with self._lock:
                info = ProviderRegistrationInfo(
                    provider_id=provider_id,
                    kind=kind,
                    capabilities=capabilities,
                    priority=priority,
                    health_score=health_score,
                    registered_at=time.monotonic(),
                )
                self._registrations[provider_id] = info
                
                # Initialize circuit breaker and rate limiter
                self._circuit_breakers[provider_id] = CircuitBreaker(
                    threshold=self._config.circuit_breaker_threshold,
                    recovery_seconds=self._config.circuit_breaker_recovery_seconds,
                )
                self._rate_limiters[provider_id] = RateLimiter(
                    max_concurrent=self._config.rate_limit_per_provider,
                )
        
        # Run async init synchronously
        asyncio.get_event_loop().run_until_complete(_add())
    
    def remove_provider(self, provider_id: str) -> bool:
        """Remove a provider from the router."""
        try:
            del self._registrations[provider_id]
            del self._circuit_breakers[provider_id]
            del self._rate_limiters[provider_id]
            return True
        except KeyError:
            return False
    
    def update_health(self, provider_id: str, health_score: float) -> None:
        """Update a provider's health score."""
        if provider_id in self._registrations:
            info = self._registrations[provider_id]
            self._registrations[provider_id] = ProviderRegistrationInfo(
                **{**info.__dict__, "health_score": health_score}
            )
    
    async def route(self, capability: str) -> RoutingResult:
        """
        Route a request to an appropriate provider.
        
        Args:
            capability: The required capability (e.g., "chat_completion")
            
        Returns:
            RoutingResult with selected provider or None
        """
        async with self._lock:
            # Find candidates supporting this capability
            candidates = []
            
            for provider_id, info in self._registrations.items():
                if not _capability_supported(info.capabilities, capability):
                    continue
                
                cb = self._circuit_breakers.get(provider_id)
                if cb is None:
                    continue
                
                # Check circuit breaker state
                if not await cb.can_request():
                    continue
                
                # Check health score (filter out very unhealthy providers)
                if info.health_score < 0.3:
                    continue
                
                candidates.append((provider_id, info))
            
            if not candidates:
                return RoutingResult(
                    provider_id=None,
                    provider_kind=None,
                    score=0.0,
                    reason="no compatible providers available",
                )
            
            # Sort by priority (descending) then health score (descending)
            candidates.sort(key=lambda x: (-x[1].priority, -x[1].health_score))
            
            # Select the best candidate
            selected_id, selected_info = candidates[0]
            
            return RoutingResult(
                provider_id=selected_id,
                provider_kind=selected_info.kind.value,
                score=min(1.0, selected_info.health_score + (selected_info.priority / 100)),
                reason=f"selected by priority and health",
            )
    
    async def execute_with_routing(
        self,
        capability: str,
        request_fn: Callable[[str], Any],
    ) -> Any:
        """
        Execute a function with automatic provider routing.
        
        Args:
            capability: The required capability
            request_fn: Function that takes provider_id and executes request
            
        Returns:
            Result from the executed function
            
        Raises:
            ProviderNotReadyError: If no suitable provider is available
            ProviderUnavailableError: If all providers are circuit-broken
        """
        result = await self.route(capability)
        
        if result.provider_id is None:
            raise ProviderNotReadyError(
                message=f"No provider supports capability '{capability}'",
                operation="routing",
                retryable=True,
            )
        
        # Execute with rate limiting and circuit breaker tracking
        provider_id = result.provider_id
        
        limiter = self._rate_limiters.get(provider_id)
        cb = self._circuit_breakers.get(provider_id)
        
        if limiter is None or cb is None:
            raise ProviderNotReadyError(
                message=f"Provider '{provider_id}' not registered",
                operation="routing",
                retryable=False,
            )
        
        try:
            async with limiter:
                try:
                    result = await request_fn(provider_id)
                    await cb.record_success()
                    return result
                except (ProviderTimeoutError, ProviderUnavailableError) as e:
                    await cb.record_failure()
                    raise
        except ProviderUnavailableError as e:
            raise ProviderUnavailableError(
                message=f"Failed to route request: {e.message}",
                operation="routing",
                retryable=True,
            )
    
    def get_provider_state(self, provider_id: str) -> Dict[str, Any]:
        """Get current state for a provider."""
        info = self._registrations.get(provider_id)
        cb = self._circuit_breakers.get(provider_id)
        
        return {
            "provider_id": provider_id,
            "kind": info.kind.value if info else None,
            "priority": info.priority if info else 0,
            "health_score": info.health_score if info else 0.0,
            "circuit_state": cb.state.value if cb else "unknown",
        }
    
    def get_all_providers(self) -> List[Dict[str, Any]]:
        """Get all registered providers with their states."""
        return [
            self.get_provider_state(pid)
            for pid in self._registrations.keys()
        ]
    
    @classmethod
    def create(cls, registry: "ProviderRegistry") -> "ProviderRouter":
        """
        Create a router from an existing provider registry.
        
        Args:
            registry: The provider registry to use
            
        Returns:
            Initialized ProviderRouter
        """
        import asyncio
        from .registry import ProviderRegistry as RegType
        
        router = cls()
        
        async def _init():
            registrations = registry.get_all_registrations()
            
            for provider_id, reg in registrations.items():
                capabilities = CapabilityDeclaration(
                    supports_chat_completion=reg.capabilities.supports_chat_completion,
                    supports_text_generation=reg.capabilities.supports_text_generation,
                    supports_embeddings=reg.capabilities.supports_embeddings,
                    supports_vision=reg.capabilities.supports_vision,
                    supports_audio_input=reg.capabilities.supports_audio_input,
                    supports_audio_output=reg.capabilities.supports_audio_output,
                    supports_image_gen=reg.capabilities.supports_image_gen,
                    supports_ocr=reg.capabilities.supports_ocr,
                    supports_detection=reg.capabilities.supports_detection,
                    supports_segmentation=reg.capabilities.supports_segmentation,
                    supports_streaming=reg.capabilities.supports_streaming,
                    supports_tool_calling=reg.capabilities.supports_tool_calling,
                    supports_structured_output=reg.capabilities.supports_structured_output,
                    supports_reranking=reg.capabilities.supports_reranking,
                )
                
                router.add_provider(
                    provider_id=provider_id,
                    kind=ProviderKind(reg.kind) if reg.kind in [k.value for k in ProviderKind] else ProviderKind.REMOTE_API,
                    capabilities=capabilities,
                    priority=0,  # Default priority
                    health_score=1.0 if reg.status == ProviderStatus.RUNNING else 0.5,
                )
        
        asyncio.get_event_loop().run_until_complete(_init())
        return router
    
    def __len__(self) -> int:
        """Return number of registered providers."""
        return len(self._registrations)
    
    def __contains__(self, provider_id: str) -> bool:
        """Check if a provider is registered."""
        return provider_id in self._registrations


@dataclass(frozen=True)
class ProviderRegistrationInfo:
    """
    Internal info for a registered provider.
    
    Args:
        provider_id: Unique identifier
        kind: Provider kind
        capabilities: Declared capabilities
        priority: Selection priority
        health_score: Current health (0.0-1.0)
        registered_at: When this was registered
    """
    provider_id: str
    kind: ProviderKind
    capabilities: CapabilityDeclaration
    priority: int = 0
    health_score: float = 1.0
    registered_at: float = field(default_factory=time.monotonic)


def _capability_supported(capabilities: CapabilityDeclaration, capability: str) -> bool:
    """Check if a capability is supported."""
    support_map = {
        "chat_completion": capabilities.supports_chat_completion,
        "text_generation": capabilities.supports_text_generation,
        "embeddings": capabilities.supports_embeddings,
        "vision": capabilities.supports_vision,
        "asr": capabilities.supports_audio_input,
        "tts": capabilities.supports_audio_output,
        "image_gen": capabilities.supports_image_gen,
        "ocr": capabilities.supports_ocr,
        "detection": capabilities.supports_detection,
        "segmentation": capabilities.supports_segmentation,
        "streaming": capabilities.supports_streaming,
        "tool_calling": capabilities.supports_tool_calling,
        "structured_output": capabilities.supports_structured_output,
        "reranking": capabilities.supports_reranking,
    }
    
    return support_map.get(capability, False)


__all__ = [
    # State
    "RoutingState",
    
    # Data classes
    "RoutingResult",
    "RoutingConfig",
    "RoutingDecision",
    "RoutingPolicy",
    "ProviderPriority",
    
    # Classes
    "CircuitBreaker",
    "RateLimiter",
    "ProviderRouter",
]