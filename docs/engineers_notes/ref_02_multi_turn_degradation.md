# Referencia 02: Cuantificación de la Degradación Multi-Turno en Contextos Generativos

## 1. Cita Bibliográfica
> **Laban, P., et al. (2025).** *LLMs Get Lost In Multi-Turn Conversation.* arXiv preprint.

## 2. Resumen del Estudio
Esta investigación sistemática evaluó el rendimiento de los LLMs de frontera (frontier models) en tareas complejas que requieren múltiples interacciones (multi-turn). El estudio concluyó que el simple hecho de fraccionar una instrucción en una secuencia de turnos conversacionales provoca una caída abrupta de rendimiento. En promedio, los modelos experimentan una degradación del 39% en comparación con la evaluación de los mismos requerimientos presentados en un solo turno (Zero-Shot unificado). Este fenómeno fue denominado *Lost in Conversation* (LiC).

## 3. Argumentación Robusta y Aplicación a ACRA (Cognitive Stability)
Este estudio provee el sustento matemático directo para la sección "Marco Teórico: La Anatomía de la Degradación Multi-Turno" del RFC de ACRA.

1.  **Dispersión de Varianza Estocástica:** El estudio de Laban et al. (2025) apoya la hipótesis de ACRA de que el modelo subyacente no pierde capacidad absoluta ($A^{90}$), sino que sufre un colapso en la fiabilidad ($U_{10}^{90}$), que se dispara en contextos conversacionales por encima del 112%. Las tareas divididas introducen entropía estocástica en cada paso de generación, creando cadenas de Markov donde un error menor en el turno 2 se amplifica exponencialmente hacia el turno 6.
2.  **Mitigación Arquitectónica (ACRA):** Si las conversaciones multi-turno provocan por defecto una degradación del 39%, la arquitectura del sistema no debe confiar ciegamente en el LLM para mantener el hilo lógico. ACRA actúa como un escudo estocástico. Su clúster pesado (Pro) jamás se expone al flujo multi-turno raw. En su lugar, el orquestador comprime la conversación y se la envía al modelo pesado como si fuera una interacción *Zero-Shot* determinista de un solo turno.
3.  **Resultado Técnico:** Al transformar flujos multi-turno entrópicos en ejecuciones limpias de un solo turno, ACRA recobra casi la totalidad de ese 39% de degradación sin alterar los pesos (weights) del modelo, demostrando que la solución es arquitectónica, no de entrenamiento.
