# Correlation and Causation Contracts (Phase 4.3.13)
# ====================================================

"""
Correlation and causation tracking for integration contracts.

All cross-boundary interactions must preserve both correlation and causation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# INTEGRATION CORRELATION CHAIN (Phase 4.3.13)
# =============================================================================

@dataclass(frozen=True, slots=True)
class IntegrationCorrelationChain:
    """
    Immutable correlation chain for distributed tracing.
    
    Correlation groups semantically related operations across system boundaries.
    Examples: one user request, one TaskThread objective, one InternalEpisode.
    
    IMPORTANT: Correlation is distinct from causation - do not confuse them!
    """
    
    correlation_id: str
    """Identifier for this correlation chain."""
    
    created_at_utc: str
    """When the correlation was established (ISO 8601)."""
    
    creator_system: str = "Unknown"
    """System that initiated the correlation."""
    
    parent_correlation_id: str | None = None
    """Parent correlation ID if this is a nested operation."""
    
    @classmethod
    def new(
        cls,
        correlation_id: str,
        created_at_utc: str,
        creator_system: str = "Unknown",
        parent_correlation_id: str | None = None,
    ) -> IntegrationCorrelationChain:
        """Create a new correlation chain."""
        return cls(
            correlation_id=correlation_id,
            created_at_utc=created_at_utc,
            creator_system=creator_system,
            parent_correlation_id=parent_correlation_id,
        )


# =============================================================================
# INTEGRATION CAUSATION CHAIN (Phase 4.3.13)
# =============================================================================

@dataclass(frozen=True, slots=True)
class IntegrationCausationChain:
    """
    Immutable causation chain for semantic lineage tracking.
    
    Causation identifies the direct semantic predecessor in a chain of
    semantic operations.
    
    Example chain:
        DefaultNetworkInvocation
            causes ReflectionCapabilityRequest
        
        ReflectionCapabilityRequest
            causes ReflectionCapabilityResult
        
        ReflectionCapabilityResult
            causes ReflectiveProduct
    
    IMPORTANT: Do not use correlation alone as causal lineage!
    """
    
    causation_id: str | None  # Optional - may be None for first in chain
    """Identifier for the direct predecessor."""
    
    operation_name: str
    """Name of this operation in the causation chain."""
    
    resulting_entity_type: str
    """Type of entity produced by this operation."""
    
    @classmethod
    def new(
        cls,
        operation_name: str,
        resulting_entity_type: str,
        causation_id: str | None = None,
    ) -> IntegrationCausationChain:
        """Create a new causation chain entry."""
        return cls(
            causation_id=causation_id,
            operation_name=operation_name,
            resulting_entity_type=resulting_entity_type,
        )


# =============================================================================
# CORRELATION AND CAUSATION MANAGER (Phase 4.3.13)
# =============================================================================

class IntegrationCorrelationManager:
    """
    Manager for correlation and causation tracking.
    
    This is a metadata manager only - it does not perform any runtime operations.
    It simply validates and tracks the relationships between operations.
    """
    
    def __init__(self) -> None:
        self._correlations: dict[str, IntegrationCorrelationChain] = {}
        self._causations: list[IntegrationCausationChain] = []
    
    def create_correlation(
        self,
        correlation_id: str,
        created_at_utc: str,
        creator_system: str = "Unknown",
        parent_correlation_id: str | None = None,
    ) -> IntegrationCorrelationChain:
        """Create a new correlation and record it."""
        chain = IntegrationCorrelationChain.new(
            correlation_id=correlation_id,
            created_at_utc=created_at_utc,
            creator_system=creator_system,
            parent_correlation_id=parent_correlation_id,
        )
        self._correlations[correlation_id] = chain
        return chain
    
    def record_causation(
        self,
        operation_name: str,
        resulting_entity_type: str,
        causation_id: str | None = None,
    ) -> IntegrationCausationChain:
        """Record a new causation entry."""
        entry = IntegrationCausationChain.new(
            operation_name=operation_name,
            resulting_entity_type=resulting_entity_type,
            causation_id=causation_id,
        )
        self._causations.append(entry)
        return entry
    
    def get_correlation(self, correlation_id: str) -> IntegrationCorrelationChain | None:
        """Get a correlation chain by ID."""
        return self._correlations.get(correlation_id)
    
    @property
    def correlations(self) -> dict[str, IntegrationCorrelationChain]:
        """Read-only access to all correlations."""
        return dict(self._correlations)
    
    @property
    def causations(self) -> Tuple[IntegrationCausationChain, ...]:
        """Read-only access to all causation entries."""
        return tuple(self._causations)


__all__ = [
    "IntegrationCorrelationChain",
    "IntegrationCausationChain",
    "IntegrationCorrelationManager",
]