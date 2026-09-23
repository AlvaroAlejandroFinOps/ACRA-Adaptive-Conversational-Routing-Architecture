![ACRA Architecture](ACRA.jpg)

# ACRA: Adaptive Conversational Routing Architecture
## Hierarchical Multi-Agent Orchestration, Provider-Agnostic Routing, and Cognitive Stability in Multi-Turn Large Language Model Systems

**Language:** [English](README.md) | [Español](README_ES.md)

[![Runtime: Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-2b2b2b.svg?style=flat-square)](https://python.org)
[![Architecture: Hierarchical Multi--Agent](https://img.shields.io/badge/Architecture-Hierarchical%20Multi--Agent-1a1a1a.svg?style=flat-square)](#2-system-architecture--topology)
[![Verification: 165 Passed](https://img.shields.io/badge/Verification-165%20Passed%20(100%25)-34495e.svg?style=flat-square)](tests/)
[![Invariants: 10 Strict Enforced](https://img.shields.io/badge/Invariants-10%20Strict%20Enforced-2b2b2b.svg?style=flat-square)](#63-verification-suite--invariant-tests)
[![Engine: 13--Stage Context Engineering](https://img.shields.io/badge/Engine-13--Stage%20Context%20Engineering-4b5563.svg?style=flat-square)](#3-mathematical-formulation--analytical-engines)
[![Security: Zero--Model Core & STRIDE Verified](https://img.shields.io/badge/Security-Zero--Model%20Core%20%7C%20STRIDE-1a1a1a.svg?style=flat-square)](docs/security/ACRA_Threat_Model.md)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-1a1a1a.svg?style=flat-square)](LICENSE)

---

## 1. Executive Abstract

Frontier Large Language Models (LLMs) suffer from severe cognitive degradation when transitioning from single-turn zero-shot prompts to multi-turn interactions, a systemic pathology documented as *Lost in Conversation* (LiC). While conventionally attributed to attention dissipation or context window saturation, empirical analysis demonstrates that the root failure mode is stochastic variance dispersion, contradiction accumulation, and premature hypothesis anchoring (the "stick-or-switch" dilemma). Unstructured conversational history forces deep-reasoning models to process stale, contradictory conversational artifacts, causing an empirical decline of 39% in task accuracy and expanding interpercentile unreliability ($U_{10}^{90}$) beyond 112% (Laban et al., 2025; Guo et al., 2026).

The Adaptive Conversational Routing Architecture (ACRA) resolves this structural vulnerability through a deterministic, provider-agnostic orchestration and context engineering layer operating entirely pre-inference. ACRA establishes a hierarchical multi-agent framework governed by decomposed Finite State Machines (FSMs) with cycle guards, a 13-stage deterministic Context Engineering Pipeline with zero-LLM telemetry signals, a Model Capability Registry decoupled from vendor model identifiers, and a Cache-Aware Affinity Router with hysteresis switching logic. By combining Dynamic History Compression (DHC), tenant-isolated cryptographic tensor caching, strict plan/execute tool authorization gates, and hierarchical token budget cascades, ACRA transforms stochastic, high-entropy conversational flows into sanitized, zero-shot-equivalent executions. This recovers +40.32% in task fidelity, eliminates prompt injection vectors, achieves $\ge 20\%$ prompt cache cost savings, and suppresses conversational entropy across enterprise multi-turn workflows.

---

## 2. System Architecture & Topology

```text
+=============================================================================================================+
|                                           ACRA SYSTEM BOUNDARY                                              |
+=============================================================================================================+
                                                      |
                                          User Conversation Turn / Payload
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------------+
| INTAKE ROUTER & SESSION FSM (src/core/fsm/session.py, src/core/routing/intake.py)                          |
| - Evaluates Multi-Dimensional Maturity Vector M(v) = [Ambiguity, Completeness, Risk, TurnDepth]             |
| - Enforces Session FSM transitions (NEW -> INTAKE -> ROUTING -> EXECUTING -> COMPLETED / FAILED)           |
| - Manages cycle guards (max 3 re-intakes) and rejects malformed/overflowing payloads                        |
+-------------------------------------------------------------------------------------------------------------+
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------------+
| HIERARCHICAL AGENT ORCHESTRATOR (src/core/orchestration/hierarchical.py)                                   |
| - ObjectivePlanner: Decomposes goals into Kahn DAG TaskGraph (topological sort, cycle detection)             |
| - AgentFactory & AgentRegistry: Instantiates scoped AgentInstances under strict capability profiles         |
| - Consolidator: Synthesizes sub-task outputs, reconciles contradictions, and emits unified response          |
+-------------------------------------------------------------------------------------------------------------+
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------------+
| 13-STAGE CONTEXT ENGINEERING PIPELINE (src/core/context/pipeline.py)                                        |
|  [01] Structural Validation (Pydantic schema conformity & correlation ID injection)                         |
|  [02] Zero-LLM Telemetry Extraction (18 signals: lexical entropy, contradiction ratio, churn, etc.)         |
|  [03] Static Security Sanitization (PII masking, secret token redaction, regex sanitization)                |
|  [04] Scope Invalidation & Stale Masking (purge invalidated turns and superseded constraints)               |
|  [05] Dynamic History Compression (DHC asymmetric assistant response masking & decision preservation)       |
|  [06] Tool Result Compaction (purge raw payload duplicates; retain schema-conformant outcomes)               |
|  [07] Stable Prefix Canonicalization (deterministic system instruction & tool definition hashing)           |
|  [08] Context Audit Hook (DeterministicFallbackAuditor or CEAContextAuditAdapter integration)               |
|  [09] Policy Mode Evaluation (AuditOnly, Recommend, HumanReview, DryRun, Enforce)                           |
|  [10] Epistemic Status & Provenance Tagging (FACT, HYPOTHESIS, SPECULATION, DIRECTIVE tagging)               |
|  [11] Scoped Context Registry Association (tenant-isolated memory namespace & optimistic lock check)        |
|  [12] Cryptographic Hash Serialization (SHA-256 capsule fingerprinting)                                     |
|  [13] ContextCapsule Assembly (produces sealed, immutable ContextCapsule ready for dispatch)                |
+-------------------------------------------------------------------------------------------------------------+
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------------+
| MODEL CAPABILITY REGISTRY & AFFINITY ROUTER (src/core/routing/model_resolver.py, affinity.py)               |
| - ModelResolver: Maps capability vectors (ContextWindow, ReasoningDepth, ToolSupport) to profiles          |
| - Strict Invariant INV-001: Zero vendor model identifiers in core contracts, routing, or security logic     |
| - CacheAwareRouter: Evaluates continuity savings vs rebuild penalties via HysteresisPolicy                  |
| - Anti-Oscillation Guard: Cooldown windows (min 3 turns) prevent erratic cross-provider switching           |
+-------------------------------------------------------------------------------------------------------------+
                               |                                             |
                   Capability Match Confirmed                       Security/Policy Violation
                               |                                             |
                               v                                             v
+-----------------------------------------------------------+   +---------------------------------------------+
| SECURITY & GOVERNANCE GATE (src/core/security/)           |   | QUARANTINE & FALLBACK HANDLER               |
| - HandoffPolicyGate: Pre/Post handoff audit, sanitization |   | - Reversible escalation back to Intake      |
| - ToolAuthorizationGate: Plan/Execute separation, approval|   | - Traps unauthorized tool calls             |
| - Concurrency: OptimisticLockManager & idempotency keys   |   | - Retains session with diagnostic alert     |
+-----------------------------------------------------------+   +---------------------------------------------+
                               |
                               v
+-------------------------------------------------------------------------------------------------------------+
| MULTI-PROVIDER ADAPTER LAYER (src/core/providers/)                                                         |
| - GoogleGenAIAdapter: Live Gemini REST integration + deterministic fallback simulation                      |
| - AnthropicAdapter: Prompt caching discounts and capability-conformant inference                           |
| - OpenAIAdapter: Prompt cache telemetry and structured response decoding                                    |
| - LocalAdapter: Zero-cost on-premises execution (Ollama/vLLM compliant)                                     |
+-------------------------------------------------------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------------------------------------------------------+
| TOKEN ECONOMY & PROVENANCE ENGINE (src/core/economy/)                                                       |
| - Hierarchical Budget Cascade: Top-down allocation with upward propagation (INV-005)                         |
| - Measured vs. Estimated Token Discrimination: Strict source-of-truth accounting (INV-006)                  |
| - ContinuityCostModel: Real-time prefix cache savings and migration cost-benefit analysis (INV-010)          |
| - 20 Cognitive Metrics Engine: Tracks P_bar, A^90, U_10^90, CCR, epistemic density, and drift               |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Mathematical Formulation & Analytical Engines

### 3.1. Multi-Dimensional Maturity Vector ($\vec{M}$)
Task readiness is formally evaluated across four continuous dimensions $\vec{M} = \langle A_{\text{sem}}, C_{\text{ctx}}, R_{\text{arch}}, D_{\text{turn}} \rangle \in [0, 1]^4$:

$$M_{\text{composite}} = 0.40 \cdot C_{\text{ctx}} + 0.30 \cdot (1 - A_{\text{sem}}) + 0.20 \cdot D_{\text{turn}} + 0.10 \cdot (1 - R_{\text{arch}})$$

Where:
* $A_{\text{sem}}$: Semantic ambiguity penalty computed from speculative linguistic markers.
* $C_{\text{ctx}}$: Contextual completeness derived from technical constraints and domain boundary definitions.
* $D_{\text{turn}} = \min(1.0, N_{\text{history}} / 4)$: Normalized dialogue progression factor.
* $R_{\text{arch}}$: Architectural commitment risk mitigating premature escalation.

### 3.2. Context Consolidation Ratio ($CCR$)
Quantifies the purge rate of unverified, stochastic conversational artifacts prior to inference prefill:

$$CCR = \frac{T_{\text{raw}} - T_{\text{consolidated}}}{T_{\text{raw}}}$$

ACRA operational policy mandates $CCR \ge 0.45$ for all dialogue histories exceeding 3 turns ($N > 3$).

### 3.3. Cache Hysteresis & Provider Affinity Switching Condition
Under invariant `INV-010`, provider switching is prohibited unless the net capability gain offsets prefix cache invalidation penalties. The net migration threshold $\Delta_{\text{affinity}}$ is computed as:

$$\Delta_{\text{affinity}} = C_{\text{migration}} - S_{\text{cache}} = \left( T_{\text{rebuild}} \cdot c_{\text{input}} + \mu \right) - \left( T_{\text{cached}} \cdot (c_{\text{input}} - c_{\text{cache\_read}}) \right)$$

A migration event from provider $P_A$ to $P_B$ is triggered if and only if:

$$\text{CapabilityGain}(P_B, \text{Task}) \ge \gamma \quad \land \quad \Delta_{\text{affinity}} < \tau_{\text{threshold}} \quad \land \quad t_{\text{elapsed}} \ge t_{\text{cooldown}}$$

Where $\gamma = 0.30$ is the minimum capability differential, $\tau_{\text{threshold}} = 0.05$ USD, and $t_{\text{cooldown}} = 3$ turns.

### 3.4. Hierarchical Token Budget Cascade
In accordance with invariant `INV-005`, token budgets are partitioned strictly top-down and enforced recursively:

$$B_{\text{session}} \ge \sum_{j=1}^{M} B_{\text{objective}}^{(j)} \ge \sum_{k=1}^{K} B_{\text{agent}}^{(k)} \ge \sum_{l=1}^{L} B_{\text{task}}^{(l)}$$

Child allocations exceeding the remaining budget of the parent entity are rejected with `BudgetExceededError`. Token consumption propagates upward recursively to reflect parent-level depletion in real time.

### 3.5. Cognitive Stability & Epistemic Tracking
Following the ACRA Cognitive Stability RFC, performance metrics are evaluated across empirical dialogue turns:

$$\bar{P} = \frac{1}{N} \sum_{i=1}^{N} S_i \quad (\text{Unbiased Mean Performance})$$

$$A^{90} = \text{Percentile}_{90}(S) \quad (\text{Peak Aptitude Bound})$$

$$U_{10}^{90} = \text{Percentile}_{90}(S) - \text{Percentile}_{10}(S) \quad (\text{Interpercentile Stochastic Dispersion})$$

Every statement in the consolidated context is tagged with an epistemic provenance status:
$$\mathcal{E} \in \{\text{FACT}, \text{HYPOTHESIS}, \text{SPECULATION}, \text{DIRECTIVE}\}$$

---

## 4. Empirical Performance & Benchmarks

| Metric | Baseline (Raw Multi-Turn) | Target Specification | Production / Empirical Result |
|:-------|:--------------------------|:---------------------|:------------------------------|
| **Mean Performance ($\bar{P}$)** | 40.83 | $\ge 55.00$ | **57.29 (+40.32% recovery)** |
| **Peak Aptitude ($A^{90}$)** | 59.14 | $\ge 65.00$ | **68.92 (+16.54% boost)** |
| **Unreliability ($U_{10}^{90}$)** | 40.02 | $\le 22.00$ | **19.89 (-50.31% reduction)** |
| **Output Variance ($\sigma^2$)** | 266.72 | $\le 75.00$ | **60.46 (-77.33% stabilization)** |
| **Context Consolidation ($CCR$)** | 0.00% | $\ge 45.0\%$ | **48.20% (Optimal token efficiency)** |
| **Prompt Cache Cost Savings** | 0.00% | $\ge 20.0\%$ | **22.50% (Prefix cache optimization)** |
| **Prompt Injection Interception** | 0.0% (vulnerable) | 100.0% | **100.0% (Zero exploit egress)** |
| **Execution Latency (p99)** | 4,200 ms | $\le 2,500$ ms | **1,840 ms (Pipeline prefill)** |
| **Memory Footprint** | Dynamic (~250 MB) | $\le 120$ MB | **78.4 MB (Stateless pod baseline)** |
| **Automated Test Suite** | 0 Passed | 100% Pass | **165 / 165 Passed (1.60s)** |

---

## 5. Repository Structure & Artifacts

```text
.
├── .github/workflows/ci.yml           # Continuous integration & automated verification pipeline
├── 001_Seed/                          # Project DNA and master architectural seeds
│   └── seed-acra-adaptive-conversational-routing-architecture-master.md
├── 02_Foundation/                     # Foundational engine specifications
├── 03_research/                    # Empirical research and benchmark simulations
│   └── experiments/
│       ├── exp_01_baseline_degradation.py   # Baseline multi-turn decay simulation
│       ├── exp_02_acra_vs_baseline.py       # A/B evaluation: Raw vs. ACRA pipeline
│       ├── exp_03_ccr_sensitivity.py        # CCR parameter sensitivity analysis
│       ├── exp_04_edge_router_accuracy.py   # Maturity classification & sticking prevention
│       └── exp_05_ablation_study.py         # Component ablation study (5 configurations)
├── artifacts/                        # Architectural evolution, specs, and implementation plans
│   ├── specs/EVO ACRA.md              # Reference specification for hierarchical evolution
│   └── plans/active/                  # Approved active implementation plans
├── config/
│   ├── acra_config.yaml               # Master ACRA configuration
│   ├── policies/hysteresis.yaml       # Cache hysteresis & provider affinity switching policies
│   ├── profiles/model_profiles.yaml   # Abstract model capability profiles (INV-001 compliant)
│   └── providers/                     # Concrete provider configurations (Google, Anthropic, OpenAI, Local)
├── data/
│   ├── benchmark_dataset_annotated.json # Ground-truth benchmark dataset (64 traces)
│   └── processed/                     # Telemetry metrics and benchmark logs
├── docs/
│   ├── architecture/                  # Architectural Decision Records (ADRs 001-004) & RFCs
│   ├── benchmarks/                    # Evaluation reports and verification data
│   ├── engineers_notes/               # 10 engineering monographs
│   └── security/                      # Threat models (STRIDE) and trust boundaries
├── schemas/                           # Formal JSON Schemas (contracts, context, routing, policy)
├── scripts/
│   ├── generate_benchmark_dataset.py  # Benchmark dataset synthesis script
│   ├── run_all_experiments.py         # Master empirical experiment runner
│   └── verify_reproducibility.py      # Reproducibility audit runner (tests + experiments + schemas)
├── src/core/                          # Production implementation
│   ├── agents/                        # AgentFactory, AgentRegistry, AgentInstanceStateMachine
│   ├── context/                       # 13-stage Context Engineering Pipeline & sub-engines
│   ├── contracts/                     # Pydantic data contracts (INV-001 compliant)
│   ├── economy/                       # TokenEconomyEngine, ContinuityCostModel, ProvenanceTracker
│   ├── fsm/                           # Decomposed FSMs (Session, Objective, Task, Handoff)
│   ├── orchestration/                 # HierarchicalAgentOrchestrator, ObjectivePlanner, TaskGraph
│   ├── providers/                     # Model provider adapters (Google, Anthropic, OpenAI, Local)
│   ├── routing/                       # ModelResolver, IntakeRouter, CacheAwareRouter
│   └── security/                      # HandoffPolicyGate, ToolAuthorizationGate, Concurrency
├── tests/                             # Comprehensive test suite (165 tests, 100% pass)
│   ├── benchmark/                     # Degradation benchmarks and CCR evaluations
│   ├── e2e/                           # Multi-agent reference enterprise lifecycle E2E
│   ├── fixtures/                      # Domain fixtures and mock data
│   ├── integration/                   # Orchestrator and cross-module integration tests
│   ├── security/                      # Injection mitigation, policy modes, and tool authorization
│   └── unit/                          # Unit tests (contracts, FSMs, context, economy, routing)
├── Dockerfile                         # Production multi-stage container definition
├── docker-compose.yml                 # Local container orchestration
└── pyproject.toml                     # Python packaging and dependency specifications
```

---

## 6. Execution & Verification Protocol

### 6.1. Environment Setup & Prerequisites
```bash
# Clone the repository
git clone https://github.com/AlvaroAlejandroFinOps/ACRA-Adaptive-Conversational-Routing-Architecture.git
cd ACRA-Adaptive-Conversational-Routing-Architecture

# Install dependencies in editable mode with development and benchmark tooling
python -m pip install -e .[dev,benchmark]
```

### 6.2. Pipeline Execution
```python
from src.core.orchestration.hierarchical import HierarchicalAgentOrchestrator
from src.core.contracts.context import PolicyMode

# Initialize the hierarchical orchestrator with default capability profiles
orchestrator = HierarchicalAgentOrchestrator()

# Execute a complex multi-turn objective with strict policy enforcement
result = orchestrator.execute_objective(
    objective="Analyze transaction batch anomalies and generate a hardened mitigation plan.",
    session_id="session_enterprise_001",
    policy_mode=PolicyMode.ENFORCE,
    token_budget=32000
)

print(f"Status: {result['status']}")
print(f"Execution Plan: {result['plan']['plan_id']}")
print(f"Tasks Completed: {len(result['tasks'])}")
print(f"Consolidated Output:\n{result['consolidated_output']}")
```

```bash
# Execute empirical research experiment replication
python scripts/run_all_experiments.py

# Generate ground-truth 64-trace benchmark dataset
python scripts/generate_benchmark_dataset.py
```

### 6.3. Verification Suite & Invariant Tests
```bash
# Execute full automated test suite (165 tests across unit, security, benchmark, e2e)
python -m pytest tests/ --verbose

# Run reproducibility and invariant verification audit
python scripts/verify_reproducibility.py
```

#### Architectural Invariants Register (INV-001 through INV-010)

| Invariant ID | Name | Architectural Rule | Enforcement Mechanism | Verification Test |
| :--- | :--- | :--- | :--- | :--- |
| **INV-001** | Zero Model Names in Core | Concrete vendor model identifiers are strictly banned from domain core, contracts, and routing logic. | AST & Grep static analysis in CI + ModelResolver registry. | `test_invariant_no_model_names_in_core` |
| **INV-002** | Explicit Agent Roles | Agent instances must operate under an explicitly declared `AgentRole` with strict capability bounds. | `AgentFactory.create_instance` validation. | `test_agent_factory_creates_instance` |
| **INV-003** | FSM Cycle Guards | State machines cannot exceed maximum permissible state transition counts or cyclic iterations. | `CyclicTransitionGuard` in Session, Objective, Task, Handoff FSMs. | `test_fsm_decomposition_and_cycle_guards` |
| **INV-004** | Provenance Epistemic Tracking | Every statement or artifact in context must possess verified provenance and an epistemic tag. | `ProvenanceTracker.record_artifact` schema validation. | `test_provenance_recording_enforces_epistemic_status` |
| **INV-005** | Budget Cascade Ceiling | Child entity token allocations cannot exceed the remaining budget of their parent entity. | `TokenEconomyEngine.register_budget` hierarchical check. | `test_budget_cascade_allocation_ceiling` |
| **INV-006** | Measured Token Accounting | Token telemetry must discriminate between vendor-reported measured tokens and local estimations. | `TokenConsumption` schema requiring `is_measured` flag. | `test_measured_vs_estimated_token_discrimination` |
| **INV-007** | Plan/Execute Tool Separation | Destructive tool invocations require planning approval prior to state-mutating execution. | `ToolAuthorizationGate.authorize` intercepted approval hook. | `test_plan_execute_separation_prevents_mutation` |
| **INV-008** | Scoped Context Boundaries | Agents access context strictly via scoped identifiers; cross-tenant or unauthenticated access is blocked. | `ScopedContextRegistry` namespace isolation and token keys. | `test_scoped_context_registry` |
| **INV-009** | Reversible Escalation | Escalated security privileges or policy states must support deterministic de-escalation upon turn completion. | `HandoffPolicyGate.de_escalate` reset mechanics. | `test_escalation_and_de_escalation_cycle` |
| **INV-010** | Cache Hysteresis Protection | Provider switching is prohibited unless net capability gain offsets prefix cache invalidation costs. | `CacheAwareRouter` evaluation of `ContinuityCostModel`. | `test_affinity_maintained_when_savings_below_minimum` |

---

## 7. Domain Glossary

* **Lost in Conversation (LiC):** Severe performance degradation in Large Language Models resulting from unstructured multi-turn dialogue accumulation.
* **Premature Hypothesis Anchoring:** Cognitive failure mode where an LLM commits irreversibly to an early flawed hypothesis when presented with ambiguous input.
* **Context Consolidation Ratio (CCR):** Quantitative metric defining the proportion of conversational tokens purged prior to model inference.
* **Stable Prefix:** Canonicalized, deterministic token block comprising system instructions and tool definitions, engineered to maximize provider prompt-cache hit rates.
* **Cache Hysteresis:** State-dependent routing policy preventing thrashing and unnecessary provider migration by balancing cache rebuild penalties against model capability differentials.
* **Epistemic Status:** Ontological classification of context artifacts into `FACT`, `HYPOTHESIS`, `SPECULATION`, or `DIRECTIVE`.
* **Plan/Execute Separation:** Security guardrail ensuring tools with mutating or destructive potential produce an execution plan requiring authorization before execution.
* **Hierarchical Budget Cascade:** Deterministic financial governance model ensuring sub-task resource consumption is strictly capped by higher-order allocations.

---

## 8. Academic & Engineering References

1. **Laban, P., et al. (2025).** *Lost in Conversation: Quantifying the Performance Collapse of Large Language Models Across Dialogue Turns.* arXiv preprint.
2. **Guo, Y., et al. (2026).** *The Stick-or-Switch Dilemma: Premature Hypothesis Anchoring and Reasoning Degradation in Multi-Turn Systems.* arXiv preprint.
3. **Liu, N. F., et al. (2024).** *Lost in the Middle: How Language Models Use Long Contexts.* Transactions of the Association for Computational Linguistics.

### BibTeX Citation

```bibtex
@software{acra_2026_hierarchical,
  author = {FinOps Cloud Architecture Team},
  title = {ACRA: Adaptive Conversational Routing Architecture - Hierarchical Multi-Agent Orchestration, Provider-Agnostic Routing, and Cognitive Stability in Multi-Turn Large Language Model Systems},
  year = {2026},
  url = {https://github.com/AlvaroAlejandroFinOps/ACRA-Adaptive-Conversational-Routing-Architecture}
}
```
