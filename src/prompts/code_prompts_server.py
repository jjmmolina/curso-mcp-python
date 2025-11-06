"""
Servidor MCP con prompts para asistencia de código (ejemplo Módulo 3)
"""

import asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Prompt, PromptMessage, TextContent, GetPromptResult
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("code-prompts-mcp")

@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    return [
        Prompt(
            name="revisar_codigo",
            description="Revisa código en busca de errores, mejoras y buenas prácticas",
            arguments=[
                {"name": "lenguaje", "description": "Lenguaje de programación", "required": True},
                {"name": "codigo", "description": "Código a revisar", "required": True},
            ],
        ),
        Prompt(
            name="explicar_codigo",
            description="Explica qué hace un fragmento de código",
            arguments=[
                {"name": "codigo", "description": "Código a explicar", "required": True},
                {"name": "nivel", "description": "basico|intermedio|avanzado", "required": False},
            ],
        ),
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "revisar_codigo":
        lenguaje = arguments.get("lenguaje", "").lower()
        codigo = arguments.get("codigo", "")
        mensaje = f"""Por favor, revisa el siguiente código {lenguaje} y proporciona:

1. Errores detectados
2. Mejoras sugeridas
3. Seguridad
4. Legibilidad

```{lenguaje}
{codigo}
```
"""
        return GetPromptResult(
            description=f"Revisión de código {lenguaje}",
            messages=[PromptMessage(role="user", content=TextContent(type="text", text=mensaje))],
        )

    if name == "explicar_codigo":
        codigo = arguments.get("codigo", "")
        nivel = arguments.get("nivel", "intermedio")
        mensaje = f"""Explica qué hace el siguiente código. Nivel: {nivel}

```
{codigo}
```
"""
        return GetPromptResult(
            description=f"Explicación de código ({nivel})",
            messages=[PromptMessage(role="user", content=TextContent(type="text", text=mensaje))],
        )

    raise ValueError(f"Prompt no encontrado: {name}")

async def main():
    logger.info("Iniciando servidor de prompts de código...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
