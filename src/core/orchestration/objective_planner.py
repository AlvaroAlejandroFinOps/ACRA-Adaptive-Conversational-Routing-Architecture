"""ACRA Objective Planner.

Decomposes complex user goals into structured TaskDefinitions and DAG TaskGraphs
using the ObjectiveStateMachine (ADR-004, R-001).
"""

from __future__ import annotations

import uuid
from typing import Any
from src.core.contracts.task import DependencyType, TaskDefinition, TaskDependency
from src.core.fsm.objective import ObjectiveState, ObjectiveStateMachine
from src.core.orchestration.task_graph import TaskGraph
from src.core.routing.intake_router import IntakeClassification


class ObjectivePlanner:
    """Decomposes top-level objectives into TaskGraphs."""

    def plan_and_decompose(
        self,
        objective_id: str,
        objective_text: str,
        classification: IntakeClassification,
    ) -> tuple[TaskGraph, ObjectiveStateMachine]:
        """Decompose an objective into a dependency-ordered TaskGraph."""
        fsm = ObjectiveStateMachine(objective_id=objective_id)
        fsm.transition_to(ObjectiveState.PLANNING, reason="Decomposing objective")

        graph = TaskGraph(graph_id=f"graph_{objective_id}")

        if not classification.requires_decomposition:
            # Single task execution
            single_task = TaskDefinition(
                task_id=f"task_{objective_id}_1",
                objective_id=objective_id,
                description=objective_text,
                target_domain=classification.primary_domain,
                required_capabilities=["structured_output"],
            )
            graph.add_task(single_task)
        else:
            # Multi-stage decomposition
            # 1. Primary analysis task
            task_analyze = TaskDefinition(
                task_id=f"task_{objective_id}_analyze",
                objective_id=objective_id,
                description=f"Analyze and scope: {objective_text}",
                target_domain=classification.primary_domain,
                required_capabilities=["structured_output", "reasoning"],
            )
            graph.add_task(task_analyze)

            # 2. Execution task depending on analysis
            task_exec = TaskDefinition(
                task_id=f"task_{objective_id}_execute",
                objective_id=objective_id,
                description=f"Execute operational steps for: {objective_text}",
                target_domain=classification.primary_domain,
                required_capabilities=["structured_output", "tool_calling"],
                dependencies=[
                    TaskDependency(
                        depends_on_task_id=task_analyze.task_id,
                        dependency_type=DependencyType.HARD,
                    )
                ],
            )
            graph.add_task(task_exec)

            # 3. Verification task depending on execution
            task_verify = TaskDefinition(
                task_id=f"task_{objective_id}_verify",
                objective_id=objective_id,
                description=f"Validate policy and outcome for: {objective_text}",
                target_domain=classification.primary_domain,
                required_capabilities=["structured_output"],
                dependencies=[
                    TaskDependency(
                        depends_on_task_id=task_exec.task_id,
                        dependency_type=DependencyType.HARD,
                    )
                ],
            )
            graph.add_task(task_verify)

        fsm.transition_to(ObjectiveState.DECOMPOSED, reason=f"Decomposed into {len(graph.tasks)} tasks")
        return graph, fsm
