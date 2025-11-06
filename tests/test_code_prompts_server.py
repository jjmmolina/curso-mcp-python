import asyncio
import sys
from pathlib import Path

# Agregar 'src' al sys.path para importar módulos de ejemplo
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

from prompts import code_prompts_server  # type: ignore  # noqa: E402


def test_list_prompts_contains_expected_names():
    prompts = asyncio.run(code_prompts_server.list_prompts())
    names = {p.name for p in prompts}
    assert {"revisar_codigo", "explicar_codigo"}.issubset(names)


def test_get_prompt_revisar_codigo_basic():
    res = asyncio.run(
        code_prompts_server.get_prompt(
            name="revisar_codigo",
            arguments={"lenguaje": "python", "codigo": "print('hola')"},
        )
    )
    assert res and res.messages and res.messages[0].content.type == "text"
