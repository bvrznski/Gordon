# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Recovery Coordination Models
============================

Models for recovery coordination during orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class RecoveryStrategy:
    """
    Immutable recovery strategy model.
    
    RECOVERY-LAW-001: Recovery coordination shall remain declarative
    RECOVERY-LAW-002: Recovery shall preserve failed participants
    RECOVERY-LAW-003: Recovery strategies shall remain explicit
    
    Suggested strategies per spec:
        RETRY - attempt the operation again
        SUBSTITUTE_NETWORK - use a different network
        SKIP_OPTIONAL_STAGE - skip an optional stage
        REDUCE_SCOPE - reduce the scope of the cycle
        SAFE_TERMINATION - terminate safely with partial results
        WAIT_FOR_RECOVERY - wait for unavailable components
    """
    
    STRATEGY_RETRY = "retry"
    """Attempt the operation again."""
    
    STRATEGY_SUBSTITUTE_NETWORK = "substitute_network"
    """Use a different network as substitute."""
    
    STRATEGY_SKIP_OPTIONAL_STAGE = "skip_optional_stage"
    """Skip an optional stage."""
    
    STRATEGY_REDUCE_SCOPE = "reduce_scope"
    """Reduce the scope of the cycle."""
    
    STRATEGY_SAFE_TERMINATION = "safe_termination"
    """Terminate safely with partial results."""
    
    STRATEGY_WAIT_FOR_RECOVERY = "wait_for_recovery"
    """Wait for unavailable components."""
    
    def __init__(self, strategy_type: str):
        self._type = strategy_type
    
    @property
    def type(self) -> str:
        return self._type
    
    def is_retry(self) -> bool:
        return self._type == self.STRATEGY_RETRY
    
    def is_substitute_network(self) -> bool:
        return self._type == self.STRATEGY_SUBSTITUTE_NETWORK
    
    def is_skip_optional_stage(self) -> bool:
        return self._type == self.STRATEGY_SKIP_OPTIONAL_STAGE
    
    def is_reduce_scope(self) -> bool:
        return self._type == self.STRATEGY_REDUCE_SCOPE
    
    def is_safe_termination(self) -> bool:
        return self._type == self.STRATEGY_SAFE_TERMINATION
    
    def is_wait_for_recovery(self) -> bool:
        return self._type == self.STRATEGY_WAIT_FOR_RECOVERY
    
    def __str__(self) -> str:
        return f"RecoveryStrategy({self._type})"


@dataclass(frozen=True, slots=True)
class RecoveryCoordination:
    """
    Immutable recovery coordination model.
    
    RECOVERY-LAW-004: Recovery shall preserve selected alternatives
    RECOVERY-LAW-005: Recovery findings shall remain explicit
    RECOVERY-LAW-006: Recovery limitations shall remain explicit
    
    RECOVERY-INV-001: Recovery coordination is immutable (deeply frozen)
    RECOVERY-INV-002: Recovery coordination has no runtime references
    """
    
    strategy: str  # RecoveryStrategy.*
    """Recovery strategy to use."""
    
    failed_network_refs: tuple[str, ...] = ()
    """References to networks that failed."""
    
    alternative_network_refs: tuple[str, ...] = ()
    """Alternative networks available for recovery."""
    
    findings: tuple[str, ...] = ()
    """Findings from the recovery process."""
    
    limitations: tuple[str, ...] = ()
    """Limitations of the recovery."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def create(
        cls,
        strategy: str,
        failed_network_refs: tuple[str, ...] = (),
        alternative_network_refs: tuple[str, ...] = (),
        findings: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
    ) -> RecoveryCoordination:
        """
        Create a new recovery coordination.
        
        Args:
            strategy: Recovery strategy to use
            failed_network_refs: Networks that failed
            alternative_network_refs: Alternative networks available
            findings: Findings from recovery process
            limitations: Limitations of the recovery
            
        Returns:
            A new RecoveryCoordination instance
        """
        return cls(
            strategy=strategy,
            failed_network_refs=tuple(failed_network_refs),
            alternative_network_refs=tuple(alternative_network_refs),
            findings=tuple(findings),
            limitations=tuple(limitations),
            provenance_ref="",
        )
    
    def __str__(self) -> str:
        return f"RecoveryCoordination(strategy={self.strategy}, failed={len(self.failed_network_refs)})"