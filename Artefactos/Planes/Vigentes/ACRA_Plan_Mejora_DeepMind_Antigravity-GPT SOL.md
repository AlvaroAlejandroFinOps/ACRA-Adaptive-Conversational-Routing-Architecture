# ACRA: Plan de mejora para evaluación por Google DeepMind

> **Documento de trabajo para Antigravity IDE Agent**  
> **Proyecto:** ACRA, Adaptive Conversational Routing Architecture  
> **Objetivo:** convertir el MVP experimental actual en un proyecto técnicamente sólido, seguro, reproducible y presentable ante un equipo de investigación como Google DeepMind.  
> **Restricción vigente:** no existe presupuesto para consumir APIs comerciales de modelos de frontera. El plan prioriza pruebas locales, modelos abiertos, simulación controlada, datasets públicos y artefactos reproducibles sin costo de API.

---

## 0. Instrucciones operativas para el agente Antigravity

Este archivo es un **plan de remediación y evolución**, no una autorización para reescribir indiscriminadamente la arquitectura.

El agente debe:

1. Inspeccionar el repositorio real antes de modificar archivos.
2. Considerar la semilla maestra como mapa arquitectónico, no como evidencia de ejecución.
3. Respetar las reglas existentes:
   - El clúster Pro no recibe historial conversacional bruto.
   - El handoff debe producir un `CleanPayload` controlado.
   - Toda inferencia debe pasar por `ACRAStateMachine`.
   - Los contratos públicos deben mantener tipado estricto y validación Pydantic.
4. No afirmar que una vulnerabilidad está confirmada hasta localizarla en el código o reproducirla mediante una prueba.
5. Implementar cambios en unidades pequeñas, con pruebas y documentación.
6. No introducir credenciales, API keys ni dependencias obligatorias de pago.
7. Mantener un modo completamente local y determinista.
8. Registrar cada modificación en un changelog técnico.
9. Diferenciar en cada entrega:
   - hallazgo confirmado;
   - riesgo arquitectónico;
   - cambio implementado;
   - deuda pendiente;
   - evidencia obtenida.
10. Antes de cerrar una tarea, ejecutar las pruebas relacionadas y registrar el resultado exacto.

### Formato obligatorio de trabajo por hallazgo

Para cada punto del plan:

```text
Hallazgo:
Evidencia en el repositorio:
Riesgo:
Archivos afectados:
Cambio mínimo propuesto:
Pruebas nuevas o modificadas:
Criterios de aceptación:
Impactos laterales:
Estado: pendiente | en progreso | implementado | bloqueado
```

---

# 1. Posibilidad de que el proyecto sea abordado por Google DeepMind

## 1.1 Evaluación

Sí. El problema que aborda ACRA tiene afinidad con líneas de investigación y desarrollo relacionadas con:

- comprensión y gestión de contexto largo;
- estabilidad en conversaciones multi-turno;
- routing entre modelos con diferente costo y capacidad;
- sistemas agentic y multiagente;
- memoria jerárquica;
- context engineering;
- eficiencia de inferencia;
- seguridad y observabilidad de agentes;
- optimización conjunta de calidad, costo y latencia.

La tesis central puede expresarse así:

> ACRA trata la conversación como material fuente que debe compilarse en una especificación de ejecución segura, trazable y de alta densidad antes de entregarla al modelo de razonamiento.

Esta formulación es más fuerte que presentar ACRA solamente como un resumidor de conversaciones.

## 1.2 Aspectos potencialmente atractivos para un laboratorio de frontera

### A. Routing aprendido

Evolucionar desde reglas y umbrales fijos hacia un router que estime varias dimensiones:

- completitud de intención;
- ambigüedad residual;
- suficiencia de datos;
- riesgo de seguridad;
- necesidad de herramientas;
- costo esperado;
- dificultad de razonamiento;
- probabilidad de éxito del modelo Edge;
- beneficio esperado de escalar al modelo Pro.

A futuro, este router podría investigarse mediante:

- clasificación supervisada;
- contextual bandits;
- aprendizaje por preferencias;
- reinforcement learning offline;
- optimización multiobjetivo;
- calibración probabilística.

### B. Compresión verificable

El compresor debe preservar explícitamente:

- requisitos vigentes;
- negaciones;
- excepciones;
- restricciones numéricas;
- dependencias temporales;
- entidades;
- artefactos de código;
- decisiones aceptadas;
- decisiones reemplazadas;
- procedencia;
- nivel de confianza.

El objetivo científico no debe ser solamente comprimir más, sino demostrar que se conserva lo necesario para resolver la tarea.

### C. Contexto jerárquico

Separar el estado en niveles:

1. historial bruto cifrado y sujeto a retención;
2. memoria episódica de sesión;
3. requisitos consolidados;
4. hechos con procedencia;
5. artefactos validados;
6. decisiones vigentes y reemplazadas;
7. payload final para inferencia.

### D. Evaluación causal

Demostrar qué componente produce la mejora mediante ablaciones:

- baseline con historial completo;
- baseline con truncamiento;
- baseline con resumen simple;
- ACRA sin assistant masking;
- ACRA sin Edge Router;
- ACRA sin máquina de estados;
- ACRA sin contexto unificado;
- ACRA completo.

### E. Seguridad formal del handoff

El `CleanPayload` debe ser el resultado de una política verificable. No basta con establecer `is_sterilized=True`. Debe existir evidencia de:

- procedencia preservada;
- secretos redactados;
- PII tratada según política;
- instrucciones no confiables aisladas;
- permisos revisados;
- versión de política registrada;
- validaciones superadas.

## 1.3 Obstáculo principal

El principal obstáculo para presentar ACRA como contribución científica es que los resultados actuales se apoyan en modelos mock y distribuciones calibradas. Esto es válido para probar la arquitectura del software y el pipeline experimental, pero no demuestra comportamiento equivalente en modelos reales.

El proyecto debe evitar afirmaciones como:

- “ACRA mejora a los modelos de frontera”;
- “reduce la degradación en producción”;
- “alcanza superioridad estadística general”; 

hasta disponer de evidencia reproducible con modelos reales o, en su defecto, evidencia local claramente delimitada.

## 1.4 Estrategia sin presupuesto de API

La falta de presupuesto no impide producir evidencia útil. El plan debe utilizar una escalera de validación:

### Nivel 1: validación determinista

- mocks versionados;
- entradas congeladas;
- semillas aleatorias fijas;
- pruebas unitarias;
- pruebas de propiedades;
- invariantes de estado;
- casos adversariales manuales.

### Nivel 2: modelos abiertos pequeños en local

Integrar adaptadores opcionales para runtimes gratuitos y locales, por ejemplo:

- Ollama;
- llama.cpp;
- vLLM cuando exista GPU disponible;
- Transformers con modelos pequeños compatibles con CPU.

La implementación debe degradar elegantemente si ninguno está instalado.

### Nivel 3: notebooks gratuitos o créditos puntuales

Preparar notebooks reproducibles para entornos gratuitos o académicos, sin convertirlos en dependencia del proyecto. Los resultados deben registrar hardware, modelo, cuantización, versión y semilla.

### Nivel 4: colaboración externa

Publicar un benchmark pequeño, un protocolo de reproducción y un formulario de resultados para que terceros ejecuten modelos mayores y devuelvan métricas verificables.

---

# 2. Vulnerabilidades y debilidades que deben investigarse

> **Nota:** los siguientes puntos son hipótesis de riesgo arquitectónico derivadas de la semilla. Antigravity debe comprobar su presencia en el repositorio antes de marcarlas como vulnerabilidades confirmadas.

## 2.1 Prompt injection persistente

### Riesgo

Una instrucción maliciosa podría ser interpretada por el compresor como requisito duro y quedar preservada en el contexto consolidado. El enmascaramiento de respuestas del asistente no elimina instrucciones maliciosas procedentes del usuario, documentos, herramientas o memoria.

La compresión podría incluso transformar una instrucción maliciosa extensa y ambigua en una instrucción breve y más efectiva.

### Archivos iniciales a inspeccionar

- `src/core/dhc.py`
- `src/core/handoff.py`
- `src/core/orchestrator.py`
- `src/core/models/llm_adapter.py`
- `schemas/conversation_state.json`

### Mejora requerida

Agregar clasificación de confianza y procedencia. Como mínimo:

```text
SYSTEM_POLICY
DEVELOPER_POLICY
USER_INSTRUCTION
EXTERNAL_UNTRUSTED_DATA
TOOL_OUTPUT
MEMORY
GENERATED_CONTENT
```

El compresor nunca debe promover contenido externo no confiable a instrucción autorizada.

### Pruebas mínimas

- inyección directa en mensaje de usuario;
- inyección indirecta dentro de documento;
- instrucciones ocultas en bloque de código;
- instrucciones dentro de salida de herramienta;
- intento de promover datos a política;
- inyección persistente recuperada desde memoria;
- texto ofuscado o con caracteres invisibles.

### Criterio de aceptación

El `CleanPayload` mantiene separados datos e instrucciones, conserva la procedencia y no eleva el nivel de autoridad de contenido no confiable.

---

## 2.2 Envenenamiento de memoria

### Riesgo

Un snapshot contaminado puede influir repetidamente en inferencias futuras de la misma sesión o, si existe un error de aislamiento, de otras sesiones.

### Archivo principal

- `src/core/unified_context.py`

### Mejoras requeridas

Cada objeto persistido debe incluir al menos:

- `tenant_id`;
- `user_id` o principal equivalente;
- `session_id`;
- `task_id`;
- procedencia;
- nivel de confianza;
- timestamp de creación;
- expiración;
- versión del esquema;
- versión del compresor;
- versión de política;
- hash autenticado;
- resultado del análisis de seguridad;
- estado de revocación.

Separar lógicamente:

- memoria de usuario;
- memoria de sesión;
- memoria de tarea;
- caché técnico;
- resultados de herramientas;
- artefactos confirmados.

### Pruebas mínimas

- aislamiento entre sesiones;
- aislamiento entre tenants;
- revocación de snapshot;
- expiración;
- intento de cargar una clave manipulada;
- incompatibilidad de versión;
- actualización de permisos;
- replay de estado antiguo.

---

## 2.3 Uso insuficiente de SHA-256

### Riesgo

SHA-256 por sí solo sirve para hash o indexación, pero no proporciona autorización, confidencialidad ni integridad autenticada.

### Mejora requerida

Reemplazar la identidad simple del snapshot por una clave derivada de:

```text
tenant_id
+ user_id
+ session_id
+ task_id
+ schema_version
+ policy_version
+ random_nonce
```

Cuando exista infraestructura de secretos, usar HMAC con una clave gestionada externamente. En modo local, permitir una clave efímera de desarrollo y marcar explícitamente que no es apta para producción.

### Criterio de aceptación

No es posible recuperar un snapshot únicamente conociendo o adivinando el contenido de la conversación. Toda lectura valida identidad, ámbito, versión y autorización.

---

## 2.4 Fuga de información en `CleanPayload`

### Riesgo

`is_sterilized=True` no demuestra que se hayan eliminado:

- credenciales pegadas por el usuario;
- tokens;
- información personal;
- URLs firmadas;
- nombres internos;
- secretos contenidos en código;
- datos no necesarios para el propósito.

### Mejora requerida

Crear un `PayloadPolicyGate` entre DHC y Handoff con:

1. detección de secretos;
2. clasificación de PII;
3. redacción configurable;
4. validación de propósito;
5. política de retención;
6. auditoría del contenido transferido;
7. resultado estructurado de validación.

### Ubicación sugerida

- nuevo módulo: `src/core/payload_policy.py`
- integración: `src/core/orchestrator.py`
- integración: `src/core/handoff.py`
- contratos: `schemas/conversation_state.json`

### Criterio de aceptación

No se genera un `CleanPayload` listo para inferencia si las validaciones obligatorias no han terminado satisfactoriamente.

---

## 2.5 Manipulación del maturity score

### Riesgo

Un único score puede confundir completitud formal con seguridad o corrección semántica. Un mensaje podría parecer maduro y, sin embargo, ser peligroso, contradictorio o insuficiente.

### Mejora requerida

Reemplazar o complementar `maturity_score` con un vector:

```text
intent_completeness
constraint_completeness
data_sufficiency
ambiguity_score
conflict_score
safety_confidence
tool_readiness
expected_edge_success
expected_pro_benefit
```

La decisión debe provenir de una política explícita y auditable.

### Archivo principal

- `src/core/edge_router.py`

### Pruebas mínimas

- solicitud completa pero peligrosa;
- solicitud larga pero contradictoria;
- solicitud corta y suficiente;
- solicitud con datos ausentes;
- intento de forzar despacho mediante palabras clave;
- cuatro aclaraciones sin convergencia;
- score no calibrado o fuera de rango.

---

## 2.6 Pérdida semántica durante la compresión

### Riesgo

El CCR mide reducción, no fidelidad. Una compresión agresiva puede perder negaciones, excepciones, dependencias o restricciones críticas.

### Mejora requerida

Agregar métricas independientes:

- `constraint_recall`;
- `negation_preservation`;
- `exception_preservation`;
- `entity_recall`;
- `artifact_integrity`;
- `provenance_preservation`;
- `semantic_coverage`;
- `decision_supersession_accuracy`;
- `contradiction_retention_or_resolution`.

### Archivos iniciales

- `src/core/metrics.py`
- `src/core/dhc.py`
- `03_Research_AI/experiments/exp_03_ccr_sensitivity.py`
- `03_Research_AI/experiments/exp_05_ablation_study.py`

### Criterio de aceptación

El handoff debe cumplir simultáneamente una meta de compresión y umbrales mínimos de preservación semántica. Si no los cumple, debe reintentar con una compresión menos agresiva o hacer fallback seguro.

---

## 2.7 Assistant Response Masking excesivamente rígido

### Riesgo

Eliminar todo contenido anterior del asistente puede borrar:

- código aceptado por el usuario;
- resultados de herramientas;
- cálculos confirmados;
- decisiones cocreadas;
- artefactos validados;
- definiciones acordadas.

### Mejora requerida

Clasificar fragmentos por función, no solamente por rol:

```text
CHATTER
REJECTED_PROPOSAL
UNVERIFIED_INFERENCE
CONFIRMED_ARTIFACT
ACCEPTED_DECISION
TOOL_EVIDENCE
USER_CONFIRMED_FACT
SUPERSEDED_CONTENT
```

Los elementos confirmados deben conservarse con procedencia y evidencia de aceptación.

### Pruebas mínimas

- código del asistente aceptado explícitamente;
- código rechazado;
- corrección parcial;
- salida de herramienta confirmada;
- explicación irrelevante;
- decisión reemplazada en un turno posterior.

---

## 2.8 Replay y estados obsoletos

### Riesgo

La idempotencia puede reutilizar un payload que ya no es válido porque cambió el modelo, la política, el esquema, los permisos o las instrucciones del usuario.

### Mejora requerida

Incluir en la identidad y validación del snapshot:

- versión del esquema;
- versión del modelo;
- versión del prompt;
- versión de política;
- versión del compresor;
- número monotónico de conversación;
- expiración absoluta;
- estado de revocación.

### Criterio de aceptación

Un snapshot obsoleto se rechaza de forma controlada y activa una reconstrucción segura del contexto.

---

## 2.9 Denial of Wallet y agotamiento de recursos

### Riesgo

Aunque el entorno actual sea local, la arquitectura futura puede ser atacada mediante:

- creación masiva de sesiones;
- clarificaciones sin fin;
- recompresión repetida;
- cache misses deliberados;
- payloads excesivos;
- dispatches Pro innecesarios;
- loops de agentes.

### Mejora requerida

Implementar controles configurables:

- presupuesto de tokens por tarea;
- límite de turnos;
- límite de clarificaciones;
- límite de recompresiones;
- límite de sesiones por principal;
- deduplicación;
- circuit breaker;
- backpressure;
- timeout;
- cuota de cómputo;
- detección de abuso.

### Archivos iniciales

- `src/core/orchestrator.py`
- `src/core/state_machine.py`
- `src/core/edge_router.py`
- `config/acra_config.yaml`

---

## 2.10 Observabilidad de seguridad insuficiente

### Riesgo

Las métricas actuales se concentran en compresión, caché y verbosidad. Para un sistema agentic faltan señales de seguridad y gobernanza.

### Agregar métricas y eventos

- `prompt_injection_risk_score`;
- `untrusted_fragment_count`;
- `pii_redaction_count`;
- `secret_redaction_count`;
- `policy_gate_rejection_count`;
- `snapshot_authorization_failure_count`;
- `replay_rejection_count`;
- `router_drift_score`;
- `cost_anomaly_score`;
- `pro_dispatch_rate`;
- `clarification_loop_count`;
- `provenance_coverage_pct`.

### Requisito adicional

No registrar payloads completos por defecto. Los logs deben ser estructurados, minimizados y libres de secretos.

---

# 3. Plan de implementación priorizado

## Fase P0: seguridad y contratos antes de usar modelos reales

### Objetivo

Crear una frontera de confianza verificable entre conversación, memoria y modelo Pro.

### Tareas

- [ ] Inventariar todos los puntos donde se crea, transforma, persiste o rehidrata contexto.
- [ ] Añadir tipos de procedencia y niveles de confianza.
- [ ] Actualizar `MessageTurn`, `CompressedContext`, `ContextSnapshot` y `CleanPayload`.
- [ ] Implementar aislamiento por tenant, usuario, sesión y tarea.
- [ ] Añadir versionado y revocación de snapshots.
- [ ] Implementar `PayloadPolicyGate`.
- [ ] Añadir detección local de patrones de secretos.
- [ ] Añadir una política configurable de PII sin servicios externos.
- [ ] Crear corpus adversarial local.
- [ ] Agregar pruebas de prompt injection y memory poisoning.
- [ ] Documentar un threat model.

### Entregables

- `docs/security/ACRA_Threat_Model.md`
- `docs/security/ACRA_Trust_Boundaries.md`
- `docs/security/ACRA_Data_Flow.md`
- `src/core/payload_policy.py`
- pruebas unitarias y de integración asociadas;
- actualización de esquemas JSON;
- actualización de configuración.

### Criterios de salida

- Ningún contenido pierde su procedencia durante la consolidación.
- Ningún snapshot puede recuperarse fuera de su ámbito.
- El `CleanPayload` incorpora prueba estructurada de validación.
- El corpus adversarial básico se ejecuta en CI local.

---

## Fase P1: validez científica con presupuesto cero

### Objetivo

Producir evidencia reproducible sin depender de APIs comerciales.

### Tareas

- [ ] Definir preguntas de investigación y no solo métricas de producto.
- [ ] Congelar un benchmark versionado de conversaciones.
- [ ] Incorporar baselines fuertes.
- [ ] Implementar adaptador local opcional.
- [ ] Registrar modelo, cuantización, runtime, hardware y semillas.
- [ ] Ejecutar varias semillas por experimento.
- [ ] Calcular intervalos de confianza.
- [ ] Agregar tamaños de efecto.
- [ ] Separar resultados mock de resultados con modelos reales.
- [ ] Añadir evaluación de fidelidad semántica.
- [ ] Publicar todos los parámetros experimentales.

### Baselines obligatorios

1. historial completo;
2. truncamiento por ventana;
3. últimos N turnos;
4. resumen simple;
5. solo mensajes de usuario;
6. ACRA sin router;
7. ACRA sin masking;
8. ACRA sin UCT;
9. ACRA completo.

### Métricas mínimas

- exactitud de tarea;
- tasa de éxito;
- varianza entre semillas;
- tokens de entrada;
- tokens de salida;
- latencia;
- tasa de dispatch Pro;
- número de aclaraciones;
- preservación de restricciones;
- preservación de negaciones;
- integridad de artefactos;
- tasa de fallos de seguridad;
- costo estimado, aunque la ejecución sea local.

### Criterios de salida

- Todos los resultados pueden regenerarse desde un único comando.
- Las tablas distinguen simulación de inferencia real.
- Las conclusiones no exceden la evidencia.
- Existe al menos un resultado reproducible con un modelo abierto local, aunque sea pequeño.

---

## Fase P2: ingeniería productiva

### Objetivo

Convertir el prototipo en un servicio desplegable y observable.

### Tareas

- [ ] Añadir GitHub Actions o pipeline equivalente.
- [ ] Añadir Dockerfile reproducible.
- [ ] Añadir configuración de desarrollo y producción claramente separada.
- [ ] Incorporar OpenTelemetry.
- [ ] Definir SLO y presupuestos de error.
- [ ] Agregar pruebas de carga.
- [ ] Implementar retries acotados y circuit breakers.
- [ ] Diseñar backend distribuido de UCT con autorización.
- [ ] Diseñar estrategia de migración de esquemas.
- [ ] Crear runbooks operativos.
- [ ] Añadir SBOM y escaneo de dependencias.
- [ ] Fijar versiones de dependencias.

### Criterios de salida

- El servicio puede desplegarse sin modificar código.
- Los fallos de backend no corrompen el estado.
- Las llamadas Pro están presupuestadas y trazadas.
- Los logs no contienen secretos ni payloads completos.

---

## Fase P3: investigación avanzada

### Objetivo

Explorar contribuciones diferenciadoras con potencial de publicación.

### Líneas propuestas

- [ ] router aprendido y calibrado;
- [ ] compresor entrenado con preservación de invariantes;
- [ ] routing costo-calidad-latencia;
- [ ] memoria jerárquica;
- [ ] routing multimodal;
- [ ] verificación del handoff;
- [ ] integración con agentes y herramientas;
- [ ] aprendizaje offline a partir de feedback;
- [ ] políticas de abstención;
- [ ] evaluación de generalización entre modelos.

---

# 4. Cambios propuestos por archivo

## `src/core/models/llm_adapter.py`

- Añadir capacidades declarativas del backend.
- Incorporar adaptadores locales opcionales.
- Registrar nombre, versión, contexto máximo y configuración.
- Evitar dependencias obligatorias de proveedores comerciales.

## `src/core/edge_router.py`

- Sustituir el score monolítico por una decisión multidimensional.
- Incorporar calibración y abstención.
- Separar madurez, seguridad y suficiencia.
- Registrar explicación estructurada de la decisión.

## `src/core/dhc.py`

- Preservar procedencia y confianza.
- Clasificar fragmentos por función, no solamente por rol.
- Mantener negaciones, excepciones y decisiones reemplazadas.
- Rechazar promoción de datos no confiables a instrucciones.

## `src/core/unified_context.py`

- Incorporar aislamiento de identidad y ámbito.
- Añadir versionado, revocación e integridad autenticada.
- Separar tipos de memoria.
- Evitar que una clave de contenido sea el único control de acceso.

## `src/core/handoff.py`

- Aceptar únicamente contextos aprobados por política.
- Incluir manifiesto de procedencia.
- Incluir versiones de esquema, política, prompt y modelo.
- Rechazar payloads incompletos u obsoletos.

## `src/core/orchestrator.py`

- Insertar `PayloadPolicyGate`.
- Aplicar presupuestos y límites.
- Registrar la trazabilidad de extremo a extremo.
- Implementar fallback seguro.

## `src/core/state_machine.py`

- Añadir estados de validación, rechazo, revocación y fallback.
- Impedir bypass de controles.
- Cubrir transiciones de error.

## `src/core/metrics.py`

- Añadir métricas de fidelidad semántica.
- Añadir calibración del router.
- Añadir tamaños de efecto e intervalos de confianza.
- Separar métricas de calidad, seguridad, costo y estabilidad.

## `config/acra_config.yaml`

Agregar secciones para:

- seguridad;
- políticas de payload;
- privacidad;
- presupuesto de recursos;
- backends locales;
- observabilidad;
- umbrales de fidelidad;
- estrategia de fallback.

## `schemas/conversation_state.json`

Agregar:

- procedencia;
- nivel de confianza;
- identidad de ámbito;
- versiones;
- estado de validación;
- revocación;
- clasificación de contenido.

## `schemas/routing_decision.json`

Agregar el vector multidimensional de decisión y la política aplicada.

---

# 5. Estrategia experimental sin API key

## 5.1 No simular evidencia que no existe

Los mocks deben estar etiquetados como simulación. Nunca mezclar sus resultados con resultados obtenidos de modelos reales.

## 5.2 Matriz de ejecución recomendada

### Perfil A: CI rápido

- mocks deterministas;
- dataset pequeño;
- pruebas unitarias;
- ataques básicos;
- ejecución en CPU.

### Perfil B: benchmark local

- modelo abierto pequeño;
- cuantización documentada;
- 3 a 5 semillas;
- dataset medio;
- comparación completa de baselines.

### Perfil C: reproducción comunitaria

- notebook autocontenido;
- descarga manual o documentada del modelo;
- resultados serializados;
- manifiesto de entorno;
- checksum de dataset;
- instrucciones para aportar resultados.

## 5.3 Artefactos que deben producir los experimentos

Cada corrida debe generar:

```text
run_id
fecha UTC
commit Git
estado del working tree
modelo
runtime
cuantización
hardware
semilla
configuración ACRA
versión del dataset
métricas por ejemplo
métricas agregadas
errores
latencia
tokens
resultado de controles de seguridad
```

## 5.4 Afirmaciones permitidas según evidencia

### Con mocks solamente

Se puede afirmar:

- el pipeline es determinista bajo condiciones definidas;
- las invariantes se cumplen;
- los módulos se integran;
- las métricas reaccionan como se espera en datos sintéticos.

No se puede afirmar:

- mejora general en LLMs reales;
- reducción real de alucinaciones;
- superioridad sobre modelos de frontera;
- ahorro productivo demostrado.

### Con modelos abiertos locales

Se puede afirmar:

- comportamiento observado en los modelos y versiones probados;
- efecto en el benchmark publicado;
- costo computacional local medido;
- generalización limitada a las condiciones evaluadas.

---

# 6. Estructura recomendada para presentar el proyecto

## 6.1 Repositorio

El repositorio debería permitir comprender en menos de diez minutos:

1. el problema;
2. la hipótesis;
3. la arquitectura;
4. cómo ejecutar una demo local;
5. cómo reproducir el benchmark;
6. qué resultados son mocks;
7. qué limitaciones existen;
8. qué contribución es nueva.

## 6.2 Paper o technical report

Estructura sugerida:

1. Abstract.
2. Problema y motivación.
3. Hipótesis.
4. Related work.
5. Arquitectura ACRA.
6. Modelo de amenazas.
7. Protocolo experimental.
8. Baselines.
9. Resultados.
10. Ablaciones.
11. Análisis de fallos.
12. Limitaciones.
13. Impacto y Responsible AI.
14. Reproducibilidad.
15. Trabajo futuro.

## 6.3 Propuesta de contribuciones científicas

No presentar demasiadas contribuciones. Concentrarse en tres:

1. **Intent Maturation Routing:** retrasar el uso del modelo costoso hasta alcanzar suficiencia verificable.
2. **Provenance-Preserving Context Compilation:** convertir conversación en especificación densa sin perder autoridad ni procedencia.
3. **Causal Isolation Handoff:** reducir contaminación de respuestas previas mediante un límite de ejecución explícito y medible.

---

# 7. Criterios de aceptación globales

El proyecto estará listo para una revisión externa seria cuando:

- [ ] La instalación local sea reproducible.
- [ ] La suite completa se ejecute con un comando.
- [ ] Exista una demostración sin API key.
- [ ] Los resultados mock estén claramente separados.
- [ ] Exista al menos un benchmark con un modelo abierto real.
- [ ] Los baselines sean comparables y públicos.
- [ ] Las ablaciones aíslen la contribución de cada módulo.
- [ ] El CCR no sea la única métrica de compresión.
- [ ] El contexto preserve negaciones, restricciones y procedencia.
- [ ] El `CleanPayload` sea validado, no solamente marcado como limpio.
- [ ] Los snapshots estén aislados y sean revocables.
- [ ] Existan pruebas de prompt injection y memory poisoning.
- [ ] La documentación declare limitaciones sin sobreafirmar resultados.
- [ ] Los experimentos registren modelo, entorno, configuración y semillas.
- [ ] Exista un threat model y un data-flow diagram.
- [ ] CI, lint, typing y tests estén activos.

---

# 8. Priorización ejecutiva

## Urgente

1. Procedencia y límites de confianza.
2. Seguridad de snapshots.
3. Validación real de `CleanPayload`.
4. Fidelidad semántica del compresor.
5. Separación explícita entre mocks y evidencia real.

## Siguiente

1. Adaptador local sin costo.
2. Benchmark reproducible.
3. Baselines y ablaciones.
4. Observabilidad de seguridad.
5. CI/CD y contenedores.

## Futuro

1. Router aprendido.
2. Compresor entrenado.
3. Memoria jerárquica.
4. Optimización costo-calidad-latencia.
5. Validación con modelos mayores mediante colaboración.

---

# 9. Veredicto y dirección recomendada

ACRA posee una tesis arquitectónica atractiva: el modelo de razonamiento no debería recibir una transcripción acumulativa y contaminada, sino una especificación madura, trazable y controlada.

Su mayor potencial es evolucionar hacia una combinación de:

- gateway inteligente para LLMs;
- compilador de contexto;
- control plane de agentes;
- router costo-calidad;
- frontera de seguridad entre memoria e inferencia.

La prioridad no debe ser aumentar las afirmaciones del proyecto, sino aumentar la calidad de la evidencia. La falta de presupuesto para una API no invalida la investigación. Obliga a diseñar mejor la reproducibilidad, utilizar modelos abiertos modestos, separar simulación de observación real y facilitar que terceros ejecuten pruebas de mayor escala.

La meta para una eventual evaluación por Google DeepMind debe ser presentar:

1. una hipótesis precisa;
2. una contribución diferenciada de un resumen convencional;
3. un sistema reproducible sin servicios pagados;
4. una evaluación causal con ablaciones;
5. un modelo de seguridad fuerte;
6. limitaciones transparentes;
7. un camino claro para escalar la validación.

---

# 10. Orden de ejecución para Antigravity

Antigravity debe trabajar en este orden y no avanzar de fase si los criterios anteriores fallan:

1. **Auditoría del repositorio real** contra este documento.
2. **Informe de diferencias** entre la semilla y el código.
3. **Threat model y límites de confianza**.
4. **Contratos de procedencia, identidad y versionado**.
5. **PayloadPolicyGate y seguridad del UCT**.
6. **Pruebas adversariales**.
7. **Métricas de fidelidad semántica**.
8. **Baselines y ablaciones deterministas**.
9. **Adaptador local opcional**.
10. **Benchmark reproducible con modelo abierto**.
11. **Observabilidad, CI y empaquetado**.
12. **Actualización del paper, benchmark report y Seed Master**.

Al completar cada punto, el agente debe informar:

```text
Cambios realizados
Archivos modificados
Pruebas ejecutadas
Resultados exactos
Riesgos residuales
Supuestos
Trabajo pendiente
```

**No marcar el proyecto como “validado para modelos de frontera” hasta disponer de evidencia directa y reproducible.**
