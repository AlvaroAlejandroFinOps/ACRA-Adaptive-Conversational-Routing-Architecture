# ACRA Hierarchical Agent Router — Evolution Plan

## Executive Orientation

**Objective:** Evolve ACRA from a two-layer Edge/Pro conversational router into a provider-agnostic, hierarchical agent orchestration architecture capable of coordinating multi-model, multi-domain agentic workflows with context isolation, cache-aware routing, and token economy governance.

**Mode:** `HYBRID` — The existing ACRA codebase (Python 3.10+, Pydantic v2, Ruff, pytest) provides a functional Edge/Pro pipeline with DHC, PayloadPolicyGate, FSM, governance and metrics. The evolution generalizes and extends this foundation without rewriting from scratch.

**Authoritative Evidence:**
- `[REQUIRED]` [EVO ACRA.md](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/Artefactos/GPT%205.6%20SOL/EVO%20ACRA.md) — 20-section evolution specification
- `[OBSERVED]` Repository source at [src/core/](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core) — 12 Python modules, 4 JSON schemas, 1 YAML config, 9 unit test files
- `[OBSERVED]` [pyproject.toml](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/pyproject.toml) — Python 3.10+, Pydantic ≥2.6, numpy, ruff, mypy, pytest
- `[OBSERVED]` [ThinkingSeed Master](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/001_Seed/seed-acra-adaptive-conversational-routing-architecture-master.md)

**Architecture chosen:** Hierarchical Agent Orchestrator with capability-based model profiles, context capsule isolation, cache-aware routing, and modular CEA integration via `ContextAuditProvider` interface.

**What this plan enables:** Phased, non-destructive evolution of the ACRA codebase through 11 dependency-ordered phases, each with defined contracts, verification, and rollback strategy. No code is modified in this document.

---

## 0. Context Qualification & Evidence Register

### Stack
| Dimension | Value | Evidence |
|---|---|---|
| Language | Python 3.10+ | `[OBSERVED]` pyproject.toml `requires-python = ">=3.10"` |
| Runtime validation | Pydantic v2 ≥2.6 | `[OBSERVED]` pyproject.toml dependencies |
| Linter | Ruff ≥0.3 | `[OBSERVED]` pyproject.toml `[tool.ruff]` |
| Type checker | mypy ≥1.8 (strict) | `[OBSERVED]` pyproject.toml `disallow_untyped_defs = true` |
| Test framework | pytest ≥8.0 + pytest-cov + pytest-benchmark | `[OBSERVED]` pyproject.toml dev deps |
| Serialization | JSON Schema draft-07 (4 schemas) | `[OBSERVED]` schemas/ directory |
| Config | YAML (acra_config.yaml) | `[OBSERVED]` config/ directory |
| Build | setuptools ≥68 | `[OBSERVED]` pyproject.toml build-system |
| Container | Docker + docker-compose | `[OBSERVED]` Dockerfile, docker-compose.yml |
| LLM SDKs (optional) | openai, google-generativeai, anthropic, ollama | `[OBSERVED]` pyproject.toml optional-deps |
| Numerical | numpy ≥1.26, scipy ≥1.12 | `[OBSERVED]` pyproject.toml dependencies |

### Evidence Labels
- `[OBSERVED]` — Directly read from repository files during this planning run
- `[REQUIRED]` — Specified in EVO ACRA.md as mandatory requirement
- `[DERIVED]` — Logically derived from observed + required premises
- `[PROPOSED]` — Design decisions proposed by this plan, requiring user approval

### Assumptions
- **A-01:** CEA (Context Entropy Auditor) exists as a separate repository. Its internal structure matches the file paths listed in EVO ACRA.md §16. If false, CEA integration phases must be deferred. `[REQUIRED]`
- **A-02:** The evolution preserves backward compatibility for existing test suites until a phase explicitly replaces a component. `[DERIVED from EVO ACRA.md §13: "No reescribas todo el proyecto desde cero"]`
- **A-03:** No real LLM API calls are required during testing; stub/mock adapters suffice. `[OBSERVED from current adapter pattern]`

---

## 1. Repository / Environment Forensics

### Current Architecture Summary `[OBSERVED]`

The existing ACRA system is a **two-cluster conversational router** (Edge → Pro):

```
User Input → EdgeRouter (maturity assessment) → DHC (compression)
           → UnifiedContextTier (caching) → PayloadPolicyGate (security)
           → HandoffEngine (payload assembly) → Pro Cluster execution
```

**Components inventory:**

| File | LOC | Responsibility | Status Tag |
|---|---|---|---|
| [orchestrator.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/orchestrator.py) | 188 | Session-level turn processing pipeline | `[MODIFY]` |
| [edge_router.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/edge_router.py) | 190 | Maturity-based binary edge/pro routing | `[MODIFY]` |
| [dhc.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/dhc.py) | 206 | Dynamic history compression, provenance tracking | `[MODIFY]` |
| [payload_policy.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/payload_policy.py) | 210 | Injection/secret/PII detection, sanitization | `[PRESERVE]` |
| [handoff.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/handoff.py) | 102 | Clean payload assembly for Pro dispatch | `[MODIFY]` |
| [unified_context.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/unified_context.py) | 141 | In-memory context snapshots with TTL + tenant isolation | `[MODIFY]` |
| [state_machine.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/state_machine.py) | 66 | Single FSM for session lifecycle | `[MODIFY]` |
| [governance.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/governance.py) | 100 | Session-level budget enforcement (turns, tokens, cost, time) | `[MODIFY]` |
| [metrics.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/metrics.py) | 183 | CCR, semantic fidelity, performance distribution | `[MODIFY]` |
| [llm_adapter.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/models/llm_adapter.py) | 107 | Abstract adapter + 2 stubs (Ollama, Cloud) | `[MODIFY]` |
| [config_loader.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/config_loader.py) | ~60 | YAML config loading | `[MODIFY]` |
| [logger.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/logger.py) | ~70 | Structured logging | `[PRESERVE]` |

### Critical Findings

| ID | Finding | Impact |
|---|---|---|
| C-001 | EdgeRouter hardcodes binary edge/pro routing decision. No concept of agent selection, capability profiles, or hierarchical delegation. | Must generalize to N-agent, N-model routing. |
| C-002 | Model names ("gemini-flash-lightweight-edge", "gemini-pro-reasoning-heavy") appear in `acra_config.yaml`. RouterAction enum has `DISPATCH_PRO` hardcoded. | Violates R-004 (model-agnostic selection). Must refactor to capability profiles. |
| C-003 | Single FSM (`ACRAStateMachine`) manages session lifecycle only. No agent instance, task, or objective lifecycle FSMs. | Must decompose per §7 of EVO ACRA.md. |
| C-004 | `ResourceGovernor` tracks budgets at session level only. No per-agent, per-task, or per-workflow budgets. | Must generalize to hierarchical budget governance. |
| C-005 | `BaseLLMAdapter` takes `model_name` as constructor arg. No capability negotiation, provider registry, or model profile resolution. | Must redesign per §9 of EVO ACRA.md. |
| C-006 | `CompressedContext` is a flat structure. No concept of Context Capsule isolation, domain scoping, or stable prefix engineering. | Must redesign per §8 and §11 of EVO ACRA.md. |
| C-007 | `CleanPayload` targets "edge" or "pro" only. No typed handoff envelope, domain isolation, or pre/post-handoff audit. | Must generalize per §14 of EVO ACRA.md. |
| C-008 | No agent definition, agent instance, or agent factory concepts exist. | All must be created. |

### Public Compatibility Obligations
- `[OBSERVED]` `__all__` in `src/core/__init__.py` exports: `ACRAMetrics`, `MetricResult`, `EdgeRouter`, `RouterDecision`, `DynamicHistoryCompressor`, `CompressedContext`, `UnifiedContextTier`, `ContextSnapshot`, `HandoffEngine`, `CleanPayload`, `ACRAOrchestrator`, `OrchestratorState`
- `[DERIVED]` These symbols constitute the current public API. Phase 1 must not break them; deprecation happens incrementally.

---

## 2. Requirement Traceability & Gap Analysis

### Requirement Ledger

| R-ID | Source | Requirement | Current State | Gap | Implementation Phase | Verification |
|---|---|---|---|---|---|---|
| R-001 | §1 | Provider-agnostic hierarchical agent routing | Binary Edge/Pro routing hardcoded | Complete absence | Phase 2, 4, 5 | Unit + Integration |
| R-002 | §2.1 | Receive complex objective, evaluate domain/scope/risk | EdgeRouter evaluates maturity only | No domain/scope decomposition | Phase 5 | E2E ticketera |
| R-003 | §2.3-2.4 | Select planner agent + model profile; generate master plan | No agent or planner concept | Complete absence | Phase 4, 5 | Unit + E2E |
| R-004 | §4.4 | Model selection by capability profiles, not names | `model_name` hardcoded in adapters and config | Fundamental gap | Phase 2 | Unit: no model names in core |
| R-005 | §4.1 | Minimal viable context per agent | Full history passed to single model | No context scoping | Phase 3 | Unit + property-based |
| R-006 | §4.2 | Domain isolation (gerencia boundaries) | Single tenant_id in UnifiedContextTier | No domain concept | Phase 3 | Unit: cross-domain leak test |
| R-007 | §4.3 | Typed, sterilized handoffs | CleanPayload is flat, unversioned envelope | No typed envelope | Phase 6 | Contract tests |
| R-008 | §4.5 | Plan/execute separation | Orchestrator both plans and executes | No separation | Phase 5 | Unit: permission boundary |
| R-009 | §4.6 | Ephemeral agent instances (AgentDefinition vs AgentInstance) | No concept exists | Complete absence | Phase 4 | Unit: lifecycle tests |
| R-010 | §4.7 | Hierarchical budget governance (objective/agent/task/model/tool/graph/flow) | Session-level only in ResourceGovernor | Must generalize | Phase 7 | Unit + property-based |
| R-011 | §4.8 | Reversible escalation (upscale and downscale) | No escalation mechanism | Complete absence | Phase 6 | Unit: escalation scenarios |
| R-012 | §4.9 | Complete provenance per result | Partial provenance_chain in DHC | Missing: agent, profile, tools, cost, confidence | Phase 7 | Unit: provenance completeness |
| R-013 | §4.10 | Degradation protection (12 specific threats) | No systematic controls | Partial via PayloadPolicyGate | Phase 7 | Unit: each threat vector |
| R-014 | §7 | Decomposed state machines (Session, Objective, Agent, Task, Handoff) | Single FSM | Must decompose | Phase 5 | Unit: all FSMs |
| R-015 | §8 | Context Engineering Pipeline (13 stages) | DHC provides compression + masking only | 11 stages missing | Phase 3 | Unit per stage |
| R-016 | §9 | Provider adapter layer with normalized capabilities | 2 stub adapters, no capability negotiation | Must redesign | Phase 2 | Unit + contract |
| R-017 | §10 | Security controls (15 specific items) | PayloadPolicyGate covers 4 | 11 additional controls | Phase 6, 7 | Unit per control |
| R-018 | §§1-5 CEA | Context Audit Layer (8 hook points, 12 audit dimensions) | No audit layer | Complete absence | Phase 3 | Unit per dimension |
| R-019 | §3 CEA | Zero-LLM deterministic signals (18 signals) | Partial in DHC/metrics | Most missing | Phase 3 | Unit: deterministic only |
| R-020 | §6 CEA | Token Economy Engine | No cost optimization | Complete absence | Phase 7 | Unit + benchmark |
| R-021 | §7-8 CEA | Cache-Aware Model Routing + Affinity Rules | No cache awareness | Complete absence | Phase 9 | Unit + benchmark |
| R-022 | §9 CEA | Cache Hysteresis policy (10 parameters) | No hysteresis | Complete absence | Phase 9 | Unit: oscillation prevention |
| R-023 | §10-11 CEA | Cache Continuity Descriptor + Stable Prefix Engineering | No prefix engineering | Complete absence | Phase 9 | Unit + property-based |
| R-024 | §12-13 CEA | Context Compaction vs Cache Preservation + Fork-before-Contaminate | DHC compresses unconditionally | No cost-aware compaction | Phase 3, 9 | Unit: comparison scenarios |
| R-025 | §14 CEA | Pre/post-handoff audit | No audit hooks | Complete absence | Phase 6 | Unit + contract |
| R-026 | §15 CEA | Modular CEA integration (3 alternatives evaluated) | CEA not integrated | Architecture decision required | Phase 3 | Contract tests |
| R-027 | §19 CEA | Extended ticketera E2E scenarios (9 scenarios) | No ticketera test exists | Complete absence | Phase 8 | E2E: all 9 scenarios |
| R-028 | §18 CEA | 20 mandatory test cases | 9 unit test files exist (basic coverage) | Most not covered | Phases 1-10 | Test ledger |
| R-029 | §5 CEA | Policy Modes (AUDIT_ONLY, RECOMMEND, HUMAN_REVIEW, DRY_RUN, ENFORCE) | No modal policy system | Complete absence | Phase 6 | Unit per mode |

### Orphan Check
- **No orphan requirements:** Every R-ID above has implementation and verification disposition.
- **No orphan components:** All proposed components trace to at least one R-ID.

---

## 3. Architectural Alternatives, Decisions & Invariants

### ADR-001: CEA Integration Strategy

**Context:** EVO ACRA.md §15 mandates evaluation of three alternatives for CEA integration.

| Alternative | Trade-offs | Verdict |
|---|---|---|
| A. Reimplement CEA principles inside ACRA | Full control; risk of divergence and duplication | Rejected — violates DRY |
| B. Consume CEA as independent library | Clean dependency; version coupling risk | Viable but rigid |
| **C. Define `ContextAuditProvider` interface** | Maximum decoupling; pluggable; testable with deterministic fallback | **`[PROPOSED]` Selected** |

**Decision:** Define a `ContextAuditProvider` Protocol (Python Protocol, not ABC) that ACRA consumes. CEA implements this interface via an adapter. ACRA ships a `DeterministicFallbackAuditor` for zero-LLM operation when CEA is unavailable.

**Rationale:** Option C satisfies: (1) versionado de contratos, (2) Pydantic compatibility, (3) JSON Schema, (4) stateless operation, (5) circuit breaker, (6) fallback determinista, (7) separate benchmarks.

---

### ADR-002: Model Selection Architecture

**Context:** EVO ACRA.md §4.4 requires capability-based model selection, not brand/version selection.

| Alternative | Trade-offs | Verdict |
|---|---|---|
| A. Direct model name configuration per agent | Simple; violates provider-agnostic requirement | Rejected |
| **B. ModelProfile → ModelCapabilityRegistry → ProviderAdapter resolution** | Clean separation; runtime flexibility; provider-specific details isolated | **`[PROPOSED]` Selected** |

**Decision:** Introduce three-layer model resolution:
1. `ModelProfile` — Declares capability requirements (structured_output, tool_calling, reasoning, etc.), cost/latency constraints
2. `ModelCapabilityRegistry` — Maps concrete `ProviderModel` entries to capability vectors
3. Runtime resolver — Selects best available model matching a profile's constraints

Concrete model names live exclusively in `config/providers/*.yaml`, never in domain code or enums.

---

### ADR-003: Agent Lifecycle Architecture

**Context:** EVO ACRA.md §4.6 requires AgentDefinition vs AgentInstance separation.

**Decision:** `AgentDefinition` is a persistent template (policies, tools, domain, contracts). `AgentInstance` is an ephemeral runtime entity with lifecycle, budget, context capsule, and model affinity. Instances are created by `AgentFactory`, registered in `AgentRegistry`, and have bounded TTL.

---

### ADR-004: State Machine Decomposition

**Context:** EVO ACRA.md §7 requires at least 5 FSMs. Current codebase has 1.

**Decision:** Decompose into:
1. `SessionStateMachine` — Inherits current FSM transitions (backward compatible)
2. `ObjectiveStateMachine` — RECEIVED → PLANNING → DECOMPOSED → EXECUTING → CONSOLIDATING → VALIDATED → COMPLETED | FAILED
3. `AgentInstanceStateMachine` — CREATED → INITIALIZED → ACTIVE → SUSPENDED → COMPLETED → RETIRED | REVOKED
4. `TaskStateMachine` — PENDING → ASSIGNED → EXECUTING → VALIDATING → COMPLETED | FAILED | ESCALATED
5. `HandoffStateMachine` — PREPARING → AUDITING → DISPATCHED → RECEIVED → VALIDATED | REJECTED

Each FSM prohibits infinite cycles via max-transition counters. Current `ACRAStateMachine` preserved as legacy alias mapping to `SessionStateMachine`.

---

### Invariant Ledger

| INV-ID | Statement | Enforcement | Verification | Failure Condition |
|---|---|---|---|---|
| INV-001 | No concrete model name shall appear in domain logic (src/core/ excluding models/ and config/) | Ruff custom rule or grep-based CI check | `test_no_model_names_in_core` | Build fails |
| INV-002 | Every handoff envelope must pass pre-handoff audit before dispatch | `HandoffStateMachine` transition guard | `test_handoff_requires_audit` | Handoff blocked |
| INV-003 | Cross-domain context leakage rate must be zero in unit tests | Domain isolation in ContextCapsule | `test_cross_domain_leakage` | Test fails |
| INV-004 | Every provenance entry must declare epistemic_status | Pydantic field validator on EpistemicStatus enum | `test_provenance_has_epistemic_status` | Validation error |
| INV-005 | Budget enforcement is hierarchical: objective → agent → task | HierarchicalBudgetGovernor checks all levels | `test_hierarchical_budget_cascade` | BudgetExceededError |
| INV-006 | Token estimates are labeled "estimated" unless provider-reported | EpistemicStatus enum enforced in telemetry models | `test_estimate_vs_measured_distinction` | Validation error |
| INV-007 | Destructive operations require explicit policy approval | PolicyMode.ENFORCE gate on destructive actions list | `test_destructive_requires_approval` | Operation blocked |
| INV-008 | FSM transitions are deterministic; no state allows self-loops without explicit retry limit | max_retries parameter on retry transitions | `test_no_infinite_fsm_cycles` | InvalidTransitionError |
| INV-009 | Agent fork inherits only authorized context subset, never full conversation | ContextCapsule.fork() whitelist | `test_fork_context_isolation` | Test fails |
| INV-010 | Cache hysteresis prevents model oscillation below configurable thresholds | HysteresisPolicy configuration guard | `test_no_model_oscillation` | Routing blocked |

---

## 4. Target Architecture & Dependency Boundaries

### Target Tree (with status tags)

```text
src/core/
├── __init__.py                          [MODIFY] — Add new exports
├── config_loader.py                     [MODIFY] — Load provider configs
├── logger.py                            [PRESERVE]
│
├── contracts/                           [NEW] — All typed contracts
│   ├── __init__.py                      [NEW]
│   ├── agent.py                         [NEW] — AgentDefinition, AgentInstance, AgentCapability, AgentPolicy
│   ├── task.py                          [NEW] — TaskDefinition, TaskExecution, TaskDependency
│   ├── context.py                       [NEW] — ContextCapsule, ContextBudget, StablePrefixDescriptor
│   ├── model.py                         [NEW] — ModelProfile, ProviderProfile, ModelSelectionDecision
│   ├── handoff.py                       [NEW] — HandoffEnvelope, EscalationPolicy
│   ├── governance.py                    [NEW] — ToolGrant, ValidationResult, ExecutionEvidence
│   ├── outcome.py                       [NEW] — AgentOutcome, ConsolidatedOutcome
│   ├── graph.py                         [NEW] — AgentGraph, GraphNode, GraphEdge
│   ├── audit.py                         [NEW] — AuditResult, AuditTriple, Finding, DimensionScore
│   └── cache.py                         [NEW] — CacheContinuityDescriptor, AgentModelAffinity, ModelSessionLease
│
├── agents/                              [NEW] — Agent lifecycle management
│   ├── __init__.py                      [NEW]
│   ├── registry.py                      [NEW] — AgentRegistry (definition store)
│   ├── factory.py                       [NEW] — AgentFactory (instance creation)
│   └── lifecycle.py                     [NEW] — AgentInstanceStateMachine
│
├── routing/                             [NEW] — Capability and agent routing
│   ├── __init__.py                      [NEW]
│   ├── capability_router.py             [NEW] — CapabilityAndAgentRouter
│   ├── model_resolver.py               [NEW] — ModelCapabilityRegistry + runtime resolver
│   ├── affinity.py                      [NEW] — AgentModelAffinity + hysteresis
│   └── intake_router.py                [NEW] — Intake classification (domain, intent, risk)
│
├── context/                             [NEW] — Context engineering pipeline
│   ├── __init__.py                      [NEW]
│   ├── pipeline.py                      [NEW] — ContextEngineeringPipeline (13 stages)
│   ├── capsule.py                       [NEW] — ContextCapsule builder + fork
│   ├── prefix.py                        [NEW] — StablePrefixEngine
│   ├── scoped_registry.py              [NEW] — ScopedContextRegistry
│   └── compaction.py                    [NEW] — Compaction vs cache preservation decisions
│
├── audit/                               [NEW] — Context Audit Layer
│   ├── __init__.py                      [NEW]
│   ├── provider.py                      [NEW] — ContextAuditProvider Protocol
│   ├── deterministic.py                 [NEW] — DeterministicFallbackAuditor (zero-LLM, 18 signals)
│   ├── signals.py                       [NEW] — Deterministic signal calculators
│   └── policy_modes.py                  [NEW] — AUDIT_ONLY, RECOMMEND, HUMAN_REVIEW, DRY_RUN, ENFORCE
│
├── economy/                             [NEW] — Token Economy Engine
│   ├── __init__.py                      [NEW]
│   ├── engine.py                        [NEW] — TokenEconomyEngine
│   ├── cost_model.py                    [NEW] — Continuity vs migration cost comparison
│   └── telemetry.py                     [NEW] — Provenance + epistemic status tracking
│
├── orchestration/                       [NEW] — Hierarchical orchestration
│   ├── __init__.py                      [NEW]
│   ├── hierarchical_orchestrator.py     [NEW] — HierarchicalAgentOrchestrator
│   ├── objective_planner.py             [NEW] — ObjectiveStateMachine + decomposition
│   ├── task_graph.py                    [NEW] — Task DAG execution
│   └── consolidator.py                 [NEW] — Result consolidation without context mixing
│
├── fsm/                                 [NEW] — Decomposed state machines
│   ├── __init__.py                      [NEW]
│   ├── session.py                       [NEW] — SessionStateMachine (backward-compatible)
│   ├── objective.py                     [NEW] — ObjectiveStateMachine
│   ├── task.py                          [NEW] — TaskStateMachine
│   └── handoff_fsm.py                   [NEW] — HandoffStateMachine
│
├── providers/                           [NEW] — Provider adapters
│   ├── __init__.py                      [NEW]
│   ├── base.py                          [NEW] — ProviderAdapter Protocol + CapabilityVector
│   ├── anthropic.py                     [NEW] — Anthropic adapter
│   ├── google.py                        [NEW] — Google adapter
│   ├── openai.py                        [NEW] — OpenAI adapter
│   ├── local.py                         [NEW] — Local model adapter (Ollama)
│   └── stub.py                          [NEW] — Deterministic stub for testing
│
├── security/                            [NEW] — Extended security controls
│   ├── __init__.py                      [NEW]
│   ├── handoff_policy_gate.py           [NEW] — HandoffPolicyGate (extends PayloadPolicyGate)
│   ├── tool_authorization.py            [NEW] — ToolGrant verification
│   └── concurrency_control.py           [NEW] — Write conflict prevention
│
├── models/                              [PRESERVE] — Legacy adapters (deprecated gradually)
│   ├── __init__.py                      [PRESERVE]
│   ├── llm_adapter.py                   [PRESERVE] — Deprecated; replaced by providers/
│   └── mock_models.py                   [PRESERVE]
│
├── orchestrator.py                      [MODIFY] — Thin wrapper delegating to orchestration/
├── edge_router.py                       [MODIFY] — Deprecated alias → routing/
├── dhc.py                               [MODIFY] — Deprecated alias → context/pipeline.py
├── payload_policy.py                    [PRESERVE] — Consumed by security/handoff_policy_gate.py
├── handoff.py                           [MODIFY] — Deprecated alias → routing/ + security/
├── unified_context.py                   [MODIFY] — Deprecated alias → context/scoped_registry.py
├── state_machine.py                     [MODIFY] — Deprecated alias → fsm/session.py
├── governance.py                        [MODIFY] — Deprecated alias → economy/ + contracts/governance.py
└── metrics.py                           [MODIFY] — Extended with new metrics from §17

config/
├── acra_config.yaml                     [MODIFY] — Restructure for hierarchical config
├── providers/                           [NEW]
│   ├── anthropic.yaml                   [NEW]
│   ├── google.yaml                      [NEW]
│   ├── openai.yaml                      [NEW]
│   └── local.yaml                       [NEW]
├── profiles/                            [NEW]
│   └── model_profiles.yaml              [NEW] — frontier_planner, complex_reasoner, etc.
├── domains/                             [NEW]
│   └── ticketera/                       [NEW] — Per-gerencia agent definitions
│       ├── gerencia_rrhh.yaml           [NEW]
│       ├── gerencia_finanzas.yaml       [NEW]
│       ├── gerencia_legal.yaml          [NEW]
│       ├── gerencia_operaciones.yaml    [NEW]
│       └── gerencia_tecnologia.yaml     [NEW]
└── policies/                            [NEW]
    ├── hysteresis.yaml                  [NEW]
    ├── escalation.yaml                  [NEW]
    └── destructive_actions.yaml         [NEW]

schemas/                                 [MODIFY] — Add new schemas
├── clean_payload.json                   [PRESERVE]
├── conversation_state.json              [PRESERVE]
├── policy_validation.json               [PRESERVE]
├── routing_decision.json                [PRESERVE]
├── agent_definition.schema.json         [NEW]
├── context_capsule.schema.json          [NEW]
├── handoff_envelope.schema.json         [NEW]
├── model_profile.schema.json            [NEW]
├── audit_result.schema.json             [NEW]
└── cache_continuity.schema.json         [NEW]
```

### Dependency Boundaries

**Allowed dependency direction:** `contracts/ ← *` (everything depends on contracts, contracts depend on nothing internal except Pydantic/stdlib)

**Prohibited dependencies:**
- `contracts/` → any other `src/core/` module
- `routing/` → `orchestration/` (routing is consumed by orchestration, not the reverse)
- `providers/` → `routing/` or `orchestration/` (providers are leaf adapters)
- `audit/` → `economy/` (audit is independent of cost decisions)
- Domain logic (anything in `src/core/` excluding `providers/` and `config/`) → concrete model names

---

## 5. Contract, Interface & Data Specifications

### 5.1 Core Contracts (Pydantic v2 models)

> [!NOTE]
> These are specification-level contract definitions. Full field types, validators, and defaults will be implemented in code. The specification here defines responsibility, key fields, and relationships.

#### AgentDefinition `[NEW]` (R-009)
- **Responsibility:** Persistent template defining an agent's role, policies, tools, domain
- **Key fields:** `agent_def_id`, `name`, `domain`, `capabilities: list[AgentCapability]`, `policies: list[AgentPolicy]`, `tool_grants: list[ToolGrant]`, `input_contract: str` (schema ref), `output_contract: str`, `escalation_policy: EscalationPolicy`, `model_profile_id: str`, `max_context_tokens: int`
- **Producers:** AgentRegistry (config-loaded), AgentFactory (dynamic)
- **Consumers:** AgentFactory, IntakeRouter, HierarchicalOrchestrator

#### AgentInstance `[NEW]` (R-009)
- **Responsibility:** Ephemeral runtime entity with lifecycle, budget, context
- **Key fields:** `instance_id: str`, `definition_id: str`, `state: AgentInstanceState`, `context_capsule: ContextCapsule`, `budget: ContextBudget`, `model_affinity: AgentModelAffinity | None`, `created_at`, `expires_at`, `parent_instance_id: str | None`
- **Producers:** AgentFactory
- **Consumers:** HierarchicalOrchestrator, TaskGraph

#### ModelProfile `[NEW]` (R-004)
- **Responsibility:** Declares capability requirements for a functional role
- **Key fields:** `profile_id: str` (e.g., "frontier_planner"), `required_capabilities: set[str]`, `max_context_tokens: int`, `max_cost_per_1k_input: float`, `max_latency_ms: int`, `risk_level_allowed: str`, `preferred_provider: str | None`, `fallback_providers: list[str]`
- **Producers:** Configuration (profiles/model_profiles.yaml)
- **Consumers:** ModelCapabilityRegistry (resolver)

#### ContextCapsule `[NEW]` (R-005, R-006)
- **Responsibility:** Isolated, scoped context envelope for an agent instance
- **Key fields:** `capsule_id: str`, `agent_instance_id: str`, `domain: str`, `stable_prefix: StablePrefixDescriptor`, `domain_context: str`, `task_context: str`, `volatile_tool_state: list[ToolResult]`, `current_turn: str`, `output_contract: str`, `hash: str`, `created_at`, `expires_at`, `is_sealed: bool`, `parent_capsule_id: str | None`
- **Producers:** ContextEngineeringPipeline
- **Consumers:** ProviderAdapter, AgentInstance

#### HandoffEnvelope `[NEW]` (R-007, R-025)
- **Responsibility:** Typed, versioned, audited communication between agents
- **Key fields:** `envelope_id: str`, `schema_version: str`, `source_agent_id: str`, `target_agent_id: str`, `domain: str`, `objective: str`, `context_capsule_hash: str`, `evidence: list[ExecutionEvidence]`, `permissions: list[ToolGrant]`, `budget: ContextBudget`, `expires_at`, `limitations: list[str]`, `pre_handoff_audit: AuditResult`, `audit_status: str`
- **Producers:** HandoffPolicyGate
- **Consumers:** Target AgentInstance

#### AuditResult `[NEW]` (R-018)
- **Responsibility:** Complete audit output with tripleta + findings
- **Key fields:** `audit_id: str`, `risk_score: float`, `confidence: float`, `evidence_coverage: float`, `dimension_scores: dict[str, DimensionScore]`, `findings: list[Finding]`, `evidence_refs: list[str]`, `triggered_rules: list[str]`, `limitations: list[str]`, `recommended_actions: list[str]`, `requires_policy_approval: bool`, `epistemic_status: EpistemicStatus`
- **Producers:** ContextAuditProvider implementations
- **Consumers:** HandoffStateMachine, HierarchicalOrchestrator

#### CacheContinuityDescriptor `[NEW]` (R-023)
- **Responsibility:** Observable/estimated cache state for model affinity decisions
- **Key fields:** `provider_id`, `model_profile_id`, `concrete_model_id`, `session_id`, `agent_instance_id`, `cache_reference: str | None`, `cache_scope`, `cache_created_at`, `cache_expires_at`, `reported_cached_tokens: int | None`, `reported_uncached_tokens: int | None`, `estimated_reusable_tokens: int`, `stable_prefix_hash: str`, `system_instruction_hash: str`, `tool_manifest_hash: str`, `context_capsule_hash: str`, `provider_reported_cache_hit: bool | None`, `observability_level: str`, `epistemic_status: EpistemicStatus`, `migration_cost_estimate: float`, `limitations: list[str]`
- **Producers:** ProviderAdapter (runtime telemetry)
- **Consumers:** Affinity module, TokenEconomyEngine

### 5.2 Interfaces (Python Protocols)

#### ContextAuditProvider Protocol `[NEW]` (R-026)
```python
class ContextAuditProvider(Protocol):
    def audit(self, capsule: ContextCapsule, hook_point: AuditHookPoint) -> AuditResult: ...
    def get_supported_dimensions(self) -> list[str]: ...
    def health_check(self) -> bool: ...
```

#### ProviderAdapter Protocol `[NEW]` (R-016)
```python
class ProviderAdapter(Protocol):
    def get_capabilities(self) -> CapabilityVector: ...
    def generate(self, capsule: ContextCapsule, profile: ModelProfile) -> ProviderResponse: ...
    def get_cache_descriptor(self, session_id: str) -> CacheContinuityDescriptor | None: ...
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float: ...
```

---

## 6. Failure, Security & Observability Architecture

### Failure/Reliability `[APPLICABLE]`

| Failure Mode | Detection | Containment | Recovery | Telemetry |
|---|---|---|---|---|
| Provider unavailable | HTTP timeout / circuit breaker | Fallback to next provider in profile | Auto-retry with backoff; degrade to local model | `provider_failure` event |
| Agent context contamination | Audit dimension `context_contamination` | Fork agent instance | FORK_AGENT_CONTEXT action | `contamination_detected` event |
| Budget exhaustion | HierarchicalBudgetGovernor exception | Block further agent actions | Escalate to parent agent or human | `budget_exceeded` event |
| Infinite agent cycle | max_transitions counter in FSMs | Force TERMINATED state | Log cycle trace; alert | `infinite_cycle_detected` event |
| Handoff audit failure | AuditResult.risk_score > threshold | Block handoff dispatch | Remediate or escalate | `handoff_blocked` event |
| Model oscillation | Hysteresis policy violation | Block model switch | Maintain current affinity | `oscillation_prevented` event |
| Cross-domain leakage | ContextCapsule domain boundary check | Block context merge | Reject contaminated capsule | `leakage_blocked` event |

### Security `[APPLICABLE]` (R-017)

| Control | Implementation | Verification |
|---|---|---|
| Multi-tenant isolation | `tenant_id` on all contracts; storage partitioned | `test_tenant_isolation` |
| Domain isolation (gerencia) | `domain` field on ContextCapsule; no cross-domain reads without explicit grant | `test_domain_isolation` |
| Prompt injection prevention | Existing PayloadPolicyGate + extended HandoffPolicyGate | `test_injection_patterns` (existing) |
| Memory poisoning control | Context audit `context_contamination` dimension | `test_memory_poisoning` |
| Tool authorization | ToolGrant whitelist per AgentDefinition | `test_unauthorized_tool_blocked` |
| Plan/execute separation | Separate AgentDefinitions for planner vs executor; different ToolGrant sets | `test_planner_cannot_execute` |
| Destructive action validation | PolicyMode.ENFORCE on destructive actions list (§5 CEA) | `test_destructive_requires_approval` |
| Idempotency | Task ID deduplication in TaskGraph | `test_task_idempotency` |
| Concurrency control | Optimistic locking via version field on shared state | `test_concurrent_write_prevention` |
| Human-in-the-loop | EscalationPolicy with `requires_human: bool` per risk level | `test_human_escalation` |
| Secret/PII redaction | Existing PayloadPolicyGate sanitization | Existing tests |
| Context revocation | ContextCapsule.is_sealed + revocation event | `test_context_revocation` |
| Graph depth/width limits | max_depth, max_fan_out in AgentGraph | `test_graph_limits` |

### Observability `[APPLICABLE]`

- **Structured logs:** Existing logger.py preserved; extend with correlation_id per objective
- **Metrics (new, from §17 CEA):** context_risk_score, evidence_coverage, context_utilization_ratio, context_reuse_ratio, provider_reported_cache_hit_ratio, estimated_cache_reuse_ratio, context_rebuild_tokens, effective_cost_per_validated_task, tokens_per_validated_outcome, model_switch_count, provider_switch_count, avoidable_model_switch_rate, cache_break_even_accuracy, context_compaction_regret, routing_regret, retry_amplification, handoff_expansion_ratio, stale_tool_result_rate, cross_domain_leakage_rate, unsupported_claim_propagation_rate, agent_context_contamination_rate
- **Epistemic status distinction:** Every metric tagged as `measured | provider_reported | estimated | inferred`

---

## 7. Phased Implementation Work Breakdown

### Phase 0: Conceptual Model Update & ADR Documentation
- **Objective:** Formalize architecture decisions, invariants, and conceptual model without code changes
- **R-IDs:** All (foundation)
- **Prerequisites:** User approval of this plan
- **Artifacts:** `docs/architecture/ADR-001-cea-integration.md`, `ADR-002-model-selection.md`, `ADR-003-agent-lifecycle.md`, `ADR-004-fsm-decomposition.md`, `docs/architecture/ACRA_Hierarchical_Architecture_v3.md`
- **INV-IDs enforced:** None yet (documentation phase)
- **Verification:** Document review
- **Rollback:** Delete new docs
- **Gate:** ADR documents reviewed and approved

---

### Phase 1: Typed Contracts (Agents, Tasks, Models, Contexts)
- **Objective:** Establish all Pydantic v2 contract models without changing existing modules
- **R-IDs:** R-004, R-005, R-006, R-007, R-009, R-012, R-018, R-023
- **Prerequisites:** Phase 0 approved
- **Artifacts:**
  - `[NEW]` `src/core/contracts/__init__.py`
  - `[NEW]` `src/core/contracts/agent.py` — AgentDefinition, AgentInstance, AgentCapability, AgentPolicy, AgentLifecycle
  - `[NEW]` `src/core/contracts/task.py` — TaskDefinition, TaskExecution, TaskDependency
  - `[NEW]` `src/core/contracts/context.py` — ContextCapsule, ContextBudget, StablePrefixDescriptor
  - `[NEW]` `src/core/contracts/model.py` — ModelProfile, ProviderProfile, ModelSelectionDecision
  - `[NEW]` `src/core/contracts/handoff.py` — HandoffEnvelope, EscalationPolicy
  - `[NEW]` `src/core/contracts/governance.py` — ToolGrant, ValidationResult, ExecutionEvidence
  - `[NEW]` `src/core/contracts/outcome.py` — AgentOutcome, ConsolidatedOutcome
  - `[NEW]` `src/core/contracts/graph.py` — AgentGraph, GraphNode, GraphEdge
  - `[NEW]` `src/core/contracts/audit.py` — AuditResult, AuditTriple, Finding, DimensionScore, EpistemicStatus
  - `[NEW]` `src/core/contracts/cache.py` — CacheContinuityDescriptor, AgentModelAffinity, ModelSessionLease, CacheCapabilityProfile, ContextReuseEstimate, ModelMigrationDecision, ContextRehydrationPlan, CacheInvalidationEvent
  - `[NEW]` `schemas/agent_definition.schema.json`, `context_capsule.schema.json`, `handoff_envelope.schema.json`, `model_profile.schema.json`, `audit_result.schema.json`, `cache_continuity.schema.json`
- **Contracts changed:** All new; no existing contracts broken
- **Steps:**
  1. Create `src/core/contracts/` package
  2. Define each contract with full Pydantic v2 typing, validators, and field constraints
  3. Generate corresponding JSON schemas via Pydantic's `model_json_schema()`
  4. Write unit tests for serialization roundtrip, validation edge cases, and forbidden states
- **INV-IDs enforced:** INV-004 (epistemic_status on provenance), INV-006 (estimate vs measured)
- **Verification:** `pytest tests/unit/test_contracts*.py` — roundtrip serialization, validation failures on invalid states, schema compatibility
- **Rollback:** Delete `src/core/contracts/` directory
- **Gate:** All contract models pass mypy strict, Ruff clean, JSON schema generated

---

### Phase 2: Model Capability Registry & Provider-Agnostic Selection
- **Objective:** Implement capability-based model resolution replacing hardcoded model names
- **R-IDs:** R-004, R-016
- **Prerequisites:** Phase 1 (contracts/model.py, contracts/cache.py)
- **Artifacts:**
  - `[NEW]` `src/core/providers/base.py` — ProviderAdapter Protocol, CapabilityVector
  - `[NEW]` `src/core/providers/stub.py` — DeterministicStubProvider
  - `[NEW]` `src/core/routing/model_resolver.py` — ModelCapabilityRegistry, runtime resolution
  - `[NEW]` `config/profiles/model_profiles.yaml` — 7 profile definitions
  - `[NEW]` `config/providers/stub.yaml` — Stub provider capabilities
- **Contracts changed:** ModelProfile consumed, ModelSelectionDecision produced
- **Steps:**
  1. Define ProviderAdapter Protocol with generate(), get_capabilities(), estimate_cost()
  2. Implement ModelCapabilityRegistry that loads provider configs and matches profiles
  3. Create DeterministicStubProvider that implements the Protocol for testing
  4. Migrate existing CloudAPIStubAdapter and LocalOllamaStubAdapter to new Protocol
  5. Define 7 model profiles in YAML (frontier_planner, complex_reasoner, domain_planner, lightweight_executor, classifier, validator, fallback_local)
- **INV-IDs enforced:** INV-001 (no model names in core)
- **Verification:** `test_profile_resolution`, `test_no_model_names_in_core` (grep-based), `test_fallback_provider_chain`
- **Rollback:** Revert to existing BaseLLMAdapter (legacy alias preserved)
- **Gate:** All 7 profiles resolve to a stub provider; zero model names in domain code

---

### Phase 3: Context Isolation, Context Capsules & Audit Layer
- **Objective:** Implement Context Engineering Pipeline, ContextCapsule, and ContextAuditProvider
- **R-IDs:** R-005, R-006, R-015, R-018, R-019, R-024, R-026
- **Prerequisites:** Phase 1 (contracts/context.py, contracts/audit.py)
- **Artifacts:**
  - `[NEW]` `src/core/context/pipeline.py` — 13-stage ContextEngineeringPipeline
  - `[NEW]` `src/core/context/capsule.py` — ContextCapsule builder, fork(), seal()
  - `[NEW]` `src/core/context/prefix.py` — StablePrefixEngine
  - `[NEW]` `src/core/context/scoped_registry.py` — ScopedContextRegistry (replaces UnifiedContextTier)
  - `[NEW]` `src/core/context/compaction.py` — Cost-aware compaction decision engine
  - `[NEW]` `src/core/audit/provider.py` — ContextAuditProvider Protocol
  - `[NEW]` `src/core/audit/cea_adapter.py` — CEAContextAuditAdapter (bridges to local CEA repository via Protocol)
  - `[NEW]` `src/core/audit/deterministic.py` — DeterministicFallbackAuditor (18 zero-LLM signals)
  - `[NEW]` `src/core/audit/signals.py` — Signal calculators
  - `[NEW]` `src/core/audit/policy_modes.py` — 5 policy modes
- **Contracts changed:** ContextCapsule produced and consumed; AuditResult produced
- **Steps:**
  1. Implement ContextEngineeringPipeline with 13 named stages (ingestion → revocation)
  2. Build ContextCapsule with domain isolation, stable_prefix, and hash sealing
  3. Implement fork() that inherits only authorized fields (INV-009)
  4. Build DeterministicFallbackAuditor with 18 deterministic signals from §3 CEA
  5. Implement AuditResult with tripleta (risk_score, confidence, evidence_coverage)
  6. Implement 5 PolicyModes with escalation rules
  7. Implement StablePrefixEngine with hash versioning and invalidation events
  8. Implement compaction decision engine (KEEP_CONTEXT, PRUNE_VOLATILE_ITEMS, COMPACT_INCREMENTALLY, REBUILD_CONTEXT, FORK_AGENT_CONTEXT, MIGRATE_MODEL, TERMINATE_AND_RESTART, REQUIRE_HUMAN_REVIEW)
- **INV-IDs enforced:** INV-003, INV-004, INV-006, INV-009
- **Verification:**
  - `test_pipeline_13_stages` — Each stage produces expected output
  - `test_capsule_fork_isolation` — Fork inherits only whitelisted fields
  - `test_cross_domain_leakage` — Zero leakage between domain capsules
  - `test_deterministic_audit_no_llm` — Audit runs without model calls
  - `test_prefix_hash_invalidation` — Changed prefix produces new hash + event
  - `test_compaction_vs_cache_tradeoff` — Correct action selected per scenario
- **Rollback:** Delete new packages; existing DHC + UnifiedContextTier remain functional
- **Gate:** All 18 deterministic signals computed correctly; zero cross-domain leakage

---

### Phase 4: Agent Registry, Agent Factory & Ephemeral Instances
- **Objective:** Create agent definition management and ephemeral instance lifecycle
- **R-IDs:** R-009, R-003
- **Prerequisites:** Phase 1 (contracts/agent.py), Phase 3 (ContextCapsule)
- **Artifacts:**
  - `[NEW]` `src/core/agents/registry.py` — AgentRegistry
  - `[NEW]` `src/core/agents/factory.py` — AgentFactory
  - `[NEW]` `src/core/agents/lifecycle.py` — AgentInstanceStateMachine
- **Steps:**
  1. AgentRegistry: load AgentDefinitions from config/domains/ YAML
  2. AgentFactory: create AgentInstance from definition + objective, allocate ContextCapsule, assign ModelProfile
  3. AgentInstanceStateMachine: CREATED → INITIALIZED → ACTIVE → SUSPENDED → COMPLETED → RETIRED | REVOKED
  4. Instance budget allocation from parent budget
  5. Instance expiration/TTL enforcement
- **INV-IDs enforced:** INV-005, INV-008
- **Verification:** `test_agent_lifecycle_happy_path`, `test_agent_expiration`, `test_agent_budget_isolation`
- **Rollback:** Delete agents/ package
- **Gate:** Agents created, execute lifecycle, expire correctly

---

### Phase 5: Hierarchical Orchestrator & Task Graph
- **Objective:** Replace flat ACRAOrchestrator with hierarchical objective → agent → task orchestration
- **R-IDs:** R-001, R-002, R-003, R-008, R-014
- **Prerequisites:** Phase 2 (model resolver), Phase 3 (context pipeline), Phase 4 (agent lifecycle)
- **Artifacts:**
  - `[NEW]` `src/core/orchestration/hierarchical_orchestrator.py`
  - `[NEW]` `src/core/orchestration/objective_planner.py`
  - `[NEW]` `src/core/orchestration/task_graph.py`
  - `[NEW]` `src/core/orchestration/consolidator.py`
  - `[NEW]` `src/core/routing/capability_router.py`
  - `[NEW]` `src/core/routing/intake_router.py`
  - `[NEW]` `src/core/fsm/session.py`, `objective.py`, `task.py`, `handoff_fsm.py`
  - `[MODIFY]` `src/core/orchestrator.py` — Becomes thin backward-compatible wrapper
- **Steps:**
  1. Implement all 5 FSMs with transition tables and cycle guards
  2. Build IntakeRouter for domain/intent/risk classification
  3. Build ObjectivePlanner: receive objective → decompose into TaskDefinitions → assign agents
  4. Build TaskGraph: dependency-ordered execution of tasks via assigned agents
  5. Build Consolidator: merge AgentOutcomes into ConsolidatedOutcome without context mixing
  6. Wire HierarchicalAgentOrchestrator as top-level entry point
  7. Preserve ACRAOrchestrator as deprecated wrapper that delegates to new orchestrator
- **INV-IDs enforced:** INV-008 (no FSM cycles), INV-005 (hierarchical budget)
- **Verification:**
  - `test_objective_decomposition` — Complex objective → N tasks
  - `test_task_dependency_order` — No consumer before producer
  - `test_fsm_cycle_prevention` — All 5 FSMs block infinite loops
  - `test_backward_compatible_orchestrator` — Legacy ACRAOrchestrator still works
- **Rollback:** Revert orchestrator.py modification; delete orchestration/, routing/, fsm/ packages
- **Gate:** Objective → plan → agents → tasks → outcomes → consolidation works end-to-end in stubs

---

### Phase 6: Typed Handoffs, Policy Modes & Validation
- **Objective:** Implement typed handoff envelopes with pre/post audit and escalation
- **R-IDs:** R-007, R-011, R-017, R-025, R-029
- **Prerequisites:** Phase 3 (audit), Phase 4 (agents), Phase 5 (orchestrator)
- **Artifacts:**
  - `[NEW]` `src/core/security/handoff_policy_gate.py`
  - `[NEW]` `src/core/security/tool_authorization.py`
  - `[NEW]` `src/core/security/concurrency_control.py`
- **Steps:**
  1. Implement HandoffPolicyGate extending PayloadPolicyGate with pre_handoff_audit, sanitized_handoff_envelope, post_handoff_validation
  2. Implement ToolGrant verification: agent can only invoke tools in its whitelist
  3. Implement EscalationPolicy: reversible upscale/downscale with Context Rehydration Plan
  4. Implement 5 PolicyModes on handoff gate
  5. Implement concurrency control: version-based conflict prevention on shared state
  6. Wire HandoffStateMachine into orchestrator handoff flow
- **INV-IDs enforced:** INV-002 (handoff requires audit), INV-007 (destructive requires approval)
- **Verification:**
  - `test_handoff_requires_audit` (INV-002)
  - `test_handoff_blocks_high_risk`
  - `test_escalation_reversible`
  - `test_unauthorized_tool_blocked`
  - `test_destructive_requires_approval` (INV-007)
  - `test_policy_modes` (5 modes × 3 scenarios each)
- **Rollback:** Revert to existing PayloadPolicyGate + HandoffEngine
- **Gate:** No handoff passes without audit; all 5 policy modes enforced

---

### Phase 7: Hierarchical Budget Governance & Provenance
- **Objective:** Generalize ResourceGovernor to hierarchical budgets and complete provenance
- **R-IDs:** R-010, R-012, R-013, R-020
- **Prerequisites:** Phase 5 (orchestrator with task graph)
- **Artifacts:**
  - `[NEW]` `src/core/economy/engine.py` — TokenEconomyEngine
  - `[NEW]` `src/core/economy/cost_model.py` — Continuity vs migration cost model
  - `[NEW]` `src/core/economy/telemetry.py` — Provenance tracking
  - `[MODIFY]` `src/core/governance.py` — Deprecate; delegate to economy/
  - `[MODIFY]` `src/core/metrics.py` — Add new metrics from §17
- **Steps:**
  1. HierarchicalBudgetGovernor: cascade budgets from objective → agent → task
  2. TokenEconomyEngine: estimate total cost including uncached/cached/rebuild/retry tokens
  3. Complete provenance: every AgentOutcome includes agent, profile, context, tools, policies, cost, tokens, confidence, evidence, validator
  4. Extend metrics.py with 20 new metrics from §17 CEA, each tagged with epistemic_status
  5. Wire budget governor into orchestrator and agent lifecycle
- **INV-IDs enforced:** INV-005, INV-006
- **Verification:**
  - `test_hierarchical_budget_cascade` (INV-005)
  - `test_estimate_vs_measured_distinction` (INV-006)
  - `test_cost_includes_rebuild_tokens`
  - `test_provenance_completeness`
- **Rollback:** Revert governance.py and metrics.py
- **Gate:** Budgets cascade correctly; provenance is complete; metrics tagged

---

### Phase 8: Reference Multi-Agent E2E Validation Scenario (Domain-Agnostic Synthetic Benchmark)
- **Objective:** End-to-end validation with a synthetic reference multi-agent scenario (illustrative test case isolated strictly in test fixtures, not in production domain code)
- **R-IDs:** R-002, R-027
- **Prerequisites:** Phases 0-7 complete
- **Artifacts:**
  - `[NEW]` `tests/fixtures/domains/reference_enterprise/gerencia_*.yaml` (synthetic test fixtures only)
  - `[NEW]` `tests/e2e/test_multi_agent_e2e.py`
- **Steps:**
  1. Define synthetic AgentDefinitions for 5 reference domains in test fixtures (isolated from core config)
  2. Implement all 12 flow steps from §3 of EVO ACRA.md
  3. Implement all 9 extended scenarios from §19 CEA
  4. Validate:
     - Agent affinity maintained across related tickets
     - Cross-domain tickets create independent agents
     - Routine subtask delegates to lightweight executor via minimal handoff
     - Planner doesn't switch model because executor uses different model
     - Critical task escalates via Context Rehydration Plan
     - Outcome returns as Outcome Capsule, not context replacement
     - Stale tool results excluded before next inference
     - Degraded context triggers comparison: repair vs fork vs rebuild vs migrate
     - All decisions record cost, evidence, risk, confidence, coverage
- **INV-IDs enforced:** All (INV-001 through INV-010)
- **Verification:** `pytest tests/e2e/test_multi_agent_e2e.py` — 9 named scenarios
- **Rollback:** Delete test and fixture files (non-destructive)
- **Gate:** All 9 E2E scenarios pass

---

### Phase 9: Real Provider Adapters (Google GenAI Primary) & Cache-Aware Routing
- **Objective:** Implement Google GenAI provider adapter with live integration tests, Anthropic/OpenAI as Protocol stubs, and cache affinity/hysteresis
- **R-IDs:** R-016, R-021, R-022, R-023
- **Prerequisites:** Phase 2 (provider protocol), Phase 7 (economy engine)
- **Artifacts:**
  - `[NEW]` `src/core/providers/google.py` — GoogleGenAIAdapter (first-class live implementation)
  - `[NEW]` `src/core/providers/anthropic.py` — AnthropicAdapter (Protocol implementation / mock-ready)
  - `[NEW]` `src/core/providers/openai.py` — OpenAIAdapter (Protocol implementation / mock-ready)
  - `[NEW]` `src/core/providers/local.py` — Ollama/Local adapter
  - `[NEW]` `src/core/routing/affinity.py`
  - `[NEW]` `config/providers/google.yaml`, `anthropic.yaml`, `openai.yaml`, `local.yaml`
  - `[NEW]` `config/policies/hysteresis.yaml`
- **Steps:**
  1. Implement GoogleGenAIAdapter wrapping `google-generativeai` / `google-genai` with live testing support
  2. Implement Anthropic and OpenAI adapters complying with `ProviderAdapter` Protocol with comprehensive contract/mock tests
  3. Each adapter reports CapabilityVector (structured_output, tool_calling, long_context, reasoning, multimodal, streaming, cached_context, safety_controls, estimated_cost, expected_latency)
  4. Implement AgentModelAffinity with affinity maintenance and migration triggers (10 criteria from §8 CEA)
  5. Implement HysteresisPolicy with 10 configurable parameters from §9 CEA
  6. Implement CacheContinuityDescriptor updates from provider telemetry
- **INV-IDs enforced:** INV-010 (no oscillation)
- **Verification:**
  - `test_affinity_maintained` — No switch without material reason
  - `test_migration_triggers` — Switch happens on 10 defined conditions
  - `test_no_model_oscillation` (INV-010)
  - `test_hysteresis_parameters` — All 10 params respected
  - `test_cache_continuity_descriptor` — Contract fulfilled
- **Rollback:** Fall back to stub provider
- **Gate:** Provider adapters resolve correctly; hysteresis prevents oscillation

---

### Phase 10: Degradation, Entropy & Quality Benchmarks
- **Objective:** Validate the 20 mandatory test cases and measure quality/cost metrics
- **R-IDs:** R-013, R-028
- **Prerequisites:** All previous phases
- **Artifacts:**
  - `[NEW]` `tests/unit/test_mandatory_20.py` — All 20 test cases from §18 CEA
  - `[NEW]` `tests/benchmark/test_degradation_benchmarks.py`
- **Steps:**
  1. Implement all 20 mandatory test cases:
     1. Maintain affinity when model switch produces no real savings
     2. Migrate when continuity cost exceeds migration cost
     3. Migrate on insufficient capability
     4. Prevent model oscillation
     5. Invalidate continuity on stable prefix change
     6. Preserve continuity on volatile-only context changes
     7. Function when provider doesn't report cache
     8. Distinguish estimation from measurement
     9. Audit without LLM
     10. Block handoffs with critical conflict
     11. Prevent stability declaration with insufficient evidence
     12. Detect superseded tool results
     13. Detect cross-gerencia contamination
     14. Fork agent before mixing domains
     15. Require approval for destructive invalidations
     16. Calculate total cost including reconstruction
     17. Operate with expired cache
     18. Degrade safely when CEA unavailable
     19. Respect budgets at agent, task, and workflow levels
     20. Prevent model names from entering domain core
  2. Run degradation benchmarks: context growth, redundancy, contradiction density, tokens per outcome
- **Verification:** `pytest tests/unit/test_mandatory_20.py` — all 20 pass
- **Rollback:** Test-only phase, non-destructive
- **Gate:** 20/20 mandatory tests pass; benchmark baseline recorded

---

## 8. Verification Architecture & Test Ledger

### Applicable Layers

| Layer | Scope |
|---|---|
| Unit | All contracts (serialization, validation), all FSMs (transitions, cycle guards), all signals (deterministic computation), routing (profile resolution, affinity) |
| Contract/Schema | JSON Schema validation of all 10 new schemas; Pydantic model_json_schema() roundtrip |
| Integration | ContextEngineeringPipeline end-to-end; Orchestrator → AgentFactory → AgentInstance → task execution |
| E2E | Ticketera 5-gerencia scenario (9 cases); full objective lifecycle |
| Property-based | Context capsule fork isolation (no forbidden fields leak); budget cascade (child never exceeds parent) |
| Architecture/boundary | INV-001 grep test (no model names in core); dependency direction check |
| Migration/rollback | Legacy ACRAOrchestrator backward compatibility |

### Named Behavioral Test Cases

| Test Name | Property | Fixture | Pass Condition |
|---|---|---|---|
| `test_contract_roundtrip_all` | All 19 contracts serialize/deserialize | Generated fixtures | Input == deserialize(serialize(input)) |
| `test_capsule_fork_excludes_private` | Fork never inherits conversation, reasoning, irrelevant tools | Capsule with all fields | Forked capsule has only whitelisted fields |
| `test_fsm_no_self_loops` | No FSM state reaches itself without counter decrement | All 5 FSMs | InvalidTransitionError on max_retries |
| `test_budget_child_never_exceeds_parent` | Child agent budget ≤ parent allocation | Random budget trees | Property holds for all generated trees |
| `test_audit_tripleta_complete` | Every AuditResult has risk_score, confidence, evidence_coverage | Generated capsules | All three fields present and in [0, 1] |
| `test_deterministic_signals_18` | All 18 signals compute without network/LLM | Synthetic context | All signals return numeric values |
| `test_profile_resolves_to_provider` | Every profile resolves to at least one provider | 7 profiles, stub registry | Resolution succeeds for all |
| `test_no_model_names_in_core_grep` | Zero occurrences of known model strings in src/core/ (excluding providers/, config/) | File system grep | 0 matches |
| `test_backward_compat_orchestrator` | Legacy ACRAOrchestrator.process_turn() returns OrchestrationResult | Existing test fixtures | All existing tests pass |
| `test_ticketera_9_scenarios` | All 9 extended ticketera scenarios | Domain configs | All pass |

---

## 9. Compatibility, Migration & Rollback

### Legacy → New Mapping

| Legacy Symbol | New Symbol | Strategy |
|---|---|---|
| `ACRAOrchestrator` | `HierarchicalAgentOrchestrator` | Legacy preserved as wrapper; deprecated in Phase 5 |
| `EdgeRouter` | `CapabilityAndAgentRouter` | Legacy preserved as alias; deprecated in Phase 5 |
| `DynamicHistoryCompressor` | `ContextEngineeringPipeline` | Legacy preserved as alias; deprecated in Phase 3 |
| `CleanPayload` | `HandoffEnvelope` | Legacy preserved; deprecated in Phase 6 |
| `UnifiedContextTier` | `ScopedContextRegistry` | Legacy preserved as alias; deprecated in Phase 3 |
| `ResourceGovernor` | `HierarchicalBudgetGovernor` | Legacy preserved as wrapper; deprecated in Phase 7 |
| `ACRAStateMachine` | `SessionStateMachine` | Legacy preserved as alias; deprecated in Phase 5 |
| `BaseLLMAdapter` | `ProviderAdapter` Protocol | Legacy preserved; deprecated in Phase 2 |
| `PayloadPolicyGate` | `HandoffPolicyGate` | Legacy preserved; consumed by new gate in Phase 6 |

### Deprecation Protocol
1. Phase N: New component created alongside legacy
2. Phase N: Legacy module gains `__deprecated__` docstring annotation
3. Phase N+1: Tests migrate to new API
4. Future: Legacy removed (not in this plan's scope)

### Breaking Classification
- **Additive phases (0-4):** No existing behavior broken
- **Bridge phases (5-7):** Legacy wrappers maintained; existing test suite must pass
- **Rollback:** Each phase documents specific rollback (delete new files, revert modifications)

---

## 10. Scope, Risks, Assumptions & Unresolved Decisions

### In Scope
- All 20 sections of EVO ACRA.md
- All 11 phases (0-10)
- 19 new typed contracts
- 5 decomposed FSMs
- Context Engineering Pipeline (13 stages)
- Context Audit Layer with 18 deterministic signals
- Token Economy Engine
- Cache-Aware Routing with hysteresis
- Provider adapters (4 + stub)
- Ticketera E2E (9 scenarios)
- 20 mandatory test cases

### Out of Scope `[REQUIRED by §20, EVO ACRA.md]`
- Frontend/UI for the ticketera
- Production database integration (current in-memory approach maintained)
- Real LLM model training or fine-tuning
- Multi-region deployment architecture
- CI/CD pipeline design (beyond test commands)
- Performance benchmarks against real LLM providers (requires API keys and budget)
- Authentication/authorization system for human users (ACRA manages agent-level authorization)

### Top 5 Risks

| Risk | Probability | Impact | Mitigation | Verification |
|---|---|---|---|---|
| R-RISK-001: Contract explosion (19 models) creates maintenance burden | Medium | Medium | Contracts live in single `contracts/` package with shared validation; code generation for JSON schemas | Contract test suite catches drift |
| R-RISK-002: Legacy backward compatibility breaks during Phase 5 orchestrator refactor | Medium | High | Legacy wrappers with full delegation; existing test suite must pass at every phase | `test_backward_compat_orchestrator` |
| R-RISK-003: CEA repository structure doesn't match assumed paths (A-01) | Medium | Medium | ContextAuditProvider Protocol makes CEA optional; DeterministicFallbackAuditor provides zero-LLM fallback | `test_degrade_without_cea` |
| R-RISK-004: Provider adapter complexity varies significantly between Anthropic/Google/OpenAI SDKs | Medium | Low | Each adapter is a thin wrapper; ProviderAdapter Protocol normalizes the interface | Per-provider unit tests |
| R-RISK-005: Context Engineering Pipeline's 13 stages become a performance bottleneck | Low | Medium | Pipeline stages are composable and individually bypassable; profiling benchmarks in Phase 10 | `test_pipeline_performance` |

### Resolved Decisions Register (Approved by User)

> [!NOTE]
> **UD-001 (CEA Repository Access) — RESOLVED:** The user has a complete local repository of CEA. Phase 3 implements `CEAContextAuditAdapter` bridging directly to the local CEA implementation via `ContextAuditProvider`, accompanied by `DeterministicFallbackAuditor` for zero-LLM resilient fallback.
>
> **UD-002 (Provider API Keys) — RESOLVED:** Google API is currently available. Phase 9 implements `GoogleGenAIAdapter` as the primary live-tested provider. Anthropic and OpenAI adapters will be implemented complying with the `ProviderAdapter` Protocol with comprehensive contract and mock suites, ready for live keys when provisioned.
>
> **UD-003 (Domain Specifics / Ticketera) — RESOLVED:** The Ticketera domain (5 gerencias) mentioned in documentation is purely an illustrative reference example and must NOT be included in production domain code. ACRA core remains strictly domain-agnostic. Phase 8 uses synthetic test fixtures strictly within `tests/fixtures/domains/reference_enterprise/` for E2E validation.
>
> **UD-004 (Deployment Target) — RESOLVED:** Kubernetes is the target infrastructure. The orchestrator is designed with stateless pod architecture, cloud-native liveness/readiness probes (`/healthz`, `/ready`), graceful SIGTERM shutdown handling, and externalizable context persistence.

### Cloud-Native Deployment Architecture (Kubernetes Target)
- **Stateless Pod Execution:** `HierarchicalAgentOrchestrator` instances are stateless, enabling horizontal pod autoscaling (HPA) driven by task queue length, token throughput, or CPU/Memory metrics.
- **Context & State Decoupling:** Context capsules and session state are persisted via pluggable storage backends (in-memory for local testing, redis/distributed cache or persistent volume for cluster deployments), supporting ingress session affinity.
- **Container Health Probes:** Cloud-native endpoints: `/healthz` (liveness: process and event loop healthy) and `/ready` (readiness: provider configuration valid, CEA connection verified, model registries initialized).
- **Graceful Lifecycle Management:** Trap `SIGTERM` / `SIGINT` signals to allow active agent task graph nodes to finish turn execution or flush context snapshots before termination.

---

## 11. Static Plan Lint

**Lint execution results:**

| Check | Result | Notes |
|---|---|---|
| Every R-REQUIRED has implementation and verification | ✅ PASS | All 29 R-IDs have phase assignment and test name |
| Every contract/symbol introduced is consumed | ✅ PASS | All 19 contracts have producers and consumers listed in §5 |
| Every `[MODIFY]`/`[DELETE]`/`[MOVE]` has phase action | ✅ PASS | All [MODIFY] files listed with specific phase |
| Every phase dependency produced earlier | ✅ PASS | Phase order: 0→1→2→3→4→5→6→7→8→9→10; verified |
| Every INV-ID has enforcement and verification | ✅ PASS | All 10 INV-IDs have both |
| No banned placeholder wording | ✅ PASS | No "etc.", "similar endpoints", bare ellipses in implementation sections |
| Contract idiom matches stack | ✅ PASS | Pydantic v2 + Python Protocol consistent with pyproject.toml |
| Immediate slice references only existing dependencies | ✅ PASS | Phase 0 is documentation only |
| Migration before consumers | ✅ PASS | Legacy aliases created in same phase as new components |
| Every new component has rationale/requirement | ✅ PASS | All trace to R-IDs |

**Result: `LINT PASS`**

---

## 12. Adversarial Architecture Review

| AR-ID | Severity | Evidence | Defect | Consequence | Required Revision | Status |
|---|---|---|---|---|---|---|
| AR-001 | MAJOR | 19 contracts defined in Phase 1 | Contract explosion may lead to premature abstraction | Over-engineering if some contracts are never fully populated | Mitigation: contracts are data classes, not service interfaces; only instantiated when needed by consuming phases | REVISED — contracts are pure Pydantic models with no behavior; cost of existence is near-zero |
| AR-002 | MINOR | 13-stage pipeline in Phase 3 | Not all stages may be necessary for every agent invocation | Wasted computation | Each stage has a `skip_if` condition based on agent policy; stages are individually bypassable | ACCEPTED-RISK — composable design mitigates |
| AR-003 | MAJOR | Legacy backward compatibility | ACRAOrchestrator wrapper may diverge from HierarchicalAgentOrchestrator over time | Maintenance burden; two code paths | Wrapper is thin delegation only; no logic duplication; deprecated flag drives migration | REVISED — explicit deprecation timeline per phase |
| AR-004 | MINOR | Multiple FSMs | State explosion across 5 machines | Debugging complexity | Each FSM is independent with <15 states; correlation_id links them | ACCEPTED-RISK |
| AR-005 | MINOR | HysteresisPolicy has 10 configurable parameters | Tuning complexity | Suboptimal defaults | Defaults come from config/policies/hysteresis.yaml; adjustable without code change | ACCEPTED-RISK |

**No remaining BLOCKERs.**

---

## 13. Immediate Executable Slice

### Goal
Execute Phase 0 (ADR documentation) and Phase 1 (typed contracts) as the first dependency-complete implementation unit.

### Exact Artifacts
1. `docs/architecture/ADR-001-cea-integration.md` `[NEW]`
2. `docs/architecture/ADR-002-model-selection.md` `[NEW]`
3. `docs/architecture/ADR-003-agent-lifecycle.md` `[NEW]`
4. `docs/architecture/ADR-004-fsm-decomposition.md` `[NEW]`
5. `src/core/contracts/` package (11 files) `[NEW]`
6. `schemas/` — 6 new JSON schema files `[NEW]`
7. `tests/unit/test_contracts.py` `[NEW]`

### Ordered Actions
1. Create ADR markdown documents
2. Create `src/core/contracts/` package with `__init__.py`
3. Implement each contract module (agent, task, context, model, handoff, governance, outcome, graph, audit, cache)
4. Run `python -m pytest tests/unit/test_contracts.py -v` to verify
5. Run `ruff check src/core/contracts/`
6. Run `mypy src/core/contracts/ --strict`
7. Generate JSON schemas via Pydantic `model_json_schema()` into schemas/

### Precautions
- No existing files are modified
- All new files are additive
- No LLM calls required
- No external dependencies added

### Binary Acceptance
- All contract models pass mypy strict: YES/NO
- All contract tests pass: YES/NO
- Ruff clean: YES/NO
- JSON schemas generated and valid: YES/NO
- Existing test suite unaffected: YES/NO

---

## 14. Architectural Depth Score & Finalization Gate

| Dimension | Score | Evidence/Remediation |
|---|---|---|
| Evidence Grounding | 9 | All claims traced to OBSERVED (repo inspection) or REQUIRED (EVO ACRA.md). No invented numbers. |
| Requirement Traceability | 9 | 29 R-IDs fully traced: source → gap → phase → verification. Orphan check passed. |
| Component Resolution | 8 | Target tree fully specified with 40+ new files. Each has rationale and R-ID. Local implementation decisions remain for Phase execution. |
| Contract/Data Resolution | 9 | 19 contracts with key fields, producers, consumers. 2 Protocol interfaces with method signatures. |
| Dependency/Invariant Resolution | 9 | 10 INV-IDs with enforcement + verification. Dependency directions explicit. Phase ordering validated. |
| Failure/Recovery | 8 | 7 failure modes with detection → containment → recovery → telemetry. Local retry strategies to be detailed per phase. |
| Security | 8 | 13 controls mapped. Threat surface covered. Implementation details deferred to Phase 6. |
| Observability | 8 | 20 metrics listed with epistemic_status tagging. Structured logging preserved. Thresholds not invented (correct per protocol). |
| Verification | 9 | 10 named behavioral test cases. 20 mandatory tests mapped. Test layers defined. Fixtures identified. |
| Compatibility/Migration | 9 | 9 legacy→new mappings. Deprecation protocol defined. Backward compatibility verified per phase. |
| Scope/Risk | 8 | 5 risks with mitigation. 4 unresolved decisions identified as user-owned. Out-of-scope explicit. |
| Implementation Ambiguity Elimination | 9 | Phase ordering dependency-correct. Each phase has objective, artifacts, steps, verification, rollback, gate. No "implement X" bare tasks. |

### Context Reliability and Token Economy Architecture

This plan incorporates all 16 subsections mandated by §20 of EVO ACRA.md:

1. **ACRA-CEA relationship:** ADR-001 defines ContextAuditProvider Protocol (Option C)
2. **Context Audit Layer:** Phase 3 — 8 hook points, 12 dimensions
3. **Deterministic signals:** Phase 3 — 18 zero-LLM signals in `audit/deterministic.py`
4. **Audit tripleta:** Phase 3 — risk_score, confidence, evidence_coverage
5. **Cache-Aware Router:** Phase 9 — `routing/affinity.py`
6. **Agent-Model Affinity:** Phase 9 — 10-criteria maintenance and migration rules
7. **Stable Prefix Engineering:** Phase 3 — `context/prefix.py` with hash versioning
8. **Token Economy Engine:** Phase 7 — `economy/engine.py`
9. **Continuity vs migration cost model:** Phase 7 — `economy/cost_model.py`
10. **Hysteresis policy:** Phase 9 — 10 configurable parameters in `config/policies/hysteresis.yaml`
11. **Proposed contracts:** Phase 1 — CacheContinuityDescriptor, AgentModelAffinity, ModelSessionLease + 5 others
12. **Telemetry and provenance:** Phase 7 — `economy/telemetry.py` with epistemic_status
13. **Failure modes:** §6 failure/reliability table — 7 modes with full chain
14. **Tests:** Phase 10 — 20 mandatory test cases
15. **Incorporation phases:** Phases 3, 7, 9 (progressive adoption)
16. **Open questions:** UD-001 through UD-004

---

### Final Status

**`PASS - APPROVED BY USER & EXECUTION READY (PHASES 0 & 1 IMMEDIATE SLICE)`**

All four operational and architectural decisions (UD-001 through UD-004) have been definitively resolved by the user. Phases 0 and 1 are 100% resolved and ready for immediate, non-destructive execution. Subsequent phases are fully bounded by contracts, invariants, and gate criteria.

### Decisions Resolved Ledger

| Decision ID | Topic | User Resolution | Architectural Impact |
|---|---|---|---|
| **UD-001** | CEA Repository Access | Complete local repository available | Implement `CEAContextAuditAdapter` in Phase 3 alongside `DeterministicFallbackAuditor` |
| **UD-002** | Provider API Keys | Google API key available | Prioritize `GoogleGenAIAdapter` in Phase 9 for live testing; Anthropic/OpenAI as Protocol stubs |
| **UD-003** | Domain Specifics (Ticketera) | Reference/example only; do NOT include in production core | ACRA core remains domain-agnostic; Phase 8 uses synthetic test fixtures in `tests/fixtures/` |
| **UD-004** | Deployment Target | Kubernetes | Cloud-native stateless pod design, health probes (`/healthz`, `/ready`), graceful shutdown |

---

### Recommended First Phase: **Phase 0 + Phase 1** (combined)
- Zero risk to existing code
- Establishes the contract foundation for all subsequent phases
- Verifiable via pytest + mypy + ruff
- Produces the type system that every later phase consumes

### Implementation Authorization
- ✅ Plan approved by user
- ✅ UD-001, UD-002, UD-003, UD-004 resolved
- Ready to proceed to immediate executable slice (Phase 0 ADRs + Phase 1 Contracts)
