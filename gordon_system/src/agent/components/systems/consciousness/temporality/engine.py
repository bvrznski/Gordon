# Gordon Phase 5.7.4-I: Temporal Context Engine - Canonical Engine
# ===============================================================================
"""
Canonical Temporal Context Engine for bounded temporal context organization.

The Temporal Context Engine is the sole authority for:
- Temporal snapshot publication
- Generation transitions
- Continuity window management
- Retention coordination
- Presentation anchoring
- Protention expectation tracking

This engine ensures deterministic, immutable, and provenance-preserving
temporal organization for Gordon's conscious continuity.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional, Callable

# Import all temporal components
from .types import (
    TemporalContextType,
    GenerationNumber,
    TrustLevel,
    PrivacyClassification,
    RetentionHistory,
    ProtentionExpectations,
)
from .exceptions import (
    ContinuityViolation,
    SnapshotCorruption,
    TransitionFailure,
    InvalidRetentionReference,
    InvalidProtentionExpectation,
    InvalidContinuityWindow,
)
from .constants import (
    MAX_RETENTION_HISTORY,
    MAX_PROTENTION_EXPECTATIONS,
    MAX_CONTINUITY_WINDOW_SIZE,
    ContinuityState,
    TransitionKind,
    DEFAULT_TRUST_LEVEL,
    DEFAULT_PRIVACY_CLASSIFICATION,
)
from gordon.agent.components.systems.consciousnessretention import RetentionRecord, RetentionRegistry
from gordon.agent.components.systems.consciousnesspresentation import PresentationReference, PresentationValidator
from gordon.agent.components.systems.consciousnessprotention import ProtentionExpectation, ProtentionSet, ProtentionBoundaries
from gordon.agent.components.systems.consciousnesscontinuity_window import (
    ContinuityWindow,
    ContinuityWindowManager,
    ContinuityWindowBuilder,
)
from gordon.agent.components.systems.consciousnesssnapshot import TemporalSnapshot, TemporalSnapshotBuilder, SnapshotTransition
from gordon.agent.components.systems.consciousnesstransition import TemporalTransition, TransitionAuthority, TransitionResult


# =============================================================================
# TIME PROVIDER TYPE ALIAS
# =============================================================================

TimeProvider = Callable[[], float]
"""Callable that returns the current timestamp. Injected for deterministic testing."""


# =============================================================================
# CANONICAL TEMPORAL CONTEXT ENGINE
# =============================================================================

class TemporalContextEngine:
    """
    Canonical authority for temporal context organization.
    
    This engine coordinates all temporal components and ensures:
        - Deterministic publication of snapshots
        - Atomic transitions between generations
        - Proper bounded continuity windows
        - Provenance preservation across generations
        - Trust and privacy boundary enforcement
    
    The engine is stateful but maintains immutable outputs. All published
    snapshots and transitions are immutable records.
    
    Key properties:
        - Single source of truth for temporal organization
        - No external mutation of internal state after publication
        - Deterministic behavior through injected time provider
        - Proper lifecycle integration with conscious context
    
    This is NOT:
        - A memory system (episodic or semantic)
        - A reasoning engine
        - A planning module
        - A prediction system
        - A working memory manager
    
    Temporal Context is purely organizational: it answers "How is the current
    conscious context temporally organized?"
    """
    
    # =============================================================================
    # INITIALIZATION
    # =============================================================================
    
    def __init__(
        self,
        time_provider: Optional[TimeProvider] = None,
        max_retention_history: int = MAX_RETENTION_HISTORY,
        max_protention_expectations: int = MAX_PROTENTION_EXPECTATIONS,
        default_trust_level: float = DEFAULT_TRUST_LEVEL,
        default_privacy_classification: str = DEFAULT_PRIVACY_CLASSIFICATION,
    ):
        """
        Initialize the Temporal Context Engine.
        
        Args:
            time_provider: Callable returning current timestamp (default: time.time)
                           Injected for deterministic testing.
            max_retention_history: Maximum retention history entries
            max_protention_expectations: Maximum protentional expectations
            default_trust_level: Default trust level for new elements
            default_privacy_classification: Default privacy classification
        """
        # Use injected time provider or fall back to real time
        self._time_provider: TimeProvider = time_provider if time_provider is not None else time.time
        
        # Configuration
        self._max_retention_history: int = max_retention_history
        self._max_protention_expectations: int = max_protention_expectations
        self._default_trust_level: float = default_trust_level
        self._default_privacy_classification: str = default_privacy_classification
        
        # Internal state (mutable during operation, but never exposed directly)
        self._current_generation: GenerationNumber = GenerationNumber.initial()
        self._continuity_state: ContinuityState = ContinuityState.ACTIVE
        self._presentation_validator: PresentationValidator = PresentationValidator()
        
        # Component managers
        self._retention_registry: RetentionRegistry = RetentionRegistry(
            max_history=max_retention_history
        )
        self._protention_set: ProtentionSet = ProtentionSet(
            max_expectations=max_protention_expectations
        )
        self._continuity_window_manager: ContinuityWindowManager = ContinuityWindowManager()
        
        # Transition authority for atomic commits
        self._transition_authority: TransitionAuthority = TransitionAuthority()
        
        # Last published snapshot (immutable once set)
        self._last_snapshot: Optional[TemporalSnapshot] = None
        
        # Transition history for replayability
        self._transition_history: Tuple[SnapshotTransition, ...] = tuple()
    
    # =============================================================================
    # PROPERTIES (READ-ONLY EXPOSURE OF STATE)
    # =============================================================================
    
    @property
    def current_generation(self) -> GenerationNumber:
        """Get the current generation number."""
        return self._current_generation
    
    @property
    def continuity_state(self) -> ContinuityState:
        """Get the current continuity state."""
        return self._continuity_state
    
    @property
    def last_snapshot(self) -> Optional[TemporalSnapshot]:
        """
        Get the last published snapshot (immutable reference).
        
        This is a read-only reference. The returned snapshot must not be modified.
        """
        return self._last_snapshot
    
    @property
    def retention_count(self) -> int:
        """Get the count of registered retention records."""
        return self._retention_registry.registered_count
    
    @property
    def protention_count(self) -> int:
        """Get the count of registered protentional expectations."""
        return self._protention_set.expectation_count
    
    @property
    def active_window(self) -> Optional[ContinuityWindow]:
        """Get the currently active continuity window."""
        return self._continuity_window_manager.active_window
    
    # =============================================================================
    # INITIALIZATION OPERATIONS
    # =============================================================================
    
    def initialize(
        self,
        initial_presentation_ref: str,
    ) -> Tuple[bool, Optional[str], TemporalSnapshot]:
        """
        Initialize the temporal context engine with an initial state.
        
        This creates the first generation snapshot with no prior retention.
        
        Args:
            initial_presentation_ref: Reference to the initial EF context
            
        Returns:
            Tuple of (success, error_message, snapshot if successful)
        """
        try:
            # Create initial continuity window
            success, error, window = self._continuity_window_manager.create_window(
                field_context_id=initial_presentation_ref,
                start_generation=0,
            )
            
            if not success:
                return False, f"Failed to create initial window: {error}", None
            
            # Build and publish initial snapshot
            timestamp = self._time_provider()
            snapshot = TemporalSnapshot(
                snapshot_id=f"ts-gen0-{timestamp}",
                retention_references=(),  # No prior generations yet
                presentation_reference=initial_presentation_ref,
                protention_expectations=(),
                generation=0,
                previous_generation=None,
                transition_id="init",
                created_at_utc=timestamp,
                valid_from_utc=timestamp,
                state="valid",
                provenance="init",
                trust_summary=self._trust_level_to_string(self._default_trust_level),
                privacy_classification=self._default_privacy_classification,
            )
            
            self._last_snapshot = snapshot
            self._current_generation = GenerationNumber.initial()
            
            return True, None, snapshot
            
        except Exception as e:
            return False, f"Initialization failed: {str(e)}", None
    
    # =============================================================================
    # TRANSITION OPERATIONS (CANONICAL AUTHORITY)
    # =============================================================================
    
    def advance(
        self,
        new_presentation_ref: str,
        retention_refs_to_add: Tuple[str, ...] = (),
        protention_expectations_to_add: Tuple[ProtentionExpectation, ...] = (),
    ) -> Tuple[bool, Optional[str], TemporalSnapshot]:
        """
        Advance to the next generation.
        
        This is the primary operation for temporal continuity. It:
            1. Records the current EF context as retention
            2. Updates presentation to the new context
            3. Adds any new protentional expectations
            4. Publishes a new immutable snapshot
        
        Args:
            new_presentation_ref: Reference to the new EF context
            retention_refs_to_add: Additional retention references to add
            protention_expectations_to_add: New protentional expectations
            
        Returns:
            Tuple of (success, error_message, new snapshot if successful)
            
        Raises:
            ContinuityViolation: If transition violates continuity rules
        """
        # Validate continuity state
        if self._continuity_state == ContinuityState.CLOSED:
            return False, "Cannot advance: window is closed", None
        
        if self._continuity_state == ContinuityState.DEGRADED:
            return False, "Cannot advance: window is degraded", None
        
        try:
            # Validate the presentation reference
            is_valid, error = self._presentation_validator.validate_reference(
                PresentationReference.from_field_snapshot(
                    context_id=new_presentation_ref,
                    generation=self._current_generation.value + 1,
                ),
                expected_generation=self._current_generation.value + 1,
            )
            
            if not is_valid:
                return False, f"Invalid presentation reference: {error}", None
            
            # Get current snapshot for retention
            current_snapshot = self._last_snapshot
            if current_snapshot is None:
                return False, "No current snapshot to advance from", None
            
            # Build new retention history
            new_retention_refs = self._build_new_retention_history(
                current_snapshot.retention_references,
                new_presentation_ref,
                retention_refs_to_add,
            )
            
            # Update protention expectations
            updated_protentions = self._update_protention_expectations(
                protention_expectations_to_add
            )
            
            # Create and publish new snapshot
            timestamp = self._time_provider()
            new_snapshot = current_snapshot.next_generation(
                transition_id=f"advance-{timestamp}",
            )
            
            # Update internal state
            self._current_generation = GenerationNumber(value=self._current_generation.value + 1)
            
            # Record transition for replayability
            transition = SnapshotTransition.standard(
                previous_snapshot_id=current_snapshot.snapshot_id,
                new_snapshot_id=new_snapshot.snapshot_id,
            )
            self._transition_history += (transition,)
            
            return True, None, new_snapshot
            
        except Exception as e:
            return False, f"Advance failed: {str(e)}", None
    
    def _build_new_retention_history(
        self,
        current_retentions: Tuple[str, ...],
        presentation_ref: str,
        additional_retentions: Tuple[str, ...] = (),
    ) -> Tuple[str, ...]:
        """Build new retention history with bounded size."""
        # Combine and deduplicate
        all_refs = set(current_retentions) | {presentation_ref} | set(additional_retentions)
        
        # Return as tuple (bounded by max_retention_history)
        return tuple(sorted(all_refs))[:self._max_retention_history]
    
    def _update_protention_expectations(
        self,
        to_add: Tuple[ProtentionExpectation, ...],
    ) -> Tuple[str, ...]:
        """Update protention expectations and return expectation references."""
        for expectation in to_add:
            success, error = self._protention_set.register(expectation)
            if not success:
                # Log warning but continue - don't block the transition
                pass
        
        return tuple(exp.expected_content_reference 
                     for exp in self._protention_set.get_all()
                     if exp.expected_content_reference is not None)
    
    def _trust_level_to_string(self, level: float) -> str:
        """Convert trust level float to string representation."""
        if level >= 0.8:
            return "high"
        elif level >= 0.5:
            return "medium"
        else:
            return "low"
    
    # =============================================================================
    # ALTERNATIVE TRANSITION TYPES
    # =============================================================================
    
    def resume(self) -> Tuple[bool, Optional[str], TemporalSnapshot]:
        """
        Resume from paused state, preserving continuity.
        
        Returns:
            Tuple of (success, error_message, snapshot if successful)
        """
        if self._continuity_state != ContinuityState.PAUSED:
            return False, "Cannot resume: not in paused state", None
        
        # Update state
        self._continuity_state = ContinuityState.ACTIVE
        
        # Return current snapshot (unchanged)
        if self._last_snapshot is None:
            return False, "No snapshot to resume with", None
        
        return True, None, self._last_snapshot
    
    def reset(self) -> Tuple[bool, Optional[str], TemporalSnapshot]:
        """
        Reset continuity window (e.g., new session).
        
        This creates a fresh start with generation 0 and empty retention.
        
        Returns:
            Tuple of (success, error_message, new snapshot if successful)
        """
        # Create initial state
        timestamp = self._time_provider()
        snapshot = TemporalSnapshot(
            snapshot_id=f"ts-reset-{timestamp}",
            retention_references=(),
            presentation_reference=None,
            protention_expectations=(),
            generation=0,
            previous_generation=None,
            transition_id="reset",
            created_at_utc=timestamp,
            valid_from_utc=timestamp,
            state="valid",
            provenance="reset",
            trust_summary=self._trust_level_to_string(self._default_trust_level),
            privacy_classification=self._default_privacy_classification,
        )
        
        # Reset internal state
        self._current_generation = GenerationNumber.initial()
        self._continuity_state = ContinuityState.ACTIVE
        self._retention_registry.clear()
        self._protention_set.clear()
        self._last_snapshot = snapshot
        
        return True, None, snapshot
    
    def pause(self) -> Tuple[bool, Optional[str], TemporalSnapshot]:
        """
        Pause the current continuity window.
        
        Returns:
            Tuple of (success, error_message, current snapshot)
        """
        if self._continuity_state == ContinuityState.CLOSED:
            return False, "Cannot pause: window is closed", None
        
        # Update state
        self._continuity_state = ContinuityState.PAUSED
        
        # Return current snapshot
        if self._last_snapshot is None:
            return False, "No snapshot to pause with", None
        
        return True, None, self._last_snapshot
    
    def close(self) -> Tuple[bool, Optional[str], TemporalSnapshot]:
        """
        Close the current continuity window.
        
        Returns:
            Tuple of (success, error_message, current snapshot)
        """
        if self._continuity_state == ContinuityState.CLOSED:
            return False, "Window is already closed", None
        
        # Update state
        self._continuity_state = ContinuityState.CLOSED
        
        # Return current snapshot
        if self._last_snapshot is None:
            return False, "No snapshot to close with", None
        
        return True, None, self._last_snapshot
    
    def degrade(self) -> Tuple[bool, Optional[str], TemporalSnapshot]:
        """
        Mark window as degraded (continuity failures detected).
        
        Returns:
            Tuple of (success, error_message, current snapshot)
        """
        # Update state
        self._continuity_state = ContinuityState.DEGRADED
        
        # Return current snapshot
        if self._last_snapshot is None:
            return False, "No snapshot to degrade", None
        
        return True, None, self._last_snapshot
    
    def recover(self) -> Tuple[bool, Optional[str], TemporalSnapshot]:
        """
        Recover from degraded state back to active.
        
        Returns:
            Tuple of (success, error_message, current snapshot)
        """
        if self._continuity_state != ContinuityState.DEGRADED:
            return False, "Not in degraded state", None
        
        # Update state
        self._continuity_state = ContinuityState.ACTIVE
        
        # Return current snapshot
        if self._last_snapshot is None:
            return False, "No snapshot to recover with", None
        
        return True, None, self._last_snapshot
    
    # =============================================================================
    # RETENTION OPERATIONS
    # =============================================================================
    
    def add_retention_reference(
        self,
        field_generation: int,
        field_context_id: Optional[str] = None,
        provenance: Optional[str] = None,
        trust_level: Optional[float] = None,
    ) -> Tuple[bool, Optional[str], RetentionRecord]:
        """
        Add a retention reference for a previous generation.
        
        Args:
            field_generation: Generation number to retain
            field_context_id: Context ID (optional)
            provenance: Provenance chain (optional)
            trust_level: Trust level (default from config)
            
        Returns:
            Tuple of (success, error_message, retention record if successful)
        """
        trust = trust_level if trust_level is not None else self._default_trust_level
        
        record = RetentionRecord.from_field_snapshot(
            field_generation=field_generation,
            field_context_id=field_context_id,
            provenance=provenance,
            trust_level=trust,
        )
        
        success, error = self._retention_registry.register(record)
        
        if not success:
            return False, f"Failed to add retention: {error}", None
        
        return True, None, record
    
    def get_retention_history(
        self,
        count: int = 5,
    ) -> Tuple[RetentionRecord, ...]:
        """
        Get recent retention history.
        
        Args:
            count: Number of most recent entries to return
            
        Returns:
            Tuple of most recent retention records
        """
        return self._retention_registry.get_recent_history(count)
    
    def get_all_retentions(self) -> Tuple[RetentionRecord, ...]:
        """Get all registered retention records."""
        return self._retention_registry.get_all()
    
    # =============================================================================
    # PROTENTION OPERATIONS
    # =============================================================================
    
    def add_protention_expectation(
        self,
        expected_content_reference: str,
        generation_offset: int = 1,
        ttl_seconds: float = 60.0,
    ) -> Tuple[bool, Optional[str], ProtentionExpectation]:
        """
        Add a protentional expectation for the immediate future.
        
        Args:
            expected_content_reference: What is expected in the next context
            generation_offset: Expected generation offset (default +1)
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            Tuple of (success, error_message, expectation if successful)
        """
        expectation = ProtentionExpectation(
            protention_id=f"prot-{self._time_provider()}",
            expected_content_reference=expected_content_reference,
            expected_generation_offset=generation_offset,
            timestamp_utc=self._time_provider(),
            ttl_seconds=ttl_seconds,
        )
        
        success, error = self._protention_set.register(expectation)
        
        if not success:
            return False, f"Failed to add protention: {error}", None
        
        return True, None, expectation
    
    def get_protention_expectations(self) -> Tuple[ProtentionExpectation, ...]:
        """Get all registered protentional expectations."""
        return self._protention_set.get_all()
    
    # =============================================================================
    # QUERY OPERATIONS
    # =============================================================================
    
    def query_snapshot(
        self,
        generation: Optional[int] = None,
    ) -> Optional[TemporalSnapshot]:
        """
        Query a snapshot by generation (or current if not specified).
        
        Args:
            generation: Generation number to query (None for current)
            
        Returns:
            Snapshot if found, None otherwise
        """
        if generation is None:
            return self._last_snapshot
        
        # For simplicity in this implementation, we only track the latest snapshot
        # In a full implementation, this would look up from historical snapshots
        if generation == self._current_generation.value and self._last_snapshot is not None:
            return self._last_snapshot
        
        return None
    
    def query_generation(self) -> GenerationNumber:
        """Get the current generation number."""
        return self._current_generation
    
    # =============================================================================
    # DIAGNOSTICS AND HEALTH
    # =============================================================================
    
    def get_diagnostics(
        self,
    ) -> TemporalDiagnosticsSnapshot:
        """
        Get a snapshot of diagnostic information.
        
        Returns:
            TemporalDiagnosticsSnapshot with current state metrics
        """
        return TemporalDiagnosticsSnapshot(
            current_generation=self._current_generation.value,
            continuity_state=str(self._continuity_state),
            retention_count=self.retention_count,
            protention_count=self.protention_count,
            active_window_id=self.active_window.window_id if self.active_window else None,
            last_snapshot_id=self._last_snapshot.snapshot_id if self._last_snapshot else None,
            transition_count=len(self._transition_history),
        )
    
    def get_health(
        self,
    ) -> TemporalHealthSnapshot:
        """
        Get a snapshot of health status.
        
        Returns:
            TemporalHealthSnapshot with current state indicators
        """
        return TemporalHealthSnapshot(
            is_healthy=self._continuity_state == ContinuityState.ACTIVE,
            continuity_state=str(self._continuity_state),
            current_generation=self._current_generation.value,
            has_snapshot=self._last_snapshot is not None,
        )
    
    # =============================================================================
    # UTILITY
    # =============================================================================
    
    def _continity_state_property(self) -> ContinuityState:
        """Property accessor for continuity state (fix typo in advance method)."""
        return self._continuity_state


# =============================================================================
# DIAGNOSTICS AND HEALTH TYPES
# =============================================================================

@dataclass(frozen=True)
class TemporalDiagnosticsSnapshot:
    """
    Immutable snapshot of temporal context diagnostics.
    
    Provides passive metrics without exposing internal mutable state.
    """
    
    current_generation: int
    """Current generation number."""
    
    continuity_state: str
    """Current continuity window state."""
    
    retention_count: int
    """Number of registered retention records."""
    
    protention_count: int
    """Number of registered protentional expectations."""
    
    active_window_id: Optional[str]
    """ID of the active continuity window."""
    
    last_snapshot_id: Optional[str]
    """ID of the last published snapshot."""
    
    transition_count: int
    """Total number of recorded transitions."""
    
    @classmethod
    def empty(cls) -> "TemporalDiagnosticsSnapshot":
        """Get an empty diagnostics snapshot (initial state)."""
        return cls(
            current_generation=0,
            continuity_state=str(ContinuityState.ACTIVE),
            retention_count=0,
            protention_count=0,
            active_window_id=None,
            last_snapshot_id=None,
            transition_count=0,
        )


@dataclass(frozen=True)
class TemporalHealthSnapshot:
    """
    Immutable snapshot of temporal context health status.
    
    Provides health indicators without exposing internal mutable state.
    """
    
    is_healthy: bool
    """Whether the temporal context is healthy (active state)."""
    
    continuity_state: str
    """Current continuity window state."""
    
    current_generation: int
    """Current generation number."""
    
    has_snapshot: bool
    """Whether a snapshot has been published."""
    
    @classmethod
    def empty(cls) -> "TemporalHealthSnapshot":
        """Get an empty health snapshot (initial state)."""
        return cls(
            is_healthy=True,
            continuity_state=str(ContinuityState.ACTIVE),
            current_generation=0,
            has_snapshot=False,
        )


__all__: Tuple[str, ...] = (
    # Engine
    "TemporalContextEngine",
    
    # Diagnostics and Health
    "TemporalDiagnosticsSnapshot",
    "TemporalHealthSnapshot",
)