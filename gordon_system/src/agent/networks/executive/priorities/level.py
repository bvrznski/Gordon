# Executive Priority Level
# =========================

"""
Executive Priority Level - Typed priority levels for executive ordering.

Priority levels indicate the relative claim on limited executive control.
"""

from __future__ import annotations


class ExecutivePriorityLevel:
    """
    Typed priority levels.
    
    These represent semantic categories, not numeric scores that can be arbitrarily added.
    
    Level semantics:
        DORMANT: Not currently under consideration
        BACKGROUND: Low-priority background items
        LOW: Minimal executive attention needed
        NORMAL: Standard priority for regular goals/commitments
        ELEVATED: Requires more attention than normal
        HIGH: Significant claim on executive resources
        CRITICAL: High-value item requiring immediate attention
        BLOCKING: Prevents progress (not necessarily highest value)
        MANDATORY_REVIEW: Review required before continuation
    """
    
    DORMANT = "dormant"
    """Not currently under consideration."""
    
    BACKGROUND = "background"
    """Low-priority background items."""
    
    LOW = "low"
    """Minimal executive attention needed."""
    
    NORMAL = "normal"
    """Standard priority for regular goals/commitments."""
    
    ELEVATED = "elevated"
    """Requires more attention than normal."""
    
    HIGH = "high"
    """Significant claim on executive resources."""
    
    CRITICAL = "critical"
    """High-value item requiring immediate attention."""
    
    BLOCKING = "blocking"
    """Prevents progress (not necessarily highest value)."""
    
    MANDATORY_REVIEW = "mandatory_review"
    """Review required before continuation."""