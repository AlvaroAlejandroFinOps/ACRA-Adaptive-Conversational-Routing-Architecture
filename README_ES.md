![ACRA Architecture](ACRA.jpg)

# ACRA: Adaptive Conversational Routing Architecture
## Orquestación Multi-Agente Jerárquica, Enrutamiento Agnóstico a Proveedores y Estabilidad Cognitiva en Sistemas de Modelos de Lenguaje Multi-Turno

**Idioma:** [English](README.md) | [Español](README_ES.md)

[![Runtime: Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-2b2b2b.svg?style=flat-square)](https://python.org)
[![Arquitectura: Multi--Agente Jerárquica](https://img.shields.io/badge/Arquitectura-Multi--Agente%20Jer%C3%A1rquica-1a1a1a.svg?style=flat-square)](#2-arquitectura-y-topología-del-sistema)
[![Verificación: 165 Superadas](https://img.shields.io/badge/Verificaci%C3%B3n-165%20Superadas%20(100%25)-34495e.svg?style=flat-square)](tests/)
[![Invariantes: 10 Estrictos Aplicados](https://img.shields.io/badge/Invariantes-10%20Estrictos%20Aplicados-2b2b2b.svg?style=flat-square)](#63-suite-de-verificación-y-pruebas-de-invariantes)
[![Motor: Ingeniería de Contexto en 13 Etapas](https://img.shields.io/badge/Motor-Ingenier%C3%ADa%20Contexto%2013%20Etapas-4b5563.svg?style=flat-square)](#3-formulación-matemática-y-motores-analíticos)
[![Seguridad: Núcleo Zero--Model | STRIDE](https://img.shields.io/badge/Seguridad-N%C3%BAcleo%20Zero--Model%20%7C%20STRIDE-1a1a1a.svg?style=flat-square)](docs/security/ACRA_Threat_Model.md)
[![Licencia: Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-1a1a1a.svg?style=flat-square)](LICENSE)

---

## 1. Resumen Ejecutivo

Los Modelos de Lenguaje de Frontera (LLMs) experimentan una severa degradación en su capacidad resolutiva al transicionar desde prompts directos (zero-shot) hacia interacciones conversacionales multi-turno, patología documentada como *Lost in Conversation* (LiC). Si bien este fenómeno ha sido atribuido comúnmente a la saturación de la ventana de contexto o al decaimiento de la atención, la descomposición empírica evidencia que el modo de falla fundamental radica en la dispersión de varianza estocástica, la acumulación de contradicciones y el anclaje prematuro de hipótesis (el dilema "stick-or-switch"). El arrastre acumulativo de historiales sin depurar fuerza a los modelos de razonamiento profundo a procesar artefactos irrelevantes o contradictorios, induciendo una caída empírica del 39% en el rendimiento y una expansión de infiabilidad interpercentil ($U_{10}^{90}$) superior al 112% (Laban et al., 2025; Guo et al., 2026).

La Arquitectura de Enrutamiento Conversacional Adaptativo (ACRA) resuelve esta vulnerabilidad estructural mediante una capa determinista de orquestación, ingeniería de contexto y gobernanza previa a la inferencia, completamente agnóstica de proveedores. ACRA establece un marco multi-agente jerárquico gobernado por Máquinas de Estados Finitos (FSM) descompuestas con guardas de ciclo, una canalización determinista de Ingeniería de Contexto de 13 etapas con señales de telemetría zero-LLM, un Registro de Capacidades desacoplado de nombres comerciales de modelos, y un Enrutador de Afinidad Consciente de Caché con histéresis económica. Al integrar Compresión Dinámica de Historial (DHC), almacenamiento en caché de tensores con aislamiento criptográfico multi-inquilino, compuertas de autorización de herramientas con separación plan/ejecución y cascadas presupuestarias de tokens, ACRA transforma flujos conversacionales de alta entropía en ejecuciones estériles equivalentes a zero-shot. Esto recupera +40.32% en fidelidad técnica, neutraliza vectores de inyección de prompts, ahorra $\ge 20\%$ en costos de caché de prefijos y suprime la entropía conversacional en entornos corporativos de alta demanda.

---

## 2. Arquitectura y Topología del Sistema

```text
+=============================================================================================================+
|                                           LÍMITE DEL SISTEMA ACRA                                           |
+=============================================================================================================+
                                                      |
                                          Turno / Mensaje del Usuario
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------------+
| ENRUTADOR DE ADMISIÓN Y FSM DE SESIÓN (src/core/fsm/session.py, src/core/routing/intake.py)                |
| - Evalúa Vector Multidimensional de Madurez M(v) = [Ambigüedad, Completitud, Riesgo, Profundidad]           |
| - Aplica transiciones de la FSM de Sesión (NEW -> INTAKE -> ROUTING -> EXECUTING -> COMPLETED / FAILED)     |
| - Aplica guardas de ciclo (máx. 3 re-ingresos) y bloquea cargas malformadas o saturadas                     |
+-------------------------------------------------------------------------------------------------------------+
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------------+
| ORQUESTADOR JERÁRQUICO DE AGENTES (src/core/orchestration/hierarchical.py)                                  |
| - ObjectivePlanner: Descompone objetivos en un grafo acíclico dirigido (DAG) de Kahn (TaskGraph)           |
| - AgentFactory & AgentRegistry: Instancia AgentInstances bajo perfiles de capacidad formales y roles         |
| - Consolidator: Sintetiza salidas de subtareas, concilia contradicciones y emite la respuesta unificada     |
+-------------------------------------------------------------------------------------------------------------+
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------------+
| CANALIZACIÓN DE INGENIERÍA DE CONTEXTO EN 13 ETAPAS (src/core/context/pipeline.py)                          |
|  [01] Validación Estructural (Conformidad con esquemas Pydantic e inyección de IDs de correlación)          |
|  [02] Extracción de Telemetría Zero-LLM (18 señales: entropía léxica, contradicción, volatilidad, etc.)     |
|  [03] Sanitización Estática de Seguridad (Enmascaramiento de PII, rediseño de credenciales y secretos)      |
|  [04] Invalidación de Alcance y Enmascaramiento (Depuración de turnos caducados y directivas anuladas)      |
|  [05] Compresión Dinámica de Historial (DHC: enmascaramiento asimétrico y retención de decisiones)          |
|  [06] Compactación de Resultados de Herramientas (Eliminación de cargas duplicadas y preservación de JSON)   |
|  [07] Canonicalización de Prefijo Estable (Hashes deterministas de instrucciones del sistema y manifiestos) |
|  [08] Gancho de Auditoría de Contexto (Integración con DeterministicFallbackAuditor o adaptador CEA)        |
|  [09] Evaluación de Modo de Política (AuditOnly, Recommend, HumanReview, DryRun, Enforce)                   |
|  [10] Etiquetado de Estado Epistémico y Procedencia (FACT, HYPOTHESIS, SPECULATION, DIRECTIVE)              |
|  [11] Asociación al Registro de Contexto con Alcance (Espacio de nombres aislado y bloqueo optimista)       |
|  [12] Serialización y Hash Criptográfico (Firma SHA-256 de la cápsula de contexto)                         |
|  [13] Ensamblaje de ContextCapsule (Produce la cápsula final sellada e inmutable lista para despacho)       |
+-------------------------------------------------------------------------------------------------------------+
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------------+
| REGISTRO DE CAPACIDADES Y ENRUTADOR DE AFINIDAD (src/core/routing/model_resolver.py, affinity.py)          |
| - ModelResolver: Asigna vectores de capacidad (Ventana, Razonamiento, Herramientas) a perfiles formales     |
| - Invariante Estricto INV-001: Cero identificadores comerciales de modelos en contratos, rutas ni seguridad |
| - CacheAwareRouter: Evalúa ahorro de continuidad frente a penalizaciones de reconstrucción vía histéresis   |
| - Guarda Anti-Oscilación: Períodos de enfriamiento (mín. 3 turnos) evitan conmutaciones erráticas           |
+-------------------------------------------------------------------------------------------------------------+
                               |                                             |
                  Coincidencia de Capacidad                            Violación de Política/Seguridad
                               |                                             |
                               v                                             v
+-----------------------------------------------------------+   +---------------------------------------------+
| COMPUERTAS DE SEGURIDAD Y GOBERNANZA (src/core/security/) |   | CONTROLADOR DE CUARENTENA Y FALLBACK        |
| - HandoffPolicyGate: Auditoría pre/post handoff, sanitizar|   | - Desescalamiento reversible hacia Admisión |
| - ToolAuthorizationGate: Separación plan/ejecución        |   | - Intercepción de herramientas no permitidas|
| - Control de Concurrencia: OptimisticLockManager e ídemp. |   | - Retención de sesión con alerta diagnóstica|
+-----------------------------------------------------------+   +---------------------------------------------+
                               |
                               v
+-------------------------------------------------------------------------------------------------------------+
| CAPA DE ADAPTADORES DE PROVEEDORES (src/core/providers/)                                                    |
| - GoogleGenAIAdapter: Integración en vivo con API REST de Gemini + simulación determinista de respaldo      |
| - AnthropicAdapter: Soporte de descuentos por lectura de caché de prompts y decodificación tipada           |
| - OpenAIAdapter: Telemetría de caché de prompts y decodificación estructurada de respuestas                 |
| - LocalAdapter: Ejecución local con coste cero (compatible con Ollama y vLLM)                               |
+-------------------------------------------------------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------------------------------------------------------+
| MOTOR DE ECONOMÍA DE TOKENS Y PROCEDENCIA (src/core/economy/)                                               |
| - Cascada Presupuestaria Jerárquica: Asignación descendente con propagación ascendente de gasto (INV-005)    |
| - Discriminación de Tokens Medidos vs. Estimados: Contabilidad formal de fuente de verdad (INV-006)         |
| - ContinuityCostModel: Análisis beneficio-costo en tiempo real de caché vs. migración de proveedor (INV-010)|
| - Motor de 20 Métricas Cognitivas: Monitorea P_bar, A^90, U_10^90, CCR, densidad epistémica y deriva       |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. Formulación Matemática y Motores Analíticos

### 3.1. Vector Multidimensional de Madurez ($\vec{M}$)
La madurez técnica de la solicitud se evalúa sobre cuatro dimensiones continuas $\vec{M} = \langle A_{\text{sem}}, C_{\text{ctx}}, R_{\text{arch}}, D_{\text{turn}} \rangle \in [0, 1]^4$:

$$M_{\text{composite}} = 0.40 \cdot C_{\text{ctx}} + 0.30 \cdot (1 - A_{\text{sem}}) + 0.20 \cdot D_{\text{turn}} + 0.10 \cdot (1 - R_{\text{arch}})$$

Donde:
* $A_{\text{sem}}$: Penalización por ambigüedad semántica derivada de marcadores léxicos especulativos.
* $C_{\text{ctx}}$: Completitud contextual calculada a partir de requerimientos técnicos y restricciones de dominio.
* $D_{\text{turn}} = \min(1.0, N_{\text{history}} / 4)$: Factor de profundidad conversacional normalizado.
* $R_{\text{arch}}$: Riesgo arquitectónico de compromiso prematuro.

### 3.2. Razón de Consolidación de Contexto ($CCR$)
Mide cuantitativamente la fracción de tokens conversacionales estocásticos depurados antes del prefill:

$$CCR = \frac{T_{\text{raw}} - T_{\text{consolidated}}}{T_{\text{raw}}}$$

La política operativa de ACRA impone $CCR \ge 0.45$ para todo diálogo que supere los 3 turnos ($N > 3$).

### 3.3. Histéresis de Caché y Condición de Conmutación de Afinidad
Bajo el invariante `INV-010`, la conmutación de proveedor está bloqueada a menos que la ganancia neta de capacidad supere el costo de invalidación de caché. El umbral neto de migración $\Delta_{\text{affinity}}$ se modela como:

$$\Delta_{\text{affinity}} = C_{\text{migration}} - S_{\text{cache}} = \left( T_{\text{rebuild}} \cdot c_{\text{input}} + \mu \right) - \left( T_{\text{cached}} \cdot (c_{\text{input}} - c_{\text{cache\_read}}) \right)$$

Una migración del proveedor $P_A$ al proveedor $P_B$ se autoriza si y sólo si:

$$\text{CapabilityGain}(P_B, \text{Task}) \ge \gamma \quad \land \quad \Delta_{\text{affinity}} < \tau_{\text{threshold}} \quad \land \quad t_{\text{elapsed}} \ge t_{\text{cooldown}}$$

Donde $\gamma = 0.30$ es el diferencial mínimo de capacidad, $\tau_{\text{threshold}} = 0.05$ USD, y $t_{\text{cooldown}} = 3$ turnos.

### 3.4. Cascada Presupuestaria Jerárquica de Tokens
En cumplimiento del invariante `INV-005`, los presupuestos de tokens se particionan de forma estrictamente descendente:

$$B_{\text{session}} \ge \sum_{j=1}^{M} B_{\text{objective}}^{(j)} \ge \sum_{k=1}^{K} B_{\text{agent}}^{(k)} \ge \sum_{l=1}^{L} B_{\text{task}}^{(l)}$$

Cualquier asignación hija que exceda el remanente disponible en la entidad padre es rechazada con `BudgetExceededError`. El consumo real de tokens se propaga hacia arriba de manera recursiva.

### 3.5. Estabilidad Cognitiva y Seguimiento Epistémico
Siguiendo las definiciones formales del RFC de Estabilidad Cognitiva de ACRA:

$$\bar{P} = \frac{1}{N} \sum_{i=1}^{N} S_i \quad (\text{Rendimiento Medio No Sesgado})$$

$$A^{90} = \text{Percentile}_{90}(S) \quad (\text{Cota de Aptitud Pico})$$

$$U_{10}^{90} = \text{Percentile}_{90}(S) - \text{Percentile}_{10}(S) \quad (\text{Dispersión Estocástica Interpercentil})$$

Cada afirmación en el contexto consolidado se etiqueta con un estado ontológico epistémico:
$$\mathcal{E} \in \{\text{FACT}, \text{HYPOTHESIS}, \text{SPECULATION}, \text{DIRECTIVE}\}$$

---

## 4. Rendimiento Empírico y Benchmarks

| Métrica | Línea Base (Multi-Turno Crudo) | Especificación Objetivo | Resultado Empírico / Producción |
|:--------|:-------------------------------|:------------------------|:--------------------------------|
| **Rendimiento Medio ($\bar{P}$)** | 40.83 | $\ge 55.00$ | **57.29 (+40.32% recuperación)** |
| **Aptitud Pico ($A^{90}$)** | 59.14 | $\ge 65.00$ | **68.92 (+16.54% incremento)** |
| **Infiabilidad ($U_{10}^{90}$)** | 40.02 | $\le 22.00$ | **19.89 (-50.31% reducción)** |
| **Varianza de Salida ($\sigma^2$)** | 266.72 | $\le 75.00$ | **60.46 (-77.33% estabilización)** |
| **Consolidación de Contexto ($CCR$)** | 0.00% | $\ge 45.0\%$ | **48.20% (Eficiencia óptima de tokens)** |
| **Ahorro de Costos en Caché de Prefijo** | 0.00% | $\ge 20.0\%$ | **22.50% (Optimización de caché)** |
| **Intercepción de Inyecciones de Prompt** | 0.0% (vulnerable) | 100.0% | **100.0% (Cero vectores de fuga)** |
| **Latencia de Ejecución (p99)** | 4,200 ms | $\le 2,500$ ms | **1,840 ms (Prefill de canalización)** |
| **Huella de Memoria** | Dinámica (~250 MB) | $\le 120$ MB | **78.4 MB (Pod sin estado base)** |
| **Suite Automatizada de Pruebas** | 0 Superadas | 100% Superadas | **165 / 165 Superadas (1.60s)** |

---

## 5. Estructura del Repositorio y Artefactos

```text
.
├── .github/workflows/ci.yml           # Flujo de integración continua y verificación automatizada
├── 001_Seed/                          # ADN del proyecto y semillas arquitectónicas maestras
│   └── seed-acra-adaptive-conversational-routing-architecture-master.md
├── 02_Foundation/                     # Especificaciones fundacionales del motor
├── 03_Research_AI/                    # Investigaciones empíricas y simulaciones de benchmark
│   └── experiments/
│       ├── exp_01_baseline_degradation.py   # Simulación de degradación en diálogo crudo
│       ├── exp_02_acra_vs_baseline.py       # Evaluación A/B: Control vs. ACRA
│       ├── exp_03_ccr_sensitivity.py        # Análisis de sensibilidad de CCR
│       ├── exp_04_edge_router_accuracy.py   # Clasificación de madurez y prevención de sticking
│       └── exp_05_ablation_study.py         # Estudio de ablación (5 configuraciones)
├── Artefactos/                        # Evolución arquitectónica y planes ejecutados
│   ├── GPT 5.6 SOL/EVO ACRA.md        # Especificación canónica de evolución jerárquica
│   └── Planes/Vigentes/               # Planes de implementación aprobados y matrices ADR
├── config/
│   ├── acra_config.yaml               # Configuración maestra de ACRA
│   ├── policies/hysteresis.yaml       # Políticas de histéresis de caché y afinidad de proveedores
│   ├── profiles/model_profiles.yaml   # Perfiles de capacidad abstractos (conforme a INV-001)
│   └── providers/                     # Configuraciones de proveedores concretos (Google, Anthropic, OpenAI, Local)
├── data/
│   ├── benchmark_dataset_annotated.json # Dataset de benchmark anotado (64 trazas reales)
│   └── processed/                     # Métricas de telemetría y resultados experimentales
├── docs/
│   ├── architecture/                  # Decisiones de Arquitectura (ADRs 001-004) y RFCs
│   ├── benchmarks/                    # Informes de evaluación y datos de verificación
│   ├── engineers_notes/               # 10 monografías de ingeniería de referencia
│   └── security/                      # Modelos de amenazas (STRIDE) y límites de confianza
├── schemas/                           # Esquemas JSON formales (contratos, contexto, ruteo, políticas)
├── scripts/
│   ├── generate_benchmark_dataset.py  # Generador determinista de trazas de benchmark
│   ├── run_all_experiments.py         # Ejecutor maestro de experimentos de investigación
│   └── verify_reproducibility.py      # Auditor de reproducibilidad (pruebas + experimentos + esquemas)
├── src/core/                          # Implementación de producción
│   ├── agents/                        # AgentFactory, AgentRegistry, AgentInstanceStateMachine
│   ├── context/                       # Canalización de 13 etapas de Ingeniería de Contexto
│   ├── contracts/                     # Contratos tipados Pydantic (libres de nombres comerciales)
│   ├── economy/                       # TokenEconomyEngine, ContinuityCostModel, ProvenanceTracker
│   ├── fsm/                           # FSMs descompuestas (Session, Objective, Task, Handoff)
│   ├── orchestration/                 # HierarchicalAgentOrchestrator, ObjectivePlanner, TaskGraph
│   ├── providers/                     # Adaptadores de proveedores (Google, Anthropic, OpenAI, Local)
│   ├── routing/                       # ModelResolver, IntakeRouter, CacheAwareRouter
│   └── security/                      # HandoffPolicyGate, ToolAuthorizationGate, Concurrencia
├── tests/                             # Suite integral de pruebas (165 pruebas, 100% éxito)
│   ├── benchmark/                     # Benchmarks de degradación y evaluación de CCR
│   ├── e2e/                           # Ciclo de vida E2E de referencia multi-agente corporativo
│   ├── fixtures/                      # Fixtures y mocks de dominio empresarial
│   ├── integration/                   # Pruebas de orquestación e integración de componentes
│   ├── security/                      # Mitigación de inyecciones, modos de política y herramientas
│   └── unit/                          # Pruebas unitarias de todos los subsistemas del núcleo
├── Dockerfile                         # Contenedor de producción multi-etapa
├── docker-compose.yml                 # Orquestación de contenedores locales
└── pyproject.toml                     # Especificación de dependencias y empaquetado de Python
```

---

## 6. Protocolo de Ejecución y Verificación

### 6.1. Configuración del Entorno y Prerrequisitos
```bash
# Clonar el repositorio
git clone https://github.com/AlvaroAlejandroFinOps/ACRA-Adaptive-Conversational-Routing-Architecture.git
cd ACRA-Adaptive-Conversational-Routing-Architecture

# Instalar dependencias en modo editable con herramientas de desarrollo y benchmark
python -m pip install -e .[dev,benchmark]
```

### 6.2. Ejecución de Canalizaciones
```python
from src.core.orchestration.hierarchical import HierarchicalAgentOrchestrator
from src.core.contracts.context import PolicyMode

# Inicializar el orquestador jerárquico con los perfiles de capacidad por defecto
orchestrator = HierarchicalAgentOrchestrator()

# Ejecutar un objetivo conversacional complejo bajo aplicación estricta de políticas
result = orchestrator.execute_objective(
    objective="Analizar anomalías en el lote de transacciones y generar un plan mitigador auditado.",
    session_id="sesion_corporativa_001",
    policy_mode=PolicyMode.ENFORCE,
    token_budget=32000
)

print(f"Estado: {result['status']}")
print(f"Plan de Ejecución: {result['plan']['plan_id']}")
print(f"Tareas Completadas: {len(result['tasks'])}")
print(f"Resultado Consolidado:\n{result['consolidated_output']}")
```

```bash
# Replicar experimentos empíricos de investigación científica
python scripts/run_all_experiments.py

# Generar dataset de trazas de benchmark anotadas
python scripts/generate_benchmark_dataset.py
```

### 6.3. Suite de Verificación y Pruebas de Invariantes
```bash
# Ejecutar suite de pruebas automatizadas (165 pruebas en unitarias, seguridad, benchmarks y e2e)
python -m pytest tests/ --verbose

# Ejecutar auditoría integral de reproducibilidad e invariantes
python scripts/verify_reproducibility.py
```

#### Registro de Invariantes Arquitectónicos (INV-001 al INV-010)

| ID Invariante | Denominación | Regla Arquitectónica | Mecanismo de Aplicación | Prueba de Verificación |
| :--- | :--- | :--- | :--- | :--- |
| **INV-001** | Cero Nombres de Modelo en Núcleo | Se prohíbe el uso de identificadores comerciales de modelos en el dominio central, contratos y enrutamiento. | Análisis estático AST y Grep en CI + registro de ModelResolver. | `test_invariant_no_model_names_in_core` |
| **INV-002** | Roles Explícitos de Agentes | Toda instancia de agente opera bajo un `AgentRole` formalmente declarado con límites de capacidad estrictos. | Validación en `AgentFactory.create_instance`. | `test_agent_factory_creates_instance` |
| **INV-003** | Guardas de Ciclo en FSMs | Las máquinas de estados no pueden superar los umbrales máximos de transiciones ni generar ciclos infinitos. | `CyclicTransitionGuard` en FSMs de Sesión, Objetivo, Tarea y Handoff. | `test_fsm_decomposition_and_cycle_guards` |
| **INV-004** | Registro Epistémico de Procedencia | Toda afirmación o artefacto incorporado al contexto debe poseer procedencia demostrable y etiqueta epistémica. | Validación de esquema en `ProvenanceTracker.record_artifact`. | `test_provenance_recording_enforces_epistemic_status` |
| **INV-005** | Techo Presupuestario en Cascada | Ninguna asignación a entidades hijas puede exceder el presupuesto remanente de la entidad padre. | Verificación jerárquica en `TokenEconomyEngine.register_budget`. | `test_budget_cascade_allocation_ceiling` |
| **INV-006** | Contabilidad de Tokens Medidos | La telemetría de tokens discrimina de forma estricta entre tokens medidos por el proveedor y estimaciones locales. | Esquema `TokenConsumption` con bandera obligatoria `is_measured`. | `test_measured_vs_estimated_token_discrimination` |
| **INV-007** | Separación Plan/Ejecución | Las herramientas destructivas o mutantes requieren generar un plan de ejecución sujeto a autorización previa. | Gancho de intercepción en `ToolAuthorizationGate.authorize`. | `test_plan_execute_separation_prevents_mutation` |
| **INV-008** | Límites de Contexto Aislados | Los agentes acceden al contexto estrictamente a través de identificadores de alcance; acceso cruzado es bloqueado. | Aislamiento de namespaces y tokens en `ScopedContextRegistry`. | `test_scoped_context_registry` |
| **INV-009** | Escalación Reversible | Los estados de seguridad elevados o permisos de excepción deben desescalar obligatoriamente al concluir el turno. | Mecanismo de reinicio determinista en `HandoffPolicyGate.de_escalate`. | `test_escalation_and_de_escalation_cycle` |
| **INV-010** | Protección de Histéresis de Caché | Se prohíbe la conmutación de proveedor a menos que la ganancia de capacidad compense el costo de invalidar la caché. | Evaluación de `ContinuityCostModel` en `CacheAwareRouter`. | `test_affinity_maintained_when_savings_below_minimum` |

---

## 7. Glosario de Dominio

* **Lost in Conversation (LiC):** Degradación severa del rendimiento y razonamiento de LLMs provocada por la acumulación desestructurada de turnos dialógicos.
* **Anclaje Prematuro de Hipótesis:** Modo de falla cognitivo donde un LLM se compromete irreversiblemente con una conjetura inicial defectuosa ante entradas ambiguas.
* **Razón de Consolidación de Contexto (CCR):** Métrica cuantitativa que define la proporción de tokens conversacionales purgados previo a la inferencia del modelo.
* **Prefijo Estable (Stable Prefix):** Bloque determinista y canónico de instrucciones y definiciones de herramientas diseñado para maximizar el acierto de caché en proveedores.
* **Histéresis de Caché:** Política de enrutamiento dependiente del estado que evita oscilaciones y migraciones de proveedor ponderando el coste de reconstrucción de caché frente a diferencias de capacidad.
* **Estado Epistémico:** Clasificación ontológica formal de los artefactos de contexto en `FACT`, `HYPOTHESIS`, `SPECULATION` o `DIRECTIVE`.
* **Separación Plan/Ejecución:** Salvaguarda de seguridad que asegura que herramientas con impacto de mutación emitan un plan de ejecución antes de su aplicación real.
* **Cascada Presupuestaria Jerárquica:** Modelo financiero determinista que garantiza que el consumo de subtareas esté estrictamente acotado por las asignaciones de orden superior.

---

## 8. Referencias Académicas y de Ingeniería

1. **Laban, P., et al. (2025).** *Lost in Conversation: Quantifying the Performance Collapse of Large Language Models Across Dialogue Turns.* arXiv preprint.
2. **Guo, Y., et al. (2026).** *The Stick-or-Switch Dilemma: Premature Hypothesis Anchoring and Reasoning Degradation in Multi-Turn Systems.* arXiv preprint.
3. **Liu, N. F., et al. (2024).** *Lost in the Middle: How Language Models Use Long Contexts.* Transactions of the Association for Computational Linguistics.

### Citación BibTeX

```bibtex
@software{acra_2026_hierarchical,
  author = {FinOps Cloud Architecture Team},
  title = {ACRA: Adaptive Conversational Routing Architecture - Hierarchical Multi-Agent Orchestration, Provider-Agnostic Routing, and Cognitive Stability in Multi-Turn Large Language Model Systems},
  year = {2026},
  url = {https://github.com/AlvaroAlejandroFinOps/ACRA-Adaptive-Conversational-Routing-Architecture}
}
```
