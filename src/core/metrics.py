"""
ACRA Metrics: Implementación formal de las ecuaciones matemáticas del RFC.
- Rendimiento Promedio (P̄)
- Aptitud al percentil 90 (A⁹⁰)
- Infiabilidad interpercentil (U₁₀⁹⁰)
- Context Consolidation Ratio (CCR)
"""

from __future__ import annotations

from typing import Sequence, Dict, Any, List
import numpy as np
from pydantic import BaseModel, Field

from src.core.contracts.audit import EpistemicStatus


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

    @staticmethod
    def evaluate_cognitive_degradation_report(
        context_risk_score: float = 0.05,
        evidence_coverage: float = 1.0,
        context_utilization_ratio: float = 0.85,
        context_reuse_ratio: float = 0.60,
        provider_reported_cache_hit_ratio: float = 0.50,
        estimated_cache_reuse_ratio: float = 0.55,
        context_rebuild_tokens: int = 0,
        effective_cost_per_validated_task: float = 0.02,
        tokens_per_validated_outcome: int = 1200,
        model_switch_count: int = 0,
        provider_switch_count: int = 0,
        avoidable_model_switch_rate: float = 0.0,
        cache_break_even_accuracy: float = 0.95,
        context_compaction_regret: float = 0.02,
        routing_regret: float = 0.01,
        retry_amplification: float = 1.0,
        handoff_expansion_ratio: float = 1.05,
        stale_tool_result_rate: float = 0.0,
        cross_domain_leakage_rate: float = 0.0,
        agent_context_contamination_rate: float = 0.0,
    ) -> CognitiveDegradationReport:
        """Compute comprehensive 20-metric degradation and quality report tagged with epistemic status (§17)."""
        return CognitiveDegradationReport(
            context_risk_score=MetricWithEpistemicStatus(
                value=float(context_risk_score), epistemic_status=EpistemicStatus.VERIFIED, description="Composite risk from audit layer"
            ),
            evidence_coverage=MetricWithEpistemicStatus(
                value=float(evidence_coverage), epistemic_status=EpistemicStatus.MEASURED, description="Substantiated claim coverage"
            ),
            context_utilization_ratio=MetricWithEpistemicStatus(
                value=float(context_utilization_ratio), epistemic_status=EpistemicStatus.MEASURED, description="Context tokens utilized in reasoning"
            ),
            context_reuse_ratio=MetricWithEpistemicStatus(
                value=float(context_reuse_ratio), epistemic_status=EpistemicStatus.PROVIDER_REPORTED, description="Ratio of reused tokens from cache"
            ),
            provider_reported_cache_hit_ratio=MetricWithEpistemicStatus(
                value=float(provider_reported_cache_hit_ratio), epistemic_status=EpistemicStatus.PROVIDER_REPORTED, description="Direct provider cache hit rate"
            ),
            estimated_cache_reuse_ratio=MetricWithEpistemicStatus(
                value=float(estimated_cache_reuse_ratio), epistemic_status=EpistemicStatus.ESTIMATED, description="Estimated reusable token ratio"
            ),
            context_rebuild_tokens=MetricWithEpistemicStatus(
                value=float(context_rebuild_tokens), epistemic_status=EpistemicStatus.MEASURED, description="Re-ingested tokens due to cache miss"
            ),
            effective_cost_per_validated_task=MetricWithEpistemicStatus(
                value=float(effective_cost_per_validated_task), epistemic_status=EpistemicStatus.MEASURED, description="USD cost per successful task outcome"
            ),
            tokens_per_validated_outcome=MetricWithEpistemicStatus(
                value=float(tokens_per_validated_outcome), epistemic_status=EpistemicStatus.MEASURED, description="Total tokens consumed per outcome"
            ),
            model_switch_count=MetricWithEpistemicStatus(
                value=float(model_switch_count), epistemic_status=EpistemicStatus.MEASURED, description="Count of model transitions"
            ),
            provider_switch_count=MetricWithEpistemicStatus(
                value=float(provider_switch_count), epistemic_status=EpistemicStatus.MEASURED, description="Count of provider handoffs"
            ),
            avoidable_model_switch_rate=MetricWithEpistemicStatus(
                value=float(avoidable_model_switch_rate), epistemic_status=EpistemicStatus.INFERRED, description="Fraction of model switches with negative ROI"
            ),
            cache_break_even_accuracy=MetricWithEpistemicStatus(
                value=float(cache_break_even_accuracy), epistemic_status=EpistemicStatus.ESTIMATED, description="Accuracy threshold needed to justify switch"
            ),
            context_compaction_regret=MetricWithEpistemicStatus(
                value=float(context_compaction_regret), epistemic_status=EpistemicStatus.INFERRED, description="Quality drop due to aggressive compaction"
            ),
            routing_regret=MetricWithEpistemicStatus(
                value=float(routing_regret), epistemic_status=EpistemicStatus.INFERRED, description="Cost differential from sub-optimal routing decisions"
            ),
            retry_amplification=MetricWithEpistemicStatus(
                value=float(retry_amplification), epistemic_status=EpistemicStatus.MEASURED, description="Ratio of total calls to primary task attempts"
            ),
            handoff_expansion_ratio=MetricWithEpistemicStatus(
                value=float(handoff_expansion_ratio), epistemic_status=EpistemicStatus.MEASURED, description="Context size inflation ratio during handoff"
            ),
            stale_tool_result_rate=MetricWithEpistemicStatus(
                value=float(stale_tool_result_rate), epistemic_status=EpistemicStatus.MEASURED, description="Frequency of invalidated tool outputs retained"
            ),
            cross_domain_leakage_rate=MetricWithEpistemicStatus(
                value=float(cross_domain_leakage_rate), epistemic_status=EpistemicStatus.MEASURED, description="Rate of cross-domain context contamination"
            ),
            agent_context_contamination_rate=MetricWithEpistemicStatus(
                value=float(agent_context_contamination_rate), epistemic_status=EpistemicStatus.INFERRED, description="Contamination from volatile parent state"
            ),
        )


class MetricWithEpistemicStatus(BaseModel):
    """An individual degradation/quality metric tagged with its epistemic status (INV-004)."""
    value: float = Field(..., description="Numerical metric value")
    epistemic_status: EpistemicStatus = Field(..., description="Declared epistemic status (INV-004)")
    description: str = Field(default="", description="Diagnostic purpose of the metric")


class CognitiveDegradationReport(BaseModel):
    """Comprehensive container for the 20 degradation & quality metrics (§17 EVO ACRA.md)."""
    context_risk_score: MetricWithEpistemicStatus
    evidence_coverage: MetricWithEpistemicStatus
    context_utilization_ratio: MetricWithEpistemicStatus
    context_reuse_ratio: MetricWithEpistemicStatus
    provider_reported_cache_hit_ratio: MetricWithEpistemicStatus
    estimated_cache_reuse_ratio: MetricWithEpistemicStatus
    context_rebuild_tokens: MetricWithEpistemicStatus
    effective_cost_per_validated_task: MetricWithEpistemicStatus
    tokens_per_validated_outcome: MetricWithEpistemicStatus
    model_switch_count: MetricWithEpistemicStatus
    provider_switch_count: MetricWithEpistemicStatus
    avoidable_model_switch_rate: MetricWithEpistemicStatus
    cache_break_even_accuracy: MetricWithEpistemicStatus
    context_compaction_regret: MetricWithEpistemicStatus
    routing_regret: MetricWithEpistemicStatus
    retry_amplification: MetricWithEpistemicStatus
    handoff_expansion_ratio: MetricWithEpistemicStatus
    stale_tool_result_rate: MetricWithEpistemicStatus
    cross_domain_leakage_rate: MetricWithEpistemicStatus
    agent_context_contamination_rate: MetricWithEpistemicStatus

