# Scalar Comparator - Phase 4.9.3
# ================================
"""
Scalar value comparison implementation.

LAW COMPLIANCE:
    * COMPARATOR-LAW-001: Scalar comparison domain only
    * COMPARATOR-LAW-002: Pure function (no side effects)
    * COMPARATOR-LAW-003: Deterministic outputs
    * COMPARATOR-LAW-004: Stateless (no internal state between calls)
    * COMPARATOR-LAW-005: Returns only Residual
    * COMPARATOR-LAW-006-008: No PredictionError/PredictionErrorState construction
"""

from __future__ import annotations

from typing import Any

from gordon_system.src.agent.networks.default.predictive.error.comparators.base import (
    Comparator,
    Residual,
)


class ScalarComparator(Comparator):
    """
    Compare scalar values (numeric, boolean) for mismatch detection.
    
    Computes:
        - semantic delta
        - normalized difference  
        - tolerance checking
        
    NO interpretation. No belief revision.
    """

    @property
    def name(self) -> str:
        return "scalar"

    @property
    def supported_representations(self) -> tuple[str, ...]:
        return ("scalar", "numeric", "boolean")

    def is_compatible(
        self,
        expected_repr: str | None,
        observed_repr: str | None,
    ) -> bool:
        """Check if both values are scalar representations."""
        supported = set(self.supported_representations)
        expected_is_scalar = expected_repr in supported if expected_repr else False
        observed_is_scalar = observed_repr in supported if observed_repr else False
        return expected_is_scalar and observed_is_scalar

    def compare(
        self,
        expected: Any,
        observed: Any,
        policy: dict[str, Any] | None = None,
    ) -> Residual:
        """
        Compare two scalar values.
        
        Algorithm:
            validate scalar schema
            ↓
            validate units (if applicable)
            ↓
            compute semantic delta
            ↓
            normalize if required  
            ↓
            apply tolerance policy
            ↓
            construct ScalarResidual
            
        Complexity: O(1)
        """
        # Handle unknown values explicitly
        if expected is None and observed is None:
            return Residual(
                expected=None,
                observed=None,
                difference=0.0,
                representation="scalar",
                confidence=1.0,
                uncertainty=0.0,
            )

        # Handle mismatched nullity
        if (expected is None) != (observed is None):
            max_val = 1.0
            diff = abs(float(expected)) if expected is not None else abs(float(observed))
            normalized_diff = min(1.0, diff / max_val) if max_val > 0 else 1.0
            return Residual(
                expected=expected,
                observed=observed,
                difference=normalized_diff,
                representation="scalar",
                confidence=0.5,
                uncertainty=0.5,
            )

        # Both are non-None: compute difference
        try:
            # Try numeric comparison first
            if isinstance(expected, (int, float)) and isinstance(observed, (int, float)):
                diff = float(expected) - float(observed)
                
                # Get tolerance from policy (default 0.0 for strict comparison)
                tolerance = policy.get("tolerance", 0.0) if policy else 0.0
                
                # Normalize difference to [0, 1] range
                max_abs = max(abs(expected), abs(observed), 1.0)
                normalized_diff = abs(diff) / max_abs if max_abs > 0 else 0.0
                
                return Residual(
                    expected=expected,
                    observed=observed,
                    difference=normalized_diff,
                    representation="scalar",
                    confidence=1.0 if normalized_diff <= tolerance else 0.5,
                    uncertainty=0.0 if normalized_diff <= tolerance else 0.5,
                )

            # Fallback: boolean or other scalar comparison
            diff = 0.0 if expected == observed else 1.0
            return Residual(
                expected=expected,
                observed=observed,
                difference=diff,
                representation="scalar",
                confidence=1.0 if diff == 0.0 else 0.5,
                uncertainty=0.0 if diff == 0.0 else 0.5,
            )

        except (TypeError, ValueError):
            # Cannot compare - return unknown
            return Residual(
                expected=expected,
                observed=observed,
                difference=None,
                representation="scalar",
                confidence=0.0,
                uncertainty=1.0,
            )