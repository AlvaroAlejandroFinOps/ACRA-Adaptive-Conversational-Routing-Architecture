# ADR-004: Finite State Machine (FSM) Decomposition Architecture

## Status
Accepted (Approved by User in Evolution Plan)

## Context
Legacy ACRA managed session progression using a single state machine (`ACRAStateMachine`) with states `INTAKE`, `ANALYZING`, `COMPRESSING`, `EVALUATING`, `HANDOFF_READY`, `DISPATCHED`, `COMPLETED`, `TERMINATED`.

This single FSM conflated session lifecycle, agent lifecycle, task decomposition, and inter-agent handoff mechanics, preventing parallel task execution, independent sub-agent coordination, and granular audit gating.

## Alternatives Considered
1. **Option A: Mega-FSM (Single state machine with 40+ states):** High combinatorial complexity, severe race condition risks, impossible to audit cleanly.
2. **Option B: Unconstrained Event Bus:** No formal state constraints. High risk of non-deterministic behavior, infinite loops, and untraceable failures.
3. **Option C: Decomposed, Orthogonal Finite State Machines:** Separate concerns into 5 distinct, deterministic FSMs linked by correlation IDs and guarded by cycle prevention limits.

## Decision
Adopt **Option C**.

Decompose system state management into 5 orthogonal state machines:
1. **`SessionStateMachine`:** High-level conversation session lifecycle (maintains backward compatibility with legacy `ACRAStateMachine`).
2. **`ObjectiveStateMachine`:** Tracks high-level goal resolution:
   - `RECEIVED` → `PLANNING` → `DECOMPOSED` → `EXECUTING` → `CONSOLIDATING` → `VALIDATED` → `COMPLETED` | `FAILED`
3. **`AgentInstanceStateMachine`:** Tracks ephemeral agent instance execution:
   - `CREATED` → `INITIALIZED` → `ACTIVE` → `SUSPENDED` → `COMPLETED` → `RETIRED` | `REVOKED`
4. **`TaskStateMachine`:** Manages discrete task units within the TaskGraph:
   - `PENDING` → `ASSIGNED` → `EXECUTING` → `VALIDATING` → `COMPLETED` | `FAILED` | `ESCALATED`
5. **`HandoffStateMachine`:** Enforces audited inter-agent handoffs:
   - `PREPARING` → `AUDITING` → `DISPATCHED` → `RECEIVED` → `VALIDATED` | `REJECTED`

## Invariants Enforced
- **INV-002:** Every handoff envelope must pass pre-handoff audit before dispatch.
- **INV-008:** FSM transitions are strictly deterministic; no state allows self-loops without an explicit retry limit (`max_retries`).

## Consequences
- **Positive:**
  - Clear separation of operational concerns.
  - Provable termination guarantees and infinite loop prevention.
  - High observability: state transitions emit structured telemetry with correlation IDs.
- **Negative:**
  - Need to manage coordination and event propagation across multiple state machines.
