# Proof Optimization - Phase 7.1
# ===============================

"""
Canonical Proof Optimization Contract.

Proof Optimization simplifies proofs without changing conclusions.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ProofOptimization:
    """
    An optimized version of a proof.
    
    Optimization may include:
        - Removing redundant steps
        - Merging equivalent paths
        - Reusing lemmas
        - Eliminating dead branches
    
    Optimization never changes conclusions; it preserves logical equivalence.
    """
    
    # Identity
    optimization_id: str                    # Unique optimization identifier
    
    # Original proof
    original_proof: str                     # Proof ID of the original
    
    # Optimized version
    optimized_proof: str                    # Resulting optimized proof ID
    
    # Optimization steps applied
    optimization_steps: Tuple[str, ...]     # What changes were made?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None  # Which deduction session?
    
    @property
    def step_count(self) -> int:
        """Count of optimization steps."""
        return len(self.optimization_steps)
    
    @classmethod
    def create(
        cls,
        original_proof: str,
        optimized_proof: str,
        optimization_steps: Optional[List[str]] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> ProofOptimization:
        """Create a new proof optimization record."""
        return cls(
            optimization_id=f"proof_optimization:{uuid.uuid4().hex[:16]}",
            original_proof=original_proof,
            optimized_proof=optimized_proof,
            optimization_steps=tuple(optimization_steps or []),
            source_descriptor_id=source_descriptor_id,
        )
    
    def append_step(self, step: str) -> ProofOptimization:
        """Return a copy with an additional optimization step."""
        return dataclass_replace(
            self,
            optimization_steps=self.optimization_steps + (step,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ProofOptimization",
]