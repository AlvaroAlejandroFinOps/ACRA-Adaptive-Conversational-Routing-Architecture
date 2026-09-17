"""ACRA Task Contracts.

Defines TaskDefinition, TaskExecution, TaskDependency, and TaskState for TaskGraph orchestration.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class TaskState(str, Enum):
    """Lifecycle states for a discrete task within the TaskGraph (ADR-004)."""
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"


class DependencyType(str, Enum):
    """Type of dependency relationship between tasks in the DAG."""
    HARD = "HARD"           # Prerequisite must succeed
    OPTIONAL = "OPTIONAL"   # Prerequisite runs first if possible; continues on failure
    CONDITIONAL = "CONDITIONAL" # Prerequisite triggers task only on specific branch outcome


class TaskDependency(BaseModel):
    """Dependency constraint between tasks."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    depends_on_task_id: str = Field(..., description="ID of prerequisite task")
    dependency_type: DependencyType = Field(default=DependencyType.HARD, description="Type of dependency")


class TaskDefinition(BaseModel):
    """Specification of an atomic work unit decomposed from an objective."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: str = Field(..., description="Unique task identifier")
    objective_id: str = Field(..., description="Parent objective ID")
    description: str = Field(..., description="Detailed task instructions")
    target_domain: str = Field(..., description="Domain to which this task belongs")
    required_capabilities: list[str] = Field(default_factory=list, description="Required agent capabilities")
    dependencies: list[TaskDependency] = Field(default_factory=list, description="DAG dependencies")
    input_data: dict[str, Any] = Field(default_factory=dict, description="Input parameters and payloads")
    timeout_seconds: int = Field(default=60, ge=1, description="Execution timeout in seconds")


class TaskExecution(BaseModel):
    """Runtime tracking of a task execution instance."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(..., description="Unique execution run UUID")
    task_id: str = Field(..., description="Associated TaskDefinition ID")
    assigned_agent_instance_id: str = Field(..., description="Assigned AgentInstance ID")
    state: TaskState = Field(default=TaskState.PENDING, description="Current execution state")
    started_at: datetime | None = Field(default=None, description="Execution start timestamp")
    completed_at: datetime | None = Field(default=None, description="Execution completion timestamp")
    error_message: str | None = Field(default=None, description="Error detail if failed")
    retry_count: int = Field(default=0, ge=0, description="Number of execution retries attempted")
