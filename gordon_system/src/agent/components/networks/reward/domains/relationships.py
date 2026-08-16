# Multi-Domain Reward Engine - Domain Relationships (Phase 4.10.5)
# =================================================================

"""
Domain relationship types and relationship models for Phase 4.10.5.

This module defines the semantic relationship types between reward domains and
the immutable relationship data structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class DomainRelationshipType(Enum):
    """
    Canonical domain relationship types.
    
    RELATIONSHIP-LAW-001: Domain relationships remain explicitly represented.
    RELATIONSHIP-LAW-002: Relationship types remain explicit.
    RELATIONSHIP-LAW-003: Relationships preserve provenance.
    RELATIONSHIP-LAW-004: Relationships remain immutable.
    RELATIONSHIP-LAW-005: Conflicting domains remain simultaneously representable.
    RELATIONSHIP-LAW-006: Supporting domains remain explicitly linked.
    RELATIONSHIP-LAW-007: Relationship analysis remains deterministic.
    RELATIONSHIP-LAW-008: Relationship analysis shall never resolve conflicts automatically.
    """
    
    # Supportive relationships
    SUPPORTS = "supports"
    """Domain A supports domain B (mutually reinforcing)."""
    
    REINFORCES = "reinforces"
    """Domain A reinforces domain B (strengthens presence)."""
    
    # Conflictual relationships  
    CONFLICTS_WITH = "conflicts_with"
    """Domain A conflicts with domain B (opposing values)."""
    
    COMPETES_WITH = "competes_with"
    """Domain A competes with domain B (zero-sum potential)."""
    
    # Independent relationships
    INDEPENDENT_OF = "independent_of"
    """Domain A is independent of domain B (no interaction)."""
    
    # Hierarchical relationships
    DERIVED_FROM = "derived_from"
    """Domain A is derived from domain B."""
    
    # Duplicate/same-domain relationship
    DUPLICATES = "duplicates"
    """Domain A duplicates domain B (redundant representation)."""
    
    # Unknown relationship
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DomainRelationship:
    """
    A semantic relationship between two reward domains.
    
    PROPERTIES:
        • source_domain: The source domain in the relationship
        • target_domain: The target domain in the relationship  
        • relationship_type: The type of relationship
        • confidence: Confidence in the relationship (0.0-1.0)
        • provenance: Source information for traceability
    
    RELATIONSHIP-LAW-003: Relationships preserve provenance.
    RELATIONSHIP-LAW-004: Relationships remain immutable.
    """
    
    source_domain: str
    """The source domain identifier."""
    
    target_domain: str  
    """The target domain identifier."""
    
    relationship_type: DomainRelationshipType = DomainRelationshipType.UNKNOWN
    """The type of relationship between domains."""
    
    confidence: float = 1.0
    """Confidence in the relationship (0.0-1.0)."""
    
    provenance: str = "unknown"
    """Source information for traceability."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.source_domain}→{self.relationship_type.value}→{self.target_domain}"
    
    def to_dict(self) -> dict:
        """Convert relationship to dictionary representation."""
        return {
            "relationship_id": self.canonical_identity,
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "relationship_type": self.relationship_type.value,
            "confidence": self.confidence,
            "provenance": self.provenance,
        }
    
    @classmethod
    def create_supports(
        cls,
        source: str,
        target: str,
        confidence: float = 1.0,
    ) -> DomainRelationship:
        """Create a supports relationship."""
        return cls(
            source_domain=source,
            target_domain=target,
            relationship_type=DomainRelationshipType.SUPPORTS,
            confidence=confidence,
        )
    
    @classmethod
    def create_reinforces(
        cls,
        source: str,
        target: str,
        confidence: float = 1.0,
    ) -> DomainRelationship:
        """Create a reinforces relationship."""
        return cls(
            source_domain=source,
            target_domain=target,
            relationship_type=DomainRelationshipType.REINFORCES,
            confidence=confidence,
        )
    
    @classmethod
    def create_conflicts_with(
        cls,
        source: str,
        target: str,
        confidence: float = 1.0,
    ) -> DomainRelationship:
        """Create a conflicts-with relationship."""
        return cls(
            source_domain=source,
            target_domain=target,
            relationship_type=DomainRelationshipType.CONFLICTS_WITH,
            confidence=confidence,
        )
    
    @classmethod
    def create_independent_of(
        cls,
        source: str,
        target: str,
        confidence: float = 1.0,
    ) -> DomainRelationship:
        """Create an independent-of relationship."""
        return cls(
            source_domain=source,
            target_domain=target,
            relationship_type=DomainRelationshipType.INDEPENDENT_OF,
            confidence=confidence,
        )
    
    @classmethod
    def create_derived_from(
        cls,
        source: str,
        target: str,
        confidence: float = 1.0,
    ) -> DomainRelationship:
        """Create a derived-from relationship."""
        return cls(
            source_domain=source,
            target_domain=target,
            relationship_type=DomainRelationshipType.DERIVED_FROM,
            confidence=confidence,
        )
    
    @classmethod
    def from_dict(cls, data: dict) -> DomainRelationship:
        """Create relationship from dictionary representation."""
        rel_type_str = data.get("relationship_type", "unknown")
        try:
            rel_type = DomainRelationshipType(rel_type_str)
        except ValueError:
            rel_type = DomainRelationshipType.UNKNOWN
        
        return cls(
            source_domain=data.get("source_domain", ""),
            target_domain=data.get("target_domain", ""),
            relationship_type=rel_type,
            confidence=float(data.get("confidence", 1.0)),
            provenance=data.get("provenance", "unknown"),
        )


@dataclass(frozen=True)
class DomainRelationshipGraph:
    """
    An immutable graph of domain relationships.
    
    PROPERTIES:
        • nodes: Set of domain identifiers (nodes in the graph)
        • edges: Tuple of DomainRelationship instances (edges in the graph)
        • adjacency_list: Mapping from domain to its relationships
    
    GRAPH-LAW-001: Graph remains immutable.
    GRAPH-LAW-002: All relationships are preserved.
    """
    
    nodes: Tuple[str, ...] = field(default_factory=tuple)
    """Set of domain identifiers (nodes in the graph)."""
    
    edges: Tuple[DomainRelationship, ...] = field(default_factory=tuple)
    """Tuple of domain relationships (edges in the graph)."""
    
    @property
    def adjacency_list(self) -> dict:
        """
        Build an adjacency list representation of the graph.
        
        Returns:
            Dict mapping source domain to list of relationship tuples
        """
        adj: dict = {}
        for edge in self.edges:
            src = edge.source_domain
            if src not in adj:
                adj[src] = []
            adj[src].append((edge.target_domain, edge.relationship_type.value))
        return adj
    
    def get_outgoing(self, domain: str) -> Tuple[DomainRelationship, ...]:
        """Get all outgoing relationships from a domain."""
        return tuple(e for e in self.edges if e.source_domain == domain)
    
    def get_incoming(self, domain: str) -> Tuple[DomainRelationship, ...]:
        """Get all incoming relationships to a domain."""
        return tuple(e for e in self.edges if e.target_domain == domain)
    
    def has_relationship(
        self,
        source: str,
        target: str,
        rel_type: DomainRelationshipType = None,
    ) -> bool:
        """
        Check if a relationship exists between two domains.
        
        Args:
            source: Source domain
            target: Target domain  
            rel_type: Optional specific relationship type to check
            
        Returns:
            True if relationship exists, False otherwise
        """
        for edge in self.edges:
            if edge.source_domain == source and edge.target_domain == target:
                if rel_type is None or edge.relationship_type == rel_type:
                    return True
        return False
    
    def find_conflicts(self) -> Tuple[DomainRelationship, ...]:
        """Find all conflict relationships in the graph."""
        return tuple(
            e for e in self.edges
            if e.relationship_type == DomainRelationshipType.CONFLICTS_WITH
        )
    
    def find_supports(self) -> Tuple[DomainRelationship, ...]:
        """Find all support relationships in the graph."""
        return tuple(
            e for e in self.edges
            if e.relationship_type in (
                DomainRelationshipType.SUPPORTS,
                DomainRelationshipType.REINFORCES,
            )
        )
    
    def to_dict(self) -> dict:
        """Convert graph to dictionary representation."""
        return {
            "graph_id": "domain_relationship_graph",
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": list(self.nodes),
            "edges": [e.to_dict() for e in self.edges],
        }
    
    @classmethod
    def create_empty(cls) -> DomainRelationshipGraph:
        """Create an empty relationship graph."""
        return cls()
    
    @classmethod
    def from_edges(cls, edges: Tuple[DomainRelationship, ...]) -> DomainRelationshipGraph:
        """Create a graph from a tuple of edges, extracting nodes."""
        nodes = set()
        for edge in edges:
            nodes.add(edge.source_domain)
            nodes.add(edge.target_domain)
        
        return cls(
            nodes=tuple(sorted(nodes)),
            edges=edges,
        )