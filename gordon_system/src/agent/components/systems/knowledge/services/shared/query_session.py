"""Query Session - Phase 6.9 Part 2 Section 2.

This module implements the canonical contract for query sessions that execute
within Knowledge Service layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# QUERY KINDS - Phase 6.9 Part 1 Section 3
# =============================================================================


class QueryKind(Enum):
    """
    Kinds of Knowledge Queries.
    
    Semantic Lookups:
        EXACT       -> Exact identity match lookup
        SEMANTIC    -> Semantic similarity based lookup
        STRUCTURAL  -> Structure-based pattern matching
    
    Graph Operations:
        ONTOLOGY    -> Ontology navigation and inference
        GRAPH       -> General graph traversal query
        DEPENDENCY  -> Dependency chain analysis
    
    Temporal and Causal:
        TEMPORAL    -> Time-ordered queries
        CAUSAL      -> Causality chain queries
    
    Complex Queries:
        MULTI_LAYER -> Multi-layer semantic queries
    """
    
    EXACT = "exact"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    ONTOLOGY = "ontology"
    GRAPH = "graph"
    DEPENDENCY = "dependency"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    MULTI_LAYER = "multi_layer"
    UNKNOWN = "unknown"


# =============================================================================
# ORDERING DIRECTIONS - Phase 6.9 Part 1 Section 4
# =============================================================================


class OrderingDirection(Enum):
    """Directions for query result ordering."""
    
    ASCENDING = "ascending"
    DESCENDING = "descending"


# =============================================================================
# CONSTRAINT TYPE - Phase 6.9 Part 1 Section 3
# =============================================================================


@dataclass(frozen=True)
class Constraint:
    """
    Query constraint specification.
    
    Fields:
        field_name: Name of the field to constrain
        operator: Comparison operator (equals, contains, in, etc.)
        value: Value to compare against
        negate: If True, negate the constraint logic
    """
    
    field_name: str
    operator: str  # "equals", "contains", "in", "gt", "lt", "starts_with", etc.
    value: Any
    negate: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert constraint to dictionary."""
        return {
            "field_name": self.field_name,
            "operator": self.operator,
            "value": str(self.value) if not isinstance(self.value, (dict, list)) else self.value,
            "negate": self.negate,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Constraint:
        """Create constraint from dictionary."""
        return cls(
            field_name=data.get("field_name", ""),
            operator=data.get("operator", "equals"),
            value=data.get("value", None),
            negate=bool(data.get("negate", False)),
        )


# =============================================================================
# KNOWLEDGE QUERY - Phase 6.9 Part 1 Section 1
# =============================================================================


@dataclass(frozen=True)
class KnowledgeQuery:
    """
    Query definition for Knowledge Services.
    
    Queries remain side-effect free and deterministic per QUERY-LAW-003.
    
    Fields:
        query_identity: Unique identifier for this query
        query_kind: Kind of query (exact, semantic, structural, etc.)
        target_artifacts: Types of artifacts to retrieve
        constraints: Filtering constraints on results
        ordering: Result ordering specifications
        execution_plan: Optional execution plan (for complex queries)
        
    Invariants:
        * Queries remain immutable once created
        * Execution is side-effect free
        * Equivalent queries produce equivalent results
    """
    
    query_identity: str  # Unique identifier
    
    # Query kind (required)
    query_kind: QueryKind
    
    # Target artifacts (optional - if None, all supported types)
    target_artifacts: Optional[Tuple[str, ...]] = None
    
    # Constraints
    constraints: Tuple[Constraint, ...] = field(default_factory=tuple)
    
    # Ordering specifications
    ordering: List[Tuple[str, str]] = field(default_factory=list)  # [(field, direction)]
    
    # Execution metadata
    execution_plan: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Validate query after creation."""
        if not self.query_identity:
            raise ValueError("query_identity cannot be empty")
    
    @property
    def is_exact(self) -> bool:
        """Check if this is an exact match query."""
        return self.query_kind == QueryKind.EXACT
    
    @property
    def is_semantic(self) -> bool:
        """Check if this is a semantic similarity query."""
        return self.query_kind == QueryKind.SEMANTIC
    
    def add_constraint(
        self,
        field_name: str,
        operator: str,
        value: Any,
        negate: bool = False,
    ) -> "KnowledgeQuery":
        """Add a constraint and return new query."""
        new_constraints = tuple(list(self.constraints) + [
            Constraint(field_name, operator, value, negate),
        ])
        return KnowledgeQuery(
            query_identity=self.query_identity,
            query_kind=self.query_kind,
            target_artifacts=self.target_artifacts,
            constraints=new_constraints,
            ordering=list(self.ordering),
            execution_plan=self.execution_plan,
        )
    
    def add_ordering(self, field_name: str, direction: str) -> "KnowledgeQuery":
        """Add an ordering specification and return new query."""
        new_ordering = list(self.ordering) + [(field_name, direction)]
        return KnowledgeQuery(
            query_identity=self.query_identity,
            query_kind=self.query_kind,
            target_artifacts=self.target_artifacts,
            constraints=self.constraints,
            ordering=new_ordering,
            execution_plan=self.execution_plan,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary for serialization."""
        return {
            "query_identity": self.query_identity,
            "query_kind": self.query_kind.value,
            "target_artifacts": list(self.target_artifacts) if self.target_artifacts else None,
            "constraints": [c.to_dict() for c in self.constraints],
            "ordering": list(self.ordering),
            "execution_plan": self.execution_plan,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeQuery":
        """Create query from dictionary."""
        constraints = []
        for c_data in data.get("constraints", []):
            if isinstance(c_data, dict):
                constraints.append(Constraint.from_dict(c_data))
        
        return cls(
            query_identity=data.get("query_identity", str(uuid.uuid4())),
            query_kind=QueryKind(data.get("query_kind", "unknown")),
            target_artifacts=tuple(data.get("target_artifacts", [])) if data.get("target_artifacts") else None,
            constraints=tuple(constraints),
            ordering=list(data.get("ordering", [])),
            execution_plan=data.get("execution_plan"),
        )
    
    @classmethod
    def create_exact(
        cls,
        target_identity: str,
        target_artifact_type: Optional[str] = None,
    ) -> "KnowledgeQuery":
        """Create an exact match query."""
        return cls(
            query_identity=f"query:{uuid.uuid4().hex[:16]}",
            query_kind=QueryKind.EXACT,
            target_artifacts=(target_artifact_type,) if target_artifact_type else None,
            constraints=(
                Constraint("identity", "equals", target_identity),
            ),
        )
    
    @classmethod
    def create_semantic(
        cls,
        semantic_text: str,
        target_artifact_type: Optional[str] = None,
        min_similarity: float = 0.5,
    ) -> "KnowledgeQuery":
        """Create a semantic similarity query."""
        return cls(
            query_identity=f"query:{uuid.uuid4().hex[:16]}",
            query_kind=QueryKind.SEMANTIC,
            target_artifacts=(target_artifact_type,) if target_artifact_type else None,
            constraints=(
                Constraint("semantic_text", "contains", semantic_text),
                Constraint("similarity", "gt", min_similarity),
            ),
        )


# =============================================================================
# QUERY SESSION - Phase 6.9 Part 2 Section 2
# =============================================================================


@dataclass(frozen=True)
class QuerySession:
    """
    Session for executing queries within Knowledge Services.
    
    Sessions preserve execution history and diagnostics per QUERY-LAW-005, QUERY-LAW-006.
    
    Fields:
        session_identity: Unique identifier for this session
        executed_queries: List of queries executed in this session
        participating_services: Services that participated in query execution
        execution_plan: Complete execution plan used (if any)
        results: Results from all queries
        diagnostics: Execution diagnostics and metrics
        
    Invariants:
        * Session is immutable - new sessions created for modifications
        * Query provenance remains complete
        * Execution history is traceable
    """
    
    session_identity: str  # Unique identifier
    
    # Queries executed (required)
    executed_queries: Tuple[KnowledgeQuery, ...]
    
    # Services that participated
    participating_services: Tuple[str, ...] = field(default_factory=tuple)
    
    # Execution plan
    execution_plan: Optional[Dict[str, Any]] = None
    
    # Results from queries
    results: Dict[str, List[Any]] = field(default_factory=dict)  # {query_id: [results]}
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance (required per QUERY-LAW-004)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate session after creation."""
        if not self.session_identity:
            raise ValueError("session_identity cannot be empty")
    
    @property
    def query_count(self) -> int:
        """Number of queries executed in this session."""
        return len(self.executed_queries)
    
    @property
    def result_count(self) -> int:
        """Total number of results across all queries."""
        return sum(len(r) for r in self.results.values())
    
    @classmethod
    def create_initial(
        cls,
        query: KnowledgeQuery,
        participating_service: Optional[str] = None,
    ) -> "QuerySession":
        """
        Create a new initial query session.
        
        Args:
            query: First query to execute
            participating_service: Service that will participate (optional)
            
        Returns:
            New QuerySession with the initial query
            
        This method creates the initial version of a session, setting up:
            - Unique session_identity
            - Initial provenance record
            - First query added
        """
        session_id = f"session:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Query session initialization",
                "originating_system": "knowledge-services-system",
                "timestamp_utc": time.time(),
            },
        )
        
        participants = (participating_service,) if participating_service else tuple()
        
        return cls(
            session_identity=session_id,
            executed_queries=(query,),
            participating_services=participants,
            provenance=initial_provenance,
        )
    
    def add_query(self, query: KnowledgeQuery) -> "QuerySession":
        """Add a query to the session and return new session."""
        return QuerySession(
            session_identity=self.session_identity,
            executed_queries=tuple(list(self.executed_queries) + [query]),
            participating_services=self.participating_services,
            execution_plan=self.execution_plan,
            results=dict(self.results),
            diagnostics=dict(self.diagnostics),
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": f"Added query: {query.query_identity}",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def add_result(
        self,
        query_id: str,
        results: List[Any],
    ) -> "QuerySession":
        """Add results for a query and return new session."""
        new_results = dict(self.results)
        if query_id in new_results:
            new_results[query_id] = list(new_results[query_id]) + list(results)
        else:
            new_results[query_id] = list(results)
        
        return QuerySession(
            session_identity=self.session_identity,
            executed_queries=self.executed_queries,
            participating_services=self.participating_services,
            execution_plan=self.execution_plan,
            results=new_results,
            diagnostics=dict(self.diagnostics),
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": f"Added {len(results)} results for query: {query_id}",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def add_diagnostics(self, diagnostics: Dict[str, Any]) -> "QuerySession":
        """Add diagnostics to the session and return new session."""
        new_diagnostics = dict(self.diagnostics)
        new_diagnostics.update(diagnostics)
        
        return QuerySession(
            session_identity=self.session_identity,
            executed_queries=self.executed_queries,
            participating_services=self.participating_services,
            execution_plan=self.execution_plan,
            results=dict(self.results),
            diagnostics=new_diagnostics,
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": "Added diagnostics",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def add_service_participation(self, service_id: str) -> "QuerySession":
        """Record that a service participated in query execution."""
        if service_id in self.participating_services:
            return self
        
        new_participants = tuple(list(self.participating_services) + [service_id])
        
        return QuerySession(
            session_identity=self.session_identity,
            executed_queries=self.executed_queries,
            participating_services=new_participants,
            execution_plan=self.execution_plan,
            results=dict(self.results),
            diagnostics=dict(self.diagnostics),
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": f"Service participation: {service_id}",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def set_execution_plan(self, plan: Dict[str, Any]) -> "QuerySession":
        """Set the complete execution plan for this session."""
        return QuerySession(
            session_identity=self.session_identity,
            executed_queries=self.executed_queries,
            participating_services=self.participating_services,
            execution_plan=plan,
            results=dict(self.results),
            diagnostics=dict(self.diagnostics),
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": "Execution plan set",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_identity": self.session_identity,
            "executed_queries": [q.to_dict() for q in self.executed_queries],
            "participating_services": list(self.participating_services),
            "execution_plan": self.execution_plan,
            "results": dict(self.results),
            "diagnostics": dict(self.diagnostics),
            "provenance": list(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuerySession":
        """Create session from dictionary."""
        queries = []
        for q_data in data.get("executed_queries", []):
            if isinstance(q_data, dict):
                queries.append(KnowledgeQuery.from_dict(q_data))
        
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            session_identity=data.get("session_identity", str(uuid.uuid4())),
            executed_queries=tuple(queries),
            participating_services=tuple(data.get("participating_services", [])),
            execution_plan=data.get("execution_plan"),
            results=dict(data.get("results", {})),
            diagnostics=dict(data.get("diagnostics", {})),
            provenance=tuple(provenance),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Query kinds (Part 1 Section 3)
    "QueryKind",
    # Ordering directions (Part 1 Section 4)
    "OrderingDirection",
    # Constraint (Part 1 Section 3)
    "Constraint",
    # Knowledge query (Part 1 Section 1)
    "KnowledgeQuery",
    # Query session (Part 2 Section 2)
    "QuerySession",
]