# ACRA Security Architecture & STRIDE Threat Model

## 1. Executive Security Summary
Adaptive Conversational Routing Architecture (ACRA) mediates multi-turn conversational interactions by decoupling low-cost edge ambiguity absorption from deep-reasoning frontier clusters. Because the Edge Router, Dynamic History Compressor (DHC), and Unified Context Tier (UCT) manipulate execution payloads before prefill into heavyweight clusters, strict security boundaries and cryptographic invariants are mandatory.

This document details the threat model, attack surface, STRIDE taxonomy, mitigation controls, and verification guarantees implemented in ACRA.

---

## 2. Trust Boundaries & Assets Under Protection

```
               [ UNTRUSTED ZONE ]
                       │
             User Input / External Web
                       │
       ┌───────────────▼────────────────┐
       │   EDGE CLUSTER (Untrusted)      │
       │   - Ambient Chat Turns         │
       │   - Exploration & Clarification │
       └───────────────┬────────────────┘
                       │
         [ BOUNDARY: PayloadPolicyGate ]
         - Static Injection Detection
         - Credential & PII Redaction
         - Trust Promotion Invariant
         - SHA-256 Sterilization Hash
                       │
       ┌───────────────▼────────────────┐
       │   PRO CLUSTER (Frontier Model) │
       │   - Deterministic Execution    │
       │   - Clean Baseline (Zero Drift)│
       └────────────────────────────────┘
```

### Protected Assets
1. **Frontier Model Ingestion Canvas:** Protection against prompt injection, instruction override, and adversarial jailbreaks.
2. **Context Memory Cache (UCT):** Protection against cross-tenant data leakage, cache poisoning, and deserialization attacks.
3. **Sensitive Data Assets:** Prevention of credential leaks (API keys, RSA keys, tokens) and PII propagation into prefill buffers.
4. **Finite Compute Resources:** Prevention of Denial-of-Service via payload inflation and recursive turn exhaustion.

---

## 3. STRIDE Threat Analysis & Implemented Mitigations

| Threat (STRIDE) | Attack Vector | Potential Impact | ACRA Mitigation Architecture | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Untrusted user turns forging role as `system` or claiming verified provenance | Attacker overrides system guardrails | `ContentProvenance` enforcement + `PayloadPolicyGate` blocks `USER_DIRECT` masquerading as `system` role | **Enforced** |
| **Tampering** | In-flight mutation of compressed context or cache key collision | Execution of poisoned instructions in Pro cluster | Cryptographic SHA-256 sterilization hash + tenant salted cache keys | **Enforced** |
| **Repudiation** | Ambiguous turn lineage during security post-mortem | Inability to attribute toxic injections to specific turns | `provenance_chain` records `source_id`, `role`, `provenance`, and `trust_level` for every turn | **Enforced** |
| **Information Disclosure** | Cross-tenant cache hit or hardcoded secrets in conversation history | Leaking confidential proprietary context or user secrets | Multi-tenant isolation (`tenant_id` in UCT) + automated secret & PII redaction (`sanitize()`) | **Enforced** |
| **Denial of Service** | Gigabyte payload inflation or token flooding attacks | Exhausting Edge memory and Pro prefill buffers | `max_payload_bytes` (256 KB hard cap) + `ResourceGovernor` token budgets | **Enforced** |
| **Elevation of Privilege** | Untrusted content promoted to `TRUSTED` state | Malicious prompt executes under system privilege | Invariant rule: `USER_DIRECT` turns cannot hold `TRUSTED` level; violations trigger `POLICY_REJECTED` | **Enforced** |

---

## 4. Policy Gate Enforcement Details

The `PayloadPolicyGate` acts as an absolute deterministic filter prior to calling `HandoffEngine.assemble_clean_payload()`.

```python
result = policy_gate.validate(payload_text, provenance_chain)
if not result.passed:
    # Abort dispatch to pro cluster; retain in Edge
    state = OrchestratorState.POLICY_REJECTED
```

### Key Detection Signatures:
- **Injection Signatures:** `(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions?`, `(?i)system\s+(override|bypass)`, `(?i)jailbreak`, `(?i)dan\s+mode`, `(?i)<\|im_start\|>\s*system`, `(?i)\[INST\]\s*<<SYS>>`.
- **Secret Signatures:** OpenAI API keys (`sk-[a-zA-Z0-9]{20,}`), AWS access keys (`AKIA[0-9A-Z]{16}`), GitHub PATs (`ghp_`), RSA/SSH private keys (`-----BEGIN.*PRIVATE KEY-----`).
- **PII Patterns:** Credit card numbers (Luhn candidate regex), US SSN formats.

---

## 5. Formal Invariants
1. **Zero-Untrusted-Precedence:** No user turn can alter system directives.
2. **Deterministic-Revocation:** If a snapshot is revoked (`revoke_snapshot()`), subsequent retrieval returns `None` deterministically.
3. **Tenant-Partitioning:** Context cached for tenant $T_A$ with session $S$ is strictly disjoint in hash space from tenant $T_B$ with session $S$:
$$\text{CacheKey}(T_A, S, C, \sigma) \neq \text{CacheKey}(T_B, S, C, \sigma)$$
