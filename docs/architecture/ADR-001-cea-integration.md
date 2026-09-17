# ADR-001: Context Audit Layer & CEA Integration Architecture

## Status
Accepted (Approved by User in Evolution Plan)

## Context
ACRA requires deep context quality, entropy, contamination, and security auditing across multiple points of the agent lifecycle: intake, pre-inference, post-tool execution, pre-handoff, post-handoff, post-consolidation, eviction, and model migration.

The Context Entropy Auditor (CEA) exists as a comprehensive local repository providing specialized context inspection and entropy analysis. ACRA must consume audit capabilities without creating tight circular or direct hardcoded coupling, maintaining zero-LLM operational resilience when CEA is in degraded mode or when running lightweight autonomous workflows.

## Alternatives Considered
1. **Option A: Reimplement CEA inside ACRA:** Violates single responsibility principle, duplicates code, complicates maintenance across distinct research tracks.
2. **Option B: Direct library dependency with tight coupling:** Rigid version binding, breaks if CEA is refactored, prevents lightweight or standalone testing.
3. **Option C: Interface-driven `ContextAuditProvider` Protocol with pluggable adapters:** Define a Python `Protocol` within ACRA contracts. ACRA consumes this protocol; CEA integration is mediated by a dedicated adapter (`CEAContextAuditAdapter`), while a `DeterministicFallbackAuditor` provides 18 zero-LLM signals natively.

## Decision
Adopt **Option C**.

ACRA defines:
1. `ContextAuditProvider` Protocol in `src/core/contracts/audit.py` (and implemented in `src/core/audit/provider.py`).
2. `CEAContextAuditAdapter` in `src/core/audit/cea_adapter.py` bridging directly to the local CEA repository.
3. `DeterministicFallbackAuditor` in `src/core/audit/deterministic.py` providing deterministic zero-LLM metrics across 12 dimensions (verbosity, repetitive patterns, injection heuristics, code preservation, stale tool output, etc.).
4. Canonical `AuditResult` contract featuring the mandatory tripleta: `risk_score` (0.0–1.0), `confidence` (0.0–1.0), and `evidence_coverage` (0.0–1.0), accompanied by `epistemic_status` tagging.

## Consequences
- **Positive:**
  - Maximum decoupling between ACRA orchestration and CEA analysis logic.
  - Complete zero-LLM testability without external service dependencies.
  - Seamless fallback via circuit breaker when external audit exceeds latency budgets.
  - Rigorous Pydantic v2 typing and JSON Schema validation for all audit results.
- **Negative:**
  - Requires maintaining adapter mapping code between CEA internal models and ACRA's `AuditResult` contract.
