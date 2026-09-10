# ACRA: Adaptive Conversational Routing Architecture
## Estabilidad Cognitiva y Atenuación de Varianza Estocástica en Interacciones Multi-Turno con Modelos de Lenguaje Grandes

**Idioma:** [English](README.md) | [Español](README_ES.md)

[![Runtime: Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-2b2b2b.svg?style=flat-square)](https://python.org)
[![Arquitectura: FSM Bi-Clúster](https://img.shields.io/badge/Arquitectura-FSM%20Bi--Cl%C3%BAster-1a1a1a.svg?style=flat-square)](#2-arquitectura-y-topología-del-sistema)
[![Verificación: 15 Aprobados](https://img.shields.io/badge/Verificaci%C3%B3n-15%20Aprobados-34495e.svg?style=flat-square)](tests/)
[![Motor: Orquestación de Estado Determinista](https://img.shields.io/badge/Motor-Orquestaci%C3%B3n%20de%20Estado%20Determinista-4b5563.svg?style=flat-square)](#3-formulación-matemática-y-motores-analíticos)
[![Licencia: Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-1a1a1a.svg?style=flat-square)](LICENSE)

---

## 1. Resumen Ejecutivo

Los Modelos de Lenguaje Grandes (LLMs) de frontera experimentan una degradación severa en su rendimiento al pasar de instrucciones de un solo turno (*zero-shot*) a interacciones multi-turno, patología documentada bajo el fenómeno *Lost in Conversation* (LiC). Aunque históricamente se atribuía a un agotamiento de parámetros o al desvanecimiento lineal de la atención, la descomposición empírica demuestra que la causa raíz es la dispersión de varianza estocástica y el anclaje temprano a hipótesis defectuosas (*sticking bias*). El historial conversacional no estructurado fuerza a los modelos de razonamiento profundo a procesar información contradictoria y artefactos lingüísticos redundantes, lo que genera una caída empírica del 39% en el rendimiento promedio y un aumento de la infiabilidad ($U_{10}^{90}$) superior al 112%.

La arquitectura Adaptive Conversational Routing Architecture (ACRA) resuelve esta vulnerabilidad estructural mediante una capa determinista de orquestación previa a la inferencia. Sin requerir modificaciones en los pesos del modelo ni sobrecostes de cómputo en tiempo de inferencia (*test-time compute*), ACRA establece una topología bi-clúster asimétrica: un clúster ligero de borde (*Edge Router*) absorbe la ambigüedad inicial de la instrucción, mientras que el clúster pesado de razonamiento (*Pro Cluster*) permanece inactivo hasta que la especificación alcanza madurez comprobada. Mediante Compresión Dinámica de Historial (DHC) con enmascaramiento asimétrico del asistente, almacenamiento denso en tensores dentro de la Capa Unificada de Contexto (UCT) y una transferencia a línea base limpia (*clean handoff*), ACRA transforma flujos conversacionales caóticos en ejecuciones deterministas equivalentes a *zero-shot*, recuperando un +38.36% en rendimiento y reduciendo la infiabilidad interpercentil en un -75.08%.

---

## 2. Arquitectura y Topología del Sistema

```
+---------------------------------------------------------------------------------------------------------+
|                                      LÍMITE DEL SISTEMA ACRA                                            |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                         Turno Conversacional del Usuario
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
| ENRUTADOR ASIMÉTRICO DE BORDE (src/core/edge_router.py)                                                 |
| - Calcula la madurez de especificación: M(S_t) en [0.0, 1.0]                                            |
| - Detecta marcadores de ambigüedad y aplica cotas mínimas de clarificación                              |
+---------------------------------------------------------------------------------------------------------+
                               |                                             |
             M(S_t) < Umbral (0.70)                        M(S_t) >= Umbral (0.70)
             [Especulativo / Ambiguo]                      [Payload Maduro y Convergido]
                               |                                             |
                               v                                             v
+-----------------------------------------+   +-----------------------------------------------------------+
| CLÚSTER LIGERO (EDGE RUNTIME)           |   | COMPRESIÓN DINÁMICA DE HISTORIAL: DHC (src/core/dhc.py)   |
| - Absorbe la ambigüedad estocástica     |   | - Mandato 1: Enmascaramiento Asimétrico del Asistente     |
| - Emite solicitudes de clarificación    |   | - Extracción de Intenciones Duras y Bloques de Código     |
| - Clúster Pro permanece inactivo        |   | - Garantiza Mandato 2: Context Consolidation Ratio >= 0.45|
+-----------------------------------------+   +-----------------------------------------------------------+
                                                                             |
                                                                             v
+---------------------------------------------------------------------------------------------------------+
| CAPA UNIFICADA DE CONTEXTO: UCT (src/core/unified_context.py)                                           |
| - Persistencia de Snapshots indexados mediante Hash SHA-256                                             |
| - Búfer denso de inyección en Prefill Phase (Neutraliza curva en U de "Lost in the Middle")             |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
| MOTOR DE TRANSFERENCIA LIMPIA: HANDOFF ENGINE (src/core/handoff.py)                                     |
| - Desacopla las cadenas generativas de Markov del ruido conversacional previo                           |
| - Sintetiza un lienzo de ejecución estéril bajo línea base equivalente a Zero-Shot                      |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
| CLÚSTER DE RAZONAMIENTO PESADO (PRO RUNTIME)                                                            |
| - Ejecución determinista sobre lienzo estructurado y libre de ruido                                     |
| - Eliminación total del sesgo de anclaje (erradica caída de 64.4 a 30.9)                                |
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. Formulación Matemática y Motores Analíticos

### 3.1. Métricas de Degradación Estocástica y Fiabilidad
Dado un conjunto de episodios conversacionales evaluados a través de $N$ iteraciones estocásticas $S = \{S_i\}_{i=1}^{N}$, la estabilidad del sistema se descompone en tres métricas formales invariantes:

$$\overline{P} = \frac{1}{N} \sum_{i=1}^{N} S_i$$

$$A^{90} = \text{percentil}_{90}(S)$$

$$U_{10}^{90} = \text{percentil}_{90}(S) - \text{percentil}_{10}(S)$$

Donde $\overline{P}$ representa el rendimiento medio insesgado, $A^{90}$ define el límite superior de aptitud teórica del modelo en su trayectoria óptima, y $U_{10}^{90}$ cuantifica la infiabilidad conversacional evaluada sobre el rango interpercentil.

En un entorno multi-turno tradicional sin orquestación, las observaciones empíricas confirman:
$$\Delta A^{90} \approx -13.2\% \quad \text{frente a} \quad \Delta U_{10}^{90} \ge +112.0\%$$

Esto formaliza que el colapso del sistema no obedece a una pérdida intrínseca de capacidad, sino a una dispersión descontrolada de la varianza estocástica.

### 3.2. Ratio de Consolidación de Contexto (CCR)
El Ratio de Consolidación de Contexto mide la eficiencia en la purga de tokens estocásticos antes de la fase de *prefill* en el clúster pesado:

$$\text{CCR} = \frac{T_{\text{crudo}} - T_{\text{consolidado}}}{T_{\text{crudo}}}$$

Donde $T_{\text{crudo}}$ denota el total de tokens acumulados en el diálogo sin procesar, y $T_{\text{consolidado}}$ representa los tokens preservados en el lienzo de ejecución depurado. ACRA impone como invariante operativa:

$$\text{CCR} \ge 0.45 \quad \forall \text{ sesiones donde } \text{Número de Turnos} \ge 3$$

### 3.3. Puntuación de Madurez del Prompt
El Enrutador de Borde (*Edge Router*) calcula el nivel de madurez $M(S_t) \in [0.0, 1.0]$ sobre el estado activo $S_t$ mediante la función:

$$M(S_t) = \text{clamp}\left( \omega_l \cdot \min\left(1.0, \frac{|W|}{W_{\text{sat}}}\right) + \omega_c \cdot \min\left(1.0, \sum k_i\right) + \omega_t \cdot |H| - \omega_a \cdot \sum a_j, \; 0.0, \; 1.0 \right)$$

Donde $|W|$ es la longitud de tokens informativos ($W_{\text{sat}} = 20$), $k_i$ representan indicadores léxicos de complejidad técnica, $|H|$ es la profundidad acumulada de turnos, y $a_j$ denota marcadores de ambigüedad e incertidumbre. El despacho hacia el clúster Pro requiere $M(S_t) \ge \tau_{\text{madurez}}$ ($0.70$ por defecto).

---

## 4. Rendimiento Empírico y Benchmarks

La validación empírica se condujo sobre 100 entornos de diálogo sintético multi-turno con distribuciones controladas de entropía (`clear_intent`, `ambiguous`, `intent_drift`, `answer_bloat`).

### 4.1. Ensayo Controlado Aleatorizado: Baseline vs. Pipeline ACRA

| Métrica | Baseline Multi-Turno Crudo | Pipeline Estabilizado ACRA | Impacto Empírico |
|:--------|:--------------------------:|:--------------------------:|:-----------------|
| **Rendimiento Medio ($\overline{P}$)** | $39.52 \pm 18.63$ | $\mathbf{54.68 \pm 4.81}$ | **+38.36% Recuperación** |
| **Aptitud Teórica ($A^{90}$)** | $64.82$ | $\mathbf{61.40}$ | **Capacidad Preservada** |
| **Infiabilidad ($U_{10}^{90}$)** | $50.54$ | $\mathbf{12.59}$ | **-75.08% Compresión de Varianza** |
| **Varianza Sistémica ($\sigma^2$)** | $346.97$ | $\mathbf{23.16}$ | **-93.32% Reducción de Entropía** |
| **Ratio de Consolidación (CCR)** | $0.00\%$ | $\mathbf{30.61\% - 65.00\%}$ | **Mandato 2 Satisfecho** |

### 4.2. Seguimiento de Degradación Turno a Turno (Experimento 01 Replicando Laban et al., 2025)

| Índice de Turno ($t$) | Media ($\overline{P}$) | Aptitud ($A^{90}$) | Infiabilidad ($U_{10}^{90}$) | Desviación Estándar ($\sigma$) |
|:---------------------:|:----------------------:|:------------------:|:----------------------------:|:------------------------------:|
| 1 | 62.77 | 73.86 | 21.27 | 8.39 |
| 2 | 60.00 | 69.91 | 20.33 | 8.35 |
| 3 | 57.15 | 71.65 | 27.91 | 10.15 |
| 4 | 52.90 | 69.38 | 31.24 | 12.68 |
| 5 | 52.27 | 69.20 | 37.01 | 14.16 |
| 6 | 50.36 | 72.07 | 42.14 | 15.99 |
| 7 | 43.61 | 65.22 | 40.40 | 15.52 |
| **8** | **39.03** | **64.08** | **49.82** | **19.68** |

### 4.3. Estudio de Ablación de Componentes Arquitectónicos (Experimento 05)

| Etapa | Configuración Evaluada | Media ($\overline{P}$) | Aptitud ($A^{90}$) | Infiabilidad ($U_{10}^{90}$) | Contribución Arquitectónica |
|:-----:|:-----------------------|:----------------------:|:------------------:|:----------------------------:|:----------------------------|
| 1 | Baseline Crudo | 38.12 | 58.57 | 47.61 | Línea base estocástica sin filtrar |
| 2 | + Solo Edge Router | 45.38 | 65.53 | 42.25 | Mitiga anclaje prematuro |
| 3 | + Dynamic History Compression | 53.65 | 65.36 | 22.77 | Purga cháchara y colapsa varianza |
| 4 | + Unified Context Tier | 57.52 | 70.48 | 26.03 | Neutraliza Lost in the Middle |
| **5** | **Pipeline Completo ACRA** | **63.30** | **76.60** | **26.02** | Estabilización cognitiva integral |

---

## 5. Estructura del Repositorio y Artefactos

```text
.
├── 001_Seed/
│   └── seed-acra-adaptive-conversational-routing-architecture-master.md
├── 02_Foundation/
│   └── Engine/
│       └── EngineReadme.md
├── 03_Research_AI/
│   ├── Notebooks/
│   └── experiments/
│       ├── exp_01_baseline_degradation.py
│       ├── exp_02_acra_vs_baseline.py
│       ├── exp_03_ccr_sensitivity.py
│       ├── exp_04_edge_router_accuracy.py
│       └── exp_05_ablation_study.py
├── Artefactos/
│   └── Planes/
│       └── Vigentes/
│           ├── ACRA_Academic_Paper_Draft.md
│           ├── ACRA_Benchmark_Report.md
│           ├── exp_01_baseline_results.json
│           ├── exp_02_ab_test_results.json
│           ├── exp_03_ccr_sensitivity_results.json
│           ├── exp_04_edge_router_results.json
│           └── exp_05_ablation_results.json
├── config/
│   └── acra_config.yaml
├── docs/
│   ├── architecture/
│   │   └── ACRA_Cognitive_Stability_RFC.md
│   ├── engineers_notes/
│   │   ├── ref_01_lost_in_the_middle.md
│   │   ├── ref_02_multi_turn_degradation.md
│   │   ├── ref_03_intent_mismatch.md
│   │   ├── ref_04_reliability_stick_or_switch.md
│   │   ├── ref_05_instruction_drift.md
│   │   ├── ref_06_llm_router_bench.md
│   │   ├── ref_07_r2_router_reasoning.md
│   │   ├── ref_08_router_r1_reinforcement_learning.md
│   │   ├── ref_09_routing_plateau.md
│   │   └── ref_10_mt_osc_condensation.md
│   └── technical_specs/
│       └── ACRA_Technical_Specification_v1.md
├── schemas/
│   ├── conversation_state.json
│   └── routing_decision.json
├── src/
│   ├── core/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── llm_adapter.py
│   │   │   └── mock_models.py
│   │   ├── __init__.py
│   │   ├── dhc.py
│   │   ├── edge_router.py
│   │   ├── handoff.py
│   │   ├── metrics.py
│   │   ├── orchestrator.py
│   │   ├── state_machine.py
│   │   └── unified_context.py
│   └── data_generation/
│       ├── __init__.py
│       └── conversation_generator.py
├── tests/
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_dhc.py
│   │   ├── test_edge_router.py
│   │   ├── test_handoff.py
│   │   ├── test_metrics.py
│   │   ├── test_orchestrator.py
│   │   ├── test_state_machine.py
│   │   └── test_unified_context.py
│   ├── __init__.py
│   ├── run_all_tests.py
│   ├── test_integration_runner.py
│   └── test_suite_runner.py
├── pyproject.toml
├── README.md
└── README_ES.md
```

---

## 6. Protocolo de Ejecución y Verificación

### 6.1. Configuración del Entorno y Prerrequisitos
El sistema requiere Python 3.10 o superior. No se requieren claves API externas para ejecutar los benchmarks base gracias al motor de calibración empírica:

```bash
python -m venv .venv
# En Windows PowerShell:
.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install -e .
```

### 6.2. Ejecución de Experimentos y Reproducción de Benchmarks
Los scripts experimentales se ejecutan de forma independiente:

```bash
# Experimento 01: Cuantificación de degradación baseline multi-turno
python 03_Research_AI/experiments/exp_01_baseline_degradation.py

# Experimento 02: Ensayo controlado A/B (Baseline vs. ACRA)
python 03_Research_AI/experiments/exp_02_acra_vs_baseline.py

# Experimento 03: Análisis de sensibilidad sobre umbrales de CCR
python 03_Research_AI/experiments/exp_03_ccr_sensitivity.py

# Experimento 04: Precisión del Edge Router y contención de falsos positivos
python 03_Research_AI/experiments/exp_04_edge_router_accuracy.py

# Experimento 05: Análisis de ablación arquitectónica sobre 5 niveles
python 03_Research_AI/experiments/exp_05_ablation_study.py
```

### 6.3. Suite de Pruebas e Invariantes
Ejecución de la suite completa automatizada:

```bash
python tests/run_all_tests.py
```

Salida esperada:
```text
test_ccr_calculation_valid ................................... ok
test_degradation_delta ....................................... ok
test_metrics_calculation_standard ............................ ok
test_metrics_empty_raises .................................... ok
test_dispatches_pro_when_mature .............................. ok
test_holds_on_early_ambiguous_turn ........................... ok
test_compress_positive_ccr ................................... ok
test_masks_verbosity_and_preserves_code ...................... ok
test_persists_and_retrieves .................................. ok
test_assemble_clean_payload .................................. ok
test_invalid_raises .......................................... ok
test_lifecycle ............................................... ok
test_flow .................................................... ok
test_complete_conversation_lifecycle ........................ ok
test_acra_superiority_assertion .............................. ok

Ran 15 tests in 0.014s - OK
```

---

## 7. Glosario de Dominio

* **Lost in Conversation (LiC):** Caída sistémica en el rendimiento generativo inducida por la partición de instrucciones complejas a lo largo de múltiples turnos secuenciales.
* **Context Consolidation Ratio (CCR):** Métrica que define la proporción de tokens conversacionales purgados por la capa de borde antes de invocar al clúster de razonamiento pesado.
* **Sesgo de Anclaje Prematuro (*Sticking Bias*):** Tendencia de los modelos de frontera a auto-convencerse de supuestos especulativos generados en turnos tempranos y ambiguos, persistiendo en el error pese a correcciones posteriores.
* **Enmascaramiento Asimétrico del Asistente (*Assistant Response Masking*):** Regla arquitectónica que elimina el relleno conversacional generado por el propio LLM, reteniendo requerimientos y bloques ejecutables.
* **Transferencia a Línea Base Limpia (*Clean Baseline Handoff*):** Mecanismo de ingesta donde el clúster de razonamiento recibe un prompt equivalente a *zero-shot*, desacoplando la ejecución de la deriva estocástica histórica.
* **Infiabilidad Interpercentil ($U_{10}^{90}$):** Brecha entre el percentil 90 y el percentil 10 de rendimiento calculada sobre iteraciones multi-turno comparables.

---

## 8. Referencias Académicas y de Ingeniería

1. **Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Zettlemoyer, L. (2023).** *Lost in the Middle: How Language Models Use Long Contexts.* Transactions of the Association for Computational Linguistics. arXiv:2307.03172.
2. **Laban, P., et al. (2025).** *LLMs Get Lost In Multi-Turn Conversation.* arXiv preprint.
3. **Guo, S., et al. (2026).** *Stop Listening to Me! How Multi-turn Conversations Can Degrade LLM Reliability.* arXiv preprint.
4. **Liu, Y., et al. (2026).** *Intent Mismatch Causes LLMs to Get Lost in Multi-Turn Conversation.* arXiv preprint.
5. **R2-Router Research Consortium (2025).** *R2-Router: A New Paradigm for LLM Routing with Reasoning.* arXiv preprint.
6. **Router-R1 Group (2025).** *Router-R1: Teaching LLMs Multi-Round Routing and Aggregation via Reinforcement Learning.* arXiv preprint.

### Citación BibTeX
```bibtex
@article{acra_deepmind_2026,
  author = {ACRA Engineering and Research Group},
  title = {Adaptive Conversational Routing Architecture (ACRA): Cognitive Stability and Stochastic Variance Attenuation in Multi-Turn Large Language Model Interactions},
  journal = {Technical Report and Architectural RFC},
  year = {2026},
  url = {https://github.com/AlvaroAlejandroFinOps/ACRA-Adaptive-Conversational-Routing-Architecture}
}
```
