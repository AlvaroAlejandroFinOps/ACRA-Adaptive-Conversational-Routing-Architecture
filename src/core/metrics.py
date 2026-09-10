"""
ACRA Metrics: Implementación formal de las ecuaciones matemáticas del RFC.
- Rendimiento Promedio (P̄)
- Aptitud al percentil 90 (A⁹⁰)
- Infiabilidad interpercentil (U₁₀⁹⁰)
- Context Consolidation Ratio (CCR)
"""

from typing import Sequence, Dict, Any, List
import numpy as np
from pydantic import BaseModel, Field


class MetricResult(BaseModel):
    """Contenedor validado de métricas cognitivas y de estabilización."""
    mean_performance: float = Field(..., description="Rendimiento promedio insesgado P̄")
    aptitude_p90: float = Field(..., description="Aptitud teórica en mejor escenario A⁹⁰")
    unreliability_p10_p90: float = Field(..., description="Brecha estocástica U₁₀⁹⁰")
    sample_size: int = Field(..., description="Número de simulaciones/turnos N")
    additional_stats: Dict[str, float] = Field(default_factory=dict)


class ACRAMetrics:
    """Motor matemático de evaluación de estabilidad cognitiva para ACRA."""

    @staticmethod
    def calculate_performance_distribution(scores: Sequence[float]) -> MetricResult:
        """
        Calcula las métricas formales del RFC:
        P̄ = (1/N) * sum(S_i)
        A⁹⁰ = percentile_90(S)
        U₁₀⁹⁰ = percentile_90(S) - percentile_10(S)
        """
        if not scores:
            raise ValueError("El conjunto de evaluaciones S no puede estar vacío.")

        arr = np.array(scores, dtype=np.float64)
        n = len(arr)
        
        p_bar = float(np.mean(arr))
        p90 = float(np.percentile(arr, 90))
        p10 = float(np.percentile(arr, 10))
        u10_90 = float(p90 - p10)

        std_dev = float(np.std(arr))
        variance = float(np.var(arr))

        return MetricResult(
            mean_performance=p_bar,
            aptitude_p90=p90,
            unreliability_p10_p90=u10_90,
            sample_size=n,
            additional_stats={
                "std_dev": std_dev,
                "variance": variance,
                "p10": p10,
                "p50_median": float(np.median(arr)),
            }
        )

    @staticmethod
    def calculate_ccr(raw_tokens: int, consolidated_tokens: int) -> float:
        """
        Calcula el Context Consolidation Ratio (CCR):
        CCR = (Tokens_Raw - Tokens_Consolidados) / Tokens_Raw
        Representa el porcentaje de tokens estocásticos/ruido purgados.
        Mandato 2 de ACRA: Debe ser > 45% en conversaciones de > 3 turnos.
        """
        if raw_tokens <= 0:
            return 0.0
        if consolidated_tokens < 0:
            raise ValueError("Tokens consolidados no pueden ser negativos.")
        
        purged = raw_tokens - consolidated_tokens
        if purged < 0:
            # Caso anómalo donde la consolidación infló el prompt
            return 0.0
        return float(purged / raw_tokens)

    @staticmethod
    def compute_degradation_delta(single_turn_scores: Sequence[float], multi_turn_scores: Sequence[float]) -> Dict[str, float]:
        """
        Calcula la brecha relativa de degradación multi-turno frente a single-turn:
        ΔP̄ = (P̄_single - P̄_multi) / P̄_single
        ΔU = (U_multi - U_single) / U_single
        """
        m_single = ACRAMetrics.calculate_performance_distribution(single_turn_scores)
        m_multi = ACRAMetrics.calculate_performance_distribution(multi_turn_scores)

        perf_drop = (m_single.mean_performance - m_multi.mean_performance) / (m_single.mean_performance or 1e-9)
        apt_drop = (m_single.aptitude_p90 - m_multi.aptitude_p90) / (m_single.aptitude_p90 or 1e-9)
        unrel_increase = (m_multi.unreliability_p10_p90 - m_single.unreliability_p10_p90) / (m_single.unreliability_p10_p90 or 1e-9)

        return {
            "performance_drop_pct": float(perf_drop * 100.0),
            "aptitude_drop_pct": float(apt_drop * 100.0),
            "unreliability_increase_pct": float(unrel_increase * 100.0),
            "single_mean": m_single.mean_performance,
            "multi_mean": m_multi.mean_performance,
            "single_unreliability": m_single.unreliability_p10_p90,
            "multi_unreliability": m_multi.unreliability_p10_p90,
        }
