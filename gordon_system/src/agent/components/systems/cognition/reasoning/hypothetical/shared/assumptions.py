# Assumption Management - Phase 7.15 Part 2
# ===========================================

"""
Canonical Assumption Contract.

Every hypothesis depends upon assumptions.
Assumptions include physical, logical, semantic, environmental, and resource assumptions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AssumptionKind(Enum):
    """Kinds of assumptions."""
    
    PHYSICAL = "physical"                     # Physical laws and properties
    LOGICAL = "logical"                       # Logical axioms and rules
    SEMANTIC = "semantic"                     # Meaning and interpretation
    ENVIRONMENTAL = "environmental"           # Environmental conditions
    RESOURCE = "resource"                     # Resource availability
    epistemic = "epistemic"                   # Knowledge-related assumptions


class AssumptionJustification(Enum):
    """Ways an assumption can be justified."""
    
    AXIOMATIC = "axiomatic"                   # Taken as fundamental
    EMPIRICAL = "empirical"                   # Supported by observation
    CONVENIENCE = "convenience"               # Pragmatic simplification
    CONVENTIONAL = "conventional"             # Widely accepted convention
    THEORETICAL = "theoretical"               # Derived from theory


@dataclass(frozen=True)
class Assumption:
    """
    An assumption underlying a hypothesis.
    
    Every hypothesis depends upon explicit assumptions that define
    the context in which it is valid.
    """
    
    # Identity
    assumption_id: str                        # Unique identifier
    semantic_identity: str                    # Stable identity for comparison
    
    # Content
    assumption_statement: str                 # The assumed proposition
    assumption_kind: AssumptionKind           # What kind of assumption?
    
    # Justification
    justification: AssumptionJustification = AssumptionJustification.CONVENIENCE
    justifying_evidence: Tuple[str, ...] = ()  # Supporting evidence if any
    
    # Scope
    scope: str = "default"                    # Context where this applies
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    origin_context: str = "unknown"
    
    @property
    def is_justified(self) -> bool:
        """Check if assumption has justification."""
        return self.justifying_evidence != ()
    
    @classmethod
    def create(
        cls,
        assumption_statement: str,
        assumption_kind: AssumptionKind = AssumptionKind.LOGICAL,
        justification: AssumptionJustification = AssumptionJustification.CONVENIENCE,
        scope: str = "default",
        origin_context: str = "unknown",
    ) -> Assumption:
        """Create a new assumption."""
        return cls(
            assumption_id=f"assumption:{uuid.uuid4().hex[:16]}",
            semantic_identity=assumption_statement,
            assumption_statement=assumption_statement,
            assumption_kind=assumption_kind,
            justification=justification,
            scope=scope,
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class AssumptionManagement:
    """
    Management record for assumptions.
    
    Tracks the set of assumptions, their dependencies, and justifications.
    """
    
    # Identity
    management_id: str                        # Unique identifier
    
    # Contents
    participating_assumptions: Tuple[Assumption, ...]  # All assumptions tracked
    
    # Dependencies
    dependency_graph: Dict[str, Tuple[str, ...]] = field(default_factory=dict)  # assumption -> dependencies
    
    # Justification summary
    overall_justification: str = "default"    # Overall assessment
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_assumptions(self) -> int:
        """Return number of assumptions tracked."""
        return len(self.participating_assumptions)
    
    @classmethod
    def create(
        cls,
        participating_assumptions: List[Assumption],
        dependency_graph: Optional[Dict[str, List[str]]] = None,
        overall_justification: str = "default",
    ) -> AssumptionManagement:
        """Create a new assumption management record."""
        return cls(
            management_id=f"assumption_mgmt:{uuid.uuid4().hex[:16]}",
            participating_assumptions=tuple(participating_assumptions),
            dependency_graph={k: tuple(v) for k, v in (dependency_graph or {}).items()},
            overall_justification=overall_justification,
        )


@dataclass(frozen=True)
class HiddenAssumption:
    """
    An assumption that may not be explicitly stated but is required.
    
    Detecting hidden assumptions is critical for robust hypothetical reasoning.
    """
    
    # Identity
    hidden_assumption_id: str                 # Unique identifier
    
    # Content
    inferred_statement: str                   # What is being assumed?
    required_by: Tuple[str, ...] = ()         # Which hypotheses/assumptions require it?
    
    # Assessment
    confidence: float = 0.5                   # How likely is this assumption?
    impact: str = "medium"                    # "low", "medium", "high"
    
    # Metadata
    detected_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        inferred_statement: str,
        required_by: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> HiddenAssumption:
        """Create a new hidden assumption."""
        return cls(
            hidden_assumption_id=f"hidden:{uuid.uuid4().hex[:16]}",
            inferred_statement=inferred_statement,
            required_by=tuple(required_by or []),
            confidence=confidence,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AssumptionKind",
    "AssumptionJustification",
    "Assumption",
    "AssumptionManagement",
    "HiddenAssumption",
]