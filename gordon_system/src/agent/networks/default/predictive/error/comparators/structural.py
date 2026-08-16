# Structural Comparator - Phase 4.9.3
# =====================================
"""
Tree/graph comparison implementation.
"""

from __future__ import annotations

from typing import Any, Set, Dict

from gordon_system.src.agent.networks.default.predictive.error.comparators.base import (
    Comparator,
    Residual,
)


class StructuralComparator(Comparator):
    """Compare structural values (trees, graphs) for mismatch detection."""

    @property
    def name(self) -> str:
        return "structural"

    @property
    def supported_representations(self) -> tuple[str, ...]:
        return ("structure", "tree", "graph")

    def is_compatible(
        self,
        expected_repr: str | None,
        observed_repr: str | None,
    ) -> bool:
        supported = set(self.supported_representations)
