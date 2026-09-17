"""Unit tests for ACRA typed contracts (Phase 1).

Validates Pydantic v2 schemas, roundtrip serialization, and invariant enforcement.
"""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from src.core.contracts.agent import (
    AgentCapability,
    AgentDefinition,
    AgentInstance,
    AgentInstanceState,
    AgentPolicy,
)
from src.core.contracts.audit import (
    AuditHookPoint,
    AuditResult,
    AuditTriple,
    ContextAuditProvider,
    DimensionScore,
    EpistemicStatus,
    Finding,
    FindingSeverity,
)
from src.core.contracts.cache import (
    AgentModelAffinity,
    CacheCapabilityProfile,
    CacheContinuityDescriptor,
    CacheInvalidationEvent,
    CacheObservabilityLevel,
    ContextRehydrationPlan,
    ContextReuseEstimate,
    ModelMigrationDecision,
    ModelSessionLease,
)
from src.core.contracts.context import (
    ContextBudget,
    ContextCapsule,
    StablePrefixDescriptor,
    ToolResult,
)
from src.core.contracts.governance import (
    ExecutionEvidence,
    PolicyMode,
    ToolGrant,
    ValidationResult,
)
from src.core.contracts.graph import (
    AgentGraph,
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
)
from src.core.contracts.handoff import (
    EscalationPolicy,
    HandoffEnvelope,
    HandoffState,
)
from src.core.contracts.model import (
    CapabilityVector,
    ModelProfile,
    ModelSelectionDecision,
    ProviderProfile,
)
from src.core.contracts.outcome import (
    AgentOutcome,
    ConsolidatedOutcome,
)
from src.core.contracts.task import (
    DependencyType,
    TaskDefinition,
    TaskDependency,
    TaskExecution,
    TaskState,
)


class TestContextContracts:
    """Test ContextCapsule, ContextBudget, and StablePrefixDescriptor."""

    def test_budget_exhaustion_and_remaining(self) -> None:
        """Verify ContextBudget calculates remaining tokens and cost correctly (INV-005)."""
        budget = ContextBudget(
            max_tokens=1000,
            max_turns=5,
            max_cost_usd=0.10,
            consumed_tokens=400,
            consumed_cost_usd=0.04,
        )
        assert budget.remaining_tokens() == 600
        assert pytest.approx(budget.remaining_cost_usd(), 0.001) == 0.06
        assert not budget.is_exhausted()

        exhausted_tokens = ContextBudget(
            max_tokens=1000,
            max_turns=5,
            max_cost_usd=0.10,
            consumed_tokens=1000,
            consumed_cost_usd=0.04,
        )
        assert exhausted_tokens.is_exhausted()

    def test_capsule_fork_isolation(self) -> None:
        """Verify ContextCapsule.fork() inherits only authorized context (INV-003, INV-009)."""
        prefix = StablePrefixDescriptor(
            prefix_id="pfx_1",
            content_hash="abc123hash",
            version=1,
            token_count=150,
            system_instruction_hash="sys_hash",
            tool_manifest_hash="tool_hash",
        )
        tool_result = ToolResult(
            tool_name="db_query",
            call_id="c_1",
            status="SUCCESS",
            content="Sensitive secret row data",
            content_hash="res_hash",
        )
        parent_capsule = ContextCapsule(
            capsule_id="cap_parent_001",
            agent_instance_id="inst_parent",
            domain="finance",
            stable_prefix=prefix,
            domain_context="Confidential budget allocation formula",
            task_context="Calculate quarterly taxes",
            volatile_tool_state=[tool_result],
            current_turn="User: What is the bottom line?",
            output_contract="json",
            capsule_hash="parenthash123",
        )

        forked = parent_capsule.fork(
            new_instance_id="inst_child",
            new_domain="legal",
            whitelisted_task_context="Review contract compliance clause 4",
        )

        assert forked.agent_instance_id == "inst_child"
        assert forked.domain == "legal"
        assert forked.parent_capsule_id == "cap_parent_001"
        # Invariants: domain_context and volatile tool state are completely wiped
        assert forked.domain_context == ""
        assert len(forked.volatile_tool_state) == 0
        assert forked.current_turn == ""
        assert forked.task_context == "Review contract compliance clause 4"
        assert forked.stable_prefix == prefix


class TestAuditContracts:
    """Test AuditResult, tripleta, and Protocol."""

    def test_audit_result_serialization_and_tripleta(self) -> None:
        """Verify AuditResult tripleta properties and serialization."""
        triple = AuditTriple(risk_score=0.15, confidence=0.95, evidence_coverage=0.88)
        finding = Finding(
            finding_id="f_1",
            dimension="verbosity",
            severity=FindingSeverity.LOW,
            message="Assistant response contains conversational padding",
        )
        audit = AuditResult(
            audit_id="aud_100",
            hook_point=AuditHookPoint.PRE_INFERENCE,
            triple=triple,
            findings=[finding],
            epistemic_status=EpistemicStatus.VERIFIED,
        )

        assert audit.risk_score == 0.15
        assert audit.confidence == 0.95
        assert audit.evidence_coverage == 0.88
        assert audit.epistemic_status == EpistemicStatus.VERIFIED

        # Roundtrip JSON
        json_data = audit.model_dump_json()
        deserialized = AuditResult.model_validate_json(json_data)
        assert deserialized.audit_id == audit.audit_id
        assert deserialized.risk_score == 0.15
        assert len(deserialized.findings) == 1

    def test_context_audit_provider_protocol_check(self) -> None:
        """Verify runtime protocol check works for ContextAuditProvider."""
        class MockAuditor:
            def audit(self, context_payload: object, hook_point: AuditHookPoint) -> AuditResult:
                return AuditResult(
                    audit_id="dummy",
                    hook_point=hook_point,
                    triple=AuditTriple(risk_score=0.0, confidence=1.0, evidence_coverage=1.0),
                    epistemic_status=EpistemicStatus.STUB,
                )

            def get_supported_dimensions(self) -> list[str]:
                return ["mock_dimension"]

            def health_check(self) -> bool:
                return True

        auditor = MockAuditor()
        assert isinstance(auditor, ContextAuditProvider)


class TestHandoffContracts:
    """Test HandoffEnvelope and pre-handoff audit dispatchability (INV-002)."""

    def test_handoff_envelope_dispatchable_when_audit_passes(self) -> None:
        """Handoff is dispatchable only when audit passes and risk is within threshold."""
        safe_audit = AuditResult(
            audit_id="aud_safe",
            hook_point=AuditHookPoint.PRE_HANDOFF,
            triple=AuditTriple(risk_score=0.2, confidence=0.9, evidence_coverage=0.9),
            epistemic_status=EpistemicStatus.VERIFIED,
        )
        budget = ContextBudget(max_tokens=4000)
        envelope = HandoffEnvelope(
            envelope_id="env_1",
            source_agent_id="agent_planner",
            target_agent_id="agent_executor",
            domain="operations",
            objective="Deploy hotfix container",
            context_capsule_hash="hash_capsule_123",
            budget=budget,
            pre_handoff_audit=safe_audit,
            audit_status="PASSED",
        )
        assert envelope.is_dispatchable()

    def test_handoff_envelope_blocks_high_risk(self) -> None:
        """Handoff blocks if risk_score > 0.8 or audit status is REJECTED (INV-002)."""
        risky_audit = AuditResult(
            audit_id="aud_risky",
            hook_point=AuditHookPoint.PRE_HANDOFF,
            triple=AuditTriple(risk_score=0.85, confidence=0.9, evidence_coverage=0.7),
            epistemic_status=EpistemicStatus.VERIFIED,
        )
        envelope = HandoffEnvelope(
            envelope_id="env_2",
            source_agent_id="agent_planner",
            target_agent_id="agent_executor",
            domain="security",
            objective="Delete audit logs",
            context_capsule_hash="hash_capsule_456",
            budget=ContextBudget(max_tokens=2000),
            pre_handoff_audit=risky_audit,
            audit_status="PASSED",
        )
        assert not envelope.is_dispatchable()


class TestAgentAndTaskContracts:
    """Test AgentDefinition, AgentInstance, and Task contracts."""

    def test_agent_instance_expiration(self) -> None:
        """Verify AgentInstance tracks TTL expiration correctly."""
        now = datetime.now(timezone.utc)
        prefix = StablePrefixDescriptor(
            prefix_id="pfx_1",
            content_hash="h1",
            system_instruction_hash="h2",
            tool_manifest_hash="h3",
        )
        capsule = ContextCapsule(
            capsule_id="c_1",
            agent_instance_id="inst_1",
            domain="general",
            stable_prefix=prefix,
        )
        instance = AgentInstance(
            instance_id="inst_1",
            definition_id="def_agent_test",
            state=AgentInstanceState.ACTIVE,
            context_capsule=capsule,
            budget=ContextBudget(max_tokens=5000),
            created_at=now,
            expires_at=now,
        )
        assert instance.is_expired(current_time=now)


class TestCacheContracts:
    """Test CacheContinuityDescriptor, Affinity, and Invariant validation."""

    def test_cache_continuity_descriptor_serialization(self) -> None:
        """Verify CacheContinuityDescriptor serialization and fields."""
        desc = CacheContinuityDescriptor(
            provider_id="google",
            model_profile_id="frontier_planner",
            concrete_model_id="gemini-2.5-pro",
            session_id="sess_123",
            agent_instance_id="inst_456",
            stable_prefix_hash="prefix_hash_abc",
            system_instruction_hash="sys_hash_abc",
            tool_manifest_hash="tools_hash_abc",
            context_capsule_hash="capsule_hash_abc",
            reported_cached_tokens=1500,
            reported_uncached_tokens=250,
            observability_level=CacheObservabilityLevel.FULL_TELEMETRY,
            epistemic_status=EpistemicStatus.VERIFIED,
        )
        dump = desc.model_dump()
        assert dump["provider_id"] == "google"
        assert dump["reported_cached_tokens"] == 1500
        assert dump["epistemic_status"] == "VERIFIED"


class TestSchemaStrictness:
    """Ensure all contract models forbid unknown extra fields."""

    def test_forbids_extra_fields(self) -> None:
        """Verify extra='forbid' raises ValidationError on arbitrary fields."""
        with pytest.raises(ValidationError):
            AgentCapability(name="coding", level="EXPERT", unknown_extra_attribute="illegal")
