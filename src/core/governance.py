"""
Resource Governor: Enforces compute limits, token budgets, execution timeouts,
and max turn recursion caps to prevent resource exhaustion and Denial-of-Service.
"""

import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class BudgetExceededError(Exception):
    pass


class ResourceUsage(BaseModel):
    session_id: str
    turns_count: int = 0
    total_tokens_consumed: int = 0
    total_latency_ms: float = 0.0
    estimated_cost_usd: float = 0.0


class ResourceGovernor:
    """
    Gobernador de recursos y límites operativos de ACRA.
    Garantiza que ninguna sesión exceda presupuestos de cómputo o cause bucles infinitos.
    """

    def __init__(
        self,
        max_turns_per_session: int = 25,
        max_tokens_per_session: int = 64000,
        max_session_duration_sec: float = 600.0,
        max_cost_usd_per_session: float = 1.00,
    ):
        self.max_turns_per_session = max_turns_per_session
        self.max_tokens_per_session = max_tokens_per_session
        self.max_session_duration_sec = max_session_duration_sec
        self.max_cost_usd_per_session = max_cost_usd_per_session
        self._session_usage: Dict[str, ResourceUsage] = {}
        self._session_start_times: Dict[str, float] = {}

    def start_session_if_absent(self, session_id: str) -> None:
        if session_id not in self._session_start_times:
            self._session_start_times[session_id] = time.time()
            self._session_usage[session_id] = ResourceUsage(session_id=session_id)

    def check_and_record(
        self,
        session_id: str,
        tokens_added: int = 0,
        latency_added_ms: float = 0.0,
        cost_added_usd: float = 0.0,
    ) -> ResourceUsage:
        """
        Verifica si la sesión actual excede los umbrales configurados y registra el consumo.
        Lanza BudgetExceededError si se sobrepasa algún límite.
        """
        self.start_session_if_absent(session_id)
        usage = self._session_usage[session_id]
        start_time = self._session_start_times[session_id]

        # 1. Verificar límite de duración temporal
        elapsed = time.time() - start_time
        if elapsed > self.max_session_duration_sec:
            raise BudgetExceededError(
                f"Session {session_id} exceeded time limit: {elapsed:.1f}s > {self.max_session_duration_sec}s"
            )

        # 2. Verificar límite de turnos
        usage.turns_count += 1
        if usage.turns_count > self.max_turns_per_session:
            raise BudgetExceededError(
                f"Session {session_id} exceeded turn limit: {usage.turns_count} > {self.max_turns_per_session}"
            )

        # 3. Registrar y verificar tokens
        usage.total_tokens_consumed += tokens_added
        if usage.total_tokens_consumed > self.max_tokens_per_session:
            raise BudgetExceededError(
                f"Session {session_id} exceeded token limit: {usage.total_tokens_consumed} > {self.max_tokens_per_session}"
            )

        # 4. Registrar y verificar costo
        usage.total_latency_ms += latency_added_ms
        usage.estimated_cost_usd += cost_added_usd
        if usage.estimated_cost_usd > self.max_cost_usd_per_session:
            raise BudgetExceededError(
                f"Session {session_id} exceeded cost ceiling: ${usage.estimated_cost_usd:.4f} > ${self.max_cost_usd_per_session:.2f}"
            )

        return usage

    def get_usage(self, session_id: str) -> Optional[ResourceUsage]:
        return self._session_usage.get(session_id)

    def reset_session(self, session_id: str) -> None:
        self._session_usage.pop(session_id, None)
        self._session_start_times.pop(session_id, None)
