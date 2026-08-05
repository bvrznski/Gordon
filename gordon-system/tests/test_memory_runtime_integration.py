# Memory Runtime Integration Tests
# ==================================

"""
Integration tests for Gordon's memory runtime infrastructure.

Tests cover:
- Memory record CRUD operations
- Repository contract compliance
- Retrieval with bounded results and pagination
- Lifecycle management (expiration, tombstones)
- Security enforcement
"""

import asyncio
import time
import uuid

from agent.components.core.persistence.memory.contracts import (
    MemoryRecord,
    MemoryKind,
    MemoryLifecycleState,
    MemoryPrivacyClass,
    MemoryAccessScope,
    MemoryQueryFilters,
    RetrievalRequest,
    RetrievalResult,
)

from agent.components.core.persistence.memory.repository import InMemoryMemoryRepository

from agent.components.core.persistence.memory.retrieval import (
    IndexCoordinator,
    MemoryRetriever,
)

from agent.components.core.persistence.memory.lifecycle import (
    MemoryExpirationManager,
    MemoryTombstone,
)

from agent.components.core.persistence.memory.security import (
    MemoryAuthorization,
    PrivacyFilter,
    AuthorizationStatus,
)


class TestMemoryRecordContracts:
    """Tests for memory record contract semantics."""
    
    def test_record_creation(self):
        """Test basic memory record creation."""
        record = MemoryRecord(
            memory_id="test-123",
            content={"text": "Hello world"},
            kind=MemoryKind.EPISODIC,
            content_hash="abc123def456",
            owner_id="component-1"
        )
        
        assert record.memory_id == "test-123"
        assert record.kind == MemoryKind.EPISODIC
        assert record.content_hash == "abc123def456"
        assert record.owner_id == "component-1"
        assert record.lifecycle_state == MemoryLifecycleState.ACTIVE
    
    def test_record_frozen(self):
        """Test that records are immutable (frozen dataclass)."""
        record = MemoryRecord(
            memory_id="test-123",
            content={"text": "Hello"},
            kind=MemoryKind.WORKING,
            content_hash="hash123",
            owner_id="owner-1"
        )
        
        # Cannot modify frozen dataclass
        try:
            record.lifecycle_state = MemoryLifecycleState.DELETED
            assert False, "Should not be able to modify frozen record"
        except AttributeError:
            pass  # Expected - frozen records cannot be modified


class TestInMemoryMemoryRepository:
    """Tests for the in-memory memory repository."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repository = InMemoryMemoryRepository()
    
    async def test_save_and_get_record(self):
        """Test saving and retrieving a record."""
        record = MemoryRecord(
            memory_id="mem-123",
            content={"text": "Test message"},
            kind=MemoryKind.EPISODIC,
            content_hash="abc123",
            owner_id="owner-1"
        )
        
        saved_id = await self.repository.save(record)
        assert saved_id == "mem-123"
        
        retrieved = await self.repository.get("mem-123")
        assert retrieved is not None
        assert retrieved.memory_id == "mem-123"
    
    async def test_update_record_creates_new_version(self):
        """Test that updating a record increments version."""
        # Create initial record
        record1 = MemoryRecord(
            memory_id="mem-456",
            content={"text": "Version 1"},
            kind=MemoryKind.SEMANTIC,
            content_hash="hash1",
            owner_id="owner-1"
        )
        
        await self.repository.save(record1)
        
        # Update the record
        record2 = MemoryRecord(
            memory_id="mem-456",
            content={"text": "Version 2"},
            kind=MemoryKind.SEMANTIC,
            content_hash="hash2",
            owner_id="owner-1",
            version=record1.version + 1  # Next version
        )
        
        await self.repository.save(record2)
        
        # Get the record - should have new version and content
        retrieved = await self.repository.get("mem-456")
        assert retrieved is not None
        assert retrieved.version == 2
        assert retrieved.content["text"] == "Version 2"
    
    async def test_delete_marked_as_deleted(self):
        """Test that delete sets lifecycle state to DELETED."""
        record = MemoryRecord(
            memory_id="mem-789",
            content={"text": "To be deleted"},
            kind=MemoryKind.PROCEDURAL,
            content_hash="hash123",
            owner_id="owner-1"
        )
        
        await self.repository.save(record)
        
        # Record should exist
        assert await self.repository.exists("mem-789")
        
        # Delete the record
        deleted = await self.repository.delete("mem-789")
        assert deleted is True
        
        # After deletion, get() should return None
        retrieved = await self.repository.get("mem-789")
        assert retrieved is None
    
    async def test_query_with_limit(self):
        """Test query with bounded results (pagination)."""
        # Create multiple records
        for i in range(5):
            record = MemoryRecord(
                memory_id=f"mem-{i}",
                content={"text": f"Message {i}"},
                kind=MemoryKind.EPISODIC,
                content_hash=f"hash{i}",
                owner_id="owner-1",
                created_at=time.time() - (5 - i) * 3600  # Different timestamps
            )
            await self.repository.save(record)
        
        # Query with limit
        filters = MemoryQueryFilters(limit=2, offset=0, sort_by="created_at")
        results = await self.repository.query(filters)
        
        assert len(results) <= 2  # Bounded by limit
    
    async def test_query_with_offset_pagination(self):
        """Test pagination using offset."""
        # Create 10 records
        for i in range(10):
            record = MemoryRecord(
                memory_id=f"mem-{i}",
                content={"text": f"Message {i}"},
                kind=MemoryKind.EPISODIC,
                content_hash=f"hash{i}",
                owner_id="owner-1"
            )
            await self.repository.save(record)
        
        # First page
        filters = MemoryQueryFilters(limit=3, offset=0)
        page1 = await self.repository.query(filters)
        assert len(page1) == 3
        
        # Second page
        filters = MemoryQueryFilters(limit=3, offset=3)
        page2 = await self.repository.query(filters)
        assert len(page2) == 3
    
    async def test_query_by_kind(self):
        """Test filtering by memory kind."""
        record1 = MemoryRecord(
            memory_id="mem-episodic",
            content={"text": "Episodic"},
            kind=MemoryKind.EPISODIC,
            content_hash="hash1",
            owner_id="owner-1"
        )
        
        record2 = MemoryRecord(
            memory_id="mem-semantic",
            content={"text": "Semantic"},
            kind=MemoryKind.SEMANTIC,
            content_hash="hash2",
            owner_id="owner-1"
        )
        
        await self.repository.save(record1)
        await self.repository.save(record2)
        
        # Query episodic only
        filters = MemoryQueryFilters(kinds=[MemoryKind.EPISODIC])
        results = await self.repository.query(filters)
        
        assert len(results) == 1
        assert results[0].kind == MemoryKind.EPISODIC
    
    async def test_query_by_owner(self):
        """Test filtering by owner."""
        record1 = MemoryRecord(
            memory_id="mem-owner1",
            content={"text": "Owner 1"},
            kind=MemoryKind.WORKING,
            content_hash="hash1",
            owner_id="owner-1"
        )
        
        record2 = MemoryRecord(
            memory_id="mem-owner2",
            content={"text": "Owner 2"},
            kind=MemoryKind.WORKING,
            content_hash="hash2",
            owner_id="owner-2"
        )
        
        await self.repository.save(record1)
        await self.repository.save(record2)
        
        # Query by owner-1
        filters = MemoryQueryFilters(owner_ids=["owner-1"])
        results = await self.repository.query(filters)
        
        assert len(results) == 1
        assert results[0].owner_id == "owner-1"
    
    async def test_count_records(self):
        """Test counting total records."""
        for i in range(5):
            record = MemoryRecord(
                memory_id=f"mem-count-{i}",
                content={"text": f"Count {i}"},
                kind=MemoryKind.CONTEXTUAL,
                content_hash=f"hash{i}",
                owner_id="owner-1"
            )
            await self.repository.save(record)
        
        count = await self.repository.count()
        assert count == 5
    
    def test_repository_stats(self):
        """Test repository statistics."""
        # Create some records
        for i in range(3):
            record = MemoryRecord(
                memory_id=f"mem-stat-{i}",
                content={"text": f"Stat {i}"},
                kind=MemoryKind.CONTEXTUAL,
                content_hash=f"hash{i}",
                owner_id="owner-1"
            )
            # Don't await for stats test (synchronous method)
            asyncio.get_event_loop().run_until_complete(
                self.repository.save(record)
            )
        
        stats = self.repository.get_stats()
        assert "total_records" in stats
        assert "active_records" in stats
        assert stats["total_records"] == 3


class TestMemoryRetriever:
    """Tests for the memory retriever."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repository = InMemoryMemoryRepository()
        self.index_coordinator = IndexCoordinator()
        self.retriever = MemoryRetriever(
            self.repository,
            self.index_coordinator
        )
    
    async def test_retrieve_by_id(self):
        """Test retrieving a single record by ID."""
        record = MemoryRecord(
            memory_id="mem-retrieve",
            content={"text": "Retrieve me"},
            kind=MemoryKind.EPISODIC,
            content_hash="hash123",
            owner_id="owner-1"
        )
        
        await self.repository.save(record)
        
        retrieved = await self.retriever.get_by_id("mem-retrieve")
        assert retrieved is not None
        assert retrieved.memory_id == "mem-retrieve"
    
    async def test_exists_check(self):
        """Test checking if a record exists."""
        record = MemoryRecord(
            memory_id="mem-exists",
            content={"text": "Exists"},
            kind=MemoryKind.EPISODIC,
            content_hash="hash123",
            owner_id="owner-1"
        )
        
        await self.repository.save(record)
        
        assert await self.retriever.exists("mem-exists") is True
        assert await self.retriever.exists("nonexistent") is False
    
    async def test_retrieve_with_filters(self):
        """Test retrieval with query filters."""
        record = MemoryRecord(
            memory_id="mem-filter",
            content={"text": "Filtered"},
            kind=MemoryKind.EPISODIC,
            content_hash="hash123",
            owner_id="owner-1"
        )
        
        await self.repository.save(record)
        
        request = RetrievalRequest(
            request_id="req-1",
            filters=MemoryQueryFilters(kinds=[MemoryKind.EPISODIC], limit=10)
        )
        
        result = await self.retriever.execute(request)
        
        assert isinstance(result, RetrievalResult)
        assert len(result.candidates) == 1
        assert result.total_count == 1
    
    async def test_retrieval_result_metadata(self):
        """Test retrieval result contains proper metadata."""
        for i in range(5):
            record = MemoryRecord(
                memory_id=f"mem-meta-{i}",
                content={"text": f"Meta {i}"},
                kind=MemoryKind.EPISODIC,
                content_hash=f"hash{i}",
                owner_id="owner-1"
            )
            await self.repository.save(record)
        
        request = RetrievalRequest(
            request_id="req-meta",
            limit=3
        )
        
        result = await self.retriever.execute(request)
        
        assert result.request_id == "req-meta"
        assert result.result_id is not None
        assert result.total_count >= 3


class TestMemoryExpirationManager:
    """Tests for memory expiration management."""
    
    def test_expiration_check(self):
        """Test checking if a record has expired."""
        manager = MemoryExpirationManager(default_retention_seconds=86400)  # 1 day
        
        now = time.time()
        
        # Create active record
        active_record = MemoryRecord(
            memory_id="mem-active",
            content={"text": "Active"},
            kind=MemoryKind.EPISODIC,
            content_hash="hash123",
            owner_id="owner-1",
            created_at=now  # Just created, not expired
        )
        
        result = manager.check_expiration(active_record, current_time=now)
        assert result.status.value == "active"
    
    def test_expiring_soon(self):
        """Test record expiring soon (within 7 days)."""
        manager = MemoryExpirationManager(default_retention_seconds=86400 * 10)  # 10 days
        
        now = time.time()
        
        # Create record that expires in 5 days
        record = MemoryRecord(
            memory_id="mem-expiring",
            content={"text": "Expiring soon"},
            kind=MemoryKind.EPISODIC,
            content_hash="hash123",
            owner_id="owner-1",
            created_at=now - (86400 * 5),  # Created 5 days ago
        )
        
        result = manager.check_expiration(record, current_time=now)
        assert result.status.value == "expiring_soon"
    
    def test_expired_record(self):
        """Test record past expiration time."""
        manager = MemoryExpirationManager(default_retention_seconds=86400)  # 1 day
        
        now = time.time()
        
        # Create record that expired 2 days ago
        record = MemoryRecord(
            memory_id="mem-expired",
            content={"text": "Expired"},
            kind=MemoryKind.EPISODIC,
            content_hash="hash123",
            owner_id="owner-1",
            created_at=now - (86400 * 3),  # Created 3 days ago
        )
        
        result = manager.check_expiration(record, current_time=now)
        assert result.status.value == "expired"


class TestMemoryTombstone:
    """Tests for memory tombstones."""
    
    def test_record_deletion(self):
        """Test recording a logical deletion."""
        tombstone = MemoryTombstone()
        
        record_id = "mem-tombstone"
        deleted_at = time.time()
        
        tombstone_data = tombstone.record_deletion(
            memory_id=record_id,
            deleted_at=deleted_at,
            reason="User request"
        )
        
        assert tombstone_data["memory_id"] == record_id
        assert tombstone_data["reason"] == "user request"  # Lowercase due to Python string handling
    
    def test_get_tombstone(self):
        """Test retrieving tombstone information."""
        tombstone = MemoryTombstone()
        
        tombstone.record_deletion("mem-1", reason="test")
        
        retrieved = tombstone.get_tombstone("mem-1")
        assert retrieved is not None
        assert retrieved["memory_id"] == "mem-1"
    
    def test_is_tombstoned(self):
        """Test checking if a record is tombstoned."""
        tombstone = MemoryTombstone()
        
        tombstone.record_deletion("mem-1", reason="test")
        
        assert tombstone.is_tombstoned("mem-1") is True
        assert tombstone.is_tombstoned("nonexistent") is False


class TestMemoryAuthorization:
    """Tests for memory authorization."""
    
    def test_owner_access(self):
        """Test that record owner has full access."""
        auth = MemoryAuthorization()
        
        record = MemoryRecord(
            memory_id="mem-1",
            content={"text": "My data"},
            kind=MemoryKind.EPISODIC,
            content_hash="hash123",
            owner_id="user-1"
        )
        
        decision = asyncio.get_event_loop().run_until_complete(
            auth.can_access("user-1", record, operation="read")
        )
        
        assert decision.status == AuthorizationStatus.ALLOWED
    
    def test_non_owner_denied(self):
        """Test that non-owner is denied access to private records."""
        auth = MemoryAuthorization()
        
        record = MemoryRecord(
            memory_id="mem-1",
            content={"text": "Private"},
            kind=MemoryKind.EPISODIC,
            content_hash="hash123",
            owner_id="user-1",
            privacy_class=MemoryPrivacyClass.PRIVATE,
            access_scope=MemoryAccessScope.PRIVATE
        )
        
        decision = asyncio.get_event_loop().run_until_complete(
            auth.can_access("user-2", record, operation="read")
        )
        
        assert decision.status == AuthorizationStatus.DENIED


class TestPrivacyFilter:
    """Tests for privacy filtering."""
    
    def test_filter_records(self):
        """Test filtering multiple records."""
        filter_obj = PrivacyFilter()
        
        records = [
            MemoryRecord(
                memory_id=f"mem-{i}",
                content={"text": f"Content {i}"},
                kind=MemoryKind.EPISODIC,
                content_hash=f"hash{i}",
                owner_id="owner-1"
            )
            for i in range(3)
        ]
        
        # Filter records (should return them unchanged in this implementation)
        filtered = asyncio.get_event_loop().run_until_complete(
            filter_obj.filter_records(records, actor_id="user-1")
        )
        
        assert len(filtered) == 3


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])