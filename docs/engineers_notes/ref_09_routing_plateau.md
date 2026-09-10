# Referencia 09: Límites de Enrutamiento (The Routing Plateau) y Ratio de Consolidación

## 1. Cita Bibliográfica
> **[Investigadores de Costo/Beneficio en LLMs] (2025).** *The Routing Plateau: Understanding and Breaking the Accuracy Limits of LLM Routers.* arXiv preprint.

## 2. Resumen del Estudio
Este estudio expone "el estancamiento del enrutamiento" (The Routing Plateau). Demuestra que los enrutadores tradicionales basados en clasificadores pre-entrenados alcanzan un límite rápido en sus mejoras de precisión frente a fallos dinámicos en la recuperación de contexto. Cuando los routers solo intentan predecir qué modelo es "mejor" sin gestionar el *estado* del contexto, el rendimiento del sistema completo se estanca, ya que envían prompts ruidosos o incompletos al mejor modelo, resultando en respuestas de baja calidad independientemente del modelo seleccionado.

## 3. Argumentación Robusta y Aplicación a ACRA (Cognitive Stability)
La teoría del *Routing Plateau* valida la necesidad de ir más allá del enrutamiento pasivo e introducir métricas de consolidación de contexto como las delineadas en ACRA.

1.  **Vulnerabilidad Cognitiva:** Seleccionar el modelo correcto es inútil si el *payload* (el texto enviado) arrastra el ruido estocástico de diez turnos conversacionales previos. El modelo fallará por exceso de contexto irresoluble, no por falta de capacidad intrínseca.
2.  **Mitigación Arquitectónica (ACRA):** ACRA rompe este estancamiento mediante el **Mandato 2: Implementación del Context Consolidation Ratio (CCR)**. ACRA exige a los sistemas medir qué porcentaje de tokens estocásticos inútiles (saludos, verbosidad) el enrutador logró purgar *antes* de invocar al clúster pesado.
3.  **Resultado Técnico:** ACRA obliga a que el sistema mantenga un CCR superior al 45%. Al purgar activamente el ruido y consolidar el estado *antes* del enrutamiento final, ACRA soluciona la limitación expuesta en el *Routing Plateau*. El clúster pesado siempre recibe un contexto purificado, asegurando que la máxima precisión posible (Accuracy Limit) se expanda hacia el techo teórico del modelo.
