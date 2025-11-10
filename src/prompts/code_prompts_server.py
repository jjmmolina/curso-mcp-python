"""
Servidor MCP con prompts para asistencia de código (ejemplo Módulo 3)
"""

import asyncio
from pydantic import Field
from mcp.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent, GetPromptResult
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = FastMCP(
    "code-prompts-mcp",
    "Un servidor que ofrece prompts para asistencia de código.",
)

@server.prompt()
def revisar_codigo(
    lenguaje: str = Field(..., description="Lenguaje de programación del código a revisar"),
    codigo: str = Field(..., description="Fragmento de código que necesita revisión")
) -> GetPromptResult:
    """Revisa código en busca de errores, mejoras y buenas prácticas."""
    mensaje = f"""Por favor, revisa el siguiente código {lenguaje} y proporciona:

1. Errores detectados
2. Mejoras sugeridas
3. Aspectos de seguridad
4. Comentarios sobre legibilidad

```{lenguaje}
{codigo}
```
"""
    return GetPromptResult(
        description=f"Revisión de código {lenguaje}",
        messages=[PromptMessage(role="user", content=TextContent(type="text", text=mensaje))],
    )

@server.prompt()
def explicar_codigo(
    codigo: str = Field(..., description="Código a explicar"),
    nivel: str = Field("intermedio", description="Nivel de detalle: basico|intermedio|avanzado")
) -> GetPromptResult:
    """Explica qué hace un fragmento de código."""
    mensaje = f"""Explica qué hace el siguiente código. La explicación debe ser de nivel {nivel}.

```
{codigo}
```
"""
    return GetPromptResult(
        description=f"Explicación de código (nivel {nivel})",
        messages=[PromptMessage(role="user", content=TextContent(type="text", text=mensaje))],
    )

async def main():
    logger.info("Iniciando servidor de prompts de código con FastMCP...")
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
