# Gordon Testing Infrastructure
# =============================
#
# Production-grade testing, validation, verification & quality assurance architecture.

"""
Gordon Testing Infrastructure

This package provides production-grade testing infrastructure for the Gordon
autonomous cognitive agent. It implements a comprehensive quality architecture
with:

- Canonical test coordinator for orchestration
- Validation managers per domain (source, config, schema, etc.)
- Verification managers for contracts, invariants, requirements
- Quality assurance with governance policies and gates
- Evidence management with traceability
- Scoped certification decisions

The testing architecture follows these principles:

1. Testing is evidence production, not just test execution
2. Validation ≠ Verification (different purposes)
3. Verification ≠ Certification (evidence vs decision)
4. Coverage ≠ Correctness (necessary but insufficient)
5. Passing tests ≠ Complete assurance
6. Determinism ≠ Sufficient coverage

All tests must be:
- Isolated (no shared mutable state)
- Reproducible (same inputs → same outputs)
- Deterministic (when environment is controlled)
- Owned (clear ownership for maintenance and triage)
- Evidence-backed (produce verifiable artifacts)

Test Taxonomy
-------------
Tests are classified by scope, purpose, and evidence type:

UNIT              - Test individual units in isolation
COMPONENT         - Test complete component interfaces  
CONTRACT          - Verify implementations satisfy protocols
INTEGRATION       - Test component boundaries and interactions
SYSTEM            - Test complete runtime behavior
END_TO_END        - Test user- or operator-visible workflows
ACCEPTANCE        - Verify against acceptance criteria
REGRESSION        - Prevent known defects from recurring
PROPERTY          - Verify properties across inputs (property-based)
METAMORPHIC       - Verify metamorphic relations between outputs
FUZZ              - Explore input space for boundary violations
MUTATION          - Test fault detection capability
PERFORMANCE       - Verify performance characteristics
LOAD              - Verify behavior under load
STRESS            # Test limits and failure modes
SOAK              # Test long-running stability
SECURITY          # Verify security boundaries
FAILURE           # Test failure handling and recovery
RECOVERY          # Test recovery from failures
CONCURRENCY       # Test concurrent execution correctness
DISTRIBUTED       # Test distributed behavior
COMPATIBILITY     # Test across versions/platforms
MIGRATION         # Test migration paths
INSTALLATION      # Test installation workflows
RELEASE           # Test release-candidate readiness
CERTIFICATION     # Verify certification requirements

Test Markers
------------
Markers categorize tests and enable selection/filtering:

unit, component, contract, integration, system, e2e,
acceptance, slow, gpu, network, distributed, fuzz,
mutation, performance, security, recovery, concurrency,
release, certification

Architecture Modules
--------------------
coordinators/     # Test orchestration (TestCoordinator)
validation/       # Validation authorities per domain
verification/     # Verification authorities
quality/          # Quality governance and policy
evidence/         # Evidence management and traceability
certification/    # Certification decisions and reports
suites/           # Test suite definitions
environments/     # Test environment specifications
fixtures/         # Fixture architecture and lifecycle
data/             # Test data generation and management
doubles/          # Mocks, fakes, stubs, simulators, emulators
fault_injection/  # Failure injection testing
reports/          # Reports and documentation

Usage Example
-------------
```python
from gordon_system.src.agent.components.core.testing import (
    TestCoordinator,
)

# Create test coordinator with environment config
coordinator = TestCoordinator(
    runtime_id="test_runtime_123",
    environment="LOCAL"
)

# Validate source code
validation_result = coordinator.run_validation()

# Run tests
results = coordinator.run_tests(
    selection={"include_markers": ["unit", "contract"]}
)

# Evaluate quality gates
gates = coordinator.evaluate_quality_gates()
```
"""

from .coordinators import TestCoordinator

# Authorities - Validation managers (placeholders for future implementation)
from .validation import (
    SourceValidator,
    ConfigValidator,
    ImportValidator,
    PackageValidator,
    APIDocValidator,
    DocumentationValidator,
    ArtifactValidator,
    ReleaseValidator,
)

# Verification authorities
from .verification import (
    VerificationManager,
    ContractVerifier,
    InvariantVerifier,
)

# Quality governance and policy
from .quality import (
    QualityAssuranceManager,
    QualityPolicy,
    QualityGate,
    QualityGateStatus,
)

# Evidence management
from .evidence import (
    EvidenceManager,
    EvidenceArtifact,
    EvidenceBundle,
)

# Certification decisions and reports
from .certification import (
    CertificationManager,
    CertificationRequest,
    CertificationDecision,
    CertificationReport,
)

# Markers
from .markers import (
    MarkerType,
    get_marker_definition,
    get_markers_by_category,
    is_execution_scope_marker,
    is_special_testing_marker,
    is_resource_marker,
)

__all__ = [
    # Main coordinators
    "TestCoordinator",
    
    # Authorities
    "SourceValidator",
    "ConfigValidator",
    "ImportValidator",
    "PackageValidator",
    "APIDocValidator",
    "DocumentationValidator",
    "ArtifactValidator",
    "ReleaseValidator",
    "VerificationManager",
    "ContractVerifier",
    "InvariantVerifier",
    "QualityAssuranceManager",
    "QualityPolicy",
    "QualityGate",
    "QualityGateStatus",
    "EvidenceManager",
    "EvidenceArtifact",
    "EvidenceBundle",
    "CertificationManager",
    "CertificationRequest",
    "CertificationDecision",
    "CertificationReport",
]