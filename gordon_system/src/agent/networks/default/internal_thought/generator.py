# Thought Generator - Semantic Content Generation
# ================================================

"""
ThoughtGenerator for generating InternalThought instances from context.

The generator is responsible for:
    - Inspecting InternalContext
    - Inspecting InternalEpisode  
    - Identifying generation opportunities
    - Producing bounded InternalThoughts
    - Assigning confidence
    - Assigning provenance
    - Assigning semantic relationships

The generator never:
    * Invokes Executive
    * Executes capabilities
    * Performs actions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Dict, Any


@dataclass(frozen=True, slots=True)
class ThoughtGenerator:
    """
    Generator for internally created semantic thought candidates.
    
    The generator operates on InternalContext and InternalEpisode to produce
    bounded InternalThought instances that may later be evaluated, reflected upon,
    simulated, integrated, remembered or discarded by other components.
    
    ARCHITECTURAL PRINCIPLES:
        - Generation never executes behavior
        - Generation never invokes Executive  
        - Generation never schedules threads
        - Generated thoughts remain semantic objects only
        
    GENERATION PIPELINE:
        1. Inspect context (InternalContext)
        2. Inspect episode (InternalEpisode) 
        3. Identify generation opportunities
        4. Apply generation rules
        5. Validate and assess
        6. Produce bounded thought candidates
        
    THOUGHT KINDS SUPPORTED:
        - reflection: Self-referential processing
        - hypothesis: Proposed explanation awaiting validation
        - prediction: Expected outcome based on models
        - simulation: Scenario exploration
        - counterfactual: Alternative scenario analysis
        - evaluation: Assessment of validity or utility
        - association: Concept connections
        - question: Unknowns requiring answers
        - goal: Desired state representation
        - reminder: Attention-calling for unresolved matters
        - integration: Disparate information combination
        - narrative: Story structure maintenance
        - curiosity: Exploration signals
        - insight: Pattern recognition
        - explanation: How/why reasoning
        - constraint: Boundary identification
        - conflict: Contradiction detection
        - abstraction: General principles
        - concept_formation: New category formation
        - plan_idea: Coordination strategy
        - memory_link: Memory connections
        
    DETERMINISM REQUIREMENT:
        Given identical inputs (context, episode, configuration), the generator
        must produce equivalent thoughts. Randomness only enters through input
        variation, not generation logic.
    """
    
    # Generator configuration
    maximum_thoughts_per_generation: int = 10
    """Maximum thoughts to generate in one operation."""
    
    minimum_confidence: float = 0.3
    """Minimum confidence threshold for generated thoughts."""
    
    enable_reflection_generation: bool = True
    """Enable reflection-based thought generation."""
    
    enable_hypothesis_generation: bool = True
    """Enable hypothesis-based thought generation."""
    
    enable_prediction_generation: bool = True
    """Enable prediction-based thought generation."""
    
    # Generation history (bounded)
    last_generated_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of recently generated thoughts (for bounded history)."""
    
    def generate_from_context(
        self,
        context_data: Dict[str, Any],
        episode_data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Tuple[Any, ...], Tuple[str, ...]]:
        """
        Generate thought candidates from internal context.
        
        Args:
            context_data: InternalContext data for generation reference
            episode_data: Optional InternalEpisode data for context
            
        Returns:
            Tuple of (thoughts, error_messages)
            - thoughts: Generated InternalThought instances
            - error_messages: Any validation errors encountered
        """
        generated_thoughts = []
        errors = []
        
        # Get context information
        context_id = context_data.get("context_id", "unknown")
        context_version = context_data.get("version", "v1")
        active_focus_strength = context_data.get("active_focus_strength", 0.5)
        unresolved_goal_count = context_data.get("unresolved_goal_count", 0)
        
        originating_episode_id = None
        if episode_data:
            originating_episode_id = episode_data.get("episode_id")
        
        # Determine generation opportunities based on context state
        
        # 1. Check for unfinished reasoning or contradictions
        if self.enable_reflection_generation and unresolved_goal_count > 0:
            thought = self._generate_reflection_thought(
                context_id=context_id,
                context_version=context_version,
                originating_episode_id=originating_episode_id,
                unresolved_goals=unresolved_goal_count,
            )
            if thought:
                generated_thoughts.append(thought)
        
        # 2. Generate prediction opportunities
        if self.enable_prediction_generation and active_focus_strength > 0.3:
            for i in range(min(2, self.maximum_thoughts_per_generation - len(generated_thoughts))):
                thought = self._generate_prediction_thought(
                    context_id=context_id,
                    context_version=context_version,
                    originating_episode_id=originating_episode_id,
                    prediction_index=i,
                )
                if thought:
                    generated_thoughts.append(thought)
        
        # 3. Generate association thoughts for complex contexts
        if active_focus_strength > 0.5 and unresolved_goal_count > 1:
            thought = self._generate_association_thought(
                context_id=context_id,
                context_version=context_version,
                originating_episode_id=originating_episode_id,
            )
            if thought:
                generated_thoughts.append(thought)
        
        # 4. Generate curiosity signals for new contexts
        if len(self.last_generated_ids) < 5:  # New generation cycle
            thought = self._generate_curiosity_thought(
                context_id=context_id,
                context_version=context_version,
                originating_episode_id=originating_episode_id,
            )
            if thought:
                generated_thoughts.append(thought)
        
        # Update last generated IDs for bounded history
        new_ids = tuple(t.thought_id for t in generated_thoughts)
        self.last_generated_ids = new_ids + self.last_generated_ids[:10]
        
        return tuple(generated_thoughts), tuple(errors)
    
    def _generate_reflection_thought(
        self,
        context_id: str,
        context_version: str,
        originating_episode_id: Optional[str],
        unresolved_goals: int,
    ) -> Any:
        """Generate a reflection thought."""
        if unresolved_goals < 1:
            return None
        
        concept = f"reflect_on_unresolved:{unresolved_goals}_goals"
        purpose = "Analyze unresolved goals and derive insights for resolution"
        
        from .factory import create_factory
        factory = create_factory()
        success, result = factory.new_thought(
            concept=concept,
            purpose=purpose,
            thought_kind="reflection",
            originating_episode_id=originating_episode_id or "",
            originating_context_version=context_version,
            generator_type="default",
            assessment={"confidence": 0.7},
        )
        
        if success:
            return result
        return None
    
    def _generate_prediction_thought(
        self,
        context_id: str,
        context_version: str,
        originating_episode_id: Optional[str],
        prediction_index: int,
    ) -> Any:
        """Generate a prediction thought."""
        concept = f"predict_outcome:{prediction_index}"
        purpose = f"Formulate expected outcome {prediction_index} based on current models"
        
        from .factory import create_factory
        factory = create_factory()
        success, result = factory.new_thought(
            concept=concept,
            purpose=purpose,
            thought_kind="prediction",
            originating_episode_id=originating_episode_id or "",
            originating_context_version=context_version,
            generator_type="default",
            assessment={"confidence": 0.6},
        )
        
        if success:
            return result
        return None
    
    def _generate_association_thought(
        self,
        context_id: str,
        context_version: str,
        originating_episode_id: Optional[str],
    ) -> Any:
        """Generate an association thought."""
        concept = "associate_concepts:complex_context"
        purpose = "Identify connections between concepts in complex context"
        
        from .factory import create_factory
        factory = create_factory()
        success, result = factory.new_thought(
            concept=concept,
            purpose=purpose,
            thought_kind="association",
            originating_episode_id=originating_episode_id or "",
            originating_context_version=context_version,
            generator_type="default",
            assessment={"confidence": 0.5},
        )
        
        if success:
            return result
        return None
    
    def _generate_curiosity_thought(
        self,
        context_id: str,
        context_version: str,
        originating_episode_id: Optional[str],
    ) -> Any:
        """Generate a curiosity thought."""
        concept = "explore_new_connections"
        purpose = "Explore potential connections and associations"
        
        from .factory import create_factory
        factory = create_factory()
        success, result = factory.new_thought(
            concept=concept,
            purpose=purpose,
            thought_kind="curiosity",
            originating_episode_id=originating_episode_id or "",
            originating_context_version=context_version,
            generator_type="default",
            assessment={"confidence": 0.4},
        )
        
        if success:
            return result
        return None
    
    def reset_history(self) -> None:
        """Reset the generation history for a new cycle."""
        self.last_generated_ids = ()
    
    @classmethod
    def create(cls, **kwargs) -> ThoughtGenerator:
        """Create a new generator with configuration."""
        return ThoughtGenerator(**kwargs)
