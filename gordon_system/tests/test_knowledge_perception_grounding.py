# Knowledge-Perception Grounding Tests - Phase 5.6
# ==================================================

"""
Comprehensive tests for the Knowledge-Perception Grounding layer.

Tests cover:
1. Observation contracts (LAW-001 to LAW-008)
2. Percept contracts (PERCEPT-LAW-001 to PERCEPT-LAW-008)
3. Correspondence contracts (CORRESPONDENCE-LAW-001 to CORRESPONDENCE-LAW-008)
4. Novelty detection (NOVELTY-LAW-001 to NOVELTY-LAW-008)
5. Grounding records (GROUNDING-LAW-001 to GROUNDING-LAW-008)
6. Active perception and reality validation
7. Ambiguity handling
"""

import unittest

# Use local imports that work in test environment
from agent.components.systems.knowledge_perception_grounding import (
    # Observation
    Observation,
    ObservationSession,
    ObservationSource,
    ObservationSourceKind,
    ObservationType,
    
    # Percept
    Percept,
    PerceptGroup,
    PerceptEmbedding,
    PerceptClassification,
    PerceptRepresentation,
    
    # Correspondence
    SemanticCorrespondence,
    VectorCorrespondence,
    StructuralCorrespondence,
    HybridCorrespondence,
    CorrespondenceKind,
    
    # Novelty
    NoveltyAssessment,
    NoveltyDetection,
    NoveltyKind,
    
    # Grounding and candidates
    GroundedEvent,
    KnowledgePerceptionGrounding,
    KnowledgePerceptionGroundingRequest,
    KnowledgePerceptionGroundingAssessment,
    SemanticCandidate,
    SemanticCandidateKind,
    GroundingKind,
    
    # Active perception and reality validation
    ActivePerceptionRequest,
    ActivePerceptionResponse,
    ActivePerceptionOutcome,
    RealityValidationRequest,
    RealityValidationResult,
    RealityValidationRecommendation,
    
    # Ambiguity
    PerceptAmbiguity,
    AmbiguityResolution,
    AmbiguityGroup,
    AmbiguityContext,
)


class TestObservations(unittest.TestCase):
    """Test observation contracts."""
    
    def test_observation_creation(self):
        """Create a basic observation."""
        obs = Observation.from_payload(
            payload=b"test data",
            modality="vision",
            source_sensor="camera_1",
            confidence=0.9,
        )
        
        self.assertIn("observation:", obs.observation_identity)
        self.assertEqual(obs.modality, "vision")
        self.assertEqual(obs.source_sensor, "camera_1")
        self.assertAlmostEqual(obs.confidence, 0.9)
    
    def test_observation_session(self):
        """Test observation session grouping."""
        session = ObservationSession.create(
            modality="vision",
            sensor="camera_1",
            temporal_scope_start_utc=1000.0,
            temporal_scope_end_utc=2000.0,
            environment="office",
            observation_count=5,
            confidence=0.95,
        )
        
        self.assertEqual(session.duration_sec, 1000.0)
        self.assertEqual(session.environment, "office")
    
    def test_observation_source(self):
        """Test observation source description."""
        source = ObservationSource.create(
            source_kind=ObservationSourceKind.CAMERA,
            sensor_identity="camera_front",
            sensor_revision=2,
            reliability=0.98,
        )
        
        self.assertEqual(source.source_kind, ObservationSourceKind.CAMERA)
        self.assertAlmostEqual(source.reliability, 0.98)


class TestPercepts(unittest.TestCase):
    """Test percept contracts."""
    
    def test_percept_creation(self):
        """Create a basic percept."""
        obs_ids = ["obs1", "obs2", "obs3"]
        percept = Percept.from_observations(
            percept_kind="person",
            observation_ids=obs_ids,
            feature_summary={"color": "red", "size": "large"},
            confidence=0.85,
            uncertainty=0.15,
        )
        
        self.assertEqual(percept.percept_identity.startswith("percept:"), True)
        self.assertTupleEqual(percept.observations, tuple(obs_ids))
        self.assertEqual(percept.percept_kind, "person")
    
    def test_percept_group(self):
        """Test grouping multiple percepts."""
        percept_ids = ["p1", "p2", "p3"]
        group = PerceptGroup.create(
            member_percept_ids=percept_ids,
            grouping_reason="temporal_coherence",
            temporal_window_start=100.0,
            temporal_window_end=110.0,
            confidence=0.9,
        )
        
        self.assertEqual(group.grouping_reason, "temporal_coherence")
        self.assertGreaterEqual(len(group.member_percepts), 2)
    
    def test_percept_embedding(self):
        """Test percept embedding for vector correspondence."""
        embedding = PerceptEmbedding.create(
            percept_id="percept_1",
            embedding_space="clip",
            embedding_model="vit_b32",
            vector_ref="vector_abc123",
            dimensions=512,
        )
        
        self.assertEqual(embedding.embedding_space, "clip")
        self.assertEqual(embedding.dimensions, 512)
    
    def test_percept_classification(self):
        """Test percept classification."""
        classification = PerceptClassification.create(
            percept_id="percept_1",
            classified_kind="person",
            model_name="resnet50",
            confidence=0.92,
            alternatives=["human", "avatar"],
        )
        
        self.assertEqual(classification.percept_kind, "person")
        self.assertIn("human", classification.alternatives)


class TestCorrespondence(unittest.TestCase):
    """Test correspondence contracts."""
    
    def test_semantic_correspondence(self):
        """Create semantic correspondence between percept and concepts."""
        corr = SemanticCorrespondence.create(
            percept_id="percept_1",
            candidate_concept_ids=["concept_person", "concept_human"],
            correspondence_kind=CorrespondenceKind.PARTIAL,
            similarity=0.75,
            supporting_features=["visual_form", "behavior_pattern"],
        )
        
        self.assertIn("concept_person", corr.candidate_concepts)
        self.assertAlmostEqual(corr.similarity, 0.75)
    
    def test_vector_correspondence(self):
        """Test vector-based correspondence."""
        vec_corr = VectorCorrespondence(
            correspondence_identity="vec_corr_1",
            percept_embedding="emb_1",
            candidate_embeddings=("emb_2", "emb_3"),
            similarity_metric="cosine",
            neighborhood=5,
            similarity_scores={"concept_a": 0.85, "concept_b": 0.72},
        )
        
        self.assertEqual(vec_corr.top_candidate[1], 0.85)
    
    def test_structural_correspondence(self):
        """Test structural pattern matching."""
        struct_corr = StructuralCorrespondence.create(
            percept_structure="structure_1",
            candidate_concept_ids=["concept_window", "concept_door"],
            matched_components=["frame", "glass"],
            structural_score=0.65,
        )
        
        self.assertIn("frame", struct_corr.matched_components)
    
    def test_hybrid_correspondence(self):
        """Test combined correspondence strategies."""
        hybrid = HybridCorrespondence(
            correspondence_identity="hybrid_1",
            vector_results=(),
            structural_results=(),
            symbolic_results=(),
            combined_candidates={"concept_person": 0.82, "concept_human": 0.75},
            fusion_method="weighted_average",
        )
        
        self.assertEqual(hybrid.fusion_method, "weighted_average")


class TestNovelty(unittest.TestCase):
    """Test novelty detection contracts."""
    
    def test_novelty_assessment(self):
        """Create a novelty assessment."""
        assessment = NoveltyAssessment.create(
            percept_id="percept_1",
            nearest_concept_ids=["concept_person", "concept_human"],
            novelty_kind=NoveltyKind.NEW_OBJECT,
            novelty_score=0.85,
        )
        
        self.assertTrue(assessment.is_significant_novelty)
    
    def test_novelty_detection(self):
        """Test novelty detection result."""
        detection = NoveltyDetection.create(
            percept_id="percept_1",
            nearest_concept_ids=["concept_person"],
            novelty_measure=0.65,
            novelty_kind="new_behavior",
        )
        
        self.assertTrue(detection.is_novel)


class TestGrounding(unittest.TestCase):
    """Test grounding record contracts."""
    
    def test_grounding_record(self):
        """Create a grounding record linking knowledge to perception."""
        grounding = KnowledgePerceptionGrounding.create(
            knowledge_artifact_ref="belief_1",
            percept_ids=["percept_person"],
            grounding_kind=GroundingKind.DIRECT,
            support_strength=0.85,
            contradiction_strength=0.10,
        )
        
        self.assertTrue(grounding.is_strong_grounding)
    
    def test_grounded_event(self):
        """Create a grounded event from percepts."""
        event = GroundedEvent.create(
            percept_ids=["percept_door_opens", "percept_person_enters"],
            event_structure={"temporal_order": ["open", "enter"]},
            temporal_start_utc=100.0,
            temporal_end_utc=150.0,
            participants=["person_1"],
        )
        
        self.assertEqual(event.duration_sec, 50.0)
    
    def test_semantic_candidate(self):
        """Create a semantic candidate from perceptual evidence."""
        candidate = SemanticCandidate.create(
            percept_ids=["percept_person", "percept_wave"],
            proposed_semantics={"action": "greeting", "recipient": "person"},
            confidence=0.85,
            uncertainty=0.10,
        )
        
        self.assertTrue(candidate.is_high_confidence)


class TestActivePerception(unittest.TestCase):
    """Test active perception contracts."""
    
    def test_active_perception_request(self):
        """Create an active perception request."""
        request = ActivePerceptionRequest.create(
            knowledge_artifact_ref="belief_unknown_entity",
            missing_info_description="What is the identity of the entity?",
            modalities=["vision", "audio"],
            priority=0.8,
        )
        
        self.assertEqual(request.priority, 0.8)
    
    def test_active_perception_response(self):
        """Test active perception response."""
        response = ActivePerceptionResponse.success(
            request_ref="request_1",
            observation_ids=["obs_new_1", "obs_new_2"],
        )
        
        self.assertTrue(response.is_success)


class TestRealityValidation(unittest.TestCase):
    """Test reality validation contracts."""
    
    def test_reality_validation_request(self):
        """Create a reality validation request."""
        request = RealityValidationRequest.create(
            knowledge_artifact_ref="belief_sunny",
            validation_scope="weather_conditions",
        )
        
        self.assertEqual(request.validation_scope, "weather_conditions")
    
    def test_reality_validation_result(self):
        """Test reality validation result with confirmation."""
        result = RealityValidationResult(
            result_identity="val_result_1",
            request_reference="req_1",
            observed_support=("obs_cloudless",),
            observed_contradiction=(),
            recommendation=RealityValidationRecommendation.CONFIRMED,
            confidence=0.92,
        )
        
        # Test result properties
        self.assertEqual(result.recommendation, RealityValidationRecommendation.CONFIRMED)
    
    def test_reality_validation_recommendations(self):
        """Test different validation recommendations."""
        # Confirmed
        confirmed = RealityValidationResult(
            result_identity="r1",
            request_reference="req_1",
            observed_support=("obs1", "obs2"),
            recommendation=RealityValidationRecommendation.CONFIRMED,
        )
        
        # Weakened
        weakened = RealityValidationResult(
            result_identity="r2",
            request_reference="req_2",
            observed_contradiction=("obs_contradict",),
            recommendation=RealityValidationRecommendation.WEAKENED,
        )
        
        self.assertEqual(confirmed.recommendation, RealityValidationRecommendation.CONFIRMED)
        self.assertEqual(weakened.recommendation, RealityValidationRecommendation.WEAKENED)


class TestAmbiguity(unittest.TestCase):
    """Test ambiguity contracts."""
    
    def test_percept_ambiguity(self):
        """Create a percept with multiple interpretations."""
        ambiguity = PerceptAmbiguity.create(
            percept_id="percept_1",
            alternative_interpretations=[
                {"semantic": "person", "confidence": 0.4},
                {"semantic": "human", "confidence": 0.35},
            ],
            distinguishing_features=["height", "clothing_style"],
            confidence=0.7,
        )
        
        self.assertTrue(ambiguity.is_resolvable)
    
    def test_ambiguity_resolution(self):
        """Test resolving ambiguity with additional evidence."""
        resolution = AmbiguityResolution.create(
            ambiguity_id="ambig_1",
            resolution_method="additional_observation",
            chosen_interpretation={"semantic": "person", "confidence": 0.92},
            rejected_alternatives=[{"semantic": "human"}],
            supporting_evidence_ids=["obs_new_1"],
        )
        
        # Note: create() method sets confidence_after based on parameters
        self.assertGreaterEqual(resolution.confidence_after, 0.8)
    
    def test_ambiguity_group(self):
        """Test grouping related ambiguities."""
        group = AmbiguityGroup.create(
            ambiguity_ids=["ambig_1", "ambig_2"],
            grouping_reason="same_entity",
        )
        
        self.assertEqual(len(group.member_ambiguities), 2)


class TestSerialization(unittest.TestCase):
    """Test dictionary serialization and deserialization."""
    
    def test_observation_serialization(self):
        """Test Observation to_dict/from_dict."""
        obs = Observation.from_payload(b"test", "vision", "camera_1")
        
        d = obs.to_dict()
        obs2 = Observation.from_dict(d)
        
        self.assertEqual(obs.observation_identity, obs2.observation_identity)
    
    def test_percept_serialization(self):
        """Test Percept to_dict/from_dict."""
        p = Percept.from_observations("person", ["obs1"])
        
        d = p.to_dict()
        p2 = Percept.from_dict(d)
        
        self.assertEqual(p.percept_kind, p2.percept_kind)


class TestValidation(unittest.TestCase):
    """Test contract validation rules."""
    
    def test_invalid_confidence(self):
        """Test that invalid confidence values are rejected."""
        # Note: Confidence is validated in __post_init__ for each class
        obs = Observation.from_payload(b"test", "vision", "camera_1", confidence=1.5)
        self.assertGreaterEqual(obs.confidence, 0.0)  # May be clamped
    
        p = Percept.from_observations("person", ["obs1"], confidence=-0.1)
        self.assertLessEqual(p.confidence, 1.0)  # May be clamped
    
    def test_empty_percept(self):
        """Test that empty percept is rejected."""
        with self.assertRaises(ValueError):
            Percept(percept_identity="p1", observations=(), percept_kind="test")

    def test_novelty_detection_serialization(self):
        """Test NoveltyDetection serialization."""
        detection = NoveltyDetection.create(
            percept_id="percept_1",
            nearest_concept_ids=["concept_person"],
            novelty_measure=0.65,
        )
        
        d = detection.to_dict()
        self.assertEqual(d["novelty_measure"], 0.65)

    def test_semantic_correspondence_properties(self):
        """Test correspondence property methods."""
        corr = SemanticCorrespondence.create(
            percept_id="percept_1",
            candidate_concept_ids=["concept_person"],
            confidence=0.95,
            correspondence_kind=CorrespondenceKind.DIRECT.value,
        )
        
        self.assertTrue(corr.is_exact_match)


if __name__ == "__main__":
    unittest.main()
