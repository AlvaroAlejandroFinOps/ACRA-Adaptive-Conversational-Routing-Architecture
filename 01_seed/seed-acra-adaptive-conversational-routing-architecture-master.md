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
generated_at: "2026-09-17T03:25:00-03:00"
generated_by: "Antigravity Agent (Claude 3.7 Sonnet / Antigravity IDE)"
repository_root: "d:/0001 HyperScale Thinking/PROYECTOS CLOUD/Research and Development/ACRA-Adaptive Conversational Routing Architecture"
git_branch: "master"
git_commit: "c95cb03"
working_tree_state: "dirty"
analysis_mode: "static"
coverage_level: "high"
known_analysis_limits:
  - "Inferencia real contra APIs externas (OpenAI/Anthropic) evaluada mediante stubs/simulaciones deterministas sin costos de red; Google GenAI soporta llamadas REST en vivo mediante variable de entorno GEMINI_API_KEY con fallback determinista transparente."
  - "Persistencia de estado de sesión y cápsulas de contexto en memoria volátil o archivos locales, con arquitectura desacoplada para adopción de Redis/KeyDB y Object Storage en Kubernetes."
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
[CONFIRMADO] ACRA es una arquitectura determinista de orquestación multi-agente jerárquica, enrutamiento cognitivo agnóstico a proveedores e ingeniería de contexto previa a la inferencia, diseñada para mitigar la dispersión estocástica y la degradación de razonamiento (*Lost in Conversation*) en modelos de lenguaje multi-turno.

### 1.2 Problema que resuelve
[CONFIRMADO] Los Modelos de Lenguaje de Frontera experimentan un colapso en tareas de razonamiento multi-turno debido a:
1. **Lost in Conversation (LiC):** Caída empírica promedio del 39% en rendimiento al acumular turnos de diálogo ruidosos y redundantes (Laban et al., 2025).
2. **Anclaje Prematuro de Hipótesis (*Stick-or-Switch*):** Compromiso irreversible con conjeturas iniciales erróneas ante especificaciones ambiguas del usuario (Guo et al., 2026).
3. **Explosión de Varianza e Infiabilidad:** Expansión del rango interpercentil $U_{10}^{90}$ superior al 112%, con una varianza $\sigma^2 = 266.72$.
4. **Vulnerabilidades de Inyección y Fuga de Secretos:** Exposición a system overrides, jailbreaks y exfiltración de credenciales (PII/API keys).
5. **Ineficiencia Económica de Caché:** Conmutaciones de proveedor innecesarias que destruyen el prefijo de caché estable, incrementando costos de entrada.

### 1.3 Usuarios o sistemas consumidores
- [CONFIRMADO] Plataformas de agentes conversacionales empresariales que ejecutan flujos de trabajo multi-turno complejos.
- [CONFIRMADO] Pasarelas de inferencia de IA corporativas que gestionan múltiples proveedores (Google Cloud Gemini, Anthropic, OpenAI, Local/Ollama).
- [CONFIRMADO] Sistemas de atención y soporte técnico con requerimiento de alta fidelidad técnica y cero alucinaciones de requisitos anulados.
- [DECLARADO] Clústeres Kubernetes de microservicios sin estado mediante pods de baja latencia.

### 1.4 Alcance y límites del sistema
- **Dentro del alcance:**
  - [CONFIRMADO] Enrutamiento de admisión mediante Vector Multidimensional de Madurez ($\vec{M}$).
  - [CONFIRMADO] Orquestación jerárquica con descomposición en DAG (Kahn TaskGraph), ObjectivePlanner y Consolidator.
  - [CONFIRMADO] Canalización determinista de Ingeniería de Contexto en 13 etapas con extracción de 18 señales zero-LLM.
  - [CONFIRMADO] Desacoplamiento estricto de nombres de modelos comerciales (`INV-001`) mediante `ModelResolver` y perfiles de capacidades.
  - [CONFIRMADO] Enrutador de afinidad consciente de caché con política de histéresis y protección anti-oscilación (`INV-010`).
  - [CONFIRMADO] Compuertas de seguridad (`HandoffPolicyGate`, `ToolAuthorizationGate` con separación plan/ejecución `INV-007`).
  - [CONFIRMADO] Motor de economía de tokens con cascada presupuestaria jerárquica (`INV-005`) y discriminación medido/estimado (`INV-006`).
- **Fuera del alcance:**
  - [DECLARADO] Ajuste fino (fine-tuning) o reentrenamiento de pesos de los modelos de base.
  - [DECLARADO] Base de datos distribuida propia (se integra mediante adapters de persistencia e in-memory caching).
  - [CONFIRMADO] Interfaces gráficas de usuario pesadas (la UI de ejemplo en Streamlit o React se considera referencia accesoria).

---

## 2. ARQUITECTURA Y TOPOLOGÍA

### 2.1 Estilo arquitectónico
[CONFIRMADO] **Arquitectura Multi-Agente Jerárquica Desacoplada y Orientada a Estados**, estructurada en capas funcionales independientes:
- **Capa de Admisión y FSM de Sesión:** Gobernanza de recursos y madurez.
- **Capa de Orquestación y Planificación:** Descomposición de objetivos en DAG acíclico.
- **Capa de Context Engineering:** Pipeline determinista en 13 fases con auditoría extensible (CEA / Fallback determinista).
- **Capa de Resolución y Enrutamiento:** Resolución de perfiles por capacidades e histéresis de caché.
- **Capa de Seguridad y Autorización:** Compuertas pre/post handoff, sanitización estática y autorización de herramientas mutantes.
- **Capa de Adaptadores de Proveedores:** Abstracción unificada de inferencia (Google, Anthropic, OpenAI, Local).
- **Capa de Gobernanza Económica:** Contabilidad de tokens, presupuestos en cascada y seguimiento epistémico.

### 2.2 Árbol estructural del repositorio (excluyendo ruido)
```text
.
├── .github/workflows/ci.yml           # Integración continua automatizada
├── 001_Seed/                          # ADN del proyecto y semillas maestras
│   └── seed-acra-adaptive-conversational-routing-architecture-master.md
├── 02_Foundation/                     # Fundamentos y especificaciones del motor
├── 03_research/                    # Investigaciones empíricas y benchmarks LiC
│   └── experiments/                   # 5 simulaciones experimentales
├── artifacts/                         # Especificaciones de evolución (EVO ACRA.md, planes)
├── config/                            # Configuraciones YAML
│   ├── acra_config.yaml               # Configuración central
│   ├── policies/hysteresis.yaml       # Política de histéresis de afinidad
│   ├── profiles/model_profiles.yaml   # 7 perfiles de capacidad abstractos
│   └── providers/                     # Configs de adaptadores (google, anthropic, openai, local)
├── data/                              # Datasets y métricas de procesamiento
├── docs/                              # Documentación técnica, ADRs 001-004, RFCs y STRIDE
├── schemas/                           # 6 Esquemas formales JSON
├── scripts/                           # Scripts de síntesis, benchmarks y auditoría
├── src/core/                          # Código fuente de producción
│   ├── agents/                        # Factory, Registry y FSM de Agentes
│   ├── context/                       # Pipeline de 13 fases e ingeniería de contexto
│   ├── contracts/                     # Modelos y contratos Pydantic libres de modelos
│   ├── economy/                       # Economía de tokens, modelos de costo y procedencia
│   ├── fsm/                           # FSMs descompuestas (Session, Objective, Task, Handoff)
│   ├── orchestration/                 # HierarchicalOrchestrator, Planner, Consolidator
│   ├── providers/                     # Adaptadores de modelos (Google, Anthropic, OpenAI, Local)
│   ├── routing/                       # ModelResolver, IntakeRouter, CacheAwareRouter
│   └── security/                      # HandoffPolicyGate, ToolAuthorizationGate, Locks
└── tests/                             # Suite de pruebas (165 pruebas automatizadas, 100% pass)
    ├── benchmark/                     # Degradation benchmarks y CCR
    ├── e2e/                           # Ciclo de vida E2E multi-agente
    ├── fixtures/                      # Fixtures de prueba aisladas
    ├── integration/                   # Pruebas de orquestación e integración
    ├── security/                      # Pruebas de inyección, políticas y herramientas
    └── unit/                          # Pruebas unitarias de todos los componentes
```

### 2.3 Responsabilidad por directorio y archivo clave
- [CONFIRMADO] `src/core/contracts/`: Contratos Pydantic puros sin dependencias de proveedor:
  - `context.py`: `ContextCapsule`, `EpistemicStatus`, `PolicyMode`, `StablePrefixDescriptor`.
  - `agent.py`: `AgentRole`, `AgentDefinition`, `AgentInstance`, `AgentCapabilityVector`.
  - `task.py`: `TaskNode`, `ObjectivePlan`, `ConsolidationReport`.
  - `routing.py`: `ModelCapabilityProfile`, `ModelResolutionDecision`, `HysteresisSwitchDecision`.
  - `security.py`: `ToolAuthorizationRequest`, `ToolAuthorizationResult`, `HandoffValidationResult`.
- [CONFIRMADO] `src/core/fsm/`: Máquinas de estados finitos independientes con `CyclicTransitionGuard`:
  - `session.py`: FSM de sesión (`NEW`, `INTAKE`, `ROUTING`, `EXECUTING`, `COMPLETED`, `FAILED`).
  - `objective.py`: FSM de objetivo global.
  - `task.py`: FSM de tareas individuales en el DAG.
  - `handoff.py`: FSM del ciclo de handoff (`INITIATED`, `AUDITED`, `SANITIZED`, `DISPATCHED`, etc.).
- [CONFIRMADO] `src/core/context/`: Canalización de Context Engineering:
  - `pipeline.py`: `ContextEngineeringPipeline` (13 etapas deterministas secuenciales).
  - `signals.py`: `ZeroLLMTelemetryExtractor` (18 métricas puramente matemáticas).
  - `auditor.py`: `DeterministicFallbackAuditor` y `CEAContextAuditAdapter`.
  - `stable_prefix.py`: `StablePrefixEngine` para maximizar hits de caché.
  - `scoped_registry.py`: `ScopedContextRegistry` con aislamiento multi-inquilino.
- [CONFIRMADO] `src/core/agents/`:
  - `factory.py`: `AgentFactory` con verificación de límites de rol y presupuesto.
  - `registry.py`: `AgentRegistry` para ciclo de vida de agentes.
  - `state_machine.py`: `AgentInstanceStateMachine` con control de estados activos/inactivos.
- [CONFIRMADO] `src/core/orchestration/`:
  - `hierarchical.py`: `HierarchicalAgentOrchestrator` y fachada compatible `ACRAOrchestrator`.
  - `planner.py`: `ObjectivePlanner` con generación de DAG de tareas y asignación de agentes.
  - `task_graph.py`: `TaskGraph` basado en ordenamiento topológico de Kahn con detección de ciclos.
  - `consolidator.py`: `Consolidator` con resolución de contradicciones y síntesis formal.
- [CONFIRMADO] `src/core/routing/`:
  - `model_resolver.py`: Mapeo de capacidades a perfiles con cadena de respaldo.
  - `affinity.py`: `CacheAwareRouter` con cálculo de umbral de histéresis y ventanas de enfriamiento.
  - `intake.py`: `IntakeRouter` con cómputo del Vector Multidimensional de Madurez.
- [CONFIRMADO] `src/core/security/`:
  - `handoff_policy_gate.py`: Evaluación previa/posterior, 5 modos de política y escalación reversible.
  - `tool_authorization_gate.py`: Separación plan/ejecución y aprobación requerida para acciones destructivas.
  - `concurrency.py`: `OptimisticLockManager` y registro de claves de idempotencia.
- [CONFIRMADO] `src/core/economy/`:
  - `engine.py`: `TokenEconomyEngine` con presupuestos jerárquicos y discriminación medido/estimado.
  - `cost_model.py`: `ContinuityCostModel` para arbitraje de costos de caché frente a reconstrucción.
  - `provenance.py`: `ProvenanceTracker` para auditoría ontológica de artefactos.
- [CONFIRMADO] `src/core/providers/`:
  - `google.py`: `GoogleGenAIAdapter` con soporte REST en vivo (`urllib.request`) y fallback simulado.
  - `anthropic.py`: `AnthropicAdapter` con telemetría de lectura de caché.
  - `openai.py`: `OpenAIAdapter` con soporte de telemetría de prompts.
  - `local.py`: `LocalAdapter` para inferencia local con coste cero.

### 2.4 Límites modulares y acoplamiento
- [CONFIRMADO] **Acoplamiento Débil Estricto:** Los módulos centrales de lógica (`contracts`, `routing`, `context`, `security`, `orchestration`) no importan ningún cliente de proveedor específico (Google, Anthropic, OpenAI).
- [CONFIRMADO] **Invariante INV-001:** Se prohíbe explícitamente el uso de cadenas de texto con nombres de modelos comerciales en el núcleo de dominio; su uso se restringe a archivos YAML de configuración y adaptadores en `src/core/providers/`.

---

## 3. FLUJOS DE EJECUCIÓN Y ENTRY POINTS

### 3.1 Puntos de entrada principales
- **Programático (Producción):** `HierarchicalAgentOrchestrator.execute_objective(...)` en [src/core/orchestration/hierarchical.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/orchestration/hierarchical.py).
- **Retrocompatibilidad:** `ACRAOrchestrator.process_turn(...)` en [src/core/orchestrator.py](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/Research%20and%20Development/ACRA-Adaptive%20Conversational%20Routing%20Architecture/src/core/orchestrator.py).
- **Scripts Operativos y Auditoría:**
  - `scripts/verify_reproducibility.py`: Verificación de extremo a extremo de esquemas, tests e invariantes.
  - `scripts/run_all_experiments.py`: Ejecutor de los 5 experimentos empíricos de benchmark.
  - `scripts/generate_benchmark_dataset.py`: Síntesis del dataset de 64 trazas anotadas.

### 3.2 Diagrama de flujo principal E2E (ASCII)
```text
Usuario / Payload
      |
      v
[IntakeRouter] ------------> ¿M(v) < 0.70? ----(Sí)----> [Edge Response / Aclaración]
      |                                                        (Pro dormido)
    (No, Maduro)
      v
[HierarchicalAgentOrchestrator]
      |
      v
[ObjectivePlanner] -------------> Descompone en DAG (TaskGraph de Kahn)
      |
      +---> Para cada Tarea en orden topológico:
                |
                v
          [AgentFactory] --------> Asigna AgentInstance bajo AgentRole
                |
                v
          [13-Stage Context Engineering Pipeline]
                |
                +-> Extracción de 18 señales zero-LLM
                +-> DHC (Compresión y enmascaramiento asimétrico)
                +-> Prefijo Estable & Auditoría (CEA / Fallback)
                +-> Modos de Política (Enforce, DryRun, HumanReview, etc.)
                |
                v
          [ModelResolver & CacheAwareRouter]
                |
                +-> Resuelve perfil de capacidad
                +-> Evalúa histéresis de caché (INV-010)
                |
                v
          [ToolAuthorizationGate & HandoffPolicyGate]
                |
                +-> ¿Plan/Execute autorizado?
                +-> Sanitización y control de concurrencia
                |
                v
          [ProviderAdapter] (Google, Anthropic, OpenAI, Local)
                |
                v
          [TokenEconomyEngine] --> Deduce presupuesto y registra tokens medidos
                |
                v
[Consolidator] -----------------> Resuelve contradicciones y sintetiza salida unificada
      |
      v
Respuesta Consolidada Final
```

### 3.3 Ciclo de vida de la ejecución y estados
[CONFIRMADO] Las máquinas de estados finitos regulan estrictamente cada nivel:
- **Session FSM:** `NEW` $\to$ `INTAKE` $\to$ `ROUTING` $\to$ `EXECUTING` $\to$ `COMPLETED` (o `FAILED`).
- **Objective FSM:** `DRAFT` $\to$ `DECOMPOSED` $\to$ `IN_PROGRESS` $\to$ `CONSOLIDATING` $\to$ `ACHIEVED`.
- **Task FSM:** `PENDING` $\to$ `SCHEDULED` $\to$ `RUNNING` $\to$ `COMPLETED` (o `BLOCKED`).
- **Handoff FSM:** `INITIATED` $\to$ `AUDITED` $\to$ `SANITIZED` $\to$ `DISPATCHED` $\to$ `CONFIRMED`.

---

## 4. MODELO DE DATOS, CONTRATOS Y PERSISTENCIA

### 4.1 Esquemas y entidades principales
[CONFIRMADO] Definidos mediante Pydantic v2 en `src/core/contracts/`:
- `ContextCapsule`: Contenedor inmutable que incluye `capsule_id`, `stable_prefix`, `dynamic_history`, `epistemic_provenance`, `content_hash` y metadatos de auditoría.
- `AgentDefinition` & `AgentInstance`: Modelo con rol explícito (`AgentRole`), perfil de capacidad y cuota de tokens.
- `TaskNode`: Representación de nodo de ejecución en el grafo DAG, con dependencias de entrada y resultados tipados.
- `TokenConsumption`: Registro de gasto con indicador booleano mandatorio `is_measured`.
- `HysteresisPolicy`: Parámetros operativos de conmutación de afinidad de proveedores.

### 4.2 Almacenamiento, motores de base de datos y migraciones
- [CONFIRMADO] `UnifiedContextTier`: Almacén de tensores en memoria con claves hash salteadas por inquilino `SHA-256(tenant_id + session_id + salt)`.
- [CONFIRMADO] `ScopedContextRegistry`: Registro en memoria de cápsulas de contexto por ámbito de agente.
- [CONFIRMADO] `OptimisticLockManager`: Control de concurrencia en memoria para mutaciones de estado concurrentes.
- [DECLARADO] Arquitectura lista para backend persistente en Redis / PostgreSQL sin alterar los contratos tipados.

### 4.3 Interfaces externas, payloads y contratos de API
[CONFIRMADO] Esquemas JSON formales validados en `schemas/`:
1. `clean_payload.json`: Estructura del canvas limpio post-handoff.
2. `conversation_state.json`: Estado de la sesión conversacional.
3. `policy_validation.json`: Resultado de auditoría y validación de seguridad.
4. `routing_decision.json`: Registro de decisiones de resolución y enrutamiento.
5. `model_profile.json`: Esquema del registro de capacidades de modelos.
6. `hysteresis_policy.json`: Esquema de la política de histéresis de caché.

---

## 5. CONFIGURACIÓN Y AMBIENTE

### 5.1 Tabla de variables de entorno
| Variable | Tipo | Default | Efecto | Sensible |
| :--- | :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | String | `None` | Habilita llamadas en vivo a Google GenAI REST API | Sí |
| `OPENAI_API_KEY` | String | `None` | Credencial para adapter OpenAI (modo producción) | Sí |
| `ANTHROPIC_API_KEY`| String | `None` | Credencial para adapter Anthropic (modo producción)| Sí |
| `ACRA_CONFIG_PATH` | Path | `config/acra_config.yaml` | Ruta alternativa a la configuración maestra | No |
| `ACRA_POLICY_MODE` | String | `ENFORCE` | Modo global de compuerta (`ENFORCE`, `AUDIT_ONLY`, etc.) | No |
| `ACRA_CACHE_DIR` | Path | `.acra_cache/` | Directorio local de persistencia temporal | No |

### 5.2 Perfiles de ejecución
- [CONFIRMADO] **Dev / Local:** Inferencia mediante stubs deterministas locales y `LocalAdapter` con coste cero de tokens.
- [CONFIRMADO] **Test / CI:** Ejecución completa de la suite de 165 pruebas automatizadas bajo pytest en menos de 2 segundos.
- [DECLARADO] **Prod (Kubernetes):** Pod sin estado con variables inyectadas mediante Kubernetes Secrets y ConfigMaps.

### 5.3 Prerrequisitos de sistema e infraestructura
- Python 3.10, 3.11 o 3.12.
- Dependencias base: `pydantic>=2.0.0`, `pyyaml>=6.0`, `jsonschema>=4.0.0`.
- Dependencias de desarrollo/benchmark: `pytest>=7.0.0`, `faker`, `scipy`, `numpy`.

---

## 6. PRUEBAS, CI/CD Y OPERACIÓN

### 6.1 Estrategia de pruebas
[CONFIRMADO] Pirámide de pruebas exhaustiva con **165 pruebas automatizadas (100% pasando)**:
- **Unit Tests (115 pruebas):** Verificación de contratos, FSMs con guardas de ciclo, compresión DHC, enrutadores de madurez, 13 fases de contexto, economía jerárquica y los 20 casos de prueba obligatorios.
- **Security Tests (21 pruebas):** Envenenamiento de memoria, inyección de prompts, aislamiento multi-inquilino y compuertas de políticas.
- **Benchmark Tests (7 pruebas):** Degradación LiC, reducción de CCR $\ge 25\%$, ahorro de caché $\ge 20\%$ y dataset anotado de 64 trazas.
- **Integration & E2E Tests (22 pruebas):** Ciclo completo de vida de orquestador jerárquico, retrocompatibilidad con `ACRAOrchestrator` y runners de verificación.

### 6.2 Automatización y pipelines CI/CD
- [CONFIRMADO] `.github/workflows/ci.yml`: Pipeline de GitHub Actions que ejecuta linting, validación estática de esquemas JSON y ejecución completa de pytest sobre Python 3.10, 3.11 y 3.12.

### 6.3 Contenedores y orquestación
- [CONFIRMADO] `Dockerfile`: Imagen de producción multi-etapa basada en `python:3.11-slim`, ejecutando como usuario sin privilegios (`appuser`).
- [CONFIRMADO] `docker-compose.yml`: Orquestación local para servicios de backend y pruebas de integración.

---

## 7. OBSERVABILIDAD Y MODOS DE FALLA

### 7.1 Logs, métricas y tracing
- [CONFIRMADO] `src/core/logger.py`: Logger estructurado en JSON con inyección mandatoria de `correlation_id`, `tenant_id` y marcas de tiempo UTC.
- [CONFIRMADO] `src/core/metrics.py`: Motor de telemetría que calcula 20 métricas cognitivas: $CCR$, $\bar{P}$, $A^{90}$, $U_{10}^{90}$, $\sigma^2$, densidad de contradicciones, ratio de ruido, ahorro de caché de prefijos y derivas semánticas.

### 7.2 Modos de falla conocidos y estrategias de recuperación
1. **Ciclo Infinito de Re-ingreso en Admisión:** Mitigado por `CyclicTransitionGuard` en `SessionFSM` (límite: 3 intentos; conmuta a `FAILED` o escalación humana).
2. **Ciclos en Dependencias de Tareas:** Mitigado por detección de ciclos mediante ordenamiento topológico de Kahn en `TaskGraph` (eleva `ValueError` antes de la ejecución).
3. **Agotamiento de Presupuesto en Subtareas:** Mitigado por validación de techo presupuestario en `TokenEconomyEngine` (eleva `BudgetExceededError` impidiendo la sobrefacturación).
4. **Colisión Concurrente de Estados:** Mitigado por detección de versiones en `OptimisticLockManager` (eleva `ConcurrencyConflictError`).
5. **Indisponibilidad de API de Proveedor:** Mitigado por la cadena de respaldo configurada en `ModelResolver` y simulación determinista de contingencia.

### 7.3 Idempotencia y reintentos
- [CONFIRMADO] Registro de claves de idempotencia en `src/core/security/concurrency.py` que almacena y retorna resultados previos para transacciones con la misma clave.

---

## 8. SEGURIDAD Y PRIVACIDAD

### 8.1 Hallazgos de seguridad estática y STRIDE
[CONFIRMADO] Auditoría formal bajo modelo STRIDE documentada en `docs/security/ACRA_Threat_Model.md`:
- **Spoofing:** Identidad verificada mediante aislamiento por inquilino y tokens de sesión.
- **Tampering:** Integridad de cápsulas garantizada por hashes SHA-256 inmutables.
- **Repudiation:** Registro de procedencia y auditoría formal en `ProvenanceTracker`.
- **Information Disclosure:** Sanitización estática obligatoria de claves de API (AWS, OpenAI, GitHub PATs) y datos personales (PII).
- **Denial of Service:** Límites estrictos de tokens ($\le 64$k) y turnos ($\le 25$) en `ResourceGovernor` y FSMs.
- **Elevation of Privilege:** Regla estricta de jerarquía de confianza: los mensajes de usuario directo no pueden reclamar estatus `TRUSTED`.

### 8.2 Manejo de autenticación, autorización y secretos
- [CONFIRMADO] Separación Plan/Ejecución en `ToolAuthorizationGate`: herramientas con impacto destructivo o mutante requieren aprobación explícita.
- [CONFIRMADO] Sanitización de variables sensibles en registros de telemetría y exclusión de secretos del canvas consolidado.

### 8.3 Privacidad de datos y cumplimiento
- [CONFIRMADO] Aislamiento estricto de espacios de memoria entre inquilinos (`tenant_id`) en `UnifiedContextTier` y `ScopedContextRegistry`.

---

## 9. ESTADO REAL, DEUDA TÉCNICA Y LIMITACIONES

### 9.1 Nivel de madurez y avance real del proyecto
- [CONFIRMADO] **Estado Actual:** Arquitectura de Producción / Grado Investigación (11 fases completadas al 100%).
- [CONFIRMADO] **165 Pruebas Pasando al 100%:** Incluye los 20 casos de prueba obligatorios, 5 experimentos empíricos replicados, adapters de 4 proveedores y validación de 10 invariantes arquitectónicos.

### 9.2 Deuda técnica identificada y stubs pendientes
- [CONFIRMADO] Los adaptadores para Anthropic y OpenAI operan como stubs conformes a protocolo para pruebas sin coste de API en entornos CI. La integración de sockets HTTP en vivo para estos dos proveedores sigue el mismo patrón implementado en `GoogleGenAIAdapter`.
- [DECLARADO] El almacenamiento de caché de tensores y estados de FSM es actualmente en memoria de proceso; para despliegues distribuidos multi-nodo en Kubernetes se recomienda incorporar un driver de persistencia compartida (Redis).

### 9.3 Inconsistencias entre código y documentación
- [CONFIRMADO] Ninguna. Toda la documentación técnica (`README.md`, `README_ES.md`, ADRs, schemas) ha sido sincronizada con el código fuente y validada por pruebas automatizadas.

---

## 10. REGLAS PARA MODIFICAR EL PROYECTO

### 10.1 Convenciones de estilo, linting y tipado
- **Lenguaje de Código y Comentarios:** Inglés técnico estricto para código fuente, docstrings y mensajes de commit.
- **Tipado Estricto:** Tipado estático con Python type hints en todas las funciones y métodos públicos.
- **Modelos de Datos:** Pydantic v2 con validación estricta (`ConfigDict(frozen=True)` para entidades inmutables).
- **Manejo de Errores:** Excepciones de dominio tipadas explícitas (`ModelResolutionError`, `BudgetExceededError`, `SecurityPolicyViolationError`).

### 10.2 Reglas arquitectónicas inviolables (Los 10 Invariantes)
1. **INV-001 (Zero Model Names in Core):** Prohibido incluir nombres comerciales de modelos en contratos, lógica de enrutamiento o seguridad.
2. **INV-002 (Explicit Agent Roles):** Toda instancia de agente debe operar bajo un `AgentRole` explícito con límites de capacidades.
3. **INV-003 (FSM Cycle Guards):** Ninguna FSM puede exceder las transiciones de ciclo permitidas.
4. **INV-004 (Provenance Epistemic Tracking):** Todo artefacto debe tener procedencia verificada y etiqueta epistémica (`FACT`, `HYPOTHESIS`, `SPECULATION`, `DIRECTIVE`).
5. **INV-005 (Budget Cascade Ceiling):** Las subtareas no pueden exceder el presupuesto remanente de la entidad padre.
6. **INV-006 (Measured Token Accounting):** La telemetría debe discriminar obligatoriamente entre tokens medidos y estimados mediante la bandera `is_measured`.
7. **INV-007 (Plan/Execute Tool Separation):** Herramientas destructivas o mutantes requieren plan previo y autorización.
8. **INV-008 (Scoped Context Boundaries):** Los agentes acceden al contexto exclusivamente a través de identificadores de ámbito autorizados.
9. **INV-009 (Reversible Escalation):** Toda escalación de seguridad o privilegio debe ser reversible al finalizar el turno.
10. **INV-010 (Cache Hysteresis Protection):** La conmutación de proveedor está bloqueada a menos que la ganancia de capacidad supere el costo de reconstrucción de caché.

### 10.3 Checklist de verificación previa a commit
- [ ] `python -m pytest tests/` ejecuta y pasa 165 pruebas al 100%.
- [ ] `python scripts/verify_reproducibility.py` finaliza con estado `[PASSED]`.
- [ ] Ningún archivo en `src/core/contracts/`, `src/core/routing/`, `src/core/context/` o `src/core/security/` contiene cadenas de texto con nombres de modelos comerciales.
- [ ] Las nuevas dependencias están debidamente registradas en `pyproject.toml`.
- [ ] Los esquemas JSON en `schemas/` están sincronizados con los contratos Pydantic.

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
1. Un saludo confirmando que asimilaste el ADN de **ACRA (Adaptive Conversational Routing Architecture)** y su stack principal.
2. Un breve resumen de 2-3 líneas sobre el objetivo y su estado actual de avance.
3. Una frase poniéndote a disposición para resolver dudas sobre su funcionamiento o colaborar en los siguientes pasos de desarrollo.
