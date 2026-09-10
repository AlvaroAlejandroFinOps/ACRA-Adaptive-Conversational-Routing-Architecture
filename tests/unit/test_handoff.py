import pytest
from src.core.handoff import HandoffEngine
from src.core.edge_router import RouterDecision, RouterAction
from src.core.dhc import CompressedContext


def test_handoff_assembles_sterilized_payload():
    engine = HandoffEngine(enforce_sterilization=True)
    decision = RouterDecision(
        action=RouterAction.DISPATCH_PRO,
        maturity_score=0.88,
        target_cluster="pro",
        reasoning="Ready for deep reasoning execution",
        active_turn=3,
    )
    compressed = CompressedContext(
        raw_tokens_estimate=350,
        consolidated_tokens_estimate=120,
        ccr=0.65,
        purged_chatter_count=3,
        consolidated_user_requirements=["Requirement 1", "Requirement 2"],
        crystallized_code_artifacts=[],
        clean_history_prompt="1. Req 1\n2. Req 2",
    )

    payload = engine.assemble_clean_payload("session_123", decision, compressed)
    assert payload.target_cluster == "pro"
    assert payload.is_sterilized is True
    assert "CONSOLIDATED EXECUTION CANVAS" in payload.prefill_prompt
    assert payload.ccr == 0.65
