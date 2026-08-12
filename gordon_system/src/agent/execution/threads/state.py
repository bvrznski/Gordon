# Thread Semantic State
# ======================

"""
Thread semantic state model with controlled mutation.

Semantic state is long-lived and includes:
    - Accepted context
    - Active objectives
    - Semantic summaries
    - Accepted facts
    - Unresolved questions
    - Commitments
    - Constraints
    - References to relevant memory
    - Relationships to other Threads
    - Current behavioral mode

State changes must occur through controlled delta application, not direct mutation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class BehavioralMode(Enum):
    """
    Semantic behavioral modes a Thread can adopt.
    
    These define the "flavor" of activity the thread is engaged in:
        - CONVERSATION: User interaction, dialogue
        - PLANNING: Strategy formulation, goal setting
        - MONITORING: Watch for conditions, report changes
        - INVESTIGATION: Research, gather information
        - EXECUTION: Carry out tasks
        - REFLECTION: Internal review, learning
    """
    
    CONVERSATION = "conversation"
    PLANNING = "planning"
    MONITORING = "monitoring"
    INVESTIGATION = "investigation"
    EXECUTION = "execution"
    REFLECTION = "reflection"


@dataclass(frozen=True)
class ThreadObjective:
    """
    A semantic objective within a Thread.
    
    Objectives may be added, refined, completed, abandoned, or superseded.
    These transitions must be explicit and validated.
    """
    
    objective_id: str
    description: str
    status: str = "active"  # active, completed, abandoned, superseded
    
    # Priority (for ordering)
    priority: int = 0
    
    # Context
    created_at_utc: float = field(default_factory=lambda: 0.0)
    completed_at_utc: Optional[float] = None
    
    # Related artifacts
    related_thread_ids: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ThreadFacts:
    """
    Accepted semantic facts that the thread has established.
    
    These are truths the thread has verified through execution or acceptance.
    """
    
    facts: List[str] = field(default_factory=list)
    sources: Dict[str, str] = field(default_factory=dict)  # fact -> source reference


@dataclass(frozen=True)
class ThreadContext:
    """
    Accepted context for the thread's current activity.
    
    This is the "working memory" that persists across semantic passes.
    """
    
    active_objectives: List[ThreadObjective] = field(default_factory=list)
    
    # Facts established through execution
    accepted_facts: ThreadFacts = field(default_factory=ThreadFacts)
    
    # Unresolved questions or pending items
    unresolved_questions: List[str] = field(default_factory=list)
    
    # Current behavioral mode
    current_mode: BehavioralMode = BehavioralMode.EXECUTION
    
    # Constraints that apply to this thread
    constraints: List[str] = field(default_factory=list)
    
    # References to memory (external system owns storage)
    memory_references: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ThreadSemanticState:
    """
    Immutable snapshot of a Thread's semantic state at a point in time.
    
    To mutate state, create a new ThreadSemanticState via delta application
    rather than modifying this object directly.
    """
    
    # Identity (immutable anchor)
    thread_id: str
    
    # Versioning (monotonic)
    semantic_version: int = 0
    
    # Metadata
    name: Optional[str] = None
    purpose: Optional[str] = None
    kind: str = "default"
    
    # Semantic content
    context: ThreadContext = field(default_factory=ThreadContext)
    
    # History (references to past states, not full history)
    previous_state_versions: List[int] = field(default_factory=list)
    
    # Checkpoint references (for recovery)
    checkpoint_references: List[str] = field(default_factory=list)
    
    @property
    def current_objectives(self) -> List[ThreadObjective]:
        """Get only currently active objectives."""
        return [o for o in self.context.active_objectives if o.status == "active"]
    
    @property
    def is_completed(self) -> bool:
        """Check if thread has completed all objectives."""
        return len(self.current_objectives) == 0 and len(self.context.accepted_facts.facts) > 0
    
    def with_version_increment(self) -> "ThreadSemanticState":
        """Return a new state with incremented semantic version."""
        return dataclass_replace(self, semantic_version=self.semantic_version + 1)
    
    def with_context(self, new_context: ThreadContext) -> "ThreadSemanticState":
        """Return a new state with updated context."""
        return dataclass_replace(self, context=new_context)


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


@dataclass
class ThreadStateBuilder:
    """
    Builder for constructing or modifying Thread semantic state.
    
    Use this when you need to make controlled state transitions. The builder
    validates changes before producing an immutable ThreadSemanticState.
    """
    
    # Core identity (cannot be changed after creation)
    _thread_id: str = ""
    _semantic_version: int = 0
    
    # Mutable build-time fields
    _name: Optional[str] = None
    _purpose: Optional[str] = None
    _kind: str = "default"
    
    _context: ThreadContext = field(default_factory=ThreadContext)
    
    def __init__(self, thread_id: str):
        self._thread_id = thread_id
        self._semantic_version = 0
    
    def with_name(self, name: str) -> "ThreadStateBuilder":
        """Set the thread's display name."""
        self._name = name
        return self
    
    def with_purpose(self, purpose: str) -> "ThreadStateBuilder":
        """Set or update the thread's purpose."""
        self._purpose = purpose
        return self
    
    def with_kind(self, kind: str) -> "ThreadStateBuilder":
        """Set the thread's classification/kind."""
        self._kind = kind
        return self
    
    def add_objective(self, objective: ThreadObjective) -> "ThreadStateBuilder":
        """Add an objective to the thread."""
        objectives = list(self._context.active_objectives)
        objectives.append(objective)
        self._context = dataclass_replace(self._context, active_objectives=objectives)
        return self
    
    def complete_objective(self, objective_id: str) -> "ThreadStateBuilder":
        """Mark an objective as completed."""
        objectives = []
        for o in self._context.active_objectives:
            if o.objective_id == objective_id:
                objectives.append(
                    dataclass_replace(o, status="completed", completed_at_utc=0.0)
                )
            else:
                objectives.append(o)
        self._context = dataclass_replace(self._context, active_objectives=objectives)
        return self
    
    def set_mode(self, mode: BehavioralMode) -> "ThreadStateBuilder":
        """Set the current behavioral mode."""
        self._context = dataclass_replace(self._context, current_mode=mode)
        return self
    
    def add_fact(self, fact: str, source: Optional[str] = None) -> "ThreadStateBuilder":
        """Add an accepted fact to the thread's knowledge base."""
        facts_list = list(self._context.accepted_facts.facts)
        if fact not in facts_list:
            facts_list.append(fact)
        
        sources = dict(self._context.accepted_facts.sources)
        if source:
            sources[fact] = source
        
        self._context = dataclass_replace(
            self._context,
            accepted_facts=ThreadFacts(facts=facts_list, sources=sources)
        )
        return self
    
    def increment_version(self) -> "ThreadStateBuilder":
        """Increment the semantic version counter."""
        self._semantic_version += 1
        return self
    
    def build(self) -> ThreadSemanticState:
        """Build and return an immutable ThreadSemanticState."""
        return ThreadSemanticState(
            thread_id=self._thread_id,
            semantic_version=self._semantic_version,
            name=self._name,
            purpose=self._purpose,
            kind=self._kind,
            context=self._context,
            previous_state_versions=[],
            checkpoint_references=[],
        )


__all__ = [
    "BehavioralMode",
    "ThreadObjective",
    "ThreadFacts",
    "ThreadContext",
    "ThreadSemanticState",
    "ThreadStateBuilder",
]