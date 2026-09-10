"""
Integration Tests: Test del flujo orquestado completo y test del benchmark A/B.
"""

import unittest
from src.core.orchestrator import ACRAOrchestrator, OrchestratorState
from src.core.models.mock_models import MockProModel
from src.core.metrics import ACRAMetrics
from src.data_generation.conversation_generator import ConversationGenerator


class TestIntegrationOrchestratorFlow(unittest.TestCase):
    def test_complete_conversation_lifecycle(self):
        orchestrator = ACRAOrchestrator()
        pro = MockProModel()
        session_id = "integ_sess_999"

        # Turno 1: Ambigüedad -> Edge contención
        res1 = orchestrator.process_turn(session_id, "Hola, tengo dudas sobre cómo optimizar un sistema.")
        self.assertEqual(res1.active_state, OrchestratorState.CLARIFYING)
        self.assertIsNone(res1.clean_payload)

        # Turno 2: Clarificación con ambigüedad persistente
        res2 = orchestrator.process_turn(session_id, "No estoy seguro, quizás algo con python y consultas lentas.")
        self.assertEqual(res2.active_state, OrchestratorState.CLARIFYING)

        # Turno 3: Especificación madura -> Despacho a Pro
        mature_input = (
            "Necesito diseñar una arquitectura distribuida con un algoritmo concurrente para balancear carga "
            "en streaming con tolerancia a fallos y sin memory leak."
        )
        res3 = orchestrator.process_turn(
            session_id,
            mature_input,
            pro_inference_simulator_fn=lambda p: pro.generate(p, is_acra_payload=True).content
        )

        self.assertEqual(res3.active_state, OrchestratorState.DISPATCHING_PRO)
        self.assertIsNotNone(res3.clean_payload)
        self.assertTrue(res3.clean_payload.is_sterilized)
        self.assertGreater(res3.ccr, 0.0)
        self.assertIn("MockPro", res3.response_text)


class TestIntegrationABBenchmark(unittest.TestCase):
    def test_acra_superiority_assertion(self):
        suite = ConversationGenerator.generate_benchmark_suite(num_conversations=20)
        orchestrator = ACRAOrchestrator()
        pro = MockProModel()

        baseline_scores = []
        acra_scores = []

        for conv in suite:
            raw_prompt = "\n".join([t.user_prompt for t in conv.turns])
            resp_raw = pro.generate(raw_prompt, is_acra_payload=False)
            baseline_scores.append(resp_raw.metadata["simulated_score"])

            session_id = f"integ_{conv.conversation_id}"
            last_res = None
            for t in conv.turns:
                last_res = orchestrator.process_turn(
                    session_id,
                    t.user_prompt,
                    pro_inference_simulator_fn=lambda p: pro.generate(p, is_acra_payload=True).metadata["simulated_score"]
                )

            if last_res and last_res.active_state == OrchestratorState.DISPATCHING_PRO:
                resp_pro = pro.generate(last_res.clean_payload.prefill_prompt, is_acra_payload=True)
                acra_scores.append(resp_pro.metadata["simulated_score"])
            else:
                acra_scores.append(50.0)

        dist_base = ACRAMetrics.calculate_performance_distribution(baseline_scores)
        dist_acra = ACRAMetrics.calculate_performance_distribution(acra_scores)

        # Invariante de estabilización cognitiva: ACRA debe reducir la infiabilidad
        self.assertGreater(dist_acra.mean_performance, dist_base.mean_performance)


if __name__ == "__main__":
    unittest.main()
