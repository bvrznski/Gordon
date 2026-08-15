# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Tests for Action Ontology Subsystem (Phase 4.5.3)

This module provides comprehensive tests for the canonical Action ontology.
"""

import pytest
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gordon_system.src.agent.action.ontology import (
    categories,
    purposes,
    kinds,
    capabilities,
    targets,
    subjects,
    effects,
    relationships,
    composition,
    modality,
    validation,
)


class TestActionCategories:
    """Tests for ActionCategory ontology."""
    
    def test_categories_have_unique_values(self):
        values = [c.value for c in categories.ActionCategory]
        assert len(values) == len(set(values)), "Duplicate category values detected"
    
    def test_category_count(self):
        # Should have all required categories from spec
        expected_categories = {
            "observational", "informational", "computational",
            "transformational", "communicative", "delegative",
            "resource", "memory", "workspace", "planning_support",
            "executive_support", "monitoring_support", "recovery_support",
            "security", "policy", "configuration", "external_interaction",
            "physical", "composite", "general", "unknown"
        }
        actual_values = {c.value for c in categories.ActionCategory}
        assert expected_categories.issubset(actual_values), \
            f"Missing categories: {expected_categories - actual_values}"
    
    def test_category_kinds(self):
        """Test that categories have associated kinds."""
        cat = categories.ActionCategory.OBSERVATIONAL
        kinds_list = cat.get_kinds()
        assert isinstance(kinds_list, tuple)
        assert len(kinds_list) > 0
    
    def test_is_informational_property(self):
        assert categories.ActionCategory.OBSERVATIONAL.is_informational
        assert not categories.ActionCategory.COMPUTATIONAL.is_informational


class TestActionKinds:
    """Tests for ActionKind ontology."""
    
    def test_kinds_have_unique_values(self):
        values = [k.value for k in kinds.ActionKind]
        assert len(values) == len(set(values)), "Duplicate kind values detected"
    
    def test_kind_category_relationship(self):
        """Test that kinds can be mapped to categories."""
        from gordon_system.src.agent.action.ontology.categories import _KIND_CATEGORIES
        category = _KIND_CATEGORIES.get(kinds.ActionKind.READ)
        assert isinstance(category, categories.ActionCategory)
    
    def test_is_informational_property(self):
        kind = kinds.ActionKind.OBSERVE
        assert kind.is_informational
    
    def test_is_transformative_property(self):
        kind = kinds.ActionKind.CREATE
        assert kind.is_transformative


class TestActionPurposes:
    """Tests for ActionPurpose ontology."""
    
    def test_purposes_have_unique_values(self):
        values = [p.value for p in purposes.ActionPurpose]
        assert len(values) == len(set(values)), "Duplicate purpose values detected"
    
    def test_is_informational_property(self):
        assert purposes.ActionPurpose.READ.is_informational
        assert not purposes.ActionPurpose.CREATE.is_informational
    
    def test_is_mutating_property(self):
        assert purposes.ActionPurpose.TRANSFORM.is_mutating
        assert not purposes.ActionPurpose.INSPECT.is_mutating


class TestActionCapabilities:
    """Tests for ActionCapability ontology."""
    
    def test_capabilities_have_unique_values(self):
        values = [c.value for c in capabilities.ActionCapability]
        assert len(values) == len(set(values)), "Duplicate capability values detected"
    
    def test_is_computational_property(self):
        assert capabilities.ActionCapability.NETWORK.is_computational
        assert not capabilities.ActionCapability.FILESYSTEM.is_computational


class TestActionTargets:
    """Tests for ActionTargetKind ontology."""
    
    def test_targets_have_unique_values(self):
        values = [t.value for t in targets.ActionTargetKind]
        assert len(values) == len(set(values)), "Duplicate target values detected"
    
    def test_filesystem_targets_exist(self):
        expected_fs_targets = {
            "file", "directory", "path"
        }
        actual_values = {t.value for t in targets.ActionTargetKind}
        assert expected_fs_targets.issubset(actual_values)


class TestActionSubjects:
    """Tests for ActionSubjectKind ontology."""
    
    def test_subjects_have_unique_values(self):
        values = [s.value for s in subjects.ActionSubjectKind]
        assert len(values) == len(set(values)), "Duplicate subject values detected"
    
    def test_user_related_subjects_exist(self):
        expected = {"user", "operator", "assistant"}
        actual = {s.value for s in subjects.ActionSubjectKind}
        assert expected.issubset(actual)


class TestActionEffects:
    """Tests for ActionEffectKind ontology."""
    
    def test_effects_have_unique_values(self):
        values = [e.value for e in effects.ActionEffectKind]
        assert len(values) == len(set(values)), "Duplicate effect values detected"
    
    def test_state_change_effects_exist(self):
        expected = {"state_created", "state_updated", "state_removed"}
        actual = {e.value for e in effects.ActionEffectKind}
        assert expected.issubset(actual)


class TestActionRelationships:
    """Tests for ActionRelationship ontology."""
    
    def test_relationships_have_unique_values(self):
        values = [r.value for r in relationships.ActionRelationship]
        assert len(values) == len(set(values)), "Duplicate relationship values detected"
    
    def test_hierarchical_relationships_exist(self):
        expected = {"is_a", "specializes", "generalizes"}
        actual = {r.value for r in relationships.ActionRelationship}
        assert expected.issubset(actual)
    
    def test_reversal_relationships_exist(self):
        expected = {"compensates_for", "rolls_back", "undoes", "restores"}
        actual = {r.value for r in relationships.ActionRelationship}
        assert expected.issubset(actual)


class TestActionComposition:
    """Tests for Action Composition ontology."""
    
    def test_composition_types_have_unique_values(self):
        values = [t.value for t in composition.ActionCompositionType]
        assert len(values) == len(set(values)), "Duplicate composition type values detected"
    
    def test_composite_patterns_exist(self):
        expected = {"pipeline", "chain", "map", "reduce"}
        actual = {p.value for p in composition.ActionCompositePattern}
        assert expected.issubset(actual)


class TestActionModality:
    """Tests for ActionModality ontology."""
    
    def test_modalities_have_unique_values(self):
        values = [m.value for m in modality.ActionModality]
        assert len(values) == len(set(values)), "Duplicate modality values detected"
    
    def test_is_read_only_property(self):
        assert modality.ActionModality.READ_ONLY.is_read_only
        assert not modality.ActionModality.STATE_MODIFYING.is_read_only


class TestValidation:
    """Tests for ontology validation."""
    
    def test_validate_ontology_consistency(self):
        result = validation.validate_ontology_consistency()
        assert isinstance(result, validation.OntologyValidationResult)
    
    def test_validate_acyclic(self):
        assert validation.validate_acyclic() is True
    
    def test_validate_unique_values(self):
        assert validation.validate_unique_values() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])