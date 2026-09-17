"""ACRA Deterministic Signal Calculators.

Implements the 18 zero-LLM deterministic context signals specified in EVO ACRA.md §3 CEA.
Completely decoupled from model inference, network calls, and external providers.
"""

from __future__ import annotations

import re
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import EpistemicStatus


class DeterministicSignals(BaseModel):
    """Container for the 18 deterministic context audit signals."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    estimated_input_tokens: int = Field(default=0, ge=0, description="1. Estimated input tokens from text length")
    estimated_output_tokens: int = Field(default=0, ge=0, description="2. Estimated output tokens expected")
    context_utilization_ratio: float = Field(default=0.0, ge=0.0, description="3. Input tokens / max_tokens ceiling")
    exact_document_duplicates: int = Field(default=0, ge=0, description="4. Number of identical text snippets/documents")
    duplicate_ids_found: int = Field(default=0, ge=0, description="5. Collision count in task or tool call IDs")
    superseded_tool_results: int = Field(default=0, ge=0, description="6. Tool results overwritten by later calls for same tool")
    messages_since_last_user_turn: int = Field(default=0, ge=0, description="7. Agent self-loops / tool calls without user interaction")
    repeated_instruction_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="8. Proportion of repetitive instructions")
    stale_context_items: int = Field(default=0, ge=0, description="9. Elements flagged with stale=True")
    orphan_tool_results: int = Field(default=0, ge=0, description="10. Tool results without corresponding tool request reference")
    unresolved_contradictions: int = Field(default=0, ge=0, description="11. Detected opposing directives (e.g., 'must include' vs 'never include')")
    cross_domain_references: int = Field(default=0, ge=0, description="12. References to external/foreign domain entities")
    handoff_depth: int = Field(default=0, ge=0, description="13. Delegation chain depth from root objective")
    graph_fan_out: int = Field(default=0, ge=0, description="14. Number of parallel downstream tasks spawned")
    retry_count: int = Field(default=0, ge=0, description="15. Number of retries on current task")
    model_switch_count: int = Field(default=0, ge=0, description="16. Model transitions within active session")
    provider_switch_count: int = Field(default=0, ge=0, description="17. Provider transitions within active session")
    context_rebuild_count: int = Field(default=0, ge=0, description="18. Full context reconstructions triggered")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.ESTIMATED, description="Signals status")


class SignalCalculator:
    """Calculates zero-LLM deterministic audit metrics from context snapshots."""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count deterministically using whitespace and punctuation heuristics."""
        if not text:
            return 0
        words = len(text.split())
        punctuation_count = len(re.findall(r"[^\w\s]", text))
        return int(words * 1.3 + punctuation_count * 0.5)

    @classmethod
    def calculate(
        cls,
        current_turn: str = "",
        task_context: str = "",
        domain_context: str = "",
        max_tokens_budget: int = 8000,
        tool_results: list[dict[str, Any]] | None = None,
        turn_history: list[str] | None = None,
        target_domain: str = "default",
        known_foreign_domains: list[str] | None = None,
        handoff_depth: int = 0,
        graph_fan_out: int = 1,
        retry_count: int = 0,
        model_switch_count: int = 0,
        provider_switch_count: int = 0,
        context_rebuild_count: int = 0,
    ) -> DeterministicSignals:
        """Compute all 18 signals deterministically."""
        all_text = f"{domain_context} {task_context} {current_turn}".strip()
        input_tokens = cls.estimate_tokens(all_text)
        expected_output = max(50, int(input_tokens * 0.25))

        utilization_ratio = (input_tokens / max_tokens_budget) if max_tokens_budget > 0 else 0.0

        # Duplicate detection
        paragraphs = [p.strip() for p in all_text.split("\n\n") if len(p.strip()) > 30]
        exact_duplicates = len(paragraphs) - len(set(paragraphs))

        # Tool results signals
        t_results = tool_results or []
        stale_count = sum(1 for t in t_results if t.get("is_stale", False))
        tool_names = [t.get("tool_name", "") for t in t_results]
        superseded = len(tool_names) - len(set(tool_names))

        call_ids = [t.get("call_id") for t in t_results if t.get("call_id")]
        dup_ids = len(call_ids) - len(set(call_ids))
        orphan_count = sum(1 for t in t_results if not t.get("call_id"))

        # Messages since last user turn
        history = turn_history or []
        messages_since_user = 0
        for msg in reversed(history):
            if msg.lower().startswith("user:"):
                break
            messages_since_user += 1

        # Repetition ratio
        sentences = [s.strip() for s in re.split(r"[.!?]", all_text) if len(s.strip()) > 15]
        repeated_ratio = (1.0 - (len(set(sentences)) / len(sentences))) if sentences else 0.0

        # Direct contradiction heuristics (simple pattern checks)
        contradictions = 0
        if "must not" in all_text.lower() and "must always" in all_text.lower():
            contradictions += 1
        if "prohibited" in all_text.lower() and "mandatory" in all_text.lower():
            contradictions += 1

        # Cross-domain references check
        foreign_refs = 0
        if known_foreign_domains:
            for fd in known_foreign_domains:
                if fd != target_domain and re.search(rf"\b{re.escape(fd)}\b", all_text, re.IGNORECASE):
                    foreign_refs += 1

        return DeterministicSignals(
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=expected_output,
            context_utilization_ratio=round(utilization_ratio, 4),
            exact_document_duplicates=exact_duplicates,
            duplicate_ids_found=dup_ids,
            superseded_tool_results=superseded,
            messages_since_last_user_turn=messages_since_user,
            repeated_instruction_ratio=round(max(0.0, min(1.0, repeated_ratio)), 4),
            stale_context_items=stale_count,
            orphan_tool_results=orphan_count,
            unresolved_contradictions=contradictions,
            cross_domain_references=foreign_refs,
            handoff_depth=handoff_depth,
            graph_fan_out=graph_fan_out,
            retry_count=retry_count,
            model_switch_count=model_switch_count,
            provider_switch_count=provider_switch_count,
            context_rebuild_count=context_rebuild_count,
            epistemic_status=EpistemicStatus.ESTIMATED,
        )
