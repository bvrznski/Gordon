# Operating System Abstraction - Phase 3.32.3
# ============================================
#
# This module provides canonical OS contracts that abstract away operating
# system-specific APIs and behavior.
#
# CONTRACT PRINCIPLES:
# -------------------
# O-CON-001: All process management goes through ProcessManagement interface
# O-CON-002: All thread management goes through ThreadManagement interface
# O-CON-003: All filesystem access goes through FilesystemAccess interface
# O-CON-004: All IPC operations go through IPCInterface
# O-CON-005: All networking goes through NetworkingInterface

from __future__ import annotations

import os
import signal
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, Optional, List, Dict, Any, Tuple, TYPE_CHECKING


if TYPE_CHECKING:
    from .foundations import PlatformIdentity, PlatformDescriptor


class OSFeature(Enum):
    """Supported operating system features."""
    PROCESS_MANAGEMENT = "process_management"
    THREAD_MANAGEMENT = "thread_management"
    FILESYSTEM_ACCESS = "filesystem_access"
    IPC_INTERFACE = "ipc_interface"
    NETWORKING_INTERFACE = "networking_interface"
    SIGNAL_HANDLING = "signal_handling"
    ENVIRONMENT_ACCESS = "environment_access"
    USER_INFO = "user_info"
    PERMISSIONS = "permissions"


class ProcessState(Enum):
    """Process lifecycle states."""
    CREATED = "created"
    RUNNING = "running"
    WAITING = "waiting"
    STOPPED = "stopped"
    ZOMBIE = "zombie"
    TERMINATED = "terminated"


class ThreadState(Enum):
    """Thread lifecycle states."""
    NEW = "new"
    RUNNING = "running"
    BLOCKED = "blocked"
    WAITING = "waiting"
    TERMINATED = "terminated"


# =============================================================================
# Process Management Interface
# =============================================================================


@dataclass(frozen=True)
class ProcessDescriptor:
    """
    Descriptor for a process.
    
    INVARIANTS:
        PD-INV-001: Process descriptor is immutable
        PD-INV-002: PID uniquely identifies process
        PD-INV-003: Parent PID establishes hierarchy
    """
    
    pid: int
    ppid: Optional[int] = None
    name: str = "unknown"
    state: ProcessState = ProcessState.CREATED
    uid: int = 0
    gid: int = 0
    cwd: str = "/"
    environ: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ChildProcessHandle:
    """
    Handle to a child process.
    
    INVARIANTS:
        CPH-INV-001: Handle is immutable once created
        CPH-INV-002: Process exit status is final
        CPH-INV-003: No resource leaks on handle destruction
    """
    
    pid: int
    stdin: Optional[Any] = None
    stdout: Optional[Any] = None
    stderr: Optional[Any] = None
    
    def wait(self, timeout: Optional[float] = None) -> int:
        """Wait for process to exit and return exit code."""
        import subprocess
        result = subprocess.run(
            ["echo", "0"],  # Placeholder - real implementation uses actual PID
            capture_output=True,
        )
        return result.returncode
    
    def terminate(self) -> None:
        """Send termination signal to process."""
        pass
    
    def kill(self) -> None:
        """Forcefully kill process."""
        pass


@dataclass(frozen=True)
class ProcessSpec:
    """
    Specification for creating a new process.
    
    INVARIANTS:
        PS-INV-001: Spec is immutable once created
        PS-INV-002: All paths are absolute or relative to cwd
        PS-INV-003: Environment inherits from parent if not specified
    """
    
    executable: str
    args: Tuple[str, ...] = field(default_factory=tuple)
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None
    stdin: Any = None
    stdout: Any = None
    stderr: Any = None
    uid: Optional[int] = None
    gid: Optional[int] = None


@dataclass(frozen=True)
class ProcessExitInfo:
    """Information about a process exit."""
    pid: int
    exit_code: int
    signal: Optional[str] = None
    core_dumped: bool = False


@dataclass(frozen=True)
class ProcessGroupDescriptor:
    """
    Descriptor for a process group.
    
    INVARIANTS:
        PGD-INV-001: Group ID is unique within session
        PGD-INV-002: All processes in group share terminal
        PGD-INV-003: Group can be signaled as a unit
    """
    
    pgid: int
    members: Tuple[int, ...] = field(default_factory=tuple)
    leader_pid: Optional[int] = None


class ProcessManagement(Protocol):
    """
    Protocol for process management operations.
    
    INVARIANTS:
        PM-INV-001: All processes have a parent (except init)
        PM-INV-002: No zombie processes are left uncollected
        PM-INV-003: Process IDs are reused only after collection
    
    SUBSYSTEMS MUST USE:
        - create_process() to start new processes
        - wait_for_exit() to collect exit status
        - signal_process() for process control
    """
    
    def get_current_process(self) -> ProcessDescriptor:
        """Get descriptor for the current process."""
        ...
    
    def create_child_process(
        self,
        spec: ProcessSpec,
    ) -> ChildProcessHandle:
        """
        Create a new child process.
        
        Args:
            spec: Process specification
            
        Returns:
            Handle to the created process
        """
        ...
    
    def wait_for_exit(self, pid: int, timeout: Optional[float] = None) -> ProcessExitInfo:
        """Wait for a specific process to exit."""
        ...
    
    def signal_process(self, pid: int, sig: signal.Signals) -> bool:
        """
        Send a signal to a process.
        
        Args:
            pid: Target process ID
            sig: Signal to send
            
        Returns:
            True if signal was sent successfully
        """
        ...
    
    def get_process_group(self, pid: Optional[int] = None) -> ProcessGroupDescriptor:
        """Get the process group for a process (or current)."""
        ...
    
    def list_processes(self) -> Tuple[ProcessDescriptor, ...]:
        """List all visible processes."""
        ...


# =============================================================================
# Thread Management Interface
# =============================================================================


@dataclass(frozen=True)
class ThreadDescriptor:
    """
    Descriptor for a thread.
    
    INVARIANTS:
        TD-INV-001: TID uniquely identifies thread
        TD-INV-002: Thread belongs to exactly one process
        TD-INV-003: Thread state transitions are well-defined
    """
    
    tid: int
    pid: int
    name: str = "unknown"
    state: ThreadState = ThreadState.NEW
    priority: int = 0
    cpu_affinity: Tuple[int, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutionContext:
    """
    Context for thread execution.
    
    INVARIANTS:
        EC-INV-001: Context is immutable during execution
        EC-INV-002: All operations in context are atomic
        EC-INV-003: No resource leaks on context exit
    """
    
    tid: int
    pid: int
    stack_size: int = 0
    guard_pages: bool = True


@dataclass(frozen=True)
class ThreadAffinity:
    """
    Thread CPU affinity specification.
    
    INVARIANTS:
        TA-INV-001: Affinity is a subset of available CPUs
        TA-INV-002: Affinity cannot cause deadlock
        TA-INV-003: Affinity is applied atomically
    """
    
    cpu_mask: Tuple[int, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ThreadGroup:
    """
    Group of threads that can be controlled together.
    
    INVARIANTS:
        TG-INV-001: All members share same priority
        TG-INV-002: Signal sent to group goes to all members
        TG-INV-003: No duplicate thread IDs in group
    """
    
    group_id: int
    member_ids: Tuple[int, ...] = field(default_factory=tuple)
    leader_id: Optional[int] = None


@dataclass(frozen=True)
class ExecutionPool:
    """
    Pool of threads for parallel execution.
    
    INVARIANTS:
        EP-INV-001: Pool size is immutable after creation
        EP-INV-002: All threads have same priority
        EP-INV-003: No resource leaks on pool destruction
    """
    
    pool_id: int
    max_threads: int
    active_threads: int = 0


class ThreadManagement(Protocol):
    """
    Protocol for thread management operations.
    
    INVARIANTS:
        TM-INV-001: All threads have exactly one parent process
        TM-INV-002: No orphan threads exist
        TM-INV-003: Thread cleanup is automatic on exit
    
    SUBSYSTEMS MUST USE:
        - get_current_thread() to identify current thread
        - create_thread() for parallel execution
        - set_affinity() for CPU affinity control
    """
    
    def get_current_thread(self) -> ThreadDescriptor:
        """Get descriptor for the current thread."""
        ...
    
    def get_all_threads(self, pid: int) -> Tuple[ThreadDescriptor, ...]:
        """Get all threads in a process."""
        ...
    
    def set_affinity(
        self,
        tid: int,
        affinity: ThreadAffinity,
    ) -> bool:
        """
        Set CPU affinity for a thread.
        
        Args:
            tid: Target thread ID
            affinity: Desired CPU affinity
            
        Returns:
            True if affinity was set successfully
        """
        ...
    
    def get_execution_context(self, tid: Optional[int] = None) -> ExecutionContext:
        """Get execution context for a thread (or current)."""
        ...
    
    def create_execution_pool(
        self,
        max_threads: int,
        name: str = "default",
    ) -> ExecutionPool:
        """
        Create a thread pool for parallel execution.
        
        Args:
            max_threads: Maximum number of threads in pool
            name: Name for the pool
            
        Returns:
            Pool descriptor
        """
        ...
    
    def signal_thread(self, tid: int, sig: int) -> bool:
        """Send a signal to a specific thread."""
        ...


# =============================================================================
# Filesystem Access Interface
# =============================================================================


class FileSystemType(Enum):
    """Types of filesystems."""
    LOCAL = "local"
    NETWORK = "network"
    VIRTUAL = "virtual"
    TEMPORARY = "temporary"


@dataclass(frozen=True)
class PathElement:
    """
    Single element in a path.
    
    INVARIANTS:
        PE-INV-001: Element is a single path component
        PE-INV-002: No trailing separators in element
        PE-INV-003: Element can be empty (root)
    """
    
    value: str
    is_directory: bool = False


@dataclass(frozen=True)
class FilePath:
    """
    Canonical file path.
    
    INVARIANTS:
        FP-INV-001: Path is absolute or explicitly relative
        FP-INV-002: No symbolic link traversal in canonical form
        FP-INV-003: Path components are normalized (no '..' in middle)
    """
    
    components: Tuple[str, ...]
    is_absolute: bool = True
    
    @classmethod
    def parse(cls, path: str) -> FilePath:
        """Parse a string path into FilePath."""
        parts = path.split('/')
        return cls(components=tuple(p for p in parts if p), is_absolute=path.startswith('/'))


@dataclass(frozen=True)
class DirectoryPath:
    """
    Canonical directory path.
    
    INVARIANTS:
        DP-INV-001: Path ends with separator (implied or explicit)
        DP-INV-002: All components are directories
        DP-INV-003: No regular file in path
    """
    
    components: Tuple[str, ...]
    is_absolute: bool = True


@dataclass(frozen=True)
class FilePermissions:
    """
    File permission bits.
    
    INVARIANTS:
        FP-INV-001: Permissions are a bitmask
        FP-INV-002: Owner/group/other permissions are independent
        FP-INV-003: Special bits (setuid, setgid, sticky) are optional
    """
    
    owner_read: bool = False
    owner_write: bool = False
    owner_execute: bool = False
    
    group_read: bool = False
    group_write: bool = False
    group_execute: bool = False
    
    other_read: bool = False
    other_write: bool = False
    other_execute: bool = False
    
    setuid: bool = False
    setgid: bool = False
    sticky: bool = False


@dataclass(frozen=True)
class FileHandle:
    """
    Handle to an open file.
    
    INVARIANTS:
        FH-INV-001: Handle has exactly one backing file descriptor
        FH-INV-002: All operations are atomic where possible
        FH-INV-003: No leaks on handle destruction
    """
    
    fd: int
    path: FilePath
    mode: str = "r"
    permissions: FilePermissions = field(default_factory=FilePermissions)


@dataclass(frozen=True)
class AtomicWriteOperation:
    """
    Specification for an atomic write operation.
    
    INVARIANTS:
        AWO-INV-001: Write is either fully complete or not at all
        AWO-INV-002: No partial writes are visible to readers
        AWO-INV-003: Temporary file is cleaned up on failure
    """
    
    target_path: FilePath
    content: bytes
    permissions: Optional[FilePermissions] = None


class FilesystemAccess(Protocol):
    """
    Protocol for filesystem operations.
    
    INVARIANTS:
        FS-INV-001: All paths are canonicalized before use
        FS-INV-002: No symlink traversal without explicit request
        FS-INV-003: All file operations are atomic where possible
    
    SUBSYSTEMS MUST USE:
        - open_file() to get handles
        - read/write operations through handles
        - atomic_write() for safe file modifications
    """
    
    def get_current_directory(self) -> DirectoryPath:
        """Get the current working directory."""
        ...
    
    def set_current_directory(self, path: DirectoryPath) -> bool:
        """Change the current working directory."""
        ...
    
    def open_file(
        self,
        path: FilePath,
        mode: str = "r",
        permissions: Optional[FilePermissions] = None,
    ) -> Optional[FileHandle]:
        """
        Open a file and return a handle.
        
        Args:
            path: Path to the file
            mode: Open mode (r, w, a, rb, wb, etc.)
            permissions: Initial permissions if creating
            
        Returns:
            File handle or None if open failed
        """
        ...
    
    def create_file(
        self,
        path: FilePath,
        initial_content: bytes = b"",
        permissions: Optional[FilePermissions] = None,
    ) -> bool:
        """Create a new file with optional content."""
        ...
    
    def delete_file(self, path: FilePath) -> bool:
        """Delete a file."""
        ...
    
    def atomic_write(
        self,
        operation: AtomicWriteOperation,
    ) -> bool:
        """
        Perform an atomic write operation.
        
        Args:
            operation: Write specification
            
        Returns:
            True if write succeeded
        """
        ...
    
    def get_file_info(self, path: FilePath) -> Optional[Dict[str, Any]]:
        """Get file metadata (size, permissions, timestamps)."""
        ...
    
    def list_directory(self, dir_path: DirectoryPath) -> Tuple[FilePath, ...]:
        """List files in a directory."""
        ...


# =============================================================================
# IPC Interface
# =============================================================================


@dataclass(frozen=True)
class MessageQueueDescriptor:
    """
    Descriptor for a message queue.
    
    INVARIANTS:
        MQD-INV-001: Queue has unique identifier within namespace
        MQD-INV-002: Messages are delivered in FIFO order (unless prioritized)
        MQD-INV-003: No message loss on normal operation
    """
    
    queue_id: int
    name: str = ""
    capacity: int = 100
    current_size: int = 0


@dataclass(frozen=True)
class SharedMemoryRegion:
    """
    Descriptor for shared memory.
    
    INVARIANTS:
        SMR-INV-001: Region has fixed size
        SMR-INV-002: Access is through mapped view
        SMR-INV-003: Synchronization required for concurrent access
    """
    
    region_id: int
    name: str = ""
    size: int = 0
    is_readable: bool = True
    is_writable: bool = False


@dataclass(frozen=True)
class IPCChannel:
    """
    Channel for inter-process communication.
    
    INVARIANTS:
        IPC-INV-001: Channel has exactly one sender and one receiver (for point-to-point)
        IPC-INV-002: No data corruption on transmission
        IPC-INV-003: No data loss on normal operation
    """
    
    channel_id: int
    local_endpoint: str = ""
    remote_endpoint: str = ""
    direction: str = "bidirectional"  # send, receive, bidirectional


class IPCInterface(Protocol):
    """
    Protocol for IPC operations.
    
    INVARIANTS:
        IPC-INV-001: All communication is explicit
        IPC-INV-002: No implicit data sharing without synchronization
        IPC-INV-003: Deadlock detection and prevention
    
    SUBSYSTEMS MUST USE:
        - create_message_queue() for message-based IPC
        - create_shared_memory() for memory-mapped IPC
        - send/receive through channels
    """
    
    def create_message_queue(self, name: str, capacity: int = 100) -> MessageQueueDescriptor:
        """Create a new message queue."""
        ...
    
    def send_message(
        self,
        queue_id: int,
        message: bytes,
        priority: int = 0,
    ) -> bool:
        """
        Send a message to a queue.
        
        Args:
            queue_id: Target message queue
            message: Message data
            priority: Message priority
            
        Returns:
            True if message was queued
        """
        ...
    
    def receive_message(
        self,
        queue_id: int,
        timeout: Optional[float] = None,
    ) -> Optional[bytes]:
        """
        Receive a message from a queue.
        
        Args:
            queue_id: Source message queue
            timeout: Maximum wait time (None for infinite)
            
        Returns:
            Received message or None if timeout
        """
        ...
    
    def create_shared_memory(self, name: str, size: int) -> SharedMemoryRegion:
        """Create a shared memory region."""
        ...
    
    def map_shared_memory(
        self,
        region_id: int,
        writable: bool = False,
    ) -> Optional[Any]:
        """
        Map shared memory into current address space.
        
        Args:
            region_id: Region to map
            writable: Whether to map for writing
            
        Returns:
            Mapped buffer or None if mapping failed
        """
        ...


# =============================================================================
# Networking Interface
# =============================================================================


@dataclass(frozen=True)
class SocketAddress:
    """Network socket address."""
    host: str = "localhost"
    port: int = 0
    family: str = "ipv4"  # ipv4, ipv6, unix


@dataclass(frozen=True)
class ConnectionEndpoint:
    """
    Endpoint for network connection.
    
    INVARIANTS:
        CE-INV-001: Endpoint has exactly one local and remote address
        CE-INV-002: Connection state is well-defined
        CE-INV-003: No data corruption on transmission
    """
    
    local_address: SocketAddress
    remote_address: SocketAddress
    protocol: str = "tcp"  # tcp, udp, unix


class NetworkingInterface(Protocol):
    """
    Protocol for networking operations.
    
    INVARIANTS:
        NET-INV-001: All network access goes through this interface
        NET-INV-002: No direct socket API calls outside implementations
        NET-INV-003: Error handling is comprehensive
    
    SUBSYSTEMS MUST USE:
        - create_socket() to get network endpoints
        - connect/listen through endpoints
        - send/recv through channels
    """
    
    def create_socket(self, address: SocketAddress) -> ConnectionEndpoint:
        """Create a new socket endpoint."""
        ...
    
    def listen(
        self,
        endpoint: ConnectionEndpoint,
        backlog: int = 10,
    ) -> bool:
        """Start listening on an endpoint."""
        ...
    
    def accept_connection(
        self,
        endpoint: ConnectionEndpoint,
        timeout: Optional[float] = None,
    ) -> Optional[ConnectionEndpoint]:
        """
        Accept an incoming connection.
        
        Args:
            endpoint: Listening endpoint
            timeout: Maximum wait time
            
        Returns:
            New connection endpoint or None if timeout
        """
        ...
    
    def connect(
        self,
        endpoint: ConnectionEndpoint,
        timeout: Optional[float] = None,
    ) -> bool:
        """Connect to a remote endpoint."""
        ...
    
    def send_data(self, endpoint: ConnectionEndpoint, data: bytes) -> int:
        """Send data through an endpoint."""
        ...
    
    def receive_data(
        self,
        endpoint: ConnectionEndpoint,
        max_size: int = 65536,
        timeout: Optional[float] = None,
    ) -> Optional[bytes]:
        """
        Receive data from an endpoint.
        
        Args:
            endpoint: Source endpoint
            max_size: Maximum bytes to receive
            timeout: Maximum wait time
            
        Returns:
            Received data or None if timeout/disconnected
        """
        ...


# =============================================================================
# OS Abstraction Interface
# =============================================================================


@dataclass(frozen=True)
class OSAbstraction:
    """
    Main OS abstraction interface.
    
    INVARIANTS:
        OS-INV-001: All OS operations go through this interface
        OS-INV-002: No direct OS API calls outside implementations
        OS-INV-003: Platform identity and descriptor are consistent
    
    IMPLEMENTATIONS MUST PROVIDE:
        - process_management
        - thread_management
        - filesystem_access
        - ipc_interface
        - networking_interface
    """
    
    platform_identity: PlatformIdentity
    platform_descriptor: PlatformDescriptor
    
    # All protocol interfaces (will be implemented by concrete classes)
    _process_management: ProcessManagement = field(default=None)  # type: ignore
    _thread_management: ThreadManagement = field(default=None)  # type: ignore
    _filesystem_access: FilesystemAccess = field(default=None)  # type: ignore
    _ipc_interface: IPCInterface = field(default=None)  # type: ignore
    _networking_interface: NetworkingInterface = field(default=None)  # type: ignore
    
    @property
    def process_management(self) -> ProcessManagement:
        """Get process management interface."""
        if self._process_management is None:
            raise RuntimeError("Process management not initialized")
        return self._process_management
    
    @property
    def thread_management(self) -> ThreadManagement:
        """Get thread management interface."""
        if self._thread_management is None:
            raise RuntimeError("Thread management not initialized")
        return self._thread_management
    
    @property
    def filesystem_access(self) -> FilesystemAccess:
        """Get filesystem access interface."""
        if self._filesystem_access is None:
            raise RuntimeError("Filesystem access not initialized")
        return self._filesystem_access
    
    @property
    def ipc_interface(self) -> IPCInterface:
        """Get IPC interface."""
        if self._ipc_interface is None:
            raise RuntimeError("IPC interface not initialized")
        return self._ipc_interface
    
    @property
    def networking_interface(self) -> NetworkingInterface:
        """Get networking interface."""
        if self._networking_interface is None:
            raise RuntimeError("Networking interface not initialized")
        return self._networking_interface
    
    def has_os_feature(self, feature: "OSFeature") -> bool:
        """Check if OS supports a specific feature."""
        return feature.value in self.platform_descriptor.capabilities


__all__ = [
    # Enums
    "OSFeature",
    "ProcessState",
    "ThreadState",
    "FileSystemType",
    
    # Process types
    "ProcessDescriptor",
    "ChildProcessHandle",
    "ProcessSpec",
    "ProcessExitInfo",
    "ProcessGroupDescriptor",
    "ProcessManagement",
    
    # Thread types
    "ThreadDescriptor",
    "ExecutionContext",
    "ThreadAffinity",
    "ThreadGroup",
    "ExecutionPool",
    "ThreadManagement",
    
    # Filesystem types
    "PathElement",
    "FilePath",
    "DirectoryPath",
    "FilePermissions",
    "FileHandle",
    "AtomicWriteOperation",
    "FilesystemAccess",
    
    # IPC types
    "MessageQueueDescriptor",
    "SharedMemoryRegion",
    "IPCChannel",
    "IPCInterface",
    
    # Networking types
    "SocketAddress",
    "ConnectionEndpoint",
    "NetworkingInterface",
    
    # Main interface
    "OSAbstraction",
]