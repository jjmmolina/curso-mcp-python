import asyncio
import sys
from pathlib import Path

# Agregar 'src' al sys.path para importar módulos de ejemplo
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

from tools import notas_server  # type: ignore  # noqa: E402


def test_list_tools_contains_expected_names():
    tools = asyncio.run(notas_server.list_tools())
    names = {t.name for t in tools}
    assert {"crear_nota", "listar_notas", "buscar_notas", "eliminar_nota"}.issubset(names)


def test_buscar_notas_handles_empty_storage(tmp_path):
    # Asegura que el archivo de notas no interfiera usando un directorio temporal
    original_file = notas_server.NOTAS_FILE
    notas_server.NOTAS_FILE = tmp_path / "notas.json"

    try:
        # Debe responder sin errores aunque no haya notas
        result = asyncio.run(notas_server.buscar_notas({"termino": "nada"}))
        assert result and result[0].type == "text"
    finally:
        notas_server.NOTAS_FILE = original_file
