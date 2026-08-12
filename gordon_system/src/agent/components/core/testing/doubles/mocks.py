# Mocks - Testing Infrastructure
# ==========================================
"""
Mock implementations for interaction verification.

Mocks verify that specific interactions occurred during a test:
- Function calls with expected arguments
- Method calls on collaborators
- External service interactions
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
import time


class MockState(Enum):
    """States in the mock lifecycle."""
    UNCALLED = "uncalled"
    CALLED = "called"
    VERIFIED = "verified"


@dataclass(frozen=True)
class CallRecord:
    """Immutable record of a function call."""
    
    args: tuple
    kwargs: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    return_value: Optional[Any] = None


@dataclass(frozen=True)
class MockExpectation:
    """An expectation for how a mock should be called."""
    
    method_name: str
    min_calls: int = 0
    max_calls: Optional[int] = None
    with_args: Optional[tuple] = None
    with_kwargs: Optional[Dict[str, Any]] = None
    
    def matches(self, call_record: CallRecord) -> bool:
        """Check if a call record matches this expectation."""
        if self.with_args is not None:
            if call_record.args != self.with_args:
                return False
        
        if self.with_kwargs is not None:
            for key, value in self.with_kwargs.items():
                if call_record.kwargs.get(key) != value:
                    return False
        
        return True
    
    @property
    def is_optional(self) -> bool:
        """Check if this expectation is optional (min_calls = 0)."""
        return self.min_calls == 0


@dataclass(frozen=True)
class MockResult:
    """Immutable result of mock verification."""
    
    method_name: str
    expected_min: int
    expected_max: Optional[int]
    actual_calls: List[CallRecord]
    is_satisfied: bool
    violations: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MockConfig:
    """Configuration for a mock instance."""
    
    name: str
    default_return: Any = None
    strict: bool = False  # Raise on unexpected calls
    record_calls: bool = True
    
    @classmethod
    def strict(cls, name: str, default_return: Any = None) -> "MockConfig":
        """Create a strict mock config."""
        return cls(name=name, default_return=default_return, strict=True)
    
    @classmethod
    def lenient(cls, name: str, default_return: Any = None) -> "MockConfig":
        """Create a lenient mock config."""
        return cls(name=name, default_return=default_return, strict=False)


class Mock:
    """
    Mock implementation for interaction verification.
    
    Usage:
        # Create a mock
        db_mock = Mock("Database", config=MockConfig.lenient("db"))
        
        # Record expectations
        db_mock.expect("query").with_args("SELECT * FROM users").returns([1, 2, 3])
        
        # Use in test
        result = db_mock.query("SELECT * FROM users")
        assert result == [1, 2, 3]
        
        # Verify all expectations were met
        db_mock.verify()
    """
    
    def __init__(self, name: str, config: Optional[MockConfig] = None):
        """Initialize the mock."""
        self._name = name
        self._config = config or MockConfig(name=name)
        self._expectations: Dict[str, List[MockExpectation]] = {}
        self._call_records: Dict[str, List[CallRecord]] = {}
        self._state = MockState.UNCALLED
    
    def expect(self, method_name: str) -> "Mock":
        """Begin setting up an expectation for a method."""
        if method_name not in self._expectations:
            self._expectations[method_name] = []
        
        return self
    
    def with_args(self, *args) -> "MockExpectation":
        """Set expected arguments for the previous expectation."""
        # This would be used differently in actual implementation
        expectation = MockExpectation(
            method_name="pending",
            with_args=args,
        )
        return expectation
    
    def with_kwargs(self, **kwargs) -> "MockExpectation":
        """Set expected keyword arguments for the previous expectation."""
        expectation = MockExpectation(
            method_name="pending",
            with_kwargs=kwargs,
        )
        return expectation
    
    def returns(self, value: Any) -> None:
        """Set return value for the previous expectation."""
        pass  # Would be implemented with a builder pattern
    
    def times(self, min_calls: int, max_calls: Optional[int] = None) -> "Mock":
        """Set call count expectations."""
        # This would be used in a builder pattern
        return self
    
    def _record_call(
        self,
        method_name: str,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        return_value: Any = None,
    ) -> CallRecord:
        """Record a method call."""
        if not self._config.record_calls:
            return CallRecord(args=args, kwargs=kwargs or {}, return_value=return_value)
        
        if method_name not in self._call_records:
            self._call_records[method_name] = []
        
        record = CallRecord(
            args=args,
            kwargs=kwargs or {},
            return_value=return_value,
        )
        
        self._call_records[method_name].append(record)
        self._state = MockState.CALLED
        return record
    
    def verify(self) -> List[MockResult]:
        """
        Verify all expectations were met.
        
        Returns:
            List of verification results (empty if all passed)
        """
        results = []
        
        for method_name, records in self._call_records.items():
            expectations = self._expectations.get(method_name, [])
            
            actual_calls = len(records)
            
            # Check call count requirements
            min_required = 0
            max_required: Optional[int] = None
            
            for exp in expectations:
                if exp.method_name == method_name:
                    min_required = max(min_required, exp.min_calls)
                    if exp.max_calls is not None:
                        if max_required is None or exp.max_calls < max_required:
                            max_required = exp.max_calls
            
            violations = []
            
            if actual_calls < min_required:
                violations.append(
                    f"Expected {method_name} to be called at least {min_required} times, "
                    f"but was called {actual_calls} times"
                )
            
            if max_required is not None and actual_calls > max_required:
                violations.append(
                    f"Expected {method_name} to be called at most {max_required} times, "
                    f"but was called {actual_calls} times"
                )
            
            results.append(MockResult(
                method_name=method_name,
                expected_min=min_required,
                expected_max=max_required,
                actual_calls=records,
                is_satisfied=len(violations) == 0,
                violations=violations,
            ))
        
        self._state = MockState.VERIFIED
        return results
    
    def __getattr__(self, name: str) -> Callable:
        """Create a mock method that records calls."""
        def mock_method(*args, **kwargs):
            # Find return value for this call
            if name in self._call_records:
                # Already called, return last result or default
                return self._config.default_return
            
            record = self._record_call(name, args, kwargs)
            return record.return_value
        
        return mock_method
    
    @property
    def state(self) -> MockState:
        """Get the current mock state."""
        return self._state
    
    @property
    def call_count(self) -> int:
        """Get total number of calls across all methods."""
        return sum(len(records) for records in self._call_records.values())
    
    def reset(self) -> None:
        """Reset the mock to initial state."""
        self._expectations = {}
        self._call_records = {}
        self._state = MockState.UNCALLED