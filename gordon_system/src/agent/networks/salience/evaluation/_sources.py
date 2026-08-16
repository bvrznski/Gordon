# Salience Network Source Classification
# ======================================

"""
Canonical source classification for salience evaluation (Phase 4.8.5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SalienceSourceKind(Enum):
    """
    Canonical source classification for salience evaluation.
    
    Each kind represents a distinct origin of semantic information that
    contributes to salience assessment.
    """
    BOTTOM_UP = "bottom_up"
    """Signals arising from raw perceptual input properties (intensity, contrast)."""
    
    TOP_DOWN = "top_down"
    """Signals relative to active cognitive context (Goals, expectations)."""
    
    GOAL_DRIVEN = "goal_driven"
    """Signals related to active Goal relevance and completion."""
    
    CONTEXTUAL = "contextual"
    """Signals relative to current environmental or mission context."""
    
    MOTIVATIONAL = "motivational"
    """Signals from motivational drive and value projections."""
    
    EMOTIONAL = "emotional"
    """Signals from affective state (where applicable)."""
    
    MEMORY_DRIVEN = "memory_driven"
    """Signals from Memory retrieval and association."""
    
    SENSORY = "sensory"
    """Direct sensory observation signals."""
    
    EXECUTIVE = "executive"
    """Signals from Executive directives and criticality projections."""
    
    PREDICTIVE = "predictive"
    """Signals from predictive expectation and error."""
    
    TEMPORAL = "temporal"
    """Signals related to time, deadlines, and urgency windows."""
    
    SOCIAL = "social"
    """Signals from social cognition (where applicable)."""