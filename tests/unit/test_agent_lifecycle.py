"""Unit tests for ACRA Agent Registry, Agent Factory, and AgentInstanceStateMachine (Phase 4).

Verifies ephemeral instance creation, hierarchical budget cascading (INV-005),
and deterministic lifecycle transitions without infinite cycles (INV-008).
"""

from datetime import datetime, timezone, timedelta
import pytest

from src.core.agents.factory import AgentFactory
from src.core.agents.lifecycle import (
    AgentInstanceStateMachine,
    InvalidStateTransitionError,
)
from src.core.agents.registry import AgentRegistry
from src.core.contracts.agent import (
    AgentCapability,
    AgentDefinition,
    AgentInstance,
    AgentInstanceState,
    AgentPolicy,
)
from src.core.contracts.context import ContextBudget, StablePrefixDescriptor


@pytest.fixture
def sample_prefix() -> StablePrefixDescriptor:
    """Fixture providing a stable prefix descriptor."""
    return StablePrefixDescriptor(
        prefix_id="pfx_agent_test",
        content_hash="hash_pfx_123",
        system_instruction_hash="sys_h",
        tool_manifest_hash="tool_h",
    )


@pytest.fixture
def sample_definition() -> AgentDefinition:
    """Fixture providing a sample AgentDefinition."""
    return AgentDefinition(
        agent_def_id="def_security_auditor",
        name="Security Auditor Agent",
        domain="security",
        description="Audits access permissions and zero-trust policies",
        capabilities=[AgentCapability(name="policy_audit", level="EXPERT")],
        policies=[
            AgentPolicy(
                policy_id="pol_1",
                name="no_unencrypted_keys",
                rule_type="security",
                expression="keys must be hashed",
            )
        ],
        tool_grants=[],
        input_contract="json",
        output_contract="json",
        model_profile_id="validator",
        max_context_tokens=8000,
    )


class TestAgentInstanceStateMachine:
    """Verifies deterministic transitions and guard rails of AgentInstanceStateMachine."""

    def test_agent_lifecycle_happy_path(self) -> None:
        """Verify normal linear lifecycle: CREATED -> INITIALIZED -> ACTIVE -> COMPLETED -> RETIRED."""
        fsm = AgentInstanceStateMachine(instance_id="inst_001")
        assert fsm.state == AgentInstanceState.CREATED

        fsm.transition_to(AgentInstanceState.INITIALIZED, reason="Capsule loaded")
        assert fsm.state == AgentInstanceState.INITIALIZED

        fsm.transition_to(AgentInstanceState.ACTIVE, reason="Dispatched to worker")
        assert fsm.state == AgentInstanceState.ACTIVE
        assert fsm.is_active()

        fsm.transition_to(AgentInstanceState.COMPLETED, reason="Task finished successfully")
        assert fsm.state == AgentInstanceState.COMPLETED

        fsm.transition_to(AgentInstanceState.RETIRED, reason="Context unmounted")
        assert fsm.state == AgentInstanceState.RETIRED
        assert fsm.is_terminal()
        assert len(fsm.history) == 5

    def test_agent_lifecycle_suspension_and_resume(self) -> None:
        """Verify ACTIVE -> SUSPENDED -> ACTIVE state flow."""
        fsm = AgentInstanceStateMachine(instance_id="inst_002")
        fsm.transition_to(AgentInstanceState.INITIALIZED)
        fsm.transition_to(AgentInstanceState.ACTIVE)

        fsm.transition_to(AgentInstanceState.SUSPENDED, reason="Waiting on external tool")
        assert fsm.state == AgentInstanceState.SUSPENDED
        assert not fsm.is_active()

        fsm.transition_to(AgentInstanceState.ACTIVE, reason="Tool result delivered")
        assert fsm.state == AgentInstanceState.ACTIVE

    def test_agent_lifecycle_revocation(self) -> None:
        """Verify revocation immediately moves instance to terminal REVOKED state."""
        fsm = AgentInstanceStateMachine(instance_id="inst_003")
        fsm.transition_to(AgentInstanceState.INITIALIZED)
        fsm.transition_to(AgentInstanceState.ACTIVE)

        fsm.transition_to(AgentInstanceState.REVOKED, reason="Budget exceeded or security abort")
        assert fsm.state == AgentInstanceState.REVOKED
        assert fsm.is_terminal()

    def test_invalid_transitions_raise(self) -> None:
        """Verify illegal transitions raise InvalidStateTransitionError."""
        fsm = AgentInstanceStateMachine(instance_id="inst_004")
        # Cannot jump from CREATED directly to COMPLETED
        with pytest.raises(InvalidStateTransitionError, match="Illegal state transition"):
            fsm.transition_to(AgentInstanceState.COMPLETED)

        # Cannot transition out of terminal RETIRED
        fsm.transition_to(AgentInstanceState.INITIALIZED)
        fsm.transition_to(AgentInstanceState.ACTIVE)
        fsm.transition_to(AgentInstanceState.COMPLETED)
        fsm.transition_to(AgentInstanceState.RETIRED)

        with pytest.raises(InvalidStateTransitionError, match="Illegal state transition"):
            fsm.transition_to(AgentInstanceState.ACTIVE)

    def test_cycle_guard_prevents_infinite_oscillations(self) -> None:
        """Verify transition counter prevents infinite state loops (INV-008)."""
        fsm = AgentInstanceStateMachine(instance_id="inst_cycle", max_transitions=6)
        fsm.transition_to(AgentInstanceState.INITIALIZED)
        fsm.transition_to(AgentInstanceState.ACTIVE)

        # Oscillate between ACTIVE and SUSPENDED
        fsm.transition_to(AgentInstanceState.SUSPENDED)
        fsm.transition_to(AgentInstanceState.ACTIVE)
        fsm.transition_to(AgentInstanceState.SUSPENDED)
        fsm.transition_to(AgentInstanceState.ACTIVE)  # Reaches 6 transitions

        # Next transition exceeds limit and raises
        with pytest.raises(InvalidStateTransitionError, match="cycle guard"):
            fsm.transition_to(AgentInstanceState.SUSPENDED)


class TestAgentFactory:
    """Verifies AgentFactory instance generation and budget cascading (INV-005)."""

    def test_factory_creates_instance_with_budget_cascade(
        self,
        sample_definition: AgentDefinition,
        sample_prefix: StablePrefixDescriptor,
    ) -> None:
        """Verify AgentFactory cascades budget from parent and constructs isolated capsule."""
        factory = AgentFactory(default_ttl_seconds=600)
        parent_budget = ContextBudget(
            max_tokens=5000,
            max_cost_usd=0.50,
            consumed_tokens=1000,
            consumed_cost_usd=0.10,
        )

        instance, fsm = factory.create_instance(
            definition=sample_definition,
            task_objective="Audit firewall ACL rules",
            stable_prefix=sample_prefix,
            parent_budget=parent_budget,
            allocated_tokens=2000,
            allocated_cost_usd=0.20,
        )

        assert isinstance(instance, AgentInstance)
        assert instance.state == AgentInstanceState.CREATED
        assert instance.definition_id == sample_definition.agent_def_id
        assert instance.context_capsule.domain == "security"
        assert instance.context_capsule.task_context == "Audit firewall ACL rules"

        # Cascaded budget verification (INV-005)
        assert instance.budget.max_tokens == 2000
        assert instance.budget.max_cost_usd == 0.20
        assert instance.budget.consumed_tokens == 0

        # FSM verification
        assert isinstance(fsm, AgentInstanceStateMachine)
        assert fsm.state == AgentInstanceState.CREATED

    def test_agent_expiration_ttl(
        self,
        sample_definition: AgentDefinition,
        sample_prefix: StablePrefixDescriptor,
    ) -> None:
        """Verify agent TTL expiration logic."""
        factory = AgentFactory(default_ttl_seconds=10)
        instance, _ = factory.create_instance(
            definition=sample_definition,
            task_objective="Short lived check",
            stable_prefix=sample_prefix,
            ttl_seconds=10,
        )

        now = datetime.now(timezone.utc)
        assert not instance.is_expired(current_time=now)

        future = now + timedelta(seconds=20)
        assert instance.is_expired(current_time=future)


class TestAgentRegistry:
    """Verifies AgentRegistry storage, queries, and domain filtering."""

    def test_registry_register_and_filter(self, sample_definition: AgentDefinition) -> None:
        """Verify registry stores and filters definitions by domain."""
        registry = AgentRegistry()
        registry.register_definition(sample_definition)

        # Definition in legal domain
        legal_def = AgentDefinition(
            agent_def_id="def_legal_advisor",
            name="Legal Advisor",
            domain="legal",
            description="Reviews legal compliance",
        )
        registry.register_definition(legal_def)

        assert registry.get_definition("def_security_auditor") is not None
        assert registry.get_definition("def_legal_advisor") is not None

        # Filter by domain
        security_defs = registry.list_definitions(domain="security")
        assert len(security_defs) == 1
        assert security_defs[0].agent_def_id == "def_security_auditor"

        legal_defs = registry.list_definitions(domain="legal")
        assert len(legal_defs) == 1
        assert legal_defs[0].agent_def_id == "def_legal_advisor"

        all_defs = registry.list_definitions()
        assert len(all_defs) == 2
