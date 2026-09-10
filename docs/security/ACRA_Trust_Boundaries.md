# ACRA Trust Boundaries & Provenance Verification Specification

## 1. Provenance Hierarchy

ACRA classifies conversational tokens across 7 distinct provenance tiers and 4 cryptographic trust levels:

### Provenance Classification (`ContentProvenance`)
| Tier | Provenance Identifier | Origin | Inherent Trust |
| :--- | :--- | :--- | :--- |
| **0** | `SYSTEM_PROMPT` | Static operator configuration | `TRUSTED` |
| **1** | `MEMORY_CACHE` | Verified UCT Snapshot with valid hash | `VERIFIED` |
| **2** | `CONFIRMED_ARTIFACT` | Validated code block / architectural decision | `VERIFIED` |
| **3** | `ASSISTANT_GENERATED` | Edge model or Pro model response | `VERIFIED` (if sanitized) |
| **4** | `RETRIEVED_CONTEXT` | Vector DB or external RAG source | `UNTRUSTED` |
| **5** | `EXTERNAL_TOOL` | Tool output / API response | `UNTRUSTED` |
| **6** | `USER_DIRECT` | Direct client input stream | `UNTRUSTED` |

### Trust Levels (`TrustLevel`)
- `TRUSTED`: Authorized system configuration. Cannot be overridden by lower tiers.
- `VERIFIED`: Content that has passed through DHC compression and `PayloadPolicyGate` validation.
- `UNTRUSTED`: Raw incoming content. Must undergo sanitization and policy inspection.
- `TAINTED`: Flagged content containing injection patterns, leaked secrets, or syntax anomalies.

---

## 2. Invariants & Escalation Rules

### Invariant 1: Non-Promotion Rule
An untrusted turn (`USER_DIRECT`, `EXTERNAL_TOOL`, `RETRIEVED_CONTEXT`) cannot transition to `TRUSTED` or `VERIFIED` status without explicit deterministic validation via `PayloadPolicyGate`. Any turn claiming `role=system` with provenance `USER_DIRECT` triggers immediate `POLICY_REJECTED`.

### Invariant 2: Dynamic History Sanitization
During dynamic compression (DHC):
- Conversational chatter is eliminated.
- Confirmed architectural decisions and code blocks are preserved.
- If a user cancels or amends a requirement, it is marked in `superseded_items` rather than silently erased.

### Invariant 3: Handoff Verification
Every payload prepared for Pro cluster execution includes:
- `sterilization_hash`: SHA-256 of the exact consolidated string.
- `validation_result`: Complete policy audit trail with zero critical violations.
- `policy_version`: Policy definition version (`1.0.0`).
- `compressor_version`: Compressor engine version (`2.0.0`).
