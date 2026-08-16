# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Resource Allocation Model
=========================

Semantic resource allocation for orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ResourceAllocation:
    """
    Immutable resource allocation model.
    
    RESOURCE-LAW-001: Resource allocation remains semantic
    RESOURCE-LAW-002: Hardware allocation belongs outside the COE
    RESOURCE-LAW-003: Resource budgets shall remain explicit
    
    RESOURCE-INV-001: Allocation is immutable (deeply frozen)
    RESOURCE-INV-002: Allocation has no runtime references
    """
    
    compute_budget: int = 0
    """Semantic compute budget unit."""
    
    workspace_budget: int = 0
    """Semantic workspace capacity unit."""
    
    context_budget: int = 0
    """Semantic context window budget unit."""
    
    attention_budget: float = 1.0
    """Semantic attention allocation (0.0 to 1.0)."""
    
    latency_budget: float = 0.0
    """Semantic latency budget in semantic time units."""
    
    priority_budget: int = 0
    """Semantic priority unit."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def create(
        cls,
        compute_budget: int = 0,
        workspace_budget: int = 0,
        context_budget: int = 0,
        attention_budget: float = 1.0,
        latency_budget: float = 0.0,
        priority_budget: int = 0,
    ) -> ResourceAllocation:
        """
        Create a new resource allocation.
        
        Args:
            compute_budget: Semantic compute budget
            workspace_budget: Semantic workspace capacity
            context_budget: Semantic context window budget
            attention_budget: Attention allocation (0.0 to 1.0)
            latency_budget: Latency budget in semantic time units
            priority_budget: Priority unit
            
        Returns:
            A new ResourceAllocation instance
        """
        return cls(
            compute_budget=compute_budget,
            workspace_budget=workspace_budget,
            context_budget=context_budget,
            attention_budget=min(0.0, max(1.0, attention_budget)),
            latency_budget=latency_budget,
            priority_budget=priority_budget,
            provenance_ref="",
        )
    
    def __str__(self) -> str:
        return f"ResourceAllocation(compute={self.compute_budget}, workspace={self.workspace_budget})"