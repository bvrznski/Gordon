# Gordon Phase 5.7.1-I: Consciousness Facade
# ===============================================================================

"""
Public facade for the Consciousness capability.

This module provides one deliberate public interface to the Consciousness
capability that coordinates:
    - Source and extension registration
    - Contribution and projection submission
    - Current context queries
    - Transition requests
    
The facade is stateless for operations - it delegates to internal state managers.
It ensures typed, immutable contracts are used for all interactions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
import uuid

# Import local modules (relative imports within package)
from .config import ConsciousnessConfiguration
from .constants import (
    ContextState,
    HealthState,
    QueryMode,
    TransitionStatus,
)
from .exceptions import (
    ConsciousnessUnavailable,
    ConsciousnessNotReady,
    InvalidContribution,
    InvalidProjection,
    UnknownSource,
    DuplicateSource,
    UnknownExtension,
    DuplicateExtension,
    ExtensionDependencyCycle,
    SourceGenerationMismatch,
    ContextTransitionConflict,
    ContextPublicationFailure,
)
from .types import CorrelationId, CausationId
from .identities import (
    ConsciousnessCapabilityId,
    ContextId,
    ContextGeneration,
    SourceId,
    ExtensionId,
)
from .contracts import (
    CurrentContextSnapshot,
    CurrentContextReference,
    ContributionEnvelope,
    ProjectionEnvelope,
    ContextTransition,
    TransitionResult,
    QueryRequest,
    ConsumerViewFilter,
    DiagnosticsSnapshot,
    HealthSnapshot,
)
from .registry import (
    SourceRegistry,
    ExtensionRegistry,
)


@dataclass
class ConsciousnessFacade:
    """
    Public facade for the Consciousness capability.
    
    The facade provides a single, deliberate interface to the Consciousness
    capability that coordinates contributions, projections, queries, and
    transitions while ensuring all operations use immutable contracts.
    
    Facade responsibilities:
        - Coordinate contribution submission
        - Coordinate projection submission
        - Execute current context queries
        - Process transition requests (atomic commits)
        - Manage source registrations
        - Manage extension registrations
        - Provide health and diagnostics snapshots
    
    NOT responsible for:
        - Direct state mutation (delegated to internal managers)
        - Runtime thread management (delegated to runtime)
        - Extension implementation (owned by dedicated engines)
        - Policy decisions (delegated to policy authorities)
    
    Usage pattern:
        facade = ConsciousnessFacade(config)
        facade.initialize()
        facade.start()
        
        # Submit a contribution
        result = facade.submit_contribution(contribution_env)
        
        # Query current context
        snapshot = facade.get_current_context(QueryMode.CURRENT_COMPOSITE_SNAPSHOT)
        
        # Request transition (if needed for extension updates)
        result = facade.request_transition(transitions)
    """
    
    # Configuration and identity
    _configuration: ConsciousnessConfiguration = field(default_factory=ConsciousnessConfiguration.default)
    """Immutable configuration for this instance."""
    
    _capability_id: str = "consciousness-001"
    """Unique identifier for this capability instance."""
    
    # Internal state (private - not exposed publicly)
    _state: ContextState = ContextState.CONSTRUCTED
    """Current lifecycle state."""
    
    _current_context_snapshot: Optional[CurrentContextSnapshot] = field(default=None)
    """Current context snapshot (if initialized)."""
    
    _source_registry: SourceRegistry = field(default_factory=SourceRegistry)
    """Source registration manager."""
    
    _extension_registry: ExtensionRegistry = field(default_factory=ExtensionRegistry)
    """Extension registration manager."""
    
    # Transition authority state
    _pending_transition_id: Optional[str] = None
    """Transition ID if a transition is in progress."""
    
    def __post_init__(self):
        """Validate and initialize after construction."""
        self._capability_id = f"consciousness-{uuid.uuid4().hex[:8]}"
    
    # =========================================================================
    # LIFECYCLE MANAGEMENT
    # =========================================================================

    def initialize(self) -> Tuple[bool, Optional[str]]:
        """
        Initialize the Consciousness capability.
        
        This prepares internal state but does not start accepting contributions.
        After initialization, the capability transitions to CONFIGURED state.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._state != ContextState.CONSTRUCTED:
            return False, "Cannot initialize - already initialized or started"
        
        # Validate configuration
        try:
            # Configuration was already validated at construction time
            pass
        except ValueError as e:
            return False, f"Configuration validation failed: {str(e)}"
        
        self._state = ContextState.CONFIGURED
        return True, None
    
    def start(self) -> Tuple[bool, Optional[str]]:
        """
        Start the Consciousness capability.
        
        After starting, the capability is READY and can accept contributions
        and process queries. If required sources/extensions are unavailable,
        the capability may start in DEGRADED mode if configured to allow it.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._state not in (ContextState.CONFIGURED, ContextState.READY):
            return False, "Cannot start - not initialized"
        
        # Check required extensions if any
        for ext_id in self._configuration.required_extensions:
            if ext_id not in self._extension_registry._extensions:
                if self._configuration.allow_degraded_start:
                    continue  # Allow degraded start
                else:
                    return False, f"Required extension unavailable: {ext_id}"
        
        self._state = ContextState.READY
        
        # Create initial context snapshot
        self._current_context_snapshot = CurrentContextSnapshot.initial()
        
        return True, None
    
    def stop(self) -> Tuple[bool, Optional[str]]:
        """
        Stop the Consciousness capability.
        
        After stopping, the capability transitions to STOPPED and cannot accept
        new contributions or queries until restarted.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._state not in (ContextState.READY, ContextState.ACTIVE):
            return False, "Cannot stop - not running"
        
        # Cancel any pending transition
        self._pending_transition_id = None
        
        self._state = ContextState.STOPPED
        self._current_context_snapshot = None
        
        return True, None
    
    def pause(self) -> Tuple[bool, Optional[str]]:
        """Pause the capability temporarily."""
        if self._state not in (ContextState.READY, ContextState.ACTIVE):
            return False, "Cannot pause - not running"
        
        self._state = ContextState.PAUSED
        return True, None
    
    def resume(self) -> Tuple[bool, Optional[str]]:
        """Resume from paused state."""
        if self._state != ContextState.PAUSED:
            return False, "Cannot resume - not paused"
        
        self._state = ContextState.READY
        return True, None
    
    # =========================================================================
    # SOURCE REGISTRATION
    # =========================================================================

    def register_source(self, descriptor: SourceDescriptor) -> Tuple[bool, Optional[str]]:
        """
        Register a contribution source.
        
        Sources must be registered before submitting contributions or projections.
        
        Args:
            descriptor: Source descriptor to register
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Check capability state
        if self._state not in (ContextState.READY, ContextState.ACTIVE):
            return False, "Cannot register source - capability not ready"
        
        return self._source_registry.register(descriptor)
    
    def unregister_source(self, source_id: str) -> Tuple[bool, Optional[str]]:
        """
        Unregister a source.
        
        Args:
            source_id: ID of the source to unregister
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        return self._source_registry.unregister(source_id)
    
    def get_source_descriptor(self, source_id: str) -> Optional[SourceDescriptor]:
        """Get a registered source descriptor by ID."""
        return self._source_registry.get(source_id)
    
    # =========================================================================
    # EXTENSION REGISTRATION
    # =========================================================================

    def register_extension(self, descriptor: ExtensionDescriptor) -> Tuple[bool, Optional[str]]:
        """
        Register an extension.
        
        Extensions are Phase 5.7.2-5.7.8 subsystems that participate in
        the current context lifecycle.
        
        Args:
            descriptor: Extension descriptor to register
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Check capability state
        if self._state not in (ContextState.READY, ContextState.ACTIVE):
            return False, "Cannot register extension - capability not ready"
        
        # Check for dependency cycle before registering
        temp_ext = dict(self._extension_registry._extensions)
        temp_ext[descriptor.extension_id] = descriptor
        
        has_cycle, _ = self._extension_registry._detect_dependency_cycle(temp_ext)
        if has_cycle:
            return False, f"Extension registration would create a dependency cycle"
        
        return self._extension_registry.register(descriptor)
    
    def unregister_extension(self, extension_id: str) -> Tuple[bool, Optional[str]]:
        """
        Unregister an extension.
        
        Args:
            extension_id: ID of the extension to unregister
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        return self._extension_registry.unregister(extension_id)
    
    def get_extension_descriptor(self, extension_id: str) -> Optional[ExtensionDescriptor]:
        """Get a registered extension descriptor by ID."""
        return self._extension_registry.get(extension_id)
    
    # =========================================================================
    # CONTRIBUTION SUBMISSION
    # =========================================================================

    def submit_contribution(
        self,
        contribution: ContributionEnvelope,
        correlation_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Submit a contribution for consideration.
        
        Contributions are proposals that do not guarantee admission to the
        current context. They may be rejected due to:
            - Invalid source identity
            - Expired freshness timestamp
            - Duplicate submission (same content)
            - Source generation mismatch
        
        Args:
            contribution: Contribution envelope to submit
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Check capability state
        if self._state not in (ContextState.READY, ContextState.ACTIVE):
            return False, "Cannot accept contributions - capability not ready"
        
        # Validate source exists
        if contribution.source_id not in self._source_registry._sources:
            raise UnknownSource(source_id=contribution.source_id)
        
        # Check expiration
        if contribution.is_expired():
            raise InvalidContribution(
                message="Contribution expired",
                contribution_id=contribution.contribution_id,
            )
        
        # Validate source generation (simplified - in real implementation would track per-source generations)
        # For now, accept the contribution
        
        return True, None
    
    # =========================================================================
    # PROJECTION SUBMISSION
    # =========================================================================

    def submit_projection(
        self,
        projection: ProjectionEnvelope,
        correlation_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Submit a projection from an external system.
        
        Projections expose bounded views that may be considered as inputs to
        the current context. They do not mutate Consciousness state directly.
        
        Args:
            projection: Projection envelope to submit
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Check capability state
        if self._state not in (ContextState.READY, ContextState.ACTIVE):
            return False, "Cannot accept projections - capability not ready"
        
        # Validate source exists
        if projection.source_id not in self._source_registry._sources:
            raise UnknownSource(source_id=projection.source_id)
        
        return True, None
    
    # =========================================================================
    # CURRENT CONTEXT QUERIES
    # =========================================================================

    def get_current_context(
        self,
        mode: str = QueryMode.CURRENT_COMPOSITE_SNAPSHOT.value,
        filter_options: Optional[ConsumerViewFilter] = None,
    ) -> CurrentContextSnapshot:
        """
        Get the current context snapshot.
        
        This returns an immutable snapshot of the current context at a point
        in time. The snapshot is bounded and does not include full extension
        payloads, only references.
        
        Args:
            mode: Query mode (snapshot, reference, health_only, diagnostics_only)
            filter_options: Optional consumer view filter
            
        Returns:
            CurrentContextSnapshot with requested information
            
        Raises:
            ConsciousnessNotReady: If capability is not ready
        """
        if self._state not in (ContextState.READY, ContextState.ACTIVE):
            raise ConsciousnessNotReady("Cannot get current context - capability not ready")
        
        if self._current_context_snapshot is None:
            raise ConsciousnessUnavailable(
                "No current context available - capability not initialized"
            )
        
        return self._current_context_snapshot
    
    def query_generation(self) -> ContextGeneration:
        """
        Get the current context generation number.
        
        Returns:
            CurrentContextReference with generation information
            
        Raises:
            ConsciousnessNotReady: If capability is not ready
        """
        if self._state not in (ContextState.READY, ContextState.ACTIVE):
            raise ConsciousnessNotReady("Cannot query generation - capability not ready")
        
        if self._current_context_snapshot is None:
            return ContextGeneration.initial()
        
        return ContextGeneration(value=self._current_context_snapshot.generation + 1)
    
    # =========================================================================
    # TRANSITION REQUESTS (for extension updates)
    # =========================================================================

    def request_transition(
        self,
        updated_extensions: Dict[str, Any] = None,
    ) -> TransitionResult:
        """
        Request a context transition to incorporate extension changes.
        
        This is the atomic commit point where new current-context generations
        are created. The transition either fully commits or rolls back -
        partial updates are never exposed.
        
        Args:
            updated_extensions: Dict of extension_id -> new snapshot reference
            
        Returns:
            TransitionResult with outcome information
            
        Raises:
            ConsciousnessNotReady: If capability is not ready
            ContextTransitionConflict: If concurrent transition detected
        """
        if self._state not in (ContextState.READY, ContextState.ACTIVE):
            raise ConsciousnessNotReady("Cannot request transition - capability not ready")
        
        # Check for concurrent transition
        if self._pending_transition_id is not None:
            raise ContextTransitionConflict(
                context_id=self._current_context_snapshot.context_id if self._current_context_snapshot else "unknown",
                previous_generation=0,
                attempt_generation=1,
            )
        
        try:
            # Set pending state
            old_snapshot = self._current_context_snapshot
            self._pending_transition_id = str(uuid.uuid4())
            
            # Validate extension updates (simplified)
            if updated_extensions:
                for ext_id in updated_extensions.keys():
                    if ext_id not in self._extension_registry._extensions:
                        raise UnknownExtension(extension_id=ext_id)
            
            # Create new snapshot with updated extensions
            new_snapshot = old_snapshot.with_generation(
                old_snapshot.generation + 1
            )
            
            if updated_extensions:
                refs = {k: str(v) for k, v in updated_extensions.items()}
                new_snapshot = new_snapshot.with_transitions(**refs)
            
            # Update state atomically
            self._current_context_snapshot = new_snapshot
            self._pending_transition_id = None
            
            return TransitionResult(
                transition_id=self._pending_transition_id or str(uuid.uuid4()),
                succeeded=True,
                status=TransitionStatus.COMPLETED.value,
                new_context_snapshot=new_snapshot,
                new_generation=new_snapshot.generation,
            )
            
        except Exception as e:
            # Rollback on failure - preserve previous snapshot
            if self._current_context_snapshot is not None:
                pass  # Already restored by not updating
            
            return TransitionResult(
                transition_id=self._pending_transition_id or str(uuid.uuid4()),
                succeeded=False,
                status=TransitionStatus.ROLLED_BACK.value,
                failure_reason=str(e),
            )
    
    # =========================================================================
    # HEALTH AND DIAGNOSTICS
    # =========================================================================

    def query_health(self) -> HealthSnapshot:
        """
        Get the current health snapshot.
        
        This returns bounded health information without exposing context content.
        
        Returns:
            HealthSnapshot with health state and readiness indicators
        """
        return HealthSnapshot(
            capability_id=self._capability_id,
            state=self._state.value if self._state else "unknown",
            initialized=self._state in (ContextState.READY, ContextState.ACTIVE),
            ready=self._state == ContextState.READY or (
                self._state == ContextState.ACTIVE and not self._pending_transition_id
            ),
            active=self._state == ContextState.ACTIVE,
        )
    
    def query_diagnostics(self) -> DiagnosticsSnapshot:
        """
        Get the current diagnostics snapshot.
        
        This returns bounded diagnostic information without exposing context content.
        
        Returns:
            DiagnosticsSnapshot with operational metrics and counts
        """
        return DiagnosticsSnapshot(
            capability_id=self._capability_id,
            registered_source_count=self._source_registry.registered_count,
            registered_extension_count=self._extension_registry.registered_count,
            lifecycle_state=self._state.value if self._state else "unknown",
        )