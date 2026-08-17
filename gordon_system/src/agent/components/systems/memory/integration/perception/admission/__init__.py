# Memory-Perception Integration - Admission Module
# ================================================

"""
Admission Module: Prepares observations for Memory admission.

Observation Admission transforms perceptual evidence into candidate Memory
submissions. Admission does not decide:

* persistence
* retention  
* consolidation
* forgetting

Those remain Memory responsibilities. Integration merely prepares candidate evidence.
"""

from __future__ import annotations

# Admission-specific types will be imported from their respective modules
from gordon_system.src.agent.components.systems.memory.integration.perception.admission.candidate import (
    ObservationMemoryCandidate,
)

__all__ = [
    "ObservationMemoryCandidate",
]