"""
ACRA Orchestrator: Orquestador integral de estado conversacional.
Coordina Edge Router, DHC, Unified Context Tier y Handoff Engine.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

from .edge_router import EdgeRouter, RouterDecision, RouterAction, MessageTurn, TurnRole
from .dhc import DynamicHistoryCompressor, CompressedContext
from .unified_context import UnifiedContextTier, ContextSnapshot
from .handoff import HandoffEngine, CleanPayload


class OrchestratorState(str, Enum):
    IDLE = "idle"
    EVALUATING = "evaluating"
    CLARIFYING = "clarifying"
    CONSOLIDATING = "consolidating"
    DISPATCHING_PRO = "dispatching_pro"


class OrchestrationResult(BaseModel):
    session_id: str
    active_state: OrchestratorState
    decision: RouterDecision
    compressed_context: CompressedContext
    clean_payload: Optional[CleanPayload] = None
    response_text: str
    ccr: float


class ACRAOrchestrator:
    """
    Máquina de estados orquestadora de ACRA.
    Intercepta el flujo multi-turno, resguarda el clúster Pro y entrega estabilización cognitiva.
    """

    def __init__(
        self,
        edge_router: Optional[EdgeRouter] = None,
        compressor: Optional[DynamicHistoryCompressor] = None,
        context_tier: Optional[UnifiedContextTier] = None,
        handoff_engine: Optional[HandoffEngine] = None,
    ):
        self.router = edge_router or EdgeRouter()
        self.compressor = compressor or DynamicHistoryCompressor()
        self.context_tier = context_tier or UnifiedContextTier()
        self.handoff = handoff_engine or HandoffEngine()
        self.conversations: Dict[str, List[MessageTurn]] = {}

    def process_turn(
        self,
        session_id: str,
        user_message: str,
        pro_inference_simulator_fn: Optional[Any] = None,
    ) -> OrchestrationResult:
        """
        Ejecuta el ciclo de vida de un turno conversacional bajo la arquitectura ACRA.
        """
        history = self.conversations.get(session_id, [])
        turn_idx = len(history) + 1

        # 1. Enrutamiento y evaluación de madurez en Edge Router
        decision = self.router.route(history, user_message)

        # 2. Compresión Dinámica de Historial (DHC)
        compressed_ctx = self.compressor.compress(history, user_message)

        # 3. Persistencia en Unified Context Tier
        self.context_tier.persist_snapshot(session_id, turn_idx, compressed_ctx)

        # 4. Decisión de acción
        clean_payload: Optional[CleanPayload] = None
        state: OrchestratorState

        if decision.action == RouterAction.DISPATCH_PRO:
            state = OrchestratorState.DISPATCHING_PRO
            clean_payload = self.handoff.assemble_clean_payload(session_id, decision, compressed_ctx)
            
            # Ejecución en clúster pesado
            if pro_inference_simulator_fn:
                raw_out = pro_inference_simulator_fn(clean_payload.prefill_prompt)
                response_content = str(raw_out)
            else:
                response_content = (
                    f"[PRO CLUSTER EXECUTION COMPLETE]\n"
                    f"Processed clean consolidated payload under zero-shot deterministic regime.\n"
                    f"CCR achieved: {compressed_ctx.ccr:.2%}"
                )
        else:
            state = OrchestratorState.CLARIFYING
            response_content = (
                f"[EDGE CLUSTER - CLARIFICATION TURN {turn_idx}]\n"
                f"Spec maturity: {decision.maturity_score:.2f} (Threshold: {self.router.maturity_threshold:.2f}).\n"
                f"Please refine details or requirements so deep reasoning pro-cluster can engage safely."
            )

        # Registrar turnos en historial local de la sesión
        history.append(MessageTurn(
            role=TurnRole.USER,
            content=user_message,
            turn_index=turn_idx,
        ))
        history.append(MessageTurn(
            role=TurnRole.ASSISTANT,
            content=response_content,
            turn_index=turn_idx,
            is_clarification=(decision.action != RouterAction.DISPATCH_PRO)
        ))
        self.conversations[session_id] = history

        return OrchestrationResult(
            session_id=session_id,
            active_state=state,
            decision=decision,
            compressed_context=compressed_ctx,
            clean_payload=clean_payload,
            response_text=response_content,
            ccr=compressed_ctx.ccr,
        )
