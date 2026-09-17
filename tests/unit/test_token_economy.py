"""Tests for ACRA Phase 7: Hierarchical Budget Governance & Provenance.

Verifies:
- INV-004: Mandatory EpistemicStatus on every provenance entry.
- INV-005: Hierarchical budget cascade ceiling and recursive upward consumption.
- INV-006: Explicit measured vs estimated token labeling.
- INV-010: Cache hysteresis and continuity vs migration cost model.
- R-010: Hierarchical budget governance (session -> objective -> task -> agent).
- R-012: Complete provenance tracking.
- R-023: Continuity vs migration cost tradeoffs.
- 20 Cognitive degradation & quality metrics (§17 EVO ACRA.md).
- Legacy ResourceGovernor backward compatibility.
"""

from __future__ import annotations

import pytest
from src.core.contracts.audit import EpistemicStatus
from src.core.contracts.context import ContextBudget
from src.core.economy.engine import (
    TokenEconomyEngine,
    BudgetExceededError,
)
from src.core.economy.cost_model import (
    ContinuityCostModel,
    MigrationTradeoffAssessment,
)
from src.core.economy.telemetry import (
    ProvenanceTracker,
    ProvenanceRecord,
)
from src.core.governance import ResourceGovernor, ResourceUsage
from src.core.metrics import ACRAMetrics, CognitiveDegradationReport


# ---------------------------------------------------------------------------
# Test 1: Hierarchical Budget Cascade (INV-005, INV-006)
# ---------------------------------------------------------------------------
class TestHierarchicalBudgetCascade:
    def test_budget_cascade_allocation_ceiling(self):
        """INV-005: Child budget allocation cannot exceed parent's remaining capacity."""
        engine = TokenEconomyEngine()

        # Root session budget: 10,000 tokens, $1.00
        session_b = ContextBudget(max_tokens=10000, max_cost_usd=1.00)
        engine.register_budget("session_root", session_b)

        # Valid child objective budget: 6,000 tokens, $0.50
        obj_b = ContextBudget(max_tokens=6000, max_cost_usd=0.50)
        engine.register_budget("obj_1", obj_b, parent_id="session_root")

        # Second child requesting 5,000 tokens (remaining in session is 10,000, but unallocated ceiling)
        # However if a child requests 15,000 tokens > session max_tokens, must raise BudgetExceededError
        oversubscribed_b = ContextBudget(max_tokens=15000, max_cost_usd=0.50)
        with pytest.raises(BudgetExceededError) as exc_info:
            engine.register_budget("obj_too_big", oversubscribed_b, parent_id="session_root")
        assert "INV-005 Violation" in str(exc_info.value)

    def test_hierarchical_consumption_propagates_upward(self):
        """Consumption at leaf agent propagates upward across task, objective, and session."""
        engine = TokenEconomyEngine()

        # Session -> Objective -> Task -> Agent
        engine.register_budget("sess", ContextBudget(max_tokens=10000, max_cost_usd=2.00))
        engine.register_budget("obj", ContextBudget(max_tokens=5000, max_cost_usd=1.00), parent_id="sess")
        engine.register_budget("task", ContextBudget(max_tokens=3000, max_cost_usd=0.50), parent_id="obj")
        engine.register_budget("agent", ContextBudget(max_tokens=1500, max_cost_usd=0.25), parent_id="task")

        # Consume 500 tokens at agent level
        updated_agent = engine.record_consumption(
            entity_id="agent",
            tokens=500,
            cost_usd=0.05,
            is_measured=True,
        )
        assert updated_agent.consumed_tokens == 500
        assert updated_agent.remaining_tokens() == 1000

        # Verify all ancestors reflected the 500 tokens
        assert engine.get_budget("task").consumed_tokens == 500
        assert engine.get_budget("obj").consumed_tokens == 500
        assert engine.get_budget("sess").consumed_tokens == 500

        # Further consumption of 1,200 tokens at agent breaches agent ceiling (1500 max)
        with pytest.raises(BudgetExceededError) as exc_info:
            engine.record_consumption(entity_id="agent", tokens=1200, cost_usd=0.10)
        assert "Budget exceeded at 'agent'" in str(exc_info.value)

    def test_measured_vs_estimated_token_discrimination(self):
        """INV-006: Measured vs estimated tokens are discriminated cleanly."""
        engine = TokenEconomyEngine()
        engine.register_budget("agent_1", ContextBudget(max_tokens=5000))

        # Measured tokens (e.g. from provider response usage)
        engine.record_consumption("agent_1", tokens=800, is_measured=True)
        # Estimated tokens (e.g. heuristic token counter before dispatch)
        engine.record_consumption("agent_1", tokens=350, is_measured=False)

        breakdown = engine.get_token_breakdown("agent_1")
        assert breakdown["measured_tokens"] == 800
        assert breakdown["estimated_tokens"] == 350
        assert breakdown["total_tokens"] == 1150

    def test_reservation_and_commit_lifecycle(self):
        """Budget reservation holds capacity and commits actual consumption."""
        engine = TokenEconomyEngine()
        engine.register_budget("agent_res", ContextBudget(max_tokens=2000, max_cost_usd=0.50))

        res_id = engine.reserve("agent_res", tokens=1000, cost_usd=0.20)
        assert res_id.startswith("res_")

        # Commit with actual consumption (900 tokens)
        updated = engine.commit_reservation(
            reservation_id=res_id,
            actual_tokens=900,
            actual_cost_usd=0.18,
            is_measured=True,
        )
        assert updated.consumed_tokens == 900
        assert updated.remaining_tokens() == 1100


# ---------------------------------------------------------------------------
# Test 2: Continuity vs Migration Cost Model (R-023, INV-010)
# ---------------------------------------------------------------------------
class TestContinuityCostModel:
    def test_continuity_savings_calculation(self):
        """Verify USD savings calculated from cached prefix tokens."""
        # 100,000 cached tokens at $1.00/M uncached vs $0.50/M cached rate
        savings = ContinuityCostModel.calculate_continuity_savings(
            cached_tokens=100_000,
            uncached_cost_per_million=1.00,
            cached_cost_per_million=0.50,
        )
        # Cost without cache = 0.10, with cache = 0.05 -> savings = 0.05
        assert pytest.approx(savings, 0.001) == 0.05

    def test_migration_penalty_calculation(self):
        """Verify rebuild token overhead and latency penalty."""
        penalty = ContinuityCostModel.calculate_migration_penalty(
            rebuild_tokens=50_000,
            target_model_cost_per_million=2.00,
            latency_overhead_ms=200.0,
        )
        # 50,000 tokens * $2.00 / 1M = $0.10
        assert pytest.approx(penalty["rebuild_cost_usd"], 0.001) == 0.10
        assert penalty["latency_penalty_ms"] == 200.0

    def test_tradeoff_recommends_staying_when_capability_gain_low(self):
        """INV-010: Cache hysteresis recommends staying when migration has no ROI."""
        assessment = ContinuityCostModel.evaluate_migration_tradeoff(
            active_model_cost_per_million=1.00,
            target_model_cost_per_million=3.00,
            cached_prefix_tokens=40_000,
            new_prompt_tokens=5_000,
            expected_output_tokens=1_000,
            target_capability_gain=0.10,  # Marginal gain
        )
        assert assessment.recommend_migration is False
        assert "favor remaining on active model" in assessment.justification
        assert assessment.epistemic_status == EpistemicStatus.ESTIMATED

    def test_tradeoff_recommends_migration_when_capability_gain_high(self):
        """High capability differential justifies migration cost."""
        assessment = ContinuityCostModel.evaluate_migration_tradeoff(
            active_model_cost_per_million=1.00,
            target_model_cost_per_million=3.00,
            cached_prefix_tokens=40_000,
            new_prompt_tokens=5_000,
            expected_output_tokens=1_000,
            target_capability_gain=0.75,  # Substantial capability gain
        )
        assert assessment.recommend_migration is True
        assert "Capability gain" in assessment.justification


# ---------------------------------------------------------------------------
# Test 3: Provenance Tracker & Epistemic Status (INV-004, INV-006)
# ---------------------------------------------------------------------------
class TestProvenanceTracker:
    def test_provenance_recording_enforces_epistemic_status(self):
        """INV-004: All provenance records declare epistemic status."""
        tracker = ProvenanceTracker()

        rec = tracker.record(
            session_id="sess_prov_001",
            agent_id="inst_agent_alpha",
            model_profile_id="fast_reasoner",
            provider_id="stub_provider",
            epistemic_status=EpistemicStatus.MEASURED,
            tokens_consumed=450,
            is_measured_tokens=True,
            cost_usd=0.0045,
            tool_calls=["search_kb"],
        )
        assert rec.epistemic_status == EpistemicStatus.MEASURED
        assert rec.record_id.startswith("prov_")

        # Verify integrity
        assert tracker.verify_chain_epistemic_integrity("sess_prov_001") is True

    def test_provenance_session_summary_aggregates_metrics(self):
        """Session summary aggregates measured vs estimated tokens and epistemic distribution."""
        tracker = ProvenanceTracker()
        sess_id = "sess_prov_agg"

        tracker.record(
            session_id=sess_id,
            agent_id="agent_1",
            model_profile_id="p1",
            provider_id="prov_1",
            epistemic_status=EpistemicStatus.MEASURED,
            tokens_consumed=300,
            is_measured_tokens=True,
            cost_usd=0.01,
            tool_calls=["tool_a"],
        )
        tracker.record(
            session_id=sess_id,
            agent_id="agent_2",
            model_profile_id="p2",
            provider_id="prov_1",
            epistemic_status=EpistemicStatus.ESTIMATED,
            tokens_consumed=200,
            is_measured_tokens=False,
            cost_usd=0.005,
            tool_calls=["tool_b"],
        )

        summary = tracker.get_session_summary(sess_id)
        assert summary["record_count"] == 2
        assert summary["total_tokens_measured"] == 300
        assert summary["total_tokens_estimated"] == 200
        assert summary["total_tokens"] == 500
        assert pytest.approx(summary["total_cost_usd"], 0.0001) == 0.015
        assert summary["tools_invoked"] == ["tool_a", "tool_b"]
        assert summary["epistemic_distribution"]["MEASURED"] == 1
        assert summary["epistemic_distribution"]["ESTIMATED"] == 1


# ---------------------------------------------------------------------------
# Test 4: 20 Degradation & Quality Metrics (§17 EVO ACRA.md)
# ---------------------------------------------------------------------------
class TestTwentyCognitiveMetrics:
    def test_all_twenty_metrics_computed_with_epistemic_status(self):
        """Verify all 20 metrics exist and declare valid EpistemicStatus."""
        report: CognitiveDegradationReport = ACRAMetrics.evaluate_cognitive_degradation_report(
            context_risk_score=0.08,
            evidence_coverage=0.92,
            context_utilization_ratio=0.88,
            context_reuse_ratio=0.65,
            provider_reported_cache_hit_ratio=0.70,
            estimated_cache_reuse_ratio=0.68,
            context_rebuild_tokens=150,
            effective_cost_per_validated_task=0.015,
            tokens_per_validated_outcome=980,
            model_switch_count=2,
            provider_switch_count=1,
            avoidable_model_switch_rate=0.05,
            cache_break_even_accuracy=0.93,
            context_compaction_regret=0.01,
            routing_regret=0.005,
            retry_amplification=1.1,
            handoff_expansion_ratio=1.02,
            stale_tool_result_rate=0.0,
            cross_domain_leakage_rate=0.0,
            agent_context_contamination_rate=0.0,
        )

        # 1. context_risk_score
        assert report.context_risk_score.value == 0.08
        assert report.context_risk_score.epistemic_status == EpistemicStatus.VERIFIED

        # 2. evidence_coverage
        assert report.evidence_coverage.value == 0.92
        assert report.evidence_coverage.epistemic_status == EpistemicStatus.MEASURED

        # 3. context_utilization_ratio
        assert report.context_utilization_ratio.value == 0.88
        assert report.context_utilization_ratio.epistemic_status == EpistemicStatus.MEASURED

        # 4. context_reuse_ratio
        assert report.context_reuse_ratio.value == 0.65
        assert report.context_reuse_ratio.epistemic_status == EpistemicStatus.PROVIDER_REPORTED

        # 5. provider_reported_cache_hit_ratio
        assert report.provider_reported_cache_hit_ratio.value == 0.70
        assert report.provider_reported_cache_hit_ratio.epistemic_status == EpistemicStatus.PROVIDER_REPORTED

        # 6. estimated_cache_reuse_ratio
        assert report.estimated_cache_reuse_ratio.value == 0.68
        assert report.estimated_cache_reuse_ratio.epistemic_status == EpistemicStatus.ESTIMATED

        # 7. context_rebuild_tokens
        assert report.context_rebuild_tokens.value == 150.0
        assert report.context_rebuild_tokens.epistemic_status == EpistemicStatus.MEASURED

        # 8. effective_cost_per_validated_task
        assert report.effective_cost_per_validated_task.value == 0.015
        assert report.effective_cost_per_validated_task.epistemic_status == EpistemicStatus.MEASURED

        # 9. tokens_per_validated_outcome
        assert report.tokens_per_validated_outcome.value == 980.0
        assert report.tokens_per_validated_outcome.epistemic_status == EpistemicStatus.MEASURED

        # 10. model_switch_count
        assert report.model_switch_count.value == 2.0
        assert report.model_switch_count.epistemic_status == EpistemicStatus.MEASURED

        # 11. provider_switch_count
        assert report.provider_switch_count.value == 1.0
        assert report.provider_switch_count.epistemic_status == EpistemicStatus.MEASURED

        # 12. avoidable_model_switch_rate
        assert report.avoidable_model_switch_rate.value == 0.05
        assert report.avoidable_model_switch_rate.epistemic_status == EpistemicStatus.INFERRED

        # 13. cache_break_even_accuracy
        assert report.cache_break_even_accuracy.value == 0.93
        assert report.cache_break_even_accuracy.epistemic_status == EpistemicStatus.ESTIMATED

        # 14. context_compaction_regret
        assert report.context_compaction_regret.value == 0.01
        assert report.context_compaction_regret.epistemic_status == EpistemicStatus.INFERRED

        # 15. routing_regret
        assert report.routing_regret.value == 0.005
        assert report.routing_regret.epistemic_status == EpistemicStatus.INFERRED

        # 16. retry_amplification
        assert report.retry_amplification.value == 1.1
        assert report.retry_amplification.epistemic_status == EpistemicStatus.MEASURED

        # 17. handoff_expansion_ratio
        assert report.handoff_expansion_ratio.value == 1.02
        assert report.handoff_expansion_ratio.epistemic_status == EpistemicStatus.MEASURED

        # 18. stale_tool_result_rate
        assert report.stale_tool_result_rate.value == 0.0
        assert report.stale_tool_result_rate.epistemic_status == EpistemicStatus.MEASURED

        # 19. cross_domain_leakage_rate
        assert report.cross_domain_leakage_rate.value == 0.0
        assert report.cross_domain_leakage_rate.epistemic_status == EpistemicStatus.MEASURED

        # 20. agent_context_contamination_rate
        assert report.agent_context_contamination_rate.value == 0.0
        assert report.agent_context_contamination_rate.epistemic_status == EpistemicStatus.INFERRED


# ---------------------------------------------------------------------------
# Test 5: Legacy ResourceGovernor Backward Compatibility
# ---------------------------------------------------------------------------
class TestResourceGovernorCompatibility:
    def test_legacy_governor_enforces_limits(self):
        """Ensure ResourceGovernor continues functioning and raises BudgetExceededError."""
        gov = ResourceGovernor(
            max_turns_per_session=3,
            max_tokens_per_session=1000,
            max_cost_usd_per_session=0.05,
        )
        session_id = "legacy_session_001"

        # Turn 1: 300 tokens, $0.01
        u1 = gov.check_and_record(session_id, tokens_added=300, cost_added_usd=0.01)
        assert u1.turns_count == 1
        assert u1.total_tokens_consumed == 300

        # Turn 2: 400 tokens, $0.01
        u2 = gov.check_and_record(session_id, tokens_added=400, cost_added_usd=0.01)
        assert u2.turns_count == 2
        assert u2.total_tokens_consumed == 700

        # Turn 3: 400 tokens -> exceeds 1000 token limit
        with pytest.raises(BudgetExceededError) as exc_info:
            gov.check_and_record(session_id, tokens_added=400, cost_added_usd=0.01)
        assert "exceeded token limit" in str(exc_info.value)
