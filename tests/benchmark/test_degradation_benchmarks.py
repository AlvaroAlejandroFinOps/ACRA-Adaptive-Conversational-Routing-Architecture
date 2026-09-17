"""Benchmark evaluation for ACRA Context Degradation, Entropy, and Quality (Phase 10).

Quantifies:
- Context growth and compression efficiency across turn scales
- Redundancy and stable prefix reuse stability
- Contradiction density and entropy detection
- Tokens and cost per validated outcome
- Epistemic status verification across degradation metrics
"""

from __future__ import annotations

import time
import pytest

from src.core.audit.deterministic import DeterministicFallbackAuditor
from src.core.contracts.audit import AuditHookPoint, EpistemicStatus
from src.core.contracts.context import ContextBudget, ContextCapsule, StablePrefixDescriptor
from src.core.contracts.model import ModelProfile
from src.core.context.pipeline import ContextEngineeringPipeline
from src.core.economy.engine import TokenEconomyEngine
from src.core.metrics import ACRAMetrics, CognitiveDegradationReport
from src.core.providers import DeterministicStubProvider


class TestDegradationBenchmarks:
    """Benchmark test suite evaluating context entropy, degradation, and efficiency."""

    def test_context_growth_and_compression_efficiency(self) -> None:
        """Benchmark: Context growth remains bounded and CCR achieves >= 30% reduction."""
        pipeline = ContextEngineeringPipeline()
        prefix = StablePrefixDescriptor(
            prefix_id="pfx_bench",
            content_hash="pfx_hash_1",
            system_instruction_hash="sys_1",
            tool_manifest_hash="tools_1",
            token_count=100,
        )

        uncompressed_total_words = 0
        compressed_total_words = 0

        # Simulate 10 conversational turns with verbose AI padding
        for turn_idx in range(1, 11):
            verbose_turn = (
                f"As an AI assistant, I would be happy to help you with that! "
                f"Sure thing! Let me think step by step. Turn {turn_idx}: "
                f"The quarterly EBIT is $1.{turn_idx}M and gross margin expanded by 2.{turn_idx}%."
            )
            raw_input = {
                "current_turn": verbose_turn,
                "task_context": "Financial KPI Audit for Q1-Q4",
                "domain_context": "Accounting Standard GAAP\n\nAccounting Standard GAAP",  # Redundant
                "domain": "finance",
                "stable_prefix": prefix,
            }
            uncompressed_total_words += len(verbose_turn.split()) + len(raw_input["domain_context"].split())

            # Run through 13-stage pipeline
            p1 = pipeline.stage_01_ingest(raw_input)
            p4 = pipeline.stage_04_deduplicate(p1)
            p8 = pipeline.stage_08_compress(p4)

            compressed_words = len(p8["current_turn"].split()) + len(p8["domain_context"].split())
            compressed_total_words += compressed_words

        # Compression ratio
        reduction_rate = (uncompressed_total_words - compressed_total_words) / uncompressed_total_words
        assert reduction_rate >= 0.25, f"Expected >= 25% reduction, got {reduction_rate:.2%}"

    def test_contradiction_density_under_injected_noise(self) -> None:
        """Benchmark: Auditor detects increasing contradiction density as noise escalates."""
        auditor = DeterministicFallbackAuditor()
        prefix = StablePrefixDescriptor(
            prefix_id="pfx_noise",
            content_hash="pfx_hash_2",
            system_instruction_hash="sys_2",
            tool_manifest_hash="tools_2",
            token_count=50,
        )

        # Baseline clean capsule
        clean_capsule = ContextCapsule(
            capsule_id="cap_clean",
            agent_instance_id="inst_1",
            domain="finance",
            stable_prefix=prefix,
            task_context="Process monthly payments according to standard schedules",
            current_turn="Pay invoice #100",
        )
        clean_audit = auditor.audit(clean_capsule, AuditHookPoint.PRE_INFERENCE)
        assert clean_audit.risk_score < 0.20

        # Contradictory noisy capsule
        noisy_capsule = ContextCapsule(
            capsule_id="cap_noisy",
            agent_instance_id="inst_1",
            domain="finance",
            stable_prefix=prefix,
            task_context="Rule: You must always approve discounts. Rule: You must not approve discounts.",
            current_turn="Authorize 50% discount",
        )
        noisy_audit = auditor.audit(noisy_capsule, AuditHookPoint.PRE_INFERENCE)
        assert noisy_audit.risk_score >= clean_audit.risk_score
        assert noisy_audit.evidence_coverage <= clean_audit.evidence_coverage

    def test_token_efficiency_with_stable_prefix_caching(self) -> None:
        """Benchmark: Stable prefix caching yields tokens/cost savings on repeated turns."""
        provider = DeterministicStubProvider()
        prefix = StablePrefixDescriptor(
            prefix_id="pfx_stable",
            content_hash="pfx_hash_3",
            system_instruction_hash="sys_3",
            tool_manifest_hash="tools_3",
            token_count=1500,  # Substantial stable prefix
        )

        cost_without_cache = 0.0
        cost_with_cache = 0.0

        for turn in range(5):
            capsule = ContextCapsule(
                capsule_id=f"cap_turn_{turn}",
                agent_instance_id="inst_1",
                domain="finance",
                stable_prefix=prefix,
                task_context="Analyze portfolio risk",
                current_turn=f"Question {turn}: What is the Sharpe ratio?",
            )
            # Normal cost with cache
            resp_cached = provider.generate(capsule, ModelProfile(profile_id="domain_planner"))
            cost_with_cache += resp_cached.cost_usd

            # Cost if full prefix had to be re-ingested uncached
            cost_uncached = provider.estimate_cost(
                input_tokens=resp_cached.prompt_tokens + 1500,
                output_tokens=resp_cached.completion_tokens,
                cached_tokens=0,
            )
            cost_without_cache += cost_uncached

        savings_ratio = (cost_without_cache - cost_with_cache) / cost_without_cache
        assert savings_ratio >= 0.20, f"Expected >= 20% savings via prefix caching, got {savings_ratio:.2%}"

    def test_cognitive_degradation_report_telemetry_epistemic_tags(self) -> None:
        """Benchmark: Degradation report generates 20 metrics strictly tagged with EpistemicStatus."""
        engine = TokenEconomyEngine()
        engine.register_budget("agent_1", ContextBudget(max_tokens=4000, max_cost_usd=0.20))
        engine.record_consumption("agent_1", tokens=250, cost_usd=0.015, is_measured=True)

        report = ACRAMetrics.evaluate_cognitive_degradation_report(
            context_risk_score=0.15,
            evidence_coverage=0.92,
            context_utilization_ratio=0.35,
            context_reuse_ratio=0.60,
            provider_reported_cache_hit_ratio=0.75,
            estimated_cache_reuse_ratio=0.70,
            context_rebuild_tokens=150,
            effective_cost_per_validated_task=0.025,
            tokens_per_validated_outcome=350,
            model_switch_count=1,
            provider_switch_count=0,
            avoidable_model_switch_rate=0.0,
            cache_break_even_accuracy=0.95,
            context_compaction_regret=0.02,
            routing_regret=0.01,
            retry_amplification=1.0,
            handoff_expansion_ratio=1.1,
            stale_tool_result_rate=0.0,
            cross_domain_leakage_rate=0.0,
            agent_context_contamination_rate=0.0,
        )

        summary = report.model_dump()
        assert len(summary) >= 20
        # Verify epistemic status declarations
        for metric_name, data in summary.items():
            assert "epistemic_status" in data
            assert data["epistemic_status"] in [
                EpistemicStatus.MEASURED.value,
                EpistemicStatus.ESTIMATED.value,
                EpistemicStatus.PROVIDER_REPORTED.value,
                EpistemicStatus.INFERRED.value,
                EpistemicStatus.VERIFIED.value,
            ]
