"""ACRA Routing Package.

Exposes capability-based routing, intake triage, model resolution, and agent assignment.
"""

from src.core.routing.affinity import (
    CacheAwareRouter,
    HysteresisPolicy,
)
from src.core.routing.capability_router import (
    CapabilityAndAgentRouter,
    RoutingError,
)
from src.core.routing.intake_router import (
    IntakeClassification,
    IntakeRouter,
)
from src.core.routing.model_resolver import (
    ModelCapabilityRegistry,
    ResolutionError,
)

__all__ = [
    "ModelCapabilityRegistry",
    "ResolutionError",
    "IntakeRouter",
    "IntakeClassification",
    "CapabilityAndAgentRouter",
    "RoutingError",
    "HysteresisPolicy",
    "CacheAwareRouter",
]

