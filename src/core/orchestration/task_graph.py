"""ACRA Task Graph and DAG Execution Scheduler.

Implements TaskGraph scheduling with dependency resolution and cycle prevention (INV-008).
"""

from __future__ import annotations

from typing import Any
from src.core.contracts.task import DependencyType, TaskDefinition, TaskState
from src.core.fsm.task import TaskStateMachine


class CycleDetectedError(ValueError):
    """Raised when a circular dependency is detected in the Task DAG."""
    pass


class TaskGraph:
    """Directed Acyclic Graph of tasks decomposed from an objective."""

    def __init__(self, graph_id: str) -> None:
        self.graph_id = graph_id
        self.tasks: dict[str, TaskDefinition] = {}
        self.fsms: dict[str, TaskStateMachine] = {}

    def add_task(self, task: TaskDefinition) -> None:
        """Add a TaskDefinition and its TaskStateMachine to the DAG."""
        self.tasks[task.task_id] = task
        self.fsms[task.task_id] = TaskStateMachine(task_id=task.task_id)

    def get_execution_order(self) -> list[str]:
        """Compute topological sort of task IDs using Kahn's algorithm (INV-008)."""
        in_degree: dict[str, int] = {t_id: 0 for t_id in self.tasks}
        adj_list: dict[str, list[str]] = {t_id: [] for t_id in self.tasks}

        for task in self.tasks.values():
            for dep in task.dependencies:
                prereq_id = dep.depends_on_task_id
                if prereq_id in self.tasks:
                    adj_list[prereq_id].append(task.task_id)
                    in_degree[task.task_id] += 1

        queue = [t_id for t_id, deg in in_degree.items() if deg == 0]
        order: list[str] = []

        while queue:
            current = queue.pop(0)
            order.append(current)
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.tasks):
            raise CycleDetectedError("Circular task dependency detected in TaskGraph (INV-008)")

        return order

    def get_ready_tasks(self) -> list[str]:
        """Return list of tasks whose dependencies are COMPLETED and are currently PENDING."""
        ready = []
        for t_id, task in self.tasks.items():
            fsm = self.fsms[t_id]
            if fsm.state == TaskState.PENDING:
                all_deps_done = True
                for dep in task.dependencies:
                    if dep.dependency_type == DependencyType.HARD:
                        prereq_fsm = self.fsms.get(dep.depends_on_task_id)
                        if not prereq_fsm or prereq_fsm.state != TaskState.COMPLETED:
                            all_deps_done = False
                            break
                if all_deps_done:
                    ready.append(t_id)
        return ready

    def mark_completed(self, task_id: str) -> None:
        """Advance task through VALIDATING to COMPLETED."""
        fsm = self.fsms[task_id]
        if fsm.state == TaskState.PENDING:
            fsm.transition_to(TaskState.ASSIGNED)
        if fsm.state == TaskState.ASSIGNED:
            fsm.transition_to(TaskState.EXECUTING)
        if fsm.state == TaskState.EXECUTING:
            fsm.transition_to(TaskState.VALIDATING)
        if fsm.state == TaskState.VALIDATING:
            fsm.transition_to(TaskState.COMPLETED)
