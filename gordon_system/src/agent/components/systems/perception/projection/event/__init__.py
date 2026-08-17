# Perception Projection - Event Module
# ======================================

"""
Event Projection: Exposes observed state transitions.

An Event Projection exposes observed state transitions. It may include Event
identity, kind, participants, temporal order, spatial relations, source Modalities,
supporting evidence, missing intervals, conflicts, alternative Event structures,
confidence, uncertainty.

An Event Projection shall not silently encode causality.
"""

from .projection import (
    EventProjection,
    EventSequenceProjection,
)

__all__ = [
    "EventProjection",
    "EventSequenceProjection",
]