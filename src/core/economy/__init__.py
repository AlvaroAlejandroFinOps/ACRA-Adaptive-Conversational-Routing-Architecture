"""ACRA Economy and Resource Governance Package.

Exports:
- TokenEconomyEngine, BudgetExceededError (hierarchical budget cascade, reservations, INV-005, INV-006)
- ContinuityCostModel, MigrationTradeoffAssessment (continuity vs migration cost model, R-023, INV-010)
- ProvenanceTracker, ProvenanceRecord (telemetry and provenance tracking, INV-004)
"""

from src.core.economy.engine import (
    TokenEconomyEngine,
    BudgetExceededError,
)
from src.core.economy.cost_model import (
    ContinuityCostModel,
    MigrationTradeoffAssessment,
)
from src.core.economy.telemetry import (
    ProvenanceTracker,
    ProvenanceRecord,
)

__all__ = [
    "TokenEconomyEngine",
    "BudgetExceededError",
    "ContinuityCostModel",
    "MigrationTradeoffAssessment",
    "ProvenanceTracker",
    "ProvenanceRecord",
]
