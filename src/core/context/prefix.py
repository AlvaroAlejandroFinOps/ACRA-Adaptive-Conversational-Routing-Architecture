"""ACRA Stable Prefix Engine.

Implements prefix caching preparation and stability tracking (R-024).
Maintains immutable prefixes and generates CacheInvalidationEvents upon mutation.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from src.core.contracts.cache import CacheInvalidationEvent
from src.core.contracts.context import StablePrefixDescriptor


class StablePrefixEngine:
    """Engine responsible for computing, caching, and tracking stable prompt prefixes."""

    def __init__(self) -> None:
        self._prefix_cache: dict[str, StablePrefixDescriptor] = {}
        self._invalidation_history: list[CacheInvalidationEvent] = []

    @staticmethod
    def hash_text(text: str) -> str:
        """Return SHA-256 hash of text."""
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    @classmethod
    def hash_tool_manifest(cls, tools: list[dict[str, Any]] | list[Any]) -> str:
        """Compute canonical digest of tool schemas."""
        serialized = json.dumps(
            [t if isinstance(t, dict) else getattr(t, "__dict__", str(t)) for t in tools],
            sort_keys=True,
            default=str,
        )
        return cls.hash_text(serialized)

    def build_prefix(
        self,
        prefix_id: str,
        system_instruction: str,
        tool_manifest: list[dict[str, Any]] | list[Any],
        estimated_token_count: int = 0,
    ) -> StablePrefixDescriptor:
        """Create or update a StablePrefixDescriptor, tracking version bumps and invalidations."""
        sys_hash = self.hash_text(system_instruction)
        tools_hash = self.hash_tool_manifest(tool_manifest)
        combined_content = f"SYS:{sys_hash}|TOOLS:{tools_hash}"
        content_hash = self.hash_text(combined_content)

        existing = self._prefix_cache.get(prefix_id)
        version = 1
        if existing:
            if existing.content_hash != content_hash:
                version = existing.version + 1
                invalidation = CacheInvalidationEvent(
                    event_id=f"inv_{prefix_id}_v{version}",
                    prefix_hash=existing.content_hash,
                    reason=f"Prefix '{prefix_id}' modified (version bumped to {version})",
                    timestamp=datetime.now(timezone.utc),
                )
                self._invalidation_history.append(invalidation)
            else:
                return existing

        descriptor = StablePrefixDescriptor(
            prefix_id=prefix_id,
            content_hash=content_hash,
            version=version,
            token_count=estimated_token_count,
            system_instruction_hash=sys_hash,
            tool_manifest_hash=tools_hash,
            created_at=datetime.now(timezone.utc),
        )

        self._prefix_cache[prefix_id] = descriptor
        return descriptor

    def get_invalidation_events(self) -> list[CacheInvalidationEvent]:
        """Retrieve recorded prefix invalidation events."""
        return list(self._invalidation_history)
