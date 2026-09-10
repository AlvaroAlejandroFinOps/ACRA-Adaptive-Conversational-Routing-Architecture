# ACRA: Adaptive Conversational Routing Architecture
## Cognitive Stability for Multi-Turn Large Language Model Interactions

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![Tests: 15 Passed](https://img.shields.io/badge/Tests-15%20Passed-success.svg)](tests/)
[![Paper Draft: Ready](https://img.shields.io/badge/Paper-Draft%20Available-orange.svg)](Artefactos/Planes/Vigentes/ACRA_Academic_Paper_Draft.md)

ACRA es un framework arquitectónico de orquestación de estado diseñado para resolver la **degradación cognitiva multi-turno** en Modelos de Lenguaje Grandes (LLMs). Sin requerir reentrenamiento de pesos ni sobrecoste de cómputo en inferencia, ACRA recupera hasta un **+38.36%** del rendimiento degradado en diálogos extendidos y reduce la infiabilidad estocástica en un **-75.08%**.

---

## Estructura del Repositorio

```
├── 001_Seed/                  # Semilla y ADN del proyecto
├── 02_Foundation/Engine/      # Guía de gobernanza de directorios
├── 03_Research_AI/            # Scripts de experimentos y notebooks
│   └── experiments/           # 5 experimentos científicos reproducibles (exp_01 a exp_05)
├── Artefactos/Planes/Vigentes/# Entregables académicos (Paper Draft, Benchmark Report, JSONs)
├── config/                    # Configuración global (acra_config.yaml)
├── docs/                      # RFCs, notas de ingeniería y especificaciones técnicas
│   ├── architecture/          # ACRA_Cognitive_Stability_RFC.md
│   ├── engineers_notes/       # 10 notas con fundamentación bibliográfica (ref_01 a ref_10)
│   └── technical_specs/       # ACRA_Technical_Specification_v1.md
├── schemas/                   # Esquemas JSON formales (conversation_state, routing_decision)
├── src/                       # Código fuente modular
│   ├── core/                  # Motor ACRA (metrics, router, DHC, UCT, handoff, orchestrator)
│   └── data_generation/       # Generador de conversaciones sintéticas multi-turno
└── tests/                     # Suite de 15 tests unitarios e integrados (run_all_tests.py)
```

---

## Quickstart

### 1. Ejecutar la Suite Completa de Tests
```bash
python tests/run_all_tests.py
```

### 2. Reproducir los Experimentos Científicos
```bash
# Experimento 01: Degradación baseline (Laban et al., 2025)
python 03_Research_AI/experiments/exp_01_baseline_degradation.py

# Experimento 02: A/B Testing Baseline vs. ACRA Pipeline
python 03_Research_AI/experiments/exp_02_acra_vs_baseline.py

# Experimento 03: Análisis de Sensibilidad CCR (Context Consolidation Ratio)
python 03_Research_AI/experiments/exp_03_ccr_sensitivity.py

# Experimento 04: Precisión del Edge Router y Prevención de Anclaje
python 03_Research_AI/experiments/exp_04_edge_router_accuracy.py

# Experimento 05: Estudio de Ablación Arquitectónica
python 03_Research_AI/experiments/exp_05_ablation_study.py
```

---

## Principales Resultados Empíricos

| Métrica | Baseline Raw Multi-Turn | ACRA Pipeline | Impacto |
|:---|:---:|:---:|:---:|
| **Rendimiento Promedio ($P̄$)** | 39.52 | **54.68** | **+38.36% Recuperación** |
| **Infiabilidad ($U_{10}^{90}$)** | 50.54 | **12.59** | **-75.08% Estabilización** |
| **Varianza ($\sigma^2$)** | 346.97 | **23.16** | **-93.32% Reducción de Ruido** |
| **Ratio de Consolidación (CCR)** | N/A | **30.6% - 65.0%** | **Mandato de Purga Cumplido** |

---

## Entregables Académicos

- [Draft de Paper Académico (Paper-Grade)](Artefactos/Planes/Vigentes/ACRA_Academic_Paper_Draft.md)
- [Reporte Consolidado de Benchmarks](Artefactos/Planes/Vigentes/ACRA_Benchmark_Report.md)
- [Especificación Técnica v1.0](docs/technical_specs/ACRA_Technical_Specification_v1.md)
- [RFC Arquitectónico de Estabilidad Cognitiva](docs/architecture/ACRA_Cognitive_Stability_RFC.md)

---

## Licencia

Distribuido bajo la Licencia Apache 2.0. Consulte `LICENSE` para obtener más información.
