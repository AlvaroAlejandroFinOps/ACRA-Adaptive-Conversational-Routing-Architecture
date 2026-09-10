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


from .state_machine import ACRAStateMachine, SystemState


class OrchestratorState(str, Enum):
    IDLE = "idle"
    EVALUATING = "evaluating"
    CLARIFYING = "clarifying"
    CONSOLIDATING = "consolidating"
    VALIDATING = "validating"
    POLICY_REJECTED = "policy_rejected"
    FALLBACK = "fallback"
    DISPATCHING_PRO = "dispatching_pro"
    REVOKED = "revoked"


class OrchestrationResult(BaseModel):
    session_id: str
    active_state: OrchestratorState
    decision: RouterDecision
    compressed_context: CompressedContext
    clean_payload: Optional[CleanPayload] = None
    response_text: str
    ccr: float
    fsm_state: Optional[SystemState] = None


from .governance import ResourceGovernor, BudgetExceededError


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
        governor: Optional[ResourceGovernor] = None,
    ):
        self.router = edge_router or EdgeRouter()
        self.compressor = compressor or DynamicHistoryCompressor()
        self.context_tier = context_tier or UnifiedContextTier()
        self.handoff = handoff_engine or HandoffEngine()
        self.governor = governor or ResourceGovernor()
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

        # 0. Verificación de límites de gobernanza operativa
        try:
            self.governor.check_and_record(session_id, tokens_added=len(user_message.split()))
        except BudgetExceededError as e:
            fallback_dec = self.router.route(history, user_message)
            fallback_ctx = self.compressor.compress(history, user_message)
            return OrchestrationResult(
                session_id=session_id,
                active_state=OrchestratorState.POLICY_REJECTED,
                decision=fallback_dec,
                compressed_context=fallback_ctx,
                clean_payload=None,
                response_text=f"[RESOURCE GOVERNOR INTERVENTION] {str(e)}",
                ccr=0.0,
                fsm_state=SystemState.POLICY_REJECTED,
            )

        # 1. Enrutamiento y evaluación de madurez en Edge Router
        decision = self.router.route(history, user_message)

        # 2. Compresión Dinámica de Historial (DHC)
        compressed_ctx = self.compressor.compress(history, user_message)

        # 3. Persistencia en Unified Context Tier
        self.context_tier.persist_snapshot(session_id, turn_idx, compressed_ctx)

        # 4. Inspección temprana de seguridad en el perímetro Edge
        early_policy_check = self.handoff.policy_gate.validate(
            user_message,
            provenance_chain=compressed_ctx.provenance_chain,
        )

        clean_payload: Optional[CleanPayload] = None
        state: OrchestratorState
        fsm_state: Optional[SystemState] = None

        if not early_policy_check.passed:
            state = OrchestratorState.POLICY_REJECTED
            fsm_state = SystemState.POLICY_REJECTED
            response_content = (
                f"[SECURITY POLICY ENFORCEMENT - DISPATCH ABORTED]\n"
                f"Payload contained {len(early_policy_check.violations)} policy violation(s). "
                f"Execution held in Edge cluster for sanitization."
            )
            clean_payload = CleanPayload(
                session_id=session_id,
                target_cluster="edge",
                prefill_prompt=early_policy_check.sanitized_content or user_message,
                ccr=0.0,
                is_sterilized=False,
                validation_result=early_policy_check,
            )
        elif decision.action == RouterAction.DISPATCH_PRO:
            clean_payload = self.handoff.assemble_clean_payload(session_id, decision, compressed_ctx)

            # Validar si el payload consolidado superó el PayloadPolicyGate
            if clean_payload.validation_result and not clean_payload.validation_result.passed:
                state = OrchestratorState.POLICY_REJECTED
                fsm_state = SystemState.POLICY_REJECTED
                response_content = (
                    f"[SECURITY POLICY ENFORCEMENT - DISPATCH ABORTED]\n"
                    f"Payload contained {len(clean_payload.validation_result.violations)} policy violation(s). "
                    f"Execution held in Edge cluster for sanitization."
                )
            else:
                state = OrchestratorState.DISPATCHING_PRO
                fsm_state = SystemState.EXECUTING_PRO
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
            fsm_state = SystemState.CLARIFYING
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
            fsm_state=fsm_state,
        )
