"""
Edge Router: Clasificador de madurez del prompt y aislador estocástico.
Previene el anclaje temprano (Stick-or-Switch) manteniendo el modelo Pro inactivo
hasta que la especificación conversacional haya madurado.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class TurnRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ContentProvenance(str, Enum):
    USER_DIRECT = "user_direct"
    ASSISTANT_GENERATED = "assistant_generated"
    SYSTEM_PROMPT = "system_prompt"
    EXTERNAL_TOOL = "external_tool"
    RETRIEVED_CONTEXT = "retrieved_context"
    MEMORY_CACHE = "memory_cache"
    UNKNOWN = "unknown"


class TrustLevel(str, Enum):
    TRUSTED = "trusted"
    VERIFIED = "verified"
    UNTRUSTED = "untrusted"
    TAINTED = "tainted"


class ContentClassification(str, Enum):
    PROMPT_INSTRUCTION = "prompt_instruction"
    CONVERSATIONAL_CHATTER = "conversational_chatter"
    CONFIRMED_ARTIFACT = "confirmed_artifact"
    CODE_BLOCK = "code_block"
    REASONING_CHAIN = "reasoning_chain"
    UNTRUSTED_INJECTION_CANDIDATE = "untrusted_injection_candidate"


class MessageTurn(BaseModel):
    role: TurnRole
    content: str
    turn_index: int
    token_count: Optional[int] = None
    is_clarification: bool = False
    provenance: ContentProvenance = ContentProvenance.USER_DIRECT
    trust_level: TrustLevel = TrustLevel.UNTRUSTED
    source_id: Optional[str] = None


class MaturityVector(BaseModel):
    semantic_ambiguity: float = Field(..., ge=0.0, le=1.0, description="Ambiguity level (1.0 = highly ambiguous)")
    contextual_completeness: float = Field(..., ge=0.0, le=1.0, description="Completeness of technical constraints")
    architectural_risk: float = Field(..., ge=0.0, le=1.0, description="Risk score of premature execution")
    turn_depth: float = Field(..., ge=0.0, le=1.0, description="Normalized turn depth [0, 1]")

    @property
    def composite_score(self) -> float:
        """Score escalar de madurez derivado vectorialmente."""
        score = (
            0.40 * self.contextual_completeness
            + 0.30 * (1.0 - self.semantic_ambiguity)
            + 0.20 * self.turn_depth
            + 0.10 * (1.0 - self.architectural_risk)
        )
        return float(max(0.0, min(1.0, score)))


class RouterAction(str, Enum):
    CLARIFY = "clarify"           # Permanecer en clúster ligero para solicitar especificación
    HOLD = "hold"                 # Procesar en edge sin escalar
    DISPATCH_PRO = "dispatch_pro" # Escalar al clúster pesado (payload maduro)


class RouterDecision(BaseModel):
    action: RouterAction
    maturity_score: float = Field(..., ge=0.0, le=1.0, description="Nivel de madurez de la intención [0, 1]")
    target_cluster: str = Field(..., description="'edge' o 'pro'")
    reasoning: str
    active_turn: int
    maturity_vector: Optional[MaturityVector] = None


class EdgeRouter:
    """
    Enrutador asimétrico de borde.
    Mantiene aislado el modelo Pro durante el 0-20% de una conversación ambigua.
    """

    def __init__(
        self,
        maturity_threshold: float = 0.70,
        min_turns_before_pro: int = 1,
        complexity_keywords: Optional[List[str]] = None,
        ambiguity_markers: Optional[List[str]] = None,
    ):
        self.maturity_threshold = maturity_threshold
        self.min_turns_before_pro = min_turns_before_pro
        self.complexity_keywords = complexity_keywords or [
            "algoritmo", "arquitectura", "optimizar", "demostrar", "formalizar",
            "proof", "refactor", "distributed", "concurrency", "mathematical",
            "benchmark", "asíncrono", "memory leak", "pipeline", "sqlx", "dbt"
        ]
        self.ambiguity_markers = ambiguity_markers or [
            "quizás", "tal vez", "no estoy seguro", "algo como", "ayúdame con",
            "maybe", "not sure", "something like", "or whatever", "how do i start"
        ]

    def evaluate_maturity(self, history: List[MessageTurn], current_input: str) -> MaturityVector:
        """
        Evalúa las cuatro dimensiones vectoriales de madurez:
        1. Ambigüedad semántica (penalización por marcadores vagos)
        2. Completitud contextual (términos técnicos, longitud y densidad)
        3. Riesgo arquitectónico (ausencia de restricciones o turnos breves)
        4. Profundidad de turnos (convergencia en la conversación)
        """
        combined_text = (current_input + " " + " ".join([m.content for m in history if m.role == TurnRole.USER])).lower()
        words = combined_text.split()
        word_count = len(words)

        # 1. Ambigüedad semántica [0, 1]
        ambiguity_count = sum(1 for marker in self.ambiguity_markers if marker in combined_text)
        semantic_ambiguity = min(1.0, ambiguity_count * 0.30)

        # 2. Completitud contextual [0, 1]
        length_factor = min(1.0, word_count / 18.0)
        complexity_hits = sum(1 for kw in self.complexity_keywords if kw in combined_text)
        complexity_factor = min(1.0, complexity_hits * 0.35)
        contextual_completeness = min(1.0, (length_factor * 0.45) + (complexity_factor * 0.55))

        # 3. Profundidad de turnos [0, 1] (saturación en 4 turnos)
        turn_depth = min(1.0, len(history) / 4.0)

        # 4. Riesgo arquitectónico [0, 1] (inverso de la especificidad técnica y estabilidad)
        architectural_risk = max(0.0, 1.0 - (contextual_completeness * 0.70 + turn_depth * 0.30))

        return MaturityVector(
            semantic_ambiguity=float(semantic_ambiguity),
            contextual_completeness=float(contextual_completeness),
            architectural_risk=float(architectural_risk),
            turn_depth=float(turn_depth),
        )

    def assess_maturity(self, history: List[MessageTurn], current_input: str) -> float:
        """
        Evalúa el grado de completitud y madurez de la consulta actual considerando el historial.
        Mantiene compatibilidad retrospectiva total computando el score compuesto del vector.
        """
        vector = self.evaluate_maturity(history, current_input)
        return vector.composite_score

    def route(self, history: List[MessageTurn], current_input: str) -> RouterDecision:
        """Determina si la consulta se despacha al clúster Pro o se maneja en Edge."""
        turn_index = len(history) + 1
        vector = self.evaluate_maturity(history, current_input)
        score = vector.composite_score

        if turn_index < self.min_turns_before_pro:
            return RouterDecision(
                action=RouterAction.HOLD,
                maturity_score=score,
                target_cluster="edge",
                reasoning="Turnos mínimos no alcanzados para activación de clúster pesado.",
                active_turn=turn_index,
                maturity_vector=vector,
            )

        if score >= self.maturity_threshold:
            return RouterDecision(
                action=RouterAction.DISPATCH_PRO,
                maturity_score=score,
                target_cluster="pro",
                reasoning=f"Madurez de especificación ({score:.2f} >= {self.maturity_threshold}) confirmada. Despacho seguro sin riesgo de anclaje temprano.",
                active_turn=turn_index,
                maturity_vector=vector,
            )
        else:
            return RouterDecision(
                action=RouterAction.CLARIFY,
                maturity_score=score,
                target_cluster="edge",
                reasoning=f"Especificación inmadura ({score:.2f} < {self.maturity_threshold}). Edge absorbe ambigüedad para evitar error de sticking.",
                active_turn=turn_index,
                maturity_vector=vector,
            )
