"""ACRA Agent Registry.

Implements AgentRegistry managing persistent AgentDefinition templates (ADR-003).
Supports registering, querying, and loading definitions from YAML manifests.
"""

from __future__ import annotations

import os
import yaml
from typing import Any
from src.core.contracts.agent import AgentDefinition


class AgentRegistry:
    """Registry maintaining persistent AgentDefinitions partitioned by domain."""

    def __init__(self) -> None:
        self._definitions: dict[str, AgentDefinition] = {}

    def register_definition(self, definition: AgentDefinition) -> None:
        """Register an AgentDefinition in the registry."""
        self._definitions[definition.agent_def_id] = definition

    register = register_definition

    def get_definition(self, agent_def_id: str) -> AgentDefinition | None:
        """Retrieve an AgentDefinition by ID."""
        return self._definitions.get(agent_def_id)

    get = get_definition

    def list_definitions(self, domain: str | None = None) -> list[AgentDefinition]:
        """List all definitions, optionally filtered by domain."""
        if domain is None:
            return list(self._definitions.values())
        return [d for d in self._definitions.values() if d.domain == domain]

    def load_from_yaml(self, yaml_path: str) -> AgentDefinition:
        """Load an AgentDefinition from a YAML file."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Agent definition file not found: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        definition = AgentDefinition(**data)
        self.register_definition(definition)
        return definition

    def load_from_directory(self, dir_path: str) -> list[AgentDefinition]:
        """Load all YAML agent definitions in a directory recursively."""
        loaded: list[AgentDefinition] = []
        if not os.path.exists(dir_path):
            return loaded

        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith((".yaml", ".yml")):
                    full_path = os.path.join(root, file)
                    try:
                        definition = self.load_from_yaml(full_path)
                        loaded.append(definition)
                    except Exception:
                        pass
        return loaded
