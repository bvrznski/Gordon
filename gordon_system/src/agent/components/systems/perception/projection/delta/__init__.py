# Perception Projection - Delta Module
# ====================================

"""
Delta Projection: Communicates changes relative to a prior projection.

An Incremental Projection communicates changes relative to a prior projection.
Deltas preserve revision continuity and provide efficient incremental updates.
"""

from .delta import (
    PerceptionProjectionDelta,
)

__all__ = ["PerceptionProjectionDelta"]