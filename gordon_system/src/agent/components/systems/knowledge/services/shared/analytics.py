"""Analytics Service - Phase 6.9 Part 2 Section 17.

This module implements the canonical contract for knowledge analytics
in Knowledge Services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# METRICS - Phase 6.9 Part 2 Section 17
# =============================================================================


@dataclass(frozen=True)
class KnowledgeMetrics:
    """
    Metrics for knowledge evaluation.
    
    Per ANALYTICS-LAW-004: Analytics provenance shall remain complete.
    
    Fields:
        coverage: Fraction of expected knowledge that is present (0.0 - 1.0)
        consistency: Degree of logical consistency in the knowledge
        redundancy: Amount of redundant information
        fragmentation: Degree of knowledge fragmentation
        graph_density: Graph density metric
        ontology_quality: Quality score for ontological structure
    """
    
    coverage: float = 0.0
    consistency: float = 0.0
    redundancy: float = 0.0
    fragmentation: float = 1.0
    graph_density: float = 0.0
    ontology_quality: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "coverage": self.coverage,
            "consistency": self.consistency,
            "redundancy": self.redundancy,
            "fragmentation": self.fragmentation,
            "graph_density": self.graph_density,
            "ontology_quality": self.ontology_quality,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KnowledgeMetrics:
        """Create metrics from dictionary."""
        return cls(
            coverage=float(data.get("coverage", 0.0)),
            consistency=float(data.get("consistency", 0.0)),
            redundancy=float(data.get("redundancy", 0.0)),
            fragmentation=float(data.get("fragmentation", 1.0)),
            graph_density=float(data.get("graph_density", 0.0)),
            ontology_quality=float(data.get("ontology_quality", 0.0)),
        )


# =============================================================================
# ANALYTICS FINDING - Phase 6.9 Part 2 Section 17
# =============================================================================


@dataclass(frozen=True)
class AnalyticsFinding:
    """
    Finding from analytics evaluation.
    
    Per ANALYTICS-LAW-002: Analytics shall preserve findings.
    
    Fields:
        finding_identity: Unique identifier for this finding
        category: Category of the finding (coverage, consistency, etc.)
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
    def from_dict(cls, data: Dict[str, Any]) -> AnalyticsFinding:
        """Create finding from dictionary."""
        return cls(
            finding_identity=data.get("finding_identity", str(uuid.uuid4())),
            category=data.get("category", "unknown"),
            severity=data.get("severity", "info"),
            description=data.get("description", ""),
        )
    
    @classmethod
    def create_info(cls, category: str, description: str = "") -> "AnalyticsFinding":
        """Create an info-level finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            category=category,
            severity="info",
            description=description,
        )
    
    @classmethod
    def create_warning(cls, category: str, description: str = "") -> "AnalyticsFinding":
        """Create a warning-level finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            category=category,
            severity="warning",
            description=description,
        )
    
    @classmethod
    def create_error(cls, category: str, description: str = "") -> "AnalyticsFinding":
        """Create an error-level finding."""
        return cls(
            finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
            category=category,
            severity="error",
            description=description,
        )


# =============================================================================
# ANALYTICS PIPELINE - Phase 6.9 Part 2 Section 17
# =============================================================================


@dataclass(frozen=True)
class AnalyticsPipeline:
    """
    Pipeline for knowledge analytics operations.
    
    Per ANALYTICS-LAW-004: Analytics provenance shall remain complete.
    
    Fields:
        analytics_identity: Unique identifier for this pipeline
        evaluated_scope: Scope being analyzed
        
    Invariants:
        * Analytics are observational (ANALYTICS-LAW-001)
        * Provenance is preserved
        * Results are immutable (implied)
    """
    
    analytics_identity: str  # Unique identifier
    
    evaluated_scope: Dict[str, Any]
    
    metrics: KnowledgeMetrics = field(default_factory=KnowledgeMetrics)
    findings: Tuple[AnalyticsFinding, ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate pipeline after creation."""
        if not self.analytics_identity:
            raise ValueError("analytics_identity cannot be empty")
    
    @classmethod
    def create_initial(
        cls,
        scope: Dict[str, Any],
    ) -> "AnalyticsPipeline":
        """
        Create initial analytics pipeline.
        
        Args:
            scope: Scope to analyze
            
        Returns:
            New AnalyticsPipeline ready for evaluation
        """
        return cls(
            analytics_identity=f"analytics:{uuid.uuid4().hex[:16]}",
            evaluated_scope=dict(scope),
        )
    
    def add_finding(
        self,
        finding: AnalyticsFinding,
    ) -> "AnalyticsPipeline":
        """Add a finding to the analytics."""
        return AnalyticsPipeline(
            analytics_identity=self.analytics_identity,
            evaluated_scope=dict(self.evaluated_scope),
            metrics=self.metrics,
            findings=tuple(list(self.findings) + [finding]),
            recommendations=self.recommendations,
        )
    
    def add_recommendation(
        self,
        recommendation: str,
    ) -> "AnalyticsPipeline":
        """Add a recommendation to the analytics."""
        return AnalyticsPipeline(
            analytics_identity=self.analytics_identity,
            evaluated_scope=dict(self.evaluated_scope),
            metrics=self.metrics,
            findings=self.findings,
            recommendations=tuple(list(self.recommendations) + [recommendation]),
        )
    
    def update_metrics(
        self,
        metrics: KnowledgeMetrics,
    ) -> "AnalyticsPipeline":
        """Update the metrics for this analytics."""
        return AnalyticsPipeline(
            analytics_identity=self.analytics_identity,
            evaluated_scope=dict(self.evaluated_scope),
            metrics=metrics,
            findings=self.findings,
            recommendations=self.recommendations,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary."""
        return {
            "analytics_identity": self.analytics_identity,
            "evaluated_scope": dict(self.evaluated_scope),
            "metrics": self.metrics.to_dict(),
            "findings": [f.to_dict() for f in self.findings],
            "recommendations": list(self.recommendations),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalyticsPipeline":
        """Create pipeline from dictionary."""
        findings = []
        for f_data in data.get("findings", []):
            if isinstance(f_data, dict):
                findings.append(AnalyticsFinding.from_dict(f_data))
        
        return cls(
            analytics_identity=data.get("analytics_identity", str(uuid.uuid4())),
            evaluated_scope=dict(data.get("evaluated_scope", {})),
            metrics=KnowledgeMetrics.from_dict(data.get("metrics", {})),
            findings=tuple(findings),
            recommendations=tuple(data.get("recommendations", [])),
        )


# =============================================================================
# KNOWLEDGE ANALYTICS - Phase 6.9 Part 2 Section 16
# =============================================================================


@dataclass(frozen=True)
class KnowledgeAnalytics:
    """
    Analytics evaluation result for knowledge services.
    
    Per ANALYTICS-LAW-001: Analytics shall remain observational.
    Per ANALYTICS-LAW-007: Analytics shall remain independently inspectable.
    
    Fields:
        analytics_identity: Unique identifier for this analysis
        evaluated_scope: Scope that was analyzed
        metrics: Evaluated metrics
        
    Invariants:
        * Analytics are observational only (ANALYTICS-LAW-001)
        * Findings are preserved (ANALYTICS-LAW-002)
        * Provenance is complete (ANALYTICS-LAW-004)
        * Results never modify artifacts (implied by ANALYTICS-LAW-006)
    """
    
    analytics_identity: str  # Unique identifier
    
    evaluated_scope: Dict[str, Any]
    
    metrics: KnowledgeMetrics
    findings: Tuple[AnalyticsFinding, ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate analytics after creation."""
        if not self.analytics_identity:
            raise ValueError("analytics_identity cannot be empty")
    
    @property
    def is_healthy(self) -> bool:
        """Check if evaluated scope appears healthy based on metrics."""
        return (
            self.metrics.consistency > 0.8 and
            self.metrics.coverage > 0.7 and
            self.metrics.fragmentation < 0.3
        )
    
    @classmethod
    def create_initial(
        cls,
        scope: Dict[str, Any],
    ) -> "KnowledgeAnalytics":
        """
        Create initial knowledge analytics.
        
        Args:
            scope: Scope to analyze
            
        Returns:
            New KnowledgeAnalytics ready for evaluation
        """
        return cls(
            analytics_identity=f"analytics:{uuid.uuid4().hex[:16]}",
            evaluated_scope=dict(scope),
            metrics=KnowledgeMetrics(),
            provenance=(
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": "Knowledge analytics initialization",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics to dictionary."""
        return {
            "analytics_identity": self.analytics_identity,
            "evaluated_scope": dict(self.evaluated_scope),
            "metrics": self.metrics.to_dict(),
            "findings": [f.to_dict() for f in self.findings],
            "recommendations": list(self.recommendations),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeAnalytics":
        """Create analytics from dictionary."""
        findings = []
        for f_data in data.get("findings", []):
            if isinstance(f_data, dict):
                findings.append(AnalyticsFinding.from_dict(f_data))
        
        return cls(
            analytics_identity=data.get("analytics_identity", str(uuid.uuid4())),
            evaluated_scope=dict(data.get("evaluated_scope", {})),
            metrics=KnowledgeMetrics.from_dict(data.get("metrics", {})),
            findings=tuple(findings),
            recommendations=tuple(data.get("recommendations", [])),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Knowledge metrics (Part 2 Section 17)
    "KnowledgeMetrics",
    # Analytics findings
    "AnalyticsFinding",
    # Analytics pipeline
    "AnalyticsPipeline",
    # Knowledge analytics
    "KnowledgeAnalytics",
]