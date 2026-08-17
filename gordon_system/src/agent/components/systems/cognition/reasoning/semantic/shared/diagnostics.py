# Semantic Diagnostics - Phase 7.10
# ==================================

"""
Semantic diagnostics utilities for monitoring and troubleshooting.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Diagnostic record from semantic reasoning.
    
    Diagnostics include:
        - Performance metrics
        - Inference steps
        - Validation checks
        - Governance evaluations
    
    Diagnostics remain inspectable for debugging and auditing.
    """
    
    diagnostic_id: str                      # Unique identifier
    diagnostic_type: str                    # e.g., "inference", "validation"
    message: str                            # Diagnostic message
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp_utc: float = field(default_factory=time.time)
    severity: str = "info"                  # info, warning, error
    
    @classmethod
    def info(cls, message: str, **metadata: Any) -> DiagnosticsRecord:
        """Create an info diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="info",
            message=message,
            metadata=metadata,
            severity="info",
        )
    
    @classmethod
    def warning(cls, message: str, **metadata: Any) -> DiagnosticsRecord:
        """Create a warning diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="warning",
            message=message,
            metadata=metadata,
            severity="warning",
        )
    
    @classmethod
    def error(cls, message: str, **metadata: Any) -> DiagnosticsRecord:
        """Create an error diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="error",
            message=message,
            metadata=metadata,
            severity="error",
        )


@dataclass(frozen=True)
class SemanticTrace:
    """
    Complete trace of a semantic reasoning session.
    
    A trace contains:
        - Reasoning steps
        - Semantic graph (concepts and relations)
        - Diagnostics
        - Provenance
    
    Traces remain independently inspectable for auditing.
    """
    
    # Identity
    trace_id: str                           # Unique identifier
    
    # Reasoning goal
    reasoning_goal: str                     # What was reasoned about?
    
    # Steps (in chronological order)
    reasoning_steps: Tuple[DiagnosticsRecord, ...] = ()
    
    # Semantic graph
    semantic_graph: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    # State
    state: str = "tracing"
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
    ) -> SemanticTrace:
        """Create a new semantic trace."""
        return cls(
            trace_id=f"trace:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
        )
    
    def add_step(self, step: DiagnosticsRecord) -> SemanticTrace:
        """Add a reasoning step to the trace."""
        new_steps = tuple(self.reasoning_steps) + (step,)
        return dataclass_replace(
            self,
            reasoning_steps=new_steps,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DiagnosticsRecord",
    "SemanticTrace",
]