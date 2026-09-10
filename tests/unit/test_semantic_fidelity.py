"""
Unit tests for MaturityVector and Semantic Fidelity Metrics (SF-Key, SF-Neg, CRR, EFR).
"""

import pytest
from src.core.edge_router import EdgeRouter, MessageTurn, TurnRole, MaturityVector
from src.core.metrics import ACRAMetrics, SemanticFidelityReport


def test_maturity_vector_evaluation():
    router = EdgeRouter()
    history = [
        MessageTurn(role=TurnRole.USER, content="¿Podrías ayudarme con algo? No estoy seguro...", turn_index=1),
        MessageTurn(role=TurnRole.ASSISTANT, content="¿Qué necesitas?", turn_index=1),
    ]

    vector = router.evaluate_maturity(history, "tal vez una base de datos")
    assert vector.semantic_ambiguity > 0.4
    assert vector.contextual_completeness < 0.5
    assert vector.composite_score < router.maturity_threshold

    # High complexity, low ambiguity query
    vector_mature = router.evaluate_maturity(
        history,
        "Implementar un algoritmo distribuido con arquitectura de pipeline asíncrono y benchmark formal."
    )
    assert vector_mature.contextual_completeness > 0.6
    assert vector_mature.composite_score > vector.composite_score


def test_semantic_fidelity_sf_key():
    consolidated = (
        "### CONSOLIDATED USER REQUIREMENTS:\n"
        "1. Build a distributed consensus engine using Raft algorithm.\n"
        "2. Target sub-5ms commit latency."
    )
    key_reqs = [
        "distributed consensus engine Raft algorithm",
        "sub-5ms commit latency",
    ]
    sf_key = ACRAMetrics.calculate_sf_key(consolidated, key_reqs)
    assert sf_key == 1.0

    missing_reqs = ["blockchain zero knowledge snark proof"]
    sf_key_missing = ACRAMetrics.calculate_sf_key(consolidated, missing_reqs)
    assert sf_key_missing == 0.0


def test_semantic_fidelity_sf_neg():
    consolidated = (
        "### CONSOLIDATED USER REQUIREMENTS:\n"
        "1. Use PostgreSQL database.\n"
    )
    negated_items = ["MongoDB document store", "Redis caching"]
    sf_neg = ACRAMetrics.calculate_sf_neg(consolidated, negated_items)
    assert sf_neg == 1.0

    # If negated item leaks into prompt:
    leaked_prompt = "Use PostgreSQL and Redis caching."
    sf_neg_leaked = ACRAMetrics.calculate_sf_neg(leaked_prompt, negated_items)
    assert sf_neg_leaked == 0.5


def test_evaluate_semantic_fidelity_report():
    report = ACRAMetrics.evaluate_semantic_fidelity(
        consolidated_text="Distributed Raft engine with sub-5ms commit latency.",
        key_requirements=["Distributed Raft engine", "sub-5ms commit latency"],
        negated_items=["MongoDB document store"],
        raw_tokens=200,
        consolidated_tokens=80,
        expected_cluster="pro",
        actual_cluster="pro",
    )
    assert isinstance(report, SemanticFidelityReport)
    assert report.sf_key == 1.0
    assert report.sf_neg == 1.0
    assert report.crr > 0.50
    assert report.routing_fidelity == 1.0
    assert report.composite_fidelity > 0.80
