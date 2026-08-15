# Contracts Module Package
# =======================

"""
Contracts package for internal episode coordination boundaries.

Provides immutable request and result models for capability invocation.
"""

from __future__ import annotations

from .capability import (
    InternalCapabilityRequest,
    InternalCapabilityRequestId,
    InternalCapabilityResult,
    InternalCapabilityResultId,
)

__all__ = [
    "InternalCapabilityRequest",
    "InternalCapabilityRequestId",
    "InternalCapabilityResult",
    "InternalCapabilityResultId",
]