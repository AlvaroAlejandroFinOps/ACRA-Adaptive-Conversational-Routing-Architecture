# Referencia 04: Fiabilidad Conversacional y Anclaje (Stick-or-Switch)

## 1. Cita Bibliográfica
> **Guo, S., et al. (2026).** *Stop Listening to Me! How Multi-turn Conversations Can Degrade LLM Reliability.* arXiv preprint.

## 2. Resumen del Estudio
Esta investigación documenta cómo las conversaciones extendidas degradan la fiabilidad inherente de los LLMs frente a instrucciones engañosas o cambios de contexto. Identifica problemas críticos como el comportamiento de "stick-or-switch": los modelos tienden a aferrarse rígidamente a suposiciones tempranas defectuosas generadas en los primeros turnos (sticking) a pesar de correcciones posteriores, o cambian ciegamente su comportamiento ante instrucciones incorrectas del usuario (switching). El estudio concluye que interactuar demasiado con un LLM antes de definir el problema cristaliza errores lógicos.

## 3. Argumentación Robusta y Aplicación a ACRA (Cognitive Stability)
El estudio de Guo et al. justifica científicamente el mecanismo de **Aislamiento en Edge Router (Prevención de Anclaje)** de ACRA, diseñado específicamente para evitar que los modelos valiosos caigan en estas trampas cognitivas.

1.  **Vulnerabilidad Cognitiva (Intentos de Respuesta Prematuros):** Como describe el RFC de ACRA, en las fases tempranas de la conversación (0-20% del chat), las especificaciones del usuario son ambiguas. Si un modelo pesado intenta resolver el problema aquí, se auto-convence de soluciones subóptimas y sufre del problema de "sticking" documentado en el paper, anclándose a suposiciones falsas irreversibles (reduciendo su score de 64.4 a 30.9).
2.  **Mitigación Arquitectónica (ACRA):** ACRA resuelve este problema mediante un ruteo asimétrico estricto. El modelo Pro de razonamiento profundo permanece inactivo (aislado) durante la fase de clarificación. Un modelo ligero (Edge Router) es el único encargado de manejar la ambigüedad, hacer preguntas clarificatorias y absorber el riesgo estocástico.
3.  **Resultado Técnico:** Se bloquea matemáticamente el sesgo de respuestas prematuras en el motor principal. Cuando el Edge Router considera que la instrucción es madura, la consolida y la envía al clúster Pro, el cual procesa el problema en frío, sin arrastrar ningún tipo de anclaje (sticking bias) de turnos previos.
