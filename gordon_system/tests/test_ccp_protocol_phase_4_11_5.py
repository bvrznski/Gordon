# Gordon Cognitive Architecture - Phase 4.11.5 Test Suite
# ===========================================================

"""
Cognitive Coordination Protocol (CCP) - Phase 4.11.5 Tests

Test suite for the Canonical Semantic Communication Protocol between
cognitive networks in Gordon.
"""

import pytest

# =============================================================================
# CCP IMPORTS TEST
# =============================================================================


class TestCCPImports:
    """Test CCP module imports are correct and complete."""
    
    def test_ccp_protocol_identity_import(self):
        """Test CCPProtocolIdentity can be imported."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPProtocolIdentity,
        )
        
        identity = CCPProtocolIdentity.v1_0()
        assert identity.semantic_name == "CognitiveCoordinationProtocol"
        assert identity.major_version == 1
        assert identity.minor_version == 0
    
    def test_ccp_message_kind_import(self):
        """Test CCPMessageKind can be imported."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageKind,
        )
        
        kinds = [k.value for k in CCPMessageKind]
        assert "projection_publication" in kinds
        assert "state_publication" in kinds
    
    def test_ccp_payload_kind_import(self):
        """Test CCPPayloadKind can be imported."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPPayloadKind,
        )
        
        payloads = [p.value for p in CCPPayloadKind]
        assert "network_projection" in payloads
        assert "coordination_state" in payloads
    
    def test_ccp_message_import(self):
        """Test CCPMessage can be imported."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessage,
        )
        
        msg = CCPMessage(
            identity="msg:test:1",
            message_kind="test_kind",
            payload_kind="test_payload",
            publisher="network:1",
        )
        assert msg.identity == "msg:test:1"
    
    def test_ccp_publication_import(self):
        """Test CCPPublication can be imported."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessage,
            CCPMessageVisibility,
            CCPPublisherReference,
            CCPPublication,
        )
        
        msg = CCPMessage(
            identity="msg:1",
            message_kind="test",
            payload_kind="test",
            publisher="network:1",
        )
        
        pub = CCPPublication.create_initial(
            message=msg,
            publisher=CCPPublisherReference.for_network("network:1", "TestNetwork"),
            visibility=CCPMessageVisibility(visibility_scope="targeted_networks"),
        )
        
        assert pub.identity == "pub:msg:1"
    
    def test_ccp_subscription_import(self):
        """Test CCPSubscription can be imported."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPConsumerReference,
            CCPSubscription,
        )
        
        consumer = CCPConsumerReference.for_network("consumer:1", "TestNetwork")
        sub = CCPSubscription.for_consumer(
            consumer=consumer,
            kinds=("projection_publication",),
        )
        
        assert sub.subscriber_reference.network_identity == "consumer:1"


# =============================================================================
# CCP MESSAGE VALIDATION TESTS
# =============================================================================


class TestCCPMessageValidation:
    """Test message validation functions."""
    
    def test_validate_identity_valid(self):
        """Test valid identity passes validation."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageValidator,
        )
        
        valid, error = CCPMessageValidator.validate_identity("msg:test:1")
        assert valid is True
        assert error is None
    
    def test_validate_identity_empty(self):
        """Test empty identity fails validation."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageValidator,
        )
        
        valid, error = CCPMessageValidator.validate_identity("")
        assert valid is False
        assert error is not None
    
    def test_validate_version_valid(self):
        """Test valid version passes validation."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageValidator,
        )
        
        valid, error = CCPMessageValidator.validate_version("1.0.0")
        assert valid is True
        assert error is None
    
    def test_validate_version_invalid(self):
        """Test invalid version fails validation."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageValidator,
        )
        
        valid, error = CCPMessageValidator.validate_version("1.0")
        assert valid is False
        assert "must be in format" in str(error)
    
    def test_validate_confidence_valid(self):
        """Test valid confidence passes validation."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageValidator,
        )
        
        valid, error = CCPMessageValidator.validate_confidence(0.75)
        assert valid is True
        assert error is None
    
    def test_validate_confidence_invalid(self):
        """Test invalid confidence fails validation."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageValidator,
        )
        
        valid, error = CCPMessageValidator.validate_confidence(1.5)
        assert valid is False
        assert "must be between" in str(error)


# =============================================================================
# CCP COMPATIBILITY TESTS
# =============================================================================


class TestCCPCompatibility:
    """Test protocol compatibility checking."""
    
    def test_same_major_version_compatible(self):
        """Test same major version is compatible."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPCompatibilityChecker,
        )
        
        status = CCPCompatibilityChecker.check_compatibility("1.0.0", "1.2.0")
        assert status in ("fully_compatible", "forward_compatible")
    
    def test_different_major_version_incompatible(self):
        """Test different major versions are incompatible."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPCompatibilityChecker,
        )
        
        status = CCPCompatibilityChecker.check_compatibility("1.0.0", "2.0.0")
        assert status == "incompatible"
    
    def test_major_version_match(self):
        """Test major version matching."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPCompatibilityChecker,
        )
        
        result = CCPCompatibilityChecker.check_major_version_match("1.2.3", "1.4.5")
        assert result is True


class TestCCPSerialization:
    """Test deterministic serialization."""
    
    def test_serialize_message(self):
        """Test message serialization produces JSON."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessage,
        )
        from gordon_system.src.agent.components.networks.coordinator.protocol.serialization import (
            CCPSerializer,
        )
        
        msg = CCPMessage(
            identity="msg:test:1",
            message_kind="test_kind",
            payload_kind="test_payload",
            publisher="network:1",
            protocol_version="1.0.0",
            revision=1,
            confidence=0.95,
            uncertainty=0.05,
        )
        
        # Use asdict to get dict representation, then serialize
        from dataclasses import asdict
        msg_dict = asdict(msg)
        serialized = CCPSerializer.serialize(msg_dict)
        assert isinstance(serialized, str)
        assert '"identity":' in serialized
    
    def test_deserialize_message(self):
        """Test message deserialization."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessage,
        )
        from gordon_system.src.agent.components.networks.coordinator.protocol.serialization import (
            CCPSerializer,
        )
        
        msg = CCPMessage(
            identity="msg:test:1",
            message_kind="test_kind",
            payload_kind="test_payload",
            publisher="network:1",
        )
        
        # Use asdict to get dict representation, then serialize
        from dataclasses import asdict
        msg_dict = asdict(msg)
        serialized = CCPSerializer.serialize(msg_dict)
        deserialized = CCPSerializer.deserialize(serialized)
        
        assert isinstance(deserialized, dict)
        assert deserialized.get("identity") == "msg:test:1"
    
    def test_serialization_is_deterministic(self):
        """Test serialization is deterministic (same input -> same output)."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessage,
        )
        from gordon_system.src.agent.components.networks.coordinator.protocol.serialization import (
            CCPSerializer,
        )
        
        msg = CCPMessage(
            identity="msg:test:1",
            message_kind="test_kind",
            payload_kind="test_payload",
            publisher="network:1",
        )
        
        # Use asdict to get dict representation
        from dataclasses import asdict
        msg_dict = asdict(msg)
        
        out1 = CCPSerializer.serialize(msg_dict)
        out2 = CCPSerializer.serialize(msg_dict)
        
        assert out1 == out2


# =============================================================================
# CCP MESSAGE KINDS TESTS
# =============================================================================


class TestCCPMessageKinds:
    """Test message kind taxonomy."""
    
    def test_all_required_message_kinds_present(self):
        """Test all required message kinds are defined."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageKind,
        )
        
        required_kinds = [
            "projection_publication",
            "state_publication",
            "capability_advertisement",
            "requirement_declaration",
            "subscription_declaration",
            "acknowledgement",
            "acceptance",
            "rejection",
            "deferral",
            "negotiation_request",
            "synchronization_request",
        ]
        
        kinds = [k.value for k in CCPMessageKind]
        
        for kind in required_kinds:
            assert kind in kinds, f"Missing required message kind: {kind}"
    
    def test_message_kind_values_are_unique(self):
        """Test all message kind values are unique."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageKind,
        )
        
        values = [k.value for k in CCPMessageKind]
        assert len(values) == len(set(values)), "Duplicate message kind values found"


# =============================================================================
# CCP VISIBILITY TESTS
# =============================================================================


class TestCCPVisibility:
    """Test visibility scope configuration."""
    
    def test_create_visibility(self):
        """Test creating a visibility configuration."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageVisibility,
        )
        
        visibility = CCPMessageVisibility(
            visibility_scope="targeted_networks",
            target_networks=("network:1", "network:2"),
            can_be_observed=False,
        )
        
        assert visibility.visibility_scope == "targeted_networks"
        assert len(visibility.target_networks) == 2
    
    def test_default_visibility(self):
        """Test default visibility configuration."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessageVisibility,
        )
        
        visibility = CCPMessageVisibility()
        
        assert visibility.visibility_scope == ""
        assert len(visibility.target_networks) == 0


# =============================================================================
# CCP PUBLICATION TESTS
# =============================================================================


class TestCCPPublication:
    """Test publication record creation and properties."""
    
    def test_create_publication(self):
        """Test creating a publication."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPMessage,
            CCPPublisherReference,
            CCPMessageVisibility,
            CCPPublication,
        )
        
        msg = CCPMessage(
            identity="msg:test:1",
            message_kind="test",
            payload_kind="test",
            publisher="network:1",
        )
        
        pub = CCPPublication.create_initial(msg, CCPPublisherReference.for_network("net:1", "Test"), 
                                           CCPMessageVisibility(visibility_scope="global_coordination"))
        
        assert pub.identity == "pub:msg:test:1"
        assert pub.publication_revision == 1
        assert pub.publication_status == "created"


# =============================================================================
# CCP SUBSCRIPTION TESTS
# =============================================================================


class TestCCPSubscription:
    """Test subscription record creation and properties."""
    
    def test_create_subscription(self):
        """Test creating a subscription."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPConsumerReference,
            CCPSubscription,
        )
        
        consumer = CCPConsumerReference.for_network("consumer:1", "TestNetwork")
        sub = CCPSubscription.for_consumer(
            consumer=consumer,
            kinds=("projection_publication",),
            payloads=("network_projection",),
        )
        
        assert sub.subscriber_reference is not None
        assert len(sub.subscribed_message_kinds) > 0


# =============================================================================
# CCP ACKNOWLEDGEMENT TESTS
# =============================================================================


class TestCCPAcknowledgement:
    """Test acknowledgement record creation."""
    
    def test_create_received_acknowledgement(self):
        """Test creating a received acknowledgement."""
        from gordon_system.src.agent.components.networks.coordinator.protocol import (
            CCPAcknowledgement,
            CCPConsumerReference,
        )
        
        consumer = CCPConsumerReference.for_network("consumer:1", "TestNetwork")
        ack = CCPAcknowledgement.for_received("pub:test:1", consumer)
        
        assert ack.acknowledgement_kind == "received"
        assert ack.confidence == 1.0
        assert ack.uncertainty == 0.0