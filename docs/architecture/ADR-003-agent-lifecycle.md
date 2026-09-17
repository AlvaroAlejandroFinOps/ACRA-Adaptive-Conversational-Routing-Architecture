# ADR-003: Agent Lifecycle & Ephemeral Instance Architecture

## Status
Accepted (Approved by User in Evolution Plan)

## Context
Legacy ACRA operated on flat conversation sessions where turn progression was managed as a single stream without domain or agent boundaries.

To support complex, multi-domain, hierarchical problem solving (e.g., enterprise operations, security, legal, operations), ACRA requires discrete agents with clear policy scopes, bounded permissions, isolated contexts, and strictly governed lifecycles.

## Alternatives Considered
1. **Option A: Monolithic Multi-Tool Agent:** Single agent with all tools and system prompts concatenated. Causes context explosion, prompt injection vulnerability, cross-domain data leakage, and high inference costs.
2. **Option B: Persistent Agent Daemons:** Long-running agent instances retaining state indefinitely. High risk of memory leaks, state contamination, and unpredictable state drift.
3. **Option C: Definition vs Ephemeral Instance Separation (AgentDefinition vs AgentInstance):** Clear separation between static declarative templates and ephemeral, scoped, budget-constrained runtime instances.

## Decision
Adopt **Option C**.

1. **`AgentDefinition` (Template):** Persistent declarative specification containing:
   - Unique identifier and domain scope.
   - Declared capabilities and policy rules.
   - Explicit `ToolGrant` whitelist.
   - Input/output contract schemas.
   - Assigned `ModelProfile`.
   - Escalation and handoff policies.
2. **`AgentInstance` (Ephemeral Runtime):** Dynamic instance created on demand by `AgentFactory`:
   - Isolated `ContextCapsule` with cryptographic integrity hash.
   - Scoped `ContextBudget` cascaded from parent objective/orchestrator.
   - Strict TTL expiration and maximum turn limits.
   - Dedicated `AgentInstanceStateMachine` (CREATED → INITIALIZED → ACTIVE → SUSPENDED → COMPLETED → RETIRED | REVOKED).

## Invariants Enforced
- **INV-003:** Cross-domain context leakage rate must be zero.
- **INV-005:** Budget enforcement is hierarchical (Objective → Agent → Task).
- **INV-009:** Agent fork inherits only authorized context subset via whitelist.

## Consequences
- **Positive:**
  - Robust domain isolation and zero cross-contamination.
  - Ephemeral instances prevent context bloat and state drift.
  - Fine-grained token budgeting and tool security enforcement.
- **Negative:**
  - Requires explicit factory creation and lifecycle management overhead.
