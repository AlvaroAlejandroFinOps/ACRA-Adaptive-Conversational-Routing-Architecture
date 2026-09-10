"""
Unit tests for ResourceGovernor, ACRAConfig loader, and ACRALogger.
"""

import pytest
from src.core.governance import ResourceGovernor, BudgetExceededError
from src.core.config_loader import ACRAConfig
from src.core.logger import ACRALogger


def test_resource_governor_enforces_turn_limit():
    governor = ResourceGovernor(max_turns_per_session=3)
    session_id = "test_gov_session_1"

    governor.check_and_record(session_id)  # Turn 1
    governor.check_and_record(session_id)  # Turn 2
    governor.check_and_record(session_id)  # Turn 3

    # Turn 4 should raise BudgetExceededError
    with pytest.raises(BudgetExceededError) as exc_info:
        governor.check_and_record(session_id)
    assert "exceeded turn limit" in str(exc_info.value)


def test_resource_governor_enforces_token_limit():
    governor = ResourceGovernor(max_tokens_per_session=1000)
    session_id = "test_gov_session_2"

    governor.check_and_record(session_id, tokens_added=800)

    # Adding 300 more tokens should exceed 1000
    with pytest.raises(BudgetExceededError) as exc_info:
        governor.check_and_record(session_id, tokens_added=300)
    assert "exceeded token limit" in str(exc_info.value)


def test_config_loader_validates_yaml():
    config = ACRAConfig.load_from_yaml()
    assert config.version == "2.0.0"
    assert config.routing.default_maturity_threshold == 0.70
    assert config.routing.min_turns_before_pro == 1
    assert config.compression.target_min_ccr == 0.45
    assert config.security.block_injections is True
    assert config.security.block_secrets is True
    assert config.governance.max_turns_per_session == 25
    assert config.tenants.default_tenant == "default"


def test_logger_sanitizes_secrets(capsys):
    logger = ACRALogger(name="test_logger")
    logger.info("Deploying with secret api_key = sk-123456789012345678901234 on node.")

    captured = capsys.readouterr()
    assert "sk-123456789012345678901234" not in captured.out
    assert "[REDACTED_SECRET]" in captured.out
