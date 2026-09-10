"""
Handoff Engine: Lógica de Línea Base Clean y corte de cascada de tokens.
Ensambla el payload determinista de destino para que el clúster Pro opere en régimen Zero-Shot equivalente.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .dhc import CompressedContext
from .edge_router import RouterDecision
from .payload_policy import PayloadPolicyGate, PolicyValidationResult


class CleanPayload(BaseModel):
    session_id: str
    target_cluster: str
    prefill_prompt: str
    ccr: float
    is_sterilized: bool = True
    schema_version: str = "2.0.0"
    policy_version: str = "1.0.0"
    compressor_version: str = "2.0.0"
    sterilization_hash: Optional[str] = None
    validation_result: Optional[PolicyValidationResult] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HandoffEngine:
    """
    Motor de Handoff asimétrico entre Edge y Pro.
    Garantiza que ninguna cadena de Markov errática arrastrada por turnos previos contamine la inferencia del modelo Pro.
    """

    def __init__(
        self,
        enforce_sterilization: bool = True,
        policy_gate: Optional[PayloadPolicyGate] = None,
    ):
        self.enforce_sterilization = enforce_sterilization
        self.policy_gate = policy_gate or PayloadPolicyGate()

    def assemble_clean_payload(
        self,
        session_id: str,
        decision: RouterDecision,
        compressed_ctx: CompressedContext,
        system_instructions: Optional[str] = None,
    ) -> CleanPayload:
        """
        Ensambla el payload purgado y estéril con corte total de cascadas de alucinaciones.
        Ejecuta la validación de PayloadPolicyGate para garantizar esterilización criptográfica.
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

        validation_result = self.policy_gate.validate(
            sterilized_prompt,
            provenance_chain=compressed_ctx.provenance_chain,
        )

        # Si no pasa y se exige esterilización estricta, usar contenido sanitizado
        effective_prompt = sterilized_prompt
        if not validation_result.passed and validation_result.sanitized_content:
            effective_prompt = validation_result.sanitized_content

        is_sterilized_flag = validation_result.passed if self.enforce_sterilization else True

        meta = {
            "maturity_score": decision.maturity_score,
            "raw_tokens_estimate": compressed_ctx.raw_tokens_estimate,
            "consolidated_tokens_estimate": compressed_ctx.consolidated_tokens_estimate,
            "purged_chatter_count": compressed_ctx.purged_chatter_count,
            "retained_decisions_count": len(compressed_ctx.retained_decisions),
            "superseded_items_count": len(compressed_ctx.superseded_items),
            "policy_passed": validation_result.passed,
            "violations_count": len(validation_result.violations),
        }

        return CleanPayload(
            session_id=session_id,
            target_cluster=decision.target_cluster,
            prefill_prompt=effective_prompt,
            ccr=compressed_ctx.ccr,
            is_sterilized=is_sterilized_flag,
            schema_version="2.0.0",
            policy_version=validation_result.policy_version,
            compressor_version="2.0.0",
            sterilization_hash=validation_result.sterilization_hash,
            validation_result=validation_result,
            metadata=meta,
        )
