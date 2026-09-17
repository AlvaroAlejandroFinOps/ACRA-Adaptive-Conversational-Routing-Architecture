"""ACRA Context Compaction Decision Engine.

Evaluates trade-offs between context continuity, cache preservation, and entropy reduction.
Implements the 8 compaction actions specified in EVO ACRA.md §8 / §20.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import AuditResult
from src.core.contracts.context import ContextBudget, ContextCapsule


class CompactionAction(str, Enum):
    """Actions emitted to optimize context health and token economics."""
    KEEP_CONTEXT = "KEEP_CONTEXT"                     # Maintain active context unmodified
    PRUNE_VOLATILE_ITEMS = "PRUNE_VOLATILE_ITEMS"     # Discard stale tool results and ephemeral items
    COMPACT_INCREMENTALLY = "COMPACT_INCREMENTALLY"   # Summarize older turns while keeping prefix
    REBUILD_CONTEXT = "REBUILD_CONTEXT"               # Complete rehydration from canonical state
    FORK_AGENT_CONTEXT = "FORK_AGENT_CONTEXT"         # Fork child agent with whitelisted slice (INV-009)
    MIGRATE_MODEL = "MIGRATION_RECOMMENDED"           # Migrate to larger context window model
    TERMINATE_AND_RESTART = "TERMINATE_AND_RESTART"   # Non-recoverable degradation; reset agent
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"     # Severe ambiguity or policy impasse


class CompactionDecision(BaseModel):
    """Output of compaction decision evaluation."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    action: CompactionAction = Field(..., description="Selected context optimization action")
    rationale: str = Field(..., description="Justification considering continuity vs loss")
    expected_token_savings: int = Field(default=0, ge=0, description="Estimated token reduction")
    cache_preserved: bool = Field(default=True, description="Whether prefix cache remains valid")


class CompactionDecisionEngine:
    """Decision engine selecting optimal context hygiene action."""

    @classmethod
    def evaluate(
        cls,
        capsule: ContextCapsule,
        audit: AuditResult,
        budget: ContextBudget | None = None,
        cache_discount_ratio: float = 0.5,
    ) -> CompactionDecision:
        """Select best compaction strategy based on context health and token economics."""
        risk = audit.risk_score
        stale_count = sum(1 for t in capsule.volatile_tool_state if t.is_stale)
        utilization = 0.0
        if budget and budget.max_tokens > 0:
            current_tokens = len(f"{capsule.task_context} {capsule.current_turn}".split()) * 2
            utilization = current_tokens / budget.max_tokens

        # Severe unrecoverable risk or instruction conflict impasse
        if risk > 0.85:
            return CompactionDecision(
                action=CompactionAction.TERMINATE_AND_RESTART,
                rationale=f"Critical context entropy risk ({risk:.2f}) exceeds safe bounds",
                expected_token_savings=0,
                cache_preserved=False,
            )

        # Cross-domain contamination detected -> fork clean context (INV-009)
        if "cross_domain_leakage" in audit.dimension_scores:
            if audit.dimension_scores["cross_domain_leakage"].score > 0.3:
                return CompactionDecision(
                    action=CompactionAction.FORK_AGENT_CONTEXT,
                    rationale="Cross-domain references detected; forking agent with isolated context (INV-009)",
                    expected_token_savings=200,
                    cache_preserved=True,
                )

        # Stale tools present without major text bloat
        if stale_count > 0:
            return CompactionDecision(
                action=CompactionAction.PRUNE_VOLATILE_ITEMS,
                rationale=f"Pruning {stale_count} stale tool results to avoid obsolete state",
                expected_token_savings=stale_count * 100,
                cache_preserved=True,
            )

        # High utilization -> incremental compaction or rebuild
        if utilization > 0.85:
            return CompactionDecision(
                action=CompactionAction.COMPACT_INCREMENTALLY,
                rationale=f"Context utilization is high ({utilization:.1%}); compacting older history",
                expected_token_savings=int(budget.max_tokens * 0.3) if budget else 1000,
                cache_preserved=True,
            )

        # Clean context
        return CompactionDecision(
            action=CompactionAction.KEEP_CONTEXT,
            rationale="Context is healthy and within budget; preserving prefix cache",
            expected_token_savings=0,
            cache_preserved=True,
        )
