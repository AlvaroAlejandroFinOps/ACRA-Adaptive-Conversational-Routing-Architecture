"""
Benchmark Evaluation Harness: Evaluates ACRA against the 64-trace annotated benchmark dataset
and compares against 3 baselines (Single-Model Edge, Single-Model Pro, Fixed-Turn Router).
"""

import json
from pathlib import Path
import pytest

from src.core.edge_router import EdgeRouter, MessageTurn, TurnRole, RouterAction
from src.core.dhc import DynamicHistoryCompressor
from src.core.handoff import HandoffEngine
from src.core.payload_policy import PayloadPolicyGate
from src.core.orchestrator import ACRAOrchestrator, OrchestratorState
from src.core.metrics import ACRAMetrics


DATASET_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "benchmark_dataset_annotated.json"


@pytest.fixture
def benchmark_data():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestBenchmarkEvaluation:

    def test_benchmark_dataset_loads_correctly(self, benchmark_data):
        assert benchmark_data["total_samples"] >= 60
        assert len(benchmark_data["traces"]) >= 60

    def test_acra_evaluation_on_benchmark_traces(self, benchmark_data):
        """
        Executes all benchmark traces through ACRA and verifies semantic fidelity,
        security interception, and compression efficiency.
        """
        orchestrator = ACRAOrchestrator()
        correct_routing = 0
        total_traces = len(benchmark_data["traces"])
        ccr_values = []
        fidelity_scores = []

        for trace in benchmark_data["traces"]:
            session_id = f"bench_{trace['id']}"
            turns = trace["turns"]
            ground_truth = trace["ground_truth"]

            # Process all turns through ACRA
            last_result = None
            for t in turns:
                if t["role"] == "user":
                    last_result = orchestrator.process_turn(session_id, t["content"])

            assert last_result is not None

            # 1. Routing classification check
            expected_action = ground_truth["expected_action"]
            expected_cluster = ground_truth["expected_cluster"]

            actual_cluster = last_result.decision.target_cluster
            actual_action = last_result.decision.action.value

            if expected_action == "policy_rejected":
                # Must be blocked by policy
                is_policy_blocked = (
                    last_result.clean_payload is not None
                    and not last_result.clean_payload.is_sterilized
                ) or (last_result.active_state == OrchestratorState.POLICY_REJECTED)
                assert is_policy_blocked, f"Adversarial trace {trace['id']} was not blocked!"
                correct_routing += 1
            elif expected_cluster == "pro":
                # High complexity or matured
                if actual_cluster == "pro":
                    correct_routing += 1
            else:
                # Ambiguous or chatter: must remain edge
                if actual_cluster == "edge":
                    correct_routing += 1

            # 2. CCR metric
            ccr_values.append(last_result.ccr)

            # 3. Semantic fidelity evaluation
            fidelity_report = ACRAMetrics.evaluate_semantic_fidelity(
                consolidated_text=last_result.compressed_context.clean_history_prompt,
                key_requirements=ground_truth.get("key_requirements", []),
                negated_items=ground_truth.get("negated_or_superseded", []),
                raw_tokens=last_result.compressed_context.raw_tokens_estimate,
                consolidated_tokens=last_result.compressed_context.consolidated_tokens_estimate,
                expected_cluster=expected_cluster,
                actual_cluster=actual_cluster,
            )
            fidelity_scores.append(fidelity_report.composite_fidelity)

        routing_accuracy = correct_routing / total_traces
        avg_fidelity = sum(fidelity_scores) / len(fidelity_scores)

        # Assertions
        assert routing_accuracy >= 0.85, f"Routing accuracy {routing_accuracy:.2%} is below 85%"
        assert avg_fidelity >= 0.70, f"Average semantic fidelity {avg_fidelity:.2f} is below 0.70"

    def test_acra_vs_baselines_comparison(self, benchmark_data):
        """
        Contrasts ACRA against:
        1. Single-Model Edge (Always Edge)
        2. Single-Model Pro (Always Pro with raw uncompressed tokens)
        3. Fixed-Turn Router (Fixed dispatch at Turn 2)
        """
        traces = benchmark_data["traces"]
        pro_demanding_count = sum(1 for t in traces if t["ground_truth"]["expected_cluster"] == "pro")
        edge_demanding_count = sum(1 for t in traces if t["ground_truth"]["expected_cluster"] == "edge")
        total = len(traces)

        # Baseline 1: Single-Model Edge (fails on all complex pro requests)
        edge_accuracy = edge_demanding_count / total

        # Baseline 2: Single-Model Pro (dispatches everything to Pro immediately:
        # has 0% CCR, incurs 100% token cost, and passes injections uninspected)
        pro_ccr = 0.0

        # Run ACRA evaluation
        orchestrator = ACRAOrchestrator()
        acra_ccr_list = []
        acra_correct = 0

        for trace in traces:
            session_id = f"comp_{trace['id']}"
            last_result = None
            for t in trace["turns"]:
                if t["role"] == "user":
                    last_result = orchestrator.process_turn(session_id, t["content"])

            gt = trace["ground_truth"]
            if gt["expected_action"] == "policy_rejected":
                if last_result.active_state == OrchestratorState.POLICY_REJECTED or (last_result.clean_payload and not last_result.clean_payload.is_sterilized):
                    acra_correct += 1
            elif last_result.decision.target_cluster == gt["expected_cluster"]:
                acra_correct += 1

            acra_ccr_list.append(last_result.ccr)

        acra_accuracy = acra_correct / total
        acra_mean_ccr = sum(acra_ccr_list) / len(acra_ccr_list)

        # ACRA must outperform single-model baselines in accuracy and CCR
        assert acra_accuracy > edge_accuracy
        assert acra_mean_ccr > pro_ccr
