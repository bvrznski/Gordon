# Abduction Shared Module - Phase 7.3
# ====================================

"""
Shared types and utilities for abductive reasoning.

This module provides:
    - Common data structures used across all abductive modules
"""

from agent.components.systems.cognition.reasoning.abductive.shared.descriptor import (
    AbductionDescriptor,
    AbductionSessionIdentity,
    AbductionMode,
    AbductionLifecycle,
)

__all__ = [
    "AbductionDescriptor",
    "AbductionSessionIdentity",
    "AbductionMode",
    "AbductionLifecycle",
]