# Referencia 07: R2-Router y Enrutamiento Focalizado en Razonamiento

## 1. Cita Bibliográfica
> **[Investigadores de Routing] (2025).** *R2-Router: A New Paradigm for LLM Routing with Reasoning.* arXiv preprint.

## 2. Resumen del Estudio
El *R2-Router* introduce un cambio de paradigma en el enrutamiento de LLMs: en lugar de enrutar basándose puramente en la dificultad superficial de la pregunta, el enrutador evalúa explícitamente si la consulta requiere capacidades de *razonamiento profundo* (multi-paso, lógica formal, matemáticas). El estudio demuestra que reservar los modelos frontera de forma exclusiva para tareas de razonamiento maximiza el retorno de inversión computacional y previene que estos modelos se degraden o "alucinen" al tratar de aplicar cadenas lógicas a tareas triviales.

## 3. Argumentación Robusta y Aplicación a ACRA (Cognitive Stability)
Este estudio apoya la bifurcación de clústeres propuesta en ACRA y valida la topología asimétrica entre nodos ligeros y pesados.

1.  **Vulnerabilidad Cognitiva:** Forzar a un modelo de alto razonamiento a operar en tareas administrativas o de interacción superficial (cháchara, recolección de contexto inicial) disminuye su fiabilidad cuando eventualmente se le pide resolver el problema real (por acumulación de tokens irrelevantes).
2.  **Mitigación Arquitectónica (ACRA):** De acuerdo con el paradigma del *R2-Router*, ACRA mantiene su modelo *Pro* (el clúster pesado) en una reserva de exclusividad estricta. El modelo Pro nunca ejecuta tareas de formateo, recolección de variables o saludo. Estas son gestionadas localmente por el *Edge Router*.
3.  **Resultado Técnico:** El clúster Pro se activa bajo un régimen de *ejecución consolidada*, donde se aplica 100% al razonamiento profundo sobre un *payload* estructurado. Esto garantiza que la Aptitud Teórica del modelo ($A^{90}$) se alcance y se mantenga consistente, eliminando el desgaste cognitivo por tareas espurias.
