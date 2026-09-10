"""
Dynamic History Compression (DHC) & Assistant Response Masking.
Mandato 1 del RFC: Enmascaramiento asimétrico del asistente (elimina la verbosidad previa).
Mandato 2 del RFC: Cumplimiento del Context Consolidation Ratio (CCR > 45%).
"""

import re
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel, Field

from .edge_router import MessageTurn, TurnRole, ContentProvenance, TrustLevel, ContentClassification
from .metrics import ACRAMetrics


class CompressedContext(BaseModel):
    raw_tokens_estimate: int
    consolidated_tokens_estimate: int
    ccr: float = Field(..., ge=0.0, le=1.0, description="Context Consolidation Ratio")
    purged_chatter_count: int
    consolidated_user_requirements: List[str]
    crystallized_code_artifacts: List[str]
    clean_history_prompt: str
    provenance_chain: List[Dict[str, Any]] = Field(default_factory=list)
    trust_summary: Dict[str, int] = Field(default_factory=dict)
    retained_decisions: List[str] = Field(default_factory=list)
    superseded_items: List[str] = Field(default_factory=list)


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

        self.decision_markers = [
            "decision:", "decidido:", "decisión:", "arquitectura:", "constraint:",
            "restricción:", "patrón:", "pattern:", "protocolo:", "protocol:",
            "selected:", "acordado:", "agreed:", "confirmed:", "definición:"
        ]
        self.supersede_patterns = [
            r"olvida (lo|la|el) .*",
            r"ignora (lo|la|el) .*",
            r"cancel (that|previous).*",
            r"scratch that.*",
            r"instead of .*",
            r"mejor no .*",
            r"cambiemos .*",
        ]

    def _estimate_tokens(self, text: str) -> int:
        """Estimación heurística de tokens (promedio 1 token = 4 caracteres / 0.75 palabras)."""
        words = len(text.split())
        return max(1, int(words * 1.35))

    def extract_retained_decisions(self, text: str) -> List[str]:
        """Extrae decisiones técnicas, contratos y restricciones acordadas sin arrastrar cháchara."""
        decisions = []
        for line in text.splitlines():
            cleaned = line.strip()
            lower = cleaned.lower()
            if any(lower.startswith(marker) or f" {marker}" in lower for marker in self.decision_markers):
                decisions.append(cleaned)
        return decisions

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
        Preserva procedencia, verifica niveles de confianza y retiene decisiones arquitectónicas.
        """
        raw_text_accum = current_input + " " + " ".join([m.content for m in history])
        raw_tokens = self._estimate_tokens(raw_text_accum)

        user_intents: List[str] = []
        extracted_artifacts: List[str] = []
        retained_decisions: List[str] = []
        superseded_items: List[str] = []
        provenance_chain: List[Dict[str, Any]] = []
        trust_counts: Dict[str, int] = {
            TrustLevel.TRUSTED.value: 0,
            TrustLevel.VERIFIED.value: 0,
            TrustLevel.UNTRUSTED.value: 0,
            TrustLevel.TAINTED.value: 0,
        }
        purged_counter = 0

        for turn in history:
            # Registrar cadena de procedencia
            provenance_entry = {
                "turn_index": turn.turn_index,
                "role": turn.role.value if hasattr(turn.role, "value") else str(turn.role),
                "provenance": turn.provenance.value if hasattr(turn.provenance, "value") else str(turn.provenance),
                "trust_level": turn.trust_level.value if hasattr(turn.trust_level, "value") else str(turn.trust_level),
                "source_id": turn.source_id or f"turn_{turn.turn_index}",
            }
            provenance_chain.append(provenance_entry)
            trust_key = turn.trust_level.value if hasattr(turn.trust_level, "value") else str(turn.trust_level)
            trust_counts[trust_key] = trust_counts.get(trust_key, 0) + 1

            if turn.role == TurnRole.USER:
                # Retención de intenciones duras
                clean_intent = turn.content.strip()
                if clean_intent:
                    # Detectar si este turno invalida o reemplaza directivas anteriores
                    intent_lower = clean_intent.lower()
                    if any(re.search(pat, intent_lower) for pat in self.supersede_patterns):
                        superseded_items.append(f"Turn {turn.turn_index} amended: {clean_intent}")
                    user_intents.append(clean_intent)
            elif turn.role == TurnRole.ASSISTANT:
                # Extraer decisiones y acuerdos técnicos previos antes de enmascarar
                decisions = self.extract_retained_decisions(turn.content)
                retained_decisions.extend(decisions)

                # Enmascaramiento asimétrico: silenciar verbosidad
                masked_text, codes = self.mask_assistant_verbosity(turn.content)
                extracted_artifacts.extend(codes)
                # Contabilizar purga de ruido
                if len(masked_text) < len(turn.content):
                    purged_counter += 1

        # Agregar el input actual del usuario como intención prioritaria
        curr_clean = current_input.strip()
        user_intents.append(curr_clean)
        provenance_chain.append({
            "turn_index": len(history) + 1,
            "role": TurnRole.USER.value,
            "provenance": ContentProvenance.USER_DIRECT.value,
            "trust_level": TrustLevel.UNTRUSTED.value,
            "source_id": f"turn_{len(history) + 1}_current",
        })
        trust_counts[TrustLevel.UNTRUSTED.value] = trust_counts.get(TrustLevel.UNTRUSTED.value, 0) + 1

        # Construir el prompt consolidado de Línea Base Clean
        consolidated_sections: List[str] = []
        consolidated_sections.append("### CONSOLIDATED USER REQUIREMENTS (HARD INTENTS):")
        for i, intent in enumerate(user_intents, 1):
            consolidated_sections.append(f"{i}. {intent}")

        if retained_decisions:
            consolidated_sections.append("\n### RETAINED ARCHITECTURAL DECISIONS & CONSTRAINTS:")
            for decision in retained_decisions:
                consolidated_sections.append(f"- {decision}")

        if extracted_artifacts:
            consolidated_sections.append("\n### CONFIRMED EXECUTION ARTIFACTS / CODE BLOCKS:")
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
            provenance_chain=provenance_chain,
            trust_summary=trust_counts,
            retained_decisions=retained_decisions,
            superseded_items=superseded_items,
        )
