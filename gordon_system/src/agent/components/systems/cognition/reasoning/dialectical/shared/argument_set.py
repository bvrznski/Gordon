# Dialectical Argument Set - Phase 7.17
# ======================================

"""
Canonical Dialectical Argument Set Contract.

Dialectical Reasoning operates over explicit Argument Sets.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ArgumentSet:
    """
    An immutable set of arguments for dialectical analysis.

    Argument Sets define:
        - Participating arguments
        - Evaluation criteria
        - Shared evidence
        - Reasoning constraints
        - Termination conditions

    Argument Sets remain immutable during analysis to preserve traceability.
    """

    # Identity
    argument_set_id: str                    # Unique identifier

    # Participating arguments
    participating_arguments: Tuple[str, ...]  # Argument IDs

    # Shared evidence (evidence supporting all arguments)
    shared_evidence: Tuple[Dict[str, Any], ...] = ()

    # Evaluation scope (what aspects are being evaluated?)
    evaluation_scope: str = "truth_value"

    # Timing
    created_at_utc: float = field(default_factory=time.time)

    @classmethod
    def create(
        cls,
        participating_arguments: List[str],
        shared_evidence: Optional[List[Dict[str, Any]]] = None,
        evaluation_scope: str = "truth_value",
    ) -> ArgumentSet:
        """Create a new argument set."""
        return cls(
            argument_set_id=f"argument_set:{uuid.uuid4().hex[:16]}",
            participating_arguments=tuple(participating_arguments),
            shared_evidence=tuple(shared_evidence or []),
            evaluation_scope=evaluation_scope,
        )

    def with_additional_argument(self, argument_id: str) -> ArgumentSet:
        """Return a copy with an additional argument."""
        return dataclass_replace(
            self,
            participating_arguments=self.participating_arguments + (argument_id,),
        )

    def with_evidence(self, evidence_item: Dict[str, Any]) -> ArgumentSet:
        """Return a copy with additional evidence."""
        return dataclass_replace(
            self,
            shared_evidence=self.shared_evidence + (evidence_item,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ArgumentSet",
]