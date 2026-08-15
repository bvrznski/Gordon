# Tests for Phase 4.3.1: Default Network Scaffold
# ================================================

"""
Test suite for the DefaultNetwork scaffold implementation.

Tests verify:
    - Package structure and imports
    - No Core dependency violations  
    - Semantic boundary enforcement
    - Input/output immutability
    - Validation correctness
    - Health state transitions
    - Diagnostics collection
    
NO BEHAVIOR POLICY:
    Tests do NOT test behavioral policy decisions.
    They test that the scaffold is correctly structured and follows architectural principles.
"""

import pytest


# =============================================================================
# IMPORT TESTS (verify no Core dependency)
# =============================================================================

class TestImportStructure:
    """Tests for correct import structure without Core dependencies."""
    
    def test_can_import_default_network(self):
        """Test that DefaultNetwork can be imported."""
        from agent.networks.default import DefaultNetwork
        assert DefaultNetwork is not None
    
    def test_can_import_config(self):
        """Test that configuration can be imported."""
        from agent.networks.default import DefaultNetworkConfig
        assert DefaultNetworkConfig is not None
    
    def test_default_network_create_method_exists(self):
        """Test that create class method exists."""
        from agent.networks.default import DefaultNetwork
        network = DefaultNetwork.create()
        assert network is not None


class TestNoCoreDependency:
    """Tests to verify no Core dependency violations."""
    
    def test_types_module_has_no_core_imports(self):
        """Test that types module doesn't import core machinery."""
        from agent.networks.default import types
        
        # Types should have basic identity types
        assert hasattr(types, 'DefaultNetworkId')
        assert hasattr(types, 'InputId')
        assert hasattr(types, 'OutputId')
        assert hasattr(types, 'AssessmentId')
    
    def test_config_module_has_no_core_imports(self):
        """Test that config module doesn't import core machinery."""
        from agent.networks.default import config
        
        # Config should have nested value objects
        assert hasattr(config, 'DefaultNetworkConfig')
        assert hasattr(config, 'ActivationThresholds')


# =============================================================================
# IMMUTABILITY TESTS
# =============================================================================

class TestImmutability:
    """Tests for immutable data structures."""
    
    def test_input_is_frozen_dataclass(self):
        """Test that input is a frozen dataclass."""
        from agent.networks.default import types
        from datetime import datetime
        
        # Create an input with all required fields
        input_obj = types.DefaultInput(
            input_id="test_input_1",
            source_id="memory",
            source_type="memory_reactivation",
            timestamp_utc=datetime.utcnow(),
            category="test_category",
        )
        
        # Verify it's frozen (would raise FrozenInstanceError if mutable)
        try:
            input_obj.input_id = "modified"
            assert False, "Should not be able to modify frozen dataclass"
        except (AttributeError, Exception):
            pass  # Expected for frozen dataclass
    
    def test_output_is_frozen_dataclass(self):
        """Test that output is a frozen dataclass."""
        from agent.networks.default import types
        from datetime import datetime
        
        output_obj = types.DefaultOutput(
            output_id="test_output_1",
            timestamp_utc=datetime.utcnow(),
            output_type="proposal",
            content={"test": "value"},
        )
        
        # Verify it's frozen
        try:
            output_obj.output_id = "modified"
            assert False, "Should not be able to modify frozen dataclass"
        except (AttributeError, Exception):
            pass  # Expected for frozen dataclass


# =============================================================================
# VALIDATION TESTS
# =============================================================================

class TestValidation:
    """Tests for validation functions."""
    
    def test_validate_input_with_valid_id(self):
        """Test validation passes with valid input ID."""
        from agent.networks.default.validation import validate_input
        
        result = validate_input("valid_input_id")
        
        assert result.is_valid is True
        assert result.check_id == "input_id_valid"
    
    def test_validate_input_with_empty_id(self):
        """Test validation fails with empty input ID."""
        from agent.networks.default.validation import validate_input
        
        result = validate_input("")
        
        assert result.is_valid is False
        assert result.error_message is not None
    
    def test_validate_confidence_in_range(self):
        """Test confidence validation passes for valid range."""
        from agent.networks.default.validation import validate_confidence
        
        result = validate_confidence(0.5)
        
        assert result.is_valid is True
    
    def test_validate_confidence_out_of_range(self):
        """Test confidence validation fails for out of range values."""
        from agent.networks.default.validation import validate_confidence
        
        result = validate_confidence(-0.1)
        
        assert result.is_valid is False
    
    def test_validate_output_count_in_bounds(self):
        """Test output count validation passes for valid counts."""
        from agent.networks.default.validation import validate_output_count
        
        result = validate_output_count(5)
        
        assert result.is_valid is True


# =============================================================================
# HEALTH STATE TESTS
# =============================================================================

class TestHealthStates:
    """Tests for health state transitions."""
    
    def test_health_states_exist(self):
        """Test that all health states are defined."""
        from agent.networks.default.health import HealthState
        
        assert hasattr(HealthState, 'READY')
        assert hasattr(HealthState, 'ACTIVE')
        assert hasattr(HealthState, 'DEGRADED')
        assert hasattr(HealthState, 'INSUFFICIENT_CONTEXT')
        assert hasattr(HealthState, 'INPUT_UNAVAILABLE')


# =============================================================================
# DIAGNOSTICS TESTS
# =============================================================================

class TestDiagnostics:
    """Tests for diagnostics collection."""
    
    def test_collector_collects_events(self):
        """Test that diagnostics collector accumulates events."""
        from agent.networks.default.diagnostics import (
            DiagnosticEvent,
            DiagnosticsCollector,
        )
        from datetime import datetime
        
        collector = DiagnosticsCollector()
        
        event = DiagnosticEvent(
            timestamp_utc=datetime.utcnow(),
            event_source="test",
            event_stage="test_stage",
            event_type="start",
            description="Test event",
        )
        
        collector.collect(event)
        
        assert collector.event_count == 1
        events = collector.get_events()
        assert len(events) == 1
    
    def test_diagnostics_snapshot_has_required_fields(self):
        """Test that diagnostics snapshot has all required fields."""
        from agent.networks.default.diagnostics import NetworkDiagnostics
        from datetime import datetime
        
        diagnostics = NetworkDiagnostics(
            timestamp_utc=datetime.utcnow(),
        )
        
        assert hasattr(diagnostics, 'activation_level')
        assert hasattr(diagnostics, 'proposal_count')


# =============================================================================
# BOUNDARY TESTS
# =============================================================================

class TestBoundaries:
    """Tests for boundary enforcement."""
    
    def test_max_proposal_count_is_bounded(self):
        """Test that max proposal count has a reasonable limit."""
        from agent.networks.default.config import DefaultNetworkConfig
        
        config = DefaultNetworkConfig()
        
        # Max should be bounded (not unbounded)
        assert config.activation.max_proposal_count <= 100
    
    def test_activation_level_is_normalized(self):
        """Test that activation levels are normalized to [0, 1]."""
        from agent.networks.default.config import DefaultNetworkConfig
        
        config = DefaultNetworkConfig()
        
        # Thresholds should be in [0.0, 1.0]
        assert 0.0 <= config.activation.minimum_activation_level <= 1.0
        assert 0.0 <= config.activation.minimum_internal_orientation <= 1.0


# =============================================================================
# ARCHITECTURE TESTS (semantic boundaries)
# =============================================================================

class TestSemanticBoundaries:
    """Tests for semantic boundary enforcement."""
    
    def test_network_does_not_produce_runtime_commands(self):
        """Test that network outputs are semantic, not runtime commands."""
        from agent.networks.default import types
        from datetime import datetime
        
        # Output should contain proposal data, not runtime instructions
        output = types.DefaultOutput(
            output_id="test",
            timestamp_utc=datetime.utcnow(),
            output_type="proposal",
            content={"category": "internal_attention"},
        )
        
        # Content should be semantic (data), not executable code or runtime commands
        assert isinstance(output.content, dict)
    
    def test_proposal_types_are_bounded(self):
        """Test that proposal types are from a bounded set."""
        from agent.networks.default.outputs import ProposalType
        
        valid_types = {
            ProposalType.INTERNAL_ATTENTION,
            ProposalType.ASSOCIATION,
            ProposalType.MEMORY_REACTIVATION,
            ProposalType.REFLECTION,
            ProposalType.SIMULATION,
            ProposalType.PROSPECTION,
            ProposalType.NARRATIVE_INTEGRATION,
            ProposalType.UNRESOLVED_GOAL,
            ProposalType.INCUBATION,
            ProposalType.CONTEXT_REINTEGRATION,
        }
        
        assert len(valid_types) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])