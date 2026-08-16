# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Execution Policy Models
=======================

Policies that influence orchestration behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ExecutionPolicy:
    """
    Immutable execution policy model.
    
    POLICY-LAW-001: Every orchestration shall reference exactly one execution policy
    POLICY-LAW-002: Policies influence orchestration without altering cognition
    
    Suggested policies per spec:
        LATENCY_OPTIMIZED - minimize response time
        THROUGHPUT_OPTIMIZED - maximize processing rate
        RESOURCE_EFFICIENT - minimize resource usage
        SAFETY_FIRST - prioritize safety over speed
        EXPLORATORY - encourage experimentation
        DETERMINISTIC - ensure reproducibility
    """
    
    policy_type: str = ""
    """Type of execution policy."""
    
    latency_budget_ms: float = 0.0
    """Latency budget in milliseconds (semantic)."""
    
    throughput_target: float = 0.0
    """Throughput target per semantic time unit."""
    
    resource_efficiency_target: float = 1.0
    """Resource efficiency target (0.0 to 1.0)."""
    
    safety_constraints: tuple[str, ...] = ()
    """Safety constraints that must be enforced."""
    
    exploration_bonus: float = 0.0
    """Exploration bonus for alternative strategies."""
    
    deterministic_ordering: bool = True
    """Whether to enforce deterministic ordering."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def latency_optimized(cls, budget_ms: float = 100.0) -> ExecutionPolicy:
        """Create a latency-optimized policy."""
        return cls(
            policy_type="latency_optimized",
            latency_budget_ms=budget_ms,
            deterministic_ordering=True,
        )
    
    @classmethod
    def throughput_optimized(cls, target: float = 100.0) -> ExecutionPolicy:
        """Create a throughput-optimized policy."""
        return cls(
            policy_type="throughput_optimized",
            throughput_target=target,
            deterministic_ordering=False,
        )
    
    @classmethod
    def resource_efficient(cls) -> ExecutionPolicy:
        """Create a resource-efficient policy."""
        return cls(
            policy_type="resource_efficient",
            resource_efficiency_target=0.8,
            deterministic_ordering=True,
        )
    
    @classmethod
    def safety_first(cls, constraints: tuple[str, ...] = ()) -> ExecutionPolicy:
        """Create a safety-first policy."""
        return cls(
            policy_type="safety_first",
            safety_constraints=constraints,
            deterministic_ordering=True,
        )
    
    @classmethod
    def exploratory(cls) -> ExecutionPolicy:
        """Create an exploratory policy."""
        return cls(
            policy_type="exploratory",
            exploration_bonus=0.1,
            deterministic_ordering=False,
        )
    
    @classmethod
    def deterministic(cls) -> ExecutionPolicy:
        """Create a deterministic policy."""
        return cls(
            policy_type="deterministic",
            deterministic_ordering=True,
        )
    
    def is_latency_optimized(self) -> bool:
        return self.policy_type == "latency_optimized"
    
    def is_throughput_optimized(self) -> bool:
        return self.policy_type == "throughput_optimized"
    
    def is_resource_efficient(self) -> bool:
        return self.policy_type == "resource_efficient"
    
    def is_safety_first(self) -> bool:
        return self.policy_type == "safety_first"
    
    def is_exploratory(self) -> bool:
        return self.policy_type == "exploratory"
    
    def is_deterministic(self) -> bool:
        return self.policy_type == "deterministic"
    
    def __str__(self) -> str:
        return f"ExecutionPolicy({self.policy_type})"