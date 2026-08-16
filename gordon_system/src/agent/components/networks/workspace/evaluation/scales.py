# Evaluation Scales
# ================

"""
Canonical evaluation scale definitions.
"""

from __future__ import annotations

from enum import Enum


class WorkspaceEvaluationScaleKind(Enum):
    """
    Canonical scale kinds for evaluation dimensions.

    Scale kind determines interpretation of values and valid operations.
    """

    # =========================================================================
    # DISCRETE SCALES
    # =========================================================================

    BINARY = "binary"
    """Two-valued scale (true/false, yes/no)."""

    CATEGORICAL = "categorical"
    """Nominal categories without order."""

    # =========================================================================
    # ORDERED SCALES
    # =========================================================================

    ORDINAL = "ordinal"
    """Ordered categories with relative ranking."""

    INTERVAL = "interval"
    """Equal intervals between values, no true zero."""

    RATIO = "ratio"
    """True ratio scale with meaningful zero point."""

    # =========================================================================
    # PROBABILITY SCALES
    # =========================================================================

    PROBABILITY = "probability"
    """Probability values [0.0, 1.0]."""

    # =========================================================================
    # BOUNDED DECIMAL SCALES
    # =========================================================================

    BOUNDED_DECIMAL = "bounded_decimal"
    """Decimal within bounded range."""

    # =========================================================================
    # STRUCTURED VALUES
    # =========================================================================

    STRUCTURED = "structured"
    """Complex structured value (e.g., tuple, mapping)."""

    UNKNOWN = "unknown"
    """Unknown or unspecified scale kind."""


WorkspaceEvaluationScale = str
"""
Immutable reference to an evaluation scale definition.

Format: "scale_kind@revision"
Examples:
    "probability@1"
    "bounded_decimal_0_to_100@2"
"""