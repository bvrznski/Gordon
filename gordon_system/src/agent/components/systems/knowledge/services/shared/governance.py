"""Knowledge Service Governance - Phase 6.9 Part 2 Section 20.

This module implements the canonical contract for knowledge service governance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# GOVERNANCE FINDING - Phase 6.9 Part 2 Section 20
# =============================================================================


@dataclass(frozen=True)
class GovernanceFinding:
    """
    Finding from governance evaluation.
    
    Per GOVERNANCE-LAW-005: Governance shall preserve findings.
    
    Fields:
        finding_identity: Unique identifier for this finding
        category: Category of the finding (determinism, staleness, etc.)
        severity: Severity level (info, warning, error)
        description: Description of the finding
    """
    
    finding_identity: str  # Unique identifier
    
    category: str
    severity: str  # "info", "warning", "error"
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "finding_identity": self.finding_identity,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GovernanceFinding:
        """Create finding from dictionary."""
        return cls(
            finding_identity=data.get("finding_identity", str(uuid.uuid4())),
            category=data.get("category", "unknown"),
            severity=data.get("severity", "info"),
            description=data.get("description", ""),
        )
    
    @classmethod
    def create_info(cls, category: str, description: str = "") -> "GovernanceFinding":
        """Create an info-level finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            category=category,
            severity="info",
            description=description,
        )
    
    @classmethod
    def create_warning(cls, category: str, description: str = "") -> "GovernanceFinding":
        """Create a warning-level finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            category=category,
            severity="warning",
            description=description,
        )
    
    @classmethod
    def create_error(cls, category: str, description: str = "") -> "GovernanceFinding":
        """Create an error-level finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            category=category,
            severity="error",
            description=description,
        )


# =============================================================================
# KNOWLEDGE SERVICE GOVERNANCE - Phase 6.9 Part 2 Section 20
# =============================================================================


@dataclass(frozen=True)
class KnowledgeServiceGovernance:
    """
    Governance evaluation for knowledge services.
    
    Per GOVERNANCE-LAW-001: Knowledge Service Governance shall remain observational.
    Per GOVERNANCE-LAW-008: Equivalent Service states shall produce equivalent governance evaluations.
    
    Fields:
        governance_identity: Unique identifier for this governance evaluation
        evaluated_services: Services being governed
        
    Invariants:
        * Governance is observational (GOVERNANCE-LAW-001)
        * Finds nondeterminism (GOVERNANCE-LAW-002)
        * Detects stale caches (GOVERNANCE-LAW-003)
        * Detects incomplete explanations (GOVERNANCE-LAW-004)
        * Preserves findings (GOVERNANCE-LAW-005)
        * Never modifies semantic knowledge directly (GOVERNANCE-LAW-007)
    """
    
    governance_identity: str  # Unique identifier
    
    evaluated_services: Tuple[str, ...]
    
    findings: Tuple[GovernanceFinding, ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    violations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate governance after creation."""
        if not self.governance_identity:
            raise ValueError("governance_identity cannot be empty")
    
    @property
    def is_compliant(self) -> bool:
        """Check if all services appear compliant based on findings."""
        error_count = sum(1 for f in self.findings if f.severity == "error")
        return error_count == 0
    
    @classmethod
    def create_initial(
        cls,
        service_ids: Optional[List[str]] = None,
    ) -> "KnowledgeServiceGovernance":
        """
        Create initial governance evaluation.
        
        Args:
            service_ids: Services to evaluate (optional)
            
        Returns:
            New KnowledgeServiceGovernance ready for evaluation
        """
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_services=tuple(service_ids or []),
        )
    
    def add_finding(
        self,
        finding: GovernanceFinding,
    ) -> "KnowledgeServiceGovernance":
        """Add a finding to the governance evaluation."""
        return KnowledgeServiceGovernance(
            governance_identity=self.governance_identity,
            evaluated_services=self.evaluated_services,
            findings=tuple(list(self.findings) + [finding]),
            recommendations=self.recommendations,
            violations=self.violations,
        )
    
    def add_recommendation(
        self,
        recommendation: str,
    ) -> "KnowledgeServiceGovernance":
        """Add a recommendation to the governance evaluation."""
        return KnowledgeServiceGovernance(
            governance_identity=self.governance_identity,
            evaluated_services=self.evaluated_services,
            findings=self.findings,
            recommendations=tuple(list(self.recommendations) + [recommendation]),
            violations=self.violations,
        )
    
    def add_violation(
        self,
        violation: Dict[str, Any],
    ) -> "KnowledgeServiceGovernance":
        """Add a violation to the governance evaluation."""
        return KnowledgeServiceGovernance(
            governance_identity=self.governance_identity,
            evaluated_services=self.evaluated_services,
            findings=self.findings,
            recommendations=self.recommendations,
            violations=tuple(list(self.violations) + [violation]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert governance evaluation to dictionary."""
        return {
            "governance_identity": self.governance_identity,
            "evaluated_services": list(self.evaluated_services),
            "findings": [f.to_dict() for f in self.findings],
            "recommendations": list(self.recommendations),
            "violations": list(self.violations),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeServiceGovernance":
        """Create governance evaluation from dictionary."""
        return cls(
            governance_identity=data.get("governance_identity", str(uuid.uuid4())),
            evaluated_services=tuple(data.get("evaluated_services", [])),
            findings=tuple(GovernanceFinding.from_dict(f) for f in data.get("findings", []) if isinstance(f, dict)),
            recommendations=tuple(data.get("recommendations", [])),
            violations=tuple(data.get("violations", [])),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Governance findings (Part 2 Section 20)
    "GovernanceFinding",
    # Knowledge service governance
    "KnowledgeServiceGovernance",
]