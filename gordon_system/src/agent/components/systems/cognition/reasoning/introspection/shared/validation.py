# Introspection Validation - Phase 7.29
# ======================================

"""
Introspection Validation observes introspection correctness.

Validation is:
    Observational - It evaluates, not modifies introspection artifacts
    
Validation ensures:
    - Introspection sessions produce valid self models
    - Awareness assessments are complete and accurate
    - Consistency checks are thorough
    - Diagnostics are reproducible
    - Publications preserve semantic correctness
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class IntrospectionValidation:
    """
    Validation of introspection reasoning.
    
    A validation contains:
        - Explicit identity
        - Evaluated artifacts (self models, awareness, consistency, diagnostics, publications)
        - Findings (validations performed)
        - Quality scores
        - Provenance tracking
    
    Validation remains observational.
    """
    
    # Identity
    validation_id: str                        # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Evaluated artifacts
    evaluated_artifacts: List[str] = field(default_factory=list)  # What was validated?
    
    # Findings
    validation_findings: List[Dict[str, Any]] = field(default_factory=list)  # Results
    issue_count: int = 0                      # Number of issues found
    
    # Quality scores
    self_model_quality: float = 1.0           # Self model quality score
    awareness_quality: float = 1.0            # Awareness quality score
    consistency_quality: float = 1.0          # Consistency quality score
    diagnostic_quality: float = 1.0           # Diagnostic quality score
    
    # Overall validation result
    overall_validation_result: str = "valid"  # valid, warning, invalid
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    validation_strategy: str = "default"      # Strategy used
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        strategy: str = "default",
    ) -> IntrospectionValidation:
        """Create a new introspection validation."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            validation_strategy=strategy,
        )
    
    def with_findings(self, findings: List[Dict[str, Any]]) -> IntrospectionValidation:
        """Return a copy with added findings."""
        return dataclass_replace(
            self,
            validation_findings=self.validation_findings + findings,
            issue_count=len([f for f in findings if f.get("is_issue", False)]),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "IntrospectionValidation",
]