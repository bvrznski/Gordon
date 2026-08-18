# Normative Conflicts Module
# ===========================

"""
Conflict resolution module for normative reasoning.

This module provides:
    - Conflict identification between values, principles, and obligations
    - Resolution strategies
    - Confidence in conflict analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import time
import uuid


@dataclass(frozen=True)
class ConflictResolution:
    """Resolution of a normative conflict."""
    
    resolution_id: str = field(default_factory=lambda: f"conflict_resolution:{uuid.uuid4().hex[:16]}")
    conflict_id: str
    resolution_strategy: str = "precedence"  # precedence, balance, override, reject
    chosen_option: Optional[str] = None
    confidence: float = 0.0
    
    @classmethod
    def create(cls, conflict_id: str, strategy: str = "precedence",
               chosen_option: Optional[str] = None,
               confidence: float = 0.5) -> "ConflictResolution":
        return cls(conflict_id=conflict_id, resolution_strategy=strategy,
                   chosen_option=chosen_option, confidence=confidence)


__all__ = ["ConflictResolution"]