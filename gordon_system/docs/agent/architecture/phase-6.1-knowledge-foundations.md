# Phase 6.1: Knowledge Foundations

## Overview

Phase 6.1 establishes the seven foundational semantic primitives that form the basis of semantic organization in Gordon's cognitive system.

## Semantic Primitives

### 1. Identity - Unique Semantic Identity

**Purpose:** Provides stable, unique identifiers for knowledge artifacts independent of their content.

**Key Properties:**
- Immutable once assigned
- Distinct from content (content can change without changing identity)
- Enables revision tracking across content changes
- Supports namespace qualification

**Components:**
- `SemanticIdentity` - Core identity representation
- `IdentitySource` - Origin mechanisms (system, external, user-defined, derived)
- `IdentityResolution` - Conflict resolution strategies (first-wins, highest-authority, merge, conflict)
- `IdentityTracker` - Monitors identities across revisions
- `IdentityValidator` - Ensures uniqueness and consistency

### 2. Provenance - Origin Tracking and History

**Purpose:** Records complete lifecycle of semantic artifacts including when, where, who, and how changes occurred.

**Key Properties:**
- Complete auditability
- Revision history preservation
- Source accountability
- Trust assessment based on origin

**Components:**
- `ProvenanceEvent` - Individual change records with actor, action, timestamp, context
- `ProvenanceTrail` - Complete event chain from creation to current state
- `ProvenanceValidator` - Ensures integrity and chronological ordering

### 3. Validity - Truth and Logical Soundness Assessment

**Purpose:** Evaluates whether claims are logically correct and supported by evidence.

**Key Properties:**
- Distinct from truth (valid logic can be applied to false premises)
- Supports multiple assessment states
- Evidence-based evaluation
- Reasoning explanation

**Components:**
- `ValidityState` - Assessment outcomes (valid, invalid, unknown, suspicious, partially_valid, conditionally_valid)
- `EvidenceKind` - Categories of supporting evidence (empirical, logical, consistency, authority, experimental, analytical)
- `ValidityEvidence` - Supporting evidence for validity claims
- `ValidityAssessment` - Complete evaluation result with confidence and reasoning
- `ValidityEngine` - Automated assessment using evidence analysis

### 4. Confidence - Semantic Certainty Metrics

**Purpose:** Measures how strongly the system holds a belief based on evidence.

**Key Properties:**
- Range: 0.0 (no confidence) to 1.0 (full confidence)
- Distinct from perception and memory confidence
- Aggregateable across multiple sources
- Supports revision tracking

**Components:**
- `ConfidenceSource` - Origin mechanisms (evidence support, reasoning validity, consistency, consensus)
- `SemanticConfidence` - Core metric representation with source tracking
- `ConfidenceAggregator` - Combines multiple confidence metrics

### 5. Uncertainty - Semantic Ambiguity Metrics

**Purpose:** Measures semantic ambiguity and limits of knowledge.

**Key Properties:**
- Range: 0.0 (no uncertainty) to 1.0 (complete uncertainty)
- Distinct from perception and memory uncertainty
- Measures incomplete information, not observational noise
- Aggregateable across sources

**Components:**
- `UncertaintySource` - Origin mechanisms (classification ambiguity, relation ambiguity, model incompleteness, evidence gap)
- `SemanticUncertainty` - Core metric representation with source tracking
- `UncertaintyAggregator` - Combines multiple uncertainty metrics

### 6. Revision - Change Management and Versioning

**Purpose:** Tracks all changes to knowledge artifacts over time.

**Key Properties:**
- Complete version history
- Enables rollback operations
- Supports comparison between revisions
- Automatic revision numbering

**Components:**
- `RevisionEventType` - Types of changes (initial, update, refinement, correction, superseded, merge, split)
- `RevisionEvent` - Individual change records
- `RevisionHistory` - Complete version sequence
- `RevisionManager` - Operations on revision history (compare, rollback)

### 7. Scope - Semantic Domain Boundaries

**Purpose:** Defines where and when knowledge is applicable.

**Key Properties:**
- Domain-specific applicability
- Boundary definitions with inclusivity flags
- Value-range filtering within domains
- Exclusion specifications

**Components:**
- `ScopeDomain` - Primary discourse domains (physical, social, logical, emotional, temporal, causal)
- `ScopeBoundary` - Numeric boundaries for domain values
- `SemanticScope` - Complete scope definition
- `ScopeValidator` - Ensures consistency and completeness

### 8. Authority - Source Reliability and Weight

**Purpose:** Measures source reliability to weight evidence appropriately.

**Key Properties:**
- Hierarchical classification of source quality
- Domain expertise tracking
- Assessment confidence
- Evidence-based evaluation

**Components:**
- `AuthorityLevel` - Reliability classifications (primary_evidence, peer_reviewed, expert_consensus, established_fact, secondary_source, anonymous, unverified)
- `AuthoritySource` - Source identity and metadata
- `AuthorityAssessment` - Evaluation of source reliability with confidence
- `AuthorityValidator` - Ensures assessment consistency

## Implementation

All semantic primitives support:
- Serialization to/from dictionary format
- Immutable dataclass representations (frozen=True)
- Validation methods
- Complete provenance tracking through their operations

## Integration Points

These foundations integrate with:
- **Perception** - Grounded evidence sources
- **Memory** - Historical evidence sources
- **Knowledge-Perception Grounding** - Present grounding references
- **Knowledge-Memory Integration** - Historical grounding references
- **Shared Knowledge Artifacts** (Phase 5.4) - Assertions, propositions, concepts, relations, models, beliefs

## Next Document

**Phase 6.2: Representations**

Defines semantic representation mechanisms:
- Symbolic representations (required)
- Vector representations (optional)
- Latent representations (optional)
- Hybrid representations
- Mappings and alignment between representations

## End of Phase 6.1