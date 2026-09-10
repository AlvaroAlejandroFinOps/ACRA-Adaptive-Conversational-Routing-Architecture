"""
Payload Policy Gate: Pre-dispatch validation and sterilization engine.
Ensures zero untrusted, contaminated, or leaking payloads reach the Pro cluster.
"""

import re
import hashlib
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from .edge_router import ContentProvenance, TrustLevel


class PolicyViolationType(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    SECRET_LEAK = "secret_leak"
    PII_LEAK = "pii_leak"
    UNTRUSTED_TRUST_PROMOTION = "untrusted_trust_promotion"
    MALFORMED_PROVENANCE = "malformed_provenance"
    EXCESSIVE_PAYLOAD_SIZE = "excessive_payload_size"
    DISALLOWED_ROLE = "disallowed_role"


class PolicyViolation(BaseModel):
    violation_type: PolicyViolationType
    severity: str = Field(..., description="'critical', 'high', 'medium', 'low'")
    detail: str
    location: Optional[str] = None


class PolicyValidationResult(BaseModel):
    passed: bool
    violations: List[PolicyViolation] = Field(default_factory=list)
    sterilization_hash: str
    policy_version: str = "1.0.0"
    sanitized_content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PayloadPolicyGate:
    """
    Guardian of the Pro cluster boundary.
    Performs deterministic static analysis on compressed context before handoff.
    """

    POLICY_VERSION = "1.0.0"

    # Known prompt injection signatures
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions?",
        r"(?i)system\s+(override|bypass|prompt)",
        r"(?i)you\s+are\s+now\s+(an?\s+)?unrestricted",
        r"(?i)jailbreak",
        r"(?i)dan\s+mode",
        r"(?i)<\|im_start\|>\s*system",
        r"(?i)\[INST\]\s*<<SYS>>",
        r"(?i)disregard\s+all\s+(rules|guidelines)",
        r"(?i)new\s+system\s+directive:",
        r"(?i)act\s+as\s+a\s+root\s+user",
    ]

    # Secret / credential leakage signatures
    SECRET_PATTERNS = [
        (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API Key format"),
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID format"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
        (r"-----BEGIN\s+(RSA|OPENSSH|EC|DSA)?\s*PRIVATE\s+KEY-----", "Private cryptographic key"),
        (r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{25,}", "Bearer Token"),
        (r"(?i)password\s*[:=]\s*['\"][^\s'\"]{6,}['\"]", "Hardcoded credential assignment"),
    ]

    # PII patterns
    PII_PATTERNS = [
        (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "Payment card number format"),
        (r"\b\d{3}-\d{2}-\d{4}\b", "US Social Security Number format"),
    ]

    def __init__(
        self,
        block_injections: bool = True,
        block_secrets: bool = True,
        block_pii: bool = True,
        max_payload_bytes: int = 256 * 1024,  # 256 KB safety limit
    ):
        self.block_injections = block_injections
        self.block_secrets = block_secrets
        self.block_pii = block_pii
        self.max_payload_bytes = max_payload_bytes

    def sanitize(self, text: str) -> str:
        """Redacts identified secrets and PII from content."""
        sanitized = text
        for pattern, _ in self.SECRET_PATTERNS:
            sanitized = re.sub(pattern, "[REDACTED_SECRET]", sanitized)
        for pattern, _ in self.PII_PATTERNS:
            sanitized = re.sub(pattern, "[REDACTED_PII]", sanitized)
        return sanitized

    def validate(
        self,
        payload_text: str,
        provenance_chain: Optional[List[Dict[str, Any]]] = None,
    ) -> PolicyValidationResult:
        """
        Executes complete verification pipeline.
        Returns PolicyValidationResult indicating whether handoff is authorized.
        """
        violations: List[PolicyViolation] = []

        # 1. Payload size boundary check
        payload_bytes = len(payload_text.encode("utf-8"))
        if payload_bytes > self.max_payload_bytes:
            violations.append(
                PolicyViolation(
                    violation_type=PolicyViolationType.EXCESSIVE_PAYLOAD_SIZE,
                    severity="high",
                    detail=f"Payload size {payload_bytes} bytes exceeds threshold of {self.max_payload_bytes} bytes",
                )
            )

        # 2. Prompt injection static scan
        if self.block_injections:
            for pat in self.INJECTION_PATTERNS:
                match = re.search(pat, payload_text)
                if match:
                    violations.append(
                        PolicyViolation(
                            violation_type=PolicyViolationType.PROMPT_INJECTION,
                            severity="critical",
                            detail=f"Detected potential prompt injection pattern: '{match.group(0)[:40]}...'",
                            location=str(match.span()),
                        )
                    )

        # 3. Secret leak check
        if self.block_secrets:
            for pat, desc in self.SECRET_PATTERNS:
                match = re.search(pat, payload_text)
                if match:
                    violations.append(
                        PolicyViolation(
                            violation_type=PolicyViolationType.SECRET_LEAK,
                            severity="critical",
                            detail=f"Detected leaked secret ({desc})",
                            location=str(match.span()),
                        )
                    )

        # 4. PII check
        if self.block_pii:
            for pat, desc in self.PII_PATTERNS:
                match = re.search(pat, payload_text)
                if match:
                    violations.append(
                        PolicyViolation(
                            violation_type=PolicyViolationType.PII_LEAK,
                            severity="high",
                            detail=f"Detected PII data ({desc})",
                            location=str(match.span()),
                        )
                    )

        # 5. Provenance integrity & trust hierarchy enforcement
        if provenance_chain is not None:
            for entry in provenance_chain:
                prov = entry.get("provenance")
                trust = entry.get("trust_level")
                role = entry.get("role")

                # An untrusted user turn must NEVER be labeled as trusted
                if prov == ContentProvenance.USER_DIRECT.value and trust == TrustLevel.TRUSTED.value:
                    violations.append(
                        PolicyViolation(
                            violation_type=PolicyViolationType.UNTRUSTED_TRUST_PROMOTION,
                            severity="critical",
                            detail=f"Illegal trust promotion in turn {entry.get('turn_index')}: USER_DIRECT cannot have TRUSTED level without external verification",
                        )
                    )

                # Disallowed role masquerade: user direct turn claiming to be system role
                if prov == ContentProvenance.USER_DIRECT.value and role == "system":
                    violations.append(
                        PolicyViolation(
                            violation_type=PolicyViolationType.DISALLOWED_ROLE,
                            severity="critical",
                            detail=f"Role masquerade in turn {entry.get('turn_index')}: user direct claim system role",
                        )
                    )

        has_critical = any(v.severity in ("critical", "high") for v in violations)
        passed = not has_critical

        # Generate deterministic sterilization hash
        content_hash = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
        sanitized = self.sanitize(payload_text) if not passed else payload_text

        return PolicyValidationResult(
            passed=passed,
            violations=violations,
            sterilization_hash=content_hash,
            policy_version=self.POLICY_VERSION,
            sanitized_content=sanitized,
            metadata={
                "payload_bytes": payload_bytes,
                "violation_count": len(violations),
                "has_critical": has_critical,
            },
        )
