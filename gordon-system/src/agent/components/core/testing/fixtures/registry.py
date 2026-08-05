# Fixture Registry - Testing Infrastructure
# ==========================================
"""
FixtureRegistry: Manages fixtures with dependency graph and lifecycle.

The FixtureRegistry owns:
- Fixture registration and discovery
- Fixture dependency resolution (DAG)
- Fixture scope management (function, class, module, session)
- Fixture cleanup verification

This implements fixture architecture following best practices:
- Fixtures represent runtime structure
- Composable builders for test data
- Protocol-aware fakes
- Clear ownership tracking
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Callable, Any
from enum import Enum
import uuid
import time


class FixtureScope(Enum):
    """Fixture lifecycle scope."""
    FUNCTION = "function"   # Created per test function
    CLASS = "class"         # Created per test class
    MODULE = "module"       # Created per module
    SESSION = "session"     # Created once per test session


@dataclass(frozen=True)
class FixtureRegistration:
    """Immutable registration of a fixture."""
    
    fixture_id: str
    name: str
    factory: Callable[[], Any]
    scope: FixtureScope
    owner: str  # Team or module responsible for this fixture
    dependencies: List[str] = field(default_factory=list)  # Fixture IDs this depends on
    cleanup: Optional[Callable[[Any], None]] = None  # Cleanup function
    creation_time: float = field(default_factory=time.time)
    
    def __hash__(self) -> int:
        return hash(self.fixture_id)


@dataclass(frozen=True)
class FixtureResult:
    """Immutable result of fixture execution."""
    
    fixture_id: str
    name: str
    value: Any
    scope: FixtureScope
    owner: str
    created_at: float
    lifetime_seconds: Optional[float] = None
    
    def release(self) -> None:
        """Mark fixture as released."""
        pass  # Immutable - just record the time


@dataclass(frozen=True)
class FixtureDependencyError(Exception):
    """Raised when fixture dependencies cannot be resolved."""
    
    fixture_name: str
    missing_dependencies: List[str]
    
    def __str__(self) -> str:
        return f"Cannot resolve fixtures for '{self.fixture_name}': missing {self.missing_dependencies}"


@dataclass(frozen=True)
class FixtureCycleError(Exception):
    """Raised when fixture dependency cycle is detected."""
    
    cycle: List[str]
    
    def __str__(self) -> str:
        return f"Fixture dependency cycle detected: {' → '.join(self.cycle)}"


class FixtureRegistry:
    """
    Manages fixtures with dependency graph and lifecycle control.
    
    The registry implements:
    - Fixed scope-based fixture lifetime
    - Dependency resolution using topological sort
    - Cycle detection to prevent infinite loops
    - Cleanup verification for proper resource management
    
    Usage:
        registry = FixtureRegistry()
        
        @registry.fixture(scope=FixtureScope.FUNCTION, owner="testing-team")
        def test_data():
            return {"key": "value"}
        
        # Fixtures are automatically resolved by dependencies
        result = registry.get_fixture("dependent_fixture", 
                                       depends_on=["test_data"])
    """
    
    def __init__(self):
        """Initialize the fixture registry."""
        self._registrations: Dict[str, FixtureRegistration] = {}
        self._instances: Dict[FixtureScope, Dict[str, Any]] = {
            scope: {} for scope in FixtureScope
        }
        self._cleanup_queue: List[Callable[[Any], None]] = []
    
    def register_fixture(
        self,
        name: str,
        factory: Callable[[], Any],
        scope: FixtureScope = FixtureScope.FUNCTION,
        owner: str = "unknown",
        dependencies: Optional[List[str]] = None,
        cleanup: Optional[Callable[[Any], None]] = None,
    ) -> str:
        """
        Register a new fixture with the registry.
        
        Args:
            name: Human-readable name for the fixture
            factory: Function that creates the fixture instance
            scope: Lifetime scope for this fixture
            owner: Owner identifier (team or module)
            dependencies: List of fixture names this depends on
            cleanup: Optional cleanup function
            
        Returns:
            Fixture ID (unique identifier)
        """
        fixture_id = f"fixture_{uuid.uuid4().hex[:8]}"
        
        registration = FixtureRegistration(
            fixture_id=fixture_id,
            name=name,
            factory=factory,
            scope=scope,
            owner=owner,
            dependencies=dependencies or [],
            cleanup=cleanup,
        )
        
        self._registrations[fixture_id] = registration
        return fixture_id
    
    def get_fixture(self, fixture_id: str, dependencies: Optional[Dict[str, Any]] = None) -> Any:
        """
        Get a fixture instance, resolving its dependencies.
        
        Args:
            fixture_id: ID of the fixture to retrieve
            dependencies: Pre-resolved dependency instances
            
        Returns:
            The fixture instance
            
        Raises:
            FixtureDependencyError: If dependencies cannot be resolved
            FixtureCycleError: If circular dependencies are detected
        """
        if fixture_id not in self._registrations:
            raise ValueError(f"Unknown fixture ID: {fixture_id}")
        
        registration = self._registrations[fixture_id]
        scope = registration.scope
        
        # Check cache for this scope
        cached = self._instances[scope].get(fixture_id)
        if cached is not None:
            return cached
        
        # Resolve dependencies first (topological sort)
        resolved_deps = self._resolve_dependencies(
            fixture_id, 
            set(), 
            dependencies or {}
        )
        
        # Create the instance
        try:
            instance = registration.factory()
            
            # Store in cache for scope lifetime
            self._instances[scope][fixture_id] = instance
            
            # Register cleanup if provided
            if registration.cleanup:
                self._cleanup_queue.append(registration.cleanup)
            
            return instance
            
        except Exception as e:
            raise RuntimeError(f"Failed to create fixture '{registration.name}': {e}")
    
    def _resolve_dependencies(
        self,
        fixture_id: str,
        visiting: Set[str],
        pre_resolved: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve all dependencies for a fixture using topological sort."""
        registration = self._registrations[fixture_id]
        resolved = dict(pre_resolved)
        
        # Track visiting for cycle detection
        if fixture_id in visiting:
            cycle_path = list(visiting) + [fixture_id]
            raise FixtureCycleError(cycle=cycle_path)
        
        visiting.add(fixture_id)
        
        try:
            for dep_id in registration.dependencies:
                if dep_id not in resolved:
                    if dep_id not in self._registrations:
                        raise FixtureDependencyError(
                            fixture_name=registration.name,
                            missing_dependencies=[dep_id]
                        )
                    resolved[dep_id] = self.get_fixture(dep_id, resolved)
            
            return resolved
            
        finally:
            visiting.remove(fixture_id)
    
    def cleanup(self) -> None:
        """Clean up all fixtures in reverse creation order."""
        while self._cleanup_queue:
            cleanup_fn = self._cleanup_queue.pop()
            try:
                cleanup_fn(None)  # Instance may already be deleted
            except Exception:
                pass  # Ignore cleanup errors
    
    @property
    def registrations(self) -> Dict[str, FixtureRegistration]:
        """Get all registered fixtures."""
        return dict(self._registrations)
    
    def get_fixtures_by_scope(self, scope: FixtureScope) -> List[FixtureRegistration]:
        """Get all fixtures for a specific scope."""
        return [
            reg for reg in self._registrations.values() 
            if reg.scope == scope
        ]
    
    def verify_cleanup(self, fixture_id: str) -> bool:
        """
        Verify that a fixture has been properly cleaned up.
        
        Args:
            fixture_id: ID of the fixture to check
            
        Returns:
            True if cleaned up, False otherwise
        """
        # Check if still in any instance cache
        for scope_instances in self._instances.values():
            if fixture_id in scope_instances:
                return False
        
        return True


class FixtureBuilder:
    """
    Builder pattern for creating composable fixtures.
    
    Usage:
        builder = FixtureBuilder()
        
        data = (
            builder.add("key", "value")
            .add("count", 42)
            .build()
        )
        
        # Compose with other builders
        full_data = builder.compose(
            {"nested": {"data": data}}
        ).build()
    """
    
    def __init__(self):
        """Initialize the fixture builder."""
        self._data: Dict[str, Any] = {}
    
    def add(self, key: str, value: Any) -> "FixtureBuilder":
        """Add a key-value pair to the fixture data."""
        self._data[key] = value
        return self
    
    def update(self, data: Dict[str, Any]) -> "FixtureBuilder":
        """Update with multiple key-value pairs."""
        self._data.update(data)
        return self
    
    def compose(self, other: Dict[str, Any]) -> "FixtureBuilder":
        """Compose with another dictionary (deep merge)."""
        # Simple shallow merge for now
        result = FixtureBuilder()
        result._data = dict(self._data)
        result._data.update(other)
        return result
    
    def build(self) -> Dict[str, Any]:
        """Build the final fixture data."""
        return dict(self._data)


def fixture(
    scope: FixtureScope = FixtureScope.FUNCTION,
    owner: str = "unknown",
    dependencies: Optional[List[str]] = None,
    cleanup: Optional[Callable[[Any], None]] = None,
) -> Callable[[Callable[[], Any]], str]:
    """
    Decorator to register a fixture.
    
    Usage:
        @fixture(scope=FixtureScope.FUNCTION, owner="testing-team")
        def test_data():
            return {"key": "value"}
    """
    def decorator(factory: Callable[[], Any]) -> str:
        registry = FixtureRegistry()
        return registry.register_fixture(
            name=factory.__name__,
            factory=factory,
            scope=scope,
            owner=owner,
            dependencies=dependencies or [],
            cleanup=cleanup,
        )
    return decorator