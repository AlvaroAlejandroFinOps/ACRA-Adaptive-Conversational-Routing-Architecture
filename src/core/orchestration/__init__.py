"""ACRA Orchestration Package.

Exposes hierarchical agent orchestration, DAG task scheduling,
objective decomposition, and outcome consolidation.
"""

from src.core.orchestration.consolidator import Consolidator
from src.core.orchestration.hierarchical_orchestrator import HierarchicalAgentOrchestrator
from src.core.orchestration.objective_planner import ObjectivePlanner
from src.core.orchestration.task_graph import (
    CycleDetectedError,
    TaskGraph,
)

__all__ = [
    "HierarchicalAgentOrchestrator",
    "ObjectivePlanner",
    "TaskGraph",
    "CycleDetectedError",
    "Consolidator",
]
