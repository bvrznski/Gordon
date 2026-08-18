# Topology Module - Phase 7.38
# =============================

"""
Topology management for Systems Reasoning.

Topology management evaluates:
    - component organization
    - hierarchical structure
    - network connectivity
    - boundary definition
    - dependency topology
    - modularity
"""

from .manager import TopologyManager, TopologyAnalysis

__all__ = [
    "TopologyManager",
    "TopologyAnalysis",
]