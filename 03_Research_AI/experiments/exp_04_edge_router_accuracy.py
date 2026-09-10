"""
Experimento 04: Evaluación de Precisión del Edge Router.
Mide la precisión, recall y F1 en la clasificación de madurez del prompt,
evaluando la tasa de prevención de anclaje prematuro (Guo et al., 2026).
"""

import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.edge_router import EdgeRouter, RouterAction
from src.data_generation.conversation_generator import ConversationGenerator


def run_experiment_4():
    print("=== [ACRA Experiment 04] Edge Router Maturity Accuracy Benchmark ===")
    router = EdgeRouter(maturity_threshold=0.50, min_turns_before_pro=1)
    suite = ConversationGenerator.generate_benchmark_suite(num_conversations=60)

    tp, fp, tn, fn = 0, 0, 0, 0

    for conv in suite:
        history = []
        for turn in conv.turns:
            dec = router.route(history, turn.user_prompt)
            predicted_mature = (dec.action == RouterAction.DISPATCH_PRO)
            actual_mature = turn.expected_mature

            if predicted_mature and actual_mature:
                tp += 1
            elif predicted_mature and not actual_mature:
                fp += 1
            elif not predicted_mature and not actual_mature:
                tn += 1
            else:
                fn += 1
            
            # Registrar el turno en el historial para el siguiente turno de la conversación
            from src.core.edge_router import MessageTurn, TurnRole
            history.append(MessageTurn(role=TurnRole.USER, content=turn.user_prompt, turn_index=turn.turn_index))

    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print(f"Total Evaluated Turns : {total}")
    print(f"True Positives  (TP)  : {tp}")
    print(f"True Negatives  (TN)  : {tn}")
    print(f"False Positives (FP)  : {fp} (Riesgo de anclaje prematuro evitado)")
    print(f"False Negatives (FN)  : {fn}")
    print("-" * 45)
    print(f"Accuracy              : {accuracy:.2%}")
    print(f"Precision             : {precision:.2%}")
    print(f"Recall                : {recall:.2%}")
    print(f"F1 Score              : {f1:.2%}")

    res = {
        "total_turns": total,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": {"tp": tp, "tn": tn, "fp": fp, "fn": fn}
    }

    out_file = ROOT_DIR / "Artefactos" / "Planes" / "Vigentes" / "exp_04_edge_router_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(f"\n[OK] Experiment 04 results saved to: {out_file}")


if __name__ == "__main__":
    run_experiment_4()
