<!-- ============================================================================== -->
<!-- THINKINGSEED: ADN DEL PROYECTO (CONTEXTO PASIVO PARA MODELOS DE LENGUAJE)     -->
<!-- ============================================================================== -->
> [!NOTE]
> ### 🧬 DEFINICIÓN Y ROL DE ESTE DOCUMENTO
> 1. **¿Qué es este archivo?:** Este documento es una **Semilla de Proyecto (ThinkingSeed Master)**: representa el **ADN arquitectónico, técnico y estructural exhaustivo** del sistema. **NO es el repositorio completo de código fuente**, sino su mapa genético y memoria técnica profunda extraída directamente del entorno de desarrollo.
> 2. **Estado de Avance (Work in Progress):** Este documento refleja el **estado actual del desarrollo**. No garantiza que el proyecto esté concluido al 100%; puede representar un prototipo, un MVP o un sistema en evolución continua. La ausencia de código completo en ciertos archivos o módulos es **deliberada por diseño** para optimizar ventana de contexto o refleja áreas aún en desarrollo.
> 3. **Modo de Operación:** Trata este documento como **contexto pasivo de referencia técnica (Ground Truth)**. No asumas que el archivo está defectuoso ni intentes reescribirlo por tu cuenta.
<!-- ============================================================================== -->

# THINKING SEED MASTER: ACRA (Adaptive Conversational Routing Architecture)

## 0. IDENTIDAD Y METADATOS
```yaml
seed_schema_version: "2.0"
project_name: "ACRA-Adaptive-Conversational-Routing-Architecture"
repository_name: "ACRA-Adaptive Conversational Routing Architecture"
project_type: "ml-system"
repository_mode: "single-project"
generated_at: "2026-09-17T00:50:00-03:00"
generated_by: "Antigravity Agent (Gemini 3.8 Flash)"
repository_root: "d:/0001 HyperScale Thinking/PROYECTOS CLOUD/Research and Development/ACRA-Adaptive Conversational Routing Architecture"
git_branch: "master"
git_commit: "0eee88b"
working_tree_state: "dirty"
analysis_mode: "static"
coverage_level: "high"
known_analysis_limits:
  - "Inferencia real contra APIs externas (OpenAI/Gemini/Anthropic) evaluada mediante stubs y simulación determinista para reproducibilidad sin costos de red."
  - "Persistencia en disco o base de datos externa es simulada mediante almacenamiento en memoria con TTL determinista en UnifiedContextTier."
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
- **1.1 Proyecto en una frase:** `[CONFIRMADO]` ACRA es una arquitectura de enrutamiento conversacional asimétrico de dos capas (Edge y Pro) diseñada para erradicar la degradación cognitiva acumulativa, la infiabilidad estocástica y la pérdida de atención (*Lost in the Middle*) en interacciones multi-turno con Large Language Models.
- **1.2 Problema que resuelve:** `[CONFIRMADO]` En interacciones multi-turno prolongadas (8 a 25 turnos), los LLMs sufren colapso de razonamiento por acumulación de *conversational chatter*, anclaje errático prematuro (*Stick-or-Switch problem*), derivación de directivas (*instruction drift*) y explosión de costos innecesarios en clústeres pesados de frontera.
- **1.3 Usuarios o sistemas consumidores:** `[INFERIDO]` Motores de inferencia empresarial, orquestadores de agentes autónomos, frameworks de diálogo técnico complejo (ingeniería de software, finanzas, arquitectura cloud) y plataformas SaaS que requieren interacciones multi-turno con modelos de frontera (Gemini Pro, Claude Sonnet/Opus, GPT-4/5).
- **1.4 Alcance y límites del sistema:** `[CONFIRMADO]` Intercepta cada turno a nivel de borde (Edge), consolida y comprime dinámicamente el historial (DHC), valida esterilidad y políticas de seguridad (PayloadPolicyGate), controla transiciones formales de estado (FSM) y transfiere un *Clean Payload* al modelo de frontera únicamente cuando la especificación alcanza madurez técnica verificada. No incluye frontend gráfico integrado ni infraestructura de base de datos relacional pesada.

---

## 2. ARQUITECTURA Y TOPOLOGÍA
- **2.1 Estilo arquitectónico:** `[CONFIRMADO]` Arquitectura desacoplada en tubería asimétrica orientada a eventos conversacionales con máquina de estados finitos determinista (FSM), compresión semántica DHC, control de políticas de esterilización previa a la inferencia de frontera y aislamiento criptográfico multi-tenant.

- **2.2 Árbol estructural del repositorio:**
```text
ACRA-Adaptive Conversational Routing Architecture/
├── .dockerignore
├── ACRA.jpg
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
├── README_ES.md
├── 001_Seed/
│   └── seed-acra-adaptive-conversational-routing-architecture-master.md
├── 02_Foundation/
│   └── Engine/
│       └── EngineReadme.md
├── 03_Research_AI/
│   └── experiments/
│       ├── exp_01_baseline_degradation.py
│       ├── exp_02_acra_vs_baseline.py
│       ├── exp_03_ccr_sensitivity.py
│       ├── exp_04_edge_router_accuracy.py
│       └── exp_05_ablation_study.py
├── Artefactos/
│   ├── GPT 5.6 SOL/
│   │   └── ACRA_Plan_Mejora_DeepMind_Antigravity-GPT SOL.md
│   └── Planes/Vigentes/
│       ├── ACRA_Academic_Paper_Draft.md
│       ├── ACRA_Benchmark_Report.md
│       ├── exp_01_baseline_results.json
│       ├── exp_02_ab_test_results.json
│       ├── exp_03_ccr_sensitivity_results.json
│       ├── exp_04_edge_router_results.json
│       └── exp_05_ablation_results.json
├── config/
│   └── acra_config.yaml
├── data/
│   ├── benchmark_dataset_annotated.json
│   └── processed/
│       └── all_experiments_summary.json
├── docs/
│   ├── architecture/
│   │   ├── ACRA_Cognitive_Stability_RFC.md
│   │   └── ACRA_System_Specification_v2.md
│   ├── benchmarks/
│   │   └── ACRA_Evaluation_Report.md
│   ├── engineers_notes/ (ref_01 a ref_10)
│   ├── security/
│   │   ├── ACRA_Threat_Model.md
│   │   └── ACRA_Trust_Boundaries.md
│   └── technical_specs/
│       └── ACRA_Technical_Specification_v1.md
├── schemas/
│   ├── clean_payload.json
│   ├── conversation_state.json
│   ├── policy_validation.json
│   └── routing_decision.json
├── scripts/
│   ├── generate_benchmark_dataset.py
│   ├── run_all_experiments.py
│   └── verify_reproducibility.py
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config_loader.py
│   │   ├── dhc.py
│   │   ├── edge_router.py
│   │   ├── governance.py
│   │   ├── handoff.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   ├── orchestrator.py
│   │   ├── payload_policy.py
│   │   ├── state_machine.py
│   │   ├── unified_context.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── llm_adapter.py
│   │       └── mock_models.py
│   └── data_generation/
│       └── conversation_generator.py
└── tests/
    ├── __init__.py
    ├── run_all_tests.py
    ├── test_integration_runner.py
    ├── test_suite_runner.py
    ├── benchmark/
    │   └── test_benchmark_dataset.py
    ├── security/
    │   ├── test_memory_poisoning.py
    │   ├── test_payload_policy.py
    │   ├── test_prompt_injection.py
    │   └── test_tenant_isolation.py
    └── unit/
        ├── test_dhc.py
        ├── test_edge_router.py
        ├── test_governance_and_config.py
        ├── test_handoff.py
        ├── test_metrics.py
        ├── test_orchestrator.py
        ├── test_semantic_fidelity.py
        ├── test_state_machine.py
        └── test_unified_context.py
```

- **2.3 Responsabilidad por directorio y archivo clave:**
  - `src/core/orchestrator.py`: `[CONFIRMADO]` Orquestador central. Coordina el flujo de cada turno (`process_turn`), valida transiciones FSM, invoca DHC, evalúa políticas y resguarda el clúster Pro.
  - `src/core/edge_router.py`: `[CONFIRMADO]` Clasificador liviano que calcula el vector de madurez (`MaturityVector`), el riesgo arquitectónico y emite la acción (`HOLD_LOCAL_EDGE`, `CLARIFY_LOCAL_EDGE`, `DISPATCH_PRO`).
  - `src/core/dhc.py`: `[CONFIRMADO]` Compresor dinámico de historial. Ejecuta enmascaramiento asimétrico del asistente, preserva bloques de código y decisiones clave, y purga charla conversacional.
  - `src/core/payload_policy.py`: `[CONFIRMADO]` Compuerta de validación estática previa al handoff. Detecta inyecciones de prompt, fugas de secretos (API keys de OpenAI, AWS, GitHub, claves privadas) y fugas PII.
  - `src/core/handoff.py`: `[CONFIRMADO]` Ensamblador de `CleanPayload` con sellado criptográfico (`sterilization_hash`) y directivas de ejecución.
  - `src/core/unified_context.py`: `[CONFIRMADO]` Almacenamiento y caché de contexto con salting SHA-256, aislamiento por inquilino (`tenant_id`) y soporte de revocación inmediata.
  - `src/core/state_machine.py`: `[CONFIRMADO]` Máquina formal de 12 estados (`SystemState`) que impide transiciones ilícitas durante el ciclo de vida de la sesión.
  - `src/core/governance.py`: `[CONFIRMADO]` Gobernador de recursos (`ResourceGovernor`) que monitorea turnos, tokens acumulados, latencia y presupuesto en dólares para evitar denegación de servicio.
  - `src/core/metrics.py`: `[CONFIRMADO]` Motor de cálculo de ecuaciones matemáticas formales: Rendimiento Promedio ($P̄$), Aptitud $A^{90}$, Infiabilidad $U_{10}^{90}$, fidelidades semánticas ($SF_{key}$, $SF_{neg}$) y $CCR$.
  - `src/core/config_loader.py`: `[CONFIRMADO]` Validador Pydantic de la configuración global YAML (`config/acra_config.yaml`).
  - `src/core/logger.py`: `[CONFIRMADO]` Logger estructurado JSON con correlación (`correlation_id`) y ofuscación automática de credenciales/secretos.
  - `src/core/models/`: `[CONFIRMADO]` Adaptadores y stubs (`BaseLLMAdapter`, `LocalOllamaStubAdapter`, `MockEdgeModel`, `MockProModel`) con perfiles de costo y latencia.
  - `schemas/`: `[CONFIRMADO]` Esquemas JSON de validación estricta para payloads limpios, estado conversacional y decisiones de ruteo.
  - `03_Research_AI/experiments/`: `[CONFIRMADO]` 5 suites experimentales formales para validación de hipótesis de degradación, A/B testing, sensibilidad CCR y ablación.
- **2.4 Límites modulares y acoplamiento:** `[CONFIRMADO]` Acoplamiento débil mediante contratos tipados con Pydantic y enums estrictos. Ningún módulo del núcleo depende de llamadas de red no encapsuladas en adaptadores. El Edge Router no tiene acoplamiento directo con la inferencia Pro.

---

## 3. FLUJOS DE EJECUCIÓN Y ENTRY POINTS
- **3.1 Puntos de entrada principales:**
  - `src/core/orchestrator.py::ACRAOrchestrator.process_turn(...)`: `[CONFIRMADO]` Entry point programático principal para procesar turnos conversacionales en runtime.
  - `scripts/run_all_experiments.py`: `[CONFIRMADO]` Script CLI para reproducir los 5 experimentos científicos y compilar métricas agregadas en `data/processed/all_experiments_summary.json`.
  - `scripts/verify_reproducibility.py`: `[CONFIRMADO]` Verificación automatizada de consistencia y reproducibilidad de benchmarks.
  - `tests/run_all_tests.py`: `[CONFIRMADO]` Runner unificado de la suite de pruebas.
- **3.2 Diagrama de flujo principal E2E:**
```mermaid
sequenceDiagram
    autonumber
    actor User as Usuario / Cliente
    participant SM as ACRA State Machine
    participant Gov as Resource Governor
    participant ER as Edge Router
    participant DHC as Dynamic History Compressor
    participant PG as Payload Policy Gate
    participant UC as Unified Context Tier
    participant HO as Handoff Engine
    participant Pro as Clúster Pro (Frontier LLM)

    User->>SM: Mensaje entrante (Turno N)
    SM->>Gov: Validar presupuesto (turnos, tokens, USD)
    Gov-->>SM: Presupuesto OK
    SM->>ER: Evaluar madurez y ambigüedad
    alt Madurez insuficiente (< 0.70) o Turnos iniciales
        ER-->>SM: HOLD_LOCAL_EDGE / CLARIFY_LOCAL_EDGE
        SM-->>User: Respuesta clarificadora / Asistencia local Edge
    else Madurez confirmada (>= 0.70)
        ER-->>SM: DISPATCH_PRO
        SM->>DHC: Comprimir historial conversacional (CCR > 0.45)
        DHC-->>SM: CompressedContext (Chatter purgado, código retenido)
        SM->>PG: Validar políticas (Inyecciones, Secretos, PII)
        alt Infracción de seguridad detectada
            PG-->>SM: PolicyViolation (Critical/High)
            SM-->>User: Bloqueo de seguridad / Fallback local
        else Payload estéril verificado
            PG-->>SM: Validación Aprobada (Hash criptográfico)
            SM->>HO: Ensamblar CleanPayload
            HO->>UC: Persistir snapshot (Tenant ID + Salt SHA-256)
            HO->>Pro: Despacho a inferencia de frontera (Prefill optimizado)
            Pro-->>SM: Respuesta de alta fidelidad
            SM-->>User: Retorno estabilizado al usuario
        end
    end
```
- **3.3 Ciclo de vida de la ejecución y estados:** `[CONFIRMADO]` Estados gobernados por `ACRAStateMachine`: `IDLE` -> `INGESTING` -> (`CLARIFYING` | `CONSOLIDATING`) -> `VALIDATING` -> (`POLICY_REJECTED` | `ROUTING_PRO`) -> `EXECUTING_PRO` -> `RESPONDING` -> `IDLE` / `TERMINATED`. Las transiciones directas prohibidas (e.g., `INGESTING` -> `ROUTING_PRO` sin consolidación previa) disparan de inmediato `InvalidTransitionError`.

---

## 4. MODELO DE DATOS, CONTRATOS Y PERSISTENCIA
- **4.1 Esquemas y entidades principales:**
  - `MessageTurn`: `[CONFIRMADO]` Representa cada interacción con atributos: `role`, `content`, `turn_index`, `token_count`, `provenance`, `trust_level` y `source_id`.
  - `MaturityVector`: `[CONFIRMADO]` Vector continuo 4D: `semantic_ambiguity`, `contextual_completeness`, `architectural_risk`, `turn_depth`.
  - `RouterDecision`: `[CONFIRMADO]` Salida del clasificador Edge: `action`, `target_cluster`, `maturity_score`, `risk_score`, `confidence`, `rationale`.
  - `CompressedContext`: `[CONFIRMADO]` Contexto depurado con ratios de compresión, lista de requerimientos del usuario, artefactos de código cristalizados y cadena de procedencia.
  - `CleanPayload`: `[CONFIRMADO]` Carga limpia empaquetada para el modelo de frontera: `prefill_prompt`, `sterilization_hash`, `is_sterilized`, versiones de esquema y metadatos.
  - `ContextSnapshot`: `[CONFIRMADO]` Instantánea persistente con `tenant_id`, `cache_key` SHA-256, estado de revocación (`is_revoked`) y marca temporal.
- **4.2 Almacenamiento, motores de base de datos y migraciones:** `[CONFIRMADO]` Almacenamiento en memoria volátil en `UnifiedContextTier` estructurado mediante diccionarios indexados por clave criptográfica con invalidación por TTL (3600 segundos por defecto) y revocación inmediata. `[INFERIDO]` No existen motores SQL/NoSQL externos en la versión base; la persistencia a disco se realiza a través de serialización JSON estricta (`schemas/`).
- **4.3 Interfaces externas, payloads y contratos de API:** `[CONFIRMADO]` Esquemas formales JSON en directorio `schemas/`:
  - `schemas/clean_payload.json`: Valida el contrato pre-inferencia Pro.
  - `schemas/conversation_state.json`: Valida la estructura de sesiones activas.
  - `schemas/policy_validation.json`: Valida infracciones y eventos de seguridad.
  - `schemas/routing_decision.json`: Valida decisiones y justificaciones del enrutador.

---

## 5. CONFIGURACIÓN Y AMBIENTE
- **5.1 Tabla de variables y configuraciones (`config/acra_config.yaml`):**
| Parámetro | Tipo | Default | Efecto en Runtime | Sensible |
| :--- | :--- | :--- | :--- | :--- |
| `routing.default_maturity_threshold` | `float` | `0.70` | Umbral mínimo para autorizar handoff a clúster Pro | No |
| `routing.min_turns_before_pro` | `int` | `1` | Turnos Edge mínimos requeridos antes de permitir despacho | No |
| `routing.max_clarification_turns` | `int` | `4` | Límite de preguntas de clarificación en Edge | No |
| `compression.target_min_ccr` | `float` | `0.45` | Ratio mínimo exigido de compresión contextual | No |
| `caching.ttl_seconds` | `int` | `3600` | Tiempo de vida de snapshots de contexto | No |
| `caching.salt` | `str` | `"acra_kernel_salt_v1"` | Salteado para generación determinista de hash SHA-256 | Sí |
| `security.block_injections` | `bool` | `true` | Bloqueo activo de intentos de Jailbreak / Override | No |
| `security.block_secrets` | `bool` | `true` | Inspección y redacción de API keys y claves privadas | No |
| `governance.max_turns_per_session` | `int` | `25` | Límite máximo de turnos permitidos por sesión | No |
| `governance.max_tokens_per_session`| `int` | `64000` | Límite acumulativo de tokens por sesión | No |
| `governance.max_cost_usd_per_session`| `float` | `1.00` | Límite presupuestario en dólares por sesión | No |
| `tenants.enforce_tenant_isolation` | `bool` | `true` | Aislamiento criptográfico entre diferentes inquilinos | No |

- **5.2 Perfiles de ejecución:** `[CONFIRMADO]` Entorno único configurable mediante YAML (`production-ready`) con flags para pruebas locales y simulación determinista sin dependencias obligatorias de cloud.
- **5.3 Prerrequisitos de sistema e infraestructura:** `[CONFIRMADO]` Python `>=3.10` (testeado y operativo en Python 3.12.10). Paquetes obligatorios: `numpy>=1.26.0`, `scipy>=1.12.0`, `pydantic>=2.6.0`, `pyyaml>=6.0`, `rich>=13.7.0`, `matplotlib>=3.8.0`, `seaborn>=0.13.0`, `pandas>=2.2.0`. Contenedorización disponible mediante `Dockerfile` y `docker-compose.yml`.

---

## 6. PRUEBAS, CI/CD Y OPERACIÓN
- **6.1 Estrategia de pruebas:** `[CONFIRMADO]`
  - Suite unitaria exhaustiva (`tests/unit/`): cubre DHC, Edge Router, Gobernanza, Handoff, Métricas, Orquestador, Fidelidad Semántica, Máquina de Estados y Contexto Unificado.
  - Suite de seguridad estricta (`tests/security/`): cubre inyección de prompts, envenenamiento de memoria, fuga de credenciales y aislamiento multi-tenant.
  - Suite de benchmarks y datasets (`tests/benchmark/`): valida el dataset anotado de 500 trazas conversacionales.
  - Estado actual de validación: **56 pruebas pasando con 100% de éxito (0 fallas)** en un tiempo de ejecución de ~3.72 segundos.
- **6.2 Automatización y pipelines CI/CD:** `[INFERIDO]` Configuración de pytest y linters lista en `pyproject.toml` (`tool.pytest.ini_options`, `tool.ruff`, `tool.mypy`).
- **6.3 Contenedores y orquestación:** `[CONFIRMADO]` `Dockerfile` multi-stage optimizado basado en `python:3.11-slim` con usuario no-root (`acrauser`) y `docker-compose.yml` para despliegue aislado.

---

## 7. OBSERVABILIDAD Y MODOS DE FALLA
- **7.1 Logs, métricas y tracing:** `[CONFIRMADO]`
  - Logger estructurado JSON en `src/core/logger.py` con emisión en tiempo real, `correlation_id` por turno y filtro automático de secretos regex.
  - Módulo de métricas matemáticas en `src/core/metrics.py` con cálculo insesgado de percentiles ($P_{10}$, $P_{50}$, $P_{90}$) y varianza.
- **7.2 Modos de falla conocidos y estrategias de recuperación:** `[CONFIRMADO]`
  - *Exceso de presupuesto / DoS:* `BudgetExceededError` es capturado y transiciona la sesión a `TERMINATED` o `FALLBACK` local en Edge.
  - *Detección de Prompt Injection o Fuga:* Transición inmediata a `POLICY_REJECTED`, emitiendo advertencia de seguridad sin despachar al clúster Pro.
  - *Transición ilícita de estado:* `InvalidTransitionError` previene la corrupción del ciclo de vida conversacional.
  - *Caída de conectividad de APIs externas:* `LocalOllamaStubAdapter` y adaptadores cuentan con degradación elegante a simulación determinista sin interrumpir la suite de pruebas.
- **7.3 Idempotencia y reintentos:** `[CONFIRMADO]` La computación de hashes de esterilización SHA-256 garantiza que ante el reenvío de un mismo payload validado, la respuesta y la clave de caché sean deterministas.

---

## 8. SEGURIDAD Y PRIVACIDAD
- **8.1 Hallazgos de seguridad estática:** `[CONFIRMADO]` No se detectaron secretos ni credenciales en texto plano en el árbol de código. El código utiliza placeholders y variables ofuscadas.
- **8.2 Manejo de autenticación, autorización y secretos:** `[CONFIRMADO]`
  - `PayloadPolicyGate` escanea patrones de OpenAI API keys (`sk-[a-zA-Z0-9]{20,}`), AWS access keys (`AKIA[0-9A-Z]{16}`), GitHub personal access tokens (`ghp_[a-zA-Z0-9]{36}`) y bloques de certificados PEM (`-----BEGIN PRIVATE KEY-----`).
  - Detección de patrones de jailbreak (e.g. `dan mode`, `ignore previous instructions`, `<|im_start|>system`).
- **8.3 Privacidad de datos y cumplimiento:** `[CONFIRMADO]`
  - Sanitización activa de PII (correos electrónicos y tarjetas de crédito mediante algoritmos regex en `src/core/payload_policy.py`).
  - Aislamiento estricto multi-inquilino en `UnifiedContextTier` mediante inclusión del `tenant_id` en el hash de caché criptográfica (`tenant_id::session_id::clean_prompt::salt`).

---

## 9. ESTADO REAL, DEUDA TÉCNICA Y LIMITACIONES
- **9.1 Nivel de madurez y avance real del proyecto:** `[CONFIRMADO]` Nivel de madurez **Alpha Avanzado / Research Production-Ready**. El núcleo algorítmico, las suites experimentales completas, el dataset anotado de 500 diálogos y la totalidad de los tests (56/56) están 100% operativos e integrados.
- **9.2 Deuda técnica identificada y stubs pendientes:**
  - `src/core/models/llm_adapter.py`: `[CONFIRMADO]` Los adaptadores para proveedores de frontera comerciales (OpenAI, Anthropic, Gemini API) son stubs simulados o degradan a simulación local determinista; falta implementar clientes de red asíncronos nativos para producción abierta.
  - `src/core/unified_context.py`: `[CONFIRMADO]` El almacenamiento de caché de contexto reside en memoria de proceso (`Dict[str, ContextSnapshot]`); la persistencia distribuida para escalado horizontal (e.g., Redis o Memcached) no está implementada.
  - `02_Foundation/Engine/`: `[DECLARADO]` Directorio con documentación introductoria, sin módulos ejecutables adicionales.
- **9.3 Inconsistencias entre código y documentación:** `[CONFIRMADO]` La documentación en `docs/` y `README.md` describe la arquitectura con alta precisión matemática y coincide plenamente con los nombres de clases y funciones en `src/core/`.

---

## 10. REGLAS PARA MODIFICAR EL PROYECTO
- **10.1 Convenciones de estilo, linting y tipado:** `[CONFIRMADO]`
  - Python 3.10+ con tipado estático obligatorio (`mypy` con `disallow_untyped_defs = true`).
  - Modelos de datos y configuraciones definidos exclusivamente con **Pydantic v2** (`BaseModel`, `Field`).
  - Linter Ruff con límite estricto de 100 caracteres por línea (`line-length = 100`).
- **10.2 Reglas arquitectónicas inviolables:**
  - **Inviolabilidad de la frontera Pro:** Ningún payload puede ser remitido al clúster Pro sin pasar por la compresión de `DynamicHistoryCompressor` y la validación de `PayloadPolicyGate`.
  - **Asimetría de enmascaramiento:** Está prohibido reenviar la verbosidad y las respuestas intermedias del asistente al clúster pesado; únicamente se transmiten los requerimientos consolidados del usuario y los artefactos de código verificados.
  - **Determinismo FSM:** Toda nueva etapa en el ciclo conversacional debe ser declarada en `SystemState` y validada en `ACRAStateMachine.VALID_TRANSITIONS`.
- **10.3 Checklist de verificación previa a commit:**
  1. Ejecutar la suite completa de pruebas: `python -m pytest` (asegurar 56/56 pasadas).
  2. Verificar que no se hayan introducido credenciales o API keys en código de pruebas o fixtures.
  3. Ejecutar `ruff check .` para garantizar conformidad de estilo.

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
1. Un saludo confirmando que asimilaste el ADN de **ACRA (Adaptive Conversational Routing Architecture)** y su stack principal (Python 3.10+, Pydantic v2, Edge Router, DHC, FSM determinista, Caching SHA-256).
2. Un breve resumen de 2-3 líneas sobre el objetivo y su estado actual de avance (Alpha Avanzado con 56/56 pruebas operativas y 5 suites experimentales validadas).
3. Una frase poniéndote a disposición para resolver dudas sobre su funcionamiento o colaborar en los siguientes pasos de desarrollo.
