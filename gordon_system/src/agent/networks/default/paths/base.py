# Default Network Path Abstraction Base
# ======================================

"""
Path handler protocol and core types for the Default Network.

This module defines:
    - DefaultNetworkPathHandler: Protocol for runtime-neutral path handlers
    - DefaultNetworkPathContext: Immutable context passed to handlers
    - DefaultNetworkPathResult: Immutable result produced by handlers

All contracts are deeply immutable to ensure deterministic behavior,
replayability, and thread safety. No live objects or runtime references
may be embedded.

PHASE 4.3.12: Path Handler Protocol
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, Tuple, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from ..result import DefaultNetworkProduct, DefaultNetworkProposal
    from ..state import DefaultNetworkTransition


# =============================================================================
# DEFAULT NETWORK PATH HANDLER PROTOCOL
# =============================================================================

class DefaultNetworkPathHandler(Protocol):
    """
    Protocol for runtime-neutral path handlers.
    
    Each specialized path (reflection, simulation, narrative, etc.)
    implements this protocol with its own context and result types.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-PATH-HANDLER-INV-001: Handler is stateless or explicitly state-projected
        DEFAULT-PATH-HANDLER-INV-002: Handler produces deterministic outputs for same inputs
        DEFAULT-PATH-HANDLER-INV-003: Handler performs bounded local progression only
        DEFAULT-PATH-HANDLER-INV-004: Handler has no runtime side effects outside return value
    
    PROPERTIES:
        - path: Which DefaultNetworkPath this handler implements
        
    PROCESSING:
        - process: Perform one bounded semantic progression
    
    NOT RESPONSIBLE FOR:
        - Scheduling or waiting
        - Executing external capabilities
        - Mutating external state
        - Creating runtime threads or tasks
    """
    
    @property
    def path(self) -> str:
        """Which DefaultNetworkPath this handler implements."""
        ...
    
    def process(
        self,
        context: DefaultNetworkPathContext,
    ) -> DefaultNetworkPathResult:
        """
        Process one bounded semantic progression.
        
        Args:
            context: Immutable input context
            
        Returns:
            Immutable result with products, thoughts, requests, proposals
        """
        ...


# =============================================================================
# DEFAULT NETWORK PATH CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkPathContext:
    """
    Immutable context passed to path handlers.
    
    Contains all information a handler needs without runtime references.
    
    PROPERTIES:
        - request: The DefaultNetworkRequest being processed
        - selected_path: Which path is being executed
        
    COORDINATION STATE:
        - internal_context: The bound InternalContext
        - episode: The InternalEpisode being coordinated
        - current_thoughts: Thoughts available from this coordination cycle
        
    SPECIALIZED RESULTS:
        - capability_results: External capability results already supplied
        - external_decisions: External authority decisions (if any)
        
    CONFIGURATION:
        - path_configuration: Path-specific configuration
        - evaluation_time: Canonical time reference for semantic operations
        
    CHAINING:
        - correlation_id: For distributed tracing
        - provenance: Origin record
    
    NOT INCLUDES:
        - Live objects, callbacks, or service handles
        - Runtime scheduling references
        - External capability implementations
    """
    
    # Request being processed (required - no defaults)
    request_id: str
    """The DefaultNetworkRequest ID."""
    
    purpose: str
    """Request purpose (DefaultNetworkPurpose.*)."""
    
    subject: str
    """Request subject (DefaultNetworkSubject).*)."""
    
    selected_path: str
    """Which path is being executed."""
    
    internal_context_ref: str
    """Reference to InternalContext."""
    
    current_thoughts: Tuple[str, ...]
    """References to thoughts available."""
    
    capability_results: Tuple[str, ...]
    """IDs of external capability results already provided."""
    
    external_decisions: Tuple[str, ...]
    """IDs of external authority decisions."""
    
    evaluation_time_utc: datetime
    """Canonical time reference for semantic operations."""
    
    # Optional fields with defaults - must come after required fields
    episode_id: Optional[str] = None
    """ID of the InternalEpisode (if any)."""
    
    episode_state: Optional[str] = None
    """Current episode state (for handlers that need it)."""
    
    feedback: Tuple[str, ...] = field(default_factory=tuple)
    """Feedback items from previous processing."""
    
    path_configuration: Optional[dict] = field(default_factory=dict)
    """Path-specific configuration (JSON-compatible)."""
    
    configuration_revision: Optional[str] = None
    """Configuration version."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for tracing."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    @classmethod
    def new(
        cls,
        request_id: str,
        purpose: str,
        subject: str,
        selected_path: str,
        internal_context_ref: str,
        evaluation_time_utc: datetime,
    ) -> DefaultNetworkPathContext:
        """Create a new path context."""
        return cls(
            request_id=request_id,
            purpose=purpose,
            subject=subject,
            selected_path=selected_path,
            internal_context_ref=internal_context_ref,
            current_thoughts=(),
            capability_results=(),
            external_decisions=(),
            evaluation_time_utc=evaluation_time_utc,
            episode_id=None,
            episode_state=None,
            feedback=(),
            path_configuration={},
            configuration_revision=None,
            correlation_id=None,
            provenance_ref=None,
        )


# =============================================================================
# DEFAULT NETWORK PATH RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkPathResult:
    """
    Immutable result produced by path handlers.
    
    Contains all semantic products generated by one bounded handler execution.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-PATH-RESULT-INV-001: Result is immutable (deeply frozen dataclass with tuples)
        DEFAULT-PATH-RESULT-INV-002: Result contains no runtime references
        DEFAULT-PATH-RESULT-INV-003: Products preserve specialized types
        DEFAULT-PATH-RESULT-INV-004: External requests are typed and bounded
        
    PRODUCTS:
        - path_products: Semantic products generated by this path
        - internal_thoughts: Thoughts generated or updated
        
    EXTERNAL INTERFACE:
        - external_requests: Requests for external computation (NOT executed)
        - proposals: Advisory proposals (NOT applied)
        
    OUTCOME:
        - path_outcome: Result of this path's processing
        - continuation: Recommended next steps (advisory only)
        
    STATE MANAGEMENT:
        - transitions: State transitions caused by this path
        
    OBSERVABILITY:
        - diagnostics: Processing diagnostics for this path
        - confidence: Overall confidence in this result
        
    PROVENANCE:
        - provenance_ref: Reference to provenance record
    
    NOT RESPONSIBLE FOR:
        - Executing external requests
        - Applying proposals
        - Mutating external state
    """
    
    # Path identification (required - no defaults)
    path: str
    """Which DefaultNetworkPath produced this result."""
    
    # Products (semantic outputs) - required - no defaults
    path_products: Tuple[DefaultNetworkProduct, ...]
    """Semantic products generated by this path."""
    
    internal_thoughts: Tuple[str, ...]
    """References to thoughts generated or updated."""
    
    external_requests: Tuple[str, ...]
    """IDs of external requests created (NOT executed)."""
    
    proposals: Tuple[DefaultNetworkProposal, ...]
    """Advisory proposals (NOT applied)."""
    
    # Outcome and continuation (required - no defaults)
    path_outcome: str
    """Result of this path's processing."""
    
    transitions: Tuple[DefaultNetworkTransition, ...]
    """State transitions caused by this path."""
    
    episode_revision: int = 1
    """Episode revision after this path execution."""
    
    # Optional fields with defaults - must come after required fields
    continuation_kind: Optional[str] = None
    """Recommended next step classification."""
    
    confidence: float = 0.5
    """Confidence in this result (0.0 to 1.0)."""
    
    completeness_status: str = "partial"
    """Completeness status."""
    
    diagnostics_summary: str = ""
    """Diagnostics summary for this path."""
    
    provenance_ref: Optional[str] = None
    """Reference to provenance record."""
    
    @classmethod
    def new(
        cls,
        path: str,
        path_products: Tuple[DefaultNetworkProduct, ...],
        transitions: Tuple[DefaultNetworkTransition, ...],
        confidence: float = 0.5,
    ) -> DefaultNetworkPathResult:
        """Create a new path result."""
        return cls(
            path=path,
            path_products=path_products,
            internal_thoughts=(),
            external_requests=(),
            proposals=(),
            path_outcome="success" if len(path_products) > 0 else "partial",
            transitions=transitions,
            episode_revision=1,
            continuation_kind=None,
            confidence=confidence,
            completeness_status="partial" if len(path_products) == 0 else "complete",
            diagnostics_summary="Path processing completed.",
            provenance_ref=None,
        )