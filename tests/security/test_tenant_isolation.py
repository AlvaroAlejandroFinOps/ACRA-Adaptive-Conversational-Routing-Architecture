"""
Security Test Suite: Multi-Tenant Isolation & Cross-Session Leakage Prevention.
Verifies snapshots and cache entries from Tenant A are completely inaccessible to Tenant B.
"""

import pytest
from src.core.unified_context import UnifiedContextTier
from src.core.dhc import DynamicHistoryCompressor
from src.core.edge_router import MessageTurn, TurnRole


class TestTenantIsolation:

    def test_tenant_cannot_read_another_tenants_snapshot(self):
        uct = UnifiedContextTier()
        compressor = DynamicHistoryCompressor()
        shared_session_id = "colliding_session_id_001"

        history_a = [MessageTurn(role=TurnRole.USER, content="Confidential Tenant A data", turn_index=1)]
        compressed_a = compressor.compress(history_a, "Tenant A requirement")
        uct.persist_snapshot(shared_session_id, 1, compressed_a, tenant_id="tenant_alpha")

        history_b = [MessageTurn(role=TurnRole.USER, content="Tenant B public request", turn_index=1)]
        compressed_b = compressor.compress(history_b, "Tenant B requirement")
        uct.persist_snapshot(shared_session_id, 1, compressed_b, tenant_id="tenant_beta")

        # Tenant Alpha should get Tenant Alpha data
        snap_a = uct.get_latest_snapshot(shared_session_id, tenant_id="tenant_alpha")
        assert snap_a is not None
        assert "Confidential Tenant A" in snap_a.prefill_ready_text

        # Tenant Beta should get Tenant Beta data, NOT Alpha's
        snap_b = uct.get_latest_snapshot(shared_session_id, tenant_id="tenant_beta")
        assert snap_b is not None
        assert "Confidential Tenant A" not in snap_b.prefill_ready_text
        assert "Tenant B public" in snap_b.prefill_ready_text

        # Tenant Gamma (unrelated) querying the same session should get None
        snap_gamma = uct.get_latest_snapshot(shared_session_id, tenant_id="tenant_gamma")
        assert snap_gamma is None

    def test_cache_keys_are_cryptographically_separated_by_tenant(self):
        uct = UnifiedContextTier()
        compressor = DynamicHistoryCompressor()
        session_id = "test_sess"
        history = [MessageTurn(role=TurnRole.USER, content="Identical content", turn_index=1)]
        compressed = compressor.compress(history, "Identical current")

        snap_a = uct.persist_snapshot(session_id, 1, compressed, tenant_id="tenant_1")
        snap_b = uct.persist_snapshot(session_id, 1, compressed, tenant_id="tenant_2")

        assert snap_a.cache_key != snap_b.cache_key
        assert snap_a.tenant_id == "tenant_1"
        assert snap_b.tenant_id == "tenant_2"
