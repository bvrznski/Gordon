# Alerting Network Dependencies
# =============================

"""
Immutable dependency container for AlertingNetwork.

Dependencies are narrow, well-defined interfaces. They do NOT include:
- Concrete ExecutionThread
- Concrete ExecutionLoop
- scheduler implementation
- Executive Network
- FocusingNetwork
- SalienceNetwork
- Perception implementation
"""

from __future__ import annotations

from typing import Protocol, Optional
from abc import abstractmethod
from datetime import datetime


class ClockProtocol(Protocol):
    """
    Abstraction for time source.
    
    Allows the network to receive timestamps without depending on wall-clock
    implementations directly. This enables deterministic testing and flexible
    time management in simulations.
    """
    
    @abstractmethod
    def now(self) -> datetime:
        """Return current timestamp."""
        ...


class IdentityProvider(Protocol):
    """
    Abstraction for ID generation.
    
    Provides unique identifiers for assessments, inputs, and provenance
    tracking without embedding implementation details.
    """
    
    @abstractmethod
    def generate_assessment_id(self) -> str:
        """Generate a unique assessment ID."""
        ...
    
    @abstractmethod
    def generate_correlation_id(self) -> str:
        """Generate a correlation ID for traceability."""
        ...


class MetricsPort(Protocol):
    """
    Port for recording diagnostic metrics.
    
    The network may report metrics through this port but does NOT own them.
    Downstream systems decide how to aggregate and display metrics.
    """
    
    @abstractmethod
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        ...
    
    @abstractmethod
    def record_histogram(self, name: str, value: float) -> None:
        """Record a histogram value (e.g., demand score)."""
        ...


class TracePort(Protocol):
    """
    Port for distributed tracing.
    
    Allows the network to contribute trace events without owning the tracing
    infrastructure. Trace propagation is controlled by higher layers.
    """
    
    @abstractmethod
    def span(self, name: str, **kwargs) -> Optional[object]:
        """Begin a new trace span (or return None if tracing disabled)."""
        ...


class AlertingNetworkDependencies:
    """
    Immutable container for AlertingNetwork dependencies.
    
    All fields are optional and may be None. The network gracefully handles
    missing dependencies by omitting corresponding functionality.
    """
    
    def __init__(
        self,
        clock: Optional[ClockProtocol] = None,
        identity_provider: Optional[IdentityProvider] = None,
        metrics_port: Optional[MetricsPort] = None,
        trace_port: Optional[TracePort] = None,
    ):
        """
        Initialize dependencies.
        
        Args:
            clock: Time source for timestamps. If None, caller-supplied
                timestamps are used directly.
            identity_provider: ID generator. If None, IDs must be supplied
                by the caller.
            metrics_port: Metrics recorder. If None, no metrics are recorded.
            trace_port: Tracing port. If None, no tracing occurs.
        """
        self._clock = clock
        self._identity_provider = identity_provider
        self._metrics_port = metrics_port
        self._trace_port = trace_port

    @property
    def clock(self) -> Optional[ClockProtocol]:
        """Return the configured ClockProtocol."""
        return self._clock

    @property
    def identity_provider(self) -> Optional[IdentityProvider]:
        """Return the configured IdentityProvider."""
        return self._identity_provider

    @property
    def metrics_port(self) -> Optional[MetricsPort]:
        """Return the configured MetricsPort."""
        return self._metrics_port

    @property
    def trace_port(self) -> Optional[TracePort]:
        """Return the configured TracePort."""
        return self._trace_port

    def is_empty(self) -> bool:
        """Return True if no dependencies are configured."""
        return (
            self._clock is None and
            self._identity_provider is None and
            self._metrics_port is None and
            self._trace_port is None
        )