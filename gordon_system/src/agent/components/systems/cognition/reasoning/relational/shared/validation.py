# Relational Validation - Phase 7.11
# ====================================

"""
Canonical Relational Validation.

Validation remains observational - it does not modify relational artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ValidationKind(Enum):
    """Kinds of validation findings."""
    
    GRAPH_INCONSISTENCY = "graph_inconsistency"         # Graph structure issues
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"   # Meaning conflicts
    CONSTRAINT_VIOLATION = "constraint_violation"       # Constraint not satisfied
    RELATION_ERROR = "relation_error"                   # Relation definition issue


@dataclass(frozen=True)
class RelationalValidation:
    """
    Observational validation of relational structures.
    
    Validation never modifies relational artifacts directly. It only reports findings.
    """
    
    # Identity
    validation_id: str                    # Unique validation identifier
    
    # Validation findings (what was found, not changed)
    findings: Tuple[str, ...] = ()        # List of validation findings
    
    # Kind of each finding (for categorization)
    finding_kinds: Dict[str, ValidationKind] = field(default_factory=dict)
    
    # Overall validation result
    overall_result: str = "pending"       # pending, valid, invalid
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None   # If derived from graph analysis
    
    @classmethod
    def create(
        cls,
    ) -> RelationalValidation:
        """Create a new relational validation."""
        return cls(
            validation_id=f"relational_validation:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
        )
    
    def record_finding(self, finding: str, kind: ValidationKind = ValidationKind.GRAPH_INCONSISTENCY) -> RelationalValidation:
        """Record a validation finding."""
        new_findings = self.findings + (finding,)
        new_kinds = dict(self.finding_kinds)
        new_kinds[finding] = kind
        return dataclass_replace(
            self,
            findings=new_findings,
            finding_kinds=new_kinds,
        )
    
    def set_result(self, result: str) -> RelationalValidation:
        """Set the overall validation result."""
        return dataclass_replace(
            self,
            overall_result=result,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RelationalValidation",
    "ValidationKind",
]