# Referencia 03: Desajuste de Intención (Intent Mismatch) y Ambigüedad Estructural

## 1. Cita Bibliográfica
> **Liu, Y., et al. (2026).** *Intent Mismatch Causes LLMs to Get Lost in Multi-Turn Conversation.* arXiv preprint.

## 2. Resumen del Estudio
Este trabajo analiza *por qué* ocurre la degradación en los turnos conversacionales, argumentando que el problema raíz es el "desajuste de intención" (Intent Mismatch). A medida que la conversación evoluciona y el usuario refina, corrige o cambia sus peticiones, el contexto conversacional se llena de ambigüedad estructural. El LLM se ve obligado a procesar información conflictiva (ej. "Haz X, no, mejor haz Y"), lo que rompe su capacidad para generar respuestas coherentes porque la atención del modelo se divide entre instrucciones contradictorias o descontinuadas presentes en el historial.

## 3. Argumentación Robusta y Aplicación a ACRA (Cognitive Stability)
La hipótesis del *Intent Mismatch* respalda sólidamente los mecanismos de **Lógica de Handoff** y el aislamiento cognitivo que implementa ACRA.

1.  **Vulnerabilidad Cognitiva:** El RFC de ACRA señala la "Desviación por Verbosidad", donde los turnos pasados confunden al modelo. El artículo de Liu et al. confirma que los LLMs son extremadamente susceptibles a procesar el ruido especulativo de turnos previos, tratándolo erróneamente como restricciones activas.
2.  **Mitigación Arquitectónica (ACRA):** La arquitectura ACRA impone una **Línea Base Clean**. Antes de invocar al modelo pesado que resolverá el problema, el orquestador se encarga de abstraer exclusivamente las *intenciones duras* del usuario, filtrando todas las idas y vueltas, dudas, y desajustes ("Intent Mismatch") del historial conversacional.
3.  **Resultado Técnico:** Se interrumpe la cadena causal de degradación descrita en el estudio. El *payload* final que ACRA rutea al modelo Pro representa un "lienzo cognitivamente estéril". Al eliminar los artefactos de las rectificaciones humanas, el modelo no sufre de partición de atención y puede dedicar el 100% de su capacidad inferencial a la intención actual y madura.
