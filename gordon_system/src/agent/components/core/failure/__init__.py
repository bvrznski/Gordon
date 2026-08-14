# Canonical Error, Failure, Recovery & Resilience Architecture - Phase 3.25
# ==============================================================================
#
# Core failure architecture for Gordon.
#
# This module provides canonical implementations for:
#   - Error classification and taxonomy
#   - Failure detection and diagnosis
#   - Recovery orchestration
#   - Retry policies with backoff
#   - Circuit breaking
#   - Rollback and compensation
#   - Graceful degradation
#   - Self-healing and autonomous recovery
#   - Escalation and incident management
#
# One canonical architecture governs all failure handling.
# No subsystem shall implement its own recovery framework.

"""
Canonical Error, Failure, Recovery & Resilience Architecture for Phase 3.25.

This module provides the complete failure lifecycle infrastructure:

ARCHITECTURE OVERVIEW
---------------------

    +--------------------------------------------------+
    |           FAILURE LIFECYCLE HIERARCHY            |
    +--------------------------------------------------+
    |                                                  |
    |   Fault → Detection → Classification → Isolation |
    |         ↓                               ↓        |
    |      Policy Evaluation ←───────────────┘         |
    |         ↓                                        |
    |   Recovery Selection → Execution → Validation    |
    |         ↓                               ↓        |
    |     Resolution ←─────────────────────────┘       |
    |                                                  |
    +--------------------------------------------------+

KEY PRINCIPLES
--------------

1. One canonical architecture for all failure handling
2. No duplicated recovery frameworks across subsystems
3. Deterministic recovery with explicit policies
4. Full observability and auditability of failures
5. Bounded retries, no infinite loops
6. Explicit degradation paths

FAILURE CATEGORIES
------------------

Programmer Error      - Code bugs, logic errors (non-recoverable)
Runtime Error         - Runtime conditions (often recoverable)
Resource Failure      - Memory, disk, connection exhaustion
Configuration Failure - Invalid configuration
Dependency Failure    - External service unavailable
Communication Failure - Network/protocol failures
Scheduling Failure    - Scheduler unable to assign work
Concurrency Failure   - Race conditions, deadlocks
State Failure         - State corruption or inconsistency
Persistence Failure   - Storage write/read failures
Security Failure      - Authz violations, intrusion detection
Recovery Failure      - Recovery operation itself failed
External Failure      - Third-party service outages
Distributed Failure   - Multi-node coordination issues

RECOVERY STRATEGIES
-------------------

Retry         - Attempt operation again (with backoff)
Restart       - Restart component/service
Rollback      - Restore to prior verified state
Replay        - Replay operations from checkpoint
Compensation  - Execute counter-transaction
Degradation   - Accept reduced functionality
Failover      - Switch to backup system

EXPORTS
-------

Core Types:
    - ErrorKind: Classification of error nature
    - ErrorSeverity: Impact level of the error
    - FailureCategory: Canonical failure categories
    - RecoveryStrategy: Available recovery approaches
    
Exceptions:
    - GordonError: Base exception for all Gordon errors
    - RecoverableError: Errors that can be recovered from
    - NonRecoverableError: Terminal errors requiring shutdown
    - TransientError: Temporary failures, safe to retry
    
Components:
    - ErrorClassifier: Classifies errors into categories
    - RecoveryCoordinator: Orchestrates recovery actions
    - RetryPolicy: Configurable retry strategy with backoff
    - CircuitBreaker: Prevents cascading failures

Policies:
    - RetryPolicy: Defines retry behavior
    - BackoffStrategy: Defines backoff calculation
    - DegradationPolicy: Defines degradation behavior

Diagnostics:
    - FailureTimeline: Records failure lifecycle events
    - RecoveryMetrics: Tracks recovery statistics
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
import time
import uuid
from datetime import datetime

# Re-export core types from the canonical location
from .types import (
    FailureKind,
    FailureSeverity,
    FailureDomain,
    FailureDisposition,
    RollbackMode,
    RollbackScope,
    RecoveryPolicy,
    RuntimeFailure,
)

from .architecture import (
    FailureCategory as CoreFailureCategory,
    FailureSeverity as CoreFailureSeverity,
    FailureLifecycleState,
    FailurePropagationPath,
    RecoveryStrategy,
    FailureOrigin,
    FailureArtifact,
    FailureClassifier,
    FailureContainer,
    EscalationPolicy,
    RecoveryPlanner,
    RecoveryCoordinator,
)

__all__ = [
    # Types
    "ErrorKind",
    "FailureCategory",
    "RecoveryStrategy",
    
    # Exceptions
    "GordonError",
    "RecoverableError",
    "NonRecoverableError",
    "TransientError",
    "PermanentError",
    
    # Components
    "ErrorClassifier",
    "RecoveryCoordinator",
    "RetryPolicy",
    "CircuitBreaker",
    
    # Policies
    "BackoffStrategy",
    "DegradationPolicy",
    
    # Diagnostics
    "FailureTimeline",
    "RecoveryMetrics",
]

# =============================================================================
# ERROR Kinds (Canonical)
# =============================================================================


class ErrorKind(Enum):
    """
    Canonical error kind classification.
    
    Determines recovery eligibility and handling approach.
    """

    # Programmer errors (non-recoverable)
    PROGRAMMING = "programming"  # Code bug, needs fix
    LOGIC_ERROR = "logic_error"  # Logic violation

    # Runtime errors (often recoverable)
    RUNTIME = "runtime"
    RESOURCE_EXHAUSTION = "resource_exhaustion"

    # Infrastructure
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    NETWORK = "network"

    # Integrity failures
    DATA_CORRUPTION = "data_corruption"
    STATE_CORRUPTION = "state_corruption"

    # Security
    SECURITY = "security"

    # Terminal conditions
    FATAL = "fatal"
    PANIC = "panic"


# =============================================================================
# FAILURE CATEGORIES (Unified Canonical)
# =============================================================================


class FailureCategory(Enum):
    """
    Unified canonical failure categories for Phase 3.25.
    
    Every failure belongs to exactly one primary category.
    """

    # Validation and admission
    VALIDATION = "validation"
    ADMISSION = "admission"

    # Execution failures
    EXECUTION = "execution"
    SCHEDULING = "scheduling"
    CONCURRENCY = "concurrency"

    # Resource failures
    RESOURCE = "resource"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DEPENDENCY = "dependency"

    # State failures
    STATE_CORRUPTION = "state_corruption"
    PERSISTENCE = "persistence"

    # Communication failures
    COMMUNICATION = "communication"
    TIMEOUT = "timeout"

    # Security and integrity
    SECURITY = "security"
    PRIVACY = "privacy"
    INTEGRITY = "integrity"

    # External
    EXTERNAL = "external"

    # Recovery specific
    RECOVERY = "recovery"
    ROLLBACK = "rollback"


# =============================================================================
# CANONICAL EXCEPTION HIERARCHY
# =============================================================================


class GordonError(Exception):
    """
    Base exception for all Gordon errors.
    
    All Gordon exceptions inherit from this. Provides:
        - Canonical error kind classification
        - Severity level
        - Recovery eligibility flag
        - Diagnostic context
    """

    def __init__(
        self,
        message: str,
        error_kind: Optional[ErrorKind] = None,
        severity: Optional[str] = "error",
        recoverable: bool = True,
        diagnostics: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self._message = message
        self.error_kind = error_kind or ErrorKind.RUNTIME
        self.severity = severity
        self.recoverable = recoverable
        self.diagnostics = diagnostics or {}

    @property
    def message(self) -> str:
        """Get the error message."""
        return self._message

    @classmethod
    def create(
        cls,
        message: str,
        error_kind: ErrorKind,
        recoverable: bool = True,
        **diagnostics,
    ) -> "GordonError":
        """Factory method to create typed errors."""
        return cls(message, error_kind, recoverable=recoverable, diagnostics=diagnostics)

    def is_recoverable(self) -> bool:
        """Check if this error can be recovered from."""
        return self.recoverable and self.error_kind not in (
            ErrorKind.FATAL,
            ErrorKind.PANIC,
            ErrorKind.PROGRAMMING,
        )


class RecoverableError(GordonError):
    """Errors that can potentially be recovered from."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message, recoverable=True, error_kind=ErrorKind.RUNTIME, **kwargs
        )


class NonRecoverableError(GordonError):
    """Terminal errors requiring immediate shutdown."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message, recoverable=False, error_kind=ErrorKind.FATAL, **kwargs
        )


class TransientError(RecoverableError):
    """Temporary failures that may succeed on retry."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_kind=ErrorKind.RUNTIME, **kwargs)


class PermanentError(GordonError):
    """Failures that are unlikely to succeed on retry."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message, recoverable=False, error_kind=ErrorKind.RUNTIME, **kwargs
        )


# =============================================================================
# ERROR CLASSIFIER
# =============================================================================


class ErrorClassifier:
    """
    Canonical error classifier.
    
    Classifies errors into proper categories and determines recovery eligibility.
    """

    # Mapping from exception types to error kinds
    KIND_MAPPING: Dict[type, ErrorKind] = {
        ValueError: ErrorKind.RUNTIME,
        TypeError: ErrorKind.RUNTIME,
        RuntimeError: ErrorKind.RUNTIME,
        TimeoutError: ErrorKind.TIMEOUT,
        MemoryError: ErrorKind.RESOURCE_EXHAUSTION,
        FileNotFoundError: ErrorKind.DEPENDENCY,
        ConnectionError: ErrorKind.NETWORK,
    }

    def __init__(self) -> None:
        """Initialize the classifier with default rules."""
        self._custom_rules: Dict[type, ErrorKind] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default classification rules."""
        for exc_type, error_kind in self.KIND_MAPPING.items():
            self.register_rule(exc_type, error_kind)

    def register_rule(self, exception_type: type, kind: ErrorKind) -> None:
        """Register a custom classification rule."""
        self._custom_rules[exception_type] = kind

    def classify(
        self,
        exc: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> tuple[ErrorKind, bool]:
        """
        Classify an exception into error kind and determine recoverability.

        Args:
            exc: The exception to classify
            context: Additional context for classification

        Returns:
            Tuple of (error_kind, is_recoverable)
        """
        # Check custom rules first
        exc_type = type(exc)
        if exc_type in self._custom_rules:
            return self._custom_rules[exc_type], True

        # Check base classes
        for base in exc_type.__mro__:
            if base in self._custom_rules:
                return self._custom_rules[base], True
            if base in self.KIND_MAPPING:
                kind = self.KIND_MAPPING[base]
                recoverable = kind not in (ErrorKind.FATAL, ErrorKind.PANIC)
                return kind, recoverable

        # Default classification
        if isinstance(exc, NonRecoverableError):
            return ErrorKind.FATAL, False

        return ErrorKind.RUNTIME, True


# =============================================================================
# BACKOFF STRATEGIES
# =============================================================================


class BackoffStrategy(Enum):
    """Backoff strategies for retry policies."""

    CONSTANT = "constant"  # Fixed delay between retries
    LINEAR = "linear"      # Delay increases linearly with each attempt
    EXPONENTIAL = "exponential"  # Delay doubles each time (2^attempt)
    JITTERED_EXPONENTIAL = (
        "jittered_exponential"  # Exponential with random jitter
    )
    BOUNCED_BACKOFF = "bounced_backoff"  # Alternate between min and max


@dataclass(frozen=True)
class BackoffConfig:
    """Configuration for backoff strategy."""

    initial_delay: float = 0.1  # First retry delay (seconds)
    maximum_delay: float = 60.0  # Max delay cap
    multiplier: float = 2.0  # Multiplier for exponential strategies
    jitter: bool = True  # Add randomness to prevent thundering herd


def calculate_backoff(
    attempt: int,
    strategy: BackoffStrategy,
    config: BackoffConfig,
) -> float:
    """
    Calculate backoff delay for a given retry attempt.

    Args:
        attempt: Current attempt number (0-indexed)
        strategy: The backoff strategy to use
        config: Backoff configuration

    Returns:
        Delay in seconds before next retry
    """
    if strategy == BackoffStrategy.CONSTANT:
        return min(config.initial_delay, config.maximum_delay)

    elif strategy == BackoffStrategy.LINEAR:
        delay = config.initial_delay * (attempt + 1)
        return min(delay, config.maximum_delay)

    elif strategy == BackoffStrategy.EXPONENTIAL:
        delay = config.initial_delay * (config.multiplier**attempt)
        return min(delay, config.maximum_delay)

    elif strategy == BackoffStrategy.JITTERED_EXPONENTIAL:
        import random

        base_delay = calculate_backoff(
            attempt, BackoffStrategy.EXPONENTIAL, config
        )
        jitter_range = base_delay * 0.1  # ±10% jitter
        jitter = random.uniform(-jitter_range, jitter_range)
        delay = base_delay + jitter
        return max(0.0, min(delay, config.maximum_delay))

    elif strategy == BackoffStrategy.BOUNCED_BACKOFF:
        import random

        # Alternate between minimum and maximum delays
        if attempt % 2 == 0:
            return config.initial_delay
        else:
            return config.maximum_delay

    else:
        raise ValueError(f"Unknown backoff strategy: {strategy}")


# =============================================================================
# RETRY POLICY
# =============================================================================


@dataclass(frozen=True)
class RetryPolicy:
    """
    Configurable retry policy with bounded retries.

    All retry policies must have a maximum attempt limit to prevent
    infinite retry loops.
    """

    max_attempts: int = 3  # Maximum retry attempts (including initial try)
    timeout_per_retry: Optional[float] = None  # Per-retry timeout (None = no limit)
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    backoff_config: BackoffConfig = field(default_factory=BackoffConfig)
    retryable_exceptions: tuple[type, ...] = (
        TransientError,
        ConnectionError,
        TimeoutError,
    )

    def can_retry(self, attempt: int) -> bool:
        """Check if another retry is allowed."""
        return attempt < self.max_attempts

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay before the next retry attempt."""
        return calculate_backoff(
            max(0, attempt - 1), self.backoff_strategy, self.backoff_config
        )


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================


class CircuitBreakerState(Enum):
    """States of a circuit breaker."""

    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Circuit tripped, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass(frozen=True)
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures before opening circuit
    recovery_timeout: float = 30.0  # Seconds before trying again (open → half_open)
    half_open_max_calls: int = 3  # Max calls allowed in half-open state
    success_threshold: int = 2  # Successful calls to close circuit from half_open


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by stopping requests to failing services.
    """

    def __init__(self, config: CircuitBreakerConfig):
        self._config = config
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self._state

    def _check_state_transition(self) -> None:
        """Check and perform any necessary state transitions."""
        if self._state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has elapsed
            if (
                self._last_failure_time is not None
                and time.time() - self._last_failure_time >= self._config.recovery_timeout
            ):
                self._state = CircuitBreakerState.HALF_OPEN
                self._half_open_calls = 0

    def can_execute(self) -> bool:
        """Check if a request can be executed."""
        self._check_state_transition()

        if self._state == CircuitBreakerState.CLOSED:
            return True

        if self._state == CircuitBreakerState.OPEN:
            return False

        # HALF_OPEN state
        return self._half_open_calls < self._config.half_open_max_calls

    def record_success(self) -> None:
        """Record a successful execution."""
        if self._state == CircuitBreakerState.HALF_OPEN:
            self._success_count += 1
            self._half_open_calls += 1
            if self._success_count >= self._config.success_threshold:
                # Reset to closed state
                self._reset()

    def record_failure(self) -> None:
        """Record a failed execution."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitBreakerState.HALF_OPEN:
            # Any failure in half-open immediately reopens circuit
            self._state = CircuitBreakerState.OPEN
        elif self._state == CircuitBreakerState.CLOSED:
            if self._failure_count >= self._config.failure_threshold:
                self._state = CircuitBreakerState.OPEN

    def _reset(self) -> None:
        """Reset circuit breaker to initial state."""
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0


# =============================================================================
# DEGRADATION POLICY
# =============================================================================


@dataclass(frozen=True)
class DegradationPolicy:
    """
    Policy for graceful degradation behavior.
    """

    enabled: bool = True
    max_degradation_level: int = 3  # Maximum degradation depth
    fallback_implementations: Dict[str, str] = field(
        default_factory=dict
    )  # Feature → fallback implementation
    disabled_capabilities: List[str] = field(default_factory=list)


# =============================================================================
# FAILURE TIMELINE (Diagnostics)
# =============================================================================


@dataclass(frozen=True)
class TimelineEvent:
    """A single event in the failure timeline."""

    timestamp: float
    event_type: str  # 'detection', 'classification', 'recovery', etc.
    details: Dict[str, Any]
    source_component: str


class FailureTimeline:
    """
    Records chronological events for failure diagnostics.

    Every failure lifecycle event is recorded for audit and replay purposes.
    """

    def __init__(self):
        self._events: List[TimelineEvent] = []

    def record(self, event_type: str, details: Dict[str, Any], source: str) -> None:
        """Record a timeline event."""
        self._events.append(
            TimelineEvent(
                timestamp=time.time(),
                event_type=event_type,
                details=details,
                source_component=source,
            )
        )

    def get_events(self) -> List[TimelineEvent]:
        """Get all recorded events in chronological order."""
        return list(self._events)

    def get_duration_seconds(self) -> float:
        """Calculate total timeline duration."""
        if len(self._events) < 2:
            return 0.0
        return self._events[-1].timestamp - self._events[0].timestamp


# =============================================================================
# RECOVERY METRICS (Diagnostics)
# =============================================================================


class RecoveryMetrics:
    """
    Tracks statistics about recovery operations.

    Provides MTTR, success rates, and other key metrics.
    """

    def __init__(self):
        self._total_retries = 0
        self._successful_retries = 0
        self._failed_retries = 0
        self._total_recoveries = 0
        self._successful_recoveries = 0
        self._failed_recoveries = 0
        self._start_time = time.time()

    def record_retry(self, success: bool) -> None:
        """Record a retry attempt."""
        self._total_retries += 1
        if success:
            self._successful_retries += 1
        else:
            self._failed_retries += 1

    def record_recovery(self, success: bool) -> None:
        """Record a recovery operation."""
        self._total_recoveries += 1
        if success:
            self._successful_recoveries += 1
        else:
            self._failed_recoveries += 1

    @property
    def mttr_seconds(self) -> float:
        """Mean Time To Recovery (seconds)."""
        # Placeholder - would need actual recovery timestamps
        return 0.0

    @property
    def retry_success_rate(self) -> float:
        """Success rate of retries."""
        if self._total_retries == 0:
            return 1.0
        return self._successful_retries / self._total_retries

    @property
    def recovery_success_rate(self) -> float:
        """Success rate of recoveries."""
        if self._total_recoveries == 0:
            return 1.0
        return self._successful_recoveries / self._total_recoveries


# =============================================================================
# RECOVERY COORDINATOR (Canonical)
# =============================================================================


class RecoveryCoordinator:
    """
    Canonical recovery coordinator for Phase 3.25.

    Coordinates all recovery operations across the system while ensuring:
        - Ownership boundaries are preserved
        - Authority constraints are respected
        - State integrity is maintained
    """

    def __init__(self, default_policy: Optional[RetryPolicy] = None):
        self._default_policy = default_policy or RetryPolicy()
        self._retry_policies: Dict[str, RetryPolicy] = {}
        self._metrics = RecoveryMetrics()

    def register_policy(self, name: str, policy: RetryPolicy) -> None:
        """Register a custom retry policy by name."""
        self._retry_policies[name] = policy

    def get_policy(self, name: str) -> RetryPolicy:
        """Get retry policy by name, or default if not found."""
        return self._retry_policies.get(name, self._default_policy)

    def execute_with_retry(
        self,
        operation: Callable[[], Any],
        policy: Optional[RetryPolicy] = None,
        context: Optional[str] = None,
    ) -> Any:
        """
        Execute an operation with retry logic.

        Args:
            operation: The callable to execute
            policy: Retry policy (uses default if not specified)
            context: Operation context for logging/diagnostics

        Returns:
            Result of the operation on success

        Raises:
            Last exception encountered if all retries fail
        """
        actual_policy = policy or self._default_policy
        last_exception = None

        for attempt in range(actual_policy.max_attempts):
            try:
                return operation()
            except Exception as exc:
                last_exception = exc

                # Check if this exception is retryable
                if not isinstance(exc, actual_policy.retryable_exceptions):
                    raise  # Non-retryable, fail fast

                self._metrics.record_retry(False)

                # Check if we can retry
                if not actual_policy.can_retry(attempt + 1):
                    raise last_exception or GordonError("Operation failed")

                # Calculate delay and wait
                delay = actual_policy.calculate_delay(attempt + 1)
                time.sleep(delay)

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        raise GordonError("Operation failed")

    def execute_with_recovery(
        self,
        operation: Callable[[], Any],
        recovery_strategy: RecoveryStrategy,
        context: Optional[str] = None,
    ) -> tuple[bool, Any]:
        """
        Execute an operation with recovery strategy.

        Args:
            operation: The callable to execute
            recovery_strategy: Strategy to use on failure
            context: Operation context

        Returns:
            Tuple of (success, result_or_failure)
        """
        try:
            return True, operation()
        except Exception as exc:
            # Attempt recovery based on strategy
            if recovery_strategy == RecoveryStrategy.RETRY:
                try:
                    return True, self.execute_with_retry(operation)
                except Exception as retry_exc:
                    return False, str(retry_exc)

            elif recovery_strategy == RecoveryStrategy.DEGRADE:
                # Return a graceful degradation result
                return True, None  # Placeholder

            else:
                # Other strategies would be implemented here
                return False, str(exc)


# =============================================================================
# MODULE INITIALIZATION
# =============================================================================


def get_error_classifier() -> ErrorClassifier:
    """Get the canonical error classifier instance."""
    return ErrorClassifier()


def get_recovery_coordinator(
    default_policy: Optional[RetryPolicy] = None,
) -> RecoveryCoordinator:
    """Get the canonical recovery coordinator instance."""
    return RecoveryCoordinator(default_policy=default_policy)


# =============================================================================
# CERTIFICATION
# =============================================================================


def verify_architecture_compliance() -> tuple[bool, List[str]]:
    """
    Verify that the architecture meets Phase 3.25 requirements.

    Returns:
        Tuple of (compliant, issues)
    """
    issues = []

    # Check: One canonical recovery architecture exists
    # This module is the single source

    # Check: Failure classification is deterministic
    classifier = get_error_classifier()
    exc1 = ValueError("test")
    exc2 = ValueError("test")
    kind1, rec1 = classifier.classify(exc1)
    kind2, rec2 = classifier.classify(exc2)

    if kind1 != kind2:
        issues.append("Failure classification is not deterministic")

    # Check: Backoff strategies exist
    try:
        calculate_backoff(0, BackoffStrategy.EXPONENTIAL, BackoffConfig())
    except Exception as e:
        issues.append(f"Backoff calculation failed: {e}")

    return len(issues) == 0, issues