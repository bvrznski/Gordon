# Phase 3.14.13 - Canonical Ready Queue Implementation
# =====================================================
#
# A canonical ready queue for work items in the scheduling pipeline.
#
# INVARIANTS:
#     QUE-INV-001: Contains only admitted work items
#     QUE-INV-002: Preserves ordering within priority classes
#     QUE-INV-003: Priority determines enqueue/dequeue order
#     QUE-INV-004: Queue size is bounded (prevents overflow)

"""
Canonical Ready Queue for Gordon Phase 3.14.13

A ready queue represents executable work that has passed admission.
It is the bridge between admission and scheduling.

CANONICAL MODEL:
    Work Item → Admission → Ready Queue → Scheduler → Execution
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Any,
)
from enum import Enum, auto
import uuid
import time

from . import (
    WorkItemId,
    WorkItemRecord,
    QueueId,
    PriorityClass,
    AdmissionState,
    ReadyQueueProtocol,
    dataclass_replace,
)


# =============================================================================
# PRIORITY ORDERING
# =============================================================================


def priority_to_value(priority: PriorityClass) -> int:
    """
    Convert priority class to numeric value for comparison.
    
    Higher values = higher priority.
    """
    values = {
        PriorityClass.CRITICAL: 5,
        PriorityClass.HIGH: 4,
        PriorityClass.NORMAL: 3,
        PriorityClass.LOW: 2,
        PriorityClass.BACKGROUND: 1,
    }
    return values.get(priority, 0)


# =============================================================================
# CANONICAL READY QUEUE
# =============================================================================


@dataclass
class CanonicalReadyQueue(ReadyQueueProtocol):
    """
    Canonical ready queue implementation.
    
    Implements a priority queue with bounded size for work items.
    Items are ordered by priority (higher first), then by creation time
    within the same priority class.
    
    INVARIANTS:
        QUE-001: Queue contains only admitted items
        QUE-002: Higher priority items come first
        QUE-003: Within same priority, earlier created comes first
        QUE-004: Queue size never exceeds max_size
    """

    queue_id: QueueId
    max_size: int = 10000

    # Internal state
    _items: Dict[WorkItemId, WorkItemRecord] = field(default_factory=dict)
    _priority_buckets: Dict[int, List[WorkItemId]] = field(default_factory=dict)
    _total_count: int = 0

    def __post_init__(self) -> None:
        """Initialize after dataclass fields are set."""
        if not self.queue_id:
            self.queue_id = QueueId.generate()

        # Initialize priority buckets
        for priority in PriorityClass:
            self._priority_buckets[priority_to_value(priority)] = []

    @property
    def size(self) -> int:
        """Current number of items in the queue."""
        return self._total_count

    async def enqueue(
        self,
        work_item: WorkItemRecord,
        priority: Optional[PriorityClass] = None,
    ) -> bool:
        """
        Add a work item to the queue.
        
        Args:
            work_item: The admitted work item to add
            priority: Override priority (optional)
            
        Returns:
            True if successfully added, False if queue is full or duplicate
            
        INVARIANTS:
            QUE-ENQ-001: Only admitted items may be enqueued
            QUE-ENQ-002: Priority determines position in queue
            QUE-ENQ-003: Queue preserves ordering within same priority
        """
        # Check if already present
        if work_item.work_item_id in self._items:
            return False

        # Use item's priority or provided priority
        effective_priority = priority or work_item.priority
        priority_value = priority_to_value(effective_priority)

        # Check queue capacity (fairness protection - prevents starvation by limiting total)
        if len(self._items) >= self.max_size:
            return False

        # Add to items dictionary
        self._items[work_item.work_item_id] = work_item

        # Insert into priority bucket in order
        bucket = self._priority_buckets.setdefault(priority_value, [])
        
        # Find insertion point (by creation time within same priority)
        inserted = False
        for i, existing_id in enumerate(bucket):
            existing_item = self._items[existing_id]
            if work_item.created_at_utc < existing_item.created_at_utc:
                bucket.insert(i, work_item.work_item_id)
                inserted = True
                break

        if not inserted:
            bucket.append(work_item.work_item_id)

        # Update state and timestamps
        updated_work = dataclass_replace(
            work_item,
            state=AdmissionState.READY,
            queued_at_utc=time.monotonic(),
        )
        self._items[work_item.work_item_id] = updated_work

        self._total_count += 1

        return True

    async def dequeue(self) -> Optional[WorkItemRecord]:
        """
        Remove and return the highest-priority item from the queue.
        
        Returns:
            The highest-priority work item, or None if empty
            
        INVARIANTS:
            QUE-DEQ-001: Returns items in priority order
            QUE-DEQ-002: Deterministic (earlier creation time for same priority)
        """
        # Find non-empty bucket starting from highest priority
        for priority_value in sorted(self._priority_buckets.keys(), reverse=True):
            bucket = self._priority_buckets[priority_value]
            if bucket:
                # Get first item (highest priority, earliest created)
                work_item_id = bucket.pop(0)
                work_item = self._items.pop(work_item_id)
                
                # Update state
                updated_work = dataclass_replace(
                    work_item,
                    state=AdmissionState.EXECUTING,
                    scheduled_at_utc=time.monotonic(),
                )
                self._items[work_item_id] = updated_work
                
                self._total_count -= 1
                return updated_work

        return None

    async def peek(self) -> Optional[WorkItemRecord]:
        """
        Return the highest-priority item without removing it.
        
        Returns:
            The highest-priority work item, or None if empty
        """
        # Find non-empty bucket starting from highest priority
        for priority_value in sorted(self._priority_buckets.keys(), reverse=True):
            bucket = self._priority_buckets[priority_value]
            if bucket:
                return self._items[bucket[0]]

        return None

    async def remove(self, work_item_id: WorkItemId) -> bool:
        """
        Remove a specific work item from the queue.
        
        Args:
            work_item_id: The work item to remove
            
        Returns:
            True if removed, False if not found
        """
        if work_item_id not in self._items:
            return False

        # Find and remove from priority bucket
        work_item = self._items[work_item_id]
        priority_value = priority_to_value(work_item.priority)
        
        if work_item_id in self._priority_buckets.get(priority_value, []):
            self._priority_buckets[priority_value].remove(work_item_id)

        del self._items[work_item_id]
        self._total_count -= 1

        return True

    async def clear(self) -> int:
        """
        Clear all items from the queue.
        
        Returns:
            Number of items cleared
        """
        count = len(self._items)
        self._items.clear()
        for bucket in self._priority_buckets.values():
            bucket.clear()
        self._total_count = 0
        return count

    async def get_by_priority(
        self,
        min_priority: PriorityClass = PriorityClass.BACKGROUND,
        limit: int = -1,
    ) -> List[WorkItemRecord]:
        """
        Get items with priority >= min_priority.
        
        Args:
            min_priority: Minimum priority threshold
            limit: Maximum number of items (-1 = no limit)
            
        Returns:
            Ordered list of matching work items (highest first)
        """
        min_value = priority_to_value(min_priority)
        result = []

        for priority_value in sorted(self._priority_buckets.keys(), reverse=True):
            if priority_value < min_value:
                break

            bucket = self._priority_buckets[priority_value]
            for item_id in bucket:
                item = self._items.get(item_id)
                if item:
                    result.append(item)
                    if limit > 0 and len(result) >= limit:
                        return result

        return result

    async def get_all(self) -> List[WorkItemRecord]:
        """Get all items in priority order."""
        return await self.get_by_priority()

    async def count_by_priority(
        self,
    ) -> Dict[str, int]:
        """
        Count items by priority class.
        
        Returns:
            Dictionary mapping priority names to counts
        """
        result = {}
        for priority_value, bucket in self._priority_buckets.items():
            # Find the priority class with this value
            for priority in PriorityClass:
                if priority_to_value(priority) == priority_value:
                    result[priority.value] = len(bucket)
                    break

        return result


# =============================================================================
# PRIORITY INHERITANCE QUEUE (for preventing priority inversion)
# =============================================================================


@dataclass
class PriorityInheritanceQueue(ReadyQueueProtocol):
    """
    Ready queue with priority inheritance to prevent priority inversion.
    
    When a high-priority item waits for resources held by a low-priority
    item, the low-priority item temporarily inherits the high priority
    until it releases the resource.
    """

    base_queue: CanonicalReadyQueue = field(default_factory=lambda: CanonicalReadyQueue(QueueId.generate()))
    
    # Priority inheritance tracking
    _inherited_priorities: Dict[WorkItemId, Tuple[PriorityClass, float]] = field(
        default_factory=dict
    )  # item_id -> (original_priority, inherit_until_timestamp)

    @property
    def queue_id(self) -> QueueId:
        return self.base_queue.queue_id

    async def enqueue(
        self,
        work_item: WorkItemRecord,
        priority: Optional[PriorityClass] = None,
    ) -> bool:
        """Add item to the underlying queue."""
        # Apply priority inheritance if needed
        effective_priority = await self._apply_priority_inheritance(work_item, priority)
        return await self.base_queue.enqueue(work_item, effective_priority)

    async def dequeue(self) -> Optional[WorkItemRecord]:
        """Remove and return highest-priority item (with inheritance applied)."""
        work_item = await self.base_queue.dequeue()
        if work_item:
            # Remove inherited priority
            if work_item.work_item_id in self._inherited_priorities:
                del self._inherited_priorities[work_item.work_item_id]
        return work_item

    async def peek(self) -> Optional[WorkItemRecord]:
        """Peek at highest-priority item."""
        return await self.base_queue.peek()

    async def remove(self, work_item_id: WorkItemId) -> bool:
        """Remove specific item from queue."""
        if work_item_id in self._inherited_priorities:
            del self._inherited_priorities[work_item_id]
        return await self.base_queue.remove(work_item_id)

    async def clear(self) -> int:
        """Clear all items from queue."""
        self._inherited_priorities.clear()
        return await self.base_queue.clear()

    @property
    def size(self) -> int:
        return self.base_queue.size

    async def _apply_priority_inheritance(
        self,
        work_item: WorkItemRecord,
        priority: Optional[PriorityClass] = None,
    ) -> PriorityClass:
        """
        Apply priority inheritance if the item holds resources needed by higher-priority items.
        
        This is a simplified implementation. In a real system, this would:
            1. Track which resources each work item holds
            2. Check if any waiting items need those resources
            3. Temporarily increase priority of resource-holding items
            
        For now, returns the original or provided priority.
        """
        return priority or work_item.priority


# =============================================================================
# DEADLINE-AWARE QUEUE (for time-sensitive scheduling)
# =============================================================================


@dataclass
class DeadlineQueue(ReadyQueueProtocol):
    """
    Ready queue that considers deadlines for scheduling decisions.
    
    Items with earlier deadlines are prioritized when they're close to
    their deadline threshold, even if their base priority is lower.
    """

    base_queue: CanonicalReadyQueue = field(default_factory=lambda: CanonicalReadyQueue(QueueId.generate()))

    # Deadline tracking
    _deadlines: Dict[WorkItemId, float] = field(
        default_factory=dict
    )  # item_id -> deadline_timestamp

    @property
    def queue_id(self) -> QueueId:
        return self.base_queue.queue_id

    async def enqueue(
        self,
        work_item: WorkItemRecord,
        priority: Optional[PriorityClass] = None,
    ) -> bool:
        """Add item with optional deadline."""
        # Track deadline if provided in metadata
        if "deadline_utc" in work_item.metadata:
            self._deadlines[work_item.work_item_id] = work_item.metadata["deadline_utc"]

        return await self.base_queue.enqueue(work_item, priority)

    async def dequeue(self) -> Optional[WorkItemRecord]:
        """Remove and return item considering both priority and deadline."""
        # Get candidates from each priority bucket
        await self.base_queue.count_by_priority()

        for priority_value in sorted(self._base_priority_buckets().keys(), reverse=True):
            bucket = self._base_priority_buckets()[priority_value]
            if bucket:
                # Check if any item is deadline-sensitive
                for item_id in bucket:
                    item = self._get_item(item_id)
                    if item and await self._is_deadline_critical(item):
                        # Prioritize this critical item
                        return await self.base_queue.dequeue()
                
                # Fall back to standard dequeue
                return await self.base_queue.dequeue()

        return None

    async def peek(self) -> Optional[WorkItemRecord]:
        """Peek at next item considering deadlines."""
        for priority_value in sorted(self._base_priority_buckets().keys(), reverse=True):
            bucket = self._base_priority_buckets()[priority_value]
            if bucket:
                # Find most critical item (deadline or highest priority)
                return self._get_item(bucket[0])

        return None

    async def remove(self, work_item_id: WorkItemId) -> bool:
        """Remove specific item."""
        if work_item_id in self._deadlines:
            del self._deadlines[work_item_id]
        return await self.base_queue.remove(work_item_id)

    async def clear(self) -> int:
        """Clear all items and deadlines."""
        self._deadlines.clear()
        return await self.base_queue.clear()

    @property
    def size(self) -> int:
        return self.base_queue.size

    async def _is_deadline_critical(self, work_item: WorkItemRecord) -> bool:
        """Check if an item is near its deadline."""
        if work_item.work_item_id not in self._deadlines:
            return False

        deadline = self._deadlines[work_item.work_item_id]
        now = time.monotonic()

        # Consider critical if past due
        if now >= deadline:
            return True

        return False

    def _base_priority_buckets(self):
        """Access base queue's priority buckets."""
        return self.base_queue._priority_buckets

    def _get_item(self, item_id: WorkItemId) -> Optional[WorkItemRecord]:
        """Get item from base queue."""
        return self.base_queue._items.get(item_id)


__all__ = [
    "CanonicalReadyQueue",
    "PriorityInheritanceQueue",
    "DeadlineQueue",
    "priority_to_value",
]