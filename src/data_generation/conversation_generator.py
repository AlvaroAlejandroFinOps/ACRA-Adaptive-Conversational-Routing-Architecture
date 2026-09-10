"""
Data Generation & Synthetic Multi-Turn Conversations.
Permite simular corpus conversacionales multi-turno con perfiles controlados de degradación:
- clear_intent: Instrucciones maduras desde el inicio.
- ambiguous: Consultas vagas que requieren clarificación.
- intent_drift: Desvío y contradicciones en turnos intermedios.
- answer_bloat: Salidas verbosas y código redundante.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SimulatedTurn(BaseModel):
    turn_index: int
    user_prompt: str
    expected_mature: bool
    noise_level: float = 0.0


class SyntheticConversation(BaseModel):
    conversation_id: str
    profile: str
    turns: List[SimulatedTurn]
    ground_truth_solution_score: float = 85.0


class ConversationGenerator:
    """Generador de diálogos sintéticos para experimentación rigurosa."""

    PROFILES = ["clear_intent", "ambiguous", "intent_drift", "answer_bloat"]

    @staticmethod
    def generate_benchmark_suite(num_conversations: int = 50) -> List[SyntheticConversation]:
        """Genera un lote balanceado de conversaciones multi-turno."""
        suite: List[SyntheticConversation] = []

        for i in range(num_conversations):
            profile = ConversationGenerator.PROFILES[i % len(ConversationGenerator.PROFILES)]
            conv_id = f"sim_conv_{i:04d}_{profile}"
            turns: List[SimulatedTurn] = []

            if profile == "clear_intent":
                turns.append(SimulatedTurn(
                    turn_index=1,
                    user_prompt="Diseñar e implementar un algoritmo en Python para balanceo de carga estocástico con límites de VRAM.",
                    expected_mature=True,
                    noise_level=0.05
                ))
            elif profile == "ambiguous":
                turns.append(SimulatedTurn(
                    turn_index=1,
                    user_prompt="Hola, quiero hacer algo con servidores.",
                    expected_mature=False,
                    noise_level=0.70
                ))
                turns.append(SimulatedTurn(
                    turn_index=2,
                    user_prompt="Quizás optimizar los tiempos de inferencia de unos modelos.",
                    expected_mature=False,
                    noise_level=0.45
                ))
                turns.append(SimulatedTurn(
                    turn_index=3,
                    user_prompt="Específicamente implementar un router con umbrales de latencia y saturación de memoria distribuida.",
                    expected_mature=True,
                    noise_level=0.10
                ))
            elif profile == "intent_drift":
                turns.append(SimulatedTurn(
                    turn_index=1,
                    user_prompt="Crea una función para calcular estadísticas descriptivas sobre tensores.",
                    expected_mature=True,
                    noise_level=0.10
                ))
                turns.append(SimulatedTurn(
                    turn_index=2,
                    user_prompt="Olvida los tensores, ahora quiero un scraper de noticias en asyncio.",
                    expected_mature=True,
                    noise_level=0.60
                ))
            elif profile == "answer_bloat":
                turns.append(SimulatedTurn(
                    turn_index=1,
                    user_prompt="Explícame cómo funciona un Transformer en multi-head attention.",
                    expected_mature=True,
                    noise_level=0.20
                ))
                turns.append(SimulatedTurn(
                    turn_index=2,
                    user_prompt="Ahora optimiza el mecanismo con sliding window attention para secuencias largas.",
                    expected_mature=True,
                    noise_level=0.25
                ))

            suite.append(SyntheticConversation(
                conversation_id=conv_id,
                profile=profile,
                turns=turns,
                ground_truth_solution_score=85.0
            ))

        return suite
