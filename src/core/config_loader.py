"""
Configuration Loader & Validator: Parses acra_config.yaml using Pydantic models.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
from pydantic import BaseModel, Field


class ClusterConfig(BaseModel):
    model_name: str
    max_tokens: int = 2048
    temperature: float = 0.0
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


class RoutingConfig(BaseModel):
    default_maturity_threshold: float = 0.70
    min_turns_before_pro: int = 1
    max_clarification_turns: int = 4
    edge_cluster: ClusterConfig
    pro_cluster: ClusterConfig


class CompressionConfig(BaseModel):
    target_min_ccr: float = 0.45
    enforce_assistant_masking: bool = True
    preserve_code_blocks: bool = True
    strip_conversational_chatter: bool = True
    extract_architectural_decisions: bool = True


class CachingConfig(BaseModel):
    ttl_seconds: float = 3600.0
    enable_nvlink_tensor_caching_simulation: bool = True
    salt: str = "acra_kernel_salt_v1"


class SecurityConfig(BaseModel):
    block_injections: bool = True
    block_secrets: bool = True
    block_pii: bool = True
    max_payload_bytes: int = 262144
    policy_version: str = "1.0.0"
    enforce_provenance_verification: bool = True


class GovernanceConfig(BaseModel):
    max_turns_per_session: int = 25
    max_tokens_per_session: int = 64000
    max_session_duration_sec: float = 600.0
    max_cost_usd_per_session: float = 1.00


class TenantsConfig(BaseModel):
    default_tenant: str = "default"
    enforce_tenant_isolation: bool = True


class TelemetryConfig(BaseModel):
    log_level: str = "INFO"
    structured_json: bool = True
    enable_correlation_id: bool = True


class ACRAConfig(BaseModel):
    version: str = "2.0.0"
    environment: str = "production-ready"
    routing: RoutingConfig
    compression: CompressionConfig
    caching: CachingConfig
    security: SecurityConfig
    governance: GovernanceConfig
    tenants: TenantsConfig
    telemetry: TelemetryConfig
    evaluation: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def load_from_yaml(cls, path: Optional[Path] = None) -> "ACRAConfig":
        if path is None:
            path = Path(__file__).resolve().parent.parent.parent / "config" / "acra_config.yaml"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)
