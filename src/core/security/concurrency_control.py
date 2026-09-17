"""ACRA Concurrency Control and Optimistic Locking.

Implements version-based conflict detection for shared state across concurrent agents,
and idempotency registration for deduplicating task and handoff dispatches.
"""

from __future__ import annotations

import threading
from typing import Any


class VersionConflictError(Exception):
    """Raised when an optimistic lock check fails due to concurrent modification."""
    pass


class OptimisticLockManager:
    """Manages versioned entities and provides optimistic locking and idempotency deduplication."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._versions: dict[str, int] = {}
        self._data: dict[str, Any] = {}
        self._idempotency_registry: dict[str, Any] = {}

    def get_version(self, entity_id: str) -> int:
        """Get current version number of an entity (defaults to 0 if untracked)."""
        with self._lock:
            return self._versions.get(entity_id, 0)

    def get_data(self, entity_id: str) -> Any | None:
        """Get stored data for an entity."""
        with self._lock:
            return self._data.get(entity_id)

    def commit(self, entity_id: str, expected_version: int, new_data: Any) -> int:
        """Atomically commit update if expected_version matches current version.

        Raises:
            VersionConflictError: If current version does not equal expected_version.

        Returns:
            int: The new incremented version.
        """
        with self._lock:
            current_version = self._versions.get(entity_id, 0)
            if current_version != expected_version:
                raise VersionConflictError(
                    f"Optimistic lock conflict on entity '{entity_id}': expected v{expected_version}, found v{current_version}"
                )

            new_version = current_version + 1
            self._versions[entity_id] = new_version
            self._data[entity_id] = new_data
            return new_version

    def register_idempotency_key(self, key: str, result: Any) -> bool:
        """Register an idempotency key.

        Returns:
            bool: True if key was newly registered, False if duplicate was detected.
        """
        with self._lock:
            if key in self._idempotency_registry:
                return False
            self._idempotency_registry[key] = result
            return True

    def get_idempotent_result(self, key: str) -> Any | None:
        """Retrieve stored result for a previously processed idempotency key."""
        with self._lock:
            return self._idempotency_registry.get(key)

    def clear(self) -> None:
        """Reset all tracked state and idempotency keys."""
        with self._lock:
            self._versions.clear()
            self._data.clear()
            self._idempotency_registry.clear()
