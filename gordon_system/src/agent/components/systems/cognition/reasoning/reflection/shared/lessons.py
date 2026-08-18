# Lesson Extraction - Phase 7.28
# ==============================

"""
Lesson Extraction determines valuable lessons from completed cognition.

Lessons determine:
    - Successful practices
    - Avoidable mistakes
    - Reusable procedures
    - Unexpected discoveries
    - Recommended improvements
    - Future cautions

Lessons remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ExtractedLesson:
    """
    Extracted lesson from completed cognition.
    
    A lesson contains:
        - Explicit identity
        - Lesson type (success, mistake, improvement, etc.)
        - Supporting evidence
        - Applicability conditions
        - Provenance tracking
    
    Lessons remain independently inspectable.
    """
    
    # Identity
    lesson_id: str                            # Unique lesson identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Lesson classification
    lesson_type: str                          # Type: success, mistake, improvement, etc.
    lesson_category: str                      # Category: decision, execution, reasoning, strategy
    
    # Content
    lesson_statement: str                     # What was learned?
    rationale: Dict[str, Any]                 # Why is this a lesson?
    
    # Supporting evidence
    supporting_evidence: List[Dict[str, Any]] = field(default_factory=list)  # Evidence items
    source_sessions: List[str] = field(default_factory=list)                 # Source sessions
    
    # Applicability
    applicability_conditions: Dict[str, Any] = field(default_factory=dict)   # When to apply?
    recommended_actions: List[str] = field(default_factory=list)             # What to do?
    
    # Quality metrics
    evidence_count: int = 0                   # Number of supporting evidence items
    confidence_score: float = 0.0             # Confidence in lesson
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    origin_context: str = "unknown"           # Where extraction originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        lesson_type: str,
        lesson_statement: str,
        rationale: Dict[str, Any],
        supporting_evidence: Optional[List[Dict[str, Any]]] = None,
        source_sessions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> ExtractedLesson:
        """Create a new extracted lesson."""
        return cls(
            lesson_id=f"lesson:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            lesson_type=lesson_type,
            lesson_category="general",
            lesson_statement=lesson_statement,
            rationale=rationale,
            supporting_evidence=supporting_evidence or [],
            source_sessions=source_sessions or [],
            evidence_count=len(supporting_evidence or []),
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class LessonManagement:
    """
    Management of lesson extraction process.
    
    A management object contains:
        - Extraction identity and strategy
        - Current state
        - Extracted lessons
        - Quality metrics
        - Provenance tracking
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Configuration
    lesson_type_filter: List[str] = field(default_factory=list)  # Filter by type
    min_evidence_per_lesson: int = 1            # Minimum evidence per lesson
    max_lessons: int = 20                         # Maximum lessons to extract
    
    # Current state
    current_stage: str = "initializing"         # Extraction stage
    
    # Results (can be None if not yet completed)
    extracted_lessons: List[ExtractedLesson] = field(default_factory=list)   # Extracted lessons
    
    # Quality metrics
    lesson_quality_score: float = 0.0           # Overall quality score
    coverage_count: int = 0                     # Number of sessions covered
    
    # Compatibility
    compatibility_revision: int = 1             # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_sessions: List[str] = field(default_factory=list)   # Source sessions
    origin_context: str = "unknown"                             # Where extraction originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        source_sessions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> LessonManagement:
        """Create a new lesson management."""
        return cls(
            management_id=f"lesson_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            source_sessions=source_sessions or [],
            origin_context=origin_context,
        )


__all__ = [
    "ExtractedLesson",
    "LessonManagement",
]