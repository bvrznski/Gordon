# Thread Identity
# ===============

"""
Semantic Thread identity model.

Thread identity is:
    - Immutable (cannot change once created)
    - Unique within its execution domain
    - Stable across suspension and resumption
    - Distinct from runtime handles, scheduler task IDs, persistence record IDs
"""

from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass(frozen=True)
class ThreadId:
    """
    Immutable semantic identifier for a Thread.
    
    ThreadId is the canonical identity - all references to this thread must use
    this exact instance or an equal value. It is NOT:
        - A runtime execution handle
        - A scheduler task ID
        - A persistence record ID
    
    These may map to ThreadId but are distinct concepts.
    """
    
    value: str  # The actual identifier string
    
    @classmethod
    def generate(cls) -> "ThreadId":
        """Generate a new unique thread ID."""
        return cls(value=str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ThreadName:
    """
    Human-readable name for a Thread.
    
    Not used for identity comparison - only for display and debugging.
    """
    
    value: str
    
    @classmethod
    def from_purpose(cls, purpose: str) -> "ThreadName":
        """Generate a thread name from its purpose."""
        # Sanitize: lowercase, replace spaces with underscores, truncate
        sanitized = purpose.lower().replace(" ", "_")[:50]
        return cls(value=sanitized)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ThreadMetadata:
    """
    Immutable metadata associated with a Thread.
    
    Contains semantic information that helps identify the thread's role
    without exposing mutable state.
    """
    
    # Basic identification
    thread_id: ThreadId
    name: Optional[ThreadName] = None
    
    # Purpose (why this thread exists)
    purpose: Optional[str] = None
    
    # Creation metadata
    created_at_utc: float = field(default_factory=lambda: 0.0)  # Set by system
    created_by: Optional[str] = None  # Who/what created it
    
    # Classification
    kind: str = "default"  # e.g., "conversation", "planning", "monitoring"
    
    # Semantic version (monotonically increases with state changes)
    semantic_version: int = 0


@dataclass(frozen=True)
class ThreadDescriptor:
    """
    Read-only descriptor for identifying and referencing a Thread.
    
    Used when you need to reference a thread without exposing its full state.
    Think of this as the "pointer" to a thread rather than the thread itself.
    """
    
    thread_id: ThreadId
    name: Optional[str] = None
    kind: Optional[str] = None
    
    # Lifecycle information (owned by Core for runtime, but here for reference)
    is_active: bool = False
    is_completed: bool = False
    
    # Parent relationship (optional)
    parent_thread_id: Optional[ThreadId] = None
    
    @classmethod
    def from_metadata(cls, metadata: ThreadMetadata) -> "ThreadDescriptor":
        """Create a descriptor from full metadata."""
        return cls(
            thread_id=metadata.thread_id,
            name=metadata.name.value if metadata.name else None,
            kind=metadata.kind,
            is_active=False,  # Lifecycle state comes from Core
            is_completed=False,
            parent_thread_id=None,
        )


__all__ = [
    "ThreadId",
    "ThreadName",
    "ThreadMetadata",
    "ThreadDescriptor",
]