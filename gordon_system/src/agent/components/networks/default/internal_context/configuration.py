# Internal Context Configuration
# ==============================

"""
Immutable configuration for InternalContext assembly.

Configuration controls how context is assembled without containing provider
implementations or runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True, slots=True)
class InternalContextConfig:
    """
    Immutable configuration for internal context assembly.
    
    Configuration controls the assembly process but does NOT contain:
        • Provider implementations
        • Runtime state
        • Live references to subsystems
        
    CONFIGURATION GROUPS:
        
        capacity:
            • maximum_total_items: Hard limit on total items across all projections
            • per_projection_limits: Max items per projection kind
            
        freshness:
            • maximum_age_seconds: Oldest acceptable projection age
            • require_freshness_validation: Whether to validate freshness
            
        confidence:
            • minimum_confidence: Minimum acceptable confidence level (0.0-1.0)
            
        projection_requirements:
            • required_projection_kinds: Which projections are mandatory
            • optional_projection_kinds: Which are nice to have
            
        normalization:
            • stable_ordering: Whether to enforce deterministic ordering
            • normalize_string_length: Maximum string length for normalized values
            
        conflict_handling:
            • record_all_conflicts: Whether to keep all conflicts (not just first N)
            • maximum_conflict_records: How many conflicts to retain
            
        history:
            • maximum_history_entries: How many context snapshots to keep in memory
            • store_snapshots: Whether to store historical snapshots
            
        provenance:
            • record_provenance: Whether to track full provenance
            • maximum_provenance_entries: How many source references to retain
            
        validation:
            • strict_mode: Whether to fail on any validation issue
            • verify_projection_integrity: Whether to validate projection sources
            
        diagnostics:
            • enable_diagnostics: Whether to collect assembly metrics
    """
    
    # Capacity constraints
    maximum_total_items: int = 500
    """Maximum total items across all projections."""
    
    per_projection_limits: dict[str, int] = field(default_factory=lambda: {
        "objectives": 50,
        "commitments": 50,
        "memory": 200,
        "identity": 100,
        "narrative": 50,
        "prediction": 100,
        "workspace": 30,
        "working_memory": 50,
        "execution": 20,
        "attention": 50,
        "affect": 20,
        "concerns": 100,
        "resources": 20,
    })
    """Per-projection maximum item counts."""
    
    # Freshness constraints
    maximum_age_seconds: float = 3600.0  # 1 hour
    """Maximum age in seconds for projections (None = no constraint)."""
    
    require_freshness_validation: bool = True
    """Whether to validate projection freshness during assembly."""
    
    # Confidence constraints
    minimum_confidence: float = 0.3
    """Minimum acceptable confidence level (0.0 to 1.0)."""
    
    # Projection requirements
    required_projection_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Projection kinds that must be present (empty = no additional requirements)."""
    
    optional_projection_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Projection kinds that are desirable but not required."""
    
    # Normalization options
    stable_ordering: bool = True
    """Whether to enforce deterministic ordering of collections."""
    
    normalize_string_length: int | None = 256
    """Maximum string length for normalized values (None = no truncation)."""
    
    # Conflict handling
    record_all_conflicts: bool = False
    """Whether to keep all conflicts or only up to a limit."""
    
    maximum_conflict_records: int = 50
    """Maximum conflict records to retain when record_all_conflicts=False."""
    
    # History constraints
    maximum_history_entries: int = 100
    """How many context snapshots to keep in memory."""
    
    store_snapshots: bool = False
    """Whether to store historical snapshots for debugging."""
    
    # Provenance
    record_provenance: bool = True
    """Whether to track full provenance of assembly."""
    
    maximum_provenance_entries: int = 20
    """Maximum source references in provenance records."""
    
    # Validation
    strict_mode: bool = False
    """Whether to fail on any validation issue (vs. warning and proceeding)."""
    
    verify_projection_integrity: bool = True
    """Whether to validate projection sources during assembly."""
    
    # Diagnostics
    enable_diagnostics: bool = False
    """Whether to collect assembly metrics for diagnostics."""
    
    @classmethod
    def strict_config(cls) -> InternalContextConfig:
        """Create a configuration with stricter limits."""
        return cls(
            maximum_total_items=250,
            maximum_age_seconds=1800.0,  # 30 minutes
            minimum_confidence=0.6,
            record_all_conflicts=True,
            strict_mode=True,
            verify_projection_integrity=True,
        )
    
    @classmethod
    def permissive_config(cls) -> InternalContextConfig:
        """Create a configuration with relaxed limits for exploratory contexts."""
        return cls(
            maximum_total_items=1000,
            maximum_age_seconds=7200.0,  # 2 hours
            minimum_confidence=0.2,
            record_all_conflicts=False,
            strict_mode=False,
            verify_projection_integrity=False,
        )
    
    def get_projection_limit(self, kind: str) -> int:
        """Get the maximum items limit for a projection kind."""
        return self.per_projection_limits.get(kind, 50)