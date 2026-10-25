"""
VectoraFix Public Interface Specification
Module: contracts.sandbox_interface

Defines the contract for isolated Docker sandboxes and terminal operators.
Enforces non-root execution, read-only root filesystems, atomic writes,
and deterministic rollback boundaries.
"""

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class CommandExecutionResult(BaseModel):
    """Output from an isolated container execution invocation."""
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False


class FileIntegrityCheck(BaseModel):
    """SHA-256 pre-condition validation for atomic file rewrites."""
    path: str
    expected_sha256: str
    actual_sha256: str
    matches: bool


class ISandboxRuntime(ABC):
    """
    Contract interface for container runtime isolation.
    Guarantees container containment, network policy enforcement,
    and rollback snapshot management.
    """

    @abstractmethod
    async def initialize_workspace(self, commit_sha: str) -> None:
        """Mounts immutable snapshot of repository at commit_sha into /workspace."""
        pass

    @abstractmethod
    async def execute_command(
        self,
        cmd: list[str],
        timeout_seconds: int = 180,
        enable_network: bool = False,
    ) -> CommandExecutionResult:
        """Executes a command inside the container under non-root permissions."""
        pass

    @abstractmethod
    async def verify_and_write_file(
        self,
        rel_path: str,
        expected_sha256: str,
        new_content: str,
    ) -> bool:
        """
        Atomically replaces target file if and only if existing content matches expected_sha256.
        Triggers automatic snapshot rollback upon mismatch or failure.
        """
        pass

    @abstractmethod
    async def compute_workspace_diff(self) -> str:
        """Generates unified diff comparing modified workspace to clean baseline."""
        pass

    @abstractmethod
    async def teardown(self) -> None:
        """Destroys container, ephemeral volumes, and transient bridges."""
        pass
