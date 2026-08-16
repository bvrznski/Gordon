# Executive Conflict Status Types
# ===============================

"""
Types for representing the lifecycle state of executive conflicts.

Status is semantic, not a runtime job status. It tracks whether a conflict
is detected, validated, resolved, etc.
"""

from __future__ import annotations

from typing import Tuple


class ExecutiveConflictStatus:
    """
    Lifecycle statuses for executive conflicts.
    """
    
    DETECTED = "detected"
    VALIDATING = "validating"
    CONFIRMED = "confirmed"
    PARTIALLY_CONFIRMED = "partially_confirmed"
    DISPUTED = "disputed"
    UNRESOLVED = "unresolved"
    UNDER_REVIEW = "under_review"
    WAITING_FOR_EVIDENCE = "waiting_for_evidence"
    WAITING_FOR_AUTHORITY = "waiting_for_authority"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    SUPERSEDED = "superseded"
    DISMISSED = "dismissed"
    EXPIRED = "expired"
    INVALID = "invalid"
    UNKNOWN = "unknown"

    @classmethod
    def all_statuses(cls) -> Tuple[str, ...]:
        return tuple(v for k, v in vars(cls).items() if not k.startswith('_') and isinstance(v, str))


__all__: Tuple[str, ...] = ("ExecutiveConflictStatus",)