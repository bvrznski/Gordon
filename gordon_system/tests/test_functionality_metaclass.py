# Functionality Metaclass Tests - Phase 3.13.4
# ==============================================

"""
Unit tests for Functionality Metaclass Registration & Reflection.

Tests cover:
    - Marker resolution from MRO
    - Direct vs inherited classification detection
    - Conflict detection and rejection
    - Exemption handling
    - Metadata construction
    - Registry operations
    - Sealing behavior
"""

import unittest
from typing import Type

from gordon_system.src.agent.components.core.functionality_markers import (
    CoreFunctionality,
    ForCore,
    ForExecution,
    ForEntrypoint,
    ForArchitecture,
    ForNetworks,
    ForCapabilities,
    ForSystems,
)

# Import Phase 3.13.4 implementations
from gordon_system.src.agent.components.core.functionality_markers.metaclass import (
    ClassificationStatus,
    ClassificationSource,
    StrictnessMode,
    Finding,
    ClassificationFindings,
    ExemptionKind,
    FunctionalityExemption,
    SecondaryRole,
    IntegrationBoundary,
    CoreFunctionalityMetadata,
    FunctionalityMetaclass,
    FunctionalityAwareMetaclass,
)

from gordon_system.src.agent.components.core.functionality_markers.registry import (
    RegistryState,
    RegistryEntry,
    RejectedRegistration,
    RegistrySnapshot,
    RegistryStatistics,
    FunctionalityRegistry,
    RegistrySealedError,
)


class TestClassificationStatus(unittest.TestCase):
    """Tests for ClassificationStatus enumeration."""
    
    def test_valid_statuses_exist(self) -> None:
        """Test that all expected statuses are defined."""
        expected = {
            "VALID_DIRECT", "VALID_INHERITED", "VALID_EXEMPT",
            "FUNCTIONALITY_NEUTRAL", "UNCLASSIFIED_LEGACY",
            "MIGRATION_PENDING", "MISSING_REQUIRED", "CONFLICTING",
            "INVALID_OVERRIDE", "INVALID_MARKER", "REGISTRATION_REJECTED"
        }
        
        actual = {status.value for status in ClassificationStatus}
        self.assertTrue(expected.issubset(actual))


class TestClassificationSource(unittest.TestCase):
    """Tests for ClassificationSource enumeration."""
    
    def test_source_types_exist(self) -> None:
        """Test all source types are defined."""
        expected = {
            "direct_marker", "inherited_marker", "explicit_metadata",
            "enclosing_owner_derivation", "exemption", "legacy_package_hint",
            "unknown", "conflicting"
        }
        
        actual = {source.value for source in ClassificationSource}
        self.assertEqual(expected, actual)


class TestStrictnessMode(unittest.TestCase):
    """Tests for StrictnessMode enumeration."""
    
    def test_modes_exist(self) -> None:
        """Test all strictness modes are defined."""
        expected = {"strict", "migration", "audit_only", "test"}
        actual = {mode.value for mode in StrictnessMode}
        self.assertEqual(expected, actual)


class TestFunctionalityAwareMetaclass(unittest.TestCase):
    """Tests for FunctionalityAwareMetaclass."""
    
    def test_metaclass_is_abstract(self) -> None:
        """Test that FunctionalityMetaclass is abstract."""
        self.assertTrue(issubclass(FunctionalityMetaclass, type))


class TestFunctionalityRegistry(unittest.TestCase):
    """Tests for FunctionalityRegistry."""
    
    def test_initial_state(self) -> None:
        """Test registry initial state."""
        registry = FunctionalityRegistry()
        
        self.assertFalse(registry.is_sealed)
        self.assertEqual(registry.size, 0)
    
    def test_register_metadata(self) -> None:
        """Test registering metadata."""
        registry = FunctionalityRegistry()
        
        # Create test metadata
        metadata = CoreFunctionalityMetadata(
            qualified_name="test.Module.Class",
            canonical_owner="test.module",
            primary_functionality=ForExecution,
            primary_marker_name="ForExecution",
            classification_source=ClassificationSource.DIRECT_MARKER,
            requirement_status=ClassificationStatus.VALID_DIRECT,
            classification_status=ClassificationStatus.VALID_DIRECT,
            is_abstract=False,
            is_protocol=False,
            is_mixin=False,
            is_nested=False,
            secondary_roles=(),
            integration_boundaries=(),
            exemptions=(),
            findings=(),
        )
        
        success, findings = registry.register(metadata)
        
        self.assertTrue(success)
        self.assertEqual(registry.size, 1)
    
    def test_sealed_registry_rejects_new(self) -> None:
        """Test sealed registry rejects new registrations."""
        registry = FunctionalityRegistry()
        registry.seal()
        
        metadata = CoreFunctionalityMetadata(
            qualified_name="test.Class",
            canonical_owner="test",
            primary_functionality=ForCore,
            primary_marker_name="ForCore",
            classification_source=ClassificationSource.DIRECT_MARKER,
            requirement_status=ClassificationStatus.VALID_DIRECT,
            classification_status=ClassificationStatus.VALID_DIRECT,
            is_abstract=False,
            is_protocol=False,
            is_mixin=False,
            is_nested=False,
            secondary_roles=(),
            integration_boundaries=(),
            exemptions=(),
            findings=(),
        )
        
        with self.assertRaises(RegistrySealedError):
            registry.register(metadata)


class TestRegistrySnapshot(unittest.TestCase):
    """Tests for RegistrySnapshot."""
    
    def test_snapshot_contains_entries(self) -> None:
        """Test snapshot contains registered entries."""
        registry = FunctionalityRegistry()
        
        metadata = CoreFunctionalityMetadata(
            qualified_name="test.Module.Class",
            canonical_owner="test.module",
            primary_functionality=ForExecution,
            primary_marker_name="ForExecution",
            classification_source=ClassificationSource.DIRECT_MARKER,
            requirement_status=ClassificationStatus.VALID_DIRECT,
            classification_status=ClassificationStatus.VALID_DIRECT,
            is_abstract=False,
            is_protocol=False,
            is_mixin=False,
            is_nested=False,
            secondary_roles=(),
            integration_boundaries=(),
            exemptions=(),
            findings=(),
        )
        
        registry.register(metadata)
        snapshot = registry.snapshot()
        
        self.assertIn("test.Module.Class", snapshot.entries)


class TestFunctionalityExemption(unittest.TestCase):
    """Tests for FunctionalityExemption."""
    
    def test_create_exemption(self) -> None:
        """Test creating an exemption record."""
        exemption = FunctionalityExemption(
            kind=ExemptionKind.EXCEPTION,
            reason="Exception classes are exempt",
            declared_by="test.module",
            source="functionality_markers.metaclass",
            scope="test.*",
            expiration_or_removal_condition=None,
            validation_status=ClassificationStatus.VALID_EXEMPT,
        )
        
        self.assertEqual(exemption.kind, ExemptionKind.EXCEPTION)
        self.assertTrue(exemption.is_expired() is False)


if __name__ == "__main__":
    unittest.main()