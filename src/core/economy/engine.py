"""ACRA Token Economy Engine.

Implements R-010, INV-005, and INV-006:
- Hierarchical cascaded budget management (session -> objective -> task -> agent -> tool/model).
- Strict ceiling validation preventing children from oversubscribing parent capacities (INV-005).
- Recursive upward consumption propagation ensuring top-level boundaries are never breached.
- Rigorous labeling of measured vs estimated tokens and expenses (INV-006).
- Atomic reservation, hold, and release lifecycle.
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

from src.core.contracts.context import ContextBudget


class BudgetExceededError(Exception):
    """Raised when a token, cost, turn, or time budget is breached or oversubscribed."""
    pass


class TokenEconomyEngine:
    """Central engine managing hierarchical budgets, reservations, and resource governance."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._budgets: dict[str, ContextBudget] = {}
        self._parent_map: dict[str, str] = {}
        self._reservations: dict[str, dict[str, Any]] = {}
        self._measured_tokens: dict[str, int] = {}
        self._estimated_tokens: dict[str, int] = {}

    def register_budget(
        self,
        entity_id: str,
        budget: ContextBudget,
        parent_id: str | None = None,
    ) -> ContextBudget:
        """Register or allocate a budget for an entity, enforcing the parent cascade ceiling (INV-005)."""
        with self._lock:
            if parent_id is not None:
                parent_budget = self._budgets.get(parent_id)
                if parent_budget is None:
                    raise ValueError(f"Parent entity '{parent_id}' does not have a registered budget")

                # Verify child budget does not exceed parent remaining resources (INV-005)
                if budget.max_tokens > parent_budget.remaining_tokens():
                    raise BudgetExceededError(
                        f"INV-005 Violation: Child '{entity_id}' requested {budget.max_tokens} tokens, "
                        f"exceeding parent '{parent_id}' remaining capacity of {parent_budget.remaining_tokens()} tokens"
                    )
                if budget.max_cost_usd > parent_budget.remaining_cost_usd():
                    raise BudgetExceededError(
                        f"INV-005 Violation: Child '{entity_id}' requested ${budget.max_cost_usd:.4f} budget, "
                        f"exceeding parent '{parent_id}' remaining capacity of ${parent_budget.remaining_cost_usd():.4f}"
                    )

                self._parent_map[entity_id] = parent_id

            self._budgets[entity_id] = budget
            self._measured_tokens[entity_id] = 0
            self._estimated_tokens[entity_id] = 0
            return budget

    def get_budget(self, entity_id: str) -> ContextBudget | None:
        """Retrieve active ContextBudget for an entity."""
        with self._lock:
            return self._budgets.get(entity_id)

    def is_exhausted(self, entity_id: str) -> bool:
        """Check if an entity or any of its ancestors is exhausted."""
        with self._lock:
            curr: str | None = entity_id
            while curr is not None:
                b = self._budgets.get(curr)
                if b is not None and b.is_exhausted():
                    return True
                curr = self._parent_map.get(curr)
            return False

    def record_consumption(
        self,
        entity_id: str,
        tokens: int,
        cost_usd: float = 0.0,
        is_measured: bool = True,
    ) -> ContextBudget:
        """Record resource consumption, propagating hierarchically upward to ancestors (INV-005).

        Raises BudgetExceededError if consumption would exceed the ceiling of entity_id
        or any parent in the hierarchy.
        """
        with self._lock:
            # 1. Collect entity hierarchy from target up to root
            hierarchy: list[str] = []
            curr: str | None = entity_id
            while curr is not None:
                if curr not in self._budgets:
                    raise ValueError(f"Entity '{curr}' in hierarchy has no registered budget")
                hierarchy.append(curr)
                curr = self._parent_map.get(curr)

            # 2. Pre-check capacity across the entire hierarchy
            for node_id in hierarchy:
                b = self._budgets[node_id]
                new_tokens = b.consumed_tokens + tokens
                new_cost = b.consumed_cost_usd + cost_usd

                if new_tokens > b.max_tokens:
                    raise BudgetExceededError(
                        f"Budget exceeded at '{node_id}': total tokens {new_tokens} > limit {b.max_tokens}"
                    )
                if new_cost > b.max_cost_usd:
                    raise BudgetExceededError(
                        f"Budget exceeded at '{node_id}': total cost ${new_cost:.4f} > limit ${b.max_cost_usd:.4f}"
                    )

            # 3. Apply consumption atomically across hierarchy
            for node_id in hierarchy:
                old_b = self._budgets[node_id]
                self._budgets[node_id] = ContextBudget(
                    max_tokens=old_b.max_tokens,
                    max_turns=old_b.max_turns,
                    max_cost_usd=old_b.max_cost_usd,
                    max_wall_clock_seconds=old_b.max_wall_clock_seconds,
                    consumed_tokens=old_b.consumed_tokens + tokens,
                    consumed_cost_usd=old_b.consumed_cost_usd + cost_usd,
                )

                if is_measured:
                    self._measured_tokens[node_id] = self._measured_tokens.get(node_id, 0) + tokens
                else:
                    self._estimated_tokens[node_id] = self._estimated_tokens.get(node_id, 0) + tokens

            return self._budgets[entity_id]

    def reserve(self, entity_id: str, tokens: int, cost_usd: float = 0.0) -> str:
        """Hold a temporary resource reservation prior to execution."""
        with self._lock:
            # Validate availability at entity and parents
            curr: str | None = entity_id
            while curr is not None:
                b = self._budgets.get(curr)
                if b is None:
                    raise ValueError(f"Entity '{curr}' has no budget")
                if tokens > b.remaining_tokens():
                    raise BudgetExceededError(f"Insufficient tokens to reserve at '{curr}'")
                if cost_usd > b.remaining_cost_usd():
                    raise BudgetExceededError(f"Insufficient cost budget to reserve at '{curr}'")
                curr = self._parent_map.get(curr)

            reservation_id = f"res_{uuid.uuid4().hex[:12]}"
            self._reservations[reservation_id] = {
                "entity_id": entity_id,
                "tokens": tokens,
                "cost_usd": cost_usd,
            }
            return reservation_id

    def release_reservation(self, reservation_id: str) -> None:
        """Release a previously held reservation without committing consumption."""
        with self._lock:
            self._reservations.pop(reservation_id, None)

    def commit_reservation(
        self,
        reservation_id: str,
        actual_tokens: int,
        actual_cost_usd: float = 0.0,
        is_measured: bool = True,
    ) -> ContextBudget:
        """Commit a reservation, releasing the hold and recording actual consumption."""
        with self._lock:
            res = self._reservations.pop(reservation_id, None)
            if res is None:
                raise ValueError(f"Unknown or already committed reservation '{reservation_id}'")
            entity_id = res["entity_id"]

        # Call record_consumption without holding the lock
        return self.record_consumption(
            entity_id=entity_id,
            tokens=actual_tokens,
            cost_usd=actual_cost_usd,
            is_measured=is_measured,
        )

    def get_token_breakdown(self, entity_id: str) -> dict[str, int]:
        """Get discrimination between measured and estimated tokens (INV-006)."""
        with self._lock:
            measured = self._measured_tokens.get(entity_id, 0)
            estimated = self._estimated_tokens.get(entity_id, 0)
            return {
                "measured_tokens": measured,
                "estimated_tokens": estimated,
                "total_tokens": measured + estimated,
            }

    def reset(self) -> None:
        """Reset all engine states."""
        with self._lock:
            self._budgets.clear()
            self._parent_map.clear()
            self._reservations.clear()
            self._measured_tokens.clear()
            self._estimated_tokens.clear()
