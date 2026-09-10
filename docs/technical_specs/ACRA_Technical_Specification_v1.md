# ACRA Technical Specification v1.0

## 1. Módulos del Sistema

ACRA se estructura en torno a una máquina de estados determinista compuesta por 6 subsistemas:

1. **`ACRAMetrics` (`src/core/metrics.py`):**
   - Formaliza $P̄$, $A^{90}$, $U_{10}^{90}$ y $\text{CCR}$.
2. **`EdgeRouter` (`src/core/edge_router.py`):**
   - Evalúa madurez $[0.0, 1.0]$ y aísla el clúster Pro de ambigüedades tempranas.
3. **`DynamicHistoryCompressor` (`src/core/dhc.py`):**
   - Aplica enmascaramiento asimétrico del asistente y purga ruido conversacional.
4. **`UnifiedContextTier` (`src/core/unified_context.py`):**
   - Mantiene snapshots densos en memoria y caché SHA-256 para erradicar el valle de atención en U.
5. **`HandoffEngine` (`src/core/handoff.py`):**
   - Ensambla payloads estériles de línea base limpia (Zero-Shot equivalente).
6. **`ACRAOrchestrator` (`src/core/orchestrator.py`):**
   - Máquina de estados que coordina el ciclo de vida del turno y la persistencia de sesiones.

## 2. Diagrama de Transición de Estados

```
[IDLE] ───> [INGESTING] ───┬───> [CLARIFYING] ───> [RESPONDING] ───> [IDLE]
                           │
                           └───> [CONSOLIDATING] ───> [ROUTING_PRO] ───> [EXECUTING_PRO] ───> [RESPONDING] ───> [IDLE]
```

## 3. Interfaces y Contratos de Datos

- **Estado Conversacional:** Definido bajo [`schemas/conversation_state.json`](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/DeepMind/ACRA-Adaptive%20Conversational%20Routing%20Architecture/schemas/conversation_state.json).
- **Decisiones de Ruteo:** Definidas bajo [`schemas/routing_decision.json`](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/DeepMind/ACRA-Adaptive%20Conversational%20Routing%20Architecture/schemas/routing_decision.json).
- **Configuración Global:** Centralizada en [`config/acra_config.yaml`](file:///d:/0001%20HyperScale%20Thinking/PROYECTOS%20CLOUD/DeepMind/ACRA-Adaptive%20Conversational%20Routing%20Architecture/config/acra_config.yaml).
