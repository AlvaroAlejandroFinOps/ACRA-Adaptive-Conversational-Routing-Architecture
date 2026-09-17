"""ACRA Contracts Package.

Exposes all typed domain models, protocols, and data contracts.
Contracts are pure Pydantic v2 models and Python Protocols with zero side-effects.
"""

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

__all__ = [
    # Agent
    "AgentCapability",
    "AgentDefinition",
    "AgentInstance",
    "AgentInstanceState",
    "AgentPolicy",
    # Audit
    "AuditHookPoint",
    "AuditResult",
    "AuditTriple",
    "ContextAuditProvider",
    "DimensionScore",
    "EpistemicStatus",
    "Finding",
    "FindingSeverity",
    # Cache
    "AgentModelAffinity",
    "CacheCapabilityProfile",
    "CacheContinuityDescriptor",
    "CacheInvalidationEvent",
    "CacheObservabilityLevel",
    "ContextRehydrationPlan",
    "ContextReuseEstimate",
    "ModelMigrationDecision",
    "ModelSessionLease",
    # Context
    "ContextBudget",
    "ContextCapsule",
    "StablePrefixDescriptor",
    "ToolResult",
    # Governance
    "ExecutionEvidence",
    "PolicyMode",
    "ToolGrant",
    "ValidationResult",
    # Graph
    "AgentGraph",
    "EdgeType",
    "GraphEdge",
    "GraphNode",
    "NodeType",
    # Handoff
    "EscalationPolicy",
    "HandoffEnvelope",
    "HandoffState",
    # Model
    "CapabilityVector",
    "ModelProfile",
    "ModelSelectionDecision",
    "ProviderProfile",
    # Outcome
    "AgentOutcome",
    "ConsolidatedOutcome",
    # Task
    "DependencyType",
    "TaskDefinition",
    "TaskDependency",
    "TaskExecution",
    "TaskState",
]
