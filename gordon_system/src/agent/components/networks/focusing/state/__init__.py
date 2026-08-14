# Focusing Network State Module
# ==============================

"""
State models for the FocusingNetwork.

This module defines immutable state representations without computational
implementation. All state transitions must be explicit.
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class FocusTargetState:
    """
    Immutable state for a single focus target.

    Represents the current assessment of a target without any runtime behavior.
    """

    target_id: str
    """Unique identifier for this target."""

    priority_score: float = field(default=0.0)
    """Current priority score (0.0 to 1.0)."""

    modality: str = field(default="unknown")
    """Attention modality of this target."""

    source: str = field(default="unknown")
    """Origin of the focus candidate."""


@dataclass(frozen=True)
class FocusingNetworkState:
    """
    Immutable state for the entire FocusingNetwork.

    Represents a complete snapshot of network state at a point in time.
    All state transitions produce new snapshots - never modify existing ones.
    """

    focus_targets: Tuple[FocusTargetState, ...] = field(default_factory=tuple)
    """Current focus target assessments."""

    current_focus_strength: float = field(default=0.0)
    """Overall network focus strength (0.0 to 1.0)."""