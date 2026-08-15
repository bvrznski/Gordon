# Executive State Identity Types
# ==============================

"""
Identity types for executive state and context.

These provide stable, immutable identifiers for state entities that are
distinct from runtime or subsystem identities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
import hashlib


# =============================================================================
# STATE IDENTITY TYPES
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateId:
    """
    Unique identifier for an Executive State instance.
    
    State IDs are stable across state revisions - they identify the same
    logical state entity even as its contents change.
    """
    
    value: str = field(default_factory=lambda: f"exec_state_{hashlib.sha256(b'initial').hexdigest()[:16]}")
    
    @classmethod
    def generate(cls) -> ExecutiveStateId:
        """Generate a new unique state ID."""
        import uuid
        return cls(value=f"exec_state_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def initial(cls) -> ExecutiveStateId:
        """Return the canonical initial state ID."""
        return cls(value="exec_state_initial")


@dataclass(frozen=True)
class ExecutiveStateRevision:
    """
    Revision identifier for an Executive State.
    
    Revisions are strictly monotonic integers representing the state's
    position in its history. Each transition produces a new revision.
    """
    
    value: int = 0
    
    def next(self) -> ExecutiveStateRevision:
        """Return the next revision number."""
        return ExecutiveStateRevision(value=self.value + 1)
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ExecutiveContextId:
    """
    Unique identifier for an Executive Context instance.
    
    Context IDs identify specific context snapshots, which are immutable.
    """
    
    value: str = field(default_factory=lambda: f"exec_context_{hashlib.sha256(b'initial').hexdigest()[:16]}")
    
    @classmethod
    def generate(cls) -> ExecutiveContextId:
        """Generate a new unique context ID."""
        import uuid
        return cls(value=f"exec_context_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ExecutiveContextRevision:
    """
    Revision identifier for an Executive Context.
    
    Context revisions track the version of external projections included
    in a context snapshot.
    """
    
    value: int = 1
    
    def next(self) -> ExecutiveContextRevision:
        """Return the next revision number."""
        return ExecutiveContextRevision(value=self.value + 1)
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ExecutiveStateSchemaVersion:
    """
    Schema version for Executive State.
    
    Used to track schema evolution and ensure compatibility.
    """
    
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    @property
    def value(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class ExecutiveContextSchemaVersion:
    """
    Schema version for Executive Context.
    
    Used to track schema evolution and ensure compatibility.
    """
    
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    @property
    def value(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


# =============================================================================
# STATE IDENTITY COMPARISON TYPES
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStateIdentityMatch:
    """
    Result of comparing two state identities.
    
    Used to validate that transitions are applied to the correct state.
    """
    
    matches: bool
    """Whether the IDs match."""
    
    expected_id: str
    """The ID that was expected."""
    
    actual_id: str
    """The ID found in the state."""
    
    @classmethod
    def match(cls, expected: ExecutiveStateId, actual: ExecutiveStateId) -> ExecutiveStateIdentityMatch:
        """Create a match result for matching IDs."""
        return cls(
            matches=True,
            expected_id=expected.value,
            actual_id=actual.value,
        )
    
    @classmethod
    def mismatch(cls, expected: ExecutiveStateId, actual: ExecutiveStateId) -> ExecutiveStateIdentityMatch:
        """Create a mismatch result for non-matching IDs."""
        return cls(
            matches=False,
            expected_id=expected.value,
            actual_id=actual.value,
        )


@dataclass(frozen=True)
class ExecutiveContextIdentityMatch:
    """
    Result of comparing two context identities.
    
    Used to validate that context references are correct.
    """
    
    matches: bool
    expected_id: str
    actual_id: str
    
    @classmethod
    def match(cls, expected: ExecutiveContextId, actual: ExecutiveContextId) -> ExecutiveContextIdentityMatch:
        return cls(matches=True, expected_id=expected.value, actual_id=actual.value)
    
    @classmethod
    def mismatch(cls, expected: ExecutiveContextId, actual: ExecutiveContextId) -> ExecutiveContextIdentityMatch:
        return cls(matches=False, expected_id=expected.value, actual_id=actual.value)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveStateId",
    "ExecutiveStateRevision",
    "ExecutiveContextId",
    "ExecutiveContextRevision",
    "ExecutiveStateSchemaVersion",
    "ExecutiveContextSchemaVersion",
    "ExecutiveStateIdentityMatch",
    "ExecutiveContextIdentityMatch",
)