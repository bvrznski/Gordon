# Salience Network Landscape Module
# ==================================

"""
Canonical Global Salience Landscape implementation (Phase 4.8.8).

This module provides immutable, semantic construction of global salience landscapes.

ARCHITECTURAL INVARIANTS:
    - L-INV-001: Landscape is purely semantic (no runtime behavior)
    - L-INV-002: All outputs are immutable frozen dataclasses
    - L-INV-003: Deterministic for equivalent inputs
    - L-INV-004: No Attention allocation responsibility

ARCHITECTURAL OWNERSHIP:
    The Landscape owns:
        - Global activation estimation
        - Baseline salience reference
        - Resource pressure estimates
        - Cognitive load estimates  
        - Environmental load estimates
        - Novelty, conflict, uncertainty, urgency density estimations
        - Contextual gradients
        - Salience hotspots
        - System coherence
        - System readiness
        
    The Landscape does NOT own:
        - Attention allocation (owned by Attention Network)
        - Executive switching
        - Working Memory admission
        - Runtime scheduling

ARCHITECTURAL FLOW:
    Candidate Evaluation -> Competition -> Dynamics -> Landscape -> Attention
    
    The Landscape answers: "What is the overall salience state of cognition?"
    
    It does NOT answer: "Which Candidate receives Attention?" (that's Phase 4.9)
"""

from __future__ import annotations

# =============================================================================
# PHASE 4.8.8 PARTS
# =============================================================================

from ._request import (
    LandscapePolicy,
    ContextProjection,
    LandscapeRequest,
)

from ._state import (
    GlobalActivation,
    BaselineSalience,
    ResourcePressure,
    CognitiveLoad,
    EnvironmentalLoad,
    NoveltyDensity,
    ConflictDensity,
    UncertaintyDensity,
    UrgencyDensity,
    ContextualGradient,
    SalienceHotspot,
    SystemCoherence,
    SystemReadiness,
    LandscapeState,
)

from ._builder import (
    LandscapeBuilder,
)

__all__ = [
    # Request types
    "LandscapePolicy",
    "ContextProjection", 
    "LandscapeRequest",
    
    # State types (result components)
    "GlobalActivation",
    "BaselineSalience",
    "ResourcePressure",
    "CognitiveLoad",
    "EnvironmentalLoad",
    "NoveltyDensity",
    "ConflictDensity",
    "UncertaintyDensity",
    "UrgencyDensity",
    "ContextualGradient",
    "SalienceHotspot",
    "SystemCoherence",
    "SystemReadiness",
    "LandscapeState",
    
    # Builder
    "LandscapeBuilder",
]

# =============================================================================
# CANONICAL METADATA (Phase 4.8.8)
# =============================================================================

__version__ = "1.0.0"
PACKAGE_NAME = "gordon.networks.salience.landscape"
DISPLAY_NAME = "Global Salience Landscape"
ARCHITECTURAL_LAYER = "salience_network"
PACKAGE_STATUS = "stable"
IMPLEMENTATION_PHASE = "4.8.8"
CANONICAL = True