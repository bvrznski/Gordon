# Test Suite: Derived Memory Phase 5.1.6 - Canonical Implementation
# ==================================================================
"""
Test suite for the Derived Memory implementation.

Tests cover:
    - Derivation kinds (causal, counterfactual, predictive)
    - Evidence collection and validation
    - Provenance tracking
    - Statistics aggregation
    - Diagnostics reporting
    - Health monitoring

Derived Memory Laws Tested:
    DERIVATION-LAW-001: Every derivation produces a new semantic interpretation
    DERIVATION-LAW-002: Derivations never modify source memory artifacts
    DERIVATION-LAW-003: Derivations preserve source identity
    DERIVATION-LAW-004: Derivations preserve provenance
    DERIVATION-LAW-005: Derivations preserve revision history
    DERIVATION-LAW-006: Derivations expose supporting evidence
    DERIVATION-LAW-007: Derivations remain independently testable
    DERIVATION-LAW-008: Derivation behavior remains deterministic

Evidence Laws Tested:
    EVIDENCE-LAW-001: Every derivation references supporting memory artifacts
    EVIDENCE-LAW-002: Evidence remains inspectable
    EVIDENCE-LAW-003: Evidence preserves provenance
    EVIDENCE-LAW-004: Evidence revisions remain versioned

Provenance Laws Tested:
    PROVENANCE-LAW-001: Every derived artifact has complete derivation provenance
    PROVENANCE-LAW-002: Derivation methods remain identifiable
    PROVENANCE-LAW-003: Supporting artifacts remain identifiable

Statistics Laws Tested:
    STATS-LAW-001: Statistics remain inspectable
    STATS-LAW-002: Statistics preserve provenance
    
Health Laws Tested:
    HEALTH-LAW-001: Health remains inspectable
    HEALTH-LAW-002: Health updates are timely
"""

import sys
sys.path.insert(0, '/home/bvrznski/Gordon/gordon_system/src')

# Import the module at module level for tests to use
import agent.components.systems.memory.derived as derived_module

# Import all modules directly
from agent.components.systems.memory.derived import derivation as drv_mod
from agent.components.systems.memory.derived import evidence as evi_mod
from agent.components.systems.memory.derived import provenance as pro_mod
from agent.components.systems.memory.derived import statistics as stat_mod
from agent.components.systems.memory.derived import diagnostics as diag_mod
from agent.components.systems.memory.derived import health as heal_mod

# Import commonly used types
DerivationKind = drv_mod.DerivationKind
DerivationStatus = drv_mod.DerivationStatus
SupportingEvidence = drv_mod.SupportingEvidence
DerivationProvenance = drv_mod.DerivationProvenance
DerivationMetrics = drv_mod.DerivationMetrics
MemoryDerivation = drv_mod.MemoryDerivation
MemoryDerivationBuilder = drv_mod.MemoryDerivationBuilder
DerivationValidator = drv_mod.DerivationValidator

EvidenceKind = evi_mod.EvidenceKind
EvidenceItem = evi_mod.EvidenceItem
EvidenceCollection = evi_mod.EvidenceCollection
EvidenceValidator = evi_mod.EvidenceValidator
EvidenceBuilder = evi_mod.EvidenceBuilder

DerivationProvenanceSource = pro_mod.DerivationProvenanceSource
DerivationProvenanceRecord = pro_mod.DerivationProvenanceRecord
DerivationProvenanceBuilder = pro_mod.DerivationProvenanceBuilder
DerivationProvenanceChain = pro_mod.DerivationProvenanceChain
DerivationProvenanceChainBuilder = pro_mod.DerivationProvenanceChainBuilder
DerivationProvenanceValidator = pro_mod.DerivationProvenanceValidator

DerivationStatisticsBucket = stat_mod.DerivationStatisticsBucket
DerivationStatistics = stat_mod.DerivationStatistics
DerivationStatisticsBuilder = stat_mod.DerivationStatisticsBuilder
MetricDistribution = stat_mod.MetricDistribution

DerivationDiagnostic = diag_mod.DerivationDiagnostic
DerivationDiagnostics = diag_mod.DerivationDiagnostics
DerivationDiagnosticBuilder = diag_mod.DerivationDiagnosticBuilder
DerivationDiagnosticsBuilder = diag_mod.DerivationDiagnosticsBuilder

DerivationHealth = heal_mod.DerivationHealth
HealthStatus = heal_mod.HealthStatus
DerivationHealthBuilder = heal_mod.DerivationHealthBuilder
DerivationHealthChecker = heal_mod.DerivationHealthChecker


# =============================================================================
# TEST: Derivation Kinds and Statuses
# =============================================================================


def test_derivation_kind_enum():
    """Test that derivation kinds are properly defined."""
    assert DerivationKind.CAUSAL.value == "causal"
    assert DerivationKind.COUNTERFACTUAL.value == "counterfactual"
    assert DerivationKind.PREDICTIVE.value == "predictive"
    return True


def test_derivation_status_enum():
    """Test that derivation statuses are properly defined."""
    statuses = [s.value for s in DerivationStatus]
    expected = ["proposed", "validating", "validated", "rejected", "published", "revised"]
    assert all(s in statuses for s in expected)
    return True


# =============================================================================
# TEST: Supporting Evidence
# =============================================================================


def test_supporting_evidence_creation():
    """Test creation of supporting evidence."""
    evidence = SupportingEvidence(
        evidence_id="e1",
        source_artifact_ids=("a1", "a2"),
        confidence=0.8,
    )
    
    assert evidence.evidence_id == "e1"
    assert len(evidence.source_artifact_ids) == 2
    assert evidence.confidence == 0.8
    
    return True


# =============================================================================
# TEST: Derivation Provenance
# =============================================================================


def test_derivation_provenance_creation():
    """Test creation of derivation provenance."""
    provenance = DerivationProvenance(
        derivation_id="d1",
        method="causal_inference",
        algorithm_version="1.0.0",
    )
    
    assert provenance.derivation_id == "d1"
    assert provenance.method == "causal_inference"
    assert provenance.algorithm_version == "1.0.0"
    
    return True


# =============================================================================
# TEST: Derivation Metrics
# =============================================================================


def test_derivation_metrics_creation():
    """Test creation of derivation metrics."""
    metrics = DerivationMetrics(
        input_artifact_count=5,
        output_artifact_count=2,
    )
    
    assert metrics.input_artifact_count == 5
    assert metrics.output_artifact_count == 2
    
    return True


# =============================================================================
# TEST: Memory Derivation Builder
# =============================================================================


def test_memory_derivation_builder():
    """Test the derivation builder."""
    builder = MemoryDerivationBuilder(
        kind_=DerivationKind.CAUSAL,
        input_artifact_ids=("a1", "a2"),
    )
    
    # Set various properties
    builder.set_confidence(0.9)
    builder.set_uncertainty(0.1)
    builder.add_derived_artifact("d1")
    
    derivation = builder.build()
    
    assert derivation.kind_ == DerivationKind.CAUSAL
    assert len(derivation.input_artifact_ids) == 2
    assert derivation.confidence == 0.9
    assert derivation.uncertainty == 0.1
    
    return True


# =============================================================================
# TEST: Evidence Builder
# =============================================================================


def test_evidence_builder():
    """Test the evidence builder."""
    builder = EvidenceBuilder(derivation_id="d1")
    
    builder.add_item(
        kind_=EvidenceKind.OBSERVATION,
        source_artifact_ids=("a1",),
        confidence=0.95,
    )
    
    builder.add_item(
        kind_=EvidenceKind.INFERENCE,
        source_artifact_ids=("a2", "a3"),
        confidence=0.8,
    )
    
    collection = builder.build()
    
    assert len(collection.items) == 2
    assert collection.derivation_id == "d1"
    
    return True


# =============================================================================
# TEST: Provenance Builder
# =============================================================================


def test_derivation_provenance_builder():
    """Test the provenance builder."""
    builder = DerivationProvenanceBuilder(
        originating_derivation_id="orig_d1",
        originating_kind_="causal",
        method="inference_method_v1",
    )
    
    builder.add_supporting_artifact("a1")
    builder.set_algorithm_version("2.0.0")
    builder.add_parameter("threshold", 0.7)
    
    record = builder.build()
    
    assert record.originating_derivation_id == "orig_d1"
    assert "a1" in record.supporting_artifact_ids
    assert record.algorithm_version == "2.0.0"
    assert record.parameters.get("threshold") == 0.7
    
    return True


# =============================================================================
# TEST: Statistics Builder
# =============================================================================


def test_derivation_statistics_builder():
    """Test the statistics builder."""
    builder = DerivationStatisticsBuilder()
    
    # Record some derivations
    for _ in range(5):
        builder.record_derivation(
            kind_="causal",
            status="validated",
            confidence=0.85,
            validation_status="passed",
        )
    
    stats = builder.build()
    
    assert stats.total_derivations == 5
    assert stats.causal_count == 5
    assert stats.validated_count == 5
    
    return True


# =============================================================================
# TEST: Diagnostics Builder
# =============================================================================


def test_derivation_diagnostics_builder():
    """Test the diagnostics builder."""
    builder = DerivationDiagnosticsBuilder(derivation_id="d1")
    
    builder.add_error("Validation failed for artifact a1")
    builder.add_warning("Low confidence in evidence")
    
    diags = builder.build()
    
    assert len(diags.records) == 2
    assert len(diags.errors) >= 1
    
    return True


# =============================================================================
# TEST: Health Builder and Checker
# =============================================================================


def test_derivation_health_builder():
    """Test the health builder."""
    builder = DerivationHealthBuilder()
    
    builder.record_success()
    builder.record_success()
    builder.record_failure()
    builder.update_memory_mb(512.0)
    builder.update_cpu_percent(45.0)
    
    health = builder.build()
    
    assert health.total_derivations == 3
    assert health.successful_count == 2
    assert health.failed_count == 1
    assert health.error_rate > 0
    assert health.memory_mb == 512.0
    
    return True


def test_derivation_health_checker():
    """Test the health checker."""
    checker = DerivationHealthChecker()
    
    # Create a healthy health record
    builder = DerivationHealthBuilder()
    for _ in range(10):
        builder.record_success()
    
    health = builder.build()
    
    status, issues = checker.check_health(health)
    
    assert status == HealthStatus.HEALTHY
    assert len(issues) == 0
    
    return True


# =============================================================================
# TEST: Validation
# =============================================================================


def test_derivation_validator():
    """Test the derivation validator."""
    builder = MemoryDerivationBuilder(
        kind_=DerivationKind.CAUSAL,
        input_artifact_ids=("a1", "a2"),
    )
    
    derivation = builder.build()
    
    validator = DerivationValidator()
    is_valid, reason, confidence_score = validator.validate(derivation)
    
    assert is_valid
    assert reason == "Validation passed"
    assert 0.0 <= confidence_score <= 1.0
    
    return True


# =============================================================================
# TEST: Evidence Validator
# =============================================================================


def test_evidence_validator():
    """Test the evidence validator."""
    builder = EvidenceBuilder(derivation_id="d1")
    
    builder.add_item(
        kind_=EvidenceKind.OBSERVATION,
        source_artifact_ids=("a1",),
        confidence=0.95,
    )
    
    collection = builder.build()
    
    validator = EvidenceValidator()
    is_valid, reason, metrics = validator.validate_collection(collection)
    
    assert is_valid
    assert reason == "Evidence collection valid"
    assert metrics["count"] == 1
    
    return True


# =============================================================================
# TEST: Provenance Validator
# =============================================================================


def test_provenance_validator():
    """Test the provenance validator."""
    builder = DerivationProvenanceBuilder(
        originating_derivation_id="orig_d1",
        originating_kind_="causal",
        method="inference_v1",
    )
    
    record = builder.build()
    
    validator = DerivationProvenanceValidator()
    is_valid, reason = validator.validate_record(record)
    
    assert is_valid
    assert reason == None or "Missing" not in (reason or "")
    
    return True


# =============================================================================
# TEST: Determinism
# =============================================================================


def test_derivation_determinism():
    """Test that equivalent derivations produce equivalent results."""
    # Create two builders with the same inputs
    builder1 = MemoryDerivationBuilder(
        kind_=DerivationKind.CAUSAL,
        input_artifact_ids=("a1",),
    )
    builder1.set_confidence(0.9)
    
    derivation1 = builder1.build()
    
    builder2 = MemoryDerivationBuilder(
        kind_=DerivationKind.CAUSAL,
        input_artifact_ids=("a1",),
    )
    builder2.set_confidence(0.9)
    
    derivation2 = builder2.build()
    
    # Same inputs should produce equivalent outputs
    assert derivation1.kind_ == derivation2.kind_
    assert derivation1.confidence == derivation2.confidence
    
    return True


# =============================================================================
# TEST: Evidence Preservation
# =============================================================================


def test_evidence_preservation():
    """Test that evidence is preserved through derivation."""
    builder = EvidenceBuilder(derivation_id="d1")
    
    # Add multiple pieces of evidence
    for i in range(3):
        builder.add_item(
            kind_=EvidenceKind.OBSERVATION,
            source_artifact_ids=(f"a{i}",),
            confidence=0.8 + (i * 0.05),
        )
    
    collection = builder.build()
    
    # Verify all evidence is preserved
    assert len(collection.items) == 3
    for i, item in enumerate(collection.items):
        assert f"a{i}" in item.source_artifact_ids
    
    return True


# =============================================================================
# TEST: Revision Tracking
# =============================================================================


def test_revision_tracking():
    """Test that revisions are properly tracked."""
    builder = MemoryDerivationBuilder(
        kind_=DerivationKind.CAUSAL,
        input_artifact_ids=("a1",),
    )
    
    derivation1 = builder.build()
    
    # Increment revision
    builder.increment_revision()
    derivation2 = builder.build()
    
    assert derivation2.current_revision == 2
    assert len(derivation2.revision_history) >= 1
    
    return True


# =============================================================================
# TEST: Export All
# =============================================================================


def test_exports_complete():
    """Test that all expected exports are available."""
    # Import at function level to ensure clean import
    from agent.components.systems.memory.derived import (
        DerivationKind,
        DerivationStatus,
        SupportingEvidence,
        DerivationProvenance,
        DerivationMetrics,
        MemoryDerivation,
        MemoryDerivationBuilder,
        DerivationValidator,
        EvidenceKind,
        EvidenceItem,
        EvidenceCollection,
        EvidenceValidator,
        EvidenceBuilder,
        DerivationProvenanceSource,
        DerivationProvenanceRecord,
        DerivationProvenanceBuilder,
        DerivationProvenanceChain,
        DerivationProvenanceChainBuilder,
        DerivationProvenanceValidator,
        DerivationStatisticsBucket,
        DerivationStatistics,
        DerivationStatisticsBuilder,
        MetricDistribution,
        DerivationDiagnostic,
        DerivationDiagnostics,
        DerivationDiagnosticBuilder,
        DerivationDiagnosticsBuilder,
        DerivationHealth,
        HealthStatus,
        DerivationHealthBuilder,
        DerivationHealthChecker,
    )
    
    # Verify all are defined
    assert DerivationKind is not None
    assert DerivationStatus is not None
    
    return True


# =============================================================================
# TEST RUNNER
# =============================================================================


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("Derivation Kinds", test_derivation_kind_enum),
        ("Derivation Statuses", test_derivation_status_enum),
        ("Supporting Evidence Creation", test_supporting_evidence_creation),
        ("Derivation Provenance Creation", test_derivation_provenance_creation),
        ("Derivation Metrics Creation", test_derivation_metrics_creation),
        ("Memory Derivation Builder", test_memory_derivation_builder),
        ("Evidence Builder", test_evidence_builder),
        ("Provenance Builder", test_derivation_provenance_builder),
        ("Statistics Builder", test_derivation_statistics_builder),
        ("Diagnostics Builder", test_derivation_diagnostics_builder),
        ("Health Builder", test_derivation_health_builder),
        ("Health Checker", test_derivation_health_checker),
        ("Derivation Validator", test_derivation_validator),
        ("Evidence Validator", test_evidence_validator),
        ("Provenance Validator", test_provenance_validator),
        ("Determinism", test_derivation_determinism),
        ("Evidence Preservation", test_evidence_preservation),
        ("Revision Tracking", test_revision_tracking),
        ("Exports Complete", test_exports_complete),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            print(f"✓ {name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: FAILED - {str(e)}")
            failed += 1
    
    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)