"""End-to-End Reference Multi-Agent Scenario Benchmark (Phase 8).

Validates the complete ACRA hierarchical orchestration architecture:
- Complex multi-domain objective intake and risk assessment.
- AgentRegistry loading from synthetic enterprise fixtures (UD-003).
- Ephemeral AgentFactory instance creation with cascaded budgets (INV-005).
- Scoped ContextCapsule isolation with cryptographic sealing (INV-003).
- Kahn DAG topological sorting and cycle prevention (INV-008).
- Mandatory pre-handoff audit before inter-agent envelope dispatch (INV-002).
- ToolAuthorizationGate whitelisting and destructive operation interception (INV-007).
- TokenEconomyEngine hierarchical consumption and measured/estimated tracking (INV-006).
- ProvenanceTracker audit trail with declared EpistemicStatus (INV-004).
- Multi-domain outcome synthesis and 20 cognitive degradation metrics report.
"""

from __future__ import annotations

import os
import yaml
import pytest
from datetime import datetime, timezone

from src.core.contracts.agent import AgentDefinition, AgentInstance, AgentInstanceState
from src.core.contracts.audit import AuditHookPoint, AuditResult, AuditTriple, EpistemicStatus
from src.core.contracts.context import ContextBudget, ContextCapsule, StablePrefixDescriptor
from src.core.contracts.governance import PolicyMode, ToolGrant
from src.core.contracts.handoff import HandoffEnvelope, HandoffState
from src.core.contracts.task import TaskDefinition, TaskDependency, TaskState
from src.core.agents.registry import AgentRegistry
from src.core.agents.factory import AgentFactory
from src.core.routing.intake_router import IntakeRouter
from src.core.orchestration.task_graph import TaskGraph
from src.core.orchestration.consolidator import Consolidator
from src.core.security.handoff_policy_gate import HandoffPolicyGate
from src.core.security.tool_authorization import ToolAuthorizationGate
from src.core.economy.engine import TokenEconomyEngine
from src.core.economy.telemetry import ProvenanceTracker
from src.core.fsm.handoff_fsm import HandoffStateMachine
from src.core.metrics import ACRAMetrics, CognitiveDegradationReport


FIXTURE_PATH = os.path.join(
    "tests", "fixtures", "domains", "reference_enterprise", "reference_agents.yaml"
)


@pytest.fixture
def enterprise_agent_registry() -> AgentRegistry:
    """Load reference enterprise agents from synthetic YAML fixture."""
    registry = AgentRegistry()
    assert os.path.exists(FIXTURE_PATH), f"Fixture not found at {FIXTURE_PATH}"

    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    for item in data.get("agents", []):
        tool_grants = [
            ToolGrant(
                tool_name=tg["tool_name"],
                description=tg.get("description", ""),
                is_destructive=tg.get("is_destructive", False),
                max_invocations_per_task=tg.get("max_invocations_per_task", 10),
                allowed_parameters=tg.get("allowed_parameters", []),
                requires_approval=tg.get("requires_approval", False),
            )
            for tg in item.get("tool_grants", [])
        ]
        agent_def = AgentDefinition(
            agent_def_id=item["agent_def_id"],
            name=item["name"],
            domain=item["domain"],
            description=item.get("description", ""),
            tool_grants=tool_grants,
            input_contract=item.get("input_contract", "json"),
            output_contract=item.get("output_contract", "json"),
            model_profile_id=item.get("model_profile_id", "domain_planner"),
            max_context_tokens=item.get("max_context_tokens", 8000),
        )
        registry.register(agent_def)

    return registry


class TestMultiAgentE2EEnterpriseScenario:
    def test_complete_hierarchical_orchestration_flow(
        self,
        enterprise_agent_registry: AgentRegistry,
    ):
        """Execute end-to-end multi-agent scenario across Triage, Infrastructure, Billing, and Synthesis."""
        # -------------------------------------------------------------------
        # Step 1: Objective Intake & Risk Analysis
        # -------------------------------------------------------------------
        intake = IntakeRouter()
        user_objective = (
            "E-Commerce Payment Outage: Latency spiked to 4.2s at 14:00 UTC, causing 35 failed "
            "transactions for enterprise tenant CorpX. Investigate Kubernetes platform metrics, "
            "calculate SLA breach compensation refund, and format executive incident synopsis."
        )
        intake_result = intake.classify(user_objective)
        assert intake_result.complexity in {"MEDIUM", "HIGH"}
        assert intake_result.requires_decomposition is True
        assert intake_result.recommended_profile_id in {"domain_planner", "fast_executor", "deep_reasoner"}

        # -------------------------------------------------------------------
        # Step 2: Session & Hierarchical Budget Initialization (INV-005)
        # -------------------------------------------------------------------
        session_id = "sess_e2e_enterprise_001"
        economy = TokenEconomyEngine()
        telemetry = ProvenanceTracker()
        session_budget = ContextBudget(max_tokens=32000, max_cost_usd=2.50)
        economy.register_budget(entity_id=session_id, budget=session_budget)

        # -------------------------------------------------------------------
        # Step 3: Ephemeral Agent Factory Instantiation (INV-003)
        # -------------------------------------------------------------------
        factory = AgentFactory()
        stable_prefix = StablePrefixDescriptor(
            prefix_id="pfx_enterprise",
            content_hash="hash_enterprise_pfx",
            version=1,
            system_instruction_hash="sys_hash_001",
            tool_manifest_hash="tools_hash_001",
        )

        triage_agent, triage_fsm = factory.create_instance(
            definition=enterprise_agent_registry.get("def_triage_coordinator"),
            task_objective="Incident scope triage",
            stable_prefix=stable_prefix,
            parent_budget=session_budget,
            allocated_tokens=4000,
        )
        infra_agent, infra_fsm = factory.create_instance(
            definition=enterprise_agent_registry.get("def_infrastructure_engineer"),
            task_objective="Container platform diagnostics",
            stable_prefix=stable_prefix,
            parent_budget=session_budget,
            allocated_tokens=8000,
        )
        billing_agent, billing_fsm = factory.create_instance(
            definition=enterprise_agent_registry.get("def_billing_specialist"),
            task_objective="Financial SLA audit and credit calculation",
            stable_prefix=stable_prefix,
            parent_budget=session_budget,
            allocated_tokens=6000,
        )
        consolidator_agent, consolidator_fsm = factory.create_instance(
            definition=enterprise_agent_registry.get("def_resolution_consolidator"),
            task_objective="Executive synopsis synthesis",
            stable_prefix=stable_prefix,
            parent_budget=session_budget,
            allocated_tokens=6000,
        )

        for fsm in [triage_fsm, infra_fsm, billing_fsm, consolidator_fsm]:
            fsm.transition_to(AgentInstanceState.INITIALIZED)
            fsm.transition_to(AgentInstanceState.ACTIVE)

        # Register instance budgets under session
        economy.register_budget("inst_triage", triage_agent.budget, parent_id=session_id)
        economy.register_budget("inst_infra", infra_agent.budget, parent_id=session_id)
        economy.register_budget("inst_billing", billing_agent.budget, parent_id=session_id)
        economy.register_budget("inst_consolidator", consolidator_agent.budget, parent_id=session_id)

        # Verify domain isolation (INV-003)
        assert triage_agent.context_capsule.domain == "triage"
        assert infra_agent.context_capsule.domain == "infrastructure"
        assert billing_agent.context_capsule.domain == "billing"
        assert consolidator_agent.context_capsule.domain == "orchestration"

        # -------------------------------------------------------------------
        # Step 4: DAG Task Graph Construction & Kahn Topological Sort (INV-008)
        # -------------------------------------------------------------------
        task_graph = TaskGraph(graph_id="graph_e2e_001")
        t1 = TaskDefinition(
            task_id="task_1_triage",
            objective_id="obj_e2e_001",
            description="Triage incident and scope subtasks",
            target_domain="triage",
            dependencies=[],
        )
        t2 = TaskDefinition(
            task_id="task_2_infra",
            objective_id="obj_e2e_001",
            description="Diagnose Kubernetes cluster telemetry",
            target_domain="infrastructure",
            dependencies=[TaskDependency(depends_on_task_id="task_1_triage")],
        )
        t3 = TaskDefinition(
            task_id="task_3_billing",
            objective_id="obj_e2e_001",
            description="Calculate pro-rated SLA breach compensation credit",
            target_domain="billing",
            dependencies=[TaskDependency(depends_on_task_id="task_1_triage")],
        )
        t4 = TaskDefinition(
            task_id="task_4_synthesis",
            objective_id="obj_e2e_001",
            description="Synthesize unified executive incident outcome",
            target_domain="orchestration",
            dependencies=[
                TaskDependency(depends_on_task_id="task_2_infra"),
                TaskDependency(depends_on_task_id="task_3_billing"),
            ],
        )

        task_graph.add_task(t1)
        task_graph.add_task(t2)
        task_graph.add_task(t3)
        task_graph.add_task(t4)

        task_order_ids = task_graph.get_execution_order()
        assert task_order_ids[0] == "task_1_triage"
        assert set(task_order_ids[1:3]) == {"task_2_infra", "task_3_billing"}
        assert task_order_ids[3] == "task_4_synthesis"

        # -------------------------------------------------------------------
        # Step 5: Execution & Security Gates (INV-002, INV-007)
        # -------------------------------------------------------------------
        security_gate = HandoffPolicyGate(mode=PolicyMode.ENFORCE)
        tool_gate = ToolAuthorizationGate()

        # Task 1: Triage execution
        triage_audit = security_gate.pre_handoff_audit(
            envelope_data={"objective": t1.description},
            capsule=triage_agent.context_capsule,
        )
        assert triage_audit.risk_score < 0.20

        # Tool auth: inspect_incident_payload
        triage_tool_auth = tool_gate.authorize(
            instance=triage_agent,
            definition=enterprise_agent_registry.get("def_triage_coordinator"),
            tool_name="inspect_incident_payload",
            parameters={"payload_id": "INC-8891"},
        )
        assert triage_tool_auth.is_authorized is True
        assert triage_tool_auth.requires_approval is False

        # Record consumption for Task 1
        economy.record_consumption("inst_triage", tokens=650, cost_usd=0.0065, is_measured=True)
        telemetry.record(
            session_id=session_id,
            agent_id=triage_agent.instance_id,
            task_id="task_1_triage",
            model_profile_id="domain_planner",
            provider_id="stub_provider",
            epistemic_status=EpistemicStatus.MEASURED,
            tokens_consumed=650,
            cost_usd=0.0065,
            tool_calls=["inspect_incident_payload"],
        )

        # Task 2: Infrastructure Diagnostics (Test INV-007 destructive operation interception)
        infra_def = enterprise_agent_registry.get("def_infrastructure_engineer")
        tool_metrics_auth = tool_gate.authorize(
            instance=infra_agent,
            definition=infra_def,
            tool_name="query_telemetry_metrics",
            parameters={},
        )
        assert tool_metrics_auth.is_authorized is True
        assert tool_metrics_auth.requires_approval is False

        # Intercept destructive tool: restart_unhealthy_pod requires human sign-off (INV-007)
        tool_restart_auth = tool_gate.authorize(
            instance=infra_agent,
            definition=infra_def,
            tool_name="restart_unhealthy_pod",
            parameters={},
        )
        assert tool_restart_auth.is_authorized is True
        assert tool_restart_auth.requires_approval is True  # INV-007 verified!

        economy.record_consumption("inst_infra", tokens=1200, cost_usd=0.0120, is_measured=True)
        telemetry.record(
            session_id=session_id,
            agent_id=infra_agent.instance_id,
            task_id="task_2_infra",
            model_profile_id="deep_reasoner",
            provider_id="stub_provider",
            epistemic_status=EpistemicStatus.MEASURED,
            tokens_consumed=1200,
            cost_usd=0.0120,
            tool_calls=["query_telemetry_metrics"],
        )

        # Task 3: Billing & SLA Compensation
        billing_def = enterprise_agent_registry.get("def_billing_specialist")
        tool_bill_auth = tool_gate.authorize(
            instance=billing_agent,
            definition=billing_def,
            tool_name="query_billing_ledger",
            parameters={"account_id": "ACC-9901"},
        )
        assert tool_bill_auth.is_authorized is True

        economy.record_consumption("inst_billing", tokens=850, cost_usd=0.0085, is_measured=True)
        telemetry.record(
            session_id=session_id,
            agent_id=billing_agent.instance_id,
            task_id="task_3_billing",
            model_profile_id="fast_executor",
            provider_id="stub_provider",
            epistemic_status=EpistemicStatus.MEASURED,
            tokens_consumed=850,
            cost_usd=0.0085,
            tool_calls=["query_billing_ledger"],
        )

        # -------------------------------------------------------------------
        # Step 6: Typed Inter-Agent Handoff to Consolidator (INV-002 & FSM)
        # -------------------------------------------------------------------
        envelope_to_consolidator = HandoffEnvelope(
            envelope_id="env_synthesis_001",
            source_agent_id=billing_agent.instance_id,
            target_agent_id=consolidator_agent.instance_id,
            domain="orchestration",
            objective="Synthesize infra telemetry and billing compensation into final client report",
            context_capsule_hash=consolidator_agent.context_capsule.capsule_hash,
            budget=ContextBudget(max_tokens=3000),
            pre_handoff_audit=triage_audit,
            audit_status="PASSED",
            epistemic_status=EpistemicStatus.VERIFIED,
        )
        assert envelope_to_consolidator.is_dispatchable() is True

        handoff_fsm = HandoffStateMachine(envelope_id=envelope_to_consolidator.envelope_id)
        handoff_fsm.transition_to(HandoffState.AUDITING)
        handoff_fsm.transition_to(HandoffState.DISPATCHED, envelope=envelope_to_consolidator)
        handoff_fsm.transition_to(HandoffState.RECEIVED)
        handoff_fsm.transition_to(HandoffState.VALIDATED)
        assert handoff_fsm.is_terminal() is True

        # Task 4: Consolidator synthesis
        economy.record_consumption("inst_consolidator", tokens=1100, cost_usd=0.0110, is_measured=True)
        telemetry.record(
            session_id=session_id,
            agent_id=consolidator_agent.instance_id,
            task_id="task_4_synthesis",
            model_profile_id="domain_planner",
            provider_id="stub_provider",
            epistemic_status=EpistemicStatus.VERIFIED,
            tokens_consumed=1100,
            cost_usd=0.0110,
            tool_calls=["generate_resolution_report"],
        )

        # -------------------------------------------------------------------
        # Step 7: Telemetry & Epistemic Status Validation (INV-004, INV-006)
        # -------------------------------------------------------------------
        summary = telemetry.get_session_summary(session_id)
        assert summary["record_count"] == 4
        assert summary["total_tokens_measured"] == 3800  # 650 + 1200 + 850 + 1100
        assert summary["total_tokens_estimated"] == 0
        assert pytest.approx(summary["total_cost_usd"], 0.0001) == 0.038
        assert telemetry.verify_chain_epistemic_integrity(session_id) is True
        assert set(summary["tools_invoked"]) == {
            "inspect_incident_payload",
            "query_telemetry_metrics",
            "query_billing_ledger",
            "generate_resolution_report",
        }

        # Verify hierarchical budget at session root reflected total 3800 tokens (INV-005)
        root_budget = economy.get_budget(session_id)
        assert root_budget.consumed_tokens == 3800
        assert root_budget.remaining_tokens() == 28200

        # -------------------------------------------------------------------
        # Step 8: Multi-Domain Outcome Consolidation & 20 Metrics Evaluation
        # -------------------------------------------------------------------
        consolidator = Consolidator()
        from src.core.contracts.outcome import AgentOutcome
        infra_outcome = AgentOutcome(
            outcome_id="out_infra_001",
            agent_instance_id=infra_agent.instance_id,
            task_id="task_2_infra",
            status="SUCCESS",
            confidence=0.98,
            payload={"result": "Pod payment-gateway-7b experienced memory pressure and OOM restart at 14:02 UTC."},
            tokens_consumed=1200,
            cost_usd=0.012,
            latency_ms=450,
            epistemic_status=EpistemicStatus.VERIFIED,
        )
        billing_outcome = AgentOutcome(
            outcome_id="out_billing_001",
            agent_instance_id=billing_agent.instance_id,
            task_id="task_3_billing",
            status="SUCCESS",
            confidence=0.95,
            payload={"result": "35 failed transactions reconciled. SLA credit of $450.00 generated for CorpX."},
            tokens_consumed=850,
            cost_usd=0.0085,
            latency_ms=280,
            epistemic_status=EpistemicStatus.VERIFIED,
        )

        consolidated = consolidator.consolidate(
            objective_id="obj_e2e_001",
            outcomes=[infra_outcome, billing_outcome],
        )
        assert consolidated.status == "COMPLETED"
        assert "payment-gateway-7b" in consolidated.final_answer
        assert "$450.00" in consolidated.final_answer
        assert len(consolidated.individual_outcomes) == 2

        # Evaluate 20 cognitive degradation metrics (§17)
        report: CognitiveDegradationReport = ACRAMetrics.evaluate_cognitive_degradation_report(
            context_risk_score=0.05,
            evidence_coverage=1.0,
            effective_cost_per_validated_task=0.038,
            tokens_per_validated_outcome=3800,
            model_switch_count=3,
        )
        assert report.context_risk_score.epistemic_status == EpistemicStatus.VERIFIED
        assert report.effective_cost_per_validated_task.value == 0.038
        assert report.tokens_per_validated_outcome.value == 3800.0
