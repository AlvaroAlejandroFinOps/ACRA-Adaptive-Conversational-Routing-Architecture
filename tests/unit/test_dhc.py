import pytest
from src.core.dhc import DynamicHistoryCompressor
from src.core.edge_router import MessageTurn, TurnRole


def test_dhc_masks_assistant_verbosity_and_preserves_code():
    dhc = DynamicHistoryCompressor()
    verbose_reply = (
        "¡Hola! Por supuesto, con gusto te ayudo. Como modelo de lenguaje entiendo tu solicitud.\n"
        "Aquí está la función que me pediste:\n"
        "```python\ndef compute_hash(data):\n    return hash(data)\n```\n"
        "Espero que esto te sea de utilidad. Avísame si necesitas algo más."
    )

    cleaned_text, code_blocks = dhc.mask_assistant_verbosity(verbose_reply)
    assert len(code_blocks) == 1
    assert "def compute_hash" in code_blocks[0]
    assert "como modelo de lenguaje" not in cleaned_text.lower()
    assert "avísame si necesitas algo más" not in cleaned_text.lower()


def test_dhc_compress_calculates_positive_ccr():
    dhc = DynamicHistoryCompressor()
    history = [
        MessageTurn(
            role=TurnRole.USER,
            content="Necesito crear un índice invertido en memoria para búsqueda rápida.",
            turn_index=1
        ),
        MessageTurn(
            role=TurnRole.ASSISTANT,
            content=(
                "¡Hola estimado usuario! Con muchísimo gusto voy a asistirte en este proyecto tan interesante. "
                "Crear un índice invertido es una técnica clásica en recuperación de información. "
                "Permíteme explicarte durante varios párrafos introductorios sobre cómo funciona la indexación. "
                "Los índices invertidos mapean palabras a identificadores de documentos..."
            ),
            turn_index=1
        )
    ]
    current_input = "La restricción crítica es soportar 100k documentos con latencia menor a 5ms."

    comp_res = dhc.compress(history, current_input)
    assert comp_res.ccr > 0.0
    assert comp_res.consolidated_tokens_estimate < comp_res.raw_tokens_estimate
    assert len(comp_res.consolidated_user_requirements) == 2
