# Correlation & Causation Identities - Phase 3.19.7
# =====================================================

"""
Correlation and causation identity types for traceability across operations.

Every execution in Gordon should be:
    - Traceable through correlation IDs (operations belonging together)
    - Traced through causation chains (what created what)

CORRELATION & CAUSATION HIERARCHY:
    CorrelationId           - Operations belonging together
        └── CausationId         - What created what
            ├── ExecutionChainId  - Full chain of execution
            └── DependencyChainId - Dependencies between operations
            
INVARIANTS:
    COR-001: Correlation IDs group related operations
    COR-002: Causation IDs trace creation relationships
    COR-003: Chains enable complete traceability
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import uuid


# =============================================================================
# CORRELATION IDENTITY
# =============================================================================


@dataclass(frozen=True)
class CorrelationId:
    """
    Canonical identity for correlating related operations.
    
    Correlation IDs group together operations that belong to the same
    logical operation or request, even across different threads or processes.
    
    INVARIANTS:
        COR-001: All operations in a correlation share the same ID
        COR-002: Correlation IDs are globally unique
        COR-003: Correlation is transitive (A↔B and B↔C implies A↔C)
        
    PARAMETERS:
        value         - The actual UUID string
        scope         - Scope of correlation (request, transaction, session, etc.)
    """
    
    value: str = field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:20]}")
    scope: Optional[str] = None  # e.g., "request", "transaction", "session"
    
    @classmethod
    def generate(cls) -> "CorrelationId":
        """Generate a new correlation ID."""
        return cls()
    
    @classmethod
    def for_request(cls, value: str) -> "CorrelationId":
        """Create a correlation ID with request scope."""
        return cls(value=f"req_{value}", scope="request")
    
    @classmethod
    def for_transaction(cls, value: str) -> "CorrelationId":
        """Create a correlation ID with transaction scope."""
        return cls(value=f"txn_{value}", scope="transaction")
    
    @property
    def is_request(self) -> bool:
        """Check if this is a request-scoped correlation."""
        return self.scope == "request"
    
    @property
    def is_transaction(self) -> bool:
        """Check if this is a transaction-scoped correlation."""
        return self.scope == "transaction"


# =============================================================================
# CAUSATION IDENTITY
# =============================================================================


@dataclass(frozen=True)
class CausationId:
    """
    Canonical identity for causation relationships.
    
    Causation IDs trace which operation created or triggered another,
    forming a causal chain through the system.
    
    INVARIANTS:
        CAS-001: Every effect has exactly one direct cause
        CAS-002: Causation forms a directed acyclic graph (no cycles)
        CAS-003: Causation IDs are globally unique
        
    PARAMETERS:
        value         - The actual UUID string
        cause_value   - The ID of the causing operation
        effect_value  - The ID of the affected operation
    """
    
    value: str = field(default_factory=lambda: f"caus_{uuid.uuid4().hex[:20]}")
    cause_id: Optional[str] = None
    effect_id: Optional[str] = None
    
    @classmethod
    def generate(cls) -> "CausationId":
        """Generate a new causation ID."""
        return cls()
    
    @classmethod
    def for_cause_and_effect(
        cls,
        cause_value: str,
        effect_value: str,
    ) -> "CausationId":
        """Create a causation ID for a specific cause-effect pair."""
        hash_input = f"{cause_value}:{effect_value}"
        value = uuid.uuid5(uuid.NAMESPACE_DNS, hash_input).hex[:20]
        return cls(value=f"caus_{value}", cause_id=cause_value, effect_id=effect_value)


# =============================================================================
# EXECUTION CHAIN IDENTITY
# =============================================================================


@dataclass(frozen=True)
class ExecutionChainId:
    """
    Canonical identity for a chain of execution.
    
    An execution chain represents the complete sequence of operations
    that occurred as part of a single logical execution.
    
    INVARIANTS:
        EXE-001: Every operation belongs to exactly one execution chain
        EXE-002: Execution chains form linear sequences with causation links
        EXE-003: Chain IDs are globally unique
        
    PARAMETERS:
        value         - The actual UUID string
        root_id       - ID of the root/root cause operation
        length        - Number of operations in this chain
    """
    
    value: str = field(default_factory=lambda: f"chain_{uuid.uuid4().hex[:20]}")
    root_id: Optional[str] = None
    length: int = 1
    
    @classmethod
    def generate(cls, root_id: Optional[str] = None) -> "ExecutionChainId":
        """Generate a new execution chain ID."""
        return cls(root_id=root_id)
    
    @property
    def is_root(self) -> bool:
        """Check if this chain has no parent (is the root)."""
        return self.root_id is None


# =============================================================================
# DEPENDENCY CHAIN IDENTITY
# =============================================================================


@dataclass(frozen=True)
class DependencyChainId:
    """
    Canonical identity for a dependency resolution chain.
    
    Dependency chains track which dependencies were resolved to complete
    an operation, including transitive dependencies.
    
    INVARIANTS:
        DEP-001: Every operation has zero or more dependency chains
        DEP-002: Dependency chains form trees (no cycles in dependencies)
        DEP-003: Dependency chain IDs are globally unique
        
    PARAMETERS:
        value         - The actual UUID string
        dependent_id  - ID of the operation that depends on others
        depends_on_ids - List of dependency IDs
    """
    
    value: str = field(default_factory=lambda: f"dep_{uuid.uuid4().hex[:20]}")
    dependent_id: Optional[str] = None
    depends_on_ids: tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def generate(
        cls,
        dependent_id: Optional[str] = None,
        depends_on_ids: Optional[tuple[str, ...]] = None,
    ) -> "DependencyChainId":
        """Generate a new dependency chain ID."""
        return cls(
            dependent_id=dependent_id,
            depends_on_ids=depends_on_ids or tuple(),
        )


# =============================================================================
# TRACE IDENTITY
# =============================================================================


@dataclass(frozen=True)
class TraceId:
    """
    Canonical identity for a distributed trace.
    
    Trace IDs enable end-to-end tracing across service boundaries in
    distributed Gordon deployments.
    
    INVARIANTS:
        TRC-001: Every request has exactly one trace ID
        TRC-002: Trace IDs propagate across service boundaries
        TRC-003: All spans in a trace share the same trace ID
        
    PARAMETERS:
        value         - The actual UUID string
        parent_span   - Parent span ID (if any)
    """
    
    value: str = field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:20]}")
    parent_span_id: Optional[str] = None
    
    @classmethod
    def generate(cls) -> "TraceId":
        """Generate a new trace ID."""
        return cls()
    
    @property
    def is_root(self) -> bool:
        """Check if this is the root span (no parent)."""
        return self.parent_span_id is None


# =============================================================================
# SPAN IDENTITY
# =============================================================================


@dataclass(frozen=True)
class SpanId:
    """
    Canonical identity for a trace span.
    
    Spans represent individual operations within a distributed trace,
    with start/end timestamps and metadata.
    
    INVARIANTS:
        SPN-001: Every span belongs to exactly one trace
        SPN-002: Spans can have parent-child relationships
        SPN-003: Span IDs are unique within their trace
        
    PARAMETERS:
        value         - The actual UUID string  
        trace_id      - Parent trace ID
        parent_span   - Parent span ID (if any)
    """
    
    value: str = field(default_factory=lambda: f"span_{uuid.uuid4().hex[:20]}")
    trace_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    
    @classmethod
    def generate(cls, trace_id: Optional[str] = None) -> "SpanId":
        """Generate a new span ID."""
        return cls(trace_id=trace_id)


# =============================================================================
# CORRELATION REGISTRY
# =============================================================================


class CorrelationRegistry:
    """
    Registry for tracking correlation and causation relationships.
    
    Provides utilities for managing correlation groups, causation chains,
    and trace relationships.
    
    INVARIANTS:
        CR-001: Correlation IDs map to sets of related operation IDs
        CR-002: Causation forms a directed acyclic graph
        CR-003: Trace relationships are properly nested
        
    METHODS:
        correlate()         - Register correlation between operations
        cause()             - Register causation relationship
        get_correlated()    - Get all correlated operations
        get_causes()        - Get causal ancestors of an operation
        get_trace()         - Get complete trace for an operation
    """
    
    def __init__(self):
        self._correlations: dict[str, set[str]] = {}  # corr_id -> {operation_ids}
        self._causations: dict[str, Optional[str]] = {}  # effect_id -> cause_id
        self._traces: dict[str, list[SpanId]] = {}  # trace_id -> spans
    
    def correlate(self, correlation_id: str, operation_ids: list[str]) -> None:
        """Register operations as correlated under the given ID."""
        if correlation_id not in self._correlations:
            self._correlations[correlation_id] = set()
        self._correlations[correlation_id].update(operation_ids)
    
    def cause(self, effect_id: str, cause_id: Optional[str]) -> None:
        """Register a causation relationship."""
        self._causations[effect_id] = cause_id
    
    def get_correlated(self, correlation_id: str) -> set[str]:
        """Get all operation IDs correlated under the given ID."""
        return self._correlations.get(correlation_id, set())
    
    def get_causes(self, effect_id: str) -> list[tuple[str, ...]]:
        """
        Get causal chain for an operation.
        
        Returns list of cause IDs from most recent to root.
        """
        causes = []
        current = effect_id
        
        while current and current in self._causations:
            next_cause = self._causations[current]
            if next_cause:
                causes.append(next_cause)
            current = next_cause
            
        return causes
    
    def get_trace(self, trace_id: str) -> list[SpanId]:
        """Get all spans in a trace."""
        return self._traces.get(trace_id, [])
    
    def add_span_to_trace(self, span: SpanId) -> None:
        """Add a span to its trace."""
        if span.trace_id not in self._traces:
            self._traces[span.trace_id] = []
        self._traces[span.trace_id].append(span)
    
    def get_root_cause(self, effect_id: str) -> Optional[str]:
        """Get the root cause of an operation."""
        causes = self.get_causes(effect_id)
        return causes[-1] if causes else None


__all__ = [
    "CorrelationId",
    "CausationId",
    "ExecutionChainId",
    "DependencyChainId",
    "TraceId",
    "SpanId",
    "CorrelationRegistry",
]