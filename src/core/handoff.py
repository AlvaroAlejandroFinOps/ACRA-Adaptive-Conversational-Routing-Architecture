"""
Handoff Engine: Lógica de Línea Base Clean y corte de cascada de tokens.
Ensambla el payload determinista de destino para que el clúster Pro opere en régimen Zero-Shot equivalente.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .dhc import CompressedContext
from .edge_router import RouterDecision


class CleanPayload(BaseModel):
    session_id: str
    target_cluster: str
    prefill_prompt: str
    ccr: float
    is_sterilized: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HandoffEngine:
    """
    Motor de Handoff asimétrico entre Edge y Pro.
    Garantiza que ninguna cadena de Markov errática arrastrada por turnos previos contamine la inferencia del modelo Pro.
    """

    def __init__(self, enforce_sterilization: bool = True):
        self.enforce_sterilization = enforce_sterilization

    def assemble_clean_payload(
        self,
        session_id: str,
        decision: RouterDecision,
        compressed_ctx: CompressedContext,
        system_instructions: Optional[str] = None,
    ) -> CleanPayload:
        """
        Ensambla el payload purgado y estéril con corte total de cascadas de alucinaciones.
        """
        sys_directive = system_instructions or (
            "You are a frontier reasoning model operating under an ACRA-stabilized cognitive pipeline.\n"
            "All background context has been verified and purged of conversational drift."
        )

        sterilized_prompt = (
            f"=== SYSTEM DIRECTIVE ===\n{sys_directive}\n\n"
            f"=== CONSOLIDATED EXECUTION CANVAS ===\n"
            f"{compressed_ctx.clean_history_prompt}\n\n"
            f"=== INSTRUCTION ===\n"
            f"Execute solution deterministically addressing only the hard requirements above."
        )

        return CleanPayload(
            session_id=session_id,
            target_cluster=decision.target_cluster,
            prefill_prompt=sterilized_prompt,
            ccr=compressed_ctx.ccr,
            is_sterilized=self.enforce_sterilization,
            metadata={
                "maturity_score": decision.maturity_score,
                "raw_tokens_estimate": compressed_ctx.raw_tokens_estimate,
                "consolidated_tokens_estimate": compressed_ctx.consolidated_tokens_estimate,
                "purged_chatter_count": compressed_ctx.purged_chatter_count,
            },
        )
