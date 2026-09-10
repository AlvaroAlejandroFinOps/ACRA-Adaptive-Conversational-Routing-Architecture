import pytest
from src.core.edge_router import EdgeRouter, RouterAction, MessageTurn, TurnRole


def test_edge_router_holds_on_early_ambiguous_turn():
    router = EdgeRouter(maturity_threshold=0.70, min_turns_before_pro=2)
    history = []
    current_input = "hola, tal vez me puedas ayudar con algo"

    decision = router.route(history, current_input)
    assert decision.action == RouterAction.HOLD
    assert decision.target_cluster == "edge"
    assert decision.maturity_score < 0.70


def test_edge_router_dispatches_pro_when_mature():
    router = EdgeRouter(maturity_threshold=0.65, min_turns_before_pro=1)
    history = [
        MessageTurn(role=TurnRole.USER, content="Quiero diseñar la arquitectura de un pipeline distribuido", turn_index=1),
        MessageTurn(role=TurnRole.ASSISTANT, content="Por favor especifica las restricciones de concurrencia y volumen", turn_index=1),
    ]
    current_input = "El pipeline procesa 50GB en streaming, con deduplicación y optimizar la latencia mediante un algoritmo concurrente."

    decision = router.route(history, current_input)
    assert decision.action == RouterAction.DISPATCH_PRO
    assert decision.target_cluster == "pro"
    assert decision.maturity_score >= 0.65


def test_edge_router_clarifies_when_turn_count_met_but_ambiguous():
    router = EdgeRouter(maturity_threshold=0.70, min_turns_before_pro=1)
    history = [
        MessageTurn(role=TurnRole.USER, content="hola", turn_index=1),
        MessageTurn(role=TurnRole.ASSISTANT, content="en qué te ayudo?", turn_index=1),
    ]
    current_input = "no estoy seguro, quizás algo con python o lo que sea"

    decision = router.route(history, current_input)
    assert decision.action == RouterAction.CLARIFY
    assert decision.target_cluster == "edge"
