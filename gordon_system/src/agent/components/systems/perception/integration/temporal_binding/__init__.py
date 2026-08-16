# Temporal Binding - Phase 5.2.3
# ===============================

"""
Temporal Binding: Organizes perceptual artifacts into coherent time-local structures.

Temporal Binding answers:
    Which artifacts belong to the same perceptual episode, interval or event window?
"""

from gordon_system.src.agent.components.systems.perception.integration.temporal_binding.request import TemporalBindingRequest
from gordon_system.src.agent.components.systems.perception.integration.temporal_binding.result import TemporalBindingResult
from gordon_system.src.agent.components.systems.perception.integration.temporal_binding.binding import (
    TemporalBinding,
    BindingWindow,
)

__all__ = [
    "TemporalBindingRequest",
    "TemporalBindingResult",
    "TemporalBinding",
    "BindingWindow",
]