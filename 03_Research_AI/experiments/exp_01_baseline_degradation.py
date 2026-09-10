"""
Experimento 01: Cuantificación de la Degradación Multi-Turno en Condiciones Baseline (Laban et al., 2025 Replicación).
Calcula formalmente P̄, A⁹⁰, U₁₀⁹⁰ a lo largo de 1 a 10 turnos conversacionales sin orquestador.
"""

import sys
import json
from pathlib import Path
import numpy as np

# Configurar path de importación
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.metrics import ACRAMetrics
from src.core.models.mock_models import EmpiricalCalibrator


def run_experiment_1(num_trials: int = 100, max_turns: int = 8):
    print(f"=== [ACRA Experiment 01] Multi-Turn Baseline Degradation Simulation ===")
    print(f"Running N={num_trials} trials across 1 to {max_turns} turns...\n")

    results_by_turn = {}

    for turn in range(1, max_turns + 1):
        scores = []
        # En cada turno adicional, la entropía estocástica se amplifica
        # Simulando la degradación de Laban et al.: media cae ~39% y varianza sube ~112%
        degradation_factor = 1.0 - (0.055 * (turn - 1))
        std_expansion_factor = 1.0 + (0.16 * (turn - 1))

        current_mean = max(20.0, EmpiricalCalibrator.ZERO_SHOT_MEAN * degradation_factor)
        current_std = EmpiricalCalibrator.ZERO_SHOT_STD * std_expansion_factor

        for _ in range(num_trials):
            val = float(np.random.normal(current_mean, current_std))
            scores.append(max(0.0, min(100.0, val)))

        dist = ACRAMetrics.calculate_performance_distribution(scores)
        results_by_turn[turn] = {
            "mean_P": round(dist.mean_performance, 2),
            "aptitude_A90": round(dist.aptitude_p90, 2),
            "unreliability_U10_90": round(dist.unreliability_p10_p90, 2),
            "std_dev": round(dist.additional_stats["std_dev"], 2),
        }

    print(f"{'Turn':<6} | {'Mean (P_bar)':<12} | {'Aptitude (A90)':<16} | {'Unreliability (U10_90)':<22} | {'Std Dev':<8}")
    print("-" * 72)
    for t, data in results_by_turn.items():
        print(f"{t:<6} | {data['mean_P']:<12} | {data['aptitude_A90']:<16} | {data['unreliability_U10_90']:<22} | {data['std_dev']:<8}")

    # Exportar resultados estructurados
    output_path = ROOT_DIR / "Artefactos" / "Planes" / "Vigentes" / "exp_01_baseline_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_by_turn, f, indent=2)
    print(f"\n[OK] Experiment 01 results exported to: {output_path}")
    return results_by_turn


if __name__ == "__main__":
    run_experiment_1()
