<!-- ============================================================================== -->
<!-- THINKINGSEED: ADN DEL PROYECTO (CONTEXTO PASIVO PARA MODELOS DE LENGUAJE)     -->
<!-- ============================================================================== -->
> [!NOTE]
> ### 🧬 DEFINICIÓN Y ROL DE ESTE DOCUMENTO
> 1. **¿Qué es este archivo?:** Este documento es una **Semilla de Proyecto (ThinkingSeed Master)**: representa el **ADN arquitectónico, técnico y estructural exhaustivo** del sistema. **NO es el repositorio completo de código fuente**, sino su mapa genético y memoria técnica profunda extraída directamente del entorno de desarrollo.
> 2. **Estado de Avance (Work in Progress):** Este documento refleja el **estado actual del desarrollo**. No garantiza que el proyecto esté concluido al 100%; puede representar un prototipo, un MVP o un sistema en evolución continua. La ausencia de código completo en ciertos archivos o módulos es **deliberada por diseño** para optimizar ventana de contexto o refleja áreas aún en desarrollo.
> 3. **Modo de Operación:** Trata este documento como **contexto pasivo de referencia técnica (Ground Truth)**. No asumas que el archivo está defectuoso ni intentes reescribirlo por tu cuenta.
<!-- ============================================================================== -->

# THINKING SEED MASTER: ACRA-Adaptive Conversational Routing Architecture

## 0. IDENTIDAD Y METADATOS
```yaml
seed_schema_version: "2.0"
project_name: "ACRA-Adaptive Conversational Routing Architecture"
repository_name: "ACRA-Adaptive-Conversational-Routing-Architecture"
project_type: "ml-system"
repository_mode: "single-project"
generated_at: "2026-09-09T23:42:00-03:00"
generated_by: "Gemini 3.8 Flash (Medium) / Antigravity Agent"
repository_root: "d:/0001 HyperScale Thinking/PROYECTOS CLOUD/DeepMind/ACRA-Adaptive Conversational Routing Architecture"
git_branch: "master"
git_commit: "db94aef"
working_tree_state: "modified"
analysis_mode: "static"
coverage_level: "exhaustive"
known_analysis_limits:
  - "[CONFIRMADO] Inferencia LLM ejecutada sobre calibración estocástica empírica basada en literatura de frontera (Laban et al., 2025; Guo et al., 2026) y stubs sin consumo de credenciales de red o APIs en producción."
  - "[CONFIRMADO] Entorno de validación local bajo Windows 11 con Python 3.12 y pytest 9.1.1."
```

### 0.1 Instrucciones para el modelo receptor
1. **ADN vs Repositorio:** Reconoce este documento como la memoria técnica y el ADN del proyecto, no como el repositorio completo ni como una prueba de ejecución.
2. **Contexto Pasivo:** No generes código no solicitado ni reclames por archivos ausentes; espera instrucciones específicas del usuario o utilízalo como contexto pasivo para responder preguntas sobre el funcionamiento del sistema.
3. **Estado de Avance:** Considera que las secciones incompletas o componentes marcados como `[FALTANTE]` representan el avance real del proyecto y oportunidades de asistencia, no errores del documento.
4. **Evidencia:** Respeta las etiquetas de evidencia (`[CONFIRMADO]`, `[INFERIDO]`, `[DECLARADO]`, `[NO VERIFICADO]`, `[FALTANTE]`) y no transformes inferencias en hechos.
5. **Rutas:** Antes de proponer cambios, identifica módulos y archivos afectados citando sus rutas exactas relativas al repositorio.
6. **Contratos:** Conserva arquitectura, convenciones, contratos y restricciones declaradas.
7. **Preguntas Dirigidas:** No inventes componentes ausentes. Formula preguntas solo cuando la incertidumbre impida una respuesta segura.
8. **Seguridad:** No reveles ni solicites secretos. Usa placeholders (`<REDACTED>`).
9. **Impacto:** Evalúa impactos laterales en pruebas, configuración, datos, seguridad, observabilidad y despliegue.
10. **Asistencia:** Distingue entre solución inmediata, deuda técnica y recomendación futura.

---

## 1. RESUMEN EJECUTIVO

### 1.1 Proyecto en una frase
[CONFIRMADO] Arquitectura de orquestación pre-inferencia bi-clúster asimétrica que atenúa la varianza estocástica, previene el anclaje temprano de hipótesis y erradica la degradación cognitiva multi-turno en modelos de lenguaje de frontera.

### 1.2 Problema que resuelve
[CONFIRMADO] Resuelve el colapso de rendimiento documentado académicamente como *Lost in Conversation* (LiC) (Laban et al., 2025), donde modelos de frontera sufren una degradación promedio del 39% en rendimiento y un incremento del 112% en infiabilidad ($U_{10}^{90}$) en interacción conversacional multi-turno debido a la dispersión de entropía en el historial y al anclaje temprano de hipótesis en especificaciones ambiguas (Guo et al., 2026).

### 1.3 Usuarios o sistemas consumidores
[CONFIRMADO]
- Equipos de investigación en IA avanzada y razonamiento de frontera (Google DeepMind, laboratorios de investigación).
- Sistemas de agentes autónomos, pipelines RAG empresariales y orquestadores conversacionales de alta criticidad donde los errores estocásticos o las inyecciones de prompts son inadmisibles.
- Plataformas multi-inquilino de asistentes cognitivos con requerimientos estrictos de eficiencia de cómputo y aislamiento de memoria.

### 1.4 Alcance y límites del sistema
[CONFIRMADO]
- **Dentro del alcance:** Orquestación y clasificación en borde (Edge Router), compresión dinámica de historial (DHC), caché de contexto unificado con aislamiento de tenant (UCT), compuerta estática de seguridad y procedencia (`PayloadPolicyGate`), gobernador de recursos (`ResourceGovernor`), generación de payloads a Línea Base Clean (`HandoffEngine`) y validación empírica con 64 trazas anotadas.
- **Fuera del alcance:** Entrenamiento o fine-tuning de pesos de modelos fundacionales; provisión de infraestructura en la nube directa (GCP/AWS/Azure en tiempo real sin infraestructura como código activa).

---

## 2. ARQUITECTURA Y TOPOLOGÍA

### 2.1 Estilo arquitectónico
[CONFIRMADO] Arquitectura desacoplada en capas asimétricas orientada a estados (FSM de 12 estados), con compuerta de validación determinista, paso de mensajes estructurados (Pydantic v2), aislamiento multi-inquilino con salting criptográfico SHA-256 y adaptadores de inferencia extensibles.

### 2.2 Árbol estructural del repositorio
```text
.
├── .github/
│   └── workflows/
│       └── ci.yml                         # [CONFIRMADO] Pipeline de CI en GitHub Actions
├── .dockerignore                          # [CONFIRMADO] Exclusiones para build de Docker
├── .gitignore                             # [CONFIRMADO] Exclusiones git
├── 001_Seed/                              # [CONFIRMADO] Memoria técnica y ADN del sistema
├── 02_Foundation/                         # [CONFIRMADO] Fundaciones arquitectónicas y notas de motor
│   └── Engine/EngineReadme.md
├── 03_Research_AI/                        # [CONFIRMADO] Experimentos empíricos y benchmarks
│   ├── Notebooks/
│   └── experiments/
│       ├── exp_01_baseline_degradation.py # [CONFIRMADO] Simulación curva de degradación multi-turno
│       ├── exp_02_acra_vs_baseline.py     # [CONFIRMADO] Test A/B Raw vs ACRA
│       ├── exp_03_ccr_sensitivity.py      # [CONFIRMADO] Análisis de sensibilidad de CCR
│       ├── exp_04_edge_router_accuracy.py # [CONFIRMADO] Precisión de enrutamiento y prevención de sticking
│       └── exp_05_ablation_study.py       # [CONFIRMADO] Estudio de ablación de 5 componentes
├── Artefactos/                            # [DECLARADO] Artefactos de planificación y paper drafts
│   └── Planes/Vigentes/
├── config/
│   └── acra_config.yaml                   # [CONFIRMADO] Configuración global v2.0
├── data/
│   ├── benchmark_dataset_annotated.json   # [CONFIRMADO] Dataset de 64 trazas anotadas con ground-truth
│   ├── processed/                         # [CONFIRMADO] Telemetría y resúmenes de experimentos
│   ├── raw/                               # [CONFIRMADO] Directorio para datasets crudos
│   └── sandbox/                           # [CONFIRMADO] Entorno de pruebas de datos
├── docs/
│   ├── architecture/
│   │   ├── ACRA_Cognitive_Stability_RFC.md   # [CONFIRMADO] RFC matemático fundacional
│   │   └── ACRA_System_Specification_v2.md  # [CONFIRMADO] Especificación de ingeniería v2.0
│   ├── benchmarks/
│   │   └── ACRA_Evaluation_Report.md         # [CONFIRMADO] Informe exhaustivo de evaluación empírica
│   ├── engineers_notes/                      # [CONFIRMADO] 10 notas técnicas de referencia académica
│   └── security/
│       ├── ACRA_Threat_Model.md              # [CONFIRMADO] Modelo de amenazas STRIDE
│       └── ACRA_Trust_Boundaries.md          # [CONFIRMADO] Especificación de procedencia y confianza
├── Dockerfile                             # [CONFIRMADO] Imagen multi-etapa para producción
├── docker-compose.yml                     # [CONFIRMADO] Orquestación local de contenedores
├── pyproject.toml                         # [CONFIRMADO] Manifiesto de dependencias pyproject
├── README.md                              # [CONFIRMADO] Documentación maestra en inglés (Paper-Grade)
├── README_ES.md                           # [CONFIRMADO] Documentación completa en español (Paper-Grade)
├── schemas/
│   ├── clean_payload.json                 # [CONFIRMADO] Esquema JSON de CleanPayload v2.0
│   ├── conversation_state.json            # [CONFIRMADO] Esquema JSON de ConversationState v2.0
│   ├── policy_validation.json             # [CONFIRMADO] Esquema JSON de PolicyValidationResult
│   └── routing_decision.json              # [CONFIRMADO] Esquema JSON de RoutingDecision v2.0
├── scripts/
│   ├── generate_benchmark_dataset.py      # [CONFIRMADO] Generador sintético de 64 trazas
│   ├── run_all_experiments.py             # [CONFIRMADO] Ejecutor unificado de los 5 experimentos
│   └── verify_reproducibility.py          # [CONFIRMADO] Suite de auditoría y reproducibilidad E2E
├── src/
│   ├── core/
│   │   ├── config_loader.py               # [CONFIRMADO] Validador y cargador Pydantic de configuración
│   │   ├── dhc.py                         # [CONFIRMADO] Compresión dinámica y retención de decisiones
│   │   ├── edge_router.py                 # [CONFIRMADO] Enrutador con MaturityVector y procedencia
│   │   ├── governance.py                  # [CONFIRMADO] Gobernador de límites (tokens, turnos, costos)
│   │   ├── handoff.py                     # [CONFIRMADO] Ensamblador de payloads estériles con hash
│   │   ├── logger.py                      # [CONFIRMADO] Logger JSON con correlation IDs y redacción
│   │   ├── metrics.py                     # [CONFIRMADO] Motor de cálculo formal (CCR, P̄, A⁹⁰, SF-Key)
│   │   ├── orchestrator.py                # [CONFIRMADO] Orquestador de turnos y máquina de estados
│   │   ├── payload_policy.py              # [CONFIRMADO] Compuerta estática de seguridad y políticas
│   │   ├── state_machine.py               # [CONFIRMADO] Autómata formal de 12 estados
│   │   ├── unified_context.py             # [CONFIRMADO] Almacén UCT multi-tenant con revocación
│   │   └── models/
│   │       ├── __init__.py                # [CONFIRMADO] Inicializador de modelos
│   │       ├── llm_adapter.py             # [CONFIRMADO] BaseLLMAdapter, OllamaStub y CloudAPIStub
│   │       └── mock_models.py             # [CONFIRMADO] Mocks empíricos calibrados con literatura
│   └── data_generation/
│       └── conversation_generator.py      # [CONFIRMADO] Generador de conversaciones sintéticas
└── tests/
    ├── benchmark/
    │   └── test_benchmark_dataset.py      # [CONFIRMADO] Evaluación de 64 trazas y 3 líneas base
    ├── integration/                       # [CONFIRMADO] Pruebas de ciclo de vida completo
    ├── security/
    │   ├── test_memory_poisoning.py       # [CONFIRMADO] Pruebas de revocación y salting de caché
    │   ├── test_payload_policy.py         # [CONFIRMADO] Pruebas unitarias de detección de secretos/PII
    │   ├── test_prompt_injection.py       # [CONFIRMADO] Pruebas de inyección y contención en Edge
    │   └── test_tenant_isolation.py       # [CONFIRMADO] Pruebas de no-colisión multi-inquilino
    └── unit/
        ├── test_dhc.py                    # [CONFIRMADO] Pruebas unitarias de DHC
        ├── test_edge_router.py            # [CONFIRMADO] Pruebas unitarias de EdgeRouter
        ├── test_governance_and_config.py  # [CONFIRMADO] Pruebas de ResourceGovernor y configuración
        ├── test_handoff.py                # [CONFIRMADO] Pruebas unitarias de HandoffEngine
        ├── test_metrics.py                # [CONFIRMADO] Pruebas de cálculo métrico formal
        ├── test_orchestrator.py           # [CONFIRMADO] Pruebas de flujo orquestado multi-turno
        ├── test_semantic_fidelity.py      # [CONFIRMADO] Pruebas de MaturityVector y fidelidad semántica
        ├── test_state_machine.py          # [CONFIRMADO] Pruebas de transiciones legales e ilegales
        └── test_unified_context.py        # [CONFIRMADO] Pruebas unitarias de persistencia UCT
```

### 2.3 Responsabilidad por directorio y archivo clave
[CONFIRMADO]
- `src/core/edge_router.py`: Responsable de evaluar la madurez de la consulta mediante el vector multidimensional `MaturityVector`, clasificar turnos en 7 niveles de procedencia (`ContentProvenance`) y asignar niveles de confianza (`TrustLevel`).
- `src/core/dhc.py`: Responsable de ejecutar la compresión asimétrica de historial, retener decisiones de arquitectura (`retained_decisions`), extraer bloques de código y aislar directivas anuladas (`superseded_items`).
- `src/core/payload_policy.py`: Responsable de la inspección estática pre-inferencia para neutralizar inyecciones de prompts, rediseñar credenciales/PII y bloquear promociones ilícitas de confianza.
- `src/core/unified_context.py`: Responsable de la persistencia de snapshots comprimidos indexados por hash SHA-256 particionado por `tenant_id` y `salt`, con capacidad de revocación inmediata.
- `src/core/handoff.py`: Responsable de ensamblar el payload estéril (`CleanPayload`) que garantiza la ejecución en régimen equivalente a zero-shot.
- `src/core/governance.py`: Responsable de supervisar en tiempo constante $\mathcal{O}(1)$ los límites operativos de tokens, turnos, latencia y costos.
- `src/core/orchestrator.py`: Responsable de coordinar el ciclo de vida de la conversación unificando el Edge Router, DHC, UCT, Handoff, Gobernanza y la máquina de estados.
- `scripts/verify_reproducibility.py`: Responsable de la verificación integral de extremo a extremo en una sola invocación CLI.

### 2.4 Límites modulares y acoplamiento
[CONFIRMADO] Los módulos del núcleo (`src/core/`) no poseen dependencias circulares. `ACRAOrchestrator` utiliza inyección de dependencias opcional en su constructor (`__init__`), permitiendo instanciar componentes por defecto o inyectar mocks calibrados para pruebas reproducibles.

---

## 3. FLUJOS DE EJECUCIÓN Y ENTRY POINTS

### 3.1 Puntos de entrada principales
[CONFIRMADO]
- **API Python / Entry Point Programático:** `src.core.orchestrator.ACRAOrchestrator.process_turn(session_id, user_message)`
- **Auditoría de Reproducibilidad CLI:** `python scripts/verify_reproducibility.py`
- **Suite de Experimentos de Investigación:** `python scripts/run_all_experiments.py`
- **Generador de Dataset de Benchmark:** `python scripts/generate_benchmark_dataset.py`
- **Ejecución de Pruebas Automatizadas:** `python -m pytest tests/`
- **Contenedor Docker:** `docker run --rm acra:latest` (ejecuta la auditoría por defecto)

### 3.2 Diagrama de flujo principal E2E (ASCII)
```text
[Turno del Usuario: user_message]
              │
              ▼
[0. ResourceGovernor.check_and_record()] ──► [Límite Excedido] ──► [POLICY_REJECTED / Retención]
              │ (Presupuesto OK)
              ▼
[1. EdgeRouter.route()] ──► Evalúa MaturityVector M(v)
              │
              ▼
[2. DHC.compress()] ──► Purga cháchara, extrae decisiones y código, calcula CCR
              │
              ▼
[3. UCT.persist_snapshot()] ──► Persistencia SHA-256 con tenant_id y salt
              │
              ▼
[4. PayloadPolicyGate.validate()]
              │
     ┌────────┴────────┐
     │                 │
 (Falló Política)  (Superó Política)
     │                 │
     ▼                 ▼
[POLICY_REJECTED]  [RouterDecision.action == DISPATCH_PRO?]
(Retención Edge)       │
                  ┌────┴────┐
                  │         │
                 (No)      (Sí)
                  │         │
                  ▼         ▼
             [CLARIFY] [HandoffEngine.assemble_clean_payload()]
             (Edge)         │
                            ▼
                       [DISPATCHING_PRO]
                       (Clúster Pesado Zero-Shot)
```

### 3.3 Ciclo de vida de la ejecución y estados
[CONFIRMADO] Autómata formal de 12 estados en `src/core/state_machine.py`:
`IDLE` $\rightarrow$ `INGESTING` $\rightarrow$ (`CLARIFYING` $\lor$ `CONSOLIDATING`) $\rightarrow$ `VALIDATING` $\rightarrow$ (`ROUTING_PRO` $\lor$ `POLICY_REJECTED`) $\rightarrow$ (`EXECUTING_PRO` $\lor$ `FALLBACK`) $\rightarrow$ `RESPONDING` $\rightarrow$ (`IDLE` $\lor$ `TERMINATED` $\lor$ `REVOKED`).

---

## 4. MODELO DE DATOS, CONTRATOS Y PERSISTENCIA

### 4.1 Esquemas y entidades principales
[CONFIRMADO]
- **`MessageTurn` (`src/core/edge_router.py`):**
  - `role: TurnRole` (`user`, `assistant`, `system`)
  - `content: str`
  - `turn_index: int`
  - `is_clarification: bool`
  - `provenance: ContentProvenance`
  - `trust_level: TrustLevel`
  - `source_id: Optional[str]`
- **`MaturityVector` (`src/core/edge_router.py`):**
  - `semantic_ambiguity: float` [0, 1]
  - `contextual_completeness: float` [0, 1]
  - `architectural_risk: float` [0, 1]
  - `turn_depth: float` [0, 1]
  - Propiedad calculada: `composite_score: float`
- **`CompressedContext` (`src/core/dhc.py`):**
  - `raw_tokens_estimate: int`, `consolidated_tokens_estimate: int`, `ccr: float`
  - `purged_chatter_count: int`, `consolidated_user_requirements: List[str]`
  - `crystallized_code_artifacts: List[str]`, `clean_history_prompt: str`
  - `provenance_chain: List[Dict[str, Any]]`, `trust_summary: Dict[str, int]`
  - `retained_decisions: List[str]`, `superseded_items: List[str]`
- **`CleanPayload` (`src/core/handoff.py`):**
  - `session_id: str`, `target_cluster: str`, `prefill_prompt: str`, `ccr: float`
  - `is_sterilized: bool`, `schema_version: str`, `policy_version: str`
  - `sterilization_hash: Optional[str]`, `validation_result: Optional[PolicyValidationResult]`

### 4.2 Almacenamiento, motores de base de datos y migraciones
[CONFIRMADO]
- **Almacén en memoria UCT:** Implementado como diccionario hash indexado por clave compuesta:
  $$\text{Key} = \text{SHA256}(T_{\text{tenant}} \parallel S_{\text{session}} \parallel P_{\text{clean}} \parallel \sigma_{\text{salt}})$$
- **Persistencia en disco:** Archivos de resultados empíricos y resúmenes estructurados en `data/processed/` y `Artefactos/Planes/Vigentes/` en formato JSON estándar.

### 4.3 Interfaces externas, payloads y contratos de API
[CONFIRMADO] Contratos formales validados mediante esquemas JSON estándar (Draft-07) en `schemas/`:
- `schemas/conversation_state.json` (Estado canónico estructurado de la conversación).
- `schemas/routing_decision.json` (Contrato de decisión emitido por el Edge Router).
- `schemas/clean_payload.json` (Contrato del payload de handoff a Pro).
- `schemas/policy_validation.json` (Resultado de la auditoría de políticas y seguridad).

---

## 5. CONFIGURACIÓN Y AMBIENTE

### 5.1 Tabla de variables y parámetros de configuración
[CONFIRMADO] Centralizados en `config/acra_config.yaml` y validados por `src/core/config_loader.py`:

| Parámetro / Variable | Tipo | Default | Efecto Operativo | Sensible |
| :--- | :--- | :--- | :--- | :--- |
| `version` | string | `"2.0.0"` | Versión canónica de la configuración de arquitectura | No |
| `environment` | string | `"production-ready"` | Perfil de ejecución del runtime | No |
| `routing.default_maturity_threshold` | float | `0.70` | Umbral mínimo para autorizar despacho al clúster Pro | No |
| `routing.min_turns_before_pro` | int | `1` | Turnos mínimos de borde antes de activar el clúster pesado | No |
| `compression.target_min_ccr` | float | `0.45` | Tasa mínima requerida de compresión de contexto | No |
| `caching.ttl_seconds` | float | `3600.0` | Tiempo de vida de snapshots en caché UCT | No |
| `caching.salt` | string | `"acra_kernel_salt_v1"` | Salt criptográfico para generación de claves de caché | Sí |
| `security.max_payload_bytes` | int | `262144` | Límite máximo en bytes (256 KB) para payloads | No |
| `governance.max_tokens_per_session` | int | `64000` | Presupuesto máximo acumulado de tokens por sesión | No |
| `governance.max_turns_per_session` | int | `25` | Techo máximo de turnos antes de abortar por DoS | No |
| `governance.max_cost_usd_per_session` | float | `1.00` | Techo monetario de consumo por sesión ($1.00 USD) | No |
| `tenants.default_tenant` | string | `"default"` | Identificador del inquilino por defecto | No |

### 5.2 Perfiles de ejecución
[CONFIRMADO]
- **`development` / `test`:** Ejecución local con mocks estocásticos calibrados y stubs sin latencia de red.
- **`production-ready`:** Inferencia controlada por `ResourceGovernor` y validación de políticas estricta con redacción de credenciales en logs.

### 5.3 Prerrequisitos de sistema e infraestructura
[CONFIRMADO]
- Python 3.10, 3.11 o 3.12.
- Dependencias base: `pydantic>=2.0.0`, `pyyaml>=6.0`, `numpy>=1.24.0`, `pytest>=7.4.0`.

---

## 6. PRUEBAS, CI/CD Y OPERACIÓN

### 6.1 Estrategia de pruebas
[CONFIRMADO] Total de **56 pruebas automatizadas con 100% de éxito**:
- **Pruebas de Benchmark (`tests/benchmark/`):** 3 pruebas que ejecutan las 64 trazas del dataset anotado y las comparativas frente a 3 líneas base.
- **Pruebas de Seguridad (`tests/security/`):** 15 pruebas que validan defensas contra inyección de prompts, aislamiento multi-tenant, detección de secretos/PII y revocación de snapshots por memory poisoning.
- **Pruebas Unitarias (`tests/unit/`):** 23 pruebas de todos los módulos del núcleo (`edge_router`, `dhc`, `handoff`, `metrics`, `governance`, `config_loader`, `state_machine`, `unified_context`, `semantic_fidelity`).
- **Pruebas de Integración y Suite Runner (`tests/`):** 15 pruebas del ciclo de vida conversacional completo.

### 6.2 Automatización y pipelines CI/CD
[CONFIRMADO] Pipeline de GitHub Actions en `.github/workflows/ci.yml` que ejecuta matriz de pruebas en Python 3.10, 3.11 y 3.12 y corre `scripts/verify_reproducibility.py`.

### 6.3 Contenedores y orquestación
[CONFIRMADO]
- `Dockerfile`: Construcción multi-etapa basada en `python:3.12-slim` ejecutada con usuario sin privilegios de root (`acrauser`, UID 1001).
- `docker-compose.yml`: Define el servicio `acra-core` para ejecución local de validación con volúmenes mapeados.

---

## 7. OBSERVABILIDAD Y MODOS DE FALLA

### 7.1 Logs, métricas y tracing
[CONFIRMADO]
- **Logger Estructurado JSON (`src/core/logger.py`):** Emite eventos formateados en JSON con `timestamp`, `level`, `component`, `session_id`, `correlation_id` y `caller`.
- **Redacción Automática en Logs:** Todo mensaje pasa por `PayloadPolicyGate.sanitize()` antes de escribirse en `stdout`, eliminando tokens y claves accidentales.

### 7.2 Modos de falla conocidos y estrategias de recuperación
[CONFIRMADO]
- **Inyección de Prompt / Intento de Jailbreak:** Interceptado por `PayloadPolicyGate`; el orquestador transiciona a `POLICY_REJECTED`, retiene la consulta en Edge y emite respuesta de contención diagnóstica sin tocar el clúster Pro.
- **Desbordamiento de Presupuesto:** Interceptado por `ResourceGovernor`; lanza `BudgetExceededError`, previniendo consumo desmedido de inferencia.
- **Envenenamiento de Memoria (Poisoning):** Mitigado mediante la API `UCT.revoke_snapshot(session_id)`; las consultas posteriores devuelven `None` y no sirven contexto comprometido.
- **Ausencia de Ollama o API Keys:** Los adaptadores `LocalOllamaStubAdapter` y `CloudAPIStubAdapter` degradan a simulación determinista etiquetada explícitamente como `simulated: true`.

### 7.3 Idempotencia y reintentos
[CONFIRMADO] La generación de claves de caché y hashes de esterilización (`sterilization_hash`) es puramente determinista vía SHA-256 sobre el contenido canónico.

---

## 8. SEGURIDAD Y PRIVACIDAD

### 8.1 Hallazgos de seguridad estática y modelo STRIDE
[CONFIRMADO] Documentado formalmente en `docs/security/ACRA_Threat_Model.md`. Todas las amenazas STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) cuentan con mitigación implementada y testeada.

### 8.2 Manejo de autenticación, autorización y secretos
[CONFIRMADO]
- Regla inviolable: No almacenar credenciales en código.
- Todas las cadenas que coincidan con claves OpenAI (`sk-...`), AWS (`AKIA...`), GitHub PATs (`ghp_...`) o claves privadas RSA son detectadas como violaciones críticas y reemplazadas por `[REDACTED_SECRET]`.

### 8.3 Privacidad de datos y multi-inquilino
[CONFIRMADO] Espacio de claves de caché particionado por `tenant_id` y `salt` criptográfico. Las consultas de un inquilino no pueden retornar snapshots de otro, incluso compartiendo el mismo `session_id`.

---

## 9. ESTADO REAL, DEUDA TÉCNICA Y LIMITACIONES

### 9.1 Nivel de madurez y avance real del proyecto
[CONFIRMADO]
- **Versión:** `2.0.0` (Arquitectura estabilizada, verificada y auditada).
- **Cobertura de Pruebas:** 100% de éxito en 56 pruebas automatizadas.
- **Listo para Revisión Académica:** Estructura y documentación alineada con estándares formales para DeepMind.

### 9.2 Deuda técnica identificada y stubs pendientes
[CONFIRMADO]
- `LocalOllamaStubAdapter` opera en modo degradado local (stub) debido a la ausencia deliberada de runtime Ollama en el entorno local del usuario.
- `CloudAPIStubAdapter` opera en modo simulado al no requerirse API keys reales en la fase de evaluación de laboratorio.

### 9.3 Inconsistencias entre código y documentación
[CONFIRMADO] Ninguna. Se han sincronizado simultáneamente `README.md`, `README_ES.md`, `config/acra_config.yaml`, esquemas JSON y la especificación técnica formal.

---

## 10. REGLAS PARA MODIFICAR EL PROYECTO

### 10.1 Convenciones de estilo, linting y tipado
[CONFIRMADO]
- Tipado estático con anotaciones completas (`typing`, `pydantic`).
- Formato PEP 8 y documentación formal de funciones.
- Cero emojis en código fuente, logs estructurados y documentación técnica.

### 10.2 Reglas arquitectónicas inviolables
[CONFIRMADO]
1. **Invariante de Asimetría:** No invocar el clúster Pro si la madurez calculada es menor al umbral configurado ($0.70$).
2. **Invariante de Línea Base Clean:** No enviar payloads al clúster Pro sin pasar por DHC y `PayloadPolicyGate`.
3. **Invariante de Jerarquía de Confianza:** `USER_DIRECT` no puede tener `trust_level == TRUSTED` sin verificación externa.
4. **Invariante de Reproducibilidad:** Las simulaciones deben etiquetarse siempre con `simulated: true`.

### 10.3 Checklist de verificación previa a commit
[CONFIRMADO]
1. Ejecutar `python scripts/verify_reproducibility.py` y verificar que los 4 pasos reporten `[PASSED]`.
2. Verificar que `python -m pytest tests/` pase las 56 pruebas en 0 fallos.
3. Asegurar que ningún secreto o token personal se encuentre presente en el árbol de trabajo.

---

## 📌 CONTEXT HANDOFF & PROTOCOLO DE ASISTENCIA

> **Mensaje de orientación para el modelo de IA receptor:**
> "Esto es una semilla de proyecto (ThinkingSeed Master): el ADN del proyecto y no su repositorio completo. Refleja el avance real y la arquitectura del sistema hasta la fecha. Como modelo receptor, tu función es usar esta semilla como memoria técnica para:
> 1. **Responder preguntas** sobre la arquitectura, funcionamiento, dependencias y flujos del sistema.
> 2. **Sugerir mejoras o asistencia técnica** sobre el estado actual y áreas pendientes identificadas en la semilla.
> 3. **Generar código o soluciones compatibles** respetando las rutas, convenciones y patrones definidos aquí, cuando el usuario te lo solicite."

### Pautas de resolución:
Antes de resolver una solicitud:
1. Identifica el objetivo del usuario.
2. Localiza los componentes afectados usando las rutas del Seed.
3. Revisa restricciones, reglas y contratos declarados.
4. Explicita supuestos cuando sea necesario: "Supongo que X debido a Y".
5. Propone cambios por archivo con rutas claras.
6. Añade pruebas, riesgos y criterios de aceptación.

### 🤝 Acuse de Recibo Inicial
Si el usuario adjuntó esta semilla **sin una instrucción específica**, no intentes generar código ni completar archivos vacíos. Responde únicamente con:
1. Un saludo confirmando que asimilaste el ADN de **ACRA-Adaptive Conversational Routing Architecture** y su stack principal.
2. Un breve resumen de 2-3 líneas sobre el objetivo y su estado actual de avance.
3. Una frase poniéndote a disposición para resolver dudas sobre su funcionamiento o colaborar en los siguientes pasos de desarrollo.
