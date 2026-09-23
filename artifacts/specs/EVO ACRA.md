# MISIÓN: PLAN DE EVOLUCIÓN DE ACRA HACIA UN ROUTER JERÁRQUICO DE AGENTES

Analiza la ThinkingSeed Master y el repositorio actual de ACRA antes de proponer
cualquier modificación.

La semilla representa el ADN y el estado actual del proyecto, pero la visión de
ACRA ha evolucionado. No debes interpretar la arquitectura Edge/Pro actual como
el destino final ni eliminarla automáticamente. Debes identificar qué componentes
pueden generalizarse y reutilizarse dentro de la nueva arquitectura.

## 1. NUEVA VISIÓN DEL PROYECTO

ACRA debe evolucionar desde un router conversacional Edge/Pro hacia una
arquitectura agnóstica de proveedores para el enrutamiento jerárquico de agentes.

ACRA debe poder coordinar flujos agénticos que utilicen modelos de diferentes
proveedores, incluyendo, sin limitarse a:

- Anthropic
- Google
- OpenAI
- modelos locales
- futuros proveedores compatibles mediante adaptadores

No se deben codificar nombres de modelos concretos dentro de la lógica del
dominio. Los modelos deben seleccionarse mediante perfiles declarativos de
capacidad, costo, latencia, contexto, seguridad y confiabilidad.

## 2. OBJETIVO PRINCIPAL

Diseñar una arquitectura que permita:

1. Recibir un objetivo complejo del usuario.
2. Evaluar su dominio, alcance, riesgo y complejidad.
3. Seleccionar un agente planificador y un perfil de modelo adecuado.
4. Generar un plan maestro.
5. Descomponer el objetivo en dominios o unidades organizacionales.
6. Crear definiciones de agentes especializados por dominio.
7. Aislar el contexto, memoria, políticas y herramientas de cada agente.
8. Instanciar agentes efímeros para tareas concretas.
9. Seleccionar modelos diferentes para planificación, razonamiento, ejecución,
   validación y escalamiento.
10. Aplicar ingeniería de contexto antes de cada handoff.
11. Evitar propagación innecesaria del historial entre agentes.
12. Controlar entropía contextual, tokens, costo, latencia y riesgo.
13. Consolidar los resultados sin mezclar contextos incompatibles.
14. Registrar procedencia, decisiones, evidencia y consumo de recursos.
15. Retirar o revocar las instancias y contextos cuando termine la tarea.

## 3. CASO DE REFERENCIA OBLIGATORIO

Utiliza como escenario de validación una ticketera empresarial que atiende a cinco
gerencias con contextos, políticas, herramientas y restricciones diferentes.

Flujo esperado:

1. El usuario solicita crear una ticketera para cinco gerencias.
2. ACRA evalúa la complejidad del objetivo.
3. Un Strategic Planner Agent, asignado a un perfil de modelo de alta capacidad,
   crea el plan general.
4. Un Domain Decomposer o Agent Factory, asignado a un perfil medio, crea las
   definiciones de cinco agentes especializados, uno por gerencia.
5. Cada agente de gerencia posee:
   - contexto aislado;
   - políticas propias;
   - fuentes autorizadas;
   - herramientas permitidas;
   - memoria separada;
   - presupuesto de tokens y costo;
   - criterios de escalamiento;
   - contrato de entrada y salida.
6. Cuando llega un ticket, un Intake Router identifica la gerencia, intención,
   prioridad, sensibilidad, complejidad y riesgo.
7. El ticket se entrega únicamente al agente especializado correspondiente.
8. Un Planning Agent genera el plan de resolución usando un perfil de modelo
   apropiado para la complejidad.
9. Uno o más Execution Agents ligeros ejecutan las tareas autorizadas.
10. Un Validator Agent comprueba el resultado antes del cierre.
11. Si existe ambigüedad, riesgo, conflicto de políticas o baja confianza, ACRA
    escala la tarea a otro perfil de modelo o a revisión humana.
12. Al finalizar, ACRA conserva solo el resumen, evidencia y decisiones necesarias.
    El contexto transitorio debe expirar o ser revocado.

## 4. PRINCIPIOS ARQUITECTÓNICOS

El plan debe preservar los siguientes principios:

### 4.1 Contexto mínimo viable

Cada agente debe recibir solo el contexto necesario para su responsabilidad.
No debe recibir el historial conversacional completo por defecto.

### 4.2 Aislamiento por dominio

Los contextos, memorias, políticas, herramientas y datos de una gerencia no
pueden filtrarse a otra, salvo mediante un contrato explícito y autorizado.

### 4.3 Handoffs tipados y esterilizados

Toda comunicación entre agentes debe realizarse mediante contratos versionados.
No se debe reenviar texto conversacional libre cuando pueda utilizarse una
estructura tipada.

### 4.4 Selección agnóstica de modelos

La lógica debe seleccionar perfiles de capacidad, no marcas o versiones fijas.

Perfiles iniciales sugeridos:

- frontier_planner
- complex_reasoner
- domain_planner
- lightweight_executor
- classifier
- validator
- fallback_local

Cada perfil debe declarar:

- capacidades requeridas;
- contexto máximo;
- costo máximo;
- latencia objetivo;
- nivel de riesgo permitido;
- soporte de herramientas;
- soporte de salida estructurada;
- proveedor preferido y proveedores alternativos.

### 4.5 Separación entre planificar y ejecutar

El agente que diseña un plan no debe obtener automáticamente permisos para
ejecutarlo. La ejecución requiere políticas, herramientas y autorización propias.

### 4.6 Agentes efímeros

Distinguir entre AgentDefinition y AgentInstance. Una definición puede ser
persistente, pero una instancia debe tener ciclo de vida, presupuesto, contexto
y permisos limitados.

### 4.7 Gobernanza por tarea y por grafo

Los límites no deben existir solo por sesión. Incorporar presupuestos por:

- objetivo;
- agente;
- tarea;
- modelo;
- herramienta;
- rama del grafo;
- flujo completo.

### 4.8 Escalamiento reversible

Una tarea puede escalar a un modelo más potente cuando su confianza sea baja,
pero también debe poder volver a un modelo ligero después de resolver la
ambigüedad.

### 4.9 Procedencia completa

Cada resultado debe indicar:

- agente que lo produjo;
- perfil de modelo utilizado;
- contexto recibido;
- herramientas invocadas;
- políticas aplicadas;
- costo aproximado;
- tokens consumidos;
- nivel de confianza;
- evidencias;
- agente o humano que validó el resultado.

### 4.10 Protección contra degradación

El sistema debe controlar explícitamente:

- crecimiento contextual;
- redundancia;
- contradicciones;
- instruction drift;
- memory poisoning;
- propagación de alucinaciones;
- ciclos entre agentes;
- duplicación de tareas;
- colisiones de escritura;
- escalamiento infinito;
- fan-out descontrolado;
- exceso de costo.

## 5. REUTILIZACIÓN DEL ADN ACTUAL

Analiza específicamente los siguientes componentes actuales y determina cómo
generalizarlos:

- src/core/orchestrator.py
- src/core/edge_router.py
- src/core/dhc.py
- src/core/payload_policy.py
- src/core/handoff.py
- src/core/unified_context.py
- src/core/state_machine.py
- src/core/governance.py
- src/core/metrics.py
- src/core/models/llm_adapter.py
- schemas/
- config/acra_config.yaml
- tests/

Considera las siguientes posibles evoluciones, pero no las aceptes sin analizar:

- ACRAOrchestrator -> HierarchicalAgentOrchestrator
- EdgeRouter -> CapabilityAndAgentRouter
- DynamicHistoryCompressor -> ContextEngineeringPipeline
- CleanPayload -> ContextCapsule o AgentTaskEnvelope
- UnifiedContextTier -> ScopedContextRegistry
- ResourceGovernor -> HierarchicalBudgetGovernor
- StateMachine -> AgentLifecycle y WorkflowStateMachine
- BaseLLMAdapter -> ProviderAdapter con ModelCapabilityRegistry
- PayloadPolicyGate -> HandoffPolicyGate

Identifica qué clases pueden mantenerse sin cambios, cuáles requieren
generalización, cuáles deben dividirse y cuáles deben quedar obsoletas.

## 6. ENTIDADES Y CONTRATOS QUE DEBES EVALUAR

Analiza la incorporación de contratos tipados para:

- AgentDefinition
- AgentInstance
- AgentCapability
- AgentPolicy
- AgentLifecycle
- ModelProfile
- ProviderProfile
- ModelSelectionDecision
- TaskDefinition
- TaskExecution
- TaskDependency
- AgentGraph
- ContextCapsule
- ContextBudget
- HandoffEnvelope
- ToolGrant
- EscalationPolicy
- ValidationResult
- ExecutionEvidence
- AgentOutcome
- ConsolidatedOutcome

No generes implementaciones completas en esta fase. Define responsabilidades,
relaciones, invariantes y ubicación propuesta.

## 7. MÁQUINAS DE ESTADO

Evalúa si la FSM conversacional actual debe descomponerse al menos en:

1. SessionStateMachine
2. ObjectiveStateMachine
3. AgentInstanceStateMachine
4. TaskStateMachine
5. HandoffStateMachine

Incluye estados, transiciones válidas, transiciones prohibidas y condiciones de
terminación. Presta especial atención a ciclos, retries y escalamiento infinito.

## 8. INGENIERÍA DE CONTEXTO

Diseña conceptualmente un Context Engineering Pipeline con etapas como:

1. ingestión;
2. clasificación;
3. recuperación selectiva;
4. deduplicación;
5. detección de contradicciones;
6. segmentación por dominio;
7. sanitización;
8. compresión;
9. preservación de decisiones y evidencias;
10. cálculo de presupuesto contextual;
11. ensamblado del Context Capsule;
12. sellado o hash;
13. expiración y revocación.

Define métricas para evaluar higiene contextual:

- context relevance ratio;
- context redundancy ratio;
- contradiction density;
- unsupported claim propagation;
- tokens per successful outcome;
- handoff expansion ratio;
- context reuse ratio;
- task retry rate;
- cross-domain leakage rate;
- routing regret;
- escalation efficiency;
- cost per validated task.

No inventes fórmulas como hechos. Si propones fórmulas nuevas, márcalas como
propuestas experimentales.

## 9. PROVEEDORES Y MODELOS

La arquitectura debe ser independiente de Anthropic, Google y OpenAI.

Diseña una capa de adaptadores donde cada proveedor exponga capacidades
normalizadas, tales como:

- structured_output;
- tool_calling;
- long_context;
- reasoning;
- multimodal;
- streaming;
- cached_context;
- safety_controls;
- estimated_cost;
- expected_latency.

El router debe resolver un perfil lógico a un proveedor y modelo disponibles en
runtime.

Ejemplo conceptual:

frontier_planner -> modelo disponible con alta capacidad de planificación;
domain_planner -> modelo medio con salida estructurada;
lightweight_executor -> modelo de bajo costo con tool calling;
validator -> modelo independiente del productor cuando el riesgo lo requiera.

Los nombres concretos de modelos deben permanecer en configuración y no en el
núcleo del dominio.

## 10. SEGURIDAD Y CONTROL

Incluye en el plan:

- aislamiento multi-tenant;
- aislamiento por gerencia;
- prevención de prompt injection;
- control de memoria contaminada;
- autorización de herramientas;
- separación plan/execute;
- validación de acciones destructivas;
- idempotencia;
- control de concurrencia;
- prevención de escrituras simultáneas incompatibles;
- trazabilidad;
- revocación de contexto;
- human-in-the-loop según riesgo;
- redacción de secretos y PII;
- límites de profundidad y anchura del grafo.

## 11. ENTREGABLE SOLICITADO

Crea un plan de evolución técnico, no una implementación inmediata.

El documento debe contener:

1. Resumen ejecutivo de la nueva visión.
2. Diferencias entre la arquitectura actual y la arquitectura objetivo.
3. Componentes actuales reutilizables.
4. Componentes que deben cambiar.
5. Arquitectura lógica objetivo.
6. Grafo jerárquico de agentes.
7. Flujo completo del caso de la ticketera.
8. Modelo de datos y contratos propuestos.
9. Estrategia de selección de modelos.
10. Ingeniería y ciclo de vida del contexto.
11. FSM o máquinas de estado necesarias.
12. Seguridad, gobernanza y aislamiento.
13. Observabilidad y métricas.
14. Estrategia de pruebas.
15. Plan de migración incremental por fases.
16. Rutas exactas de archivos afectados.
17. Riesgos y mitigaciones.
18. Criterios de aceptación por fase.
19. Preguntas abiertas que realmente bloqueen decisiones.
20. Lista de elementos que quedan deliberadamente fuera de alcance.

## 12. FASES MÍNIMAS DEL PLAN

Propón fases pequeñas y verificables. Como referencia:

- Fase 0: actualización del modelo conceptual y ADR.
- Fase 1: contratos de agentes, tareas, modelos y contextos.
- Fase 2: registro de capacidades y selección agnóstica de modelos.
- Fase 3: aislamiento de contexto y Context Capsules.
- Fase 4: Agent Registry, Agent Factory e instancias efímeras.
- Fase 5: orquestador jerárquico y grafo de tareas.
- Fase 6: handoffs tipados, políticas y validación.
- Fase 7: gobernanza jerárquica de costos, tokens y concurrencia.
- Fase 8: caso E2E de la ticketera con cinco gerencias.
- Fase 9: adaptadores reales multi-proveedor.
- Fase 10: benchmarks de degradación, entropía, calidad y costo.

Para cada fase entrega:

- objetivo;
- alcance;
- archivos afectados;
- contratos nuevos o modificados;
- pruebas;
- riesgos;
- dependencias;
- criterio de aceptación;
- estrategia de rollback.

## 13. RESTRICCIONES

- No reescribas todo el proyecto desde cero.
- No elimines el ADN funcional existente sin justificarlo.
- No implementes proveedores reales antes de estabilizar los contratos.
- No mezcles lógica de proveedor con lógica de dominio.
- No compartas contexto global completo entre agentes.
- No permitas handoffs sin validación.
- No permitas ejecución de herramientas solo porque un plan la solicite.
- No uses nombres concretos de modelos dentro de enums centrales.
- No afirmes que una métrica es científicamente válida sin evidencia.
- No modifiques código en esta etapa.
- No crees archivos todavía, excepto el documento de plan solicitado.
- Conserva Python 3.10+, Pydantic v2, tipado estricto, Ruff y los contratos
  versionados existentes.

## 14. FORMATO DE RESPUESTA

Antes del plan:

1. Resume en no más de diez puntos tu comprensión de la nueva visión.
2. Explica qué partes de la semilla actual siguen vigentes.
3. Identifica cualquier contradicción crítica entre el diseño actual y el nuevo.

Después, genera el plan completo y guárdalo en:

artifacts/plans/active/ACRA_Hierarchical_Agent_Router_Evolution_Plan.md

No implementes el plan todavía.

Finaliza con:

- decisiones arquitectónicas pendientes;
- cinco riesgos principales;
- primera fase recomendada;
- criterios para autorizar la implementación.

# EXTENSIÓN OBLIGATORIA: AUDITORÍA DE ENTROPÍA CONTEXTUAL Y ECONOMÍA DE CACHÉ

La arquitectura objetivo de ACRA debe incorporar los principios relevantes del
proyecto Context Entropy Auditor, CEA, sin fusionar ambos repositorios de forma
irreflexiva.

CEA debe analizarse como una posible capa independiente de auditoría contextual,
mientras ACRA conserva la responsabilidad de orquestación, enrutamiento,
gobernanza y ciclo de vida de agentes.

No implementes esta integración todavía. Diseña su arquitectura, contratos,
puntos de extensión, fases de adopción y criterios de aceptación.

## 1. PRINCIPIO EPISTEMOLÓGICO

ACRA no debe afirmar acceso a mecanismos internos no observables de un modelo.

Está prohibido afirmar que ACRA conoce directamente:

- pesos internos;
- logits;
- residual streams;
- mecanismos internos de atención;
- contenido físico del KV Cache;
- tasa real de reutilización de caché si el proveedor no la reporta;
- causas internas de una alucinación.

Las decisiones deben basarse exclusivamente en:

- contenido observable;
- contratos;
- telemetría de runtime;
- metadatos reportados por proveedores;
- usage records;
- tokens de entrada y salida;
- tokens cacheados reportados;
- identificadores de contexto o caché;
- eventos de herramientas;
- resultados verificables;
- señales deterministas;
- estimaciones explícitamente identificadas como estimaciones.

Toda señal debe declarar provenance y epistemic_status, utilizando categorías
equivalentes a:

- observed;
- runtime_measured;
- provider_reported;
- estimated;
- inferred;
- unknown.

No conviertas una estimación en una medición.

## 2. CONTEXT AUDIT LAYER

Diseña una Context Audit Layer compatible con el enfoque de CEA.

Esta capa debe poder operar:

1. antes de crear un Context Capsule;
2. antes de cada handoff;
3. antes de invocar un modelo;
4. después de una llamada a herramientas;
5. antes de consolidar resultados;
6. antes de retener memoria de largo plazo;
7. antes de cambiar de modelo o proveedor;
8. al cerrar una instancia de agente.

La auditoría debe evaluar como mínimo:

- instruction_conflict;
- task_ambiguity;
- context_contamination;
- evidence_quality;
- state_integrity;
- redundancy_pressure;
- context_utilization;
- evidence_coverage;
- stale_tool_results;
- duplicate_documents;
- identifier_collisions;
- cross_domain_leakage;
- unsupported_claim_propagation.

Mantén las seis dimensiones originales de CEA como núcleo estable. Las
dimensiones adicionales deben declararse como extensiones específicas de ACRA
y no como capacidades ya validadas por CEA.

## 3. SEÑALES DETERMINISTAS ZERO-LLM

La primera fase de auditoría debe ejecutarse sin utilizar otro LLM cuando sea
posible.

Evalúa señales deterministas como:

- estimated_input_tokens;
- estimated_output_tokens;
- context_utilization_ratio;
- exact_document_duplicates;
- duplicate_ids_found;
- superseded_tool_results;
- messages_since_last_user_turn;
- repeated_instruction_ratio;
- stale_context_items;
- orphan_tool_results;
- unresolved_contradictions;
- cross_domain_references;
- handoff_depth;
- graph_fan_out;
- retry_count;
- model_switch_count;
- provider_switch_count;
- context_rebuild_count.

Los algoritmos deterministas deben permanecer desacoplados de proveedores,
red y modelos.

Las estimaciones de tokens deben identificarse como estimaciones salvo que el
proveedor entregue una medición real.

## 4. TRIPLETA OBLIGATORIA DE AUDITORÍA

Toda auditoría contextual debe emitir:

- risk_score;
- confidence;
- evidence_coverage.

Además debe incluir:

- dimension_scores;
- findings;
- evidence_refs;
- triggered_rules;
- limitations;
- recommended_actions;
- requires_policy_approval.

Un contexto con cobertura insuficiente no puede declararse estable únicamente
porque no se detectaron conflictos.

## 5. POLICY MODES

Evalúa incorporar modos de operación equivalentes a:

- AUDIT_ONLY;
- RECOMMEND;
- HUMAN_REVIEW;
- DRY_RUN;
- ENFORCE.

ENFORCE sería una extensión de ACRA y no debe heredarse automáticamente de CEA.

Toda acción destructiva debe exigir aprobación o una política explícita.

Considera destructivas al menos:

- eliminar memoria;
- revocar un Context Capsule;
- reemplazar una fuente canónica;
- cancelar un grafo;
- terminar un agente;
- invalidar una caché reutilizable;
- cambiar de proveedor durante una tarea activa;
- descartar evidencia;
- sobrescribir estado compartido.

## 6. ECONOMÍA DEL TOKEN COMO OBJETIVO DE PRIMERA CLASE

ACRA no debe seleccionar modelos usando solo el precio nominal por token.

Diseña un Token Economy Engine que estime el costo total de continuidad,
ejecución, escalamiento y migración.

El costo total esperado debe considerar, cuando exista telemetría observable:

- uncached_input_tokens;
- cached_input_tokens;
- output_tokens;
- context_rebuild_tokens;
- context_rehydration_tokens;
- summarization_tokens;
- validation_tokens;
- retry_tokens;
- tool_related_tokens;
- routing_overhead_tokens;
- cache_write_cost;
- cache_read_cost;
- provider-specific minimum charges;
- expected latency;
- failure probability;
- expected retry cost.

No asumas que todos los proveedores implementan prompt caching o KV Cache con
la misma semántica.

## 7. CACHE-AWARE MODEL ROUTING

Incorpora afinidad entre una instancia de agente y el modelo o proveedor que
mantiene su continuidad contextual.

Define conceptualmente:

- AgentModelAffinity;
- ModelSessionLease;
- CacheContinuityDescriptor;
- CacheCapabilityProfile;
- ContextReuseEstimate;
- ModelMigrationDecision;
- ContextRehydrationPlan;
- CacheInvalidationEvent.

Un agente no debe cambiar automáticamente de modelo porque otro sea más barato
por token.

Antes de cambiar modelo o proveedor, ACRA debe comparar:

1. costo esperado de continuar;
2. costo esperado de migrar;
3. pérdida esperada de reutilización de contexto;
4. costo de reconstrucción del contexto;
5. riesgo de discontinuidad semántica;
6. compatibilidad de herramientas;
7. compatibilidad de salida estructurada;
8. requisitos de seguridad y residencia;
9. capacidad requerida por la siguiente tarea;
10. salud contextual actual.

## 8. REGLA DE AFINIDAD

La política predeterminada debe ser:

Mantener afinidad con el modelo actual mientras:

- cumpla la capacidad requerida;
- el contexto permanezca saludable;
- el riesgo sea aceptable;
- el presupuesto no sea excedido;
- la caché o continuidad tenga valor económico;
- las herramientas sigan siendo compatibles;
- el proveedor esté disponible;
- la tarea no cambie materialmente de naturaleza.

Permitir migración cuando:

- la capacidad sea insuficiente;
- la ventana contextual sea insuficiente;
- el riesgo contextual sea alto o crítico;
- el modelo presente degradación observable;
- una política exija otro modelo;
- el proveedor esté degradado;
- se requiera una capacidad no disponible;
- la continuidad resulte más costosa que la migración;
- deba realizarse una validación independiente;
- exista una restricción de seguridad, privacidad o cumplimiento.

## 9. CACHE HYSTERESIS

Diseña una política de histéresis que impida oscilaciones frecuentes entre
modelos.

El router no debe cambiar de modelo por mejoras marginales de costo o capacidad.

Evalúa:

- minimum_affinity_turns;
- minimum_affinity_duration;
- switch_cooldown;
- minimum_expected_savings;
- maximum_model_switches_per_task;
- maximum_provider_switches_per_workflow;
- migration_risk_threshold;
- required_capability_delta;
- cache_rebuild_break_even;
- emergency_override.

Los umbrales deben vivir en configuración, nunca hardcodeados.

## 10. CACHE CONTINUITY DESCRIPTOR

Propón un contrato tipado que represente únicamente información observable o
estimada:

- provider_id;
- model_profile_id;
- concrete_model_id;
- session_id;
- agent_instance_id;
- cache_reference;
- cache_scope;
- cache_created_at;
- cache_expires_at;
- reported_cached_tokens;
- reported_uncached_tokens;
- estimated_reusable_tokens;
- stable_prefix_hash;
- system_instruction_hash;
- tool_manifest_hash;
- context_capsule_hash;
- provider_reported_cache_hit;
- observability_level;
- epistemic_status;
- migration_cost_estimate;
- limitations.

No almacenes secretos ni material interno del proveedor.

## 11. STABLE PREFIX ENGINEERING

El diseño debe distinguir entre:

- stable_prefix;
- domain_context;
- task_context;
- volatile_tool_state;
- current_turn;
- expected_output_contract.

Evalúa mantener al inicio del contexto los elementos de mayor estabilidad:

1. identidad y reglas del agente;
2. políticas de seguridad;
3. contrato de herramientas;
4. contexto canónico de la gerencia;
5. taxonomías estables;
6. reglas del workflow.

Los elementos volátiles deben ubicarse en capas separadas y no deben modificar
innecesariamente el prefijo estable.

Toda modificación del prefijo estable debe producir:

- nueva versión;
- nuevo hash;
- evento de invalidación;
- estimación del costo de recache;
- evaluación de impacto sobre agentes activos.

No optimices el orden del prompt para un proveedor específico dentro del core.
Las particularidades deben residir en ProviderAdapter o ProviderPolicy.

## 12. CONTEXT COMPACTION VS CACHE PRESERVATION

No asumas que comprimir siempre reduce costos.

Una compresión puede:

- usar tokens adicionales;
- cambiar un prefijo cacheable;
- destruir referencias de evidencia;
- introducir pérdida semántica;
- obligar a reconstruir la caché;
- alterar el comportamiento del agente.

Antes de compactar, compara:

- costo de mantener el contexto;
- costo de resumir;
- costo de recache;
- tokens que serán reutilizados;
- riesgo de contaminación;
- presión de redundancia;
- proximidad al límite de contexto;
- vida útil esperada de la sesión.

Define al menos estas acciones:

- KEEP_CONTEXT;
- PRUNE_VOLATILE_ITEMS;
- COMPACT_INCREMENTALLY;
- REBUILD_CONTEXT;
- FORK_AGENT_CONTEXT;
- MIGRATE_MODEL;
- TERMINATE_AND_RESTART;
- REQUIRE_HUMAN_REVIEW.

## 13. FORK ANTES QUE CONTAMINAR

Cuando una subtarea cambia de dominio, objetivo o política, ACRA debe evaluar
crear una nueva AgentInstance con un Context Capsule derivado, en vez de
contaminar el contexto del agente original.

El fork debe heredar solo:

- objetivo autorizado;
- decisiones canónicas;
- evidencia necesaria;
- dependencias;
- restricciones;
- contrato de salida.

No debe heredar por defecto:

- conversación completa;
- razonamiento intermedio;
- resultados de herramientas irrelevantes;
- memoria privada de otra gerencia;
- instrucciones temporales;
- errores o hipótesis descartadas.

## 14. AUDITORÍA ANTES Y DESPUÉS DEL HANDOFF

Todo handoff debe tener:

- pre_handoff_audit;
- sanitized_handoff_envelope;
- post_handoff_validation.

El receptor debe ser capaz de verificar:

- versión de esquema;
- hash del Context Capsule;
- agente emisor;
- dominio;
- objetivo;
- evidencia;
- permisos;
- presupuesto;
- expiración;
- limitaciones;
- estado de auditoría.

Un handoff de riesgo alto no debe ejecutarse sin remediación, escalamiento o
revisión.

## 15. INTEGRACIÓN MODULAR CON CEA

Evalúa tres alternativas y recomienda una:

A. Reimplementar principios mínimos de CEA dentro de ACRA.
B. Consumir CEA como librería independiente.
C. Definir una interfaz ContextAuditProvider que permita usar CEA u otros
   auditores mediante adaptadores.

Prioriza desacoplamiento y evita duplicar lógica validada.

La opción de integración debe contemplar:

- versionado de contratos;
- compatibilidad Pydantic;
- JSON Schema;
- operación stateless;
- timeout;
- circuit breaker;
- fallback determinista;
- política ante auditor no disponible;
- trazabilidad;
- benchmarks separados.

## 16. COMPONENTES ACTUALES DE CEA A EVALUAR

Analiza conceptualmente la reutilización o adaptación de:

- src/context_auditor/auditor.py
- src/context_auditor/models.py
- src/context_auditor/scoring.py
- src/context_auditor/signals.py
- src/context_auditor/policies.py
- src/context_auditor/validators.py
- src/context_auditor/adapters/base.py
- config/scoring_defaults.yaml
- schemas/audit-input.schema.json
- schemas/audit-result.schema.json
- tests/unit/
- tests/e2e/

No copies archivos automáticamente.

Primero define:

- límites de responsabilidad;
- contratos de integración;
- dependencias;
- ciclo de vida;
- estrategia de versionado;
- ownership;
- pruebas de contrato.

## 17. NUEVAS MÉTRICAS PARA ACRA

Incluye en el plan métricas observables o estimables:

- context_risk_score;
- evidence_coverage;
- context_utilization_ratio;
- context_reuse_ratio;
- provider_reported_cache_hit_ratio;
- estimated_cache_reuse_ratio;
- context_rebuild_tokens;
- effective_cost_per_validated_task;
- tokens_per_validated_outcome;
- model_switch_count;
- provider_switch_count;
- avoidable_model_switch_rate;
- cache_break_even_accuracy;
- context_compaction_regret;
- routing_regret;
- retry_amplification;
- handoff_expansion_ratio;
- stale_tool_result_rate;
- cross_domain_leakage_rate;
- unsupported_claim_propagation_rate;
- agent_context_contamination_rate.

Distingue estrictamente entre:

- measured;
- provider_reported;
- estimated;
- inferred.

## 18. PRUEBAS OBLIGATORIAS

Agrega al plan pruebas para:

1. mantener afinidad cuando cambiar de modelo no produce ahorro real;
2. migrar cuando el costo esperado de continuidad es mayor;
3. migrar por capacidad insuficiente;
4. evitar oscilaciones entre modelos;
5. invalidar continuidad cuando cambia el prefijo estable;
6. preservar continuidad ante cambios solo en contexto volátil;
7. funcionar cuando el proveedor no reporta caché;
8. no confundir estimación con medición;
9. auditar sin utilizar un LLM;
10. bloquear handoffs con conflicto crítico;
11. impedir estabilidad con evidencia insuficiente;
12. detectar resultados de herramientas superados;
13. detectar contaminación entre gerencias;
14. crear fork de agente antes de mezclar dominios;
15. exigir aprobación para invalidaciones destructivas;
16. calcular costo total incluyendo reconstrucción;
17. operar con caché expirada;
18. degradar de forma segura si CEA no está disponible;
19. respetar presupuestos por agente, tarea y workflow;
20. impedir que nombres de modelos entren al core del dominio.

## 19. CASO DE LA TICKETERA

Añade al caso E2E de la ticketera los siguientes escenarios:

- El agente de una gerencia mantiene afinidad con su modelo mientras resuelve
  tickets relacionados y su contexto permanece saludable.
- Un ticket de otra gerencia crea un agente o contexto independiente.
- Una subtarea rutinaria se delega a un ejecutor ligero mediante un handoff
  mínimo, sin mover el contexto completo del agente planificador.
- El planificador no cambia de modelo solo porque el ejecutor use otro.
- Una tarea crítica puede escalar a un modelo avanzado mediante un Context
  Rehydration Plan explícito.
- La respuesta del modelo avanzado vuelve como un Outcome Capsule, no como un
  reemplazo indiscriminado del contexto de origen.
- Un resultado de herramienta obsoleto se excluye antes de la siguiente
  inferencia.
- Si el contexto del agente se degrada, ACRA compara reparación incremental,
  fork, reconstrucción y migración.
- Toda decisión registra costo estimado, evidencia, riesgo, confianza y cobertura.

## 20. ENTREGABLE ADICIONAL

Dentro del plan de evolución agrega una sección titulada:

"Context Reliability and Token Economy Architecture"

Esta sección debe contener:

1. relación arquitectónica entre ACRA y CEA;
2. Context Audit Layer;
3. señales deterministas;
4. tripleta de auditoría;
5. Cache-Aware Router;
6. Agent-Model Affinity;
7. Stable Prefix Engineering;
8. Token Economy Engine;
9. modelo de costos de continuidad y migración;
10. política de histéresis;
11. contratos propuestos;
12. telemetría y provenance;
13. modos de falla;
14. pruebas;
15. fases de incorporación;
16. preguntas abiertas.

No modifiques código durante esta etapa.