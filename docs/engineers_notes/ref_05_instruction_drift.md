# Referencia 05: Deriva de Instrucciones (Instruction Drift) y Sobreescritura Contextual

## 1. Cita Bibliográfica
> **[Investigadores de Fiabilidad AI] (2026).** *Quantifying Conversational Reliability of Large Language Models under Multi-Turn Interaction.* arXiv preprint.

## 2. Resumen del Estudio
Este documento cuantifica dos vectores de degradación en interacciones multi-turno: la deriva de instrucciones (*instruction drift*) y la sobreescritura contextual. Demuestra que, a medida que aumenta el volumen de tokens generados por el propio modelo en turnos anteriores (sus propias explicaciones largas y verbosas), las instrucciones originales del sistema (System Prompts) y las restricciones iniciales del usuario comienzan a diluirse y son "sobreescritas" en la atención del modelo por el texto generado recientemente, induciendo alucinaciones progresivas y fallos de consistencia.

## 3. Argumentación Robusta y Aplicación a ACRA (Cognitive Stability)
La cuantificación de la deriva de instrucciones obliga a replantear el manejo del estado conversacional. Apoya directamente el **Mandato 1: Enmascaramiento Asimétrico del Asistente** definido en la arquitectura ACRA.

1.  **Vulnerabilidad Cognitiva:** Los LLMs tienden a la hipertrofia de respuesta. Su propia verbosidad en turnos anteriores se vuelve un lastre cognitivo. Como indica el paper, este texto actúa como ruido que diluye las restricciones core de la tarea, lo que resulta en respuestas cada vez más largas y menos apegadas al *System Prompt*.
2.  **Mitigación Arquitectónica (ACRA):** ACRA no almacena la conversación cruda. Implementa un *Filtro de Enmascaramiento Asimétrico* en su *Unified Context Tier*. El sistema descarta intencionalmente la verbosidad explicativa generada por el LLM en turnos previos. Sólo se rehidratan los requerimientos explícitos del usuario y los bloques de ejecución dura (por ejemplo, fragmentos de código o *tool-calls* confirmados).
3.  **Resultado Técnico:** Al silenciar el "código basura" del propio LLM, ACRA previene físicamente la sobreescritura contextual y el *instruction drift*. Cada invocación se adhiere férreamente a las directrices de seguridad y operativas porque no hay texto intermedio excesivo compitiendo por el peso de la atención (Attention Weights).
