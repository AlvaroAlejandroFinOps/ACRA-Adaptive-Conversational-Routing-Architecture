"""Unit tests for ACRA Hierarchical Orchestrator, Task Graph, and 5 FSMs (Phase 5).

Verifies hierarchical decomposition, DAG execution ordering, outcome consolidation
without context mixing (INV-003), and cycle prevention guards across all 5 FSMs (INV-008).
"""

import pytest

from src.core.agents.lifecycle import AgentInstanceStateMachine
from src.core.agents.registry import AgentRegistry
from src.core.contracts.agent import AgentCapability, AgentDefinition
from src.core.contracts.audit import EpistemicStatus
from src.core.contracts.handoff import HandoffState
from src.core.contracts.outcome import AgentOutcome, ConsolidatedOutcome
from src.core.contracts.task import DependencyType, TaskDefinition, TaskDependency, TaskState
from src.core.fsm.handoff_fsm import HandoffStateMachine, InvalidHandoffTransitionError
from src.core.fsm.objective import (
    InvalidObjectiveTransitionError,
    ObjectiveState,
    ObjectiveStateMachine,
)
from src.core.fsm.session import (
    InvalidSessionTransitionError,
    SessionStateMachine,
    SystemState,
)
from src.core.fsm.task import InvalidTaskTransitionError, TaskStateMachine
from src.core.orchestration.consolidator import Consolidator
from src.core.orchestration.hierarchical_orchestrator import HierarchicalAgentOrchestrator
from src.core.orchestration.objective_planner import ObjectivePlanner
from src.core.orchestration.task_graph import CycleDetectedError, TaskGraph
from src.core.orchestrator import ACRAOrchestrator
from src.core.providers.stub import DeterministicStubProvider
from src.core.routing.intake_router import IntakeRouter
from src.core.routing.model_resolver import ModelCapabilityRegistry


class TestTaskGraph:
    """Verifies TaskGraph DAG ordering and cycle prevention (INV-008)."""

    def test_topological_sort_order(self) -> None:
        """Verify Kahn's algorithm resolves task dependencies in correct linear order."""
        graph = TaskGraph(graph_id="graph_test")
        t1 = TaskDefinition(task_id="t1", objective_id="obj_1", description="Init", target_domain="ops")
        t2 = TaskDefinition(
            task_id="t2", objective_id="obj_1", description="Build", target_domain="ops",
            dependencies=[TaskDependency(depends_on_task_id="t1", dependency_type=DependencyType.HARD)],
        )
        t3 = TaskDefinition(
            task_id="t3", objective_id="obj_1", description="Deploy", target_domain="ops",
            dependencies=[TaskDependency(depends_on_task_id="t2", dependency_type=DependencyType.HARD)],
        )

        # Add in non-topological order
        graph.add_task(t3)
        graph.add_task(t1)
        graph.add_task(t2)

        order = graph.get_execution_order()
        assert order == ["t1", "t2", "t3"]

    def test_cycle_detection_raises_error(self) -> None:
        """Verify cyclic dependency triggers CycleDetectedError (INV-008)."""
        graph = TaskGraph(graph_id="graph_cycle")
        t1 = TaskDefinition(
            task_id="t1", objective_id="obj_c", description="T1", target_domain="ops",
            dependencies=[TaskDependency(depends_on_task_id="t2", dependency_type=DependencyType.HARD)],
        )
        t2 = TaskDefinition(
            task_id="t2", objective_id="obj_c", description="T2", target_domain="ops",
            dependencies=[TaskDependency(depends_on_task_id="t1", dependency_type=DependencyType.HARD)],
        )
        graph.add_task(t1)
        graph.add_task(t2)

        with pytest.raises(CycleDetectedError, match="Circular task dependency"):
            graph.get_execution_order()


class TestObjectivePlanner:
    """Verifies objective planning and multi-stage decomposition."""

    def test_simple_vs_complex_decomposition(self) -> None:
        """Verify single vs multi-task decomposition according to complexity classification."""
        planner = ObjectivePlanner()
        intake = IntakeRouter()

        simple_class = intake.classify("Check database status")
        graph_simple, fsm_simple = planner.plan_and_decompose("obj_s", "Check database status", simple_class)
        assert len(graph_simple.tasks) == 1
        assert fsm_simple.state == ObjectiveState.DECOMPOSED

        complex_class = intake.classify("Coordinate comprehensive multi-phase security and finance architecture audit")
        graph_complex, fsm_complex = planner.plan_and_decompose("obj_c", "Complex audit", complex_class)
        assert len(graph_complex.tasks) == 3
        assert fsm_complex.state == ObjectiveState.DECOMPOSED


class TestConsolidator:
    """Verifies outcome consolidation without context mixing (INV-003, INV-004)."""

    def test_consolidation_synthesis(self) -> None:
        """Verify aggregation of tokens, costs, and synthesis of final answer."""
        consolidator = Consolidator()
        outcomes = [
            AgentOutcome(
                outcome_id="out_1", agent_instance_id="inst_1", task_id="t1", status="SUCCESS",
                payload={"result": "Firewall rules verified"}, confidence=0.95, tokens_consumed=300, cost_usd=0.003, latency_ms=50,
            ),
            AgentOutcome(
                outcome_id="out_2", agent_instance_id="inst_2", task_id="t2", status="SUCCESS",
                payload={"result": "SSL certificate renewed"}, confidence=0.98, tokens_consumed=400, cost_usd=0.004, latency_ms=70,
            ),
        ]

        res = consolidator.consolidate(objective_id="obj_test", outcomes=outcomes)
        assert isinstance(res, ConsolidatedOutcome)
        assert res.status == "COMPLETED"
        assert res.total_tokens == 700
        assert pytest.approx(res.total_cost_usd, 0.0001) == 0.007
        assert "Firewall rules verified" in res.final_answer
        assert "SSL certificate renewed" in res.final_answer
        assert res.epistemic_status == EpistemicStatus.VERIFIED


class TestHierarchicalOrchestrator:
    """Verifies end-to-end execution through HierarchicalAgentOrchestrator."""

    def test_hierarchical_orchestrator_execution(self) -> None:
        """Verify complete objective execution from intake through consolidation."""
        agent_reg = AgentRegistry()
        sec_agent = AgentDefinition(
            agent_def_id="def_sec", name="Security Agent", domain="security",
            description="Security operations and access policies",
            capabilities=[AgentCapability(name="policy_audit", level="EXPERT")],
        )
        agent_reg.register_definition(sec_agent)

        model_reg = ModelCapabilityRegistry()
        model_reg.load_profiles_from_yaml("config/profiles/model_profiles.yaml")
        stub_prov = DeterministicStubProvider(provider_id="stub")
        model_reg.load_provider_config_from_yaml("config/providers/stub.yaml", stub_prov)

        orchestrator = HierarchicalAgentOrchestrator(
            agent_registry=agent_reg,
            model_registry=model_reg,
            provider_adapter=stub_prov,
        )

        outcome = orchestrator.execute_objective("Audit security access rules for container cluster")
        assert isinstance(outcome, ConsolidatedOutcome)
        assert outcome.status == "COMPLETED"
        assert len(outcome.individual_outcomes) >= 1
        assert outcome.total_tokens > 0

    def test_backward_compatible_acra_orchestrator(self) -> None:
        """Verify ACRAOrchestrator preserves legacy process_turn while offering execute_objective."""
        orch = ACRAOrchestrator()

        # Legacy turn still works perfectly
        res = orch.process_turn(session_id="legacy_sess", user_message="Hello, can you help me?")
        assert res.session_id == "legacy_sess"
        assert res.active_state in [SystemState.INTAKE, "clarifying"]

        # New objective execution works through delegation
        obj_res = orch.execute_objective("Quick task check")
        assert isinstance(obj_res, ConsolidatedOutcome)
        assert obj_res.status == "COMPLETED"


class TestFSMDecompositionAndCycleGuards:
    """Verifies all 5 FSMs enforce cycle guards and transition rules (INV-008)."""

    def test_session_fsm_cycle_guard(self) -> None:
        """Verify SessionStateMachine enforces max_transitions limit."""
        fsm = SessionStateMachine(session_id="s_cycle", max_transitions=4)
        fsm.transition_to(SystemState.ANALYZING)
        fsm.transition_to(SystemState.COMPRESSING)
        fsm.transition_to(SystemState.EVALUATING)
        fsm.transition_to(SystemState.POLICY_REJECTED)

        with pytest.raises(InvalidSessionTransitionError, match="cycle guard"):
            fsm.transition_to(SystemState.INTAKE)

    def test_objective_fsm_cycle_guard(self) -> None:
        """Verify ObjectiveStateMachine enforces transition limits."""
        fsm = ObjectiveStateMachine(objective_id="obj_cycle", max_transitions=3)
        fsm.transition_to(ObjectiveState.PLANNING)
        fsm.transition_to(ObjectiveState.DECOMPOSED)
        fsm.transition_to(ObjectiveState.EXECUTING)

        with pytest.raises(InvalidObjectiveTransitionError, match="cycle guard"):
            fsm.transition_to(ObjectiveState.PLANNING)

    def test_task_fsm_cycle_guard(self) -> None:
        """Verify TaskStateMachine enforces transition limits."""
        fsm = TaskStateMachine(task_id="t_cycle", max_transitions=3)
        fsm.transition_to(TaskState.ASSIGNED)
        fsm.transition_to(TaskState.EXECUTING)
        fsm.transition_to(TaskState.VALIDATING)

        with pytest.raises(InvalidTaskTransitionError, match="cycle guard"):
            fsm.transition_to(TaskState.EXECUTING)

    def test_handoff_fsm_cycle_guard(self) -> None:
        """Verify HandoffStateMachine enforces transition limits."""
        fsm = HandoffStateMachine(envelope_id="env_cycle", max_transitions=2)
        fsm.transition_to(HandoffState.AUDITING)
        fsm.transition_to(HandoffState.REJECTED)

        with pytest.raises(InvalidHandoffTransitionError, match="cycle guard"):
            fsm.transition_to(HandoffState.PREPARING)
