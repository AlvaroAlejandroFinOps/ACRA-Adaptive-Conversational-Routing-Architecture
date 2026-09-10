import pytest
import numpy as np
from src.core.metrics import ACRAMetrics, MetricResult


def test_metrics_calculation_standard():
    scores = [50.0, 60.0, 70.0, 80.0, 90.0]
    res = ACRAMetrics.calculate_performance_distribution(scores)

    assert isinstance(res, MetricResult)
    assert res.mean_performance == 70.0
    assert res.sample_size == 5
    assert res.aptitude_p90 > res.mean_performance
    assert res.unreliability_p10_p90 > 0.0


def test_metrics_empty_raises():
    with pytest.raises(ValueError):
        ACRAMetrics.calculate_performance_distribution([])


def test_ccr_calculation_valid():
    raw = 1000
    consolidated = 450
    ccr = ACRAMetrics.calculate_ccr(raw, consolidated)
    assert ccr == 0.55
    assert ccr > 0.45  # Cumple el Mandato 2 del RFC


def test_ccr_edge_cases():
    assert ACRAMetrics.calculate_ccr(0, 10) == 0.0
    assert ACRAMetrics.calculate_ccr(100, 100) == 0.0
    assert ACRAMetrics.calculate_ccr(100, 0) == 1.0
    # Caso anómalo de expansión
    assert ACRAMetrics.calculate_ccr(100, 150) == 0.0


def test_degradation_delta():
    single = [80.0, 85.0, 90.0, 88.0, 82.0]
    multi = [40.0, 45.0, 65.0, 30.0, 50.0]
    delta = ACRAMetrics.compute_degradation_delta(single, multi)

    assert delta["performance_drop_pct"] > 30.0
    assert delta["unreliability_increase_pct"] > 0.0
