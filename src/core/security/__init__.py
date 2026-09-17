"""ACRA Security and Governance Gates Package.

Exports security gates, authorization policies, and concurrency managers:
- HandoffPolicyGate (pre/post audit, sanitization, policy modes, reversible escalation)
- ToolAuthorizationGate (whitelisting, parameter checking, plan/execute separation)
- OptimisticLockManager, VersionConflictError (concurrency and idempotency control)
"""

from src.core.security.handoff_policy_gate import (
    HandoffPolicyGate,
    HandoffSecurityError,
)
from src.core.security.tool_authorization import (
    ToolAuthorizationGate,
    ToolAuthorizationResult,
)
from src.core.security.concurrency_control import (
    OptimisticLockManager,
    VersionConflictError,
)

__all__ = [
    "HandoffPolicyGate",
    "HandoffSecurityError",
    "ToolAuthorizationGate",
    "ToolAuthorizationResult",
    "OptimisticLockManager",
    "VersionConflictError",
]
