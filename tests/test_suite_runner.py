"""
Suite ejecutable para todos los tests unitarios usando unittest nativo de Python.
"""

import unittest
from src.core.metrics import ACRAMetrics, MetricResult
from src.core.edge_router import EdgeRouter, RouterAction, RouterDecision, MessageTurn, TurnRole
from src.core.dhc import DynamicHistoryCompressor, CompressedContext
from src.core.unified_context import UnifiedContextTier
from src.core.handoff import HandoffEngine
from src.core.state_machine import ACRAStateMachine, SystemState, InvalidTransitionError
from src.core.orchestrator import ACRAOrchestrator, OrchestratorState
from src.core.models.mock_models import MockProModel


class TestACRAMetrics(unittest.TestCase):
    def test_metrics_calculation_standard(self):
        scores = [50.0, 60.0, 70.0, 80.0, 90.0]
        res = ACRAMetrics.calculate_performance_distribution(scores)
        self.assertIsInstance(res, MetricResult)
        self.assertEqual(res.mean_performance, 70.0)
        self.assertEqual(res.sample_size, 5)
        self.assertGreater(res.aptitude_p90, res.mean_performance)
        self.assertGreater(res.unreliability_p10_p90, 0.0)

    def test_metrics_empty_raises(self):
        with self.assertRaises(ValueError):
            ACRAMetrics.calculate_performance_distribution([])

    def test_ccr_calculation_valid(self):
        raw = 1000
        consolidated = 450
        ccr = ACRAMetrics.calculate_ccr(raw, consolidated)
        self.assertEqual(ccr, 0.55)
        self.assertGreater(ccr, 0.45)

    def test_degradation_delta(self):
        single = [80.0, 85.0, 90.0, 88.0, 82.0]
        multi = [40.0, 45.0, 65.0, 30.0, 50.0]
        delta = ACRAMetrics.compute_degradation_delta(single, multi)
        self.assertGreater(delta["performance_drop_pct"], 30.0)
        self.assertGreater(delta["unreliability_increase_pct"], 0.0)


class TestEdgeRouter(unittest.TestCase):
    def test_holds_on_early_ambiguous_turn(self):
        router = EdgeRouter(maturity_threshold=0.70, min_turns_before_pro=2)
        decision = router.route([], "hola, tal vez me puedas ayudar con algo")
        self.assertEqual(decision.action, RouterAction.HOLD)
        self.assertEqual(decision.target_cluster, "edge")
        self.assertLess(decision.maturity_score, 0.70)

    def test_dispatches_pro_when_mature(self):
        router = EdgeRouter(maturity_threshold=0.65, min_turns_before_pro=1)
        history = [
            MessageTurn(role=TurnRole.USER, content="Quiero diseñar la arquitectura de un pipeline distribuido", turn_index=1),
            MessageTurn(role=TurnRole.ASSISTANT, content="Por favor especifica las restricciones de concurrencia y volumen", turn_index=1),
        ]
        prompt = "El pipeline procesa 50GB en streaming, con deduplicación y optimizar la latencia mediante un algoritmo concurrente."
        decision = router.route(history, prompt)
        self.assertEqual(decision.action, RouterAction.DISPATCH_PRO)
        self.assertEqual(decision.target_cluster, "pro")


class TestDHC(unittest.TestCase):
    def test_masks_verbosity_and_preserves_code(self):
        dhc = DynamicHistoryCompressor()
        reply = (
            "¡Hola! Como modelo de lenguaje con gusto te ayudo.\n"
            "```python\ndef test(): pass\n```\n"
            "Avísame si necesitas algo más."
        )
        cleaned, code_blocks = dhc.mask_assistant_verbosity(reply)
        self.assertEqual(len(code_blocks), 1)
        self.assertNotIn("como modelo de lenguaje", cleaned.lower())

    def test_compress_positive_ccr(self):
        dhc = DynamicHistoryCompressor()
        history = [
            MessageTurn(role=TurnRole.USER, content="Necesito crear un índice invertido.", turn_index=1),
            MessageTurn(role=TurnRole.ASSISTANT, content="¡Hola! Con muchísimo gusto te explico todo el marco teórico...", turn_index=1)
        ]
        res = dhc.compress(history, "Restricción: 100k docs en < 5ms.")
        self.assertGreater(res.ccr, 0.0)
        self.assertEqual(len(res.consolidated_user_requirements), 2)


class TestUnifiedContextTier(unittest.TestCase):
    def test_persists_and_retrieves(self):
        uct = UnifiedContextTier(ttl_seconds=10.0)
        mock_comp = CompressedContext(
            raw_tokens_estimate=200,
            consolidated_tokens_estimate=90,
            ccr=0.55,
            purged_chatter_count=2,
            consolidated_user_requirements=["Req 1"],
            crystallized_code_artifacts=[],
            clean_history_prompt="1. Req 1",
        )
        snap = uct.persist_snapshot("sess_1", 2, mock_comp)
        self.assertEqual(snap.session_id, "sess_1")
        retrieved = uct.get_latest_snapshot("sess_1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.snapshot_id, snap.snapshot_id)


class TestHandoffEngine(unittest.TestCase):
    def test_assemble_clean_payload(self):
        engine = HandoffEngine()
        decision = RouterDecision(
            action=RouterAction.DISPATCH_PRO,
            maturity_score=0.85,
            target_cluster="pro",
            reasoning="mature",
            active_turn=2,
        )
        compressed = CompressedContext(
            raw_tokens_estimate=200,
            consolidated_tokens_estimate=80,
            ccr=0.60,
            purged_chatter_count=2,
            consolidated_user_requirements=["Req"],
            crystallized_code_artifacts=[],
            clean_history_prompt="Req",
        )
        payload = engine.assemble_clean_payload("sess_1", decision, compressed)
        self.assertEqual(payload.target_cluster, "pro")
        self.assertTrue(payload.is_sterilized)


class TestStateMachine(unittest.TestCase):
    def test_lifecycle(self):
        sm = ACRAStateMachine()
        sm.transition_to(SystemState.INGESTING)
        sm.transition_to(SystemState.CONSOLIDATING)
        sm.transition_to(SystemState.ROUTING_PRO)
        sm.transition_to(SystemState.EXECUTING_PRO)
        sm.transition_to(SystemState.RESPONDING)
        sm.transition_to(SystemState.IDLE)
        self.assertEqual(sm.current_state, SystemState.IDLE)

    def test_invalid_raises(self):
        sm = ACRAStateMachine()
        with self.assertRaises(InvalidTransitionError):
            sm.transition_to(SystemState.EXECUTING_PRO)


class TestOrchestrator(unittest.TestCase):
    def test_flow(self):
        orchestrator = ACRAOrchestrator()
        pro = MockProModel()
        res1 = orchestrator.process_turn("sess_100", "hola")
        self.assertEqual(res1.active_state, OrchestratorState.CLARIFYING)

        mature_prompt = (
            "Necesito optimizar la arquitectura de un pipeline distribuido con un algoritmo concurrente "
            "en Python para procesar 50GB en streaming con baja latencia y sin memory leak."
        )
        res2 = orchestrator.process_turn(
            "sess_100",
            mature_prompt,
            pro_inference_simulator_fn=lambda p: pro.generate(p, is_acra_payload=True).content
        )
        self.assertEqual(res2.active_state, OrchestratorState.DISPATCHING_PRO)
        self.assertIsNotNone(res2.clean_payload)


if __name__ == "__main__":
    unittest.main()
