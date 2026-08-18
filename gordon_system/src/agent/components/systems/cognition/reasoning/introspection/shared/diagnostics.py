# Self-Diagnostics - Phase 7.29
# ============================

"""
Self-Diagnostics determines Gordon's operational state diagnostics.

Diagnostics evaluates:
    - Resource anomalies
    - Cognitive anomalies
    - Configuration anomalies
    - Attention anomalies
    - Reasoning anomalies
    - Memory anomalies

Diagnostics remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class SelfDiagnostics:
    """
    Diagnostics for Gordon's current operational state.
    
    Diagnostics contain:
        - Explicit identity
        - Diagnostic findings
        - Severity assessments
        - Suggested actions
        - Provenance tracking
    
    Diagnostics remain independently inspectable.
    """
    
    # Identity
    diagnostics_id: str                       # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Diagnostic findings
    diagnostic_findings: List[Dict[str, Any]] = field(default_factory=list)  # All findings
    anomaly_count: int = 0                    # Total anomalies detected
    
    # Severity assessments
    overall_severity: str = "low"             # low, medium, high, critical
    severity_breakdown: Dict[str, int] = field(default_factory=dict)  # By category
    
    # Suggested actions
    suggested_actions: List[str] = field(default_factory=list)  # Action recommendations
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    diagnostic_strategy: str = "default"      # How were diagnostics run?
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        strategy: str = "default",
    ) -> SelfDiagnostics:
        """Create a new self-diagnostics report."""
        return cls(
            diagnostics_id=f"diagnostics:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            diagnostic_strategy=strategy,
        )
    
    def with_findings(self, findings: List[Dict[str, Any]]) -> SelfDiagnostics:
        """Return a copy with findings."""
        return dataclass_replace(
            self,
            diagnostic_findings=findings,
            anomaly_count=len([f for f in findings if f.get("is_anomaly", False)]),
        )


@dataclass(frozen=True)
class DiagnosticManagement:
    """
    Management of diagnostic process.
    
    A management object contains:
        - Diagnostics identity and configuration
        - Current state
        - Results
        - Provenance tracking
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Configuration
    diagnostic_strategy: str                  # Strategy used
    
    # Current state
    current_stage: str = "initializing"       # Diagnostic stage
    
    # Results (can be None if not yet completed)
    diagnostics_result: Optional[SelfDiagnostics] = None  # Result
    
    # Quality metrics
    coverage_score: float = 0.0               # How much was diagnosed?
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        diagnostic_strategy: str = "default",
    ) -> DiagnosticManagement:
        """Create a new diagnostic management."""
        return cls(
            management_id=f"diagnostic_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            diagnostic_strategy=diagnostic_strategy,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SelfDiagnostics",
    "DiagnosticManagement",
]