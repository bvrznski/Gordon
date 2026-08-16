# Comparator Base Interface - Phase 4.9.3
# =========================================
"""
Base interface for all comparators in the Prediction Error Processing Engine.

PHASE BOUNDARY:
    Pure semantic infrastructure with NO runtime dependencies.
    
COMPARATOR LAWS (PER SPEC):
    * COMPARATOR-LAW-001: Each comparator owns exactly one semantic comparison domain
    * COMPARATOR-LAW-002: Comparators shall be pure
    * COMPARATOR-LAW-003: Comparators shall be deterministic
    * COMPARATOR-LAW-004: Comparators shall be stateless
    * COMPARATOR-LAW-005: Comparators shall return Residuals only
    * COMPARATOR-LAW-006: Comparators shall never construct PredictionError directly
    * COMPARATOR-LAW-007: Comparators shall never construct PredictionErrorState
    * COMPARATOR-LAW-008: Comparators shall never invoke other comparators
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


# =============================================================================
# RESIDUAL (COMPARISON OUTPUT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Residual:
    """
    Immutable residual representing comparison result.
    
    Fields:
        expected:           The expected value/state
        observed:           The observed value/state  
        difference:         Numeric or semantic difference measure
        representation:     How the values are represented (ValueKind)
        metric:             Comparison metric used (e.g., "cosine", "euclidean")
        confidence:         Confidence in residual accuracy
        uncertainty:        Uncertainty decomposition
        provenance:         Trace of comparison process
        
    Rules:
        * Residuals are immutable
        * No interpretation encoded
        * Preserves both expected and observed representations
    """
    expected: Any | None = None
    observed: Any | None = None
    difference: float | str | None = None
    representation: str | None = None  # ValueKind enum value
    metric: str | None = None  # LatentMetric or comparison type
    confidence: float | None = None
    uncertainty: float | None = None
    provenance: tuple[str, ...] = ()  # TraceCode codes


# =============================================================================
# COMPARATOR INTERFACE (ABSTRACT BASE CLASS)
# =============================================================================

class Comparator(ABC):
    """
    Abstract base class for all comparators.
    
    Every comparator implements the same interface:
        compare(expected, observed, policy) -> Residual
    
    Rules:
        * Comparators are pure functions
        * Comparators are stateless (no internal state between calls)
        * Comparators are deterministic (same inputs = same outputs)
        * Comparators return only Residual objects
    """

    @abstractmethod
    def compare(
        self,
        expected: Any,
        observed: Any,
        policy: dict[str, Any] | None = None,
    ) -> Residual:
        """
        Compare expected value against observed value.
        
        Args:
            expected:   Expected value/state to compare against
            observed:   Observed value/state to compare with
            policy:     Optional comparison policy configuration
            
        Returns:
            Residual:   Immutable mismatch representation
            
        Raises:
            TypeError:  If schema validation fails
            ValueError: If comparison cannot be performed
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the comparator's unique identifier."""
        raise NotImplementedError

    @property
    @abstractmethod
    def supported_representations(self) -> tuple[str, ...]:
        """Return tuple of supported ValueKind representations."""
        raise NotImplementedError

    @property
    @abstractmethod
    def is_compatible(
        self,
        expected_repr: str | None,
        observed_repr: str | None,
    ) -> bool:
        """
        Check if this comparator can handle the given value representations.
        
        Args:
            expected_repr: Expected value representation (ValueKind or similar)
            observed_repr: Observed value representation (ValueKind or similar)
            
        Returns:
            True if compatible, False otherwise
        """
        raise NotImplementedError


# =============================================================================
# COMPARATOR REGISTRY ENTRY
# =============================================================================

@dataclass(frozen=True, slots=True)
class ComparatorEntry:
    """
    Registry entry mapping key to comparator instance.
    
    Fields:
        key:                Unique identifier (e.g., "scalar:value")
        comparator:         Comparator instance to invoke
        priority:           Comparison priority (higher = first)
        
    Rules:
        * Entries are immutable after construction
        * No duplicate keys permitted
    """
    key: str
    comparator: Comparator
    priority: int = 0