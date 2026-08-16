# Salience Network Context State
# ==============================
#
# Canonical implementation of external context projections (Phase 4.8.4).
#

"""
Context state for external semantic references.

CONTEXT PRESERVES EXTERNAL OWNERSHIP:
    - Goal System owns Goals
    - Task system owns Tasks  
    - Memory owns Memory records
    - Salience State only contains references
    
CONTEXT CATEGORIES:
    - Mission: Current mission context
    - Goal: Referenced Goal
    - Objective: Referenced objective
    - Task: Referenced Task
    - Environmental: External environment state
    - Temporal: Time-based context
    - Motivational: Motivational context
    - Social: Social context
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SalienceContextEntry:
    """
    Canonical external context reference entry.
    
    Each entry preserves:
        - External subsystem authority
        - Reference to the external semantic object
        - Context role in salience assessment
        - Optional relevance descriptor
    
    CONTEXT INVARIANTS:
        - SALIENCE-CONTEXT-INV-001: External ownership preserved
        - SALIENCE-CONTEXT-INV-002: Authority is explicit
        - SALIENCE-CONTEXT-INV-003: No embedded implementation objects
    """
    
    reference_id: str = field(default="")
    """Id of the external semantic object."""
    
    subsystem: str = field(default="external")
    """Authoritative subsystem for this context."""
    
    role: str = field(default="contextual")
    """Semantic role in salience assessment."""
    
    relevance: str = field(default="unknown")
    """Optional relevance descriptor."""
    
    authority_id: str = field(default="")
    """Authority responsible for this context projection."""


@dataclass(frozen=True)
class SalienceContextState:
    """
    Canonical composition of external context projections.
    
    CONTEXT COMPOSITION:
        - entries: Tuple of context references
        - active_contexts: Set of contexts currently active
        - contextual_constraints: Semantic constraints from context
    
    CONTEXT LAWS:
        - SALIENCE-CONTEXT-LAW-001: No embedded implementation objects
        - SALIENCE-CONTEXT-LAW-002: Authority is explicit per entry
        - SALIENCE-CONTEXT-LAW-003: External ownership preserved
    """
    
    entries: Tuple[SalienceContextEntry, ...] = field(default_factory=tuple)
    """External context references."""
    
    active_contexts: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of contexts currently influencing salience assessment."""
    
    contextual_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic constraints from external context."""
    
    completeness: str = field(default="unknown")
    """Semantic assessment of context coverage."""