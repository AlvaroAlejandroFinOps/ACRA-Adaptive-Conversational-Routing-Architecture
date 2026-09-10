"""
Master Experiment Runner: Executes all 5 ACRA research experiments, collects telemetry,
ensures empirical simulation flags are explicit, and synthesizes the benchmark evaluation report.
"""

import sys
import json
from pathlib import Path
import time

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import importlib

exp01_mod = importlib.import_module("03_Research_AI.experiments.exp_01_baseline_degradation")
exp02_mod = importlib.import_module("03_Research_AI.experiments.exp_02_acra_vs_baseline")
exp03_mod = importlib.import_module("03_Research_AI.experiments.exp_03_ccr_sensitivity")
exp04_mod = importlib.import_module("03_Research_AI.experiments.exp_04_edge_router_accuracy")
exp05_mod = importlib.import_module("03_Research_AI.experiments.exp_05_ablation_study")

run_experiment_1 = exp01_mod.run_experiment_1
run_experiment_2 = exp02_mod.run_experiment_2
run_experiment_3 = exp03_mod.run_experiment_3
run_experiment_4 = exp04_mod.run_experiment_4
run_experiment_5 = exp05_mod.run_experiment_5


def main():
    print("=" * 80)
    print("      ACRA ARCHITECTURE: COMPREHENSIVE EMPIRICAL EXPERIMENT SUITE")
    print("=" * 80)
    print("Methodological Note: All experiments are scientifically grounded in the empirical")
    print("findings of Laban et al. (2025) and Guo et al. (2026). Results are labeled as simulated.")
    print("=" * 80 + "\n")

    t0 = time.time()
    results = {}

    print(">>> Executing Experiment 01: Baseline Degradation Curve...")
    results["exp_01"] = {
        "title": "Baseline Multi-Turn Degradation Quantification",
        "simulated": True,
        "results": run_experiment_1(num_trials=100, max_turns=8),
    }

    print("\n>>> Executing Experiment 02: A/B Testing (Raw vs. ACRA Pipeline)...")
    results["exp_02"] = {
        "title": "A/B Testing: Raw Multi-Turn vs. ACRA Pipeline",
        "simulated": True,
        "results": run_experiment_2(num_conversations=100),
    }

    print("\n>>> Executing Experiment 03: CCR Sensitivity Analysis...")
    results["exp_03"] = {
        "title": "Context Consolidation Ratio (CCR) Sensitivity",
        "simulated": True,
        "results": run_experiment_3(),
    }

    print("\n>>> Executing Experiment 04: Edge Router Accuracy Benchmark...")
    results["exp_04"] = {
        "title": "Edge Router Routing Accuracy and Early-Lock Prevention",
        "simulated": True,
        "results": run_experiment_4(),
    }

    print("\n>>> Executing Experiment 05: Architectural Component Ablation Study...")
    results["exp_05"] = {
        "title": "Architectural Component Ablation Study",
        "simulated": True,
        "results": run_experiment_5(num_trials=100),
    }

    elapsed = time.time() - t0

    # Save comprehensive aggregate JSON
    output_dir = ROOT_DIR / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "all_experiments_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp_epoch": time.time(),
                "total_duration_sec": round(elapsed, 2),
                "simulated": True,
                "framework": "ACRA Adaptive Conversational Routing Architecture v2.0",
                "experiments": results,
            },
            f,
            indent=2,
            default=str,
        )

    print("\n" + "=" * 80)
    print(f"[SUCCESS] All 5 experiments completed in {elapsed:.2f}s.")
    print(f"[DATA] Consolidated telemetry saved to: {summary_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
