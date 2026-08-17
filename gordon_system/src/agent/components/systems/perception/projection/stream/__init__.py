# Perception Projection - Stream Module
# =====================================

"""
Stream Projection: Publishes a sequence of perceptual updates.

A Stream Projection publishes a sequence of perceptual updates. Streams expose
dropped, delayed or reordered updates and provide gap detection capabilities.
"""

from .stream import (
    PerceptionProjectionStream,
)

__all__ = ["PerceptionProjectionStream"]