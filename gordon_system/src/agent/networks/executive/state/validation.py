# Executive State Validation
# ==========================

"""
Validation types for executive state and context.

Provides typed failures for validation errors rather than generic exceptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveStateRevisionConflict:
    """
    Typed error for revision conflicts in executive state.
    
    A conflict occurs when a delta expects one base revision but the actual
    state has a different (newer) revision. This prevents silent overwrites.
    """
    
    expected_base_revision: int = 0
    """The base revision that was expected."""
    
    actual_state_revision: int = 1
    """The actual current revision of the state."""
    
    target_identity: str = "exec_state_unknown"
    """Identity being targeted by the operation."""
    
    conflicting_operation: str = "unknown"
    """Operation that caused the conflict (e.g., 'state_update')."""
    
    originating_request_id: Optional[str] = None
    """ID of the request that triggered this conflict."""
    
    impact: str = "delta_rejected"
    """Impact of the conflict on state changes."""
    
    recoverable: bool = True
    """Whether the operation can be retried after fetching latest state."""
    
    provenance_id: Optional[str] = None
    """ID of provenance record for this conflict."""
    
    @property
    def is_stale(self) -> bool:
        """Check if the delta is stale (base revision too old)."""
        return self.actual_state_revision > self.expected_base_revision


@dataclass(frozen=True)
class ExecutiveContextRevisionConflict:
    """
    Typed error for revision conflicts in executive context.
    """
    
    expected_context_revision: int = 1
    """The context revision that was expected."""
    
    actual_context_revision: int = 2
    """The actual current revision of the context."""
    
    affected_source_id: Optional[str] = None
    """Source ID affected by the conflict."""
    
    @property
    def is_stale(self) -> bool:
        return self.actual_context_revision > self.expected_context_revision


@dataclass(frozen=True)
class ExecutiveStateValidation:
    """
    Validation results for executive state.
    """
    
    valid: bool = True
    """Whether the state is valid."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation error messages."""
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation warning messages."""
    
    @classmethod
    def valid(cls) -> ExecutiveStateValidation:
        return cls(valid=True)
    
    @classmethod
    def invalid(cls, errors: Tuple[str, ...]) -> ExecutiveStateValidation:
        return cls(valid=False, errors=errors)


@dataclass(frozen=True)
class ExecutiveContextValidation:
    """
    Validation results for executive context.
    """
    
    valid: bool = True
    """Whether the context is valid."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation error messages."""
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation warning messages."""
    
    @classmethod
    def valid(cls) -> ExecutiveContextValidation:
        return cls(valid=True)
    
    @classmethod
    def invalid(cls, errors: Tuple[str, ...]) -> ExecutiveContextValidation:
        return cls(valid=False, errors=errors)


__all__: Tuple[str, ...] = (
    "ExecutiveStateRevisionConflict",
    "ExecutiveContextRevisionConflict",
    "ExecutiveStateValidation",
    "ExecutiveContextValidation",
)