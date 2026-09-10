"""
Security Test Suite: Memory Poisoning Mitigation & Snapshot Revocation.
Verifies UCT prevents poisoned context reuse and supports dynamic snapshot revocation.
"""

import pytest
from src.core.unified_context import UnifiedContextTier
from src.core.dhc import DynamicHistoryCompressor
from src.core.edge_router import MessageTurn, TurnRole


class TestMemoryPoisoningMitigation:

    def test_revocation_prevents_cache_hits(self):
        uct = UnifiedContextTier()
        compressor = DynamicHistoryCompressor()
        session_id = "poison-sess-01"

        history = [
            MessageTurn(role=TurnRole.USER, content="Clean request 1", turn_index=1),
        ]
        compressed = compressor.compress(history, "Clean current")
        snapshot = uct.persist_snapshot(session_id, 1, compressed)

        # Snapshot is active
        retrieved = uct.get_latest_snapshot(session_id)
        assert retrieved is not None
        assert retrieved.snapshot_id == snapshot.snapshot_id

        # Revoke snapshot due to suspected memory poisoning
        revoked = uct.revoke_snapshot(session_id, reason="Adversarial manipulation detected")
        assert revoked is True
        assert uct.is_revoked(session_id) is True

        # Subsequent retrieval should fail / return None
        retrieved_after = uct.get_latest_snapshot(session_id)
        assert retrieved_after is None

        stats = uct.get_cache_stats()
        assert stats["revocations"] == 1

    def test_salt_changes_cache_key_for_identical_content(self):
        uct1 = UnifiedContextTier(salt="salt_alpha")
        uct2 = UnifiedContextTier(salt="salt_beta")
        compressor = DynamicHistoryCompressor()

        history = [MessageTurn(role=TurnRole.USER, content="Target test", turn_index=1)]
        compressed = compressor.compress(history, "Target current")

        snap1 = uct1.persist_snapshot("session_x", 1, compressed)
        snap2 = uct2.persist_snapshot("session_x", 1, compressed)

        assert snap1.cache_key != snap2.cache_key
