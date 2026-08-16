# Spatial Binding Result - Phase 5.2.3
# =====================================

"""
Spatial binding results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class SpatialBindingResult:
    """
    Result of spatial binding.
    
    Fields:
        request_reference: Reference to the original request
        bindings: Created bindings
        reference_frame: Spatial reference frame used
        relations: Spatial relations between artifacts
        topology: Topological relationships
        hierarchy: Hierarchical structure (if any)
        occlusion: Occlusion information
        unresolved_artifacts: Artifacts with ambiguous bindings
        alternatives: Alternative binding structures
    """
    
    request_reference: str
    
    bindings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    reference_frame: Dict[str, Any] = field(default_factory=dict)
    relations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    topology: Tuple[str, ...] = field(default_factory=tuple)
    hierarchy: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    occlusion: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    unresolved_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    status: str = "unknown"
    
    provenance: Dict[str, Any] = field(default_factory=dict)