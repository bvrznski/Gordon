# Rule Application - Phase 7.1
# ============================

"""
Canonical Rule Application Contract.

Rule Application records the application of an inference rule to premises.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

from gordon_system.src.agent.components.systems.cognition.reasoning.deductive.shared.inference_rule import InferenceRule


@dataclass(frozen=True)
class RuleApplication:
    """
    An application of an inference rule to premises.
    
    A rule application contains:
        - Identity and provenance tracking
        - The inference rule that was applied
        - Participating premises (antecedents)
        - Resulting conclusion (consequent)
        - Provenance tracking
    
    Rule applications are deterministic; the same premises with the same rule
    always produce the same conclusion.
    """
    
    # Identity
    application_id: str                     # Unique application identifier
    semantic_identity: str                  # Stable identity for replay
    
    # Rule information
    inference_rule: InferenceRule           # Which rule was applied?
    
    # Participating premises (inputs to the rule)
    participating_premises: Tuple[str, ...]  # The premises that matched the rule's requirements
    
    # Resulting conclusion (output of the rule)
    resulting_conclusion: str               # What follows from applying the rule?
    
    # Provenance
    application_order: int = 0              # Order in which this was applied
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None  # Which deduction session?
    
    @property
    def is_valid(self) -> bool:
        """Check if the rule application is valid (premises match)."""
        return len(self.participating_premises) == self.inference_rule.required_premise_count
    
    @classmethod
    def create(
        cls,
        inference_rule: InferenceRule,
        participating_premises: List[str],
        resulting_conclusion: str,
        application_order: int = 0,
        source_descriptor_id: Optional[str] = None,
    ) -> RuleApplication:
        """Create a new rule application."""
        return cls(
            application_id=f"rule_application:{uuid.uuid4().hex[:16]}",
            semantic_identity=f"rule_app:{inference_rule.semantic_identity}:{hash(tuple(participating_premises))}",
            inference_rule=inference_rule,
            participating_premises=tuple(participating_premises),
            resulting_conclusion=resulting_conclusion,
            application_order=application_order,
            source_descriptor_id=source_descriptor_id,
        )


__all__ = [
    "RuleApplication",
]