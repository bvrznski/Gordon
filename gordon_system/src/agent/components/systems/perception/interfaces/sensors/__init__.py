# Sensors Interface Module - Phase 5.2.5
# =======================================

"""
Sensors Interface: The inbound interface for sensor evidence acquisition.

Package:
    perception/interfaces/sensors/

The Sensors Interface connects acquisition adapters and sensing infrastructure
to Perception Modalities. It is an inbound Interface that does not expose
Perception to cognition.

Purpose:
    - Sensor discovery
    - Adapter discovery  
    - Sensor capability discovery
    - Sensor availability
    - Sensor calibration references
    - Acquisition-session establishment
    - Signal publication
    - Observation publication
    - Source-health publication
    - Event-loss reporting
    - Source disconnection
    - Sensor shutdown reporting

Does NOT perform:
    - Percept construction
    - Feature extraction
    - Semantic classification
    - Modality Integration
    - Memory admission
    - Action control
"""

from .descriptor import (
    PerceptionSensorDescriptor,
    SensorKind,
)

from .acquisition import (
    SensorAcquisitionRequest,
    SensorAcquisitionResponse,
)

from .publication import (
    SensorEvidencePublication,
    EvidenceKind,
)

__all__ = [
    # Descriptors
    "PerceptionSensorDescriptor",
    "SensorKind",
    
    # Acquisition
    "SensorAcquisitionRequest", 
    "SensorAcquisitionResponse",
    
    # Publication
    "SensorEvidencePublication",
    "EvidenceKind",
]