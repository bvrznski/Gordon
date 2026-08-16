# Perception Translation - Phase 5.2.2
# ====================================

"""
Translation: Converts modality-specific representations into canonical forms.

Translation enables common downstream contracts by converting different source
representations into shared canonical perceptual fields.
"""

from __future__ import annotations

from .translation import PerceptualTranslation

__all__ = [
    "PerceptualTranslation",
]