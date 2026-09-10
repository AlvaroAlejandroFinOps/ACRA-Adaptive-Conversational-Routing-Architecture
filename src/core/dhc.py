"""
Dynamic History Compression (DHC) & Assistant Response Masking.
Mandato 1 del RFC: Enmascaramiento asimétrico del asistente (elimina la verbosidad previa).
Mandato 2 del RFC: Cumplimiento del Context Consolidation Ratio (CCR > 45%).
"""

import re
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field

from .edge_router import MessageTurn, TurnRole
from .metrics import ACRAMetrics


class CompressedContext(BaseModel):
    raw_tokens_estimate: int
    consolidated_tokens_estimate: int
    ccr: float = Field(..., ge=0.0, le=1.0, description="Context Consolidation Ratio")
    purged_chatter_count: int
    consolidated_user_requirements: List[str]
    crystallized_code_artifacts: List[str]
    clean_history_prompt: str


class DynamicHistoryCompressor:
    """
    Compresor Dinámico de Historial conversacional.
    Purga saludos, verbosidades intermedias, disculpas, meta-comentarios y alucinaciones tentativas
    antes de alcanzar la fase de Prefill en el clúster Pro.
    """

    def __init__(self, target_min_ccr: float = 0.45):
        self.target_min_ccr = target_min_ccr
        self.verbosity_patterns = [
            r"^¡?hola!?.*",
            r"^buenos días.*",
            r"^por supuesto, con gusto te ayudo.*",
            r"^ciertamente!.*",
            r"^como modelo de lenguaje.*",
            r"^espero que esto te sea de utilidad.*",
            r"^avísame si necesitas algo más.*",
            r"sure, i would be happy to help.*",
            r"hello!.*",
            r"as an ai language model.*",
        ]

    def _estimate_tokens(self, text: str) -> int:
        """Estimación heurística de tokens (promedio 1 token = 4 caracteres / 0.75 palabras)."""
        words = len(text.split())
        return max(1, int(words * 1.35))

    def mask_assistant_verbosity(self, assistant_content: str) -> Tuple[str, List[str]]:
        """
        Aplica el Mandato 1 del RFC:
        Enmascara explicaciones extensas y retiene solo artefactos duros (código, listas operativas).
        """
        # Extraer bloques de código (Markdown code fences)
        code_blocks = re.findall(r"```[\s\S]*?```", assistant_content)
        
        # Eliminar saludos y cháchara trivial de líneas
        lines = assistant_content.splitlines()
        filtered_lines = []
        for line in lines:
            line_str = line.strip().lower()
            if any(re.match(p, line_str) for p in self.verbosity_patterns):
                continue
            filtered_lines.append(line)
        
        cleaned_text = "\n".join(filtered_lines)
        return cleaned_text, code_blocks

    def compress(self, history: List[MessageTurn], current_input: str) -> CompressedContext:
        """
        Transforma un historial conversacional caótico y entrópico en un contexto consolidado estéril.
        """
        raw_text_accum = current_input + " " + " ".join([m.content for m in history])
        raw_tokens = self._estimate_tokens(raw_text_accum)

        user_intents: List[str] = []
        extracted_artifacts: List[str] = []
        purged_counter = 0

        for turn in history:
            if turn.role == TurnRole.USER:
                # Retención de intenciones duras
                clean_intent = turn.content.strip()
                if clean_intent:
                    user_intents.append(clean_intent)
            elif turn.role == TurnRole.ASSISTANT:
                # Enmascaramiento asimétrico: silenciar verbosidad
                masked_text, codes = self.mask_assistant_verbosity(turn.content)
                extracted_artifacts.extend(codes)
                # Contabilizar purga de ruido
                if len(masked_text) < len(turn.content):
                    purged_counter += 1

        # Agregar el input actual del usuario como intención prioritaria
        user_intents.append(current_input.strip())

        # Construir el prompt consolidado de Línea Base Clean
        consolidated_sections: List[str] = []
        consolidated_sections.append("### CONSOLIDATED USER REQUIREMENTS (HARD INTENTS):")
        for i, intent in enumerate(user_intents, 1):
            consolidated_sections.append(f"{i}. {intent}")

        if extracted_artifacts:
            consolidated_sections.append("\n### CONFIRMED EXECUTION ARTIFACTS / CONSTRAINTS:")
            for artifact in extracted_artifacts:
                consolidated_sections.append(artifact)

        consolidated_prompt = "\n".join(consolidated_sections)
        consolidated_tokens = self._estimate_tokens(consolidated_prompt)

        # Si por ser turnos muy cortos raw < consolidated, ajustar coherentemente
        if raw_tokens < consolidated_tokens:
            consolidated_tokens = raw_tokens

        ccr = ACRAMetrics.calculate_ccr(raw_tokens, consolidated_tokens)

        return CompressedContext(
            raw_tokens_estimate=raw_tokens,
            consolidated_tokens_estimate=consolidated_tokens,
            ccr=ccr,
            purged_chatter_count=purged_counter,
            consolidated_user_requirements=user_intents,
            crystallized_code_artifacts=extracted_artifacts,
            clean_history_prompt=consolidated_prompt,
        )
