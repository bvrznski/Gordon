# Thread Identity Tests
# =======================

"""
Tests for Thread identity model.
"""

import pytest
from agent.execution.threads import ThreadId


class TestThreadId:
    """Test ThreadId class."""
    
    def test_generate_creates_unique_ids(self):
        """Each generated ID should be unique."""
        id1 = ThreadId.generate()
        id2 = ThreadId.generate()
        
        assert id1.value != id2.value
        assert isinstance(id1, ThreadId)
        assert isinstance(id2, ThreadId)
    
    def test_id_is_string(self):
        """ThreadId.value should be a string UUID."""
        thread_id = ThreadId.generate()
        
        # Should be a valid UUID format
        parts = thread_id.value.split('-')
        assert len(parts) == 5
    
    def test_id_equality(self):
        """Two ThreadIds with same value should be equal."""
        id1 = ThreadId("test-uuid")
        id2 = ThreadId("test-uuid")
        
        assert id1 == id2
        assert hash(id1) == hash(id2)
    
    def test_id_inequality(self):
        """Different ThreadIds should not be equal."""
        id1 = ThreadId("uuid-1")
        id2 = ThreadId("uuid-2")
        
        assert id1 != id2
    
    def test_str_representation(self):
        """String representation should return the value."""
        thread_id = ThreadId.generate()
        
        assert str(thread_id) == thread_id.value


class TestThreadMetadata:
    """Test ThreadMetadata class."""
    
    @pytest.fixture
    def metadata(self):
        """Create test metadata."""
        from agent.execution.threads import ThreadId, ThreadMetadata
        
        return ThreadMetadata(
            thread_id=ThreadId.generate(),
            purpose="Test thread",
            kind="test"
        )
    
    def test_metadata_immutability(self, metadata):
        """ThreadMetadata should be frozen (immutable)."""
        with pytest.raises(Exception):
            metadata.purpose = "New purpose"  # type: ignore


class TestThreadDescriptor:
    """Test ThreadDescriptor class."""
    
    def test_descriptor_from_metadata(self):
        """Create descriptor from metadata."""
        from agent.execution.threads import (
            ThreadId,
            ThreadMetadata,
            ThreadName,
            ThreadDescriptor,
        )
        
        name = ThreadName("test-thread")
        metadata = ThreadMetadata(
            thread_id=ThreadId.generate(),
            name=name,
            kind="conversation"
        )
        
        descriptor = ThreadDescriptor.from_metadata(metadata)
        
        assert descriptor.thread_id == metadata.thread_id
        assert descriptor.name == "test-thread"
        assert descriptor.kind == "conversation"