# Autobiographical Reasoning Shared Models - Phase 7.31
# =====================================================

"""
Shared models for the Autobiographical Reasoning subsystem.

This module contains canonical contracts and data structures that define
the autobiographical reasoning architecture.
"""

from .descriptor import AutobiographicalDescriptor
from .autobiographical_set import AutobiographicalSet
from .pipeline import AutobiographicalPipeline
from .continuity import TemporalContinuity, IdentityEvolution, NarrativePublication
from .narrative import NarrativeManagement, ChronologyManagement, IdentityEvolutionManagement, AutobiographicalEvolution
from .chronology import ChronologyManagement
from .identity import IdentityEvolutionManagement
from .evolution import AutobiographicalEvolution
from .validation import AutobiographicalValidation
from .failure import AutobiographicalFailure
from .governance import AutobiographicalGovernance
from .health import AutobiographicalHealth
from .integration import AutobiographicalIntegration
from .observability import AutobiographicalObservability

__all__ = [
    # Shared Contracts
    "AutobiographicalDescriptor",
    "AutobiographicalSet",
    "AutobiographicalPipeline",
    
    # Continuity
    "TemporalContinuity",
    "IdentityEvolution",
    "NarrativePublication",
    
    # Narrative Management
    "NarrativeManagement",
    "ChronologyManagement",
    "IdentityEvolutionManagement",
    "AutobiographicalEvolution",
    
    # Chronology
    "ChronologyManagement",
    
    # Identity Evolution
    "IdentityEvolutionManagement",
    
    # Validation
    "AutobiographicalValidation",
    
    # Failure
    "AutobiographicalFailure",
    
    # Governance
    "AutobiographicalGovernance",
    
    # Health
    "AutobiographicalHealth",
    
    # Integration
    "AutobiographicalIntegration",
    
    # Observability
    "AutobiographicalObservability",
]