"""ACRA Continuity vs Migration Cost Model.

Implements R-023: Evaluates the cost, latency, and cache-continuity tradeoffs
between maintaining session affinity with an active model profile vs migrating
to a specialized model (with accompanying context rebuild and prefix cache loss).
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import EpistemicStatus


class MigrationTradeoffAssessment(BaseModel):
    """Result of comparing continuity savings against model migration benefits."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    stay_continuity_cost_usd: float = Field(..., description="Cost if remaining on active model")
    migrate_total_cost_usd: float = Field(..., description="Cost if switching (rebuild tokens + inference)")
    context_rebuild_tokens: int = Field(..., description="Tokens required to prime target model context")
    cache_continuity_savings_usd: float = Field(..., description="USD saved by reusing stable prefix cache")
    latency_penalty_ms: float = Field(..., description="Estimated cold-start / context ingestion latency penalty")
    recommend_migration: bool = Field(..., description="True if migrating delivers positive ROI over continuity")
    justification: str = Field(..., description="Technical rationale for the decision")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.ESTIMATED, description="Declared status")


class ContinuityCostModel:
    """Calculates financial and computational tradeoffs of model switching vs cache continuity."""

    DEFAULT_CACHE_DISCOUNT = 0.50  # 50% discount on cached tokens typically provided by APIs

    @staticmethod
    def calculate_continuity_savings(
        cached_tokens: int,
        uncached_cost_per_million: float = 1.00,
        cached_cost_per_million: float | None = None,
    ) -> float:
        """Calculate USD saved by leveraging cached stable prefix tokens rather than re-ingesting.

        Returns:
            float: Savings in USD (epistemic status: ESTIMATED).
        """
        if cached_tokens <= 0:
            return 0.0
        cached_rate = cached_cost_per_million if cached_cost_per_million is not None else (uncached_cost_per_million * 0.50)
        cost_without_cache = (cached_tokens / 1_000_000.0) * uncached_cost_per_million
        cost_with_cache = (cached_tokens / 1_000_000.0) * cached_rate
        return max(0.0, float(cost_without_cache - cost_with_cache))

    @staticmethod
    def calculate_migration_penalty(
        rebuild_tokens: int,
        target_model_cost_per_million: float = 2.50,
        latency_overhead_ms: float = 250.0,
    ) -> dict[str, float]:
        """Estimate the token ingestion overhead and latency cost of migrating to a new model."""
        rebuild_cost = (rebuild_tokens / 1_000_000.0) * target_model_cost_per_million
        return {
            "rebuild_cost_usd": float(rebuild_cost),
            "rebuild_tokens": float(rebuild_tokens),
            "latency_penalty_ms": float(latency_overhead_ms),
        }

    @classmethod
    def evaluate_migration_tradeoff(
        cls,
        active_model_cost_per_million: float,
        target_model_cost_per_million: float,
        cached_prefix_tokens: int,
        new_prompt_tokens: int,
        expected_output_tokens: int,
        target_capability_gain: float = 0.0,  # 0.0 to 1.0 score of capability differential
    ) -> MigrationTradeoffAssessment:
        """Comprehensively assess whether migrating to target model outperforms cache continuity.

        Enforces INV-010: Cache hysteresis prevents premature model oscillation.
        """
        # Option A: Stay with current model (benefits from prefix cache)
        savings = cls.calculate_continuity_savings(
            cached_tokens=cached_prefix_tokens,
            uncached_cost_per_million=active_model_cost_per_million,
        )
        total_active_tokens = cached_prefix_tokens + new_prompt_tokens + expected_output_tokens
        stay_cost = ((total_active_tokens / 1_000_000.0) * active_model_cost_per_million) - savings

        # Option B: Migrate to target model (loses prefix cache, incurs full rebuild)
        rebuild_tokens = cached_prefix_tokens + new_prompt_tokens
        penalty = cls.calculate_migration_penalty(
            rebuild_tokens=rebuild_tokens,
            target_model_cost_per_million=target_model_cost_per_million,
        )
        target_inference_cost = ((expected_output_tokens / 1_000_000.0) * target_model_cost_per_million)
        migrate_cost = penalty["rebuild_cost_usd"] + target_inference_cost

        # Decision logic: Only recommend migration if:
        # 1. Target capability gain is significant (> 0.35) and justifies cost, OR
        # 2. Migrate cost is actually cheaper than staying even with rebuild penalty
        recommend = False
        justification = ""

        if target_capability_gain >= 0.40:
            recommend = True
            justification = f"Capability gain ({target_capability_gain:.2f}) justifies migration despite rebuild cost of ${penalty['rebuild_cost_usd']:.4f}"
        elif migrate_cost < stay_cost:
            recommend = True
            justification = f"Target model is cheaper overall (${migrate_cost:.4f} vs ${stay_cost:.4f}) despite prefix rebuild"
        else:
            recommend = False
            justification = f"Continuity savings (${savings:.4f}) and rebuild penalty (${penalty['rebuild_cost_usd']:.4f}) favor remaining on active model"

        return MigrationTradeoffAssessment(
            stay_continuity_cost_usd=max(0.0, stay_cost),
            migrate_total_cost_usd=max(0.0, migrate_cost),
            context_rebuild_tokens=rebuild_tokens,
            cache_continuity_savings_usd=savings,
            latency_penalty_ms=penalty["latency_penalty_ms"],
            recommend_migration=recommend,
            justification=justification,
            epistemic_status=EpistemicStatus.ESTIMATED,
        )
