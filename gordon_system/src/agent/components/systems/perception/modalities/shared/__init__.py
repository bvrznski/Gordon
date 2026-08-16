# Shared Perception Modality Contracts - Phase 5.2
# ================================================

"""
Shared contracts for Perception Modalities.

This package provides the common interfaces and data structures used across
all modalities (both sensory and digital).

Exported modules:
    modality.py     - Base PerceptionModality class and shared enums
    descriptor.py   - ModalityDescriptor for capability discovery
    capability.py   - Declarative capability declarations
    permission.py   - Authorization grants
    sandbox.py      - Sandbox profile definitions
    availability.py - State of readiness tracking
    lifecycle.py    - Lifecycle state transitions
    calibration.py  - Sensor alignment and calibration
    correlation.py  - Cross-modal evidence grouping
    validation.py   - Pre-activation verification
    health.py       - Operational health status
    diagnostics.py  - Runtime diagnostic information

All modalities implement the same external semantic boundary. Only internal
acquisition mechanisms differ.
"""

from .modality import (
    ModalityFamily,
    ModalityKind,
    ActivationMode,
    ModalityState,
    CalibrationState,
    TrustProfile,
    CalibrationMetadata,
    ModalityHealth,
    ModalityDiagnostics,
    ModalityMetrics,
    PerceptionModality,
    dataclass_replace,
)

from .descriptor import (
    ObservationKind,
    SignalKind,
    FeatureKind,
    PerceptKind,
    SandboxLevel,
    ActivationMode as DescriptorActivationMode,
    Compatibility,
    ModalityDescriptor,
)

from .capability import (
    CapabilityKind,
    CapabilityScope,
    ModalityCapability,
    CapabilitySet,
)

from .permission import (
    PermissionDecision,
    PermissionScope,
    ModalityPermission,
    PermissionSet,
    PermissionEvaluator,
)

from .sandbox import (
    SandboxProfile,
    VisibilityScope,
    SandboxConstraint,
    ModalitySandboxProfile,
    SandboxValidator,
)

from .availability import (
    AvailabilityState,
    AvailabilityReason,
    AvailabilityReport,
    AvailabilityChecker,
)

from .lifecycle import (
    LifecycleState,
    LifecycleEvent,
    LifecycleTransition,
    LifecycleHistory,
    LifecycleManager,
)

from .calibration import (
    CalibrationState,
    CalibrationMethod,
    CalibrationMetadata as CalibrationMetadataClass,
    CalibrationStateData,
    Calibrator,
)

from .correlation import (
    CorrelationType,
    CorrelationCandidate,
    CrossModalCorrelation,
    Correlator,
)

from .validation import (
    ValidationStatus,
    ValidationCheck,
    ValidationResult,
    Validator,
)

from .health import (
    ComponentHealth,
    ModalityHealth,
    HealthReporter,
)

from .diagnostics import (
    DiagnosticsMetrics,
    ModalityDiagnostics,
    DiagnosticLogger,
)

__all__: list[str] = [
    # modality.py exports
    "ModalityFamily",
    "ModalityKind",
    "ActivationMode",
    "ModalityState",
    "CalibrationState",
    "TrustProfile",
    "CalibrationMetadata",
    "ModalityHealth",
    "ModalityDiagnostics",
    "ModalityMetrics",
    "PerceptionModality",
    "dataclass_replace",
    
    # descriptor.py exports
    "ObservationKind",
    "SignalKind",
    "FeatureKind",
    "PerceptKind",
    "SandboxLevel",
    "DescriptorActivationMode",
    "Compatibility",
    "ModalityDescriptor",
    
    # capability.py exports
    "CapabilityKind",
    "CapabilityScope",
    "ModalityCapability",
    "CapabilitySet",
    
    # permission.py exports
    "PermissionDecision",
    "PermissionScope",
    "ModalityPermission",
    "PermissionSet",
    "PermissionEvaluator",
    
    # sandbox.py exports
    "SandboxProfile",
    "VisibilityScope",
    "SandboxConstraint",
    "ModalitySandboxProfile",
    "SandboxValidator",
    
    # availability.py exports
    "AvailabilityState",
    "AvailabilityReason",
    "AvailabilityReport",
    "AvailabilityChecker",
    
    # lifecycle.py exports
    "LifecycleState",
    "LifecycleEvent",
    "LifecycleTransition",
    "LifecycleHistory",
    "LifecycleManager",
    
    # calibration.py exports
    "CalibrationState",
    "CalibrationMethod",
    "CalibrationMetadataClass",
    "CalibrationStateData",
    "Calibrator",
    
    # correlation.py exports
    "CorrelationType",
    "CorrelationCandidate",
    "CrossModalCorrelation",
    "Correlator",
    
    # validation.py exports
    "ValidationStatus",
    "ValidationCheck",
    "ValidationResult",
    "Validator",
    
    # health.py exports
    "ComponentHealth",
    "ModalityHealth",
    "HealthReporter",
    
    # diagnostics.py exports
    "DiagnosticsMetrics",
    "ModalityDiagnostics",
    "DiagnosticLogger",
]