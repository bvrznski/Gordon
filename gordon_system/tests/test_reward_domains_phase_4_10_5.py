# Tests for Phase 4.10.5 - Multi-Domain Reward Engine
# ======================================================

"""
Test suite for the Multi-Domain Reward Engine (Phase 4.10.5).

This module tests:
    * Domain classification
    * Taxonomy system
    * Profile construction
    * State generation
    * Validation logic
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import phase 4.10.5 components using relative imports from gordon_system
from agent.components.networks.reward.domains.domain import (
    RewardDomain,
    DomainType,
)

from agent.components.networks.reward.domains.taxonomy import (
    RewardTaxonomy,
    DomainClassificationRules,
)

from agent.components.networks.reward.domains.classifiers.base import (
    BaseRewardClassifier,
    ClassifierResult,
)

from agent.components.networks.reward.domains.classifiers.intrinsic import (
    IntrinsicRewardClassifier,
)

from agent.components.networks.reward.domains.classifiers.extrinsic import (
    ExtrinsicRewardClassifier,
)

from agent.components.networks.reward.domains.profile import (
    RewardProfile,
    DomainProfile,
)

from agent.components.networks.reward.domains.state import (
    MultiDomainRewardState,
)

from agent.components.networks.reward.domains.engine import (
    RewardDomainEngine,
)


# =============================================================================
# TEST SUITE 1: DOMAIN TYPE ENUM
# =============================================================================

class TestDomainType:
    """Test domain type enum values."""
    
    def test_intrinsic_domain(self):
        """Test intrinsic domain type exists and has correct value."""
        assert DomainType.INTRINSIC.value == "intrinsic"
    
    def test_extrinsic_domain(self):
        """Test extrinsic domain type exists and has correct value."""
        assert DomainType.EXTRINSIC.value == "extrinsic"
    
    def test_social_domain(self):
        """Test social domain type exists and has correct value."""
        assert DomainType.SOCIAL.value == "social"
    
    def test_epistemic_domain(self):
        """Test epistemic domain type exists and has correct value."""
        assert DomainType.EPISTEMIC.value == "epistemic"
    
    def test_competence_domain(self):
        """Test competence domain type exists and has correct value."""
        assert DomainType.COMPETENCE.value == "competence"
    
    def test_autonomy_domain(self):
        """Test autonomy domain type exists and has correct value."""
        assert DomainType.AUTONOMY.value == "autonomy"
    
    def test_curiosity_domain(self):
        """Test curiosity domain type exists and has correct value."""
        assert DomainType.CURIOSITY.value == "curiosity"
    
    def test_mission_domain(self):
        """Test mission domain type exists and has correct value."""
        assert DomainType.MISSION.value == "mission"
    
    def test_normative_domain(self):
        """Test normative domain type exists and has correct value."""
        assert DomainType.NORMATIVE.value == "normative"


# =============================================================================
# TEST SUITE 2: REWARD DOMAIN MODEL
# =============================================================================

class TestRewardDomain:
    """Test RewardDomain model."""
    
    def test_create_intrinsic_domain(self):
        """Test creating an intrinsic reward domain."""
        domain = RewardDomain.create_intrinsic(
            estimate_refs=("est_1", "est_2"),
            confidence=0.8,
        )
        
        assert domain.domain_type == DomainType.INTRINSIC
        assert domain.confidence == 0.8
        # Uncertainty is set to 0.0 by default in factory methods
        assert domain.uncertainty == 0.0
        assert len(domain.supporting_estimates) == 2
    
    def test_create_extrinsic_domain(self):
        """Test creating an extrinsic reward domain."""
        domain = RewardDomain.create_extrinsic()
        
        assert domain.domain_type == DomainType.EXTRINSIC
        assert domain.confidence == 1.0
        assert domain.uncertainty == 0.0
    
    def test_domain_is_valid(self):
        """Test domain validation."""
        domain = RewardDomain.create_intrinsic(confidence=0.7)
        assert domain.is_valid is True
    
    def test_domain_to_dict(self):
        """Test domain dictionary conversion."""
        domain = RewardDomain.create_intrinsic()
        d = domain.to_dict()
        
        assert d["domain_type"] == "intrinsic"
        assert d["confidence"] == 1.0
        assert "revision" in d


# =============================================================================
# TEST SUITE 3: TAXONOMY SYSTEM
# =============================================================================

class TestTaxonomy:
    """Test taxonomy system."""
    
    def test_canonical_taxonomy_exists(self):
        """Test that canonical taxonomy can be created."""
        taxonomy = RewardTaxonomy.create_canonical()
        
        assert taxonomy.domain_count > 0
    
    def test_get_domain_by_alias(self):
        """Test domain lookup by alias."""
        taxonomy = RewardTaxonomy.create_canonical()
        
        result = taxonomy.get_domain_type_by_alias("intrinsic_reward")
        assert result == DomainType.INTRINSIC
    
    def test_classification_rules_exists(self):
        """Test that classification rules can be created."""
        rules = DomainClassificationRules.create_canonical()
        
        assert rules.threshold_count > 0


# =============================================================================
# TEST SUITE 4: CLASSIFIERS
# =============================================================================

class TestClassifiers:
    """Test domain classifiers."""
    
    def test_intrinsic_classifier_domain_type(self):
        """Test intrinsic classifier returns correct domain type."""
        classifier = IntrinsicRewardClassifier()
        
        assert classifier.domain_type == DomainType.INTRINSIC
    
    def test_extrinsic_classifier_domain_type(self):
        """Test extrinsic classifier returns correct domain type."""
        classifier = ExtrinsicRewardClassifier()
        
        assert classifier.domain_type == DomainType.EXTRINSIC
    
    def test_classifier_classifies_estimates(self):
        """Test that classifiers can classify reward estimates."""
        classifier = IntrinsicRewardClassifier()
        
        estimates = (
            {"estimate_id": "est_1", "magnitude": 0.5, "source": "problem_solving"},
        )
        
        result = classifier.classify(estimates)
        
        assert result.domain_type == DomainType.INTRINSIC
        assert result.is_valid is True


# =============================================================================
# TEST SUITE 5: PROFILE CONSTRUCTION
# =============================================================================

class TestProfile:
    """Test reward profile construction."""
    
    def test_domain_profile_from_domain(self):
        """Test creating domain profile from domain."""
        domain = RewardDomain.create_intrinsic(confidence=0.7)
        profile = DomainProfile.from_domain(domain)
        
        assert profile.domain_type == DomainType.INTRINSIC
        assert profile.confidence == 0.7
    
    def test_reward_profile_from_domains(self):
        """Test creating reward profile from domains."""
        domain1 = RewardDomain.create_intrinsic(confidence=0.8)
        domain2 = RewardDomain.create_extrinsic(confidence=0.6)
        
        profile = RewardProfile.from_domains((domain1, domain2))
        
        assert profile.total_domains == 2
        assert profile.aggregate_confidence == 0.7  # (0.8 + 0.6) / 2


# =============================================================================
# TEST SUITE 6: MULTI-DOMAIN STATE
# =============================================================================

class TestMultiDomainState:
    """Test multi-domain reward state."""
    
    def test_state_creation(self):
        """Test creating multi-domain reward state."""
        engine = RewardDomainEngine()
        
        estimates = (
            {"estimate_id": "est_1", "magnitude": 0.5, "source": "intrinsic"},
        )
        
        trace, state = engine.classify_domains(estimates)
        
        assert len(trace) > 0
        assert state.has_domains is True
    
    def test_state_get_domain_confidence(self):
        """Test getting domain confidence from state."""
        engine = RewardDomainEngine()
        
        estimates = (
            {"estimate_id": "est_1", "magnitude": 0.5, "source": "intrinsic"},
        )
        
        _, state = engine.classify_domains(estimates)
        
        # Check that we can access domain confidence
        conf = state.get_domain_confidence(DomainType.INTRINSIC)
        assert isinstance(conf, float)


# =============================================================================
# TEST SUITE 7: INTEGRATION
# =============================================================================

class TestIntegration:
    """Test integration between components."""
    
    def test_full_classification_pipeline(self):
        """Test complete classification pipeline."""
        engine = RewardDomainEngine()
        
        # Create sample estimates with various domains
        estimates = (
            {"estimate_id": "est_1", "magnitude": 0.5, "source": "problem_solving"},
            {"estimate_id": "est_2", "magnitude": 0.3, "source": "task_completion"},
            {"estimate_id": "est_3", "magnitude": 0.7, "source": "knowledge_acquisition"},
        )
        
        trace, state = engine.classify_domains(estimates)
        
        # Verify pipeline completed
        assert "STATE_CONSTRUCTED" in trace or "VALIDATION_COMPLETED" in trace
        
        # Verify state structure
        assert state.reward_profile is not None
        assert state.domain_graph is not None
    
    def test_empty_estimates_handled(self):
        """Test handling of empty estimates."""
        engine = RewardDomainEngine()
        
        trace, state = engine.classify_domains(())
        
        # State should be created even for empty input
        assert state is not None


# =============================================================================
# TEST SUITE 8: DETERMINISM
# =============================================================================

class TestDeterminism:
    """Test deterministic behavior."""
    
    def test_same_inputs_produce_same_outputs(self):
        """Test that same inputs produce identical outputs."""
        engine = RewardDomainEngine()
        
        estimates = (
            {"estimate_id": "est_1", "magnitude": 0.5, "source": "intrinsic"},
        )
        
        _, state1 = engine.classify_domains(estimates)
        _, state2 = engine.classify_domains(estimates)
        
        # States should have identical structure
        assert state1.total_domains == state2.total_domains


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])