# Execution Package Tree Documentation (Phase 3.10.8)
# =====================================================

"""
Canonical execution package structure.

Execution is organized into four primary semantic categories:

    THREADS
        Long-lived semantic activity ownership
        
    LOOPS  
        Continuation and repetition policy ownership
        
    CYCLES
        Finite semantic progression ownership
        
    STREAMS
        Ordered semantic information flow ownership

Each category may contain multiple concrete implementations as subpackages.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class ExecutionCategory:
    """A top-level execution category."""
    name: str
    description: str
    implementations: List[str]


EXECUTION_CATEGORIES = [
    ExecutionCategory(
        name="threads",
        description="Long-lived semantic activity ownership. Threads own persistent identity, purpose, objectives, and completion intent.",
        implementations=[
            "conversation",  # Conversation threads
            "task",          # Task threads  
            "monitoring",    # Monitoring threads
            "internal",      # Internal threads
        ],
    ),
    ExecutionCategory(
        name="loops",
        description="Continuation and repetition policy ownership. Loops own next-Cycle selection, continuation conditions, and repetition policies.",
        implementations=[
            "conversation",  # Conversation loop policy
            "task",          # Task loop policy
            "planning",      # Planning loop policy  
            "monitoring",    # Monitoring loop policy
            "recovery",      # Recovery loop policy
            "idle",          # Idle loop policy
        ],
    ),
    ExecutionCategory(
        name="cycles",
        description="Finite semantic progression ownership. Cycles own one complete finite semantic pass with stages and terminal outcomes.",
        implementations=[
            "interpretation",  # Interpretation cycles (Conversation)
            "response",        # Response cycles (Conversation)  
            "planning",        # Planning cycles (Task)
            "execution",       # Execution cycles (Task)
            "evaluation",      # Evaluation cycles (Task)
            "observation",     # Observation cycles (Monitoring)
            "reflection",      # Reflection cycles (Internal)
        ],
    ),
    ExecutionCategory(
        name="streams",
        description="Ordered semantic information flow ownership. Streams own the ordered flow of semantic artifacts between producers and consumers.",
        implementations=[
            "perception",    # Ordered perceptual artifacts
            "cognition",     # Ordered cognitive proposals, results, revisions, conflicts
            "consciousness", # Ordered conscious-context artifacts and transitions
            "memory",        # Ordered memory presentations, proposals, commits
            "action",        # Ordered action proposals, outcomes, effect feedback
        ],
    ),
]

__all__ = [
    "EXECUTION_CATEGORIES",
    "ExecutionCategory",
]