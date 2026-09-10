import pytest
from src.core.unified_context import UnifiedContextTier
from src.core.dhc import CompressedContext


def test_unified_context_tier_persists_and_retrieves():
    uct = UnifiedContextTier(ttl_seconds=10.0)
    mock_compressed = CompressedContext(
        raw_tokens_estimate=200,
        consolidated_tokens_estimate=90,
        ccr=0.55,
        purged_chatter_count=2,
        consolidated_user_requirements=["Requirement A", "Requirement B"],
        crystallized_code_artifacts=[],
        clean_history_prompt="### CONSOLIDATED USER REQUIREMENTS:\n1. Req A\n2. Req B",
    )

    snap = uct.persist_snapshot(
        session_id="session_test_01",
        total_turns=3,
        compressed_ctx=mock_compressed,
    )

    assert snap.session_id == "session_test_01"
    assert "ACRA CONSOLIDATED CONTEXT" in snap.prefill_ready_text

    retrieved = uct.get_latest_snapshot("session_test_01")
    assert retrieved is not None
    assert retrieved.snapshot_id == snap.snapshot_id

    stats = uct.get_cache_stats()
    assert stats["active_sessions"] == 1
    assert stats["cache_hits"] == 1
