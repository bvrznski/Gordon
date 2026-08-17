# Deductive Proof - Phase 7.1
# ============================

"""
Canonical Deductive Proof Contract.

Deductive Proofs construct formal proofs from premises via inference rules.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ProofStepKind(Enum):
    """Kinds of steps in a proof."""
    
    PREMISE = "premise"                       # A premise is introduced
    RULE_APPLICATION = "rule_application"     # An inference rule is applied
    INTERMEDIATE_CONCLUSION = "intermediate_conclusion"  # Result from previous step
    FINAL_CONCLUSION = "final_conclusion"     # The final result of the proof


@dataclass(frozen=True)
class ProofNode:
    """
    A node in a proof graph.
    
    Each node represents either a premise or an intermediate/final conclusion.
    """
    
    # Identity
    node_id: str                            # Unique node identifier
    
    # Content
    statement: str                          # What is being stated?
    node_kind: ProofStepKind                # What kind of node?
    
    # Provenance
    step_number: int = 0                    # Order in the proof sequence
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_premise(self) -> bool:
        """Check if this is a premise."""
        return self.node_kind == ProofStepKind.PREMISE
    
    @property
    def is_conclusion(self) -> bool:
        """Check if this is a conclusion (intermediate or final)."""
        return self.node_kind in (
            ProofStepKind.INTERMEDIATE_CONCLUSION,
            ProofStepKind.FINAL_CONCLUSION,
        )


@dataclass(frozen=True)
class ProofStep:
    """
    A single step in a deductive proof.
    
    Each step consists of:
        - Premises being used (antecedents)
        - Rule being applied
        - Conclusion being derived (consequent)
    
    Steps remain explicit; they can be independently verified.
    """
    
    # Identity
    step_id: str                            # Unique step identifier
    
    # Input premises
    input_nodes: Tuple[str, ...]            # Which nodes are the inputs?
    
    # Rule application
    rule_applied: Optional[str] = None      # Which rule was applied? (None for premises)
    
    # Output conclusion
    output_node: str                        # What is produced?
    
    # Provenance
    step_number: int = 0                    # Order in proof sequence
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create_premise(
        cls,
        premise_statement: str,
        step_number: int = 0,
    ) -> ProofStep:
        """Create a premise introduction step."""
        return cls(
            step_id=f"step:{uuid.uuid4().hex[:8]}",
            input_nodes=(),
            rule_applied=None,
            output_node=premise_statement,
            step_number=step_number,
        )
    
    @classmethod
    def create_application(
        cls,
        rule_identity: str,
        input_statements: List[str],
        conclusion_statement: str,
        step_number: int = 0,
    ) -> ProofStep:
        """Create a rule application step."""
        return cls(
            step_id=f"step:{uuid.uuid4().hex[:8]}",
            input_nodes=tuple(input_statements),
            rule_applied=rule_identity,
            output_node=conclusion_statement,
            step_number=step_number,
        )


@dataclass(frozen=True)
class DeductiveProof:
    """
    A formal deductive proof.
    
    A proof contains:
        - Participating premises
        - Inference steps (applications of rules)
        - Intermediate conclusions
        - Final conclusion
    
    Proofs remain inspectable; they can be independently verified.
    """
    
    # Identity
    proof_id: str                           # Unique proof identifier
    semantic_identity: str                  # Stable identity for replay
    
    # Participating premises
    participating_premises: Tuple[str, ...]  # All premises used in this proof
    
    # Inference steps
    inference_steps: Tuple[ProofStep, ...]  # Steps from premises to conclusion
    
    # Resulting conclusion
    resulting_conclusion: str               # The final conclusion
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None  # Which deduction session?
    
    @property
    def step_count(self) -> int:
        """Count of inference steps."""
        return len(self.inference_steps)
    
    @property
    def is_complete(self) -> bool:
        """Check if the proof has at least one premise and a conclusion."""
        return (
            len(self.participating_premises) > 0 
            and self.step_count >= 1
            and self.resulting_conclusion != ""
        )
    
    @classmethod
    def create(
        cls,
        premises: List[str],
        inference_steps: List[ProofStep],
        final_conclusion: str,
        source_descriptor_id: Optional[str] = None,
    ) -> DeductiveProof:
        """Create a new deductive proof."""
        return cls(
            proof_id=f"proof:{uuid.uuid4().hex[:16]}",
            semantic_identity=f"proof:{hash(tuple(premises))}:{final_conclusion}",
            participating_premises=tuple(premises),
            inference_steps=tuple(inference_steps),
            resulting_conclusion=final_conclusion,
            source_descriptor_id=source_descriptor_id,
        )
    
    def append_step(self, step: ProofStep) -> DeductiveProof:
        """Return a copy with an additional inference step."""
        return dataclass_replace(
            self,
            inference_steps=self.inference_steps + (step,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DeductiveProof",
    "ProofStep",
    "ProofNode",
    "ProofStepKind",
]