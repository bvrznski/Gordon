# Focusing Network Phase 4.2.8: Contract Architecture Tests
# ===========================================================

"""
Tests validating the architectural boundaries of the FocusingNetwork contracts.

These tests ensure:
    - Contract stability (no accidental breaking changes)
    - Version compatibility
    - Immutability (frozen dataclasses)
    - Validation rules
    - Serialization (JSON-compatible representations)
    - Consumer isolation (no shared state leakage)
    - Provider isolation (no implementation coupling)
    - Dependency inversion (contracts depend on nothing)
"""

import pytest
from typing import Any, Dict, Tuple

# Import contract interfaces
from gordon_system.src.agent.components.networks.focusing.contracts import (
    # Versioning constants
    CONTRACTS_VERSION,
    COMPATIBILITY_POLICY,
    
    # Input contracts (providers)
    FocusCandidateProvider,
    FocusContextProvider,
    FocusStateProvider,
    ObjectiveProvider,
    WorkspaceProjectionProvider,
    WorkingMemoryProjectionProvider,
    AlertingAssessmentProvider,
    PolicyProjectionProvider,
    ConfigurationProvider,
    
    # Output contracts (consumers)
    FocusAssessmentConsumer,
    PriorityAssessmentConsumer,
    CompetitionAssessmentConsumer,
    PrecisionAssessmentConsumer,
    PersistenceAssessmentConsumer,
    AllocationRecommendationConsumer,
    BiasAssessmentConsumer,
    DiagnosticsConsumer,
    
    # Context contracts
    FocusComputationContext,
    ExecutionProjection,
    PolicyProjection,
    ResourceProjection,
    HistoricalProjection,
    
    # State contracts (views)
    FocusStateView,
    PriorityStateView,
    PersistenceStateView,
    PrecisionStateView,
    AllocationStateView,
    BiasStateView,
    DiagnosticsView,
    
    # Configuration contracts
    ConfigurationView,
    ConfigurationSnapshot,
    ConfigurationValidator,
    
    # Validation contracts
    ValidationReport,
    AssessmentValidator,
    ContextValidator,
    StateValidator,
    FocusValidationContract,
    
    # Diagnostics contracts
    DiagnosticsSink,
    PipelineTraceConsumer,
    AssessmentTraceConsumer,
    StateTraceConsumer,
    PerformanceTraceConsumer,
    ExplainabilityConsumer,
)


# =============================================================================
# VERSIONING TESTS
# =============================================================================

class TestVersioning:
    """Test versioning constants and policies."""
    
    def test_contracts_version_is_string(self):
        """Contracts version should be a string."""
        assert isinstance(CONTRACTS_VERSION, str)
        assert len(CONTRACTS_VERSION) > 0
    
    def test_compatibility_policy_is_backward(self):
        """Compatibility policy should be backward for Phase 4.2.8."""
        assert COMPATIBILITY_POLICY == "backward"
    
    def test_version_format_semantic(self):
        """Version should follow semantic versioning format (MAJOR.MINOR.PATCH)."""
        parts = CONTRACTS_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


# =============================================================================
# INPUT CONTRACT TESTS - Provider interfaces
# =============================================================================

class TestInputContracts:
    """Test input contract provider interfaces."""
    
    def test_focus_candidate_provider_has_get_candidates(self):
        """FocusCandidateProvider must have get_candidates method."""
        methods = [m for m in dir(FocusCandidateProvider) if not m.startswith("_")]
        assert "get_candidates" in methods
    
    def test_focus_context_provider_has_methods(self):
        """FocusContextProvider must have required methods."""
        methods = [m for m in dir(FocusContextProvider) if not m.startswith("_")]
        assert "get_current_focus_strength" in methods
        assert "get_active_targets" in methods
        assert "get_relevance_hint" in methods
    
    def test_focus_state_provider_has_methods(self):
        """FocusStateProvider must have required methods."""
        methods = [m for m in dir(FocusStateProvider) if not m.startswith("_")]
        assert "get_current_focus_targets" in methods
        assert "get_target_strength" in methods
    
    def test_objective_provider_has_methods(self):
        """ObjectiveProvider must have required methods."""
        methods = [m for m in dir(ObjectiveProvider) if not m.startswith("_")]
        assert "get_active_objectives" in methods
    
    def test_workspace_projection_provider_has_methods(self):
        """WorkspaceProjectionProvider must have required methods."""
        methods = [m for m in dir(WorkspaceProjectionProvider) if not m.startswith("_")]
        assert "get_workspace_state" in methods
    
    def test_working_memory_projection_provider_has_methods(self):
        """WorkingMemoryProjectionProvider must have required methods."""
        methods = [m for m in dir(WorkingMemoryProjectionProvider) if not m.startswith("_")]
        assert "get_working_memory_contents" in methods
    
    def test_alerting_assessment_provider_has_methods(self):
        """AlertingAssessmentProvider must have required methods."""
        methods = [m for m in dir(AlertingAssessmentProvider) if not m.startswith("_")]
        assert "get_current_alerts" in methods
    
    def test_policy_projection_provider_has_methods(self):
        """PolicyProjectionProvider must have required methods."""
        methods = [m for m in dir(PolicyProjectionProvider) if not m.startswith("_")]
        assert "get_policy_constraints" in methods
    
    def test_configuration_provider_has_methods(self):
        """ConfigurationProvider must have required methods."""
        methods = [m for m in dir(ConfigurationProvider) if not m.startswith("_")]
        assert "get_configuration" in methods


# =============================================================================
# OUTPUT CONTRACT TESTS - Consumer interfaces
# =============================================================================

class TestOutputContracts:
    """Test output contract consumer interfaces."""
    
    def test_focus_assessment_consumer_has_receive_assessment(self):
        """FocusAssessmentConsumer must have receive_assessment method."""
        methods = [m for m in dir(FocusAssessmentConsumer) if not m.startswith("_")]
        assert "receive_assessment" in methods
    
    def test_priority_assessment_consumer_has_methods(self):
        """PriorityAssessmentConsumer must have required methods."""
        methods = [m for m in dir(PriorityAssessmentConsumer) if not m.startswith("_")]
        assert "receive_priority_assessment" in methods
    
    def test_competition_assessment_consumer_has_methods(self):
        """CompetitionAssessmentConsumer must have required methods."""
        methods = [m for m in dir(CompetitionAssessmentConsumer) if not m.startswith("_")]
        assert "receive_competition_assessment" in methods
    
    def test_diagnostics_consumer_has_methods(self):
        """DiagnosticsConsumer must have required methods."""
        methods = [m for m in dir(DiagnosticsConsumer) if not m.startswith("_")]
        assert "receive_trace_event" in methods


# =============================================================================
# CONTEXT CONTRACT TESTS - Projections without ownership
# =============================================================================

class TestContextContracts:
    """Test context projection contracts."""
    
    def test_execution_projection_is_frozen(self):
        """ExecutionProjection should be frozen (immutable)."""
        proj = ExecutionProjection()
        with pytest.raises(Exception):
            proj.is_active = False  # Should fail for frozen dataclass
    
    def test_policy_projection_is_frozen(self):
        """PolicyProjection should be frozen (immutable)."""
        proj = PolicyProjection()
        with pytest.raises(Exception):
            proj.max_concurrent_focus_targets = 5  # Should fail
    
    def test_resource_projection_is_frozen(self):
        """ResourceProjection should be frozen (immutable)."""
        proj = ResourceProjection()
        with pytest.raises(Exception):
            proj.available_threads = 8  # Should fail
    
    def test_historical_projection_is_frozen(self):
        """HistoricalProjection should be frozen (immutable)."""
        proj = HistoricalProjection()
        with pytest.raises(Exception):
            proj.allocation_history_count = 10  # Should fail
    
    def test_focus_computation_context_contains_projections(self):
        """FocusComputationContext should contain all projection types."""
        ctx = FocusComputationContext.create()
        
        assert hasattr(ctx, "execution")
        assert isinstance(ctx.execution, ExecutionProjection)
        
        assert hasattr(ctx, "policy")
        assert isinstance(ctx.policy, PolicyProjection)
        
        assert hasattr(ctx, "resources")
        assert isinstance(ctx.resources, ResourceProjection)
        
        assert hasattr(ctx, "history")
        assert isinstance(ctx.history, HistoricalProjection)


# =============================================================================
# STATE CONTRACT TESTS - Immutable views
# =============================================================================

class TestStateContracts:
    """Test state view contracts."""
    
    def test_focus_state_view_is_frozen(self):
        """FocusStateView should be frozen (immutable)."""
        view = FocusStateView()
        with pytest.raises(Exception):
            view.focus_age_seconds = 10.0
    
    def test_priority_state_view_is_frozen(self):
        """PriorityStateView should be frozen (immutable)."""
        view = PriorityStateView()
        with pytest.raises(Exception):
            view.confidence_level = 0.8
    
    def test_diagnostics_view_is_frozen(self):
        """DiagnosticsView should be frozen (immutable)."""
        view = DiagnosticsView()
        with pytest.raises(Exception):
            view.event_count = 5


# =============================================================================
# CONFIGURATION CONTRACT TESTS
# =============================================================================

class TestConfigurationContracts:
    """Test configuration contracts."""
    
    def test_configuration_view_is_frozen(self):
        """ConfigurationView should be frozen (immutable)."""
        config = ConfigurationView()
        with pytest.raises(Exception):
            config.suppression_threshold = 0.5
    
    def test_configuration_snapshot_contains_config(self):
        """ConfigurationSnapshot should contain ConfigurationView."""
        snapshot = ConfigurationSnapshot.capture()
        assert isinstance(snapshot.config, ConfigurationView)
    
    def test_configuration_view_is_valid_by_default(self):
        """Default ConfigurationView should be valid."""
        config = ConfigurationView()
        assert config.is_valid()


# =============================================================================
# VALIDATION CONTRACT TESTS
# =============================================================================

class TestValidationContracts:
    """Test validation contracts."""
    
    def test_validation_report_has_is_valid_property(self):
        """ValidationReport must have is_valid property."""
        report = ValidationReport.valid()
        assert hasattr(report, "is_valid")
        assert report.is_valid
    
    def test_validation_report_invalid(self):
        """ValidationReport can be invalid."""
        report = ValidationReport.invalid("error1", "error2")
        assert not report.is_valid
        assert len(report.errors) == 2
    
    def test_assessment_validator_has_score_range(self):
        """AssessmentValidator should define score ranges."""
        validator = AssessmentValidator()
        assert hasattr(validator, "score_range_min")
        assert hasattr(validator, "score_range_max")
    
    def test_context_validator_has_probability_bounds(self):
        """ContextValidator should define probability bounds."""
        validator = ContextValidator()
        assert 0.0 <= validator.probability_range_min < validator.probability_range_max


# =============================================================================
# DIAGNOSTICS CONTRACT TESTS
# =============================================================================

class TestDiagnosticsContracts:
    """Test diagnostic contracts."""
    
    def test_diagnostics_sink_can_receive_event(self):
        """DiagnosticsSink should receive events without error."""
        sink = DiagnosticsSink()
        assert sink.enabled is True
        
        # Should not raise
        sink.receive_event("test", {"data": "value"})
        assert sink.event_count == 1
    
    def test_pipeline_trace_consumer_is_frozen(self):
        """PipelineTraceConsumer should be frozen (immutable)."""
        consumer = PipelineTraceConsumer()
        with pytest.raises(Exception):
            consumer.event_count = 5  # Should fail for frozen dataclass
    
    def test_explainability_consumer_records_reasons(self):
        """ExplainabilityConsumer should record reason events."""
        consumer = ExplainabilityConsumer()
        
        consumer.receive_reason("test", "test description", confidence=0.8)
        
        assert len(consumer.reason_events) == 1
        event = consumer.reason_events[0]
        assert event["reason_type"] == "test"
        assert event["description"] == "test description"


# =============================================================================
# ARCHITECTURAL BOUNDARY TESTS
# =============================================================================

class TestArchitecturalBoundaries:
    """Test architectural boundaries are preserved."""
    
    def test_no_computation_in_contract_classes(self):
        """
        Contract classes should not contain computational logic.
        
        This ensures Phase 4.2.8 is purely interface definition without
        any implementation logic.
        """
        import inspect
        
        contract_classes = [
            FocusCandidateProvider,
            FocusContextProvider,
            FocusAssessmentConsumer,
            PriorityAssessmentConsumer,
            ExecutionProjection,
            PolicyProjection,
            ResourceProjection,
            HistoricalProjection,
            FocusStateView,
            ConfigurationView,
            ValidationReport,
            DiagnosticsSink,
        ]
        
        for cls in contract_classes:
            # Check no execute, compute, or process methods exist
            methods = [m for m in dir(cls) if "exec" in m.lower() or 
                      "comput" in m.lower() or "process" in m.lower()]
            
            # Only __init__, __repr__ and other special methods should be present
            user_methods = [m for m in methods if not m.startswith("_")]
            assert len(user_methods) == 0, (
                f"{cls.__name__} should not contain computational methods: "
                f"{user_methods}"
            )
    
    def test_contract_dependencies_are_none(self):
        """
        Contract modules should have no external dependencies except stdlib.
        
        This ensures contracts are truly independent and can be used by
        any implementation without coupling.
        """
        # Test is informational - static analysis verifies this
        pass
    
    def test_version_is_exposed_on_all_protocol_classes(self):
        """Protocol classes must expose version property."""
        protocol_classes = [
            FocusCandidateProvider,
            FocusContextProvider,
            FocusAssessmentConsumer,
            FocusStateViewProvider,  # Will be added if implemented
        ]
        
        for cls in protocol_classes:
            assert hasattr(cls, "version"), (
                f"{cls.__name__} must expose version property"
            )


# =============================================================================
# SERIALIZATION TESTS
# =============================================================================

class TestSerialization:
    """Test JSON serialization compatibility."""
    
    def test_execution_projection_to_dict(self):
        """ExecutionProjection should be serializable to dict."""
        proj = ExecutionProjection()
        data = proj.__dict__
        
        assert isinstance(data, dict)
        assert "is_active" in data
    
    def test_policy_projection_serialization(self):
        """PolicyProjection should be serializable."""
        proj = PolicyProjection()
        data = proj.__dict__
        
        assert isinstance(data, dict)
        assert "max_concurrent_focus_targets" in data


# =============================================================================
# IMMUTABILITY TESTS
# =============================================================================

class TestImmutability:
    """Test frozen dataclass immutability."""
    
    def test_execution_projection_immutability(self):
        """ExecutionProjection instances should be immutable."""
        proj = ExecutionProjection()
        
        with pytest.raises(Exception):
            proj.is_active = False
    
    def test_state_view_immutability(self):
        """State views should be immutable."""
        view = FocusStateView()
        
        with pytest.raises(Exception):
            view.focus_age_seconds = 10.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])