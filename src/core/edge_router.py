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


class MessageTurn(BaseModel):
    role: TurnRole
    content: str
    turn_index: int
    token_count: Optional[int] = None
    is_clarification: bool = False


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

    def assess_maturity(self, history: List[MessageTurn], current_input: str) -> float:
        """
        Evalúa el grado de completitud y madurez de la consulta actual considerando el historial.
        Penaliza la ambigüedad y premia la presencia de restricciones concretas y longitud crítica.
        """
        combined_text = (current_input + " " + " ".join([m.content for m in history if m.role == TurnRole.USER])).lower()
        words = combined_text.split()
        word_count = len(words)

        # 1. Base por longitud informativa (saturación en 20 palabras técnicas)
        length_factor = min(1.0, word_count / 20.0)

        # 2. Detección de marcadores de ambigüedad (penalización)
        ambiguity_count = sum(1 for marker in self.ambiguity_markers if marker in combined_text)
        ambiguity_penalty = min(0.4, ambiguity_count * 0.15)

        # 3. Detección de especificidad/complejidad (bonificación)
        complexity_hits = sum(1 for kw in self.complexity_keywords if kw in combined_text)
        complexity_bonus = min(0.50, complexity_hits * 0.25)

        # 4. Estabilidad en turnos sucesivos (más turnos de clarificación aumentan la convergencia)
        turn_stability_bonus = min(0.30, len(history) * 0.10)

        raw_score = (length_factor * 0.45) + complexity_bonus + turn_stability_bonus - ambiguity_penalty
        return float(max(0.0, min(1.0, raw_score)))

    def route(self, history: List[MessageTurn], current_input: str) -> RouterDecision:
        """Determina si la consulta se despacha al clúster Pro o se maneja en Edge."""
        turn_index = len(history) + 1
        score = self.assess_maturity(history, current_input)

        if turn_index < self.min_turns_before_pro:
            return RouterDecision(
                action=RouterAction.HOLD,
                maturity_score=score,
                target_cluster="edge",
                reasoning="Turnos mínimos no alcanzados para activación de clúster pesado.",
                active_turn=turn_index,
            )

        if score >= self.maturity_threshold:
            return RouterDecision(
                action=RouterAction.DISPATCH_PRO,
                maturity_score=score,
                target_cluster="pro",
                reasoning=f"Madurez de especificación ({score:.2f} >= {self.maturity_threshold}) confirmada. Despacho seguro sin riesgo de anclaje temprano.",
                active_turn=turn_index,
            )
        else:
            return RouterDecision(
                action=RouterAction.CLARIFY,
                maturity_score=score,
                target_cluster="edge",
                reasoning=f"Especificación inmadura ({score:.2f} < {self.maturity_threshold}). Edge absorbe ambigüedad para evitar error de sticking.",
                active_turn=turn_index,
            )
