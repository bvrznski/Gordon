# Invariant Verification - Testing Infrastructure
# ==========================================

"""
InvariantVerifier: Verifies invariants are maintained.

This module provides invariant verification for:
- State preservation
- Property maintenance across operations
- Business rule consistency
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any


@dataclass(frozen=True)
class InvariantViolation:
    """Immutable representation of an invariant violation."""
    
    invariant_id: str
    operation_name: str
    violation_type: str  # PreconditionFailed, PostconditionFailed, StateCorrupted
    description: str
    state_before: Optional[str] = None
    state_after: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "invariant_id": self.invariant_id,
            "operation_name": self.operation_name,
            "violation_type": self.violation_type,
            "description": self.description,
            "state_before": self.state_before,
            "state_after": self.state_after,
        }


@dataclass(frozen=True)
class InvariantVerificationResult:
    """Immutable result of invariant verification."""
    
    invariant_id: str
    is_maintained: bool
    violations: List[InvariantViolation]
    operations_tested: int = 0
    
    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0


class InvariantVerifier:
    """
    Verifies that invariants are maintained across operations.
    
    This verifier checks:
    - Invariants hold before and after operations
    - State transitions preserve invariants
    - Properties remain true throughout execution
    """
    
    def __init__(self):
        """Initialize the invariant verifier."""
        self._invariants: Dict[str, Callable[[Any], bool]] = {}
        self._state_getters: Dict[str, Callable[[], Any]] = {}
    
    def register_invariant(self, invariant_id: str, check_fn: Callable[[Any], bool]) -> None:
        """
        Register an invariant for verification.
        
        Args:
            invariant_id: Unique identifier for the invariant
            check_fn: Function that checks if the invariant holds
        """
        self._invariants[invariant_id] = check_fn
    
    def register_state_getter(self, state_name: str, getter_fn: Callable[[], Any]) -> None:
        """
        Register a function to get current state.
        
        Args:
            state_name: Name of the state
            getter_fn: Function that returns current state
        """
        self._state_getters[state_name] = getter_fn
    
    def check_invariant(self, invariant_id: str, state: Any) -> bool:
        """
        Check if an invariant holds for a given state.
        
        Args:
            invariant_id: ID of the invariant to check
            state: The state to check against
            
        Returns:
            True if invariant holds, False otherwise
        """
        if invariant_id not in self._invariants:
            return False
        
        try:
            return self._invariants[invariant_id](state)
        except Exception:
            return False
    
    def verify_operation(
        self,
        operation_name: str,
        state_getter: Callable[[], Any],
        operation_fn: Callable[[], Any],
        invariant_ids: List[str],
    ) -> InvariantVerificationResult:
        """
        Verify invariants before and after an operation.
        
        Args:
            operation_name: Name of the operation being tested
            state_getter: Function to get current state
            operation_fn: The operation to execute
            invariant_ids: IDs of invariants to check
            
        Returns:
            InvariantVerificationResult with verification status
        """
        violations = []
        
        for invariant_id in invariant_ids:
            # Check precondition
            state_before = state_getter()
            
            if not self.check_invariant(invariant_id, state_before):
                violations.append(
                    InvariantViolation(
                        invariant_id=invariant_id,
                        operation_name=operation_name,
                        violation_type="PreconditionFailed",
                        description=f"Invariant '{invariant_id}' failed before operation",
                        state_before=str(state_before),
                        state_after=None,
                    )
                )
            
            # Execute operation
            try:
                result = operation_fn()
                state_after = state_getter()
                
                # Check postcondition
                if not self.check_invariant(invariant_id, state_after):
                    violations.append(
                        InvariantViolation(
                            invariant_id=invariant_id,
                            operation_name=operation_name,
                            violation_type="PostconditionFailed",
                            description=f"Invariant '{invariant_id}' failed after operation",
                            state_before=str(state_before),
                            state_after=str(state_after),
                        )
                    )
            except Exception as e:
                violations.append(
                    InvariantViolation(
                        invariant_id=invariant_id,
                        operation_name=operation_name,
                        violation_type="StateCorrupted",
                        description=f"Operation raised exception: {e}",
                        state_before=str(state_getter()),
                        state_after=None,
                    )
                )
        
        return InvariantVerificationResult(
            invariant_id=invariant_ids[0] if invariant_ids else "unknown",
            is_maintained=len(violations) == 0,
            violations=violations,
            operations_tested=1 if len(violations) == 0 else 0,
        )
    
    def verify_all_invariants(self, state: Any, invariant_ids: List[str]) -> Dict[str, bool]:
        """
        Check multiple invariants against a state.
        
        Args:
            state: The state to check
            invariant_ids: IDs of invariants to check
            
        Returns:
            Dictionary mapping invariant_id to whether it holds
        """
        results = {}
        
        for invariant_id in invariant_ids:
            results[invariant_id] = self.check_invariant(invariant_id, state)
        
        return results


def verify_invariant(
    invariant_id: str,
    state: Any,
    verifier: Optional[InvariantVerifier] = None,
) -> bool:
    """
    Convenience function to verify an invariant.
    
    Args:
        invariant_id: ID of the invariant
        state: The state to check
        verifier: InvariantVerifier instance (creates new if None)
        
    Returns:
        True if invariant holds, False otherwise
    """
    v = verifier or InvariantVerifier()
    return v.check_invariant(invariant_id, state)


def check_state_preservation(
    operation_fn: Callable[[], Any],
    invariant_ids: List[str],
) -> InvariantVerificationResult:
    """
    Verify invariants are preserved across an operation.
    
    Args:
        operation_fn: The operation to execute
        invariant_ids: IDs of invariants to check
        
    Returns:
        InvariantVerificationResult with verification status
    """
    verifier = InvariantVerifier()
    
    def dummy_getter():
        return None
    
    return verifier.verify_operation(
        operation_name="state_preservation_test",
        state_getter=dummy_getter,
        operation_fn=operation_fn,
        invariant_ids=invariant_ids,
    )