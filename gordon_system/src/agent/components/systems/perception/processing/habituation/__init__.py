# Perception Habituation - Phase 5.2.2
# ====================================

"""
Habituation: Reduces processing emphasis for repetitive, stable evidence.

Habituation prevents perceptual overload by reducing repeated processing
for persistent background signals while preserving novelty detection.
"""

from __future__ import annotations

from .assessment import HabituationAssessment, HabituationLevel
from .repetition import PerceptualRepetitionPattern
from .novelty import PerceptualNoveltyAssessment

__all__ = [
    "HabituationAssessment",
    "HabituationLevel",
    "PerceptualRepetitionPattern",
    "PerceptualNoveltyAssessment",
]