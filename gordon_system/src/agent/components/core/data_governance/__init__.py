# Core Data Governance Infrastructure
# ====================================

"""
Core information governance system for Gordon autonomous cognitive agent.

Provides canonical authorities for:

* Information Lifecycle Management - tracking from creation to deletion
* Provenance & Lineage - immutable origin tracking and transformation history
* Classification & Privacy - sensitivity levels and access control
* Metadata Management - schema validation and enrichment
* Retention, Archival & Disposal - lifecycle policies with evidence preservation

Governance Model
----------------

The information governance architecture follows the canonical lifecycle:

    Information Created → Classification → Ownership Assignment → 
    Metadata Enrichment → Privacy Evaluation → Provenance Registration → 
    Storage → Sharing/Processing → Retention → Archival → 
    Deletion/Destruction

Each information object has:
    - owner: Entity responsible for the information
    - classification: Sensitivity level (PUBLIC, INTERNAL, RESTRICTED, etc.)
    - lifecycle_state: Current state in the lifecycle
    - provenance: Immutable origin and transformation history
    - metadata: Schema-validated properties
    - retention_policy: When and how it should be retained/deleted

Principles
----------

PHASE 3.7.21 REMEDIATION:
- One semantic owner per domain (no duplicates)
- Records own their semantics (lifecycle, classification, provenance)
- Provenance embedded in EventEnvelope, FailureRecord, LifecycleTransitionRecord
- Privacy controls localized (redaction, filtering at point of use)
- No central governance orchestrator

Authorities
-----------

InformationRegistry - Canonical registry for information records:
    - Information registration and cataloging
    - Owner assignment and transfer
    - Information retrieval by criteria

LifecycleCoordinator - Lifecycle state transitions:
    - State validation before transition
    - Event logging for transitions
    - Idempotent operations where appropriate

ClassificationAuthority - Classification management:
    - Classification rules and evaluation
    - Sensitivity level assignment
    - Classification evidence and audit trail

PrivacyControls - Data-oriented privacy enforcement:
    - Personal data identification
    - Field-level redaction and filtering
    - Privacy diagnostics and reporting

RetentionCoordinator - Retention policy management:
    - Retention schedule definition
    - Expiration evaluation
    - Review cycle management

ArchiveManager - Archival lifecycle management:
    - Archive policy configuration
    - Archive validation
    - Recovery from archive

DisposalAuthority - Secure deletion:
    - Deletion scheduling
    - Secure destruction methods
    - Disposal evidence preservation

Domains
-------

Information is governed across these domains:

* CONFIGURATION - System configuration and settings
* RUNTIME_STATE - Runtime execution state
* WORKING_MEMORY - Short-term working memory
* LONG_TERM_MEMORY - Persistent episodic/semantic memory
* KNOWLEDGE - Agent knowledge base
* TELEMETRY - Performance metrics and telemetry
* AUDIT - Audit trails and compliance records
* CHECKPOINTS - Checkpoint snapshots for recovery
* ARTIFACTS - Generated artifacts (outputs, results)
* LOGS - Log entries and event streams
* MODELS - ML models and parameters
* DATASETS - Training and inference datasets
* PLUGINS - Plugin configurations
* PROVIDERS - Provider configurations
* USER_INFORMATION - User-provided information
* GENERATED_OUTPUTS - Agent-generated outputs

Usage Example
-------------

    from gordon.system.agent.components.core.data_governance import (
        InformationRecord,
        EventEnvelope,
        FailureRecord,
        ClassificationLevel,
        LifecycleState,
        OwnerType
    )

    # Records own their semantics directly
    record = InformationRecord(
        information_id="data-123",
        content_hash="abc123def456",
        owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
        classification=ClassificationLevel.INTERNAL,
        lifecycle_state=LifecycleState.ACTIVE,
    )

Phase 3.7.21: Data Governance, Privacy, Provenance & Information Lifecycle.
"""

from .models import (
    # Classification
    ClassificationLevel,
    ClassificationEvidence,
    ClassificationDecision,
    
    # Ownership
    OwnerType,
    OwnerIdentity,
    OwnershipRecord,
    
    # Lifecycle
    LifecycleState,
    LifecycleEvent,
    LifecycleTransition,
    
    # Metadata
    MetadataSchema,
    MetadataVersion,
    MetadataSnapshot,
    MetadataRecord,
    
    # Provenance
    ProvenanceRecord,
    ProvenanceNode,
    ProvenanceEdge,
    LineageReport,
    ProvenanceSnapshot,
    
    # Privacy
    PrivacyLevel,
    PersonalDataIndicator,
    PrivacyPolicy,
    PrivacyDecision,
    
    # Retention
    RetentionPolicy,
    RetentionSchedule,
    ExpirationStatus,
    
    # Archive
    ArchiveRequest,
    ArchiveDecision,
    ArchiveRecord,
    ArchiveEvidence,
    
    # Disposal
    DisposalRequest,
    DisposalMethod,
    DisposalRecord,
    DisposalEvidence,
)

from .models import InformationRecord

from .information import InformationRegistry
from .lifecycle import LifecycleCoordinator
from .classification import ClassificationAuthority
from .privacy import PrivacyControls
from .retention import RetentionCoordinator
from .archive import ArchiveManager
from .disposal import DisposalAuthority

__all__ = [
    # Models - Records
    "InformationRecord",

    # Authorities (one per domain, no central orchestrator)
    "InformationRegistry",
    "LifecycleCoordinator",
    "ClassificationAuthority",
    "PrivacyControls",
    "RetentionCoordinator",
    "ArchiveManager",
    "DisposalAuthority",
    
    # Models - Classification
    "ClassificationLevel",
    "ClassificationEvidence",
    "ClassificationDecision",
    
    # Models - Ownership
    "OwnerType",
    "OwnerIdentity",
    "OwnershipRecord",
    
    # Models - Lifecycle
    "LifecycleState",
    "LifecycleEvent",
    "LifecycleTransition",
    
    # Models - Metadata
    "MetadataSchema",
    "MetadataVersion",
    "MetadataSnapshot",
    "MetadataRecord",
    
    # Models - Provenance
    "ProvenanceRecord",
    "ProvenanceNode",
    "ProvenanceEdge",
    "LineageReport",
    "ProvenanceSnapshot",
    
    # Models - Privacy
    "PrivacyLevel",
    "PersonalDataIndicator",
    "PrivacyPolicy",
    "PrivacyDecision",
    
    # Models - Retention
    "RetentionPolicy",
    "RetentionSchedule",
    "ExpirationStatus",
    
    # Models - Archive
    "ArchiveRequest",
    "ArchiveDecision",
    "ArchiveRecord",
    "ArchiveEvidence",
    
    # Models - Disposal
    "DisposalRequest",
    "DisposalMethod",
    "DisposalRecord",
    "DisposalEvidence",
]