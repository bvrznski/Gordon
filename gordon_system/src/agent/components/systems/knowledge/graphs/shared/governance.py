"""Graph Governance - Phase 6.8 Part 2.

This module implements the canonical graph governance contracts according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# GOVERNANCE FINDINGS - Phase 6.8 Section 22
# =============================================================================


@dataclass(frozen=True)
class GovernanceFindings:
    """
    Findings from graph governance evaluation.
    
    Per GOVERNANCE-LAW-001: Graph Governance shall remain observational.
    Per GOVERNANCE-LAW-005: Governance shall preserve findings.
    Per GOVERNANCE-LAW-007: Governance shall never modify graph contents directly.
    
    Findings include:
        FRAGMENTATION      -> Multiple disjoint subgraphs
        REDUNDANCY         -> Duplicate structures
        INVALID_TOPOLOGY   -> Graph doesn't match declared topology
        CONSTRAINT_VIOLATION -> Violates explicit constraints
        LAYER_INCONSISTENCY -> Inconsistent layer states
        
    Governance is purely observational.
    """
    
    # Finding identity
    finding_identity: str
    
    # Category
    category: str  # "fragmentation", "redundancy", "invalid_topology", etc.
    
    # Severity
    severity: str  # "info", "warning", "error"
    
    # Details
    description: str = ""
    affected_elements: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "finding_identity": self.finding_identity,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "affected_elements": [e for e in self.affected_elements],
        }
    
    @classmethod
    def create_info(cls, category: str, description: str = "") -> GovernanceFindings:
        """Create an informational finding."""
        return cls(
            finding_identity=f"governance:{uuid.uuid4().hex[:16]}",
            category=category,
            severity="info",
            description=description or f"{category} observation",
            affected_elements=(),
        )
    
    @classmethod
    def create_warning(cls, category: str, description: str = "") -> GovernanceFindings:
        """Create a warning finding."""
        return cls(
            finding_identity=f"governance:{uuid.uuid4().hex[:16]}",
            category=category,
            severity="warning",
            description=description or f"{category} warning",
            affected_elements=(),
        )
    
    @classmethod
    def create_error(cls, category: str, description: str = "") -> GovernanceFindings:
        """Create an error finding."""
        return cls(
            finding_identity=f"governance:{uuid.uuid4().hex[:16]}",
            category=category,
            severity="error",
            description=description or f"{category} error",
            affected_elements=(),
        )


# =============================================================================
# GRAPH GOVERNANCE - Phase 6.8 Section 22
# =============================================================================


@dataclass(frozen=True)
class GraphGovernance:
    """
    Governance evaluation of Knowledge Graphs.
    
    Per GOVERNANCE-LAW-001: Graph Governance shall remain observational.
    Per GOVERNANCE-LAW-002: Governance shall detect fragmentation.
    Per GOVERNANCE-LAW-006: Governance shall preserve provenance.
    Per GOVERNANCE-LAW-007: Governance shall never modify graph contents directly.
    
    Fields:
        governance_identity: Unique identifier for this governance evaluation
        evaluated_graphs: Graphs being governed
        findings: List of governance findings
        recommendations: Suggestions for improvement
        violations: Detected policy violations
        
    Governance provides observational insights without modifying graphs.
    """
    
    # Core identity
    governance_identity: str  # Unique governance identifier
    
    # Evaluated graphs
    evaluated_graphs: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Findings (required per GOVERNANCE-LAW-005)
    findings: Tuple[GovernanceFindings, ...] = field(default_factory=tuple)
    
    # Recommendations
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Violations
    violations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Provenance (required per GOVERNANCE-LAW-006)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate governance after creation."""
        if not self.governance_identity:
            raise ValueError("governance_identity cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        """Check if governance has valid foundational data."""
        return len(self.governance_identity) > 0
    
    @classmethod
    def create_initial(
        cls,
        graph_refs: Optional[List[Dict[str, Any]]] = None,
    ) -> "GraphGovernance":
        """
        Create a new graph governance evaluation.
        
        Args:
            graph_refs: References to graphs being governed (optional)
            
        Returns:
            New GraphGovernance with unique identity
        """
        governance_id = f"governance:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Graph governance initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [governance_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            governance_identity=governance_id,
            evaluated_graphs=tuple(graph_refs or []),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert governance to dictionary for serialization."""
        return {
            "governance_identity": self.governance_identity,
            "evaluated_graphs": [dict(g) for g in self.evaluated_graphs],
            "findings": [f.to_dict() for f in self.findings],
            "recommendations": list(self.recommendations),
            "violations": [v for v in self.violations],
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphGovernance":
        """Create governance from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        findings = []
        for f_data in data.get("findings", []):
            if isinstance(f_data, dict):
                finding_identity = f_data.get("finding_identity", str(uuid.uuid4()))
                category = f_data.get("category", "")
                severity = f_data.get("severity", "info")
                description = f_data.get("description", "")
                findings.append(GovernanceFindings(
                    finding_identity=finding_identity,
                    category=category,
                    severity=severity,
                    description=description,
                    affected_elements=tuple(f_data.get("affected_elements", [])),
                ))
        
        return cls(
            governance_identity=data.get("governance_identity", str(uuid.uuid4())),
            evaluated_graphs=tuple(data.get("evaluated_graphs", [])),
            findings=tuple(findings),
            recommendations=tuple(data.get("recommendations", [])),
            violations=tuple(data.get("violations", [])),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def add_finding(self, finding: GovernanceFindings) -> "GraphGovernance":
        """Add a governance finding and return new evaluation."""
        return GraphGovernance(
            governance_identity=self.governance_identity,
            evaluated_graphs=self.evaluated_graphs,
            findings=tuple(list(self.findings) + [finding]),
            recommendations=self.recommendations,
            violations=self.violations,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added governance finding: {finding.finding_identity}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.governance_identity] if self.provenance else [self.governance_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def add_recommendation(self, recommendation: str) -> "GraphGovernance":
        """Add a governance recommendation."""
        return GraphGovernance(
            governance_identity=self.governance_identity,
            evaluated_graphs=self.evaluated_graphs,
            findings=self.findings,
            recommendations=tuple(set(self.recommendations) | {recommendation}),
            violations=self.violations,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added recommendation: {recommendation}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.governance_identity] if self.provenance else [self.governance_identity],
                "authority": "system",
                "timestamp_utc": time.time(),
            }]),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Governance findings (Phase 6.8 Section 22)
    "GovernanceFindings",
    # Graph governance (Phase 6.8 Section 22)
    "GraphGovernance",
]