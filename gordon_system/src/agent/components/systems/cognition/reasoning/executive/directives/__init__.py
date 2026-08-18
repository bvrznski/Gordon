# Executive Directives - Phase 7.30
# ==================================

"""
Executive Directive Management.

Directives determine:
    - Which subsystem to activate/pause/etc
    - Priority of the directive
    - Conditions for activation/expiration

Directives remain explicit and inspectable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

from .shared import (
    SubsystemType,
    DirectiveKind,
    DirectiveStatus,
    DirectiveManagement,
)


@dataclass(frozen=True)
class ExecutiveDirective:
    """
    An explicit executive directive.
    
    A directive specifies:
        - What action to take (activate/pause/etc.)
        - Which subsystem is affected
        - Priority and timing constraints
        - Conditions for execution
    """
    
    # Identity
    directive_id: str                           # Unique identifier
    
    # Directive details
    directive_kind: DirectiveKind               # What kind of directive?
    target_subsystem: SubsystemType             # Affected subsystem
    
    # Configuration
    priority: int = 10                          # 1-100 (higher = more urgent)
    conditions: Dict[str, Any] = field(default_factory=dict)  # Pre-conditions
    
    # Status tracking
    status: DirectiveStatus = DirectiveStatus.PENDING
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Rationale (why this directive?)
    rationale: str = ""                         # Human-readable explanation
    
    # Timing
    issued_at_utc: float = field(default_factory=time.time)
    
    @property
    def duration_seconds(self) -> float:
        """Calculate execution duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        return 0.0
    
    @classmethod
    def create(
        cls,
        directive_kind: DirectiveKind,
        target_subsystem: SubsystemType,
        priority: int = 10,
        rationale: str = "",
    ) -> "ExecutiveDirective":
        """Create a new executive directive."""
        return cls(
            directive_id=f"directive:{uuid.uuid4().hex[:16]}",
            directive_kind=directive_kind,
            target_subsystem=target_subsystem,
            priority=priority,
            rationale=rationale,
            issued_at_utc=time.time(),
        )
    
    def with_status(self, new_status: DirectiveStatus) -> "ExecutiveDirective":
        """Return a copy with updated status."""
        return dataclass_replace(
            self,
            status=new_status,
            completed_at_utc=time.time() if new_status == DirectiveStatus.COMPLETED else None,
            started_at_utc=self.started_at_utc or time.time(),
        )


@dataclass(frozen=True)
class DirectiveAuthority:
    """
    Authority to issue directives.
    
    Defines:
        - Who can issue which kinds of directives
        - Under what conditions
        - To which subsystems
    """
    
    # Identity
    authority_id: str                           # Unique identifier
    
    # Authority scope
    directive_kinds: Tuple[DirectiveKind, ...]  # Which kinds allowed?
    target_subsystems: Tuple[SubsystemType, ...]  # Which targets allowed?
    
    # Priority limits
    max_priority: int = 100                     # Maximum priority allowed
    
    # Conditions required
    required_conditions: Tuple[str, ...] = ()   # Must-be-true conditions
    
    @classmethod
    def create(
        cls,
        directive_kinds: Optional[List[DirectiveKind]] = None,
        target_subsystems: Optional[List[SubsystemType]] = None,
        max_priority: int = 100,
    ) -> "DirectiveAuthority":
        """Create a new authority."""
        return cls(
            authority_id=f"directive_authority:{uuid.uuid4().hex[:16]}",
            directive_kinds=tuple(directive_kinds or list(DirectiveKind)),
            target_subsystems=tuple(target_subsystems or list(SubsystemType)),
            max_priority=max_priority,
        )


@dataclass(frozen=True)
class DirectiveQueue:
    """
    Queue for pending executive directives.
    
    Maintains:
        - Ordered execution queue (by priority)
        - Status tracking
        - Dependency management
    """
    
    # Identity
    queue_id: str                               # Unique identifier
    
    # Directives in queue (sorted by priority, then timestamp)
    pending_directives: Tuple[ExecutiveDirective, ...] = ()
    
    # Currently executing
    executing_directive: Optional[ExecutiveDirective] = None
    
    # Completed/failed directives
    completed_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @property
    def queue_length(self) -> int:
        """Count of pending directives."""
        return len(self.pending_directives)
    
    @classmethod
    def create(cls, queue_id: Optional[str] = None) -> "DirectiveQueue":
        """Create a new directive queue."""
        return cls(
            queue_id=queue_id or f"directive_queue:{uuid.uuid4().hex[:16]}",
        )
    
    def add_directive(self, directive: ExecutiveDirective) -> "DirectiveQueue":
        """Add a directive to the queue (sorted by priority)."""
        new_directives = tuple(sorted(
            self.pending_directives + (directive,),
            key=lambda d: (-d.priority, d.issued_at_utc),  # Higher priority first
        ))
        return dataclass_replace(self, pending_directives=new_directives)
    
    def pop_next(self) -> Tuple[ExecutiveDirective, "DirectiveQueue"]:
        """Get the next directive and remaining queue."""
        if not self.pending_directives:
            raise ValueError("Queue is empty")
        
        next_directive = self.pending_directives[0]
        remaining = self.pending_directives[1:]
        return next_directive, dataclass_replace(
            self,
            pending_directives=remaining,
            executing_directive=next_directive,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutiveDirective",
    "DirectiveAuthority",
    "DirectiveQueue",
]