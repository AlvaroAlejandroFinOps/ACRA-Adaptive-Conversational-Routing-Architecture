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


class SemanticFidelityReport(BaseModel):
    """Métricas avanzadas de fidelidad semántica de compresión y enrutamiento."""
    sf_key: float = Field(..., ge=0.0, le=1.0, description="Fidelidad en retención de requerimientos clave (SF-Key)")
    sf_neg: float = Field(..., ge=0.0, le=1.0, description="Fidelidad en exclusión de directivas anuladas/negadas (SF-Neg)")
    crr: float = Field(..., ge=0.0, le=1.0, description="Reducción de redundancia contextual (CRR)")
    routing_fidelity: float = Field(..., ge=0.0, le=1.0, description="Fidelidad en decisión de enrutamiento")
    composite_fidelity: float = Field(..., ge=0.0, le=1.0, description="Score compuesto de fidelidad cognitiva")
    details: Dict[str, Any] = Field(default_factory=dict)


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
    def calculate_sf_key(consolidated_text: str, key_requirements: List[str]) -> float:
        """
        SF-Key: Fracción de requerimientos técnicos clave preservados en el canvas consolidado.
        """
        if not key_requirements:
            return 1.0
        text_lower = consolidated_text.lower()
        matched = 0
        for req in key_requirements:
            req_words = [w.lower() for w in req.split() if len(w) > 3]
            if not req_words:
                matched += 1
                continue
            matches_count = sum(1 for w in req_words if w in text_lower)
            if matches_count / len(req_words) >= 0.60:
                matched += 1
        return float(matched / len(key_requirements))

    @staticmethod
    def calculate_sf_neg(consolidated_text: str, negated_items: List[str]) -> float:
        """
        SF-Neg: Fracción de directivas canceladas/reemplazadas que fueron exitosamente excluidas.
        Un score de 1.0 indica que ninguna directiva revocada sobrevivió en el prompt.
        """
        if not negated_items:
            return 1.0
        text_lower = consolidated_text.lower()
        leaked = 0
        for neg in negated_items:
            neg_words = [w.lower() for w in neg.split() if len(w) > 3]
            if not neg_words:
                continue
            if all(w in text_lower for w in neg_words):
                leaked += 1
        return float(1.0 - (leaked / len(negated_items)))

    @staticmethod
    def evaluate_semantic_fidelity(
        consolidated_text: str,
        key_requirements: List[str],
        negated_items: List[str],
        raw_tokens: int,
        consolidated_tokens: int,
        expected_cluster: str,
        actual_cluster: str,
    ) -> SemanticFidelityReport:
        """Genera un reporte integral de fidelidad semántica y de enrutamiento."""
        sf_key = ACRAMetrics.calculate_sf_key(consolidated_text, key_requirements)
        sf_neg = ACRAMetrics.calculate_sf_neg(consolidated_text, negated_items)
        crr = ACRAMetrics.calculate_ccr(raw_tokens, consolidated_tokens)
        routing_fidelity = 1.0 if expected_cluster.lower() == actual_cluster.lower() else 0.0

        # Ponderación formal de fidelidad
        composite = (0.35 * sf_key) + (0.25 * sf_neg) + (0.20 * crr) + (0.20 * routing_fidelity)

        return SemanticFidelityReport(
            sf_key=sf_key,
            sf_neg=sf_neg,
            crr=crr,
            routing_fidelity=routing_fidelity,
            composite_fidelity=float(composite),
            details={
                "key_requirements_count": len(key_requirements),
                "negated_items_count": len(negated_items),
                "raw_tokens": raw_tokens,
                "consolidated_tokens": consolidated_tokens,
            },
        )

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
