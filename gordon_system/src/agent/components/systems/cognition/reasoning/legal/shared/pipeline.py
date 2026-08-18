# Legal Pipeline - Phase 7.47 Part 1
# ====================================

"""
Canonical Legal Pipeline Contract.

Legal pipeline flow:
    Jurisdiction Identification
        ↓
    Legal Source Discovery
        ↓
    Legal Interpretation
        ↓
    Rights Analysis
        ↓
    Obligation Analysis
        ↓
    Compliance Assessment
        ↓
    Validation
        ↓
    Publication

Legal Reasoning remains deterministic.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class LegalStage(Enum):
    """Pipeline stages in legal reasoning."""
    
    JURISDICTION_IDENTIFICATION = "jurisdiction_identification"
    LEGAL_SOURCE_DISCOVERY = "legal_source_discovery"
    LEGAL_INTERPRETATION = "legal_interpretation"
    RIGHTS_ANALYSIS = "rights_analysis"
    OBLIGATION_ANALYSIS = "obligation_analysis"
    COMPLIANCE_ASSESSMENT = "compliance_assessment"
    VALIDATION = "validation"
    PUBLICATION = "publication"


@dataclass(frozen=True)
class LegalPipeline:
    """
    Pipeline tracking legal reasoning progress through stages.
    
    A pipeline includes:
        - Interpretation strategy used
        - Results at each stage
        - Compliance outcome
        - Diagnostic information
    
    The canonical pipeline flow ensures all aspects of legal reasoning
    are systematically addressed.
    """
    
    # Identity
    pipeline_id: str                          # Unique identifier
    
    # Pipeline state
    current_stage: LegalStage = LegalStage.JURISDICTION_IDENTIFICATION
    
    # Interpretation
    interpretation_strategy: Optional[str] = None  # Strategy used
    
    # Results
    jurisdiction_analysis: Optional[Dict[str, Any]] = None
    source_discovery_result: Optional[Dict[str, Any]] = None
    legal_interpretation: Optional[Dict[str, Any]] = None
    rights_analysis: Optional[Dict[str, Any]] = None
    obligation_analysis: Optional[Dict[str, Any]] = None
    compliance_result: Optional[Dict[str, Any]] = None
    
    # Timing
    stages_started_at: Dict[str, float] = field(default_factory=dict)
    stages_completed_at: Dict[str, float] = field(default_factory=dict)
    
    # Diagnostics
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        interpretation_strategy: Optional[str] = None,
    ) -> LegalPipeline:
        """Create a new legal pipeline."""
        return cls(
            pipeline_id=f"legal_pipeline:{uuid.uuid4().hex[:16]}",
            current_stage=LegalStage.JURISDICTION_IDENTIFICATION,
            interpretation_strategy=interpretation_strategy,
            stages_started_at={stage.value: time.time() for stage in LegalStage},
        )
    
    def advance_to(self, new_stage: LegalStage) -> LegalPipeline:
        """Return a copy with updated stage."""
        self.stages_completed_at[new_stage.value] = time.time()
        return dataclass_replace(
            self,
            current_stage=new_stage,
        )
    
    def add_diagnostic(self, diagnostic: Dict[str, Any]) -> LegalPipeline:
        """Add a diagnostic record."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + [diagnostic],
        )
    
    def add_error(self, error: Dict[str, Any]) -> LegalPipeline:
        """Add an error record."""
        return dataclass_replace(
            self,
            errors=self.errors + [error],
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "LegalPipeline",
    "LegalStage",
]