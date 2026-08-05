# Stubs - Testing Infrastructure
# ==========================================
"""
Stub implementations for providing answers without behavior.

Stubs are simpler than fakes:
- Return predefined values
- Don't implement full behavior
- Used to answer questions, not perform actions
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass(frozen=True)
class StubConfig:
    """Configuration for a stub instance."""
    
    name: str
    default_response: Optional[Any] = None
    
    @classmethod
    def with_default(cls, name: str, default: Any) -> "StubConfig":
        """Create a stub config with a default response."""
        return cls(name=name, default_response=default)


@dataclass(frozen=True)
class StubResult:
    """Immutable result from a stub operation."""
    
    success: bool
    value: Optional[Any] = None
    error_message: Optional[str] = None


class Stub:
    """
    Base class for stub implementations.
    
    Stubs provide answers without behavior:
    - Always return what they're told to return
    - Don't perform validation or processing
    - Used to isolate the unit under test
    
    Usage:
        stub = Stub("database", default_response=[])
        
        result = stub.query("SELECT * FROM users")
        assert result == []  # Always returns configured response
    """
    
    def __init__(self, name: str, config: Optional[StubConfig] = None):
        """Initialize the stub."""
        self._name = name
        self._config = config or StubConfig(name=name)
        self._responses: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Get the stub's name."""
        return self._name
    
    def set_response(self, method_name: str, value: Any) -> None:
        """Set a response for a specific method."""
        self._responses[method_name] = value
    
    def get_response(self, method_name: str) -> Optional[Any]:
        """Get the configured response for a method."""
        return self._responses.get(method_name, self._config.default_response)
    
    def __getattr__(self, name: str) -> Any:
        """Return stubbed responses for any attribute/method."""
        return self._responses.get(name, self._config.default_response)


class DatabaseStub(Stub):
    """
    A database stub that returns predefined results.
    
    Usage:
        db = DatabaseStub()
        
        # Configure responses
        db.set_query("SELECT * FROM users", [
            User(id=1, name="Alice"),
            User(id=2, name="Bob")
        ])
        
        # Execute query (returns stubbed result)
        result = db.query("SELECT * FROM users")
    """
    
    def __init__(self, config: Optional[StubConfig] = None):
        """Initialize the database stub."""
        super().__init__("database_stub", config or StubConfig(name="database_stub"))
        self._queries: Dict[str, List[Any]] = {}
        self._inserts: List[Dict[str, Any]] = []
    
    def set_query(self, sql: str, results: List[Any]) -> None:
        """Configure query response."""
        self._queries[sql] = results
    
    def query(self, sql: str) -> List[Any]:
        """Execute a query (stubbed)."""
        return list(self._queries.get(sql, []))
    
    def execute(self, sql: str, params: Optional[tuple] = None) -> int:
        """Execute a statement, return affected rows."""
        self._inserts.append({"sql": sql, "params": params})
        return 1 if params else 0
    
    def get_inserts(self) -> List[Dict[str, Any]]:
        """Get all inserts that were executed."""
        return list(self._inserts)


class ServiceStub(Stub):
    """
    A service stub for external dependencies.
    
    Usage:
        api = ServiceStub("external_api")
        
        api.set_response("get_user", {"id": 1, "name": "Alice"})
        
        result = api.get_user(user_id=1)
    """
    
    def __init__(self, name: str, config: Optional[StubConfig] = None):
        """Initialize the service stub."""
        super().__init__(name, config or StubConfig(name=name))
        self._call_log: List[Dict[str, Any]] = []
    
    def record_call(self, method_name: str, args: tuple, kwargs: Dict[str, Any]) -> None:
        """Log a method call."""
        self._call_log.append({
            "method": method_name,
            "args": args,
            "kwargs": kwargs,
            "timestamp": __import__("time").time(),
        })
    
    def get_calls(self) -> List[Dict[str, Any]]:
        """Get all recorded calls."""
        return list(self._call_log)
    
    def clear(self) -> None:
        """Clear the call log."""
        self._call_log.clear()


class TimeStub(Stub):
    """
    A time stub that provides controlled time values.
    
    Usage:
        time_stub = TimeStub()
        
        # Set specific time
        time_stub.set_now(1000.0)
        
        now = time_stub.now()
        assert now == 1000.0
    """
    
    def __init__(self, config: Optional[StubConfig] = None):
        """Initialize the time stub."""
        super().__init__("time_stub", config or StubConfig(name="time_stub"))
        self._now_value: float = 0.0
    
    def set_now(self, timestamp: float) -> None:
        """Set the current time."""
        self._now_value = timestamp
    
    def now(self) -> float:
        """Get the stubbed current time."""
        return self._now_value
    
    def advance(self, seconds: float) -> None:
        """Advance the stubbed time."""
        self._now_value += seconds


class ConfigStub(Stub):
    """
    A configuration stub for testing with controlled settings.
    
    Usage:
        config = ConfigStub()
        
        config.set("database.host", "localhost")
        config.set("database.port", 5432)
        
        host = config.get("database.host")
        assert host == "localhost"
    """
    
    def __init__(self, config: Optional[StubConfig] = None):
        """Initialize the config stub."""
        super().__init__("config_stub", config or StubConfig(name="config_stub"))
        self._settings: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._settings[key] = value
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value."""
        return self._settings.get(key, default)
    
    def has(self, key: str) -> bool:
        """Check if a setting exists."""
        return key in self._settings
    
    def clear(self) -> None:
        """Clear all settings."""
        self._settings.clear()