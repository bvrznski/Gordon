# Categorical Comparator - Phase 4.9.3
# ======================================
"""
Categorical classification comparison implementation.
"""

from __future__ import annotations

from typing import Any

from gordon_system.src.agent.networks.default.predictive.error.comparators.base import (
    Comparator,
    Residual,
)


class CategoricalComparator(Comparator):
    """Compare categorical values for mismatch detection."""

    @property
    def name(self) -> str:
        return "categorical"

    @property
    def supported_representations(self) -> tuple[str, ...]:
        return ("category", "classification", "label")

    def is_compatible(
        self,
        expected_repr: str | None,
        observed_repr: str | None,
    ) -> bool:
        supported = set(self.supported_representations)
        if expected_repr is not None:
            expected_is_cat = expected_repr in supported
        else:
            expected_is_cat = False

        if observed_repr is not None:
            observed_is_cat = observed_repr in supported
        else:
            observed_is_cat = False

        return expected_is_cat and observed_is_cat

    def compare(
        self,
        expected: Any,
        observed: Any,
        policy: dict[str, Any] | None = None,
    ) -> Residual:
        """
        Compare two categorical values.
        
        Algorithm:
            validate ontology
            compare canonical category identity
            classify disagreement
            construct CategoryResidual
            
        Complexity: O(1)
        """
        if expected is None and observed is None:
            return Residual(
                expected=None,
                observed=None,
                difference=0.0,
                representation="category",
                confidence=1.0,
                uncertainty=0.0,
            )

        if (expected is None) != (observed is None):
            return Residual(
                expected=expected,
                observed=observed,
                difference=1.0,
                representation="category",
                confidence=0.5,
                uncertainty=0.5,
            )

        match = 1.0 if expected == observed else 0.0
        return Residual(
            expected=expected,
            observed=observed,
            difference=match,
            representation="category",
            confidence=1.0 if match == 1.0 else 0.5,
            uncertainty=0.0 if match == 1.0 else 0.5,
        )