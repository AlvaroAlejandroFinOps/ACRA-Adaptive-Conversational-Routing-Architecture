"""
Master Test Runner: Ejecuta la totalidad de la suite de tests (Unitarios + Integración).
"""

import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tests.test_suite_runner import (
    TestACRAMetrics,
    TestEdgeRouter,
    TestDHC,
    TestUnifiedContextTier,
    TestHandoffEngine,
    TestStateMachine,
    TestOrchestrator,
)
from tests.test_integration_runner import (
    TestIntegrationOrchestratorFlow,
    TestIntegrationABBenchmark,
)


def suite():
    s = unittest.TestSuite()
    loader = unittest.TestLoader()
    # Unit Tests
    s.addTests(loader.loadTestsFromTestCase(TestACRAMetrics))
    s.addTests(loader.loadTestsFromTestCase(TestEdgeRouter))
    s.addTests(loader.loadTestsFromTestCase(TestDHC))
    s.addTests(loader.loadTestsFromTestCase(TestUnifiedContextTier))
    s.addTests(loader.loadTestsFromTestCase(TestHandoffEngine))
    s.addTests(loader.loadTestsFromTestCase(TestStateMachine))
    s.addTests(loader.loadTestsFromTestCase(TestOrchestrator))
    # Integration Tests
    s.addTests(loader.loadTestsFromTestCase(TestIntegrationOrchestratorFlow))
    s.addTests(loader.loadTestsFromTestCase(TestIntegrationABBenchmark))
    return s


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
