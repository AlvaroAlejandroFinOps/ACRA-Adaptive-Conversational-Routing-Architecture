"""ACRA Tool Authorization Gate.

Enforces tool security boundaries:
- Agent whitelist verification via ToolGrant (INV-007).
- Plan vs Execute role separation (planners cannot execute mutations).
- Parameter whitelist validation.
- Per-task rate/invocation limits.
- Destructive operation interception and human sign-off gating.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from src.core.contracts.agent import AgentDefinition, AgentInstance
from src.core.contracts.governance import ToolGrant


class ToolAuthorizationResult(BaseModel):
    """Result of a tool invocation authorization check."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    is_authorized: bool = Field(..., description="Whether invocation is authorized to proceed")
    requires_approval: bool = Field(default=False, description="Whether explicit human signoff is needed (INV-007)")
    reason: str = Field(default="", description="Detailed reason for decision or rejection")
    violations: list[str] = Field(default_factory=list, description="Specific security rule violations")
    sanitized_parameters: dict[str, Any] = Field(default_factory=dict, description="Validated parameters")


class ToolAuthorizationGate:
    """Evaluates agent tool invocation requests against whitelist grants and safety policies."""

    DESTRUCTIVE_NAME_PATTERNS = {"delete", "drop", "truncate", "rm", "kill", "purge", "revoke", "format"}

    def __init__(self) -> None:
        # In-memory tracking of tool invocations per (instance_id, tool_name)
        self._invocation_counts: dict[tuple[str, str], int] = {}

    def reset_task_counters(self, instance_id: str | None = None) -> None:
        """Reset invocation counters for an instance or globally."""
        if instance_id is None:
            self._invocation_counts.clear()
        else:
            keys_to_del = [k for k in self._invocation_counts if k[0] == instance_id]
            for k in keys_to_del:
                del self._invocation_counts[k]

    def authorize(
        self,
        instance: AgentInstance,
        definition: AgentDefinition,
        tool_name: str,
        parameters: dict[str, Any] | None = None,
        is_planner_role: bool = False,
    ) -> ToolAuthorizationResult:
        """Verify whether an agent instance is authorized to invoke a tool."""
        params = parameters or {}
        violations: list[str] = []

        # 1. Whitelist check: locate matching ToolGrant in agent definition
        matching_grant: ToolGrant | None = None
        for grant in definition.tool_grants:
            if grant.tool_name == tool_name or grant.tool_name == "*":
                matching_grant = grant
                break

        if matching_grant is None:
            return ToolAuthorizationResult(
                is_authorized=False,
                requires_approval=False,
                reason=f"Tool '{tool_name}' is not in agent '{definition.agent_def_id}' whitelist",
                violations=["unauthorized_tool"],
                sanitized_parameters=params,
            )

        # 2. Plan vs Execute separation check
        # Planners are strictly forbidden from invoking destructive or state-mutating tools
        if is_planner_role:
            is_mutation = (
                matching_grant.is_destructive
                or any(pattern in tool_name.lower() for pattern in self.DESTRUCTIVE_NAME_PATTERNS)
            )
            if is_mutation:
                return ToolAuthorizationResult(
                    is_authorized=False,
                    requires_approval=False,
                    reason=f"Plan/Execute Separation: Planner agent '{definition.agent_def_id}' cannot execute mutating tool '{tool_name}'",
                    violations=["plan_execute_separation_violation"],
                    sanitized_parameters=params,
                )

        # 3. Rate / Invocation limit check
        counter_key = (instance.instance_id, tool_name)
        current_count = self._invocation_counts.get(counter_key, 0)
        if current_count >= matching_grant.max_invocations_per_task:
            return ToolAuthorizationResult(
                is_authorized=False,
                requires_approval=False,
                reason=f"Tool '{tool_name}' exceeded max invocations ({matching_grant.max_invocations_per_task}) for instance '{instance.instance_id}'",
                violations=["max_invocations_exceeded"],
                sanitized_parameters=params,
            )

        # 4. Parameter whitelist verification
        if matching_grant.allowed_parameters:
            disallowed_params = [p for p in params.keys() if p not in matching_grant.allowed_parameters]
            if disallowed_params:
                return ToolAuthorizationResult(
                    is_authorized=False,
                    requires_approval=False,
                    reason=f"Parameters {disallowed_params} not permitted for tool '{tool_name}'",
                    violations=["disallowed_parameters"],
                    sanitized_parameters=params,
                )

        # 5. Destructive action checks (INV-007)
        is_destructive = matching_grant.is_destructive or any(
            pattern in tool_name.lower() for pattern in self.DESTRUCTIVE_NAME_PATTERNS
        )
        requires_approval = matching_grant.requires_approval or is_destructive

        # Record invocation count
        self._invocation_counts[counter_key] = current_count + 1

        return ToolAuthorizationResult(
            is_authorized=True,
            requires_approval=requires_approval,
            reason="Destructive operation requires human signoff (INV-007)" if requires_approval else "Tool authorized",
            violations=[],
            sanitized_parameters=params,
        )
