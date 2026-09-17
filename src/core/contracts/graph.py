"""ACRA Graph Contracts.

Defines AgentGraph, GraphNode, and GraphEdge for TaskGraph scheduling and agent topologies.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class NodeType(str, Enum):
    """Types of nodes in the orchestration graph."""
    OBJECTIVE = "OBJECTIVE"
    TASK = "TASK"
    AGENT = "AGENT"


class EdgeType(str, Enum):
    """Types of edges connecting orchestration nodes."""
    DEPENDS_ON = "DEPENDS_ON"
    ASSIGNED_TO = "ASSIGNED_TO"
    HANDOFF_TO = "HANDOFF_TO"
    CONSOLIDATES_TO = "CONSOLIDATES_TO"


class GraphNode(BaseModel):
    """A node in the orchestration DAG."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str = Field(..., description="Unique node ID in graph")
    node_type: NodeType = Field(..., description="Node classification")
    entity_id: str = Field(..., description="Reference ID to Task, Agent, or Objective entity")
    status: str = Field(default="PENDING", description="Current node status")


class GraphEdge(BaseModel):
    """A directed edge in the orchestration DAG."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    source_node_id: str = Field(..., description="Source node ID")
    target_node_id: str = Field(..., description="Target node ID")
    edge_type: EdgeType = Field(..., description="Relationship type")
    weight: float = Field(default=1.0, description="Routing or dependency weight")


class AgentGraph(BaseModel):
    """Orchestration topology graph representing objectives, tasks, and agents."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    graph_id: str = Field(..., description="Unique graph instance identifier")
    root_objective_id: str = Field(..., description="Top-level objective ID")
    nodes: dict[str, GraphNode] = Field(default_factory=dict, description="Nodes indexed by node_id")
    edges: list[GraphEdge] = Field(default_factory=list, description="List of directed edges")

    def get_dependencies_for_node(self, node_id: str) -> list[str]:
        """Return list of node IDs that the given node depends on."""
        return [
            edge.target_node_id
            for edge in self.edges
            if edge.source_node_id == node_id and edge.edge_type == EdgeType.DEPENDS_ON
        ]
