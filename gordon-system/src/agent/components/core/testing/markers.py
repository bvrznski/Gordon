# Test Markers - Testing Infrastructure
# ====================================

"""
Test marker definitions for categorization and selection.

Markers categorize tests and enable:
- Selection/filtering of test suites
- Priority-based execution
- Environment-specific execution
- Quality gate association

Marker Categories
-----------------
Execution Control
    unit, component, contract, integration, system, e2e,
    acceptance, regression

Performance
    slow, fast

Environment/Resource
    gpu, network, distributed, offline

Specialized Testing
    fuzz, mutation, performance, security, recovery, concurrency

Release
    release, certification

Example Usage
-------------
```python
from gordon_system.src.agent.components.core.testing.markers import MarkerType

# In test file:
@pytest.mark.unit
def test_basic_addition():
    ...

@pytest.mark.slow
def test_large_dataset_processing():
    ...

# Select by marker:
coordinator.run_tests(selection={"include_markers": ["contract"]})

# Exclude tests:
coordinator.run_tests(selection={"exclude_markers": ["slow", "gpu"]})
```
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from enum import Enum, auto
import uuid


class MarkerType(Enum):
    """Types of test markers."""
    
    # Execution scope markers
    UNIT = "unit"  # Individual unit tests
    COMPONENT = "component"  # Component-level tests
    CONTRACT = "contract"  # Contract verification tests
    INTEGRATION = "integration"  # Integration boundary tests
    SYSTEM = "system"  # System-level tests
    END_TO_END = "end_to_end"  # End-to-end workflow tests
    ACCEPTANCE = "acceptance"  # Acceptance criteria tests
    REGRESSION = "regression"  # Regression prevention tests
    
    # Test purpose markers
    PROPERTY = "property"  # Property-based testing
    METAMORPHIC = "metamorphic"  # Metamorphic relation tests
    FUZZ = "fuzz"  # Fuzzing tests
    MUTATION = "mutation"  # Mutation testing
    PERFORMANCE = "performance"  # Performance benchmarks
    SECURITY = "security"  # Security boundary tests
    
    # Behavior markers
    FAILURE = "failure"  # Failure handling tests
    RECOVERY = "recovery"  # Recovery behavior tests
    CONCURRENCY = "concurrency"  # Concurrency tests
    DISTRIBUTED = "distributed"  # Distributed system tests
    COMPATIBILITY = "compatibility"  # Compatibility tests
    
    # Resource/environment markers
    SLOW = "slow"  # Slow-running tests
    FAST = "fast"  # Fast-running tests
    GPU = "gpu"  # Requires GPU
    NETWORK = "network"  # Requires network access
    OFFLINE = "offline"  # Works offline only
    
    # Release markers
    RELEASE = "release"  # Release-candidate tests
    CERTIFICATION = "certification"  # Certification requirement tests


@dataclass(frozen=True)
class MarkerDefinition:
    """Definition of a marker with metadata."""
    
    marker_type: MarkerType
    name: str
    description: str
    category: str  # execution, resource, special, release
    recommended_gates: List[str] = field(default_factory=list)


# Define all markers
MARKER_DEFS: Dict[MarkerType, MarkerDefinition] = {
    MarkerType.UNIT: MarkerDefinition(
        marker_type=MarkerType.UNIT,
        name="Unit Test",
        description="Tests individual units in isolation",
        category="execution",
        recommended_gates=["UNIT_TESTS_PASS"],
    ),
    MarkerType.COMPONENT: MarkerDefinition(
        marker_type=MarkerType.COMPONENT,
        name="Component Test",
        description="Tests complete component interfaces",
        category="execution",
        recommended_gates=["CONTRACT_TESTS_PASS"],
    ),
    MarkerType.CONTRACT: MarkerDefinition(
        marker_type=MarkerType.CONTRACT,
        name="Contract Test",
        description="Verifies implementations satisfy protocols",
        category="execution",
        recommended_gates=["CONTRACT_TESTS_PASS", "UNIT_TESTS_PASS"],
    ),
    MarkerType.INTEGRATION: MarkerDefinition(
        marker_type=MarkerType.INTEGRATION,
        name="Integration Test",
        description="Tests component boundaries and interactions",
        category="execution",
        recommended_gates=["INTEGRATION_TESTS_PASS"],
    ),
    MarkerType.SYSTEM: MarkerDefinition(
        marker_type=MarkerType.SYSTEM,
        name="System Test",
        description="Tests complete runtime behavior",
        category="execution",
        recommended_gates=["SYSTEM_TESTS_PASS"],
    ),
    MarkerType.END_TO_END: MarkerDefinition(
        marker_type=MarkerType.END_TO_END,
        name="End-to-End Test",
        description="Tests user- or operator-visible workflows",
        category="execution",
        recommended_gates=["ACCEPTANCE_TESTS_PASS"],
    ),
    MarkerType.ACCEPTANCE: MarkerDefinition(
        marker_type=MarkerType.ACCEPTANCE,
        name="Acceptance Test",
        description="Verifies against acceptance criteria",
        category="execution",
        recommended_gates=["ACCEPTANCE_TESTS_PASS", "EVIDENCE_COMPLETE"],
    ),
    MarkerType.REGRESSION: MarkerDefinition(
        marker_type=MarkerType.REGRESSION,
        name="Regression Test",
        description="Prevents known defects from recurring",
        category="execution",
        recommended_gates=["UNIT_TESTS_PASS"],
    ),
    MarkerType.PROPERTY: MarkerDefinition(
        marker_type=MarkerType.PROPERTY,
        name="Property-Based Test",
        description="Verifies properties across inputs",
        category="special",
        recommended_gates=[],
    ),
    MarkerType.METAMORPHIC: MarkerDefinition(
        marker_type=MarkerType.METAMORPHIC,
        name="Metamorphic Test",
        description="Verifies metamorphic relations between outputs",
        category="special",
        recommended_gates=[],
    ),
    MarkerType.FUZZ: MarkerDefinition(
        marker_type=MarkerType.FUZZ,
        name="Fuzz Test",
        description="Explores input space for boundary violations",
        category="special",
        recommended_gates=[],
    ),
    MarkerType.MUTATION: MarkerDefinition(
        marker_type=MarkerType.MUTATION,
        name="Mutation Test",
        description="Tests fault detection capability",
        category="special",
        recommended_gates=["MUTATION_THRESHOLD_MET"],
    ),
    MarkerType.PERFORMANCE: MarkerDefinition(
        marker_type=MarkerType.PERFORMANCE,
        name="Performance Test",
        description="Verifies performance characteristics",
        category="special",
        recommended_gates=[],
    ),
    MarkerType.SECURITY: MarkerDefinition(
        marker_type=MarkerType.SECURITY,
        name="Security Test",
        description="Verifies security boundaries",
        category="special",
        recommended_gates=["SECURITY_VALIDATION_PASSES"],
    ),
    MarkerType.FAILURE: MarkerDefinition(
        marker_type=MarkerType.FAILURE,
        name="Failure Test",
        description="Tests failure handling",
        category="behavior",
        recommended_gates=[],
    ),
    MarkerType.RECOVERY: MarkerDefinition(
        marker_type=MarkerType.RECOVERY,
        name="Recovery Test",
        description="Tests recovery from failures",
        category="behavior",
        recommended_gates=[],
    ),
    MarkerType.CONCURRENCY: MarkerDefinition(
        marker_type=MarkerType.CONCURRENCY,
        name="Concurrency Test",
        description="Tests concurrent execution correctness",
        category="behavior",
        recommended_gates=[],
    ),
    MarkerType.DISTRIBUTED: MarkerDefinition(
        marker_type=MarkerType.DISTRIBUTED,
        name="Distributed Test",
        description="Tests distributed system behavior",
        category="behavior",
        recommended_gates=[],
    ),
    MarkerType.COMPATIBILITY: MarkerDefinition(
        marker_type=MarkerType.COMPATIBILITY,
        name="Compatibility Test",
        description="Tests across versions/platforms",
        category="execution",
        recommended_gates=[],
    ),
    MarkerType.SLOW: MarkerDefinition(
        marker_type=MarkerType.SLOW,
        name="Slow Test",
        description="Slow-running tests (excluded from fast runs)",
        category="resource",
        recommended_gates=[],
    ),
    MarkerType.FAST: MarkerDefinition(
        marker_type=MarkerType.FAST,
        name="Fast Test",
        description="Fast-running tests",
        category="resource",
        recommended_gates=[],
    ),
    MarkerType.GPU: MarkerDefinition(
        marker_type=MarkerType.GPU,
        name="GPU Test",
        description="Requires GPU access",
        category="resource",
        recommended_gates=[],
    ),
    MarkerType.NETWORK: MarkerDefinition(
        marker_type=MarkerType.NETWORK,
        name="Network Test",
        description="Requires network access",
        category="resource",
        recommended_gates=[],
    ),
    MarkerType.OFFLINE: MarkerDefinition(
        marker_type=MarkerType.OFFLINE,
        name="Offline Test",
        description="Works offline only (no external dependencies)",
        category="resource",
        recommended_gates=[],
    ),
    MarkerType.RELEASE: MarkerDefinition(
        marker_type=MarkerType.RELEASE,
        name="Release Test",
        description="Release-candidate validation tests",
        category="release",
        recommended_gates=["EVIDENCE_COMPLETE"],
    ),
    MarkerType.CERTIFICATION: MarkerDefinition(
        marker_type=MarkerType.CERTIFICATION,
        name="Certification Test",
        description="Certification requirement verification",
        category="release",
        recommended_gates=["CERTIFICATION_TESTS_PASS", "EVIDENCE_COMPLETE"],
    ),
}


def get_marker_definition(marker_type: MarkerType) -> MarkerDefinition:
    """Get the definition for a marker type."""
    return MARKER_DEFS[marker_type]


def get_markers_by_category(category: str) -> List[MarkerType]:
    """Get all markers in a category."""
    result = []
    for m in MARKER_DEFS.values():
        if m.category == category:
            result.append(m.marker_type)
    return result


def get_markers_for_gate(gate_id: str) -> List[MarkerType]:
    """Get markers associated with a quality gate."""
    result = []
    for defn in MARKER_DEFS.values():
        if gate_id in defn.recommended_gates:
            result.append(defn.marker_type)
    return result


def is_execution_scope_marker(marker_type: MarkerType) -> bool:
    """Check if marker is an execution scope category."""
    return marker_type in {
        MarkerType.UNIT,
        MarkerType.COMPONENT,
        MarkerType.CONTRACT,
        MarkerType.INTEGRATION,
        MarkerType.SYSTEM,
        MarkerType.END_TO_END,
        MarkerType.ACCEPTANCE,
        MarkerType.REGRESSION,
    }


def is_special_testing_marker(marker_type: MarkerType) -> bool:
    """Check if marker is a specialized testing type."""
    return marker_type in {
        MarkerType.PROPERTY,
        MarkerType.METAMORPHIC,
        MarkerType.FUZZ,
        MarkerType.MUTATION,
        MarkerType.PERFORMANCE,
        MarkerType.SECURITY,
        MarkerType.FAILURE,
        MarkerType.RECOVERY,
        MarkerType.CONCURRENCY,
        MarkerType.DISTRIBUTED,
    }


def is_resource_marker(marker_type: MarkerType) -> bool:
    """Check if marker indicates resource requirements."""
    return marker_type in {
        MarkerType.SLOW,
        MarkerType.FAST,
        MarkerType.GPU,
        MarkerType.NETWORK,
        MarkerType.OFFLINE,
    }


# Export all public API
__all__ = [
    "MarkerType",
    "MarkerDefinition",
    "MARKER_DEFS",
    "get_marker_definition",
    "get_markers_by_category",
    "get_markers_for_gate",
    "is_execution_scope_marker",
    "is_special_testing_marker",
    "is_resource_marker",
]
