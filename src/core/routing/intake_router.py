"""ACRA Intake Router.

Implements intake triage: intent classification, domain identification,
complexity evaluation, and risk profiling.
"""

from __future__ import annotations

import re
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class IntakeClassification(BaseModel):
    """Result of intake classification."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    primary_domain: str = Field(..., description="Target domain classification")
    intent: str = Field(..., description="Inferred user intent")
    complexity: str = Field(default="MEDIUM", description="Complexity tier: LOW, MEDIUM, HIGH")
    recommended_profile_id: str = Field(default="domain_planner", description="Suggested ModelProfile ID")
    risk_level: str = Field(default="LOW", description="Initial risk level: LOW, MEDIUM, HIGH")
    requires_decomposition: bool = Field(default=False, description="Whether objective demands multi-task DAG")


class IntakeRouter:
    """Classifies incoming user messages or objectives at session entry."""

    DOMAIN_KEYWORDS: dict[str, list[str]] = {
        "security": ["firewall", "auth", "permission", "token", "cve", "secret", "vulnerability", "audit"],
        "finance": ["budget", "tax", "cost", "invoice", "payroll", "revenue", "ledger", "sox"],
        "legal": ["contract", "nda", "compliance", "clause", "liability", "term", "gdpr", "copyright"],
        "operations": ["deploy", "container", "pod", "kubernetes", "infra", "server", "docker", "pipeline"],
        "hr": ["employee", "hire", "vacation", "benefit", "onboarding", "leave", "salary"],
    }

    def classify(self, user_input: str) -> IntakeClassification:
        """Analyze text to infer domain, complexity, and decomposition needs."""
        text = user_input.lower()
        words = text.split()

        # 1. Domain Matching
        matched_domain = "general"
        highest_hits = 0
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            hits = sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", text))
            if hits > highest_hits:
                highest_hits = hits
                matched_domain = domain

        # 2. Complexity & Decomposition
        requires_decomposition = False
        complexity = "LOW"
        if len(words) > 30 or highest_hits >= 2 or any(w in text for w in ["and then", "also", "after", "pipeline", "coordinate", "plan"]):
            complexity = "MEDIUM"
            requires_decomposition = True

        if len(words) > 80 or any(w in text for w in ["comprehensive", "full audit", "architecture", "multi-phase", "five", "all"]):
            complexity = "HIGH"
            requires_decomposition = True

        # 3. Profile recommendation
        if complexity == "HIGH":
            recommended_profile = "frontier_planner"
            risk_level = "MEDIUM"
        elif complexity == "MEDIUM":
            recommended_profile = "domain_planner"
            risk_level = "LOW"
        else:
            recommended_profile = "lightweight_executor"
            risk_level = "LOW"

        if "delete" in text or "drop" in text or "revoke" in text or "destroy" in text:
            risk_level = "HIGH"

        return IntakeClassification(
            primary_domain=matched_domain,
            intent="execute_task" if not requires_decomposition else "coordinate_objective",
            complexity=complexity,
            recommended_profile_id=recommended_profile,
            risk_level=risk_level,
            requires_decomposition=requires_decomposition,
        )
