# Temporal Binding Result - Phase 5.2.3
# =====================================

"""
Temporal binding results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class TemporalBindingResult:
    """
    Result of temporal binding.
    
    Fields:
        request_reference: Reference to the original request
        bindings: Created bindings
        rejected_artifacts: Artifacts that couldn't be bound
        unresolved_artifacts: Artifacts with ambiguous bindings
        ordering_constraints: Known orderings between artifacts
        missing_intervals: Gaps in observation
        alternatives: Alternative binding structures
    """
    
    request_reference: str
    
    bindings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    rejected_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    unresolved_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    ordering_constraints: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    missing_intervals: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    status: str = "unknown"
    
    provenance: Dict[str, Any] = field(default_factory=dict)