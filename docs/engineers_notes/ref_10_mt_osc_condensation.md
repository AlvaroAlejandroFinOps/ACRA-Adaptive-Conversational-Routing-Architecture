# Referencia 10: Condensación Secuencial y Mitigación del *Answer Bloat*

## 1. Cita Bibliográfica
> **[Investigadores de Context Compression] (2025-2026).** *MT-OSC: One-off Sequential Condensation for Multi-Turn Conversations.* arXiv preprint.

## 2. Resumen del Estudio
Los frameworks de condensación secuencial como *MT-OSC* proponen algoritmos que resumen y condensan automáticamente el historial del chat en segundo plano. El objetivo de este enfoque es retener la "verdad central" (core ground truth) de los requerimientos acumulados sin heredar el exceso de verbosidad o los desvíos menores del historial en crudo. Esta técnica ataca el problema del alargamiento artificial del contexto que abruma las ventanas de atención de los LLMs.

## 3. Argumentación Robusta y Aplicación a ACRA (Cognitive Stability)
El concepto de *MT-OSC* es el equivalente académico del mecanismo central de **Compresión Dinámica de Historial (DHC)** nativo en ACRA.

1.  **Vulnerabilidad Cognitiva:** El RFC de ACRA identifica la *Hipertrofia de Respuesta (Answer Bloat)*. Cuando los modelos acumulan contexto en crudo, las salidas generadas subsecuentemente se inflan entre un 20% y un 300% de manera espuria, con código ineficiente o redundante.
2.  **Mitigación Arquitectónica (ACRA):** El componente de *Compresión Dinámica de Historial (DHC)* en ACRA actúa purgando el estado conversacional durante la transición entre el clúster ligero y el pesado. Al igual que el MT-OSC, abstrae el historial conversacional transformándolo en representaciones semánticas consolidadas en lugar de un listado JSON interminable de mensajes de ida y vuelta.
3.  **Resultado Técnico:** Se logra un "Reinicio de Longitud Estocástica". La condensación asimétrica asegura que el clúster Pro evalúe una instrucción limpia en formato *Zero-Shot*, combatiendo de forma absoluta el efecto expansivo del *bloat* en entornos multi-turno prolongados.
