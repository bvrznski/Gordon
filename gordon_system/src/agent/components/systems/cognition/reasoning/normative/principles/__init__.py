# Normative Principles Module
# ============================

"""
Principle application and management module for normative reasoning.

This module provides:
    - Principle identification and categorization
    - Principle precedence and ordering
    - Principle conflict detection
    - Context-sensitive principle application
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import time
import uuid


@dataclass(frozen=True)
class PrincipleApplication:
    """Application of a principle to a specific context."""
    
    application_id: str = field(default_factory=lambda: f"principle_application:{uuid.uuid4().hex[:16]}")
    principle_name: str
    applicable_contexts: Tuple[str, ...] = ()
    precedence: int = 0
    exceptions: Tuple[str, ...] = ()
    confidence: float = 0.0
    
    @classmethod
    def create(cls, principle_name: str, precedence: int = 1,
               applicable_contexts: Optional[List[str]] = None,
               exceptions: Optional[List[str]] = None,
               confidence: float = 0.5) -> "PrincipleApplication":
        return cls(
            principle_name=principle_name,
            precedence=precedence,
            applicable_contexts=tuple(applicable_contexts or []),
            exceptions=tuple(exceptions or []),
            confidence=confidence
        )


__all__ = ["PrincipleApplication"]