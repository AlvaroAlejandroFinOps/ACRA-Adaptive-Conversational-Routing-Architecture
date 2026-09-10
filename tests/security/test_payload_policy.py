"""
Security Test Suite: Payload Policy Gate Unit Tests.
Verifies secrets detection, PII detection, sanitization, and sterilization hashing.
"""

import pytest
from src.core.payload_policy import PayloadPolicyGate, PolicyViolationType


class TestPayloadPolicyGate:

    def test_clean_payload_passes(self):
        gate = PayloadPolicyGate()
        clean_text = (
            "### CONSOLIDATED USER REQUIREMENTS:\n"
            "1. Implement a distributed Paxos consensus algorithm in Python.\n"
            "2. Optimize for low-latency network topologies."
        )
        result = gate.validate(clean_text)
        assert result.passed
        assert len(result.violations) == 0
        assert len(result.sterilization_hash) == 64  # SHA-256 hex digest
        assert result.policy_version == "1.0.0"

    def test_openai_api_key_leak_detected(self):
        gate = PayloadPolicyGate()
        leaking_text = "Here is my secret config: api_key = sk-abc12345678901234567890def for deployment."
        result = gate.validate(leaking_text)
        assert not result.passed
        assert any(v.violation_type == PolicyViolationType.SECRET_LEAK for v in result.violations)

    def test_aws_key_leak_detected(self):
        gate = PayloadPolicyGate()
        leaking_text = "AWS credentials: AKIAIOSFODNN7EXAMPLE and secret."
        result = gate.validate(leaking_text)
        assert not result.passed
        assert any(v.violation_type == PolicyViolationType.SECRET_LEAK for v in result.violations)

    def test_github_pat_leak_detected(self):
        gate = PayloadPolicyGate()
        leaking_text = "Clone with token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result = gate.validate(leaking_text)
        assert not result.passed
        assert any(v.violation_type == PolicyViolationType.SECRET_LEAK for v in result.violations)

    def test_private_key_leak_detected(self):
        gate = PayloadPolicyGate()
        leaking_text = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEowIBAAKCAQEA0Y1...\n"
            "-----END RSA PRIVATE KEY-----"
        )
        result = gate.validate(leaking_text)
        assert not result.passed
        assert any(v.violation_type == PolicyViolationType.SECRET_LEAK for v in result.violations)

    def test_sanitize_redacts_secrets_and_pii(self):
        gate = PayloadPolicyGate()
        text_with_secrets = (
            "Connect using sk-123456789012345678901234 and card 4532-1234-5678-9010."
        )
        sanitized = gate.sanitize(text_with_secrets)
        assert "sk-123456789012345678901234" not in sanitized
        assert "4532-1234-5678-9010" not in sanitized
        assert "[REDACTED_SECRET]" in sanitized
        assert "[REDACTED_PII]" in sanitized

    def test_excessive_payload_size_flagged(self):
        gate = PayloadPolicyGate(max_payload_bytes=100)
        oversized = "A" * 150
        result = gate.validate(oversized)
        assert not result.passed
        assert any(v.violation_type == PolicyViolationType.EXCESSIVE_PAYLOAD_SIZE for v in result.violations)
