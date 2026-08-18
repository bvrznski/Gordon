# Game Validation - Phase 7.43
# ==========================

"""
Canonical Game Validation definitions.

Validation is observational and never modifies game artifacts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating a single component."""
    
    component: str                          # What was validated?
    passed: bool                            # Did it pass?
    issues: Tuple[str, ...] = ()            # Any found issues?
    confidence: float = 1.0                 # Confidence in result


@dataclass(frozen=True)
class GameValidation:
    """
    Validation of game-theoretic reasoning.
    
    Validation is observational and never modifies artifacts directly.
    """
    
    # Identity
    validation_identity: str                # Unique identifier
    
    # Sessions validated
    evaluated_sessions: Tuple[str, ...] = ()  # Session IDs validated
    
    # Results
    results: Tuple[ValidationResult, ...] = ()  # Individual component results
    
    # Overall status
    overall_passed: bool = True             # Did all validations pass?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_session_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: List[str],
        source_session_id: Optional[str] = None,
    ) -> GameValidation:
        """Create a new game validation."""
        return cls(
            validation_identity=f"validation:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(evaluated_sessions),
            source_session_id=source_session_id,
        )
    
    def with_result(self, result: ValidationResult) -> GameValidation:
        """Add a validation result."""
        new_passed = self.overall_passed and result.passed
        return dataclass_replace(
            self,
            results=self.results + (result,),
            overall_passed=new_passed,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ValidationResult",
    "GameValidation",
]
