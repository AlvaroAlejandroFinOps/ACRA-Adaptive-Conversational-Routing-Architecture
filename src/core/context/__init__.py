"""ACRA Context Package.

Exposes ContextEngineeringPipeline, ContextCapsuleBuilder, StablePrefixEngine,
ScopedContextRegistry, and CompactionDecisionEngine.
"""

from src.core.context.capsule import ContextCapsuleBuilder
from src.core.context.compaction import (
    CompactionAction,
    CompactionDecision,
    CompactionDecisionEngine,
)
from src.core.context.pipeline import (
    ContextEngineeringPipeline,
    PipelineStageExecutionError,
)
from src.core.context.prefix import StablePrefixEngine
from src.core.context.scoped_registry import (
    ScopeAccessError,
    ScopedContextRegistry,
)

__all__ = [
    "ContextEngineeringPipeline",
    "PipelineStageExecutionError",
    "ContextCapsuleBuilder",
    "StablePrefixEngine",
    "ScopedContextRegistry",
    "ScopeAccessError",
    "CompactionAction",
    "CompactionDecision",
    "CompactionDecisionEngine",
]
