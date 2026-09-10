"""
ACRA: Adaptive Conversational Routing Architecture.
Módulo central para la estabilización cognitiva en interacciones multi-turno con LLMs.
"""

__version__ = "0.1.0"
__author__ = "ACRA Research Team"

from .metrics import ACRAMetrics, MetricResult
from .edge_router import EdgeRouter, RouterDecision
from .dhc import DynamicHistoryCompressor, CompressedContext
from .unified_context import UnifiedContextTier, ContextSnapshot
from .handoff import HandoffEngine, CleanPayload
from .orchestrator import ACRAOrchestrator, OrchestratorState

__all__ = [
    "ACRAMetrics",
    "MetricResult",
    "EdgeRouter",
    "RouterDecision",
    "DynamicHistoryCompressor",
    "CompressedContext",
    "UnifiedContextTier",
    "ContextSnapshot",
    "HandoffEngine",
    "CleanPayload",
    "ACRAOrchestrator",
    "OrchestratorState",
]
