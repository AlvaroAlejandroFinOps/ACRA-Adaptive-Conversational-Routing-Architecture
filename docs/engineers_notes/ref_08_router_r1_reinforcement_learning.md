# Referencia 08: Router-R1 y la Toma de Decisiones Secuencial en Enrutamiento

## 1. Cita Bibliográfica
> **[Investigadores de Reinforcement Learning para LLMs] (2025-2026).** *Router-R1: Teaching LLMs Multi-Round Routing and Aggregation via Reinforcement Learning.* arXiv preprint.

## 2. Resumen del Estudio
*Router-R1* aborda un problema crítico en la investigación del enrutamiento: tratar la asignación de modelos como una clasificación estática ("envía esta petición al Modelo A o al Modelo B"). En cambio, propone que el enrutamiento debe ser un proceso de toma de decisiones secuencial y multi-ronda. Utilizando Aprendizaje por Refuerzo (RL), entrenan al sistema para evaluar si la información disponible en un turno dado es suficiente para enviar al modelo experto, o si requiere rondas adicionales de clarificación o "pensamiento" antes de ejecutar la acción final.

## 3. Argumentación Robusta y Aplicación a ACRA (Cognitive Stability)
Este paper constituye una de las mayores justificaciones arquitectónicas para la naturaleza interactiva y orquestada de ACRA.

1.  **Vulnerabilidad Cognitiva:** Un enrutador estático que envía la solicitud inicial inmediatamente a un modelo pesado sufrirá degradación (como se indica en las referencias anteriores de caída estocástica y *Intent Mismatch*) porque ignora la evolución temporal de la conversación.
2.  **Mitigación Arquitectónica (ACRA):** ACRA no es un *proxy* ciego; es una máquina de estados orquestada. Actúa exactamente bajo la premisa de *Router-R1*: ejecuta múltiples rondas (turnos) con el usuario a través del clúster ligero. Continuamente evalúa, mediante reglas deterministas, la completitud y madurez del *payload*.
3.  **Resultado Técnico:** Las interacciones multi-ronda del usuario convergen progresivamente en ACRA hasta alcanzar el umbral de activación óptimo. Solo entonces, la solicitud consolidada se envía (rutea) al nodo *heavy*. Esto simula un proceso de *Reinforcement Learning* en tiempo real, garantizando que el coste computacional final solo se ejecute cuando el estado del problema es determinista.
