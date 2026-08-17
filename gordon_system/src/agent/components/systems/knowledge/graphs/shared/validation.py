"""Graph Validation - Phase 6.8 Part 2.

This module implements the canonical graph validation contracts according to 
Gordon Cognitive Architecture specifications (Phase 6.8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# VALIDATION RESULTS - Phase 6.8 Section 20
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a graph validation check.
    
    Per VALIDATION-LAW-001: Validation shall remain observational.
    Per VALIDATION-LAW-003: Validation shall distinguish topology errors from semantic errors.
    
    Check types:
        CONNECTIVITY     -> All nodes are reachable
        CONSISTENCY      -> No conflicting assertions
        MISSING_NODES    -> Reference to non-existent node
        BROKEN_EDGES     -> Edge references invalid endpoints
        ORPHAN_NODES     -> Node with no connections
        CONSTRAINT_VIOLATION -> Violates explicit constraints
        
    Validation remains observational - it does not modify graphs.
    """
    
    # Result identity
    result_identity: str
    
    # Check type
    check_type: str
    
    # Status
    status: str  # "pass", "fail", "warn"
    
    # Details
    description: str = ""
    findings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "result_identity": self.result_identity,
            "check_type": self.check_type,
            "status": self.status,
            "description": self.description,
            "findings": [f for f in self.findings],
        }
    
    @classmethod
    def create_pass(cls, check_type: str, description: str = "") -> ValidationResult:
        """Create a passing validation result."""
        return cls(
            result_identity=f"valid:{uuid.uuid4().hex[:16]}",
            check_type=check_type,
            status="pass",
            description=description or f"{check_type} passed",
            findings=(),
        )
    
    @classmethod
    def create_fail(cls, check_type: str, description: str = "") -> ValidationResult:
        """Create a failing validation result."""
        return cls(
            result_identity=f"valid:{uuid.uuid4().hex[:16]}",
            check_type=check_type,
            status="fail",
            description=description or f"{check_type} failed",
            findings=(),
        )
    
    @classmethod
    def create_warn(cls, check_type: str, description: str = "") -> ValidationResult:
        """Create a warning validation result."""
        return cls(
            result_identity=f"valid:{uuid.uuid4().hex[:16]}",
            check_type=check_type,
            status="warn",
            description=description or f"{check_type} warning",
            findings=(),
        )


# =============================================================================
# GRAPH VALIDATION - Phase 6.8 Section 20
# =============================================================================


@dataclass(frozen=True)
class GraphValidation:
    """
    Validation of a Knowledge Graph's integrity.
    
    Per VALIDATION-LAW-001: Validation shall remain observational.
    Per VALIDATION-LAW-002: Validation shall preserve findings.
    Per VALIDATION-LAW-005: Validation history shall remain immutable.
    Per VALIDATION-LAW-006: Validation shall never modify graphs directly.
    
    Fields:
        validation_identity: Unique identifier for this validation
        graph: Graph being validated
        validation_checks: List of checks performed
        findings: Results of all validation checks
        diagnostics: Additional diagnostic information
        
    Validation is purely observational - it never modifies the graph.
    """
    
    # Core identity
    validation_identity: str  # Unique validation identifier
    
    # Graph reference
    graph: Dict[str, Any] = field(default_factory=dict)
    
    # Checks performed (required per VALIDATION-LAW-001)
    validation_checks: Tuple[str, ...] = field(default_factory=tuple)
    
    # Findings (results) - preserved per VALIDATION-LAW-002
    findings: Tuple[ValidationResult, ...] = field(default_factory=tuple)
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance (required per VALIDATION-LAW-004)
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate validation after creation."""
        if not self.validation_identity:
            raise ValueError("validation_identity cannot be empty")
    
    @property
    def is_valid(self) -> bool:
        """Check if graph passed all validations."""
        return all(f.status != "fail" for f in self.findings)
    
    @classmethod
    def create_initial(
        cls,
        graph_id: str,
        checks: Optional[List[str]] = None,
    ) -> "GraphValidation":
        """
        Create a new graph validation.
        
        Args:
            graph_id: ID of the graph to validate
            checks: List of check types to perform (optional)
            
        Returns:
            New GraphValidation with unique identity
        """
        validation_id = f"validation:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": "Graph validation initialization",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [validation_id],
                "authority": "system",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            validation_identity=validation_id,
            graph={"graph_identity": graph_id},
            validation_checks=tuple(checks or []),
            provenance=initial_provenance,
            created_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation to dictionary for serialization."""
        return {
            "validation_identity": self.validation_identity,
            "graph": dict(self.graph),
            "validation_checks": list(self.validation_checks),
            "findings": [f.to_dict() for f in self.findings],
            "diagnostics": dict(self.diagnostics),
            "provenance": [p for p in self.provenance],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphValidation":
        """Create validation from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        findings = []
        for f_data in data.get("findings", []):
            if isinstance(f_data, dict):
                result_identity = f_data.get("result_identity", str(uuid.uuid4()))
                check_type = f_data.get("check_type", "")
                status = f_data.get("status", "pass")
                description = f_data.get("description", "")
                findings.append(ValidationResult(
                    result_identity=result_identity,
                    check_type=check_type,
                    status=status,
                    description=description,
                    findings=tuple(f_data.get("findings", [])),
                ))
        
        return cls(
            validation_identity=data.get("validation_identity", str(uuid.uuid4())),
            graph=dict(data.get("graph", {})),
            validation_checks=tuple(data.get("validation_checks", [])),
            findings=tuple(findings),
            diagnostics=dict(data.get("diagnostics", {})),
            provenance=tuple(provenance),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def add_finding(self, finding: ValidationResult) -> "GraphValidation":
        """Add a validation finding and return new validation."""
        return GraphValidation(
            validation_identity=self.validation_identity,
            graph=self.graph,
            validation_checks=self.validation_checks,
            findings=tuple(list(self.findings) + [finding]),
            diagnostics=self.diagnostics,
            provenance=tuple(list(self.provenance) + [{
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": f"Added validation finding: {finding.result_identity}",
                "originating_system": "knowledge-graph-system",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": list(self.provenance[-1].get("revision_chain", [])) + [self.validation_identity] if self.provenance else [self.validation_identity],
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
    # Validation result (Phase 6.8 Section 20)
    "ValidationResult",
    # Graph validation (Phase 6.8 Section 20)
    "GraphValidation",
]