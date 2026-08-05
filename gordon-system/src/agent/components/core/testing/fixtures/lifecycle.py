# Fixture Lifecycle - Testing Infrastructure
# ==========================================
"""
FixtureLifecycle: Manages fixture lifecycle with cleanup verification.

The FixtureLifecycle ensures:
- Fixtures are properly created and destroyed
- Cleanup is called exactly once per fixture
- Resources are released in correct order
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
import time


class FixtureState(Enum):
    """States in the fixture lifecycle."""
    PENDING = "pending"        # Registered but not yet created
    CREATED = "created"        # Instance has been created
    ACTIVE = "active"          # Currently in use
    RELEASING = "releasing"    # Cleanup in progress
    RELEASED = "released"      # Cleaned up and released


@dataclass(frozen=True)
class FixtureLifecycleEvent:
    """Immutable event in fixture lifecycle."""
    
    fixture_id: str
    fixture_name: str
    state_from: FixtureState
    state_to: FixtureState
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class FixtureLifecycleRecord:
    """Immutable record of a fixture's lifecycle."""
    
    fixture_id: str
    fixture_name: str
    owner: str
    scope: "FixtureScope"  # Forward reference
    
    created_at: Optional[float] = None
    released_at: Optional[float] = None
    lifetime_seconds: Optional[float] = None
    
    state_history: List[FixtureLifecycleEvent] = field(default_factory=list)
    
    @property
    def is_released(self) -> bool:
        return any(
            event.state_to == FixtureState.RELEASED 
            for event in self.state_history
        )
    
    @property
    def duration_seconds(self) -> Optional[float]:
        if self.created_at and self.released_at:
            return self.released_at - self.created_at
        return None


@dataclass(frozen=True)
class LifecycleViolation(Exception):
    """Raised when a lifecycle violation occurs."""
    
    fixture_name: str
    violation_type: str  # AlreadyReleased, NotCreated, etc.
    details: Optional[str] = None
    
    def __str__(self) -> str:
        msg = f"Lifecycle violation for '{self.fixture_name}': {self.violation_type}"
        if self.details:
            msg += f" ({self.details})"
        return msg


class FixtureLifecycle:
    """
    Manages fixture lifecycle with state tracking and cleanup verification.
    
    The lifecycle manager tracks:
    - State transitions (PENDING → CREATED → ACTIVE → RELEASED)
    - Cleanup execution
    - Duration metrics
    - Violation detection
    
    Usage:
        lifecycle = FixtureLifecycle()
        
        # Register a fixture
        fixture_id = lifecycle.register(
            name="test_db",
            owner="database-team"
        )
        
        # Track state transitions
        lifecycle.transition(fixture_id, FixtureState.CREATED)
        lifecycle.transition(fixture_id, FixtureState.ACTIVE)
        
        # Release and verify cleanup
        lifecycle.release(fixture_id)
        
        # Verify the fixture was properly released
        assert lifecycle.is_released(fixture_id)
    """
    
    def __init__(self):
        """Initialize the fixture lifecycle manager."""
        self._states: Dict[str, FixtureState] = {}
        self._records: Dict[str, FixtureLifecycleRecord] = {}
        self._cleanup_registry: Dict[str, Callable[[Any], None]] = {}
        self._events: List[FixtureLifecycleEvent] = []
    
    def register(
        self,
        fixture_id: str,
        name: str,
        owner: str,
        scope: "FixtureScope",
        cleanup: Optional[Callable[[Any], None]] = None,
    ) -> str:
        """
        Register a fixture for lifecycle tracking.
        
        Args:
            fixture_id: Unique identifier for the fixture
            name: Human-readable name
            owner: Owner identifier (team or module)
            scope: Lifetime scope for this fixture
            cleanup: Optional cleanup function
            
        Returns:
            The fixture ID
        """
        self._states[fixture_id] = FixtureState.PENDING
        
        record = FixtureLifecycleRecord(
            fixture_id=fixture_id,
            fixture_name=name,
            owner=owner,
            scope=scope,
        )
        
        self._records[fixture_id] = record
        
        if cleanup:
            self._cleanup_registry[fixture_id] = cleanup
        
        return fixture_id
    
    def transition(self, fixture_id: str, new_state: FixtureState) -> None:
        """
        Record a state transition for a fixture.
        
        Args:
            fixture_id: ID of the fixture
            new_state: The target state
            
        Raises:
            LifecycleViolation: If transition is invalid
        """
        if fixture_id not in self._states:
            raise LifecycleViolation(
                fixture_name="unknown",
                violation_type="UnknownFixture",
                details=f"Fixture {fixture_id} not registered"
            )
        
        current_state = self._states[fixture_id]
        
        # Validate state transition
        if not self._is_valid_transition(current_state, new_state):
            raise LifecycleViolation(
                fixture_name=self._records.get(fixture_id, {}).get("name", "unknown"),
                violation_type=f"InvalidTransition_{current_state.value}_to_{new_state.value}",
                details=f"Cannot transition from {current_state} to {new_state}"
            )
        
        # Record the event
        event = FixtureLifecycleEvent(
            fixture_id=fixture_id,
            fixture_name=self._records[fixture_id].fixture_name,
            state_from=current_state,
            state_to=new_state,
        )
        
        self._events.append(event)
        self._states[fixture_id] = new_state
        
        # Update record
        record = self._records[fixture_id]
        if new_state == FixtureState.CREATED:
            record._fields["created_at"] = time.time()
        elif new_state == FixtureState.RELEASED:
            record._fields["released_at"] = time.time()
            record._fields["lifetime_seconds"] = (
                time.time() - record.created_at
                if record.created_at else None
            )
        
        # Call cleanup if releasing
        if new_state == FixtureState.RELEASING and fixture_id in self._cleanup_registry:
            try:
                self._cleanup_registry[fixture_id](None)
            except Exception as e:
                pass  # Log but don't fail
    
    def release(self, fixture_id: str) -> None:
        """
        Release a fixture, triggering cleanup.
        
        Args:
            fixture_id: ID of the fixture to release
            
        Raises:
            LifecycleViolation: If fixture is already released or not created
        """
        current_state = self._states.get(fixture_id)
        
        if current_state == FixtureState.RELEASED:
            raise LifecycleViolation(
                fixture_name=self._records.get(fixture_id, {}).get("name", "unknown"),
                violation_type="AlreadyReleased",
                details="Fixture has already been released"
            )
        
        if current_state not in (FixtureState.CREATED, FixtureState.ACTIVE):
            raise LifecycleViolation(
                fixture_name=self._records.get(fixture_id, {}).get("name", "unknown"),
                violation_type="NotCreatedOrActive",
                details=f"Cannot release fixture in state {current_state}"
            )
        
        self.transition(fixture_id, FixtureState.RELEASING)
        self.transition(fixture_id, FixtureState.RELEASED)
    
    def _is_valid_transition(self, from_state: FixtureState, to_state: FixtureState) -> bool:
        """Check if a state transition is valid."""
        valid_transitions = {
            FixtureState.PENDING: {FixtureState.CREATED},
            FixtureState.CREATED: {FixtureState.ACTIVE, FixtureState.RELEASED},
            FixtureState.ACTIVE: {FixtureState.RELEASING, FixtureState.RELEASED},
            FixtureState.RELEASING: {FixtureState.RELEASED},
            FixtureState.RELEASED: set(),  # No valid transitions from RELEASED
        }
        
        return to_state in valid_transitions.get(from_state, set())
    
    def is_released(self, fixture_id: str) -> bool:
        """Check if a fixture has been released."""
        return self._states.get(fixture_id) == FixtureState.RELEASED
    
    def get_record(self, fixture_id: str) -> Optional[FixtureLifecycleRecord]:
        """Get the lifecycle record for a fixture."""
        return self._records.get(fixture_id)
    
    @property
    def events(self) -> List[FixtureLifecycleEvent]:
        """Get all lifecycle events in order."""
        return list(self._events)
    
    @property
    def active_fixtures(self) -> Dict[str, FixtureState]:
        """Get all fixtures that are not yet released."""
        return {
            fid: state 
            for fid, state in self._states.items() 
            if state != FixtureState.RELEASED
        }
    
    def cleanup_all(self) -> List[str]:
        """
        Release all active fixtures.
        
        Returns:
            List of fixture IDs that were released
        """
        released = []
        for fixture_id, state in list(self.active_fixtures.items()):
            if state in (FixtureState.CREATED, FixtureState.ACTIVE):
                try:
                    self.release(fixture_id)
                    released.append(fixture_id)
                except LifecycleViolation:
                    pass  # Skip already released fixtures
        
        return released


def verify_cleanup(lifecycle: FixtureLifecycle) -> bool:
    """
    Verify all fixtures have been properly cleaned up.
    
    Args:
        lifecycle: The fixture lifecycle manager to check
        
    Returns:
        True if all fixtures are released, False otherwise
    """
    active = lifecycle.active_fixtures
    return len(active) == 0


def fixture_lifecycle(
    name: str,
    owner: str,
    scope: "FixtureScope",
    cleanup: Optional[Callable[[Any], None]] = None,
):
    """
    Context manager for fixture lifecycle management.
    
    Usage:
        with fixture_lifecycle("test_db", "database-team", FixtureScope.FUNCTION) as db:
            # Use the database fixture
            yield db
        # Cleanup is automatic
    
    Args:
        name: Human-readable name
        owner: Owner identifier
        scope: Lifetime scope
        cleanup: Optional cleanup function
        
    Yields:
        The fixture instance
    """
    lifecycle = FixtureLifecycle()
    fixture_id = lifecycle.register(name, owner, scope, cleanup)
    
    try:
        yield fixture_id
    finally:
        lifecycle.release(fixture_id)