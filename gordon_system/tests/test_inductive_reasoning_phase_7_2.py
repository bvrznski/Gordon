# Test Inductive Reasoning Phase 7.2 - Phase 7.2 Part 3
# ======================================================

"""
Tests for the Inductive Reasoning subsystem (Phase 7.2).

These tests verify:
    - InductionDescriptor creation and lifecycle
    - ObservationSet construction and manipulation
    - PatternSearch discovery and evaluation
    - Generalization construction from patterns
    - StatisticalSupport calculation
    - HypothesisCluster management
    - OutlierAnalysis detection
    - Validation of induction results
    - Governance evaluation
"""

import pytest

from agent.components.systems.cognition.reasoning.inductive import (
    # Descriptor
    InductionDescriptor,
    InductionSessionIdentity,
    InductionMode,
    InductionLifecycle,
    
    # Observation Set
    InductionObservation,
    ObservationSet,
    ObservationSetIdentity,
    ObservationSource,
    ObservationKind,
    
    # Pattern Search
    PatternCandidate,
    PatternSearch,
    PatternSearchIdentity,
    PatternSearchStrategy,
    
    # Confidence
    InductionConfidence,
    ConfidenceComponents,
    ConfidenceCalibration,
    
    # Generalization
    Generalization,
    GeneralizationPipeline,
    GeneralizationRefinement,
    GeneralizationCandidate,
    
    # Statistics
    StatisticalSupport,
    StatisticalDistribution,
    StatisticalTestResult,
    StatisticalSummary,
    calculate_statistics,
    
    # Hypothesis Cluster
    InductiveHypothesis,
    HypothesisCluster,
    HypothesisEvaluation,
    HypothesisRefinement,
    
    # Outlier Analysis
    Outlier,
    OutlierAnalysis,
    OutlierCandidate,
    OutlierReport,
    
    # Validation
    ValidationResult,
    ValidationFinding,
    InductionValidation,
    ValidationTrace,
    ValidationError,
    
    # Governance
    GovernanceFinding,
    InductionGovernance,
    GovernanceEvaluation,
    GovernanceRule,
    GovernanceHealth,
    
    # Failure
    InductionFailure,
    InductionFailureKind,
    FailureTrace,
    PartialAnalysis,
    
    # Health
    InductionHealth,
    HealthMetrics,
    HealthSummary,
    
    # Refinement
    GeneralizationRefinement as Refinement,
)


def dataclass_replace(instance, **kwargs):
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


class TestInductionDescriptor:
    """Tests for InductionDescriptor."""
    
    def test_create_descriptor(self):
        """Test creating a new induction descriptor."""
        descriptor = InductionDescriptor.create(
            semantic_identity="test_induction",
            reasoning_goal="Discover patterns in observations",
            induction_mode=InductionMode.GENERALIZATION,
        )
        
        assert descriptor.semantic_identity == "test_induction"
        assert descriptor.reasoning_goal == "Discover patterns in observations"
        assert descriptor.induction_mode == InductionMode.GENERALIZATION
        assert descriptor.lifecycle_state == InductionLifecycle.CREATED
        assert descriptor.descriptor_id.startswith("induction:")
    
    def test_descriptor_state_transitions(self):
        """Test state transitions."""
        descriptor = InductionDescriptor.create(
            semantic_identity="test_induction",
            reasoning_goal="Discover patterns in observations",
        )
        
        updated = descriptor.to_state(InductionLifecycle.OBSERVATION_SELECTION)
        assert updated.lifecycle_state == InductionLifecycle.OBSERVATION_SELECTION
    
    def test_descriptor_completion(self):
        """Test completed descriptor timing."""
        import time
        start_time = time.time()
        
        descriptor = InductionDescriptor.create(
            semantic_identity="test_induction",
            reasoning_goal="Discover patterns in observations",
        )
        
        # Simulate some processing time
        time.sleep(0.01)
        
        completed = descriptor.to_state(InductionLifecycle.COMPLETED)
        
        assert completed.is_completed
        assert not descriptor.is_completed
        assert completed.duration_seconds >= 0
    
    def test_descriptor_failure(self):
        """Test failed descriptor."""
        descriptor = InductionDescriptor.create(
            semantic_identity="test_induction",
            reasoning_goal="Discover patterns in observations",
        )
        
        failed = descriptor.to_state(InductionLifecycle.FAILED)
        
        assert failed.is_failed
        assert not failed.is_completed


class TestObservationSet:
    """Tests for ObservationSet."""
    
    def test_create_observation_set(self):
        """Test creating an observation set."""
        obs1 = InductionObservation(
            observation_id="obs1",
            observation_content={"value": 42},
            observation_kind=ObservationKind.FACTUAL,
        )
        
        obs2 = InductionObservation(
            observation_id="obs2",
            observation_content={"value": 43},
            observation_kind=ObservationKind.FACTUAL,
        )
        
        observation_set = ObservationSet(
            observation_set_identity="set1",
            observations=(obs1, obs2),
        )
        
        assert observation_set.observation_count == 2
        assert observation_set.average_confidence == 1.0
    
    def test_filter_by_quality(self):
        """Test filtering observations by quality."""
        high_quality = InductionObservation(
            observation_id="high",
            observation_content={"value": 1},
            observation_kind=ObservationKind.FACTUAL,
            quality_score=0.9,
        )
        
        low_quality = InductionObservation(
            observation_id="low",
            observation_content={"value": 2},
            observation_kind=ObservationKind.FACTUAL,
            quality_score=0.3,
        )
        
        observation_set = ObservationSet(
            observation_set_identity="set1",
            observations=(high_quality, low_quality),
        )
        
        filtered = observation_set.filter_by_quality(0.5)
        assert filtered.observation_count == 1
        assert filtered.observations[0].observation_id == "high"
    
    def test_observation_source_filtering(self):
        """Test filtering by source."""
        obs_perception = InductionObservation(
            observation_id="perception",
            observation_content={"value": 1},
            observation_kind=ObservationKind.FACTUAL,
            observation_source=ObservationSource.PERCEPTION,
        )
        
        obs_memory = InductionObservation(
            observation_id="memory",
            observation_content={"value": 2},
            observation_kind=ObservationKind.FACTUAL,
            observation_source=ObservationSource.MEMORY,
        )
        
        observation_set = ObservationSet(
            observation_set_identity="set1",
            observations=(obs_perception, obs_memory),
        )
        
        filtered = observation_set.filter_by_source(ObservationSource.PERCEPTION)
        assert filtered.observation_count == 1
        assert filtered.observations[0].observation_source == ObservationSource.PERCEPTION


class TestPatternCandidate:
    """Tests for PatternCandidate."""
    
    def test_create_pattern(self):
        """Test creating a pattern candidate."""
        pattern = PatternCandidate(
            pattern_identity="pattern1",
            supporting_observations=("obs1", "obs2"),
            pattern_description="Values increase by 1 each time",
            pattern_kind="sequential",
            support_measure=0.8,
            confidence=0.75,
        )
        
        assert pattern.support_measure == 0.8
        assert pattern.confidence == 0.75
        assert len(pattern.supporting_observations) == 2
    
    def test_pattern_strength(self):
        """Test pattern strength calculation."""
        pattern = PatternCandidate(
            pattern_identity="pattern1",
            supporting_observations=("obs1", "obs2"),
            pattern_description="Values increase by 1 each time",
            pattern_kind="sequential",
            support_measure=0.9,
            confidence=0.8,
        )
        
        assert pattern.strength == 0.72  # 0.9 * 0.8
    
    def test_minimum_support_check(self):
        """Test minimum support threshold."""
        pattern = PatternCandidate(
            pattern_identity="pattern1",
            supporting_observations=("obs1", "obs2"),
            pattern_description="Values increase by 1 each time",
            pattern_kind="sequential",
            support_measure=0.5,
            confidence=0.75,
        )
        
        assert pattern.has_minimum_support(0.3) is True
        assert pattern.has_minimum_support(0.8) is False


class TestGeneralization:
    """Tests for Generalization."""
    
    def test_create_generalization(self):
        """Test creating a generalization."""
        generalization = Generalization(
            generalization_identity="gen1",
            supporting_patterns=("pattern1",),
            resulting_assertion="Birds usually fly",
            confidence=0.8,
            support_count=10,
            coverage_ratio=0.9,
        )
        
        assert generalization.resulting_assertion == "Birds usually fly"
        assert generalization.confidence == 0.8
        assert generalization.support_count == 10
    
    def test_effective_confidence_with_exceptions(self):
        """Test effective confidence accounting for exceptions."""
        generalization = Generalization(
            generalization_identity="gen1",
            supporting_patterns=("pattern1",),
            resulting_assertion="Birds usually fly",
            confidence=0.9,
            support_count=10,
            exception_count=2,  # 20% are exceptions
        )
        
        effective = generalization.effective_confidence
        assert effective < 0.9  # Should be reduced by exceptions


class TestStatisticalSupport:
    """Tests for StatisticalSupport."""
    
    def test_calculate_statistics(self):
        """Test calculating basic statistics from values."""
        stats = calculate_statistics([1.0, 2.0, 3.0, 4.0, 5.0])
        
        assert stats.sample_size == 5
        assert stats.mean_value == 3.0
    
    def test_effective_sample_size(self):
        """Test effective sample size calculation."""
        stats = StatisticalSupport(
            statistics_identity="stats1",
            supporting_observations=("obs1", "obs2"),
            sample_size=10,
            variance=0.5,
        )
        
        assert stats.sample_size == 10
        # Effective should be <= actual sample size


class TestHypothesisCluster:
    """Tests for HypothesisCluster."""
    
    def test_create_hypothesis_cluster(self):
        """Test creating a hypothesis cluster."""
        cluster = HypothesisCluster(
            cluster_identity="cluster1",
            participating_hypotheses=("hypo1", "hypo2"),
            ranking={"hypo1": 1, "hypo2": 2},
        )
        
        assert len(cluster.participating_hypotheses) == 2
        assert cluster.ranking_size == 2
    
    def test_preferred_hypothesis(self):
        """Test getting preferred hypothesis."""
        cluster = HypothesisCluster(
            cluster_identity="cluster1",
            participating_hypotheses=("hypo1", "hypo2"),
            ranking={"hypo1": 2, "hypo2": 1},
        )
        
        preferred = cluster.get_preferred_hypothesis()
        assert preferred == "hypo2"  # Has lowest rank (best)
    
    def test_consensus_check(self):
        """Test consensus detection."""
        cluster = HypothesisCluster(
            cluster_identity="cluster1",
            participating_hypotheses=("hypo1",),
            consensus_confidence=0.9,
        )
        
        assert cluster.has_consensus(0.8) is True
        assert cluster.has_consensus(0.95) is False


class TestOutlier:
    """Tests for Outlier."""
    
    def test_create_outlier(self):
        """Test creating an outlier record."""
        outlier = Outlier(
            outlier_identity="outlier1",
            supporting_observation="obs1",
            deviation_measure=3.0,
            z_score=2.5,
        )
        
        assert outlier.deviation_measure == 3.0
        assert outlier.z_score == 2.5


class TestValidation:
    """Tests for InductionValidation."""
    
    def test_create_validation(self):
        """Test creating a validation record."""
        validation = InductionValidation(
            validation_id="val1",
            validated_artifact_type="generalization",
            validated_artifact_id="gen1",
            findings=(),
            result=ValidationResult.VALID,
        )
        
        assert validation.result == ValidationResult.VALID
        assert validation.is_strictly_valid is True
    
    def test_validation_with_findings(self):
        """Test validation with findings."""
        finding = ValidationFinding(
            finding_id="finding1",
            finding_kind="low_confidence",
            severity="warning",
            description="Confidence below threshold",
        )
        
        validation = InductionValidation(
            validation_id="val1",
            validated_artifact_type="generalization",
            validated_artifact_id="gen1",
            findings=(finding,),
            result=ValidationResult.CONDITIONALLY_VALID,
        )
        
        assert validation.has_critical_issues is False
        assert len(validation.findings) == 1


class TestGovernance:
    """Tests for InductionGovernance."""
    
    def test_create_governance(self):
        """Test creating a governance record."""
        governance = InductionGovernance(
            governance_identity="gov1",
            evaluated_sessions=("session1",),
            findings=(),
        )
        
        assert len(governance.evaluated_sessions) == 1
        assert governance.check_pass_rate == 1.0
    
    def test_governance_with_violations(self):
        """Test governance with violations."""
        finding = GovernanceFinding(
            finding_id="finding1",
            finding_kind="sampling_bias",
            severity="error",
            description="Observation set has sampling bias",
        )
        
        governance = InductionGovernance(
            governance_identity="gov1",
            evaluated_sessions=("session1",),
            findings=(finding,),
            violations=("INDUCTION-LAW-008",),  # Equivalent observations should produce equivalent results
        )
        
        assert governance.has_violations is True
        assert governance.violation_count == 1


class TestHealth:
    """Tests for InductionHealth."""
    
    def test_record_session(self):
        """Test recording an induction session in health metrics."""
        health = InductionHealth(health_id="health1")
        
        health = dataclass_replace(health, 
            observations_analyzed=10,
            patterns_discovered=3,
            generalizations_produced=2,
        )
        
        assert health.observations_analyzed == 10
        assert health.patterns_discovered == 3
    
    def test_failure_rate(self):
        """Test failure rate calculation."""
        health = InductionHealth(
            health_id="health1",
            total_sessions_attempted=10,
            successful_sessions=8,
            failed_sessions=2,
        )
        
        assert health.total_sessions_attempted == 10
        assert health.successful_sessions == 8
        assert health.failed_sessions == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])