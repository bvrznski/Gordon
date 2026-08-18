# Root-Cause Analysis Module - Phase 7.39
# =======================================

"""
Root-Cause Analysis for Diagnostic Reasoning.

This module provides:
    - Causal chain analysis
    - Root cause identification
    - Alternative explanation generation
    - Confidence estimation
"""

from agent.components.systems.cognition.reasoning.diagnostic.root_causes.model import (
    RootCauseModel,
    CausalChain,
)

__all__ = [
    "RootCauseModel",
    "CausalChain",
]