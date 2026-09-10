# ACRA System Specification v2.0
## Formal Architecture, Mathematical Model, and Operational Semantics

**Document Identifier:** `ACRA-SPEC-2026-V2`  
**Status:** Canonical Engineering Specification  
**Classification:** Research / Enterprise Systems Architecture  

---

## 1. System Overview & Core Invariants

The Adaptive Conversational Routing Architecture (ACRA) mediates multi-turn conversational interactions between client applications and heterogeneous Large Language Model (LLM) clusters.

### Core Architectural Invariants:
1. **The Asymmetry Invariant:** The heavy frontier reasoning model (Pro cluster) SHALL NOT process conversational turns while specification maturity $M(\vec{v})$ remains below the configured threshold $\theta_{\text{maturity}}$ ($0.70$).
2. **The Clean Baseline Invariant:** All payloads dispatched to the Pro cluster SHALL be synthesized into a consolidated canvas purged of conversational drift, disclaimers, greetings, and apologies, achieving a Context Consolidation Ratio $CCR \ge 0.45$ for interactions with turn depth $N > 3$.
3. **The Non-Promotion Invariant:** Content originating from untrusted client turns (`USER_DIRECT`) SHALL NOT be promoted to `TRUSTED` or `VERIFIED` levels without explicit deterministic verification via `PayloadPolicyGate`.
4. **The Tenant Partitioning Invariant:** Memory snapshots cached in the Unified Context Tier (UCT) for tenant $T_A$ with session $S$ SHALL be cryptographically disjoint from tenant $T_B$ with session $S$:
$$\text{CacheKey}(T_A, S, C, \sigma) \neq \text{CacheKey}(T_B, S, C, \sigma)$$
5. **The Resource Bound Invariant:** No session SHALL exceed the configured token budget $B_{\text{tokens}}$ ($64,000$ tokens) or turn recursion limit $K_{\text{turns}}$ ($25$ turns).

---

## 2. Component Specifications

### 2.1. Resource Governor (`src/core/governance.py`)
- **Interface:** `check_and_record(session_id, tokens_added, latency_added_ms, cost_added_usd) -> ResourceUsage`
- **Behavior:** Tracks cumulative consumption in constant time $\mathcal{O}(1)$. Throws `BudgetExceededError` if any bound is violated, triggering immediate quarantine.

### 2.2. Asymmetric Edge Router (`src/core/edge_router.py`)
- **Interface:** `route(history: List[MessageTurn], current_input: str) -> RouterDecision`
- **Maturity Vector Formulation:**
$$\vec{M} = \langle A_{\text{sem}}, C_{\text{ctx}}, R_{\text{arch}}, D_{\text{turn}} \rangle \in [0, 1]^4$$
$$M_{\text{composite}} = 0.40 \cdot C_{\text{ctx}} + 0.30 \cdot (1 - A_{\text{sem}}) + 0.20 \cdot D_{\text{turn}} + 0.10 \cdot (1 - R_{\text{arch}})$$
- **Routing Transition Rule:**
$$\text{Action} = \begin{cases} \text{HOLD} & \text{if } N_{\text{turns}} < N_{\text{min\_pro}} \\ \text{DISPATCH\_PRO} & \text{if } M_{\text{composite}} \ge \theta_{\text{maturity}} \\ \text{CLARIFY} & \text{otherwise} \end{cases}$$

### 2.3. Dynamic History Compressor (`src/core/dhc.py`)
- **Interface:** `compress(history: List[MessageTurn], current_input: str) -> CompressedContext`
- **Operational Logic:**
  1. Identifies and strips conversational chatter and polite boilerplate using regex filter patterns.
  2. Retains architectural decisions, protocol choices, and constraints (`retained_decisions`).
  3. Detects requirements amended or cancelled by the user and records them in `superseded_items`.
  4. Preserves markdown code fences (`crystallized_code_artifacts`).
  5. Computes Context Consolidation Ratio ($CCR$).

### 2.4. Unified Context Tier (`src/core/unified_context.py`)
- **Interface:** `persist_snapshot(...)`, `get_latest_snapshot(...)`, `revoke_snapshot(...)`
- **Key Formulation:**
$$\text{Key} = \text{SHA256}(T_{\text{tenant}} \parallel S_{\text{session}} \parallel P_{\text{clean}} \parallel \sigma_{\text{salt}})$$
- **Revocation Semantics:** Upon receiving a revocation request, the snapshot's `is_revoked` flag is set to `True`. Subsequent queries for that snapshot return `None` in $\mathcal{O}(1)$.

### 2.5. Payload Policy Gate (`src/core/payload_policy.py`)
- **Interface:** `validate(payload_text: str, provenance_chain: List[Dict]) -> PolicyValidationResult`
- **Inspection Layers:**
  1. Payload byte ceiling ($256$ KB).
  2. Static prompt injection signatures (system override, jailbreak, DAN mode).
  3. Credential leakage patterns (OpenAI, AWS, GitHub PATs, RSA private keys).
  4. PII detection (credit card candidate numbers, SSNs).
  5. Trust level escalation verification.

### 2.6. Clean Baseline Handoff Engine (`src/core/handoff.py`)
- **Interface:** `assemble_clean_payload(...) -> CleanPayload`
- **Output Properties:** `is_sterilized: bool`, `sterilization_hash: str`, `validation_result: PolicyValidationResult`, `schema_version: "2.0.0"`.

---

## 3. Finite State Machine (FSM) Formal Grammar

The system lifecycle is governed by a 12-state deterministic automaton $\mathcal{M} = \langle \mathcal{Q}, \Sigma, \delta, q_0, \mathcal{F} \rangle$:

$$\mathcal{Q} = \{ \text{IDLE}, \text{INGESTING}, \text{CLARIFYING}, \text{CONSOLIDATING}, \text{VALIDATING}, \text{POLICY\_REJECTED}, \text{FALLBACK}, \text{ROUTING\_PRO}, \text{EXECUTING\_PRO}, \text{RESPONDING}, \text{REVOKED}, \text{TERMINATED} \}$$

$$\delta(\text{IDLE}, \text{input}) = \text{INGESTING}$$
$$\delta(\text{INGESTING}, \text{vague}) = \text{CLARIFYING}$$
$$\delta(\text{INGESTING}, \text{mature}) = \text{CONSOLIDATING}$$
$$\delta(\text{CONSOLIDATING}, \text{compressed}) = \text{VALIDATING}$$
$$\delta(\text{VALIDATING}, \text{passed}) = \text{ROUTING\_PRO}$$
$$\delta(\text{VALIDATING}, \text{violation}) = \text{POLICY\_REJECTED}$$
$$\delta(\text{POLICY\_REJECTED}, \text{contain}) = \text{FALLBACK} \lor \text{RESPONDING}$$
$$\delta(\text{ROUTING\_PRO}, \text{handoff}) = \text{EXECUTING\_PRO}$$
$$\delta(\text{EXECUTING\_PRO}, \text{done}) = \text{RESPONDING}$$
$$\delta(\text{RESPONDING}, \text{next\_turn}) = \text{IDLE}$$

---

## 4. Operational Telemetry & Logging Format

All events emitted by ACRA adhere to the JSON schema:

```json
{
  "timestamp": "2026-09-09T23:00:00.000Z",
  "timestamp_epoch": 1788998400.0,
  "level": "INFO",
  "component": "orchestrator",
  "session_id": "sess_001",
  "correlation_id": "a1b2c3d4",
  "message": "Turn 2 processed successfully under clean baseline.",
  "caller": "orchestrator.py:120"
}
```
