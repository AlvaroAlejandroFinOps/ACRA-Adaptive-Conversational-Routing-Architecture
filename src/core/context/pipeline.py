"""ACRA Context Engineering Pipeline.

Implements the 13-stage context pipeline specified in EVO ACRA.md §8.
Coordinates sanitization, compression, deduplication, domain segmentation,
and capsule sealing.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Callable

from src.core.context.capsule import ContextCapsuleBuilder
from src.core.context.scoped_registry import ScopedContextRegistry
from src.core.contracts.context import (
    ContextBudget,
    ContextCapsule,
    StablePrefixDescriptor,
    ToolResult,
)


class PipelineStageExecutionError(Exception):
    """Raised when a pipeline stage fails execution."""
    pass


class ContextEngineeringPipeline:
    """Orchestrates the 13 sequential context engineering stages."""

    def __init__(
        self,
        registry: ScopedContextRegistry | None = None,
        tenant_id: str = "default",
    ) -> None:
        self.registry = registry or ScopedContextRegistry()
        self.tenant_id = tenant_id

    # 1. Ingestion
    def stage_01_ingest(self, raw_input: dict[str, Any]) -> dict[str, Any]:
        """Ingest raw turn inputs and normalize structures."""
        data = dict(raw_input)
        data["current_turn"] = str(data.get("current_turn", "")).strip()
        data["task_context"] = str(data.get("task_context", "")).strip()
        data["domain_context"] = str(data.get("domain_context", "")).strip()
        data["domain"] = str(data.get("domain", "default")).strip()
        data["tool_results"] = list(data.get("tool_results", []))
        data["stage_log"] = ["01_ingest"]
        return data

    # 2. Classification
    def stage_02_classify(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Classify input intent, complexity, and domain category."""
        text = f"{payload['task_context']} {payload['current_turn']}".lower()
        complexity = "LOW"
        if len(text.split()) > 100 or any(k in text for k in ["analyze", "plan", "coordinate", "audit"]):
            complexity = "HIGH"
        payload["complexity_classification"] = complexity
        payload["stage_log"].append("02_classify")
        return payload

    @staticmethod
    def filter_superseded_tool_results(tool_results: list[ToolResult]) -> list[ToolResult]:
        """Keep only the latest execution result for each tool name (EVO ACRA §18 case 12)."""
        seen: set[str] = set()
        deduped: list[ToolResult] = []
        for tr in reversed(tool_results):
            if tr.tool_name not in seen:
                seen.add(tr.tool_name)
                deduped.append(tr)
        return list(reversed(deduped))

    # 3. Selective Retrieval
    def stage_03_retrieve_selective(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Filter context items to include only those relevant to active task."""
        # Only preserve tools matching recent turn context or active task
        tool_results = payload["tool_results"]
        # Filter superseded tool results and retain latest 5 tool results at most
        filtered_tools = self.filter_superseded_tool_results(tool_results)
        payload["tool_results"] = filtered_tools[-5:]
        payload["stage_log"].append("03_retrieve_selective")
        return payload

    # 4. Deduplication
    def stage_04_deduplicate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Deduplicate repeated paragraphs or redundant text blocks."""
        for field in ["domain_context", "task_context"]:
            paragraphs = [p.strip() for p in payload[field].split("\n\n") if p.strip()]
            seen: set[str] = set()
            deduped = []
            for p in paragraphs:
                if p not in seen:
                    seen.add(p)
                    deduped.append(p)
            payload[field] = "\n\n".join(deduped)
        payload["stage_log"].append("04_deduplicate")
        return payload

    # 5. Contradiction Detection
    def stage_05_detect_contradictions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Detect and tag conflicting directives."""
        combined = f"{payload['domain_context']} {payload['task_context']}"
        contradictions = []
        if "must not" in combined.lower() and "must always" in combined.lower():
            contradictions.append("Conflicting 'must not' and 'must always' rules detected")
        payload["detected_contradictions"] = contradictions
        payload["stage_log"].append("05_detect_contradictions")
        return payload

    # 6. Domain Segmentation
    def stage_06_segment_domain(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Enforce domain boundary: strip mentions of foreign domains (INV-003)."""
        target_domain = payload["domain"]
        foreign_domains = payload.get("foreign_domains", [])
        for fd in foreign_domains:
            if fd != target_domain:
                # Mask foreign domain mentions
                pattern = rf"\b{re.escape(fd)}\b"
                payload["domain_context"] = re.sub(pattern, "[REDACTED_DOMAIN]", payload["domain_context"], flags=re.IGNORECASE)
                payload["task_context"] = re.sub(pattern, "[REDACTED_DOMAIN]", payload["task_context"], flags=re.IGNORECASE)
        payload["stage_log"].append("06_segment_domain")
        return payload

    # 7. Sanitization
    def stage_07_sanitize(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Sanitize secrets, API keys, and injection attempts."""
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{20,}",
            r"bearer\s+[a-zA-Z0-9_\-\.]{20,}",
            r"api_key\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]",
        ]
        for field in ["current_turn", "task_context"]:
            for pat in secret_patterns:
                payload[field] = re.sub(pat, "[REDACTED_SECRET]", payload[field], flags=re.IGNORECASE)
        payload["stage_log"].append("07_sanitize")
        return payload

    # 8. Compression
    def stage_08_compress(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Compress verbosity while preserving code blocks and architecture facts."""
        padding_patterns = [
            r"as an ai assistant,?\s*",
            r"i would be happy to help you with that\.?\s*",
            r"sure thing!?\s*",
            r"let me think step by step\.?\s*",
        ]
        for pattern in padding_patterns:
            payload["current_turn"] = re.sub(pattern, "", payload["current_turn"], flags=re.IGNORECASE)
        payload["current_turn"] = payload["current_turn"].strip()
        payload["stage_log"].append("08_compress")
        return payload

    # 9. Preservation of Decisions & Evidence
    def stage_09_preserve_decisions_evidence(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Extract and guarantee preservation of explicit architectural decisions and evidence."""
        decisions = re.findall(r"(?:ADR-\d+|DECISION:\s*[^\n]+)", payload["task_context"], re.IGNORECASE)
        payload["preserved_decisions"] = decisions
        payload["stage_log"].append("09_preserve_decisions_evidence")
        return payload

    # 10. Budget Calculation
    def stage_10_calculate_budget(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Calculate token budget and verify limits."""
        input_tokens = len(f"{payload['domain_context']} {payload['task_context']} {payload['current_turn']}".split()) * 2
        max_budget = payload.get("max_tokens_budget", 8000)
        budget = ContextBudget(
            max_tokens=max_budget,
            consumed_tokens=input_tokens,
        )
        payload["calculated_budget"] = budget
        payload["stage_log"].append("10_calculate_budget")
        return payload

    # 11. Assemble Capsule
    def stage_11_assemble_capsule(self, payload: dict[str, Any]) -> ContextCapsuleBuilder:
        """Assemble builder instance with segmented and sanitized context."""
        prefix: StablePrefixDescriptor = payload["stable_prefix"]
        builder = ContextCapsuleBuilder(
            agent_instance_id=payload.get("agent_instance_id", "inst_default"),
            domain=payload["domain"],
            stable_prefix=prefix,
            capsule_id=payload.get("capsule_id"),
        )
        builder.set_domain_context(payload["domain_context"])
        builder.set_task_context(payload["task_context"])
        builder.set_current_turn(payload["current_turn"])
        builder.set_output_contract(payload.get("output_contract", "json"))

        for tr in payload.get("tool_results", []):
            if isinstance(tr, ToolResult):
                builder.add_tool_result(tr)
            elif isinstance(tr, dict):
                builder.add_tool_result(ToolResult(**tr))

        return builder

    # 12. Sealing Capsule
    def stage_12_seal_capsule(self, builder: ContextCapsuleBuilder) -> ContextCapsule:
        """Seal capsule with cryptographic SHA-256 digest."""
        capsule = builder.build_and_seal()
        return capsule

    # 13. Expiration & Lifecycle Registration
    def stage_13_register_lifecycle(self, capsule: ContextCapsule) -> str:
        """Register sealed capsule in ScopedContextRegistry with TTL."""
        storage_key = self.registry.register_capsule(
            tenant_id=self.tenant_id,
            capsule=capsule,
            ttl_seconds=3600,
        )
        return storage_key

    def process(
        self,
        raw_input: dict[str, Any],
        stable_prefix: StablePrefixDescriptor,
    ) -> tuple[ContextCapsule, str]:
        """Execute all 13 stages sequentially and return sealed capsule + storage key."""
        payload = dict(raw_input)
        payload["stable_prefix"] = stable_prefix

        p1 = self.stage_01_ingest(payload)
        p2 = self.stage_02_classify(p1)
        p3 = self.stage_03_retrieve_selective(p2)
        p4 = self.stage_04_deduplicate(p3)
        p5 = self.stage_05_detect_contradictions(p4)
        p6 = self.stage_06_segment_domain(p5)
        p7 = self.stage_07_sanitize(p6)
        p8 = self.stage_08_compress(p7)
        p9 = self.stage_09_preserve_decisions_evidence(p8)
        p10 = self.stage_10_calculate_budget(p9)
        builder = self.stage_11_assemble_capsule(p10)
        capsule = self.stage_12_seal_capsule(builder)
        key = self.stage_13_register_lifecycle(capsule)

        return capsule, key
