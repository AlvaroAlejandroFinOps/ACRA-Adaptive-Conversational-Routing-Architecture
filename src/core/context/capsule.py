"""ACRA Context Capsule Builder and Integrity Verifier.

Manages assembly, mutation restrictions, hash sealing, and domain isolation for ContextCapsule.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from src.core.contracts.context import (
    ContextCapsule,
    StablePrefixDescriptor,
    ToolResult,
)


class CapsuleSealedError(Exception):
    """Raised when an edit is attempted on an already sealed ContextCapsule."""
    pass


class ContextCapsuleBuilder:
    """Builder pattern for constructing sealed ContextCapsules."""

    def __init__(
        self,
        agent_instance_id: str,
        domain: str,
        stable_prefix: StablePrefixDescriptor,
        capsule_id: str | None = None,
    ) -> None:
        self.capsule_id = capsule_id or f"cap_{uuid.uuid4().hex[:12]}"
        self.agent_instance_id = agent_instance_id
        self.domain = domain
        self.stable_prefix = stable_prefix
        self.domain_context: str = ""
        self.task_context: str = ""
        self.volatile_tool_state: list[ToolResult] = []
        self.current_turn: str = ""
        self.output_contract: str = "json"
        self.expires_at: datetime | None = None
        self.parent_capsule_id: str | None = None

    def set_domain_context(self, context_text: str) -> ContextCapsuleBuilder:
        """Set domain-specific guidelines and policies."""
        self.domain_context = context_text.strip()
        return self

    def set_task_context(self, task_text: str) -> ContextCapsuleBuilder:
        """Set task objective instructions."""
        self.task_context = task_text.strip()
        return self

    def add_tool_result(self, tool_result: ToolResult) -> ContextCapsuleBuilder:
        """Add a tool output result."""
        self.volatile_tool_state.append(tool_result)
        return self

    def set_current_turn(self, turn_text: str) -> ContextCapsuleBuilder:
        """Set active prompt turn."""
        self.current_turn = turn_text.strip()
        return self

    def set_output_contract(self, contract_name: str) -> ContextCapsuleBuilder:
        """Set target output schema/format."""
        self.output_contract = contract_name
        return self

    def set_expiration(self, expires_at: datetime) -> ContextCapsuleBuilder:
        """Set TTL expiration timestamp."""
        self.expires_at = expires_at
        return self

    def set_parent(self, parent_id: str) -> ContextCapsuleBuilder:
        """Set parent capsule ID."""
        self.parent_capsule_id = parent_id
        return self

    def prune_stale_tools(self) -> ContextCapsuleBuilder:
        """Remove tool results marked as stale or superseded."""
        self.volatile_tool_state = [t for t in self.volatile_tool_state if not t.is_stale]
        return self

    def build_and_seal(self) -> ContextCapsule:
        """Seal capsule with cryptographic hash and return frozen ContextCapsule."""
        content_hash = ContextCapsule.compute_hash(
            domain=self.domain,
            stable_prefix_hash=self.stable_prefix.content_hash,
            domain_context=self.domain_context,
            task_context=self.task_context,
            current_turn=self.current_turn,
        )

        return ContextCapsule(
            capsule_id=self.capsule_id,
            agent_instance_id=self.agent_instance_id,
            domain=self.domain,
            stable_prefix=self.stable_prefix,
            domain_context=self.domain_context,
            task_context=self.task_context,
            volatile_tool_state=list(self.volatile_tool_state),
            current_turn=self.current_turn,
            output_contract=self.output_contract,
            capsule_hash=content_hash,
            created_at=datetime.now(timezone.utc),
            expires_at=self.expires_at,
            is_sealed=True,
            parent_capsule_id=self.parent_capsule_id,
        )

    @staticmethod
    def verify_integrity(capsule: ContextCapsule) -> bool:
        """Verify that capsule hash matches its semantic contents."""
        expected = ContextCapsule.compute_hash(
            domain=capsule.domain,
            stable_prefix_hash=capsule.stable_prefix.content_hash,
            domain_context=capsule.domain_context,
            task_context=capsule.task_context,
            current_turn=capsule.current_turn,
        )
        return expected == capsule.capsule_hash
