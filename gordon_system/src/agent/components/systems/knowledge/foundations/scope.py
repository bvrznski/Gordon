# Knowledge Scope - Phase 6.1
# ==========================

"""
Knowledge Scope: Semantic domain boundaries for knowledge artifacts.

Scope defines the boundaries of applicability and relevance for semantic
artifacts, enabling the system to understand when and where a piece of
knowledge is applicable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# SCOPE DOMAINS - Semantic domains where knowledge applies
# =============================================================================


class ScopeDomain(Enum):
    """
    Semantic domains for knowledge scope.
    
    Defines the primary domains of discourse in Gordon's knowledge system.
    """
    
    PHYSICAL = "physical"                 # Physical world phenomena
    SOCIAL = "social"                     # Social interactions and norms
    LOGICAL = "logical"                   # Logical reasoning and mathematics
    EMOTIONAL = "emotional"               # Emotional states and responses
    TEMPORAL = "temporal"                 # Time-related concepts
    CAUSAL = "causal"                     # Cause-and-effect relationships
    
    GENERAL = "general"                   # General or unspecified domain


# =============================================================================
# SCOPE BOUNDARIES - Domain boundaries
# =============================================================================


@dataclass(frozen=True)
class ScopeBoundary:
    """
    Boundary definition for a semantic scope.
    
    Defines the limits of applicability for knowledge within a domain.
    
    Fields:
        boundary_identity:   Unique identifier for this boundary
        domain:              Semantic domain this boundary applies to
        lower_bound:         Lower limit (inclusive, 0.0-1.0 scale)
        upper_bound:         Upper limit (inclusive, 0.0-1.0 scale)
        inclusive_lower:     Whether the lower bound is inclusive
        inclusive_upper:     Whether the upper bound is inclusive
    """
    
    # Identity and metadata (required)
    boundary_identity: str              # Unique identifier
    
    # Domain classification
    domain: ScopeDomain = ScopeDomain.GENERAL
    
    # Boundary values (0.0-1.0 scale, normalized)
    lower_bound: float = 0.0            # Lower limit (inclusive)
    upper_bound: float = 1.0            # Upper limit (inclusive)
    
    # Inclusivity flags
    inclusive_lower: bool = True
    inclusive_upper: bool = True
    
    @property
    def is_valid(self) -> bool:
        """Check if boundary has valid data."""
        return (
            self.lower_bound <= self.upper_bound and
            0.0 <= self.lower_bound <= 1.0 and
            0.0 <= self.upper_bound <= 1.0
        )
    
    def contains_value(self, value: float) -> bool:
        """
        Check if a value falls within this boundary.
        
        Args:
            value: Value to check (normalized 0.0-1.0)
            
        Returns:
            True if value is within the boundary
        """
        in_lower = (
            value >= self.lower_bound if self.inclusive_lower else
            value > self.lower_bound
        )
        in_upper = (
            value <= self.upper_bound if self.inclusive_upper else
            value < self.upper_bound
        )
        return in_lower and in_upper
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert boundary to dictionary for serialization."""
        return {
            "boundary_identity": self.boundary_identity,
            "domain": self.domain.value if hasattr(self.domain, 'value') else str(self.domain),
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "inclusive_lower": self.inclusive_lower,
            "inclusive_upper": self.inclusive_upper,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScopeBoundary":
        """Create boundary from dictionary."""
        return cls(
            boundary_identity=data.get("boundary_identity", ""),
            domain=ScopeDomain(data.get("domain", "general")),
            lower_bound=float(data.get("lower_bound", 0.0)),
            upper_bound=float(data.get("upper_bound", 1.0)),
            inclusive_lower=bool(data.get("inclusive_lower", True)),
            inclusive_upper=bool(data.get("inclusive_upper", True)),
        )


# =============================================================================
# SEMANTIC SCOPE - Complete scope definition
# =============================================================================


@dataclass(frozen=True)
class SemanticScope:
    """
    Complete semantic scope for a knowledge artifact.
    
    Defines all domain boundaries where an artifact is applicable and any
    exclusions that apply.
    
    Fields:
        scope_identity:      Unique identifier for this scope
        domains:             Applicable domains
        boundaries:          Boundary definitions per domain
        exclusions:          Domain-specific exclusions
        created_at_utc:      When scope was defined
        revision:            Revision number
    """
    
    # Identity and metadata (required)
    scope_identity: str                 # Unique ID for this scope
    
    # Scope definition
    domains: Tuple[ScopeDomain, ...] = field(default_factory=tuple)  # Applicable domains
    boundaries: Tuple[ScopeBoundary, ...] = field(default_factory=tuple)  # Domain boundaries
    exclusions: Tuple[str, ...] = field(default_factory=tuple)  # Excluded items
    
    # Tracking
    created_at_utc: float = field(default_factory=time.time)
    revision: int = 1                   # Revision number
    
    @property
    def is_valid(self) -> bool:
        """Check if scope has valid data."""
        return (
            len(self.scope_identity) > 0 and
            all(b.is_valid for b in self.boundaries)
        )
    
    def covers_domain(self, domain: ScopeDomain) -> bool:
        """
        Check if this scope covers a specific domain.
        
        Args:
            domain: Domain to check
            
        Returns:
            True if the scope covers this domain
        """
        return domain in self.domains
    
    def is_applicable(
        self,
        domain: ScopeDomain,
        value: Optional[float] = None,
    ) -> bool:
        """
        Check if knowledge is applicable for a given context.
        
        Args:
            domain: Context domain
            value: Optional value to check against boundaries
            
        Returns:
            True if the knowledge applies in this context
        """
        # Must be in applicable domains
        if not self.covers_domain(domain):
            return False
        
        # If no boundaries defined, always applicable
        if len(self.boundaries) == 0:
            return True
        
        # Check value against boundaries if provided
        if value is not None:
            return any(b.contains_value(value) for b in self.boundaries)
        
        # Otherwise, just check domain membership
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scope to dictionary for serialization."""
        return {
            "scope_identity": self.scope_identity,
            "domains": [d.value if hasattr(d, 'value') else str(d) for d in self.domains],
            "boundaries": [b.to_dict() for b in self.boundaries],
            "exclusions": list(self.exclusions),
            "created_at_utc": self.created_at_utc,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticScope":
        """Create scope from dictionary."""
        domains = []
        for d_data in data.get("domains", []):
            try:
                domains.append(ScopeDomain(d_data))
            except ValueError:
                pass  # Skip unknown domains
        
        boundaries = []
        for b_data in data.get("boundaries", []):
            boundaries.append(ScopeBoundary.from_dict(b_data))
        
        return cls(
            scope_identity=data.get("scope_identity", str(uuid.uuid4())),
            domains=tuple(domains),
            boundaries=tuple(boundaries),
            exclusions=tuple(data.get("exclusions", [])),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            revision=int(data.get("revision", 1)),
        )


# =============================================================================
# SCOPE VALIDATOR
# =============================================================================


class ScopeValidator:
    """
    Validates scope definitions for consistency.
    
    Ensures that scopes are well-formed and don't have conflicting boundaries.
    """
    
    def __init__(
        self,
        require_at_least_one_domain: bool = True,
    ):
        """
        Initialize the validator.
        
        Args:
            require_at_least_one_domain: Whether at least one domain is required
        """
        self._require_domain = require_at_least_one_domain
    
    def validate(self, scope: SemanticScope) -> Tuple[bool, List[str]]:
        """
        Validate a semantic scope definition.
        
        Args:
            scope: Scope to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Rule 1: Must have valid identity
        if not scope.scope_identity or len(scope.scope_identity) == 0:
            issues.append("Missing scope identity")
        
        # Rule 2: Must have at least one domain
        if self._require_domain and len(scope.domains) == 0:
            issues.append("No domains defined")
        
        # Rule 3: All boundaries must be valid
        for boundary in scope.boundaries:
            if not boundary.is_valid:
                issues.append(f"Invalid boundary: {boundary.boundary_identity}")
        
        # Rule 4: Boundaries must have corresponding domains
        boundary_domains = set(b.domain for b in scope.boundaries)
        scope_domains = set(scope.domains)
        extra_boundaries = boundary_domains - scope_domains
        if extra_boundaries:
            issues.append(f"Boundaries for undefined domains: {extra_boundaries}")
        
        return len(issues) == 0, issues


__all__ = [
    "ScopeDomain",
    "ScopeBoundary",
    "SemanticScope",
    "ScopeValidator",
]