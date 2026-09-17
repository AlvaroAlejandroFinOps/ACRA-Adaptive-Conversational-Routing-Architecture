# ADR-002: Capability-Based Model Selection Architecture

## Status
Accepted (Approved by User in Evolution Plan)

## Context
In legacy ACRA, specific model identifiers (e.g., `gemini-flash-lightweight-edge`, `gemini-pro-reasoning-heavy`) were referenced in configuration and routing actions (`DISPATCH_PRO`), creating hardcoded dependencies on specific commercial providers and model tiers.

EVO ACRA.md §4.4 mandates strict capability-based model selection. The core domain, orchestration, and agent logic must remain completely agnostic to provider identities and brand/version strings (INV-001).

## Alternatives Considered
1. **Option A: Direct model naming per agent:** Hardcodes provider models into agent definitions. Fails multi-cloud portability and dynamic fallback.
2. **Option B: Three-Layer Model Resolution (ModelProfile → ModelCapabilityRegistry → ProviderAdapter):** Complete separation between functional requirement, capability mapping, and physical provider execution.

## Decision
Adopt **Option B**.

Implement a three-layer resolution architecture:
1. **`ModelProfile` (Functional Requirement):** Declares capability requirements (e.g., `required_capabilities`: `structured_output`, `tool_calling`, `reasoning`, `long_context`), maximum latency budget, risk constraints, and fallback ordering. Profiles include: `frontier_planner`, `complex_reasoner`, `domain_planner`, `lightweight_executor`, `classifier`, `validator`, `fallback_local`.
2. **`ModelCapabilityRegistry` (Capability Registry & Matcher):** Loads provider capability manifests and matches `ModelProfile` constraints against active provider offerings.
3. **`ProviderAdapter` (Execution Abstraction):** Implements normalized execution, cost estimation, and cache descriptor telemetry. Concrete model names exist exclusively in `config/providers/*.yaml`.

## Invariant Enforced
- **INV-001:** No concrete model name shall appear in domain logic (`src/core/` excluding `providers/` and `config/`). Enforced via CI grep verification.

## Consequences
- **Positive:**
  - Zero vendor lock-in.
  - Transparent failover across cloud providers (e.g., Google, Anthropic, OpenAI, local Ollama).
  - Clean capability negotiation and runtime fallback chains.
- **Negative:**
  - Additional abstraction layer requiring profile-to-model matching logic and configuration files.
