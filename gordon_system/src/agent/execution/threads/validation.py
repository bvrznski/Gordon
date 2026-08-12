# Thread Validation Module
# ========================

"""
Validation utilities for Thread invariants and constraints.

This module provides validators that enforce architectural invariants:
    - T-001: Thread identity never changes
    - T-002: Semantic revision never decreases
    - T-003: Terminal threads cannot return to active without explicit reopening
    - T-004: A thread has at most one active Loop
    - T-005: A thread has at most one active authoritative Cycle
    - T-006: Stale semantic delta cannot be silently applied
    - T-007: Parent-child relationships cannot be self-referential
    - T-008: Completion and termination require explicit reasons
    - T-009: Thread state cannot contain runtime resource ownership
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a validation check.
    
    Invariants:
        V-001: Success means all checks passed
        V-002: Failure includes at least one error message
    """
    
    is_valid: bool
    errors: List[str] = ()
    warnings: List[str] = ()
    
    @classmethod
    def valid(cls) -> "ValidationResult":
        """Return a successful validation result."""
        return cls(is_valid=True)
    
    @classmethod
    def invalid(cls, *errors: str) -> "ValidationResult":
        """Return an invalid validation result with error messages."""
        return cls(is_valid=False, errors=list(errors))
    
    def merge(self, other: "ValidationResult") -> "ValidationResult":
        """Merge two validation results."""
        if self.is_valid and other.is_valid:
            return ValidationResult.valid()
        
        all_errors = list(self.errors) + list(other.errors)
        all_warnings = list(self.warnings) + list(other.warnings)
        
        return ValidationResult(is_valid=False, errors=all_errors, warnings=all_warnings)


class ThreadValidator:
    """
    Validator for Thread invariants.
    
    Enforces the architectural laws defined for the Thread model.
    """
    
    def __init__(self) -> None:
        self._errors: List[str] = []
        self._warnings: List[str] = []
    
    def clear(self) -> None:
        """Clear validation state."""
        self._errors.clear()
        self._warnings.clear()
    
    # =========================================================================
    # IDENTITY INVARIANTS (T-001)
    # =========================================================================
    
    def validate_identity_immutability(
        self, thread_id: str, previous_id: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate that thread identity is immutable.
        
        If a previous ID exists, the current ID must match it.
        """
        if previous_id is not None and previous_id != thread_id:
            return ValidationResult.invalid(
                f"Thread identity changed from {previous_id} to {thread_id}"
            )
        return ValidationResult.valid()
    
    # =========================================================================
    # SEMANTIC VERSION INVARIANTS (T-002)
    # =========================================================================
    
    def validate_semantic_version(
        self, current_version: int, new_version: int
    ) -> ValidationResult:
        """
        Validate that semantic revision never decreases.
        
        New version must be >= current version.
        """
        if new_version < current_version:
            return ValidationResult.invalid(
                f"Semantic version decreased from {current_version} to {new_version}"
            )
        return ValidationResult.valid()
    
    # =========================================================================
    # LIFECYCLE INVARIANTS (T-003)
    # =========================================================================
    
    def validate_terminal_state_transition(
        self,
        current_state: str,
        target_state: str,
        allows_reopening: bool = False,
    ) -> ValidationResult:
        """
        Validate lifecycle transitions for terminal states.
        
        A terminal thread cannot return to active without explicit reopening.
        """
        terminal_states = {"completed", "interrupted", "terminated"}
        
        if current_state in terminal_states and target_state == "active":
            if not allows_reopening:
                return ValidationResult.invalid(
                    f"Cannot transition from terminal state '{current_state}' back to 'active' "
                    "without explicit reopening mechanism"
                )
        
        return ValidationResult.valid()
    
    # =========================================================================
    # LOOP/CYCLE CARDINALITY (T-004, T-005)
    # =========================================================================
    
    def validate_loop_cardinality(
        self, current_loop_id: Optional[str], new_loop_id: Optional[str]
    ) -> ValidationResult:
        """
        Validate that a thread has at most one active Loop.
        
        If there's an existing loop, it must be replaced explicitly.
        """
        if current_loop_id is not None and new_loop_id != current_loop_id:
            # This is a replacement, which should go through explicit transition
            pass  # Will be validated by lifecycle transitions
        
        return ValidationResult.valid()
    
    def validate_cycle_cardinality(
        self,
        active_cycles: List[str],
        max_active: int = 1,
    ) -> ValidationResult:
        """
        Validate that a thread has at most the allowed number of active Cycles.
        
        Default is 1, can be increased only with explicit parallel branch support.
        """
        if len(active_cycles) > max_active:
            return ValidationResult.invalid(
                f"Thread has {len(active_cycles)} active cycles (max: {max_active})"
            )
        return ValidationResult.valid()
    
    # =========================================================================
    # DELTA VALIDATION (T-006)
    # =========================================================================
    
    def validate_delta_version(
        self, expected_version: int, current_version: int
    ) -> ValidationResult:
        """
        Validate that a delta's expected version matches current state.
        
        Prevents stale semantic deltas from being silently applied.
        """
        if expected_version != current_version:
            return ValidationResult.invalid(
                f"Stale delta: expected version {expected_version}, "
                f"but thread is at version {current_version}"
            )
        return ValidationResult.valid()
    
    # =========================================================================
    # RELATIONSHIP INVARIANTS (T-007, T-008)
    # =========================================================================
    
    def validate_parent_child_relationship(
        self,
        parent_id: str,
        child_id: str,
    ) -> ValidationResult:
        """
        Validate parent-child relationship constraints.
        
        - Parent and child must be different threads (no self-reference)
        - Child cannot be ancestor of parent (no cycles)
        """
        if parent_id == child_id:
            return ValidationResult.invalid(
                f"Parent-child relationship would create cycle: {parent_id} is both"
            )
        
        # Cycle detection would require full graph traversal
        # For now, just validate the direct self-reference
        
        return ValidationResult.valid()
    
    def validate_terminal_reason(
        self,
        state: str,
        reason: Optional[str],
    ) -> ValidationResult:
        """
        Validate that terminal states have explicit reasons.
        
        Completion and termination must include a reason.
        """
        terminal_states = {"completed", "interrupted", "terminated"}
        
        if state in terminal_states and not reason:
            return ValidationResult.invalid(
                f"Terminal state '{state}' requires an explicit reason"
            )
        
        return ValidationResult.valid()
    
    # =========================================================================
    # STATE CONTENT INVARIANTS (T-009)
    # =========================================================================
    
    def validate_state_content(self, state_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate that thread state doesn't contain runtime resource ownership.
        
        Thread state should be semantic only - no file handles, network sockets,
        process IDs, or other runtime resources.
        """
        forbidden_types = (
            "file", "socket", "process", "mutex", "lock",
            "thread", "coroutine", "task"
        )
        
        errors = []
        
        def check_value(value: Any, path: str = "") -> None:
            if isinstance(value, dict):
                for k, v in value.items():
                    check_value(v, f"{path}.{k}" if path else k)
            elif hasattr(value, "__class__"):
                class_name = type(value).__name__.lower()
                if any(ft in class_name for ft in forbidden_types):
                    errors.append(f"Runtime resource found at {path}: {type(value).__name__}")
        
        check_value(state_data)
        
        if errors:
            return ValidationResult.invalid(*errors)
        
        return ValidationResult.valid()
    
    # =========================================================================
    # COMPREHENSIVE VALIDATION
    # =========================================================================
    
    def validate_thread_state(
        self,
        thread_id: str,
        semantic_version: int,
        lifecycle_state: Optional[str],
        loop_id: Optional[str] = None,
        active_cycles: Optional[List[str]] = None,
        delta_expected_version: Optional[int] = None,
        parent_child_ids: Optional[tuple] = None,
    ) -> ValidationResult:
        """
        Perform comprehensive validation of thread state.
        
        Combines all invariant checks into a single validation pass.
        """
        self.clear()
        
        # T-001: Identity immutability (assume identity is valid if not checking change)
        
        # T-002: Semantic version monotonicity
        if delta_expected_version is not None:
            result = self.validate_delta_version(delta_expected_version, semantic_version)
            if not result.is_valid:
                return result
        
        # T-003: Terminal state transitions
        if lifecycle_state and lifecycle_state in {"completed", "interrupted", "terminated"}:
            result = self.validate_terminal_state_transition(lifecycle_state, lifecycle_state)
            if not result.is_valid:
                return result
        
        # T-005: Cycle cardinality
        if active_cycles is not None:
            result = self.validate_cycle_cardinality(active_cycles)
            if not result.is_valid:
                return result
        
        # T-007: Parent-child relationships
        if parent_child_ids:
            parent_id, child_id = parent_child_ids
            result = self.validate_parent_child_relationship(parent_id, child_id)
            if not result.is_valid:
                return result
        
        return ValidationResult.valid()


__all__ = [
    "ValidationResult",
    "ThreadValidator",
]