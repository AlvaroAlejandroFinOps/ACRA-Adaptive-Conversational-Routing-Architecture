# Referencia 06: LLMRouterBench y Métricas de Evaluación de Enrutamiento

## 1. Cita Bibliográfica
> **[Investigadores de Evaluación de Enrutamiento] (2024-2025).** *LLMRouterBench: A Massive Benchmark and Unified Framework for LLM Routing.* arXiv preprint.

## 2. Resumen del Estudio
Este trabajo presenta un marco de evaluación exhaustivo para enrutadores de LLMs. Tradicionalmente, la selección de modelos se hacía de forma estática o mediante pruebas *ad-hoc*. *LLMRouterBench* estandariza cómo medir la eficiencia de un enrutador dinámico que debe equilibrar el uso de VRAM, el costo de inferencia por token y la calidad de la respuesta (latencia vs. precisión). Expone que muchos enrutadores superficiales fallan al intentar optimizar simultáneamente estas tres variables sin sacrificar el rendimiento final.

## 3. Argumentación Robusta y Aplicación a ACRA (Cognitive Stability)
La fundamentación técnica de *LLMRouterBench* provee la métrica base para el diseño del motor de ruteo y balanceo de carga en ACRA.

1.  **Vulnerabilidad Cognitiva:** Asignar todas las consultas, desde un saludo básico ("Hola") hasta un algoritmo complejo, a un único LLM de frontera genera un desperdicio masivo de inferencia y expone al modelo a agotamiento de contexto por turnos improductivos.
2.  **Mitigación Arquitectónica (ACRA):** ACRA emplea un sistema de *Edge Router* (clúster ligero) alineado con las mejores prácticas establecidas en *LLMRouterBench*. El enrutador de ACRA no solo clasifica el *intent*, sino que mide la "madurez" del prompt. Delega todos los turnos de clarificación estocásticos y ambiguos al clúster ligero.
3.  **Resultado Técnico:** ACRA logra optimizar las tres variables de *LLMRouterBench* (Costo, Latencia y Precisión) al asegurar que el modelo pesado solo consuma VRAM e inferencia cuando la probabilidad de éxito (basada en la madurez del payload) es máxima, reduciendo drásticamente los gastos operativos de infraestructura.
