# Semantic Execution Streams Package (Phase 3.10.8)
# ====================================================

"""
Semantic execution streams represent ordered semantic information flow.

Streams answer: What ordered semantic information flow exists between 
producers, consumers, and architectural owners over time?

Canonical stream domains:

    Perception
        Ordered perceptual artifacts

    Cognition  
        Ordered cognitive proposals, results, revisions, and conflicts

    Consciousness
        Ordered conscious-context artifacts and transitions

    Memory
        Ordered memory presentations, proposals, and memory-owned commits

    Action
        Ordered action proposals, authorization references,
        execution outcomes, and effect feedback

Streams provide semantic continuity orthogonal to:

    Thread → Loop → Cycle

Therefore Gordon possesses two complementary execution axes:

    STRUCTURAL EXECUTION AXIS
    
        Thread
            ↓
        Loop
            ↓  
        Cycle
            ↓
        Stage
            ↓
        Capability / Network / System activity

and:

    SEMANTIC INFORMATION-FLOW AXIS

        Perception Stream
        Cognition Stream
        Consciousness Stream
        Memory Stream
        Action Stream
        ...

A Cycle may consume records from several Streams.
A Cycle may produce artifacts committed to several Streams.
A Thread may span many Stream records.
A Stream may contain records produced by many Threads or Cycles.

Therefore:

    Thread identity ≠ Stream identity
    Cycle ordering ≠ Stream ordering  
    Execution lifetime ≠ Stream lifetime

Core Streams owns generic stream machinery (identity, ordering,
transport, checkpointing, replay, etc.).
Semantic Execution Streams own domain definitions and contracts.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .perception import PerceptionStream
    from .cognition import CognitionStream
    from .consciousness import ConsciousnessStream
    from .memory import MemoryStream
    from .action import ActionStream

__all__ = [
    "PerceptionStream",
    "CognitionStream", 
    "ConsciousnessStream",
    "MemoryStream",
    "ActionStream",
]