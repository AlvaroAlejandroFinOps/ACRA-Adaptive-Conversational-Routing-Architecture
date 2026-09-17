"""ACRA Context Contracts.

Defines ContextCapsule, ContextBudget, StablePrefixDescriptor, and ToolResult.
ContextCapsule is the isolated context envelope for agent instances (INV-003, INV-009).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContextBudget(BaseModel):
    """Hierarchical resource and context budget."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_tokens: int = Field(default=8000, ge=1, description="Maximum total tokens allowed")
    max_turns: int = Field(default=10, ge=1, description="Maximum inference/interaction turns allowed")
    max_cost_usd: float = Field(default=0.50, ge=0.0, description="Maximum cost budget in USD")
    max_wall_clock_seconds: int = Field(default=300, ge=1, description="Timeout in wall-clock seconds")
    consumed_tokens: int = Field(default=0, ge=0, description="Tokens consumed so far")
    consumed_cost_usd: float = Field(default=0.0, ge=0.0, description="Cost accumulated so far in USD")

    def remaining_tokens(self) -> int:
        """Remaining tokens in budget."""
        return max(0, self.max_tokens - self.consumed_tokens)

    def remaining_cost_usd(self) -> float:
        """Remaining monetary budget."""
        return max(0.0, self.max_cost_usd - self.consumed_cost_usd)

    def is_exhausted(self) -> bool:
        """Check if any budget dimension is exhausted."""
        return self.consumed_tokens >= self.max_tokens or self.consumed_cost_usd >= self.max_cost_usd


class StablePrefixDescriptor(BaseModel):
    """Descriptor for prefix caching and prompt stabilization."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    prefix_id: str = Field(..., description="Unique identifier for stable prefix")
    content_hash: str = Field(..., description="SHA-256 hash of immutable prefix content")
    version: int = Field(default=1, ge=1, description="Monotonically increasing version")
    token_count: int = Field(default=0, ge=0, description="Token length of prefix")
    system_instruction_hash: str = Field(..., description="Hash of system instruction text")
    tool_manifest_hash: str = Field(..., description="Hash of tool schema definitions")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")


class ToolResult(BaseModel):
    """Result of a tool execution within an agent turn."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    tool_name: str = Field(..., description="Name of executed tool")
    call_id: str = Field(..., description="Correlation ID of the tool call")
    status: str = Field(..., description="Execution status: SUCCESS, ERROR, TIMEOUT")
    content: str = Field(..., description="Serialized tool output or error message")
    content_hash: str = Field(..., description="Digest of tool response content")
    execution_time_ms: int = Field(default=0, ge=0, description="Execution duration in milliseconds")
    is_stale: bool = Field(default=False, description="True if output is invalidated by subsequent actions")


class ContextCapsule(BaseModel):
    """Isolated, scoped context envelope for an agent instance.

    Guarantees strict domain isolation (INV-003) and bounded context inheritance (INV-009).
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    capsule_id: str = Field(..., description="Unique capsule UUID")
    agent_instance_id: str = Field(..., description="Owner agent instance ID")
    domain: str = Field(..., description="Domain boundary (e.g., 'security', 'billing')")
    stable_prefix: StablePrefixDescriptor = Field(..., description="Immutable cached prefix descriptor")
    domain_context: str = Field(default="", description="Domain-specific policies and knowledge")
    task_context: str = Field(default="", description="Task-specific instructions and goals")
    volatile_tool_state: list[ToolResult] = Field(default_factory=list, description="Recent tool results")
    current_turn: str = Field(default="", description="Active user or system prompt for this turn")
    output_contract: str = Field(default="json", description="Target output schema/format")
    capsule_hash: str = Field(default="", description="Integrity digest of capsule contents")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp created")
    expires_at: datetime | None = Field(default=None, description="TTL expiration timestamp")
    is_sealed: bool = Field(default=False, description="Whether capsule is locked against further edits")
    parent_capsule_id: str | None = Field(default=None, description="Parent capsule if forked")

    @classmethod
    def compute_hash(cls, domain: str, stable_prefix_hash: str, domain_context: str, task_context: str, current_turn: str) -> str:
        """Compute cryptographic hash of capsule semantic contents."""
        hasher = hashlib.sha256()
        hasher.update(domain.encode("utf-8"))
        hasher.update(stable_prefix_hash.encode("utf-8"))
        hasher.update(domain_context.encode("utf-8"))
        hasher.update(task_context.encode("utf-8"))
        hasher.update(current_turn.encode("utf-8"))
        return hasher.hexdigest()

    def fork(self, new_instance_id: str, new_domain: str, whitelisted_task_context: str) -> ContextCapsule:
        """Fork a new capsule inheriting only whitelisted context (INV-009).

        Never copies volatile tool states, raw turns, or cross-domain context.
        """
        now = datetime.now(timezone.utc)
        new_hash = self.compute_hash(
            domain=new_domain,
            stable_prefix_hash=self.stable_prefix.content_hash,
            domain_context="",  # Isolated from parent domain
            task_context=whitelisted_task_context,
            current_turn="",
        )
        return ContextCapsule(
            capsule_id=f"cap_fork_{now.strftime('%Y%m%d%H%M%S')}_{new_instance_id[:8]}",
            agent_instance_id=new_instance_id,
            domain=new_domain,
            stable_prefix=self.stable_prefix,
            domain_context="",
            task_context=whitelisted_task_context,
            volatile_tool_state=[],
            current_turn="",
            output_contract=self.output_contract,
            capsule_hash=new_hash,
            created_at=now,
            expires_at=self.expires_at,
            is_sealed=False,
            parent_capsule_id=self.capsule_id,
        )
